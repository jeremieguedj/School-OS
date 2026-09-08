from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from school_os.sheets import (  # noqa: E402
    GoogleSheetsTaskAdapter,
    MANAGED_BY_VALUE,
    NativeSheetMutation,
    SheetColumns,
    SheetRow,
    SheetScope,
    normalized_snapshot,
)
from school_os.tasks import TaskError, reconcile_provider_tasks  # noqa: E402


class FixtureRows:
    """Synthetic native bridge; production code receives this surface by injection."""

    def __init__(
        self, rows: list[dict] | None = None, *, complete: bool = True,
        retarget_after_guard: bool = False,
    ) -> None:
        self.scope = SheetScope("synthetic-sheet")
        self.rows = list(rows or [])
        self.complete = complete
        self.mutations: list[NativeSheetMutation] = []
        self.reads: list[str] = []
        self.complete_reads = 0
        self.retarget_after_guard = retarget_after_guard

    def read_complete(self, scope: SheetScope):
        self.assert_scope(scope)
        self.complete_reads += 1
        return normalized_snapshot(scope, copy.deepcopy(self.rows), complete=self.complete)

    def apply_mutation(self, mutation: NativeSheetMutation) -> str:
        self.assert_scope(mutation.scope)
        self.mutations.append(mutation)
        if mutation.kind == "append":
            row_id = f"row-{len(self.rows) + 1}"
            self.rows.append({"row_id": row_id, "cells": dict(mutation.values)})
            return row_id
        if mutation.kind == "patch":
            for row in self.rows:
                if row["row_id"] == mutation.row_id:
                    self._assert_guard(row, mutation)
                    if self.retarget_after_guard:
                        row = next(item for item in self.rows if item["row_id"] != mutation.row_id)
                    row["cells"].update(mutation.values)
                    return row["row_id"]
            raise KeyError(mutation.row_id)
        if mutation.kind == "claim":
            for row in self.rows:
                if row["row_id"] == mutation.row_id:
                    self._assert_guard(row, mutation)
                    row["cells"].update(mutation.values)
                    return row["row_id"]
            raise KeyError(mutation.row_id)
        raise AssertionError(mutation.kind)

    @staticmethod
    def _assert_guard(row: dict, mutation: NativeSheetMutation) -> None:
        for column, expected in mutation.guard_cells(SheetColumns()).items():
            if row["cells"].get(column) != expected:
                raise TaskError("synthetic native Sheet row guard did not match")

    def read_exact(self, scope: SheetScope, row_id: str):
        self.assert_scope(scope)
        self.reads.append(row_id)
        for row in self.rows:
            if row["row_id"] == row_id:
                return SheetRow(row_id=row_id, cells=dict(row["cells"]))
        return None

    def assert_scope(self, scope: SheetScope) -> None:
        if scope != self.scope:
            raise AssertionError("wrong synthetic scope")


class FixtureComments:
    def __init__(self) -> None:
        self.items: list[dict[str, str]] = []

    def list_comments(self, scope: SheetScope, row_id: str, canonical_task_id: str, provider_object_id: str, effect_id: str):
        return [dict(item) for item in self.items if item["row_id"] == row_id and item["canonical_task_id"] == canonical_task_id and item["provider_object_id"] == provider_object_id and item["effect_id"] == effect_id]

    def write_comment(self, scope: SheetScope, row_id: str, canonical_task_id: str, provider_object_id: str, effect_id: str, text: str):
        item = {"row_id": row_id, "canonical_task_id": canonical_task_id, "provider_object_id": provider_object_id, "effect_id": effect_id, "text": text}
        self.items.append(item)
        return dict(item)


class GoogleSheetsTaskAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.task_schema = json.loads((ROOT / "schemas" / "task.schema.json").read_text())
        cls.register_schema = json.loads((ROOT / "schemas" / "canonical-tasks.schema.json").read_text())
        cls.state_schema = json.loads((ROOT / "schemas" / "provider-state.schema.json").read_text())

    def candidate(self, *, task_id: str = "task-1", title: str = "Return form") -> dict[str, str]:
        return {
            "canonical_task_id": task_id,
            "title": title,
            "description": "school",
            "group": "household",
            "workflow_state": "needs_action",
            "source_link": "record-1#fact-1",
        }

    def managed_row(self, *, task_id: str = "task-1", row_id: str = "row-1") -> dict:
        candidate = self.candidate(task_id=task_id)
        return {
            "row_id": row_id,
            "cells": {
                "Managed By": MANAGED_BY_VALUE,
                "Canonical Task ID": candidate["canonical_task_id"],
                "Task Origin": "source",
                "Action": candidate["title"],
                "Task Context": candidate["description"],
                "Source Link": candidate["source_link"],
                "Group": candidate["group"],
                "Workflow State": candidate["workflow_state"],
                "Status": "open",
                "Source Due": "2026-09-12",
                "Parent Planned Due": "2026-09-11",
                "Parent Progress": "parent note",
                "Completion Comment": "",
                "Unrelated": "keep",
            },
        }

    def adapter_factory(self, rows: list[dict] | None = None, *, complete: bool = True, comments=None, retarget_after_guard=False):
        port = FixtureRows(rows, complete=complete, retarget_after_guard=retarget_after_guard)
        return GoogleSheetsTaskAdapter(port.scope, port, comments=comments), port

    def adapter(self, rows: list[dict] | None = None, *, complete: bool = True, comments=None, retarget_after_guard=False):
        factory, port = self.adapter_factory(rows, complete=complete, comments=comments, retarget_after_guard=retarget_after_guard)
        return factory.begin_sync(), port

    def task(self, *, task_id: str = "task-1", action: str = "Return form") -> dict:
        return {
            "task_id": task_id, "origin": "source", "action": action, "task_context": "school",
            "entity_scope": "household", "workflow_state": "needs_action", "owner": None,
            "source_opened_date": "2026-09-07", "last_supporting_source_date": "2026-09-07",
            "source_due": "2026-09-12", "parent_planned_due": None, "source_link": "record-1#fact-1",
            "source_facts": ["fact-1"], "latest_progress": None, "provider_bindings": [],
            "lifecycle_history": [], "projection_state": {}, "revision": 1, "last_modified_evidence": {},
        }

    def state(self) -> dict:
        return {
            "provider_id": "synthetic-sheets", "adapter_id": "google-sheets", "provider_revision": None,
            "bindings": [], "cursor": None, "cursor_evidence": {}, "verified_readback": {},
        }

    def test_create_uses_string_cells_and_exact_readback(self) -> None:
        adapter, port = self.adapter()
        candidate = self.candidate(title="=SUM(1,1) literal task text")

        created = adapter.create_task(candidate)

        self.assertEqual(candidate["title"], created["title"])
        self.assertEqual(1, len(port.mutations))
        mutation = port.mutations[0]
        self.assertEqual("append", mutation.kind)
        self.assertEqual({"userEnteredValue": {"stringValue": candidate["title"]}}, mutation.native_cells()["Action"])
        self.assertEqual(["row-1"], port.reads)
        self.assertEqual(MANAGED_BY_VALUE, port.rows[0]["cells"]["Managed By"])

    def test_minimum_patch_preserves_parent_and_provider_owned_cells(self) -> None:
        adapter, port = self.adapter([self.managed_row()])

        updated = adapter.apply_patch(
            "sheets:canonical:task-1",
            {**self.candidate(), "workflow_state": "needs_review"},
        )

        self.assertEqual("needs_review", updated["workflow_state"])
        self.assertEqual(1, len(port.mutations))
        mutation = port.mutations[0]
        self.assertEqual("patch", mutation.kind)
        self.assertEqual({"Workflow State": "needs_review"}, dict(mutation.values))
        cells = port.rows[0]["cells"]
        self.assertEqual("open", cells["Status"])
        self.assertEqual("2026-09-11", cells["Parent Planned Due"])
        self.assertEqual("parent note", cells["Parent Progress"])
        self.assertEqual("keep", cells["Unrelated"])

    def test_unbound_parent_rows_are_ignored_without_title_matching(self) -> None:
        parent_row = {
            "row_id": "row-1",
            "cells": {"Action": "Return form", "Group": "household", "Status": "completed", "Workflow State": "parent choice"},
        }
        adapter, port = self.adapter([parent_row])

        self.assertEqual([], adapter.list_tasks())
        created = adapter.create_task(self.candidate())

        self.assertEqual("task-1", created["canonical_task_id"])
        self.assertEqual(2, len(port.rows))
        self.assertEqual("completed", port.rows[0]["cells"]["Status"])

    def test_corrupt_or_ambiguous_managed_rows_block_before_mutation(self) -> None:
        corrupt = self.managed_row()
        corrupt["cells"]["Canonical Task ID"] = ""
        adapter, port = self.adapter([corrupt])
        with self.assertRaisesRegex(TaskError, "missing canonical task ID"):
            adapter.create_task(self.candidate())
        self.assertEqual([], port.mutations)

        duplicate = [self.managed_row(), self.managed_row(row_id="row-2")]
        adapter, port = self.adapter(duplicate)
        with self.assertRaisesRegex(TaskError, "multiple Sheet rows"):
            adapter.list_tasks()
        self.assertEqual([], port.mutations)

    def test_incomplete_snapshot_and_missing_system_marker_block(self) -> None:
        adapter, _ = self.adapter([self.managed_row()], complete=False)
        with self.assertRaisesRegex(TaskError, "snapshot is incomplete"):
            adapter.list_tasks()

        row = self.managed_row()
        row["cells"].pop("Managed By")
        adapter, _ = self.adapter([row])
        with self.assertRaisesRegex(TaskError, "without the system marker"):
            adapter.list_tasks()

    def test_unexpected_system_field_drift_blocks_when_a_verified_baseline_is_supplied(self) -> None:
        row = self.managed_row()
        row["cells"]["Source Link"] = "unexpected-link"
        adapter, port = self.adapter([row])

        with self.assertRaisesRegex(TaskError, "unexpected system-managed"):
            adapter.verify_expected_system_fields({"task-1": self.candidate()})
        self.assertEqual([], port.mutations)

    def test_parent_observations_keep_completion_comment_and_dates_separate(self) -> None:
        row = self.managed_row()
        row["cells"].update({"Status": "completed", "Completion Comment": "Signed and returned", "Parent Planned Due": "2026-09-15"})
        adapter, _ = self.adapter([row])

        self.assertEqual(
            [{
                "canonical_task_id": "task-1", "status": "completed", "parent_planned_due": "2026-09-15",
                "parent_progress": "parent note", "completion_comment": "Signed and returned",
            }],
            adapter.parent_observations(),
        )
        self.assertEqual("2026-09-12", adapter.list_tasks()[0]["source_due"])

    def test_parent_state_supports_clearable_progress_and_completion_fields(self) -> None:
        row = self.managed_row()
        row["cells"].update({"Status": "completed", "Completion Comment": "Signed", "Parent Progress": "done"})
        adapter, port = self.adapter([row])

        updated = adapter.apply_parent_state(
            "sheets:canonical:task-1",
            status="needs_review",
            parent_progress="",
            completion_comment="",
        )

        self.assertEqual("needs_review", updated["status"])
        self.assertEqual("", updated["parent_progress"])
        self.assertEqual("", updated["completion_comment"])
        self.assertEqual(
            {"Status": "needs_review", "Parent Progress": "", "Completion Comment": ""},
            dict(port.mutations[0].values),
        )
        self.assertEqual("", adapter.parent_observations()[0]["completion_comment"])

    def test_current_core_reconciliation_replays_without_duplicate_sheet_rows(self) -> None:
        factory, port = self.adapter_factory()
        register = {"schema_version": 1, "tasks": [self.task()]}

        first = reconcile_provider_tasks(
            factory.begin_sync(), register, self.state(), task_schema=self.task_schema,
            register_schema=self.register_schema, provider_state_schema=self.state_schema,
        )
        second = reconcile_provider_tasks(
            factory.begin_sync(), register, first.provider_state, task_schema=self.task_schema,
            register_schema=self.register_schema, provider_state_schema=self.state_schema,
        )
        third = reconcile_provider_tasks(
            factory.begin_sync(), second.tasks, second.provider_state, task_schema=self.task_schema,
            register_schema=self.register_schema, provider_state_schema=self.state_schema,
        )

        self.assertEqual(1, len(port.rows))
        self.assertEqual("create_intent", first.effects[0]["kind"])
        self.assertEqual("create", second.effects[0]["kind"])
        self.assertEqual("adopt", third.effects[0]["kind"])
        self.assertEqual("sheets:canonical:task-1", third.provider_state["bindings"][0]["provider_object_id"])
        self.assertEqual(3, port.complete_reads)

    def test_one_sync_uses_one_complete_snapshot_for_multiple_tasks(self) -> None:
        factory, port = self.adapter_factory()
        register = {
            "schema_version": 1,
            "tasks": [
                self.task(task_id="task-1", action="Return form"),
                self.task(task_id="task-2", action="Buy notebook"),
            ],
        }

        first = reconcile_provider_tasks(
            factory.begin_sync(), register, self.state(), task_schema=self.task_schema,
            register_schema=self.register_schema, provider_state_schema=self.state_schema,
        )

        self.assertEqual(["create_intent", "create_intent"], [effect["kind"] for effect in first.effects])
        self.assertEqual(1, port.complete_reads)
        self.assertEqual(0, len(port.rows))

        second = reconcile_provider_tasks(
            factory.begin_sync(), register, first.provider_state, task_schema=self.task_schema,
            register_schema=self.register_schema, provider_state_schema=self.state_schema,
        )
        self.assertEqual(["create", "create"], [effect["kind"] for effect in second.effects])
        self.assertEqual(2, port.complete_reads)
        self.assertEqual(2, len(port.rows))

    def test_patch_guard_blocks_reordered_row_before_native_write(self) -> None:
        row = self.managed_row()
        adapter, port = self.adapter([row])
        adapter.list_tasks()  # establishes the per-sync canonical-ID locator
        row["cells"]["Canonical Task ID"] = "task-neighbor"

        with self.assertRaisesRegex(TaskError, "row guard"):
            adapter.apply_patch(
                "sheets:canonical:task-1",
                {**self.candidate(), "workflow_state": "needs_review"},
            )
        self.assertEqual(1, len(port.mutations))  # candidate was generated, native guard blocked it
        self.assertEqual("needs_action", row["cells"]["Workflow State"])
        adapter.reload_after_observed_drift()
        self.assertEqual(2, port.complete_reads)

    def test_exact_readback_blocks_retarget_after_native_guard(self) -> None:
        rows = [self.managed_row(), self.managed_row(task_id="task-2", row_id="row-2")]
        adapter, port = self.adapter(rows, retarget_after_guard=True)

        with self.assertRaisesRegex(TaskError, "does not match managed projection"):
            adapter.apply_patch(
                "sheets:canonical:task-1",
                {**self.candidate(), "workflow_state": "needs_review"},
            )
        self.assertEqual("needs_action", rows[0]["cells"]["Workflow State"])
        self.assertEqual("needs_review", rows[1]["cells"]["Workflow State"])

    def test_parent_candidate_claim_uses_exact_unbound_packet(self) -> None:
        parent_row = {
            "row_id": "row-1",
            "cells": {
                "Action": "Call dentist", "Group": "household", "Status": "open",
                "Parent Planned Due": "2026-09-20", "Parent Progress": "after lunch",
                "Completion Comment": "", "Unrelated": "keep",
            },
        }
        adapter, port = self.adapter([parent_row])

        [candidate] = adapter.unbound_parent_candidates()
        claimed = adapter.claim_parent_candidate(
            candidate, canonical_task_id="task-parent-1", workflow_state="needs_action"
        )

        self.assertEqual("parent", claimed["origin"])
        self.assertEqual("", claimed["source_link"])
        self.assertEqual("", claimed["description"])
        self.assertEqual("task-parent-1", port.rows[0]["cells"]["Canonical Task ID"])
        self.assertEqual("keep", port.rows[0]["cells"]["Unrelated"])
        self.assertEqual(None, port.mutations[0].expected_canonical_task_id)
        self.assertEqual("Call dentist", port.mutations[0].guard_cells(SheetColumns())["Action"])

    def test_core_journals_then_claims_one_parent_row_without_title_matching(self) -> None:
        rows = [
            {"row_id": "row-a", "cells": {"Action": "Call school", "Group": "household", "Status": "open"}},
            {"row_id": "row-b", "cells": {"Action": "Call school", "Group": "household", "Status": "open"}},
        ]
        factory, port = self.adapter_factory(rows)
        first = reconcile_provider_tasks(
            factory.begin_sync(), {"schema_version": 1, "tasks": []}, self.state(),
            task_schema=self.task_schema, register_schema=self.register_schema,
            provider_state_schema=self.state_schema,
        )
        self.assertEqual(0, len(port.mutations))
        self.assertEqual(2, len(first.provider_state["claim_intents"]))
        second = reconcile_provider_tasks(
            factory.begin_sync(), first.tasks, first.provider_state,
            task_schema=self.task_schema, register_schema=self.register_schema,
            provider_state_schema=self.state_schema,
        )
        self.assertEqual(2, len(port.mutations))
        self.assertEqual(2, len(second.provider_state["bindings"]))
        replay = reconcile_provider_tasks(
            factory.begin_sync(), second.tasks, second.provider_state,
            task_schema=self.task_schema, register_schema=self.register_schema,
            provider_state_schema=self.state_schema,
        )
        self.assertEqual(2, len(port.rows))
        self.assertEqual(2, len(replay.provider_state["bindings"]))

    def test_comment_bridge_requires_exact_effect_readback(self) -> None:
        comments = FixtureComments()
        adapter, _ = self.adapter([self.managed_row()], comments=comments)

        written = adapter.write_comment("sheets:canonical:task-1", "effect-1", "Parent-visible system reminder")

        self.assertEqual("effect-1", written["effect_id"])
        self.assertEqual([written], adapter.find_comments("sheets:canonical:task-1", "effect-1"))

    def test_targeted_cell_guards_block_cached_parent_and_managed_drift(self) -> None:
        adapter, port = self.adapter([self.managed_row()])
        adapter.list_tasks()
        port.rows[0]["cells"]["Parent Progress"] = "concurrent edit"
        with self.assertRaisesRegex(TaskError, "row guard"):
            adapter.apply_parent_state("sheets:canonical:task-1", parent_progress="stale overwrite")
        self.assertEqual("concurrent edit", port.rows[0]["cells"]["Parent Progress"])
        adapter, port = self.adapter([self.managed_row()])
        adapter.list_tasks()
        port.rows[0]["cells"]["Task Context"] = "concurrent managed drift"
        with self.assertRaisesRegex(TaskError, "row guard"):
            adapter.apply_patch("sheets:canonical:task-1", {"description": "source update"})
        self.assertEqual("concurrent managed drift", port.rows[0]["cells"]["Task Context"])

    def test_full_managed_preflight_includes_origin_due_and_system_workflow(self) -> None:
        expected = {**self.candidate(), "origin": "source", "source_due": "2026-09-12"}
        for column, drift in (("Task Origin", "parent"), ("Source Due", "unexpected"), ("Workflow State", "unexpected")):
            row = self.managed_row()
            row["cells"][column] = drift
            adapter, port = self.adapter([row])
            with self.assertRaisesRegex(TaskError, "unexpected system-managed"):
                adapter.verify_expected_system_fields({"task-1": expected})
            self.assertEqual([], port.mutations)

    def test_claim_checkpoint_recovers_either_missing_half_without_duplicate(self) -> None:
        parent_row = {"row_id": "row-1", "cells": {"Action": "Parent task", "Group": "household", "Status": "open"}}
        factory, port = self.adapter_factory([copy.deepcopy(parent_row)])
        first = reconcile_provider_tasks(factory.begin_sync(), {"schema_version": 1, "tasks": []}, self.state(), task_schema=self.task_schema, register_schema=self.register_schema, provider_state_schema=self.state_schema)
        intent_only = reconcile_provider_tasks(factory.begin_sync(), {"schema_version": 1, "tasks": []}, first.provider_state, task_schema=self.task_schema, register_schema=self.register_schema, provider_state_schema=self.state_schema)
        self.assertEqual(1, len(intent_only.tasks["tasks"]));self.assertEqual(1, len(port.rows))

        factory, port = self.adapter_factory([copy.deepcopy(parent_row)])
        first = reconcile_provider_tasks(factory.begin_sync(), {"schema_version": 1, "tasks": []}, self.state(), task_schema=self.task_schema, register_schema=self.register_schema, provider_state_schema=self.state_schema)
        lost_intent = copy.deepcopy(first.provider_state);lost_intent["claim_intents"] = []
        repaired = reconcile_provider_tasks(factory.begin_sync(), first.tasks, lost_intent, task_schema=self.task_schema, register_schema=self.register_schema, provider_state_schema=self.state_schema)
        self.assertEqual(1, len(repaired.provider_state["claim_intents"]));self.assertEqual(1, len(port.rows))
        claimed = reconcile_provider_tasks(factory.begin_sync(), repaired.tasks, repaired.provider_state, task_schema=self.task_schema, register_schema=self.register_schema, provider_state_schema=self.state_schema)
        self.assertEqual(1, len(port.rows));self.assertEqual(1, len(claimed.provider_state["bindings"]))

        factory, port = self.adapter_factory([copy.deepcopy(parent_row)])
        first = reconcile_provider_tasks(factory.begin_sync(), {"schema_version": 1, "tasks": []}, self.state(), task_schema=self.task_schema, register_schema=self.register_schema, provider_state_schema=self.state_schema)
        port.rows[0]["row_id"] = "row-moved"
        moved = reconcile_provider_tasks(factory.begin_sync(), first.tasks, first.provider_state, task_schema=self.task_schema, register_schema=self.register_schema, provider_state_schema=self.state_schema)
        self.assertEqual(1, len(port.rows));self.assertEqual(1, len(moved.provider_state["bindings"]))

    def test_unknown_managed_canonical_id_is_rejected(self) -> None:
        adapter, _ = self.adapter([self.managed_row(task_id="task-unknown")])
        with self.assertRaisesRegex(TaskError, "unknown managed canonical"):
            reconcile_provider_tasks(adapter, {"schema_version": 1, "tasks": []}, self.state(), task_schema=self.task_schema, register_schema=self.register_schema, provider_state_schema=self.state_schema)

    def test_comments_re_resolve_canonical_identity_on_each_operation(self) -> None:
        comments = FixtureComments();adapter, port = self.adapter([self.managed_row()], comments=comments)
        adapter.list_tasks();before = port.complete_reads
        adapter.write_comment("sheets:canonical:task-1", "effect-1", "Exact generic reminder")
        self.assertGreaterEqual(port.complete_reads, before + 2)


if __name__ == "__main__":
    unittest.main()
