from __future__ import annotations

import copy
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_capability_profile import validate_capability_profile  # noqa: E402
from validate_instance import validate  # noqa: E402


class RuntimeConformanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = json.loads((ROOT / "schemas" / "capability-profile.schema.json").read_text())
        cls.template = json.loads((ROOT / "templates" / "state" / "capability-profile.json").read_text())

    def profile(self) -> dict:
        profile = copy.deepcopy(self.template)
        profile["capabilities"] = [
            {
                "capability_id": "storage.read_complete",
                "status": "available",
                "verification": "synthetic scheduled-surface probe",
                "limits": "synthetic bounded input",
                "degradation": "stop_before_side_effects",
            }
        ]
        profile["conformant_operations"] = ["daily-run"]
        return profile

    def test_template_matches_schema(self) -> None:
        self.assertEqual([], validate(self.template, self.schema))

    def test_complete_scheduled_profile_is_conformant(self) -> None:
        self.assertEqual(
            [],
            validate_capability_profile(
                self.profile(),
                self.schema,
                required_capabilities=["storage.read_complete"],
                operation="daily-run",
                execution_surface="scheduled",
            ),
        )

    def test_missing_required_capability_blocks(self) -> None:
        errors = validate_capability_profile(
            self.profile(), self.schema, required_capabilities=["mail.search"]
        )
        self.assertIn("required capability 'mail.search' is missing", errors)

    def test_non_available_required_capability_blocks(self) -> None:
        for status in ("unknown", "unavailable"):
            with self.subTest(status=status):
                profile = self.profile()
                profile["capabilities"][0]["status"] = status
                errors = validate_capability_profile(
                    profile, self.schema, required_capabilities=["storage.read_complete"]
                )
                self.assertIn(
                    f"required capability 'storage.read_complete' is {status!r}, not 'available'",
                    errors,
                )

    def test_duplicate_capability_id_blocks(self) -> None:
        profile = self.profile()
        profile["capabilities"].append(copy.deepcopy(profile["capabilities"][0]))
        errors = validate_capability_profile(profile, self.schema)
        self.assertTrue(any("duplicate capability_id" in error for error in errors))

    def test_interactive_evidence_does_not_satisfy_scheduled_surface(self) -> None:
        profile = self.profile()
        profile["execution_surface"] = "interactive"
        profile["selected_adapters"]["scheduler"] = None
        profile["scheduler_behavior"] = None
        errors = validate_capability_profile(profile, self.schema, execution_surface="scheduled")
        self.assertIn("execution surface is 'interactive', expected 'scheduled'", errors)

    def test_scheduled_profile_requires_scheduler_adapter_and_behavior(self) -> None:
        profile = self.profile()
        profile["selected_adapters"]["scheduler"] = None
        profile["scheduler_behavior"] = None
        errors = validate_capability_profile(profile, self.schema)
        self.assertIn("scheduled profile requires a selected scheduler adapter", errors)
        self.assertIn("scheduled profile requires observed scheduler behavior", errors)

    def test_undeclared_operation_blocks(self) -> None:
        errors = validate_capability_profile(self.profile(), self.schema, operation="task-sync")
        self.assertIn("operation 'task-sync' is not declared conformant", errors)

    def test_cli_applies_required_scope(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            profile_path = Path(temporary) / "profile.json"
            profile_path.write_text(json.dumps(self.profile()), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "validate_capability_profile.py"),
                    str(profile_path),
                    "--required-capability",
                    "storage.read_complete",
                    "--operation",
                    "daily-run",
                    "--execution-surface",
                    "scheduled",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("conformant:", result.stdout)

    def test_every_daily_run_capability_is_in_core_catalog(self) -> None:
        daily_run = (ROOT / "core" / "operations" / "daily-run.md").read_text()
        block = re.search(r"## Required capabilities.*?\x60\x60\x60text\n(.*?)\x60\x60\x60", daily_run, re.S)
        self.assertIsNotNone(block)
        declared = {line.strip() for line in block.group(1).splitlines() if line.strip()}
        capability_contract = (ROOT / "core" / "contracts" / "capabilities.md").read_text()
        catalogued = set(re.findall(r"^(?:storage|release|coordination|mail|tasks|scheduler|audio)\.[a-z_]+$", capability_contract, re.M))
        self.assertEqual(set(), declared - catalogued)

    def test_todoist_required_operations_have_capability_ids(self) -> None:
        capability_contract = (ROOT / "core" / "contracts" / "capabilities.md").read_text()
        required = {
            "tasks.read_identity",
            "tasks.discover_configuration",
            "tasks.list_complete",
            "tasks.list_completed",
            "tasks.read_activity",
            "tasks.read_comments",
            "tasks.create",
            "tasks.update",
            "tasks.move",
            "tasks.complete",
            "tasks.reopen",
            "tasks.write_comment",
            "tasks.verify",
        }
        self.assertTrue(all(capability_id in capability_contract for capability_id in required))

    def test_chatgpt_work_has_runtime_and_scheduler_contracts(self) -> None:
        runtime = (ROOT / "adapters" / "runtimes" / "chatgpt-work.md").read_text()
        scheduler = (ROOT / "adapters" / "schedulers" / "chatgpt-work.md").read_text()
        self.assertIn("production-capable reference profile", runtime)
        self.assertIn("scheduled execution", runtime.lower())
        self.assertIn("production-capable reference adapter", scheduler)
        self.assertIn("single writer", scheduler.lower())


if __name__ == "__main__":
    unittest.main()
