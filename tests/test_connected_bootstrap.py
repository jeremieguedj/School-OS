from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from school_os.codex_bridge import CAPTURED_HOST_CAPABILITIES, HOST_BINDINGS, BridgeError, HostBindingDispatcher, JsonlPeer, create_run_directory
from school_os.connected_bootstrap import BootstrapDocument, BootstrapError, RecoveredEntrypoint, installed_command, recover_installed_entrypoint
from school_os.connected_storage import CodexDriveReferenceStorage, ConnectedStorageError
from school_os.package import INVENTORY_NAME, inventory_bytes, verify_extracted_tree


class FakeDrive:
    def __init__(self) -> None:
        self.objects = {
            "root": {"id": "root", "mime_type": "application/vnd.google-apps.folder", "parent_ids": ["test-parent"], "modified_time": "root-v1", "size": 0, "url": "https://example.invalid/root", "title": "root"},
            "bootstrap": {"id": "bootstrap", "mime_type": "text/markdown", "parent_ids": ["root"], "modified_time": "v1", "size": 4, "url": "https://example.invalid/bootstrap", "title": "BOOTSTRAP.md"},
        }

    def metadata(self, object_id: str, *, fields: str):
        return dict(self.objects[object_id])

    def fetch(self, url: str, *, raw: bool, include_base64: bool):
        if url != self.objects["bootstrap"]["url"]:
            raise AssertionError("unexpected fetch URL")
        return {"id": "bootstrap", "b64_string": "dGVzdA==", "file_size_bytes": 4, "is_empty": False}

    def list_folder(self, url: str, *, top_k: int):
        return {"complete": True, "files": [dict(self.objects["bootstrap"])]}


class ConnectedBootstrapTests(unittest.TestCase):
    def test_reference_storage_requires_exact_bytes_and_complete_listing(self) -> None:
        drive = FakeDrive()
        storage = CodexDriveReferenceStorage(drive, expected_urls={"bootstrap": "https://example.invalid/bootstrap"})
        artifact = storage.read("bootstrap")
        self.assertEqual(b"test", artifact.data)
        self.assertEqual("root", artifact.parent_id)
        self.assertEqual(["bootstrap"], [item.object_id for item in storage.list_scoped("root")])
        drive.list_folder = lambda *_args, **_kwargs: {"files": []}  # type: ignore[method-assign]
        with self.assertRaisesRegex(ConnectedStorageError, "complete"):
            storage.list_scoped("root")
        drive.objects["bootstrap"]["url"] = "https://example.invalid/substituted"
        with self.assertRaisesRegex(ConnectedStorageError, "URL"):
            storage.read("bootstrap")

    def test_bootstrap_document_is_exact_root_and_markdown_admission(self) -> None:
        valid = {
            "root_reference": {"object_id": "root", "kind": "folder", "permitted_ancestor_id": "root", "mime_type": "application/vnd.google-apps.folder", "version": "root-v1"},
            "bootstrap_reference": {"object_id": "bootstrap", "kind": "file", "permitted_ancestor_id": "root", "mime_type": "text/markdown", "version": "v1"},
            "bootstrap_url": "https://example.invalid/bootstrap",
        }
        self.assertEqual("bootstrap", BootstrapDocument.from_mapping(valid).bootstrap_reference["object_id"])
        invalid = {**valid, "extra": True}
        with self.assertRaisesRegex(BootstrapError, "exactly"):
            BootstrapDocument.from_mapping(invalid)
        invalid = {**valid, "bootstrap_url": "file:///tmp/bootstrap"}
        with self.assertRaisesRegex(BootstrapError, "HTTPS"):
            BootstrapDocument.from_mapping(invalid)
        invalid = {**valid, "bootstrap_url": "http://example.invalid/bootstrap"}
        with self.assertRaisesRegex(BootstrapError, "HTTPS"):
            BootstrapDocument.from_mapping(invalid)
        invalid = {**valid, "root_reference": {**valid["root_reference"], "mime_type": "text/plain"}}
        with self.assertRaisesRegex(BootstrapError, "Drive folder"):
            BootstrapDocument.from_mapping(invalid)

    def test_dispatcher_has_exact_contracts_and_no_arbitrary_tool(self) -> None:
        dispatcher = HostBindingDispatcher()
        calls: list[tuple[str, dict[str, object]]] = []
        metadata = {"id": "f", "mime_type": "text/plain", "url": "https://example.invalid/f", "title": "f", "parent_ids": ["root"], "modified_time": "v1", "size": 1}
        self.assertEqual(metadata, dispatcher.dispatch("drive.get_metadata", {"fileId": "f"}, lambda tool, args: calls.append((tool, args)) or metadata))
        self.assertEqual("mcp__codex_apps__google_drive_get_file_metadata", calls[0][0])
        with self.assertRaisesRegex(BridgeError, "result.mime_type"):
            dispatcher.dispatch("drive.get_metadata", {"fileId": "f"}, lambda *_: {"id": "f"})
        evidence = {"file_uri": "relative.txt", "file_sha256": "0" * 64, "file_size_bytes": 0}
        with self.assertRaisesRegex(BridgeError, "absolute"):
            dispatcher.dispatch("drive.upload_file", evidence, lambda *_: {})
        with self.assertRaisesRegex(BridgeError, "unexpected"):
            dispatcher.dispatch("tools.execute", {}, lambda *_: {})

    def test_dispatcher_confines_drive_write_and_rechecks_child_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run = Path(temporary) / "bridge"; run.mkdir(mode=0o700)
            payload = run / "payload"; payload.write_bytes(b"private bytes"); payload.chmod(0o600)
            dispatcher = HostBindingDispatcher(run)
            evidence = {"file_uri": str(payload.resolve(strict=True)), "file_sha256": __import__("hashlib").sha256(b"private bytes").hexdigest(), "file_size_bytes": 13}
            written = {"success": True, "id": "new", "mime_type": "text/plain", "url": "https://example.invalid/new", "parent_ids": ["root"], "modified_time": "v2"}
            self.assertEqual(written, dispatcher.dispatch("drive.upload_file", {**evidence, "file_name": "payload", "mime_type": "text/plain", "parent_folder_id": "root"}, lambda *_: written))
            with self.assertRaisesRegex(BridgeError, "identity, size, or hash"):
                dispatcher.dispatch("drive.upload_file", {**evidence, "file_sha256": "0" * 64, "file_name": "payload", "mime_type": "text/plain", "parent_folder_id": "root"}, lambda *_: written)
            alias = run / "alias"; alias.symlink_to(payload)
            with self.assertRaisesRegex(BridgeError, "escapes|symlink"):
                dispatcher.dispatch("drive.upload_file", {**evidence, "file_uri": str(alias), "file_name": "alias", "mime_type": "text/plain", "parent_folder_id": "root"}, lambda *_: written)
            escaped = {**evidence, "file_uri": "/etc/hosts"}
            with self.assertRaisesRegex(BridgeError, "escapes"):
                dispatcher.dispatch("drive.upload_file", {**escaped, "file_name": "hosts", "mime_type": "text/plain", "parent_folder_id": "root"}, lambda *_: written)

    def test_every_host_binding_is_captured_and_uses_advertised_sheet_comment_names(self) -> None:
        provider_bindings = {binding.tool_name for binding in HOST_BINDINGS.values() if binding.tool_name.startswith("mcp__")}
        self.assertTrue(provider_bindings <= CAPTURED_HOST_CAPABILITIES)
        self.assertEqual("mcp__codex_apps__google_drive_get_spreadsheet_metadata", HOST_BINDINGS["sheets.get_metadata"].tool_name)
        self.assertEqual("mcp__codex_apps__google_drive_get_spreadsheet_comments", HOST_BINDINGS["comments.read_spreadsheet"].tool_name)
        self.assertEqual("mcp__codex_apps__google_drive_bulk_update_file_comments", HOST_BINDINGS["comments.write_file"].tool_name)

    def test_connected_storage_failure_is_reported_as_bootstrap_error(self) -> None:
        document = BootstrapDocument.from_mapping({
            "root_reference": {"object_id": "root", "kind": "folder", "permitted_ancestor_id": "root", "mime_type": "application/vnd.google-apps.folder", "version": "v1"},
            "bootstrap_reference": {"object_id": "bootstrap", "kind": "file", "permitted_ancestor_id": "root", "mime_type": "text/markdown", "version": "v1"},
            "bootstrap_url": "https://example.invalid/bootstrap",
        })
        class FailingStorage:
            def read(self, _object_id):
                raise ConnectedStorageError("metadata disappeared")
            def list_scoped(self, _parent_id):
                raise AssertionError("must not list")
        with tempfile.TemporaryDirectory() as temporary, self.assertRaisesRegex(BootstrapError, "admitted package recovery"):
            recover_installed_entrypoint(FailingStorage(), document, run_directory=Path(temporary), operation_id="op-1")

    def test_document_mode_does_not_require_ambient_profile(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run = Path(temporary) / "run"; run.mkdir(mode=0o700)
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "run_operation.py"), "--instance", "i", "--operation", "daily-run", "--entrypoint", "manual", "--host-jsonl", str(run), "--bootstrap-document", str(run / "missing.json"), "--operation-id", "op-1", "--attempt-id", "attempt-1"],
                text=True, capture_output=True, check=False,
            )
            self.assertEqual(1, result.returncode)
            self.assertIn("cannot read bootstrap document", result.stderr)
            self.assertNotIn("--profile", result.stderr)

    def test_installed_entrypoint_runs_from_package_without_git_or_ambient_import(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            release = base / "release"
            built = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_release.py"), "--repo", str(ROOT), "--ref", "HEAD", "--version", "0.1.0-alpha.13", "--output-dir", str(release)],
                text=True, capture_output=True, check=False,
            )
            self.assertEqual(0, built.returncode, built.stderr)
            with tarfile.open(release / "school-os-0.1.0-alpha.13.tar.gz", "r:gz") as archive:
                archive.extractall(base)
            installed = base / "School-OS-0.1.0-alpha.13"
            shutil.copy(ROOT / "scripts" / "run_connected_operation.py", installed / "scripts" / "run_connected_operation.py")
            files = {path.relative_to(installed).as_posix(): path.read_bytes() for path in installed.rglob("*") if path.is_file() and path.name != INVENTORY_NAME}
            (installed / INVENTORY_NAME).write_bytes(inventory_bytes(files))
            self.assertFalse((installed / ".git").exists())
            run_directory = base / "run"; run_directory.mkdir(mode=0o700)
            result = subprocess.run(
                [sys.executable, str(installed / "scripts" / "run_connected_operation.py"), "--installed-root", str(installed), "--operation", "daily-run", "--entrypoint", "manual", "--operation-id", "op-1", "--attempt-id", "attempt-1", "--run-directory", str(run_directory), "--instance-reference", "instance-1", "--verify-only"],
                cwd=base, env={"PATH": ""}, text=True, capture_output=True, check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual("INSTALLED_ENTRYPOINT_VERIFIED", json.loads(result.stdout)["outcome"])
            self.assertEqual(verify_extracted_tree(installed).version, "0.1.0-alpha.13")

    def test_handoff_command_removes_ambient_python_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run = Path(temporary); entrypoint = run / "run_connected_operation.py"; entrypoint.write_text("", encoding="utf-8")
            recovered = RecoveredEntrypoint(run, entrypoint, {})
            with mock.patch.dict("os.environ", {"PYTHONPATH": "ambient", "PYTHONHOME": "ambient"}, clear=False):
                _, command, environment = installed_command(recovered, operation="daily-run", entrypoint="manual", operation_id="op-1", attempt_id="attempt-1", run_directory=run, instance_reference="instance-1")
            self.assertEqual(str(entrypoint), command[1])
            self.assertNotIn("PYTHONPATH", environment)
            self.assertNotIn("PYTHONHOME", environment)


if __name__ == "__main__":
    unittest.main()
