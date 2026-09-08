"""Normalize observed Gmail full/raw reads into one strict source message.

The Gmail connector returns a provider-decoded ``payload`` in a full read and
an RFC2822 message encoded in ``raw``.  This adapter binds those two views
without making raw MIME a canonical artifact: raw leaf transport bytes prove
the selected adapter body, while the existing importer owns strict admission.
"""

from __future__ import annotations

import base64
import binascii
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from email import policy
from email.parser import BytesHeaderParser, BytesParser
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .contracts import sha256_bytes
from .importer import (
    ImportError,
    _decode_declared_charset,
    _decode_transport,
    admit_exact_plaintext_representation,
    discover_direct_html_resources,
)


class GmailSourceError(ValueError):
    """Raised when full and raw Gmail source evidence cannot be reconciled."""


_BASE64URL = re.compile(r"^[A-Za-z0-9_-]+$")
_BASE64URL_BODY = re.compile(r"^[A-Za-z0-9_-]+={0,2}$")


@dataclass(frozen=True)
class _HeaderEvidence:
    """The MIME fields exposed by both the full and raw Gmail reads."""

    mime_type: str
    charset: str | None
    transfer_encoding: str
    transfer_present: bool
    disposition: str | None
    disposition_present: bool
    filename: str | None
    content_type_present: bool


@dataclass(frozen=True)
class _RawNode:
    path: str
    mime_type: str
    multipart: bool
    headers: _HeaderEvidence
    data: bytes | None = None


def _string(value: Mapping[str, Any], key: str, label: str) -> str:
    result = value.get(key)
    if not isinstance(result, str) or not result:
        raise GmailSourceError(f"{label} lacks a nonempty {key}")
    return result


def _base64url(value: Any) -> bytes:
    if not isinstance(value, str) or not value or _BASE64URL.fullmatch(value) is None:
        raise GmailSourceError("Gmail raw RFC2822 payload is not strict base64url")
    try:
        return base64.b64decode(value + "=" * (-len(value) % 4), altchars=b"-_", validate=True)
    except (binascii.Error, ValueError) as exc:
        raise GmailSourceError("Gmail raw RFC2822 payload is not decodable") from exc


def _base64url_body(value: Any) -> bytes:
    """Decode one full-read body field, accepting only canonical URL-safe padding."""
    if not isinstance(value, str) or not value or _BASE64URL_BODY.fullmatch(value) is None:
        raise GmailSourceError("Gmail provider body is not strict base64url")
    unpadded = value.rstrip("=")
    padding = len(value) - len(unpadded)
    if len(unpadded) % 4 == 1 or (padding and len(value) % 4):
        raise GmailSourceError("Gmail provider body has invalid base64url padding")
    try:
        return base64.b64decode(unpadded + "=" * (-len(unpadded) % 4), altchars=b"-_", validate=True)
    except (binascii.Error, ValueError) as exc:
        raise GmailSourceError("Gmail provider body is not decodable") from exc


def _normalized_filename(value: Any, label: str) -> str | None:
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        raise GmailSourceError(f"{label} has a malformed filename")
    return value


def _header_evidence(message: Any, label: str) -> _HeaderEvidence:
    """Return only the technical MIME headers which must agree across views."""
    values: dict[str, list[str]] = {}
    for name in ("Content-Type", "Content-Transfer-Encoding", "Content-Disposition"):
        found = message.get_all(name, [])
        if not isinstance(found, list) or len(found) > 1 or any(not isinstance(item, str) for item in found):
            raise GmailSourceError(f"{label} has ambiguous {name} evidence")
        values[name] = found
    transfer_present = bool(values["Content-Transfer-Encoding"])
    transfer = values["Content-Transfer-Encoding"][0].strip().lower() if transfer_present else "7bit"
    if not transfer:
        raise GmailSourceError(f"{label} lacks a usable transfer encoding")
    return _HeaderEvidence(
        mime_type=message.get_content_type().lower(),
        charset=(message.get_content_charset() or None),
        transfer_encoding=transfer,
        transfer_present=transfer_present,
        disposition=message.get_content_disposition(),
        disposition_present=bool(values["Content-Disposition"]),
        filename=_normalized_filename(message.get_filename(), label),
        content_type_present=bool(values["Content-Type"]),
    )


def _full_header_evidence(value: Mapping[str, Any], label: str) -> _HeaderEvidence:
    headers = value.get("headers")
    if not isinstance(headers, list):
        raise GmailSourceError(f"{label} has no complete header inventory")
    relevant: list[bytes] = []
    for header in headers:
        if (
            not isinstance(header, Mapping)
            or not isinstance(header.get("name"), str) or not header["name"]
            or not isinstance(header.get("value"), str)
        ):
            raise GmailSourceError(f"{label} has a malformed header")
        if header["name"].lower() in {
            "content-type", "content-transfer-encoding", "content-disposition",
        }:
            if "\r" in header["value"] or "\n" in header["value"]:
                raise GmailSourceError(f"{label} has an unsafe MIME header value")
            try:
                relevant.append(f'{header["name"]}: {header["value"]}\r\n'.encode("ascii"))
            except UnicodeEncodeError as exc:
                raise GmailSourceError(f"{label} has non-ASCII MIME header evidence") from exc
    try:
        parsed = BytesHeaderParser(policy=policy.compat32).parsebytes(b"".join(relevant) + b"\r\n")
    except (TypeError, ValueError) as exc:
        raise GmailSourceError(f"{label} MIME headers cannot be parsed") from exc
    if parsed.defects:
        raise GmailSourceError(f"{label} MIME headers are incomplete or malformed")
    return _header_evidence(parsed, label)


def _raw_nodes(raw: bytes) -> dict[str, _RawNode]:
    """Read the complete MIME tree and exact encoded transport payloads."""
    try:
        root = BytesParser(policy=policy.compat32).parsebytes(raw)
    except (TypeError, ValueError) as exc:
        raise GmailSourceError("Gmail raw RFC2822 payload cannot be parsed") from exc
    nodes: dict[str, _RawNode] = {}

    def walk(message: Any, path: str) -> None:
        if message.defects:
            raise GmailSourceError("Gmail raw MIME has parser defects or incomplete boundaries")
        if path in nodes:
            raise GmailSourceError("Gmail raw MIME node path is ambiguous")
        payload = message.get_payload()
        evidence = _header_evidence(message, "Gmail raw MIME part")
        if message.is_multipart():
            if not isinstance(payload, list) or not payload:
                raise GmailSourceError("Gmail raw MIME multipart has incomplete member inventory")
            nodes[path] = _RawNode(path, evidence.mime_type, True, evidence)
            for index, child in enumerate(payload):
                walk(child, f"{path}.{index}" if path else str(index))
            return
        if isinstance(payload, list) or not isinstance(payload, str):
            raise GmailSourceError("Gmail raw MIME leaf has no exact transport payload")
        try:
            encoded = payload.encode("ascii", errors="surrogateescape")
        except UnicodeEncodeError as exc:
            raise GmailSourceError("Gmail raw MIME leaf cannot preserve transport bytes") from exc
        nodes[path] = _RawNode(path, evidence.mime_type, False, evidence, encoded)

    walk(root, "")
    if not any(not node.multipart for node in nodes.values()):
        raise GmailSourceError("Gmail raw MIME payload has no leaves")
    return nodes


def _full_nodes(payload: Mapping[str, Any]) -> dict[str, tuple[Mapping[str, Any], bool, _HeaderEvidence]]:
    """Flatten every full MIME node, retaining Gmail's exact part identifiers."""
    nodes: dict[str, tuple[Mapping[str, Any], bool, _HeaderEvidence]] = {}

    def walk(part: Mapping[str, Any], expected_path: str) -> None:
        part_id = part.get("part_id")
        if not isinstance(part_id, str):
            raise GmailSourceError("Gmail full MIME part lacks a string part_id")
        if part_id != expected_path:
            raise GmailSourceError("Gmail full MIME part_id disagrees with complete raw MIME ordering")
        mime_type = _string(part, "mime_type", "Gmail full MIME part").lower()
        headers = _full_header_evidence(part, "Gmail full MIME part")
        if headers.mime_type != mime_type:
            raise GmailSourceError("Gmail full MIME type disagrees with its Content-Type header")
        filename = _normalized_filename(part.get("filename"), "Gmail full MIME part")
        if filename != headers.filename:
            raise GmailSourceError("Gmail full MIME filename disagrees with its Content-Disposition header")
        children = part.get("parts")
        if expected_path in nodes:
            raise GmailSourceError("Gmail full MIME node path is ambiguous")
        if children is not None:
            if not isinstance(children, list) or not children:
                raise GmailSourceError("Gmail full MIME multipart has incomplete member inventory")
            nodes[expected_path] = (part, True, headers)
            for index, child in enumerate(children):
                if not isinstance(child, Mapping):
                    raise GmailSourceError("Gmail full MIME multipart member is malformed")
                walk(child, f"{expected_path}.{index}" if expected_path else str(index))
            return
        body = part.get("body")
        if not isinstance(body, Mapping):
            raise GmailSourceError("Gmail full MIME leaf has no body inventory")
        size = body.get("size")
        if isinstance(size, bool) or not isinstance(size, int) or size < 0:
            raise GmailSourceError("Gmail full MIME leaf has invalid declared byte size")
        nodes[expected_path] = (part, False, headers)

    walk(payload, "")
    if not any(not multipart for _, multipart, _ in nodes.values()):
        raise GmailSourceError("Gmail full MIME payload has no leaves")
    return nodes


def _attachment(part: Mapping[str, Any], raw: _RawNode) -> bool:
    body = part["body"]
    attachment_id = body.get("attachment_id")
    filename = part.get("filename")
    if attachment_id is not None and (not isinstance(attachment_id, str) or not attachment_id):
        raise GmailSourceError("Gmail MIME attachment identity is malformed")
    _normalized_filename(filename, "Gmail MIME part")
    # Every non-text leaf is a separately visible attachment, including an
    # inline image with no filename.  Otherwise its source bytes could vanish
    # from the source inventory before attachment processing gets a chance to
    # make an explicit disposition.
    return (
        raw.mime_type not in {"text/plain", "text/html"}
        or bool(attachment_id)
        or bool(filename)
        or raw.headers.disposition == "attachment"
    )


def _decoded_leaf_bytes(part: Mapping[str, Any], raw: _RawNode) -> bytes:
    if raw.data is None:
        raise GmailSourceError("Gmail raw MIME leaf has no exact transport payload")
    try:
        decoded = _decode_transport(raw.data, raw.headers.transfer_encoding)
    except ValueError as exc:
        raise GmailSourceError(f"Gmail raw MIME leaf transport is invalid: {exc}") from exc
    body = part["body"]
    if len(decoded) != body["size"]:
        raise GmailSourceError("Gmail MIME decoded byte size disagrees with declared size")
    encoded = body.get("base64_url_content")
    if encoded is not None and _base64url_body(encoded) != decoded:
        raise GmailSourceError("Gmail MIME provider encoded body disagrees with raw MIME bytes")
    return decoded


def _provider_unicode(part: Mapping[str, Any], raw: _RawNode, decoded: bytes) -> str:
    body = part["body"]
    content = body.get("content")
    if not isinstance(content, str):
        raise GmailSourceError("Gmail text MIME leaf lacks provider-decoded Unicode content")
    if body.get("base64_url_content") is not None:
        raise GmailSourceError("Gmail text MIME leaf has competing encoded and decoded content")
    if raw.headers.charset is None or not raw.headers.charset:
        raise GmailSourceError("Gmail text MIME leaf has no declared raw charset")
    try:
        exact_unicode = _decode_declared_charset(decoded, raw.headers.charset).decode("utf-8", errors="strict")
    except ValueError as exc:
        raise GmailSourceError(f"Gmail text MIME leaf charset is invalid: {exc}") from exc
    if content != exact_unicode:
        raise GmailSourceError("Gmail text MIME provider content disagrees with decoded raw MIME bytes")
    return content


def _headers_agree(full: _HeaderEvidence, raw: _HeaderEvidence) -> bool:
    """Compare the technical header evidence, not merely a MIME-type label."""
    return (
        full.mime_type == raw.mime_type
        and full.charset == raw.charset
        and full.transfer_encoding == raw.transfer_encoding
        and full.transfer_present == raw.transfer_present
        and full.disposition == raw.disposition
        and full.disposition_present == raw.disposition_present
        and full.filename == raw.filename
        and full.content_type_present == raw.content_type_present
    )


def _timestamp(value: Mapping[str, Any], timezone: ZoneInfo) -> tuple[str, str]:
    raw = _string(value, "internal_date", "Gmail full message")
    # Gmail's observed ``internal_date`` is its decimal epoch-milliseconds API
    # field.  Requiring exactly 13 digits prevents silently treating seconds as
    # milliseconds (or vice versa).
    if len(raw) != 13 or not raw.isascii() or not raw.isdecimal():
        raise GmailSourceError("Gmail internal_date is not exact epoch milliseconds")
    try:
        instant = datetime.fromtimestamp(int(raw) / 1000, tz=UTC)
    except (OverflowError, OSError, ValueError) as exc:
        raise GmailSourceError("Gmail internal_date is outside the supported timestamp range") from exc
    return instant.strftime("%Y-%m-%dT%H:%M:%SZ"), instant.astimezone(timezone).date().isoformat()


class GmailMimeNormalizer:
    """Concrete full/raw normalizer for the observed Gmail connector shape."""

    def __init__(self, timezone: str) -> None:
        try:
            self.timezone = ZoneInfo(timezone)
        except (TypeError, ZoneInfoNotFoundError) as exc:
            raise GmailSourceError("configured source timezone is unavailable") from exc

    def normalize(self, full: Mapping[str, Any], raw: Mapping[str, Any]) -> dict[str, Any]:
        """Return one complete source-port message or fail before cataloguing.

        The returned ``parts`` use raw transport bytes and custody hashes.  The
        existing importer redoes strict transport/charset decoding while
        admitting the one selected plaintext body.  HTML alternatives remain
        independent exact parts for bounded resource discovery.
        """
        message_id = _string(full, "id", "Gmail full message")
        thread_id = _string(full, "thread_id", "Gmail full message")
        if _string(raw, "id", "Gmail raw message") != message_id or _string(raw, "thread_id", "Gmail raw message") != thread_id:
            raise GmailSourceError("Gmail full/raw message or thread identity disagrees")
        received_at, received_date = _timestamp(full, self.timezone)
        payload = full.get("payload")
        if not isinstance(payload, Mapping):
            raise GmailSourceError("Gmail full message lacks a complete MIME payload")
        full_nodes = _full_nodes(payload)
        raw_nodes = _raw_nodes(_base64url(raw.get("raw")))
        if set(full_nodes) != set(raw_nodes):
            raise GmailSourceError("Gmail full/raw MIME node inventories disagree")
        for path, (full_part, full_multipart, full_headers) in full_nodes.items():
            raw_node = raw_nodes[path]
            if full_multipart != raw_node.multipart or full_headers.mime_type != raw_node.mime_type:
                raise GmailSourceError("Gmail full/raw MIME node structure or type disagrees")
            if not _headers_agree(full_headers, raw_node.headers):
                raise GmailSourceError("Gmail full/raw MIME technical headers disagree")
        full_leaves = {
            path: part for path, (part, multipart, _) in full_nodes.items() if not multipart
        }
        raw_leaves = {path: node for path, node in raw_nodes.items() if not node.multipart}

        parts: list[dict[str, Any]] = []
        html_parts: list[dict[str, Any]] = []
        attachments: list[dict[str, Any]] = []
        text_candidates: list[dict[str, Any]] = []
        for ordinal, path in enumerate(sorted(full_leaves, key=lambda item: tuple(int(x) for x in item.split(".")) if item else ())):
            part = full_leaves[path]
            raw_leaf = raw_leaves[path]
            mime_type = _string(part, "mime_type", "Gmail full MIME leaf").lower()
            if mime_type != raw_leaf.mime_type:
                raise GmailSourceError("Gmail full/raw MIME type disagrees")
            is_attachment = _attachment(part, raw_leaf)
            role = "attachment" if is_attachment else "body"
            body = part["body"]
            decoded = _decoded_leaf_bytes(part, raw_leaf)
            if is_attachment and body.get("content") is not None:
                raise GmailSourceError("Gmail attachment has unbound provider Unicode content")
            provider_part_id = part.get("part_id")
            if not isinstance(provider_part_id, str):
                raise GmailSourceError("Gmail full MIME leaf lacks a string part_id")
            # Gmail represents a non-multipart root leaf with an empty part ID.
            # ``root`` is the fixed normalized identifier for that one observed
            # structural case; retain the provider value alongside it rather
            # than fabricating an attachment or using a filename as identity.
            part_id = provider_part_id or "root"
            item = {
                "part_id": part_id,
                "provider_part_id": provider_part_id,
                "role": role,
                "selected_plaintext": False,
                "complete": True,
                "mime_type": mime_type,
                "charset": raw_leaf.headers.charset or "binary",
                "content_transfer_encoding": raw_leaf.headers.transfer_encoding,
                "data": raw_leaf.data,
                "raw_part_sha256": sha256_bytes(raw_leaf.data),
                "raw_part_byte_length": len(raw_leaf.data),
                "raw_part_locator": {"kind": "raw_part_bytes", "byte_start": 0, "byte_end": len(raw_leaf.data)},
                "source_part_ordinal": ordinal,
            }
            if mime_type in {"text/plain", "text/html"} and not is_attachment:
                item["provider_unicode"] = _provider_unicode(part, raw_leaf, decoded)
            if mime_type == "text/plain" and not is_attachment:
                text_candidates.append(item)
            if mime_type == "text/html" and not is_attachment:
                html = dict(item)
                # The existing direct-resource helper validates exact strict
                # decoding and does not render or convert HTML to text.
                try:
                    discover_direct_html_resources(message_id, html)
                except ImportError as exc:
                    raise GmailSourceError(f"Gmail HTML alternative is not exact: {exc}") from exc
                html_parts.append(html)
            if is_attachment:
                attachment_id = body.get("attachment_id")
                if not isinstance(attachment_id, str) or not attachment_id:
                    raise GmailSourceError("Gmail attachment has no provider attachment_id")
                supported = part.get("read_attachment_supported")
                if not isinstance(supported, bool):
                    raise GmailSourceError("Gmail attachment lacks read_attachment_supported evidence")
                attachments.append({
                    "attachment_id": attachment_id,
                    "mime_type": mime_type,
                    "byte_size": body["size"],
                    "filename": part.get("filename"),
                    "read_attachment_supported": supported,
                    "part_id": part_id,
                    "source_part_ordinal": ordinal,
                })
            parts.append(item)
        if len(text_candidates) != 1:
            raise GmailSourceError("Gmail MIME has no unique provider-designated plaintext alternative")
        text_candidates[0]["selected_plaintext"] = True
        try:
            admission = admit_exact_plaintext_representation(parts, mime_tree_complete=True)
        except ImportError as exc:
            raise GmailSourceError(f"Gmail plaintext admission failed: {exc}") from exc
        if admission.outcome != "admitted" or admission.plaintext is None:
            raise GmailSourceError(f"Gmail plaintext admission failed: {admission.reason}")
        return {
            "message_id": message_id,
            "thread_id": thread_id,
            "received_at": received_at,
            "received_date": received_date,
            "mime_tree_complete": True,
            "parts": parts,
            "html_parts": html_parts,
            "attachments": attachments,
        }

    def normalize_thread(
        self, thread: Mapping[str, Any], raw_by_message_id: Mapping[str, Mapping[str, Any]],
    ) -> dict[str, Any]:
        """Normalize all ordered full-thread members with their exact raw reads.

        The caller supplies raw responses keyed only by the thread's declared
        message IDs.  Extra, missing, duplicate, or cross-thread members block;
        the returned order becomes the source-message ordinal used upstream.
        """
        conversation_id = _string(thread, "id", "Gmail full thread")
        members = thread.get("messages")
        if not isinstance(members, list) or not members:
            raise GmailSourceError("Gmail full thread lacks complete ordered members")
        normalized: list[dict[str, Any]] = []
        seen: set[str] = set()
        for ordinal, member in enumerate(members):
            if not isinstance(member, Mapping):
                raise GmailSourceError("Gmail full thread member is malformed")
            message_id = _string(member, "id", "Gmail full thread member")
            if _string(member, "thread_id", "Gmail full thread member") != conversation_id or message_id in seen:
                raise GmailSourceError("Gmail full thread member identity is ambiguous")
            raw = raw_by_message_id.get(message_id)
            if not isinstance(raw, Mapping):
                raise GmailSourceError("Gmail full thread member has no exact raw read")
            item = self.normalize(member, raw)
            item["source_message_ordinal"] = ordinal
            normalized.append(item)
            seen.add(message_id)
        if set(raw_by_message_id) != seen:
            raise GmailSourceError("Gmail raw reads do not match the complete thread membership")
        return {"conversation_id": conversation_id, "messages": normalized}
