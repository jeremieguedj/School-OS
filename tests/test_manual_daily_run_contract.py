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

    def test_scheduled_runtime_does_not_require_unobservable_run_now_provenance(self) -> None:
        recipe = (ROOT / "core" / "operations" / "daily-run.md").read_text(encoding="utf-8")
        scheduler = (ROOT / "adapters" / "schedulers" / "chatgpt-work.md").read_text(encoding="utf-8")
        self.assertIn("must not require a fresh Run-now observation", recipe)
        self.assertIn("does not expose its invocation provenance", scheduler)
        self.assertIn("`scheduler.run_now`", recipe)

    def test_daily_run_requires_raw_markdown_and_independent_source_comparison(self) -> None:
        recipe = (ROOT / "core" / "operations" / "daily-run.md").read_text(encoding="utf-8")
        runtime = (ROOT / "adapters" / "runtimes" / "chatgpt-work.md").read_text(encoding="utf-8")
        self.assertIn("raw UTF-8 Markdown", recipe)
        self.assertIn("directly with the complete plaintext body", recipe)
        self.assertIn("exact bytes", recipe)
        self.assertIn("Raw Markdown storage", runtime)
        self.assertIn("Native Google Docs", runtime)
        self.assertIn("not substitutes", runtime)

    def test_scheduled_run_cannot_stop_after_an_intermediate_phase(self) -> None:
        recipe = (ROOT / "core" / "operations" / "daily-run.md").read_text(encoding="utf-8")
        self.assertIn("must not return after a successful intermediate phase", recipe)
        self.assertIn("`COMPLETE`", recipe)
        self.assertIn("`BLOCKED`", recipe)
        self.assertIn("continue immediately to the next phase", recipe)

    def test_routine_and_dispatcher_do_not_sweep_the_logical_file_map(self) -> None:
        for relative_path in ("core/operations/daily-run.md", "core/operations/manual-daily-run.md"):
            recipe = (ROOT / relative_path).read_text(encoding="utf-8")
            normalized = " ".join(recipe.split())
            self.assertIn("logical file map", normalized)
            self.assertIn("sweep it", normalized)


if __name__ == "__main__":
    unittest.main()
