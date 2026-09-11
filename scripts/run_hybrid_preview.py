#!/usr/bin/env python3
"""Advance an installed hybrid preview through agent task exchange phases."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from school_os.bundles import read_bundle  # noqa: E402
from school_os.codex_bridge import CodexDrivePort, JsonlPeer  # noqa: E402
from school_os.connected_daily import resolve_hybrid_instance  # noqa: E402
from school_os.connected_setup import CodexDriveCreateOnlyStorage  # noqa: E402
from school_os.contracts import canonical_json_bytes, sha256_bytes  # noqa: E402
from school_os.hybrid_preview import (  # noqa: E402
    authorize_preview_action, confirm_preview_action, finish_preview,
    plan_preview_tasks,
)
from school_os.package import verify_extracted_tree  # noqa: E402


def _write_new(path: Path, data: bytes) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as handle:
        handle.write(data); handle.flush(); os.fsync(handle.fileno())


def _runtime(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    document = json.loads(path.read_text(encoding="utf-8"))
    state_bytes = Path(document["state_path"]).read_bytes()
    settings = Path(document["settings_path"]).read_bytes()
    if sha256_bytes(state_bytes) != document["state_sha256"] or sha256_bytes(settings) != document["settings_sha256"]:
        raise ValueError("hybrid runtime local byte hashes disagree")
    return document, {
        "bootstrap": document["bootstrap"],
        "bootstrap_reference": document["bootstrap_reference"],
        "current": document["current"],
        "current_reference": document["current_reference"],
        "settings": settings, "state_bundle": state_bytes,
        "state": read_bundle(state_bytes, expected_kind="state"),
    }


def _updated_runtime(document: dict[str, Any], transaction: Any, storage: Any, run_directory: Path, phase: str) -> dict[str, Any]:
    current = transaction.working.recovery["current"]
    state_reference = current["state"]["bundle_reference"]
    state_object = storage.read(state_reference["object_id"])
    if state_object is None or state_object.data is None or sha256_bytes(state_object.data) != current["state"]["bundle_sha256"]:
        raise ValueError("preview state bundle exact readback disagrees")
    generation = current.get("generation")
    if not isinstance(generation, int) or isinstance(generation, bool) or generation < 1:
        raise ValueError("preview current pointer lacks a valid generation")
    path = run_directory / f"preview-{phase}-generation-{generation:06d}.state.bundle"
    _write_new(path, state_object.data)
    return {
        **document, "current": current,
        "current_reference": transaction.working.recovery["current_reference"],
        "state_path": str(path.resolve()), "state_sha256": sha256_bytes(state_object.data),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("plan", "authorize", "confirm", "finish"))
    parser.add_argument("--installed-root", type=Path, required=True)
    parser.add_argument("--instance-document", type=Path, required=True)
    parser.add_argument("--run-directory", type=Path, required=True)
    parser.add_argument("--observed-at", required=True)
    parser.add_argument("--snapshot", type=Path)
    parser.add_argument("--result", type=Path)
    parser.add_argument("--local-day")
    parser.add_argument("--output-bundle-id")
    parser.add_argument("--output-action", type=Path)
    parser.add_argument("--output-instance", type=Path, required=True)
    parser.add_argument("--output-evidence", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        root = args.installed_root.resolve(strict=True)
        if root != ROOT.resolve(strict=True) or (root / ".git").exists():
            raise ValueError("hybrid preview requires its extracted installed package")
        verify_extracted_tree(root)
        document, recovery = _runtime(args.instance_document)
        resolved = resolve_hybrid_instance(package_root=root, recovery=recovery, entrypoint="manual")
        run_directory = args.run_directory.resolve(strict=True)
        storage = CodexDriveCreateOnlyStorage(
            CodexDrivePort(JsonlPeer(run_directory)),
            scratch_directory=run_directory / "storage-scratch",
        )
        serialization = {
            "mode": "attended_single_writer",
            "evidence": {
                "actor_id": "installed-agent-preview", "attempt_id": args.phase,
                "scheduler_inactive": True, "competing_mutators_excluded": True,
                "observed_at": args.observed_at,
            },
        }
        action = None
        if args.phase == "plan":
            if args.snapshot is None:
                raise ValueError("plan phase requires a normalized snapshot")
            advanced = plan_preview_tasks(
                storage=storage, resolved=resolved, installed_root=root,
                snapshot=json.loads(args.snapshot.read_text(encoding="utf-8")),
                serialization=serialization,
            )
        elif args.phase == "authorize":
            if args.output_action is None:
                raise ValueError("authorize phase requires an action output")
            advanced = authorize_preview_action(
                storage=storage, resolved=resolved, installed_root=root,
                serialization=serialization,
            )
            action = advanced.action
            _write_new(args.output_action, canonical_json_bytes(action))
        elif args.phase == "confirm":
            if args.result is None:
                raise ValueError("confirm phase requires an agent result")
            advanced = confirm_preview_action(
                storage=storage, resolved=resolved, installed_root=root,
                result=json.loads(args.result.read_text(encoding="utf-8")),
                serialization=serialization,
            )
        else:
            if not args.local_day or not args.output_bundle_id:
                raise ValueError("finish phase requires local day and output bundle identity")
            finished = finish_preview(
                storage=storage, resolved=resolved, installed_root=root,
                local_day=args.local_day, output_identity=args.output_bundle_id,
                serialization=serialization,
            )
            advanced = finished
        updated = _updated_runtime(document, advanced.transaction, storage, run_directory, args.phase)
        evidence = {
            "schema_version": 1, "phase": args.phase,
            "generation": advanced.transaction.working.recovery["current"]["generation"],
            "checkpoint_id": advanced.checkpoint["checkpoint_id"],
            "remaining_work": advanced.checkpoint["remaining_work"],
            "effect_id": action["effect_id"] if action else None,
            "outcome": "PREVIEW_READY" if args.phase == "finish" else "ADVANCED",
        }
        _write_new(args.output_instance, canonical_json_bytes(updated))
        _write_new(args.output_evidence, canonical_json_bytes(evidence))
    except Exception as exc:
        print(f"blocked: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"outcome": evidence["outcome"], "phase": args.phase, "evidence_sha256": sha256_bytes(canonical_json_bytes(evidence))}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
