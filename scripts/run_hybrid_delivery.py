#!/usr/bin/env python3
"""Advance one installed hybrid run through ordered final brief delivery."""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from school_os.codex_bridge import CodexDrivePort, CodexGmailPort, JsonlPeer  # noqa: E402
from school_os.connected_daily import resolve_hybrid_instance  # noqa: E402
from school_os.connected_setup import CodexDriveCreateOnlyStorage  # noqa: E402
from school_os.contracts import canonical_json_bytes, sha256_bytes  # noqa: E402
from school_os.hybrid_delivery import (  # noqa: E402
    authorize_hybrid_audio, deliver_hybrid_email, prepare_hybrid_delivery,
    record_hybrid_audio,
)
from school_os.hybrid_runtime import load_runtime, updated_runtime, write_new, write_outputs  # noqa: E402
from school_os.package import verify_extracted_tree  # noqa: E402


def _private_json(path: Path, instance_document: Path, label: str) -> dict[str, Any]:
    if path.parent.resolve(strict=True) != instance_document.parent.resolve(strict=True):
        raise ValueError(f"{label} escapes the private runtime directory")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def _serialization(args: argparse.Namespace) -> dict[str, Any]:
    if args.serialization is not None:
        return _private_json(args.serialization, args.instance_document, "serialization evidence")
    if args.entrypoint != "manual":
        raise ValueError("scheduled delivery requires runtime serialization evidence")
    return {
        "mode": "attended_single_writer",
        "evidence": {
            "actor_id": "installed-manual-delivery", "attempt_id": args.phase,
            "scheduler_inactive": True, "competing_mutators_excluded": True,
            "observed_at": args.observed_at,
        },
    }


def _audio_worker(root: Path) -> Any:
    path = root / "automation" / "audio-brief" / "elevenlabs_audio_brief.py"
    spec = importlib.util.spec_from_file_location("school_os_installed_audio_worker", path)
    if spec is None or spec.loader is None:
        raise ValueError("installed audio worker is unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("prepare", "audio", "deliver"))
    parser.add_argument("--installed-root", type=Path, required=True)
    parser.add_argument("--instance-document", type=Path, required=True)
    parser.add_argument("--run-directory", type=Path, required=True)
    parser.add_argument("--observed-at", required=True)
    parser.add_argument("--entrypoint", choices=("manual", "scheduled"), required=True)
    parser.add_argument("--delivery-variant", required=True)
    parser.add_argument("--local-day", required=True)
    parser.add_argument("--output-bundle-id")
    parser.add_argument("--audio-configuration", type=Path)
    parser.add_argument("--serialization", type=Path)
    parser.add_argument("--output-instance", type=Path, required=True)
    parser.add_argument("--output-evidence", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        root = args.installed_root.resolve(strict=True)
        if root != ROOT.resolve(strict=True) or (root / ".git").exists():
            raise ValueError("hybrid delivery requires its extracted installed package")
        verify_extracted_tree(root)
        document, recovery = load_runtime(args.instance_document)
        resolved = resolve_hybrid_instance(
            package_root=root, recovery=recovery, entrypoint=args.entrypoint,
            delivery_variant=args.delivery_variant,
        )
        run_directory = args.run_directory.resolve(strict=True)
        peer = JsonlPeer(run_directory)
        storage = CodexDriveCreateOnlyStorage(
            CodexDrivePort(peer), scratch_directory=run_directory / "storage-scratch",
        )
        serialization = _serialization(args)
        audio_outcome = None
        if args.phase == "prepare":
            if not args.output_bundle_id:
                raise ValueError("delivery prepare requires an output bundle identity")
            advanced = prepare_hybrid_delivery(
                storage=storage, resolved=resolved, installed_root=root,
                local_day=args.local_day, output_identity=args.output_bundle_id,
                serialization=serialization,
            )
        elif args.phase == "audio":
            if args.audio_configuration is None:
                raise ValueError("audio phase requires private audio configuration")
            configuration = _private_json(
                args.audio_configuration, args.instance_document,
                "audio configuration",
            )
            authorized = authorize_hybrid_audio(
                storage=storage, resolved=resolved, installed_root=root,
                local_day=args.local_day, configuration=configuration,
                serialization=serialization,
            )
            if not authorized.audio_call_required:
                advanced = authorized
                audio_outcome = "skipped_empty"
            else:
                manifest_path = run_directory / (
                    "audio-manifest-" + sha256_bytes(authorized.audio_manifest)[:16] + ".json"
                )
                write_new(manifest_path, authorized.audio_manifest)
                resolved.state = authorized.transaction
                worker = _audio_worker(root)
                api_key = os.environ.get("ELEVENLABS_API_KEY")
                if not api_key:
                    audio_outcome = "unavailable"
                    advanced = record_hybrid_audio(
                        storage=storage, resolved=resolved, installed_root=root,
                        outcome=audio_outcome, serialization=serialization,
                    )
                else:
                    try:
                        manifest = json.loads(authorized.audio_manifest)
                        inputs, _omitted = worker.build_inputs(manifest)
                        worker.validate_voice_ids(inputs, api_key)
                        body = worker.request_audio(inputs, manifest["run_date"], api_key)
                        audio_directory = run_directory / (
                            "audio-output-" + sha256_bytes(authorized.audio_manifest)[:16]
                        )
                        audio_directory.mkdir(mode=0o700)
                        output, _digest = worker.write_fresh_mp3(
                            audio_directory, manifest["run_date"], body,
                        )
                        audio_outcome = "verified"
                        advanced = record_hybrid_audio(
                            storage=storage, resolved=resolved, installed_root=root,
                            outcome=audio_outcome, serialization=serialization,
                            audio_identity="audio-" + sha256_bytes(body),
                            filename=output.name, audio_bytes=output.read_bytes(),
                        )
                    except worker.BriefError:
                        audio_outcome = "failed"
                        advanced = record_hybrid_audio(
                            storage=storage, resolved=resolved, installed_root=root,
                            outcome=audio_outcome, serialization=serialization,
                        )
        else:
            advanced = deliver_hybrid_email(
                storage=storage, gmail=CodexGmailPort(peer), resolved=resolved,
                installed_root=root, serialization=serialization,
            )
        updated = updated_runtime(
            document, advanced.transaction, storage, run_directory,
            f"delivery-{args.phase}",
        )
        evidence = {
            "schema_version": 1, "outcome": (
                "DELIVERY_CONFIRMED" if args.phase == "deliver" else "DELIVERY_ADVANCED"
            ),
            "phase": args.phase,
            "generation": advanced.transaction.working.recovery["current"]["generation"],
            "checkpoint_id": advanced.checkpoint["checkpoint_id"],
            "remaining_work": advanced.checkpoint["remaining_work"],
            "delivery_key_sha256": sha256_bytes(advanced.delivery_key.encode("utf-8")),
            "audio_outcome": audio_outcome,
        }
        write_outputs(
            output_instance=args.output_instance,
            output_evidence=args.output_evidence,
            runtime=updated, evidence=evidence,
        )
    except Exception as exc:
        print(f"blocked: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({
        "outcome": evidence["outcome"], "phase": args.phase,
        "evidence_sha256": sha256_bytes(canonical_json_bytes(evidence)),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
