"""Bounded, lossless import helpers for complete synthetic mail scopes."""

from __future__ import annotations

import base64
import binascii
import codecs
import quopri
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Any
from urllib.parse import urlparse

from .adapters import Page, ReadResult
from .contracts import sha256_bytes


class ImportError(ValueError):
    """Raised when a complete import scope cannot safely continue."""


@dataclass(frozen=True)
class Enumeration:
    """Complete scope evidence, including every page and duplicate disposition."""

    conversations: tuple[dict[str, Any], ...]
    page_tokens: tuple[str | None, ...]
    dispositions: tuple[dict[str, str], ...]


@dataclass(frozen=True)
class ImportBatch:
    """One bounded, stable subset and the exact work remaining after it."""

    conversations: tuple[dict[str, Any], ...]
    completed_ids: tuple[str, ...]
    remaining_ids: tuple[str, ...]
    byte_count: int


@dataclass(frozen=True)
class AttachmentOutcome:
    """Visible attachment result with distinct original/extracted evidence."""

    attachment_id: str
    outcome: str
    mime_type: str | None
    original_content_sha256: str | None
    extracted_text_sha256: str | None
    text: str | None
    locator: dict[str, Any] | None
    origin: str = "mime_attachment"


@dataclass(frozen=True)
class AttachmentExtraction:
    """Exact text and one source locator returned by a selected extractor."""

    text: str
    locator: Mapping[str, Any]


@dataclass(frozen=True)
class DirectHtmlResource:
    """One direct image/PDF reference found in a complete HTML MIME part."""

    resource_id: str
    origin: str
    url: str
    source_message_id: str
    html_part_id: str
    html_part_sha256: str
    occurrence: int
    attribute: str


@dataclass(frozen=True)
class DirectResourceRead:
    """One bounded direct-resource fetch returned by the selected adapter."""

    url: str
    redirect_chain: tuple[str, ...]
    data: bytes
    mime_type: str


@dataclass(frozen=True)
class DirectResourceOutcome:
    """Processing result retaining HTML and extraction provenance separately."""

    resource: DirectHtmlResource
    outcome: str
    original_content_sha256: str | None
    extracted_text_sha256: str | None
    text: str | None
    locator: dict[str, Any] | None


class _DirectResourceParser(HTMLParser):
    """Extract only direct image/PDF URL attributes; never render HTML text."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.references: list[tuple[str, str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value for key, value in attrs}
        if tag.lower() == "img" and isinstance(values.get("src"), str):
            self.references.append(("html_embedded", "src", values["src"]))
            return
        candidate = values.get("href") if tag.lower() == "a" else values.get("src") or values.get("data")
        declared_type = values.get("type")
        if isinstance(candidate, str) and (
            urlparse(candidate).path.lower().endswith(".pdf") or declared_type == "application/pdf"
        ):
            self.references.append(("html_linked", "href" if tag.lower() == "a" else "src", candidate))


@dataclass(frozen=True)
class SourceAdmission:
    """One fail-closed decision before a message can enter a source record."""

    outcome: str
    reason: str
    plaintext: bytes | None
    selected_part_id: str | None = None
    declared_charset: str | None = None
    content_transfer_encoding: str | None = None


def _conversation_id(value: Mapping[str, Any]) -> str:
    identity = value.get("conversation_id")
    if not isinstance(identity, str) or not identity:
        raise ImportError("enumerated conversation has no immutable conversation_id")
    return identity


def _decode_quoted_printable(data: bytes) -> bytes:
    """Decode quoted-printable only when every escape/soft break is explicit."""
    offset = 0
    while offset < len(data):
        if data[offset] != ord("="):
            offset += 1
            continue
        if offset + 1 >= len(data):
            raise ValueError("quoted-printable input ends with an incomplete escape")
        if data[offset + 1] == ord("\n"):
            offset += 2
            continue
        if (
            data[offset + 1] == ord("\r")
            and offset + 2 < len(data)
            and data[offset + 2] == ord("\n")
        ):
            offset += 3
            continue
        if offset + 2 >= len(data) or any(
            value not in b"0123456789abcdefABCDEF" for value in data[offset + 1:offset + 3]
        ):
            raise ValueError("quoted-printable input has an invalid escape")
        offset += 3
    return quopri.decodestring(data)


def _decode_transport(data: bytes, encoding: str) -> bytes:
    normalized = encoding.lower()
    if normalized in {"identity", "7bit", "8bit", "binary"}:
        return data
    if normalized == "quoted-printable":
        return _decode_quoted_printable(data)
    if normalized == "base64":
        try:
            return base64.b64decode(b"".join(data.split()), validate=True)
        except (ValueError, binascii.Error) as exc:
            raise ValueError("base64 input is invalid") from exc
    raise ValueError("content-transfer encoding is unsupported")


def _decode_declared_charset(data: bytes, charset: str) -> bytes:
    try:
        codec = codecs.lookup(charset)
    except LookupError as exc:
        raise ValueError("declared charset is unsupported") from exc
    try:
        return data.decode(codec.name, errors="strict").encode("utf-8", errors="strict")
    except UnicodeError as exc:
        raise ValueError("declared charset decoding is lossy or invalid") from exc


def _strict_html_part_bytes(html_part: Mapping[str, Any]) -> tuple[str, bytes]:
    part_id = html_part.get("part_id")
    if not isinstance(part_id, str) or not part_id:
        raise ImportError("HTML MIME part has no immutable part_id")
    if html_part.get("complete") is not True or html_part.get("mime_type") != "text/html":
        raise ImportError("HTML MIME part is incomplete or has the wrong MIME type")
    charset = html_part.get("charset")
    encoding = html_part.get("content_transfer_encoding")
    data = html_part.get("data")
    if not isinstance(charset, str) or not isinstance(encoding, str) or not isinstance(data, bytes):
        raise ImportError("HTML MIME part lacks strict decoding evidence")
    try:
        return part_id, _decode_declared_charset(_decode_transport(data, encoding), charset)
    except ValueError as exc:
        raise ImportError(f"HTML MIME part cannot be decoded strictly: {exc}") from exc


def _direct_https_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc) and not parsed.username and not parsed.password


def discover_direct_html_resources(
    source_message_id: str, html_part: Mapping[str, Any],
) -> tuple[DirectHtmlResource, ...]:
    """Inventory direct image/PDF resources without converting HTML to text."""
    if not source_message_id:
        raise ImportError("HTML resource source message identity is required")
    part_id, html_bytes = _strict_html_part_bytes(html_part)
    parser = _DirectResourceParser()
    try:
        parser.feed(html_bytes.decode("utf-8", errors="strict"))
        parser.close()
    except (UnicodeError, ValueError) as exc:
        raise ImportError("HTML resource discovery cannot parse a complete strict HTML part") from exc
    html_hash = sha256_bytes(html_bytes)
    resources: list[DirectHtmlResource] = []
    for occurrence, (origin, attribute, url) in enumerate(parser.references):
        if not _direct_https_url(url):
            raise ImportError("HTML resource URL is not a direct HTTPS URL")
        resource_id = "resource-" + sha256_bytes(
            f"{source_message_id}\0{part_id}\0{occurrence}\0{attribute}\0{url}".encode("utf-8")
        )
        resources.append(DirectHtmlResource(
            resource_id, origin, url, source_message_id, part_id, html_hash, occurrence, attribute,
        ))
    return tuple(resources)


def _expected_resource_mime(data: bytes) -> str | None:
    if data.startswith(b"%PDF-"):
        return "application/pdf"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    return None


def process_direct_html_resources(
    resources: Sequence[DirectHtmlResource], *,
    fetch_resource: Callable[[str], DirectResourceRead],
    extractors: Mapping[str, Callable[[DirectResourceRead], AttachmentExtraction]],
    max_bytes: int,
    max_redirects: int,
) -> tuple[DirectResourceOutcome, ...]:
    """Fetch only enumerated direct resources and require exact provenance."""
    if max_bytes < 1 or max_redirects < 0:
        raise ImportError("direct resource bounds are invalid")
    outcomes: list[DirectResourceOutcome] = []
    for resource in resources:
        try:
            read = fetch_resource(resource.url)
        except OSError:
            outcomes.append(DirectResourceOutcome(resource, "inaccessible", None, None, None, None))
            continue
        chain = tuple(read.redirect_chain)
        if (
            not isinstance(read.data, bytes)
            or not isinstance(read.mime_type, str)
            or not chain
            or chain[0] != resource.url
            or chain[-1] != read.url
            or len(chain) - 1 > max_redirects
            or any(not _direct_https_url(url) for url in chain)
            or len(read.data) > max_bytes
        ):
            outcomes.append(DirectResourceOutcome(resource, "manual_review", None, None, None, None))
            continue
        expected_mime = _expected_resource_mime(read.data)
        if expected_mime is None or read.mime_type != expected_mime:
            outcomes.append(DirectResourceOutcome(resource, "manual_review", None, None, None, None))
            continue
        extractor = extractors.get(read.mime_type)
        if extractor is None:
            outcomes.append(DirectResourceOutcome(resource, "manual_review", sha256_bytes(read.data), None, None, None))
            continue
        try:
            extracted = extractor(read)
            extracted_bytes = extracted.text.encode("utf-8", errors="strict")
        except (UnicodeError, ValueError, OSError):
            outcomes.append(DirectResourceOutcome(resource, "manual_review", sha256_bytes(read.data), None, None, None))
            continue
        locator = dict(extracted.locator)
        kind = locator.get("kind")
        if kind == "extracted_text_span":
            valid_locator = (
                isinstance(locator.get("byte_start"), int)
                and isinstance(locator.get("byte_end"), int)
                and 0 <= locator["byte_start"] < locator["byte_end"] <= len(extracted_bytes)
            )
        elif kind == "provider_page_region":
            valid_locator = (
                isinstance(locator.get("page"), int)
                and locator["page"] >= 1
                and isinstance(locator.get("region"), str)
                and bool(locator["region"])
            )
        else:
            valid_locator = False
        if not valid_locator:
            outcomes.append(DirectResourceOutcome(resource, "manual_review", sha256_bytes(read.data), None, None, None))
            continue
        outcomes.append(DirectResourceOutcome(
            resource,
            "extracted",
            sha256_bytes(read.data),
            sha256_bytes(extracted_bytes),
            extracted.text,
            locator,
        ))
    return tuple(outcomes)


def require_message_source_coverage(
    plaintext: bytes, resource_outcomes: Sequence[DirectResourceOutcome],
) -> None:
    """Reject cursor-ready coverage while any discovered direct resource is open."""
    unresolved = [outcome for outcome in resource_outcomes if outcome.outcome not in {"extracted", "excluded_by_policy"}]
    if unresolved:
        raise ImportError("direct HTML resource coverage remains unresolved")
    if not plaintext and resource_outcomes and not any(
        outcome.outcome == "extracted" for outcome in resource_outcomes
    ):
        raise ImportError("empty plaintext cannot establish source coverage without resource extraction")


def admit_exact_plaintext_representation(
    parts: Sequence[Mapping[str, Any]], *, mime_tree_complete: bool = True,
) -> SourceAdmission:
    """Strictly decode one provider-designated plaintext body for cataloguing.

    The caller is the selected mail adapter: it flattens a complete MIME tree,
    marks exactly one body part ``selected_plaintext``, and inventories
    attachments separately with ``role: attachment``. This helper performs no
    HTML conversion, whitespace normalization, or MIME-source persistence.
    ``admitted`` bytes are the canonical UTF-8 encoding of the adapter's exact
    decoded Unicode body; all other outcomes are ineligible for any downstream
    catalog, Fact, view, task, or cursor write.
    """
    if not mime_tree_complete:
        return SourceAdmission("manual_review", "MIME tree is incomplete", None)
    if not parts or any(not isinstance(part, Mapping) for part in parts):
        return SourceAdmission("manual_review", "MIME part metadata is malformed", None)
    selected = [part for part in parts if part.get("selected_plaintext") is True]
    if len(selected) != 1:
        reason = (
            "provider did not designate one complete plaintext body"
            if not selected
            else "multiple provider-designated plaintext bodies are ambiguous"
        )
        return SourceAdmission("unsupported", reason, None)
    part = selected[0]
    part_id = part.get("part_id")
    role = part.get("role")
    mime_type = part.get("mime_type")
    charset = part.get("charset")
    encoding = part.get("content_transfer_encoding")
    if not isinstance(part_id, str) or not part_id or role != "body":
        return SourceAdmission("manual_review", "selected MIME body metadata is malformed", None)
    if part.get("complete") is not True:
        return SourceAdmission("manual_review", "selected MIME body is incomplete", None, part_id)
    if mime_type != "text/plain":
        return SourceAdmission("unsupported", "selected body is not text/plain", None, part_id)
    if not isinstance(charset, str) or not charset:
        return SourceAdmission("manual_review", "selected body has no declared charset", None, part_id)
    if not isinstance(encoding, str) or not encoding:
        return SourceAdmission("manual_review", "selected body has no transfer encoding", None, part_id)
    data = part.get("data")
    if not isinstance(data, bytes):
        return SourceAdmission("manual_review", "selected body bytes are unavailable", None, part_id)
    other_plain_bodies = [
        candidate
        for candidate in parts
        if candidate is not part
        and candidate.get("role") == "body"
        and candidate.get("mime_type") == "text/plain"
    ]
    if other_plain_bodies:
        return SourceAdmission("unsupported", "multiple plausible plain-text bodies are ambiguous", None, part_id)
    if any(candidate.get("role") not in {"body", "attachment"} for candidate in parts):
        return SourceAdmission("manual_review", "MIME part role is malformed", None, part_id)
    try:
        plaintext = _decode_declared_charset(_decode_transport(data, encoding), charset)
    except ValueError as exc:
        return SourceAdmission("unsupported", str(exc), None, part_id, charset, encoding)
    return SourceAdmission(
        "admitted",
        "one complete provider-designated plaintext body decoded strictly",
        plaintext,
        part_id,
        charset,
        encoding,
    )


def enumerate_conversations(
    search: Callable[[str | None], Page], *, start_page_token: str | None = None
) -> Enumeration:
    """Read every page once and retain one deterministically ordered identity set."""
    token = start_page_token
    seen_tokens: set[str | None] = set()
    by_id: dict[str, dict[str, Any]] = {}
    tokens: list[str | None] = []
    dispositions: list[dict[str, str]] = []
    while True:
        if token in seen_tokens:
            raise ImportError("enumeration page token repeated before completion")
        seen_tokens.add(token)
        tokens.append(token)
        page = search(token)
        for item in page.items:
            copied = dict(item)
            identity = _conversation_id(copied)
            if identity in by_id:
                dispositions.append({"conversation_id": identity, "outcome": "duplicate"})
                continue
            by_id[identity] = copied
            dispositions.append({"conversation_id": identity, "outcome": "included"})
        if page.next_page_token is None:
            break
        token = page.next_page_token
    return Enumeration(
        tuple(by_id[identity] for identity in sorted(by_id)), tuple(tokens), tuple(dispositions)
    )


def next_import_batch(
    conversations: Sequence[Mapping[str, Any]], *, completed_ids: Sequence[str],
    max_records: int, max_bytes: int,
) -> ImportBatch:
    """Select the next whole records without truncation or cursor guesswork."""
    if max_records < 1 or max_bytes < 1:
        raise ImportError("import limits must be at least one record and one byte")
    completed = set(completed_ids)
    ordered = sorted((dict(item) for item in conversations), key=_conversation_id)
    ids = [_conversation_id(item) for item in ordered]
    if len(ids) != len(set(ids)):
        raise ImportError("import batch input has duplicate immutable conversation IDs")
    selected: list[dict[str, Any]] = []
    used_bytes = 0
    for item in ordered:
        identity = _conversation_id(item)
        if identity in completed:
            continue
        size = item.get("byte_size")
        if not isinstance(size, int) or size < 0:
            raise ImportError("import conversation is missing exact byte_size evidence")
        if size > max_bytes:
            raise ImportError("oversized single conversation cannot be truncated")
        if len(selected) == max_records or used_bytes + size > max_bytes:
            break
        selected.append(item)
        used_bytes += size
    selected_ids = {_conversation_id(item) for item in selected}
    new_completed = tuple(sorted(completed | selected_ids))
    remaining = tuple(identity for identity in ids if identity not in new_completed)
    return ImportBatch(tuple(selected), new_completed, remaining, used_bytes)


def process_attachments(
    attachments: Sequence[Mapping[str, Any]], *, read_attachment: Callable[[str], ReadResult],
    supported_mime_types: Sequence[str], max_bytes: int,
    extractors: Mapping[str, Callable[[ReadResult], AttachmentExtraction]] | None = None,
) -> tuple[AttachmentOutcome, ...]:
    """Process separately inventoried attachments with verifiable provenance."""
    if max_bytes < 1:
        raise ImportError("attachment byte limit must be positive")
    supported = set(supported_mime_types)
    selected_extractors = dict(extractors or {})
    outcomes: list[AttachmentOutcome] = []
    seen: set[str] = set()
    for attachment in attachments:
        attachment_id = attachment.get("attachment_id")
        mime_type = attachment.get("mime_type")
        byte_size = attachment.get("byte_size")
        if not isinstance(attachment_id, str) or not attachment_id:
            raise ImportError("attachment has no immutable attachment_id")
        if attachment_id in seen:
            outcomes.append(AttachmentOutcome(attachment_id, "duplicate", None, None, None, None, None))
            continue
        seen.add(attachment_id)
        if not isinstance(mime_type, str) or mime_type not in supported:
            outcomes.append(AttachmentOutcome(attachment_id, "unsupported", mime_type if isinstance(mime_type, str) else None, None, None, None, None))
            continue
        if not isinstance(byte_size, int) or byte_size < 0 or byte_size > max_bytes:
            outcomes.append(AttachmentOutcome(attachment_id, "manual_review", mime_type, None, None, None, None))
            continue
        try:
            result = read_attachment(attachment_id)
        except OSError:
            outcomes.append(AttachmentOutcome(attachment_id, "inaccessible", mime_type, None, None, None, None))
            continue
        if result.identity != attachment_id or result.mime_type != mime_type or len(result.data) != byte_size:
            outcomes.append(AttachmentOutcome(attachment_id, "inaccessible", mime_type, None, None, None, None))
            continue
        original_hash = sha256_bytes(result.data) if attachment.get("original_bytes_observed", True) is True else None
        if mime_type == "text/plain":
            try:
                text = result.data.decode("utf-8", errors="strict")
            except UnicodeDecodeError:
                outcomes.append(AttachmentOutcome(attachment_id, "unsupported", mime_type, original_hash, None, None, None))
                continue
            extracted = AttachmentExtraction(
                text,
                {"kind": "extracted_text_span", "byte_start": 0, "byte_end": len(result.data)},
            )
        else:
            extractor = selected_extractors.get(mime_type)
            if extractor is None:
                outcomes.append(AttachmentOutcome(attachment_id, "manual_review", mime_type, original_hash, None, None, None))
                continue
            try:
                extracted = extractor(result)
            except (UnicodeError, ValueError, OSError):
                outcomes.append(AttachmentOutcome(attachment_id, "manual_review", mime_type, original_hash, None, None, None))
                continue
        if not isinstance(extracted.text, str):
            outcomes.append(AttachmentOutcome(attachment_id, "manual_review", mime_type, original_hash, None, None, None))
            continue
        extracted_bytes = extracted.text.encode("utf-8", errors="strict")
        locator = dict(extracted.locator)
        kind = locator.get("kind")
        if kind == "extracted_text_span":
            start = locator.get("byte_start")
            end = locator.get("byte_end")
            valid_locator = isinstance(start, int) and isinstance(end, int) and 0 <= start < end <= len(extracted_bytes)
        elif kind == "provider_page_region":
            valid_locator = isinstance(locator.get("page"), int) and locator["page"] >= 1 and isinstance(locator.get("region"), str) and bool(locator["region"])
        else:
            valid_locator = False
        if not valid_locator:
            outcomes.append(AttachmentOutcome(attachment_id, "manual_review", mime_type, original_hash, None, None, None))
            continue
        outcomes.append(AttachmentOutcome(
            attachment_id,
            "extracted",
            mime_type,
            original_hash,
            sha256_bytes(extracted_bytes),
            extracted.text,
            locator,
        ))
    return tuple(outcomes)
