from __future__ import annotations

import unittest

from school_os.hybrid_preview import _planned_task_sync_transition


class HybridPreviewTransitionTests(unittest.TestCase):
    def test_zero_actions_completes_task_sync_without_dispatch(self) -> None:
        phase, completed, remaining = _planned_task_sync_transition(0)

        self.assertEqual("task_sync", phase)
        self.assertEqual(
            ["preflight", "discover", "catalog", "reconcile", "task_sync"],
            completed,
        )
        self.assertEqual({"phase": "brief_delivery"}, remaining)

    def test_pending_actions_remain_at_reconcile_boundary(self) -> None:
        phase, completed, remaining = _planned_task_sync_transition(2)

        self.assertEqual("reconcile", phase)
        self.assertEqual(
            ["preflight", "discover", "catalog", "reconcile"], completed,
        )
        self.assertEqual(
            {"phase": "task_sync", "pending_action_count": 2}, remaining,
        )


if __name__ == "__main__":
    unittest.main()
