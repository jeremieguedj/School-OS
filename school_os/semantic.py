"""Narrow, source-bound semantic extraction and independent audit helpers."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from .contracts import canonical_json_bytes, sha256_bytes, validate


class SemanticError(ValueError):
    """Raised when semantic output is not traceable to the supplied packet."""


@dataclass(frozen=True)
class SemanticPacket:
    """Bounded source segments supplied to one live interpreter invocation."""

    record_id: str
    conversation_id: str
    segments: tuple[dict[str, Any], ...]

    def as_mapping(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "record_id": self.record_id,
            "conversation_id": self.conversation_id,
            "segments": [dict(segment) for segment in self.segments],
        }


def stable_fact_id(
    record_id: str, message_id: str, content_id: str, byte_start: int,
    byte_end: int, candidate_kind: str,
) -> str:
    """Assign a Fact identity from immutable provenance and an exact span."""
    if not all(isinstance(item, str) and item for item in (record_id, message_id, content_id, candidate_kind)):
        raise SemanticError("Fact identity components must be non-empty strings")
    if byte_start < 0 or byte_end <= byte_start:
        raise SemanticError("Fact span must be non-empty")
    material = "\0".join((record_id, message_id, content_id, str(byte_start), str(byte_end), candidate_kind))
    return "fact-" + sha256_bytes(material.encode("utf-8"))


def _validated(value: Any, schema: Mapping[str, Any], label: str) -> None:
    errors = validate(value, dict(schema))
    if errors:
        raise SemanticError(f"invalid {label}: " + "; ".join(errors))


def _segments_by_id(packet: SemanticPacket) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for segment in packet.segments:
        segment_id = segment.get("segment_id")
        text = segment.get("text")
        message_id = segment.get("source_message_id")
        content_id = segment.get("content_id")
        received_date = segment.get("received_date")
        if not all(isinstance(item, str) and item for item in (segment_id, text, message_id, content_id, received_date)):
            raise SemanticError("semantic packet segment lacks immutable identity or exact text")
        if segment_id in result:
            raise SemanticError("semantic packet has duplicate segment IDs")
        attachment = segment.get("attachment")
        if attachment is not None and not isinstance(attachment, Mapping):
            raise SemanticError("semantic packet attachment provenance is malformed")
        result[segment_id] = dict(segment)
    if not result:
        raise SemanticError("semantic packet has no source segments")
    return result


def _exact_span_text(segment: Mapping[str, Any], start: int, end: int) -> str:
    data = segment["text"].encode("utf-8")
    if start < 0 or end <= start or end > len(data):
        raise SemanticError("semantic candidate span is outside its source segment")
    try:
        return data[start:end].decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise SemanticError("semantic candidate splits a UTF-8 source character") from exc


def interpret_packet(
    packet: SemanticPacket,
    interpreter: Callable[[Mapping[str, Any]], Mapping[str, Any]],
    *, fact_schema: Mapping[str, Any], extraction_schema: Mapping[str, Any],
) -> dict[str, Any]:
    """Run one interpreter and mechanically bind its claims to exact segments.

    The interpreter receives source text but never supplies record IDs, source
    IDs, Fact IDs, attachment provenance, or serialized output. Candidate text
    must be the exact UTF-8 byte span the interpreter selected; rephrasing is
    rejected before any canonical Fact can be produced.
    """
    segments = _segments_by_id(packet)
    raw = interpreter(packet.as_mapping())
    if not isinstance(raw, Mapping):
        raise SemanticError("semantic interpreter did not return an object")
    candidates = raw.get("candidates")
    coverage = raw.get("coverage")
    review_cases = raw.get("review_cases", [])
    if not isinstance(candidates, Sequence) or isinstance(candidates, (str, bytes)):
        raise SemanticError("semantic interpreter candidates must be an array")
    if not isinstance(coverage, Sequence) or isinstance(coverage, (str, bytes)):
        raise SemanticError("semantic interpreter coverage must be an array")
    if not isinstance(review_cases, Sequence) or isinstance(review_cases, (str, bytes)):
        raise SemanticError("semantic interpreter review_cases must be an array")
    covered: set[str] = set()
    for entry in coverage:
        if not isinstance(entry, Mapping):
            raise SemanticError("semantic coverage entry is malformed")
        segment_id = entry.get("segment_id")
        outcome = entry.get("outcome")
        reason = entry.get("reason")
        if segment_id not in segments or outcome not in {"covered", "no_fact", "review"} or not isinstance(reason, str) or not reason:
            raise SemanticError("semantic coverage lacks a declared source-segment disposition")
        if segment_id in covered:
            raise SemanticError("semantic coverage has duplicate source-segment disposition")
        covered.add(segment_id)
    if covered != set(segments):
        raise SemanticError("semantic coverage does not account for every source segment")
    facts: list[dict[str, Any]] = []
    seen_fact_ids: set[str] = set()
    for candidate in candidates:
        if not isinstance(candidate, Mapping):
            raise SemanticError("semantic candidate is malformed")
        segment_id = candidate.get("segment_id")
        start = candidate.get("byte_start")
        end = candidate.get("byte_end")
        kind = candidate.get("candidate_kind")
        category = candidate.get("category")
        entity_scope = candidate.get("entity_scope")
        text = candidate.get("text")
        flags = candidate.get("flags")
        if not isinstance(segment_id, str) or segment_id not in segments:
            raise SemanticError("semantic candidate references an unknown source segment")
        if not isinstance(start, int) or not isinstance(end, int) or not isinstance(kind, str) or not kind:
            raise SemanticError("semantic candidate lacks an exact span or kind")
        if not isinstance(category, str) or not isinstance(entity_scope, str) or not isinstance(text, str) or not isinstance(flags, Mapping):
            raise SemanticError("semantic candidate lacks required classified content")
        segment = segments[segment_id]
        if text != _exact_span_text(segment, start, end):
            raise SemanticError("semantic candidate text is not its exact source span")
        fact = {
            "fact_id": stable_fact_id(packet.record_id, segment["source_message_id"], segment["content_id"], start, end, kind),
            "record_id": packet.record_id,
            "source_message_id": segment["source_message_id"],
            "source_byte_start": start,
            "source_byte_end": end,
            "received_date": segment["received_date"],
            "entity_scope": entity_scope,
            "category": category,
            "text": text,
            "flags": dict(flags),
        }
        if segment.get("attachment") is not None:
            fact["attachment"] = dict(segment["attachment"])
        _validated(fact, fact_schema, "semantic Fact")
        if fact["fact_id"] in seen_fact_ids:
            raise SemanticError("semantic candidates produce duplicate stable Fact IDs")
        seen_fact_ids.add(fact["fact_id"])
        facts.append(fact)
    if any(not isinstance(entry, Mapping) for entry in review_cases):
        raise SemanticError("semantic review case is malformed")
    result = {
        "schema_version": 1,
        "conversation_id": packet.conversation_id,
        "candidates": [dict(candidate) for candidate in candidates],
        "coverage": [dict(entry) for entry in coverage],
        "attachment_outcomes": [],
        "review_cases": [dict(entry) for entry in review_cases],
    }
    _validated(result, extraction_schema, "semantic extraction result")
    return {"facts": facts, "result": result, "packet_sha256": sha256_bytes(canonical_json_bytes(packet.as_mapping()))}


def validate_independent_audit(
    packet: SemanticPacket, interpreted: Mapping[str, Any], audit: Mapping[str, Any],
) -> None:
    """Require an independent source-segment disposition before acceptance."""
    segments = _segments_by_id(packet)
    if audit.get("packet_sha256") != interpreted.get("packet_sha256"):
        raise SemanticError("independent audit does not identify the interpreted source packet")
    entries = audit.get("segments")
    if not isinstance(entries, Sequence) or isinstance(entries, (str, bytes)):
        raise SemanticError("independent audit segments must be an array")
    seen: set[str] = set()
    for entry in entries:
        if not isinstance(entry, Mapping):
            raise SemanticError("independent audit entry is malformed")
        segment_id = entry.get("segment_id")
        disposition = entry.get("disposition")
        if segment_id not in segments or disposition not in {"accepted", "review", "blocked"}:
            raise SemanticError("independent audit lacks a valid source-segment disposition")
        if segment_id in seen:
            raise SemanticError("independent audit has duplicate segment disposition")
        seen.add(segment_id)
    if seen != set(segments):
        raise SemanticError("independent audit does not account for every source segment")
    if any(entry.get("disposition") != "accepted" for entry in entries):
        raise SemanticError("independent audit did not accept every source segment")
