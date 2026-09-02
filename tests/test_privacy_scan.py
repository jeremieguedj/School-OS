from __future__ import annotations

import sys
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from privacy_scan import configured_private_needles, scan_text, scan_tracked_files  # noqa: E402


class PrivacyScanTests(unittest.TestCase):
    def test_drive_and_docs_urls_fail(self) -> None:
        for text in (
            "https://" + "drive.google.com/drive/folders/SYNTHETIC",
            "https://" + "docs.google.com/document/d/SYNTHETIC",
        ):
            self.assertTrue(scan_text("fixture.txt", text))

    def test_drive_like_identifier_fails(self) -> None:
        identifier = "1AbCdEfGhIjKlMnOp" + "QrStUvWxYz_23456789"
        self.assertIn("Drive-like identifier", scan_text("fixture.txt", identifier)[0])

    def test_non_reserved_email_fails(self) -> None:
        address = "person" + "@school.edu"
        self.assertIn("email address", scan_text("fixture.txt", address)[0])

    def test_reserved_synthetic_emails_pass(self) -> None:
        for address in ("tester@example.invalid", "fixture@example.com", "fixture@example.org"):
            self.assertEqual([], scan_text("fixture.txt", address))

    def test_private_key_and_credential_assignment_fail(self) -> None:
        marker = "-----BEGIN " + "PRIVATE KEY-----"
        assignment = "api" + "_key = live_secret_material_123"
        self.assertTrue(scan_text("fixture.txt", marker))
        self.assertTrue(scan_text("fixture.txt", assignment))

    def test_placeholder_credentials_pass(self) -> None:
        assignment = "client" + "_secret: REPLACE_WITH_PRIVATE_SECRET"
        self.assertEqual([], scan_text("fixture.txt", assignment))

    def test_environment_needles_are_not_embedded_in_diagnostics(self) -> None:
        needle = "private" + "-household-marker"
        needles = configured_private_needles({"SCHOOL_OS_PRIVATE_NEEDLES": needle + "\nsecond-private-value"})
        violations = scan_text("fixture.txt", f"prefix {needle} suffix", needles)
        self.assertEqual(1, len(violations))
        self.assertNotIn(needle, violations[0])

    def test_github_urls_and_generic_provider_names_pass(self) -> None:
        text = (
            "https://github.com/example/RepositoryWithMixedCase123456789 "
            "Google Drive, Gmail, Todoist, and GitHub are supported provider names."
        )
        self.assertEqual([], scan_text("fixture.txt", text))

    def test_tracked_scan_uses_environment_needles_and_ignores_untracked_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            needle = "known-private" + "-marker"
            (repo / "tracked.txt").write_text(f"contains {needle}\n", encoding="utf-8")
            (repo / "untracked.txt").write_text("person" + "@school.edu\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "add", "tracked.txt"], check=True)
            with mock.patch.dict("os.environ", {"SCHOOL_OS_PRIVATE_NEEDLES": needle}, clear=False):
                violations = scan_tracked_files(repo)
            self.assertEqual(1, len(violations))
            self.assertIn("configured private needle 1", violations[0])
            self.assertNotIn(needle, violations[0])


if __name__ == "__main__":
    unittest.main()
