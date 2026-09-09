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
            "root": {"id": "root", "mime_type": "application/vnd.google-apps.folder", "parent_ids": ["test-parent"], "modified_time": "root-v1", "size": 0, "url": "https://example.invalid/root", "title": "root", "data": None},
            "bootstrap": {"id": "bootstrap", "mime_type": "text/markdown", "parent_ids": ["root"], "modified_time": "v1", "size": 4, "url": "https://example.invalid/bootstrap", "title": "BOOTSTRAP.md", "data": b"test"},
        }
        self.search_pages = None
        self.search_calls = []

    def metadata(self, object_id: str, *, fields: str):
        return dict(self.objects[object_id])

    def fetch(self, url: str, *, raw: bool, include_base64: bool):
        item = next(item for item in self.objects.values() if item["url"] == url)
        data = item["data"]
        return {"id": item["id"], "b64_string": __import__("base64").b64encode(data).decode("ascii"), "file_size_bytes": len(data), "is_empty": not data}

    def search_page(self, parent_id: str, *, item_type: str, topn: int, page_token: str | None = None):
        self.search_calls.append((parent_id, item_type, topn, page_token))
        if self.search_pages is not None:
            return self.search_pages[(item_type, page_token)]
        values = []
        for item in self.objects.values():
            if item["parent_ids"] != [parent_id]:
                continue
            observed_type = (
                "folder" if item["mime_type"] == "application/vnd.google-apps.folder"
                else "image" if item["mime_type"].startswith("image/") else "document"
            )
            if observed_type == item_type:
                values.append({key: item[key] for key in ("id", "title", "mime_type", "url", "parent_ids")})
        return {"results": values, "next_page_token": None}


class ConnectedBootstrapTests(unittest.TestCase):
    @staticmethod
    def _tool_result(result: object) -> dict[str, object]:
        return {"structuredContent": {"result": result}}

    def test_reference_storage_requires_exact_bytes_and_complete_listing(self) -> None:
        drive = FakeDrive()
        storage = CodexDriveReferenceStorage(drive, expected_urls={"bootstrap": "https://example.invalid/bootstrap"})
        artifact = storage.read("bootstrap")
        self.assertEqual(b"test", artifact.data)
        self.assertEqual("root", artifact.parent_id)
        self.assertEqual(["bootstrap"], [item.object_id for item in storage.list_scoped("root")])
        drive.objects["bootstrap"]["url"] = "https://example.invalid/substituted"
        with self.assertRaisesRegex(ConnectedStorageError, "URL"):
            storage.read("bootstrap")

    def test_reference_storage_accepts_only_google_drivesdk_suffix_for_same_object(self) -> None:
        drive = FakeDrive()
        drive.objects["bootstrap"]["url"] = "https://drive.example.invalid/file/d/bootstrap/view"
        with mock.patch("school_os.connected_storage._GOOGLE_DRIVE_HOSTS", frozenset({"drive.example.invalid"})):
            storage = CodexDriveReferenceStorage(
                drive,
                expected_urls={"bootstrap": "https://drive.example.invalid/file/d/bootstrap/view?usp=drivesdk"},
            )
            self.assertEqual(b"test", storage.read("bootstrap").data)

            for expected in (
                "https://drive.example.invalid/file/d/wrong-bootstrap/view?usp=drivesdk",
                "https://docs.example.invalid/file/d/bootstrap/view?usp=drivesdk",
                "https://drive.example.invalid/file/d/bootstrap/view?resourcekey=changed",
            ):
                with self.subTest(expected=expected), self.assertRaisesRegex(ConnectedStorageError, "URL"):
                    CodexDriveReferenceStorage(drive, expected_urls={"bootstrap": expected}).read("bootstrap")

    def test_reference_storage_observed_empty_search_exhausts_every_category(self) -> None:
        drive = FakeDrive()
        del drive.objects["bootstrap"]
        self.assertEqual([], CodexDriveReferenceStorage(drive).list_scoped("root"))
        self.assertEqual(
            [("root", item_type, 1000, None) for item_type in ("document", "image", "folder")],
            drive.search_calls,
        )

    def test_reference_storage_paginates_documents_images_and_folders(self) -> None:
        drive = FakeDrive()
        drive.objects.update({
            "second": {"id": "second", "mime_type": "application/pdf", "parent_ids": ["root"], "modified_time": "v1", "size": 3, "url": "https://example.invalid/second", "title": "second.pdf", "data": b"pdf"},
            "image": {"id": "image", "mime_type": "image/png", "parent_ids": ["root"], "modified_time": "v1", "size": 3, "url": "https://example.invalid/image", "title": "image.png", "data": b"png"},
            "folder": {"id": "folder", "mime_type": "application/vnd.google-apps.folder", "parent_ids": ["root"], "modified_time": "v1", "size": 0, "url": "https://example.invalid/folder", "title": "folder", "data": None},
        })
        listed = lambda identifier: {key: drive.objects[identifier][key] for key in ("id", "title", "mime_type", "url", "parent_ids")}
        drive.search_pages = {
            ("document", None): {"results": [listed("bootstrap")], "next_page_token": "documents-2"},
            ("document", "documents-2"): {"results": [listed("second")], "next_page_token": None},
            ("image", None): {"results": [listed("image")], "next_page_token": None},
            ("folder", None): {"results": [listed("folder")], "next_page_token": None},
        }
        result = CodexDriveReferenceStorage(drive).list_scoped("root")
        self.assertEqual(["bootstrap", "second", "image", "folder"], [item.object_id for item in result])
        self.assertIn(("root", "document", 1000, "documents-2"), drive.search_calls)

    def test_reference_storage_rejects_repeated_or_unknown_continuation(self) -> None:
        drive = FakeDrive()
        drive.search_pages = {
            ("document", None): {"results": [], "next_page_token": "repeat"},
            ("document", "repeat"): {"results": [], "next_page_token": "repeat"},
        }
        with self.assertRaisesRegex(ConnectedStorageError, "continuation"):
            CodexDriveReferenceStorage(drive).list_scoped("root")

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
        self.assertEqual(metadata, dispatcher.dispatch("drive.get_metadata", {"fileId": "f"}, lambda tool, args: calls.append((tool, args)) or self._tool_result(metadata)))
        self.assertEqual("mcp__codex_apps__google_drive_get_file_metadata", calls[0][0])
        with self.assertRaisesRegex(BridgeError, "result.mime_type"):
            dispatcher.dispatch("drive.get_metadata", {"fileId": "f"}, lambda *_: self._tool_result({"id": "f"}))
        evidence = {"file_uri": "relative.txt", "file_sha256": "0" * 64, "file_size_bytes": 0}
        with self.assertRaisesRegex(BridgeError, "absolute"):
            dispatcher.dispatch("drive.upload_file", evidence, lambda *_: self._tool_result({}))
        with self.assertRaisesRegex(BridgeError, "unexpected"):
            dispatcher.dispatch("tools.execute", {}, lambda *_: self._tool_result({}))

    def test_dispatcher_maps_scoped_page_to_advertised_drive_search(self) -> None:
        dispatcher = HostBindingDispatcher()
        calls: list[tuple[str, dict[str, object]]] = []
        page = {"results": [], "next_page_token": None}
        result = dispatcher.dispatch(
            "drive.search_page",
            {"parent_id": "folder_1", "item_type": "document", "topn": 1000},
            lambda tool, args: calls.append((tool, dict(args))) or self._tool_result(page),
        )
        self.assertEqual(page, result)
        self.assertEqual("mcp__codex_apps__google_drive_search", calls[0][0])
        self.assertEqual({
            "special_filter_query_str": "'folder_1' in parents and trashed = false",
            "item_type": "document", "topn": 1000,
        }, calls[0][1])
        dispatcher.dispatch(
            "drive.search_page",
            {"parent_id": "folder_1", "item_type": "document", "topn": 1000, "page_token": "opaque-2"},
            lambda tool, args: calls.append((tool, dict(args))) or self._tool_result(page),
        )
        self.assertEqual("opaque-2", calls[1][1]["page_token"])
        with self.assertRaisesRegex(BridgeError, "unsupported page shape"):
            dispatcher.dispatch(
                "drive.search_page",
                {"parent_id": "folder_1", "item_type": "folder", "topn": 1000},
                lambda *_: self._tool_result({"files": []}),
            )
        invoked: list[bool] = []
        with self.assertRaisesRegex(BridgeError, "advertised paginated category"):
            dispatcher.dispatch(
                "drive.search_page",
                {"parent_id": "folder_1", "item_type": "all", "topn": 1000},
                lambda *_: invoked.append(True) or self._tool_result(page),
            )
        self.assertEqual([], invoked)

    def test_dispatcher_confines_drive_write_and_rechecks_child_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run = Path(temporary) / "bridge"; run.mkdir(mode=0o700)
            payload = run / "payload"; payload.write_bytes(b"private bytes"); payload.chmod(0o600)
            dispatcher = HostBindingDispatcher(run)
            evidence = {"file_uri": str(payload.resolve(strict=True)), "file_sha256": __import__("hashlib").sha256(b"private bytes").hexdigest(), "file_size_bytes": 13}
            written = {"success": True, "id": "new", "mime_type": "text/plain", "url": "https://example.invalid/new", "parent_id": "root"}
            native_calls: list[dict[str, object]] = []
            def consume(_tool, arguments):
                native_calls.append(arguments)
                payload.write_bytes(b"changed after admission")
                payload.chmod(0o600)
                self.assertEqual(b"private bytes", Path(arguments["file_uri"]).read_bytes())
                self.assertNotIn("file_sha256", arguments)
                self.assertNotIn("file_size_bytes", arguments)
                return self._tool_result(written)
            self.assertEqual(written, dispatcher.dispatch("drive.upload_file", {**evidence, "file_name": "payload", "mime_type": "text/plain", "parent_folder_id": "root"}, consume))
            self.assertEqual(1, len(native_calls))
            self.assertNotEqual(evidence["file_uri"], native_calls[0]["file_uri"])
            self.assertFalse(Path(native_calls[0]["file_uri"]).exists())
            payload.write_bytes(b"private bytes"); payload.chmod(0o600)
            with self.assertRaisesRegex(BridgeError, "identity, size, or hash"):
                dispatcher.dispatch("drive.upload_file", {**evidence, "file_sha256": "0" * 64, "file_name": "payload", "mime_type": "text/plain", "parent_folder_id": "root"}, lambda *_: self._tool_result(written))
            alias = run / "alias"; alias.symlink_to(payload)
            with self.assertRaisesRegex(BridgeError, "escapes|symlink"):
                dispatcher.dispatch("drive.upload_file", {**evidence, "file_uri": str(alias), "file_name": "alias", "mime_type": "text/plain", "parent_folder_id": "root"}, lambda *_: self._tool_result(written))
            escaped = {**evidence, "file_uri": "/etc/hosts"}
            with self.assertRaisesRegex(BridgeError, "escapes"):
                dispatcher.dispatch("drive.upload_file", {**escaped, "file_name": "hosts", "mime_type": "text/plain", "parent_folder_id": "root"}, lambda *_: self._tool_result(written))

    def test_advertised_native_request_and_result_shapes_are_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run = Path(temporary) / "bridge"; run.mkdir(mode=0o700)
            payload = run / "payload"; payload.write_bytes(b"payload"); payload.chmod(0o600)
            image = run / "image"; image.write_bytes(b"image"); image.chmod(0o600)
            evidence = {"file_uri": str(payload.resolve(strict=True)), "file_sha256": __import__("hashlib").sha256(b"payload").hexdigest(), "file_size_bytes": 7}
            dispatcher = HostBindingDispatcher(run)
            metadata = {"id": "file", "mime_type": "text/plain", "url": "https://example.invalid/file", "title": "file", "parent_ids": ["root"], "modified_time": "v1", "size": "7"}
            self.assertEqual(7, dispatcher.dispatch("drive.get_metadata", {"fileId": "file"}, lambda *_: self._tool_result(metadata))["size"])
            seen: list[dict[str, object]] = []
            updated = {"success": True, "id": "file", "mime_type": "text/plain", "url": "https://example.invalid/file", "modified_time": "v2", "parent_ids": ["new-parent"], "size": "7"}
            dispatcher.dispatch("drive.update_file", {"fileId": "file", **evidence, "mime_type": "text/plain", "addParents": "new-parent"}, lambda _tool, args: seen.append(args) or self._tool_result(updated))
            self.assertEqual("new-parent", seen[0]["addParents"])
            self.assertEqual({"fileId", "file_uri", "mime_type", "addParents"}, set(seen[0]))
            delivered = dispatcher.dispatch("gmail.send", {"to": "tester@example.invalid", "subject": "Subject", "payload": {"mime_type": "text/plain", "body": {"content": "hello"}}}, lambda *_: self._tool_result({"id": "message"}))
            self.assertEqual("message", delivered["id"])
            images: list[dict[str, object]] = []
            dispatcher.dispatch("sheets.batch_update", {"spreadsheet_id": "sheet", "requests": [{"addSheet": {"properties": {"title": "X"}}}], "image_uris": str(image.resolve(strict=True))}, lambda _tool, args: images.append(args) or self._tool_result({"spreadsheetId": "sheet", "replies": []}))
            self.assertNotEqual(str(image.resolve(strict=True)), images[0]["image_uris"])
            self.assertFalse(Path(images[0]["image_uris"]).exists())

    def test_child_ports_roundtrip_through_actual_host_dispatcher(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run = Path(temporary) / "bridge"; run.mkdir(mode=0o700)
            process = subprocess.Popen(
                [sys.executable, str(ROOT / "tests" / "support" / "host_roundtrip_child.py"), str(run)],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, bufsize=1,
            )
            self.addCleanup(lambda: process.poll() is None and process.kill())
            native_results = {
                "drive.get_metadata": {"id": "file-1", "mime_type": "text/plain", "url": "https://example.invalid/file-1", "title": "file-1", "parent_ids": ["root"], "modified_time": "v1", "size": "4"},
                "gmail.send": {"id": "message-1", "snippet": "sent"},
                "gmail.read_attachment": {"message_id": "message-1", "attachment_id": "attachment-1", "file_uri": {"download_url": "https://example.invalid/attachment-1", "mime_type": "application/pdf"}},
                "sheets.batch_update": {"spreadsheetId": "sheet-1", "replies": []},
                "comments.write_file": {"fileId": "sheet-1", "created_comments": [{"id": "comment-1", "content": "Exact note"}], "created_replies": [], "resolved_comments": [], "total_operations": 1},
            }
            observed: list[tuple[str, dict[str, object]]] = []
            dispatcher = HostBindingDispatcher(run)
            for _ in native_results:
                line = process.stdout.readline().strip() if process.stdout is not None else ""
                fields = line.split(" ", 4)
                self.assertEqual("SCHOOL_OS_REQUEST", fields[0], line)
                _, request_id, kind, digest, request_path = fields
                control = dispatcher.dispatch_request_file(
                    request_id=request_id, kind=kind, request_sha256=digest,
                    request_path=Path(request_path),
                    invoke=lambda tool, args, kind=kind: observed.append((tool, dict(args))) or self._tool_result(native_results[kind]),
                )
                assert process.stdin is not None
                process.stdin.write(json.dumps(control) + "\n"); process.stdin.flush()
            final = process.stdout.readline() if process.stdout is not None else ""
            stderr = process.stderr.read() if process.stderr is not None else ""
            self.assertEqual(0, process.wait(timeout=10), stderr)
            if process.stdin is not None:
                process.stdin.close()
            if process.stdout is not None:
                process.stdout.close()
            if process.stderr is not None:
                process.stderr.close()
            results = json.loads(final)
            self.assertEqual("file-1", results["drive"]["id"])
            self.assertEqual("message-1", results["gmail"]["id"])
            self.assertEqual("attachment-1", results["attachment"]["attachment_id"])
            self.assertEqual("sheet-1", results["sheets"]["spreadsheetId"])
            self.assertEqual("comment-1", results["comment"]["created_comments"][0]["id"])
            self.assertEqual(
                [HOST_BINDINGS[kind].tool_name for kind in native_results],
                [tool for tool, _args in observed],
            )

    def test_advertised_gmail_and_comment_shapes_are_strict(self) -> None:
        dispatcher = HostBindingDispatcher()
        gmail_args = {
            "to": "student@example.invalid", "subject": "Subject",
            "payload": {"mime_type": "text/plain", "body": {"content": "hello"}},
            "classification_label_values": [{"label_id": "label-1", "fields": [{"field_id": "field-1", "selection": "choice-1"}]}],
            "response_fields": ["id", "snippet", "history_id", "internal_date", "payload", "size_estimate", "classification_label_values"],
        }
        self.assertEqual("message", dispatcher.dispatch("gmail.send", gmail_args, lambda *_: self._tool_result({"id": "message", "snippet": "sent"}))["id"])
        with self.assertRaisesRegex(BridgeError, "unadvertised"):
            dispatcher.dispatch("gmail.send", {**gmail_args, "response_fields": ["raw"]}, lambda *_: self._tool_result({"id": "message"}))
        invoked: list[bool] = []
        with self.assertRaisesRegex(BridgeError, "invalid shape"):
            dispatcher.dispatch("comments.write_file", {"id": "file", "comments": [{"bogus": 1}]}, lambda *_: invoked.append(True) or self._tool_result({}))
        self.assertEqual([], invoked)
        with self.assertRaisesRegex(BridgeError, "created_comments"):
            dispatcher.dispatch("comments.write_file", {"id": "file", "comments": [{"content": "note"}]}, lambda *_: self._tool_result({}))

    def test_malformed_native_requests_block_before_invocation(self) -> None:
        dispatcher = HostBindingDispatcher()
        invoked: list[str] = []
        for kind, arguments in (
            ("drive.get_metadata", {"fileId": "file", "fields": 7}),
            ("gmail.read_attachment", {"message_id": "message"}),
            ("comments.write_file", {}),
        ):
            with self.assertRaises(BridgeError):
                dispatcher.dispatch(kind, arguments, lambda *_: invoked.append(kind) or self._tool_result({}))
        self.assertEqual([], invoked)

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
