#!/usr/bin/env python3
"""Create a validated local School-OS instance candidate without provider effects.

``answers.json`` supplies confirmed values plus paths to an already extracted,
verified package and its release archive. ``references.json`` supplies observed
object-reference evidence and expected returned object identities. The command
does not contact a provider or create objects; a storage-capable installer must
perform and verify those writes with ``school_os.install.verify_candidate_readback``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from school_os.install import InstallationError, scaffold_instance


def _load_object(path: Path, label: str) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise InstallationError(f"cannot read {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise InstallationError(f"{label} must be a JSON object")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--answers", required=True, type=Path)
    parser.add_argument("--references", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        manifest = scaffold_instance(_load_object(args.answers, "answers"), _load_object(args.references, "references"), args.output)
    except InstallationError as exc:
        print(f"invalid: {exc}", file=sys.stderr)
        return 1
    print(f"candidate: {args.output}")
    for path, record in sorted(manifest["files"].items()):
        print(f"{path}: {record['sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
