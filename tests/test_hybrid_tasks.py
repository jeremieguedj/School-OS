from __future__ import annotations

import json
import unittest
from pathlib import Path

from school_os.agent_tasks import (
    initialize_provider_state, normalized_observation, plan_task_sync,
)
from school_os.connected_storage import BundleTransactionStore
from school_os.contracts import canonical_json_bytes, sha256_bytes
from school_os.hybrid_tasks import (
    HybridTaskError, abort_hybrid_task_switch, activate_hybrid_task_switch,
    adapter_configuration_path, authorize_hybrid_task_action,
    begin_hybrid_task_switch, confirm_hybrid_task_action,
    plan_hybrid_task_sync, provider_state_path,
)
from tests.test_bundles import HybridInstallTests, HybridStorage


ROOT = Path(__file__).resolve().parents[1]


class HybridTaskSwitchTests(HybridInstallTests):
    def setUp(self) -> None:
        self.schemas = {
            name: json.loads((ROOT / "schemas" / name).read_text())
            for name in (
                "task.schema.json", "canonical-tasks.schema.json",
                "provider-state.schema.json", "task-adapter-snapshot.schema.json",
                "task-adapter-action.schema.json", "task-adapter-result.schema.json",
            )
        }

    def task(self) -> dict:
        return {
            "task_id": "task-1", "origin": "source", "action": "Return form",
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

    def observed(self, provider_object_id: str, **changes) -> dict:
        value = {
            "provider_object_id": provider_object_id,
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

    def snapshot(self, provider: str, binding: str, tasks=(), *, capture: str) -> dict:
        return {
            "schema_version": 1, "contract_version": "agent-task-v1",
            "request_id": "request-" + capture, "provider_id": provider,
            "adapter_id": "agent-" + provider, "binding_id": binding,
            "scope_sha256": sha256_bytes(provider.encode()), "capture_id": capture,
            "captured_at": "2026-09-10T10:00:00-07:00", "complete": True,
            "collections": [{
                "name": "tasks", "complete": True, "next_page_token": None,
                "item_count": len(tasks),
            }],
            "tasks": list(tasks), "unbound_candidates": [],
            "proposed_cursor": "cursor-" + capture,
            "evidence": {"private_receipt_sha256": "b" * 64},
        }

    def initial(self):
        storage = HybridStorage()
        transaction = BundleTransactionStore.from_recovery(self.install(storage))
        register = {"schema_version": 1, "tasks": [self.task()]}
        sheet_binding = "sheet-binding"
        sheet_state = initialize_provider_state(
            provider_id="sheet", adapter_id="agent-sheet",
            binding_id=sheet_binding, scope_sha256=sha256_bytes(b"sheet"),
        )
        sheet_snapshot = self.snapshot(
            "sheet", sheet_binding, [self.observed("sheet-row-1")], capture="sheet-1",
        )
        planned = plan_task_sync(
            register, sheet_state, sheet_snapshot,
            task_schema=self.schemas["task.schema.json"],
            register_schema=self.schemas["canonical-tasks.schema.json"],
            provider_state_schema=self.schemas["provider-state.schema.json"],
            snapshot_schema=self.schemas["task-adapter-snapshot.schema.json"],
            action_schema=self.schemas["task-adapter-action.schema.json"],
        )
        self.assertEqual((), planned.actions)
        planned.canonical_tasks["tasks"][0]["provider_bindings"] = [{
            "provider_id": "sheet", "provider_object_id": "sheet-row-1",
        }]
        binding = {
            "adapter_configuration_path": adapter_configuration_path(sheet_binding),
            "adapter_configuration_sha256": sha256_bytes(b"{}\n"),
            "adapter_contract_version": "agent-task-v1", "adapter_id": "agent-sheet",
            "binding_id": sheet_binding, "provider_id": "sheet",
            "provider_state_path": provider_state_path(sheet_binding),
            "scope_sha256": sha256_bytes(b"sheet"), "status": "active",
        }
        selector = {
            "schema_version": 2, "selected_provider": "google_sheets",
            "status": "bound", "bindings": {"google_sheets": binding},
            "switch": None,
        }
        transaction = (
            transaction
            .stage("data/canonical-tasks.json", canonical_json_bytes(planned.canonical_tasks), role="canonical_tasks", media_type="application/json", schema_id="canonical-tasks.schema.json")
            .stage(binding["provider_state_path"], canonical_json_bytes(planned.provider_state), role="task_sync_state", media_type="application/json", schema_id="provider-state.schema.json")
            .stage(binding["adapter_configuration_path"], b"{}\n", role="task_adapter_configuration", media_type="application/json")
            .stage("state/task-provider-selector.json", canonical_json_bytes(selector), role="task_provider_selector", media_type="application/json", schema_id="task-provider-selector.schema.json")
            .publish(storage, self.serialization)
        )
        return storage, transaction, planned.provider_state, sheet_snapshot

    def result(self, action: dict, readback: dict) -> dict:
        return {
            "schema_version": 1, "contract_version": "agent-task-v1",
            "effect_id": action["effect_id"], "provider_id": action["provider_id"],
            "adapter_id": action["adapter_id"], "binding_id": action["binding_id"],
            "scope_sha256": action["scope_sha256"], "outcome": "confirmed",
            "readback": readback, "guard_evidence": {"matched": True},
            "postcondition_evidence": {"matched": True},
            "evidence": {"private_receipt_sha256": "c" * 64},
        }

    def test_guided_switch_stages_before_activation_and_reuses_dormant_mapping(self) -> None:
        storage, transaction, sheet_state, sheet_snapshot = self.initial()
        target = {
            "provider_key": "todoist", "provider_id": "todoist",
            "adapter_id": "agent-todoist", "binding_id": "todoist-binding",
            "scope_sha256": sha256_bytes(b"todoist"),
        }
        todoist_empty = self.snapshot("todoist", "todoist-binding", capture="todoist-0")
        begun = begin_hybrid_task_switch(
            storage=storage, transaction=transaction, installed_root=ROOT,
            target=target, target_snapshot=todoist_empty,
            adapter_configuration=b"{}\n",
            old_snapshot_sha256=sheet_state["last_snapshot_sha256"],
            serialization=self.serialization,
        )
        selector = json.loads(begun.transaction.read("state/task-provider-selector.json").data)
        self.assertEqual("google_sheets", selector["selected_provider"])
        self.assertEqual("active", selector["bindings"]["google_sheets"]["status"])
        self.assertEqual("staging", selector["bindings"]["todoist"]["status"])
        self.assertEqual(["create_task"], [item["kind"] for item in begun.provider_state["pending_actions"]])

        authorized = authorize_hybrid_task_action(
            storage=storage, transaction=begun.transaction, installed_root=ROOT,
            serialization=self.serialization, provider_key="todoist",
        )
        action = authorized.action
        confirmed = confirm_hybrid_task_action(
            storage=storage, transaction=authorized.transaction, installed_root=ROOT,
            serialization=self.serialization, provider_key="todoist",
            result=self.result(action, self.observed("todoist-task-1")),
        )
        final_todoist = self.snapshot(
            "todoist", "todoist-binding", [self.observed("todoist-task-1")],
            capture="todoist-1",
        )
        activated = activate_hybrid_task_switch(
            storage=storage, transaction=confirmed.transaction,
            installed_root=ROOT, target_snapshot=final_todoist,
            serialization=self.serialization,
        )
        selector = json.loads(activated.transaction.read("state/task-provider-selector.json").data)
        self.assertEqual("todoist", selector["selected_provider"])
        self.assertEqual("dormant", selector["bindings"]["google_sheets"]["status"])
        self.assertEqual("active", selector["bindings"]["todoist"]["status"])

        pulled = plan_hybrid_task_sync(
            storage=storage, transaction=activated.transaction,
            installed_root=ROOT, snapshot=final_todoist,
            serialization=self.serialization,
        )
        target_state = pulled.provider_state
        back = {
            "provider_key": "google_sheets", "provider_id": "sheet",
            "adapter_id": "agent-sheet", "binding_id": "sheet-binding",
            "scope_sha256": sha256_bytes(b"sheet"),
        }
        switching_back = begin_hybrid_task_switch(
            storage=storage, transaction=pulled.transaction, installed_root=ROOT,
            target=back, target_snapshot=sheet_snapshot,
            adapter_configuration=None,
            old_snapshot_sha256=target_state["last_snapshot_sha256"],
            serialization=self.serialization,
        )
        returned = activate_hybrid_task_switch(
            storage=storage, transaction=switching_back.transaction,
            installed_root=ROOT, target_snapshot=sheet_snapshot,
            serialization=self.serialization,
        )
        selector = json.loads(returned.transaction.read("state/task-provider-selector.json").data)
        self.assertEqual("google_sheets", selector["selected_provider"])
        self.assertEqual(provider_state_path("sheet-binding"), selector["bindings"]["google_sheets"]["provider_state_path"])
        register = json.loads(returned.transaction.read("data/canonical-tasks.json").data)
        self.assertEqual(2, len(register["tasks"][0]["provider_bindings"]))

    def test_nonempty_new_target_and_dormant_parent_edits_block_without_selector_change(self) -> None:
        storage, transaction, sheet_state, _ = self.initial()
        target = {
            "provider_key": "todoist", "provider_id": "todoist",
            "adapter_id": "agent-todoist", "binding_id": "todoist-binding",
            "scope_sha256": sha256_bytes(b"todoist"),
        }
        nonempty = self.snapshot(
            "todoist", "todoist-binding", [self.observed("unexpected")],
            capture="todoist-bad",
        )
        before = transaction.working.recovery["current"]["generation"]
        with self.assertRaisesRegex(HybridTaskError, "not empty"):
            begin_hybrid_task_switch(
                storage=storage, transaction=transaction, installed_root=ROOT,
                target=target, target_snapshot=nonempty,
                adapter_configuration=b"{}\n",
                old_snapshot_sha256=sheet_state["last_snapshot_sha256"],
                serialization=self.serialization,
            )
        self.assertEqual(before, transaction.working.recovery["current"]["generation"])

    def test_abort_discards_only_undispatched_target_actions_and_dormant_cannot_dispatch(self) -> None:
        storage, transaction, sheet_state, _ = self.initial()
        target = {
            "provider_key": "todoist", "provider_id": "todoist",
            "adapter_id": "agent-todoist", "binding_id": "todoist-binding",
            "scope_sha256": sha256_bytes(b"todoist"),
        }
        empty = self.snapshot("todoist", "todoist-binding", capture="todoist-abort")
        begun = begin_hybrid_task_switch(
            storage=storage, transaction=transaction, installed_root=ROOT,
            target=target, target_snapshot=empty, adapter_configuration=b"{}\n",
            old_snapshot_sha256=sheet_state["last_snapshot_sha256"],
            serialization=self.serialization,
        )
        aborted = abort_hybrid_task_switch(
            storage=storage, transaction=begun.transaction, installed_root=ROOT,
            serialization=self.serialization,
        )
        selector = json.loads(aborted.read("state/task-provider-selector.json").data)
        target_state = json.loads(aborted.read(provider_state_path("todoist-binding")).data)
        self.assertEqual("google_sheets", selector["selected_provider"])
        self.assertEqual("dormant", selector["bindings"]["todoist"]["status"])
        self.assertEqual([], target_state["pending_actions"])
        with self.assertRaisesRegex(HybridTaskError, "selected or staged"):
            authorize_hybrid_task_action(
                storage=storage, transaction=aborted, installed_root=ROOT,
                serialization=self.serialization, provider_key="todoist",
            )

        restarted = begin_hybrid_task_switch(
            storage=storage, transaction=aborted, installed_root=ROOT,
            target=target, target_snapshot=empty, adapter_configuration=None,
            old_snapshot_sha256=sheet_state["last_snapshot_sha256"],
            serialization=self.serialization,
        )
        authorized = authorize_hybrid_task_action(
            storage=storage, transaction=restarted.transaction, installed_root=ROOT,
            serialization=self.serialization, provider_key="todoist",
        )
        with self.assertRaisesRegex(HybridTaskError, "may have reached"):
            abort_hybrid_task_switch(
                storage=storage, transaction=authorized.transaction,
                installed_root=ROOT, serialization=self.serialization,
            )


if __name__ == "__main__":
    unittest.main()
