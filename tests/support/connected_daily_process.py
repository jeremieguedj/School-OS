#!/usr/bin/env python3
"""Fresh-process harness for the concrete connected daily runtime."""

from __future__ import annotations

import json
import pickle
import sys
from pathlib import Path

sys.dont_write_bytecode = True
package_root = Path(sys.argv[2]).resolve(strict=True)
sys.path.insert(0, str(package_root))
sys.path.insert(1, str(Path(__file__).resolve().parents[2]))

from school_os.connected_daily import ConnectedDailyRuntime
from school_os.connected_sheets import GoogleSheetsScope
from tests.test_instance_scaffolding import ConnectedRuntimeGmail, ConnectedSetupDrive, ConnectedSetupSheets


state_path = Path(sys.argv[1])
state = pickle.loads(state_path.read_bytes())
scope = GoogleSheetsScope(**state["sheet_scope"])
drive = ConnectedSetupDrive()
drive.objects, drive.sequence = state["drive_objects"], state["drive_sequence"]
sheets = ConnectedSetupSheets(scope)
sheets.grid, sheets.headers = state["sheet_grid"], state["sheet_headers"]


class ProcessGmail(ConnectedRuntimeGmail):
    def send(self, request):
        response = super().send(request)
        if state["failure"] == "caught":
            raise RuntimeError("synthetic lost accepted-send response")
        if state["failure"] == "hard":
            raise SystemExit("synthetic hard process stop after acceptance")
        return response


gmail = ProcessGmail()
gmail.messages = state["gmail_messages"]
gmail.send_count = state["gmail_send_count"]


class NoSemantic:
    def interpret(self, _packet):
        raise AssertionError("zero-hit process recovery must not interpret")

    def audit(self, _packet, _interpretation):
        raise AssertionError("zero-hit process recovery must not audit")


try:
    result = ConnectedDailyRuntime(
        installed_root=package_root, recovery=state["recovery"],
        run_directory=Path(state["run_directory"]), drive=drive,
        gmail=gmail, sheets=sheets, semantic=NoSemantic(),
    ).run(
        entrypoint="manual", operation_id=state["operation_id"],
        attempt_id=state["attempt_id"],
    )
    print(json.dumps({
        "outcome": result.outcome, "outputs": list(result.outputs),
        "send_count": gmail.send_count,
    }, sort_keys=True))
finally:
    state.update({
        "drive_objects": drive.objects, "drive_sequence": drive.sequence,
        "sheet_grid": sheets.grid, "sheet_headers": sheets.headers,
        "gmail_messages": gmail.messages, "gmail_send_count": gmail.send_count,
    })
    state_path.write_bytes(pickle.dumps(state))
