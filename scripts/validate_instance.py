#!/usr/bin/env python3
"""Validate a School-OS instance manifest using only the Python standard library.

The YAML reader intentionally accepts only the mapping/scalar subset used by the
instance template. Rejecting aliases, tags, sequences, and duplicate keys keeps
validation predictable without adding a runtime YAML dependency.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from school_os.contracts import ContractError, load_mapping as load_manifest, load_mapping_yaml, validate


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument(
        "--schema",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "schemas" / "instance.schema.json",
    )
    args = parser.parse_args(argv)
    try:
        manifest = load_manifest(args.manifest)
        schema = json.loads(args.schema.read_text(encoding="utf-8"))
        errors = validate(manifest, schema)
    except (OSError, json.JSONDecodeError, ContractError) as exc:
        print(f"invalid: {exc}", file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"valid: {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
