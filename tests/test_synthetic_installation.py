from __future__ import annotations

import json
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "synthetic-fixtures" / "alpha13"

from tests.support.fakes import FixtureMail, FixtureTasks, SendSink  # noqa: E402


class SyntheticInstallationTests(unittest.TestCase):
    def test_fresh_process_scaffolds_and_resolves_only_extracted_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            output = base / "release"
            built = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_release.py"), "--repo", str(ROOT), "--ref", "HEAD", "--version", "0.1.0-alpha.13", "--output-dir", str(output)],
                text=True, capture_output=True, check=False,
            )
            self.assertEqual(0, built.returncode, built.stderr)
            archive = output / "school-os-0.1.0-alpha.13.tar.gz"
            with tarfile.open(archive, "r:gz") as package:
                package.extractall(base)
            extracted = base / "School-OS-0.1.0-alpha.13"
            answers = json.loads((FIXTURE / "answers.json").read_text(encoding="utf-8"))
            answers["package_root"] = str(extracted)
            answers["package_archive"] = str(archive)
            answers["package_source_identity"]["commit"] = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True, capture_output=True, check=True).stdout.strip()
            answers_path = base / "answers.json"
            references_path = base / "references.json"
            answers_path.write_text(json.dumps(answers), encoding="utf-8")
            references_path.write_bytes((FIXTURE / "references.json").read_bytes())
            candidate = base / "instance"
            installed = subprocess.run(
                [sys.executable, str(extracted / "scripts" / "scaffold_instance.py"), "--answers", str(answers_path), "--references", str(references_path), "--output", str(candidate)],
                text=True, capture_output=True, check=False,
            )
            self.assertEqual(0, installed.returncode, installed.stderr)
            self.assertIn("candidate:", installed.stdout)
            self.assertIn("config/daily-run-personal-values.md:", installed.stdout)
            resolved = subprocess.run(
                [sys.executable, "-c", "from pathlib import Path; from school_os.references import load_operation_registry; r=Path.cwd(); print(load_operation_registry(r/'core/operations/registry.json', r/'schemas/operation-registry.schema.json', r)['daily-run'])"],
                cwd=extracted, text=True, capture_output=True, check=False,
            )
            self.assertEqual(0, resolved.returncode, resolved.stderr)
            self.assertEqual("core/operations/daily-run.md", resolved.stdout.strip())
            self.assertTrue((candidate / "state" / "installation-manifest.json").is_file())
            self.assertEqual([], json.loads((FIXTURE / "source-corpus.json").read_text(encoding="utf-8"))["conversations"])
            self.assertEqual([], FixtureMail().search())
            self.assertEqual([], FixtureTasks().tasks)
            self.assertEqual([], SendSink().deliveries)


if __name__ == "__main__":
    unittest.main()
