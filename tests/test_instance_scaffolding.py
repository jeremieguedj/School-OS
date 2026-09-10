from __future__ import annotations

import gzip
import base64
import hashlib
import json
import pickle
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

from school_os.contracts import canonical_json_bytes, sha256_bytes  # noqa: E402
from school_os.bundles import BundleEntry, member_reference  # noqa: E402
from school_os.package import inventory_bytes  # noqa: E402
from school_os.install import (  # noqa: E402
    DAILY_REFERENCE_KINDS,
    INTEGRATION_REFERENCE_KINDS,
    InstallationError,
    MANAGED_PATHS,
    OPERATION_STATE_PATH,
    PACKAGE_ARCHIVE_PATH,
    PACKAGE_CHECKSUMS_PATH,
    compose_create_only_candidate_payloads,
    extract_recovered_package,
    initial_operation_state_bytes,
    install_create_only_generation,
    publish_hybrid_content_bundle,
    recover_hybrid_generation,
    recover_create_only_generation,
    scaffold_instance,
    validate_candidate,
    verify_candidate_readback,
)
from school_os.references import StoredObject  # noqa: E402
from school_os.connected_setup import (  # noqa: E402
    bind_hybrid_task_projection,
    CodexDriveCreateOnlyStorage,
    FOLDER_MIME,
    SETUP_FILE_ROLES,
    compose_hybrid_connected_inputs,
    install_hybrid_connected_instance,
    install_connected_instance,
)
from school_os.connected_sheets import GoogleSheetsScope  # noqa: E402
from school_os.connected_daily import (  # noqa: E402
    ConnectedDailyRuntime, REQUIRED_CAPABILITIES, readmit_connected_profile,
    resolve_hybrid_instance,
)
from school_os.daily import PHASES  # noqa: E402
from school_os.hybrid_operations import HybridCheckpointPublisher  # noqa: E402
from school_os.operations import checkpoint_pointer  # noqa: E402


TEST_ARCHIVE = b"synthetic admitted release archive"
TEST_ARCHIVE_SHA = sha256_bytes(TEST_ARCHIVE)
TEST_CHECKSUMS = f"{TEST_ARCHIVE_SHA}  synthetic-release.archive\n".encode("utf-8")
PACKAGE_PAYLOADS = {PACKAGE_ARCHIVE_PATH: TEST_ARCHIVE, PACKAGE_CHECKSUMS_PATH: TEST_CHECKSUMS}


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


class ConnectedSetupDrive:
    def __init__(self) -> None:
        self.sequence = 1
        self.objects = {
            "instance-root": {
                "id": "instance-root", "title": "School-OS", "mime_type": "application/vnd.google-apps.folder",
                "parent_ids": [], "modified_time": "1", "url": "https://drive.example.invalid/instance-root", "data": None,
            }
        }

    def metadata(self, file_id: str, *, fields: str):
        item = self.objects[file_id]
        result = {key: item[key] for key in ("id", "title", "mime_type", "parent_ids", "modified_time", "url")}
        if item["data"] is not None:
            result["size"] = len(item["data"])
        return result

    def fetch(self, url: str, *, raw: bool, include_base64: bool):
        item = next(value for value in self.objects.values() if value["url"] == url)
        data = item["data"]
        return {
            "id": item["id"], "b64_string": base64.b64encode(data).decode("ascii"),
            "file_size_bytes": len(data), "is_empty": not data,
        }

    def search_page(self, parent_id: str, *, item_type: str, topn: int, page_token: str | None = None):
        if page_token is not None:
            raise AssertionError("synthetic setup listing has one page per type")
        files = [
            {"id": item["id"], "title": item["title"], "mime_type": item["mime_type"],
             "url": item["url"], "parent_ids": item["parent_ids"]}
            for item in self.objects.values()
            if item["parent_ids"] == [parent_id] and (
                "folder" if item["mime_type"] == "application/vnd.google-apps.folder"
                else "image" if item["mime_type"].startswith("image/") else "document"
            ) == item_type
        ]
        return {"results": files, "next_page_token": None}

    def upload(self, file_uri: str, *, file_name: str, mime_type: str, parent_folder_id: str):
        self.sequence += 1
        identifier = f"created-{self.sequence}"
        data = Path(file_uri).read_bytes()
        item = {
            "id": identifier, "title": file_name, "mime_type": mime_type,
            "parent_ids": [parent_folder_id], "modified_time": str(self.sequence),
            "url": f"https://drive.example.invalid/{identifier}", "data": data,
        }
        self.objects[identifier] = item
        return {"success": True, "id": identifier, "mime_type": mime_type, "parent_id": parent_folder_id, "url": item["url"]}

    def create_folder(self, name: str, parent_folder: str):
        self.sequence += 1
        identifier = f"created-{self.sequence}"
        item = {
            "id": identifier, "title": name, "mime_type": "application/vnd.google-apps.folder",
            "parent_ids": [parent_folder], "modified_time": str(self.sequence),
            "url": f"https://drive.example.invalid/{identifier}", "data": None,
        }
        self.objects[identifier] = item
        return {"success": True, "id": identifier, "parent_id": parent_folder, "title": name, "url": item["url"]}

    def update(self, file_id: str, *, file_uri: str, mime_type: str):
        self.sequence += 1
        item = self.objects[file_id]
        item["data"] = Path(file_uri).read_bytes()
        item["mime_type"] = mime_type
        item["modified_time"] = str(self.sequence)
        return {
            "success": True, "id": file_id, "mime_type": mime_type,
            "parent_id": item["parent_ids"][0], "url": item["url"],
            "modified_time": item["modified_time"],
        }


class ConnectedSetupSheets:
    def __init__(self, scope: GoogleSheetsScope) -> None:
        self.scope = scope
        self.headers: list[str] | None = None
        self.grid: list[list[str | None]] = [
            [None] * (scope.last_column - scope.first_column + 1)
            for _ in range(scope.last_row - scope.first_row + 1)
        ]

    def metadata(self, **arguments):
        return {
            "spreadsheetId": self.scope.spreadsheet_id,
            "sheets": [{"properties": {"sheetId": self.scope.sheet_id, "title": self.scope.sheet_title}}],
        }

    def cells(self, **arguments):
        last = max((index for index, row in enumerate(self.grid) if any(value is not None for value in row)), default=-1)
        row_data = [{"values": [
            {} if value is None else {"formattedValue": value, "userEnteredValue": {"stringValue": value}}
            for value in row
        ]} for row in self.grid[:last + 1]]
        return {
            "spreadsheetId": self.scope.spreadsheet_id,
            "sheets": [{
                "properties": {"sheetId": self.scope.sheet_id, "title": self.scope.sheet_title},
                "data": [{
                    "startRow": self.scope.first_row - 1,
                    "startColumn": self.scope.first_column - 1,
                    "rowData": row_data,
                }],
            }],
        }

    def batch_update(self, **arguments):
        for request in arguments["requests"]:
            update = request["updateCells"]
            target = update["range"]
            start_row = target["startRowIndex"] - (self.scope.first_row - 1)
            start_column = target["startColumnIndex"] - (self.scope.first_column - 1)
            for row_offset, row in enumerate(update["rows"]):
                for column_offset, value in enumerate(row["values"]):
                    self.grid[start_row + row_offset][start_column + column_offset] = value["userEnteredValue"]["stringValue"]
        if all(isinstance(value, str) and value for value in self.grid[0]):
            self.headers = list(self.grid[0])
        return {"spreadsheetId": self.scope.spreadsheet_id}

    def all_comments(self, **arguments):
        return ()


class ConnectedRuntimeGmail:
    def __init__(self, *, source_enabled: bool = False) -> None:
        self.peer = object()
        self.messages: dict[str, bytes] = {}
        self.send_count = 0
        self.source_enabled = source_enabled
        self.source_body = "Return the signed form."
        transport = base64.b64encode(self.source_body.encode("utf-8"))
        self.source_raw = (
            b"Content-Type: text/plain; charset=utf-8\r\n"
            b"Content-Transfer-Encoding: base64\r\n\r\n" + transport
        )
        self.source_full = {
            "id": "source-message-1", "thread_id": "source-thread-1",
            "internal_date": "1788854400000",
            "payload": {
                "part_id": "", "mime_type": "text/plain", "filename": "",
                "headers": [
                    {"name": "Content-Type", "value": 'text/plain; charset="utf-8"'},
                    {"name": "Content-Transfer-Encoding", "value": "base64"},
                ],
                "body": {"size": len(self.source_body.encode("utf-8")), "base64_url_content": None, "content": self.source_body, "attachment_id": None},
                "read_attachment_supported": None, "parts": None,
            },
        }

    def search_ids(self, **arguments):
        if arguments["query"].startswith("in:sent"):
            return {"message_ids": list(self.messages), "next_page_token": None}
        return {"message_ids": ["source-message-1"] if self.source_enabled else [], "next_page_token": None}

    def send(self, request):
        self.send_count += 1
        identifier = f"sent-{self.send_count}"
        text, html = request["payload"]["parts"]
        headers = [f'To: {request["to"]}']
        if "cc" in request:
            headers.append(f'Cc: {request["cc"]}')
        if "bcc" in request:
            headers.append(f'Bcc: {request["bcc"]}')
        headers.extend([
            f'Subject: {request["subject"]}', 'MIME-Version: 1.0',
            'Content-Type: multipart/alternative; boundary="school-os-test"', '',
        ])
        parts = []
        for mime_type, content in (("text/plain", text["body"]["content"]), ("text/html", html["body"]["content"])):
            parts.extend([
                "--school-os-test", f"Content-Type: {mime_type}; charset=utf-8",
                "Content-Transfer-Encoding: base64", "",
                base64.b64encode(content.encode("utf-8")).decode("ascii"),
            ])
        parts.extend(["--school-os-test--", ""])
        self.messages[identifier] = ("\r\n".join([*headers, *parts])).encode("ascii")
        return {"id": identifier, "thread_id": identifier, "label_ids": ["SENT"]}

    def read(self, message_id: str, format: str):
        if message_id == "source-message-1":
            if format == "full":
                return dict(self.source_full)
            return {
                "id": message_id, "thread_id": "source-thread-1",
                "raw": base64.urlsafe_b64encode(self.source_raw).decode("ascii").rstrip("="),
            }
        data = self.messages[message_id]
        return {
            "id": message_id, "thread_id": message_id, "label_ids": ["SENT"],
            "raw": base64.urlsafe_b64encode(data).decode("ascii").rstrip("="),
        }

    def read_thread(self, thread_id: str, *, max_messages: int):
        return {"id": thread_id, "messages": [dict(self.source_full)]}


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

    def make_connected_observed(self, profile: dict | None = None) -> dict:
        observed = {
            role: {"name": f"observed/{role}.json", "data": b"{}\n", "mime_type": "application/json"}
            for role in SETUP_FILE_ROLES
        }
        values = {
            "source_scope": {"schema_version": 1, "adapter_id": "gmail-v1", "query": "from:school newer_than:14d", "label_ids": ["INBOX"], "max_results": 100, "max_thread_messages": 100},
            "delivery_configuration": {"schema_version": 1, "variant": "manual-test", "to": ["parent@example.invalid"], "cc": [], "bcc": [], "subject_prefix": "School updates"},
            "canonical_action_register": {"schema_version": 1, "tasks": []},
            "task_sync_state": {"provider_id": "sheet-1", "adapter_id": "google-sheets-v1", "provider_revision": None, "bindings": [], "cursor": None, "cursor_evidence": {}, "verified_readback": {}},
            "source_checkpoint": {"schema_version": 1, "eligible_cursor": None},
            "source_catalog_index": {"schema_version": 1, "records": []},
            "guidelines": {"schema_version": 1, "guidelines": []},
            "rolling_updates": {"schema_version": 1, "rolling_updates": []},
            "delivery_state": {"schema_version": 1, "deliveries": {}, "effects": {}},
            "final_run_checkpoint": {"schema_version": 1, "last_run": None},
            "brief_template": {"version": "test-v1", "html": "<html>{{BRIEF_CONTENT}}</html>", "text": "{{BRIEF_CONTENT}}", "placeholders": {"BRIEF_CONTENT": {"kind": "content"}}},
        }
        for role, value in values.items():
            observed[role]["data"] = json.dumps(value, sort_keys=True, separators=(",", ":")).encode() + b"\n"
        observed["runtime_profile"]["data"] = canonical_json_bytes(profile) if profile is not None else (ROOT / "templates" / "state" / "capability-profile.json").read_bytes()
        return observed

    def make_connected_profile(self) -> dict:
        profile = json.loads((ROOT / "templates" / "state" / "capability-profile.json").read_text(encoding="utf-8"))
        profile.update({
            "profile_id": "connected-test", "runtime_adapter": "runtimes/codex.md",
            "execution_surface": "manual", "evidence_class": "synthetic",
            "runtime_selector": {"model": "test", "reasoning_effort": "none"},
            "selected_adapters": {"mail": "mail/gmail.md", "tasks": "tasks/google-sheets.md", "scheduler": None, "audio": None},
            "verified_at": "2026-09-08T12:00:00Z",
            "adapter_versions": {"runtime": "1", "mail": "1", "tasks": "1", "scheduler": None},
            "authentication": {"status": "available", "verified_at": "2026-09-08T12:00:00Z", "recheck_trigger": "test"},
            "network_paths": {name: {"status": "available" if name != "scheduler" else "not_required"} for name in ("storage", "mail", "tasks", "scheduler")},
            "observations": {name: {"status": "available"} for name in ("local_execution", "storage_read_complete", "pagination", "file_transfer")},
            "limits": {"max_records_per_unit": 10, "max_bytes_per_unit": 262144},
            "capabilities": [
                {"capability_id": name, "status": "available", "verification": {"synthetic": True}, "degradation": "stop"}
                for name in REQUIRED_CAPABILITIES
            ],
            "scheduler_behavior": None, "conformant_operations": ["daily-run"],
        })
        return profile

    def make_scheduled_profile(self) -> dict:
        profile = self.make_connected_profile()
        profile.update({
            "profile_id": "connected-scheduled-test",
            "execution_surface": "scheduled", "evidence_class": "observed",
            "selected_adapters": {**profile["selected_adapters"], "scheduler": "schedulers/test.md"},
            "adapter_versions": {**profile["adapter_versions"], "scheduler": "1"},
            "network_paths": {**profile["network_paths"], "scheduler": {"status": "available"}},
            "scheduler_behavior": {"verified": True},
        })
        profile["capabilities"] += [
            {"capability_id": name, "status": "available", "verification": {"observed": True}, "degradation": "stop"}
            for name in ("scheduler.inspect", "scheduler.verify")
        ]
        return profile

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

        manifest_path = first / "state/installation-manifest.json"
        tampered = json.loads(manifest_path.read_text())
        tampered["package"]["archive_reference"] = self.reference("unadmitted-archive")
        manifest_path.write_text(json.dumps(tampered), encoding="utf-8")
        with self.assertRaisesRegex(InstallationError, "archive_reference disagrees"):
            validate_candidate(first, self.package_root)

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
            package={"version": "0.1.0-alpha.13", "source_identity": {"repository": "example", "commit": "a" * 40}, "archive_sha256": TEST_ARCHIVE_SHA, "inventory_sha256": "b" * 64},
            payloads={**PACKAGE_PAYLOADS,"instance.yaml": b"instance\n", "state/operation-state.json": b"{}\n"},
        )
        self.assertNotIn("installation_manifest_reference", result["manifest"])
        self.assertEqual("verified", result["admission"]["verification_status"])
        self.assertEqual(["instance.yaml", "state/operation-state.json", PACKAGE_CHECKSUMS_PATH, PACKAGE_ARCHIVE_PATH, "state/installation-manifest.json", "state/installation-admission.json", "BOOTSTRAP.md"], storage.calls)

    def test_connected_setup_proves_empty_root_initializes_headers_and_installs(self) -> None:
        scope = GoogleSheetsScope(
            "sheet-1", "https://sheets.example.invalid/sheet-1", 7, "Tasks",
            1, 20, 1, 13,
        )
        drive = ConnectedSetupDrive()
        sheets = ConnectedSetupSheets(scope)
        observed = self.make_connected_observed()
        root = {
            "object_id": "instance-root", "kind": "folder",
            "permitted_ancestor_id": "instance-root", "mime_type": "application/vnd.google-apps.folder", "version": "1",
        }
        result = install_connected_instance(
            storage=CodexDriveCreateOnlyStorage(drive, scratch_directory=self.base / "scratch"),
            sheets=sheets, root_reference=root, answers=self.answers,
            observed_payloads=observed, sheet_scope=scope,
        )
        self.assertTrue(result["root_initially_empty"])
        self.assertEqual(13, len(sheets.headers or []))
        self.assertIn("bootstrap_reference", result["bootstrap_document"])
        created_names = {item["title"] for item in drive.objects.values()}
        self.assertTrue(set(MANAGED_PATHS) <= created_names)
        self.assertIn("source-catalog", created_names)
        self.assertIn("operation-checkpoints", created_names)

    def test_hybrid_setup_collapses_seed_objects_into_settings_and_state(self) -> None:
        package, archive, settings, entries, fingerprint = compose_hybrid_connected_inputs(
            self.answers, self.make_connected_observed(),
        )
        self.assertEqual(self.archive.read_bytes(), archive)
        self.assertEqual(sha256_bytes(archive), package["archive_sha256"])
        self.assertIn(b'instance_id: "synthetic-alpha13"', settings)
        self.assertIn("state/operation-state.json", entries)
        self.assertIn("state/task-provider-selector.json", entries)
        self.assertNotIn("source_scope", entries)
        selector = json.loads(entries["state/task-provider-selector.json"].data)
        self.assertEqual("unbound", selector["status"])
        self.assertEqual(2, selector["schema_version"])
        self.assertIsNone(selector["switch"])
        self.assertEqual(64, len(fingerprint))

    def test_hybrid_connected_install_writes_only_five_files_before_projection(self) -> None:
        drive = ConnectedSetupDrive()
        storage = CodexDriveCreateOnlyStorage(
            drive, scratch_directory=self.base / "hybrid-scratch",
        )
        root = {
            "object_id": "instance-root", "kind": "folder",
            "permitted_ancestor_id": "instance-root", "mime_type": FOLDER_MIME,
            "version": "1",
        }
        result = install_hybrid_connected_instance(
            storage=storage, root_reference=root, answers=self.answers,
            observed_payloads=self.make_connected_observed(),
            runtime={
                "implementation": "CPython", "python_version": "3.12.14",
                "dependency_fingerprint": "d" * 64,
            },
        )
        children = [
            item for item in drive.objects.values()
            if item["parent_ids"] == ["instance-root"]
        ]
        self.assertEqual(5, len(children))
        self.assertEqual({
            "BOOTSTRAP.json", "CURRENT.json", "package.tar.gz",
            "settings.yaml", "state-000001.bundle",
        }, {item["title"] for item in children})
        self.assertEqual("unbound", result["projection_status"])
        self.assertEqual("application/json", result["bootstrap_document"]["bootstrap_reference"]["mime_type"])

    def test_hybrid_agent_projection_binding_is_post_admission_generation_two(self) -> None:
        drive = ConnectedSetupDrive()
        storage = CodexDriveCreateOnlyStorage(
            drive, scratch_directory=self.base / "hybrid-bind-scratch",
        )
        root = {
            "object_id": "instance-root", "kind": "folder",
            "permitted_ancestor_id": "instance-root", "mime_type": FOLDER_MIME,
            "version": "1",
        }
        installed = install_hybrid_connected_instance(
            storage=storage, root_reference=root, answers=self.answers,
            observed_payloads=self.make_connected_observed(),
            runtime={
                "implementation": "CPython", "python_version": "3.12.14",
                "dependency_fingerprint": "d" * 64,
            },
        )
        binding = {
            "provider_key": "google_sheets", "provider_id": "sheet-1",
            "adapter_id": "user-agent-sheet-v1", "binding_id": "binding-1",
            "scope_sha256": "e" * 64,
        }
        snapshot = {
            "schema_version": 1, "contract_version": "agent-task-v1",
            "request_id": "bind-read-1", "provider_id": "sheet-1",
            "adapter_id": "user-agent-sheet-v1", "binding_id": "binding-1",
            "scope_sha256": "e" * 64, "capture_id": "capture-1",
            "captured_at": "2026-09-09T00:00:00Z", "complete": True,
            "collections": [{"name": "tasks", "complete": True, "next_page_token": None, "item_count": 0}],
            "tasks": [], "unbound_candidates": [], "proposed_cursor": None,
            "evidence": {"private_receipt_sha256": "f" * 64},
        }
        result = bind_hybrid_task_projection(
            storage=storage, root_reference=root,
            bootstrap_reference=installed["bootstrap_document"]["bootstrap_reference"],
            binding=binding, snapshot=snapshot,
            adapter_configuration=canonical_json_bytes({"private_layout": "agent-owned"}),
            package_root=self.package_root,
            serialization={
                "mode": "attended_single_writer",
                "evidence": {
                    "actor_id": "setup-test", "attempt_id": "bind-1",
                    "scheduler_inactive": True,
                    "competing_mutators_excluded": True,
                    "observed_at": "2026-09-09T00:00:00Z",
                },
            },
        )
        self.assertEqual("bound", result["projection_status"])
        recovered = recover_hybrid_generation(
            storage, root_reference=root,
            bootstrap_reference=installed["bootstrap_document"]["bootstrap_reference"],
        )
        self.assertEqual(2, recovered["current"]["generation"])
        selector = json.loads(recovered["state"].entries["state/task-provider-selector.json"])
        self.assertEqual("google_sheets", selector["selected_provider"])
        self.assertEqual("active", selector["bindings"]["google_sheets"]["status"])
        self.assertEqual("sheet-1", selector["bindings"]["google_sheets"]["provider_id"])
        resolved = resolve_hybrid_instance(
            package_root=self.package_root, recovery=recovered,
            entrypoint="manual",
        )
        self.assertEqual("sheet-1", resolved.task_binding["provider_id"])
        self.assertEqual("manual", resolved.profile["execution_surface"])
        self.assertEqual(
            "data/canonical-tasks.json", resolved.file_map["canonical_action_register"],
        )
        checkpoint = {
            "schema_version": 1, "checkpoint_id": "op-1-checkpoint-0000",
            "operation_id": "op-1", "attempt_id": "attempt-1",
            "pinned_release": {
                "version": resolved.instance["system_version"],
                "source_commit": "a" * 40,
            },
            "scope": {"entrypoint": "manual"},
            "configuration_fingerprint": resolved.configuration_fingerprint,
            "phase": "preflight", "completed_phases": ["preflight"],
            "completed_units": [], "remaining_work": {}, "artifacts": [],
            "effects": [], "verification": {"phase_output": {"verified": True}},
            "blocker": None, "predecessor": None, "sequence": 0,
        }
        operation_state = {
            "schema_version": 1, "status": "running",
            "current_operation": {"operation_id": "op-1", "attempt_id": "attempt-1"},
            "serialization": {
                "mode": "attended_single_writer",
                "evidence": {"entrypoint": "manual"},
            },
            "checkpoint": checkpoint_pointer(checkpoint), "last_terminal": None,
        }
        committed = HybridCheckpointPublisher(
            resolved.state,
            state_schema=json.loads((self.package_root / "schemas" / "operation-state.schema.json").read_text()),
            checkpoint_schema=json.loads((self.package_root / "schemas" / "operation-checkpoint.schema.json").read_text()),
        ).commit(
            storage=storage, checkpoint=checkpoint, operation_state=operation_state,
            serialization={
                "mode": "attended_single_writer",
                "evidence": {
                    "actor_id": "setup-test", "attempt_id": "attempt-1",
                    "scheduler_inactive": True,
                    "competing_mutators_excluded": True,
                    "observed_at": "2026-09-09T00:00:01Z",
                },
            },
        )
        self.assertEqual(3, committed.transaction.working.recovery["current"]["generation"])
        self.assertNotIn("object_id", committed.checkpoint_peer.as_mapping())
        self.assertEqual(
            committed.checkpoint_reference.bundle_sha256,
            committed.operation_state_reference.bundle_sha256,
        )
        source = publish_hybrid_content_bundle(
            storage, recovery=committed.transaction.working.recovery,
            bundle_kind="source", identity="source-batch-000001",
            entries={
                "sources/thread-1/body.txt": BundleEntry(
                    b"complete source body", "source_body", "text/plain",
                ),
            },
        )
        source_body = member_reference(
            source["bundle_reference"], source["bundle"],
            "sources/thread-1/body.txt",
        )
        index = canonical_json_bytes({
            "records": [{
                "fact_ids": [], "record_id": "thread-1",
                "record_sha256": sha256_bytes(b"complete source body"),
                "source_members": {"body": source_body.as_mapping()},
            }],
            "schema_version": 2,
        })
        catalog_transaction = committed.transaction.stage(
            "data/source-catalog-index.json", index,
        )
        catalog_peer = catalog_transaction.read("data/source-catalog-index.json").reference
        catalog_checkpoint = {
            **checkpoint,
            "checkpoint_id": "op-1-checkpoint-0001", "phase": "catalog",
            "completed_phases": ["preflight", "discover", "catalog"],
            "predecessor": checkpoint_pointer(checkpoint), "sequence": 1,
            "verification": {
                "phase_output": {
                    "catalog_index": catalog_peer.as_mapping(),
                    "phase_complete": True, "verified": True,
                },
            },
        }
        catalog_state = {
            **operation_state, "checkpoint": checkpoint_pointer(catalog_checkpoint),
        }
        adopted = HybridCheckpointPublisher(
            catalog_transaction,
            state_schema=json.loads((self.package_root / "schemas" / "operation-state.schema.json").read_text()),
            checkpoint_schema=json.loads((self.package_root / "schemas" / "operation-checkpoint.schema.json").read_text()),
        ).commit(
            storage=storage, checkpoint=catalog_checkpoint,
            operation_state=catalog_state,
            serialization={
                "mode": "attended_single_writer",
                "evidence": {
                    "actor_id": "setup-test", "attempt_id": "attempt-1",
                    "scheduler_inactive": True,
                    "competing_mutators_excluded": True,
                    "observed_at": "2026-09-09T00:00:02Z",
                },
            },
        )
        self.assertEqual(4, adopted.transaction.working.recovery["current"]["generation"])
        canonical_index = json.loads(adopted.transaction.read("data/source-catalog-index.json").data)
        self.assertEqual(
            source["bundle_sha256"],
            canonical_index["records"][0]["source_members"]["body"]["bundle_sha256"],
        )

    def test_hybrid_agent_binding_failure_leaves_unbound_generation_active(self) -> None:
        drive = ConnectedSetupDrive()
        storage = CodexDriveCreateOnlyStorage(
            drive, scratch_directory=self.base / "hybrid-bind-failure-scratch",
        )
        root = {
            "object_id": "instance-root", "kind": "folder",
            "permitted_ancestor_id": "instance-root", "mime_type": FOLDER_MIME,
            "version": "1",
        }
        installed = install_hybrid_connected_instance(
            storage=storage, root_reference=root, answers=self.answers,
            observed_payloads=self.make_connected_observed(),
            runtime={
                "implementation": "CPython", "python_version": "3.12.14",
                "dependency_fingerprint": "d" * 64,
            },
        )
        def fail_update(*_args, **_kwargs):
            raise OSError("simulated lost pointer response")

        drive.update = fail_update
        with self.assertRaisesRegex(InstallationError, "pointer update outcome is unknown"):
            bind_hybrid_task_projection(
                storage=storage, root_reference=root,
                bootstrap_reference=installed["bootstrap_document"]["bootstrap_reference"],
                binding={
                    "provider_key": "google_sheets", "provider_id": "sheet-1",
                    "adapter_id": "user-agent-sheet-v1", "binding_id": "binding-1",
                    "scope_sha256": "e" * 64,
                },
                snapshot={
                    "schema_version": 1, "contract_version": "agent-task-v1",
                    "request_id": "bind-read-1", "provider_id": "sheet-1",
                    "adapter_id": "user-agent-sheet-v1", "binding_id": "binding-1",
                    "scope_sha256": "e" * 64, "capture_id": "capture-1",
                    "captured_at": "2026-09-09T00:00:00Z", "complete": True,
                    "collections": [{"name": "tasks", "complete": True, "next_page_token": None, "item_count": 0}],
                    "tasks": [], "unbound_candidates": [], "proposed_cursor": None,
                    "evidence": {"private_receipt_sha256": "f" * 64},
                },
                adapter_configuration=canonical_json_bytes({"private_layout": "agent-owned"}),
                package_root=self.package_root,
                serialization={
                    "mode": "attended_single_writer",
                    "evidence": {
                        "actor_id": "setup-test", "attempt_id": "bind-1",
                        "scheduler_inactive": True,
                        "competing_mutators_excluded": True,
                        "observed_at": "2026-09-09T00:00:00Z",
                    },
                },
            )
        recovered = recover_hybrid_generation(
            storage, root_reference=root,
            bootstrap_reference=installed["bootstrap_document"]["bootstrap_reference"],
        )
        self.assertEqual(1, recovered["current"]["generation"])
        selector = json.loads(recovered["state"].entries["state/task-provider-selector.json"])
        self.assertEqual("unbound", selector["status"])

    def test_connected_create_adopts_exact_id_when_receipt_omits_url(self) -> None:
        drive = ConnectedSetupDrive()
        original_upload = drive.upload

        def incomplete_upload(*args, **kwargs):
            result = original_upload(*args, **kwargs)
            result.pop("url")
            return result

        drive.upload = incomplete_upload
        storage = CodexDriveCreateOnlyStorage(
            drive, scratch_directory=self.base / "scratch",
        )
        created = storage.create_file(
            "instance-root", "state/example.json", b"{}\n", "application/json",
        )
        self.assertEqual("state/example.json", created.name)
        self.assertEqual(b"{}\n", created.data)

    def test_connected_create_admits_only_byte_proven_archive_mime_equivalents(self) -> None:
        archive = gzip.compress(b"pinned release archive")
        for observed_mime in (
            "application/octet-stream", "application/gzip", "application/x-gzip",
        ):
            with self.subTest(observed_mime=observed_mime):
                drive = ConnectedSetupDrive()
                original_upload = drive.upload

                def normalized_upload(*args, _observed=observed_mime, **kwargs):
                    result = original_upload(*args, **kwargs)
                    result["mime_type"] = _observed
                    drive.objects[result["id"]]["mime_type"] = _observed
                    return result

                drive.upload = normalized_upload
                created = CodexDriveCreateOnlyStorage(
                    drive, scratch_directory=self.base / f"scratch-{observed_mime.rsplit('/', 1)[-1]}",
                ).create_file(
                    "instance-root", PACKAGE_ARCHIVE_PATH, archive,
                    "application/octet-stream",
                )
                self.assertEqual(observed_mime, created.mime_type)
                self.assertEqual(archive, created.data)

        drive = ConnectedSetupDrive()
        original_upload = drive.upload

        def invalid_normalization(*args, **kwargs):
            result = original_upload(*args, **kwargs)
            result["mime_type"] = "text/plain"
            drive.objects[result["id"]]["mime_type"] = "text/plain"
            return result

        drive.upload = invalid_normalization
        with self.assertRaisesRegex(InstallationError, "readback mismatch: MIME"):
            CodexDriveCreateOnlyStorage(
                drive, scratch_directory=self.base / "scratch-invalid-mime",
            ).create_file(
                "instance-root", PACKAGE_ARCHIVE_PATH, archive,
                "application/octet-stream",
            )
        with self.assertRaisesRegex(InstallationError, "gzip signature"):
            CodexDriveCreateOnlyStorage(
                ConnectedSetupDrive(), scratch_directory=self.base / "scratch-invalid-bytes",
            ).create_file(
                "instance-root", PACKAGE_ARCHIVE_PATH, b"not gzip",
                "application/octet-stream",
            )

    def test_connected_create_names_the_exact_failed_readback_property(self) -> None:
        drive = ConnectedSetupDrive()
        original_upload = drive.upload

        def renamed_upload(*args, **kwargs):
            result = original_upload(*args, **kwargs)
            drive.objects[result["id"]]["title"] = "different.json"
            return result

        drive.upload = renamed_upload
        with self.assertRaisesRegex(InstallationError, "readback mismatch: name"):
            CodexDriveCreateOnlyStorage(
                drive, scratch_directory=self.base / "scratch-renamed",
            ).create_file(
                "instance-root", "state/example.json", b"{}\n", "application/json",
            )

    def test_connected_setup_refuses_nonempty_root_before_sheet_write(self) -> None:
        scope = GoogleSheetsScope(
            "sheet-1", "https://sheets.example.invalid/sheet-1", 7, "Tasks",
            1, 20, 1, 13,
        )
        drive = ConnectedSetupDrive()
        drive.uploaded = drive.upload(
            str(self.archive), file_name="existing", mime_type="application/octet-stream",
            parent_folder_id="instance-root",
        )
        sheets = ConnectedSetupSheets(scope)
        root = {
            "object_id": "instance-root", "kind": "folder",
            "permitted_ancestor_id": "instance-root", "mime_type": "application/vnd.google-apps.folder", "version": "1",
        }
        with self.assertRaisesRegex(InstallationError, "not initially empty"):
            install_connected_instance(
                storage=CodexDriveCreateOnlyStorage(drive, scratch_directory=self.base / "scratch"),
                sheets=sheets, root_reference=root, answers=self.answers,
                observed_payloads={}, sheet_scope=scope,
            )
        self.assertIsNone(sheets.headers)

    def test_connected_runtime_executes_all_seven_phases_and_commits_cursor_last(self) -> None:
        profile = self.make_connected_profile()
        scope = GoogleSheetsScope(
            "sheet-1", "https://sheets.example.invalid/sheet-1", 7, "Tasks",
            1, 20, 1, 13,
        )
        drive = ConnectedSetupDrive()
        sheets = ConnectedSetupSheets(scope)
        storage = CodexDriveCreateOnlyStorage(drive, scratch_directory=self.base / "setup-scratch")
        root = {
            "object_id": "instance-root", "kind": "folder",
            "permitted_ancestor_id": "instance-root", "mime_type": "application/vnd.google-apps.folder", "version": "1",
        }
        installed = install_connected_instance(
            storage=storage, sheets=sheets, root_reference=root, answers=self.answers,
            observed_payloads=self.make_connected_observed(profile), sheet_scope=scope,
        )
        recovery = recover_create_only_generation(
            storage, root_reference=root,
            bootstrap_reference=installed["bootstrap_document"]["bootstrap_reference"],
        )
        run_directory = self.base / "connected-run"
        run_directory.mkdir(mode=0o700)
        gmail = ConnectedRuntimeGmail()
        class UnusedSemantic:
            def interpret(self, _packet):
                raise AssertionError("zero-hit run must not interpret")
            def audit(self, _packet, _interpretation):
                raise AssertionError("zero-hit run must not audit")
        result = ConnectedDailyRuntime(
            installed_root=self.package_root, recovery=recovery,
            run_directory=run_directory, drive=drive, gmail=gmail,
            sheets=sheets, semantic=UnusedSemantic(),
        ).run(entrypoint="manual", operation_id="connected-zero-hit", attempt_id="attempt-1")
        self.assertEqual("COMPLETE", result.outcome)
        self.assertEqual(tuple(PHASES), result.completed_phases)
        self.assertEqual(1, gmail.send_count)
        final_item = next(item for item in drive.objects.values() if item["title"] == "observed/final_run_checkpoint.json")
        cursor_item = next(item for item in drive.objects.values() if item["title"] == "observed/source_checkpoint.json")
        self.assertLess(int(final_item["modified_time"]), int(cursor_item["modified_time"]))

    def test_connected_preview_renders_and_commits_without_reserving_or_sending(self) -> None:
        profile = self.make_connected_profile()
        scope = GoogleSheetsScope(
            "sheet-1", "https://sheets.example.invalid/sheet-1", 7, "Tasks",
            1, 20, 1, 13,
        )
        drive = ConnectedSetupDrive()
        sheets = ConnectedSetupSheets(scope)
        storage = CodexDriveCreateOnlyStorage(drive, scratch_directory=self.base / "preview-setup")
        root = {
            "object_id": "instance-root", "kind": "folder",
            "permitted_ancestor_id": "instance-root",
            "mime_type": "application/vnd.google-apps.folder", "version": "1",
        }
        installed = install_connected_instance(
            storage=storage, sheets=sheets, root_reference=root, answers=self.answers,
            observed_payloads=self.make_connected_observed(profile), sheet_scope=scope,
        )
        recovery = recover_create_only_generation(
            storage, root_reference=root,
            bootstrap_reference=installed["bootstrap_document"]["bootstrap_reference"],
        )
        delivery_item = next(
            item for item in drive.objects.values()
            if item["title"] == "observed/delivery_state.json"
        )
        delivery_before = (delivery_item["modified_time"], delivery_item["data"])
        run_directory = self.base / "preview-run"
        run_directory.mkdir(mode=0o700)
        gmail = ConnectedRuntimeGmail()

        result = ConnectedDailyRuntime(
            installed_root=self.package_root, recovery=recovery,
            run_directory=run_directory, drive=drive, gmail=gmail,
            sheets=sheets, semantic=object(),
        ).run(
            entrypoint="manual", operation_id="connected-preview",
            attempt_id="attempt-1", preview_only=True,
        )

        self.assertEqual("PREVIEW_READY", result.outcome)
        self.assertEqual(tuple(PHASES), result.completed_phases)
        self.assertEqual(0, gmail.send_count)
        self.assertFalse(result.outputs["brief_delivery"]["delivery_reserved"])
        self.assertFalse(result.outputs["brief_delivery"]["delivery_sent"])
        self.assertEqual([], result.outputs["brief_delivery"]["effects"])
        self.assertEqual(delivery_before, (delivery_item["modified_time"], delivery_item["data"]))
        final_item = next(
            item for item in drive.objects.values()
            if item["title"] == "observed/final_run_checkpoint.json"
        )
        final = json.loads(final_item["data"])
        self.assertEqual("PREVIEW_READY", final["outcome"])
        self.assertFalse(final["delivery_reserved"])
        self.assertIsNone(final["delivery"])
        self.assertIn("brief_html", final)
        cursor_item = next(
            item for item in drive.objects.values()
            if item["title"] == "observed/source_checkpoint.json"
        )
        self.assertLess(int(final_item["modified_time"]), int(cursor_item["modified_time"]))

        with self.assertRaisesRegex(Exception, "manual-only"):
            ConnectedDailyRuntime(
                installed_root=self.package_root, recovery=recovery,
                run_directory=run_directory, drive=drive, gmail=gmail,
                sheets=sheets, semantic=object(),
            ).run(
                entrypoint="scheduled", operation_id="bad-preview",
                attempt_id="attempt-1", scheduler_admitted=True,
                preview_only=True,
            )

    def test_connected_runtime_nonempty_join_survives_a_later_zero_hit_run(self) -> None:
        scope = GoogleSheetsScope(
            "sheet-1", "https://sheets.example.invalid/sheet-1", 7, "Tasks",
            1, 20, 1, 13,
        )
        drive = ConnectedSetupDrive()
        sheets = ConnectedSetupSheets(scope)
        storage = CodexDriveCreateOnlyStorage(drive, scratch_directory=self.base / "setup-scratch")
        root = {
            "object_id": "instance-root", "kind": "folder",
            "permitted_ancestor_id": "instance-root", "mime_type": "application/vnd.google-apps.folder", "version": "1",
        }
        installed = install_connected_instance(
            storage=storage, sheets=sheets, root_reference=root, answers=self.answers,
            observed_payloads=self.make_connected_observed(self.make_connected_profile()), sheet_scope=scope,
        )
        recovery = recover_create_only_generation(
            storage, root_reference=root,
            bootstrap_reference=installed["bootstrap_document"]["bootstrap_reference"],
        )
        run_directory = self.base / "connected-run"
        run_directory.mkdir(mode=0o700)
        gmail = ConnectedRuntimeGmail(source_enabled=True)

        class Semantic:
            def interpret(self, packet):
                return {
                    "candidates": [{
                        "segment_id": segment["segment_id"], "byte_start": 0,
                        "byte_end": len(segment["text"].encode("utf-8")),
                        "candidate_kind": "statement", "category": "school",
                        "entity_scope": "child_1", "text": segment["text"],
                        "flags": {"is_update": False, "is_durable": False, "is_guideline": False, "is_action": True},
                    } for segment in packet["segments"]],
                    "coverage": [{
                        "segment_id": segment["segment_id"], "byte_start": 0,
                        "byte_end": len(segment["text"].encode("utf-8")),
                        "outcome": "fact", "reason": "action statement",
                    } for segment in packet["segments"]],
                    "review_cases": [],
                }

            def audit(self, packet, interpreted):
                return {
                    "packet_sha256": interpreted["packet_sha256"],
                    "interpreted_sha256": interpreted["interpreted_sha256"],
                    "coverage": [{
                        "segment_id": segment["segment_id"], "byte_start": 0,
                        "byte_end": len(segment["text"].encode("utf-8")),
                        "outcome": "fact",
                        "source_quote_sha256": hashlib.sha256(segment["text"].encode()).hexdigest(),
                        "interpreted_reason_sha256": hashlib.sha256(b"action statement").hexdigest(),
                        "audit_disposition": "accepted", "reason": "source quote checked",
                    } for segment in packet["segments"]],
                    "facts": [{
                        "fact_id": fact["fact_id"],
                        "source_quote_sha256": hashlib.sha256(fact["source_quote"].encode()).hexdigest(),
                        "canonical_text_sha256": hashlib.sha256(fact["text"].encode()).hexdigest(),
                        "classification": {
                            "candidate_kind": "statement", "category": "school", "entity_scope": "child_1",
                            "flags": fact["flags"],
                        },
                        "audit_disposition": "accepted", "reason": "wording checked",
                    } for fact in interpreted["facts"]],
                    "source_outcomes": [],
                    "mime_accounting": [{
                        "message_id": item["message_id"],
                        "accounting_sha256": item["accounting_sha256"],
                        "audit_disposition": "accepted",
                        "reason": "complete MIME disposition inventory checked",
                    } for item in packet.get("mime_accounting", [])],
                }

        runtime = lambda: ConnectedDailyRuntime(
            installed_root=self.package_root, recovery=recovery,
            run_directory=run_directory, drive=drive, gmail=gmail,
            sheets=sheets, semantic=Semantic(),
        )
        first = runtime().run(entrypoint="manual", operation_id="nonempty", attempt_id="attempt-1")
        self.assertEqual("COMPLETE", first.outcome)
        self.assertEqual(1, gmail.send_count)
        first_input = next(item for item in drive.objects.values() if item["title"] == "state/runs/nonempty-brief-input.json")
        first_value = json.loads(first_input["data"])
        self.assertEqual("Return the signed form.", first_value["tasks"][0]["text"])
        self.assertEqual("2026-09-08", first_value["tasks"][0]["received_date"])
        self.assertTrue(first_value["tasks"][0]["source_link"].startswith("https://drive.example.invalid/"))
        self.assertEqual("Return the signed form.", sheets.grid[1][3])

        gmail.source_enabled = False
        second = runtime().run(entrypoint="manual", operation_id="zero-after-nonempty", attempt_id="attempt-1")
        self.assertEqual("COMPLETE", second.outcome)
        self.assertEqual(1, gmail.send_count)
        second_input = next(item for item in drive.objects.values() if item["title"] == "state/runs/zero-after-nonempty-brief-input.json")
        second_value = json.loads(second_input["data"])
        self.assertEqual(first_value["tasks"], second_value["tasks"])

    def test_connected_runtime_recovers_unknown_send_after_local_reset(self) -> None:
        for hard_stop in (False, True):
            with self.subTest(hard_stop=hard_stop):
                scope = GoogleSheetsScope(
                    "sheet-1", "https://sheets.example.invalid/sheet-1", 7, "Tasks",
                    1, 20, 1, 13,
                )
                drive, sheets = ConnectedSetupDrive(), ConnectedSetupSheets(scope)
                storage = CodexDriveCreateOnlyStorage(drive, scratch_directory=self.base / f"setup-{hard_stop}")
                root = {
                    "object_id": "instance-root", "kind": "folder",
                    "permitted_ancestor_id": "instance-root",
                    "mime_type": "application/vnd.google-apps.folder", "version": "1",
                }
                installed = install_connected_instance(
                    storage=storage, sheets=sheets, root_reference=root, answers=self.answers,
                    observed_payloads=self.make_connected_observed(self.make_connected_profile()), sheet_scope=scope,
                )
                recovery = recover_create_only_generation(
                    storage, root_reference=root,
                    bootstrap_reference=installed["bootstrap_document"]["bootstrap_reference"],
                )
                run_directory = self.base / f"reset-{hard_stop}"
                run_directory.mkdir(mode=0o700)

                class LostAfterAcceptance(ConnectedRuntimeGmail):
                    def send(inner_self, request):
                        result = super(LostAfterAcceptance, inner_self).send(request)
                        if hard_stop:
                            raise SystemExit("synthetic hard process stop")
                        raise RuntimeError("synthetic lost send response")

                gmail = LostAfterAcceptance()
                first = ConnectedDailyRuntime(
                    installed_root=self.package_root, recovery=recovery,
                    run_directory=run_directory, drive=drive, gmail=gmail,
                    sheets=sheets, semantic=object(),
                )
                with self.assertRaises(SystemExit if hard_stop else Exception):
                    first.run(entrypoint="manual", operation_id=f"resume-{hard_stop}", attempt_id="attempt-1")
                shutil.rmtree(run_directory)
                run_directory.mkdir(mode=0o700)
                result = ConnectedDailyRuntime(
                    installed_root=self.package_root, recovery=recovery,
                    run_directory=run_directory, drive=drive, gmail=gmail,
                    sheets=sheets, semantic=object(),
                ).run(entrypoint="manual", operation_id=f"resume-{hard_stop}", attempt_id="attempt-2")
                self.assertEqual("COMPLETE", result.outcome)
                self.assertEqual(("brief_delivery", "commit"), tuple(result.outputs))
                self.assertEqual(1, gmail.send_count)

    def test_connected_runtime_recovers_caught_and_hard_unknown_send_in_fresh_processes(self) -> None:
        for failure in ("caught", "hard"):
            with self.subTest(failure=failure):
                scope = GoogleSheetsScope(
                    "sheet-1", "https://sheets.example.invalid/sheet-1", 7, "Tasks",
                    1, 20, 1, 13,
                )
                drive, sheets = ConnectedSetupDrive(), ConnectedSetupSheets(scope)
                storage = CodexDriveCreateOnlyStorage(drive, scratch_directory=self.base / f"process-setup-{failure}")
                root = {
                    "object_id": "instance-root", "kind": "folder",
                    "permitted_ancestor_id": "instance-root",
                    "mime_type": "application/vnd.google-apps.folder", "version": "1",
                }
                installed = install_connected_instance(
                    storage=storage, sheets=sheets, root_reference=root, answers=self.answers,
                    observed_payloads=self.make_connected_observed(self.make_connected_profile()), sheet_scope=scope,
                )
                recovery = recover_create_only_generation(
                    storage, root_reference=root,
                    bootstrap_reference=installed["bootstrap_document"]["bootstrap_reference"],
                )
                run_directory = self.base / f"process-run-{failure}"
                run_directory.mkdir(mode=0o700)
                state_path = self.base / f"process-state-{failure}.pickle"
                state = {
                    "sheet_scope": {
                        "spreadsheet_id": scope.spreadsheet_id, "spreadsheet_url": scope.spreadsheet_url,
                        "sheet_id": scope.sheet_id, "sheet_title": scope.sheet_title,
                        "first_row": scope.first_row, "last_row": scope.last_row,
                        "first_column": scope.first_column, "last_column": scope.last_column,
                    },
                    "drive_objects": drive.objects, "drive_sequence": drive.sequence,
                    "sheet_grid": sheets.grid, "sheet_headers": sheets.headers,
                    "gmail_messages": {}, "gmail_send_count": 0,
                    "recovery": recovery, "run_directory": str(run_directory),
                    "operation_id": f"process-resume-{failure}", "attempt_id": "attempt-1",
                    "failure": failure,
                }
                state_path.write_bytes(pickle.dumps(state))
                command = [
                    sys.executable, str(ROOT / "tests/support/connected_daily_process.py"),
                    str(state_path), str(self.package_root),
                ]
                first = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
                self.assertNotEqual(0, first.returncode)
                saved = pickle.loads(state_path.read_bytes())
                self.assertEqual(1, saved["gmail_send_count"], first.stderr)
                shutil.rmtree(run_directory)
                run_directory.mkdir(mode=0o700)
                saved.update({"failure": None, "attempt_id": "attempt-2"})
                state_path.write_bytes(pickle.dumps(saved))
                second = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
                self.assertEqual(0, second.returncode, second.stderr)
                outcome = json.loads(second.stdout)
                self.assertEqual("COMPLETE", outcome["outcome"])
                self.assertEqual(["brief_delivery", "commit"], outcome["outputs"])
                self.assertEqual(1, outcome["send_count"])

    def test_profile_readmission_selects_distinct_manual_and_scheduled_evidence(self) -> None:
        scope = GoogleSheetsScope(
            "sheet-1", "https://sheets.example.invalid/sheet-1", 7, "Tasks",
            1, 20, 1, 13,
        )
        drive, sheets = ConnectedSetupDrive(), ConnectedSetupSheets(scope)
        storage = CodexDriveCreateOnlyStorage(drive, scratch_directory=self.base / "setup-profile")
        root = {
            "object_id": "instance-root", "kind": "folder",
            "permitted_ancestor_id": "instance-root",
            "mime_type": "application/vnd.google-apps.folder", "version": "1",
        }
        installed = install_connected_instance(
            storage=storage, sheets=sheets, root_reference=root, answers=self.answers,
            observed_payloads=self.make_connected_observed(), sheet_scope=scope,
        )
        recovery = recover_create_only_generation(
            storage, root_reference=root,
            bootstrap_reference=installed["bootstrap_document"]["bootstrap_reference"],
        )
        run_directory = self.base / "profile-run"
        run_directory.mkdir(mode=0o700)
        with self.assertRaisesRegex(Exception, "not declared conformant|authentication is 'unknown'"):
            ConnectedDailyRuntime(
                installed_root=self.package_root, recovery=recovery, run_directory=run_directory,
                drive=drive, gmail=ConnectedRuntimeGmail(), sheets=sheets, semantic=object(),
            ).run(entrypoint="manual", operation_id="unknown-profile", attempt_id="attempt-1")
        manual = self.make_connected_profile()
        manual["evidence_class"] = "observed"
        admitted_manual = readmit_connected_profile(
            installed_root=self.package_root, recovery=recovery, run_directory=run_directory,
            drive=drive, entrypoint="manual", profile_data=canonical_json_bytes(manual),
        )
        scheduled = self.make_scheduled_profile()
        admitted_scheduled = readmit_connected_profile(
            installed_root=self.package_root, recovery=recovery, run_directory=run_directory,
            drive=drive, entrypoint="scheduled", profile_data=canonical_json_bytes(scheduled),
        )
        self.assertEqual("connected-test", admitted_manual["profile_id"])
        self.assertEqual("connected-scheduled-test", admitted_scheduled["profile_id"])
        result = ConnectedDailyRuntime(
            installed_root=self.package_root, recovery=recovery, run_directory=run_directory,
            drive=drive, gmail=ConnectedRuntimeGmail(), sheets=sheets, semantic=object(),
        ).run(
            entrypoint="scheduled", operation_id="scheduled-profile", attempt_id="attempt-1",
            scheduler_admitted=True,
        )
        self.assertEqual("COMPLETE", result.outcome)

    def test_configured_test_variants_send_once_each_and_same_variant_replay_suppresses(self) -> None:
        scope = GoogleSheetsScope(
            "sheet-1", "https://sheets.example.invalid/sheet-1", 7, "Tasks",
            1, 20, 1, 13,
        )
        drive, sheets = ConnectedSetupDrive(), ConnectedSetupSheets(scope)
        storage = CodexDriveCreateOnlyStorage(drive, scratch_directory=self.base / "setup-variants")
        root = {
            "object_id": "instance-root", "kind": "folder",
            "permitted_ancestor_id": "instance-root",
            "mime_type": "application/vnd.google-apps.folder", "version": "1",
        }
        observed = self.make_connected_observed(self.make_connected_profile())
        delivery = {
            "schema_version": 1, "variant": "ordinary-daily",
            "test_variants": {"manual": "manual-acceptance-test", "scheduled": "scheduled-acceptance-test"},
            "to": ["parent@example.invalid"], "cc": [], "bcc": [], "subject_prefix": "TEST School updates",
        }
        observed["delivery_configuration"]["data"] = canonical_json_bytes(delivery)
        installed = install_connected_instance(
            storage=storage, sheets=sheets, root_reference=root, answers=self.answers,
            observed_payloads=observed, sheet_scope=scope,
        )
        recovery = recover_create_only_generation(
            storage, root_reference=root,
            bootstrap_reference=installed["bootstrap_document"]["bootstrap_reference"],
        )
        run_directory = self.base / "variant-run"
        run_directory.mkdir(mode=0o700)
        readmit_connected_profile(
            installed_root=self.package_root, recovery=recovery, run_directory=run_directory,
            drive=drive, entrypoint="scheduled", profile_data=canonical_json_bytes(self.make_scheduled_profile()),
        )
        gmail = ConnectedRuntimeGmail()

        def run(entrypoint: str, operation_id: str, variant: str) -> None:
            result = ConnectedDailyRuntime(
                installed_root=self.package_root, recovery=recovery, run_directory=run_directory,
                drive=drive, gmail=gmail, sheets=sheets, semantic=object(),
            ).run(
                entrypoint=entrypoint, operation_id=operation_id, attempt_id="attempt-1",
                scheduler_admitted=entrypoint == "scheduled", delivery_variant=variant,
            )
            self.assertEqual("COMPLETE", result.outcome)

        run("manual", "manual-test-send", "manual-acceptance-test")
        run("scheduled", "scheduled-test-send", "scheduled-acceptance-test")
        run("manual", "manual-test-replay", "manual-acceptance-test")
        self.assertEqual(2, gmail.send_count)
        state = json.loads(next(
            item["data"] for item in drive.objects.values()
            if item["title"] == "observed/delivery_state.json"
        ))
        self.assertEqual(
            {"manual-acceptance-test", "scheduled-acceptance-test"},
            {item["intent"]["variant"] for item in state["deliveries"].values()},
        )
        self.assertTrue(all(item["intent"]["to"] == ["parent@example.invalid"] for item in state["deliveries"].values()))

    def test_create_only_generation_adopts_one_lost_response_without_retry(self) -> None:
        storage = CreateOnlyFakeStorage(lose_after_create=True)
        result = install_create_only_generation(
            storage,
            root_reference={"object_id": "instance-root", "kind": "folder", "permitted_ancestor_id": "instance-root", "version": "1"},
            package={"version": "0.1.0-alpha.13", "source_identity": {"repository": "example", "commit": "a" * 40}, "archive_sha256": TEST_ARCHIVE_SHA, "inventory_sha256": "b" * 64},
            payloads={**PACKAGE_PAYLOADS,"instance.yaml": b"instance\n"},
        )
        self.assertEqual("verified", result["admission"]["verification_status"])
        self.assertEqual(6, len(storage.calls))

    def test_staged_payload_builder_uses_the_first_created_state_reference(self) -> None:
        storage = CreateOnlyFakeStorage()
        state_bytes = initial_operation_state_bytes(self.package_root)
        state = storage.create_file("instance-root", OPERATION_STATE_PATH, state_bytes, "application/json")
        state_reference = {
            "object_id": state.object_id,
            "kind": state.kind,
            "permitted_ancestor_id": "instance-root",
            "mime_type": state.mime_type,
            "version": state.version,
        }
        package, payloads = compose_create_only_candidate_payloads(
            self.answers,
            instance_root=self.references["instance_root"],
            observed=self.references["observed"],
            operation_state_reference=state_reference,
        )
        self.assertEqual(state_bytes, payloads[OPERATION_STATE_PATH])
        self.assertFalse(any(b"transient-create-only-" in data for data in payloads.values()))
        result = install_create_only_generation(
            storage,
            root_reference=self.references["instance_root"],
            package=package,
            payloads=payloads,
            existing_payloads={OPERATION_STATE_PATH: state},
        )
        self.assertEqual(
            state_reference,
            result["manifest"]["files"][OPERATION_STATE_PATH]["object_reference"],
        )
        self.assertEqual(1, storage.calls.count(OPERATION_STATE_PATH))
        alternate_archive = gzip.compress(
            gzip.decompress(result["package_archive"]), compresslevel=1, mtime=0,
        )
        self.assertNotEqual(result["package_archive"], alternate_archive)
        alternate_sums = (
            f"{sha256_bytes(alternate_archive)}  {result['manifest']['package']['archive_name']}\n"
        ).encode("utf-8")
        substituted = {
            **result, "package_archive": alternate_archive,
            "package_checksums": alternate_sums,
        }
        with self.assertRaisesRegex(InstallationError, "archive bytes disagree with admitted hash"):
            extract_recovered_package(substituted, self.base / "substituted-package")
        self.assertFalse((self.base / "substituted-package").exists())
        checksum_substituted = {
            **result, "package_checksums": result["package_checksums"] + b"\n",
        }
        with self.assertRaisesRegex(InstallationError, "checksums bytes disagree with admitted hash"):
            extract_recovered_package(checksum_substituted, self.base / "substituted-checksums")
        self.assertFalse((self.base / "substituted-checksums").exists())
        shutil.rmtree(self.package_root)
        extracted = extract_recovered_package(result, self.base / "recovered-package")
        self.assertTrue((extracted / "START-HERE.md").is_file())
        self.assertFalse((extracted / ".git").exists())

    def test_create_only_generation_blocks_ambiguous_lost_response(self) -> None:
        storage = CreateOnlyFakeStorage(lose_after_create=True, duplicate_after_loss=True)
        with self.assertRaisesRegex(InstallationError, "ambiguous"):
            install_create_only_generation(
                storage,
                root_reference={"object_id": "instance-root", "kind": "folder", "permitted_ancestor_id": "instance-root", "version": "1"},
                package={"version": "0.1.0-alpha.13", "source_identity": {"repository": "example", "commit": "a" * 40}, "archive_sha256": TEST_ARCHIVE_SHA, "inventory_sha256": "b" * 64},
                payloads={**PACKAGE_PAYLOADS,"instance.yaml": b"instance\n"},
            )
        self.assertEqual(["instance.yaml"], storage.calls)

    def test_fresh_bootstrap_recovery_rejects_tamper_metadata_and_incomplete_generation(self) -> None:
        root = {"object_id": "instance-root", "kind": "folder", "permitted_ancestor_id": "instance-root", "version": "1"}
        package = {"version": "0.1.0-alpha.13", "source_identity": {"repository": "example", "commit": "a" * 40}, "archive_sha256": TEST_ARCHIVE_SHA, "inventory_sha256": "b" * 64}
        storage = CreateOnlyFakeStorage()
        result = install_create_only_generation(storage, root_reference=root, package=package, payloads={**PACKAGE_PAYLOADS,"instance.yaml": b"instance\n", "state/operation-state.json": b"{}\n"})
        recovered = recover_create_only_generation(storage, root_reference=root, bootstrap_reference=result["bootstrap_reference"])
        self.assertEqual(result["manifest"], recovered["manifest"])
        manifest_id = result["manifest_reference"]["object_id"]
        storage.objects = [replace(item, data=b"{}\n") if item.object_id == manifest_id else item for item in storage.objects]
        with self.assertRaisesRegex(InstallationError, "hash disagrees"):
            recover_create_only_generation(storage, root_reference=root, bootstrap_reference=result["bootstrap_reference"])

        storage = CreateOnlyFakeStorage()
        result = install_create_only_generation(storage, root_reference=root, package=package, payloads={**PACKAGE_PAYLOADS,"instance.yaml": b"instance\n"})
        instance_id = result["manifest"]["files"]["instance.yaml"]["object_reference"]["object_id"]
        storage.objects = [replace(item, data=b"changed\n") if item.object_id == instance_id else item for item in storage.objects]
        with self.assertRaisesRegex(InstallationError, "hash disagrees"):
            recover_create_only_generation(storage, root_reference=root, bootstrap_reference=result["bootstrap_reference"])

        storage = CreateOnlyFakeStorage()
        result = install_create_only_generation(storage, root_reference=root, package=package, payloads={**PACKAGE_PAYLOADS,"instance.yaml": b"instance\n"})
        instance_id = result["manifest"]["files"]["instance.yaml"]["object_reference"]["object_id"]
        storage.objects = [replace(item, mime_type="text/plain") if item.object_id == instance_id else item for item in storage.objects]
        with self.assertRaisesRegex(InstallationError, "reference failed"):
            recover_create_only_generation(storage, root_reference=root, bootstrap_reference=result["bootstrap_reference"])

        storage = CreateOnlyFakeStorage()
        result = install_create_only_generation(storage, root_reference=root, package=package, payloads={**PACKAGE_PAYLOADS,"instance.yaml": b"instance\n"})
        instance_id = result["manifest"]["files"]["instance.yaml"]["object_reference"]["object_id"]
        storage.objects = [replace(item, parent_id="outside-root", ancestor_ids=("instance-root", "outside-root")) if item.object_id == instance_id else item for item in storage.objects]
        with self.assertRaisesRegex(InstallationError, "outside the declared root"):
            recover_create_only_generation(storage, root_reference=root, bootstrap_reference=result["bootstrap_reference"])

        storage = CreateOnlyFakeStorage()
        result = install_create_only_generation(storage, root_reference=root, package=package, payloads={**PACKAGE_PAYLOADS,"instance.yaml": b"instance\n"})
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
