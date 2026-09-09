from __future__ import annotations

import base64
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from school_os.connected_tasks import (  # noqa: E402
    ConnectedTaskWorker,
    unresolved_finite_task_selection,
)
from school_os.connected_storage import DriveReference, StoredArtifact  # noqa: E402
from school_os.contracts import canonical_json_bytes  # noqa: E402
from school_os.tasks import canonical_task_id, reconcile_canonical_tasks  # noqa: E402
from tests.support.fakes import FixtureTasks  # noqa: E402


class MemoryStore:
    def __init__(self, values: dict[str, bytes]) -> None:
        self.values = dict(values)
        self.writes: list[str] = []
        self.reads: list[str] = []
        self.versions = {key: "v1" for key in values}

    def read(self, reference: DriveReference) -> StoredArtifact:
        self.reads.append(reference.object_id)
        version = self.versions[reference.object_id]
        if reference.version is not None and reference.version != version:
            raise AssertionError("stale durable reference")
        return StoredArtifact(DriveReference(reference.object_id, reference.parent_id, reference.mime_type, reference.url, version), self.values[reference.object_id])

    def replace(self, reference: DriveReference, data: bytes, mime_type: str) -> StoredArtifact:
        if mime_type != "application/json":
            raise AssertionError("wrong MIME")
        if reference.version is not None and reference.version != self.versions[reference.object_id]:
            raise AssertionError("replacement used stale durable reference")
        self.values[reference.object_id] = data
        self.versions[reference.object_id] = f"v{int(self.versions[reference.object_id][1:]) + 1}"
        self.writes.append(reference.object_id)
        return StoredArtifact(DriveReference(reference.object_id, reference.parent_id, reference.mime_type, reference.url, self.versions[reference.object_id]), data)


class ConnectedTaskWorkerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fact_schema = json.loads((ROOT / "schemas/fact.schema.json").read_text())
        cls.task_schema = json.loads((ROOT / "schemas/task.schema.json").read_text())
        cls.register_schema = json.loads((ROOT / "schemas/canonical-tasks.schema.json").read_text())
        cls.state_schema = json.loads((ROOT / "schemas/provider-state.schema.json").read_text())

    def refs(self):
        parent = "private-state"
        return (
            DriveReference("facts", parent, "application/json", "memory://facts"),
            DriveReference("tasks", parent, "application/json", "memory://tasks"),
            DriveReference("provider", parent, "application/json", "memory://provider"),
        )

    @staticmethod
    def fact() -> dict:
        return {
            "fact_id": "fact-action", "record_id": "record-1", "source_message_id": "message-1",
            "source_byte_start": 0, "source_byte_end": 3, "received_date": "2026-09-07",
            "entity_scope": "household", "category": "school", "text": "Return form",
            "flags": {"is_update": False, "is_durable": False, "is_guideline": False, "is_action": True},
        }

    def worker(self, store: MemoryStore) -> ConnectedTaskWorker:
        return ConnectedTaskWorker(
            store=store, fact_schema=self.fact_schema, task_schema=self.task_schema,
            register_schema=self.register_schema, provider_state_schema=self.state_schema,
        )

    def test_source_register_is_durable_before_the_second_call_creates(self) -> None:
        facts, tasks, provider_state = self.refs()
        store = MemoryStore({
            facts.object_id: canonical_json_bytes({"schema_version": 1, "record_id": "record-1", "facts": [self.fact()]}),
            tasks.object_id: canonical_json_bytes({"schema_version": 1, "tasks": []}),
            provider_state.object_id: canonical_json_bytes({"provider_id": "synthetic", "adapter_id": "synthetic-tasks", "provider_revision": None, "bindings": [], "cursor": None, "cursor_evidence": {}, "verified_readback": {}}),
        })
        port = FixtureTasks()
        links = {canonical_task_id("fact-action"): "https://example.invalid/source/message-1"}
        first = self.worker(store).run_once(facts=[facts], canonical_tasks=tasks, provider_state=provider_state, provider=port, task_source_links=links)
        self.assertTrue(first.continuation_required)
        self.assertEqual([], port.tasks)
        persisted = json.loads(store.values[tasks.object_id])
        self.assertEqual("fact-action", persisted["tasks"][0]["source_facts"][0])
        self.assertEqual("pending", json.loads(store.values[provider_state.object_id])["effect_intents"][0]["outcome"])
        second = self.worker(store).run_once(facts=[facts], canonical_tasks=first.canonical_tasks.reference, provider_state=first.provider_state.reference, provider=port, task_source_links=links)
        self.assertFalse(second.continuation_required)
        self.assertEqual(1, len(port.tasks))
        self.assertEqual("all_unresolved_finite", second.brief_tasks["selection"])
        self.assertEqual("https://example.invalid/source/message-1", second.brief_tasks["tasks"][0]["source_link"])
        self.assertGreaterEqual(store.writes.count(tasks.object_id), 2)
        self.assertGreaterEqual(store.writes.count(provider_state.object_id), 3)  # intent, pre-dispatch, final state

    def test_public_reconcile_then_provider_sync_uses_returned_reference_without_facts(self) -> None:
        facts, tasks, provider_state = self.refs()
        store = MemoryStore({
            facts.object_id: canonical_json_bytes({"schema_version": 1, "record_id": "record-1", "facts": [self.fact()]}),
            tasks.object_id: canonical_json_bytes({"schema_version": 1, "tasks": []}),
            provider_state.object_id: canonical_json_bytes({"provider_id": "synthetic", "adapter_id": "synthetic-tasks", "provider_revision": None, "bindings": [], "cursor": None, "cursor_evidence": {}, "verified_readback": {}}),
        })
        worker = self.worker(store)
        links = {canonical_task_id("fact-action"): "https://example.invalid/source/message-1"}
        reconciled = worker.reconcile(facts=[facts], canonical_tasks=tasks, task_source_links=links)
        self.assertEqual("tasks", reconciled.canonical_tasks.reference.object_id)
        self.assertEqual([], json.loads(store.values[provider_state.object_id]).get("effect_intents", []))
        # A provider-only pass must consume only the returned canonical pointer,
        # not rederive canonical state from the Fact artifact.
        store.values[facts.object_id] = b"not provider input"
        store.reads.clear()
        first = worker.task_sync(
            canonical_tasks=reconciled.canonical_tasks.reference, provider_state=provider_state,
            provider=FixtureTasks(), task_source_links=links,
        )
        self.assertNotIn(facts.object_id, store.reads)
        self.assertEqual("pending", json.loads(first.provider_state.data)["effect_intents"][0]["outcome"])
        self.assertEqual("all_unresolved_finite", first.brief_tasks["selection"])

    def test_task_sync_rejects_a_newer_canonical_version_before_provider_read(self) -> None:
        facts, tasks, provider_state = self.refs()
        store = MemoryStore({
            facts.object_id: canonical_json_bytes({"schema_version": 1, "record_id": "record-1", "facts": [self.fact()]}),
            tasks.object_id: canonical_json_bytes({"schema_version": 1, "tasks": []}),
            provider_state.object_id: canonical_json_bytes({"provider_id": "synthetic", "adapter_id": "synthetic-tasks", "provider_revision": None, "bindings": [], "cursor": None, "cursor_evidence": {}, "verified_readback": {}}),
        })
        worker = self.worker(store)
        links = {canonical_task_id("fact-action"): "https://example.invalid/source/message-1"}
        reconciled = worker.reconcile(facts=[facts], canonical_tasks=tasks, task_source_links=links)
        exact_data = reconciled.canonical_tasks.data
        exact_version = reconciled.canonical_tasks.reference.version
        substituted = json.loads(exact_data)
        substituted["tasks"][0]["action"] = "substituted after handoff"
        store.values[tasks.object_id] = canonical_json_bytes(substituted)
        store.versions[tasks.object_id] = "v3"
        provider = FixtureTasks()
        store.reads.clear()
        with self.assertRaisesRegex(AssertionError, "stale durable reference"):
            worker.task_sync(
                canonical_tasks=reconciled.canonical_tasks.reference, provider_state=provider_state,
                provider=provider, task_source_links=links,
            )
        self.assertEqual([tasks.object_id], store.reads)
        self.assertEqual([], provider.calls)

        # The exact v2 handoff remains valid and still does not reread Facts.
        store.values[tasks.object_id] = exact_data
        store.versions[tasks.object_id] = exact_version
        store.reads.clear()
        result = worker.task_sync(
            canonical_tasks=reconciled.canonical_tasks.reference, provider_state=provider_state,
            provider=provider, task_source_links=links,
        )
        self.assertNotIn(facts.object_id, store.reads)
        self.assertTrue(result.continuation_required)

    def test_fresh_process_production_sheets_create_and_reminder_recovery(self) -> None:
        """Hard exits use the concrete worker, Sheets port, and durable references.

        Each child starts with no Python state from the prior process.  The
        synthetic connector persists the provider row/comment before exiting,
        then hides it once so a recovery pass must block rather than dispatch.
        A later exact observation adopts the original effect.
        """
        child = ROOT / "tests" / "support" / "connected_task_recovery_child.py"
        with tempfile.TemporaryDirectory() as temporary:
            state = Path(temporary) / "durable-connected-task.json"
            environment = {**os.environ, "PYTHONPATH": str(ROOT)}
            for kind, exit_code, dispatch in (("create", 70, "create"), ("comment", 71, "comment")):
                with self.subTest(effect=kind):
                    initialized = subprocess.run([sys.executable, str(child), "initialize", kind, str(state)], cwd=ROOT, env=environment, text=True, capture_output=True)
                    self.assertEqual(0, initialized.returncode, initialized.stderr)
                    crashed = subprocess.run([sys.executable, str(child), "crash", kind, str(state)], cwd=ROOT, env=environment, text=True, capture_output=True)
                    self.assertEqual(exit_code, crashed.returncode, crashed.stderr)
                    crashed_state = json.loads(state.read_text(encoding="utf-8"))
                    persisted = json.loads(base64.b64decode(crashed_state["artifacts"]["provider"]["data_b64"]))
                    self.assertEqual("unknown", persisted["effect_intents"][0]["outcome"])
                    self.assertEqual(1, crashed_state["dispatches"][dispatch])
                    blocked = subprocess.run([sys.executable, str(child), "block", kind, str(state)], cwd=ROOT, env=environment, text=True, capture_output=True)
                    self.assertEqual(0, blocked.returncode, blocked.stderr)
                    blocked_result = json.loads(blocked.stdout)
                    self.assertTrue(blocked_result["blocked"])
                    self.assertEqual(1, blocked_result["dispatches"][dispatch])
                    self.assertEqual("unknown", blocked_result["effect_intents"][0]["outcome"])
                    recovered = subprocess.run([sys.executable, str(child), "recover", kind, str(state)], cwd=ROOT, env=environment, text=True, capture_output=True)
                    self.assertEqual(0, recovered.returncode, recovered.stderr)
                    recovered_result = json.loads(recovered.stdout)
                    self.assertTrue(recovered_result["recovered"])
                    self.assertEqual(1, recovered_result["dispatches"][dispatch])
                    self.assertEqual([], recovered_result["effect_intents"])

    def test_parent_added_selection_preserves_undated_absent_provenance(self) -> None:
        parent = {
            "task_id": "task-parent-1", "origin": "parent", "action": "Call school",
            "task_context": "", "entity_scope": "household", "workflow_state": "needs_action",
            "owner": None, "source_opened_date": None, "last_supporting_source_date": None,
            "source_due": None, "parent_planned_due": None, "source_link": None,
            "source_facts": [], "latest_progress": None, "provider_bindings": [], "lifecycle_history": [],
            "projection_state": {"resolution": "unresolved"}, "resolution": "unresolved",
            "revision": 1, "last_modified_evidence": {},
        }
        selection = unresolved_finite_task_selection({"schema_version": 1, "tasks": [parent]})
        self.assertEqual("parent", selection["tasks"][0]["origin"])
        self.assertIsNone(selection["tasks"][0]["last_supporting_source_date"])
        self.assertIsNone(selection["tasks"][0]["source_link"])

    def test_verified_no_fact_disposition_allows_task_only_reconciliation(self) -> None:
        facts, tasks, provider_state = self.refs()
        existing = reconcile_canonical_tasks({"schema_version": 1, "tasks": []}, [self.fact()], fact_schema=self.fact_schema, task_schema=self.task_schema, register_schema=self.register_schema)
        store = MemoryStore({
            facts.object_id: canonical_json_bytes({"schema_version": 1, "facts": []}),
            tasks.object_id: canonical_json_bytes(existing),
            provider_state.object_id: canonical_json_bytes({"provider_id": "synthetic", "adapter_id": "synthetic-tasks", "provider_revision": None, "bindings": [], "cursor": None, "cursor_evidence": {}, "verified_readback": {}}),
        })
        result = self.worker(store).run_once(facts=[], canonical_tasks=tasks, provider_state=provider_state, provider=FixtureTasks(), task_source_links={canonical_task_id("fact-action"): "https://example.invalid/source/message-1"}, source_disposition={"verified": True, "phase_complete": True, "remaining_work": {}})
        self.assertTrue(result.continuation_required)
        self.assertEqual("source", result.brief_tasks["tasks"][0]["origin"])

    def test_selection_invokes_the_accepted_brief_builder_with_later_support_date(self) -> None:
        source = {
            "task_id": "task-source", "origin": "source", "action": "Use corrected action",
            "task_context": "school", "entity_scope": "household", "workflow_state": "needs_action",
            "owner": None, "source_opened_date": "2026-09-01", "last_supporting_source_date": "2026-09-07",
            "source_due": None, "parent_planned_due": None, "source_link": "record#fact", "source_facts": ["fact-1"],
            "latest_progress": None, "provider_bindings": [], "lifecycle_history": [], "projection_state": {"resolution": "unresolved"},
            "resolution": "unresolved", "revision": 1, "last_modified_evidence": {},
        }
        parent = {**source, "task_id": "task-parent", "origin": "parent", "action": "Parent action", "source_opened_date": None, "last_supporting_source_date": None, "source_link": None, "source_facts": []}
        selection = unresolved_finite_task_selection({"schema_version": 1, "tasks": [source, parent]}, task_source_links={"task-source": "https://example.invalid/source/message-1"})
        self.assertEqual("2026-09-07", selection["tasks"][1]["last_supporting_source_date"])
        code = """import json, os
from school_os.brief import build_brief_input
selection=json.loads(os.environ['TASK_SELECTION'])
fact={'fact_id':'fact-1','record_id':'record-1','source_message_id':'message-1','received_date':'2026-09-07','entity_scope':'household','text':'Update','flags':{'is_update':False,'is_guideline':False,'is_action':True}}
value=build_brief_input(run_local_date='2026-09-07', timezone='UTC', entities=[{'entity_id':'household','display_name':'Household','kind':'household'}], scope_to_entity={'household':'household'}, facts=[fact], source_record_map={'fact-1':{'record_id':'record-1','source_message_id':'message-1','gmail_internal_date_ms':1788768000000,'source_message_ordinal':0,'source_content_ordinal':0,'verified_link':'https://example.invalid/source/message-1'}}, current_guideline_selection=[], unresolved_task_view=selection, input_hashes={})
assert value['tasks'][0]['received_date'] is None
assert value['tasks'][1]['received_date']=='2026-09-07'
"""
        environment = {**os.environ, "PYTHONPATH": str(ROOT), "TASK_SELECTION": json.dumps(selection)}
        result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=environment, cwd=ROOT)
        self.assertEqual(0, result.returncode, result.stderr)


if __name__ == "__main__":
    unittest.main()
