"""Exact, fail-closed resolution for private storage references.

Names are presentation only.  Operations use opaque object identities together
with kind, ancestor, MIME, and optional version evidence, so lookalike files
cannot be selected by a fresh runtime or recovery process.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Protocol, Sequence

from .contracts import ContractError, load_mapping, validate


class ReferenceError(ValueError):
    """Raised when a reference is malformed, unsafe, mismatched, or ambiguous."""


@dataclass(frozen=True)
class ObjectReference:
    object_id: str
    kind: str
    permitted_ancestor_id: str
    mime_type: str | None = None
    version: str | None = None

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> "ObjectReference":
        allowed = {"object_id", "kind", "permitted_ancestor_id", "mime_type", "version"}
        if set(value) - allowed:
            raise ReferenceError("object reference has unknown fields")
        try:
            reference = cls(
                object_id=value["object_id"],
                kind=value["kind"],
                permitted_ancestor_id=value["permitted_ancestor_id"],
                mime_type=value.get("mime_type"),
                version=value.get("version"),
            )
        except KeyError as exc:
            raise ReferenceError(f"object reference is missing {exc.args[0]!r}") from exc
        if (
            not isinstance(reference.object_id, str)
            or not reference.object_id
            or reference.kind not in {"file", "folder"}
            or not isinstance(reference.permitted_ancestor_id, str)
            or not reference.permitted_ancestor_id
            or reference.mime_type is not None and (not isinstance(reference.mime_type, str) or not reference.mime_type)
            or reference.version is not None and (not isinstance(reference.version, str) or not reference.version)
        ):
            raise ReferenceError("invalid object reference")
        return reference


@dataclass(frozen=True)
class StoredObject:
    object_id: str
    kind: str
    parent_id: str | None
    ancestor_ids: tuple[str, ...]
    mime_type: str | None
    version: str | None
    name: str
    data: bytes | None = None


class ReferenceStorage(Protocol):
    def read(self, object_id: str) -> StoredObject | None:
        """Return exact current metadata (and bytes when applicable) by opaque ID."""

    def list_scoped(self, parent_id: str) -> Sequence[StoredObject]:
        """Return the complete scoped listing for a bounded lookup."""


def _verify_object(
    object_: StoredObject,
    reference: ObjectReference,
    *,
    expected_kind: str | None = None,
    required_mime_type: str | None = None,
    instance_root_id: str | None = None,
) -> StoredObject:
    if object_.object_id != reference.object_id:
        raise ReferenceError("storage returned a different object identity")
    if object_.kind != reference.kind:
        raise ReferenceError("object kind does not match reference")
    if expected_kind is not None and object_.kind != expected_kind:
        raise ReferenceError("object kind does not match operation requirement")
    permitted_ancestor = instance_root_id or reference.permitted_ancestor_id
    if reference.permitted_ancestor_id != permitted_ancestor:
        raise ReferenceError("reference is not permitted under this instance root")
    if permitted_ancestor not in object_.ancestor_ids and object_.parent_id != permitted_ancestor:
        raise ReferenceError("object is outside the permitted instance location")
    expected_mime = required_mime_type or reference.mime_type
    if expected_mime is not None and object_.mime_type != expected_mime:
        raise ReferenceError("object MIME type does not match reference")
    if reference.version is not None and object_.version != reference.version:
        raise ReferenceError("object version evidence does not match reference")
    return object_


def resolve_reference(
    storage: ReferenceStorage,
    reference: ObjectReference,
    *,
    expected_kind: str | None = None,
    required_mime_type: str | None = None,
    instance_root_id: str | None = None,
) -> StoredObject:
    """Resolve one opaque reference and verify every declared identity boundary."""
    object_ = storage.read(reference.object_id)
    if object_ is None:
        raise ReferenceError("referenced object was not found")
    return _verify_object(
        object_,
        reference,
        expected_kind=expected_kind,
        required_mime_type=required_mime_type,
        instance_root_id=instance_root_id,
    )


def discover_unique(
    storage: ReferenceStorage,
    *,
    parent_id: str,
    name: str,
    kind: str,
    mime_type: str | None = None,
) -> StoredObject:
    """Resolve a bootstrap-time scoped name lookup only when exactly one match exists."""
    matches = [
        object_
        for object_ in storage.list_scoped(parent_id)
        if object_.parent_id == parent_id
        and object_.name == name
        and object_.kind == kind
        and (mime_type is None or object_.mime_type == mime_type)
    ]
    if not matches:
        raise ReferenceError("scoped lookup found no matching object")
    if len(matches) != 1:
        raise ReferenceError("scoped lookup is ambiguous")
    return matches[0]


def _safe_recipe_path(raw: str) -> PurePosixPath:
    path = PurePosixPath(raw)
    if not raw or raw.startswith("/") or "\\" in raw or any(part in {"", ".", ".."} for part in path.parts):
        raise ReferenceError(f"unsafe operation recipe path: {raw!r}")
    return path


def load_operation_registry(registry_path: Path, schema_path: Path, installed_root: Path) -> dict[str, str]:
    """Load a registry and prove every recipe is an installed regular payload file."""
    try:
        registry = load_mapping(registry_path)
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, ContractError) as exc:
        raise ReferenceError(f"cannot load operation registry: {exc}") from exc
    errors = validate(registry, schema)
    if errors:
        raise ReferenceError("invalid operation registry: " + "; ".join(errors))
    operations = registry["operations"]
    if not isinstance(operations, dict):
        raise ReferenceError("operation registry operations must be an object")
    root = installed_root.resolve()
    for operation, raw_path in operations.items():
        if not isinstance(operation, str) or not isinstance(raw_path, str):
            raise ReferenceError("operation registry must contain string operation paths")
        path = _safe_recipe_path(raw_path)
        candidate = (root / path).resolve()
        try:
            candidate.relative_to(root)
        except ValueError as exc:
            raise ReferenceError("operation recipe escapes the installed root") from exc
        if candidate.is_symlink() or not candidate.is_file():
            raise ReferenceError(f"operation recipe is not an installed regular file: {raw_path!r}")
    return {name: path for name, path in operations.items() if isinstance(name, str) and isinstance(path, str)}
