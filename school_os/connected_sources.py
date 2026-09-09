"""Finite exact-byte source adapters for the connected Gmail ingestion path.

This module deliberately owns only source bytes and selected extraction.  The
ingestor still owns complete threads, cataloguing, audit, and cursor decisions.
Host implementations dispatch the two named bridge kinds documented in
``codex_bridge``: ``resource.fetch_https`` and ``extract.image``.
"""

from __future__ import annotations

import base64
import binascii
import io
import os
import stat
import subprocess
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from PIL import Image, UnidentifiedImageError
from pypdf import PdfReader

from .codex_bridge import BridgeError, CodexGmailPort, CodexSourceHostPort, JsonlPeer
from .contracts import sha256_bytes
from .importer import AttachmentExtraction, AttachmentRead, DirectResourceRead


class ConnectedSourcesError(ValueError):
    """Raised when source bytes or finite extractor evidence is incomplete."""


_IMAGE_MIME = {"image/png": b"\x89PNG\r\n\x1a\n", "image/jpeg": b"\xff\xd8\xff"}


def _https(value: Any) -> str:
    if not isinstance(value, str):
        raise ConnectedSourcesError("resource URL is malformed")
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
        raise ConnectedSourcesError("resource URL is not direct HTTPS")
    return value


def _strict_base64(value: Any) -> bytes:
    if not isinstance(value, str):
        raise ConnectedSourcesError("host byte response lacks standard base64")
    try:
        return base64.b64decode(value, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ConnectedSourcesError("host byte response has invalid standard base64") from exc


def _positive_int(value: Any) -> bool:
    return type(value) is int and value > 0


def _finite_host_arguments(kind: str, args: Mapping[str, Any]) -> None:
    """Validate the named host helpers independently of JSONL dispatch."""
    if kind == "resource.fetch_https":
        required = {"url", "max_bytes", "max_redirects", "timeout_ms"}
        if set(args) != required or not _positive_int(args.get("max_bytes")) or not _positive_int(args.get("timeout_ms")) or type(args.get("max_redirects")) is not int or args["max_redirects"] < 0:
            raise ConnectedSourcesError("HTTPS host helper arguments are not finite and bounded")
        _https(args.get("url"))
        return
    if kind == "extract.image":
        required = {"path", "source_id", "mime_type", "original_sha256", "byte_length", "width", "height"}
        if set(args) != required:
            raise ConnectedSourcesError("image host helper arguments have an unsupported shape")
        if not isinstance(args.get("path"), str) or not Path(args["path"]).is_absolute() or not all(isinstance(args.get(name), str) and args[name] for name in ("source_id", "mime_type", "original_sha256")) or type(args.get("byte_length")) is not int or args["byte_length"] < 0 or not _positive_int(args.get("width")) or not _positive_int(args.get("height")):
            raise ConnectedSourcesError("image host helper arguments are malformed")
        return
    raise ConnectedSourcesError("unexpected finite source host helper kind")


def _contained_regular(path: Path, root: Path) -> Path:
    root = root.resolve(strict=True)
    try:
        candidate = path.resolve(strict=True)
        candidate.relative_to(root)
    except (OSError, ValueError) as exc:
        raise ConnectedSourcesError("source file escapes the private run directory") from exc
    status = candidate.stat(follow_symlinks=False)
    if not stat.S_ISREG(status.st_mode) or path.is_symlink():
        raise ConnectedSourcesError("source file is not a contained regular file")
    return candidate


def _image_details(data: bytes, mime_type: str, *, max_pixels: int, max_dimension: int) -> tuple[int, int]:
    signature = _IMAGE_MIME.get(mime_type)
    if signature is None or not data.startswith(signature):
        raise ConnectedSourcesError("image signature disagrees with declared MIME type")
    try:
        with Image.open(io.BytesIO(data)) as image:
            if image.get_format_mimetype() != mime_type or getattr(image, "n_frames", 1) != 1:
                raise ConnectedSourcesError("image MIME or frame count is unsupported")
            width, height = image.size
            image.verify()
    except (UnidentifiedImageError, OSError, SyntaxError) as exc:
        raise ConnectedSourcesError("image bytes cannot be decoded exactly") from exc
    if not all(isinstance(value, int) and value > 0 for value in (width, height)) or width > max_dimension or height > max_dimension or width * height > max_pixels:
        raise ConnectedSourcesError("image dimensions exceed the selected bound")
    return width, height


@dataclass(frozen=True)
class SourceBounds:
    max_bytes: int = 1_048_576
    max_redirects: int = 3
    timeout_ms: int = 10_000
    max_image_pixels: int = 16_000_000
    max_image_dimension: int = 8_000
    max_image_text_bytes: int = 256_000
    max_pdf_pages: int = 100


class ConnectedSourceAdapters:
    """Translate finite bridge/file responses into existing importer contracts."""

    def __init__(self, *, peer: JsonlPeer, run_directory: Path, bounds: SourceBounds = SourceBounds()) -> None:
        if min(bounds.max_bytes, bounds.timeout_ms, bounds.max_image_pixels, bounds.max_image_dimension, bounds.max_image_text_bytes, bounds.max_pdf_pages) < 1 or bounds.max_redirects < 0:
            raise ConnectedSourcesError("source bounds are invalid")
        self.gmail = CodexGmailPort(peer)
        self.host = CodexSourceHostPort(peer)
        self.run_directory = run_directory.resolve(strict=True)
        self.bounds = bounds

    def gmail_attachment(
        self, message_id: str, attachment_id: str, *, mime_type: str, declared_byte_size: int,
    ) -> AttachmentRead:
        """Read a Gmail attachment only through a contained original-byte file."""
        if not all(isinstance(value, str) and value for value in (message_id, attachment_id, mime_type)) or not isinstance(declared_byte_size, int) or declared_byte_size < 0:
            raise ConnectedSourcesError("attachment request lacks exact identity/MIME/size")
        result = self.gmail.read_attachment(message_id, attachment_id)
        if not isinstance(result, Mapping) or set(result) != {"message_id", "attachment_id", "mime_type", "byte_size", "file_uri"}:
            raise ConnectedSourcesError("Gmail attachment response has an unsupported shape")
        if result.get("message_id") != message_id or result.get("attachment_id") != attachment_id or result.get("mime_type") != mime_type or result.get("byte_size") != declared_byte_size:
            raise ConnectedSourcesError("Gmail attachment response identity/MIME/size disagrees")
        file_uri = result.get("file_uri")
        if not isinstance(file_uri, str):
            raise ConnectedSourcesError("Gmail attachment response lacks an original file URI")
        path = _contained_regular(Path(file_uri), self.run_directory)
        data = path.read_bytes()
        if len(data) != declared_byte_size or len(data) > self.bounds.max_bytes:
            raise ConnectedSourcesError("Gmail attachment original bytes exceed or disagree with declared size")
        return AttachmentRead(
            attachment_id, mime_type, True, declared_byte_size, data, None,
            {"kind": "provider_attachment_file", "message_id": message_id, "attachment_id": attachment_id, "sha256": sha256_bytes(data)},
        )

    def fetch_https(self, url: str) -> DirectResourceRead:
        requested = _https(url)
        result = self.host.fetch_https(
            url=requested, max_bytes=self.bounds.max_bytes,
            max_redirects=self.bounds.max_redirects, timeout_ms=self.bounds.timeout_ms,
        )
        required = {"requested_url", "final_url", "redirect_chain", "status_code", "mime_type", "content_encoding", "declared_content_length", "bytes_read", "eof", "complete", "b64_string"}
        if not isinstance(result, Mapping) or set(result) != required:
            raise ConnectedSourcesError("HTTPS host response has an unsupported shape")
        data = _strict_base64(result.get("b64_string"))
        chain = result.get("redirect_chain")
        if (
            result.get("requested_url") != requested or not isinstance(chain, list) or not chain
            or any(_https(item) != item for item in chain) or chain[0] != requested
            or result.get("final_url") != chain[-1] or len(chain) - 1 > self.bounds.max_redirects
            or len(set(chain)) != len(chain) or result.get("status_code") != 200
            or not isinstance(result.get("mime_type"), str) or not result["mime_type"]
            or result.get("content_encoding") != "identity"
            or result.get("eof") is not True or result.get("complete") is not True
            or type(result.get("bytes_read")) is not int or result["bytes_read"] != len(data)
            or len(data) > self.bounds.max_bytes
            or (result.get("declared_content_length") is not None and (type(result["declared_content_length"]) is not int or result["declared_content_length"] != len(data)))
        ):
            raise ConnectedSourcesError("HTTPS host response lacks complete bounded byte evidence")
        return DirectResourceRead(
            result["final_url"], tuple(chain), data, result["mime_type"], 200, True, True,
            len(data), result["declared_content_length"],
        )

    def extract_image(self, *, source_id: str, data: bytes, mime_type: str) -> AttachmentExtraction:
        if not isinstance(source_id, str) or not source_id or not isinstance(data, bytes) or len(data) > self.bounds.max_bytes:
            raise ConnectedSourcesError("image extraction input is invalid")
        width, height = _image_details(data, mime_type, max_pixels=self.bounds.max_image_pixels, max_dimension=self.bounds.max_image_dimension)
        name = f"image-{sha256_bytes(data)}"
        path = self.run_directory / name
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            checked = _contained_regular(path, self.run_directory)
            observed = checked.read_bytes()
            if observed != data:
                raise ConnectedSourcesError("image file changed before host extraction")
            result = self.host.extract_image(
                path=str(checked), source_id=source_id, mime_type=mime_type,
                original_sha256=sha256_bytes(data), byte_length=len(data), width=width, height=height,
            )
        finally:
            path.unlink(missing_ok=True)
        required = {"source_id", "mime_type", "original_sha256", "byte_length", "width", "height", "complete", "text"}
        if not isinstance(result, Mapping) or set(result) != required or result.get("source_id") != source_id or result.get("mime_type") != mime_type or result.get("original_sha256") != sha256_bytes(data) or result.get("byte_length") != len(data) or result.get("width") != width or result.get("height") != height or result.get("complete") is not True or not isinstance(result.get("text"), str):
            raise ConnectedSourcesError("image host response lacks exact identity and completeness evidence")
        text = result["text"]
        if not text or len(text.encode("utf-8", errors="strict")) > self.bounds.max_image_text_bytes:
            raise ConnectedSourcesError("image host response has empty or oversized text")
        return AttachmentExtraction(text, {"kind": "provider_page_region", "page": 1, "region": "full_image"}, ("image:1",), 1)

    def extract_pdf(self, *, source_id: str, data: bytes) -> AttachmentExtraction:
        """Render every ordered PDF page and bind each one to image extraction."""
        if not isinstance(source_id, str) or not source_id or not data.startswith(b"%PDF-") or len(data) > self.bounds.max_bytes:
            raise ConnectedSourcesError("PDF extraction input is invalid")
        try:
            reader = PdfReader(io.BytesIO(data), strict=True)
            if reader.is_encrypted:
                raise ConnectedSourcesError("encrypted PDF cannot establish complete reader-visible content")
            pages = list(reader.pages)
        except ConnectedSourcesError:
            raise
        except Exception as exc:
            raise ConnectedSourcesError("PDF cannot be parsed completely") from exc
        if not pages or len(pages) > self.bounds.max_pdf_pages:
            raise ConnectedSourcesError("PDF page count is outside the selected bound")
        digest = sha256_bytes(data)
        pdf_path = self.run_directory / f"pdf-{digest}.pdf"
        descriptor = os.open(pdf_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        texts: list[str] = []
        try:
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            if _contained_regular(pdf_path, self.run_directory).read_bytes() != data:
                raise ConnectedSourcesError("PDF file changed before rendering")
            for number in range(1, len(pages) + 1):
                prefix = self.run_directory / f"pdf-{digest}-page-{number}"
                image_path = prefix.with_suffix(".png")
                try:
                    subprocess.run(
                        ["pdftoppm", "-f", str(number), "-l", str(number), "-png", "-singlefile", str(pdf_path), str(prefix)],
                        check=True, timeout=max(1, self.bounds.timeout_ms / 1000),
                        capture_output=True,
                    )
                    rendered = _contained_regular(image_path, self.run_directory).read_bytes()
                    if len(rendered) > self.bounds.max_bytes:
                        raise ConnectedSourcesError("rendered PDF page exceeds the selected byte bound")
                    extracted = self.extract_image(
                        source_id=f"{source_id}:page:{number}", data=rendered, mime_type="image/png",
                    )
                    texts.append(extracted.text)
                except (OSError, subprocess.SubprocessError, ConnectedSourcesError) as exc:
                    raise ConnectedSourcesError(f"PDF page {number} needs qualified visual extraction") from exc
                finally:
                    image_path.unlink(missing_ok=True)
        finally:
            pdf_path.unlink(missing_ok=True)
        combined = "\n\f\n".join(texts)
        encoded = combined.encode("utf-8", errors="strict")
        return AttachmentExtraction(
            combined, {"kind": "extracted_text_span", "byte_start": 0, "byte_end": len(encoded)},
            tuple(f"page:{number}" for number in range(1, len(pages) + 1)), len(pages),
        )


@dataclass(frozen=True)
class SourceHostHelpers:
    """Executable finite host-helper route for the named bridge dispatch kinds.

    The surrounding Codex host supplies a bounded HTTPS implementation and an
    original-detail image viewer/semantic callback. This adapter validates the
    call shape before returning it to the JSONL bridge; it does not turn either
    callback into an arbitrary tool executor.
    """

    fetch_https_impl: Callable[[Mapping[str, Any]], Mapping[str, Any]]
    extract_image_impl: Callable[[Mapping[str, Any]], Mapping[str, Any]]
    run_directory: Path

    def dispatch(self, kind: str, args: Mapping[str, Any]) -> Mapping[str, Any]:
        _finite_host_arguments(kind, args)
        if kind == "resource.fetch_https":
            return self.fetch_https_impl(dict(args))
        if kind == "extract.image":
            path = _contained_regular(Path(args["path"]), self.run_directory)
            data = path.read_bytes()
            mime_type = args.get("mime_type")
            if (
                args.get("original_sha256") != sha256_bytes(data)
                or args.get("byte_length") != len(data)
                or not isinstance(mime_type, str)
            ):
                raise ConnectedSourcesError("image host helper observed different original bytes")
            width, height = _image_details(data, mime_type, max_pixels=16_000_000, max_dimension=8_000)
            if args.get("width") != width or args.get("height") != height:
                raise ConnectedSourcesError("image host helper observed different dimensions")
            return self.extract_image_impl(dict(args))
        raise ConnectedSourcesError("unexpected finite source host helper kind")
