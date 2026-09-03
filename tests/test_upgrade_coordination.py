from __future__ import annotations

import copy
import json
import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_capability_profile import validate_capability_profile  # noqa: E402


class UpgradeCoordinationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.upgrade = (ROOT / "core" / "operations" / "system-upgrade.md").read_text()
        cls.capabilities = (ROOT / "core" / "contracts" / "capabilities.md").read_text()
        cls.updates = (ROOT / "docs" / "updates.md").read_text()
        cls.migration = (ROOT / "docs" / "current-instance-migration.md").read_text()
        block = re.search(
            r"## Required capabilities and execution surface.*?```text\n(.*?)```",
            cls.upgrade,
            re.S,
        )
        if block is None:
            raise AssertionError("system-upgrade required-capability block is missing")
        cls.required_capabilities = [
            line.strip() for line in block.group(1).splitlines() if line.strip()
        ]
        cls.profile_schema = json.loads(
            (ROOT / "schemas" / "capability-profile.schema.json").read_text()
        )
        cls.profile_template = json.loads(
            (ROOT / "templates" / "state" / "capability-profile.json").read_text()
        )

    def upgrade_profile(self) -> dict:
        profile = copy.deepcopy(self.profile_template)
        profile["execution_surface"] = "interactive"
        profile["selected_adapters"]["scheduler"] = None
        profile["scheduler_behavior"] = None
        profile["conformant_operations"] = ["system-upgrade"]
        profile["capabilities"] = [
            {
                "capability_id": capability_id,
                "status": "available",
                "verification": "synthetic attended interactive probe",
                "limits": "synthetic bounded upgrade",
                "degradation": "stop_before_first_write",
            }
            for capability_id in self.required_capabilities
        ]
        return profile

    def test_upgrade_required_capabilities_are_catalogued(self) -> None:
        catalogued = set(
            re.findall(
                r"^(?:storage|release|coordination|mail|tasks|scheduler|audio)\.[a-z0-9_]+$",
                self.capabilities,
                re.M,
            )
        )
        required_section = self.upgrade.split("## Procedure", 1)[0]
        mentioned = set(
            re.findall(
                r"(?:storage|release|coordination|mail|tasks|scheduler|audio)\.[a-z0-9_]+",
                required_section,
            )
        )
        self.assertEqual(set(), mentioned - catalogued)

    def test_missing_or_unavailable_upgrade_capability_blocks(self) -> None:
        missing_profile = self.upgrade_profile()
        missing_id = self.required_capabilities[0]
        missing_profile["capabilities"] = missing_profile["capabilities"][1:]
        errors = validate_capability_profile(
            missing_profile,
            self.profile_schema,
            required_capabilities=self.required_capabilities,
            operation="system-upgrade",
            execution_surface="interactive",
        )
        self.assertIn(f"required capability {missing_id!r} is missing", errors)

        unavailable_profile = self.upgrade_profile()
        unavailable_id = self.required_capabilities[-1]
        unavailable_profile["capabilities"][-1]["status"] = "unavailable"
        errors = validate_capability_profile(
            unavailable_profile,
            self.profile_schema,
            required_capabilities=self.required_capabilities,
            operation="system-upgrade",
            execution_surface="interactive",
        )
        self.assertIn(
            f"required capability {unavailable_id!r} is 'unavailable', not 'available'",
            errors,
        )

    def test_upgrade_requires_attended_interactive_profile(self) -> None:
        profile = self.upgrade_profile()
        profile["execution_surface"] = "scheduled"
        errors = validate_capability_profile(
            profile,
            self.profile_schema,
            required_capabilities=self.required_capabilities,
            operation="system-upgrade",
            execution_surface="interactive",
        )
        self.assertIn("execution surface is 'scheduled', expected 'interactive'", errors)

    def test_native_conditional_mode_is_preserved(self) -> None:
        self.assertIn("`native_conditional`", self.upgrade)
        self.assertIn("bind the journaled active-release generation/revision", self.upgrade)
        self.assertIn("atomically bind the expected provider version", self.updates)

    def test_supervised_fallback_has_exclusive_writer_gate(self) -> None:
        required = (
            "`supervised_operational_single_writer`",
            "paused or disabled",
            "one upgrade actor",
            "no-concurrent-mutators guard",
            "direct Drive edits",
        )
        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.upgrade)

    def test_fallback_version_evidence_is_exact_and_complete(self) -> None:
        for phrase in ("exact target file ID", "`modified_time`", "SHA-256 of the complete bytes"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.upgrade)
                self.assertIn(phrase, self.capabilities)

    def test_fallback_uses_create_only_backups_and_journal_checkpoints(self) -> None:
        self.assertIn("generation-specific backup with create-only semantics", self.upgrade)
        self.assertIn("append-only checkpoint per phase", self.upgrade)
        self.assertIn("exact predecessor checkpoint ID and SHA-256", self.upgrade)

    def test_activation_is_last_and_immediately_verified(self) -> None:
        self.assertIn("Activate last", self.upgrade)
        self.assertIn("Immediately read back the active control file", self.upgrade)
        self.assertIn("Keep all schedules paused", self.upgrade)

    def test_restore_fails_closed_to_manual_recovery(self) -> None:
        self.assertIn("stop for manual recovery", self.upgrade)
        self.assertIn("Never claim automatic rollback without `storage.restore_verified`", self.upgrade)

    def test_completed_migration_is_verified_not_reapplied(self) -> None:
        self.assertIn("already records a migration complete", self.upgrade)
        self.assertIn("do not back up or rewrite that target", self.upgrade)

    def test_private_migration_evidence_supports_both_coordination_modes(self) -> None:
        for phrase in (
            "`native_conditional`",
            "provider generation/revision token",
            "`supervised_operational_single_writer`",
            "exact file ID",
            "`modified_time`",
            "complete-byte SHA-256",
            "no-concurrent-mutators guard",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.migration)


if __name__ == "__main__":
    unittest.main()
