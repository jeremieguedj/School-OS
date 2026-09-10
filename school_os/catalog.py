"""Lossless version-2 source-catalog framing and verification helpers."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from .contracts import canonical_json_bytes, sha256_bytes, validate


class CatalogError(ValueError):
    """Raised when a source conversation or catalog record is unsafe."""


RECORD_PREFIX = b"# School-OS source catalog record v2\n"
RECORD_MARKER = b"<!-- school-os-record "
MESSAGE_MARKER = b"<!-- school-os-message "
CONTENT_MARKER = b"<!-- school-os-content "
MARKER_END = b" -->\n"


@dataclass(frozen=True)
class CatalogRecord:
    """Parsed immutable record header and ordered exact source bodies."""

    header: dict[str, Any]
    bodies: tuple[tuple[str, str], ...]
    contents: tuple[tuple[str, str], ...] = ()
    record_sha256: str | None = None


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


def stable_content_id(source_message_id: str, kind: str, source_id: str) -> str:
    """Derive content identity from immutable message and body/resource identity."""
    if not all(isinstance(item, str) and item for item in (source_message_id, kind, source_id)):
        raise CatalogError("content identity requires message, kind, and source identity")
    return "content-" + sha256_bytes(
        f"{source_message_id}\0{kind}\0{source_id}".encode("utf-8")
    )


def _outcome_mapping(
    value: Any, *, source_message_id: str, kind: str, outcome_ordinal: int,
) -> dict[str, Any]:
    """Convert one importer-owned outcome into a strict catalog mapping."""
    if kind == "attachment":
        attachment_id = value.attachment_id
        content_id = stable_content_id(source_message_id, kind, attachment_id)
        if value.source_message_id not in {None, source_message_id}:
            raise CatalogError("attachment outcome belongs to a different source message")
        result = {
            "attachment_id": attachment_id,
            "content_id": content_id,
            "source_message_id": source_message_id,
            "origin": value.origin,
            "outcome": value.outcome,
            "mime_type": value.mime_type,
            "original_bytes_observed": value.original_bytes_observed,
            "original_content_sha256": value.original_content_sha256,
            "extracted_text_sha256": value.extracted_text_sha256,
            "extracted_text": value.text,
            "locator": dict(value.locator) if value.locator is not None else None,
            "read_evidence": dict(value.read_evidence) if value.read_evidence is not None else None,
            "complete_units": list(value.complete_units),
            "unit_count": value.unit_count,
            "disposition_reason": value.disposition_reason,
        }
    elif kind == "resource":
        resource = value.resource
        if resource.source_message_id != source_message_id:
            raise CatalogError("direct resource belongs to a different source message")
        result = {
            "resource_id": resource.resource_id,
            "content_id": stable_content_id(source_message_id, kind, resource.resource_id),
            "source_message_id": source_message_id,
            "origin": resource.origin,
            "outcome": value.outcome,
            "mime_type": value.fetch_evidence.get("verified_mime_type") if value.fetch_evidence else None,
            "html_part_id": resource.html_part_id,
            "html_part_sha256": resource.html_part_sha256,
            "html_decoded_sha256": resource.html_decoded_sha256,
            "occurrence": resource.occurrence,
            "attribute": resource.attribute,
            "original_url": resource.url,
            "final_url": value.final_url,
            "redirect_chain": list(value.redirect_chain),
            "fetch_evidence": dict(value.fetch_evidence) if value.fetch_evidence is not None else None,
            "original_bytes_observed": value.original_content_sha256 is not None,
            "original_content_sha256": value.original_content_sha256,
            "extracted_text_sha256": value.extracted_text_sha256,
            "extracted_text": value.text,
            "locator": dict(value.locator) if value.locator is not None else None,
            "complete_units": list(value.complete_units),
            "unit_count": value.unit_count,
            "disposition_reason": value.disposition_reason,
        }
    else:
        raise CatalogError("unsupported catalog outcome kind")
    source_identity = result.get("attachment_id") or result.get("resource_id")
    result["outcome_id"] = "outcome-" + sha256_bytes(
        f"{source_message_id}\0{kind}\0{outcome_ordinal}\0{source_identity}".encode("utf-8")
    )
    _validate_content_outcome(result, kind)
    return result


def build_catalog_message(
    *, message_id: str, received_at: str, received_date: str, admission: Any | None,
    attachment_outcomes: Sequence[Any] = (), resource_outcomes: Sequence[Any] = (),
    gmail_internal_date_ms: int | None = None,
    mime_accounting: Mapping[str, Any] | None = None,
    mime_contents: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Bind one admitted body and importer-owned outcomes into catalog input."""
    if not all(isinstance(item, str) and item for item in (message_id, received_at, received_date)):
        raise CatalogError("catalog message lacks source identity or time")
    if admission is None:
        if not isinstance(mime_accounting, Mapping) or mime_accounting.get("primary_content_id") is not None:
            raise CatalogError("a missing primary body requires complete MIME accounting")
        body = None
        custody = None
        content_id = None
    else:
        if admission.outcome != "admitted" or admission.plaintext is None:
            raise CatalogError("only an admitted exact plaintext body can enter a catalog message")
        if not isinstance(admission.selected_part_id, str) or not admission.selected_part_id:
            raise CatalogError("admitted body lacks selected MIME-part identity")
        body = admission.plaintext.decode("utf-8", errors="strict")
        body_bytes = body.encode("utf-8")
        content_id = stable_content_id(message_id, "body", admission.selected_part_id)
        raw_locator = dict(admission.raw_part_locator or {})
        custody = {
            "outcome": "admitted",
            "complete": True,
            "content_id": content_id,
            "selected_part_id": admission.selected_part_id,
            "declared_charset": admission.declared_charset,
            "content_transfer_encoding": admission.content_transfer_encoding,
            "raw_part_sha256": admission.raw_part_sha256,
            "raw_part_byte_length": admission.raw_part_byte_length,
            "raw_part_locator": raw_locator,
            "provider_unicode_sha256": sha256_bytes(body_bytes),
            "plaintext_sha256": sha256_bytes(body_bytes),
            "plaintext_byte_length": len(body_bytes),
        }
    attachments = [
        _outcome_mapping(value, source_message_id=message_id, kind="attachment", outcome_ordinal=index)
        for index, value in enumerate(attachment_outcomes)
    ]
    resources = [
        _outcome_mapping(value, source_message_id=message_id, kind="resource", outcome_ordinal=index)
        for index, value in enumerate(resource_outcomes)
    ]
    content_ids = [*([] if content_id is None else [content_id]), *(value["content_id"] for value in [*attachments, *resources] if value["outcome"] == "extracted")]
    if len(content_ids) != len(set(content_ids)):
        raise CatalogError("catalog message has duplicate content identity")
    outcome_ids = [value["outcome_id"] for value in [*attachments, *resources]]
    if len(outcome_ids) != len(set(outcome_ids)):
        raise CatalogError("catalog message has duplicate outcome identity")
    result = {
        "message_id": message_id,
        "received_at": received_at,
        "received_date": received_date,
        "body": body,
        "body_custody": custody,
        "attachments": attachments,
        "resources": resources,
    }
    if mime_accounting is not None or mime_contents is not None:
        if not isinstance(mime_accounting, Mapping) or not isinstance(mime_contents, Sequence):
            raise CatalogError("MIME accounting and content inventory must be supplied together")
        result["mime_accounting"] = dict(mime_accounting)
        result["mime_contents"] = [dict(item) for item in mime_contents]
        # The primary body remains a compatibility/presentation alias. Its
        # custody identity must be the primary accounted content identity.
        primary = mime_accounting.get("primary_content_id")
        if primary != content_id:
            raise CatalogError("admitted body differs from MIME accounting primary content")
        try:
            from .mime_accounting import validate_mime_accounting
            validate_mime_accounting(result)
        except ValueError as exc:
            raise CatalogError(str(exc)) from exc
    if gmail_internal_date_ms is not None:
        if isinstance(gmail_internal_date_ms, bool) or not isinstance(gmail_internal_date_ms, int) or gmail_internal_date_ms < 0:
            raise CatalogError("catalog message Gmail internal date is invalid")
        result["gmail_internal_date_ms"] = gmail_internal_date_ms
    return result


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


def _validate_hash(value: Any, label: str, *, nullable: bool = False) -> None:
    if nullable and value is None:
        return
    if not isinstance(value, str) or len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
        raise CatalogError(f"{label} is not a lower-case SHA-256 digest")


def _validate_extraction_custody(value: Mapping[str, Any], kind: str, text: str) -> None:
    """Recheck persisted unit and locator evidence."""
    mime_type = value["mime_type"]
    unit_count = value["unit_count"]
    units = value["complete_units"]
    if not isinstance(unit_count, int) or unit_count < 1 or not isinstance(units, list):
        raise CatalogError(f"extracted {kind} lacks complete ordered unit evidence")
    prefix = "page" if mime_type == "application/pdf" else "image" if mime_type.startswith("image/") else "text"
    if units != [f"{prefix}:{index}" for index in range(1, unit_count + 1)]:
        raise CatalogError(f"extracted {kind} unit evidence is incomplete or unordered")
    locator = value.get("locator")
    if not isinstance(locator, Mapping):
        raise CatalogError(f"extracted {kind} lacks an extraction locator")
    text_length = len(text.encode("utf-8"))
    if locator.get("kind") == "extracted_text_span":
        locator_valid = (
            locator.get("byte_start") == 0
            and locator.get("byte_end") == text_length
            and text_length > 0
        )
    elif locator.get("kind") == "provider_page_region":
        locator_valid = (
            unit_count == 1
            and locator.get("page") == 1
            and isinstance(locator.get("region"), str)
            and bool(locator["region"])
        )
    else:
        locator_valid = False
    if not locator_valid:
        raise CatalogError(f"extracted {kind} locator does not cover the preserved extraction")



def _validate_attachment_read_evidence(value: Mapping[str, Any]) -> None:
    evidence = value.get("read_evidence")
    if evidence is None:
        if value.get("outcome") == "extracted":
            raise CatalogError("extracted attachment lacks typed complete read evidence")
        return
    expected_keys = {
        "complete", "identity", "mime_type", "declared_byte_size",
        "observed_byte_size", "mode", "locator", "version",
    }
    if not isinstance(evidence, Mapping) or set(evidence) != expected_keys:
        raise CatalogError("attachment lacks typed complete read evidence")
    declared = evidence.get("declared_byte_size")
    observed = evidence.get("observed_byte_size")
    original_observed = value["original_bytes_observed"]
    version = evidence.get("version")
    if (
        evidence.get("complete") is not True
        or evidence.get("identity") != value["attachment_id"]
        or evidence.get("mime_type") != value.get("mime_type")
        or not isinstance(declared, int) or declared < 0
        or evidence.get("mode") != ("original_bytes" if original_observed else "provider_extracted_text")
        or not isinstance(evidence.get("locator"), Mapping)
        or version is not None and not isinstance(version, str)
        or (observed != declared if original_observed else observed is not None)
    ):
        raise CatalogError("attachment read evidence disagrees with its custody")


def _validate_resource_fetch_evidence(value: Mapping[str, Any]) -> None:
    evidence = value.get("fetch_evidence")
    if evidence is None:
        if value.get("outcome") == "extracted":
            raise CatalogError("extracted resource lacks typed complete fetch evidence")
        return
    expected_keys = {
        "status_code", "complete", "eof", "bytes_read",
        "declared_content_length", "declared_mime_type", "verified_mime_type",
    }
    if not isinstance(evidence, Mapping) or set(evidence) != expected_keys:
        raise CatalogError("resource lacks typed complete fetch evidence")
    byte_count = evidence.get("bytes_read")
    declared = evidence.get("declared_content_length")
    if (
        evidence.get("status_code") != 200
        or evidence.get("complete") is not True
        or evidence.get("eof") is not True
        or not isinstance(byte_count, int) or byte_count < 1
        or declared is not None and declared != byte_count
        or not isinstance(evidence.get("declared_mime_type"), str)
        or not evidence["declared_mime_type"]
        or evidence.get("verified_mime_type") != value.get("mime_type")
        or value["original_bytes_observed"] is not True
    ):
        raise CatalogError("resource fetch evidence disagrees with its custody")


def _validate_content_outcome(value: Mapping[str, Any], kind: str) -> None:
    required = {
        "outcome_id", "content_id", "source_message_id", "origin", "outcome", "mime_type",
        "original_bytes_observed", "original_content_sha256", "extracted_text_sha256",
        "extracted_text", "locator", "complete_units", "unit_count", "disposition_reason",
    }
    if kind == "attachment":
        required |= {"attachment_id", "read_evidence"}
        allowed_origins = {"mime_attachment"}
    else:
        required |= {
            "resource_id", "html_part_id", "html_part_sha256", "html_decoded_sha256",
            "occurrence", "attribute",
            "original_url", "final_url", "redirect_chain", "fetch_evidence",
        }
        allowed_origins = {"html_embedded", "html_linked"}
    if set(value) != required:
        raise CatalogError(f"{kind} outcome lacks required typed custody fields")
    if not all(isinstance(value.get(key), str) and value[key] for key in ("outcome_id", "content_id", "source_message_id")):
        raise CatalogError(f"{kind} outcome lacks immutable content/message identity")
    identity_key = "attachment_id" if kind == "attachment" else "resource_id"
    if not isinstance(value.get(identity_key), str) or not value[identity_key]:
        raise CatalogError(f"{kind} outcome lacks immutable source identity")
    if value.get("origin") not in allowed_origins:
        raise CatalogError(f"{kind} outcome has invalid origin")
    allowed_outcomes = {"extracted", "duplicate", "unsupported", "inaccessible", "excluded_by_policy", "manual_review"}
    if value.get("outcome") not in allowed_outcomes:
        raise CatalogError(f"{kind} outcome has invalid disposition")
    reason = value.get("disposition_reason")
    if not isinstance(reason, str) or not reason.strip():
        raise CatalogError(f"{kind} outcome lacks a disposition reason")
    _validate_hash(value.get("original_content_sha256"), f"{kind} original-content hash", nullable=True)
    _validate_hash(value.get("extracted_text_sha256"), f"{kind} extracted-text hash", nullable=True)
    original_bytes_observed = value.get("original_bytes_observed")
    if not isinstance(original_bytes_observed, bool):
        raise CatalogError(f"{kind} original-byte observation must be Boolean")
    if original_bytes_observed != (value.get("original_content_sha256") is not None):
        raise CatalogError(f"{kind} original-byte observation and hash disagree")
    if kind == "attachment":
        _validate_attachment_read_evidence(value)
    else:
        _validate_resource_fetch_evidence(value)
    text = value.get("extracted_text")
    if value.get("outcome") == "extracted":
        if not isinstance(value.get("mime_type"), str) or not value["mime_type"]:
            raise CatalogError(f"extracted {kind} lacks a verified MIME type")
        if not isinstance(text, str) or not text:
            raise CatalogError(f"extracted {kind} lacks preserved UTF-8 text")
        encoded = text.encode("utf-8")
        if value.get("extracted_text_sha256") != sha256_bytes(encoded):
            raise CatalogError(f"extracted {kind} text hash disagrees")
        _validate_extraction_custody(value, kind, text)
    elif text is not None or value.get("extracted_text_sha256") is not None:
        raise CatalogError(f"non-extracted {kind} cannot retain inferred extracted text")
    elif value.get("locator") is not None or value.get("complete_units") != [] or value.get("unit_count") is not None:
        raise CatalogError(f"non-extracted {kind} cannot retain extraction custody")
    if kind == "resource":
        _validate_hash(value.get("html_part_sha256"), "raw HTML-part hash")
        _validate_hash(value.get("html_decoded_sha256"), "decoded HTML-part hash")
        if not isinstance(value.get("html_part_id"), str) or not value["html_part_id"]:
            raise CatalogError("resource outcome lacks HTML-part identity")
        if not isinstance(value.get("occurrence"), int) or value["occurrence"] < 0:
            raise CatalogError("resource outcome has invalid HTML occurrence")
        if not isinstance(value.get("attribute"), str) or not value["attribute"]:
            raise CatalogError("resource outcome lacks HTML attribute locator")
        if not isinstance(value.get("original_url"), str) or not value["original_url"]:
            raise CatalogError("resource outcome lacks original URL")
        if value.get("fetch_evidence") is not None:
            chain = value.get("redirect_chain")
            if not isinstance(chain, list) or not chain or chain[0] != value["original_url"] or chain[-1] != value.get("final_url"):
                raise CatalogError("resource outcome has invalid redirect custody")


def _validate_mime_external_outcomes(message: Mapping[str, Any]) -> None:
    accounting = message.get("mime_accounting")
    if not isinstance(accounting, Mapping):
        return
    nodes = accounting.get("nodes")
    attachments = message.get("attachments")
    if not isinstance(nodes, list) or not isinstance(attachments, list):
        raise CatalogError("MIME accounting cannot be matched to attachment outcomes")
    external = [
        item for item in nodes
        if isinstance(item, Mapping) and item.get("disposition") == "external_attachment"
    ]
    if len(external) != len(attachments):
        raise CatalogError("MIME external leaves and attachment outcomes differ")


def _validate_custody_message(message: Mapping[str, Any]) -> None:
    custody = message.get("body_custody")
    if custody is None:
        if message.get("body") is not None:
            raise CatalogError("source message has a body without custody")
        attachments = message.get("attachments")
        resources = message.get("resources")
        if not isinstance(attachments, list) or not isinstance(resources, list):
            raise CatalogError("source message lacks attachment/resource inventories")
        for kind, values in (("attachment", attachments), ("resource", resources)):
            for value in values:
                if not isinstance(value, Mapping):
                    raise CatalogError(f"{kind} outcome is malformed")
                _validate_content_outcome(value, kind)
        try:
            from .mime_accounting import validate_mime_accounting
            validate_mime_accounting(message)
            _validate_mime_external_outcomes(message)
        except ValueError as exc:
            raise CatalogError(str(exc)) from exc
        return
    if not isinstance(custody, Mapping):
        raise CatalogError("version-2 source message lacks typed body custody")
    body = message.get("body")
    if not isinstance(body, str):
        raise CatalogError("version-2 source message body is not Unicode")
    body_bytes = body.encode("utf-8")
    required = {
        "outcome", "complete", "content_id", "selected_part_id", "declared_charset",
        "content_transfer_encoding", "raw_part_sha256", "raw_part_byte_length",
        "raw_part_locator", "provider_unicode_sha256", "plaintext_sha256",
        "plaintext_byte_length",
    }
    if not required.issubset(custody) or custody.get("outcome") != "admitted" or custody.get("complete") is not True:
        raise CatalogError("version-2 source message body is not admitted and complete")
    for key in ("content_id", "selected_part_id", "declared_charset", "content_transfer_encoding"):
        if not isinstance(custody.get(key), str) or not custody[key]:
            raise CatalogError(f"body custody lacks {key}")
    for key in ("raw_part_sha256", "provider_unicode_sha256", "plaintext_sha256"):
        _validate_hash(custody.get(key), f"body {key}")
    if custody.get("plaintext_sha256") != sha256_bytes(body_bytes) or custody.get("provider_unicode_sha256") != sha256_bytes(body_bytes):
        raise CatalogError("body custody does not equal the admitted provider Unicode")
    if custody.get("plaintext_byte_length") != len(body_bytes):
        raise CatalogError("body custody byte length disagrees")
    raw_length = custody.get("raw_part_byte_length")
    raw_locator = custody.get("raw_part_locator")
    if (
        not isinstance(raw_length, int) or raw_length < 0
        or not isinstance(raw_locator, Mapping)
        or raw_locator.get("kind") != "raw_part_bytes"
        or raw_locator.get("byte_start") != 0
        or raw_locator.get("byte_end") != raw_length
    ):
        raise CatalogError("body custody lacks a complete raw-part locator")
    attachments = message.get("attachments")
    resources = message.get("resources")
    if not isinstance(attachments, list) or not isinstance(resources, list):
        raise CatalogError("version-2 source message lacks attachment/resource inventories")
    for value in attachments:
        if not isinstance(value, Mapping):
            raise CatalogError("attachment outcome is malformed")
        _validate_content_outcome(value, "attachment")
    for value in resources:
        if not isinstance(value, Mapping):
            raise CatalogError("resource outcome is malformed")
        _validate_content_outcome(value, "resource")
    ids = (
        [item.get("content_id") for item in message.get("mime_contents", [])]
        if isinstance(message.get("mime_contents"), list)
        else [custody["content_id"]]
    )
    ids.extend(value["content_id"] for value in [*attachments, *resources] if value["outcome"] == "extracted")
    if len(ids) != len(set(ids)):
        raise CatalogError("source message has duplicate content identity")
    outcome_ids = [value["outcome_id"] for value in [*attachments, *resources]]
    if len(outcome_ids) != len(set(outcome_ids)):
        raise CatalogError("source message has duplicate outcome identity")
    if any(value["source_message_id"] != message.get("message_id") for value in [*attachments, *resources]):
        raise CatalogError("content outcome source-message association disagrees")
    if "mime_accounting" in message or "mime_contents" in message:
        try:
            from .mime_accounting import validate_mime_accounting
            validate_mime_accounting(message)
            _validate_mime_external_outcomes(message)
        except ValueError as exc:
            raise CatalogError(str(exc)) from exc


def validate_source_conversation(conversation: Mapping[str, Any], schema: Mapping[str, Any]) -> None:
    """Validate a complete adapter-returned conversation before serialization."""
    version = conversation.get("schema_version")
    if version == 1:
        # Read/repair compatibility for alpha.13's earlier synthetic packets.
        # Operational source admission writes schema version 2 only.
        required = {"schema_version", "adapter_id", "conversation_id", "scope", "pagination", "messages"}
        if set(conversation) != required or not isinstance(conversation.get("messages"), list) or not conversation["messages"]:
            raise CatalogError("invalid legacy source conversation")
        if not isinstance(conversation.get("pagination"), Mapping) or conversation["pagination"].get("completed") is not True:
            raise CatalogError("legacy source conversation pagination is incomplete")
        for message in conversation["messages"]:
            if not isinstance(message, Mapping) or set(message) != {"message_id", "received_at", "body", "attachments"}:
                raise CatalogError("invalid legacy source message")
            if not isinstance(message.get("body"), str) or not isinstance(message.get("attachments"), list):
                raise CatalogError("invalid legacy source message content")
    elif version in {2, 3}:
        errors = validate(conversation, dict(schema))
        if errors:
            raise CatalogError("invalid source conversation: " + "; ".join(errors))
        if version == 3 and any(
            not {"mime_accounting", "mime_contents"} <= set(message)
            for message in conversation["messages"]
        ):
            raise CatalogError("version-3 source conversation lacks MIME accounting")
    else:
        raise CatalogError("source conversation has an unsupported schema version")
    message_ids = [message["message_id"] for message in conversation["messages"]]
    if len(message_ids) != len(set(message_ids)):
        raise CatalogError("source conversation has duplicate immutable message_id values")
    if version in {2, 3}:
        for message in conversation["messages"]:
            _validate_custody_message(message)


def serialize_v2_record(conversation: Mapping[str, Any], schema: Mapping[str, Any]) -> bytes:
    """Mechanically frame every complete UTF-8 body using its exact byte count."""
    validate_source_conversation(conversation, schema)
    messages = conversation["messages"]
    custody_version = (
        2 if conversation.get("schema_version") == 3
        else 1 if conversation.get("schema_version") == 2
        else None
    )
    body_content_frames: list[dict[str, Any]] = []
    mime_content_frames: list[dict[str, Any]] = []
    extracted_content_frames: list[dict[str, Any]] = []
    header_messages: list[dict[str, Any]] = []
    for message in messages:
        if custody_version is None:
            header_messages.append({
                "message_id": message["message_id"],
                "received_at": message["received_at"],
                "attachments": message["attachments"],
            })
            continue
        body = message["body"].encode("utf-8") if isinstance(message["body"], str) else None
        body_custody = dict(message["body_custody"]) if isinstance(message["body_custody"], Mapping) else None
        header_message = {
            "message_id": message["message_id"],
            "received_at": message["received_at"],
            "received_date": message["received_date"],
            **({"gmail_internal_date_ms": message["gmail_internal_date_ms"]} if "gmail_internal_date_ms" in message else {}),
            "body_custody": body_custody,
            "attachments": [
                {key: item for key, item in outcome.items() if key != "extracted_text"}
                for outcome in message["attachments"]
            ],
            "resources": [
                {key: item for key, item in outcome.items() if key != "extracted_text"}
                for outcome in message["resources"]
            ],
        }
        if custody_version == 2:
            header_message["mime_accounting"] = dict(message["mime_accounting"])
            header_message["mime_contents"] = [
                {key: value for key, value in item.items() if key != "text"}
                for item in message["mime_contents"]
            ]
        header_messages.append(header_message)
        if body is not None and body_custody is not None:
            body_content_frames.append({
                "content_id": body_custody["content_id"],
                "content_kind": "body",
                "source_message_id": message["message_id"],
                "byte_length": len(body),
                "sha256": sha256_bytes(body),
            })
        if custody_version == 2:
            for item in message["mime_contents"]:
                if body_custody is not None and item["content_id"] == body_custody["content_id"]:
                    continue
                text = item["text"].encode("utf-8")
                mime_content_frames.append({
                    "content_id": item["content_id"],
                    "content_kind": item["content_kind"],
                    "source_message_id": message["message_id"],
                    "byte_length": len(text),
                    "sha256": sha256_bytes(text),
                })
        for kind, outcomes in (("attachment", message["attachments"]), ("resource", message["resources"])):
            for outcome in outcomes:
                if outcome["outcome"] != "extracted":
                    continue
                text = outcome["extracted_text"].encode("utf-8")
                extracted_content_frames.append({
                    "content_id": outcome["content_id"],
                    "content_kind": kind,
                    "source_message_id": message["message_id"],
                    "byte_length": len(text),
                    "sha256": sha256_bytes(text),
                })
    header = {
        "adapter_id": conversation["adapter_id"],
        "conversation_id": conversation["conversation_id"],
        "format_version": 2,
        "pagination": conversation["pagination"],
        "record_id": stable_record_id(conversation["adapter_id"], conversation["conversation_id"]),
        "scope": conversation["scope"],
        "messages": header_messages,
    }
    if custody_version is not None:
        header["custody_version"] = custody_version
        header["content_frames"] = [*body_content_frames, *mime_content_frames, *extracted_content_frames]
    result = bytearray(RECORD_PREFIX + RECORD_MARKER + _canonical_inline(header) + MARKER_END)
    for message_index, message in enumerate(messages):
        if message["body"] is None:
            continue
        body = message["body"].encode("utf-8")
        descriptor = {"byte_length": len(body), "message_id": message["message_id"]}
        if custody_version is not None:
            descriptor.update({
                "content_id": message["body_custody"]["content_id"],
                "sha256": sha256_bytes(body),
            })
        result.extend(MESSAGE_MARKER + _canonical_inline(descriptor) + MARKER_END)
        result.extend(body)
    if custody_version is not None:
        content_by_id = {
            outcome["content_id"]: outcome["extracted_text"]
            for message in messages
            for outcome in [*message["attachments"], *message["resources"]]
            if outcome["outcome"] == "extracted"
        }
        if custody_version == 2:
            content_by_id.update({
                item["content_id"]: item["text"]
                for message in messages for item in message["mime_contents"]
                if message["body_custody"] is None or item["content_id"] != message["body_custody"]["content_id"]
            })
        for descriptor in [*mime_content_frames, *extracted_content_frames]:
            text = content_by_id[descriptor["content_id"]].encode("utf-8")
            result.extend(CONTENT_MARKER + _canonical_inline(descriptor) + MARKER_END)
            result.extend(text)
    return bytes(result)


def parse_v2_record(data: bytes) -> CatalogRecord:
    """Parse byte-counted frames without interpreting body headings or delimiters."""
    if not data.startswith(RECORD_PREFIX):
        raise CatalogError("record is not a v2 source catalog record")
    header, offset = _read_marker(data, len(RECORD_PREFIX), RECORD_MARKER, "record")
    if header.get("format_version") != 2 or not isinstance(header.get("messages"), list):
        raise CatalogError("record header is not a complete v2 catalog header")
    custody_version = header.get("custody_version")
    if custody_version not in {None, 1, 2}:
        raise CatalogError("record has an unsupported custody version")
    frames = header.get("content_frames") if custody_version in {1, 2} else None
    if custody_version in {1, 2} and (not isinstance(frames, list) or not frames):
        raise CatalogError("custody record lacks ordered content frames")
    bodies: list[tuple[str, str]] = []
    contents: list[tuple[str, str]] = []
    body_frames = [frame for frame in frames or [] if isinstance(frame, Mapping) and frame.get("content_kind") == "body"]
    expected_body_count = sum(
        1 for item in header["messages"]
        if isinstance(item, Mapping) and item.get("body_custody") is not None
    ) if custody_version == 2 else len(header["messages"])
    if custody_version in {1, 2} and len(body_frames) != expected_body_count:
        raise CatalogError("custody record body-frame inventory is incomplete")
    for expected in header["messages"]:
        if not isinstance(expected, dict) or not isinstance(expected.get("message_id"), str):
            raise CatalogError("record header has invalid ordered message metadata")
        if custody_version == 2 and expected.get("body_custody") is None:
            continue
        descriptor, offset = _read_marker(data, offset, MESSAGE_MARKER, "message")
        message_id = descriptor.get("message_id")
        length = descriptor.get("byte_length")
        if message_id != expected["message_id"] or not isinstance(length, int) or length < 0:
            raise CatalogError("message frame does not match ordered header metadata")
        body = data[offset:offset + length]
        if len(body) != length:
            raise CatalogError("message frame is shorter than its declared UTF-8 byte length")
        try:
            decoded = body.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise CatalogError("message body is not UTF-8") from exc
        if custody_version in {1, 2}:
            body_custody = expected.get("body_custody")
            if not isinstance(body_custody, Mapping):
                raise CatalogError("custody record message lacks body metadata")
            content_id = descriptor.get("content_id")
            matching = [frame for frame in body_frames if frame.get("content_id") == content_id]
            if (
                content_id != body_custody.get("content_id")
                or descriptor.get("sha256") != sha256_bytes(body)
                or body_custody.get("plaintext_sha256") != sha256_bytes(body)
                or len(matching) != 1
                or dict(matching[0]) != {
                    "content_id": content_id,
                    "content_kind": "body",
                    "source_message_id": message_id,
                    "byte_length": length,
                    "sha256": sha256_bytes(body),
                }
            ):
                raise CatalogError("message body frame disagrees with custody metadata")
            contents.append((content_id, decoded))
        bodies.append((message_id, decoded))
        offset += length
    if custody_version in {1, 2}:
        seen_content_ids = {content_id for content_id, _text in contents}
        for expected in frames:
            if not isinstance(expected, Mapping):
                raise CatalogError("content-frame inventory entry is malformed")
            if expected.get("content_kind") == "body":
                continue
            allowed_kinds = {"attachment", "resource"}
            if custody_version == 2:
                allowed_kinds |= {"body_supplement", "html_evidence"}
            if expected.get("content_kind") not in allowed_kinds:
                raise CatalogError("content-frame inventory has an invalid kind")
            descriptor, offset = _read_marker(data, offset, CONTENT_MARKER, "content")
            if descriptor != dict(expected):
                raise CatalogError("content frame does not match ordered custody metadata")
            content_id = descriptor.get("content_id")
            length = descriptor.get("byte_length")
            if (
                not isinstance(content_id, str) or not content_id
                or content_id in seen_content_ids or not isinstance(length, int)
                or length < (0 if expected.get("content_kind") in {"body_supplement", "html_evidence"} else 1)
            ):
                raise CatalogError("content frame has invalid identity or length")
            text_bytes = data[offset:offset + length]
            if len(text_bytes) != length:
                raise CatalogError("content frame is shorter than its declared UTF-8 byte length")
            if descriptor.get("sha256") != sha256_bytes(text_bytes):
                raise CatalogError("content frame hash disagrees with its exact bytes")
            try:
                text = text_bytes.decode("utf-8", errors="strict")
            except UnicodeDecodeError as exc:
                raise CatalogError("content frame is not UTF-8") from exc
            contents.append((content_id, text))
            seen_content_ids.add(content_id)
            offset += length
        declared_ids = [frame.get("content_id") for frame in frames]
        if declared_ids != [content_id for content_id, _text in contents]:
            raise CatalogError("parsed content order disagrees with custody inventory")
    if offset != len(data):
        raise CatalogError("record has trailing bytes outside declared message frames")
    record = CatalogRecord(header, tuple(bodies), tuple(contents), sha256_bytes(data))
    if custody_version in {1, 2}:
        verified_catalog_contents(record)
    return record


def verified_catalog_contents(record: CatalogRecord) -> tuple[dict[str, Any], ...]:
    """Dereference typed, hashed body/extraction frames from one parsed record."""
    custody_version = record.header.get("custody_version")
    if custody_version not in {1, 2}:
        raise CatalogError("catalog record lacks typed source custody")
    messages = record.header.get("messages")
    frames = record.header.get("content_frames")
    if not isinstance(messages, list) or not isinstance(frames, list):
        raise CatalogError("catalog custody inventories are malformed")
    bodies = dict(record.bodies)
    content_text = dict(record.contents)
    if len(content_text) != len(record.contents):
        raise CatalogError("catalog content frames have duplicate identities")
    frames_by_id: dict[str, dict[str, Any]] = {}
    for frame in frames:
        if not isinstance(frame, Mapping):
            raise CatalogError("catalog content frame metadata is malformed")
        content_id = frame.get("content_id")
        if not isinstance(content_id, str) or not content_id or content_id in frames_by_id:
            raise CatalogError("catalog content frame metadata has duplicate identity")
        frames_by_id[content_id] = dict(frame)
    entries: list[dict[str, Any]] = []
    used: set[str] = set()
    for message_ordinal, header_message in enumerate(messages):
        if not isinstance(header_message, Mapping):
            raise CatalogError("catalog message metadata is malformed")
        message_id = header_message.get("message_id")
        body = bodies.get(message_id)
        if not isinstance(message_id, str) or (custody_version == 1 and body is None):
            raise CatalogError("catalog message body cannot be dereferenced")
        reconstructed = dict(header_message)
        reconstructed["body"] = body
        if custody_version == 2:
            raw_mime_contents = reconstructed.get("mime_contents")
            if not isinstance(raw_mime_contents, list):
                raise CatalogError("catalog message lacks MIME content metadata")
            reconstructed["mime_contents"] = [
                {**dict(item), "text": content_text.get(item.get("content_id"))}
                for item in raw_mime_contents if isinstance(item, Mapping)
            ]
            if len(reconstructed["mime_contents"]) != len(raw_mime_contents):
                raise CatalogError("catalog MIME content metadata is malformed")
        for collection in ("attachments", "resources"):
            outcomes = reconstructed.get(collection)
            if not isinstance(outcomes, list):
                raise CatalogError("catalog content outcomes are malformed")
            restored: list[dict[str, Any]] = []
            for outcome in outcomes:
                if not isinstance(outcome, Mapping):
                    raise CatalogError("catalog content outcome is malformed")
                item = dict(outcome)
                item["extracted_text"] = content_text.get(item.get("content_id")) if item.get("outcome") == "extracted" else None
                restored.append(item)
            reconstructed[collection] = restored
        _validate_custody_message(reconstructed)
        body_custody = reconstructed["body_custody"]
        body_id = body_custody["content_id"] if isinstance(body_custody, Mapping) else None
        body_bytes = body.encode("utf-8") if isinstance(body, str) else None
        if body_id is not None and body_bytes is not None:
            body_frame = frames_by_id.get(body_id)
            if body_frame != {
                "content_id": body_id,
                "content_kind": "body",
                "source_message_id": message_id,
                "byte_length": len(body_bytes),
                "sha256": sha256_bytes(body_bytes),
            }:
                raise CatalogError("catalog body frame cannot be dereferenced exactly")
        if custody_version == 1:
            ordered_mime_contents = [{
                "content_id": body_id, "content_kind": "body", "text": body,
                "sha256": sha256_bytes(body_bytes), "custody": dict(body_custody),
                "disposition": "interpret", "source_part_id": body_custody["selected_part_id"],
                "provider_part_id": body_custody["selected_part_id"], "mime_type": "text/plain",
                "duplicate_of_part_id": None, "byte_length": len(body_bytes),
            }]
        else:
            ordered_mime_contents = reconstructed["mime_contents"]
        content_ordinal = 0
        for mime_content in ordered_mime_contents:
            content_id = mime_content["content_id"]
            text = mime_content["text"]
            encoded = text.encode("utf-8")
            frame = frames_by_id.get(content_id)
            expected_frame = {
                "content_id": content_id,
                "content_kind": mime_content["content_kind"],
                "source_message_id": message_id,
                "byte_length": len(encoded),
                "sha256": sha256_bytes(encoded),
            }
            if frame != expected_frame:
                raise CatalogError("catalog MIME content frame cannot be dereferenced exactly")
            used.add(content_id)
            entries.append({
                "content_id": content_id,
                "content_kind": mime_content["content_kind"],
                "source_message_id": message_id,
                "message_ordinal": message_ordinal,
                "content_ordinal": content_ordinal,
                "received_at": reconstructed["received_at"],
                "received_date": reconstructed["received_date"],
                "sha256": sha256_bytes(encoded),
                "text": text,
                "provenance": {
                    "mime_type": mime_content["mime_type"],
                    "disposition": mime_content["disposition"],
                    "source_part_id": mime_content["source_part_id"],
                    "provider_part_id": mime_content["provider_part_id"],
                    "duplicate_of_part_id": mime_content["duplicate_of_part_id"],
                    "custody": deepcopy(mime_content["custody"]),
                },
            })
            content_ordinal += 1
        for kind, collection in (("attachment", "attachments"), ("resource", "resources")):
            for outcome in reconstructed[collection]:
                if outcome["outcome"] != "extracted":
                    continue
                content_id = outcome["content_id"]
                text = outcome["extracted_text"]
                encoded = text.encode("utf-8")
                if frames_by_id.get(content_id) != {
                    "content_id": content_id,
                    "content_kind": kind,
                    "source_message_id": message_id,
                    "byte_length": len(encoded),
                    "sha256": sha256_bytes(encoded),
                }:
                    raise CatalogError("catalog extraction frame cannot be dereferenced exactly")
                used.add(content_id)
                provenance = {key: value for key, value in outcome.items() if key != "extracted_text"}
                entries.append({
                    "content_id": content_id,
                    "content_kind": kind,
                    "source_message_id": message_id,
                    "message_ordinal": message_ordinal,
                    "content_ordinal": content_ordinal,
                    "received_at": reconstructed["received_at"],
                    "received_date": reconstructed["received_date"],
                    "sha256": sha256_bytes(encoded),
                    "text": text,
                    "provenance": provenance,
                })
                content_ordinal += 1
    if used != set(frames_by_id) or used != set(content_text):
        raise CatalogError("catalog contains unreferenced or missing content frames")
    return tuple(entries)


def validate_source_to_record(data: bytes, source_bodies: Mapping[str, Any]) -> list[str]:
    """Prove exact ordered adapter bodies against a parsed v2 record."""
    try:
        parsed = parse_v2_record(data)
    except CatalogError as exc:
        return [str(exc)]
    errors: list[str] = []
    if source_bodies.get("schema_version") == 1 and isinstance(source_bodies.get("messages"), list):
        from .mime_accounting import accounting_sha256
        content_text = dict(parsed.contents)
        header_messages = parsed.header.get("messages")
        if not isinstance(header_messages, list):
            return ["catalog header message inventory is malformed"]
        expected_messages = source_bodies["messages"]
        if len(expected_messages) != len(header_messages):
            errors.append("ordered message count differs")
        if [item.get("message_id") for item in header_messages] != [item.get("message_id") for item in expected_messages if isinstance(item, Mapping)]:
            errors.append("ordered message IDs differ")
        for expected, header in zip(expected_messages, header_messages):
            if not isinstance(expected, Mapping) or not isinstance(header, Mapping):
                errors.append("source snapshot message is malformed")
                continue
            accounting = header.get("mime_accounting")
            if not isinstance(accounting, Mapping) or expected.get("accounting_sha256") != accounting_sha256(accounting):
                errors.append(f"message {expected.get('message_id')!r} accounting differs")
            contents = expected.get("contents")
            if not isinstance(contents, list):
                errors.append(f"message {expected.get('message_id')!r} content snapshot is malformed")
                continue
            declared_contents = header.get("mime_contents")
            if not isinstance(declared_contents, list) or [item.get("content_id") for item in declared_contents if isinstance(item, Mapping)] != [item.get("content_id") for item in contents if isinstance(item, Mapping)]:
                errors.append(f"message {expected.get('message_id')!r} ordered content IDs differ")
            for item in contents:
                if not isinstance(item, Mapping):
                    errors.append("source snapshot content is malformed")
                    continue
                content_id = item.get("content_id")
                text = item.get("text")
                if not isinstance(content_id, str) or content_text.get(content_id) != text:
                    errors.append(f"content {content_id!r} is missing or not verbatim")
                elif item.get("sha256") != sha256_bytes(text.encode("utf-8")):
                    errors.append(f"content {content_id!r} source hash disagrees")
        return errors
    catalogued = dict(parsed.bodies)
    if list(message_id for message_id, _body in parsed.bodies) != list(source_bodies):
        errors.append("ordered message IDs differ")
    for message_id, body in source_bodies.items():
        if message_id not in catalogued:
            errors.append(f"message {message_id!r} is missing from the raw-message section")
        elif catalogued[message_id] != body:
            errors.append(f"message {message_id!r} body is not verbatim")
    return errors


def verify_persisted_record(source_bodies: Mapping[str, Any], intended: bytes, persisted: bytes) -> None:
    """Require independent source equality and intended-byte readback equality."""
    errors = validate_source_to_record(intended, source_bodies)
    if errors:
        raise CatalogError("source-to-record verification failed: " + "; ".join(errors))
    if persisted != intended:
        raise CatalogError("intended-to-persisted byte verification failed")


def recover_catalog_index(
    source_bodies: Mapping[str, Any], intended: bytes, persisted: bytes,
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
