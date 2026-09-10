#!/usr/bin/env python3
"""Verify an admitted package, then run its concrete connected daily operation."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from school_os.bundles import BundleError, read_bundle
from school_os.contracts import sha256_bytes
from school_os.package import PackageError, verify_extracted_tree


def _private_runtime_bytes(path_value: object, *, document_path: Path, label: str) -> bytes:
    if not isinstance(path_value, str):
        raise ValueError(f"installed {label} path is invalid")
    path = Path(path_value)
    try:
        if path.parent.resolve(strict=True) != document_path.parent.resolve(strict=True):
            raise ValueError(f"installed {label} path escapes its private run directory")
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"installed {label} file is unavailable")
        return path.read_bytes()
    except OSError as exc:
        raise ValueError(f"cannot read installed {label}: {exc}") from exc


def _runtime_document(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read installed instance document: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("installed instance document has an unsupported shape")
    if value.get("schema_version") == 1:
        if set(value) != {"schema_version", "root_reference", "manifest", "manifest_reference", "admission_reference"}:
            raise ValueError("installed instance document has an unsupported shape")
        return value
    required = {
        "bootstrap", "bootstrap_reference", "current", "current_reference", "layout",
        "root_reference", "schema_version", "settings_path", "settings_sha256",
        "state_path", "state_sha256",
    }
    if value.get("schema_version") != 2 or value.get("layout") != "hybrid-bundle-v1" or set(value) != required:
        raise ValueError("installed instance document has an unsupported shape")
    settings = _private_runtime_bytes(value["settings_path"], document_path=path, label="settings")
    state_bytes = _private_runtime_bytes(value["state_path"], document_path=path, label="state bundle")
    if sha256_bytes(settings) != value.get("settings_sha256") or sha256_bytes(state_bytes) != value.get("state_sha256"):
        raise ValueError("installed hybrid runtime bytes disagree with their hashes")
    try:
        state = read_bundle(state_bytes, expected_kind="state")
    except BundleError as exc:
        raise ValueError(f"installed hybrid state bundle is invalid: {exc}") from exc
    current = value["current"]
    bootstrap = value["bootstrap"]
    if (
        not isinstance(current, dict) or not isinstance(bootstrap, dict)
        or bootstrap.get("root_reference") != value["root_reference"]
        or bootstrap.get("settings_sha256") != value["settings_sha256"]
        or current.get("state", {}).get("bundle_sha256") != value["state_sha256"]
    ):
        raise ValueError("installed hybrid runtime bindings disagree")
    return {
        "bootstrap": bootstrap,
        "bootstrap_reference": value["bootstrap_reference"],
        "current": current,
        "current_reference": value["current_reference"],
        "settings": settings,
        "state_bundle": state_bytes,
        "state": state,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--installed-root", type=Path, required=True)
    parser.add_argument("--operation", choices=("daily-run",), required=True)
    parser.add_argument("--entrypoint", choices=("manual", "scheduled"), required=True)
    parser.add_argument("--operation-id", required=True)
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument("--run-directory", type=Path, required=True)
    parser.add_argument("--instance-reference", required=True)
    parser.add_argument("--instance-document", type=Path)
    parser.add_argument("--scheduler-admitted", action="store_true")
    parser.add_argument("--delivery-variant")
    parser.add_argument("--preview-only", action="store_true")
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args(argv)
    try:
        root = args.installed_root.resolve(strict=True)
        if root != ROOT.resolve(strict=True) or os.environ.get("SCHOOL_OS_INSTALLED_ROOT") not in {None, str(root)}:
            raise ValueError("installed entrypoint root differs from its executable package")
        if (root / ".git").exists() or not args.run_directory.resolve(strict=True).is_dir():
            raise ValueError("installed entrypoint requires an extracted package and private run directory")
        verify_extracted_tree(root)
        import school_os
        module_path = Path(school_os.__file__ or "").resolve(strict=True)
        module_path.relative_to(root)
    except (OSError, PackageError, ValueError) as exc:
        print(f"blocked: {exc}", file=sys.stderr)
        return 1
    evidence = {"installed_root": str(root), "operation_id": args.operation_id, "attempt_id": args.attempt_id}
    if args.verify_only:
        print(json.dumps({"outcome": "INSTALLED_ENTRYPOINT_VERIFIED", **evidence}, sort_keys=True))
        return 0
    if args.instance_document is None:
        print("blocked: installed execution requires its admitted instance document", file=sys.stderr)
        return 1
    try:
        from school_os.codex_bridge import CodexDrivePort, CodexGmailPort, CodexSemanticPort, CodexSheetsPort, JsonlPeer
        from school_os.connected_daily import ConnectedDailyRuntime
        document = _runtime_document(args.instance_document)
        if "manifest" in document and document["root_reference"] != document["manifest"].get("instance_root_reference"):
            raise ValueError("installed instance document root disagrees with its manifest")
        peer = JsonlPeer(args.run_directory)
        result = ConnectedDailyRuntime(
            installed_root=root, recovery=document, run_directory=args.run_directory,
            drive=CodexDrivePort(peer), gmail=CodexGmailPort(peer),
            sheets=CodexSheetsPort(peer), semantic=CodexSemanticPort(peer),
        ).run(
            entrypoint=args.entrypoint, operation_id=args.operation_id,
            attempt_id=args.attempt_id, scheduler_admitted=args.scheduler_admitted,
            delivery_variant=args.delivery_variant,
            preview_only=args.preview_only,
        )
    except Exception as exc:
        print(f"blocked: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"instance": args.instance_reference, "operation_id": result.operation_id, "attempt_id": result.attempt_id, "outcome": result.outcome, "completed_phases": list(result.completed_phases)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
