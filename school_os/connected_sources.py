"""Finite exact-byte source adapters for the connected Gmail ingestion path.

This module deliberately owns only source bytes and selected extraction.  The
ingestor still owns complete threads, cataloguing, audit, and cursor decisions.
Host implementations dispatch the two named bridge kinds documented in
``codex_bridge``: ``resource.fetch_https`` and ``extract.image``.
"""

from __future__ import annotations

import base64
import binascii
import http.client
import io
import ipaddress
import math
import os
import resource
import socket
import ssl
import stat
import subprocess
import time
import uuid
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

from PIL import Image, UnidentifiedImageError
from pypdf import PdfReader

from .codex_bridge import CodexGmailPort, CodexSourceHostPort, JsonlPeer
from .contracts import sha256_bytes
from .importer import AttachmentExtraction, AttachmentRead, DirectResourceRead


class ConnectedSourcesError(ValueError):
    """Raised when source bytes or finite extractor evidence is incomplete."""


_IMAGE_MIME = {"image/png": b"\x89PNG\r\n\x1a\n", "image/jpeg": b"\xff\xd8\xff"}
_REDIRECT_STATUSES = {301, 302, 303, 307, 308}
_GMAIL_ATTACHMENT_KEYS = {
    "attachment_id", "content", "content_truncated", "extraction_file_uri",
    "file_uri", "filename", "images", "message_id", "mime_type", "size_bytes",
}
_HOST_MAX_BYTES = 8_388_608
_HOST_MAX_REDIRECTS = 5
_HOST_MAX_TIMEOUT_MS = 60_000


def _https(value: Any) -> str:
    if not isinstance(value, str):
        raise ConnectedSourcesError("resource URL is malformed")
    if any(ord(character) <= 32 or ord(character) == 127 for character in value):
        raise ConnectedSourcesError("resource URL contains unsafe whitespace or controls")
    parsed = urlparse(value)
    try:
        parsed.port
    except ValueError as exc:
        raise ConnectedSourcesError("resource URL port is malformed") from exc
    if (
        parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password
        or parsed.fragment or parsed.hostname.endswith(".")
    ):
        raise ConnectedSourcesError("resource URL is not direct HTTPS")
    return value


def _remaining_seconds(deadline: float, clock: Callable[[], float]) -> float:
    remaining = deadline - clock()
    if remaining <= 0:
        raise ConnectedSourcesError("HTTPS fetch exceeded its end-to-end deadline")
    return remaining


def _public_addresses(host: str, port: int, resolver: Callable[..., Any]) -> tuple[str, ...]:
    try:
        answers = resolver(host, port, type=socket.SOCK_STREAM)
    except OSError as exc:
        raise ConnectedSourcesError("HTTPS host DNS resolution failed") from exc
    addresses: list[str] = []
    for answer in answers:
        try:
            address = answer[4][0]
            parsed = ipaddress.ip_address(address.split("%", 1)[0])
        except (IndexError, TypeError, ValueError):
            raise ConnectedSourcesError("HTTPS host DNS answer is malformed")
        if not parsed.is_global:
            raise ConnectedSourcesError("HTTPS host resolves outside the public address space")
        if str(parsed) not in addresses:
            addresses.append(str(parsed))
    if not addresses:
        raise ConnectedSourcesError("HTTPS host has no public address")
    return tuple(addresses)


class _PinnedHTTPSConnection(http.client.HTTPSConnection):
    """TLS connection pinned to one already-reviewed DNS address."""

    def __init__(self, host: str, port: int, address: str, *, timeout: float, context: ssl.SSLContext) -> None:
        super().__init__(host, port=port, timeout=timeout, context=context)
        self._school_os_address = address

    def connect(self) -> None:
        raw = socket.create_connection((self._school_os_address, self.port), self.timeout)
        try:
            self.sock = self._context.wrap_socket(raw, server_hostname=self.host)
        except Exception:
            raw.close()
            raise


@dataclass(frozen=True)
class BoundedHttpsFetcher:
    """Concrete streaming HTTPS GET with public-address and completeness gates."""

    resolver: Callable[..., Any] = socket.getaddrinfo
    connection_factory: Callable[[str, int, str, float], Any] | None = None
    clock: Callable[[], float] = time.monotonic

    def _connection(self, host: str, port: int, address: str, timeout: float) -> Any:
        if self.connection_factory is not None:
            return self.connection_factory(host, port, address, timeout)
        return _PinnedHTTPSConnection(
            host, port, address, timeout=timeout, context=ssl.create_default_context(),
        )

    def __call__(self, args: Mapping[str, Any]) -> Mapping[str, Any]:
        _finite_host_arguments("resource.fetch_https", args)
        requested = _https(args["url"])
        maximum = args["max_bytes"]
        deadline = self.clock() + (args["timeout_ms"] / 1000)
        chain = [requested]
        current = requested
        for redirect_count in range(args["max_redirects"] + 1):
            parsed = urlparse(current)
            assert parsed.hostname is not None
            port = parsed.port or 443
            addresses = _public_addresses(parsed.hostname, port, self.resolver)
            connection = None
            last_error: Exception | None = None
            for address in addresses:
                try:
                    connection = self._connection(
                        parsed.hostname, port, address, _remaining_seconds(deadline, self.clock),
                    )
                    path = parsed.path or "/"
                    if parsed.query:
                        path += "?" + parsed.query
                    connection.request("GET", path, headers={
                        "Accept-Encoding": "identity", "Connection": "close",
                        "User-Agent": "School-OS/0.1 bounded-source-fetch",
                    })
                    response = connection.getresponse()
                    break
                except (OSError, ssl.SSLError, http.client.HTTPException) as exc:
                    last_error = exc
                    if connection is not None:
                        connection.close()
                    connection = None
            if connection is None:
                raise ConnectedSourcesError("HTTPS connection failed for every reviewed public address") from last_error
            try:
                if response.status in _REDIRECT_STATUSES:
                    locations = response.headers.get_all("Location") or []
                    if len(locations) != 1 or redirect_count >= args["max_redirects"]:
                        raise ConnectedSourcesError("HTTPS redirect is missing, ambiguous, or exceeds the bound")
                    target = _https(urljoin(current, locations[0]))
                    if target in chain:
                        raise ConnectedSourcesError("HTTPS redirect loop is not allowed")
                    chain.append(target)
                    current = target
                    continue
                if response.status != 200:
                    raise ConnectedSourcesError("HTTPS resource did not return status 200")
                encodings = response.headers.get_all("Content-Encoding") or []
                if len(encodings) > 1 or (encodings and encodings[0].strip().lower() not in {"", "identity"}):
                    raise ConnectedSourcesError("HTTPS resource content encoding is unsupported")
                types = response.headers.get_all("Content-Type") or []
                if len(types) != 1:
                    raise ConnectedSourcesError("HTTPS resource lacks one declared MIME type")
                mime_type = types[0].split(";", 1)[0].strip().lower()
                if not mime_type or "/" not in mime_type or "," in mime_type:
                    raise ConnectedSourcesError("HTTPS resource MIME type is malformed")
                lengths = response.headers.get_all("Content-Length") or []
                declared: int | None = None
                if lengths:
                    if len(lengths) != 1:
                        raise ConnectedSourcesError("HTTPS resource has ambiguous content length")
                    try:
                        declared = int(lengths[0], 10)
                    except ValueError as exc:
                        raise ConnectedSourcesError("HTTPS resource content length is malformed") from exc
                    if declared < 0 or declared > maximum:
                        raise ConnectedSourcesError("HTTPS resource exceeds the selected byte bound")
                chunks: list[bytes] = []
                observed = 0
                while True:
                    remaining = _remaining_seconds(deadline, self.clock)
                    if getattr(connection, "sock", None) is not None:
                        connection.sock.settimeout(remaining)
                    chunk = response.read(min(65_536, maximum + 1 - observed))
                    if not chunk:
                        break
                    observed += len(chunk)
                    if observed > maximum:
                        raise ConnectedSourcesError("HTTPS resource exceeds the selected byte bound")
                    chunks.append(chunk)
                data = b"".join(chunks)
                if declared is not None and declared != len(data):
                    raise ConnectedSourcesError("HTTPS resource ended before its declared byte length")
                return {
                    "requested_url": requested, "final_url": current, "redirect_chain": chain,
                    "status_code": 200, "mime_type": mime_type, "content_encoding": "identity",
                    "declared_content_length": declared, "bytes_read": len(data), "eof": True,
                    "complete": True, "b64_string": base64.b64encode(data).decode("ascii"),
                }
            except (OSError, ssl.SSLError, http.client.HTTPException) as exc:
                raise ConnectedSourcesError("HTTPS response was truncated or unreadable") from exc
            finally:
                connection.close()
        raise ConnectedSourcesError("HTTPS redirect bound was exhausted")


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
        if (
            set(args) != required or not _positive_int(args.get("max_bytes"))
            or args["max_bytes"] > _HOST_MAX_BYTES or not _positive_int(args.get("timeout_ms"))
            or args["timeout_ms"] > _HOST_MAX_TIMEOUT_MS or type(args.get("max_redirects")) is not int
            or not 0 <= args["max_redirects"] <= _HOST_MAX_REDIRECTS
        ):
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


def _pdf_number(value: Any, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ConnectedSourcesError(f"PDF {label} is malformed") from exc
    if not math.isfinite(number):
        raise ConnectedSourcesError(f"PDF {label} is not finite")
    return number


def _pdf_render_scale(page: Any, bounds: "SourceBounds") -> tuple[int, int]:
    try:
        media = page.mediabox
        crop = page.cropbox
        boxes = (
            tuple(_pdf_number(value, "page box") for value in (media.left, media.bottom, media.right, media.top)),
            tuple(_pdf_number(value, "page box") for value in (crop.left, crop.bottom, crop.right, crop.top)),
        )
        rotation_value = _pdf_number(page.get("/Rotate", 0) or 0, "page rotation")
        rotation = int(rotation_value)
    except ConnectedSourcesError:
        raise
    except Exception as exc:
        raise ConnectedSourcesError("PDF page box or rotation cannot be inspected") from exc
    if rotation != rotation_value or rotation % 90 or abs(rotation) > 270:
        raise ConnectedSourcesError("PDF page rotation is unsupported")
    dimensions: list[tuple[float, float]] = []
    for left, bottom, right, top in boxes:
        width, height = right - left, top - bottom
        if (
            min(width, height) <= 0 or max(width, height) > bounds.max_pdf_page_points
            or max(abs(left), abs(bottom), abs(right), abs(top)) > bounds.max_pdf_page_points
        ):
            raise ConnectedSourcesError("PDF page box is outside the pre-render bound")
        dimensions.append((width, height))
    media_values, crop_values = boxes
    if (
        crop_values[0] < media_values[0] or crop_values[1] < media_values[1]
        or crop_values[2] > media_values[2] or crop_values[3] > media_values[3]
    ):
        raise ConnectedSourcesError("PDF crop box is outside its media box")
    width, height = dimensions[1]
    if rotation % 180:
        width, height = height, width
    long_side, short_side = max(width, height), min(width, height)
    natural_long = math.ceil(long_side * bounds.pdf_render_dpi / 72)
    pixel_long = math.floor(math.sqrt(bounds.max_image_pixels * long_side / short_side))
    scale = min(natural_long, bounds.max_image_dimension, pixel_long)
    if scale < 1:
        raise ConnectedSourcesError("PDF page cannot fit the pre-render pixel bound")
    pixels = scale * max(1, math.ceil(scale * short_side / long_side))
    while pixels > bounds.max_image_pixels and scale > 1:
        scale -= 1
        pixels = scale * max(1, math.ceil(scale * short_side / long_side))
    if pixels > bounds.max_image_pixels:
        raise ConnectedSourcesError("PDF page cannot fit the pre-render pixel bound")
    return scale, pixels


def _reject_unsupported_pdf_features(reader: PdfReader, pages: list[Any]) -> None:
    """Inventory only feature keys; never extract hidden or embedded payloads."""
    try:
        root = reader.trailer["/Root"].get_object()
        names = root.get("/Names")
        if names is not None and "/EmbeddedFiles" in names.get_object():
            raise ConnectedSourcesError("PDF embedded files are unsupported")
        if "/AF" in root:
            raise ConnectedSourcesError("PDF associated files are unsupported")
        for page in pages:
            if "/AF" in page:
                raise ConnectedSourcesError("PDF associated page files are unsupported")
            annotations = page.get("/Annots") or []
            for reference in annotations:
                annotation = reference.get_object()
                if annotation.get("/Subtype") in {"/FileAttachment", "/RichMedia", "/3D", "/Movie", "/Sound", "/Screen"}:
                    raise ConnectedSourcesError("PDF contains an unsupported substantive annotation")
    except ConnectedSourcesError:
        raise
    except Exception as exc:
        raise ConnectedSourcesError("PDF feature inventory cannot be completed") from exc


def _limit_render_file(size: int) -> None:
    _soft, hard = resource.getrlimit(resource.RLIMIT_FSIZE)
    selected = size if hard == resource.RLIM_INFINITY else min(size, hard)
    resource.setrlimit(resource.RLIMIT_FSIZE, (selected, hard))


@dataclass(frozen=True)
class SourceBounds:
    max_bytes: int = 1_048_576
    max_redirects: int = 3
    timeout_ms: int = 10_000
    max_image_pixels: int = 16_000_000
    max_image_dimension: int = 8_000
    max_image_text_bytes: int = 256_000
    max_pdf_pages: int = 100
    max_pdf_page_points: int = 14_400
    max_pdf_rendered_bytes: int = 16_777_216
    max_pdf_rendered_pixels: int = 64_000_000
    max_pdf_text_bytes: int = 1_048_576
    pdf_render_dpi: int = 150


class ConnectedSourceAdapters:
    """Translate finite bridge/file responses into existing importer contracts."""

    def __init__(self, *, peer: JsonlPeer, run_directory: Path, bounds: SourceBounds = SourceBounds()) -> None:
        positive_bounds = (
            bounds.max_bytes, bounds.timeout_ms, bounds.max_image_pixels,
            bounds.max_image_dimension, bounds.max_image_text_bytes, bounds.max_pdf_pages,
            bounds.max_pdf_page_points, bounds.max_pdf_rendered_bytes,
            bounds.max_pdf_rendered_pixels, bounds.max_pdf_text_bytes, bounds.pdf_render_dpi,
        )
        if (
            any(type(value) is not int or value < 1 for value in positive_bounds)
            or type(bounds.max_redirects) is not int
            or bounds.max_bytes > _HOST_MAX_BYTES
            or not 0 <= bounds.max_redirects <= _HOST_MAX_REDIRECTS
            or bounds.timeout_ms > _HOST_MAX_TIMEOUT_MS
        ):
            raise ConnectedSourcesError("source bounds are invalid")
        self.gmail = CodexGmailPort(peer)
        self.host = CodexSourceHostPort(peer)
        self.run_directory = run_directory.resolve(strict=True)
        self.bounds = bounds

    def gmail_attachment(
        self, message_id: str, attachment_id: str, *, mime_type: str, declared_byte_size: int,
    ) -> AttachmentRead:
        """Read the advertised Gmail original-file object, never its preview."""
        if not all(isinstance(value, str) and value for value in (message_id, attachment_id, mime_type)) or type(declared_byte_size) is not int or declared_byte_size < 0:
            raise ConnectedSourcesError("attachment request lacks exact identity/MIME/size")
        result = self.gmail.read_attachment(message_id, attachment_id)
        if (
            not isinstance(result, Mapping) or not {"message_id", "attachment_id", "mime_type", "filename"} <= set(result)
            or not set(result) <= _GMAIL_ATTACHMENT_KEYS
        ):
            raise ConnectedSourcesError("Gmail attachment response has an unsupported shape")
        size_bytes = result.get("size_bytes")
        if (
            result.get("message_id") != message_id or result.get("attachment_id") != attachment_id
            or result.get("mime_type") != mime_type
            or not isinstance(result.get("filename"), str) or not result["filename"]
            or (size_bytes is not None and (type(size_bytes) is not int or size_bytes < 0 or size_bytes != declared_byte_size))
        ):
            raise ConnectedSourcesError("Gmail attachment response identity/MIME/size disagrees")
        file_uri = result.get("file_uri")
        if not isinstance(file_uri, Mapping) or set(file_uri) - {"download_url", "file_id", "file_name", "mime_type"}:
            raise ConnectedSourcesError("Gmail attachment response lacks an original file URI")
        download_url, file_id = file_uri.get("download_url"), file_uri.get("file_id")
        if (
            _https(download_url) != download_url or not isinstance(file_id, str) or not file_id
            or (file_uri.get("mime_type") is not None and file_uri.get("mime_type") != mime_type)
            or (file_uri.get("file_name") is not None and not isinstance(file_uri.get("file_name"), str))
        ):
            raise ConnectedSourcesError("Gmail original file reference is malformed or disagrees")
        truncated = result.get("content_truncated", False)
        if type(truncated) is not bool:
            raise ConnectedSourcesError("Gmail extraction truncation flag is malformed")
        for key in ("content", "images"):
            if key in result and not isinstance(result[key], list):
                raise ConnectedSourcesError("Gmail inline extraction preview is malformed")
        extraction_uri = result.get("extraction_file_uri")
        if extraction_uri is not None:
            if (
                not isinstance(extraction_uri, Mapping)
                or set(extraction_uri) - {"download_url", "file_id", "file_name", "mime_type"}
                or _https(extraction_uri.get("download_url")) != extraction_uri.get("download_url")
                or not isinstance(extraction_uri.get("file_id"), str) or not extraction_uri["file_id"]
            ):
                raise ConnectedSourcesError("Gmail complete extraction file reference is malformed")
        original = self.fetch_https(download_url)
        data = original.data
        if original.mime_type != mime_type:
            raise ConnectedSourcesError("Gmail original download MIME type disagrees")
        if len(data) != declared_byte_size or len(data) > self.bounds.max_bytes:
            raise ConnectedSourcesError("Gmail attachment original bytes exceed or disagree with declared size")
        return AttachmentRead(
            attachment_id, mime_type, True, declared_byte_size, data, None,
            {
                "kind": "provider_attachment_download", "message_id": message_id,
                "attachment_id": attachment_id, "file_id": file_id,
                "requested_url": download_url, "final_url": original.url,
                "sha256": sha256_bytes(data), "size_bytes": len(data),
                "provider_preview_ignored": True, "provider_preview_truncated": truncated,
            },
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
        _reject_unsupported_pdf_features(reader, pages)
        render_plans = tuple(_pdf_render_scale(page, self.bounds) for page in pages)
        if sum(plan[1] for plan in render_plans) > self.bounds.max_pdf_rendered_pixels:
            raise ConnectedSourcesError("PDF pages exceed the aggregate pre-render pixel bound")
        digest = sha256_bytes(data)
        pdf_path = self.run_directory / f"pdf-{digest}.pdf"
        descriptor = os.open(pdf_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        texts: list[str] = []
        rendered_bytes = 0
        text_bytes = 0
        try:
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            if _contained_regular(pdf_path, self.run_directory).read_bytes() != data:
                raise ConnectedSourcesError("PDF file changed before rendering")
            for number, (scale, _planned_pixels) in enumerate(render_plans, start=1):
                prefix = self.run_directory / f"pdf-{digest}-page-{number}"
                image_path = prefix.with_suffix(".png")
                try:
                    subprocess.run(
                        [
                            "pdftoppm", "-f", str(number), "-l", str(number),
                            "-r", str(self.bounds.pdf_render_dpi), "-scale-to", str(scale),
                            "-cropbox", "-png", "-singlefile", str(pdf_path), str(prefix),
                        ],
                        check=True, timeout=max(1, self.bounds.timeout_ms / 1000),
                        capture_output=True,
                        preexec_fn=lambda: _limit_render_file(min(
                            self.bounds.max_bytes,
                            self.bounds.max_pdf_rendered_bytes - rendered_bytes,
                        )),
                    )
                    rendered = _contained_regular(image_path, self.run_directory).read_bytes()
                    rendered_bytes += len(rendered)
                    if len(rendered) > self.bounds.max_bytes or rendered_bytes > self.bounds.max_pdf_rendered_bytes:
                        raise ConnectedSourcesError("rendered PDF pages exceed the selected byte bound")
                    extracted = self.extract_image(
                        source_id=f"{source_id}:page:{number}", data=rendered, mime_type="image/png",
                    )
                    encoded_page = extracted.text.encode("utf-8", errors="strict")
                    separator_bytes = 3 if texts else 0
                    text_bytes += separator_bytes + len(encoded_page)
                    if text_bytes > self.bounds.max_pdf_text_bytes:
                        raise ConnectedSourcesError("PDF extracted text exceeds the aggregate selected bound")
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
    """Concrete HTTPS helper plus a two-step native ``view_image`` handoff.

    The handoff is intentionally explicit: the Codex host invokes only
    ``view_image(path=<copy>, detail="original")``, transcribes all visible
    content, and then calls :meth:`complete_image`.  The stable copy is checked
    both immediately before the handoff and immediately after the view.
    """

    run_directory: Path
    fetch_https_impl: Callable[[Mapping[str, Any]], Mapping[str, Any]] = field(default_factory=BoundedHttpsFetcher)
    max_image_pixels: int = 16_000_000
    max_image_dimension: int = 8_000
    max_bytes: int = _HOST_MAX_BYTES

    def __post_init__(self) -> None:
        if any(type(value) is not int or value < 1 for value in (
            self.max_image_pixels, self.max_image_dimension, self.max_bytes,
        )) or self.max_bytes > _HOST_MAX_BYTES:
            raise ConnectedSourcesError("source host image bounds are invalid")

    @property
    def view_directory(self) -> Path:
        root = self.run_directory.resolve(strict=True)
        directory = root / ".source-host-view"
        directory.mkdir(mode=0o700, exist_ok=True)
        status = directory.lstat()
        if directory.is_symlink() or not stat.S_ISDIR(status.st_mode):
            raise ConnectedSourcesError("source host view directory is not a real directory")
        resolved = directory.resolve(strict=True)
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise ConnectedSourcesError("source host view directory escapes the private run directory") from exc
        os.chmod(directory, 0o700)
        return resolved

    def dispatch(self, kind: str, args: Mapping[str, Any]) -> Mapping[str, Any]:
        _finite_host_arguments(kind, args)
        if kind == "resource.fetch_https":
            result = self.fetch_https_impl(dict(args))
            if not isinstance(result, Mapping):
                raise ConnectedSourcesError("HTTPS helper returned a non-object result")
            return dict(result)
        if kind == "extract.image":
            raise ConnectedSourcesError("image extraction requires the prepare/view/complete host loop")
        raise ConnectedSourcesError("unexpected finite source host helper kind")

    def prepare_image(self, args: Mapping[str, Any]) -> Mapping[str, Any]:
        _finite_host_arguments("extract.image", args)
        source = _contained_regular(Path(args["path"]), self.run_directory)
        if source.stat(follow_symlinks=False).st_size > self.max_bytes:
            raise ConnectedSourcesError("image source exceeds the finite host byte bound")
        data = source.read_bytes()
        mime_type = args["mime_type"]
        if args["original_sha256"] != sha256_bytes(data) or args["byte_length"] != len(data):
            raise ConnectedSourcesError("image host helper observed different original bytes")
        width, height = _image_details(
            data, mime_type, max_pixels=self.max_image_pixels,
            max_dimension=self.max_image_dimension,
        )
        if args["width"] != width or args["height"] != height:
            raise ConnectedSourcesError("image host helper observed different dimensions")
        suffix = ".png" if mime_type == "image/png" else ".jpg"
        copy_path = self.view_directory / f"{args['original_sha256']}-{uuid.uuid4().hex}{suffix}"
        descriptor = os.open(copy_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
        except Exception:
            copy_path.unlink(missing_ok=True)
            raise
        stable = _contained_regular(copy_path, self.view_directory)
        status = stable.stat(follow_symlinks=False)
        copied = stable.read_bytes()
        after_read = stable.stat(follow_symlinks=False)
        if copied != data or (status.st_dev, status.st_ino, status.st_size, status.st_mtime_ns) != (
            after_read.st_dev, after_read.st_ino, after_read.st_size, after_read.st_mtime_ns,
        ):
            stable.unlink(missing_ok=True)
            raise ConnectedSourcesError("host-owned image copy differs from the verified original")
        return {
            "native_tool": "view_image", "arguments": {"path": str(stable), "detail": "original"},
            "source": dict(args), "stable_copy": {
                "path": str(stable), "device": status.st_dev, "inode": status.st_ino,
                "size": status.st_size, "mtime_ns": status.st_mtime_ns,
                "sha256": sha256_bytes(data),
            },
        }

    def complete_image(self, handoff: Mapping[str, Any], text: str) -> Mapping[str, Any]:
        if not isinstance(handoff, Mapping) or set(handoff) != {"native_tool", "arguments", "source", "stable_copy"}:
            raise ConnectedSourcesError("image view handoff is malformed")
        arguments = handoff.get("arguments")
        if not isinstance(arguments, Mapping) or handoff.get("native_tool") != "view_image" or arguments.get("detail") != "original":
            raise ConnectedSourcesError("image view did not use original detail")
        source, stable_copy = handoff.get("source"), handoff.get("stable_copy")
        if not isinstance(source, Mapping) or not isinstance(stable_copy, Mapping):
            raise ConnectedSourcesError("image view handoff identity is malformed")
        _finite_host_arguments("extract.image", source)
        path = _contained_regular(Path(stable_copy.get("path", "")), self.view_directory)
        if arguments.get("path") != str(path):
            raise ConnectedSourcesError("image viewer path differs from the stable copy")
        status = path.stat(follow_symlinks=False)
        data = path.read_bytes()
        after_read = path.stat(follow_symlinks=False)
        expected_status = (
            stable_copy.get("device"), stable_copy.get("inode"), stable_copy.get("size"),
            stable_copy.get("mtime_ns"), stable_copy.get("sha256"),
        )
        actual_status = (status.st_dev, status.st_ino, status.st_size, status.st_mtime_ns, sha256_bytes(data))
        final_status = (after_read.st_dev, after_read.st_ino, after_read.st_size, after_read.st_mtime_ns, sha256_bytes(data))
        if actual_status != expected_status or final_status != expected_status or sha256_bytes(data) != source["original_sha256"]:
            raise ConnectedSourcesError("image bytes changed between verification and viewing")
        if not isinstance(text, str) or not text:
            raise ConnectedSourcesError("original-detail image view returned no visible text")
        return {
            "source_id": source["source_id"], "mime_type": source["mime_type"],
            "original_sha256": source["original_sha256"], "byte_length": source["byte_length"],
            "width": source["width"], "height": source["height"], "complete": True,
            "text": text,
        }

    def cleanup_image(self, handoff: Mapping[str, Any]) -> None:
        stable_copy = handoff.get("stable_copy") if isinstance(handoff, Mapping) else None
        if isinstance(stable_copy, Mapping) and isinstance(stable_copy.get("path"), str):
            try:
                path = _contained_regular(Path(stable_copy["path"]), self.view_directory)
            except ConnectedSourcesError:
                return
            path.unlink(missing_ok=True)
