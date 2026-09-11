#!/usr/bin/env python3
"""Advance one selected or staged agent-managed task provider."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from school_os.codex_bridge import CodexDrivePort, JsonlPeer  # noqa: E402
from school_os.connected_daily import resolve_hybrid_instance  # noqa: E402
from school_os.connected_setup import CodexDriveCreateOnlyStorage  # noqa: E402
from school_os.contracts import canonical_json_bytes, sha256_bytes  # noqa: E402
from school_os.hybrid_runtime import (  # noqa: E402
    load_runtime, updated_runtime, write_new, write_outputs,
)
from school_os.hybrid_tasks import (  # noqa: E402
    authorize_hybrid_task_action, confirm_hybrid_task_action,
    plan_hybrid_task_sync,
)
from school_os.package import verify_extracted_tree  # noqa: E402


def _private_json(path: Path, instance_document: Path, label: str) -> dict[str, Any]:
    if path.parent.resolve(strict=True) != instance_document.parent.resolve(strict=True):
        raise ValueError(f"{label} escapes the private runtime directory")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def _serialization(args: argparse.Namespace) -> dict[str, Any]:
    if args.serialization is not None:
        return _private_json(
            args.serialization, args.instance_document, "serialization evidence",
        )
    if args.entrypoint != "manual":
        raise ValueError("scheduled task sync requires runtime serialization evidence")
    return {
        "mode": "attended_single_writer",
        "evidence": {
            "actor_id": "installed-agent-task-sync", "attempt_id": args.phase,
            "scheduler_inactive": True, "competing_mutators_excluded": True,
            "observed_at": args.observed_at,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("plan", "authorize", "confirm"))
    parser.add_argument("--installed-root", type=Path, required=True)
    parser.add_argument("--instance-document", type=Path, required=True)
    parser.add_argument("--run-directory", type=Path, required=True)
    parser.add_argument("--observed-at", required=True)
    parser.add_argument("--entrypoint", choices=("manual", "scheduled"), default="manual")
    parser.add_argument("--serialization", type=Path)
    parser.add_argument("--provider-key")
    parser.add_argument("--snapshot", type=Path)
    parser.add_argument("--result", type=Path)
    parser.add_argument("--completion-policy", type=Path)
    parser.add_argument("--output-action", type=Path)
    parser.add_argument("--output-instance", type=Path, required=True)
    parser.add_argument("--output-evidence", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        root = args.installed_root.resolve(strict=True)
        if root != ROOT.resolve(strict=True) or (root / ".git").exists():
            raise ValueError("hybrid task sync requires its extracted installed package")
        verify_extracted_tree(root)
        document, recovery = load_runtime(args.instance_document)
        resolved = resolve_hybrid_instance(
            package_root=root, recovery=recovery, entrypoint=args.entrypoint,
        )
        run_directory = args.run_directory.resolve(strict=True)
        storage = CodexDriveCreateOnlyStorage(
            CodexDrivePort(JsonlPeer(run_directory)),
            scratch_directory=run_directory / "storage-scratch",
        )
        serialization = _serialization(args)
        policy = (
            _private_json(args.completion_policy, args.instance_document, "completion policy")
            if args.completion_policy else None
        )
        action = None
        if args.phase == "plan":
            if args.snapshot is None:
                raise ValueError("task plan requires a complete normalized snapshot")
            advanced = plan_hybrid_task_sync(
                storage=storage, transaction=resolved.state, installed_root=root,
                snapshot=_private_json(args.snapshot, args.instance_document, "task snapshot"),
                serialization=serialization, provider_key=args.provider_key,
                completion_policy=policy,
            )
        elif args.phase == "authorize":
            if args.output_action is None:
                raise ValueError("task authorization requires an action output")
            advanced = authorize_hybrid_task_action(
                storage=storage, transaction=resolved.state, installed_root=root,
                serialization=serialization, provider_key=args.provider_key,
            )
            action = advanced.action
            write_new(args.output_action, canonical_json_bytes(action))
        else:
            if args.result is None:
                raise ValueError("task confirmation requires a normalized result")
            advanced = confirm_hybrid_task_action(
                storage=storage, transaction=resolved.state, installed_root=root,
                result=_private_json(args.result, args.instance_document, "task result"),
                serialization=serialization, provider_key=args.provider_key,
            )
        updated = updated_runtime(
            document, advanced.transaction, storage, run_directory,
            f"task-{advanced.provider_key}-{args.phase}",
        )
        evidence = {
            "schema_version": 1, "outcome": "TASK_SYNC_ADVANCED",
            "phase": args.phase, "provider_key": advanced.provider_key,
            "generation": advanced.transaction.working.recovery["current"]["generation"],
            "pending_action_count": len(advanced.provider_state.get("pending_actions", [])),
            "effect_id": action["effect_id"] if action else None,
        }
        write_outputs(
            output_instance=args.output_instance,
            output_evidence=args.output_evidence,
            runtime=updated, evidence=evidence,
        )
    except Exception as exc:
        print(f"blocked: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({
        "outcome": evidence["outcome"],
        "evidence_sha256": sha256_bytes(canonical_json_bytes(evidence)),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
