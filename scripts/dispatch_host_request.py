#!/usr/bin/env python3
"""Dispatch one School-OS bridge request through the reviewed host binding."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from school_os.codex_bridge import HOST_BINDINGS, BridgeError, HostBindingDispatcher
from school_os.contracts import canonical_json_bytes


def _exclusive(path: Path, data: bytes) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb", closefd=False) as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
    finally:
        os.close(descriptor)


def _contained_file(raw: str, run_dir: Path, suffix: str) -> Path:
    path = Path(raw)
    resolved = path.resolve(strict=True)
    resolved.relative_to(run_dir)
    status = path.lstat()
    if (
        resolved.parent != run_dir
        or not resolved.name.endswith(suffix)
        or stat.S_ISLNK(status.st_mode)
        or not stat.S_ISREG(status.st_mode)
        or stat.S_IMODE(status.st_mode) != 0o600
    ):
        raise BridgeError("native result is not an admitted private file")
    return resolved


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--request-id", required=True)
    parser.add_argument("--kind", required=True)
    parser.add_argument("--request-sha256", required=True)
    parser.add_argument("--request-path", type=Path, required=True)
    args = parser.parse_args(argv)
    run_dir = args.run_dir.resolve(strict=True)
    native_request_path = run_dir / f"{args.request_id}.native-request.json"
    native_result_path: Path | None = None

    def invoke(tool_name: str, native_args: dict[str, Any]) -> Any:
        nonlocal native_result_path
        if tool_name != HOST_BINDINGS[args.kind].tool_name:
            raise BridgeError("dispatcher selected an unexpected host binding")
        request_bytes = canonical_json_bytes({
            "request_id": args.request_id,
            "tool_name": tool_name,
            "args": native_args,
        })
        _exclusive(native_request_path, request_bytes)
        print(
            "SCHOOL_OS_NATIVE_REQUEST",
            args.request_id,
            hashlib.sha256(request_bytes).hexdigest(),
            native_request_path,
            flush=True,
        )
        line = sys.stdin.readline()
        if not line:
            raise BridgeError("native host result control is missing")
        control = json.loads(line)
        if not isinstance(control, dict) or set(control) != {
            "request_id", "native_result_path", "sha256",
        }:
            raise BridgeError("native host result control has an invalid shape")
        if control["request_id"] != args.request_id:
            raise BridgeError("native host result control is mismatched")
        native_result_path = _contained_file(
            control["native_result_path"], run_dir, ".native-result.json",
        )
        data = native_result_path.read_bytes()
        if hashlib.sha256(data).hexdigest() != control["sha256"]:
            raise BridgeError("native host result hash disagrees")
        value = json.loads(data)
        if not isinstance(value, dict):
            raise BridgeError("native host result must be an object")
        return value

    try:
        result = HostBindingDispatcher(run_dir).dispatch_request_file(
            request_id=args.request_id,
            kind=args.kind,
            request_sha256=args.request_sha256,
            request_path=args.request_path,
            invoke=invoke,
        )
    except (BridgeError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"blocked: {exc}", file=sys.stderr)
        return 1
    finally:
        native_request_path.unlink(missing_ok=True)
        if native_result_path is not None:
            native_result_path.unlink(missing_ok=True)
    print(json.dumps(result, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
