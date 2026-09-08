from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from verify_release import ReleaseVerificationError, candidate_assets, verify_remote_release  # noqa: E402


class ReleaseVerificationTests(unittest.TestCase):
    repo = "example/school-os"
    version = "1.2.3-alpha.1"
    commit = "a" * 40

    def setUp(self) -> None:
        self.assets = {
            "school-os-1.2.3-alpha.1.tar.gz": b"synthetic archive bytes",
            "SHA256SUMS": b"synthetic checksum bytes\n",
        }
        self.release = {
            "tagName": "v1.2.3-alpha.1",
            "targetCommitish": self.commit,
            "isDraft": True,
            "isImmutable": False,
            "assets": [{"name": name} for name in self.assets],
        }

    def runner(self, command: list[str]) -> bytes:
        if command[:3] == ["gh", "release", "view"]:
            return json.dumps(self.release).encode("utf-8")
        if command[:2] == ["gh", "api"] and "/git/ref/tags/" in command[2]:
            return json.dumps({"object": {"type": "tag", "sha": "b" * 40}}).encode("utf-8")
        if command[:2] == ["gh", "api"] and "/git/tags/" in command[2]:
            return json.dumps({"object": {"type": "commit", "sha": self.commit}}).encode("utf-8")
        if command[:3] == ["gh", "release", "download"]:
            directory = Path(command[command.index("--dir") + 1])
            for name, content in self.assets.items():
                (directory / name).write_bytes(content)
            return b""
        raise AssertionError(f"unexpected command: {command}")

    def verify(self, *, draft: bool = True) -> None:
        verify_remote_release(
            repo=self.repo,
            version=self.version,
            commit=self.commit,
            expected_assets=self.assets,
            draft=draft,
            runner=self.runner,
        )

    def test_draft_requires_exact_candidate_tag_commit_and_downloaded_bytes(self) -> None:
        self.verify()

    def test_candidate_build_requires_the_declared_exact_ref_and_manifest_status(self) -> None:
        commit = subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"], check=True, capture_output=True, text=True,
        ).stdout.strip()
        assets = candidate_assets(ROOT, "HEAD", commit, "0.1.0-alpha.13", "unreleased")
        self.assertEqual({"school-os-0.1.0-alpha.13.tar.gz", "SHA256SUMS"}, set(assets))
        with self.assertRaisesRegex(ReleaseVerificationError, "does not resolve"):
            candidate_assets(ROOT, "HEAD", "0" * 40, "0.1.0-alpha.13", "unreleased")

    def test_wrong_release_commit_fails_before_download(self) -> None:
        self.release["targetCommitish"] = "c" * 40

        with self.assertRaisesRegex(ReleaseVerificationError, "target commit"):
            self.verify()

    def test_unexpected_or_duplicate_remote_asset_fails(self) -> None:
        self.release["assets"] = [{"name": "SHA256SUMS"}]
        with self.assertRaisesRegex(ReleaseVerificationError, "missing"):
            self.verify()

        self.release["assets"] = [{"name": name} for name in self.assets]
        self.release["assets"].append({"name": "notes.txt"})

        with self.assertRaisesRegex(ReleaseVerificationError, "assets do not match"):
            self.verify()

        self.release["assets"] = [{"name": name} for name in self.assets] + [{"name": "SHA256SUMS"}]
        with self.assertRaisesRegex(ReleaseVerificationError, "duplicate"):
            self.verify()

    def test_truncated_download_fails_byte_equality(self) -> None:
        original = self.runner

        def truncated(command: list[str]) -> bytes:
            if command[:3] == ["gh", "release", "download"]:
                directory = Path(command[command.index("--dir") + 1])
                for name, content in self.assets.items():
                    (directory / name).write_bytes(content[:1])
                return b""
            return original(command)

        with self.assertRaisesRegex(ReleaseVerificationError, "bytes differ"):
            verify_remote_release(
                repo=self.repo, version=self.version, commit=self.commit,
                expected_assets=self.assets, draft=True, runner=truncated,
            )

    def test_lightweight_tag_or_mutable_published_release_fails(self) -> None:
        def lightweight(command: list[str]) -> bytes:
            if command[:2] == ["gh", "api"] and "/git/ref/tags/" in command[2]:
                return json.dumps({"object": {"type": "commit", "sha": self.commit}}).encode("utf-8")
            return self.runner(command)

        with self.assertRaisesRegex(ReleaseVerificationError, "annotated"):
            verify_remote_release(
                repo=self.repo, version=self.version, commit=self.commit,
                expected_assets=self.assets, draft=True, runner=lightweight,
            )

        self.release["isDraft"] = False
        with self.assertRaisesRegex(ReleaseVerificationError, "not immutable"):
            self.verify(draft=False)


if __name__ == "__main__":
    unittest.main()
