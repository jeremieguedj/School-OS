from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from school_os.agent_tasks import (  # noqa: E402
    AgentTaskError, authorize_next_action, confirm_action,
    initialize_provider_state, normalized_observation, plan_task_sync,
)
from school_os.contracts import sha256_bytes  # noqa: E402


class AgentTaskTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schemas = {
            name: json.loads((ROOT / "schemas" / name).read_text())
            for name in (
                "task.schema.json", "canonical-tasks.schema.json",
                "provider-state.schema.json", "task-adapter-snapshot.schema.json",
                "task-adapter-action.schema.json", "task-adapter-result.schema.json",
            )
        }

    def task(self, *, action: str = "Return form") -> dict:
        return {
            "task_id": "task-1", "origin": "source", "action": action,
            "task_context": "School", "entity_scope": "household",
            "workflow_state": "needs_action", "owner": None,
            "source_opened_date": "2026-09-07",
            "last_supporting_source_date": "2026-09-07", "source_due": None,
            "parent_planned_due": None, "source_link": "record-1#fact-1",
            "source_facts": ["fact-1"], "latest_progress": None,
            "provider_bindings": [], "lifecycle_history": [],
            "projection_state": {"resolution": "unresolved"},
            "resolution": "unresolved", "revision": 1,
            "last_modified_evidence": {},
        }

    def state(self) -> dict:
        return initialize_provider_state(
            provider_id="projection-1", adapter_id="agent-sheet-v1",
            binding_id="binding-1", scope_sha256="a" * 64,
        )

    def snapshot(self, tasks=(), candidates=(), *, request_id="read-1") -> dict:
        return {
            "schema_version": 1, "contract_version": "agent-task-v1",
            "request_id": request_id, "provider_id": "projection-1",
            "adapter_id": "agent-sheet-v1", "binding_id": "binding-1",
            "scope_sha256": "a" * 64, "capture_id": "capture-1",
            "captured_at": "2026-09-10T10:00:00-07:00", "complete": True,
            "collections": [{
                "name": "tasks", "complete": True,
                "next_page_token": None, "item_count": len(tasks),
            }],
            "tasks": list(tasks), "unbound_candidates": list(candidates),
            "proposed_cursor": "cursor-1",
            "evidence": {"private_receipt_sha256": "b" * 64},
        }

    def observed(self, **changes) -> dict:
        value = {
            "provider_object_id": "provider-task-1",
            "canonical_task_id": "task-1", "origin": "source",
            "action": "Return form", "task_context": "School",
            "entity_scope": "household", "workflow_state": "needs_action",
            "source_link": "record-1#fact-1", "source_due": None,
            "parent_planned_due": None, "latest_progress": None,
            "resolution": "unresolved", "completion_comment": None,
            "provider_revision": "revision-1", "comment_evidence": [],
        }
        value.update(changes)
        return normalized_observation(value)

    def plan(self, register, state, snapshot):
        return plan_task_sync(
            register, state, snapshot,
            task_schema=self.schemas["task.schema.json"],
            register_schema=self.schemas["canonical-tasks.schema.json"],
            provider_state_schema=self.schemas["provider-state.schema.json"],
            snapshot_schema=self.schemas["task-adapter-snapshot.schema.json"],
            action_schema=self.schemas["task-adapter-action.schema.json"],
        )

    def test_empty_complete_projection_plans_no_provider_call_and_confirms_create(self) -> None:
        register = {"schema_version": 1, "tasks": [self.task()]}
        planned = self.plan(register, self.state(), self.snapshot())
        self.assertEqual(["create_task"], [item["kind"] for item in planned.actions])
        self.assertEqual([], planned.provider_state["bindings"])
        authorized_state, action = authorize_next_action(
            planned.provider_state,
            action_schema=self.schemas["task-adapter-action.schema.json"],
            provider_state_schema=self.schemas["provider-state.schema.json"],
        )
        self.assertEqual("unknown", action["outcome"])
        self.assertEqual(1, action["dispatch_attempt"])
        readback = self.observed()
        result = {
            "schema_version": 1, "contract_version": "agent-task-v1",
            "effect_id": action["effect_id"], "provider_id": "projection-1",
            "adapter_id": "agent-sheet-v1", "binding_id": "binding-1",
            "scope_sha256": "a" * 64, "outcome": "confirmed",
            "readback": readback, "guard_evidence": {"matched": True},
            "postcondition_evidence": {"matched": True},
            "evidence": {"private_receipt_sha256": "c" * 64},
        }
        confirmed = confirm_action(
            planned.canonical_tasks, authorized_state, result,
            register_schema=self.schemas["canonical-tasks.schema.json"],
            provider_state_schema=self.schemas["provider-state.schema.json"],
            action_schema=self.schemas["task-adapter-action.schema.json"],
            result_schema=self.schemas["task-adapter-result.schema.json"],
        )
        self.assertEqual((), confirmed.remaining_actions)
        self.assertEqual("provider-task-1", confirmed.provider_state["bindings"][0]["provider_object_id"])
        self.assertEqual("cursor-1", confirmed.provider_state["cursor"])
        self.assertEqual("provider-task-1", confirmed.canonical_tasks["tasks"][0]["provider_bindings"][0]["provider_object_id"])

    def test_parent_only_edit_is_imported_before_update_action(self) -> None:
        initial = self.plan(
            {"schema_version": 1, "tasks": [self.task()]}, self.state(),
            self.snapshot([self.observed()]),
        )
        self.assertEqual((), initial.actions)
        edited = self.observed(
            action="Parent wording", parent_planned_due="2026-09-15",
            provider_revision="revision-2",
        )
        planned = self.plan(initial.canonical_tasks, initial.provider_state, self.snapshot([edited]))
        task = planned.canonical_tasks["tasks"][0]
        self.assertEqual("Parent wording", task["action"])
        self.assertEqual("2026-09-15", task["parent_planned_due"])
        self.assertEqual((), planned.actions)

    def test_simultaneous_parent_and_canonical_change_is_durable_review(self) -> None:
        initial = self.plan(
            {"schema_version": 1, "tasks": [self.task()]}, self.state(),
            self.snapshot([self.observed()]),
        )
        changed = json.loads(json.dumps(initial.canonical_tasks))
        changed["tasks"][0]["action"] = "Canonical wording"
        remote = self.observed(action="Parent wording", provider_revision="revision-2")
        planned = self.plan(changed, initial.provider_state, self.snapshot([remote]))
        self.assertEqual("needs_review", planned.canonical_tasks["tasks"][0]["workflow_state"])
        self.assertEqual("Return form", planned.provider_state["bindings"][0]["last_parent_snapshot"]["action"]["value"])
        self.assertEqual((), planned.actions)
        self.assertEqual("simultaneous canonical and parent changes", planned.review_cases[0]["reason"])

    def test_incomplete_or_provider_specific_snapshot_blocks(self) -> None:
        incomplete = self.snapshot()
        incomplete["complete"] = False
        with self.assertRaisesRegex(AgentTaskError, "invalid task-adapter snapshot"):
            self.plan({"schema_version": 1, "tasks": [self.task()]}, self.state(), incomplete)
        polluted = self.observed()
        polluted["sheet_row"] = 9
        with self.assertRaisesRegex(AgentTaskError, "provider-specific"):
            self.plan(
                {"schema_version": 1, "tasks": [self.task()]}, self.state(),
                self.snapshot([polluted]),
            )

    def test_unknown_result_never_advances_binding_or_cursor(self) -> None:
        planned = self.plan(
            {"schema_version": 1, "tasks": [self.task()]}, self.state(), self.snapshot(),
        )
        authorized, action = authorize_next_action(
            planned.provider_state,
            action_schema=self.schemas["task-adapter-action.schema.json"],
            provider_state_schema=self.schemas["provider-state.schema.json"],
        )
        result = {
            "schema_version": 1, "contract_version": "agent-task-v1",
            "effect_id": action["effect_id"], "provider_id": "projection-1",
            "adapter_id": "agent-sheet-v1", "binding_id": "binding-1",
            "scope_sha256": "a" * 64, "outcome": "unknown",
            "readback": None, "guard_evidence": {},
            "postcondition_evidence": {}, "evidence": {"reason": "lost-response"},
        }
        unresolved = confirm_action(
            planned.canonical_tasks, authorized, result,
            register_schema=self.schemas["canonical-tasks.schema.json"],
            provider_state_schema=self.schemas["provider-state.schema.json"],
            action_schema=self.schemas["task-adapter-action.schema.json"],
            result_schema=self.schemas["task-adapter-result.schema.json"],
        )
        self.assertEqual([], unresolved.provider_state["bindings"])
        self.assertIsNone(unresolved.provider_state["cursor"])
        self.assertEqual("unknown", unresolved.remaining_actions[0]["outcome"])


if __name__ == "__main__":
    unittest.main()
