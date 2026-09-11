from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "run_hybrid_preview", ROOT / "scripts" / "run_hybrid_preview.py",
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class HybridPreviewCliTests(unittest.TestCase):
    def transaction(self, generation: int, data: bytes) -> SimpleNamespace:
        reference = {"object_id": f"state-{generation}"}
        current = {
            "generation": generation,
            "state": {
                "bundle_reference": reference,
                "bundle_sha256": hashlib.sha256(data).hexdigest(),
            },
        }
        return SimpleNamespace(working=SimpleNamespace(recovery={
            "current": current,
            "current_reference": {"object_id": "current"},
        }))

    def test_repeated_phase_generations_use_distinct_local_artifacts(self) -> None:
        payloads = {"state-5": b"state-five", "state-7": b"state-seven"}

        class Storage:
            @staticmethod
            def read(object_id: str) -> SimpleNamespace:
                return SimpleNamespace(data=payloads[object_id])

        with tempfile.TemporaryDirectory() as temporary:
            run = Path(temporary)
            first = MODULE._updated_runtime({}, self.transaction(5, payloads["state-5"]), Storage(), run, "authorize")
            second = MODULE._updated_runtime({}, self.transaction(7, payloads["state-7"]), Storage(), run, "authorize")
            self.assertNotEqual(first["state_path"], second["state_path"])
            self.assertTrue(Path(first["state_path"]).is_file())
            self.assertTrue(Path(second["state_path"]).is_file())
            with self.assertRaises(FileExistsError):
                MODULE._updated_runtime({}, self.transaction(7, payloads["state-7"]), Storage(), run, "authorize")

    def test_scheduled_continuation_requires_private_runtime_serialization(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            private = Path(temporary)
            instance = private / "instance.json"
            instance.write_text("{}", encoding="utf-8")
            missing = SimpleNamespace(
                serialization=None, entrypoint="scheduled", phase="plan",
                instance_document=instance, observed_at="2026-09-10T00:00:00Z",
            )
            with self.assertRaisesRegex(ValueError, "requires runtime serialization"):
                MODULE._serialization(missing)
            evidence = private / "serialization.json"
            expected = {
                "mode": "runtime_serialized",
                "evidence": {
                    "instance_key": "instance", "queue_receipt": "queue",
                    "competing_mutators_excluded": True,
                    "observed_at": "2026-09-10T00:00:00Z",
                },
            }
            evidence.write_text(json.dumps(expected), encoding="utf-8")
            admitted = SimpleNamespace(
                serialization=evidence, entrypoint="scheduled", phase="plan",
                instance_document=instance, observed_at="2026-09-10T00:00:00Z",
            )
            self.assertEqual(expected, MODULE._serialization(admitted))


if __name__ == "__main__":
    unittest.main()
