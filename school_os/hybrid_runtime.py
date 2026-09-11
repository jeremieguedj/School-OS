"""Shared local handoff helpers for installed hybrid command entrypoints."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .bundles import read_bundle
from .contracts import canonical_json_bytes, sha256_bytes


def write_new(path: Path, data: bytes) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())


def load_runtime(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    document = json.loads(path.read_text(encoding="utf-8"))
    state_bytes = Path(document["state_path"]).read_bytes()
    settings = Path(document["settings_path"]).read_bytes()
    if (
        sha256_bytes(state_bytes) != document["state_sha256"]
        or sha256_bytes(settings) != document["settings_sha256"]
    ):
        raise ValueError("hybrid runtime local byte hashes disagree")
    return document, {
        "bootstrap": document["bootstrap"],
        "bootstrap_reference": document["bootstrap_reference"],
        "current": document["current"],
        "current_reference": document["current_reference"],
        "settings": settings,
        "state_bundle": state_bytes,
        "state": read_bundle(state_bytes, expected_kind="state"),
    }


def updated_runtime(
    document: dict[str, Any], transaction: Any, storage: Any,
    run_directory: Path, label: str,
) -> dict[str, Any]:
    current = transaction.working.recovery["current"]
    state_reference = current["state"]["bundle_reference"]
    state_object = storage.read(state_reference["object_id"])
    if (
        state_object is None or state_object.data is None
        or sha256_bytes(state_object.data) != current["state"]["bundle_sha256"]
    ):
        raise ValueError("hybrid state bundle exact readback disagrees")
    generation = current.get("generation")
    if not isinstance(generation, int) or isinstance(generation, bool) or generation < 1:
        raise ValueError("hybrid current pointer lacks a valid generation")
    path = run_directory / f"{label}-generation-{generation:06d}.state.bundle"
    write_new(path, state_object.data)
    return {
        **document,
        "current": current,
        "current_reference": transaction.working.recovery["current_reference"],
        "state_path": str(path.resolve()),
        "state_sha256": sha256_bytes(state_object.data),
    }


def write_outputs(
    *, output_instance: Path, output_evidence: Path,
    runtime: dict[str, Any], evidence: dict[str, Any],
) -> None:
    write_new(output_instance, canonical_json_bytes(runtime))
    write_new(output_evidence, canonical_json_bytes(evidence))
