#!/usr/bin/env python3
"""Validate an observed capability profile and its requested execution scope."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable

from validate_instance import ContractError, load_manifest, validate


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = ROOT / "schemas" / "capability-profile.schema.json"


def validate_capability_profile(
    profile: dict[str, Any],
    schema: dict[str, Any],
    *,
    required_capabilities: Iterable[str] = (),
    operation: str | None = None,
    execution_surface: str | None = None,
) -> list[str]:
    """Return structural and fail-closed conformance errors for one profile."""
    errors = validate(profile, schema)
    if errors:
        return errors

    capabilities: dict[str, dict[str, Any]] = {}
    for index, record in enumerate(profile["capabilities"]):
        capability_id = record["capability_id"]
        if capability_id in capabilities:
            errors.append(f"$.capabilities[{index}]: duplicate capability_id {capability_id!r}")
        else:
            capabilities[capability_id] = record

    for capability_id in required_capabilities:
        record = capabilities.get(capability_id)
        if record is None:
            errors.append(f"required capability {capability_id!r} is missing")
        elif record["status"] != "available":
            errors.append(
                f"required capability {capability_id!r} is {record['status']!r}, not 'available'"
            )

    if operation is not None and operation not in profile["conformant_operations"]:
        errors.append(f"operation {operation!r} is not declared conformant")

    if execution_surface is not None and profile["execution_surface"] != execution_surface:
        errors.append(
            f"execution surface is {profile['execution_surface']!r}, expected {execution_surface!r}"
        )

    if profile["execution_surface"] == "scheduled":
        if profile["selected_adapters"]["scheduler"] is None:
            errors.append("scheduled profile requires a selected scheduler adapter")
        if profile["scheduler_behavior"] is None:
            errors.append("scheduled profile requires observed scheduler behavior")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile", type=Path)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--required-capability", action="append", default=[])
    parser.add_argument("--operation")
    parser.add_argument("--execution-surface", choices=("interactive", "scheduled"))
    args = parser.parse_args(argv)
    try:
        profile = load_manifest(args.profile)
        schema = json.loads(args.schema.read_text(encoding="utf-8"))
        errors = validate_capability_profile(
            profile,
            schema,
            required_capabilities=args.required_capability,
            operation=args.operation,
            execution_surface=args.execution_surface,
        )
    except (OSError, json.JSONDecodeError, ContractError) as exc:
        print(f"invalid: {exc}", file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"conformant: {args.profile}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
