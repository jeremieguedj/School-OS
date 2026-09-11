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

    def result(self, action: dict, readback: dict, *, outcome: str = "confirmed") -> dict:
        return {
            "schema_version": 1, "contract_version": "agent-task-v1",
            "effect_id": action["effect_id"], "provider_id": "projection-1",
            "adapter_id": "agent-sheet-v1", "binding_id": "binding-1",
            "scope_sha256": "a" * 64, "outcome": outcome,
            "readback": readback if outcome == "confirmed" else None,
            "guard_evidence": {"matched": outcome == "confirmed"},
            "postcondition_evidence": {"matched": outcome == "confirmed"},
            "evidence": {"private_receipt_sha256": "c" * 64},
        }

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

    def test_parent_completion_and_reopen_are_imported_without_overwrite(self) -> None:
        initial = self.plan(
            {"schema_version": 1, "tasks": [self.task()]}, self.state(),
            self.snapshot([self.observed()]),
        )
        completed = self.observed(
            resolution="completed", completion_comment="Done after calling",
            provider_revision="revision-2",
        )
        accepted = self.plan(
            initial.canonical_tasks, initial.provider_state,
            self.snapshot([completed], request_id="read-2"),
        )
        task = accepted.canonical_tasks["tasks"][0]
        self.assertEqual("completed", task["resolution"])
        self.assertEqual("parent_completion", task["lifecycle_history"][-1]["kind"])
        self.assertEqual((), accepted.actions)
        self.assertEqual("Done after calling", accepted.provider_state["bindings"][0]["last_parent_snapshot"]["completion_comment"]["value"])

        reopened = self.observed(
            resolution="unresolved", completion_comment="Done after calling",
            provider_revision="revision-3",
        )
        accepted = self.plan(
            accepted.canonical_tasks, accepted.provider_state,
            self.snapshot([reopened], request_id="read-3"),
        )
        task = accepted.canonical_tasks["tasks"][0]
        self.assertEqual("unresolved", task["resolution"])
        self.assertEqual("parent_reopen", task["lifecycle_history"][-1]["kind"])
        self.assertEqual((), accepted.actions)

    def test_missing_completion_comment_plans_comment_then_reopen_and_recovers(self) -> None:
        initial = self.plan(
            {"schema_version": 1, "tasks": [self.task()]}, self.state(),
            self.snapshot([self.observed()]),
        )
        completed = self.observed(
            resolution="completed", completion_comment=None,
            provider_revision="revision-2",
        )
        planned = self.plan(
            initial.canonical_tasks, initial.provider_state,
            self.snapshot([completed], request_id="read-2"),
        )
        self.assertEqual(
            ["write_system_comment", "set_task_resolution"],
            [item["kind"] for item in planned.actions],
        )
        authorized, comment = authorize_next_action(
            planned.provider_state,
            action_schema=self.schemas["task-adapter-action.schema.json"],
            provider_state_schema=self.schemas["provider-state.schema.json"],
        )
        unknown = confirm_action(
            planned.canonical_tasks, authorized,
            self.result(comment, {}, outcome="unknown"),
            register_schema=self.schemas["canonical-tasks.schema.json"],
            provider_state_schema=self.schemas["provider-state.schema.json"],
            action_schema=self.schemas["task-adapter-action.schema.json"],
            result_schema=self.schemas["task-adapter-result.schema.json"],
        )
        self.assertEqual("unknown", unknown.remaining_actions[0]["outcome"])
        comment_readback = self.observed(
            resolution="completed", completion_comment=None,
            provider_revision="revision-3",
            comment_evidence=[{
                "comment_id": "comment-1", "kind": "system",
                "text": comment["postconditions"]["system_comment"]["text"],
                "effect_id": comment["effect_id"],
            }],
        )
        commented = confirm_action(
            planned.canonical_tasks, unknown.provider_state,
            self.result(comment, comment_readback),
            register_schema=self.schemas["canonical-tasks.schema.json"],
            provider_state_schema=self.schemas["provider-state.schema.json"],
            action_schema=self.schemas["task-adapter-action.schema.json"],
            result_schema=self.schemas["task-adapter-result.schema.json"],
        )
        self.assertEqual(("set_task_resolution",), tuple(item["kind"] for item in commented.remaining_actions))
        authorized, reopen = authorize_next_action(
            commented.provider_state,
            action_schema=self.schemas["task-adapter-action.schema.json"],
            provider_state_schema=self.schemas["provider-state.schema.json"],
        )
        reopened_readback = self.observed(
            resolution="unresolved", completion_comment=None,
            provider_revision="revision-4",
            comment_evidence=comment_readback["comment_evidence"],
        )
        reopened = confirm_action(
            commented.canonical_tasks, authorized,
            self.result(reopen, reopened_readback),
            register_schema=self.schemas["canonical-tasks.schema.json"],
            provider_state_schema=self.schemas["provider-state.schema.json"],
            action_schema=self.schemas["task-adapter-action.schema.json"],
            result_schema=self.schemas["task-adapter-result.schema.json"],
        )
        self.assertEqual((), reopened.remaining_actions)
        task = reopened.canonical_tasks["tasks"][0]
        self.assertEqual("unresolved", task["resolution"])
        self.assertEqual("reopened_missing_completion_comment", task["lifecycle_history"][-1]["kind"])

    def test_source_resolution_projects_as_dedicated_action_and_completed_missing_task_is_not_created(self) -> None:
        initial = self.plan(
            {"schema_version": 1, "tasks": [self.task()]}, self.state(),
            self.snapshot([self.observed()]),
        )
        completed = json.loads(json.dumps(initial.canonical_tasks))
        completed["tasks"][0]["resolution"] = "completed"
        completed["tasks"][0]["projection_state"]["resolution"] = "completed"
        planned = self.plan(completed, initial.provider_state, self.snapshot([self.observed()]))
        self.assertEqual(["set_task_resolution"], [item["kind"] for item in planned.actions])

        absent_state = self.state()
        absent = self.plan(completed, absent_state, self.snapshot())
        self.assertEqual((), absent.actions)

    def test_parent_candidate_claim_uses_candidate_identity_not_duplicate_title(self) -> None:
        candidates = [
            {
                "candidate_id": identity, "provider_object_id": identity,
                "action": "Same title", "entity_scope": "household",
                "parent_planned_due": None, "latest_progress": None,
                "completion_comment": None, "guard": {"row": identity},
            }
            for identity in ("candidate-a", "candidate-b")
        ]
        planned = self.plan(
            {"schema_version": 1, "tasks": []}, self.state(),
            self.snapshot(candidates=candidates),
        )
        self.assertEqual(2, len(planned.actions))
        self.assertTrue(all(item["kind"] == "claim_task" for item in planned.actions))
        self.assertEqual(
            {"candidate-a", "candidate-b"},
            {item["expected"]["candidate"]["candidate_id"] for item in planned.actions},
        )

    def test_comment_evidence_is_strict_and_system_effect_bound(self) -> None:
        malformed = self.observed()
        malformed["comment_evidence"] = [{"text": "unbound"}]
        malformed["observation_sha256"] = sha256_bytes(
            json.dumps(
                {key: value for key, value in malformed.items() if key != "observation_sha256"},
                sort_keys=True, separators=(",", ":"),
            ).encode()
        )
        with self.assertRaisesRegex(AgentTaskError, "comment evidence"):
            self.plan(
                {"schema_version": 1, "tasks": [self.task()]}, self.state(),
                self.snapshot([malformed]),
            )


if __name__ == "__main__":
    unittest.main()
