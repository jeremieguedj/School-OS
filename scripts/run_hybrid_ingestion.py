#!/usr/bin/env python3
"""Run and canonically commit one complete hybrid-layout source ingestion."""

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

from school_os.bundles import read_bundle
from school_os.codex_bridge import CodexDrivePort, CodexGmailPort, CodexSemanticPort, JsonlPeer
from school_os.connected_daily import resolve_hybrid_instance
from school_os.connected_setup import CodexDriveCreateOnlyStorage
from school_os.contracts import canonical_json_bytes, sha256_bytes
from school_os.hybrid_ingestion import (
    SourceByteCapture, commit_ingestion, stage_connected_ingestion,
)
from school_os.package import verify_extracted_tree


def _bytes(path_value: Any, document: Path, label: str) -> bytes:
    if not isinstance(path_value, str):
        raise ValueError(f"{label} path is malformed")
    path = Path(path_value)
    if path.parent.resolve(strict=True) != document.parent.resolve(strict=True):
        raise ValueError(f"{label} path escapes the private runtime directory")
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"{label} file is unavailable")
    return path.read_bytes()


def _runtime(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "bootstrap", "bootstrap_reference", "current", "current_reference", "layout",
        "root_reference", "schema_version", "settings_path", "settings_sha256",
        "state_path", "state_sha256",
    }
    if not isinstance(value, dict) or set(value) != required or value.get("layout") != "hybrid-bundle-v1":
        raise ValueError("hybrid runtime document has an unsupported shape")
    settings = _bytes(value["settings_path"], path, "settings")
    state_bytes = _bytes(value["state_path"], path, "state")
    if sha256_bytes(settings) != value["settings_sha256"] or sha256_bytes(state_bytes) != value["state_sha256"]:
        raise ValueError("hybrid runtime document byte hashes disagree")
    state = read_bundle(state_bytes, expected_kind="state")
    if value["current"].get("state", {}).get("bundle_sha256") != state.sha256:
        raise ValueError("hybrid runtime document current pointer disagrees")
    return {
        "bootstrap": value["bootstrap"],
        "bootstrap_reference": value["bootstrap_reference"],
        "current": value["current"],
        "current_reference": value["current_reference"],
        "settings": settings,
        "state_bundle": state_bytes,
        "state": state,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--installed-root", type=Path, required=True)
    parser.add_argument("--instance-document", type=Path, required=True)
    parser.add_argument("--run-directory", type=Path, required=True)
    parser.add_argument("--operation-id", required=True)
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument("--source-bundle-id", required=True)
    parser.add_argument("--observed-at", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        root = args.installed_root.resolve(strict=True)
        if root != ROOT.resolve(strict=True) or (root / ".git").exists():
            raise ValueError("hybrid ingestion requires its extracted installed package")
        run_directory = args.run_directory.resolve(strict=True)
        if not run_directory.is_dir():
            raise ValueError("hybrid ingestion run directory is unavailable")
        verify_extracted_tree(root)
        recovery = _runtime(args.instance_document)
        resolved = resolve_hybrid_instance(
            package_root=root, recovery=recovery, entrypoint="manual",
        )
        peer = JsonlPeer(run_directory)
        drive = CodexDrivePort(peer)
        storage = CodexDriveCreateOnlyStorage(
            drive, scratch_directory=run_directory / "storage-scratch",
        )
        capture = SourceByteCapture()
        staged = stage_connected_ingestion(
            installed_root=root, resolved=resolved, run_directory=run_directory,
            gmail=CodexGmailPort(peer), semantic=CodexSemanticPort(peer),
            capture=capture,
        )
        committed = commit_ingestion(
            storage=storage, resolved=resolved, staged=staged, capture=capture,
            identity=args.source_bundle_id, operation_id=args.operation_id,
            attempt_id=args.attempt_id,
            source_commit=recovery["bootstrap"]["source_identity"]["commit"],
            serialization={
                "mode": "attended_single_writer",
                "evidence": {
                    "actor_id": "installed-manual-ingestion",
                    "attempt_id": args.attempt_id,
                    "scheduler_inactive": True,
                    "competing_mutators_excluded": True,
                    "observed_at": args.observed_at,
                },
            },
            installed_root=root,
        )
        evidence = {
            "schema_version": 1,
            "outcome": "HYBRID_INGESTION_COMMITTED",
            "generation": committed.checkpoint.transaction.working.recovery["current"]["generation"],
            "source_bundle_sha256": committed.publication.source["bundle_sha256"],
            "source_bundle_reference": committed.publication.source["bundle_reference"],
            "catalog_index_reference": committed.checkpoint.transaction.durable_reference(
                "data/source-catalog-index.json"
            ).as_mapping(),
            "facts_reference": committed.checkpoint.transaction.durable_reference(
                "data/facts.json"
            ).as_mapping(),
            "completed_unit_count": len(staged.result.completed_units),
            "fact_count": len(committed.publication.facts["facts"]),
            "raw_message_count": len(capture.messages),
            "attachment_count": len(capture.attachments),
            "direct_resource_count": len(capture.resources),
            "eligible_cursor_advanced": False,
        }
        output = canonical_json_bytes(evidence)
        descriptor = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(output)
            handle.flush()
            os.fsync(handle.fileno())
    except Exception as exc:
        print(f"blocked: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({
        "outcome": "HYBRID_INGESTION_COMMITTED",
        "evidence_sha256": sha256_bytes(output),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
