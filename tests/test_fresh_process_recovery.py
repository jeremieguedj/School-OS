from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class FreshProcessRecoveryTests(unittest.TestCase):
    def test_deleted_local_output_resumes_in_a_new_process(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            durable = root / "durable.json"
            local = root / "local-output.json"
            durable.write_text(json.dumps({"previous": {"verified": True, "phase": "catalog"}}), encoding="utf-8")
            local.write_text("discardable", encoding="utf-8")
            local.unlink()
            code = (
                "import json,sys; from pathlib import Path; "
                "from tests.test_daily_runner import DailyRunnerTests; "
                "from school_os.daily import run_daily; "
                "x=DailyRunnerTests('test_manual_runs_all_phases_without_scheduler'); x.setUpClass(); "
                "stages,_=x.stages(); data=json.loads((Path(sys.argv[1])/'durable.json').read_text()); "
                "r=run_daily(profile=x.profile('manual'),capability_schema=x.schema,entrypoint='manual',operation_id='daily-001',attempt_id='attempt-002',stages=stages,resume_after='catalog',durable_predecessor_output=data['previous']); "
                "print(json.dumps([r.outcome,r.operation_id,r.attempt_id,next(iter(r.outputs))]))"
            )
            result = subprocess.run([sys.executable, "-c", code, str(root)], cwd=ROOT, text=True, capture_output=True, check=False)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(["COMPLETE", "daily-001", "attempt-002", "reconcile"], json.loads(result.stdout))


if __name__ == "__main__":
    unittest.main()
