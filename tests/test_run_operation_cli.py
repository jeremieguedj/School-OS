from __future__ import annotations

import base64
import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from school_os.daily import PHASES
from scripts import run_operation


ROOT = Path(__file__).resolve().parents[1]


class RunOperationCliTests(unittest.TestCase):
    def files(self, base: Path) -> tuple[Path, Path]:
        profile = json.loads((ROOT / "templates" / "state" / "capability-profile.json").read_text())
        profile["execution_surface"] = "manual"
        profile["evidence_class"] = "synthetic"
        profile["authentication"]["status"] = "available"
        profile["conformant_operations"] = ["daily-run"]
        for name in ("storage", "mail", "tasks"):
            profile["network_paths"][name]["status"] = "available"
        for observation in profile["observations"].values():
            observation["status"] = "available"
        profile["capabilities"] = [
            {"capability_id": name, "status": "available", "verification": {}, "degradation": "stop_before_side_effects"}
            for name in ("storage.read_complete", "mail.search", "tasks.list_complete")
        ]
        profile_path = base / "profile.json"
        stages_path = base / "stages.json"
        profile_path.write_text(json.dumps(profile), encoding="utf-8")
        stages_path.write_text(json.dumps({phase: {"verified": True, "phase": phase} for phase in PHASES}), encoding="utf-8")
        return profile_path, stages_path

    def command(self, profile: Path) -> list[str]:
        return [sys.executable, str(ROOT / "scripts" / "run_operation.py"), "--instance", "synthetic", "--operation", "daily-run", "--profile", str(profile), "--operation-id", "op-1", "--attempt-id", "attempt-1"]

    def test_stage_results_are_explicitly_synthetic_and_exclude_real_entrypoint(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            profile, stages = self.files(Path(temporary))
            result = subprocess.run(self.command(profile) + ["--stage-results", str(stages)], text=True, capture_output=True, check=False)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual("COMPLETE", json.loads(result.stdout)["outcome"])
            rejected = subprocess.run(self.command(profile) + ["--stage-results", str(stages), "--entrypoint", "manual"], text=True, capture_output=True, check=False)
            self.assertNotEqual(0, rejected.returncode)
            self.assertIn("mutually exclusive", rejected.stderr)

    def test_host_mode_requires_bootstrap_and_entrypoint(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            profile, _ = self.files(Path(temporary))
            run_dir = Path(temporary) / "run"
            run_dir.mkdir(mode=0o700)
            result = subprocess.run(self.command(profile) + ["--host-jsonl", str(run_dir)], text=True, capture_output=True, check=False)
            self.assertNotEqual(0, result.returncode)
            self.assertIn("requires --bootstrap-reference and --entrypoint", result.stderr)

    def test_host_mode_requires_narrow_profile_and_complete_exact_bootstrap_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            profile_path, _ = self.files(base)
            profile = json.loads(profile_path.read_text())
            profile["conformant_operations"] = []
            profile["capabilities"] = [profile["capabilities"][0]]
            profile["network_paths"]["mail"]["status"] = "unavailable"
            profile["network_paths"]["tasks"]["status"] = "unavailable"
            profile["observations"]["pagination"]["status"] = "unknown"
            profile_path.write_text(json.dumps(profile), encoding="utf-8")
            run_dir = base / "run"
            run_dir.mkdir(mode=0o700)
            bootstrap = base / "bootstrap.json"
            bootstrap.write_text(json.dumps({"object_id": "bootstrap-id", "url": "drive://bootstrap-id"}))
            argv = self.command(profile_path)[2:] + [
                "--host-jsonl", str(run_dir), "--bootstrap-reference", str(bootstrap),
                "--entrypoint", "manual",
            ]
            content = b"# Private bootstrap\n"

            class CompleteDrive:
                def __init__(self, _peer): pass
                def metadata(self, object_id, *, fields):
                    return {"id": object_id, "size": str(len(content))}
                def fetch(self, url, *, raw=True, include_base64=True):
                    return {
                        "id": "bootstrap-id", "b64_string": base64.b64encode(content).decode("ascii"),
                        "file_size_bytes": len(content), "is_empty": False,
                    }

            output = io.StringIO()
            with mock.patch.object(run_operation, "CodexDrivePort", CompleteDrive), contextlib.redirect_stdout(output):
                self.assertEqual(0, run_operation.main(argv))
            self.assertEqual("BOOTSTRAP_READBACK_VERIFIED", json.loads(output.getvalue())["outcome"])

            class EmptyDrive(CompleteDrive):
                def fetch(self, url, *, raw=True, include_base64=True):
                    return {"id": "bootstrap-id"}

            error = io.StringIO()
            with mock.patch.object(run_operation, "CodexDrivePort", EmptyDrive), contextlib.redirect_stderr(error):
                self.assertEqual(1, run_operation.main(argv))
            self.assertIn("lacks complete raw base64 bytes", error.getvalue())

            profile_path.write_text("{}\n", encoding="utf-8")
            constructed = []
            class UnexpectedDrive(CompleteDrive):
                def __init__(self, peer): constructed.append(peer)
            error = io.StringIO()
            with mock.patch.object(run_operation, "CodexDrivePort", UnexpectedDrive), contextlib.redirect_stderr(error):
                self.assertEqual(1, run_operation.main(argv))
            self.assertEqual([], constructed)
            self.assertIn("invalid capability profile", error.getvalue())


if __name__ == "__main__":
    unittest.main()
