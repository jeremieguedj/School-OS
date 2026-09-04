from __future__ import annotations

import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_instance import load_mapping_yaml, validate  # noqa: E402


class InstanceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = json.loads((ROOT / "schemas" / "instance.schema.json").read_text())
        cls.instance = load_mapping_yaml((ROOT / "templates" / "instance.yaml").read_text())

    def test_template_matches_schema(self) -> None:
        self.assertEqual([], validate(self.instance, self.schema))

    def test_all_template_root_fields_are_declared(self) -> None:
        self.assertEqual(set(self.instance), set(self.schema["properties"]))

    def test_unknown_nested_property_is_rejected(self) -> None:
        candidate = copy.deepcopy(self.instance)
        candidate["state"]["private_runtime_hint"] = "not-part-of-contract"
        self.assertIn("$.state: unexpected property 'private_runtime_hint'", validate(candidate, self.schema))

    def test_missing_template_field_is_rejected(self) -> None:
        candidate = copy.deepcopy(self.instance)
        del candidate["configuration"]["policies_reference"]
        self.assertIn("$.configuration: missing required property 'policies_reference'", validate(candidate, self.schema))

    def test_daily_run_personal_values_are_an_explicit_instance_dependency(self) -> None:
        self.assertEqual(
            "config/daily-run-personal-values.md",
            self.instance["configuration"]["daily_run_personal_values_reference"],
        )

    def test_cli_validates_template(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate_instance.py"), str(ROOT / "templates" / "instance.yaml")],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("valid:", result.stdout)


if __name__ == "__main__":
    unittest.main()
