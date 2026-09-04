from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ManualDailyRunContractTests(unittest.TestCase):
    def test_manual_request_dispatches_through_the_verified_schedule(self) -> None:
        recipe = (ROOT / "core" / "operations" / "manual-daily-run.md").read_text(encoding="utf-8")
        self.assertIn("run-now", recipe)
        self.assertIn("same stable schedule identity", recipe)
        self.assertIn("not an alternate implementation", recipe)
        self.assertIn("do not press run-now again", recipe)
        self.assertIn("`scheduler.run_now`", recipe)

    def test_manual_request_does_not_create_a_second_sender(self) -> None:
        recipe = (ROOT / "core" / "operations" / "manual-daily-run.md").read_text(encoding="utf-8")
        self.assertIn("Do not read source mail", recipe)
        self.assertIn("send mail in this dispatcher", recipe)
        self.assertIn("does not modify the next", recipe)

    def test_daily_run_uses_delivery_idempotency_not_a_drive_lease(self) -> None:
        recipe = (ROOT / "core" / "operations" / "daily-run.md").read_text(encoding="utf-8")
        required = recipe.split("## Required capabilities", 1)[1].split("For a scheduler-issued run", 1)[0]
        self.assertNotIn("coordination.ensure_idle", required)
        self.assertIn("do not create or wait for a separate Drive lease", recipe)
        self.assertIn("matching Sent message", recipe)
        self.assertIn("verified message ID and delivery key", recipe)


if __name__ == "__main__":
    unittest.main()
