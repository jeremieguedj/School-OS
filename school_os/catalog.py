"""Lossless version-2 source-catalog framing and verification helpers."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from .contracts import canonical_json_bytes, sha256_bytes, validate


class CatalogError(ValueError):
    """Raised when a source conversation or catalog record is unsafe."""


RECORD_PREFIX = b"# School-OS source catalog record v2\n"
RECORD_MARKER = b"<!-- school-os-record "
MESSAGE_MARKER = b"<!-- school-os-message "
MARKER_END = b" -->\n"


@dataclass(frozen=True)
class CatalogRecord:
    """Parsed immutable record header and ordered exact source bodies."""

    header: dict[str, Any]
    bodies: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class CatalogRecovery:
    """A verified index candidate for a record persisted before its index write."""

    index: dict[str, Any]
    record_id: str
    adopted: bool


def stable_record_id(adapter_id: str, conversation_id: str) -> str:
    """Derive a record identity only from immutable adapter/conversation IDs."""
    if not adapter_id or not conversation_id:
        raise CatalogError("adapter_id and conversation_id must be non-empty")
    return "record-" + sha256_bytes(f"{adapter_id}\0{conversation_id}".encode("utf-8"))


def _canonical_inline(value: Mapping[str, Any]) -> bytes:
    return canonical_json_bytes(dict(value)).rstrip(b"\n")


def _read_marker(data: bytes, offset: int, prefix: bytes, label: str) -> tuple[dict[str, Any], int]:
    if not data.startswith(prefix, offset):
        raise CatalogError(f"expected {label} marker at byte {offset}")
    start = offset + len(prefix)
    end = data.find(MARKER_END, start)
    if end < 0:
        raise CatalogError(f"unterminated {label} marker")
    try:
        value = json.loads(data[start:end].decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CatalogError(f"invalid {label} marker JSON") from exc
    if not isinstance(value, dict):
        raise CatalogError(f"{label} marker must be an object")
    return value, end + len(MARKER_END)


def validate_source_conversation(conversation: Mapping[str, Any], schema: Mapping[str, Any]) -> None:
    """Validate a complete adapter-returned conversation before serialization."""
    errors = validate(conversation, dict(schema))
    if errors:
        raise CatalogError("invalid source conversation: " + "; ".join(errors))
    message_ids = [message["message_id"] for message in conversation["messages"]]
    if len(message_ids) != len(set(message_ids)):
        raise CatalogError("source conversation has duplicate immutable message_id values")


def serialize_v2_record(conversation: Mapping[str, Any], schema: Mapping[str, Any]) -> bytes:
    """Mechanically frame every complete UTF-8 body using its exact byte count."""
    validate_source_conversation(conversation, schema)
    messages = conversation["messages"]
    header = {
        "adapter_id": conversation["adapter_id"],
        "conversation_id": conversation["conversation_id"],
        "format_version": 2,
        "pagination": conversation["pagination"],
        "record_id": stable_record_id(conversation["adapter_id"], conversation["conversation_id"]),
        "scope": conversation["scope"],
        "messages": [
            {"message_id": message["message_id"], "received_at": message["received_at"], "attachments": message["attachments"]}
            for message in messages
        ],
    }
    result = bytearray(RECORD_PREFIX + RECORD_MARKER + _canonical_inline(header) + MARKER_END)
    for message in messages:
        body = message["body"].encode("utf-8")
        descriptor = {"byte_length": len(body), "message_id": message["message_id"]}
        result.extend(MESSAGE_MARKER + _canonical_inline(descriptor) + MARKER_END)
        result.extend(body)
    return bytes(result)


def parse_v2_record(data: bytes) -> CatalogRecord:
    """Parse byte-counted frames without interpreting body headings or delimiters."""
    if not data.startswith(RECORD_PREFIX):
        raise CatalogError("record is not a v2 source catalog record")
    header, offset = _read_marker(data, len(RECORD_PREFIX), RECORD_MARKER, "record")
    if header.get("format_version") != 2 or not isinstance(header.get("messages"), list):
        raise CatalogError("record header is not a complete v2 catalog header")
    bodies: list[tuple[str, str]] = []
    for expected in header["messages"]:
        if not isinstance(expected, dict) or not isinstance(expected.get("message_id"), str):
            raise CatalogError("record header has invalid ordered message metadata")
        descriptor, offset = _read_marker(data, offset, MESSAGE_MARKER, "message")
        message_id = descriptor.get("message_id")
        length = descriptor.get("byte_length")
        if message_id != expected["message_id"] or not isinstance(length, int) or length < 0:
            raise CatalogError("message frame does not match ordered header metadata")
        body = data[offset:offset + length]
        if len(body) != length:
            raise CatalogError("message frame is shorter than its declared UTF-8 byte length")
        try:
            bodies.append((message_id, body.decode("utf-8")))
        except UnicodeDecodeError as exc:
            raise CatalogError("message body is not UTF-8") from exc
        offset += length
    if offset != len(data):
        raise CatalogError("record has trailing bytes outside declared message frames")
    return CatalogRecord(header, tuple(bodies))


def validate_source_to_record(data: bytes, source_bodies: Mapping[str, str]) -> list[str]:
    """Prove exact ordered adapter bodies against a parsed v2 record."""
    try:
        parsed = parse_v2_record(data)
    except CatalogError as exc:
        return [str(exc)]
    catalogued = dict(parsed.bodies)
    errors: list[str] = []
    if list(message_id for message_id, _body in parsed.bodies) != list(source_bodies):
        errors.append("ordered message IDs differ")
    for message_id, body in source_bodies.items():
        if message_id not in catalogued:
            errors.append(f"message {message_id!r} is missing from the raw-message section")
        elif catalogued[message_id] != body:
            errors.append(f"message {message_id!r} body is not verbatim")
    return errors


def verify_persisted_record(source_bodies: Mapping[str, str], intended: bytes, persisted: bytes) -> None:
    """Require independent source equality and intended-byte readback equality."""
    errors = validate_source_to_record(intended, source_bodies)
    if errors:
        raise CatalogError("source-to-record verification failed: " + "; ".join(errors))
    if persisted != intended:
        raise CatalogError("intended-to-persisted byte verification failed")


def recover_catalog_index(
    source_bodies: Mapping[str, str], intended: bytes, persisted: bytes,
    index: Mapping[str, Any], facts: list[Mapping[str, Any]],
) -> CatalogRecovery:
    """Adopt one verified orphaned record without inventing index rows or Fact IDs.

    The caller owns guarded storage writes. This pure recovery step first proves
    both source equality and readback bytes, then returns either an idempotent
    existing index or a candidate with exactly one new row.
    """
    verify_persisted_record(source_bodies, intended, persisted)
    record = parse_v2_record(persisted)
    record_id = record.header.get("record_id")
    if not isinstance(record_id, str) or not record_id:
        raise CatalogError("persisted record has no immutable record_id")
    fact_ids: list[str] = []
    for fact in facts:
        if fact.get("record_id") != record_id:
            raise CatalogError("recovery Fact does not link to the persisted record")
        fact_id = fact.get("fact_id")
        if not isinstance(fact_id, str) or not fact_id:
            raise CatalogError("recovery Fact has no stable fact_id")
        fact_ids.append(fact_id)
    if len(fact_ids) != len(set(fact_ids)):
        raise CatalogError("recovery Facts contain duplicate stable fact_id values")
    existing_rows = index.get("records", [])
    if not isinstance(existing_rows, list) or any(not isinstance(row, Mapping) for row in existing_rows):
        raise CatalogError("catalog index records must be an array of objects")
    rows = [dict(row) for row in existing_rows]
    matches = [row for row in rows if row.get("record_id") == record_id]
    if len(matches) > 1:
        raise CatalogError("catalog index has duplicate rows for one record")
    entry = {"record_id": record_id, "record_sha256": sha256_bytes(persisted), "fact_ids": fact_ids}
    if matches:
        if matches[0] != entry:
            raise CatalogError("existing catalog index row disagrees with verified record or Fact IDs")
        return CatalogRecovery({"schema_version": 1, "records": rows}, record_id, True)
    rows.append(entry)
    rows.sort(key=lambda row: row["record_id"])
    return CatalogRecovery({"schema_version": 1, "records": rows}, record_id, True)
