from __future__ import annotations

import base64
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class FreshProcessRecoveryTests(unittest.TestCase):
    def test_recovery_evidence_manifest_names_restart_cases(self) -> None:
        evidence = json.loads((ROOT / "tests" / "synthetic-fixtures" / "alpha13" / "recovery-evidence.json").read_text(encoding="utf-8"))
        self.assertEqual(1, evidence["schema_version"])
        self.assertEqual(
            [
                "planned-boundary resume after deleted local output",
                "catalog record before durable index",
                "task create/update after provider persistence",
                "system comment after provider persistence",
                "delivery after provider acceptance before confirmation",
            ],
            evidence["fresh_process_cases"],
        )

    def restart(self, root: Path, payload: dict) -> dict:
        durable = root / "durable-state.json"
        output = root / "recovered-state.json"
        local = root / "discardable-local-work"
        durable.write_text(json.dumps(payload), encoding="utf-8")
        local.write_text("discardable", encoding="utf-8")
        local.unlink()
        result = subprocess.run(
            [sys.executable, "tests/support/fresh_process_recovery.py", str(durable), str(output)],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        return json.loads(output.read_text(encoding="utf-8"))

    def test_deleted_local_output_resumes_in_a_new_process(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            durable = root / "durable.json"
            local = root / "local-output.json"
            durable.write_text(json.dumps({"previous": {"verified": True, "phase": "catalog"}}), encoding="utf-8")
            local.write_text("discardable", encoding="utf-8")
            local.unlink()
            code = (
                "import json,sys; from pathlib import Path; "
                "from tests.test_daily_runner import DailyRunnerTests; "
                "from school_os.daily import run_daily; "
                "x=DailyRunnerTests('test_manual_runs_all_phases_without_scheduler'); x.setUpClass(); "
                "stages,_=x.stages(); data=json.loads((Path(sys.argv[1])/'durable.json').read_text()); "
                "r=run_daily(profile=x.profile('manual'),capability_schema=x.schema,entrypoint='manual',operation_id='daily-001',attempt_id='attempt-002',stages=stages,resume_after='catalog',durable_predecessor_output=data['previous']); "
                "print(json.dumps([r.outcome,r.operation_id,r.attempt_id,next(iter(r.outputs))]))"
            )
            result = subprocess.run([sys.executable, "-c", code, str(root)], cwd=ROOT, text=True, capture_output=True, check=False)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(["COMPLETE", "daily-001", "attempt-002", "reconcile"], json.loads(result.stdout))

    def test_catalog_task_comment_and_delivery_recover_in_new_processes(self) -> None:
        from school_os.catalog import serialize_v2_record, stable_record_id
        from school_os.contracts import canonical_json_bytes, sha256_bytes

        conversation = {
            "schema_version": 1, "adapter_id": "synthetic-mail", "conversation_id": "restart-001", "scope": {},
            "pagination": {"completed": True}, "messages": [{"message_id": "message-001", "received_at": "2026-09-07T08:00:00-07:00", "body": "Return form", "attachments": []}],
        }
        schema = json.loads((ROOT / "schemas" / "source-conversation.schema.json").read_text(encoding="utf-8"))
        record = serialize_v2_record(conversation, schema)
        task = {"task_id": "task-1", "origin": "source", "action": "Return form", "task_context": "school", "entity_scope": "household", "workflow_state": "needs_action", "owner": None, "source_opened_date": "2026-09-07", "last_supporting_source_date": "2026-09-07", "source_due": None, "parent_planned_due": None, "source_link": "record-1#fact-1", "source_facts": ["fact-1"], "latest_progress": None, "provider_bindings": [], "lifecycle_history": [], "projection_state": {}, "revision": 1, "last_modified_evidence": {}}
        projection = {"canonical_task_id": "task-1", "origin": "source", "title": "Return form", "description": "school", "group": "household", "workflow_state": "needs_action", "source_link": "record-1#fact-1", "source_due": ""}
        projection_hash = sha256_bytes(canonical_json_bytes(projection))
        state = {"provider_id": "synthetic", "adapter_id": "synthetic-tasks", "provider_revision": None, "bindings": [], "effect_intents": [{"effect_id": "effect-task-create-restart", "kind": "task_create", "task_id": "task-1", "projection_sha256": projection_hash, "projection": projection, "outcome": "unknown", "dispatch_attempt": 1, "verification": {"prior_attempt": "lost_response"}}], "cursor": None, "cursor_evidence": {}, "verified_readback": {}}
        content = b"synthetic durable delivery"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            catalog = self.restart(root, {"kind": "catalog", "source_bodies": {"message-001": "Return form"}, "intended_b64": base64.b64encode(record).decode(), "persisted_b64": base64.b64encode(record).decode(), "index": {"schema_version": 1, "records": []}, "facts": [{"fact_id": "fact-restart-001", "record_id": stable_record_id("synthetic-mail", "restart-001")}]})
            self.assertEqual(1, len(catalog["index"]["records"]))
            recovered_task = self.restart(root, {"kind": "task", "register": {"schema_version": 1, "tasks": [task]}, "provider_state": state, "provider_tasks": [{**projection, "provider_object_id": "synthetic-task-1"}]})
            self.assertEqual(1, recovered_task["provider_task_count"])
            self.assertEqual("task-1", recovered_task["bindings"][0]["task_id"])
            self.assertEqual("adopt", recovered_task["effects"][0]["kind"])
            recovered_comment = self.restart(root, {"kind": "comment", "provider_object_id": "synthetic-task-1", "effect_id": "comment-1", "text": "Parent progress", "comments": [{"provider_object_id": "synthetic-task-1", "effect_id": "comment-1", "text": "Parent progress"}]})
            self.assertEqual(1, recovered_comment["comment_count"])
            recovered_delivery = self.restart(root, {"kind": "delivery", "content_b64": base64.b64encode(content).decode(), "delivery_key": "delivery-restart-001", "ledger": {"schema_version": 1, "entries": [{"delivery_key": "delivery-restart-001", "variant": "normal", "content_sha256": hashlib.sha256(content).hexdigest(), "recipients_fingerprint": "a" * 64, "outcome": "pending", "provider_message_id": None, "verification": {}}]}})
            self.assertEqual(1, recovered_delivery["delivery_count"])
            self.assertEqual("confirmed", recovered_delivery["ledger"]["entries"][0]["outcome"])


if __name__ == "__main__":
    unittest.main()
