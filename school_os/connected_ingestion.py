"""Concrete, bounded connector-to-catalog ingestion for an admitted instance.

This module is intentionally not a daily-operation framework.  It owns just
the source unit between a complete Gmail conversation and the durable catalog,
semantic, Fact, audit, index, and continuation artifacts.  Provider adapters
must return the explicitly documented normalized source shapes below; no
success flag supplied by a connector is trusted as verification.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Protocol

from .adapters import Page, ReadResult
from .catalog import (
    build_catalog_message,
    parse_v2_record,
    recover_catalog_index,
    serialize_v2_record,
    stable_record_id,
)
from .contracts import canonical_json_bytes, sha256_bytes, validate
from .connected_storage import (
    ArtifactStore,
    CodexDriveArtifactStore,
    ConnectedStorageError,
    DriveReference,
    StoredArtifact,
)
from .importer import (
    AttachmentExtraction,
    AttachmentRead,
    DirectResourceOutcome,
    ImportError,
    admit_exact_plaintext_representation,
    discover_direct_html_resources,
    enumerate_conversations,
    next_import_batch,
    process_attachments,
    process_direct_html_resources,
    require_complete_message_coverage,
)
from .semantic import (
    interpret_packet,
    semantic_packet_from_verified_record,
    validate_independent_audit,
)
from .gmail_source import decode_raw_rfc2822
from .mime_accounting import accounting_sha256
from .tasks import canonical_task_id


ConnectedIngestionError = ConnectedStorageError


class SourcePort(Protocol):
    """A normalized, complete Gmail source adapter.

    ``read_conversation`` must return ``conversation_id`` and every ordered
    member in ``messages``.  Each member must contain ``message_id``,
    ``received_at``, ``received_date``, ``gmail_internal_date_ms``,
    ``mime_tree_complete``, ``parts``, and
    ``attachments``.  ``parts`` are the exact adapter-returned MIME part bytes
    accepted by :func:`admit_exact_plaintext_representation`; it is not HTML
    converted text.  The port's concrete Gmail adapter is responsible for
    making a provider-designated plaintext selection and all transfer/charset
    custody fields explicit.
    """

    def search(self, scope: Mapping[str, Any], page_token: str | None) -> Page: ...
    def read_conversation(self, conversation_id: str) -> Mapping[str, Any]: ...
    def read_attachment(self, message_id: str, attachment_id: str) -> ReadResult | AttachmentRead: ...


Interpreter = Callable[[Mapping[str, Any]], Mapping[str, Any]]
Auditor = Callable[[Mapping[str, Any], Mapping[str, Any]], Mapping[str, Any]]


class CodexGmailSourceAdapter:
    """Bind fixed Gmail bridge calls to the source worker's complete port.

    Gmail's connector result is deliberately kept provider-shaped until the two
    supplied *narrow* normalizers run.  ``normalize_message`` receives the
    exact ``full`` and ``raw`` results for one full-thread member and must
    return the ``SourcePort`` message shape documented above.  It cannot alter
    the member ID or thread ID that this adapter has already verified.  The
    selected adapter can therefore establish MIME transfer/charset custody
    without storing raw MIME as a second canonical record.  PDF/image
    extraction is not fabricated here: an attachment normalizer may return a
    provider-backed :class:`AttachmentRead`, otherwise the importer produces a
    visible unresolved outcome.
    """

    def __init__(
        self, gmail: Any, *, max_thread_messages: int,
        normalize_message: Callable[[Mapping[str, Any], Mapping[str, Any]], Mapping[str, Any]],
        normalize_attachment: Callable[[str, str, Mapping[str, Any]], ReadResult | AttachmentRead],
        capture_raw_message: Callable[[str, str, bytes], None] | None = None,
        capture_attachment: Callable[[str, str, ReadResult | AttachmentRead], None] | None = None,
    ) -> None:
        if max_thread_messages < 1:
            raise ConnectedIngestionError("Gmail full-thread bound must be positive")
        self.gmail = gmail
        self.max_thread_messages = max_thread_messages
        self.normalize_message = normalize_message
        self.normalize_attachment = normalize_attachment
        self.capture_raw_message = capture_raw_message
        self.capture_attachment = capture_attachment
        self._discovery_by_thread: dict[str, set[str]] = {}

    @staticmethod
    def _full_identity(value: Any, label: str) -> tuple[str, str]:
        if not isinstance(value, Mapping):
            raise ConnectedIngestionError(f"Gmail {label} result is malformed")
        message_id = value.get("id")
        thread_id = value.get("thread_id")
        if not isinstance(message_id, str) or not message_id or not isinstance(thread_id, str) or not thread_id:
            raise ConnectedIngestionError(f"Gmail {label} result lacks exact message/thread identity")
        return message_id, thread_id

    def search(self, scope: Mapping[str, Any], page_token: str | None) -> Page:
        query = scope.get("query")
        labels = scope.get("label_ids", [])
        max_results = scope.get("max_results")
        if (
            not isinstance(query, str) or not query
            or not isinstance(labels, list) or any(not isinstance(item, str) or not item for item in labels)
            or isinstance(max_results, bool) or not isinstance(max_results, int) or max_results < 1
        ):
            raise ConnectedIngestionError("Gmail source scope lacks bounded query, labels, or page size")
        for key in ("seed_after_inclusive_ms", "seed_before_exclusive_ms"):
            bound = scope.get(key)
            if bound is not None and (
                isinstance(bound, bool) or not isinstance(bound, int) or bound < 0
            ):
                raise ConnectedIngestionError("Gmail seed bounds must be nonnegative epoch milliseconds")
        if (
            scope.get("seed_after_inclusive_ms") is not None
            and scope.get("seed_before_exclusive_ms") is not None
            and scope["seed_after_inclusive_ms"] >= scope["seed_before_exclusive_ms"]
        ):
            raise ConnectedIngestionError("Gmail seed interval must have positive width")
        start = scope.get("seed_after_inclusive_ms")
        end = scope.get("seed_before_exclusive_ms")
        provider_query = query
        if start is not None or end is not None:
            if re.search(r"(?i)(?:after|before|older|newer|older_than|newer_than):", query):
                raise ConnectedIngestionError("exact Gmail seed bounds cannot be combined with a provider date predicate")
            predicates = []
            if start is not None:
                predicates.append(f"after:{max(0, start // 1000 - 1)}")
            if end is not None:
                predicates.append(f"before:{end // 1000 + 1}")
            provider_query = " ".join((query, *predicates))
        arguments: dict[str, Any] = {"query": provider_query, "label_ids": list(labels), "max_results": max_results}
        if page_token is not None:
            arguments["next_page_token"] = page_token
        result = self.gmail.search_ids(**arguments)
        if not isinstance(result, Mapping):
            raise ConnectedIngestionError("Gmail search result is malformed")
        raw_ids, next_token = result.get("message_ids"), result.get("next_page_token")
        if not isinstance(raw_ids, list) or any(not isinstance(item, str) or not item for item in raw_ids):
            raise ConnectedIngestionError("Gmail search result lacks complete message identities")
        if next_token is not None and (not isinstance(next_token, str) or not next_token):
            raise ConnectedIngestionError("Gmail search result has an invalid next page token")
        items: list[dict[str, Any]] = []
        for message_id in raw_ids:
            full = self.gmail.read(message_id, "full")
            observed_id, thread_id = self._full_identity(full, "full-message")
            if observed_id != message_id:
                raise ConnectedIngestionError("Gmail full-message identity disagrees with search")
            if start is not None or end is not None:
                raw_timestamp = full.get("internal_date")
                if not isinstance(raw_timestamp, str) or len(raw_timestamp) != 13 or not raw_timestamp.isascii() or not raw_timestamp.isdecimal():
                    raise ConnectedIngestionError("Gmail discovery hit lacks exact epoch-millisecond internal date")
                timestamp = int(raw_timestamp)
                if start is not None and timestamp < start:
                    continue
                if end is not None and timestamp >= end:
                    continue
            discovered = self._discovery_by_thread.setdefault(thread_id, set())
            discovered.add(message_id)
            # The byte estimate is intentionally one: the immutable worker
            # later enforces its bound against actual complete catalog bytes,
            # rather than trusting a provider size estimate for a conversation.
            items.append({"conversation_id": thread_id, "byte_size": 1, "discovery_message_ids": [message_id]})
        return Page(tuple(items), next_token)

    def read_conversation(self, conversation_id: str) -> Mapping[str, Any]:
        result = self.gmail.read_thread(conversation_id, max_messages=self.max_thread_messages)
        if not isinstance(result, Mapping):
            raise ConnectedIngestionError("Gmail full-thread result is malformed")
        thread_id = result.get("id") or result.get("threadId")
        members = result.get("messages")
        if (
            thread_id != conversation_id or not isinstance(members, list) or not members
            or len(members) >= self.max_thread_messages
        ):
            raise ConnectedIngestionError("Gmail full-thread identity or membership is incomplete")
        normalized: list[dict[str, Any]] = []
        member_ids: set[str] = set()
        for full in members:
            message_id, observed_thread = self._full_identity(full, "full-thread member")
            if observed_thread != conversation_id or message_id in member_ids:
                raise ConnectedIngestionError("Gmail full-thread member identity is ambiguous")
            raw = self.gmail.read(message_id, "raw")
            raw_message_id, raw_thread_id = self._full_identity(raw, "raw-body")
            if raw_message_id != message_id or raw_thread_id != conversation_id:
                raise ConnectedIngestionError("Gmail raw-body message/thread identity disagrees with full-thread member")
            raw_bytes = (
                decode_raw_rfc2822(raw.get("raw"))
                if self.capture_raw_message is not None else None
            )
            item = self.normalize_message(full, raw)
            if (
                not isinstance(item, Mapping)
                or item.get("message_id") != message_id
                or item.get("thread_id") != conversation_id
            ):
                raise ConnectedIngestionError("Gmail MIME normalizer changed the exact message/thread identity")
            if self.capture_raw_message is not None:
                assert raw_bytes is not None
                self.capture_raw_message(message_id, conversation_id, raw_bytes)
            normalized.append(dict(item))
            member_ids.add(message_id)
        if not self._discovery_by_thread.get(conversation_id, set()) <= member_ids:
            raise ConnectedIngestionError("Gmail full thread omits a discovered source message")
        return {"conversation_id": conversation_id, "messages": normalized}

    def read_attachment(self, message_id: str, attachment_id: str) -> ReadResult | AttachmentRead:
        raw = self.gmail.read_attachment(message_id, attachment_id)
        if not isinstance(raw, Mapping):
            raise ConnectedIngestionError("Gmail attachment result is malformed")
        result = self.normalize_attachment(message_id, attachment_id, raw)
        if not isinstance(result, (ReadResult, AttachmentRead)) or result.identity != attachment_id:
            raise ConnectedIngestionError("Gmail attachment normalizer changed the exact attachment identity")
        if self.capture_attachment is not None:
            self.capture_attachment(message_id, attachment_id, result)
        return result


@dataclass(frozen=True)
class CodexSemanticCallbacks:
    """Use the bridge's fixed semantic interpreter and independent-audit calls."""

    semantic: Any

    def interpret(self, packet: Mapping[str, Any]) -> Mapping[str, Any]:
        result = self.semantic.interpret(packet)
        if not isinstance(result, Mapping):
            raise ConnectedIngestionError("semantic interpreter bridge result is malformed")
        return result

    def audit(self, packet: Mapping[str, Any], interpretation: Mapping[str, Any]) -> Mapping[str, Any]:
        result = self.semantic.audit(packet, interpretation)
        if not isinstance(result, Mapping):
            raise ConnectedIngestionError("semantic audit bridge result is malformed")
        return result


@dataclass(frozen=True)
class IngestionArtifacts:
    catalog: StoredArtifact
    interpretation: StoredArtifact
    audit: StoredArtifact
    facts: StoredArtifact


@dataclass(frozen=True)
class DiscoveryResult:
    """One exact, body-free Gmail search inventory for a single catalog run."""

    inventory: StoredArtifact
    scope_sha256: str
    conversation_ids: tuple[str, ...]

    def as_stage_result(self) -> dict[str, Any]:
        return {
            "verified": True,
            "phase": "discover",
            "phase_complete": True,
            "discovery_inventory": _artifact_pointer(self.inventory),
            "scope_sha256": self.scope_sha256,
            "conversation_ids": list(self.conversation_ids),
        }


@dataclass(frozen=True)
class IngestionResult:
    """One verified bounded catalog result; eligible cursors are output only."""

    verified: bool
    phase_complete: bool
    completed_units: tuple[str, ...]
    remaining_work: dict[str, Any]
    work: StoredArtifact
    index: StoredArtifact
    artifacts: tuple[IngestionArtifacts, ...]
    discovery: StoredArtifact
    proposed_cursor: dict[str, Any] | None

    def as_stage_result(self) -> dict[str, Any]:
        return {
            "verified": self.verified,
            "phase": "catalog",
            "phase_complete": self.phase_complete,
            "completed_units": list(self.completed_units),
            "remaining_work": dict(self.remaining_work),
            "progressed": bool(self.artifacts),
            "source_work": _artifact_pointer(self.work),
            "catalog_index": _artifact_pointer(self.index),
            "discovery_inventory": _artifact_pointer(self.discovery),
            "proposed_source_cursor": None if self.proposed_cursor is None else dict(self.proposed_cursor),
            "records": [
                {
                    "catalog": _artifact_pointer(item.catalog),
                    "interpretation": _artifact_pointer(item.interpretation),
                    "audit": _artifact_pointer(item.audit),
                    "facts": _artifact_pointer(item.facts),
                }
                for item in self.artifacts
            ],
        }


@dataclass(frozen=True)
class CurrentCatalogView:
    """All audited Facts admitted by the verified current catalog index."""

    index: StoredArtifact
    artifacts: tuple[IngestionArtifacts, ...]
    facts: tuple[dict[str, Any], ...]
    source_record_map: dict[str, dict[str, Any]]
    task_source_links: dict[str, str]
    current_guideline_selection: tuple[dict[str, Any], ...]


def _artifact_pointer(item: StoredArtifact) -> dict[str, Any]:
    return {
        "object_id": item.reference.object_id,
        "parent_id": item.reference.parent_id,
        "mime_type": item.reference.mime_type,
        "url": item.reference.url,
        "version": item.reference.version,
        "sha256": sha256_bytes(item.data),
        "byte_length": len(item.data),
    }


def _json_object(data: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ConnectedIngestionError(f"{label} is not UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise ConnectedIngestionError(f"{label} must be a JSON object")
    return value


def _work_continuation(data: bytes) -> dict[str, Any]:
    """Read run-scoped catalog work; this is never an eligible source cursor."""
    value = _json_object(data, "source work continuation")
    allowed = {"schema_version", "completed_conversation_ids", "units", "discovery_sha256"}
    if not set(value) <= allowed or not {"schema_version", "completed_conversation_ids", "units"} <= set(value) or value["schema_version"] != 1:
        raise ConnectedIngestionError("source work continuation has an unsupported shape")
    completed = value["completed_conversation_ids"]
    units = value["units"]
    if (
        not isinstance(completed, list)
        or any(not isinstance(item, str) or not item for item in completed)
        or len(completed) != len(set(completed))
        or not isinstance(units, list)
    ):
        raise ConnectedIngestionError("source work continuation has invalid completed units")
    unit_ids: set[str] = set()
    for unit in units:
        unit_allowed = {
            "conversation_id", "record_id", "record_sha256", "fact_ids",
            "discovery_message_ids", "full_message_ids",
        }
        if not isinstance(unit, Mapping) or not set(unit) <= unit_allowed or not {
            "conversation_id", "record_id", "record_sha256", "fact_ids"
        } <= set(unit):
            raise ConnectedIngestionError("source work continuation unit has an unsupported shape")
        conversation_id = unit.get("conversation_id")
        record_id = unit.get("record_id")
        digest = unit.get("record_sha256")
        fact_ids = unit.get("fact_ids")
        if (
            not isinstance(conversation_id, str) or not conversation_id
            or not isinstance(record_id, str) or not record_id
            or not isinstance(digest, str) or len(digest) != 64
            or any(character not in "0123456789abcdef" for character in digest)
            or not isinstance(fact_ids, list) or any(not isinstance(item, str) or not item for item in fact_ids)
            or len(fact_ids) != len(set(fact_ids))
            or conversation_id in unit_ids
        ):
            raise ConnectedIngestionError("source work continuation unit has invalid identity evidence")
        for key in ("discovery_message_ids", "full_message_ids"):
            identities = unit.get(key, [])
            if (
                not isinstance(identities, list)
                or any(not isinstance(item, str) or not item for item in identities)
                or len(identities) != len(set(identities))
            ):
                raise ConnectedIngestionError("source work continuation unit has invalid membership evidence")
        unit_ids.add(conversation_id)
    if unit_ids != set(completed):
        raise ConnectedIngestionError("source work continuation identities and units disagree")
    discovery_sha256 = value.get("discovery_sha256")
    if discovery_sha256 is not None and (
        not isinstance(discovery_sha256, str) or len(discovery_sha256) != 64 or any(
            character not in "0123456789abcdef" for character in discovery_sha256
        )
    ):
        raise ConnectedIngestionError("source work continuation has invalid discovery evidence")
    result = {
        "schema_version": 1,
        "completed_conversation_ids": list(completed),
        "units": [dict(item) for item in units],
    }
    result["discovery_sha256"] = discovery_sha256
    return result


def _require_string(value: Mapping[str, Any], key: str, label: str) -> str:
    candidate = value.get(key)
    if not isinstance(candidate, str) or not candidate:
        raise ConnectedIngestionError(f"{label} lacks {key}")
    return candidate


def _conversation_messages(
    source: SourcePort, conversation: Mapping[str, Any], *, max_attachment_bytes: int,
    supported_attachment_mime_types: Sequence[str], attachment_extractors: Mapping[str, Callable[[ReadResult], AttachmentExtraction]],
    excluded_attachment_mime_types: Mapping[str, str],
    resource_fetcher: Callable[[str], Any] | None,
    resource_extractors: Mapping[str, Callable[[Any], AttachmentExtraction]],
    excluded_resource_origins: Mapping[str, str],
    max_resource_bytes: int, max_resource_redirects: int,
    readback: Mapping[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    conversation_id = _require_string(conversation, "conversation_id", "enumerated conversation")
    raw = source.read_conversation(conversation_id) if readback is None else readback
    if raw.get("conversation_id") != conversation_id:
        raise ConnectedIngestionError("full conversation identity disagrees with enumeration")
    members = raw.get("messages")
    if not isinstance(members, list) or not members:
        raise ConnectedIngestionError("full conversation has no complete ordered members")
    required_hits = conversation.get("discovery_message_ids", [])
    if not isinstance(required_hits, list) or any(not isinstance(item, str) or not item for item in required_hits):
        raise ConnectedIngestionError("enumerated conversation has malformed discovery identities")
    seen_messages: set[str] = set()
    rendered: list[dict[str, Any]] = []
    source_snapshot: dict[str, Any] = {"schema_version": 1, "messages": []}
    legacy_source_bodies: dict[str, str] = {}
    accounted_mode: bool | None = None
    for member in members:
        if not isinstance(member, Mapping):
            raise ConnectedIngestionError("full conversation message is malformed")
        message_id = _require_string(member, "message_id", "full conversation message")
        if message_id in seen_messages:
            raise ConnectedIngestionError("full conversation repeats a message identity")
        seen_messages.add(message_id)
        received_at = _require_string(member, "received_at", "full conversation message")
        received_date = _require_string(member, "received_date", "full conversation message")
        parts = member.get("parts")
        if not isinstance(parts, Sequence) or isinstance(parts, (str, bytes)):
            raise ConnectedIngestionError("full conversation message has no normalized MIME parts")
        admission = admit_exact_plaintext_representation(parts, mime_tree_complete=member.get("mime_tree_complete"))
        if admission.outcome != "admitted" or admission.plaintext is None:
            accounting_candidate = member.get("mime_accounting")
            if not isinstance(accounting_candidate, Mapping) or accounting_candidate.get("primary_content_id") is not None:
                raise ConnectedIngestionError(f"message {message_id} did not admit: {admission.reason}")
            admission = None
        attachments = member.get("attachments")
        if not isinstance(attachments, Sequence) or isinstance(attachments, (str, bytes)):
            raise ConnectedIngestionError("full conversation message has malformed attachment inventory")
        attachment_items = []
        for item in attachments:
            if not isinstance(item, Mapping):
                raise ConnectedIngestionError("attachment inventory item is malformed")
            copied = dict(item)
            copied["source_message_id"] = message_id
            attachment_items.append(copied)
        attachment_outcomes = process_attachments(
            attachment_items,
            read_attachment=lambda attachment_id: source.read_attachment(message_id, attachment_id),
            supported_mime_types=tuple(supported_attachment_mime_types),
            max_bytes=max_attachment_bytes,
            extractors=attachment_extractors,
            excluded_mime_types=excluded_attachment_mime_types,
        )
        resource_outcomes: tuple[DirectResourceOutcome, ...] = ()
        html_parts = member.get("html_parts", [])
        if not isinstance(html_parts, Sequence) or isinstance(html_parts, (str, bytes)):
            raise ConnectedIngestionError("full conversation message has malformed HTML-part inventory")
        for html_part in html_parts:
            if not isinstance(html_part, Mapping):
                raise ConnectedIngestionError("HTML-part inventory item is malformed")
            resources = discover_direct_html_resources(message_id, html_part)
            if resources and resource_fetcher is None:
                raise ConnectedIngestionError("direct HTML resource retrieval is not bound on this runtime")
            if resources:
                exclusions = {
                    resource.resource_id: excluded_resource_origins[resource.origin]
                    for resource in resources
                    if resource.origin in excluded_resource_origins
                }
                resource_outcomes += process_direct_html_resources(
                    resources, fetch_resource=resource_fetcher,
                    extractors=resource_extractors, max_bytes=max_resource_bytes,
                    max_redirects=max_resource_redirects,
                    excluded_resources=exclusions,
                )
        try:
            require_complete_message_coverage(
                b"" if admission is None else admission.plaintext,
                attachment_outcomes, resource_outcomes,
            )
        except ImportError as exc:
            raise ConnectedIngestionError(f"message {message_id} has unresolved substantive source content: {exc}") from exc
        mime_accounting = member.get("mime_accounting")
        mime_contents = member.get("mime_contents")
        accounted = isinstance(mime_accounting, Mapping) and isinstance(mime_contents, Sequence)
        if accounted_mode is None:
            accounted_mode = accounted
        elif accounted_mode != accounted:
            raise ConnectedIngestionError("full conversation mixes accounted and legacy MIME messages")
        rendered.append(build_catalog_message(
            message_id=message_id, received_at=received_at, received_date=received_date,
            admission=admission, attachment_outcomes=attachment_outcomes,
            resource_outcomes=resource_outcomes,
            gmail_internal_date_ms=member.get("gmail_internal_date_ms"),
            mime_accounting=mime_accounting if accounted else None,
            mime_contents=mime_contents if accounted else None,
        ))
        if accounted:
            source_snapshot["messages"].append({
                "message_id": message_id,
                "accounting_sha256": accounting_sha256(mime_accounting),
                "contents": [
                    {
                        "content_id": item.get("content_id"),
                        "sha256": item.get("sha256"),
                        "text": item.get("text"),
                    }
                    for item in mime_contents if isinstance(item, Mapping)
                ],
            })
        else:
            legacy_source_bodies[message_id] = admission.plaintext.decode("utf-8", errors="strict")
    if not set(required_hits) <= seen_messages:
        raise ConnectedIngestionError("full conversation omits a discovery-hit message")
    return rendered, source_snapshot if accounted_mode else legacy_source_bodies


def _full_message_ids(
    source: SourcePort, conversation_id: str,
) -> tuple[Mapping[str, Any], tuple[str, ...]]:
    """Read one complete thread and retain its exact ordered member identities."""
    raw = source.read_conversation(conversation_id)
    if not isinstance(raw, Mapping) or raw.get("conversation_id") != conversation_id:
        raise ConnectedIngestionError("full conversation identity disagrees with enumeration")
    members = raw.get("messages")
    if not isinstance(members, list) or not members:
        raise ConnectedIngestionError("full conversation has no complete ordered members")
    identities: list[str] = []
    for member in members:
        if not isinstance(member, Mapping):
            raise ConnectedIngestionError("full conversation message is malformed")
        identities.append(_require_string(member, "message_id", "full conversation message"))
    if len(identities) != len(set(identities)):
        raise ConnectedIngestionError("full conversation repeats a message identity")
    return raw, tuple(identities)


def _scope_sha256(scope: Mapping[str, Any]) -> str:
    return sha256_bytes(canonical_json_bytes(dict(scope)))


def _discovery_inventory(source: SourcePort, scope: Mapping[str, Any]) -> dict[str, Any]:
    """Enumerate once and return the complete, body-free durable inventory."""
    hits: dict[str, set[str]] = {}
    pages: list[dict[str, Any]] = []

    def search(page_token: str | None) -> Page:
        page = source.search(scope, page_token)
        page_hits: list[dict[str, Any]] = []
        for raw in page.items:
            if not isinstance(raw, Mapping):
                raise ConnectedIngestionError("enumerated conversation is malformed")
            conversation_id = _require_string(raw, "conversation_id", "enumerated conversation")
            message_ids = raw.get("discovery_message_ids", [])
            if (
                not isinstance(message_ids, list)
                or not message_ids
                or any(not isinstance(item, str) or not item for item in message_ids)
            ):
                raise ConnectedIngestionError("enumerated conversation has no immutable discovery-hit identity")
            hits.setdefault(conversation_id, set()).update(message_ids)
            page_hits.append({
                "conversation_id": conversation_id,
                "message_ids": sorted(set(message_ids)),
            })
        pages.append({
            "page_token": page_token,
            "next_page_token": page.next_page_token,
            "hits": page_hits,
        })
        return page

    enumeration = enumerate_conversations(search)
    ordered_hits = {key: tuple(sorted(value)) for key, value in sorted(hits.items())}
    conversations: list[dict[str, Any]] = []
    for item in enumeration.conversations:
        copied = dict(item)
        conversation_id = _require_string(copied, "conversation_id", "enumerated conversation")
        byte_size = copied.get("byte_size")
        if isinstance(byte_size, bool) or not isinstance(byte_size, int) or byte_size < 0:
            raise ConnectedIngestionError("enumerated conversation has invalid byte-size evidence")
        conversations.append({
            "conversation_id": conversation_id,
            "byte_size": byte_size,
            "discovery_message_ids": list(ordered_hits.get(conversation_id, ())),
        })
    return {
        "schema_version": 1,
        "scope": dict(scope),
        "scope_sha256": _scope_sha256(scope),
        "page_tokens": list(enumeration.page_tokens),
        "pages": pages,
        "dispositions": [dict(item) for item in enumeration.dispositions],
        "hits": [
            {"conversation_id": key, "message_ids": list(value)}
            for key, value in ordered_hits.items()
        ],
        "conversations": conversations,
        # Catalog must re-read every selected thread, including a unit whose
        # stored hit IDs have not changed, before accepting prior work.
        "thread_recheck_conversation_ids": [item["conversation_id"] for item in conversations],
    }


def _discovery_from_artifact(data: bytes) -> tuple[dict[str, Any], list[dict[str, Any]], str]:
    """Validate the exact discovery artifact used by every catalog continuation."""
    value = _json_object(data, "discovery inventory")
    required = {
        "schema_version", "scope", "scope_sha256", "page_tokens", "pages",
        "dispositions", "hits", "conversations", "thread_recheck_conversation_ids",
    }
    if set(value) != required or value.get("schema_version") != 1 or not isinstance(value.get("scope"), Mapping):
        raise ConnectedIngestionError("discovery inventory has an unsupported shape")
    scope = dict(value["scope"])
    scope_sha256 = value.get("scope_sha256")
    if not isinstance(scope_sha256, str) or scope_sha256 != _scope_sha256(scope):
        raise ConnectedIngestionError("discovery inventory scope hash disagrees")
    tokens = value.get("page_tokens")
    if not isinstance(tokens, list) or not tokens or tokens[0] is not None or any(
        token is not None and (not isinstance(token, str) or not token) for token in tokens
    ) or len(tokens) != len(set(tokens)):
        raise ConnectedIngestionError("discovery inventory has invalid page-token evidence")
    pages = value.get("pages")
    if not isinstance(pages, list) or len(pages) != len(tokens):
        raise ConnectedIngestionError("discovery inventory has incomplete page evidence")
    page_hit_items: list[dict[str, Any]] = []
    for position, page in enumerate(pages):
        if not isinstance(page, Mapping) or set(page) != {"page_token", "next_page_token", "hits"} or page.get("page_token") != tokens[position]:
            raise ConnectedIngestionError("discovery inventory page evidence is malformed")
        next_token = page.get("next_page_token")
        if next_token is not None and (not isinstance(next_token, str) or not next_token):
            raise ConnectedIngestionError("discovery inventory page has invalid next token")
        if position + 1 < len(tokens) and next_token != tokens[position + 1]:
            raise ConnectedIngestionError("discovery inventory page order is incomplete")
        if position + 1 == len(tokens) and next_token is not None:
            raise ConnectedIngestionError("discovery inventory final page is incomplete")
        page_hits = page.get("hits")
        if not isinstance(page_hits, list):
            raise ConnectedIngestionError("discovery inventory page hits are malformed")
        for item in page_hits:
            if (
                not isinstance(item, Mapping) or set(item) != {"conversation_id", "message_ids"}
                or not isinstance(item.get("conversation_id"), str) or not item["conversation_id"]
                or not isinstance(item.get("message_ids"), list)
                or not item["message_ids"]
                or any(not isinstance(hit, str) or not hit for hit in item["message_ids"])
                or len(item["message_ids"]) != len(set(item["message_ids"]))
            ):
                raise ConnectedIngestionError("discovery inventory page hit is malformed")
            page_hit_items.append({
                "conversation_id": item["conversation_id"],
                "message_ids": list(item["message_ids"]),
            })
    dispositions = value.get("dispositions")
    if not isinstance(dispositions, list) or any(
        not isinstance(item, Mapping) or set(item) != {"conversation_id", "outcome"}
        or not isinstance(item.get("conversation_id"), str) or not item["conversation_id"]
        or item.get("outcome") not in {"included", "duplicate"}
        for item in dispositions
    ):
        raise ConnectedIngestionError("discovery inventory dispositions are malformed")
    conversations = value.get("conversations")
    if not isinstance(conversations, list):
        raise ConnectedIngestionError("discovery inventory conversations are malformed")
    normalized: list[dict[str, Any]] = []
    ids: list[str] = []
    for item in conversations:
        if not isinstance(item, Mapping) or set(item) != {"conversation_id", "byte_size", "discovery_message_ids"}:
            raise ConnectedIngestionError("discovery inventory conversation has an unsupported shape")
        conversation_id = _require_string(item, "conversation_id", "discovery inventory conversation")
        byte_size = item.get("byte_size")
        hits = item.get("discovery_message_ids")
        if (
            isinstance(byte_size, bool) or not isinstance(byte_size, int) or byte_size < 0
            or not isinstance(hits, list) or not hits
            or any(not isinstance(hit, str) or not hit for hit in hits)
            or len(hits) != len(set(hits))
        ):
            raise ConnectedIngestionError("discovery inventory conversation has invalid evidence")
        ids.append(conversation_id)
        normalized.append({"conversation_id": conversation_id, "byte_size": byte_size, "discovery_message_ids": list(hits)})
    if ids != sorted(ids) or len(ids) != len(set(ids)) or value.get("thread_recheck_conversation_ids") != ids:
        raise ConnectedIngestionError("discovery inventory thread recheck evidence is incomplete")
    expected_hits = [{"conversation_id": item["conversation_id"], "message_ids": item["discovery_message_ids"]} for item in normalized]
    if value.get("hits") != expected_hits:
        raise ConnectedIngestionError("discovery inventory hit evidence disagrees with conversations")
    page_seen: set[str] = set()
    expected_dispositions: list[dict[str, str]] = []
    page_hit_ids: dict[str, set[str]] = {}
    for item in page_hit_items:
        conversation_id = item["conversation_id"]
        expected_dispositions.append({
            "conversation_id": conversation_id,
            "outcome": "duplicate" if conversation_id in page_seen else "included",
        })
        page_seen.add(conversation_id)
        page_hit_ids.setdefault(conversation_id, set()).update(item["message_ids"])
    if dispositions != expected_dispositions or {
        conversation_id: sorted(message_ids) for conversation_id, message_ids in page_hit_ids.items()
    } != {item["conversation_id"]: item["discovery_message_ids"] for item in normalized}:
        raise ConnectedIngestionError("discovery inventory page evidence disagrees with durable hits")
    return scope, normalized, scope_sha256


def _named(
    store: ArtifactStore, parent: DriveReference, name: str, mime_type: str,
) -> StoredArtifact | None:
    artifact = store.read_named(parent, name)
    if artifact is not None and artifact.reference.mime_type != mime_type:
        raise ConnectedIngestionError(f"{name} has the wrong MIME type")
    return artifact


def _source_bodies_from_catalog(data: bytes) -> dict[str, Any]:
    record = parse_v2_record(data)
    if record.header.get("custody_version") == 2:
        text_by_id = dict(record.contents)
        return {
            "schema_version": 1,
            "messages": [
                {
                    "message_id": message["message_id"],
                    "accounting_sha256": accounting_sha256(message["mime_accounting"]),
                    "contents": [
                        {
                            "content_id": item["content_id"],
                            "sha256": item["sha256"],
                            "text": text_by_id[item["content_id"]],
                        }
                        for item in message["mime_contents"]
                    ],
                }
                for message in record.header["messages"]
            ],
        }
    return {message_id: body for message_id, body in record.bodies}


def _validated_interpretation(
    packet: Any, data: bytes, *, fact_schema: Mapping[str, Any],
    extraction_schema: Mapping[str, Any],
) -> dict[str, Any]:
    interpreted = _json_object(data, "semantic interpretation")
    if set(interpreted) != {"facts", "result", "packet_sha256", "interpreted_sha256"}:
        raise ConnectedIngestionError("semantic interpretation has an unsupported shape")
    facts = interpreted.get("facts")
    result = interpreted.get("result")
    if not isinstance(facts, list) or not isinstance(result, Mapping):
        raise ConnectedIngestionError("semantic interpretation is malformed")
    errors = validate(dict(result), dict(extraction_schema))
    for fact in facts:
        if not isinstance(fact, Mapping):
            raise ConnectedIngestionError("semantic interpretation Fact is malformed")
        errors.extend(validate(dict(fact), dict(fact_schema)))
    if errors:
        raise ConnectedIngestionError("semantic interpretation fails its schemas: " + "; ".join(errors))
    expected_hash = sha256_bytes(canonical_json_bytes({"facts": facts, "result": dict(result)}))
    if interpreted.get("interpreted_sha256") != expected_hash:
        raise ConnectedIngestionError("semantic interpretation content hash disagrees")
    expected_packet_hash = sha256_bytes(canonical_json_bytes(packet.as_mapping()))
    if interpreted.get("packet_sha256") != expected_packet_hash:
        raise ConnectedIngestionError("semantic interpretation identifies a different source packet")
    return interpreted


def _facts_bytes(record_id: str, interpreted: Mapping[str, Any]) -> bytes:
    return canonical_json_bytes({
        "schema_version": 1,
        "record_id": record_id,
        "facts": list(interpreted["facts"]),
    })


def _index_row(index: Mapping[str, Any], record_id: str) -> dict[str, Any] | None:
    if index.get("schema_version") != 1:
        raise ConnectedIngestionError("catalog index has an unsupported schema version")
    rows = index.get("records")
    if not isinstance(rows, list) or any(not isinstance(row, Mapping) for row in rows):
        raise ConnectedIngestionError("catalog index records are malformed")
    matches = [dict(row) for row in rows if row.get("record_id") == record_id]
    if len(matches) > 1:
        raise ConnectedIngestionError("catalog index has duplicate record rows")
    return matches[0] if matches else None


def _index_without(index: Mapping[str, Any], record_id: str) -> dict[str, Any]:
    _index_row(index, record_id)
    return {
        "schema_version": 1,
        "records": [dict(row) for row in index["records"] if row.get("record_id") != record_id],
    }


class ConnectedIngestionWorker:
    """Persist complete source units and auditable canonical Facts for one scope."""

    def __init__(
        self, *, source: SourcePort, store: ArtifactStore, adapter_id: str,
        catalog_schema: Mapping[str, Any], fact_schema: Mapping[str, Any],
        extraction_schema: Mapping[str, Any], interpreter: Interpreter, auditor: Auditor,
        supported_attachment_mime_types: Sequence[str] = ("text/plain",),
        attachment_extractors: Mapping[str, Callable[[ReadResult], AttachmentExtraction]] = {},
        excluded_attachment_mime_types: Mapping[str, str] = {},
        resource_fetcher: Callable[[str], Any] | None = None,
        resource_extractors: Mapping[str, Callable[[Any], AttachmentExtraction]] = {},
        excluded_resource_origins: Mapping[str, str] = {},
        max_attachment_bytes: int = 1_048_576, max_resource_bytes: int = 1_048_576,
        max_resource_redirects: int = 3,
    ) -> None:
        if not adapter_id:
            raise ConnectedIngestionError("source adapter identity is required")
        self.source, self.store, self.adapter_id = source, store, adapter_id
        self.catalog_schema, self.fact_schema, self.extraction_schema = dict(catalog_schema), dict(fact_schema), dict(extraction_schema)
        self.interpreter, self.auditor = interpreter, auditor
        self.supported_attachment_mime_types = tuple(supported_attachment_mime_types)
        self.attachment_extractors = dict(attachment_extractors)
        self.excluded_attachment_mime_types = dict(excluded_attachment_mime_types)
        self.resource_fetcher = resource_fetcher
        self.resource_extractors = dict(resource_extractors)
        self.excluded_resource_origins = dict(excluded_resource_origins)
        self.max_attachment_bytes, self.max_resource_bytes, self.max_resource_redirects = max_attachment_bytes, max_resource_bytes, max_resource_redirects

    def _validated_bundle(
        self, catalog_parent: DriveReference, catalog: StoredArtifact,
        record_id: str, packet: Any,
    ) -> tuple[IngestionArtifacts, dict[str, Any]] | None:
        interpretation = _named(
            self.store, catalog_parent, f"{record_id}.interpretation.json", "application/json"
        )
        audit_artifact = _named(
            self.store, catalog_parent, f"{record_id}.audit.json", "application/json"
        )
        facts = _named(
            self.store, catalog_parent, f"{record_id}.facts.json", "application/json"
        )
        if interpretation is None or audit_artifact is None or facts is None:
            return None
        interpreted = _validated_interpretation(
            packet, interpretation.data, fact_schema=self.fact_schema,
            extraction_schema=self.extraction_schema,
        )
        audit = _json_object(audit_artifact.data, "semantic audit")
        validate_independent_audit(packet, interpreted, audit)
        if facts.data != _facts_bytes(record_id, interpreted):
            raise ConnectedIngestionError("Facts artifact differs from its verified interpretation")
        return IngestionArtifacts(catalog, interpretation, audit_artifact, facts), interpreted

    def current_catalog_view(
        self, *, catalog_parent: DriveReference, index_reference: DriveReference,
        max_bytes: int,
    ) -> CurrentCatalogView:
        """Read every current index row and re-admit its complete audited bundle.

        This is the public reconcile/brief boundary. It deliberately does not
        use the current run's ``IngestionResult.artifacts`` because an unchanged
        or zero-hit run still needs older current Facts, guidelines, and tasks.
        """
        if max_bytes < 1:
            raise ConnectedIngestionError("current catalog view byte bound must be positive")
        index_artifact = self.store.read(index_reference.current())
        index = _json_object(index_artifact.data, "catalog index")
        _index_row(index, "__shape_check__")
        rows = index.get("records")
        if not isinstance(rows, list):
            raise ConnectedIngestionError("catalog index records must be an array")
        artifacts: list[IngestionArtifacts] = []
        all_facts: list[dict[str, Any]] = []
        source_record_map: dict[str, dict[str, Any]] = {}
        task_source_links: dict[str, str] = {}
        guideline_selection: list[dict[str, Any]] = []
        seen_records: set[str] = set()
        seen_facts: set[str] = set()
        for row in sorted(rows, key=lambda item: item.get("record_id", "") if isinstance(item, Mapping) else ""):
            if not isinstance(row, Mapping):
                raise ConnectedIngestionError("catalog index row is malformed")
            record_id = _require_string(row, "record_id", "catalog index row")
            if record_id in seen_records:
                raise ConnectedIngestionError("catalog index repeats a record identity")
            seen_records.add(record_id)
            catalog = _named(self.store, catalog_parent, f"{record_id}.md", "text/markdown")
            if catalog is None or sha256_bytes(catalog.data) != row.get("record_sha256"):
                raise ConnectedIngestionError("current catalog record hash disagrees with its index")
            parsed = parse_v2_record(catalog.data)
            if parsed.header.get("record_id") != record_id or parsed.header.get("adapter_id") != self.adapter_id:
                raise ConnectedIngestionError("current catalog record identity disagrees")
            source_bodies = _source_bodies_from_catalog(catalog.data)
            packet = semantic_packet_from_verified_record(
                catalog.data, source_bodies, max_segments=10_000, max_bytes=max_bytes,
            )
            bundle = self._validated_bundle(catalog_parent, catalog, record_id, packet)
            if bundle is None:
                raise ConnectedIngestionError("current catalog bundle is incomplete")
            admitted, interpreted = bundle
            facts = list(interpreted["facts"])
            if [fact.get("fact_id") for fact in facts] != row.get("fact_ids"):
                raise ConnectedIngestionError("current catalog Fact identities disagree with its index")
            messages = parsed.header.get("messages")
            if not isinstance(messages, list):
                raise ConnectedIngestionError("current catalog record lacks message provenance")
            by_message = {
                item.get("message_id"): item for item in messages
                if isinstance(item, Mapping) and isinstance(item.get("message_id"), str)
            }
            if len(by_message) != len(messages):
                raise ConnectedIngestionError("current catalog message provenance is ambiguous")
            for fact in facts:
                fact_id = _require_string(fact, "fact_id", "current Fact")
                message_id = _require_string(fact, "source_message_id", "current Fact")
                if fact_id in seen_facts or message_id not in by_message:
                    raise ConnectedIngestionError("current catalog Fact provenance is duplicate or absent")
                message = by_message[message_id]
                timestamp = message.get("gmail_internal_date_ms")
                message_ordinal = fact.get("source_message_ordinal")
                content_ordinal = fact.get("source_content_ordinal")
                if (
                    isinstance(timestamp, bool) or not isinstance(timestamp, int) or timestamp < 0
                    or isinstance(message_ordinal, bool) or not isinstance(message_ordinal, int) or message_ordinal < 0
                    or isinstance(content_ordinal, bool) or not isinstance(content_ordinal, int) or content_ordinal < 0
                    or fact.get("source_received_at") != message.get("received_at")
                ):
                    raise ConnectedIngestionError("current catalog Fact lacks exact Gmail time coordinates")
                link = f"{catalog.reference.url}#{fact_id}"
                source_record_map[fact_id] = {
                    "record_id": record_id, "source_message_id": message_id,
                    "gmail_internal_date_ms": timestamp,
                    "source_message_ordinal": message_ordinal,
                    "source_content_ordinal": content_ordinal,
                    "verified_link": link,
                }
                if fact.get("flags", {}).get("is_action") is True and not fact.get("task_relation"):
                    task_source_links[canonical_task_id(fact_id)] = link
                if fact.get("flags", {}).get("is_guideline") is True:
                    guideline_selection.append({
                        "fact_id": fact_id, "is_current": True,
                        "latest_source_received_date": fact.get("received_date"),
                        "verified_link": link,
                    })
                seen_facts.add(fact_id)
                all_facts.append(dict(fact))
            artifacts.append(admitted)
        return CurrentCatalogView(
            index_artifact, tuple(artifacts), tuple(all_facts), source_record_map,
            task_source_links, tuple(guideline_selection),
        )

    def _reconcile_completed_unit(
        self, *, unit: Mapping[str, Any], scope: Mapping[str, Any],
        discovery_message_ids: Sequence[str], catalog_parent: DriveReference,
        index: Mapping[str, Any], max_bytes: int,
        current_full_message_ids: Sequence[str],
    ) -> dict[str, Any] | None:
        conversation_id = unit.get("conversation_id")
        if not isinstance(conversation_id, str) or not conversation_id:
            return None
        record_id = stable_record_id(self.adapter_id, conversation_id)
        if unit.get("record_id") != record_id:
            return None
        try:
            catalog = _named(self.store, catalog_parent, f"{record_id}.md", "text/markdown")
            if catalog is None or sha256_bytes(catalog.data) != unit.get("record_sha256"):
                return None
            parsed = parse_v2_record(catalog.data)
            if (
                parsed.header.get("record_id") != record_id
                or parsed.header.get("conversation_id") != conversation_id
                or parsed.header.get("adapter_id") != self.adapter_id
                or parsed.header.get("scope") != dict(scope)
            ):
                return None
            full_message_ids = [
                message["message_id"] for message in parsed.header.get("messages", [])
                if isinstance(message, Mapping)
            ]
            stored_full_ids = unit.get("full_message_ids")
            if stored_full_ids is not None and stored_full_ids != full_message_ids:
                return None
            if list(current_full_message_ids) != full_message_ids:
                return None
            stored_hits = unit.get("discovery_message_ids", [])
            if not set(stored_hits) <= set(full_message_ids):
                return None
            if not set(discovery_message_ids) <= set(full_message_ids):
                return None
            source_bodies = _source_bodies_from_catalog(catalog.data)
            packet = semantic_packet_from_verified_record(
                catalog.data, source_bodies, max_segments=10_000, max_bytes=max_bytes,
            )
            bundle = self._validated_bundle(catalog_parent, catalog, record_id, packet)
            if bundle is None:
                return None
            _artifacts, interpreted = bundle
            fact_ids = [item.get("fact_id") for item in interpreted["facts"]]
            if fact_ids != unit.get("fact_ids"):
                return None
            expected_row = {
                "record_id": record_id,
                "record_sha256": sha256_bytes(catalog.data),
                "fact_ids": fact_ids,
            }
            if _index_row(index, record_id) != expected_row:
                return None
            return {
                "conversation_id": conversation_id,
                "record_id": record_id,
                "record_sha256": sha256_bytes(catalog.data),
                "fact_ids": fact_ids,
                "discovery_message_ids": sorted(set(stored_hits) | set(discovery_message_ids)),
                "full_message_ids": full_message_ids,
            }
        except (KeyError, TypeError, ValueError):
            return None

    def _write_or_replace(
        self, *, existing: StoredArtifact | None, parent: DriveReference,
        name: str, data: bytes, mime_type: str,
    ) -> StoredArtifact:
        artifact = (
            self.store.write_immutable(parent, name, data, mime_type)
            if existing is None
            else self.store.replace(existing.reference, data, mime_type)
        )
        if artifact.data != data:
            raise ConnectedIngestionError(f"{name} readback differs from intended bytes")
        return artifact

    def _semantic_artifacts(
        self, *, catalog_parent: DriveReference, catalog: StoredArtifact,
        packet: Any, record_id: str, known_source_change: bool,
    ) -> tuple[IngestionArtifacts, dict[str, Any]]:
        interpretation_name = f"{record_id}.interpretation.json"
        audit_name = f"{record_id}.audit.json"
        facts_name = f"{record_id}.facts.json"
        interpretation = _named(self.store, catalog_parent, interpretation_name, "application/json")
        audit_artifact = _named(self.store, catalog_parent, audit_name, "application/json")
        facts = _named(self.store, catalog_parent, facts_name, "application/json")

        interpreted: dict[str, Any] | None = None
        if interpretation is not None:
            try:
                interpreted = _validated_interpretation(
                    packet, interpretation.data, fact_schema=self.fact_schema,
                    extraction_schema=self.extraction_schema,
                )
            except ValueError:
                if not known_source_change:
                    raise
        elif audit_artifact is not None or facts is not None:
            raise ConnectedIngestionError("orphan semantic artifacts lack their interpretation")

        if interpreted is None:
            interpreted = interpret_packet(
                packet, self.interpreter, fact_schema=self.fact_schema,
                extraction_schema=self.extraction_schema,
            )
            interpretation_bytes = canonical_json_bytes(interpreted)
            interpretation = self._write_or_replace(
                existing=interpretation, parent=catalog_parent,
                name=interpretation_name, data=interpretation_bytes,
                mime_type="application/json",
            )

        audit: dict[str, Any] | None = None
        if audit_artifact is not None:
            try:
                candidate = _json_object(audit_artifact.data, "semantic audit")
                validate_independent_audit(packet, interpreted, candidate)
                audit = candidate
            except ValueError:
                audit = None
        if audit is None:
            candidate = self.auditor(packet.as_mapping(), interpreted)
            if not isinstance(candidate, Mapping):
                raise ConnectedIngestionError("independent semantic audit did not return an object")
            audit = dict(candidate)
            validate_independent_audit(packet, interpreted, audit)
            audit_artifact = self._write_or_replace(
                existing=audit_artifact, parent=catalog_parent,
                name=audit_name, data=canonical_json_bytes(audit),
                mime_type="application/json",
            )

        intended_facts = _facts_bytes(record_id, interpreted)
        if facts is None or facts.data != intended_facts:
            facts = self._write_or_replace(
                existing=facts, parent=catalog_parent, name=facts_name,
                data=intended_facts, mime_type="application/json",
            )
        if interpretation is None or audit_artifact is None:
            raise ConnectedIngestionError("semantic artifacts are incomplete after recovery")
        validate_independent_audit(
            packet, interpreted, _json_object(audit_artifact.data, "semantic audit")
        )
        if facts.data != intended_facts:
            raise ConnectedIngestionError("Facts artifact differs from its verified interpretation")
        return IngestionArtifacts(catalog, interpretation, audit_artifact, facts), interpreted

    def discover(
        self, *, scope: Mapping[str, Any], discovery_parent: DriveReference,
        discovery_name: str,
    ) -> DiscoveryResult:
        """Execute the bounded Gmail search once and persist its exact inventory.

        A retry for the same operation-scoped name adopts the verified immutable
        inventory; it never silently starts a second catalog search.
        """
        if not isinstance(discovery_name, str) or not discovery_name:
            raise ConnectedIngestionError("discovery artifact name is required")
        existing = _named(self.store, discovery_parent, discovery_name, "application/json")
        if existing is None:
            inventory = canonical_json_bytes(_discovery_inventory(self.source, scope))
            existing = self.store.write_immutable(
                discovery_parent, discovery_name, inventory, "application/json"
            )
            if existing.data != inventory:
                raise ConnectedIngestionError("discovery inventory readback differs from intended bytes")
        discovered_scope, conversations, scope_sha256 = _discovery_from_artifact(existing.data)
        if discovered_scope != dict(scope):
            raise ConnectedIngestionError("existing discovery inventory scope differs from requested scope")
        return DiscoveryResult(existing, scope_sha256, tuple(item["conversation_id"] for item in conversations))

    def catalog(
        self, *, discovery_reference: DriveReference, catalog_parent: DriveReference,
        index_reference: DriveReference, work_reference: DriveReference,
        max_records: int, max_bytes: int,
    ) -> IngestionResult:
        """Consume one verified discovery inventory without performing a search."""
        if max_records < 1 or max_bytes < 1:
            raise ConnectedIngestionError("source unit bounds must be positive")
        # Inputs may be durable pointers from an earlier process. Resolve the
        # same exact object IDs afresh, then retain every returned write guard.
        if not isinstance(discovery_reference.version, str) or not discovery_reference.version:
            raise ConnectedIngestionError("catalog requires the exact verified discovery reference")
        discovery_artifact = self.store.read(discovery_reference)
        if discovery_artifact.reference.mime_type != "application/json":
            raise ConnectedIngestionError("discovery inventory has the wrong MIME type")
        scope, conversations, scope_sha256 = _discovery_from_artifact(discovery_artifact.data)
        discovery_sha256 = sha256_bytes(discovery_artifact.data)
        continuation_artifact = self.store.read(work_reference.current())
        continuation = _work_continuation(continuation_artifact.data)
        if continuation["discovery_sha256"] not in {None, discovery_sha256}:
            raise ConnectedIngestionError("source work continuation belongs to a different discovery inventory")
        index_artifact = self.store.read(index_reference.current())
        index = _json_object(index_artifact.data, "catalog index")
        _index_row(index, "__shape_check__")

        prior_units = {
            item["conversation_id"]: item for item in continuation["units"]
        }
        valid_units: dict[str, dict[str, Any]] = {}
        prefetched: dict[str, Mapping[str, Any]] = {}
        for listed in conversations:
            conversation_id = _require_string(listed, "conversation_id", "enumerated conversation")
            prior = prior_units.get(conversation_id)
            if prior is None:
                continue
            readback, current_full_message_ids = _full_message_ids(
                self.source, conversation_id
            )
            prefetched[conversation_id] = readback
            reconciled = self._reconcile_completed_unit(
                unit=prior, scope=scope,
                discovery_message_ids=listed["discovery_message_ids"],
                catalog_parent=catalog_parent, index=index, max_bytes=max_bytes,
                current_full_message_ids=current_full_message_ids,
            )
            if reconciled is not None:
                valid_units[conversation_id] = reconciled
        batch = next_import_batch(
            conversations, completed_ids=tuple(valid_units),
            max_records=max_records, max_bytes=max_bytes,
        )
        written: list[IngestionArtifacts] = []
        actual_unit_bytes = 0
        deferred_ids: list[str] = []
        for position, listed in enumerate(batch.conversations):
            conversation_id = _require_string(listed, "conversation_id", "batch conversation")
            messages, source_bodies = _conversation_messages(
                self.source, listed, max_attachment_bytes=self.max_attachment_bytes,
                supported_attachment_mime_types=self.supported_attachment_mime_types,
                attachment_extractors=self.attachment_extractors,
                excluded_attachment_mime_types=self.excluded_attachment_mime_types,
                resource_fetcher=self.resource_fetcher,
                resource_extractors=self.resource_extractors,
                excluded_resource_origins=self.excluded_resource_origins,
                max_resource_bytes=self.max_resource_bytes,
                max_resource_redirects=self.max_resource_redirects,
                readback=prefetched.get(conversation_id),
            )
            record_id = stable_record_id(self.adapter_id, conversation_id)
            conversation = {
                "schema_version": 3 if all("mime_accounting" in item for item in messages) else 2,
                "adapter_id": self.adapter_id,
                "conversation_id": conversation_id, "scope": dict(scope),
                "pagination": {
                    "completed": True,
                    "page_tokens": list(_json_object(discovery_artifact.data, "discovery inventory")["page_tokens"]),
                    "discovery_message_ids": list(listed["discovery_message_ids"]),
                    "full_message_ids": [item["message_id"] for item in messages],
                    "dispositions": [
                        dict(item) for item in _json_object(discovery_artifact.data, "discovery inventory")["dispositions"]
                        if item["conversation_id"] == conversation_id
                    ],
                },
                "messages": messages,
            }
            intended = serialize_v2_record(conversation, self.catalog_schema)
            if len(intended) > max_bytes and not written:
                raise ConnectedIngestionError("one complete conversation exceeds the configured immutable-unit byte bound")
            if actual_unit_bytes + len(intended) > max_bytes:
                deferred_ids = [conversation_id, *[
                    _require_string(item, "conversation_id", "batch conversation")
                    for item in batch.conversations[position + 1:]
                ]]
                break
            catalog_name = f"{record_id}.md"
            existing_catalog = _named(
                self.store, catalog_parent, catalog_name, "text/markdown"
            )
            catalog_changed = False
            if existing_catalog is None:
                catalog = self.store.write_immutable(
                    catalog_parent, catalog_name, intended, "text/markdown"
                )
            elif existing_catalog.data == intended:
                catalog = existing_catalog
            else:
                previous = parse_v2_record(existing_catalog.data)
                if (
                    previous.header.get("record_id") != record_id
                    or previous.header.get("conversation_id") != conversation_id
                    or previous.header.get("adapter_id") != self.adapter_id
                ):
                    raise ConnectedIngestionError("existing catalog identity cannot be refreshed")
                catalog = self.store.replace(
                    existing_catalog.reference, intended, "text/markdown"
                )
                catalog_changed = True
            if catalog.data != intended:
                raise ConnectedIngestionError("catalog artifact readback differs from intended bytes")
            packet = semantic_packet_from_verified_record(catalog.data, source_bodies, max_segments=10_000, max_bytes=max_bytes)
            prior = prior_units.get(conversation_id)
            row = _index_row(index, record_id)
            known_source_change = catalog_changed or (
                prior is not None and prior.get("record_sha256") != sha256_bytes(catalog.data)
            ) or (
                row is not None and row.get("record_sha256") != sha256_bytes(catalog.data)
            )
            artifacts, interpreted = self._semantic_artifacts(
                catalog_parent=catalog_parent, catalog=catalog, packet=packet,
                record_id=record_id, known_source_change=known_source_change,
            )
            recovered = recover_catalog_index(
                source_bodies, intended, catalog.data, _index_without(index, record_id),
                list(interpreted["facts"]),
            )
            index_bytes = canonical_json_bytes(recovered.index)
            index_artifact = self.store.replace(
                index_artifact.reference, index_bytes, "application/json"
            )
            if index_artifact.data != index_bytes:
                raise ConnectedIngestionError("catalog index readback differs from intended bytes")
            index = recovered.index
            valid_units[conversation_id] = {
                "conversation_id": conversation_id, "record_id": record_id,
                "record_sha256": sha256_bytes(catalog.data),
                "fact_ids": [item["fact_id"] for item in interpreted["facts"]],
                "discovery_message_ids": list(listed["discovery_message_ids"]),
                "full_message_ids": [item["message_id"] for item in messages],
            }
            ordered_ids = sorted(valid_units)
            state_value = {
                "schema_version": 1,
                "discovery_sha256": discovery_sha256,
                "completed_conversation_ids": ordered_ids,
                "units": [valid_units[identity] for identity in ordered_ids],
            }
            state_bytes = canonical_json_bytes(state_value)
            continuation_artifact = self.store.replace(
                continuation_artifact.reference, state_bytes, "application/json"
            )
            if continuation_artifact.data != state_bytes:
                raise ConnectedIngestionError("source continuation readback differs from intended bytes")
            written.append(artifacts)
            actual_unit_bytes += len(intended)
        remaining_ids = tuple(dict.fromkeys([*deferred_ids, *batch.remaining_ids]))
        remaining = {"conversation_ids": list(remaining_ids)} if remaining_ids else {}
        ordered_ids = sorted(valid_units)
        final_state = canonical_json_bytes({
            "schema_version": 1,
            "discovery_sha256": discovery_sha256,
            "completed_conversation_ids": ordered_ids,
            "units": [valid_units[identity] for identity in ordered_ids],
        })
        if continuation_artifact.data != final_state:
            continuation_artifact = self.store.replace(
                continuation_artifact.reference, final_state, "application/json"
            )
        proposed_cursor = None if remaining else {
            "schema_version": 1,
            "scope_sha256": scope_sha256,
            "discovery_sha256": discovery_sha256,
            "completed_conversation_ids": ordered_ids,
        }
        return IngestionResult(
            True, not remaining, tuple(ordered_ids), remaining,
            continuation_artifact, index_artifact, tuple(written),
            discovery_artifact, proposed_cursor,
        )
