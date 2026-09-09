from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from school_os.connected_sheets import CodexSheetsTaskPort, ConnectedSheetsError, GoogleSheetsScope  # noqa: E402
from school_os.sheets import GoogleSheetsTaskAdapter, MANAGED_BY_VALUE, SheetColumns  # noqa: E402


class NativeSheets:
    """Small connector-shaped Sheets/comments fake, not an adapter fake."""

    def __init__(self) -> None:
        self.headers = list(SheetColumns().__dict__.values())
        self.grid = [self.headers, [None] * len(self.headers), [None] * len(self.headers)]
        self.comments_pages: list[list[dict]] = [[]]
        self.calls: list[str] = []

    def cells(self, **_arguments):
        self.calls.append("cells")
        return {
            "spreadsheetId": "sheet-1",
            "sheets": [{"properties": {"sheetId": 7, "title": "Tasks"}, "data": [{
                "startRow": 0, "startColumn": 0,
                "rowData": [{"values": [{"formattedValue": value, "userEnteredValue": {"stringValue": value}} if value is not None else {} for value in row]} for row in self.grid],
            }]}],
        }

    def batch_update(self, **arguments):
        self.calls.append("batch_update")
        for request in arguments["requests"]:
            update = request["updateCells"]
            row = update["range"]["startRowIndex"]
            column = update["range"]["startColumnIndex"]
            value = update["rows"][0]["values"][0]["userEnteredValue"]["stringValue"]
            self.grid[row][column] = value
        return {"spreadsheetId": "sheet-1", "replies": []}

    def all_comments(self, **_arguments):
        self.calls.append("comments")
        return tuple(copy.deepcopy(comment) for page in self.comments_pages for comment in page)

    def write_comments(self, **arguments):
        self.calls.append("write_comments")
        created = [{"id": f"comment-{len(self.comments_pages[0]) + 1}", **item} for item in arguments["comments"]]
        self.comments_pages[0].extend(copy.deepcopy(created))
        return {"fileId": "sheet-1", "created_comments": created}


class ConnectedSheetsTests(unittest.TestCase):
    def make_port(self):
        native = NativeSheets()
        scope = GoogleSheetsScope("sheet-1", "https://example.invalid/sheet-1", 7, "Tasks", 1, 3, 1, len(native.headers))
        return native, CodexSheetsTaskPort(native, scope)

    @staticmethod
    def candidate(task_id="task-1"):
        return {"canonical_task_id": task_id, "origin": "source", "title": "=literal", "description": "school", "group": "household", "workflow_state": "needs_action", "source_link": "record#fact", "source_due": ""}

    def test_complete_grid_literal_append_and_fresh_guarded_patch(self):
        native, port = self.make_port()
        adapter = GoogleSheetsTaskAdapter(port.scope, port, comments=port).begin_sync()
        created = adapter.create_task(self.candidate())
        self.assertEqual("=literal", created["title"])
        self.assertEqual(MANAGED_BY_VALUE, native.grid[1][0])
        native.grid[1][native.headers.index("Parent Progress")] = "parent note"
        patched = adapter.apply_patch(created["provider_object_id"], {"title": "Updated"})
        self.assertEqual("Updated", patched["title"])
        self.assertEqual("parent note", native.grid[1][native.headers.index("Parent Progress")])
        self.assertGreaterEqual(native.calls.count("cells"), 4)
        # A stale parent-cell expectation is rejected immediately before mutation.
        stale = adapter._find_managed_row("task-1")
        native.grid[1][native.headers.index("Action")] = "Parent changed"
        with self.assertRaisesRegex(ConnectedSheetsError, "guard"):
            adapter.apply_patch(created["provider_object_id"], {"title": "Again"})
        self.assertEqual("Parent changed", native.grid[1][native.headers.index("Action")])

    def test_comment_lookup_is_paginated_identity_enveloped_and_exact(self):
        native, port = self.make_port()
        adapter = GoogleSheetsTaskAdapter(port.scope, port, comments=port).begin_sync()
        created = adapter.create_task(self.candidate())
        written = adapter.write_comment(created["provider_object_id"], "effect-1", "Need a comment")
        self.assertEqual("Need a comment", written["text"])
        self.assertEqual(1, len(adapter.find_comments(created["provider_object_id"], "effect-1")))
        self.assertIn("write_comments", native.calls)

    def test_duplicate_canonical_identity_in_complete_snapshot_blocks(self):
        native, port = self.make_port()
        for row in (1, 2):
            native.grid[row][0] = MANAGED_BY_VALUE
            native.grid[row][1] = "task-duplicate"
            native.grid[row][2] = "source"
            native.grid[row][3] = "Action"
            native.grid[row][4] = "school"
            native.grid[row][5] = "record#fact"
            native.grid[row][6] = "household"
            native.grid[row][7] = "needs_action"
            native.grid[row][8] = "open"
            native.grid[row][9] = ""
        adapter = GoogleSheetsTaskAdapter(port.scope, port).begin_sync()
        with self.assertRaisesRegex(Exception, "multiple Sheet rows"):
            adapter.list_tasks()

    def test_formula_derived_identity_and_cross_column_scope_are_rejected(self):
        native, port = self.make_port()
        native.grid[1][0] = MANAGED_BY_VALUE
        native.grid[1][1] = "task-1"
        native.grid[1][2] = "source"
        native.grid[1][3] = "Action"
        native.grid[1][4] = "school"
        native.grid[1][5] = "record#fact"
        native.grid[1][6] = "household"
        native.grid[1][7] = "needs_action"
        native.grid[1][8] = "open"
        original = native.cells
        def formula_cells(**arguments):
            result = original(**arguments)
            for column in (0, 1):
                result["sheets"][0]["data"][0]["rowData"][1]["values"][column] = {"formattedValue": native.grid[1][column], "userEnteredValue": {"formulaValue": f'=\"{native.grid[1][column]}\"'}}
            return result
        native.cells = formula_cells
        with self.assertRaisesRegex(ConnectedSheetsError, "identity is not a literal"):
            GoogleSheetsTaskAdapter(port.scope, port).begin_sync().list_tasks()
        shifted = GoogleSheetsScope("sheet-1", "https://example.invalid/sheet-1", 7, "Tasks", 1, 3, 2, len(native.headers) + 1)
        self.assertNotEqual(port.scope, shifted.adapter_scope)

    def test_formula_header_and_empty_guard_block_before_native_mutation(self):
        native, port = self.make_port()
        original = native.cells

        def formula_headers(**arguments):
            result = original(**arguments)
            for cell in result["sheets"][0]["data"][0]["rowData"][0]["values"]:
                cell["userEnteredValue"] = {"formulaValue": f'=\"{cell["formattedValue"]}\"'}
            return result

        native.cells = formula_headers
        with self.assertRaisesRegex(ConnectedSheetsError, "header row is not literal"):
            GoogleSheetsTaskAdapter(port.scope, port).begin_sync().create_task(self.candidate())
        self.assertNotIn("batch_update", native.calls)

        native, port = self.make_port()
        for name, value in {
            "Managed By": MANAGED_BY_VALUE, "Canonical Task ID": "task-1", "Task Origin": "source",
            "Action": "Action", "Task Context": "school", "Source Link": "record#fact",
            "Group": "household", "Workflow State": "needs_action", "Status": "open", "Source Due": "",
        }.items():
            native.grid[1][native.headers.index(name)] = value
        original = native.cells

        def formula_blank_guard(**arguments):
            result = original(**arguments)
            result["sheets"][0]["data"][0]["rowData"][1]["values"][native.headers.index("Source Due")] = {
                "formattedValue": "", "userEnteredValue": {"formulaValue": '=\"\"'},
            }
            return result

        native.cells = formula_blank_guard
        with self.assertRaisesRegex(ConnectedSheetsError, "guarded cell is not a literal"):
            GoogleSheetsTaskAdapter(port.scope, port).begin_sync().apply_patch(
                "sheets:canonical:task-1", {"source_due": "2026-09-30"},
            )
        self.assertNotIn("batch_update", native.calls)

        native, port = self.make_port()
        for name, value in {
            "Managed By": MANAGED_BY_VALUE, "Canonical Task ID": "task-1", "Task Origin": "source",
            "Action": "Action", "Task Context": "school", "Source Link": "record#fact",
            "Group": "household", "Workflow State": "needs_action", "Status": "open", "Source Due": "",
        }.items():
            native.grid[1][native.headers.index(name)] = value
        original = native.cells

        def formula_unformatted_blank_guard(**arguments):
            result = original(**arguments)
            result["sheets"][0]["data"][0]["rowData"][1]["values"][native.headers.index("Parent Planned Due")] = {
                "userEnteredValue": {"formulaValue": '=\"\"'},
            }
            return result

        native.cells = formula_unformatted_blank_guard
        with self.assertRaisesRegex(ConnectedSheetsError, "guarded cell is not a literal"):
            GoogleSheetsTaskAdapter(port.scope, port).begin_sync().apply_parent_state(
                "sheets:canonical:task-1", parent_planned_due="2026-09-30",
            )
        self.assertNotIn("batch_update", native.calls)

    def test_sparse_omitted_empty_rows_remain_valid_append_targets(self):
        native, port = self.make_port()

        def sparse_cells(**_arguments):
            row_data = []
            for index, row in enumerate(native.grid):
                last = len(row) - 1 if index == 0 else next(
                    (offset for offset in range(len(row) - 1, -1, -1) if row[offset] is not None), -1,
                )
                if last >= 0:
                    row_data.append({"values": [
                        {"formattedValue": value, "userEnteredValue": {"stringValue": value}}
                        if value is not None else {}
                        for value in row[:last + 1]
                    ]})
            return {"spreadsheetId": "sheet-1", "sheets": [{"properties": {"sheetId": 7, "title": "Tasks"}, "data": [{"rowData": row_data}]}]}

        native.cells = sparse_cells
        created = GoogleSheetsTaskAdapter(port.scope, port).begin_sync().create_task(self.candidate())
        self.assertEqual("task-1", created["canonical_task_id"])
        self.assertEqual(1, native.calls.count("batch_update"))

    def test_native_sparse_trailing_cells_rows_and_zero_offsets_are_complete(self):
        native, port = self.make_port()
        def sparse_cells(**_arguments):
            return {
                "spreadsheetId": "sheet-1",
                "sheets": [{"properties": {"sheetId": 7, "title": "Tasks"}, "data": [{
                    # Google omits startRow/startColumn at their zero defaults,
                    # and omits empty trailing cells and rows.
                    "rowData": [
                        {"values": [{"formattedValue": value, "userEnteredValue": {"stringValue": value}} for value in native.headers]},
                        {"values": [{"formattedValue": value, "userEnteredValue": {"stringValue": value}} for value in [MANAGED_BY_VALUE, "task-1", "source", "Action", "school", "record#fact"]]},
                    ],
                }]}],
            }
        native.cells = sparse_cells
        snapshot = port.read_complete(port.scope)
        self.assertEqual(2, len(snapshot.rows))
        self.assertEqual("task-1", snapshot.rows[0].cells["Canonical Task ID"])
        self.assertIsNone(snapshot.rows[0].cells["Completion Comment"])
        self.assertIsNone(snapshot.rows[1].cells["Action"])

    def test_fresh_process_comment_acceptance_blocks_one_empty_lookup_then_adopts(self):
        headers = list(SheetColumns().__dict__.values())
        row = [None] * len(headers)
        for name, value in {"Managed By": MANAGED_BY_VALUE, "Canonical Task ID": "task-1", "Task Origin": "source", "Action": "Action", "Task Context": "school", "Source Link": "record#fact", "Group": "household", "Workflow State": "needs_action", "Status": "open", "Source Due": ""}.items():
            row[headers.index(name)] = value
        with tempfile.TemporaryDirectory() as temporary:
            state_path = Path(temporary) / "native.json"
            state_path.write_text(json.dumps({"headers": headers, "row": row, "comments": [], "hide_once": True, "effect_intent": {"effect_id": "effect-1", "outcome": "unknown", "dispatch_attempt": 1}}))
            code = """import json, os, sys
from pathlib import Path
from school_os.connected_sheets import CodexSheetsTaskPort, GoogleSheetsScope
state_path=Path(sys.argv[2])
class Native:
 def load(self): return json.loads(state_path.read_text())
 def save(self,x): state_path.write_text(json.dumps(x))
 def cells(self,**_):
  x=self.load(); row=x['row']
  if x.get('hide_row_once'): x['hide_row_once']=False; self.save(x); row=[None]*len(x['headers'])
  return {'spreadsheetId':'sheet-1','sheets':[{'properties':{'sheetId':7,'title':'Tasks'},'data':[{'rowData':[{'values':[{'formattedValue':v,'userEnteredValue':{'stringValue':v}} if v is not None else {} for v in x['headers']]},{'values':[{'formattedValue':v,'userEnteredValue':{'stringValue':v}} if v is not None else {} for v in row]}]}]}]}
 def batch_update(self,**arguments):
  x=self.load()
  for request in arguments['requests']:
   update=request['updateCells']; col=update['range']['startColumnIndex']; x['row'][col]=update['rows'][0]['values'][0]['userEnteredValue']['stringValue']
  self.save(x); os._exit(72)
 def all_comments(self,**_):
  x=self.load()
  if x['hide_once']: x['hide_once']=False; self.save(x); return ()
  return tuple(x['comments'])
 def write_comments(self,**arguments):
  x=self.load(); created=[{'id':'comment-1',**arguments['comments'][0]}]; x['comments'].extend(created); self.save(x); os._exit(71)
n=Native(); p=CodexSheetsTaskPort(n,GoogleSheetsScope('sheet-1','https://example.invalid/sheet-1',7,'Tasks',1,3,1,13)); object_id='sheets:canonical:task-1'
if sys.argv[1]=='row_crash':
 from school_os.sheets import NativeSheetMutation
 p.apply_mutation(NativeSheetMutation('append',p.scope,None,{'Managed By':'school-os','Canonical Task ID':'task-1','Task Origin':'source','Action':'Action','Task Context':'school','Source Link':'record#fact','Group':'household','Workflow State':'needs_action','Source Due':''},expected_canonical_task_id='task-1',expected_managed_by='school-os'))
if sys.argv[1]=='row_block': assert p.read_complete(p.scope).rows[0].cells['Canonical Task ID'] is None; raise SystemExit(0)
if sys.argv[1]=='row_adopt': assert p.read_complete(p.scope).rows[0].cells['Canonical Task ID']=='task-1'; raise SystemExit(0)
if sys.argv[1]=='crash': p.write_comment(p.scope,'sheet:7:row:2','task-1',object_id,'effect-1','Need comment')
found=p.list_comments(p.scope,'sheet:7:row:2','task-1',object_id,'effect-1')
if sys.argv[1]=='block': assert found==[] and n.load()['effect_intent']['outcome']=='unknown'; raise SystemExit(0)
assert len(found)==1 and found[0]['text']=='Need comment'; raise SystemExit(0)
"""
            environment = {**os.environ, "PYTHONPATH": str(ROOT)}
            crash = subprocess.run([sys.executable, "-c", code, "crash", str(state_path)], cwd=ROOT, env=environment)
            self.assertEqual(71, crash.returncode)
            self.assertEqual(1, len(json.loads(state_path.read_text())["comments"]))
            blocked = subprocess.run([sys.executable, "-c", code, "block", str(state_path)], cwd=ROOT, env=environment)
            self.assertEqual(0, blocked.returncode)
            adopted = subprocess.run([sys.executable, "-c", code, "adopt", str(state_path)], cwd=ROOT, env=environment)
            self.assertEqual(0, adopted.returncode)
            self.assertEqual(1, len(json.loads(state_path.read_text())["comments"]))
            row_state = {"headers": headers, "row": [None] * len(headers), "comments": [], "hide_once": False, "hide_row_once": False, "effect_intent": {"effect_id": "create-1", "outcome": "unknown", "dispatch_attempt": 1}}
            state_path.write_text(json.dumps(row_state))
            row_crash = subprocess.run([sys.executable, "-c", code, "row_crash", str(state_path)], cwd=ROOT, env=environment)
            self.assertEqual(72, row_crash.returncode)
            self.assertEqual("task-1", json.loads(state_path.read_text())["row"][headers.index("Canonical Task ID")])
            hidden = json.loads(state_path.read_text()); hidden["hide_row_once"] = True; state_path.write_text(json.dumps(hidden))
            row_blocked = subprocess.run([sys.executable, "-c", code, "row_block", str(state_path)], cwd=ROOT, env=environment)
            self.assertEqual(0, row_blocked.returncode)
            row_adopted = subprocess.run([sys.executable, "-c", code, "row_adopt", str(state_path)], cwd=ROOT, env=environment)
            self.assertEqual(0, row_adopted.returncode)


if __name__ == "__main__":
    unittest.main()
