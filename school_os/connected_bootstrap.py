"""Recover one admitted package and hand execution to its installed entrypoint.

This is deliberately only the bootstrap boundary.  It does not compose daily
phases or invoke a provider: a recovered package is verified before the local
process is replaced, and the installed entrypoint reports an explicit blocked
state until the separately owned connected composition exists.
"""

from __future__ import annotations

import os
import re
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlsplit

from .contracts import canonical_json_bytes, sha256_bytes
from .install import (
    InstallationError, extract_hybrid_package, extract_recovered_package,
    recover_create_only_generation, recover_hybrid_generation,
)
from .references import ObjectReference, ReferenceError, ReferenceStorage, resolve_reference
from .connected_storage import ConnectedStorageError


class BootstrapError(ValueError):
    """Raised when the stable bootstrap boundary is incomplete or unsafe."""


_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


@dataclass(frozen=True)
class BootstrapDocument:
    """The only mutable-host input accepted before admitted-package recovery."""

    root_reference: dict[str, Any]
    bootstrap_reference: dict[str, Any]
    bootstrap_url: str

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "BootstrapDocument":
        if not isinstance(value, Mapping) or set(value) != {"root_reference", "bootstrap_reference", "bootstrap_url"}:
            raise BootstrapError("bootstrap document must contain exactly root_reference, bootstrap_reference, and bootstrap_url")
        if not isinstance(value["root_reference"], Mapping) or not isinstance(value["bootstrap_reference"], Mapping):
            raise BootstrapError("bootstrap document references must be objects")
        url = value["bootstrap_url"]
        parsed = urlsplit(url) if isinstance(url, str) and url and not any(char.isspace() for char in url) else None
        if (
            parsed is None or parsed.scheme != "https" or not parsed.netloc or not parsed.hostname
            or parsed.username is not None or parsed.password is not None or parsed.query or parsed.fragment
            or not parsed.path.startswith("/") or url != parsed.geturl()
        ):
            raise BootstrapError("bootstrap_url must be a canonical nonempty HTTPS URL")
        try:
            root = ObjectReference.from_mapping(dict(value["root_reference"]))
            bootstrap = ObjectReference.from_mapping(dict(value["bootstrap_reference"]))
        except ReferenceError as exc:
            raise BootstrapError(f"bootstrap document has an invalid object reference: {exc}") from exc
        if (
            root.kind != "folder" or root.permitted_ancestor_id != root.object_id
            or root.mime_type != "application/vnd.google-apps.folder" or root.version is None
        ):
            raise BootstrapError("root_reference must be a versioned exact Drive folder")
        if (
            bootstrap.kind != "file"
            or bootstrap.permitted_ancestor_id != root.object_id
            or bootstrap.mime_type not in {"text/markdown", "application/json"}
        ):
            raise BootstrapError("bootstrap_reference must be an admitted bootstrap file directly under root_reference")
        return cls(dict(value["root_reference"]), dict(value["bootstrap_reference"]), url)


@dataclass(frozen=True)
class RecoveredEntrypoint:
    """An extracted verified package and its fixed installed executable."""

    root: Path
    entrypoint: Path
    recovery: Mapping[str, Any]


def load_bootstrap_document(path: Path) -> BootstrapDocument:
    import json

    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BootstrapError(f"cannot read bootstrap document: {exc}") from exc
    return BootstrapDocument.from_mapping(value)


def recover_installed_entrypoint(
    storage: ReferenceStorage,
    document: BootstrapDocument,
    *,
    run_directory: Path,
    operation_id: str,
) -> RecoveredEntrypoint:
    """Read the bootstrap by exact ID, recover it, and extract one new package.

    The layout-specific recovery repeats exact reference/hash checks for the
    complete admitted generation.  The preliminary read makes a malformed
    root/bootstrap relationship fail before archive extraction.
    """
    if _IDENTIFIER.fullmatch(operation_id) is None:
        raise BootstrapError("operation_id is not a safe stable identifier")
    try:
        root_reference = ObjectReference.from_mapping(document.root_reference)
        root = storage.read(root_reference.object_id)
        if (
            root is None or root.object_id != root_reference.object_id or root.kind != "folder"
            or root.mime_type != "application/vnd.google-apps.folder"
            or root.version != root_reference.version
        ):
            raise BootstrapError("root Drive metadata does not match the admitted versioned folder")
        bootstrap = ObjectReference.from_mapping(document.bootstrap_reference)
        resolved = resolve_reference(
            storage, bootstrap, expected_kind="file", required_mime_type=bootstrap.mime_type,
            instance_root_id=document.root_reference["object_id"],
        )
        if resolved.parent_id != document.root_reference["object_id"] or resolved.data is None:
            raise BootstrapError("bootstrap readback is not directly contained or lacks exact bytes")
        if bootstrap.mime_type == "application/json":
            recovery = recover_hybrid_generation(
                storage, root_reference=document.root_reference,
                bootstrap_reference=document.bootstrap_reference,
            )
        else:
            recovery = recover_create_only_generation(
                storage, root_reference=document.root_reference,
                bootstrap_reference=document.bootstrap_reference,
            )
        destination = run_directory / f"installed-{operation_id}"
        root = (
            extract_hybrid_package(recovery, destination)
            if bootstrap.mime_type == "application/json"
            else extract_recovered_package(recovery, destination)
        )
    except (InstallationError, ReferenceError, ConnectedStorageError, OSError) as exc:
        raise BootstrapError(f"admitted package recovery failed: {exc}") from exc
    entrypoint = root / "scripts" / "run_connected_operation.py"
    if entrypoint.is_symlink() or not entrypoint.is_file():
        raise BootstrapError("recovered package lacks its fixed connected entrypoint")
    return RecoveredEntrypoint(root, entrypoint, recovery)


def installed_command(
    recovered: RecoveredEntrypoint,
    *,
    operation: str,
    entrypoint: str,
    operation_id: str,
    attempt_id: str,
    run_directory: Path,
    instance_reference: str,
    scheduler_admitted: bool = False,
    preview_only: bool = False,
) -> tuple[str, list[str], dict[str, str]]:
    """Build a no-ambient-import exec invocation for the extracted package."""
    if operation != "daily-run" or entrypoint not in {"manual", "scheduled"}:
        raise BootstrapError("installed handoff has an unsupported operation or entrypoint")
    if preview_only and entrypoint != "manual":
        raise BootstrapError("the installed unsent preview is manual-only")
    if any(_IDENTIFIER.fullmatch(value) is None for value in (operation_id, attempt_id)):
        raise BootstrapError("installed handoff identifiers are unsafe")
    resolved_run = run_directory.resolve(strict=True)
    if not resolved_run.is_dir():
        raise BootstrapError("installed handoff run directory is unavailable")
    executable = sys.executable
    arguments = [
        executable, str(recovered.entrypoint), "--installed-root", str(recovered.root),
        "--operation", operation, "--entrypoint", entrypoint, "--operation-id", operation_id,
        "--attempt-id", attempt_id, "--run-directory", str(resolved_run),
        "--instance-reference", instance_reference,
    ]
    if scheduler_admitted:
        arguments.append("--scheduler-admitted")
    if preview_only:
        arguments.append("--preview-only")
    recovery = recovered.recovery
    if isinstance(recovery, Mapping) and isinstance(recovery.get("manifest"), Mapping):
        document = {
            "schema_version": 1,
            "root_reference": dict(recovery["manifest"]["instance_root_reference"]),
            "manifest": dict(recovery["manifest"]),
            "manifest_reference": dict(recovery["manifest_reference"]),
            "admission_reference": dict(recovery["admission_reference"]),
        }
        runtime_path = resolved_run / f"instance-runtime-{operation_id}-{attempt_id}.json"
        descriptor = os.open(runtime_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            with os.fdopen(descriptor, "wb", closefd=False) as handle:
                handle.write(canonical_json_bytes(document)); handle.flush(); os.fsync(handle.fileno())
        finally:
            os.close(descriptor)
        arguments.extend(["--instance-document", str(runtime_path)])
    elif (
        isinstance(recovery, Mapping)
        and isinstance(recovery.get("bootstrap"), Mapping)
        and isinstance(recovery.get("current"), Mapping)
    ):
        settings = recovery.get("settings")
        state_bundle = recovery.get("state_bundle")
        if not isinstance(settings, bytes) or not isinstance(state_bundle, bytes):
            raise BootstrapError("hybrid recovery lacks exact runtime state/settings bytes")
        prefix = f"instance-runtime-{operation_id}-{attempt_id}"
        settings_path = resolved_run / f"{prefix}.settings.yaml"
        state_path = resolved_run / f"{prefix}.state.bundle"
        for path, data in ((settings_path, settings), (state_path, state_bundle)):
            descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            try:
                with os.fdopen(descriptor, "wb", closefd=False) as handle:
                    handle.write(data); handle.flush(); os.fsync(handle.fileno())
            finally:
                os.close(descriptor)
        bootstrap = recovery["bootstrap"]
        current = recovery["current"]
        document = {
            "bootstrap": dict(bootstrap),
            "bootstrap_reference": dict(recovery["bootstrap_reference"]),
            "current": dict(current),
            "current_reference": dict(recovery["current_reference"]),
            "layout": "hybrid-bundle-v1",
            "root_reference": dict(bootstrap["root_reference"]),
            "schema_version": 2,
            "settings_path": str(settings_path),
            "settings_sha256": sha256_bytes(settings),
            "state_path": str(state_path),
            "state_sha256": sha256_bytes(state_bundle),
        }
        runtime_path = resolved_run / f"{prefix}.json"
        descriptor = os.open(runtime_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            with os.fdopen(descriptor, "wb", closefd=False) as handle:
                handle.write(canonical_json_bytes(document)); handle.flush(); os.fsync(handle.fileno())
        finally:
            os.close(descriptor)
        arguments.extend(["--instance-document", str(runtime_path)])
    environment = {key: value for key, value in os.environ.items() if key not in {"PYTHONPATH", "PYTHONHOME"}}
    environment["PYTHONNOUSERSITE"] = "1"
    environment["SCHOOL_OS_INSTALLED_ROOT"] = str(recovered.root)
    return executable, arguments, environment


def exec_installed_entrypoint(
    recovered: RecoveredEntrypoint,
    *,
    operation: str,
    entrypoint: str,
    operation_id: str,
    attempt_id: str,
    run_directory: Path,
    instance_reference: str,
    scheduler_admitted: bool = False,
    preview_only: bool = False,
    executor: Callable[[str, list[str], Mapping[str, str]], Any] = os.execve,
) -> Any:
    """Replace the bootstrap process; the extracted package becomes authoritative."""
    executable, arguments, environment = installed_command(
        recovered, operation=operation, entrypoint=entrypoint, operation_id=operation_id,
        attempt_id=attempt_id, run_directory=run_directory, instance_reference=instance_reference,
        scheduler_admitted=scheduler_admitted,
        preview_only=preview_only,
    )
    return executor(executable, arguments, environment)
