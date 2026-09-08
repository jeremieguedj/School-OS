"""Fail-closed transformation of the declared alpha.12 private template forms."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from .contracts import canonical_json_bytes, dump_mapping_yaml, validate


class MigrationError(ValueError):
    """Raised when a legacy form cannot be preserved without guessing."""


LEGACY_INSTANCE_KEYS = {
    "instance_format_version", "instance_id", "system_version", "data_schema_version",
    "release_channel", "active_release", "configuration", "state", "last_completed_migration",
    "latest_release_seen",
}
LEGACY_STATE_KEYS = {"schema_version", "status", "active_operation", "last_successful_run", "last_error"}
OPEN_HEADER = [
    "ID", "Action", "Task context", "Entity scope", "Workflow state", "Owner",
    "Opened source date", "Last source received date", "Source due", "Parent planned due",
    "Link", "Source Fact ID(s)", "Latest progress",
]
COMPLETION_HEADER = ["Task ID", "Outcome", "Detected at", "Evidence source", "Parent comment"]


@dataclass(frozen=True)
class Alpha13Migration:
    """Byte-stable candidate files; caller owns backup, write, and readback."""

    files: dict[str, bytes]
    migrated_task_count: int


def _mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise MigrationError(f"{label} must be an object")
    return dict(value)


def _columns(line: str, expected: list[str], label: str) -> list[str]:
    if not line.startswith("|") or not line.endswith("|"):
        raise MigrationError(f"unsupported {label} table row")
    values = [value.strip() for value in line.split("|")[1:-1]]
    if values != expected:
        raise MigrationError(f"unsupported {label} table header")
    return values


def _row(line: str, width: int, label: str) -> list[str]:
    if not line.startswith("|") or not line.endswith("|"):
        raise MigrationError(f"unsupported {label} table row")
    values = [value.strip() for value in line.split("|")[1:-1]]
    if len(values) != width:
        raise MigrationError(f"unsupported {label} table row width")
    return values


def _table_rows(lines: list[str], heading: str, header: list[str], start: int) -> tuple[list[list[str]], int]:
    if start >= len(lines) or lines[start] != heading:
        raise MigrationError(f"unsupported legacy task table: missing {heading}")
    if start + 2 >= len(lines):
        raise MigrationError(f"unsupported legacy task table: incomplete {heading}")
    _columns(lines[start + 2], header, heading)
    separator = lines[start + 3] if start + 3 < len(lines) else ""
    if not separator.startswith("|"):
        raise MigrationError(f"unsupported legacy task table: missing {heading} separator")
    rows: list[list[str]] = []
    index = start + 4
    while index < len(lines) and lines[index].startswith("|"):
        rows.append(_row(lines[index], len(header), heading))
        index += 1
    return rows, index


def migrate_legacy_task_table(markdown: str) -> dict[str, Any]:
    """Transform only the declared alpha.12 readable table without interpretation."""
    lines = markdown.splitlines()
    if len(lines) < 4 or lines[0] != "# Canonical task register":
        raise MigrationError("unsupported legacy task table title")
    try:
        open_start = lines.index("## Open tasks")
        completion_start = lines.index("## Completion history")
    except ValueError as exc:
        raise MigrationError("unsupported legacy task table sections") from exc
    open_rows, after_open = _table_rows(lines, "## Open tasks", OPEN_HEADER, open_start)
    if after_open > completion_start or any(line.strip() for line in lines[after_open:completion_start]):
        raise MigrationError("unsupported content between legacy task tables")
    completion_rows, after_completion = _table_rows(lines, "## Completion history", COMPLETION_HEADER, completion_start)
    if any(line.strip() for line in lines[after_completion:]):
        raise MigrationError("unsupported trailing legacy task content")
    tasks: dict[str, dict[str, Any]] = {}
    for row in open_rows:
        task_id, action, context, scope, workflow, owner, opened, last_source, source_due, parent_due, link, fact_ids, progress = row
        if not task_id or not action or not scope:
            raise MigrationError("legacy open task lacks required identity, action, or scope")
        if workflow not in {"needs_action", "waiting_external", "needs_review"}:
            raise MigrationError("legacy open task has unsupported workflow state")
        if task_id in tasks:
            raise MigrationError("legacy task table has duplicate task ID")
        source_facts = [item.strip() for item in fact_ids.split(",") if item.strip()]
        if len(source_facts) != len(set(source_facts)):
            raise MigrationError("legacy task has duplicate source Fact ID")
        tasks[task_id] = {
            "task_id": task_id,
            "origin": "source" if source_facts else "parent",
            "action": action,
            "task_context": context,
            "entity_scope": scope,
            "workflow_state": workflow,
            "owner": owner or None,
            "source_opened_date": opened or None,
            "last_supporting_source_date": last_source or opened or None,
            "source_due": source_due or None,
            "parent_planned_due": parent_due or None,
            "source_link": link or None,
            "source_facts": source_facts,
            "latest_progress": progress or None,
            "provider_bindings": [],
            "lifecycle_history": [],
            "projection_state": {},
            "revision": 1,
            "last_modified_evidence": {},
        }
    for task_id, outcome, detected_at, evidence_source, parent_comment in completion_rows:
        if task_id not in tasks:
            raise MigrationError("legacy completion history refers to an absent open task")
        tasks[task_id]["lifecycle_history"].append({
            "outcome": outcome, "detected_at": detected_at, "evidence_source": evidence_source,
            "parent_comment": parent_comment,
        })
    return {"schema_version": 1, "tasks": [tasks[key] for key in sorted(tasks)]}


def migrate_alpha12(
    *, instance: Mapping[str, Any], operation_state: Mapping[str, Any], file_map: Mapping[str, Any],
    action_items_markdown: str, target_version: str, task_schema: Mapping[str, Any],
    register_schema: Mapping[str, Any], instance_schema: Mapping[str, Any],
    operation_state_schema: Mapping[str, Any],
) -> Alpha13Migration:
    """Compose exact alpha.13 candidates from supported alpha.12 private forms."""
    legacy_instance = _mapping(instance, "legacy instance")
    if set(legacy_instance) != LEGACY_INSTANCE_KEYS or legacy_instance.get("data_schema_version") != 1:
        raise MigrationError("unsupported legacy instance manifest")
    active = _mapping(legacy_instance.get("active_release"), "legacy active_release")
    state = _mapping(legacy_instance.get("state"), "legacy state")
    if set(active) != {"version", "manifest_reference"} or set(state) != {"file_map_reference", "operation_state_reference"}:
        raise MigrationError("unsupported legacy instance references")
    legacy_state = _mapping(operation_state, "legacy operation state")
    if set(legacy_state) != LEGACY_STATE_KEYS or legacy_state.get("status") != "idle":
        raise MigrationError("unsupported legacy active operation state")
    if any(legacy_state[key] is not None for key in ("active_operation", "last_successful_run", "last_error")):
        raise MigrationError("legacy operation history requires an explicit private mapping")
    legacy_map = _mapping(file_map, "legacy file map")
    files = _mapping(legacy_map.get("files"), "legacy file map files")
    upgraded_map = {**legacy_map, "files": {**files, "operation_state": {}, "operation_checkpoints_folder": {}}}
    register = migrate_legacy_task_table(action_items_markdown)
    for task in register["tasks"]:
        errors = validate(task, dict(task_schema))
        if errors:
            raise MigrationError("legacy task cannot satisfy alpha.13 contract: " + "; ".join(errors))
    errors = validate(register, dict(register_schema))
    if errors:
        raise MigrationError("invalid migrated canonical task register: " + "; ".join(errors))
    if not target_version:
        raise MigrationError("target release version is required")
    upgraded_instance = {
        **legacy_instance,
        "system_version": target_version,
        "data_schema_version": 2,
        "active_release": {
            "version": target_version,
            "manifest_reference": f"system/releases/{target_version}/release.yaml",
            "operation_registry_reference": f"system/releases/{target_version}/core/operations/registry.json",
        },
        "state": {
            **state,
            "operation_state_reference": "state/operation-state.json",
            "operation_checkpoints_reference": "state/operation-checkpoints",
            "installation_manifest_reference": "state/installation-manifest.json",
        },
    }
    upgraded_state = {
        "schema_version": 1, "status": "idle", "current_operation": None,
        "serialization": None, "checkpoint": None, "last_terminal": None,
    }
    errors = validate(upgraded_instance, dict(instance_schema))
    if errors:
        raise MigrationError("invalid migrated instance manifest: " + "; ".join(errors))
    errors = validate(upgraded_state, dict(operation_state_schema))
    if errors:
        raise MigrationError("invalid migrated operation state: " + "; ".join(errors))
    return Alpha13Migration(
        {
            "instance.yaml": dump_mapping_yaml(upgraded_instance),
            "state/operation-state.json": canonical_json_bytes(upgraded_state),
            "state/file-map.yaml": dump_mapping_yaml(upgraded_map),
            "data/canonical-tasks.json": canonical_json_bytes(register),
        },
        len(register["tasks"]),
    )
