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
from school_os.capabilities import CapabilityError, qualify_execution  # noqa: E402


class RuntimeConformanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = json.loads((ROOT / "schemas" / "capability-profile.schema.json").read_text())
        cls.template = json.loads((ROOT / "templates" / "state" / "capability-profile.json").read_text())

    def profile(self) -> dict:
        profile = copy.deepcopy(self.template)
        profile["evidence_class"] = "synthetic"
        profile["authentication"]["status"] = "available"
        for name in profile["network_paths"]:
            profile["network_paths"][name]["status"] = "available" if name != "scheduler" else "not_required"
        for name in profile["observations"]:
            profile["observations"][name]["status"] = "available"
        profile["capabilities"] = [
            {"capability_id": capability_id, "status": "available", "verification": {"method": "synthetic"}, "degradation": "stop_before_side_effects"}
            for capability_id in ("storage.read_complete", "mail.search", "tasks.list_complete")
        ]
        profile["conformant_operations"] = ["daily-run"]
        return profile

    def test_template_matches_schema(self) -> None:
        self.assertEqual([], validate(self.template, self.schema))

    def test_complete_manual_profile_is_conformant_without_scheduler(self) -> None:
        self.assertEqual(
            [],
            validate_capability_profile(
                self.profile(),
                self.schema,
                required_capabilities=["storage.read_complete", "mail.search", "tasks.list_complete"],
                operation="daily-run",
                execution_surface="manual",
            ),
        )

    def test_missing_required_capability_blocks(self) -> None:
        errors = validate_capability_profile(
            self.profile(), self.schema, required_capabilities=["mail.send"]
        )
        self.assertIn("missing required capability: mail.send", errors)

    def test_non_available_required_capability_blocks(self) -> None:
        for status in ("unknown", "unavailable"):
            with self.subTest(status=status):
                profile = self.profile()
                profile["capabilities"][0]["status"] = status
                errors = validate_capability_profile(
                    profile, self.schema, required_capabilities=["storage.read_complete"]
                )
                self.assertIn(
                    f"required capability is {status!r}: storage.read_complete",
                    errors,
                )

    def test_duplicate_capability_id_blocks(self) -> None:
        profile = self.profile()
        profile["capabilities"].append(copy.deepcopy(profile["capabilities"][0]))
        errors = validate_capability_profile(profile, self.schema)
        self.assertTrue(any("duplicate capability" in error for error in errors))

    def test_manual_evidence_does_not_satisfy_scheduled_surface(self) -> None:
        profile = self.profile()
        errors = validate_capability_profile(profile, self.schema, execution_surface="scheduled")
        self.assertIn("execution surface is 'manual', expected 'scheduled'", errors)

    def test_scheduled_profile_requires_scheduler_adapter_and_behavior(self) -> None:
        profile = self.profile()
        profile["execution_surface"] = "scheduled"
        profile["selected_adapters"]["scheduler"] = None
        profile["scheduler_behavior"] = None
        profile["capabilities"].extend([
            {"capability_id": capability_id, "status": "available", "verification": {"method": "synthetic"}, "degradation": "stop_before_side_effects"}
            for capability_id in ("scheduler.inspect", "scheduler.verify")
        ])
        errors = validate_capability_profile(profile, self.schema, execution_surface="scheduled")
        self.assertIn("scheduled execution requires observed-surface evidence", errors)

    def test_scheduled_profile_requires_observed_evidence_and_each_network_path(self) -> None:
        profile = self.profile()
        profile["execution_surface"] = "scheduled"
        profile["selected_adapters"]["scheduler"] = "schedulers/synthetic.md"
        profile["scheduler_behavior"] = {"overlap": "blocked", "retry": "observed"}
        profile["network_paths"]["scheduler"]["status"] = "available"
        profile["capabilities"].extend([
            {"capability_id": capability_id, "status": "available", "verification": {"method": "synthetic"}, "degradation": "stop_before_side_effects"}
            for capability_id in ("scheduler.inspect", "scheduler.verify")
        ])
        with self.assertRaisesRegex(CapabilityError, "observed-surface"):
            qualify_execution(profile, self.schema, operation="daily-run", entrypoint="scheduled")
        profile["evidence_class"] = "observed"
        self.assertEqual("scheduled", qualify_execution(profile, self.schema, operation="daily-run", entrypoint="scheduled").entrypoint)
        for path in ("storage", "mail", "tasks", "scheduler"):
            with self.subTest(path=path):
                unavailable = copy.deepcopy(profile)
                unavailable["network_paths"][path]["status"] = "unavailable"
                with self.assertRaisesRegex(CapabilityError, path):
                    qualify_execution(unavailable, self.schema, operation="daily-run", entrypoint="scheduled")

    def test_undeclared_operation_blocks(self) -> None:
        errors = validate_capability_profile(self.profile(), self.schema, operation="task-sync")
        self.assertIn("operation is not declared conformant: task-sync", errors)

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
                    "manual",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("conformant:", result.stdout)

    def test_unknown_limits_are_conservative_and_named_blockers_fail(self) -> None:
        plan = qualify_execution(self.profile(), self.schema, operation="daily-run", entrypoint="manual")
        self.assertEqual(1, plan.max_records_per_unit)
        self.assertEqual(65536, plan.max_bytes_per_unit)
        profile = self.profile()
        profile["authentication"]["status"] = "unknown"
        with self.assertRaisesRegex(CapabilityError, "authentication is 'unknown'"):
            qualify_execution(profile, self.schema, operation="daily-run", entrypoint="manual")

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
        self.assertIn("reference profile only", runtime)
        self.assertIn("no scheduled ChatGPT Work support claim", runtime)
        self.assertIn("scheduled execution", runtime.lower())
        self.assertIn("reference adapter only", scheduler)
        self.assertIn("synthetic", scheduler)
        self.assertIn("single writer", scheduler.lower())


if __name__ == "__main__":
    unittest.main()
