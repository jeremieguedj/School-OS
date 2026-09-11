#!/usr/bin/env python3
"""Stage, activate, or abort one guided agent-managed task-provider switch."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from school_os.codex_bridge import CodexDrivePort, JsonlPeer  # noqa: E402
from school_os.connected_daily import resolve_hybrid_instance  # noqa: E402
from school_os.connected_setup import CodexDriveCreateOnlyStorage  # noqa: E402
from school_os.contracts import canonical_json_bytes, sha256_bytes  # noqa: E402
from school_os.hybrid_runtime import (  # noqa: E402
    load_runtime, updated_runtime, write_outputs,
)
from school_os.hybrid_tasks import (  # noqa: E402
    abort_hybrid_task_switch, activate_hybrid_task_switch,
    begin_hybrid_task_switch,
)
from school_os.package import verify_extracted_tree  # noqa: E402


def _private_json(path: Path, instance_document: Path, label: str) -> dict:
    if path.parent.resolve(strict=True) != instance_document.parent.resolve(strict=True):
        raise ValueError(f"{label} escapes the private runtime directory")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("begin", "activate", "abort"))
    parser.add_argument("--installed-root", type=Path, required=True)
    parser.add_argument("--instance-document", type=Path, required=True)
    parser.add_argument("--run-directory", type=Path, required=True)
    parser.add_argument("--observed-at", required=True)
    parser.add_argument("--switch-plan", type=Path)
    parser.add_argument("--target-snapshot", type=Path)
    parser.add_argument("--completion-policy", type=Path)
    parser.add_argument("--output-instance", type=Path, required=True)
    parser.add_argument("--output-evidence", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        root = args.installed_root.resolve(strict=True)
        if root != ROOT.resolve(strict=True) or (root / ".git").exists():
            raise ValueError("hybrid task switch requires its extracted installed package")
        verify_extracted_tree(root)
        document, recovery = load_runtime(args.instance_document)
        resolved = resolve_hybrid_instance(package_root=root, recovery=recovery, entrypoint="manual")
        run_directory = args.run_directory.resolve(strict=True)
        storage = CodexDriveCreateOnlyStorage(
            CodexDrivePort(JsonlPeer(run_directory)),
            scratch_directory=run_directory / "storage-scratch",
        )
        serialization = {
            "mode": "attended_single_writer",
            "evidence": {
                "actor_id": "installed-agent-task-switch", "attempt_id": args.phase,
                "scheduler_inactive": True, "competing_mutators_excluded": True,
                "observed_at": args.observed_at,
            },
        }
        policy = (
            _private_json(args.completion_policy, args.instance_document, "completion policy")
            if args.completion_policy else None
        )
        if args.phase == "begin":
            if args.switch_plan is None or args.target_snapshot is None:
                raise ValueError("switch begin requires plan and target snapshot")
            plan = _private_json(args.switch_plan, args.instance_document, "switch plan")
            if not isinstance(plan, dict) or set(plan) != {
                "target", "adapter_configuration", "old_snapshot_sha256",
            }:
                raise ValueError("guided switch plan has an unsupported shape")
            configuration = None
            if plan["adapter_configuration"] is not None:
                configuration_path = Path(plan["adapter_configuration"])
                if configuration_path.parent.resolve(strict=True) != args.switch_plan.parent.resolve(strict=True):
                    raise ValueError("switch adapter configuration escapes its private directory")
                configuration = configuration_path.read_bytes()
            advanced = begin_hybrid_task_switch(
                storage=storage, transaction=resolved.state, installed_root=root,
                target=plan["target"],
                target_snapshot=_private_json(
                    args.target_snapshot, args.instance_document, "target snapshot",
                ),
                adapter_configuration=configuration,
                old_snapshot_sha256=plan["old_snapshot_sha256"],
                serialization=serialization, completion_policy=policy,
            )
            transaction, provider_key = advanced.transaction, advanced.provider_key
        elif args.phase == "activate":
            if args.target_snapshot is None:
                raise ValueError("switch activation requires complete target readback")
            advanced = activate_hybrid_task_switch(
                storage=storage, transaction=resolved.state, installed_root=root,
                target_snapshot=_private_json(
                    args.target_snapshot, args.instance_document, "target snapshot",
                ),
                serialization=serialization, completion_policy=policy,
            )
            transaction, provider_key = advanced.transaction, advanced.provider_key
        else:
            transaction = abort_hybrid_task_switch(
                storage=storage, transaction=resolved.state, installed_root=root,
                serialization=serialization,
            )
            selector = json.loads(transaction.read("state/task-provider-selector.json").data)
            provider_key = selector["selected_provider"]
        updated = updated_runtime(
            document, transaction, storage, run_directory,
            f"task-switch-{args.phase}",
        )
        selector = json.loads(transaction.read("state/task-provider-selector.json").data)
        evidence = {
            "schema_version": 1, "outcome": "TASK_SWITCH_ADVANCED",
            "phase": args.phase, "selected_provider": selector["selected_provider"],
            "status": selector["status"], "provider_key": provider_key,
            "generation": transaction.working.recovery["current"]["generation"],
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
