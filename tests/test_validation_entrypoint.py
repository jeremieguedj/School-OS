from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ValidationEntrypointTests(unittest.TestCase):
    def test_no_argument_entrypoint_exists(self) -> None:
        path = ROOT / "scripts" / "validate.py"
        self.assertTrue(path.is_file())
        self.assertIn("def main()", path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
