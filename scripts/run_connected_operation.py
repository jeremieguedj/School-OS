#!/usr/bin/env python3
"""Verify the recovered installed root before the future connected composition.

This explicit entrypoint prevents a bootstrap process from continuing to import
ambient checkout code.  It intentionally does not implement daily phases.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from school_os.package import PackageError, verify_extracted_tree


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--installed-root", type=Path, required=True)
    parser.add_argument("--operation", choices=("daily-run",), required=True)
    parser.add_argument("--entrypoint", choices=("manual", "scheduled"), required=True)
    parser.add_argument("--operation-id", required=True)
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument("--run-directory", type=Path, required=True)
    parser.add_argument("--instance-reference", required=True)
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
    print("blocked: connected daily composition is not installed", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
