"""Fresh-process connected task recovery harness using durable synthetic evidence.

It intentionally invokes the production worker, Sheets port, and Drive
reference types.  The local JSON files are only a synthetic persistent
connector/store surface: no provider or source account is contacted.
"""
from __future__ import annotations

import base64
import json
import os
import sys
from pathlib import Path
from typing import Any

from school_os.connected_sheets import CodexSheetsTaskPort, GoogleSheetsScope
from school_os.connected_storage import DriveReference, StoredArtifact
from school_os.connected_tasks import ConnectedTaskError, ConnectedTaskWorker
from school_os.contracts import canonical_json_bytes
from school_os.sheets import GoogleSheetsTaskAdapter, MANAGED_BY_VALUE, SheetColumns
from school_os.tasks import TaskError, canonical_task_id


ROOT = Path(__file__).resolve().parents[2]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _save(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, sort_keys=True), encoding="utf-8")


class DurableStore:
    """A cross-process ArtifactStore whose versions reject stale writes."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def read(self, reference: DriveReference) -> StoredArtifact:
        state = _load(self.path)
        item = state["artifacts"][reference.object_id]
        if reference.version is not None and reference.version != item["version"]:
            raise AssertionError("stale durable reference")
        return StoredArtifact(
            DriveReference(reference.object_id, item["parent_id"], item["mime_type"], item["url"], item["version"]),
            base64.b64decode(item["data_b64"]),
        )

    def replace(self, reference: DriveReference, data: bytes, mime_type: str) -> StoredArtifact:
        state = _load(self.path)
        item = state["artifacts"][reference.object_id]
        if reference.version is not None and reference.version != item["version"]:
            raise AssertionError("stale durable reference")
        if item["mime_type"] != mime_type:
            raise AssertionError("replacement changed MIME type")
        item["data_b64"] = base64.b64encode(data).decode("ascii")
        item["version"] = f"v{int(item['version'][1:]) + 1}"
        _save(self.path, state)
        return self.read(DriveReference(reference.object_id, item["parent_id"], mime_type, item["url"], item["version"]))


class PersistentNativeSheets:
    """Connector-shaped Sheets surface with process-persistent provider evidence."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def _state(self) -> dict[str, Any]:
        return _load(self.path)

    def _write(self, state: dict[str, Any]) -> None:
        _save(self.path, state)

    @staticmethod
    def _row_data(row: list[str | None]) -> dict[str, Any]:
        return {"values": [
            {"formattedValue": value, "userEnteredValue": {"stringValue": value}}
            if value is not None else {}
            for value in row
        ]}

    def cells(self, **_arguments: Any) -> dict[str, Any]:
        state = self._state()
        rows = state["grid"]
        if state.get("hide_row_once"):
            state["hide_row_once"] = False
            self._write(state)
            rows = [rows[0], *([[None] * len(rows[0])] * (len(rows) - 1))]
        return {
            "spreadsheetId": "sheet-1",
            "sheets": [{"properties": {"sheetId": 7, "title": "Tasks"}, "data": [{
                "rowData": [self._row_data(row) for row in rows],
            }]}],
        }

    def batch_update(self, **arguments: Any) -> dict[str, Any]:
        state = self._state()
        headers = state["grid"][0]
        canonical_column = headers.index("Canonical Task ID")
        before = state["grid"][1][canonical_column]
        for request in arguments["requests"]:
            update = request["updateCells"]
            row = update["range"]["startRowIndex"]
            column = update["range"]["startColumnIndex"]
            state["grid"][row][column] = update["rows"][0]["values"][0]["userEnteredValue"]["stringValue"]
        if before in (None, "") and state["grid"][1][canonical_column] not in (None, ""):
            state["dispatches"]["create"] += 1
        hard_exit = state.get("hard_exit")
        if hard_exit == "create":
            state["hide_row_once"] = True
        self._write(state)
        if hard_exit == "create":
            os._exit(70)
        return {"spreadsheetId": "sheet-1", "replies": []}

    def all_comments(self, **_arguments: Any) -> tuple[dict[str, str], ...]:
        state = self._state()
        if state.get("hide_comment_once"):
            state["hide_comment_once"] = False
            self._write(state)
            return ()
        return tuple(dict(item) for item in state["comments"])

    def write_comments(self, **arguments: Any) -> dict[str, Any]:
        state = self._state()
        created = [{"id": f"comment-{len(state['comments']) + 1}", **item} for item in arguments["comments"]]
        state["comments"].extend(created)
        state["dispatches"]["comment"] += 1
        hard_exit = state.get("hard_exit")
        if hard_exit == "comment":
            state["hide_comment_once"] = True
        self._write(state)
        if hard_exit == "comment":
            os._exit(71)
        return {"fileId": "sheet-1", "created_comments": created}


def _schemas() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    return tuple(json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8")) for name in (
        "fact.schema.json", "task.schema.json", "canonical-tasks.schema.json", "provider-state.schema.json",
    ))  # type: ignore[return-value]


def _fact() -> dict[str, Any]:
    return {
        "fact_id": "fact-action", "record_id": "record-1", "source_message_id": "message-1",
        "source_byte_start": 0, "source_byte_end": 3, "received_date": "2026-09-07",
        "entity_scope": "household", "category": "school", "text": "Return form",
        "flags": {"is_update": False, "is_durable": False, "is_guideline": False, "is_action": True},
    }


def _reference(object_id: str, *, stale: bool = False) -> DriveReference:
    return DriveReference(object_id, "private-state", "application/json", f"memory://{object_id}", "obsolete" if stale else "v1")


def _initialize(path: Path) -> None:
    headers = list(SheetColumns().__dict__.values())
    artifacts = {
        "facts": {"parent_id": "private-state", "mime_type": "application/json", "url": "memory://facts", "version": "v1", "data_b64": base64.b64encode(canonical_json_bytes({"schema_version": 1, "record_id": "record-1", "facts": [_fact()]})).decode("ascii")},
        "tasks": {"parent_id": "private-state", "mime_type": "application/json", "url": "memory://tasks", "version": "v1", "data_b64": base64.b64encode(canonical_json_bytes({"schema_version": 1, "tasks": []})).decode("ascii")},
        "provider": {"parent_id": "private-state", "mime_type": "application/json", "url": "memory://provider", "version": "v1", "data_b64": base64.b64encode(canonical_json_bytes({"provider_id": "sheets", "adapter_id": "codex-sheets", "provider_revision": None, "bindings": [], "cursor": None, "cursor_evidence": {}, "verified_readback": {}})).decode("ascii")},
    }
    _save(path, {"artifacts": artifacts, "grid": [headers, [None] * len(headers), [None] * len(headers)], "comments": [], "dispatches": {"create": 0, "comment": 0}, "hard_exit": None, "hide_row_once": False, "hide_comment_once": False})


def _worker(path: Path) -> ConnectedTaskWorker:
    fact_schema, task_schema, register_schema, state_schema = _schemas()
    return ConnectedTaskWorker(store=DurableStore(path), fact_schema=fact_schema, task_schema=task_schema, register_schema=register_schema, provider_state_schema=state_schema)


def _run(path: Path, tasks: DriveReference, provider_state: DriveReference):
    native = PersistentNativeSheets(path)
    port = CodexSheetsTaskPort(native, GoogleSheetsScope("sheet-1", "https://example.invalid/sheet-1", 7, "Tasks", 1, 3, 1, 13))
    provider = GoogleSheetsTaskAdapter(port.scope, port, comments=port).begin_sync()
    return _worker(path).run_once(
        facts=[_reference("facts")], canonical_tasks=tasks, provider_state=provider_state,
        provider=provider, task_source_links={canonical_task_id("fact-action"): "https://example.invalid/source/message-1"},
    )


def _set_completed(path: Path) -> None:
    state = _load(path)
    state["grid"][1][state["grid"][0].index("Status")] = "completed"
    _save(path, state)


def _crash(path: Path, kind: str) -> None:
    first = _run(path, _reference("tasks", stale=True), _reference("provider", stale=True))
    if not first.continuation_required:
        raise AssertionError("first production reconciliation did not journal the create intent")
    if kind == "create":
        state = _load(path); state["hard_exit"] = "create"; _save(path, state)
        _run(path, first.canonical_tasks.reference, first.provider_state.reference)
        raise AssertionError("create did not hard-exit")
    second = _run(path, first.canonical_tasks.reference, first.provider_state.reference)
    if second.continuation_required:
        raise AssertionError("initial native create did not complete")
    _set_completed(path)
    reminder = _run(path, second.canonical_tasks.reference, second.provider_state.reference)
    if not reminder.continuation_required:
        raise AssertionError("completion policy did not journal the reminder")
    state = _load(path); state["hard_exit"] = "comment"; _save(path, state)
    _run(path, reminder.canonical_tasks.reference, reminder.provider_state.reference)
    raise AssertionError("comment did not hard-exit")


def _summary(path: Path) -> dict[str, Any]:
    state = _load(path)
    provider = json.loads(base64.b64decode(state["artifacts"]["provider"]["data_b64"]))
    return {"dispatches": state["dispatches"], "effect_intents": provider.get("effect_intents", []), "status": state["grid"][1][state["grid"][0].index("Status")]}


def main() -> None:
    mode, kind, raw_path = sys.argv[1:4]
    path = Path(raw_path)
    if mode == "initialize":
        _initialize(path)
        return
    if mode == "crash":
        _crash(path, kind)
        return
    if mode == "block":
        try:
            _run(path, _reference("tasks", stale=True), _reference("provider", stale=True))
        except (ConnectedTaskError, TaskError) as exc:
            if "remains unknown" not in str(exc):
                raise
            print(json.dumps({"blocked": True, **_summary(path)}, sort_keys=True))
            return
        raise AssertionError("transient missing provider observation did not block")
    if mode == "recover":
        result = _run(path, _reference("tasks", stale=True), _reference("provider", stale=True))
        summary = _summary(path)
        if result.continuation_required or summary["effect_intents"]:
            raise AssertionError("exact provider recovery did not clear its durable intent")
        if kind == "create" and summary["dispatches"]["create"] != 1:
            raise AssertionError("create dispatched more than once")
        if kind == "comment" and summary["dispatches"]["comment"] != 1:
            raise AssertionError("comment dispatched more than once")
        print(json.dumps({"recovered": True, **summary}, sort_keys=True))
        return
    raise AssertionError("unknown recovery child mode")


if __name__ == "__main__":
    main()
