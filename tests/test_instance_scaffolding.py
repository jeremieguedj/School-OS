from __future__ import annotations

import gzip
import json
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
from io import BytesIO
from pathlib import Path
from dataclasses import replace


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from school_os.contracts import sha256_bytes  # noqa: E402
from school_os.package import inventory_bytes  # noqa: E402
from school_os.install import (  # noqa: E402
    DAILY_REFERENCE_KINDS,
    INTEGRATION_REFERENCE_KINDS,
    InstallationError,
    MANAGED_PATHS,
    install_create_only_generation,
    recover_create_only_generation,
    scaffold_instance,
    validate_candidate,
    verify_candidate_readback,
)
from school_os.references import StoredObject  # noqa: E402


class FakeStorage:
    def __init__(self, objects: list[StoredObject]) -> None:
        self.objects = objects

    def read(self, object_id: str) -> StoredObject | None:
        return next((object_ for object_ in self.objects if object_.object_id == object_id), None)

    def list_scoped(self, parent_id: str) -> list[StoredObject]:
        return [object_ for object_ in self.objects if object_.parent_id == parent_id]


class CreateOnlyFakeStorage(FakeStorage):
    def __init__(self, *, lose_after_create: bool = False, duplicate_after_loss: bool = False) -> None:
        super().__init__([])
        self.lose_after_create = lose_after_create
        self.duplicate_after_loss = duplicate_after_loss
        self.calls: list[str] = []

    def create_file(self, parent_id: str, name: str, data: bytes, mime_type: str) -> StoredObject:
        self.calls.append(name)
        object_ = StoredObject(f"created-{len(self.objects) + 1}", "file", parent_id, (parent_id,), mime_type, str(len(self.objects) + 1), name, data)
        self.objects.append(object_)
        if self.lose_after_create:
            if self.duplicate_after_loss:
                self.objects.append(replace(object_, object_id=f"duplicate-{len(self.objects) + 1}"))
            raise OSError("lost create response")
        return object_


class InstanceScaffoldingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.package_root, self.archive = self.make_package()
        self.answers = self.make_answers()
        self.references = self.make_references()

    def make_package(self) -> tuple[Path, Path]:
        version = "0.1.0-alpha.13"
        package_root = self.base / f"School-OS-{version}"
        package_root.mkdir()
        for name in ("schemas", "core", "school_os"):
            shutil.copytree(ROOT / name, package_root / name)
        for name in ("release.yaml", "START-HERE.md"):
            shutil.copy(ROOT / name, package_root / name)
        files = {
            path.relative_to(package_root).as_posix(): path.read_bytes()
            for path in package_root.rglob("*") if path.is_file()
        }
        (package_root / "RELEASE-INVENTORY.sha256").write_bytes(inventory_bytes(files))
        archive = self.base / f"school-os-{version}.tar.gz"
        with archive.open("wb") as raw, gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w") as package:
                for path in [package_root, *sorted(package_root.rglob("*"))]:
                    relative = path.relative_to(package_root.parent).as_posix()
                    info = tarfile.TarInfo(relative)
                    info.mtime = info.uid = info.gid = 0
                    info.mode = 0o755 if path.is_dir() else 0o644
                    if path.is_dir():
                        info.type = tarfile.DIRTYPE
                        package.addfile(info)
                    else:
                        data = path.read_bytes()
                        info.size = len(data)
                        package.addfile(info, BytesIO(data))
        (self.base / "SHA256SUMS").write_text(f"{sha256_bytes(archive.read_bytes())}  {archive.name}\n", encoding="utf-8")
        return package_root, archive

    def reference(self, object_id: str, kind: str = "file") -> dict[str, str]:
        return {"object_id": object_id, "kind": kind, "permitted_ancestor_id": "instance-root", "mime_type": "application/json", "version": "1"}

    def make_references(self) -> dict:
        observed = {
            role: self.reference(f"observed-{role}", kind)
            for role, kind in {**DAILY_REFERENCE_KINDS, **INTEGRATION_REFERENCE_KINDS}.items()
        }
        returned = {path: self.reference(f"returned-{path.replace('/', '-')}") for path in MANAGED_PATHS}
        return {
            "instance_root": {"object_id": "instance-root", "kind": "folder", "permitted_ancestor_id": "instance-root", "version": "1"},
            "observed": observed,
            "returned_objects": returned,
        }

    def make_answers(self) -> dict:
        return {
            "package_root": str(self.package_root),
            "package_archive": str(self.archive),
            "package_source_identity": {"repository": "jeremieguedj/School-OS", "commit": "a" * 40},
            "instance_id": "synthetic-alpha13",
            "release_channel": "alpha",
            "household": {
                "timezone": "America/Los_Angeles",
                "entities": [
                    {"entity_id": "child_1", "display_name": "Child 1", "type": "child", "sort_order": 1},
                    {"entity_id": "household", "display_name": "Family", "type": "shared", "sort_order": 99},
                ],
                "grouping": {"canonical_scope_field": "entities", "shared_group_id": "household", "unscoped_update_group": "household"},
            },
            "integrations": {
                "runtime_adapter": "runtimes/synthetic.md", "mail_adapter": "mail/synthetic.md", "task_adapter": "tasks/synthetic.md",
                "scheduler_adapter": None, "audio_adapter": None, "task_provider_status": "not_configured",
            },
            "policies": {
                "brief": {"rolling_window_days": 7, "group_by_received_day": True, "source_links_required_for_source_backed_tasks": True},
                "tasks": {"completion_requires_parent_comment": True, "completion_comment_structure": "freeform", "reopen_when_comment_missing": True},
                "attachments": {"excluded_content_policy": "do_not_catalogue_sensitive_unrelated_content", "unsupported_outcome": "manual_review"},
                "audio": {"enabled": False, "unavailable_behavior": "disclose_optional_degradation"},
                "execution": {"max_records_per_unit": 25, "max_bytes_per_unit": 262144, "delivery_correction_policy": "explicit_authorization_required", "manual_entrypoint_authorization": "explicit_user_request_required", "serialization_mode": "attended_single_writer"},
            },
            "daily_values": {"presentation": {"brief_heading": "School updates"}},
        }

    def test_confirmed_inputs_create_byte_stable_schema_valid_candidate(self) -> None:
        first = self.base / "first"
        second = self.base / "second"
        first_manifest = scaffold_instance(self.answers, self.references, first)
        second_manifest = scaffold_instance(self.answers, self.references, second)
        self.assertEqual("candidate", first_manifest["verification_status"])
        self.assertEqual(first_manifest, second_manifest)
        self.assertEqual(
            {path.relative_to(first).as_posix(): path.read_bytes() for path in first.rglob("*") if path.is_file()},
            {path.relative_to(second).as_posix(): path.read_bytes() for path in second.rglob("*") if path.is_file()},
        )
        self.assertEqual(first_manifest, validate_candidate(first, self.package_root))
        self.assertFalse(any(b"REPLACE_WITH_" in path.read_bytes() for path in first.rglob("*") if path.is_file()))

    def test_missing_answers_fail_without_accepting_output(self) -> None:
        answers = dict(self.answers)
        del answers["daily_values"]
        output = self.base / "missing"
        with self.assertRaisesRegex(InstallationError, "daily_values"):
            scaffold_instance(answers, self.references, output)
        self.assertFalse(output.exists())

    def test_fabricated_or_unreadable_returned_reference_fails_readback(self) -> None:
        candidate = self.base / "candidate"
        manifest = scaffold_instance(self.answers, self.references, candidate)
        objects = []
        for path, record in manifest["files"].items():
            reference = record["object_reference"]
            objects.append(StoredObject(reference["object_id"], "file", "instance-root", ("instance-root",), reference.get("mime_type"), reference.get("version"), path, (candidate / path).read_bytes()))
        accepted = verify_candidate_readback(candidate, self.package_root, FakeStorage(objects))
        self.assertEqual("verified", accepted["verification_status"])
        with self.assertRaisesRegex(InstallationError, "readback"):
            verify_candidate_readback(candidate, self.package_root, FakeStorage(objects[:-1]))

    def test_cli_writes_only_the_requested_candidate(self) -> None:
        answers = self.base / "answers.json"
        references = self.base / "references.json"
        output = self.base / "cli-candidate"
        answers.write_text(json.dumps(self.answers), encoding="utf-8")
        references.write_text(json.dumps(self.references), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "scaffold_instance.py"), "--answers", str(answers), "--references", str(references), "--output", str(output)],
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("candidate:", result.stdout)
        self.assertTrue((output / "state/installation-manifest.json").is_file())

    def test_create_only_generation_has_no_self_reference_or_replace(self) -> None:
        storage = CreateOnlyFakeStorage()
        result = install_create_only_generation(
            storage,
            root_reference={"object_id": "instance-root", "kind": "folder", "permitted_ancestor_id": "instance-root", "version": "1"},
            package={"version": "0.1.0-alpha.13", "source_identity": {"repository": "example", "commit": "a" * 40}, "archive_sha256": "a" * 64, "inventory_sha256": "b" * 64},
            payloads={"instance.yaml": b"instance\n", "state/operation-state.json": b"{}\n"},
        )
        self.assertNotIn("installation_manifest_reference", result["manifest"])
        self.assertEqual("verified", result["admission"]["verification_status"])
        self.assertEqual(["instance.yaml", "state/operation-state.json", "state/installation-manifest.json", "state/installation-admission.json", "BOOTSTRAP.md"], storage.calls)

    def test_create_only_generation_adopts_one_lost_response_without_retry(self) -> None:
        storage = CreateOnlyFakeStorage(lose_after_create=True)
        result = install_create_only_generation(
            storage,
            root_reference={"object_id": "instance-root", "kind": "folder", "permitted_ancestor_id": "instance-root", "version": "1"},
            package={"version": "0.1.0-alpha.13", "source_identity": {"repository": "example", "commit": "a" * 40}, "archive_sha256": "a" * 64, "inventory_sha256": "b" * 64},
            payloads={"instance.yaml": b"instance\n"},
        )
        self.assertEqual("verified", result["admission"]["verification_status"])
        self.assertEqual(4, len(storage.calls))

    def test_create_only_generation_blocks_ambiguous_lost_response(self) -> None:
        storage = CreateOnlyFakeStorage(lose_after_create=True, duplicate_after_loss=True)
        with self.assertRaisesRegex(InstallationError, "ambiguous"):
            install_create_only_generation(
                storage,
                root_reference={"object_id": "instance-root", "kind": "folder", "permitted_ancestor_id": "instance-root", "version": "1"},
                package={"version": "0.1.0-alpha.13", "source_identity": {"repository": "example", "commit": "a" * 40}, "archive_sha256": "a" * 64, "inventory_sha256": "b" * 64},
                payloads={"instance.yaml": b"instance\n"},
            )
        self.assertEqual(["instance.yaml"], storage.calls)

    def test_fresh_bootstrap_recovery_rejects_tamper_metadata_and_incomplete_generation(self) -> None:
        root = {"object_id": "instance-root", "kind": "folder", "permitted_ancestor_id": "instance-root", "version": "1"}
        package = {"version": "0.1.0-alpha.13", "source_identity": {"repository": "example", "commit": "a" * 40}, "archive_sha256": "a" * 64, "inventory_sha256": "b" * 64}
        storage = CreateOnlyFakeStorage()
        result = install_create_only_generation(storage, root_reference=root, package=package, payloads={"instance.yaml": b"instance\n", "state/operation-state.json": b"{}\n"})
        recovered = recover_create_only_generation(storage, root_reference=root, bootstrap_reference=result["bootstrap_reference"])
        self.assertEqual(result["manifest"], recovered["manifest"])
        manifest_id = result["manifest_reference"]["object_id"]
        storage.objects = [replace(item, data=b"{}\n") if item.object_id == manifest_id else item for item in storage.objects]
        with self.assertRaisesRegex(InstallationError, "hash disagrees"):
            recover_create_only_generation(storage, root_reference=root, bootstrap_reference=result["bootstrap_reference"])

        storage = CreateOnlyFakeStorage()
        result = install_create_only_generation(storage, root_reference=root, package=package, payloads={"instance.yaml": b"instance\n"})
        instance_id = result["manifest"]["files"]["instance.yaml"]["object_reference"]["object_id"]
        storage.objects = [replace(item, data=b"changed\n") if item.object_id == instance_id else item for item in storage.objects]
        with self.assertRaisesRegex(InstallationError, "hash disagrees"):
            recover_create_only_generation(storage, root_reference=root, bootstrap_reference=result["bootstrap_reference"])

        storage = CreateOnlyFakeStorage()
        result = install_create_only_generation(storage, root_reference=root, package=package, payloads={"instance.yaml": b"instance\n"})
        instance_id = result["manifest"]["files"]["instance.yaml"]["object_reference"]["object_id"]
        storage.objects = [replace(item, mime_type="text/plain") if item.object_id == instance_id else item for item in storage.objects]
        with self.assertRaisesRegex(InstallationError, "reference failed"):
            recover_create_only_generation(storage, root_reference=root, bootstrap_reference=result["bootstrap_reference"])

        storage = CreateOnlyFakeStorage()
        result = install_create_only_generation(storage, root_reference=root, package=package, payloads={"instance.yaml": b"instance\n"})
        instance_id = result["manifest"]["files"]["instance.yaml"]["object_reference"]["object_id"]
        storage.objects = [replace(item, parent_id="outside-root", ancestor_ids=("instance-root", "outside-root")) if item.object_id == instance_id else item for item in storage.objects]
        with self.assertRaisesRegex(InstallationError, "outside the declared root"):
            recover_create_only_generation(storage, root_reference=root, bootstrap_reference=result["bootstrap_reference"])

        storage = CreateOnlyFakeStorage()
        result = install_create_only_generation(storage, root_reference=root, package=package, payloads={"instance.yaml": b"instance\n"})
        admission_id = result["admission_reference"]["object_id"]
        storage.objects = [replace(item, data=b"{}\n") if item.object_id == admission_id else item for item in storage.objects]
        with self.assertRaisesRegex(InstallationError, "admission receipt"):
            recover_create_only_generation(storage, root_reference=root, bootstrap_reference=result["bootstrap_reference"])

        incomplete = CreateOnlyFakeStorage()
        incomplete.create_file("instance-root", "instance.yaml", b"instance\n", "application/octet-stream")
        with self.assertRaisesRegex(InstallationError, "referenced object was not found"):
            recover_create_only_generation(
                incomplete, root_reference=root,
                bootstrap_reference={"object_id": "missing-bootstrap", "kind": "file", "permitted_ancestor_id": "instance-root", "mime_type": "text/markdown", "version": "1"},
            )
        self.assertFalse(hasattr(incomplete, "replace_file"))


if __name__ == "__main__":
    unittest.main()
