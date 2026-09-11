"""Exact packet binding for independent semantic qualification notes.

Qualification notes are private reviewer evidence, not canonical School-OS
data.  A note must nevertheless identify the exact packet it was reviewed
against before it can drive a semantic interpreter or audit response.  This is
especially important for a zero-Fact decision, which otherwise has no source
span capable of exposing accidental reuse against another packet.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from typing import Any

from .contracts import canonical_json_bytes, sha256_bytes


class SemanticExpectationError(ValueError):
    """Raised when private expected-content evidence is not packet-bound."""


def _digest(value: Any) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def semantic_packet_binding(packet: Mapping[str, Any]) -> dict[str, Any]:
    """Return a privacy-safe exact identity for one semantic packet mapping."""
    required = {
        "schema_version", "record_id", "conversation_id",
        "catalog_record_sha256", "segments", "source_outcomes",
    }
    if not isinstance(packet, Mapping) or not required.issubset(packet):
        raise SemanticExpectationError("semantic expectation packet is malformed")
    segments = packet.get("segments")
    if not isinstance(segments, Sequence) or isinstance(segments, (str, bytes)) or not segments:
        raise SemanticExpectationError("semantic expectation packet lacks source segments")
    bound_segments: list[dict[str, Any]] = []
    seen: set[str] = set()
    for segment in segments:
        if not isinstance(segment, Mapping):
            raise SemanticExpectationError("semantic expectation segment is malformed")
        segment_id = segment.get("segment_id")
        content_id = segment.get("content_id")
        content_sha256 = segment.get("content_sha256")
        text = segment.get("text")
        if (
            not isinstance(segment_id, str) or not segment_id or segment_id in seen
            or not isinstance(content_id, str) or not content_id
            or not isinstance(content_sha256, str) or len(content_sha256) != 64
            or not isinstance(text, str)
            or sha256_bytes(text.encode("utf-8")) != content_sha256
        ):
            raise SemanticExpectationError("semantic expectation segment identity disagrees")
        bound_segments.append({
            "segment_id": segment_id,
            "content_id": content_id,
            "content_sha256": content_sha256,
            "utf8_byte_length": len(text.encode("utf-8")),
        })
        seen.add(segment_id)
    for key in ("record_id", "conversation_id", "catalog_record_sha256"):
        if not isinstance(packet.get(key), str) or not packet[key]:
            raise SemanticExpectationError("semantic expectation packet identity is incomplete")
    return {
        "packet_sha256": _digest(dict(packet)),
        "record_id": packet["record_id"],
        "conversation_id": packet["conversation_id"],
        "catalog_record_sha256": packet["catalog_record_sha256"],
        "segments": bound_segments,
        "source_outcomes_sha256": _digest(list(packet.get("source_outcomes", []))),
        "mime_accounting_sha256": _digest(list(packet.get("mime_accounting", []))),
        "evidence_segments_sha256": _digest(list(packet.get("evidence_segments", []))),
    }


def validate_semantic_expectation(
    packet: Mapping[str, Any], expectation: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate and return one exact packet-bound private expectation note."""
    if not isinstance(expectation, Mapping) or set(expectation) != {
        "schema_version", "binding", "candidates",
    }:
        raise SemanticExpectationError("semantic expectation note has an unsupported shape")
    if expectation.get("schema_version") != 1:
        raise SemanticExpectationError("semantic expectation note version is unsupported")
    binding = expectation.get("binding")
    if not isinstance(binding, Mapping) or dict(binding) != semantic_packet_binding(packet):
        raise SemanticExpectationError("semantic expectation identifies a different packet")
    candidates = expectation.get("candidates")
    if not isinstance(candidates, Sequence) or isinstance(candidates, (str, bytes)):
        raise SemanticExpectationError("semantic expectation candidates must be an array")
    return deepcopy(dict(expectation))
