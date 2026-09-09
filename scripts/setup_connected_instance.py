#!/usr/bin/env python3
"""Install one connected instance into a proven-empty Drive root."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from school_os.codex_bridge import CodexDrivePort, CodexSheetsPort, JsonlPeer
from school_os.connected_setup import (
    CodexDriveCreateOnlyStorage, decode_observed_payloads,
    install_connected_instance,
)
from school_os.connected_sheets import GoogleSheetsScope
from school_os.contracts import canonical_json_bytes, sha256_bytes
from school_os.install import InstallationError


def _object(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InstallationError(f"cannot read setup plan: {exc}") from exc
    if not isinstance(value, dict):
        raise InstallationError("setup plan must be a JSON object")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--host-jsonl", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        plan = _object(args.plan)
        if set(plan) != {"root_reference", "answers", "observed_payloads", "sheet_scope"}:
            raise InstallationError("setup plan has an unsupported shape")
        scope = GoogleSheetsScope(**plan["sheet_scope"])
        peer = JsonlPeer(args.host_jsonl)
        result = install_connected_instance(
            storage=CodexDriveCreateOnlyStorage(
                CodexDrivePort(peer), scratch_directory=args.host_jsonl / "setup-scratch",
            ),
            sheets=CodexSheetsPort(peer), root_reference=plan["root_reference"],
            answers=plan["answers"],
            observed_payloads=decode_observed_payloads(plan["observed_payloads"]),
            sheet_scope=scope,
        )
        output = canonical_json_bytes(result)
        descriptor = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            with os.fdopen(descriptor, "wb", closefd=False) as handle:
                handle.write(output); handle.flush(); os.fsync(handle.fileno())
        finally:
            os.close(descriptor)
    except (InstallationError, OSError, TypeError, ValueError) as exc:
        print(f"blocked: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"outcome": "CONNECTED_INSTANCE_INSTALLED", "output": str(args.output), "sha256": sha256_bytes(output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
