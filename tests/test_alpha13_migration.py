from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from school_os.contracts import load_mapping_yaml
from school_os.migrate_alpha13 import MigrationError, migrate_alpha12


class Alpha13MigrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = json.loads((ROOT / "tests" / "synthetic-fixtures" / "alpha13" / "alpha12-migration.json").read_text(encoding="utf-8"))
        cls.task_schema = json.loads((ROOT / "schemas" / "task.schema.json").read_text(encoding="utf-8"))
        cls.register_schema = json.loads((ROOT / "schemas" / "canonical-tasks.schema.json").read_text(encoding="utf-8"))
        cls.instance_schema = json.loads((ROOT / "schemas" / "instance.schema.json").read_text(encoding="utf-8"))
        cls.operation_state_schema = json.loads((ROOT / "schemas" / "operation-state.schema.json").read_text(encoding="utf-8"))

    def migrate(self, fixture: dict | None = None):
        source = self.fixture if fixture is None else fixture
        return migrate_alpha12(
            instance=source["instance"], operation_state=source["operation_state"], file_map=source["file_map"],
            action_items_markdown=source["action_items_markdown"], target_version="0.1.0-alpha.13",
            task_schema=self.task_schema, register_schema=self.register_schema,
            instance_schema=self.instance_schema, operation_state_schema=self.operation_state_schema,
        )

    def test_supported_alpha12_template_migrates_byte_stably(self) -> None:
        first = self.migrate()
        second = self.migrate()
        self.assertEqual(first.files, second.files)
        instance = load_mapping_yaml(first.files["instance.yaml"].decode("utf-8"))
        self.assertEqual(2, instance["data_schema_version"])
        self.assertEqual("0.1.0-alpha.13", instance["active_release"]["version"])
        self.assertEqual("state/operation-state.json", instance["state"]["operation_state_reference"])
        self.assertIn("operation_checkpoints_folder", load_mapping_yaml(first.files["state/file-map.yaml"].decode("utf-8"))["files"])
        self.assertEqual({"schema_version": 1, "tasks": []}, json.loads(first.files["data/canonical-tasks.json"]))

    def test_supported_legacy_task_row_and_completion_history_are_preserved(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        fixture["action_items_markdown"] = fixture["action_items_markdown"].replace(
            "|---|---|---|---|---|---|---|---|---|---|---|---|---|\n\n## Completion history",
            "|---|---|---|---|---|---|---|---|---|---|---|---|---|\n| task-1 | Return form | school | household | needs_action |  | 2026-09-01 | 2026-09-02 |  | 2026-09-03 | record-1#fact-1 | fact-1 | called |\n\n## Completion history",
        ).replace(
            "## Completion history\n\n| Task ID | Outcome | Detected at | Evidence source | Parent comment |\n|---|---|---|---|---|\n",
            "## Completion history\n\n| Task ID | Outcome | Detected at | Evidence source | Parent comment |\n|---|---|---|---|---|\n| task-1 | completed | 2026-09-04 | parent | done |\n",
        )
        register = json.loads(self.migrate(fixture).files["data/canonical-tasks.json"])
        task = register["tasks"][0]
        self.assertEqual(["fact-1"], task["source_facts"])
        self.assertEqual("2026-09-02", task["last_supporting_source_date"])
        self.assertEqual("done", task["lifecycle_history"][0]["parent_comment"])

    def test_active_state_or_unknown_legacy_markdown_blocks_without_candidate(self) -> None:
        active = copy.deepcopy(self.fixture)
        active["operation_state"]["status"] = "running"
        with self.assertRaisesRegex(MigrationError, "active operation state"):
            self.migrate(active)
        markdown = copy.deepcopy(self.fixture)
        markdown["action_items_markdown"] += "unmapped private note\n"
        with self.assertRaisesRegex(MigrationError, "trailing"):
            self.migrate(markdown)

    def test_non_alpha12_source_version_blocks_without_candidate(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        fixture["instance"]["system_version"] = "0.1.0-alpha.11"
        fixture["instance"]["active_release"]["version"] = "0.1.0-alpha.11"
        with self.assertRaisesRegex(MigrationError, "unsupported legacy"):
            self.migrate(fixture)


if __name__ == "__main__":
    unittest.main()
