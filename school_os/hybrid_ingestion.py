"""Bundle-native persistence around the established connected source worker.

The connected worker still owns Gmail completeness, catalog, interpretation,
audit, and Fact validation.  This module gives it a disposable local artifact
store, captures exact source bytes, and publishes those outputs through the
approved immutable-source-bundle/current-state boundary.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from .adapters import ReadResult
from .bundles import BundleEntry, BundleMemberReference, member_reference
from .catalog import parse_v2_record
from .connected_ingestion import (
    CodexGmailSourceAdapter, CodexSemanticCallbacks, ConnectedIngestionError,
    ConnectedIngestionWorker, IngestionResult,
)
from .connected_sources import ConnectedSourceAdapters
from .connected_storage import (
    BundleTransactionStore, DriveReference, StoredArtifact,
)
from .contracts import canonical_json_bytes, sha256_bytes
from .importer import AttachmentRead, DirectResourceRead
from .install import publish_hybrid_content_bundle
from .gmail_source import GmailMimeNormalizer
from .hybrid_operations import HybridCheckpointCommit, HybridCheckpointPublisher
from .operations import checkpoint_pointer


class HybridIngestionError(ValueError):
    """Raised when staged source output cannot become canonical safely."""


_STAGE_MIME = "application/vnd.google-apps.folder"


class LocalIngestionStore:
    """Disposable exact-byte store for one invocation of the domain worker.

    Its identifiers and URLs are deliberately unusable outside this object and
    must never be written into a state or content bundle.
    """

    def __init__(self) -> None:
        self.root = DriveReference(
            "local-stage", "local-stage", _STAGE_MIME,
            "school-os-local-stage:/", "local-stage",
        )
        self._objects: dict[str, StoredArtifact] = {}
        self._names: dict[tuple[str, str], str] = {}

    def seed(self, name: str, data: bytes, mime_type: str) -> StoredArtifact:
        return self.write_immutable(self.root, name, data, mime_type)

    def read(self, reference: DriveReference) -> StoredArtifact:
        try:
            item = self._objects[reference.object_id]
        except KeyError as exc:
            raise HybridIngestionError("local ingestion artifact is absent") from exc
        if (
            item.reference.parent_id != reference.parent_id
            or item.reference.mime_type != reference.mime_type
            or reference.version is not None
            and item.reference.version != reference.version
        ):
            raise HybridIngestionError("local ingestion reference disagrees")
        return item

    def read_named(self, parent: DriveReference, name: str) -> StoredArtifact | None:
        identifier = self._names.get((parent.object_id, name))
        return None if identifier is None else self._objects[identifier]

    def write_immutable(
        self, parent: DriveReference, name: str, data: bytes, mime_type: str,
    ) -> StoredArtifact:
        current = self.read_named(parent, name)
        if current is not None:
            if current.data != data or current.reference.mime_type != mime_type:
                raise HybridIngestionError("local immutable artifact differs")
            return current
        identity = "stage-" + sha256_bytes(
            canonical_json_bytes({"name": name, "parent": parent.object_id})
        )
        reference = DriveReference(
            identity, parent.object_id, mime_type,
            f"school-os-local-stage:/{identity}", sha256_bytes(data),
        )
        artifact = StoredArtifact(reference, data)
        self._objects[identity] = artifact
        self._names[(parent.object_id, name)] = identity
        return artifact

    def replace(
        self, reference: DriveReference, data: bytes, mime_type: str,
    ) -> StoredArtifact:
        current = self.read(reference)
        updated_reference = DriveReference(
            current.reference.object_id, current.reference.parent_id, mime_type,
            current.reference.url, sha256_bytes(data),
        )
        artifact = StoredArtifact(updated_reference, data)
        self._objects[reference.object_id] = artifact
        return artifact

    def named_artifacts(self) -> dict[str, StoredArtifact]:
        return {
            name: self._objects[identifier]
            for (parent, name), identifier in self._names.items()
            if parent == self.root.object_id
        }


@dataclass
class SourceByteCapture:
    """Exact raw source bytes observed while the source worker validates them."""

    messages: dict[str, tuple[str, bytes]] = field(default_factory=dict)
    attachments: dict[tuple[str, str], tuple[str, bytes, Mapping[str, Any] | None]] = field(default_factory=dict)
    resources: dict[str, DirectResourceRead] = field(default_factory=dict)

    def raw_message(self, message_id: str, conversation_id: str, data: bytes) -> None:
        current = self.messages.get(message_id)
        value = (conversation_id, data)
        if current is not None and current != value:
            raise HybridIngestionError("raw Gmail message identity changed during capture")
        self.messages[message_id] = value

    def attachment(
        self, message_id: str, attachment_id: str,
        result: ReadResult | AttachmentRead,
    ) -> None:
        if isinstance(result, AttachmentRead):
            data, mime_type, locator = result.original_bytes, result.mime_type, result.read_locator
        else:
            data, mime_type, locator = result.data, result.mime_type, None
        if data is None or not isinstance(mime_type, str) or not mime_type:
            raise HybridIngestionError("supported attachment lacks complete original bytes")
        value = (mime_type, data, locator)
        key = (message_id, attachment_id)
        if key in self.attachments and self.attachments[key] != value:
            raise HybridIngestionError("attachment identity changed during capture")
        self.attachments[key] = value

    def resource(self, requested_url: str, result: DirectResourceRead) -> DirectResourceRead:
        if not result.complete or not result.eof or result.bytes_read != len(result.data):
            raise HybridIngestionError("direct resource lacks complete byte evidence")
        current = self.resources.get(requested_url)
        if current is not None and current != result:
            raise HybridIngestionError("direct resource changed during capture")
        self.resources[requested_url] = result
        return result


@dataclass(frozen=True)
class HybridIngestionPublication:
    """Verified source carrier and staged canonical state replacements."""

    source: Mapping[str, Any]
    transaction: BundleTransactionStore
    catalog_index: dict[str, Any]
    facts: dict[str, Any]
    fact_indexes: dict[str, Any]


@dataclass(frozen=True)
class HybridIngestionCommit:
    publication: HybridIngestionPublication
    checkpoint: HybridCheckpointCommit


@dataclass(frozen=True)
class StagedIngestion:
    """One completely validated, still-disposable worker result."""

    store: LocalIngestionStore
    result: IngestionResult


def stage_ingestion(
    *, worker_factory: Any, scope: Mapping[str, Any],
    max_records: int, max_bytes: int,
) -> StagedIngestion:
    """Run discover/catalog locally without emitting provider artifact writes."""
    if max_records < 1 or max_bytes < 1:
        raise HybridIngestionError("hybrid ingestion bounds must be positive")
    staged = LocalIngestionStore()
    index = staged.seed(
        "index.json", canonical_json_bytes({"schema_version": 1, "records": []}),
        "application/json",
    )
    work = staged.seed(
        "work.json", canonical_json_bytes({
            "schema_version": 1, "completed_conversation_ids": [], "units": [],
        }), "application/json",
    )
    worker = worker_factory(staged)
    discovery = worker.discover(
        scope=scope, discovery_parent=staged.root, discovery_name="discovery.json",
    )
    for _unit in range(1000):
        result = worker.catalog(
            discovery_reference=discovery.inventory.reference,
            catalog_parent=staged.root, index_reference=index.reference,
            work_reference=work.reference, max_records=max_records, max_bytes=max_bytes,
        )
        index, work = result.index, result.work
        if result.phase_complete:
            break
    else:
        raise HybridIngestionError("hybrid ingestion exceeded its finite unit bound")
    return StagedIngestion(staged, result)


def stage_connected_ingestion(
    *, installed_root: Any, resolved: Any, run_directory: Any,
    gmail: Any, semantic: Any, capture: SourceByteCapture,
) -> StagedIngestion:
    """Compose the existing live Gmail/semantic adapters over local staging."""
    normalizer = GmailMimeNormalizer(resolved.household["timezone"])
    source_bytes = ConnectedSourceAdapters(
        peer=gmail.peer, run_directory=run_directory,
    )
    source = CodexGmailSourceAdapter(
        gmail, max_thread_messages=resolved.source_scope["max_thread_messages"],
        normalize_message=normalizer.normalize,
        normalize_attachment=lambda message_id, attachment_id, raw: source_bytes.gmail_attachment(
            message_id, attachment_id, mime_type=raw["mime_type"],
            declared_byte_size=raw["size_bytes"],
        ),
        capture_raw_message=capture.raw_message,
        capture_attachment=capture.attachment,
    )
    callbacks = CodexSemanticCallbacks(semantic)

    def worker_factory(store: LocalIngestionStore) -> ConnectedIngestionWorker:
        def schema(name: str) -> dict[str, Any]:
            path = installed_root / "schemas" / name
            value = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(value, dict):
                raise HybridIngestionError("installed ingestion schema is malformed")
            return value

        def fetch_resource(url: str) -> DirectResourceRead:
            return capture.resource(url, source_bytes.fetch_https(url))

        return ConnectedIngestionWorker(
            source=source, store=store,
            adapter_id=resolved.source_scope["adapter_id"],
            catalog_schema=schema("source-conversation.schema.json"),
            fact_schema=schema("fact.schema.json"),
            extraction_schema=schema("extraction-result.schema.json"),
            interpreter=callbacks.interpret, auditor=callbacks.audit,
            supported_attachment_mime_types=(
                "text/plain", "application/pdf", "image/png", "image/jpeg",
            ),
            attachment_extractors={
                "application/pdf": lambda item: source_bytes.extract_pdf(
                    source_id=item.identity, data=item.data or b"",
                ),
                "image/png": lambda item: source_bytes.extract_image(
                    source_id=item.identity, data=item.data or b"",
                    mime_type=item.mime_type,
                ),
                "image/jpeg": lambda item: source_bytes.extract_image(
                    source_id=item.identity, data=item.data or b"",
                    mime_type=item.mime_type,
                ),
            },
            resource_fetcher=fetch_resource,
            max_attachment_bytes=resolved.policies["execution"]["max_bytes_per_unit"],
            max_resource_bytes=resolved.policies["execution"]["max_bytes_per_unit"],
        )

    maximum = resolved.policies["execution"]["max_bytes_per_unit"]
    return stage_ingestion(
        worker_factory=worker_factory, scope=resolved.source_scope,
        max_records=resolved.policies["execution"]["max_records_per_unit"],
        max_bytes=maximum,
    )


def _safe_key(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def _ref(source: Mapping[str, Any], path: str) -> dict[str, Any]:
    return member_reference(
        source["bundle_reference"], source["bundle"], path,
    ).as_mapping()


def _entry_path(name: str) -> str:
    if name.endswith(".md"):
        return f"catalog/records/{name}"
    if name.endswith(".interpretation.json"):
        return f"semantic/interpretations/{name}"
    if name.endswith(".audit.json"):
        return f"semantic/audits/{name}"
    if name.endswith(".facts.json"):
        return f"facts/records/{name}"
    return {
        "discovery.json": "discovery/inventory.json",
        "index.json": "catalog/index-v1.json",
        "work.json": "state/source-work.json",
    }.get(name, f"staged/{_safe_key(name)}.bin")


def publish_ingestion_result(
    *, storage: Any, transaction: BundleTransactionStore,
    result: IngestionResult, staged: LocalIngestionStore,
    capture: SourceByteCapture, identity: str,
) -> HybridIngestionPublication:
    """Publish verified worker output and stage its canonical state adoption."""
    if not result.verified or not result.phase_complete or result.remaining_work:
        raise HybridIngestionError("only one complete bounded ingestion may be published")
    named = staged.named_artifacts()
    required = {"discovery.json", "index.json", "work.json"}
    if not required <= set(named):
        raise HybridIngestionError("staged ingestion lacks discovery/index/work artifacts")
    entries: dict[str, BundleEntry] = {}
    artifact_paths: dict[str, str] = {}
    for name, artifact in sorted(named.items()):
        path = _entry_path(name)
        if path in entries:
            raise HybridIngestionError("staged ingestion paths collide")
        artifact_paths[name] = path
        entries[path] = BundleEntry(
            artifact.data, "staged_ingestion_artifact", artifact.reference.mime_type,
        )
    custody: dict[str, Any] = {"attachments": [], "messages": [], "resources": [], "schema_version": 1}
    for message_id, (conversation_id, data) in sorted(capture.messages.items()):
        path = f"raw/messages/{_safe_key(message_id)}.eml"
        entries[path] = BundleEntry(data, "raw_gmail_message", "message/rfc822")
        custody["messages"].append({
            "conversation_id": conversation_id, "message_id": message_id,
            "member_path": path, "sha256": sha256_bytes(data), "byte_length": len(data),
        })
    for (message_id, attachment_id), (mime_type, data, locator) in sorted(capture.attachments.items()):
        path = f"raw/attachments/{_safe_key(message_id + ':' + attachment_id)}.bin"
        entries[path] = BundleEntry(data, "raw_gmail_attachment", mime_type)
        custody["attachments"].append({
            "attachment_id": attachment_id, "message_id": message_id,
            "member_path": path, "mime_type": mime_type,
            "sha256": sha256_bytes(data), "byte_length": len(data),
            "read_locator": None if locator is None else dict(locator),
        })
    for requested_url, resource in sorted(capture.resources.items()):
        path = f"raw/resources/{_safe_key(requested_url)}.bin"
        entries[path] = BundleEntry(resource.data, "direct_referenced_resource", resource.mime_type)
        custody["resources"].append({
            "requested_url": requested_url,
            "requested_url_sha256": _safe_key(requested_url), "final_url": resource.url,
            "member_path": path, "mime_type": resource.mime_type,
            "sha256": sha256_bytes(resource.data), "byte_length": len(resource.data),
            "redirect_chain": list(resource.redirect_chain),
        })
    custody_bytes = canonical_json_bytes(custody)
    entries["custody/index.json"] = BundleEntry(
        custody_bytes, "source_custody_index", "application/json",
    )
    source = publish_hybrid_content_bundle(
        storage, recovery=transaction.working.recovery,
        bundle_kind="source", identity=identity, entries=entries,
    )
    index_v1 = json.loads(named["index.json"].data.decode("utf-8"))
    rows: list[dict[str, Any]] = []
    all_facts: list[dict[str, Any]] = []
    by_fact: dict[str, Any] = {}
    for row in index_v1.get("records", []):
        record_id = row["record_id"]
        catalog_name = f"{record_id}.md"
        interpretation_name = f"{record_id}.interpretation.json"
        audit_name = f"{record_id}.audit.json"
        facts_name = f"{record_id}.facts.json"
        for name in (catalog_name, interpretation_name, audit_name, facts_name):
            if name not in artifact_paths:
                raise HybridIngestionError("staged record bundle is incomplete")
        catalog_bytes = named[catalog_name].data
        parsed = parse_v2_record(catalog_bytes)
        message_ids = [item[0] for item in parsed.bodies]
        raw_messages = [
            item for item in custody["messages"] if item["message_id"] in message_ids
        ]
        attachments = [
            item for item in custody["attachments"] if item["message_id"] in message_ids
        ]
        resource_urls = {
            outcome.get("original_url")
            for message in parsed.header.get("messages", [])
            if isinstance(message, Mapping) and message.get("message_id") in message_ids
            for outcome in message.get("resources", [])
            if isinstance(outcome, Mapping) and isinstance(outcome.get("original_url"), str)
        }
        resources = [
            item for item in custody["resources"]
            if item["requested_url"] in resource_urls
        ]
        facts_value = json.loads(named[facts_name].data.decode("utf-8"))
        record_facts = facts_value.get("facts")
        if not isinstance(record_facts, list):
            raise HybridIngestionError("staged Facts record is malformed")
        source_members = {
            "catalog": _ref(source, artifact_paths[catalog_name]),
            "interpretation": _ref(source, artifact_paths[interpretation_name]),
            "audit": _ref(source, artifact_paths[audit_name]),
            "facts": _ref(source, artifact_paths[facts_name]),
            "raw_messages": [_ref(source, item["member_path"]) for item in raw_messages],
            "attachments": [_ref(source, item["member_path"]) for item in attachments],
            "direct_resources": [_ref(source, item["member_path"]) for item in resources],
        }
        rows.append({**dict(row), "source_members": source_members})
        for fact in record_facts:
            fact_id = fact.get("fact_id") if isinstance(fact, Mapping) else None
            if not isinstance(fact_id, str) or not fact_id or fact_id in by_fact:
                raise HybridIngestionError("staged Fact identity is invalid or duplicate")
            all_facts.append(dict(fact))
            by_fact[fact_id] = {
                "record_id": record_id,
                "source_message_id": fact.get("source_message_id"),
                "facts_member": source_members["facts"],
                "catalog_member": source_members["catalog"],
            }
    catalog_index = {"schema_version": 2, "records": sorted(rows, key=lambda item: item["record_id"])}
    facts = {"schema_version": 1, "facts": sorted(all_facts, key=lambda item: item["fact_id"])}
    fact_indexes = {"schema_version": 1, "by_fact_id": dict(sorted(by_fact.items()))}
    updated = transaction.stage(
        "data/source-catalog-index.json", canonical_json_bytes(catalog_index),
    ).stage(
        "data/facts.json", canonical_json_bytes(facts),
        role="canonical_facts", media_type="application/json",
    ).stage(
        "data/fact-indexes.json", canonical_json_bytes(fact_indexes),
        role="fact_indexes", media_type="application/json",
    )
    return HybridIngestionPublication(
        source, updated, catalog_index, facts, fact_indexes,
    )


def commit_ingestion(
    *, storage: Any, resolved: Any, staged: StagedIngestion,
    capture: SourceByteCapture, identity: str, operation_id: str,
    attempt_id: str, source_commit: str, serialization: Mapping[str, Any],
    installed_root: Any,
) -> HybridIngestionCommit:
    """Publish a complete source batch and atomically adopt its canonical index."""
    if len(source_commit) != 40 or any(item not in "0123456789abcdef" for item in source_commit):
        raise HybridIngestionError("ingestion source commit is invalid")
    publication = publish_ingestion_result(
        storage=storage, transaction=resolved.state, result=staged.result,
        staged=staged.store, capture=capture, identity=identity,
    )
    source_reference = dict(publication.source["bundle_reference"])
    checkpoint = {
        "schema_version": 1,
        "checkpoint_id": f"{operation_id}-checkpoint-0000",
        "operation_id": operation_id,
        "attempt_id": attempt_id,
        "pinned_release": {
            "version": resolved.instance["system_version"],
            "source_commit": source_commit,
        },
        "scope": {
            "entrypoint": "manual",
            "source_scope_sha256": sha256_bytes(canonical_json_bytes(resolved.source_scope)),
            "operation_mode": "unsent_preview",
        },
        "configuration_fingerprint": resolved.configuration_fingerprint,
        "phase": "catalog",
        "completed_phases": ["preflight", "discover", "catalog"],
        "completed_units": list(staged.result.completed_units),
        "remaining_work": {"phase": "reconcile"},
        "artifacts": [{
            "kind": "source_bundle",
            "identity": identity,
            "reference": source_reference,
            "sha256": publication.source["bundle_sha256"],
        }],
        "effects": [],
        "verification": {
            "phase_output": {
                "verified": True,
                "phase_complete": True,
                "source_bundle": source_reference,
                "source_bundle_sha256": publication.source["bundle_sha256"],
                "catalog_index": publication.transaction.read(
                    "data/source-catalog-index.json"
                ).reference.as_mapping(),
                "fact_count": len(publication.facts["facts"]),
                "proposed_source_cursor": staged.result.proposed_cursor,
                "eligible_cursor_advanced": False,
            },
        },
        "blocker": None,
        "predecessor": None,
        "sequence": 0,
    }
    operation_state = {
        "schema_version": 1,
        "status": "running",
        "current_operation": {
            "operation_id": operation_id, "attempt_id": attempt_id,
        },
        "serialization": {
            "mode": serialization["mode"],
            "evidence": {"entrypoint": "manual"},
        },
        "checkpoint": checkpoint_pointer(checkpoint),
        "last_terminal": None,
    }
    def schema(name: str) -> dict[str, Any]:
        value = json.loads((installed_root / "schemas" / name).read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise HybridIngestionError("installed operation schema is malformed")
        return value
    committed = HybridCheckpointPublisher(
        publication.transaction,
        state_schema=schema("operation-state.schema.json"),
        checkpoint_schema=schema("operation-checkpoint.schema.json"),
    ).commit(
        storage=storage, checkpoint=checkpoint, operation_state=operation_state,
        serialization=serialization,
    )
    return HybridIngestionCommit(publication, committed)
