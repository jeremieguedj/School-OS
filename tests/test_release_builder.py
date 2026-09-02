from __future__ import annotations

import hashlib
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_release import INVENTORY_NAME, build_release, verify_release_archive  # noqa: E402


class ReleaseBuilderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name) / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        subprocess.run(["git", "-C", str(self.repo), "config", "user.name", "Synthetic Tester"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "config", "user.email", "synthetic@example.invalid"], check=True)
        (self.repo / "release.yaml").write_text("system_version: 1.2.3-alpha.1\nstatus: unreleased\n", encoding="utf-8")
        (self.repo / "README.md").write_text("# Synthetic package\n", encoding="utf-8")
        nested = self.repo / "core" / "operations"
        nested.mkdir(parents=True)
        (nested / "run.md").write_text("Synthetic operation.\n", encoding="utf-8")
        (self.repo / "school-os-old.tar.gz").write_bytes(b"excluded artifact")
        (self.repo / "SHA256SUMS").write_text("excluded artifact\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(self.repo), "add", "."], check=True)
        subprocess.run(["git", "-C", str(self.repo), "commit", "-qm", "synthetic fixture"], check=True)

    def build(self, directory: str):
        return build_release(self.repo, "HEAD", "1.2.3-alpha.1", Path(self.temporary.name) / directory)

    def test_repeated_builds_are_byte_identical(self) -> None:
        first, first_sums, _ = self.build("one")
        second, second_sums, _ = self.build("two")
        self.assertEqual(first.read_bytes(), second.read_bytes())
        self.assertEqual(first_sums.read_bytes(), second_sums.read_bytes())

    def test_archive_paths_are_safe_and_have_one_root(self) -> None:
        archive, _sums, _ = self.build("safe")
        with tarfile.open(archive, "r:gz") as package:
            for member in package.getmembers():
                path = PurePosixPath(member.name)
                self.assertFalse(path.is_absolute())
                self.assertNotIn("..", path.parts)
                self.assertEqual("School-OS-1.2.3-alpha.1", path.parts[0])
                self.assertNotIn(".git", path.parts)
                self.assertNotEqual("school-os-old.tar.gz", path.name)
                self.assertNotEqual("SHA256SUMS", path.name)

    def test_inventory_is_complete_and_checksums_every_payload_file(self) -> None:
        archive, _sums, _ = self.build("inventory")
        with tarfile.open(archive, "r:gz") as package:
            files = {
                PurePosixPath(*PurePosixPath(member.name).parts[1:]).as_posix(): package.extractfile(member).read()
                for member in package.getmembers()
                if member.isfile()
            }
        inventory = files.pop(INVENTORY_NAME).decode("utf-8").splitlines()
        expected = [f"{hashlib.sha256(data).hexdigest()}  {path}" for path, data in sorted(files.items())]
        self.assertEqual(expected, inventory)

    def test_sha256sums_covers_archive_and_full_verifier_passes(self) -> None:
        archive, sums, _ = self.build("checksum")
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        self.assertEqual(f"{digest}  {archive.name}\n", sums.read_text(encoding="utf-8"))
        self.assertEqual([], verify_release_archive(archive, sums, "1.2.3-alpha.1"))

    def test_unreleased_manifest_is_packageable(self) -> None:
        archive, sums, _ = self.build("unreleased")
        self.assertTrue(archive.is_file())
        self.assertTrue(sums.is_file())


if __name__ == "__main__":
    unittest.main()
