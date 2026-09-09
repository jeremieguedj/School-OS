"""Create-only Drive installation and selected-Sheet initialization."""

from __future__ import annotations

import base64
import binascii
import json
import os
import tempfile
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .connected_sheets import CodexSheetsTaskPort, GoogleSheetsScope
from .connected_storage import (
    CodexDriveReferenceStorage, ConnectedStorageError, DriveReference, StoredArtifact,
)
from .connected_profiles import initial_profile_registry
from .contracts import canonical_json_bytes, dump_mapping_yaml, load_mapping_yaml, sha256_bytes
from .install import (
    DAILY_REFERENCE_KINDS, FILE_MAP_PATH, INTEGRATION_REFERENCE_KINDS,
    OPERATION_STATE_PATH, InstallationError, compose_create_only_candidate_payloads,
    managed_mime_type,
    initial_operation_state_bytes, install_create_only_generation,
)
from .references import ObjectReference, ReferenceError, StoredObject
from .sheets import SheetColumns


FOLDER_MIME = "application/vnd.google-apps.folder"
OBSERVED_FILE_ROLES = (
    set(DAILY_REFERENCE_KINDS) | set(INTEGRATION_REFERENCE_KINDS)
) - {"source_catalog_folder", "task_provider_selector"}
SETUP_FILE_ROLES = OBSERVED_FILE_ROLES | {"task_sync_state"}


def _object_reference(value: StoredObject, root_id: str) -> dict[str, Any]:
    if value.parent_id != root_id or root_id not in value.ancestor_ids:
        raise InstallationError("setup object is outside the empty instance root")
    return {
        "object_id": value.object_id, "kind": value.kind,
        "permitted_ancestor_id": root_id, "mime_type": value.mime_type,
        "version": value.version,
    }


class CodexDriveCreateOnlyStorage(CodexDriveReferenceStorage):
    """Actual finite Drive create surface for the existing installer protocol."""

    def __init__(self, drive: Any, *, scratch_directory: Path, expected_urls: Mapping[str, str] | None = None) -> None:
        super().__init__(drive, expected_urls=expected_urls)
        self.scratch_directory = scratch_directory

    def create_file(self, parent_id: str, name: str, data: bytes, mime_type: str) -> StoredObject:
        if not parent_id or not name or not isinstance(data, bytes) or not mime_type:
            raise InstallationError("Drive create requires exact parent, name, bytes, and MIME type")
        self.scratch_directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(self.scratch_directory, 0o700)
        descriptor, raw_path = tempfile.mkstemp(prefix="setup-", dir=self.scratch_directory)
        path = Path(raw_path)
        try:
            os.fchmod(descriptor, 0o600)
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(data); handle.flush(); os.fsync(handle.fileno())
            try:
                result = self.drive.upload(
                    str(path.resolve(strict=True)), file_name=name,
                    mime_type=mime_type, parent_folder_id=parent_id,
                )
            except Exception as exc:
                matches = [
                    item for item in self.list_scoped(parent_id)
                    if item.kind == "file" and item.name == name
                ]
                if len(matches) != 1 or matches[0].data != data or matches[0].mime_type != mime_type:
                    raise InstallationError("Drive create outcome is absent or ambiguous after provider failure") from exc
                return matches[0]
        finally:
            path.unlink(missing_ok=True)
        if (
            not isinstance(result, Mapping) or result.get("success") is not True
            or not isinstance(result.get("id"), str) or not result["id"]
            or result.get("mime_type") != mime_type or result.get("parent_id") != parent_id
            or not isinstance(result.get("url"), str) or not result["url"]
        ):
            if isinstance(result, Mapping) and isinstance(result.get("id"), str) and result["id"]:
                try:
                    recovered = self.read(result["id"])
                except Exception as exc:
                    raise InstallationError(
                        "Drive create receipt and identity readback are incomplete"
                    ) from exc
                if (
                    recovered is not None and recovered.kind == "file"
                    and recovered.name == name and recovered.parent_id == parent_id
                    and recovered.mime_type == mime_type and recovered.data == data
                ):
                    return recovered
            raise InstallationError("Drive create receipt lacks exact identity, MIME, parent, or URL")
        self.expected_urls[result["id"]] = result["url"]
        readback = self.read(result["id"])
        if readback is None or readback.name != name or readback.data != data:
            raise InstallationError("Drive create readback differs from intended name or bytes")
        return readback

    def create_folder(self, parent_id: str, name: str) -> StoredObject:
        try:
            result = self.drive.create_folder(name, parent_id)
        except Exception as exc:
            matches = [
                item for item in self.list_scoped(parent_id)
                if item.kind == "folder" and item.name == name
            ]
            if len(matches) != 1:
                raise InstallationError("Drive folder create outcome is absent or ambiguous after provider failure") from exc
            return matches[0]
        if (
            not isinstance(result, Mapping) or result.get("success") is not True
            or not isinstance(result.get("id"), str) or not result["id"]
            or result.get("parent_id") != parent_id or result.get("title") != name
            or not isinstance(result.get("url"), str) or not result["url"]
        ):
            raise InstallationError("Drive folder receipt lacks exact identity, parent, title, or URL")
        self.expected_urls[result["id"]] = result["url"]
        readback = self.read(result["id"])
        if readback is None or readback.kind != "folder" or readback.name != name or readback.parent_id != parent_id:
            raise InstallationError("Drive folder readback differs from its create receipt")
        return readback


def _headers() -> tuple[str, ...]:
    columns = SheetColumns()
    return (
        columns.managed_by, columns.canonical_task_id, columns.task_origin,
        columns.action, columns.task_context, columns.source_link, columns.group,
        columns.workflow_state, columns.status, columns.source_due,
        columns.parent_planned_due, columns.parent_progress,
        columns.completion_comment,
    )


def _prove_empty_grid(result: Any, scope: GoogleSheetsScope) -> None:
    if not isinstance(result, Mapping) or result.get("spreadsheetId") != scope.spreadsheet_id:
        raise InstallationError("Sheet empty-scope read has the wrong spreadsheet identity")
    sheets = result.get("sheets")
    if not isinstance(sheets, list) or len(sheets) != 1 or not isinstance(sheets[0], Mapping):
        raise InstallationError("Sheet empty-scope read does not contain one bounded sheet")
    sheet = sheets[0]
    properties = sheet.get("properties")
    if not isinstance(properties, Mapping) or properties.get("sheetId") != scope.sheet_id or properties.get("title") != scope.sheet_title:
        raise InstallationError("Sheet empty-scope identity disagrees")
    for block in sheet.get("data", []):
        if not isinstance(block, Mapping):
            raise InstallationError("Sheet empty-scope grid data is malformed")
        for row in block.get("rowData", []):
            if not isinstance(row, Mapping):
                raise InstallationError("Sheet empty-scope row is malformed")
            for cell in row.get("values", []):
                if not isinstance(cell, Mapping) or cell.get("formattedValue") not in (None, "") or cell.get("userEnteredValue") not in (None, {}):
                    raise InstallationError("selected Sheet managed scope is not empty")


def initialize_selected_sheet(sheets: Any, scope: GoogleSheetsScope) -> None:
    expected_headers = _headers()
    if scope.last_column - scope.first_column + 1 != len(expected_headers):
        raise InstallationError("selected Sheet scope width does not match the fixed task headers")
    metadata = sheets.metadata(
        spreadsheet_id=scope.spreadsheet_id, charts_only=False,
        include_conditional_format_rules=True,
    )
    raw_sheets = metadata.get("sheets") if isinstance(metadata, Mapping) and metadata.get("spreadsheetId") == scope.spreadsheet_id else None
    matches = [
        item for item in raw_sheets or []
        if isinstance(item, Mapping) and isinstance(item.get("properties"), Mapping)
        and item["properties"].get("sheetId") == scope.sheet_id
        and item["properties"].get("title") == scope.sheet_title
    ]
    if not isinstance(raw_sheets, list) or len(matches) != 1:
        raise InstallationError("selected Sheet metadata identity is absent or ambiguous")
    empty = sheets.cells(
        spreadsheet_id=scope.spreadsheet_id, ranges=[scope.a1_range],
        cell_fields="formattedValue,userEnteredValue",
    )
    _prove_empty_grid(empty, scope)
    request = {
        "updateCells": {
            "range": {
                "sheetId": scope.sheet_id,
                "startRowIndex": scope.first_row - 1,
                "endRowIndex": scope.first_row,
                "startColumnIndex": scope.first_column - 1,
                "endColumnIndex": scope.last_column,
            },
            "rows": [{"values": [
                {"userEnteredValue": {"stringValue": value}}
                for value in expected_headers
            ]}],
            "fields": "userEnteredValue",
        }
    }
    result = sheets.batch_update(
        spreadsheet_id=scope.spreadsheet_id, requests=[request],
        include_spreadsheet_in_response=False,
    )
    if not isinstance(result, Mapping) or result.get("spreadsheetId") != scope.spreadsheet_id:
        raise InstallationError("Sheet header initialization lacks exact spreadsheet receipt")
    snapshot = CodexSheetsTaskPort(sheets, scope).read_complete(scope.adapter_scope)
    if snapshot.rows and any(any(value not in {None, ""} for value in row.cells.values()) for row in snapshot.rows):
        raise InstallationError("Sheet data rows changed during header initialization")


def install_connected_instance(
    *, storage: CodexDriveCreateOnlyStorage, sheets: Any,
    root_reference: dict[str, Any], answers: dict[str, Any],
    observed_payloads: Mapping[str, Mapping[str, Any]],
    sheet_scope: GoogleSheetsScope,
) -> dict[str, Any]:
    """Prove an empty root, initialize its external Sheet, and install once."""
    try:
        admitted_root = ObjectReference.from_mapping(root_reference)
    except ReferenceError as exc:
        raise InstallationError(f"setup requires an exact instance root reference: {exc}") from exc
    root_id = admitted_root.object_id
    if (
        admitted_root.kind != "folder" or admitted_root.permitted_ancestor_id != root_id
        or admitted_root.mime_type != FOLDER_MIME or not admitted_root.version
    ):
        raise InstallationError("setup requires a versioned self-contained Drive folder root")
    root = storage.read(root_id)
    if root is None or root.kind != "folder" or root.version != root_reference.get("version"):
        raise InstallationError("setup root metadata differs from its admitted reference")
    if list(storage.list_scoped(root_id)) != []:
        raise InstallationError("connected installation root is not initially empty")

    if set(observed_payloads) != SETUP_FILE_ROLES:
        missing = sorted(SETUP_FILE_ROLES - set(observed_payloads))
        extra = sorted(set(observed_payloads) - SETUP_FILE_ROLES)
        raise InstallationError(f"setup observed payload roles disagree (missing={missing}, extra={extra})")
    normalized_payloads: dict[str, dict[str, Any]] = {}
    names: set[str] = set()
    for role in sorted(SETUP_FILE_ROLES):
        value = observed_payloads[role]
        if not isinstance(value, Mapping) or set(value) != {"name", "data", "mime_type"} or not isinstance(value.get("data"), bytes):
            raise InstallationError(f"setup payload {role} is malformed")
        if not isinstance(value.get("name"), str) or not value["name"] or not isinstance(value.get("mime_type"), str) or not value["mime_type"]:
            raise InstallationError(f"setup payload {role} lacks an exact name or MIME type")
        if value["mime_type"] != "application/json" or value["name"] in names:
            raise InstallationError(f"setup payload {role} must have a unique JSON artifact name")
        names.add(value["name"])
        normalized_payloads[role] = dict(value)
    from .connected_daily import validate_connected_seed_payloads
    if not isinstance(answers.get("package_root"), str) or not answers["package_root"]:
        raise InstallationError("setup answers lack an exact package root")
    try:
        validate_connected_seed_payloads(normalized_payloads, Path(answers["package_root"]))
    except (OSError, ValueError) as exc:
        raise InstallationError(f"setup payload validation failed: {exc}") from exc
    initialize_selected_sheet(sheets, sheet_scope)

    observed: dict[str, dict[str, Any]] = {}
    setup_only: dict[str, dict[str, Any]] = {}
    for role in sorted(SETUP_FILE_ROLES):
        value = normalized_payloads[role]
        created = storage.create_file(root_id, value["name"], value["data"], value["mime_type"])
        reference = _object_reference(created, root_id)
        if role == "task_sync_state":
            setup_only[role] = reference
        else:
            observed[role] = reference

    profile_reference = observed["runtime_profile"]
    profile_artifact = StoredArtifact(
        DriveReference(
            profile_reference["object_id"], root_id,
            profile_reference["mime_type"], storage.expected_urls[profile_reference["object_id"]],
            profile_reference["version"],
        ),
        normalized_payloads["runtime_profile"]["data"],
    )
    profile_registry = storage.create_file(
        root_id, "config/runtime-profile-selection.json",
        initial_profile_registry(
            profile_artifact,
            json.loads((Path(answers["package_root"]) / "schemas" / "capability-profile.schema.json").read_text(encoding="utf-8")),
        ),
        "application/json",
    )
    profile_registry_reference = _object_reference(profile_registry, root_id)

    catalog_folder = storage.create_folder(root_id, "source-catalog")
    checkpoint_folder = storage.create_folder(root_id, "operation-checkpoints")
    observed["source_catalog_folder"] = _object_reference(catalog_folder, root_id)
    selector_bytes = canonical_json_bytes({
        "schema_version": 1,
        "spreadsheet_id": sheet_scope.spreadsheet_id,
        "spreadsheet_url": sheet_scope.spreadsheet_url,
        "sheet_id": sheet_scope.sheet_id, "sheet_title": sheet_scope.sheet_title,
        "first_row": sheet_scope.first_row, "last_row": sheet_scope.last_row,
        "first_column": sheet_scope.first_column, "last_column": sheet_scope.last_column,
    })
    selector = storage.create_file(root_id, "config/task-provider-selector.json", selector_bytes, "application/json")
    observed["task_provider_selector"] = _object_reference(selector, root_id)

    package_root = Path(answers["package_root"])
    operation_state_bytes = initial_operation_state_bytes(package_root)
    operation_state = storage.create_file(
        root_id, OPERATION_STATE_PATH, operation_state_bytes,
        managed_mime_type(OPERATION_STATE_PATH),
    )
    operation_reference = _object_reference(operation_state, root_id)
    recipe = storage.create_file(
        root_id, "operations/daily-run.md",
        (package_root / "core" / "operations" / "daily-run.md").read_bytes(),
        "text/markdown",
    )
    package, payloads = compose_create_only_candidate_payloads(
        answers, instance_root=root_reference, observed=observed,
        operation_state_reference=operation_reference,
    )
    file_map = load_mapping_yaml(payloads[FILE_MAP_PATH].decode("utf-8"))
    file_map["mapping_status"] = "configured"
    file_map["files"] = {
        "capability_profile": observed["runtime_profile"],
        "operation_state": operation_reference,
        "operation_checkpoints_folder": _object_reference(checkpoint_folder, root_id),
        "source_checkpoint": observed["source_checkpoint"],
        "current_index": observed["source_catalog_index"],
        "source_catalog_folder": observed["source_catalog_folder"],
        "source_catalog_index": observed["source_catalog_index"],
        "canonical_tasks": observed["canonical_action_register"],
        "guidelines": observed["guidelines"], "rolling_updates": observed["rolling_updates"],
        "brief_template": observed["brief_template"], "family_scope": observed["source_scope"],
        "active_task_provider": observed["task_provider_selector"],
        "task_sync_state": setup_only["task_sync_state"],
        "delivery_state": observed["delivery_state"],
        "final_run_checkpoint": observed["final_run_checkpoint"],
        "manual_run_recipe": _object_reference(recipe, root_id),
        "durable_profiles": profile_registry_reference,
    }
    payloads[FILE_MAP_PATH] = dump_mapping_yaml(file_map)
    recovery = install_create_only_generation(
        storage, root_reference=root_reference, package=package,
        payloads=payloads, existing_payloads={OPERATION_STATE_PATH: operation_state},
    )
    bootstrap_reference = recovery["bootstrap_reference"]
    return {
        "bootstrap_document": {
            "root_reference": root_reference,
            "bootstrap_reference": bootstrap_reference,
            "bootstrap_url": storage.expected_urls[bootstrap_reference["object_id"]],
        },
        "manifest_reference": recovery["manifest_reference"],
        "admission_reference": recovery["admission_reference"],
        "sheet_scope_sha256": sha256_bytes(selector_bytes),
        "root_initially_empty": True,
    }


def decode_observed_payloads(value: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(value, Mapping):
        raise InstallationError("observed payloads must be an object")
    decoded: dict[str, dict[str, Any]] = {}
    for role, item in value.items():
        if not isinstance(role, str) or not isinstance(item, Mapping) or set(item) != {"name", "data_b64", "mime_type"}:
            raise InstallationError("observed payload entry is malformed")
        try:
            data = base64.b64decode(item["data_b64"], validate=True)
        except (TypeError, ValueError, binascii.Error) as exc:
            raise InstallationError("observed payload base64 is invalid") from exc
        decoded[role] = {"name": item["name"], "data": data, "mime_type": item["mime_type"]}
    return decoded
