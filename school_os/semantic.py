"""Bounded semantic extraction from verified catalog content and exact audits."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from .catalog import parse_v2_record, verified_catalog_contents, verify_persisted_record
from .contracts import canonical_json_bytes, sha256_bytes, validate


class SemanticError(ValueError):
    """Raised when semantic output is not traceable to verified source content."""


@dataclass(frozen=True)
class SemanticPacket:
    """Bounded source segments supplied to one live interpreter invocation."""

    record_id: str
    conversation_id: str
    catalog_record_sha256: str
    segments: tuple[dict[str, Any], ...]
    source_outcomes: tuple[dict[str, Any], ...] = ()
    mime_accounting: tuple[dict[str, Any], ...] = ()
    evidence_segments: tuple[dict[str, Any], ...] = ()

    def as_mapping(self) -> dict[str, Any]:
        result = {
            "schema_version": 2 if self.mime_accounting else 1,
            "record_id": self.record_id,
            "conversation_id": self.conversation_id,
            "catalog_record_sha256": self.catalog_record_sha256,
            "segments": deepcopy(self.segments),
            "source_outcomes": deepcopy(self.source_outcomes),
        }
        if self.mime_accounting:
            result["mime_accounting"] = deepcopy(self.mime_accounting)
            result["evidence_segments"] = deepcopy(self.evidence_segments)
        return result


def stable_fact_id(
    record_id: str, message_id: str, content_id: str, byte_start: int,
    byte_end: int, candidate_kind: str,
) -> str:
    """Assign a Fact identity from immutable provenance and an exact source span."""
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


def semantic_packet_from_verified_record(
    persisted: bytes, source_bodies: Mapping[str, str], *, max_segments: int,
    max_bytes: int,
) -> SemanticPacket:
    """Build one packet only from exact persisted, source-equal catalog frames."""
    if max_segments < 1 or max_bytes < 1:
        raise SemanticError("semantic packet bounds must be positive")
    verify_persisted_record(source_bodies, persisted, persisted)
    record = parse_v2_record(persisted)
    entries = verified_catalog_contents(record)
    if len(entries) > max_segments:
        raise SemanticError("verified catalog content exceeds the semantic segment bound")
    total = sum(len(entry["text"].encode("utf-8")) for entry in entries)
    if total > max_bytes:
        raise SemanticError("verified catalog content exceeds the semantic byte bound")
    segments: list[dict[str, Any]] = []
    evidence_segments: list[dict[str, Any]] = []
    for entry in entries:
        segment_id = "segment-" + sha256_bytes(
            f"{record.header['record_id']}\0{entry['content_id']}".encode("utf-8")
        )
        segment = {
            "segment_id": segment_id,
            "content_id": entry["content_id"],
            "content_kind": entry["content_kind"],
            "content_sha256": entry["sha256"],
            "source_message_id": entry["source_message_id"],
            "source_received_at": entry["received_at"],
            "received_date": entry["received_date"],
            "source_message_ordinal": entry["message_ordinal"],
            "source_content_ordinal": entry["content_ordinal"],
            "text": entry["text"],
        }
        if entry["content_kind"] != "body" or record.header.get("custody_version") == 2:
            segment["source_provenance"] = deepcopy(entry["provenance"])
        if entry["content_kind"] == "html_evidence":
            evidence_segments.append(segment)
        else:
            segments.append(segment)
    source_outcomes: list[dict[str, Any]] = []
    for message in record.header["messages"]:
        for kind, collection in (("attachment", "attachments"), ("resource", "resources")):
            for outcome in message[collection]:
                item = deepcopy(outcome)
                item["source_kind"] = kind
                if item["outcome"] not in {"extracted", "duplicate", "excluded_by_policy"}:
                    raise SemanticError("catalog has an unresolved source outcome and cannot be interpreted")
                source_outcomes.append(item)
    mime_accounting: list[dict[str, Any]] = []
    if record.header.get("custody_version") == 2:
        from .mime_accounting import accounting_sha256
        for message in record.header["messages"]:
            accounting = message["mime_accounting"]
            mime_accounting.append({
                "message_id": message["message_id"],
                "accounting_sha256": accounting_sha256(accounting),
                "node_dispositions": [
                    {
                        "path": node["path"],
                        "mime_type": node["mime_type"],
                        "disposition": node["disposition"],
                        **({"content_id": node["content_id"]} if "content_id" in node else {}),
                    }
                    for node in accounting["nodes"]
                ],
            })
    return SemanticPacket(
        record.header["record_id"], record.header["conversation_id"],
        record.record_sha256 or sha256_bytes(persisted), tuple(segments), tuple(source_outcomes),
        tuple(mime_accounting), tuple(evidence_segments),
    )


def _segments_by_id(packet: SemanticPacket) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    ordinals: set[tuple[int, int]] = set()
    for segment in packet.segments:
        segment_id = segment.get("segment_id")
        text = segment.get("text")
        message_id = segment.get("source_message_id")
        content_id = segment.get("content_id")
        content_kind = segment.get("content_kind")
        received_at = segment.get("source_received_at")
        received_date = segment.get("received_date")
        digest = segment.get("content_sha256")
        message_ordinal = segment.get("source_message_ordinal")
        content_ordinal = segment.get("source_content_ordinal")
        if not all(isinstance(item, str) and item for item in (segment_id, message_id, content_id, content_kind, received_at, received_date, digest)):
            raise SemanticError("semantic packet segment lacks immutable identity or custody")
        if not isinstance(text, str) or sha256_bytes(text.encode("utf-8")) != digest:
            raise SemanticError("semantic packet segment text does not match its catalog hash")
        if content_kind not in {"body", "body_supplement", "attachment", "resource"}:
            raise SemanticError("semantic packet segment has an invalid content kind")
        if not isinstance(message_ordinal, int) or message_ordinal < 0 or not isinstance(content_ordinal, int) or content_ordinal < 0:
            raise SemanticError("semantic packet segment lacks ordered source coordinates")
        if segment_id in result or (message_ordinal, content_ordinal) in ordinals:
            raise SemanticError("semantic packet has duplicate segment identity or ordering")
        provenance = segment.get("source_provenance")
        if content_kind in {"attachment", "resource", "body_supplement"} and not isinstance(provenance, Mapping):
            raise SemanticError("non-body segment lacks preserved source provenance")
        result[segment_id] = deepcopy(segment)
        ordinals.add((message_ordinal, content_ordinal))
    if not result:
        raise SemanticError("semantic packet has no source segments")
    ordered = sorted(result.values(), key=lambda item: (item["source_message_ordinal"], item["source_content_ordinal"]))
    if ordered != list(result.values()):
        raise SemanticError("semantic packet segments are not in canonical source order")
    return result


def _packet_hash(packet: SemanticPacket) -> str:
    if not isinstance(packet.record_id, str) or not packet.record_id or not isinstance(packet.conversation_id, str) or not packet.conversation_id:
        raise SemanticError("semantic packet lacks record or conversation identity")
    digest = packet.catalog_record_sha256
    if not isinstance(digest, str) or len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
        raise SemanticError("semantic packet lacks the exact catalog-record hash")
    seen_outcomes: set[str] = set()
    extracted_by_content: dict[str, dict[str, Any]] = {}
    for outcome in packet.source_outcomes:
        if not isinstance(outcome, Mapping):
            raise SemanticError("semantic packet source outcome is malformed")
        outcome_id = outcome.get("outcome_id")
        if not isinstance(outcome_id, str) or not outcome_id or outcome_id in seen_outcomes:
            raise SemanticError("semantic packet source outcomes lack unique immutable identity")
        if outcome.get("source_kind") not in {"attachment", "resource"} or outcome.get("outcome") not in {"extracted", "duplicate", "excluded_by_policy"}:
            raise SemanticError("semantic packet contains an unresolved source outcome")
        if outcome.get("outcome") == "extracted":
            content_id = outcome.get("content_id")
            if not isinstance(content_id, str) or not content_id or content_id in extracted_by_content:
                raise SemanticError("semantic packet has ambiguous extracted content identity")
            extracted_by_content[content_id] = dict(outcome)
        seen_outcomes.add(outcome_id)
    non_body_ids: set[str] = set()
    for segment in packet.segments:
        if segment.get("content_kind") not in {"attachment", "resource"}:
            continue
        content_id = segment.get("content_id")
        outcome = extracted_by_content.get(content_id)
        if outcome is None or outcome.get("source_kind") != segment.get("content_kind"):
            raise SemanticError("semantic segment does not dereference one extracted source outcome")
        expected_provenance = {key: value for key, value in outcome.items() if key != "source_kind"}
        if segment.get("source_provenance") != expected_provenance:
            raise SemanticError("semantic segment provenance differs from its source outcome")
        non_body_ids.add(content_id)
    if non_body_ids != set(extracted_by_content):
        raise SemanticError("semantic packet omits an extracted source outcome")
    if packet.mime_accounting:
        message_ids: set[str] = set()
        accounted_content_ids: set[str] = set()
        for item in packet.mime_accounting:
            if not isinstance(item, Mapping):
                raise SemanticError("semantic packet MIME accounting is malformed")
            message_id = item.get("message_id")
            digest = item.get("accounting_sha256")
            nodes = item.get("node_dispositions")
            if (
                not isinstance(message_id, str) or not message_id or message_id in message_ids
                or not isinstance(digest, str) or len(digest) != 64
                or not isinstance(nodes, list) or not nodes
            ):
                raise SemanticError("semantic packet MIME accounting lacks stable evidence")
            for node in nodes:
                if not isinstance(node, Mapping) or node.get("disposition") not in {
                    "structural", "interpret", "padding", "duplicate_text",
                    "html_evidence", "external_attachment",
                }:
                    raise SemanticError("semantic packet has an invalid MIME node disposition")
                if isinstance(node.get("content_id"), str):
                    accounted_content_ids.add(node["content_id"])
            message_ids.add(message_id)
        # MIME accounting owns only original text MIME units.  Extracted
        # attachment/resource segments are independently bound above through
        # their typed source outcomes and must not be folded into this set.
        supplied_content_ids = {
            item.get("content_id")
            for item in [*packet.segments, *packet.evidence_segments]
            if item.get("content_kind") in {
                "body", "body_supplement", "html_evidence",
            }
        }
        if supplied_content_ids != accounted_content_ids:
            raise SemanticError("semantic packet content does not match MIME accounting")
        for item in packet.evidence_segments:
            if (
                not isinstance(item, Mapping) or item.get("content_kind") != "html_evidence"
                or not isinstance(item.get("text"), str)
                or item.get("content_sha256") != sha256_bytes(item["text"].encode("utf-8"))
            ):
                raise SemanticError("semantic packet HTML evidence is malformed")
    mapping = packet.as_mapping()
    _segments_by_id(packet)
    return sha256_bytes(canonical_json_bytes(mapping))


def _exact_span_text(segment: Mapping[str, Any], start: int, end: int, *, allow_empty: bool = False) -> str:
    data = segment["text"].encode("utf-8")
    if start < 0 or end < start or (end == start and not allow_empty) or end > len(data):
        raise SemanticError("semantic span is outside its source segment")
    try:
        return data[start:end].decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise SemanticError("semantic span splits a UTF-8 source character") from exc


def _normalized_coverage(
    coverage: Sequence[Any], segments: Mapping[str, Mapping[str, Any]], segment_order: Mapping[str, int],
) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for entry in coverage:
        if not isinstance(entry, Mapping):
            raise SemanticError("semantic coverage entry is malformed")
        segment_id = entry.get("segment_id")
        start, end = entry.get("byte_start"), entry.get("byte_end")
        outcome, reason = entry.get("outcome"), entry.get("reason")
        if segment_id not in segments or not isinstance(start, int) or not isinstance(end, int):
            raise SemanticError("semantic coverage references an unknown segment or span")
        if outcome not in {"fact", "no_fact", "review"} or not isinstance(reason, str) or not reason.strip():
            raise SemanticError("semantic coverage lacks a declared span disposition")
        _exact_span_text(segments[segment_id], start, end, allow_empty=True)
        normalized.append({
            "segment_id": segment_id, "byte_start": start, "byte_end": end,
            "outcome": outcome, "reason": reason,
        })
    normalized.sort(key=lambda item: (segment_order[item["segment_id"]], item["byte_start"], item["byte_end"], item["outcome"], item["reason"]))
    for segment_id, segment in segments.items():
        entries = [entry for entry in normalized if entry["segment_id"] == segment_id]
        length = len(segment["text"].encode("utf-8"))
        if not entries:
            raise SemanticError("semantic coverage does not account for every source segment")
        expected_start = 0
        for entry in entries:
            if entry["byte_start"] != expected_start:
                raise SemanticError("semantic coverage spans have a gap or overlap")
            if entry["byte_end"] == entry["byte_start"] and length != 0:
                raise SemanticError("nonempty source coverage spans must be nonempty")
            expected_start = entry["byte_end"]
        if expected_start != length:
            raise SemanticError("semantic coverage does not partition the exact source bytes")
    return normalized


def _fact_attachment(segment: Mapping[str, Any], start: int, end: int) -> dict[str, Any]:
    provenance = segment["source_provenance"]
    identity = provenance.get("attachment_id") or provenance.get("resource_id")
    return {
        "attachment_id": identity,
        "content_id": segment["content_id"],
        "origin": provenance["origin"],
        "mime_type": provenance["mime_type"],
        "original_content_sha256": provenance["original_content_sha256"],
        "extracted_text_sha256": segment["content_sha256"],
        "locator": {"kind": "extracted_text_span", "byte_start": start, "byte_end": end},
        "source_locator": deepcopy(provenance["locator"]),
    }


def interpret_packet(
    packet: SemanticPacket,
    interpreter: Callable[[Mapping[str, Any]], Mapping[str, Any]],
    *, fact_schema: Mapping[str, Any], extraction_schema: Mapping[str, Any],
) -> dict[str, Any]:
    """Run one interpreter and mechanically bind wording to exact source support."""
    frozen_mapping = deepcopy(packet.as_mapping())
    frozen_packet = SemanticPacket(
        frozen_mapping["record_id"], frozen_mapping["conversation_id"],
        frozen_mapping["catalog_record_sha256"], tuple(deepcopy(frozen_mapping["segments"])),
        tuple(deepcopy(frozen_mapping["source_outcomes"])),
        tuple(deepcopy(frozen_mapping.get("mime_accounting", []))),
        tuple(deepcopy(frozen_mapping.get("evidence_segments", []))),
    )
    segments = _segments_by_id(frozen_packet)
    packet_sha256 = _packet_hash(frozen_packet)
    segment_order = {segment_id: index for index, segment_id in enumerate(segments)}
    raw = interpreter(deepcopy(frozen_mapping))
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
    normalized_coverage = _normalized_coverage(coverage, segments, segment_order)
    for coverage_item in normalized_coverage:
        disposition = segments[coverage_item["segment_id"]].get("source_provenance", {}).get("disposition")
        if disposition in {"padding", "duplicate_text"} and coverage_item["outcome"] != "no_fact":
            raise SemanticError("padding or duplicate MIME content cannot produce a Fact")
    normalized_candidates: list[dict[str, Any]] = []
    for candidate in candidates:
        if not isinstance(candidate, Mapping):
            raise SemanticError("semantic candidate is malformed")
        segment_id = candidate.get("segment_id")
        start, end = candidate.get("byte_start"), candidate.get("byte_end")
        kind = candidate.get("candidate_kind")
        category, entity_scope = candidate.get("category"), candidate.get("entity_scope")
        text, flags = candidate.get("text"), candidate.get("flags")
        if segment_id not in segments or not isinstance(start, int) or not isinstance(end, int) or not isinstance(kind, str) or not kind:
            raise SemanticError("semantic candidate lacks an exact source span or kind")
        if not isinstance(category, str) or not isinstance(entity_scope, str) or not isinstance(text, str) or not text or not isinstance(flags, Mapping):
            raise SemanticError("semantic candidate lacks required canonical wording or classification")
        source_quote = _exact_span_text(segments[segment_id], start, end)
        item = {
            "segment_id": segment_id, "byte_start": start, "byte_end": end,
            "candidate_kind": kind, "category": category, "entity_scope": entity_scope,
            "text": text, "flags": dict(flags),
        }
        if "task_relation" in candidate:
            if not isinstance(candidate["task_relation"], Mapping):
                raise SemanticError("semantic task relation is malformed")
            item["task_relation"] = deepcopy(candidate["task_relation"])
        item["source_quote_sha256"] = sha256_bytes(source_quote.encode("utf-8"))
        normalized_candidates.append(item)
    normalized_candidates.sort(key=lambda item: (
        segment_order[item["segment_id"]], item["byte_start"], item["byte_end"],
        item["candidate_kind"], canonical_json_bytes(item),
    ))
    candidate_spans = {(item["segment_id"], item["byte_start"], item["byte_end"]) for item in normalized_candidates}
    fact_coverage = {(item["segment_id"], item["byte_start"], item["byte_end"]) for item in normalized_coverage if item["outcome"] == "fact"}
    if candidate_spans != fact_coverage:
        raise SemanticError("Fact candidates and fact coverage spans do not match exactly")
    review_spans = {
        (item["segment_id"], item["byte_start"], item["byte_end"]): item["reason"]
        for item in normalized_coverage if item["outcome"] == "review"
    }
    normalized_reviews: list[dict[str, Any]] = []
    for entry in review_cases:
        if not isinstance(entry, Mapping):
            raise SemanticError("semantic review case is malformed")
        item = {key: entry.get(key) for key in ("segment_id", "byte_start", "byte_end", "reason")}
        if (
            item["segment_id"] not in segments
            or not isinstance(item["byte_start"], int)
            or not isinstance(item["byte_end"], int)
            or not isinstance(item["reason"], str)
            or not item["reason"].strip()
        ):
            raise SemanticError("semantic review case lacks an exact source span and reason")
        _exact_span_text(segments[item["segment_id"]], item["byte_start"], item["byte_end"], allow_empty=True)
        normalized_reviews.append(item)
    normalized_reviews.sort(key=lambda item: (segment_order[item["segment_id"]], item["byte_start"], item["byte_end"], item["reason"]))
    if {
        (item["segment_id"], item["byte_start"], item["byte_end"]): item["reason"]
        for item in normalized_reviews
    } != review_spans:
        raise SemanticError("review coverage and explicit review cases do not match")
    facts: list[dict[str, Any]] = []
    seen_fact_ids: set[str] = set()
    for candidate in normalized_candidates:
        segment = segments[candidate["segment_id"]]
        start, end = candidate["byte_start"], candidate["byte_end"]
        source_quote = _exact_span_text(segment, start, end)
        fact = {
            "fact_id": stable_fact_id(frozen_packet.record_id, segment["source_message_id"], segment["content_id"], start, end, candidate["candidate_kind"]),
            "record_id": frozen_packet.record_id,
            "source_message_id": segment["source_message_id"],
            "content_id": segment["content_id"],
            "source_content_sha256": segment["content_sha256"],
            "source_byte_start": start,
            "source_byte_end": end,
            "source_quote": source_quote,
            "source_received_at": segment["source_received_at"],
            "source_message_ordinal": segment["source_message_ordinal"],
            "source_content_ordinal": segment["source_content_ordinal"],
            "received_date": segment["received_date"],
            "entity_scope": candidate["entity_scope"],
            "category": candidate["category"],
            "text": candidate["text"],
            "flags": deepcopy(candidate["flags"]),
        }
        if segment["content_kind"] in {"attachment", "resource"}:
            fact["attachment"] = _fact_attachment(segment, start, end)
        if "task_relation" in candidate:
            fact["task_relation"] = deepcopy(candidate["task_relation"])
        _validated(fact, fact_schema, "semantic Fact")
        if fact["fact_id"] in seen_fact_ids:
            raise SemanticError("semantic candidates produce duplicate stable Fact IDs")
        seen_fact_ids.add(fact["fact_id"])
        facts.append(fact)
    attachment_outcomes = []
    for item in frozen_packet.source_outcomes:
        attachment_outcomes.append({
            "outcome_id": item["outcome_id"],
            "content_id": item["content_id"],
            "source_message_id": item["source_message_id"],
            "source_kind": item["source_kind"],
            "source_id": item.get("attachment_id") or item.get("resource_id"),
            "origin": item["origin"],
            "outcome": item["outcome"],
            "mime_type": item["mime_type"],
            "original_content_sha256": item["original_content_sha256"],
            "extracted_text_sha256": item["extracted_text_sha256"],
            "locator": deepcopy(item["locator"]),
            "complete_units": list(item["complete_units"]),
            "unit_count": item["unit_count"],
            "disposition_reason": item["disposition_reason"],
            "provenance_sha256": sha256_bytes(canonical_json_bytes(dict(item))),
        })
    result = {
        "schema_version": 2 if frozen_packet.mime_accounting else 1,
        "conversation_id": frozen_packet.conversation_id,
        "candidates": normalized_candidates,
        "coverage": normalized_coverage,
        "attachment_outcomes": attachment_outcomes,
        "review_cases": normalized_reviews,
    }
    if frozen_packet.mime_accounting:
        result["mime_accounting_sha256"] = sha256_bytes(
            canonical_json_bytes(list(frozen_packet.mime_accounting))
        )
    _validated(result, extraction_schema, "semantic extraction result")
    interpreted_sha256 = sha256_bytes(canonical_json_bytes({"facts": facts, "result": result}))
    return {"facts": facts, "result": result, "packet_sha256": packet_sha256, "interpreted_sha256": interpreted_sha256}


def _fact_classification(fact: Mapping[str, Any], candidate: Mapping[str, Any]) -> dict[str, Any]:
    result = {
        "candidate_kind": candidate["candidate_kind"],
        "category": fact["category"],
        "entity_scope": fact["entity_scope"],
        "flags": deepcopy(fact["flags"]),
    }
    if "task_relation" in fact:
        result["task_relation"] = deepcopy(fact["task_relation"])
    return result


def validate_independent_audit(
    packet: SemanticPacket, interpreted: Mapping[str, Any], audit: Mapping[str, Any],
) -> None:
    """Require independent acceptance of every exact span, wording, and class."""
    segments = _segments_by_id(packet)
    current_packet_hash = _packet_hash(packet)
    if audit.get("packet_sha256") != interpreted.get("packet_sha256") or audit.get("packet_sha256") != current_packet_hash:
        raise SemanticError("independent audit does not identify the exact source packet")
    if audit.get("interpreted_sha256") != interpreted.get("interpreted_sha256"):
        raise SemanticError("independent audit does not identify the exact interpreted artifact")
    result = interpreted.get("result")
    facts = interpreted.get("facts")
    if not isinstance(result, Mapping) or not isinstance(facts, Sequence) or isinstance(facts, (str, bytes)):
        raise SemanticError("interpreted artifact is malformed")
    expected_result_hash = sha256_bytes(canonical_json_bytes({"facts": list(facts), "result": dict(result)}))
    if expected_result_hash != interpreted.get("interpreted_sha256"):
        raise SemanticError("interpreted artifact changed after its result hash was assigned")
    coverage_audit = audit.get("coverage")
    fact_audit = audit.get("facts")
    outcome_audit = audit.get("source_outcomes")
    accounting_audit = audit.get("mime_accounting", [])
    if not isinstance(coverage_audit, Sequence) or isinstance(coverage_audit, (str, bytes)):
        raise SemanticError("independent audit coverage must be an array")
    if not isinstance(fact_audit, Sequence) or isinstance(fact_audit, (str, bytes)):
        raise SemanticError("independent audit facts must be an array")
    if not isinstance(outcome_audit, Sequence) or isinstance(outcome_audit, (str, bytes)):
        raise SemanticError("independent audit source_outcomes must be an array")
    if not isinstance(accounting_audit, Sequence) or isinstance(accounting_audit, (str, bytes)):
        raise SemanticError("independent audit MIME accounting must be an array")
    expected_coverage = result.get("coverage")
    if not isinstance(expected_coverage, Sequence):
        raise SemanticError("interpreted coverage is malformed")
    if len(coverage_audit) != len(expected_coverage):
        raise SemanticError("independent audit does not account for every exact coverage span")
    for expected, audited in zip(expected_coverage, coverage_audit):
        if not isinstance(audited, Mapping):
            raise SemanticError("independent coverage audit entry is malformed")
        exact = {key: expected[key] for key in ("segment_id", "byte_start", "byte_end", "outcome")}
        observed = {key: audited.get(key) for key in exact}
        if observed != exact:
            raise SemanticError("independent audit coverage does not match the interpreted span")
        segment = segments[expected["segment_id"]]
        quote = _exact_span_text(segment, expected["byte_start"], expected["byte_end"], allow_empty=True)
        if audited.get("source_quote_sha256") != sha256_bytes(quote.encode("utf-8")):
            raise SemanticError("independent audit coverage does not identify the exact source bytes")
        if audited.get("interpreted_reason_sha256") != sha256_bytes(expected["reason"].encode("utf-8")):
            raise SemanticError("independent audit coverage does not identify the interpreted disposition reason")
        if audited.get("audit_disposition") != "accepted" or not isinstance(audited.get("reason"), str) or not audited["reason"].strip():
            raise SemanticError("independent audit found an unresolved coverage error")
    candidates = result.get("candidates")
    if not isinstance(candidates, Sequence) or len(candidates) != len(facts) or len(fact_audit) != len(facts):
        raise SemanticError("independent audit does not account for every Fact")
    for fact, candidate, audited in zip(facts, candidates, fact_audit):
        if not isinstance(fact, Mapping) or not isinstance(candidate, Mapping) or not isinstance(audited, Mapping):
            raise SemanticError("independent Fact audit entry is malformed")
        if audited.get("fact_id") != fact.get("fact_id"):
            raise SemanticError("independent audit references the wrong Fact")
        if audited.get("source_quote_sha256") != sha256_bytes(fact["source_quote"].encode("utf-8")):
            raise SemanticError("independent Fact audit does not identify its exact source quote")
        if audited.get("canonical_text_sha256") != sha256_bytes(fact["text"].encode("utf-8")):
            raise SemanticError("independent Fact audit does not identify its canonical wording")
        if audited.get("classification") != _fact_classification(fact, candidate):
            raise SemanticError("independent Fact audit classification disagrees")
        if audited.get("audit_disposition") != "accepted" or not isinstance(audited.get("reason"), str) or not audited["reason"].strip():
            raise SemanticError("independent audit found unsupported Fact wording or classification")
    if len(outcome_audit) != len(packet.source_outcomes):
        raise SemanticError("independent audit does not account for every source outcome")
    for expected, audited in zip(packet.source_outcomes, outcome_audit):
        if not isinstance(audited, Mapping) or audited.get("outcome_id") != expected["outcome_id"]:
            raise SemanticError("independent audit references the wrong source outcome")
        expected_digest = sha256_bytes(canonical_json_bytes(dict(expected)))
        if audited.get("outcome_sha256") != expected_digest:
            raise SemanticError("independent audit does not identify the exact source outcome")
        if audited.get("audit_disposition") != "accepted" or not isinstance(audited.get("reason"), str) or not audited["reason"].strip():
            raise SemanticError("independent audit found an unresolved source-outcome error")
    if len(accounting_audit) != len(packet.mime_accounting):
        raise SemanticError("independent audit does not account for every MIME disposition inventory")
    for expected, audited in zip(packet.mime_accounting, accounting_audit):
        if not isinstance(audited, Mapping) or audited.get("message_id") != expected.get("message_id"):
            raise SemanticError("independent MIME audit references the wrong message")
        if audited.get("accounting_sha256") != expected.get("accounting_sha256"):
            raise SemanticError("independent MIME audit does not identify the exact accounting")
        if audited.get("audit_disposition") != "accepted" or not isinstance(audited.get("reason"), str) or not audited["reason"].strip():
            raise SemanticError("independent audit found an unresolved MIME accounting error")
