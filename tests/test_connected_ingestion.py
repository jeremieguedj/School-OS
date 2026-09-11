from __future__ import annotations

import base64
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from school_os.adapters import Page
from school_os.catalog import parse_v2_record
from school_os.connected_ingestion import (
    CodexGmailSourceAdapter,
    CodexDriveArtifactStore,
    CodexSemanticCallbacks,
    ConnectedIngestionError,
    ConnectedIngestionWorker,
    DriveReference,
    StoredArtifact,
)
from school_os.contracts import canonical_json_bytes, sha256_bytes


def _part(data: bytes) -> dict[str, Any]:
    return {
        "part_id": "plain-1", "role": "body", "selected_plaintext": True,
        "complete": True, "mime_type": "text/plain", "charset": "utf-8",
        "content_transfer_encoding": "identity", "data": data,
        "raw_part_sha256": hashlib.sha256(data).hexdigest(), "raw_part_byte_length": len(data),
        "raw_part_locator": {"kind": "raw_part_bytes", "byte_start": 0, "byte_end": len(data)},
        "provider_unicode": data.decode("utf-8"),
    }


class MemoryStore:
    def __init__(self) -> None:
        self.objects: dict[str, tuple[DriveReference, bytes]] = {}
        self.names: dict[tuple[str, str], str] = {}
        self.generation = 0

    def seed(self, reference: DriveReference, data: bytes) -> None:
        self.objects[reference.object_id] = (reference, data)

    def read(self, reference: DriveReference) -> StoredArtifact:
        stored, data = self.objects[reference.object_id]
        if stored.parent_id != reference.parent_id or stored.mime_type != reference.mime_type:
            raise AssertionError("wrong test reference")
        if reference.version is not None and stored.version != reference.version:
            raise ConnectedIngestionError("stale test reference")
        return StoredArtifact(stored, data)

    def read_named(self, parent: DriveReference, name: str) -> StoredArtifact | None:
        identifier = self.names.get((parent.object_id, name))
        return None if identifier is None else self.read(self.objects[identifier][0])

    def _new(self, parent: DriveReference, name: str, data: bytes, mime_type: str, identifier: str | None = None) -> StoredArtifact:
        self.generation += 1
        identifier = identifier or f"object-{self.generation}"
        ref = DriveReference(identifier, parent.object_id, mime_type, f"https://drive.test/{identifier}", str(self.generation))
        self.objects[identifier] = (ref, data)
        self.names[(parent.object_id, name)] = identifier
        return StoredArtifact(ref, data)

    def write_immutable(self, parent: DriveReference, name: str, data: bytes, mime_type: str) -> StoredArtifact:
        existing = self.read_named(parent, name)
        if existing is not None:
            if existing.reference.mime_type != mime_type:
                raise ConnectedIngestionError("immutable test MIME differs")
            if existing.data != data:
                raise ConnectedIngestionError("immutable test object differs")
            return existing
        return self._new(parent, name, data, mime_type)

    def replace(self, reference: DriveReference, data: bytes, mime_type: str) -> StoredArtifact:
        current = self.read(reference)
        self.generation += 1
        replaced = DriveReference(
            reference.object_id, current.reference.parent_id, mime_type,
            current.reference.url, str(self.generation),
        )
        self.objects[reference.object_id] = (replaced, data)
        return StoredArtifact(replaced, data)


class Source:
    def __init__(self, bodies: dict[str, str]) -> None:
        self.bodies = bodies
        self.search_calls: list[str | None] = []
        self.read_calls: list[str] = []

    def search(self, _scope: dict[str, Any], token: str | None) -> Page:
        self.search_calls.append(token)
        if token is not None:
            return Page((), None)
        return Page(tuple({"conversation_id": key, "byte_size": 1, "discovery_message_ids": [f"{key}-message"]} for key in sorted(self.bodies)), None)

    def read_conversation(self, identity: str) -> dict[str, Any]:
        self.read_calls.append(identity)
        return {
            "conversation_id": identity,
            "messages": [{
                "message_id": f"{identity}-message", "received_at": "2026-09-08T08:00:00Z",
                "received_date": "2026-09-08", "gmail_internal_date_ms": 1788854400000,
                "mime_tree_complete": True,
                "parts": [_part(self.bodies[identity].encode("utf-8"))], "attachments": [], "html_parts": [],
            }],
        }

    def read_attachment(self, _message_id: str, _attachment_id: str) -> Any:
        raise AssertionError("test source has no attachment")


class ReplySource(Source):
    def __init__(self) -> None:
        super().__init__({"thread-1": "Original"})
        self.reply = False

    def search(self, _scope: dict[str, Any], token: str | None) -> Page:
        self.search_calls.append(token)
        if token is not None:
            return Page((), None)
        hit = "reply-message" if self.reply else "thread-1-message"
        return Page(({
            "conversation_id": "thread-1", "byte_size": 1,
            "discovery_message_ids": [hit],
        },), None)

    def read_conversation(self, identity: str) -> dict[str, Any]:
        value = super().read_conversation(identity)
        if self.reply:
            value["messages"].append({
                "message_id": "reply-message",
                "received_at": "2026-09-09T08:00:00Z",
                "received_date": "2026-09-09", "gmail_internal_date_ms": 1788940800000,
                "mime_tree_complete": True,
                "parts": [_part(b"New reply")],
                "attachments": [],
                "html_parts": [],
            })
        return value


class OutsideQueryReplySource(ReplySource):
    def search(self, _scope: dict[str, Any], token: str | None) -> Page:
        self.search_calls.append(token)
        if token is not None:
            return Page((), None)
        return Page(({
            "conversation_id": "thread-1", "byte_size": 1,
            "discovery_message_ids": ["thread-1-message"],
        },), None)


class FaultStore(MemoryStore):
    def __init__(self) -> None:
        super().__init__()
        self.fail_index_once = True

    def replace(self, reference: DriveReference, data: bytes, mime_type: str) -> StoredArtifact:
        if reference.object_id == "index" and self.fail_index_once:
            self.fail_index_once = False
            raise SystemExit("simulated crash after semantic artifacts")
        return super().replace(reference, data, mime_type)


class ConnectedIngestionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schemas = {
            name: json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))
            for name in ("source-conversation.schema.json", "fact.schema.json", "extraction-result.schema.json")
        }

    def setUp(self) -> None:
        self.store = MemoryStore()
        self.parent = DriveReference("catalog", "root", "application/vnd.google-apps.folder", "https://drive.test/catalog", "1")
        self.index = DriveReference("index", "root", "application/json", "https://drive.test/index", "1")
        self.state = DriveReference("state", "root", "application/json", "https://drive.test/state", "1")
        self.store.seed(self.index, canonical_json_bytes({"schema_version": 1, "records": []}))
        self.store.seed(self.state, canonical_json_bytes({"schema_version": 1, "completed_conversation_ids": [], "units": []}))
        self.interpret_calls = 0
        self.audit_calls = 0

    def worker(self, source: Source, **source_policy: Any) -> ConnectedIngestionWorker:
        def interpret(packet: dict[str, Any]) -> dict[str, Any]:
            self.interpret_calls += 1
            return {
                "candidates": [{
                    "segment_id": segment["segment_id"], "byte_start": 0,
                    "byte_end": len(segment["text"].encode("utf-8")),
                    "candidate_kind": "statement", "category": "school", "entity_scope": "household",
                    "text": "Canonical wording", "flags": {"is_update": True, "is_durable": False, "is_guideline": False, "is_action": False},
                } for segment in packet["segments"]],
                "coverage": [{
                    "segment_id": segment["segment_id"], "byte_start": 0,
                    "byte_end": len(segment["text"].encode("utf-8")),
                    "outcome": "fact", "reason": "school statement",
                } for segment in packet["segments"]],
                "review_cases": [],
            }

        def audit(packet: dict[str, Any], interpreted: dict[str, Any]) -> dict[str, Any]:
            self.audit_calls += 1
            outcome = {
                "packet_sha256": interpreted["packet_sha256"], "interpreted_sha256": interpreted["interpreted_sha256"],
                "coverage": [{
                    "segment_id": segment["segment_id"], "byte_start": 0, "byte_end": len(segment["text"].encode("utf-8")), "outcome": "fact",
                    "source_quote_sha256": hashlib.sha256(segment["text"].encode()).hexdigest(),
                    "interpreted_reason_sha256": hashlib.sha256(b"school statement").hexdigest(),
                    "audit_disposition": "accepted", "reason": "source quote checked",
                } for segment in packet["segments"]],
                "facts": [{
                    "fact_id": fact["fact_id"], "source_quote_sha256": hashlib.sha256(fact["source_quote"].encode()).hexdigest(),
                    "canonical_text_sha256": hashlib.sha256(fact["text"].encode()).hexdigest(),
                    "classification": {"candidate_kind": "statement", "category": "school", "entity_scope": "household", "flags": fact["flags"]},
                    "audit_disposition": "accepted", "reason": "wording checked",
                } for fact in interpreted["facts"]],
                "source_outcomes": [{
                    "outcome_id": item["outcome_id"],
                    "outcome_sha256": sha256_bytes(canonical_json_bytes(item)),
                    "audit_disposition": "accepted",
                    "reason": "policy exclusion checked",
                } for item in packet["source_outcomes"]],
            }
            return outcome

        worker = ConnectedIngestionWorker(
            source=source, store=self.store, adapter_id="gmail-connected",
            catalog_schema=self.schemas["source-conversation.schema.json"], fact_schema=self.schemas["fact.schema.json"],
            extraction_schema=self.schemas["extraction-result.schema.json"], interpreter=interpret, auditor=audit,
            **source_policy,
        )
        # Existing custody/recovery cases share this test-only two-phase
        # convenience wrapper. The production worker deliberately has no
        # combined search/catalog entrypoint.
        def run(*, scope: dict[str, Any], catalog_parent: DriveReference,
                index_reference: DriveReference, continuation_reference: DriveReference,
                max_records: int, max_bytes: int) -> Any:
            discovery = worker.discover(
                scope=scope, discovery_parent=catalog_parent,
                discovery_name=f"test-discovery-{hashlib.sha256(canonical_json_bytes(scope)).hexdigest()}.json",
            )
            return worker.catalog(
                discovery_reference=discovery.inventory.reference,
                catalog_parent=catalog_parent, index_reference=index_reference,
                work_reference=continuation_reference, max_records=max_records,
                max_bytes=max_bytes,
            )
        setattr(worker, "run", run)
        return worker

    def test_body_only_worker_excludes_attachments_and_direct_resources_before_calls(self) -> None:
        class BodyOnlySource(Source):
            def read_conversation(nested_self, identity: str) -> dict[str, Any]:
                value = super().read_conversation(identity)
                message = value["messages"][0]
                attachment_bytes = b"attachment text must not become a Fact"
                message["parts"].append({
                    "part_id": "attachment-1", "role": "attachment",
                    "selected_plaintext": False, "complete": True,
                    "mime_type": "text/plain", "charset": "utf-8",
                    "content_transfer_encoding": "identity", "data": attachment_bytes,
                    "raw_part_sha256": hashlib.sha256(attachment_bytes).hexdigest(),
                    "raw_part_byte_length": len(attachment_bytes),
                    "raw_part_locator": {
                        "kind": "raw_part_bytes", "byte_start": 0,
                        "byte_end": len(attachment_bytes),
                    },
                })
                message["attachments"] = [{
                    "attachment_id": "mime-part-stable", "mime_type": "text/plain",
                    "byte_size": len(attachment_bytes),
                }]
                html = b'<a href="https://assets.example/notice.pdf">Notice</a>'
                message["html_parts"] = [{
                    "part_id": "html-1", "role": "body",
                    "selected_plaintext": False, "complete": True,
                    "mime_type": "text/html", "charset": "utf-8",
                    "content_transfer_encoding": "identity", "data": html,
                    "raw_part_sha256": hashlib.sha256(html).hexdigest(),
                    "raw_part_byte_length": len(html),
                    "raw_part_locator": {
                        "kind": "raw_part_bytes", "byte_start": 0,
                        "byte_end": len(html),
                    },
                    "provider_unicode": html.decode("utf-8"),
                }]
                return value

            def read_attachment(nested_self, _message_id: str, _attachment_id: str) -> Any:
                raise AssertionError("body-only worker called the attachment source")

        worker = self.worker(
            BodyOnlySource({"thread-1": "Body-only source text"}),
            supported_attachment_mime_types=(),
            excluded_attachment_mime_types={"*/*": "body-only policy"},
            attachment_extractors={},
            resource_fetcher=None,
            resource_extractors={},
            excluded_resource_origins={
                "html_embedded": "body-only policy",
                "html_linked": "body-only policy",
            },
        )
        result = worker.run(
            scope={"query": "bounded"}, catalog_parent=self.parent,
            index_reference=self.index, continuation_reference=self.state,
            max_records=1, max_bytes=8192,
        )
        record = parse_v2_record(result.artifacts[0].catalog.data)
        message = record.header["messages"][0]
        self.assertEqual(["excluded_by_policy"], [
            item["outcome"] for item in message["attachments"]
        ])
        self.assertEqual(["excluded_by_policy"], [
            item["outcome"] for item in message["resources"]
        ])
        facts = json.loads(result.artifacts[0].facts.data)["facts"]
        self.assertEqual(1, len(facts))
        self.assertEqual("Body-only source text", facts[0]["source_quote"])

    def test_binds_complete_source_bytes_to_readback_catalog_facts_audit_index_and_state(self) -> None:
        source = Source({"thread-1": "Exact Unicode café\n"})
        result = self.worker(source).run(scope={"query": "bounded"}, catalog_parent=self.parent, index_reference=self.index, continuation_reference=self.state, max_records=1, max_bytes=4096)
        self.assertTrue(result.verified)
        self.assertTrue(result.phase_complete)
        self.assertEqual(("thread-1",), result.completed_units)
        self.assertEqual(1, self.interpret_calls)
        self.assertEqual(1, self.audit_calls)
        record = result.artifacts[0]
        self.assertIn(b"Exact Unicode caf\xc3\xa9\n", record.catalog.data)
        self.assertEqual(["fact-"], [json.loads(record.facts.data)["facts"][0]["fact_id"][:5]])
        self.assertEqual(["thread-1"], json.loads(result.work.data)["completed_conversation_ids"])
        self.assertEqual(1, len(json.loads(result.index.data)["records"]))

        # A fresh worker reads durable continuation and does not rerun completed immutable units.
        replay = self.worker(source).run(scope={"query": "bounded"}, catalog_parent=self.parent, index_reference=result.index.reference, continuation_reference=result.work.reference, max_records=1, max_bytes=4096)
        self.assertEqual((), replay.artifacts)
        self.assertEqual(1, self.interpret_calls)
        self.assertEqual(1, self.audit_calls)

    def test_current_catalog_view_reloads_all_audited_facts_after_zero_new_writes(self) -> None:
        source = Source({"thread-1": "First", "thread-2": "Second"})
        worker = self.worker(source)
        first = worker.run(
            scope={"query": "bounded"}, catalog_parent=self.parent,
            index_reference=self.index, continuation_reference=self.state,
            max_records=2, max_bytes=8192,
        )
        replay = worker.run(
            scope={"query": "bounded"}, catalog_parent=self.parent,
            index_reference=first.index.reference, continuation_reference=first.work.reference,
            max_records=2, max_bytes=8192,
        )
        self.assertEqual((), replay.artifacts)
        view = worker.current_catalog_view(
            catalog_parent=self.parent, index_reference=replay.index.reference,
            max_bytes=8192,
        )
        self.assertEqual(2, len(view.artifacts))
        self.assertEqual(2, len(view.facts))
        self.assertEqual(set(fact["fact_id"] for fact in view.facts), set(view.source_record_map))
        self.assertTrue(all(item["gmail_internal_date_ms"] == 1788854400000 for item in view.source_record_map.values()))
        self.assertTrue(all(item["verified_link"].startswith("https://drive.test/") for item in view.source_record_map.values()))

    def test_interrupted_batch_advances_only_complete_units_then_resumes(self) -> None:
        source = Source({"thread-1": "First", "thread-2": "Second"})
        first = self.worker(source).run(scope={"query": "bounded"}, catalog_parent=self.parent, index_reference=self.index, continuation_reference=self.state, max_records=1, max_bytes=4096)
        self.assertFalse(first.phase_complete)
        self.assertEqual({"conversation_ids": ["thread-2"]}, first.remaining_work)
        resumed = self.worker(source).run(scope={"query": "bounded"}, catalog_parent=self.parent, index_reference=first.index.reference, continuation_reference=first.work.reference, max_records=1, max_bytes=4096)
        self.assertTrue(resumed.phase_complete)
        self.assertEqual(("thread-1", "thread-2"), resumed.completed_units)
        self.assertEqual(2, len(json.loads(resumed.index.data)["records"]))

    def test_catalog_reuses_one_verified_discovery_without_search_or_eligible_cursor_write(self) -> None:
        source = Source({"thread-1": "First", "thread-2": "Second"})
        eligible = DriveReference("eligible", "root", "application/json", "https://drive.test/eligible", "1")
        eligible_bytes = canonical_json_bytes({"eligible": "unchanged"})
        self.store.seed(eligible, eligible_bytes)
        worker = self.worker(source)
        discovery = worker.discover(
            scope={"query": "bounded"}, discovery_parent=self.parent,
            discovery_name="runs/operation-1/discovery.json",
        )
        self.assertEqual([None], source.search_calls)
        with self.assertRaisesRegex(ConnectedIngestionError, "exact verified discovery"):
            worker.catalog(
                discovery_reference=discovery.inventory.reference.current(), catalog_parent=self.parent,
                index_reference=self.index, work_reference=self.state, max_records=1, max_bytes=4096,
            )
        first = worker.catalog(
            discovery_reference=discovery.inventory.reference, catalog_parent=self.parent,
            index_reference=self.index, work_reference=self.state, max_records=1, max_bytes=4096,
        )
        self.assertFalse(first.phase_complete)
        self.assertIsNone(first.proposed_cursor)
        resumed = worker.catalog(
            discovery_reference=discovery.inventory.reference, catalog_parent=self.parent,
            index_reference=first.index.reference, work_reference=first.work.reference,
            max_records=1, max_bytes=4096,
        )
        self.assertTrue(resumed.phase_complete)
        self.assertEqual([None], source.search_calls)
        self.assertEqual(["thread-1", "thread-2"], resumed.proposed_cursor["completed_conversation_ids"])
        self.assertEqual(eligible_bytes, self.store.read(eligible).data)
        self.assertEqual(
            {"schema_version", "completed_conversation_ids", "units", "discovery_sha256"},
            set(json.loads(resumed.work.data)),
        )

    def test_empty_complete_discovery_catalogs_no_provider_work_and_retains_index(self) -> None:
        source = Source({})
        retained_index = canonical_json_bytes({
            "schema_version": 1,
            "records": [{"record_id": "retained-record", "record_sha256": "a" * 64, "fact_ids": []}],
        })
        self.store.seed(self.index, retained_index)
        worker = self.worker(source)
        discovery = worker.discover(
            scope={"query": "bounded"}, discovery_parent=self.parent,
            discovery_name="runs/empty/discovery.json",
        )
        self.assertEqual((), discovery.conversation_ids)
        self.assertEqual([None], source.search_calls)
        result = worker.catalog(
            discovery_reference=discovery.inventory.reference, catalog_parent=self.parent,
            index_reference=self.index, work_reference=self.state, max_records=1, max_bytes=4096,
        )
        self.assertTrue(result.phase_complete)
        self.assertEqual((), result.completed_units)
        self.assertEqual({}, result.remaining_work)
        self.assertEqual((), result.artifacts)
        self.assertEqual([], source.read_calls)
        self.assertEqual(0, self.interpret_calls)
        self.assertEqual(0, self.audit_calls)
        self.assertEqual(retained_index, result.index.data)
        self.assertEqual(self.index, result.index.reference)
        self.assertEqual([], result.proposed_cursor["completed_conversation_ids"])
        self.assertEqual(sha256_bytes(discovery.inventory.data), result.proposed_cursor["discovery_sha256"])
        self.assertEqual(sha256_bytes(discovery.inventory.data), json.loads(result.work.data)["discovery_sha256"])

    def test_discovery_requires_message_anchors_in_source_and_persisted_inventory(self) -> None:
        class MissingHitSource(Source):
            def search(inner_self, _scope: dict[str, Any], token: str | None) -> Page:
                inner_self.search_calls.append(token)
                if token is not None:
                    raise AssertionError("unexpected discovery page")
                return Page(({
                    "conversation_id": "thread-1", "byte_size": 1, "discovery_message_ids": [],
                },), None)

        missing = MissingHitSource({"thread-1": "Body"})
        with self.assertRaisesRegex(ConnectedIngestionError, "no immutable discovery-hit identity"):
            self.worker(missing).discover(
                scope={"query": "bounded"}, discovery_parent=self.parent,
                discovery_name="runs/missing-hit/discovery.json",
            )
        self.assertEqual([], missing.read_calls)
        self.assertEqual({}, self.store.names)

        source = Source({"thread-1": "Body"})
        worker = self.worker(source)
        discovery = worker.discover(
            scope={"query": "bounded"}, discovery_parent=self.parent,
            discovery_name="runs/anchored/discovery.json",
        )
        base = json.loads(discovery.inventory.data)
        for label, mutate in (
            ("page-hit", lambda value: value["pages"][0]["hits"][0].__setitem__("message_ids", [])),
            ("conversation", lambda value: value["conversations"][0].__setitem__("discovery_message_ids", [])),
        ):
            with self.subTest(evidence=label):
                malformed = json.loads(json.dumps(base))
                mutate(malformed)
                artifact = self.store.write_immutable(
                    self.parent, f"runs/malformed-{label}/discovery.json",
                    canonical_json_bytes(malformed), "application/json",
                )
                before_work = self.store.read(self.state).data
                before_index = self.store.read(self.index).data
                with self.assertRaisesRegex(ConnectedIngestionError, "(page hit|conversation has invalid evidence)"):
                    worker.catalog(
                        discovery_reference=artifact.reference, catalog_parent=self.parent,
                        index_reference=self.index, work_reference=self.state, max_records=1, max_bytes=4096,
                    )
                self.assertEqual(before_work, self.store.read(self.state).data)
                self.assertEqual(before_index, self.store.read(self.index).data)
        self.assertEqual([], source.read_calls)

    def test_unbound_direct_resource_blocks_before_any_catalog_state_advance(self) -> None:
        source = Source({"thread-1": "Body"})
        original = source.read_conversation

        def resource_conversation(identity: str) -> dict[str, Any]:
            value = original(identity)
            html = b'<img src="https://assets.example/notice.png">'
            value["messages"][0]["html_parts"] = [{
                "part_id": "html", "complete": True, "mime_type": "text/html", "charset": "utf-8",
                "content_transfer_encoding": "identity", "data": html, "raw_part_sha256": hashlib.sha256(html).hexdigest(),
                "raw_part_byte_length": len(html), "raw_part_locator": {"kind": "raw_part_bytes", "byte_start": 0, "byte_end": len(html)}, "provider_unicode": html.decode(),
            }]
            return value
        source.read_conversation = resource_conversation  # type: ignore[method-assign]
        with self.assertRaisesRegex(ConnectedIngestionError, "resource retrieval is not bound"):
            self.worker(source).run(scope={"query": "bounded"}, catalog_parent=self.parent, index_reference=self.index, continuation_reference=self.state, max_records=1, max_bytes=4096)
        self.assertEqual([], json.loads(self.store.read(self.state).data)["completed_conversation_ids"])

    def test_changed_thread_refreshes_exact_stable_artifacts_and_index(self) -> None:
        source = ReplySource()
        worker = self.worker(source)
        first_discovery = worker.discover(
            scope={"query": "bounded"}, discovery_parent=self.parent,
            discovery_name="runs/first/discovery.json",
        )
        first = worker.catalog(
            discovery_reference=first_discovery.inventory.reference, catalog_parent=self.parent,
            index_reference=self.index, work_reference=self.state, max_records=1, max_bytes=8192,
        )
        first_ids = tuple(item.reference.object_id for item in first.artifacts[0].__dict__.values())
        source.reply = True
        work = DriveReference("work-2", "root", "application/json", "https://drive.test/work-2", "1")
        self.store.seed(work, canonical_json_bytes({"schema_version": 1, "completed_conversation_ids": [], "units": []}))
        second_discovery = worker.discover(
            scope={"query": "bounded"}, discovery_parent=self.parent,
            discovery_name="runs/second/discovery.json",
        )
        second = worker.catalog(
            discovery_reference=second_discovery.inventory.reference, catalog_parent=self.parent,
            index_reference=self.index, work_reference=work, max_records=1, max_bytes=8192,
        )
        self.assertEqual(1, len(second.artifacts))
        self.assertEqual(first_ids, tuple(item.reference.object_id for item in second.artifacts[0].__dict__.values()))
        self.assertIn(b"New reply", second.artifacts[0].catalog.data)
        self.assertEqual(2, self.interpret_calls)
        state = json.loads(second.work.data)
        self.assertEqual(["thread-1-message", "reply-message"], state["units"][0]["full_message_ids"])
        self.assertEqual(["reply-message"], state["units"][0]["discovery_message_ids"])
        rows = json.loads(second.index.data)["records"]
        self.assertEqual(second.work.reference.parent_id, "root")
        self.assertEqual(1, len(rows))
        self.assertEqual(state["units"][0]["record_sha256"], rows[0]["record_sha256"])

    def test_completed_thread_is_reread_for_reply_outside_search_predicate(self) -> None:
        source = OutsideQueryReplySource()
        first = self.worker(source).run(
            scope={"query": "bounded"}, catalog_parent=self.parent,
            index_reference=self.index, continuation_reference=self.state,
            max_records=1, max_bytes=8192,
        )
        source.reply = True
        prior_reads = len(source.read_calls)
        second = self.worker(source).run(
            scope={"query": "bounded"}, catalog_parent=self.parent,
            index_reference=self.index, continuation_reference=self.state,
            max_records=1, max_bytes=8192,
        )
        self.assertEqual(1, len(source.read_calls) - prior_reads)
        self.assertEqual(1, len(second.artifacts))
        self.assertIn(b"New reply", second.artifacts[0].catalog.data)
        state = json.loads(second.work.data)
        self.assertEqual(
            ["thread-1-message", "reply-message"],
            state["units"][0]["full_message_ids"],
        )
        self.assertEqual(
            ["thread-1-message"],
            state["units"][0]["discovery_message_ids"],
        )
        self.assertEqual([None], source.search_calls)

    def test_untrusted_completion_claim_is_rebuilt_and_reconciled(self) -> None:
        self.store.seed(self.state, canonical_json_bytes({
            "schema_version": 1,
            "completed_conversation_ids": ["thread-1"],
            "units": [{
                "conversation_id": "thread-1", "record_id": "missing-record",
                "record_sha256": "0" * 64, "fact_ids": ["missing-fact"],
            }],
        }))
        result = self.worker(Source({"thread-1": "Source"})).run(
            scope={"query": "bounded"}, catalog_parent=self.parent,
            index_reference=self.index, continuation_reference=self.state,
            max_records=1, max_bytes=4096,
        )
        self.assertEqual(1, len(result.artifacts))
        self.assertEqual(1, len(json.loads(result.index.data)["records"]))
        self.assertNotEqual("missing-record", json.loads(result.work.data)["units"][0]["record_id"])

    def test_missing_fact_artifact_is_recovered_without_reinterpreting(self) -> None:
        source = Source({"thread-1": "Body"})
        first = self.worker(source).run(
            scope={"query": "bounded"}, catalog_parent=self.parent,
            index_reference=self.index, continuation_reference=self.state,
            max_records=1, max_bytes=4096,
        )
        facts_id = first.artifacts[0].facts.reference.object_id
        facts_name = next(
            name for (parent, name), identifier in self.store.names.items()
            if parent == self.parent.object_id and identifier == facts_id
        )
        del self.store.objects[facts_id]
        del self.store.names[(self.parent.object_id, facts_name)]
        replay = self.worker(source).run(
            scope={"query": "bounded"}, catalog_parent=self.parent,
            index_reference=self.index, continuation_reference=self.state,
            max_records=1, max_bytes=4096,
        )
        self.assertEqual(1, len(replay.artifacts))
        self.assertEqual(1, self.interpret_calls)
        self.assertEqual(1, self.audit_calls)

    def test_orphan_semantic_bundle_is_adopted_after_crash(self) -> None:
        self.store = FaultStore()
        self.store.seed(self.index, canonical_json_bytes({"schema_version": 1, "records": []}))
        self.store.seed(self.state, canonical_json_bytes({"schema_version": 1, "completed_conversation_ids": [], "units": []}))
        source = Source({"thread-1": "Body"})
        with self.assertRaises(SystemExit):
            self.worker(source).run(
                scope={"query": "bounded"}, catalog_parent=self.parent,
                index_reference=self.index, continuation_reference=self.state,
                max_records=1, max_bytes=4096,
            )
        replay = self.worker(source).run(
            scope={"query": "bounded"}, catalog_parent=self.parent,
            index_reference=self.index, continuation_reference=self.state,
            max_records=1, max_bytes=4096,
        )
        self.assertTrue(replay.phase_complete)
        self.assertEqual(1, self.interpret_calls)
        self.assertEqual(1, self.audit_calls)

    def test_multi_record_writes_advance_versions_and_original_pointers_restart(self) -> None:
        source = Source({"thread-1": "First", "thread-2": "Second"})
        result = self.worker(source).run(
            scope={"query": "bounded"}, catalog_parent=self.parent,
            index_reference=self.index, continuation_reference=self.state,
            max_records=2, max_bytes=8192,
        )
        self.assertEqual(("thread-1", "thread-2"), result.completed_units)
        replay = self.worker(source).run(
            scope={"query": "bounded"}, catalog_parent=self.parent,
            index_reference=self.index, continuation_reference=self.state,
            max_records=2, max_bytes=8192,
        )
        self.assertEqual((), replay.artifacts)
        self.assertEqual(2, len(json.loads(replay.index.data)["records"]))

    def test_two_hard_fresh_processes_resume_from_original_mutable_pointers(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            command = [
                sys.executable, str(ROOT / "tests" / "fresh_process_ingestion.py"), temporary,
            ]
            environment = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
            first = json.loads(subprocess.run(
                command, cwd=ROOT, env=environment, check=True,
                text=True, capture_output=True,
            ).stdout)
            second = json.loads(subprocess.run(
                command, cwd=ROOT, env=environment, check=True,
                text=True, capture_output=True,
            ).stdout)
            third = json.loads(subprocess.run(
                command, cwd=ROOT, env=environment, check=True,
                text=True, capture_output=True,
            ).stdout)
        self.assertEqual(["thread-1"], first["completed"])
        self.assertEqual(["thread-1", "thread-2"], second["completed"])
        self.assertEqual(0, third["written"])
        self.assertNotEqual(first["index_version"], second["index_version"])
        self.assertNotEqual(first["state_version"], second["state_version"])

    def test_work_continuation_rejects_a_different_discovery_inventory(self) -> None:
        source = Source({"thread-1": "Body"})
        self.worker(source).run(
            scope={"query": "first"}, catalog_parent=self.parent,
            index_reference=self.index, continuation_reference=self.state,
            max_records=1, max_bytes=4096,
        )
        with self.assertRaisesRegex(ConnectedIngestionError, "different discovery inventory"):
            self.worker(source).run(
                scope={"query": "second"}, catalog_parent=self.parent,
                index_reference=self.index, continuation_reference=self.state,
                max_records=1, max_bytes=4096,
            )
        self.assertEqual(1, self.interpret_calls)

    def test_duplicate_discovery_hits_are_distinct_from_full_membership(self) -> None:
        class DuplicateHitSource(Source):
            def search(inner_self, _scope: dict[str, Any], token: str | None) -> Page:
                inner_self.search_calls.append(token)
                if token is not None:
                    return Page((), None)
                return Page((
                    {"conversation_id": "thread-1", "byte_size": 1, "discovery_message_ids": ["hit-1"]},
                    {"conversation_id": "thread-1", "byte_size": 1, "discovery_message_ids": ["hit-2"]},
                ), None)

            def read_conversation(inner_self, identity: str) -> dict[str, Any]:
                inner_self.read_calls.append(identity)
                return {
                    "conversation_id": identity,
                    "messages": [{
                        "message_id": message_id,
                        "received_at": f"2026-09-0{ordinal}T08:00:00Z",
                        "received_date": f"2026-09-0{ordinal}",
                        "mime_tree_complete": True,
                        "parts": [_part(body)], "attachments": [], "html_parts": [],
                    } for ordinal, (message_id, body) in enumerate((
                        ("hit-1", b"First"), ("hit-2", b"Second"), ("member-3", b"Third")
                    ), start=1)],
                }

        result = self.worker(DuplicateHitSource({"thread-1": "unused"})).run(
            scope={"query": "bounded"}, catalog_parent=self.parent,
            index_reference=self.index, continuation_reference=self.state,
            max_records=1, max_bytes=8192,
        )
        state = json.loads(result.work.data)
        self.assertEqual(["hit-1", "hit-2"], state["units"][0]["discovery_message_ids"])
        self.assertEqual(["hit-1", "hit-2", "member-3"], state["units"][0]["full_message_ids"])
        self.assertEqual(
            ["included", "duplicate"],
            [item["outcome"] for item in json.loads(result.discovery.data)["dispositions"]],
        )


class CodexDriveArtifactStoreTests(unittest.TestCase):
    class Drive:
        def __init__(self) -> None:
            self.items: dict[str, dict[str, Any]] = {
                "state": {"id": "state", "parent_id": "root", "mime_type": "application/json", "url": "https://drive.test/state", "data": b"{}", "modified_time": "1", "title": "state.json"},
            }
            self.count = 1

        def metadata(self, identifier: str, *, fields: str) -> dict[str, Any]:
            value = self.items[identifier]
            return {"id": identifier, "mime_type": value["mime_type"], "parent_ids": [value["parent_id"]], "modified_time": value["modified_time"], "size": len(value["data"])}

        def fetch(self, url: str, *, raw: bool, include_base64: bool) -> dict[str, Any]:
            value = next(item for item in self.items.values() if item["url"] == url)
            return {"id": value["id"], "b64_string": base64.b64encode(value["data"]).decode(), "file_size_bytes": len(value["data"]), "is_empty": not value["data"]}

        def search_page(self, parent_id: str, *, item_type: str, topn: int, page_token: str | None = None) -> dict[str, Any]:
            if page_token is not None:
                raise AssertionError("synthetic artifact listing has one page per type")
            results = [
                {key: item[key] for key in ("id", "title", "mime_type", "url")} | {"parent_ids": [item["parent_id"]]}
                for item in self.items.values()
                if item["parent_id"] == parent_id and (
                    "folder" if item["mime_type"] == "application/vnd.google-apps.folder"
                    else "image" if item["mime_type"].startswith("image/") else "document"
                ) == item_type
            ]
            return {"results": results, "next_page_token": None}

        def upload(self, file_uri: str, *, file_name: str, mime_type: str, parent_folder_id: str) -> dict[str, Any]:
            self.count += 1; identifier = f"new-{self.count}"
            self.assert_absolute(file_uri)
            self.items[identifier] = {"id": identifier, "parent_id": parent_folder_id, "mime_type": mime_type, "url": f"https://drive.test/{identifier}", "data": Path(file_uri).read_bytes(), "modified_time": str(self.count), "title": file_name}
            value = self.items[identifier]
            return {"success": True, **{key: value[key] for key in ("id", "parent_id", "mime_type", "url")}}

        def update(self, identifier: str, *, file_uri: str, mime_type: str) -> dict[str, Any]:
            self.count += 1; value = self.items[identifier]
            self.assert_absolute(file_uri)
            value["data"] = Path(file_uri).read_bytes(); value["mime_type"] = mime_type; value["modified_time"] = str(self.count)
            return {"success": True, "parent_ids": [value["parent_id"]], "size": len(value["data"]), **{key: value[key] for key in ("id", "mime_type", "url", "modified_time")}}

        @staticmethod
        def assert_absolute(file_uri: str) -> None:
            if not Path(file_uri).is_absolute() or file_uri.startswith("file:"):
                raise AssertionError("Drive file_uri must be an absolute local path")

    def test_drive_store_requires_connector_readback_for_create_and_replace(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            drive = self.Drive()
            store = CodexDriveArtifactStore(drive, scratch_directory=Path(temporary))
            parent = DriveReference("root", "root", "application/vnd.google-apps.folder", "https://drive.test/root")
            created = store.write_immutable(parent, "record.md", b"exact", "text/markdown")
            self.assertEqual(b"exact", created.data)
            initial = DriveReference("state", "root", "application/json", "https://drive.test/state", "1")
            replaced = store.replace(initial, b'{"next":1}', "application/json")
            self.assertEqual(b'{"next":1}', replaced.data)
            self.assertNotEqual("1", replaced.reference.version)

    def test_immutable_adoption_requires_the_requested_mime_type(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            drive = self.Drive()
            drive.items["wrong"] = {
                "id": "wrong", "parent_id": "root", "mime_type": "application/octet-stream",
                "url": "https://drive.test/wrong", "data": b"exact", "modified_time": "2",
                "title": "record.md",
            }
            store = CodexDriveArtifactStore(drive, scratch_directory=Path(temporary))
            parent = DriveReference(
                "root", "root", "application/vnd.google-apps.folder", "https://drive.test/root"
            )
            with self.assertRaisesRegex(ConnectedIngestionError, "MIME type differs"):
                store.write_immutable(parent, "record.md", b"exact", "text/markdown")

    def test_drive_read_rejects_nonstandard_base64_and_size_mismatch(self) -> None:
        class BadDrive(self.Drive):
            def fetch(self, url: str, *, raw: bool, include_base64: bool) -> dict[str, Any]:
                value = next(item for item in self.items.values() if item["url"] == url)
                return {
                    "id": value["id"], "b64_string": "_w", "file_size_bytes": 1,
                    "is_empty": False,
                }

        with tempfile.TemporaryDirectory() as temporary:
            store = CodexDriveArtifactStore(BadDrive(), scratch_directory=Path(temporary))
            reference = DriveReference(
                "state", "root", "application/json", "https://drive.test/state", "1"
            )
            with self.assertRaisesRegex(ConnectedIngestionError, "invalid base64"):
                store.read(reference)


class CodexGmailSourceAdapterTests(unittest.TestCase):
    class Gmail:
        def __init__(self) -> None:
            self.calls: list[tuple[str, Any]] = []

        def search_ids(self, **arguments: Any) -> dict[str, Any]:
            self.calls.append(("search", arguments))
            return {"message_ids": ["hit-1"], "next_page_token": None}

        def read(self, message_id: str, format: str) -> dict[str, Any]:
            self.calls.append(("read", (message_id, format)))
            return {"id": message_id, "thread_id": "thread-1", "format": format}

        def read_thread(self, thread_id: str, *, max_messages: int) -> dict[str, Any]:
            self.calls.append(("thread", (thread_id, max_messages)))
            return {"id": thread_id, "messages": [{"id": "hit-1", "thread_id": thread_id}]}

        def read_attachment(self, message_id: str, attachment_id: str) -> dict[str, Any]:
            self.calls.append(("attachment", (message_id, attachment_id)))
            return {"id": attachment_id}

    def test_gmail_adapter_reads_page_full_thread_raw_body_and_attachment_with_exact_id_checks(self) -> None:
        gmail = self.Gmail()

        def normalize_message(full: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any]:
            self.assertEqual("hit-1", full["id"])
            self.assertEqual("raw", raw["format"])
            return {
                "message_id": full["id"], "thread_id": full["thread_id"],
                "received_at": "2026-09-08T00:00:00Z", "received_date": "2026-09-08",
                "mime_tree_complete": True, "parts": [_part(b"body")], "attachments": [], "html_parts": [],
            }

        adapter = CodexGmailSourceAdapter(
            gmail, max_thread_messages=10, normalize_message=normalize_message,
            normalize_attachment=lambda _message, attachment, _raw: __import__("school_os.adapters", fromlist=["ReadResult"]).ReadResult(b"x", attachment, "file", None, "text/plain", "1"),
        )
        page = adapter.search({"query": "newer_than:14d", "label_ids": ["INBOX"], "max_results": 25}, None)
        self.assertEqual("thread-1", page.items[0]["conversation_id"])
        conversation = adapter.read_conversation("thread-1")
        self.assertEqual("hit-1", conversation["messages"][0]["message_id"])
        attachment = adapter.read_attachment("hit-1", "attachment-1")
        self.assertEqual("attachment-1", attachment.identity)
        self.assertEqual(
            ["search", "read", "thread", "read", "attachment"],
            [item[0] for item in gmail.calls],
        )

    def test_gmail_adapter_body_only_guard_blocks_before_attachment_provider_call(self) -> None:
        gmail = self.Gmail()
        adapter = CodexGmailSourceAdapter(
            gmail, max_thread_messages=10,
            normalize_message=lambda _full, _raw: {},
            normalize_attachment=lambda _message, _attachment, _raw: self.fail(
                "disabled attachment normalizer was called"
            ),
            attachment_reads_enabled=False,
        )
        with self.assertRaisesRegex(ConnectedIngestionError, "disabled by source policy"):
            adapter.read_attachment("message-1", "attachment-1")
        self.assertEqual([], gmail.calls)

    def test_gmail_adapter_rejects_raw_or_normalized_cross_thread_identity(self) -> None:
        class WrongRawThread(self.Gmail):
            def read(inner_self, message_id: str, format: str) -> dict[str, Any]:
                result = super(WrongRawThread, inner_self).read(message_id, format)
                if format == "raw":
                    result["thread_id"] = "other-thread"
                return result

        adapter = CodexGmailSourceAdapter(
            WrongRawThread(), max_thread_messages=10,
            normalize_message=lambda full, _raw: {
                "message_id": full["id"], "thread_id": full["thread_id"],
            },
            normalize_attachment=lambda _message, _attachment, _raw: None,
        )
        adapter.search(
            {"query": "newer_than:14d", "label_ids": ["INBOX"], "max_results": 25},
            None,
        )
        with self.assertRaisesRegex(ConnectedIngestionError, "message/thread identity"):
            adapter.read_conversation("thread-1")

        adapter = CodexGmailSourceAdapter(
            self.Gmail(), max_thread_messages=10,
            normalize_message=lambda full, _raw: {
                "message_id": full["id"], "thread_id": "other-thread",
            },
            normalize_attachment=lambda _message, _attachment, _raw: None,
        )
        adapter.search(
            {"query": "newer_than:14d", "label_ids": ["INBOX"], "max_results": 25},
            None,
        )
        with self.assertRaisesRegex(ConnectedIngestionError, "message/thread identity"):
            adapter.read_conversation("thread-1")

    def test_gmail_seed_window_filters_full_hits_but_retains_selected_thread_context(self) -> None:
        start, end = 1788854400000, 1788940800000

        class WindowGmail:
            def __init__(inner_self) -> None:
                inner_self.query = None
                inner_self.messages = {
                    "before": ("thread-before", start - 1),
                    "at-start": ("thread-selected", start),
                    "at-last": ("thread-last", end - 1),
                    "at-end": ("thread-end", end),
                    "older-context": ("thread-selected", start - 86_400_000),
                }

            def search_ids(inner_self, **arguments):
                inner_self.query = arguments["query"]
                return {"message_ids": ["before", "at-start", "at-last", "at-end"], "next_page_token": None}

            def read(inner_self, message_id: str, format: str):
                thread_id, timestamp = inner_self.messages[message_id]
                return {"id": message_id, "thread_id": thread_id, "internal_date": str(timestamp), "format": format}

            def read_thread(inner_self, thread_id: str, *, max_messages: int):
                identities = [
                    identity for identity, (member_thread, _timestamp) in inner_self.messages.items()
                    if member_thread == thread_id
                ]
                return {"id": thread_id, "messages": [inner_self.read(identity, "full") for identity in identities]}

            def read_attachment(inner_self, _message_id: str, attachment_id: str):
                return {"id": attachment_id}

        gmail = WindowGmail()
        adapter = CodexGmailSourceAdapter(
            gmail, max_thread_messages=10,
            normalize_message=lambda full, _raw: {
                "message_id": full["id"], "thread_id": full["thread_id"],
                "received_at": "2026-09-08T00:00:00Z", "received_date": "2026-09-08",
                "gmail_internal_date_ms": int(full["internal_date"]),
                "mime_tree_complete": True, "parts": [_part(b"body")],
                "attachments": [], "html_parts": [],
            },
            normalize_attachment=lambda _message, _attachment, _raw: None,
        )
        page = adapter.search({
            "query": "from:school", "label_ids": ["INBOX"], "max_results": 100,
            "seed_after_inclusive_ms": start, "seed_before_exclusive_ms": end,
        }, None)
        self.assertEqual("from:school after:1788854399 before:1788940801", gmail.query)
        self.assertEqual(["thread-selected", "thread-last"], [item["conversation_id"] for item in page.items])
        selected = adapter.read_conversation("thread-selected")
        self.assertEqual(["at-start", "older-context"], [item["message_id"] for item in selected["messages"]])
        with self.assertRaisesRegex(ConnectedIngestionError, "provider date predicate"):
            adapter.search({
                "query": "from:school newer_than:14d", "label_ids": ["INBOX"], "max_results": 100,
                "seed_after_inclusive_ms": start, "seed_before_exclusive_ms": end,
            }, None)

    def test_semantic_callbacks_use_separate_fixed_calls(self) -> None:
        class Semantic:
            def __init__(self) -> None:
                self.calls: list[str] = []
            def interpret(self, packet: dict[str, Any]) -> dict[str, Any]:
                self.calls.append("interpret"); return {"packet": packet}
            def audit(self, packet: dict[str, Any], interpretation: dict[str, Any]) -> dict[str, Any]:
                self.calls.append("audit"); return {"packet": packet, "interpretation": interpretation}
        semantic = Semantic()
        callbacks = CodexSemanticCallbacks(semantic)
        interpreted = callbacks.interpret({"source": "exact"})
        audited = callbacks.audit({"source": "exact"}, interpreted)
        self.assertEqual(["interpret", "audit"], semantic.calls)
        self.assertEqual("exact", audited["packet"]["source"])


if __name__ == "__main__":
    unittest.main()
