from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

from school_os.package import verify_extracted_tree


ROOT = Path(__file__).resolve().parents[1]
class InstalledValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        output = Path(self.temporary.name) / "output"
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "build_release.py"), "--repo", str(ROOT), "--ref", "HEAD", "--version", "0.1.0-alpha.13", "--output-dir", str(output)],
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.archive = output / "school-os-0.1.0-alpha.13.tar.gz"
        self.root = Path(self.temporary.name) / "School-OS-0.1.0-alpha.13"
        with tarfile.open(self.archive, "r:gz") as package:
            package.extractall(self.temporary.name)

    def run_validator(self, target: Path, *extra: str, path_empty: bool = False) -> subprocess.CompletedProcess[str]:
        environment = None if not path_empty else {"PATH": str(Path(self.temporary.name) / "no-git")}
        return subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate_installed.py"), str(target), *extra],
            text=True, capture_output=True, check=False, env=environment,
        )

    def test_clean_candidate_passes_without_git(self) -> None:
        result = self.run_validator(self.root, "--candidate-test", path_empty=True)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertFalse((self.root / ".git").exists())

    def test_installed_clis_do_not_mutate_the_extracted_inventory_with_bytecode(self) -> None:
        before = verify_extracted_tree(self.root)
        answers = json.loads((ROOT / "tests" / "synthetic-fixtures" / "alpha13" / "answers.json").read_text(encoding="utf-8"))
        answers["package_root"] = str(self.root)
        answers["package_archive"] = str(self.archive)
        answers["package_source_identity"]["commit"] = subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True, capture_output=True, check=True,
        ).stdout.strip()
        answers_path = Path(self.temporary.name) / "answers.json"
        references_path = ROOT / "tests" / "synthetic-fixtures" / "alpha13" / "references.json"
        candidate = Path(self.temporary.name) / "candidate"
        answers_path.write_text(json.dumps(answers), encoding="utf-8")
        environment = dict(os.environ)
        environment.pop("PYTHONPYCACHEPREFIX", None)
        environment.pop("PYTHONDONTWRITEBYTECODE", None)
        scaffold = subprocess.run(
            [sys.executable, str(self.root / "scripts" / "scaffold_instance.py"), "--answers", str(answers_path), "--references", str(references_path), "--output", str(candidate)],
            text=True, capture_output=True, check=False, env=environment,
        )
        self.assertEqual(0, scaffold.returncode, scaffold.stderr)
        validator = subprocess.run(
            [sys.executable, str(self.root / "scripts" / "validate_installed.py"), str(self.root), "--candidate-test"],
            text=True, capture_output=True, check=False, env=environment,
        )
        self.assertEqual(0, validator.returncode, validator.stderr)
        self.assertEqual([], list(self.root.rglob("__pycache__")))
        self.assertEqual(before, verify_extracted_tree(self.root))

    def test_production_rejects_unreleased_and_changed_bytes(self) -> None:
        self.assertNotEqual(0, self.run_validator(self.root).returncode)
        path = self.root / "core" / "operations" / "daily-run.md"
        path.write_text(path.read_text(encoding="utf-8") + "changed\n", encoding="utf-8")
        result = self.run_validator(self.root, "--candidate-test")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("RELEASE-INVENTORY", result.stderr)

    def test_missing_registry_and_invalid_archive_evidence_fail(self) -> None:
        (self.root / "core" / "operations" / "registry.json").unlink()
        self.assertNotEqual(0, self.run_validator(self.root, "--candidate-test").returncode)
        broken = Path(self.temporary.name) / "broken.tar.gz"
        shutil.copy(self.archive, broken)
        self.assertNotEqual(0, self.run_validator(broken, "--candidate-test").returncode)


if __name__ == "__main__":
    unittest.main()
