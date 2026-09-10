import io
import json
import tarfile
import unittest

from school_os.bundles import (
    BundleEntry, BundleError, MANIFEST_PATH, build_bundle, read_bundle,
)
from school_os.contracts import canonical_json_bytes, sha256_bytes, validate
from pathlib import Path


HASH = "a" * 64


class BundleTests(unittest.TestCase):
    def entries(self):
        return {
            "state/operation-state.json": BundleEntry(
                canonical_json_bytes({"schema_version": 1, "status": "idle"}),
                "operation_state", "application/json", "operation-state.schema.json",
            ),
            "data/guidelines.json": BundleEntry(
                canonical_json_bytes({"schema_version": 1, "guidelines": []}),
                "guidelines", "application/json",
            ),
        }

    def build(self, **overrides):
        values = {
            "bundle_kind": "state", "identity": "state-000001",
            "instance_id": "instance-test", "package_sha256": HASH,
            "settings_sha256": "b" * 64,
            "configuration_fingerprint": "c" * 64,
            "entries": self.entries(), "predecessor": None,
        }
        values.update(overrides)
        return build_bundle(**values)

    def test_round_trip_is_reproducible_and_exact(self):
        first = self.build()
        second = self.build(entries=dict(reversed(list(self.entries().items()))))
        self.assertEqual(first, second)
        verified = read_bundle(first, expected_kind="state")
        self.assertEqual(sha256_bytes(first), verified.sha256)
        self.assertEqual(
            {path: entry.data for path, entry in self.entries().items()},
            dict(verified.entries),
        )
        self.assertEqual("state-000001", verified.manifest["identity"])

    def test_manifest_matches_checked_in_schema(self):
        verified = read_bundle(self.build())
        schema = json.loads(
            (Path(__file__).resolve().parents[1] / "schemas" / "state-bundle-manifest.schema.json").read_text()
        )
        self.assertEqual([], validate(dict(verified.manifest), schema))

    def test_rejects_unsafe_paths_and_bounds(self):
        for path in ("/absolute", "../escape", "a//b", "a\\b", MANIFEST_PATH):
            with self.subTest(path=path), self.assertRaises(BundleError):
                self.build(entries={path: BundleEntry(b"x", "test", "application/octet-stream")})
        with self.assertRaisesRegex(BundleError, "member .* byte bound"):
            self.build(entries={"large": BundleEntry(b"x" * (8 * 1024 * 1024 + 1), "test", "application/octet-stream")})

    def test_rejects_tampered_member_and_nonzero_trailer(self):
        original = self.build()
        tampered = bytearray(original)
        marker = canonical_json_bytes({"schema_version": 1, "guidelines": []})
        offset = original.index(marker)
        tampered[offset] ^= 1
        with self.assertRaisesRegex(BundleError, "bytes disagree"):
            read_bundle(bytes(tampered))
        with self.assertRaisesRegex(BundleError, "trailing"):
            read_bundle(original + b"x" + b"\0" * 511)

    def test_rejects_undeclared_member_and_unsafe_tar_type(self):
        manifest = read_bundle(self.build()).manifest
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode="w", format=tarfile.USTAR_FORMAT) as archive:
            manifest_bytes = canonical_json_bytes(dict(manifest))
            info = tarfile.TarInfo(MANIFEST_PATH)
            info.size = len(manifest_bytes); info.mode = 0o644
            archive.addfile(info, io.BytesIO(manifest_bytes))
            link = tarfile.TarInfo("unexpected")
            link.type = tarfile.SYMTYPE; link.linkname = "target"; link.mode = 0o644
            archive.addfile(link)
        with self.assertRaises(BundleError):
            read_bundle(buffer.getvalue())

    def test_predecessor_is_bound(self):
        value = read_bundle(self.build(
            identity="state-000002",
            predecessor={"identity": "state-000001", "sha256": "d" * 64},
        ))
        self.assertEqual("state-000001", value.manifest["predecessor"]["identity"])


if __name__ == "__main__":
    unittest.main()
