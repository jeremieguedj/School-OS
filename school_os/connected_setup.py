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

from .bundles import BundleEntry
from .connected_storage import (
    BundleWorkingState, CodexDriveReferenceStorage, ConnectedStorageError,
    DriveReference, StoredArtifact,
)
from .connected_profiles import initial_profile_registry
from .contracts import canonical_json_bytes, dump_mapping_yaml, load_mapping_yaml, sha256_bytes
from .agent_tasks import initialize_provider_state, validate_snapshot
from .install import (
    DAILY_REFERENCE_KINDS, FILE_MAP_PATH, INTEGRATION_REFERENCE_KINDS,
    HYBRID_PACKAGE_PATH, OPERATION_STATE_PATH, PACKAGE_ARCHIVE_PATH, InstallationError,
    compose_create_only_candidate_payloads,
    hybrid_package_evidence,
    install_hybrid_generation,
    recover_hybrid_generation,
    managed_mime_type,
    initial_operation_state_bytes, install_create_only_generation,
)
from .references import ObjectReference, ReferenceError, StoredObject


FOLDER_MIME = "application/vnd.google-apps.folder"
OBSERVED_FILE_ROLES = (
    set(DAILY_REFERENCE_KINDS) | set(INTEGRATION_REFERENCE_KINDS)
) - {"source_catalog_folder", "task_provider_selector"}
SETUP_FILE_ROLES = OBSERVED_FILE_ROLES | {"task_sync_state"}
DRIVE_GZIP_MIME_TYPES = frozenset({
    "application/gzip", "application/x-gzip", "application/octet-stream",
})
GZIP_SIGNATURE = b"\x1f\x8b\x08"

_HYBRID_STATE_PATHS = {
    "source_checkpoint": "state/source-checkpoint.json",
    "source_catalog_index": "data/source-catalog-index.json",
    "canonical_action_register": "data/canonical-tasks.json",
    "guidelines": "data/guidelines.json",
    "rolling_updates": "data/rolling-updates.json",
    "brief_template": "state/brief-template.json",
    "delivery_state": "state/delivery-state.json",
    "final_run_checkpoint": "state/final-run-checkpoint.json",
    "runtime_profile": "state/capability-profiles/initial.json",
    "task_sync_state": "state/task-providers/selected.json",
}


def _admitted_drive_mime_types(name: str, data: bytes, requested: str) -> frozenset[str]:
    """Keep MIME exact except for a byte-proven pinned gzip release archive."""
    if name not in {PACKAGE_ARCHIVE_PATH, HYBRID_PACKAGE_PATH}:
        return frozenset({requested})
    if not data.startswith(GZIP_SIGNATURE):
        raise InstallationError("pinned release archive lacks the gzip signature")
    return DRIVE_GZIP_MIME_TYPES


def _failed_create_readback_checks(
    value: StoredObject | None, *, parent_id: str, name: str, data: bytes,
    admitted_mime_types: frozenset[str],
) -> tuple[str, ...]:
    if value is None:
        return ("identity",)
    checks = (
        ("kind", value.kind == "file"),
        ("name", value.name == name),
        ("parent", value.parent_id == parent_id and parent_id in value.ancestor_ids),
        ("MIME", value.mime_type in admitted_mime_types),
        ("bytes", value.data == data),
    )
    return tuple(label for label, passed in checks if not passed)


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
        admitted_mime_types = _admitted_drive_mime_types(name, data, mime_type)
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
                if (
                    len(matches) != 1 or matches[0].data != data
                    or matches[0].mime_type not in admitted_mime_types
                ):
                    raise InstallationError("Drive create outcome is absent or ambiguous after provider failure") from exc
                return matches[0]
        finally:
            path.unlink(missing_ok=True)
        if (
            not isinstance(result, Mapping) or result.get("success") is not True
            or not isinstance(result.get("id"), str) or not result["id"]
            or result.get("mime_type") not in admitted_mime_types or result.get("parent_id") != parent_id
            or not isinstance(result.get("url"), str) or not result["url"]
        ):
            if isinstance(result, Mapping) and isinstance(result.get("id"), str) and result["id"]:
                try:
                    recovered = self.read(result["id"])
                except Exception as exc:
                    raise InstallationError(
                        "Drive create receipt and identity readback are incomplete"
                    ) from exc
                failed = _failed_create_readback_checks(
                    recovered, parent_id=parent_id, name=name, data=data,
                    admitted_mime_types=admitted_mime_types,
                )
                if not failed:
                    self.expected_urls[result["id"]] = self._urls[result["id"]]
                    return recovered
                raise InstallationError(
                    "Drive create readback mismatch: " + ", ".join(failed)
                )
            receipt_checks = (
                ("identity", isinstance(result, Mapping) and result.get("success") is True),
                ("MIME", isinstance(result, Mapping) and result.get("mime_type") in admitted_mime_types),
                ("parent", isinstance(result, Mapping) and result.get("parent_id") == parent_id),
                ("URL", isinstance(result, Mapping) and isinstance(result.get("url"), str) and bool(result["url"])),
            )
            failed = tuple(label for label, passed in receipt_checks if not passed)
            raise InstallationError("Drive create receipt mismatch: " + ", ".join(failed))
        self.expected_urls[result["id"]] = result["url"]
        readback = self.read(result["id"])
        failed = _failed_create_readback_checks(
            readback, parent_id=parent_id, name=name, data=data,
            admitted_mime_types=admitted_mime_types,
        )
        if failed:
            raise InstallationError("Drive create readback mismatch: " + ", ".join(failed))
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

    def replace_file(
        self, object_id: str, parent_id: str, name: str, data: bytes,
        mime_type: str, expected_version: str,
    ) -> StoredObject:
        """Replace one exact pointer under admitted single-writer evidence.

        The pre-read detects ordinary drift but is not represented as provider
        compare-and-swap. An uncertain update is adopted only when exact-ID
        readback contains the complete intended bytes.
        """
        current = self.read(object_id)
        failed = _failed_create_readback_checks(
            current, parent_id=parent_id, name=name,
            data=current.data if current is not None and current.data is not None else b"",
            admitted_mime_types=frozenset({mime_type}),
        )
        if failed or current is None or current.version != expected_version:
            raise InstallationError("Drive pointer replacement base differs: " + ", ".join(failed or ("version",)))
        self.scratch_directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(self.scratch_directory, 0o700)
        descriptor, raw_path = tempfile.mkstemp(prefix="pointer-", dir=self.scratch_directory)
        path = Path(raw_path)
        try:
            os.fchmod(descriptor, 0o600)
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(data); handle.flush(); os.fsync(handle.fileno())
            try:
                result = self.drive.update(
                    object_id, file_uri=str(path.resolve(strict=True)), mime_type=mime_type,
                )
            except Exception as exc:
                recovered = self.read(object_id)
                mismatch = _failed_create_readback_checks(
                    recovered, parent_id=parent_id, name=name, data=data,
                    admitted_mime_types=frozenset({mime_type}),
                )
                if mismatch:
                    raise OSError("Drive pointer update outcome is unknown") from exc
                return recovered
        finally:
            path.unlink(missing_ok=True)
        if (
            not isinstance(result, Mapping) or result.get("success") is not True
            or result.get("id") != object_id
        ):
            recovered = self.read(object_id)
            mismatch = _failed_create_readback_checks(
                recovered, parent_id=parent_id, name=name, data=data,
                admitted_mime_types=frozenset({mime_type}),
            )
            if mismatch:
                raise InstallationError("Drive pointer update receipt and readback differ")
            return recovered
        readback = self.read(object_id)
        mismatch = _failed_create_readback_checks(
            readback, parent_id=parent_id, name=name, data=data,
            admitted_mime_types=frozenset({mime_type}),
        )
        if mismatch:
            raise InstallationError("Drive pointer update readback mismatch: " + ", ".join(mismatch))
        return readback


def _headers() -> tuple[str, ...]:
    from .sheets import SheetColumns
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
    from .connected_sheets import CodexSheetsTaskPort
    from .sheets import SheetColumns
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


def compose_hybrid_connected_inputs(
    answers: Mapping[str, Any], observed_payloads: Mapping[str, Mapping[str, Any]],
) -> tuple[dict[str, Any], bytes, bytes, dict[str, BundleEntry], str]:
    """Collapse validated legacy setup inputs into settings plus logical state."""
    if set(observed_payloads) != SETUP_FILE_ROLES:
        raise InstallationError("hybrid setup payload roles disagree")
    normalized: dict[str, dict[str, Any]] = {}
    for role in sorted(SETUP_FILE_ROLES):
        value = observed_payloads[role]
        if (
            not isinstance(value, Mapping) or set(value) != {"name", "data", "mime_type"}
            or not isinstance(value.get("data"), bytes)
            or value.get("mime_type") != "application/json"
        ):
            raise InstallationError(f"hybrid setup payload {role} is malformed")
        normalized[role] = dict(value)
    package_root_value = answers.get("package_root")
    if not isinstance(package_root_value, str) or not package_root_value:
        raise InstallationError("hybrid setup lacks the verified package root")
    package_root = Path(package_root_value)
    from .connected_daily import validate_connected_seed_payloads
    validate_connected_seed_payloads(normalized, package_root)
    package, package_bytes = hybrid_package_evidence(dict(answers))

    def decoded(role: str) -> dict[str, Any]:
        try:
            value = json.loads(normalized[role]["data"].decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise InstallationError(f"hybrid setup payload {role} is not UTF-8 JSON") from exc
        if not isinstance(value, dict) or canonical_json_bytes(value) != normalized[role]["data"]:
            raise InstallationError(f"hybrid setup payload {role} is not canonical JSON")
        return value

    instance = {
        "data_schema_version": 2,
        "instance_format_version": 2,
        "instance_id": answers["instance_id"],
        "release_channel": answers["release_channel"],
        "system_version": package["version"],
    }
    initial_task_provider = answers.get("initial_task_provider", "google_sheets")
    if not isinstance(initial_task_provider, str) or not initial_task_provider:
        raise InstallationError("hybrid setup lacks an initial task provider key")
    settings = {
        "daily_values": {
            "presentation": answers["daily_values"]["presentation"],
            "timezone": answers["household"]["timezone"],
        },
        "delivery_configuration": decoded("delivery_configuration"),
        "household": {"schema_version": 1, **dict(answers["household"])},
        "initial_task_provider": initial_task_provider,
        "instance": instance,
        "integrations": {"schema_version": 1, **dict(answers["integrations"])},
        "policies": {"schema_version": 1, **dict(answers["policies"])},
        "schema_version": 1,
        "source_scope": decoded("source_scope"),
    }
    settings_bytes = dump_mapping_yaml(settings)
    settings_schema = json.loads(
        (package_root / "schemas" / "installation-settings.schema.json").read_text(encoding="utf-8")
    )
    from .contracts import validate
    errors = validate(settings, settings_schema)
    if errors:
        raise InstallationError("hybrid installation settings are invalid: " + "; ".join(errors))

    entries = {
        path: BundleEntry(
            normalized[role]["data"], role, "application/json",
            {
                "canonical_action_register": "canonical-tasks.schema.json",
                "task_sync_state": "provider-state.schema.json",
                "runtime_profile": "capability-profile.schema.json",
            }.get(role),
        )
        for role, path in _HYBRID_STATE_PATHS.items()
    }
    entries[_HYBRID_STATE_PATHS["task_sync_state"]] = BundleEntry(
        canonical_json_bytes({
            "provider_id": "unbound", "adapter_id": "unbound",
            "provider_revision": None, "bindings": [], "cursor": None,
            "cursor_evidence": {}, "verified_readback": {},
        }),
        "task_sync_state", "application/json", "provider-state.schema.json",
    )
    operation_state = initial_operation_state_bytes(package_root)
    entries["state/operation-state.json"] = BundleEntry(
        operation_state, "operation_state", "application/json",
        "operation-state.schema.json",
    )
    selector = canonical_json_bytes({
        "bindings": {}, "schema_version": 2,
        "selected_provider": initial_task_provider, "status": "unbound",
        "switch": None,
    })
    entries["state/task-provider-selector.json"] = BundleEntry(
        selector, "task_provider_selector", "application/json",
    )
    profile_bytes = normalized["runtime_profile"]["data"]
    try:
        profile = json.loads(profile_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InstallationError("hybrid runtime profile is not UTF-8 JSON") from exc
    if not isinstance(profile, dict):
        raise InstallationError("hybrid runtime profile must be a JSON object")
    surface = profile.get("execution_surface")
    if surface not in {"manual", "scheduled"}:
        raise InstallationError("hybrid runtime profile lacks a supported execution surface")
    profiles: dict[str, Any] = {"manual": None, "scheduled": None}
    profiles[surface] = {
        "entry_path": _HYBRID_STATE_PATHS["runtime_profile"],
        "sha256": sha256_bytes(profile_bytes),
    }
    entries["state/runtime-profile-selection.json"] = BundleEntry(
        canonical_json_bytes({
            "profiles": profiles,
            "schema_version": 1,
        }),
        "runtime_profile_selection", "application/json",
    )
    entries["state/file-map.json"] = BundleEntry(
        canonical_json_bytes({
            "files": {
                role: path for role, path in sorted(_HYBRID_STATE_PATHS.items())
            } | {
                "active_task_provider": "state/task-provider-selector.json",
                "operation_state": "state/operation-state.json",
                "runtime_profile_selection": "state/runtime-profile-selection.json",
            },
            "mapping_status": "configured", "schema_version": 2,
        }),
        "file_map", "application/json",
    )
    fingerprint = sha256_bytes(canonical_json_bytes({
        "package_sha256": package["archive_sha256"],
        "settings_sha256": sha256_bytes(settings_bytes),
    }))
    return package, package_bytes, settings_bytes, entries, fingerprint


def install_hybrid_connected_instance(
    *, storage: CodexDriveCreateOnlyStorage, root_reference: dict[str, Any],
    answers: dict[str, Any], observed_payloads: Mapping[str, Mapping[str, Any]],
    runtime: Mapping[str, str],
) -> dict[str, Any]:
    """Prove one empty root and install only the five canonical physical files."""
    try:
        admitted_root = ObjectReference.from_mapping(root_reference)
    except ReferenceError as exc:
        raise InstallationError(f"hybrid setup requires an exact instance root reference: {exc}") from exc
    root_id = admitted_root.object_id
    if (
        admitted_root.kind != "folder" or admitted_root.permitted_ancestor_id != root_id
        or admitted_root.mime_type != FOLDER_MIME or not admitted_root.version
    ):
        raise InstallationError("hybrid setup requires a versioned self-contained Drive folder root")
    root = storage.read(root_id)
    if (
        root is None or root.kind != "folder" or root.mime_type != FOLDER_MIME
        or root.version != admitted_root.version
    ):
        raise InstallationError("hybrid setup root metadata differs from its admitted reference")
    if list(storage.list_scoped(root_id)):
        raise InstallationError("hybrid installation root is not initially empty")
    package, package_bytes, settings_bytes, entries, fingerprint = compose_hybrid_connected_inputs(
        answers, observed_payloads,
    )
    recovery = install_hybrid_generation(
        storage, root_reference=root_reference, package=package,
        package_bytes=package_bytes, settings_bytes=settings_bytes,
        instance_id=answers["instance_id"], state_entries=entries,
        configuration_fingerprint=fingerprint, runtime=runtime,
    )
    bootstrap_reference = recovery["bootstrap_reference"]
    bootstrap_id = bootstrap_reference["object_id"]
    bootstrap_url = storage.expected_urls.get(bootstrap_id)
    if not isinstance(bootstrap_url, str) or not bootstrap_url:
        raise InstallationError("hybrid bootstrap lacks its exact provider URL")
    return {
        "bootstrap_document": {
            "bootstrap_reference": bootstrap_reference,
            "bootstrap_url": bootstrap_url,
            "root_reference": root_reference,
        },
        "configuration_fingerprint": fingerprint,
        "current_reference": recovery["current_reference"],
        "projection_status": "unbound",
    }


def bind_hybrid_selected_sheet(
    *, storage: CodexDriveCreateOnlyStorage, sheets: Any,
    root_reference: dict[str, Any], bootstrap_reference: dict[str, Any],
    sheet_scope: GoogleSheetsScope, serialization: Mapping[str, Any],
) -> dict[str, Any]:
    """Archived fixed-layout reference; active hybrid binding is agent-managed."""
    from .connected_sheets import CodexSheetsTaskPort
    recovery = recover_hybrid_generation(
        storage, root_reference=root_reference,
        bootstrap_reference=bootstrap_reference,
    )
    working = BundleWorkingState.from_recovery(recovery)
    selector_path = "state/task-provider-selector.json"
    try:
        selector = json.loads(working.read(selector_path).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError, ConnectedStorageError) as exc:
        raise InstallationError(f"hybrid task-provider selector is unreadable: {exc}") from exc
    if selector != {
        "bindings": {}, "schema_version": 1,
        "selected_provider": "google_sheets", "status": "unbound",
    }:
        raise InstallationError("hybrid initial task-provider selector is not exactly unbound")

    initialize_selected_sheet(sheets, sheet_scope)
    scope = {
        "first_column": sheet_scope.first_column,
        "first_row": sheet_scope.first_row,
        "last_column": sheet_scope.last_column,
        "last_row": sheet_scope.last_row,
        "sheet_id": sheet_scope.sheet_id,
        "sheet_title": sheet_scope.sheet_title,
        "spreadsheet_id": sheet_scope.spreadsheet_id,
        "spreadsheet_url": sheet_scope.spreadsheet_url,
    }
    bound_selector = {
        "bindings": {
            "google_sheets": {
                "provider_state_path": _HYBRID_STATE_PATHS["task_sync_state"],
                "scope": scope,
                "status": "active",
            },
        },
        "schema_version": 1,
        "selected_provider": "google_sheets",
        "status": "bound",
    }
    committed = working.stage(
        selector_path, canonical_json_bytes(bound_selector),
    ).publish(storage, serialization)
    durable = committed.durable_reference(selector_path)
    return {
        "configuration_fingerprint": committed.recovery["current"]["configuration_fingerprint"],
        "current_reference": committed.recovery["current_reference"],
        "projection_status": "bound",
        "selected_provider": "google_sheets",
        "selector_reference": durable.as_mapping(),
        "sheet_scope_sha256": sha256_bytes(canonical_json_bytes(scope)),
    }


def bind_hybrid_task_projection(
    *, storage: CodexDriveCreateOnlyStorage,
    root_reference: dict[str, Any], bootstrap_reference: dict[str, Any],
    binding: Mapping[str, Any], snapshot: Mapping[str, Any],
    adapter_configuration: bytes, serialization: Mapping[str, Any],
    package_root: Path,
) -> dict[str, Any]:
    """Bind an agent-prepared projection without interpreting provider details."""
    required = {
        "provider_key", "provider_id", "adapter_id", "binding_id",
        "scope_sha256",
    }
    if set(binding) != required or any(
        not isinstance(binding.get(key), str) or not binding[key]
        for key in required
    ):
        raise InstallationError("agent task binding is malformed")
    if len(binding["scope_sha256"]) != 64:
        raise InstallationError("agent task binding scope hash is malformed")
    binding_id = binding["binding_id"]
    if "/" in binding_id or "\\" in binding_id or binding_id in {".", ".."}:
        raise InstallationError("agent task binding identity is not path-safe")
    if not isinstance(adapter_configuration, bytes) or not adapter_configuration:
        raise InstallationError("agent adapter configuration bytes are required")
    recovery = recover_hybrid_generation(
        storage, root_reference=root_reference,
        bootstrap_reference=bootstrap_reference,
    )
    working = BundleWorkingState.from_recovery(recovery)
    selector_path = "state/task-provider-selector.json"
    try:
        selector = json.loads(working.read(selector_path).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError, ConnectedStorageError) as exc:
        raise InstallationError(f"hybrid task-provider selector is unreadable: {exc}") from exc
    expected = {
        "bindings": {}, "schema_version": 2,
        "selected_provider": binding["provider_key"], "status": "unbound",
        "switch": None,
    }
    if selector != expected:
        raise InstallationError("hybrid initial task-provider selector is not exactly unbound")
    snapshot_schema = json.loads(
        (package_root / "schemas" / "task-adapter-snapshot.schema.json").read_text(encoding="utf-8")
    )
    provider_state_schema = json.loads(
        (package_root / "schemas" / "provider-state.schema.json").read_text(encoding="utf-8")
    )
    try:
        normalized = validate_snapshot(snapshot, snapshot_schema)
        for field in ("provider_id", "adapter_id", "binding_id", "scope_sha256"):
            if normalized[field] != binding[field]:
                raise InstallationError(f"initial task snapshot {field} disagrees with binding")
        if normalized["tasks"] or normalized["unbound_candidates"]:
            raise InstallationError("fresh task projection must be empty before binding")
        state = initialize_provider_state(
            provider_id=binding["provider_id"], adapter_id=binding["adapter_id"],
            binding_id=binding["binding_id"], scope_sha256=binding["scope_sha256"],
        )
        from .contracts import validate
        errors = validate(state, provider_state_schema)
        if errors:
            raise InstallationError("initial provider state is invalid: " + "; ".join(errors))
    except ValueError as exc:
        if isinstance(exc, InstallationError):
            raise
        raise InstallationError(f"initial agent task snapshot is invalid: {exc}") from exc
    configuration_path = f"state/task-adapters/{binding_id}.json"
    configuration_sha256 = sha256_bytes(adapter_configuration)
    selected = {
        "adapter_configuration_path": configuration_path,
        "adapter_configuration_sha256": configuration_sha256,
        "adapter_contract_version": "agent-task-v1",
        "adapter_id": binding["adapter_id"],
        "binding_id": binding["binding_id"],
        "provider_id": binding["provider_id"],
        "provider_state_path": _HYBRID_STATE_PATHS["task_sync_state"],
        "scope_sha256": binding["scope_sha256"],
        "status": "active",
    }
    bound_selector = {
        "bindings": {binding["provider_key"]: selected},
        "schema_version": 2, "selected_provider": binding["provider_key"],
        "status": "bound", "switch": None,
    }
    committed = (
        working
        .stage(
            configuration_path, adapter_configuration,
            role="task_adapter_configuration", media_type="application/json",
        )
        .stage(
            _HYBRID_STATE_PATHS["task_sync_state"], canonical_json_bytes(state),
        )
        .stage(selector_path, canonical_json_bytes(bound_selector))
        .publish(storage, serialization)
    )
    return {
        "configuration_fingerprint": committed.recovery["current"]["configuration_fingerprint"],
        "current_reference": committed.recovery["current_reference"],
        "projection_status": "bound", "selected_provider": binding["provider_key"],
        "selector_reference": committed.durable_reference(selector_path).as_mapping(),
        "scope_sha256": binding["scope_sha256"],
        "adapter_configuration_sha256": configuration_sha256,
    }


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
