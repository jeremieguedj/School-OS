#!/usr/bin/env python3
"""Exercise the production JSONL peer/port side of one synthetic host pump."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from school_os.codex_bridge import CodexDrivePort, CodexGmailPort, CodexSheetsPort, JsonlPeer


def main(argv: list[str]) -> int:
    peer = JsonlPeer(Path(argv[1]))
    drive = CodexDrivePort(peer)
    gmail = CodexGmailPort(peer)
    sheets = CodexSheetsPort(peer)
    results = {
        "drive": drive.metadata("file-1", fields="id,mimeType,parents,modifiedTime,size"),
        "gmail": gmail.send({
            "to": "student@example.invalid", "subject": "Subject",
            "payload": {"mime_type": "text/plain", "body": {"content": "hello"}},
            "classification_label_values": [{
                "label_id": "label-1",
                "fields": [{"field_id": "field-1", "selection": "choice-1"}],
            }],
            "response_fields": ["id", "snippet"],
        }),
        "attachment": gmail.read_attachment("message-1", "attachment-1"),
        "sheets": sheets.batch_update(
            spreadsheet_id="sheet-1", requests=[{"addSheet": {"properties": {"title": "Tasks"}}}],
        ),
        "comment": sheets.write_comments(
            id="sheet-1", comments=[{"content": "Exact note", "sheet_cell_range": "Tasks!A2"}],
        ),
    }
    print(json.dumps(results, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
