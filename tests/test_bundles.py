import io
import gzip
import json
import tarfile
import tempfile
import unittest
from dataclasses import replace

from school_os.bundles import (
    BundleEntry, BundleError, MANIFEST_PATH, build_bundle, read_bundle,
)
from school_os.contracts import canonical_json_bytes, sha256_bytes, validate
from school_os.install import (
    HYBRID_BOOTSTRAP_PATH, HYBRID_CURRENT_PATH, HYBRID_PACKAGE_PATH,
    HYBRID_SETTINGS_PATH, INITIAL_STATE_PATH, InstallationError,
    extract_hybrid_package, install_hybrid_generation, publish_hybrid_state,
    recover_hybrid_generation,
)
from school_os.package import inventory_bytes
from school_os.references import StoredObject
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


class HybridStorage:
    def __init__(self, lose_name=None, lose_replace=False):
        self.objects = {}
        self.creates = []
        self.reads = []
        self.lose_name = lose_name
        self.lose_replace = lose_replace
        self.replaces = 0

    def create_file(self, parent_id, name, data, mime_type):
        self.creates.append(name)
        value = StoredObject(
            f"object-{len(self.objects) + 1}", "file", parent_id, (parent_id,),
            mime_type, f"version-{len(self.objects) + 1}", name, data,
        )
        self.objects[value.object_id] = value
        if name == self.lose_name:
            self.lose_name = None
            raise OSError("synthetic lost response")
        return value

    def read(self, object_id):
        self.reads.append(object_id)
        return self.objects.get(object_id)

    def list_scoped(self, parent_id):
        return [item for item in self.objects.values() if item.parent_id == parent_id]

    def replace_file(self, object_id, parent_id, name, data, mime_type, expected_version):
        self.replaces += 1
        current = self.objects[object_id]
        if (
            current.parent_id != parent_id or current.name != name
            or current.mime_type != mime_type or current.version != expected_version
        ):
            raise InstallationError("synthetic replacement guard failed")
        written = replace(current, data=data, version=f"replacement-{self.replaces}")
        self.objects[object_id] = written
        if self.lose_replace:
            self.lose_replace = False
            raise OSError("synthetic lost replacement response")
        return written


def package_fixture():
    version = "1.2.3-alpha.1"
    payload = {"release.yaml": f"system_version: {version}\n".encode()}
    inventory = inventory_bytes(payload)
    buffer = io.BytesIO()
    with gzip.GzipFile(fileobj=buffer, mode="wb", mtime=0, filename="") as compressed:
        with tarfile.open(fileobj=compressed, mode="w", format=tarfile.USTAR_FORMAT) as archive:
            for path, data in sorted({**payload, "RELEASE-INVENTORY.sha256": inventory}.items()):
                info = tarfile.TarInfo(f"School-OS-{version}/{path}")
                info.size = len(data); info.mode = 0o644
                archive.addfile(info, io.BytesIO(data))
    data = buffer.getvalue()
    return data, {
        "version": version,
        "source_identity": {"repository": "example/repository", "commit": "1" * 40},
        "archive_sha256": sha256_bytes(data),
        "inventory_sha256": sha256_bytes(inventory),
    }


class HybridInstallTests(unittest.TestCase):
    root = {
        "object_id": "root", "kind": "folder", "permitted_ancestor_id": "root",
        "mime_type": "application/vnd.google-apps.folder", "version": "root-v1",
    }
    runtime = {
        "implementation": "CPython", "python_version": "3.12.14",
        "dependency_fingerprint": "d" * 64,
    }
    serialization = {
        "mode": "attended_single_writer",
        "evidence": {
            "actor_id": "actor-test", "attempt_id": "attempt-test",
            "scheduler_inactive": True, "competing_mutators_excluded": True,
            "observed_at": "2026-09-09T00:00:00Z",
        },
    }

    def state_entries(self):
        return {
            "state/operation-state.json": BundleEntry(
                canonical_json_bytes({"schema_version": 1, "status": "idle"}),
                "operation_state", "application/json", "operation-state.schema.json",
            ),
        }

    def install(self, storage):
        archive, package = package_fixture()
        return install_hybrid_generation(
            storage, root_reference=self.root, package=package,
            package_bytes=archive, settings_bytes=b'schema_version: 1\n',
            instance_id="instance-test", state_entries=self.state_entries(),
            configuration_fingerprint="c" * 64,
            runtime=self.runtime,
        )

    def test_install_creates_exactly_five_files_then_recovers_each_once(self):
        storage = HybridStorage()
        recovery = self.install(storage)
        self.assertEqual([
            HYBRID_PACKAGE_PATH, HYBRID_SETTINGS_PATH, INITIAL_STATE_PATH,
            HYBRID_CURRENT_PATH, HYBRID_BOOTSTRAP_PATH,
        ], storage.creates)
        self.assertEqual(5, len(storage.objects))
        self.assertEqual(5, len(storage.reads))
        self.assertEqual("instance-test", recovery["bootstrap"]["instance_id"])
        self.assertNotIn("version", recovery["bootstrap"]["current_reference"])
        self.assertEqual("version-4", recovery["current_reference"]["version"])
        self.assertIn("state/operation-state.json", recovery["state"].entries)

    def test_lost_create_response_adopts_one_exact_object_without_duplicate(self):
        storage = HybridStorage(lose_name=INITIAL_STATE_PATH)
        self.install(storage)
        self.assertEqual(5, len(storage.objects))
        self.assertEqual(1, storage.creates.count(INITIAL_STATE_PATH))

    def test_recovery_rejects_tampered_state_bytes(self):
        storage = HybridStorage()
        recovery = self.install(storage)
        state_id = recovery["current"]["state"]["bundle_reference"]["object_id"]
        storage.objects[state_id] = replace(storage.objects[state_id], data=b"tampered")
        with self.assertRaisesRegex(InstallationError, "physical bytes"):
            recover_hybrid_generation(
                storage, root_reference=self.root,
                bootstrap_reference=recovery["bootstrap_reference"],
            )

    def test_current_identity_survives_pointer_version_change(self):
        storage = HybridStorage()
        recovery = self.install(storage)
        current_id = recovery["bootstrap"]["current_reference"]["object_id"]
        storage.objects[current_id] = replace(storage.objects[current_id], version="version-new")
        reread = recover_hybrid_generation(
            storage, root_reference=self.root,
            bootstrap_reference=recovery["bootstrap_reference"],
        )
        self.assertEqual("version-new", reread["current_reference"]["version"])

    def test_successor_preserves_previous_and_recovery_follows_current(self):
        storage = HybridStorage()
        initial = self.install(storage)
        entries = self.state_entries()
        entries["data/guidelines.json"] = BundleEntry(
            canonical_json_bytes({"schema_version": 1, "guidelines": ["one"]}),
            "guidelines", "application/json",
        )
        successor = publish_hybrid_state(
            storage, recovery=initial, state_entries=entries,
            serialization=self.serialization,
        )
        self.assertEqual(2, successor["current"]["generation"])
        self.assertEqual("state-000001", successor["current"]["previous"]["identity"])
        self.assertEqual("state-000002", successor["current"]["state"]["identity"])
        self.assertEqual(6, len(storage.objects))
        recovered = recover_hybrid_generation(
            storage, root_reference=self.root,
            bootstrap_reference=successor["bootstrap_reference"],
        )
        self.assertIn("data/guidelines.json", recovered["state"].entries)

    def test_invalid_writer_evidence_blocks_before_successor_create(self):
        storage = HybridStorage()
        initial = self.install(storage)
        invalid = json.loads(json.dumps(self.serialization))
        invalid["evidence"]["scheduler_inactive"] = False
        with self.assertRaisesRegex(InstallationError, "writer exclusion"):
            publish_hybrid_state(
                storage, recovery=initial, state_entries=self.state_entries(),
                serialization=invalid,
            )
        self.assertEqual(5, len(storage.objects))

    def test_lost_pointer_response_adopts_exact_successor_without_retry(self):
        storage = HybridStorage(lose_replace=True)
        initial = self.install(storage)
        successor = publish_hybrid_state(
            storage, recovery=initial, state_entries=self.state_entries(),
            serialization=self.serialization,
        )
        self.assertEqual(1, storage.replaces)
        self.assertEqual(2, successor["current"]["generation"])

    def test_hybrid_package_extracts_only_after_admission(self):
        storage = HybridStorage()
        recovery = self.install(storage)
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "installed"
            extracted = extract_hybrid_package(recovery, destination)
            self.assertEqual(b"system_version: 1.2.3-alpha.1\n", (extracted / "release.yaml").read_bytes())
        tampered = {**recovery, "package_archive": recovery["package_archive"] + b"x"}
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(InstallationError, "hash disagrees"):
                extract_hybrid_package(tampered, Path(temporary) / "installed")


if __name__ == "__main__":
    unittest.main()
