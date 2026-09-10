#!/usr/bin/env python3
"""Bind one agent-prepared task projection after hybrid installation."""
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
from school_os.connected_setup import (  # noqa: E402
    CodexDriveCreateOnlyStorage, bind_hybrid_task_projection,
)
from school_os.contracts import canonical_json_bytes, sha256_bytes  # noqa: E402
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
    recovery = {
        "bootstrap": document["bootstrap"],
        "bootstrap_reference": document["bootstrap_reference"],
        "current": document["current"],
        "current_reference": document["current_reference"],
        "settings": settings, "state_bundle": state_bytes,
        "state": read_bundle(state_bytes, expected_kind="state"),
    }
    return document, recovery


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--installed-root", type=Path, required=True)
    parser.add_argument("--instance-document", type=Path, required=True)
    parser.add_argument("--run-directory", type=Path, required=True)
    parser.add_argument("--binding-plan", type=Path, required=True)
    parser.add_argument("--observed-at", required=True)
    parser.add_argument("--output-instance", type=Path, required=True)
    parser.add_argument("--output-evidence", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        root = args.installed_root.resolve(strict=True)
        if root != ROOT.resolve(strict=True) or (root / ".git").exists():
            raise ValueError("task binding requires its extracted installed package")
        verify_extracted_tree(root)
        document, recovery = _runtime(args.instance_document)
        plan = json.loads(args.binding_plan.read_text(encoding="utf-8"))
        if not isinstance(plan, dict) or set(plan) != {"binding", "snapshot", "adapter_configuration"}:
            raise ValueError("agent binding plan has an unsupported shape")
        configuration_path = Path(plan["adapter_configuration"])
        if configuration_path.parent.resolve(strict=True) != args.binding_plan.parent.resolve(strict=True):
            raise ValueError("adapter configuration escapes the private plan directory")
        run_directory = args.run_directory.resolve(strict=True)
        peer = JsonlPeer(run_directory)
        storage = CodexDriveCreateOnlyStorage(
            CodexDrivePort(peer), scratch_directory=run_directory / "storage-scratch",
        )
        result = bind_hybrid_task_projection(
            storage=storage, root_reference=document["root_reference"],
            bootstrap_reference=recovery["bootstrap_reference"],
            binding=plan["binding"], snapshot=plan["snapshot"],
            adapter_configuration=configuration_path.read_bytes(),
            package_root=root,
            serialization={
                "mode": "attended_single_writer",
                "evidence": {
                    "actor_id": "installed-agent-task-binding",
                    "attempt_id": plan["snapshot"]["request_id"],
                    "scheduler_inactive": True,
                    "competing_mutators_excluded": True,
                    "observed_at": args.observed_at,
                },
            },
        )
        state_ref = result["current_reference"]
        current = storage.read(state_ref["object_id"])
        if current is None or current.data is None:
            raise ValueError("bound current pointer readback is unavailable")
        current_document = json.loads(current.data.decode("utf-8"))
        state_reference = current_document["state"]["bundle_reference"]
        state_object = storage.read(state_reference["object_id"])
        if state_object is None or state_object.data is None:
            raise ValueError("bound state bundle readback is unavailable")
        state_path = args.run_directory / "bound-state.bundle"
        _write_new(state_path, state_object.data)
        updated = {
            **document, "current": current_document,
            "current_reference": result["current_reference"],
            "state_path": str(state_path.resolve()),
            "state_sha256": sha256_bytes(state_object.data),
        }
        evidence = {
            "schema_version": 1, "outcome": "AGENT_TASK_PROJECTION_BOUND",
            "selected_provider": result["selected_provider"],
            "scope_sha256": result["scope_sha256"],
            "adapter_configuration_sha256": result["adapter_configuration_sha256"],
            "generation": current_document["generation"],
        }
        _write_new(args.output_instance, canonical_json_bytes(updated))
        _write_new(args.output_evidence, canonical_json_bytes(evidence))
    except Exception as exc:
        print(f"blocked: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"outcome": "AGENT_TASK_PROJECTION_BOUND", "evidence_sha256": sha256_bytes(canonical_json_bytes(evidence))}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
