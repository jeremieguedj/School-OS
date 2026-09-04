from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_source_record import validate_lossless_bodies  # noqa: E402


BODY_1 = "Hello families,\n\nPlease return the complete form.\n\nThank you.\n"
BODY_2 = "A second message follows.\nDo not omit this footer.\n"


def record(body_1: str = BODY_1, body_2: str = BODY_2) -> str:
    return (
        "# Synthetic source record\n\n"
        "## Facts\n\nSynthetic.\n\n"
        "## Raw message text (verbatim)\n\n"
        "### Message 1 of 2 — id msg-1\n"
        "Date: 2026-09-03\nFrom: school@example.invalid\n\n"
        f"{body_1}"
        "### Message 2 of 2 — id msg-2\n"
        "Date: 2026-09-03\nFrom: teacher@example.invalid\n\n"
        f"{body_2}"
    )


class SourceCatalogLosslessnessTests(unittest.TestCase):
    def source(self) -> dict[str, str]:
        return {"msg-1": BODY_1, "msg-2": BODY_2}

    def test_exact_ordered_bodies_pass(self) -> None:
        self.assertEqual([], validate_lossless_bodies(record(), self.source()))

    def test_truncation_fails(self) -> None:
        errors = validate_lossless_bodies(record(body_1=BODY_1[:-9]), self.source())
        self.assertTrue(any("msg-1" in error and "not verbatim" in error for error in errors))

    def test_summary_fails(self) -> None:
        errors = validate_lossless_bodies(record(body_1="Families must return a form.\n"), self.source())
        self.assertTrue(any("msg-1" in error and "not verbatim" in error for error in errors))

    def test_substitution_fails(self) -> None:
        errors = validate_lossless_bodies(record(body_2=BODY_2.replace("footer", "signature")), self.source())
        self.assertTrue(any("msg-2" in error and "not verbatim" in error for error in errors))

    def test_reordered_messages_fail(self) -> None:
        reversed_source = {"msg-2": BODY_2, "msg-1": BODY_1}
        errors = validate_lossless_bodies(record(), reversed_source)
        self.assertTrue(any("ordered message IDs differ" in error for error in errors))

    def test_whitespace_normalization_fails(self) -> None:
        errors = validate_lossless_bodies(record(body_1=BODY_1.replace("\n\n", "\n")), self.source())
        self.assertTrue(any("msg-1" in error and "not verbatim" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
