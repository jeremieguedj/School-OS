#!/usr/bin/env python3
"""Qualify and exactly readmit one observed profile into an installed instance."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from school_os.codex_bridge import CodexDrivePort, JsonlPeer
from school_os.connected_daily import readmit_connected_profile
from school_os.contracts import canonical_json_bytes, sha256_bytes
from school_os.package import PackageError, verify_extracted_tree


def _object(path: Path, label: str) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--installed-root", type=Path, required=True)
    parser.add_argument("--instance-document", type=Path, required=True)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--entrypoint", choices=("manual", "scheduled"), required=True)
    parser.add_argument("--run-directory", type=Path, required=True)
    parser.add_argument("--host-jsonl", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        root = args.installed_root.resolve(strict=True)
        if root != ROOT.resolve(strict=True) or (root / ".git").exists():
            raise ValueError("profile readmission requires its exact extracted package")
        verify_extracted_tree(root)
        document = _object(args.instance_document, "installed instance document")
        required = {"schema_version", "root_reference", "manifest", "manifest_reference", "admission_reference"}
        if set(document) != required or document.get("schema_version") != 1 or document["root_reference"] != document["manifest"].get("instance_root_reference"):
            raise ValueError("installed instance document has an unsupported shape")
        result = readmit_connected_profile(
            installed_root=root, recovery=document, run_directory=args.run_directory.resolve(strict=True),
            drive=CodexDrivePort(JsonlPeer(args.host_jsonl)), entrypoint=args.entrypoint,
            profile_data=args.profile.read_bytes(),
        )
        output = canonical_json_bytes(result)
        descriptor = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            with os.fdopen(descriptor, "wb", closefd=False) as handle:
                handle.write(output); handle.flush(); os.fsync(handle.fileno())
        finally:
            os.close(descriptor)
    except (OSError, PackageError, TypeError, ValueError) as exc:
        print(f"blocked: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"outcome": "CONNECTED_PROFILE_READMITTED", "output": str(args.output), "sha256": sha256_bytes(output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
