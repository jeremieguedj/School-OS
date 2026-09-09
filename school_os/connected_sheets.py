"""Concrete, guarded Google Sheets rows/comments ports for task sync.

This is the connector boundary for the selected Sheets adapter.  It consumes
only native structured connector responses and turns them into the narrow
``school_os.sheets`` ports; policy and reconciliation remain in ``tasks.py``.
"""
from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from .sheets import (
    MANAGED_BY_VALUE, GoogleSheetsCommentsPort, GoogleSheetsRowsPort,
    NativeSheetMutation, SheetColumns, SheetRow, SheetScope, SheetSnapshot,
    normalized_snapshot,
)
from .tasks import TaskError


class ConnectedSheetsError(TaskError):
    """Raised when a native connector result cannot prove a Sheets operation."""


@dataclass(frozen=True)
class GoogleSheetsScope:
    """One bounded private grid whose first row is the declared header row."""

    spreadsheet_id: str
    spreadsheet_url: str
    sheet_id: int
    sheet_title: str
    first_row: int
    last_row: int
    first_column: int
    last_column: int

    def __post_init__(self) -> None:
        if (
            not self.spreadsheet_id or not self.spreadsheet_url or not self.sheet_title
            or self.first_row < 1 or self.last_row <= self.first_row
            or self.first_column < 1 or self.last_column < self.first_column
        ):
            raise ConnectedSheetsError("Sheets scope has invalid bounded grid coordinates")

    @property
    def adapter_scope(self) -> SheetScope:
        return SheetScope(f"sheets:{self.spreadsheet_id}:{self.sheet_id}:{self.first_row}:{self.last_row}:{self.first_column}:{self.last_column}")

    @property
    def a1_range(self) -> str:
        return f"'{self.sheet_title}'!{_column_name(self.first_column)}{self.first_row}:{_column_name(self.last_column)}{self.last_row}"


def _column_name(index: int) -> str:
    result = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        result = chr(ord("A") + remainder) + result
    return result


def _cell_text(value: Any) -> tuple[str | None, bool, bool]:
    """Return normalized text, literal evidence, and present nonliteral evidence.

    A missing/padded CellData value is a genuine empty cell.  It differs from
    a formula or other entered/displayed value that happens to evaluate to an
    empty string (or has no formatted value at all): the latter must never be
    selected as an empty append target or overwritten by a guarded mutation.
    """
    if not isinstance(value, Mapping):
        return None, False, False
    formatted = value.get("formattedValue")
    entered = value.get("userEnteredValue")
    if isinstance(entered, Mapping) and "stringValue" in entered:
        if not isinstance(entered["stringValue"], str):
            raise ConnectedSheetsError("Sheets literal cell value is not text")
        if len(entered) != 1:
            return entered["stringValue"], False, True
        return entered["stringValue"], True, False
    if formatted is not None:
        if not isinstance(formatted, str):
            raise ConnectedSheetsError("Sheets formatted cell value is not text")
        return formatted, False, True
    # A populated user-entered value without a string literal (including a
    # formula whose display value is omitted) is evidence of a nonliteral cell.
    if entered is not None:
        return None, False, True
    return None, False, False


def _grid_data(result: Any, scope: GoogleSheetsScope) -> tuple[list[str], list[list[str | None]], list[list[bool]], list[list[bool]]]:
    if not isinstance(result, Mapping) or result.get("spreadsheetId") != scope.spreadsheet_id:
        raise ConnectedSheetsError("Sheets cell response has the wrong spreadsheet identity")
    sheets = result.get("sheets")
    if not isinstance(sheets, list) or len(sheets) != 1 or not isinstance(sheets[0], Mapping):
        raise ConnectedSheetsError("Sheets cell response does not contain one bounded grid")
    sheet = sheets[0]
    properties = sheet.get("properties")
    data = sheet.get("data")
    if not isinstance(properties, Mapping) or properties.get("sheetId") != scope.sheet_id or properties.get("title") != scope.sheet_title:
        raise ConnectedSheetsError("Sheets cell response has the wrong sheet identity")
    if not isinstance(data, list) or len(data) != 1 or not isinstance(data[0], Mapping):
        raise ConnectedSheetsError("Sheets cell response lacks one complete grid-data block")
    block = data[0]
    # Native Sheets omits zero offsets.  They are equivalent only at the
    # admitted first row/column; a nonzero scope still needs explicit matching
    # coordinates rather than a best-effort interpretation.
    start_row = block.get("startRow", 0)
    start_column = block.get("startColumn", 0)
    if start_row != scope.first_row - 1 or start_column != scope.first_column - 1:
        raise ConnectedSheetsError("Sheets grid response begins outside the admitted scope")
    raw_rows = block.get("rowData")
    width = scope.last_column - scope.first_column + 1
    height = scope.last_row - scope.first_row + 1
    if not isinstance(raw_rows, list) or not raw_rows or len(raw_rows) > height:
        raise ConnectedSheetsError("Sheets grid response is malformed or exceeds the bounded scope")
    matrix: list[list[str | None]] = []
    literals: list[list[bool]] = []
    nonliterals: list[list[bool]] = []
    for row in raw_rows:
        if not isinstance(row, Mapping):
            raise ConnectedSheetsError("Sheets grid row is malformed")
        values = row.get("values", [])
        if not isinstance(values, list) or len(values) > width:
            raise ConnectedSheetsError("Sheets grid row exceeds the declared columns")
        decoded = [_cell_text(item) for item in values]
        matrix.append([*(item[0] for item in decoded), *([None] * (width - len(values)))])
        literals.append([*(item[1] for item in decoded), *([False] * (width - len(values)))])
        nonliterals.append([*(item[2] for item in decoded), *([False] * (width - len(values)))])
    # A successful native bounded read omits trailing entirely empty rows and
    # cells.  Expand those known empties only within the already requested grid.
    matrix.extend([[None] * width for _ in range(height - len(matrix))])
    literals.extend([[False] * width for _ in range(height - len(literals))])
    nonliterals.extend([[False] * width for _ in range(height - len(nonliterals))])
    headers = matrix[0]
    if any(not isinstance(value, str) or not value for value in headers) or len(set(headers)) != len(headers):
        raise ConnectedSheetsError("Sheets header row is missing or ambiguous")
    if not all(literals[0]):
        raise ConnectedSheetsError("Sheets header row is not literal string values")
    return list(headers), matrix[1:], literals[1:], nonliterals[1:]


class CodexSheetsTaskPort(GoogleSheetsRowsPort, GoogleSheetsCommentsPort):
    """Use a fixed ``CodexSheetsPort`` surface with complete-grid safeguards."""

    def __init__(self, sheets: Any, scope: GoogleSheetsScope, *, columns: SheetColumns = SheetColumns()) -> None:
        self.sheets, self.native_scope, self.columns = sheets, scope, columns
        self.scope = scope.adapter_scope

    def read_complete(self, scope: SheetScope) -> SheetSnapshot:
        self._require_scope(scope)
        headers, rows, literals, nonliterals = self._read_grid()
        self._require_literal_identity(headers, rows, literals)
        normalized = [
            {"row_id": self._row_id(offset), "cells": dict(zip(headers, values, strict=True))}
            for offset, values in enumerate(rows, start=self.native_scope.first_row + 1)
        ]
        return normalized_snapshot(scope, normalized, complete=True)

    def read_exact(self, scope: SheetScope, row_id: str) -> SheetRow | None:
        self._require_scope(scope)
        target = self._row_number(row_id)
        headers, rows, literals, nonliterals = self._read_grid()
        self._require_literal_identity(headers, rows, literals)
        if target <= self.native_scope.first_row or target > self.native_scope.last_row:
            return None
        values = rows[target - self.native_scope.first_row - 1]
        return SheetRow(row_id=row_id, cells=dict(zip(headers, values, strict=True)))

    def apply_mutation(self, mutation: NativeSheetMutation) -> str:
        self._require_scope(mutation.scope)
        headers, rows, literals, nonliterals = self._read_grid()  # immediate, complete native guard read
        self._require_literal_identity(headers, rows, literals)
        header_index = {header: index for index, header in enumerate(headers)}
        required = set(mutation.values) | set(mutation.guard_cells(self.columns))
        if not required <= set(header_index):
            raise ConnectedSheetsError("Sheets mutation names a column absent from the fresh header row")
        if mutation.kind == "append":
            canonical = mutation.values.get(self.columns.canonical_task_id)
            if not isinstance(canonical, str) or not canonical:
                raise ConnectedSheetsError("Sheets append lacks a canonical task ID")
            canonical_column = header_index[self.columns.canonical_task_id]
            if any(row[canonical_column] == canonical for row in rows):
                raise ConnectedSheetsError("fresh Sheets grid already contains the canonical task ID")
            target_index = next((
                index for index, row in enumerate(rows)
                if all(value in (None, "") for value in row) and not any(nonliterals[index])
            ), None)
            if target_index is None:
                raise ConnectedSheetsError("bounded Sheets grid has no empty row for append")
        elif mutation.kind in {"patch", "claim"}:
            if mutation.row_id is None:
                raise ConnectedSheetsError("Sheets guarded mutation has no row locator")
            target_row = self._row_number(mutation.row_id)
            target_index = target_row - self.native_scope.first_row - 1
            if target_index < 0 or target_index >= len(rows):
                raise ConnectedSheetsError("Sheets row locator is outside the admitted grid")
            current = dict(zip(headers, rows[target_index], strict=True))
            for column, expected in mutation.guard_cells(self.columns).items():
                if current.get(column) != expected:
                    raise ConnectedSheetsError("fresh Sheets identity or expected-cell guard did not match")
                if nonliterals[target_index][header_index[column]]:
                    raise ConnectedSheetsError("fresh Sheets guarded cell is not a literal string value")
        else:
            raise ConnectedSheetsError("unexpected Sheets task mutation kind")
        target_row = self.native_scope.first_row + 1 + target_index
        native_cells = mutation.native_cells()
        # Emit a cell request only for a mapped field.  Supplying blank CellData
        # under the userEnteredValue field mask could clear a parent-owned cell.
        requests = [
            {
                "updateCells": {
                    "range": {
                        "sheetId": self.native_scope.sheet_id,
                        "startRowIndex": target_row - 1,
                        "endRowIndex": target_row,
                        "startColumnIndex": self.native_scope.first_column - 1 + header_index[header],
                        "endColumnIndex": self.native_scope.first_column + header_index[header],
                    },
                    "rows": [{"values": [native_cells[header]]}],
                    "fields": "userEnteredValue",
                }
            }
            for header in mutation.values
        ]
        result = self.sheets.batch_update(
            spreadsheet_id=self.native_scope.spreadsheet_id, requests=requests,
            include_spreadsheet_in_response=False,
        )
        if not isinstance(result, Mapping) or result.get("spreadsheetId") != self.native_scope.spreadsheet_id:
            raise ConnectedSheetsError("Sheets batch update lacks exact spreadsheet readback identity")
        return self._row_id(target_row)

    def list_comments(self, scope: SheetScope, row_id: str, canonical_task_id: str, provider_object_id: str, effect_id: str) -> Sequence[Mapping[str, Any]]:
        self._require_scope(scope)
        self.read_exact(scope, row_id)  # no mutable locator is trusted without a fresh row read
        matches: list[dict[str, Any]] = []
        for raw in self.sheets.all_comments(spreadsheet_id=self.native_scope.spreadsheet_id, include_deleted=False, page_size=100):
            parsed = _parse_comment(raw)
            if parsed is None:
                continue
            if parsed["effect_id"] == effect_id:
                if parsed["canonical_task_id"] != canonical_task_id or parsed["provider_object_id"] != provider_object_id:
                    raise ConnectedSheetsError("native comment effect identity conflicts with the requested task")
                matches.append(parsed)
        return matches

    def write_comment(self, scope: SheetScope, row_id: str, canonical_task_id: str, provider_object_id: str, effect_id: str, text: str) -> Mapping[str, Any]:
        self._require_scope(scope)
        if self.read_exact(scope, row_id) is None:
            raise ConnectedSheetsError("comment target row disappeared before write")
        content = _comment_content(canonical_task_id, provider_object_id, effect_id, text)
        result = self.sheets.write_comments(id=self.native_scope.spreadsheet_id, comments=[{"content": content}])
        if not isinstance(result, Mapping) or result.get("fileId") != self.native_scope.spreadsheet_id:
            raise ConnectedSheetsError("Sheets comment write has the wrong spreadsheet identity")
        created = result.get("created_comments")
        if not isinstance(created, list) or len(created) != 1:
            raise ConnectedSheetsError("Sheets comment write did not return one native comment")
        parsed = _parse_comment(created[0])
        expected = {"canonical_task_id": canonical_task_id, "provider_object_id": provider_object_id, "effect_id": effect_id, "text": text}
        if parsed is None or any(parsed[key] != value for key, value in expected.items()):
            raise ConnectedSheetsError("Sheets comment write returned the wrong immutable effect")
        return parsed

    def _read_grid(self) -> tuple[list[str], list[list[str | None]], list[list[bool]], list[list[bool]]]:
        result = self.sheets.cells(
            spreadsheet_id=self.native_scope.spreadsheet_id,
            ranges=[self.native_scope.a1_range],
            cell_fields="formattedValue,userEnteredValue",
        )
        return _grid_data(result, self.native_scope)

    def _require_literal_identity(self, headers: list[str], rows: list[list[str | None]], literals: list[list[bool]]) -> None:
        indexes = {header: index for index, header in enumerate(headers)}
        for row, literal in zip(rows, literals, strict=True):
            marker = row[indexes[self.columns.managed_by]]
            canonical = row[indexes[self.columns.canonical_task_id]]
            if marker not in (None, "") and not literal[indexes[self.columns.managed_by]]:
                raise ConnectedSheetsError("Sheets managed identity is not a literal string value")
            if canonical not in (None, "") and not literal[indexes[self.columns.canonical_task_id]]:
                raise ConnectedSheetsError("Sheets canonical identity is not a literal string value")

    def _require_scope(self, scope: SheetScope) -> None:
        if scope != self.scope:
            raise ConnectedSheetsError("task worker used a different Sheets scope")

    def _row_id(self, row: int) -> str:
        return f"sheet:{self.native_scope.sheet_id}:row:{row}"

    def _row_number(self, row_id: str) -> int:
        match = re.fullmatch(rf"sheet:{self.native_scope.sheet_id}:row:([1-9][0-9]*)", row_id)
        if match is None:
            raise ConnectedSheetsError("Sheets row locator is not in this sheet")
        return int(match.group(1))


_COMMENT_PREFIX = "School-OS task effect v1\n"


def _comment_content(canonical_task_id: str, provider_object_id: str, effect_id: str, text: str) -> str:
    if not all(isinstance(value, str) and value for value in (canonical_task_id, provider_object_id, effect_id, text)):
        raise ConnectedSheetsError("Sheets comment effect fields must be nonempty text")
    return f"{_COMMENT_PREFIX}Canonical Task ID: {canonical_task_id}\nProvider Object ID: {provider_object_id}\nEffect ID: {effect_id}\n\n{text}"


def _parse_comment(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, Mapping):
        raise ConnectedSheetsError("native Sheets comment is malformed")
    content = value.get("content")
    if not isinstance(content, str):
        raise ConnectedSheetsError("native Sheets comment lacks text content")
    if not content.startswith(_COMMENT_PREFIX):
        return None
    prefix, separator, text = content.partition("\n\n")
    if not separator:
        raise ConnectedSheetsError("School-OS native comment metadata is malformed")
    lines = prefix.splitlines()
    if len(lines) != 4:
        raise ConnectedSheetsError("School-OS native comment metadata has unexpected fields")
    keys = ("Canonical Task ID: ", "Provider Object ID: ", "Effect ID: ")
    values = [line.removeprefix(key) for line, key in zip(lines[1:], keys, strict=True)]
    if any(not value or line == value for line, value in zip(lines[1:], values, strict=True)):
        raise ConnectedSheetsError("School-OS native comment metadata is incomplete")
    return {"comment_id": value.get("id"), "canonical_task_id": values[0], "provider_object_id": values[1], "effect_id": values[2], "text": text}
