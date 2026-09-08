from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from school_os.contracts import load_mapping

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

    def test_candidate_build_follows_the_exact_committed_manifest_identity(self) -> None:
        commit = subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"], check=True, capture_output=True, text=True,
        ).stdout.strip()
        manifest = load_mapping(ROOT / "release.yaml")
        version = manifest["system_version"]
        status = manifest["status"]
        self.assertIn(status, {"unreleased", "released"})
        assets = candidate_assets(ROOT, "HEAD", commit, version, status)
        self.assertEqual({f"school-os-{version}.tar.gz", "SHA256SUMS"}, set(assets))
        with self.assertRaisesRegex(ReleaseVerificationError, "does not resolve"):
            candidate_assets(ROOT, "HEAD", "0" * 40, version, status)
        other_status = "released" if status == "unreleased" else "unreleased"
        with self.assertRaisesRegex(ReleaseVerificationError, "manifest status"):
            candidate_assets(ROOT, "HEAD", commit, version, other_status)

    def test_released_synthetic_candidate_cannot_be_verified_as_unreleased(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            repo.mkdir()
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.name", "Synthetic Tester"], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.email", "synthetic@example.invalid"], check=True)
            (repo / "release.yaml").write_text("system_version: 1.2.3-alpha.1\nstatus: released\n", encoding="utf-8")
            (repo / "README.md").write_text("# Synthetic package\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
            subprocess.run(["git", "-C", str(repo), "commit", "-qm", "released fixture"], check=True)
            commit = subprocess.run(
                ["git", "-C", str(repo), "rev-parse", "HEAD"], check=True, capture_output=True, text=True,
            ).stdout.strip()
            self.assertEqual(
                {"school-os-1.2.3-alpha.1.tar.gz", "SHA256SUMS"},
                set(candidate_assets(repo, "HEAD", commit, "1.2.3-alpha.1", "released")),
            )
            with self.assertRaisesRegex(ReleaseVerificationError, "manifest status"):
                candidate_assets(repo, "HEAD", commit, "1.2.3-alpha.1", "unreleased")

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
