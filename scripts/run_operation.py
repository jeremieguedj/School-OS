#!/usr/bin/env python3
"""Run an injected synthetic daily operation through the shared core runner.

This is a deliberately thin Python entrypoint. A provider-capable host binds
real selected adapters and stage callables; this repository does not contain
authenticated provider adapters. ``--stage-results`` exists solely for the
synthetic conformance path and never contacts a provider.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from school_os.capabilities import CapabilityError
from school_os.daily import DailyError, PHASES, run_daily


def _object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DailyError(f"cannot read {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise DailyError(f"{label} must be a JSON object")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", required=True, help="resolved instance reference for audit output")
    parser.add_argument("--operation", required=True, choices=("daily-run",))
    parser.add_argument("--entrypoint", required=True, choices=("manual", "scheduled"))
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--stage-results", type=Path, required=True)
    parser.add_argument("--operation-id", required=True)
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument("--scheduler-admitted", action="store_true")
    args = parser.parse_args(argv)

    try:
        profile = _object(args.profile, "capability profile")
        stage_results = _object(args.stage_results, "synthetic stage results")
        schema = _object(ROOT / "schemas" / "capability-profile.schema.json", "capability schema")
        missing = [phase for phase in PHASES if phase not in stage_results]
        if missing:
            raise DailyError("synthetic stage results missing required phase(s): " + ", ".join(missing))
        stages = {
            phase: (lambda _previous, result=dict(stage_results[phase]): result)
            for phase in PHASES
        }
        result = run_daily(
            profile=profile,
            capability_schema=schema,
            entrypoint=args.entrypoint,
            operation_id=args.operation_id,
            attempt_id=args.attempt_id,
            stages=stages,
            scheduler_admission=(lambda: args.scheduler_admitted),
        )
    except (CapabilityError, DailyError) as exc:
        print(f"blocked: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({
        "instance": args.instance,
        "operation_id": result.operation_id,
        "attempt_id": result.attempt_id,
        "outcome": result.outcome,
        "completed_phases": list(result.completed_phases),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
