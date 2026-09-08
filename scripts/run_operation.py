#!/usr/bin/env python3
"""Run synthetic conformance input or verify a Codex bridge bootstrap read.

``--stage-results`` is solely synthetic and cannot be combined with the host
bridge, a bootstrap reference, or a real entrypoint.  ``--host-jsonl`` verifies
only the exact bootstrap identity and readback through the finite bridge.  It is
not a connected daily executor or runtime-readiness claim.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import json
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from school_os.capabilities import CapabilityError, qualify_bootstrap_read
from school_os.codex_bridge import BridgeError, CodexDrivePort, JsonlPeer
from school_os.contracts import canonical_json_bytes, sha256_bytes
from school_os.daily import DailyError, PHASES, run_daily


def _object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DailyError(f"cannot read {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise DailyError(f"{label} must be a JSON object")
    return value


def _verified_bootstrap_bytes(
    metadata: Any, fetched: Any, expected_object_id: str,
) -> bytes:
    if (
        not isinstance(metadata, Mapping) or not isinstance(fetched, Mapping)
        or metadata.get("id") != expected_object_id
        or fetched.get("id") != expected_object_id
    ):
        raise DailyError("bootstrap metadata/content identity disagrees")
    encoded = fetched.get("b64_string")
    fetched_size = fetched.get("file_size_bytes")
    if not isinstance(encoded, str) or not encoded:
        raise DailyError("bootstrap fetch lacks complete raw base64 bytes")
    if isinstance(fetched_size, bool) or not isinstance(fetched_size, int) or fetched_size < 1:
        raise DailyError("bootstrap fetch lacks a valid complete-byte size")
    try:
        content = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise DailyError("bootstrap raw bytes are not valid base64") from exc
    if len(content) != fetched_size:
        raise DailyError("bootstrap raw byte length disagrees with fetch metadata")
    metadata_size = metadata.get("size")
    if isinstance(metadata_size, int) and not isinstance(metadata_size, bool):
        observed_metadata_size = metadata_size
    elif isinstance(metadata_size, str) and metadata_size.isdigit():
        observed_metadata_size = int(metadata_size)
    else:
        raise DailyError("bootstrap metadata lacks an exact byte size")
    if observed_metadata_size != len(content):
        raise DailyError("bootstrap raw byte length disagrees with Drive metadata")
    if fetched.get("is_empty") is True:
        raise DailyError("bootstrap fetch contradicts its nonempty raw bytes")
    return content


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", required=True, help="resolved instance reference for audit output")
    parser.add_argument("--operation", required=True, choices=("daily-run",))
    parser.add_argument("--entrypoint", choices=("manual", "scheduled"))
    parser.add_argument("--profile", type=Path, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--stage-results", type=Path, help="synthetic-only complete phase results")
    mode.add_argument("--host-jsonl", type=Path, metavar="RUN_DIR", help="private mode-0700 Codex bridge run directory")
    parser.add_argument("--bootstrap-reference", type=Path, help="private JSON with exact Drive bootstrap id and URL")
    parser.add_argument("--operation-id", required=True)
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument("--scheduler-admitted", action="store_true")
    args = parser.parse_args(argv)

    if args.stage_results is not None:
        if args.host_jsonl is not None or args.bootstrap_reference is not None or args.entrypoint is not None or args.scheduler_admitted:
            parser.error("--stage-results is synthetic and mutually exclusive with host/bootstrap/entrypoint options")
        args.entrypoint = "manual"
    else:
        if args.bootstrap_reference is None or args.entrypoint is None:
            parser.error("--host-jsonl requires --bootstrap-reference and --entrypoint")

    try:
        profile = _object(args.profile, "capability profile")
        schema = _object(ROOT / "schemas" / "capability-profile.schema.json", "capability schema")
        if args.host_jsonl is not None:
            qualify_bootstrap_read(profile, schema, entrypoint=args.entrypoint)
            bootstrap = _object(args.bootstrap_reference, "bootstrap reference")
            if set(bootstrap) != {"object_id", "url"} or not all(isinstance(bootstrap[key], str) and bootstrap[key] for key in bootstrap):
                raise DailyError("bootstrap reference must contain exact nonempty object_id and url")
            peer = JsonlPeer(args.host_jsonl)
            drive = CodexDrivePort(peer)
            metadata = drive.metadata(bootstrap["object_id"], fields="id,name,mimeType,parents,modifiedTime,size")
            fetched = drive.fetch(bootstrap["url"], raw=True, include_base64=True)
            bootstrap_bytes = _verified_bootstrap_bytes(metadata, fetched, bootstrap["object_id"])
            print(json.dumps({
                "instance": args.instance, "operation_id": args.operation_id,
                "attempt_id": args.attempt_id, "outcome": "BOOTSTRAP_READBACK_VERIFIED",
                "bootstrap_evidence_sha256": sha256_bytes(canonical_json_bytes({
                    "object_id": bootstrap["object_id"], "size": len(bootstrap_bytes),
                    "sha256": sha256_bytes(bootstrap_bytes),
                })),
                "entrypoint": args.entrypoint,
            }, sort_keys=True))
            return 0
        stage_results = _object(args.stage_results, "synthetic stage results")
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
            required_capabilities=("storage.read_complete", "mail.search", "tasks.list_complete"),
            scheduler_admission=(lambda: args.scheduler_admitted),
        )
    except (BridgeError, CapabilityError, DailyError) as exc:
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
