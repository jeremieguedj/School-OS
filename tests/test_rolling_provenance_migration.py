from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from migrate_rolling_provenance import Fact, migrate  # noqa: E402


CONFIG = {
    "scope_groups": {"child_1": "Child 1", "child_2": "Child 2", "household": "Family"},
    "shared_group": "Family",
    "unscoped_update_group": "Family",
}
DAY = "2026-01-08"


def fact(fact_id: str = "SYN-F1", **changes: object) -> Fact:
    values = {
        "fact_id": fact_id,
        "source_id": "SYN-SOURCE-001",
        "scope": ("child_1",),
        "text": "The class completed a science observation.",
        "is_update": True,
        "is_guideline": False,
        "is_action": False,
        "received_day": DAY,
        "record_received_dates": (),
    }
    values.update(changes)
    return Fact(**values)


def rolling(*, source: str = "SYN-SOURCE-001", group: str = "Child 1", facts: str = "") -> str:
    suffix = f" [Facts:{facts}]" if facts else ""
    return f"## {DAY}\n- {group}: The class completed a science observation. [TID:{source}]{suffix}\n"


class RollingProvenanceMigrationTests(unittest.TestCase):
    def test_exact_match_is_migrated(self) -> None:
        result = migrate(rolling(), [fact()], CONFIG)
        self.assertEqual("migrated", result["status"])
        self.assertIn("[Facts:SYN-F1]", result["output"])
        self.assertEqual(1, result["migrated_bullets"])

    def test_zero_match_blocks_without_changing_input(self) -> None:
        original = rolling()
        result = migrate(original, [fact(text="Different text.")], CONFIG)
        self.assertEqual("blocked", result["status"])
        self.assertEqual(original, result["output"])
        self.assertEqual("zero_matches", result["exceptions"][0]["reason"])

    def test_ambiguous_match_blocks_without_choosing(self) -> None:
        result = migrate(rolling(), [fact("SYN-F1"), fact("SYN-F2")], CONFIG)
        self.assertEqual("blocked", result["status"])
        self.assertEqual(["SYN-F1", "SYN-F2"], result["exceptions"][0]["candidate_fact_ids"])

    def test_multi_entity_and_unscoped_facts_project_to_shared_group(self) -> None:
        original = (
            f"## {DAY}\n"
            "- Family: The class completed a science observation. [TID:SYN-SOURCE-001]\n"
            "- Family: The class completed a science observation. [TID:SYN-SOURCE-002]\n"
        )
        facts = [
            fact("SYN-F1", scope=("child_1", "child_2")),
            fact("SYN-F2", source_id="SYN-SOURCE-002", scope=("unscoped",)),
        ]
        result = migrate(original, facts, CONFIG)
        self.assertEqual("migrated", result["status"])
        self.assertIn("[Facts:SYN-F1]", result["output"])
        self.assertIn("[Facts:SYN-F2]", result["output"])

    def test_singular_record_date_fallback_is_counted(self) -> None:
        result = migrate(
            rolling(),
            [fact(received_day=None, record_received_dates=(DAY,))],
            CONFIG,
        )
        self.assertEqual("migrated", result["status"])
        self.assertEqual(1, result["record_date_fallbacks"])

    def test_ranged_record_date_blocks(self) -> None:
        original = rolling()
        result = migrate(original, [fact(received_day=None, record_received_dates=(DAY, "2026-01-09"))], CONFIG)
        self.assertEqual("blocked", result["status"])
        self.assertEqual(original, result["output"])

    def test_missing_record_date_blocks(self) -> None:
        self.assertEqual("blocked", migrate(rolling(), [fact(received_day=None)], CONFIG)["status"])

    def test_missing_source_record_blocks(self) -> None:
        result = migrate(rolling(source="SYN-STALE-SOURCE"), [fact()], CONFIG)
        self.assertEqual("source_not_found", result["exceptions"][0]["reason"])

    def test_action_or_guideline_fact_is_ineligible(self) -> None:
        self.assertEqual("blocked", migrate(rolling(), [fact(is_action=True)], CONFIG)["status"])
        self.assertEqual("blocked", migrate(rolling(), [fact(is_guideline=True)], CONFIG)["status"])

    def test_invalid_existing_reference_blocks(self) -> None:
        original = rolling(facts="SYN-NOT-A-FACT")
        result = migrate(original, [fact()], CONFIG)
        self.assertEqual("blocked", result["status"])
        self.assertEqual(original, result["output"])
        self.assertEqual("invalid_existing_fact_references", result["exceptions"][0]["reason"])

    def test_valid_existing_reference_is_idempotent(self) -> None:
        original = rolling(facts="SYN-F1")
        result = migrate(original, [fact()], CONFIG)
        self.assertEqual("migrated", result["status"])
        self.assertEqual(original, result["output"])
        self.assertEqual(0, result["migrated_bullets"])
        self.assertEqual(1, result["idempotently_skipped_bullets"])

    def test_presentation_wrappers_and_fact_prefix_normalize(self) -> None:
        result = migrate(rolling(), [fact(text="`SYN-F1`: **The class** completed a science observation.")], CONFIG)
        self.assertEqual("migrated", result["status"])


if __name__ == "__main__":
    unittest.main()
