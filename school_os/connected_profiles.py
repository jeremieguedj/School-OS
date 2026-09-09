"""Exact Drive-backed capability-profile selection and readmission."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from .capabilities import qualify_execution
from .connected_storage import ArtifactStore, DriveReference, StoredArtifact
from .contracts import canonical_json_bytes, sha256_bytes, validate


class ConnectedProfileError(ValueError):
    """Raised when a selected or newly observed runtime profile is not exact."""


ENTRYPOINTS = ("manual", "scheduled")


def _json(data: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ConnectedProfileError(f"{label} is not UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise ConnectedProfileError(f"{label} must be a JSON object")
    return value


def _pointer(artifact: StoredArtifact) -> dict[str, Any]:
    reference = artifact.reference
    return {
        "object_id": reference.object_id,
        "parent_id": reference.parent_id,
        "mime_type": reference.mime_type,
        "url": reference.url,
        "version": reference.version,
        "sha256": sha256_bytes(artifact.data),
        "byte_length": len(artifact.data),
    }


def _artifact(store: ArtifactStore, value: Any, label: str) -> StoredArtifact:
    required = {"object_id", "parent_id", "mime_type", "url", "version", "sha256", "byte_length"}
    if not isinstance(value, Mapping) or set(value) != required:
        raise ConnectedProfileError(f"{label} has an unsupported exact-reference shape")
    if not all(isinstance(value.get(key), str) and value[key] for key in ("object_id", "parent_id", "mime_type", "url", "version")):
        raise ConnectedProfileError(f"{label} lacks an exact Drive reference")
    if (
        not isinstance(value.get("sha256"), str)
        or len(value["sha256"]) != 64
        or isinstance(value.get("byte_length"), bool)
        or not isinstance(value["byte_length"], int)
        or value["byte_length"] < 0
    ):
        raise ConnectedProfileError(f"{label} lacks exact byte evidence")
    artifact = store.read(DriveReference(
        value["object_id"], value["parent_id"], value["mime_type"], value["url"], value["version"],
    ))
    if len(artifact.data) != value["byte_length"] or sha256_bytes(artifact.data) != value["sha256"]:
        raise ConnectedProfileError(f"{label} readback differs from its admitted bytes")
    return artifact


def _registry(value: Any) -> dict[str, Any]:
    if (
        not isinstance(value, Mapping)
        or set(value) != {"schema_version", "profiles"}
        or value.get("schema_version") != 1
        or not isinstance(value.get("profiles"), Mapping)
        or set(value["profiles"]) != set(ENTRYPOINTS)
        or any(item is not None and not isinstance(item, Mapping) for item in value["profiles"].values())
    ):
        raise ConnectedProfileError("capability-profile selection has an unsupported shape")
    return {"schema_version": 1, "profiles": {key: value["profiles"][key] for key in ENTRYPOINTS}}


def initial_profile_registry(profile: StoredArtifact, profile_schema: Mapping[str, Any]) -> bytes:
    """Create a selector that retains the truthful setup profile on its one surface."""
    value = _json(profile.data, "setup capability profile")
    if validate(value, dict(profile_schema)):
        raise ConnectedProfileError("setup capability profile is not schema-valid")
    surface = value.get("execution_surface")
    profiles = {key: None for key in ENTRYPOINTS}
    if surface in profiles:
        profiles[surface] = _pointer(profile)
    return canonical_json_bytes({"schema_version": 1, "profiles": profiles})


def select_capability_profile(
    store: ArtifactStore, selection_reference: DriveReference, *, entrypoint: str,
    profile_schema: Mapping[str, Any],
) -> tuple[dict[str, Any], StoredArtifact, StoredArtifact]:
    """Resolve one exact entrypoint profile, including the installed-127 legacy form."""
    if entrypoint not in ENTRYPOINTS:
        raise ConnectedProfileError("capability-profile entrypoint is unsupported")
    selection = store.read(selection_reference.current())
    value = _json(selection.data, "capability-profile selection")
    if not validate(value, dict(profile_schema)):
        if value.get("execution_surface") != entrypoint:
            raise ConnectedProfileError(f"no admitted capability profile is selected for {entrypoint}")
        return value, selection, selection
    registry = _registry(value)
    pointer = registry["profiles"][entrypoint]
    if pointer is None:
        raise ConnectedProfileError(f"no admitted capability profile is selected for {entrypoint}")
    profile_artifact = _artifact(store, pointer, f"{entrypoint} capability profile")
    profile = _json(profile_artifact.data, f"{entrypoint} capability profile")
    errors = validate(profile, dict(profile_schema))
    if errors or profile.get("execution_surface") != entrypoint:
        raise ConnectedProfileError(f"selected {entrypoint} capability profile is invalid")
    return profile, profile_artifact, selection


def readmit_capability_profile(
    store: ArtifactStore, *, instance_root: DriveReference,
    selection_reference: DriveReference, entrypoint: str, profile_data: bytes,
    profile_schema: Mapping[str, Any], required_capabilities: tuple[str, ...],
) -> dict[str, Any]:
    """Qualify, preserve, select, and read back one independently observed profile."""
    if entrypoint not in ENTRYPOINTS:
        raise ConnectedProfileError("capability-profile entrypoint is unsupported")
    candidate = _json(profile_data, "observed capability profile")
    if candidate.get("evidence_class") != "observed":
        raise ConnectedProfileError("readmission requires observed capability evidence")
    qualify_execution(
        candidate, dict(profile_schema), operation="daily-run", entrypoint=entrypoint,
        required_capabilities=required_capabilities,
    )
    selection = store.read(selection_reference.current())
    current = _json(selection.data, "capability-profile selection")
    if not validate(current, dict(profile_schema)):
        legacy_name = f"state/capability-profiles/{current['execution_surface']}-{sha256_bytes(selection.data)}.json"
        legacy = store.write_immutable(instance_root, legacy_name, selection.data, selection.reference.mime_type)
        profiles: dict[str, Any] = {key: None for key in ENTRYPOINTS}
        if current.get("execution_surface") in profiles:
            profiles[current["execution_surface"]] = _pointer(legacy)
        registry = {"schema_version": 1, "profiles": profiles}
    else:
        registry = _registry(current)
    digest = sha256_bytes(profile_data)
    name = f"state/capability-profiles/{entrypoint}-{digest}.json"
    admitted = store.write_immutable(instance_root, name, profile_data, selection.reference.mime_type)
    registry["profiles"][entrypoint] = _pointer(admitted)
    written = store.replace(
        selection.reference, canonical_json_bytes(registry), selection.reference.mime_type,
    )
    selected, selected_artifact, readback = select_capability_profile(
        store, written.reference, entrypoint=entrypoint, profile_schema=profile_schema,
    )
    if readback.data != canonical_json_bytes(registry) or selected != candidate or selected_artifact.data != profile_data:
        raise ConnectedProfileError("capability-profile readmission did not read back exactly")
    return {
        "entrypoint": entrypoint,
        "profile_id": selected["profile_id"],
        "profile": _pointer(selected_artifact),
        "selection": _pointer(readback),
    }
