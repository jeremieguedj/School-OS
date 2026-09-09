#!/usr/bin/env python3
"""Execute the finite School-OS source-host bridge and native image handoff.

For ``resource.fetch_https`` this command writes the complete raw helper response
and prints the one JSON control line consumed by ``JsonlPeer``.  For
``extract.image`` it makes a stable host-owned copy and prints the exact
``view_image(detail="original")`` action.  After the host performs that native
tool call, it writes a mode-0600 JSON file ``{"detail":"original","text":"..."}``
in the run directory and invokes ``complete-image``.
"""

from __future__ import annotations

import argparse
import json
import os
import stat
import sys
from pathlib import Path
from typing import Any, Mapping

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from school_os.codex_bridge import MAX_REQUEST_BYTES, PROTOCOL, REQUEST_ID, _validate_request
from school_os.connected_sources import ConnectedSourcesError, SourceHostHelpers
from school_os.contracts import canonical_json_bytes, sha256_bytes


def _private_file(path: Path, run_dir: Path, suffix: str, maximum: int) -> Path:
    resolved = path.resolve(strict=True)
    try:
        resolved.relative_to(run_dir)
    except ValueError as exc:
        raise ConnectedSourcesError("source host file escapes the private run directory") from exc
    status = resolved.stat(follow_symlinks=False)
    if (
        resolved.parent != run_dir or not resolved.name.endswith(suffix)
        or not stat.S_ISREG(status.st_mode) or stat.S_IMODE(status.st_mode) != 0o600
        or status.st_size > maximum or path.is_symlink()
    ):
        raise ConnectedSourcesError("source host file is not a bounded private regular file")
    return resolved


def _run_directory(path: Path) -> Path:
    if path.is_symlink():
        raise ConnectedSourcesError("source host run directory cannot be a symlink")
    resolved = path.resolve(strict=True)
    if not resolved.is_dir() or stat.S_IMODE(resolved.stat().st_mode) != 0o700:
        raise ConnectedSourcesError("source host run directory must have mode 0700")
    return resolved


def _exclusive_json(path: Path, value: Mapping[str, Any]) -> bytes:
    payload = canonical_json_bytes(value)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        path.unlink(missing_ok=True)
        raise
    return payload


def _response_control(run_dir: Path, request_id: str, result: Mapping[str, Any]) -> Mapping[str, str]:
    response_path = run_dir / f"{request_id}.response.json"
    payload = _exclusive_json(response_path, {
        "protocol": PROTOCOL, "request_id": request_id, "result": dict(result),
    })
    return {"request_id": request_id, "response_path": str(response_path), "sha256": sha256_bytes(payload)}


def prepare(
    run_dir: Path, request_path: Path, expected_sha256: str,
    *, helpers: SourceHostHelpers | None = None,
) -> Mapping[str, Any]:
    run_dir = _run_directory(run_dir)
    request_path = _private_file(request_path, run_dir, ".request.json", MAX_REQUEST_BYTES)
    payload = request_path.read_bytes()
    if sha256_bytes(payload) != expected_sha256:
        raise ConnectedSourcesError("source host request hash disagrees with the bridge control")
    try:
        request = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ConnectedSourcesError("source host request is not UTF-8 JSON") from exc
    if not isinstance(request, dict) or set(request) != {"args", "kind", "protocol", "request_id"}:
        raise ConnectedSourcesError("source host request wrapper is malformed")
    request_id, kind, args = request["request_id"], request["kind"], request["args"]
    if (
        request["protocol"] != PROTOCOL or not isinstance(request_id, str)
        or REQUEST_ID.fullmatch(request_id) is None or request_path.name != f"{request_id}.request.json"
        or not isinstance(kind, str) or not isinstance(args, Mapping)
    ):
        raise ConnectedSourcesError("source host request identity is malformed")
    _validate_request(kind, args)
    if kind not in {"resource.fetch_https", "extract.image"}:
        raise ConnectedSourcesError("source host runner accepts only the finite source request union")
    helpers = helpers or SourceHostHelpers(run_dir)
    if kind == "resource.fetch_https":
        return {"action": "respond", "control": _response_control(run_dir, request_id, helpers.dispatch(kind, args))}
    handoff = helpers.prepare_image(args)
    state_path = run_dir / f"{request_id}.image-state.json"
    try:
        _exclusive_json(state_path, {"handoff": handoff, "request_id": request_id})
    except Exception:
        helpers.cleanup_image(handoff)
        raise
    return {
        "action": "view_image", "tool": "view_image", "arguments": handoff["arguments"],
        "state_path": str(state_path),
        "completion": {
            "command": [sys.executable, str(Path(__file__).resolve()), "complete-image", str(run_dir), str(state_path), "<mode-0600-view-result.json>"],
            "view_result_schema": {"detail": "original", "text": "complete visible transcription"},
        },
    }


def complete_image(run_dir: Path, state_path: Path, view_result_path: Path) -> Mapping[str, Any]:
    run_dir = _run_directory(run_dir)
    state_path = _private_file(state_path, run_dir, ".image-state.json", MAX_REQUEST_BYTES)
    view_result_path = _private_file(view_result_path, run_dir, ".view-result.json", MAX_REQUEST_BYTES)
    try:
        state = json.loads(state_path.read_bytes())
        viewed = json.loads(view_result_path.read_bytes())
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ConnectedSourcesError("image handoff completion is not UTF-8 JSON") from exc
    if not isinstance(state, dict) or set(state) != {"handoff", "request_id"}:
        raise ConnectedSourcesError("image handoff state is malformed")
    if (
        not isinstance(state["request_id"], str) or REQUEST_ID.fullmatch(state["request_id"]) is None
        or state_path.name != f"{state['request_id']}.image-state.json"
    ):
        raise ConnectedSourcesError("image handoff state identity is malformed")
    if not isinstance(viewed, dict) or set(viewed) != {"detail", "text"} or viewed["detail"] != "original":
        raise ConnectedSourcesError("image native-tool completion did not attest original detail")
    helpers = SourceHostHelpers(run_dir)
    handoff = state["handoff"]
    try:
        result = helpers.complete_image(handoff, viewed["text"])
        control = _response_control(run_dir, state["request_id"], result)
    finally:
        if isinstance(handoff, Mapping):
            helpers.cleanup_image(handoff)
        state_path.unlink(missing_ok=True)
        view_result_path.unlink(missing_ok=True)
    return {"action": "respond", "control": control}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    start = commands.add_parser("prepare")
    start.add_argument("run_dir", type=Path)
    start.add_argument("request_path", type=Path)
    start.add_argument("request_sha256")
    finish = commands.add_parser("complete-image")
    finish.add_argument("run_dir", type=Path)
    finish.add_argument("state_path", type=Path)
    finish.add_argument("view_result_path", type=Path)
    args = parser.parse_args(argv)
    try:
        output = (
            prepare(args.run_dir, args.request_path, args.request_sha256)
            if args.command == "prepare"
            else complete_image(args.run_dir, args.state_path, args.view_result_path)
        )
    except ConnectedSourcesError as exc:
        parser.error(str(exc))
    print(json.dumps(output, sort_keys=True, separators=(",", ":")), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
