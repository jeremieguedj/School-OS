"""Deterministic, provider-neutral private-instance candidate scaffolding.

This module writes only a local candidate directory.  A provider-capable
installer must subsequently create the declared files and call
``verify_candidate_readback`` against exact storage readbacks before it records
the manifest as verified.  Supplying a JSON reference is therefore not treated
as proof that a provider object exists.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import tempfile
import tarfile
from pathlib import Path
from typing import Any, Mapping, Protocol

from .bundles import BundleEntry, BundleError, build_bundle, read_bundle
from .contracts import ContractError, canonical_json_bytes, dump_mapping_yaml, load_mapping, load_mapping_yaml, sha256_bytes, validate
from .package import PackageError, verify_extracted_tree, verify_release_archive
from .references import ObjectReference, ReferenceError, ReferenceStorage, StoredObject, discover_unique, resolve_reference


class InstallationError(ValueError):
    """Raised when candidate inputs or readback evidence are incomplete."""


MANIFEST_PATH = "state/installation-manifest.json"
ADMISSION_PATH = "state/installation-admission.json"
BOOTSTRAP_PATH = "BOOTSTRAP.md"
FILE_MAP_PATH = "state/file-map.yaml"
OPERATION_STATE_PATH = "state/operation-state.json"
PACKAGE_ARCHIVE_PATH = "system/package/release.archive"
PACKAGE_CHECKSUMS_PATH = "system/package/SHA256SUMS"
HYBRID_BOOTSTRAP_PATH = "BOOTSTRAP.json"
HYBRID_PACKAGE_PATH = "package.tar.gz"
HYBRID_SETTINGS_PATH = "settings.yaml"
HYBRID_CURRENT_PATH = "CURRENT.json"
INITIAL_STATE_PATH = "state-000001.bundle"
STATE_BUNDLE_MIME = "application/x-tar"
JSON_MIME = "application/json"
_PACKAGE_MIME_TYPES = frozenset({
    "application/gzip", "application/x-gzip", "application/octet-stream",
})
MANAGED_PATHS = (
    "instance.yaml",
    "config/household.yaml",
    "config/integrations.yaml",
    "config/policies.yaml",
    "config/daily-run-personal-values.md",
    FILE_MAP_PATH,
    OPERATION_STATE_PATH,
    PACKAGE_ARCHIVE_PATH,
    PACKAGE_CHECKSUMS_PATH,
)
DAILY_REFERENCE_KINDS = {
    "source_checkpoint": "file",
    "source_catalog_folder": "folder",
    "source_catalog_index": "file",
    "canonical_action_register": "file",
    "guidelines": "file",
    "rolling_updates": "file",
    "brief_template": "file",
    "delivery_state": "file",
    "final_run_checkpoint": "file",
    "runtime_profile": "file",
}
INTEGRATION_REFERENCE_KINDS = {
    "source_scope": "file",
    "delivery_configuration": "file",
    "task_provider_selector": "file",
}


def managed_mime_type(path: str) -> str:
    """Return the MIME Drive reports for each managed filename."""
    if path.endswith(".json"):
        return "application/json"
    if path.endswith(".md"):
        return "text/markdown"
    return "application/octet-stream"


class CreateOnlyStorage(ReferenceStorage, Protocol):
    """Storage surface for installation generations that may never replace bytes."""

    def create_file(self, parent_id: str, name: str, data: bytes, mime_type: str) -> StoredObject: ...


def _hybrid_reference(object_: StoredObject, root_id: str, *, include_version: bool = True) -> dict[str, Any]:
    """Return an exact direct-child reference from one verified write/read receipt."""
    if (
        object_.kind != "file" or object_.parent_id != root_id
        or tuple(object_.ancestor_ids) != (root_id,) or object_.data is None
        or not object_.object_id or not object_.mime_type
    ):
        raise InstallationError("hybrid installation object is not a complete direct-root file")
    reference: dict[str, Any] = {
        "object_id": object_.object_id,
        "kind": "file",
        "permitted_ancestor_id": root_id,
        "mime_type": object_.mime_type,
    }
    if include_version:
        if not object_.version:
            raise InstallationError("hybrid installation object lacks version evidence")
        reference["version"] = object_.version
    return reference


def _hybrid_create_or_adopt(
    storage: CreateOnlyStorage, *, parent_id: str, name: str, data: bytes,
    mime_type: str, admitted_mime_types: frozenset[str] | None = None,
) -> StoredObject:
    """Create once and validate its complete receipt without a duplicate read."""
    allowed = admitted_mime_types or frozenset({mime_type})
    try:
        object_ = storage.create_file(parent_id, name, data, mime_type)
    except OSError as exc:
        try:
            object_ = discover_unique(
                storage, parent_id=parent_id, name=name, kind="file",
            )
        except ReferenceError as discover_exc:
            raise InstallationError(f"create outcome is unknown for {name}: {discover_exc}") from exc
    _hybrid_reference(object_, parent_id)
    if object_.name != name or object_.mime_type not in allowed or object_.data != data:
        raise InstallationError(f"hybrid installation create readback differs for {name}")
    return object_


def _bundle_state_reference(object_: StoredObject, root_id: str, data: bytes, identity: str) -> dict[str, Any]:
    return {
        "bundle_reference": _hybrid_reference(object_, root_id),
        "bundle_sha256": sha256_bytes(data),
        "identity": identity,
    }


def _hybrid_read(
    storage: ReferenceStorage, value: Any, *, root_id: str, name: str,
    admitted_mime_types: frozenset[str], require_version: bool = True,
) -> StoredObject:
    try:
        reference = ObjectReference.from_mapping(_require_mapping(value, f"{name} reference"))
    except ReferenceError as exc:
        raise InstallationError(f"invalid {name} reference: {exc}") from exc
    if reference.kind != "file" or reference.permitted_ancestor_id != root_id:
        raise InstallationError(f"{name} reference is outside the instance root")
    object_ = storage.read(reference.object_id)
    if (
        object_ is None or object_.kind != "file" or object_.parent_id != root_id
        or tuple(object_.ancestor_ids) != (root_id,) or object_.name != name
        or object_.mime_type not in admitted_mime_types or object_.data is None
        or (require_version and object_.version != reference.version)
    ):
        raise InstallationError(f"{name} exact readback disagrees with its reference")
    return object_


def _validate_hybrid_package(package: Mapping[str, Any], package_bytes: bytes) -> dict[str, Any]:
    required = {"version", "source_identity", "archive_sha256", "inventory_sha256"}
    if not isinstance(package, Mapping) or set(package) != required:
        raise InstallationError("hybrid package evidence has an unsupported shape")
    source = package.get("source_identity")
    if (
        not isinstance(package.get("version"), str) or not package["version"]
        or not isinstance(source, Mapping) or set(source) != {"repository", "commit"}
        or not isinstance(source.get("repository"), str) or not source["repository"]
        or re.fullmatch(r"[0-9a-f]{40}", source.get("commit", "")) is None
        or re.fullmatch(r"[0-9a-f]{64}", package.get("inventory_sha256", "")) is None
        or package.get("archive_sha256") != sha256_bytes(package_bytes)
    ):
        raise InstallationError("hybrid package identity or hash is invalid")
    return {
        "version": package["version"],
        "source_identity": dict(source),
        "archive_sha256": package["archive_sha256"],
        "inventory_sha256": package["inventory_sha256"],
    }


def _verify_hybrid_package_bytes(package: Mapping[str, Any], package_bytes: bytes) -> None:
    """Verify package structure/inventory from bytes without a sixth Drive file."""
    with tempfile.TemporaryDirectory(prefix="school-os-hybrid-package-") as temporary:
        base = Path(temporary)
        archive_path = base / HYBRID_PACKAGE_PATH
        sums_path = base / "SHA256SUMS"
        archive_path.write_bytes(package_bytes)
        sums_path.write_text(
            f"{package['archive_sha256']}  {HYBRID_PACKAGE_PATH}\n", encoding="utf-8",
        )
        errors = verify_release_archive(archive_path, sums_path, package["version"])
        if errors:
            raise InstallationError("hybrid package verification failed: " + "; ".join(errors))
        try:
            with tarfile.open(archive_path, "r:gz") as archive:
                member = archive.getmember(
                    f"School-OS-{package['version']}/RELEASE-INVENTORY.sha256"
                )
                stream = archive.extractfile(member)
                inventory = stream.read() if stream is not None else b""
        except (KeyError, OSError, tarfile.TarError) as exc:
            raise InstallationError(f"hybrid package inventory is unavailable: {exc}") from exc
        if sha256_bytes(inventory) != package["inventory_sha256"]:
            raise InstallationError("hybrid package inventory hash disagrees")


def install_hybrid_generation(
    storage: CreateOnlyStorage, *, root_reference: dict[str, Any],
    package: Mapping[str, Any], package_bytes: bytes, settings_bytes: bytes,
    instance_id: str, state_entries: Mapping[str, BundleEntry],
    configuration_fingerprint: str, runtime: Mapping[str, str],
) -> dict[str, Any]:
    """Create the five-file fresh installation and recover it from Drive once."""
    try:
        root = ObjectReference.from_mapping(root_reference)
    except ReferenceError as exc:
        raise InstallationError(f"invalid hybrid instance root: {exc}") from exc
    if root.kind != "folder" or root.permitted_ancestor_id != root.object_id or not root.version:
        raise InstallationError("hybrid instance root must be one exact versioned self-contained folder")
    if not isinstance(package_bytes, bytes) or not isinstance(settings_bytes, bytes) or not settings_bytes:
        raise InstallationError("hybrid package and settings require exact nonempty bytes")
    package_value = _validate_hybrid_package(package, package_bytes)
    _verify_hybrid_package_bytes(package_value, package_bytes)
    if not isinstance(instance_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", instance_id):
        raise InstallationError("hybrid installation lacks a safe instance ID")
    if re.fullmatch(r"[0-9a-f]{64}", configuration_fingerprint) is None:
        raise InstallationError("hybrid configuration fingerprint is invalid")
    if not isinstance(runtime, Mapping) or set(runtime) != {"implementation", "python_version", "dependency_fingerprint"}:
        raise InstallationError("hybrid runtime evidence has an unsupported shape")
    if (
        not all(isinstance(runtime.get(key), str) and runtime[key] for key in ("implementation", "python_version"))
        or re.fullmatch(r"[0-9a-f]{64}", runtime.get("dependency_fingerprint", "")) is None
    ):
        raise InstallationError("hybrid runtime evidence is incomplete")
    settings_sha256 = sha256_bytes(settings_bytes)
    try:
        state_bytes = build_bundle(
            bundle_kind="state", identity="state-000001",
            instance_id=instance_id,
            package_sha256=package_value["archive_sha256"],
            settings_sha256=settings_sha256,
            configuration_fingerprint=configuration_fingerprint,
            entries=state_entries,
        )
    except BundleError as exc:
        raise InstallationError(f"initial state bundle is invalid: {exc}") from exc

    package_object = _hybrid_create_or_adopt(
        storage, parent_id=root.object_id, name=HYBRID_PACKAGE_PATH,
        data=package_bytes, mime_type="application/octet-stream",
        admitted_mime_types=_PACKAGE_MIME_TYPES,
    )
    settings_object = _hybrid_create_or_adopt(
        storage, parent_id=root.object_id, name=HYBRID_SETTINGS_PATH,
        data=settings_bytes, mime_type="application/octet-stream",
    )
    state_object = _hybrid_create_or_adopt(
        storage, parent_id=root.object_id, name=INITIAL_STATE_PATH,
        data=state_bytes, mime_type=STATE_BUNDLE_MIME,
    )
    state_reference = _bundle_state_reference(
        state_object, root.object_id, state_bytes, "state-000001",
    )
    current = {
        "configuration_fingerprint": configuration_fingerprint,
        "generation": 1,
        "package_sha256": package_value["archive_sha256"],
        "previous": None,
        "schema_version": 1,
        "serialization": None,
        "settings_sha256": settings_sha256,
        "state": state_reference,
    }
    current_bytes = canonical_json_bytes(current)
    current_object = _hybrid_create_or_adopt(
        storage, parent_id=root.object_id, name=HYBRID_CURRENT_PATH,
        data=current_bytes, mime_type=JSON_MIME,
    )
    bootstrap = {
        "current_reference": _hybrid_reference(current_object, root.object_id, include_version=False),
        "instance_id": instance_id,
        "package_inventory_sha256": package_value["inventory_sha256"],
        "package_reference": _hybrid_reference(package_object, root.object_id),
        "package_sha256": package_value["archive_sha256"],
        "root_reference": root_reference,
        "runtime": dict(runtime),
        "schema_version": 1,
        "settings_reference": _hybrid_reference(settings_object, root.object_id),
        "settings_sha256": settings_sha256,
        "source_identity": package_value["source_identity"],
        "state_reference": _hybrid_reference(state_object, root.object_id),
        "system_version": package_value["version"],
    }
    _validated(bootstrap, Path(__file__).resolve().parents[1], "bootstrap-descriptor.schema.json", "bootstrap descriptor")
    bootstrap_object = _hybrid_create_or_adopt(
        storage, parent_id=root.object_id, name=HYBRID_BOOTSTRAP_PATH,
        data=canonical_json_bytes(bootstrap), mime_type=JSON_MIME,
    )
    return recover_hybrid_generation(
        storage, root_reference=root_reference,
        bootstrap_reference=_hybrid_reference(bootstrap_object, root.object_id),
    )


def recover_hybrid_generation(
    storage: ReferenceStorage, *, root_reference: dict[str, Any],
    bootstrap_reference: dict[str, Any],
) -> dict[str, Any]:
    """Recover exactly one admitted five-file generation with one read per object."""
    try:
        root = ObjectReference.from_mapping(root_reference)
    except ReferenceError as exc:
        raise InstallationError(f"invalid hybrid instance root: {exc}") from exc
    if root.kind != "folder" or root.permitted_ancestor_id != root.object_id:
        raise InstallationError("hybrid instance root must be a self-contained folder")
    bootstrap_object = _hybrid_read(
        storage, bootstrap_reference, root_id=root.object_id,
        name=HYBRID_BOOTSTRAP_PATH, admitted_mime_types=frozenset({JSON_MIME}),
    )
    bootstrap = _canonical_json_object(bootstrap_object.data or b"", "hybrid bootstrap")
    _validated(bootstrap, Path(__file__).resolve().parents[1], "bootstrap-descriptor.schema.json", "bootstrap descriptor")
    if bootstrap.get("root_reference") != root_reference:
        raise InstallationError("hybrid bootstrap names a different instance root")
    package_object = _hybrid_read(
        storage, bootstrap["package_reference"], root_id=root.object_id,
        name=HYBRID_PACKAGE_PATH, admitted_mime_types=_PACKAGE_MIME_TYPES,
    )
    settings_object = _hybrid_read(
        storage, bootstrap["settings_reference"], root_id=root.object_id,
        name=HYBRID_SETTINGS_PATH, admitted_mime_types=frozenset({"application/octet-stream"}),
    )
    current_object = _hybrid_read(
        storage, bootstrap["current_reference"], root_id=root.object_id,
        name=HYBRID_CURRENT_PATH, admitted_mime_types=frozenset({JSON_MIME}),
        require_version=False,
    )
    current = _canonical_json_object(current_object.data or b"", "current state pointer")
    _validated(current, Path(__file__).resolve().parents[1], "current-state.schema.json", "current state pointer")
    state = _require_mapping(current.get("state"), "current state bundle reference")
    _required_keys(state, {"bundle_reference", "bundle_sha256", "identity"}, "current state bundle reference")
    if state.get("bundle_reference") != bootstrap.get("state_reference") or current.get("generation") != 1:
        raise InstallationError("initial current pointer disagrees with bootstrap state")
    state_object = _hybrid_read(
        storage, state["bundle_reference"], root_id=root.object_id,
        name=INITIAL_STATE_PATH, admitted_mime_types=frozenset({STATE_BUNDLE_MIME}),
    )
    package_bytes = package_object.data or b""
    settings_bytes = settings_object.data or b""
    state_bytes = state_object.data or b""
    if (
        sha256_bytes(package_bytes) != bootstrap.get("package_sha256")
        or sha256_bytes(settings_bytes) != bootstrap.get("settings_sha256")
        or sha256_bytes(state_bytes) != state.get("bundle_sha256")
        or current.get("package_sha256") != bootstrap.get("package_sha256")
        or current.get("settings_sha256") != bootstrap.get("settings_sha256")
    ):
        raise InstallationError("hybrid installation physical bytes disagree with admitted hashes")
    _verify_hybrid_package_bytes({
        "version": bootstrap["system_version"],
        "archive_sha256": bootstrap["package_sha256"],
        "inventory_sha256": bootstrap["package_inventory_sha256"],
    }, package_bytes)
    try:
        verified_state = read_bundle(state_bytes, expected_kind="state")
    except BundleError as exc:
        raise InstallationError(f"current state bundle is invalid: {exc}") from exc
    manifest = verified_state.manifest
    if (
        manifest.get("identity") != state.get("identity")
        or manifest.get("instance_id") != bootstrap.get("instance_id")
        or manifest.get("package_sha256") != bootstrap.get("package_sha256")
        or manifest.get("settings_sha256") != bootstrap.get("settings_sha256")
        or manifest.get("configuration_fingerprint") != current.get("configuration_fingerprint")
        or manifest.get("predecessor") is not None
    ):
        raise InstallationError("current state bundle bindings disagree with bootstrap/current")
    return {
        "bootstrap": bootstrap,
        "bootstrap_reference": dict(bootstrap_reference),
        "current": current,
        "current_reference": _hybrid_reference(current_object, root.object_id),
        "package_archive": package_bytes,
        "settings": settings_bytes,
        "state": verified_state,
    }


def _pinned_archive_name(checksums: bytes, archive_sha256: str) -> str:
    try:
        text = checksums.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise InstallationError("pinned package checksums are not UTF-8") from exc
    lines = text.splitlines(keepends=True)
    if len(lines) != 1 or not lines[0].endswith("\n"):
        raise InstallationError("pinned checksums must contain exactly one archive entry")
    fields = lines[0][:-1].split("  ", 1)
    if (
        len(fields) != 2 or fields[0] != archive_sha256 or not fields[1]
        or Path(fields[1]).name != fields[1]
    ):
        raise InstallationError("pinned checksums do not declare the exact archive hash and name")
    return fields[1]


def parse_daily_values(data: bytes) -> dict[str, Any]:
    """Read strict YAML front matter from the private daily companion."""
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise InstallationError("daily values must be UTF-8") from exc
    if not text.startswith("---\n"):
        raise InstallationError("daily values must begin with YAML front matter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise InstallationError("daily values front matter is not closed")
    try:
        return load_mapping_yaml(text[4:end])
    except ContractError as exc:
        raise InstallationError(f"invalid daily values front matter: {exc}") from exc


def _schema(package_root: Path, name: str) -> dict[str, Any]:
    try:
        value = json.loads((package_root / "schemas" / name).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise InstallationError(f"cannot load schema {name}: {exc}") from exc
    if not isinstance(value, dict):
        raise InstallationError(f"schema {name} must be an object")
    return value


def _validated(value: Any, package_root: Path, schema_name: str, label: str) -> None:
    errors = validate(value, _schema(package_root, schema_name))
    if errors:
        raise InstallationError(f"invalid {label}: " + "; ".join(errors))


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise InstallationError(f"{label} must be an object")
    return value


def _required_keys(value: dict[str, Any], expected: set[str], label: str) -> None:
    missing = expected - set(value)
    extra = set(value) - expected
    if missing or extra:
        detail = []
        if missing:
            detail.append("missing " + ", ".join(sorted(missing)))
        if extra:
            detail.append("unexpected " + ", ".join(sorted(extra)))
        raise InstallationError(f"{label} has " + "; ".join(detail))


def _reference(value: Any, *, root_id: str, expected_kind: str, label: str) -> dict[str, Any]:
    mapping = _require_mapping(value, label)
    try:
        reference = ObjectReference.from_mapping(mapping)
    except ReferenceError as exc:
        raise InstallationError(f"invalid {label}: {exc}") from exc
    if reference.kind != expected_kind:
        raise InstallationError(f"{label} must reference a {expected_kind}")
    if reference.permitted_ancestor_id != root_id:
        raise InstallationError(f"{label} is not contained by the declared instance root")
    return dict(mapping)


def _contains_placeholder(value: Any) -> bool:
    if isinstance(value, str):
        return "REPLACE_WITH_" in value
    if isinstance(value, dict):
        return any(_contains_placeholder(key) or _contains_placeholder(item) for key, item in value.items())
    if isinstance(value, list):
        return any(_contains_placeholder(item) for item in value)
    return False


def _package_evidence(answers: dict[str, Any]) -> tuple[Path, dict[str, Any]]:
    for key in ("package_root", "package_archive", "package_source_identity"):
        if key not in answers:
            raise InstallationError(f"answers is missing {key!r}")
    if not isinstance(answers["package_root"], str) or not isinstance(answers["package_archive"], str):
        raise InstallationError("package paths must be strings")
    package_root = Path(answers["package_root"])
    archive = Path(answers["package_archive"])
    try:
        tree = verify_extracted_tree(package_root)
    except PackageError as exc:
        raise InstallationError(f"unverified package root: {exc}") from exc
    archive_errors = verify_release_archive(archive, archive.with_name("SHA256SUMS"), tree.version)
    if archive_errors:
        raise InstallationError("unverified package archive: " + "; ".join(archive_errors))
    release = load_mapping(package_root / "release.yaml")
    source = _require_mapping(answers["package_source_identity"], "package_source_identity")
    _required_keys(source, {"repository", "commit"}, "package_source_identity")
    if source.get("repository") != release.get("source_repository"):
        raise InstallationError("package source repository does not match release manifest")
    if not isinstance(source.get("commit"), str) or re.fullmatch(r"[0-9a-f]{40}", source["commit"]) is None:
        raise InstallationError("package source commit must be an exact lower-case SHA-1")
    return package_root.resolve(), {
        "version": tree.version,
        "source_identity": source,
        "archive_sha256": sha256_bytes(archive.read_bytes()),
        "inventory_sha256": tree.inventory_sha256,
    }


def initial_operation_state_bytes(package_root: Path) -> bytes:
    """Return the final, schema-valid idle state before its provider ID exists."""
    operation_state = {
        "checkpoint": None,
        "current_operation": None,
        "last_terminal": None,
        "schema_version": 1,
        "serialization": None,
        "status": "idle",
    }
    _validated(operation_state, package_root, "operation-state.schema.json", "operation state")
    return canonical_json_bytes(operation_state)


def _normalise_inputs(answers: dict[str, Any], references: dict[str, Any], package_root: Path, package: dict[str, Any]) -> tuple[dict[str, bytes], dict[str, Any]]:
    expected_answers = {
        "package_root", "package_archive", "package_source_identity", "instance_id", "release_channel",
        "household", "integrations", "policies", "daily_values",
    }
    _required_keys(answers, expected_answers, "answers")
    if not isinstance(answers["instance_id"], str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", answers["instance_id"]):
        raise InstallationError("instance_id must use a stable portable identifier")
    release = load_mapping(package_root / "release.yaml")
    if answers["release_channel"] != release.get("channel"):
        raise InstallationError("release_channel must match the verified package")

    _required_keys(references, {"instance_root", "observed", "returned_objects"}, "references")
    instance_root = _require_mapping(references["instance_root"], "instance_root")
    try:
        root_reference = ObjectReference.from_mapping(instance_root)
    except ReferenceError as exc:
        raise InstallationError(f"invalid instance_root: {exc}") from exc
    if root_reference.kind != "folder" or root_reference.permitted_ancestor_id != root_reference.object_id:
        raise InstallationError("instance_root must be a self-contained folder reference")
    root_id = root_reference.object_id

    observed = _require_mapping(references["observed"], "observed")
    expected_observed = set(DAILY_REFERENCE_KINDS) | set(INTEGRATION_REFERENCE_KINDS)
    _required_keys(observed, expected_observed, "observed")
    observed_references = {
        role: _reference(observed[role], root_id=root_id, expected_kind=kind, label=f"observed.{role}")
        for role, kind in {**DAILY_REFERENCE_KINDS, **INTEGRATION_REFERENCE_KINDS}.items()
    }
    returned = _require_mapping(references["returned_objects"], "returned_objects")
    _required_keys(returned, set(MANAGED_PATHS), "returned_objects")
    returned_references = {
        path: _reference(returned[path], root_id=root_id, expected_kind="file", label=f"returned_objects.{path}")
        for path in MANAGED_PATHS
    }

    household_answers = _require_mapping(answers["household"], "household")
    household = {"schema_version": 1, **household_answers}
    _validated(household, package_root, "household.schema.json", "household configuration")
    entity_ids = [entity["entity_id"] for entity in household["entities"]]
    orders = [entity["sort_order"] for entity in household["entities"]]
    if len(set(entity_ids)) != len(entity_ids) or len(set(orders)) != len(orders):
        raise InstallationError("household entity IDs and sort_order values must be unique")
    grouping = household["grouping"]
    if grouping["shared_group_id"] not in entity_ids or grouping["unscoped_update_group"] not in entity_ids:
        raise InstallationError("household grouping must name configured entities")

    integration_answers = _require_mapping(answers["integrations"], "integrations")
    _required_keys(integration_answers, {"runtime_adapter", "mail_adapter", "task_adapter", "scheduler_adapter", "audio_adapter", "task_provider_status"}, "integrations")
    integrations = {
        "schema_version": 1,
        "runtime_adapter": integration_answers["runtime_adapter"],
        "mail_adapter": integration_answers["mail_adapter"],
        "task_adapter": integration_answers["task_adapter"],
        "scheduler_adapter": integration_answers["scheduler_adapter"],
        "audio_adapter": integration_answers["audio_adapter"],
        "mail": {
            "source_scope_reference": observed_references["source_scope"],
            "delivery_configuration_reference": observed_references["delivery_configuration"],
        },
        "task_provider": {
            "status": integration_answers["task_provider_status"],
            "selector_reference": observed_references["task_provider_selector"],
        },
    }
    _validated(integrations, package_root, "integrations.schema.json", "integration selection")
    for label, reference in (("mail.source_scope_reference", integrations["mail"]["source_scope_reference"]), ("mail.delivery_configuration_reference", integrations["mail"]["delivery_configuration_reference"]), ("task_provider.selector_reference", integrations["task_provider"]["selector_reference"])):
        _reference(reference, root_id=root_id, expected_kind="file", label=label)

    policy_answers = _require_mapping(answers["policies"], "policies")
    policies = {"schema_version": 1, **policy_answers}
    _validated(policies, package_root, "policies.schema.json", "policy configuration")

    daily_answers = _require_mapping(answers["daily_values"], "daily_values")
    _required_keys(daily_answers, {"presentation"}, "daily_values")
    daily = {
        "schema_version": 1,
        "timezone": household["timezone"],
        "references": {role: observed_references[role] for role in DAILY_REFERENCE_KINDS},
        "presentation": daily_answers["presentation"],
    }
    _validated(daily, package_root, "daily-values.schema.json", "daily values")
    for role, kind in DAILY_REFERENCE_KINDS.items():
        _reference(daily["references"][role], root_id=root_id, expected_kind=kind, label=f"daily values reference {role}")

    version = package["version"]
    instance = {
        "instance_format_version": 1,
        "instance_id": answers["instance_id"],
        "system_version": version,
        "data_schema_version": 2,
        "release_channel": answers["release_channel"],
        "active_release": {
            "version": version,
            "manifest_reference": f"system/releases/{version}/release.yaml",
            "operation_registry_reference": f"system/releases/{version}/core/operations/registry.json",
        },
        "configuration": {
            "household_reference": "config/household.yaml",
            "integrations_reference": "config/integrations.yaml",
            "policies_reference": "config/policies.yaml",
            "daily_run_personal_values_reference": "config/daily-run-personal-values.md",
        },
        "state": {
            "file_map_reference": FILE_MAP_PATH,
            "operation_state_reference": OPERATION_STATE_PATH,
            "operation_checkpoints_reference": "state/operation-checkpoints",
            "installation_manifest_reference": MANIFEST_PATH,
        },
        "last_completed_migration": None,
        "latest_release_seen": {"version": None, "source": None},
    }
    _validated(instance, package_root, "instance.schema.json", "instance manifest")
    prose = (
        "# Daily Run Personal Values\n\n"
        "The machine-readable front matter above is the single private daily companion to the generic operation. "
        "It may customize only the approved references and presentation values. It must not contain adapter identity, provider bindings, credentials, or a replacement operation recipe.\n\n"
        "The generic daily operation still requires provenance, task reconciliation, provider readback, duplicate-delivery prevention, and sent-message verification.\n"
    ).encode("utf-8")
    operation_state_bytes = initial_operation_state_bytes(package_root)
    file_map = {
        "schema_version": 1,
        "mapping_status": "partially_configured",
        "files": {
            "capability_profile": {},
            "operation_state": returned_references[OPERATION_STATE_PATH],
            "operation_checkpoints_folder": {},
            "source_checkpoint": {},
            "current_index": {},
            "source_catalog_folder": {},
            "source_catalog_index": {},
            "canonical_tasks": {},
            "guidelines": {},
            "rolling_updates": {},
            "brief_template": {},
            "family_scope": {},
            "active_task_provider": {},
            "task_sync_state": {},
            "delivery_state": {},
            "final_run_checkpoint": {},
            "manual_run_recipe": {},
            "durable_profiles": {},
        },
    }
    files = {
        "instance.yaml": dump_mapping_yaml(instance),
        "config/household.yaml": dump_mapping_yaml(household),
        "config/integrations.yaml": dump_mapping_yaml(integrations),
        "config/policies.yaml": dump_mapping_yaml(policies),
        "config/daily-run-personal-values.md": b"---\n" + dump_mapping_yaml(daily) + b"---\n\n" + prose,
        FILE_MAP_PATH: dump_mapping_yaml(file_map),
        OPERATION_STATE_PATH: operation_state_bytes,
        PACKAGE_ARCHIVE_PATH: Path(answers["package_archive"]).read_bytes(),
        PACKAGE_CHECKSUMS_PATH: Path(answers["package_archive"]).with_name("SHA256SUMS").read_bytes(),
    }
    if any(_contains_placeholder(load_mapping_yaml(data.decode("utf-8"))) for path, data in files.items() if path.endswith(".yaml")) or b"REPLACE_WITH_" in files["config/daily-run-personal-values.md"]:
        raise InstallationError("candidate contains an unresolved placeholder")
    manifest_package = dict(package)
    manifest_package.update({
        "archive_name": Path(answers["package_archive"]).name,
        "archive_reference": returned_references[PACKAGE_ARCHIVE_PATH],
        "checksums_reference": returned_references[PACKAGE_CHECKSUMS_PATH],
        "checksums_sha256": sha256_bytes(files[PACKAGE_CHECKSUMS_PATH]),
    })
    manifest = {
        "schema_version": 2,
        "verification_status": "candidate",
        "package": manifest_package,
        "instance_root_reference": instance_root,
        "files": {
            path: {"object_reference": returned_references[path], "sha256": sha256_bytes(data)}
            for path, data in sorted(files.items())
        },
    }
    _validated(manifest, package_root, "installation-manifest.schema.json", "installation manifest")
    return files, manifest


def compose_create_only_candidate_payloads(
    answers: dict[str, Any], *, instance_root: dict[str, Any], observed: dict[str, Any], operation_state_reference: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, bytes]]:
    """Compose final candidate bytes after the immutable state object has an ID.

    The returned bytes contain only the supplied, actual operation-state
    reference. Temporary structurally valid references below exist solely to
    reuse input validation while constructing a manifest that is discarded;
    they cannot enter a returned payload or a provider write.
    """
    package_root, package = _package_evidence(answers)
    root_mapping = _require_mapping(instance_root, "instance_root")
    transient_returned = {
        path: {
            "object_id": f"transient-create-only-{index}",
            "kind": "file",
            "permitted_ancestor_id": root_mapping.get("object_id", ""),
            "mime_type": managed_mime_type(path),
            "version": "transient",
        }
        for index, path in enumerate(MANAGED_PATHS, 1)
    }
    transient_returned[OPERATION_STATE_PATH] = operation_state_reference
    files, _discarded_manifest = _normalise_inputs(
        answers,
        {"instance_root": root_mapping, "observed": observed, "returned_objects": transient_returned},
        package_root,
        package,
    )
    return package, files


def validate_candidate(candidate_root: Path, package_root: Path) -> dict[str, Any]:
    """Validate local candidate bytes and all declared object-reference evidence."""
    try:
        manifest = json.loads((candidate_root / MANIFEST_PATH).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise InstallationError(f"cannot read installation manifest: {exc}") from exc
    _validated(manifest, package_root, "installation-manifest.schema.json", "installation manifest")
    try:
        root_ref = ObjectReference.from_mapping(_require_mapping(manifest["instance_root_reference"], "instance_root_reference"))
    except ReferenceError as exc:
        raise InstallationError(f"invalid instance root reference: {exc}") from exc
    if root_ref.kind != "folder" or root_ref.permitted_ancestor_id != root_ref.object_id:
        raise InstallationError("instance root reference is not a self-contained folder")
    root_id = root_ref.object_id
    expected_paths = set(MANAGED_PATHS)
    if set(manifest["files"]) != expected_paths:
        raise InstallationError("installation manifest does not declare exactly the managed candidate files")
    for path in MANAGED_PATHS:
        data = (candidate_root / path).read_bytes()
        record = _require_mapping(manifest["files"][path], f"installation manifest file {path}")
        _required_keys(record, {"object_reference", "sha256"}, f"installation manifest file {path}")
        _reference(record["object_reference"], root_id=root_id, expected_kind="file", label=f"manifest reference {path}")
        if record["sha256"] != sha256_bytes(data):
            raise InstallationError(f"installation manifest hash disagrees for {path}")
        if b"REPLACE_WITH_" in data:
            raise InstallationError(f"unresolved placeholder in {path}")
    package = _require_mapping(manifest["package"], "installation manifest package")
    for path, field in (
        (PACKAGE_ARCHIVE_PATH, "archive_reference"),
        (PACKAGE_CHECKSUMS_PATH, "checksums_reference"),
    ):
        reference = _reference(package[field], root_id=root_id, expected_kind="file", label=f"package {field}")
        if reference != manifest["files"][path]["object_reference"]:
            raise InstallationError(f"package {field} disagrees with admitted file")
    if package["archive_sha256"] != sha256_bytes((candidate_root / PACKAGE_ARCHIVE_PATH).read_bytes()):
        raise InstallationError("package archive hash disagrees with admitted file")
    if package["checksums_sha256"] != sha256_bytes((candidate_root / PACKAGE_CHECKSUMS_PATH).read_bytes()):
        raise InstallationError("package checksums hash disagrees with admitted file")
    _validated(load_mapping(candidate_root / "instance.yaml"), package_root, "instance.schema.json", "instance manifest")
    _validated(load_mapping(candidate_root / "config" / "household.yaml"), package_root, "household.schema.json", "household configuration")
    _validated(load_mapping(candidate_root / "config" / "integrations.yaml"), package_root, "integrations.schema.json", "integration selection")
    _validated(load_mapping(candidate_root / "config" / "policies.yaml"), package_root, "policies.schema.json", "policy configuration")
    _validated(parse_daily_values((candidate_root / "config" / "daily-run-personal-values.md").read_bytes()), package_root, "daily-values.schema.json", "daily values")
    _validated(load_mapping(candidate_root / OPERATION_STATE_PATH), package_root, "operation-state.schema.json", "operation state")
    file_map = load_mapping(candidate_root / FILE_MAP_PATH)
    if file_map.get("files", {}).get("operation_state") != manifest["files"][OPERATION_STATE_PATH]["object_reference"]:
        raise InstallationError("file map operation state reference disagrees with installation manifest")
    return manifest


def scaffold_instance(answers: dict[str, Any], references: dict[str, Any], output: Path) -> dict[str, Any]:
    """Build and read back a new local candidate; never create provider objects."""
    if output.exists():
        raise InstallationError("output candidate directory already exists")
    package_root, package = _package_evidence(answers)
    files, manifest = _normalise_inputs(answers, references, package_root, package)
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix="school-os-candidate-", dir=output.parent))
    try:
        for relative, data in files.items():
            path = staging / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        manifest_path = staging / MANIFEST_PATH
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_bytes(canonical_json_bytes(manifest))
        validate_candidate(staging, package_root)
        os.replace(staging, output)
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return validate_candidate(output, package_root)


def verify_candidate_readback(candidate_root: Path, package_root: Path, storage: ReferenceStorage) -> dict[str, Any]:
    """Prove exact provider objects and bytes before accepting a candidate install."""
    manifest = validate_candidate(candidate_root, package_root)
    try:
        for path, record in manifest["files"].items():
            reference = ObjectReference.from_mapping(record["object_reference"])
            object_ = resolve_reference(storage, reference, expected_kind="file", instance_root_id=manifest["instance_root_reference"]["object_id"])
            if object_.data != (candidate_root / path).read_bytes():
                raise InstallationError(f"provider readback bytes disagree for {path}")
    except ReferenceError as exc:
        raise InstallationError(f"provider readback reference failed: {exc}") from exc
    accepted = dict(manifest)
    accepted["verification_status"] = "verified"
    return accepted


def _stored_reference(object_: StoredObject, root_id: str) -> dict[str, Any]:
    if object_.kind != "file" or object_.parent_id != root_id or root_id not in object_.ancestor_ids:
        raise InstallationError("created object is outside the declared instance root")
    if object_.data is None:
        raise InstallationError("created object has no complete readback bytes")
    return {
        "object_id": object_.object_id,
        "kind": "file",
        "permitted_ancestor_id": root_id,
        "mime_type": object_.mime_type,
        "version": object_.version,
    }


def _create_or_adopt(
    storage: CreateOnlyStorage, *, parent_id: str, name: str, data: bytes, mime_type: str,
) -> StoredObject:
    """Adopt one exact scoped object after an uncertain create response, never retry."""
    try:
        object_ = storage.create_file(parent_id, name, data, mime_type)
    except OSError as exc:
        try:
            object_ = discover_unique(storage, parent_id=parent_id, name=name, kind="file", mime_type=mime_type)
        except ReferenceError as discover_exc:
            raise InstallationError(f"create outcome is unknown for {name}: {discover_exc}") from exc
    reference = _stored_reference(object_, parent_id)
    readback = resolve_reference(storage, ObjectReference.from_mapping(reference), expected_kind="file", instance_root_id=parent_id)
    if readback.data != data:
        raise InstallationError(f"provider readback bytes disagree for {name}")
    return readback


def _canonical_json_object(data: bytes, label: str) -> dict[str, Any]:
    """Decode an immutable JSON payload without accepting alternate bytes."""
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InstallationError(f"{label} is not UTF-8 JSON") from exc
    if not isinstance(value, dict) or canonical_json_bytes(value) != data:
        raise InstallationError(f"{label} is not canonical JSON")
    return value


def _exact_reference(value: Any, *, root: ObjectReference, label: str) -> ObjectReference:
    try:
        reference = ObjectReference.from_mapping(_require_mapping(value, label))
    except ReferenceError as exc:
        raise InstallationError(f"invalid {label}: {exc}") from exc
    if reference.kind != "file" or reference.permitted_ancestor_id != root.object_id:
        raise InstallationError(f"{label} is not a file under the declared instance root")
    return reference


def _read_admitted_object(
    storage: ReferenceStorage, reference: ObjectReference, *, root_id: str, name: str, mime_type: str,
) -> StoredObject:
    try:
        object_ = resolve_reference(
            storage, reference, expected_kind="file", required_mime_type=mime_type, instance_root_id=root_id,
        )
    except ReferenceError as exc:
        raise InstallationError(f"admitted {name} reference failed: {exc}") from exc
    if object_.parent_id != root_id or object_.name != name or object_.data is None:
        raise InstallationError(f"admitted {name} is incomplete or outside the declared root")
    return object_


def _parse_bootstrap(data: bytes) -> tuple[str, str]:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise InstallationError("bootstrap must be UTF-8") from exc
    match = re.fullmatch(
        r"# School-OS instance bootstrap\n\n"
        r"instance_manifest_object_id: ([^\s]+)\n"
        r"installation_admission_object_id: ([^\s]+)\n",
        text,
    )
    if match is None:
        raise InstallationError("bootstrap has an invalid immutable admission format")
    return match.group(1), match.group(2)


def recover_create_only_generation(
    storage: ReferenceStorage, *, root_reference: dict[str, Any], bootstrap_reference: dict[str, Any],
) -> dict[str, Any]:
    """Recover only a complete, immutable generation from its bootstrap anchor."""
    try:
        root = ObjectReference.from_mapping(root_reference)
    except ReferenceError as exc:
        raise InstallationError(f"invalid instance_root: {exc}") from exc
    if root.kind != "folder" or root.permitted_ancestor_id != root.object_id:
        raise InstallationError("instance root must be a self-contained folder")
    bootstrap = _exact_reference(bootstrap_reference, root=root, label="bootstrap_reference")
    bootstrap_object = _read_admitted_object(
        storage, bootstrap, root_id=root.object_id, name=BOOTSTRAP_PATH, mime_type="text/markdown",
    )
    instance_id, admission_id = _parse_bootstrap(bootstrap_object.data)
    admission_object = storage.read(admission_id)
    if admission_object is None:
        raise InstallationError("bootstrap names a missing admission receipt")
    admission_reference = _stored_reference(admission_object, root.object_id)
    if admission_object.name != ADMISSION_PATH or admission_object.mime_type != "application/json":
        raise InstallationError("bootstrap names an invalid admission receipt")
    admission_object = _read_admitted_object(
        storage, ObjectReference.from_mapping(admission_reference), root_id=root.object_id,
        name=ADMISSION_PATH, mime_type="application/json",
    )
    admission = _canonical_json_object(admission_object.data, "admission receipt")
    _required_keys(
        admission,
        {"schema_version", "verification_status", "instance_root_reference", "content_manifest_reference", "content_manifest_sha256"},
        "admission receipt",
    )
    if admission["schema_version"] != 1 or admission["verification_status"] != "verified":
        raise InstallationError("admission receipt is not verified version 1")
    try:
        admitted_root = ObjectReference.from_mapping(_require_mapping(admission["instance_root_reference"], "admission root"))
    except ReferenceError as exc:
        raise InstallationError(f"invalid admission root: {exc}") from exc
    if admitted_root != root:
        raise InstallationError("admission receipt names a different instance root")
    manifest_reference = _exact_reference(admission["content_manifest_reference"], root=root, label="content_manifest_reference")
    manifest_object = _read_admitted_object(
        storage, manifest_reference, root_id=root.object_id, name=MANIFEST_PATH, mime_type="application/json",
    )
    if admission["content_manifest_sha256"] != sha256_bytes(manifest_object.data):
        raise InstallationError("admission receipt hash disagrees with content manifest")
    manifest = _canonical_json_object(manifest_object.data, "content manifest")
    _required_keys(manifest, {"schema_version", "verification_status", "package", "instance_root_reference", "files"}, "content manifest")
    if manifest["schema_version"] != 2 or manifest["verification_status"] != "candidate":
        raise InstallationError("content manifest is not a candidate version 2 manifest")
    try:
        manifest_root = ObjectReference.from_mapping(_require_mapping(manifest["instance_root_reference"], "content manifest root"))
    except ReferenceError as exc:
        raise InstallationError(f"invalid content manifest root: {exc}") from exc
    if manifest_root != root:
        raise InstallationError("content manifest names a different instance root")
    package = _require_mapping(manifest["package"], "content manifest package")
    _required_keys(
        package,
        {"version", "source_identity", "archive_sha256", "inventory_sha256", "archive_name", "archive_reference", "checksums_reference", "checksums_sha256"},
        "content manifest package",
    )
    source_identity = _require_mapping(package["source_identity"], "content manifest source identity")
    _required_keys(source_identity, {"repository", "commit"}, "content manifest source identity")
    if not isinstance(package["version"], str) or not isinstance(package["archive_name"], str) or Path(package["archive_name"]).name != package["archive_name"] or not isinstance(source_identity["repository"], str) or re.fullmatch(r"[0-9a-f]{40}", source_identity.get("commit", "")) is None:
        raise InstallationError("content manifest package identity is invalid")
    if any(re.fullmatch(r"[0-9a-f]{64}", package.get(key, "")) is None for key in ("archive_sha256", "inventory_sha256", "checksums_sha256")):
        raise InstallationError("content manifest package hashes are invalid")
    files = _require_mapping(manifest["files"], "content manifest files")
    if not files:
        raise InstallationError("content manifest has no payload files")
    admitted_objects: dict[str, StoredObject] = {}
    for path, record in files.items():
        if not isinstance(path, str) or not path or path in {MANIFEST_PATH, ADMISSION_PATH, BOOTSTRAP_PATH}:
            raise InstallationError("content manifest declares an unsafe payload path")
        entry = _require_mapping(record, f"content manifest file {path}")
        _required_keys(entry, {"object_reference", "sha256"}, f"content manifest file {path}")
        if not isinstance(entry["sha256"], str) or re.fullmatch(r"[0-9a-f]{64}", entry["sha256"]) is None:
            raise InstallationError(f"content manifest hash is invalid for {path}")
        reference = _exact_reference(entry["object_reference"], root=root, label=f"content manifest file {path}")
        object_ = _read_admitted_object(
            storage, reference, root_id=root.object_id, name=path, mime_type=reference.mime_type or "application/octet-stream",
        )
        if sha256_bytes(object_.data) != entry["sha256"]:
            raise InstallationError(f"content manifest hash disagrees for {path}")
        admitted_objects[path] = object_
    if PACKAGE_ARCHIVE_PATH not in admitted_objects or PACKAGE_CHECKSUMS_PATH not in admitted_objects:
        raise InstallationError("content manifest does not admit the pinned archive and checksums")
    archive_reference = _exact_reference(package["archive_reference"], root=root, label="package archive_reference")
    checksums_reference = _exact_reference(package["checksums_reference"], root=root, label="package checksums_reference")
    if archive_reference != _exact_reference(files[PACKAGE_ARCHIVE_PATH]["object_reference"], root=root, label="archive file reference"):
        raise InstallationError("package archive reference disagrees with admitted file")
    if checksums_reference != _exact_reference(files[PACKAGE_CHECKSUMS_PATH]["object_reference"], root=root, label="checksums file reference"):
        raise InstallationError("package checksums reference disagrees with admitted file")
    archive_bytes = admitted_objects[PACKAGE_ARCHIVE_PATH].data or b""
    checksums_bytes = admitted_objects[PACKAGE_CHECKSUMS_PATH].data or b""
    if sha256_bytes(archive_bytes) != package["archive_sha256"] or sha256_bytes(checksums_bytes) != package["checksums_sha256"]:
        raise InstallationError("pinned package archive or checksums hash disagrees")
    if _pinned_archive_name(checksums_bytes, package["archive_sha256"]) != package["archive_name"]:
        raise InstallationError("pinned package archive is not declared by checksums")
    if "instance.yaml" not in admitted_objects or admitted_objects["instance.yaml"].object_id != instance_id:
        raise InstallationError("bootstrap instance identity is not admitted by the content manifest")
    return {
        "manifest": manifest,
        "manifest_reference": dict(admission["content_manifest_reference"]),
        "admission": admission,
        "admission_reference": admission_reference,
        "bootstrap_reference": dict(bootstrap_reference),
        "package_archive": archive_bytes,
        "package_checksums": checksums_bytes,
    }


def install_create_only_generation(
    storage: CreateOnlyStorage,
    *,
    root_reference: dict[str, Any],
    package: dict[str, Any],
    payloads: dict[str, bytes],
    existing_payloads: dict[str, StoredObject] | None = None,
) -> dict[str, Any]:
    """Create and verify an immutable payload/manifest/admission/bootstrap generation.

    ``payloads`` must already contain final bytes: this routine never patches a
    file or hides a lost create response.  The returned bootstrap reference is
    the only fresh-process anchor; neither manifest nor bootstrap self-references.
    """
    try:
        root = ObjectReference.from_mapping(root_reference)
    except ReferenceError as exc:
        raise InstallationError(f"invalid instance_root: {exc}") from exc
    if root.kind != "folder" or root.permitted_ancestor_id != root.object_id:
        raise InstallationError("instance root must be a self-contained folder")
    if (
        not payloads
        or any(not isinstance(path, str) or not path or not isinstance(data, bytes) for path, data in payloads.items())
        or any(path in {MANIFEST_PATH, ADMISSION_PATH, BOOTSTRAP_PATH} for path in payloads)
    ):
        raise InstallationError("create-only generation requires final non-empty payload mapping")
    if PACKAGE_ARCHIVE_PATH not in payloads or PACKAGE_CHECKSUMS_PATH not in payloads:
        raise InstallationError("create-only generation requires pinned archive and checksums payloads")
    if sha256_bytes(payloads[PACKAGE_ARCHIVE_PATH]) != package.get("archive_sha256"):
        raise InstallationError("pinned archive bytes disagree with package evidence")
    archive_name = _pinned_archive_name(payloads[PACKAGE_CHECKSUMS_PATH], package["archive_sha256"])
    objects: dict[str, StoredObject] = {}
    for path, object_ in (existing_payloads or {}).items():
        if path not in payloads:
            raise InstallationError(f"existing payload is not declared: {path}")
        reference = _stored_reference(object_, root.object_id)
        readback = _read_admitted_object(
            storage,
            ObjectReference.from_mapping(reference),
            root_id=root.object_id,
            name=path,
            mime_type=reference["mime_type"] or "application/octet-stream",
        )
        if readback.data != payloads[path]:
            raise InstallationError(f"existing payload bytes disagree for {path}")
        objects[path] = readback
    for path, data in sorted(payloads.items()):
        if path not in objects:
            objects[path] = _create_or_adopt(
                storage, parent_id=root.object_id, name=path, data=data,
                mime_type=managed_mime_type(path),
            )
    admitted_package = dict(package)
    admitted_package.update({
        "archive_name": archive_name,
        "archive_reference": _stored_reference(objects[PACKAGE_ARCHIVE_PATH], root.object_id),
        "checksums_reference": _stored_reference(objects[PACKAGE_CHECKSUMS_PATH], root.object_id),
        "checksums_sha256": sha256_bytes(payloads[PACKAGE_CHECKSUMS_PATH]),
    })
    manifest = {
        "schema_version": 2,
        "verification_status": "candidate",
        "package": admitted_package,
        "instance_root_reference": root_reference,
        "files": {
            path: {"object_reference": _stored_reference(object_, root.object_id), "sha256": sha256_bytes(payloads[path])}
            for path, object_ in sorted(objects.items())
        },
    }
    manifest_bytes = canonical_json_bytes(manifest)
    manifest_object = _create_or_adopt(storage, parent_id=root.object_id, name=MANIFEST_PATH, data=manifest_bytes, mime_type="application/json")
    manifest_reference = _stored_reference(manifest_object, root.object_id)
    admission = {
        "schema_version": 1,
        "verification_status": "verified",
        "instance_root_reference": root_reference,
        "content_manifest_reference": manifest_reference,
        "content_manifest_sha256": sha256_bytes(manifest_bytes),
    }
    admission_bytes = canonical_json_bytes(admission)
    admission_object = _create_or_adopt(storage, parent_id=root.object_id, name=ADMISSION_PATH, data=admission_bytes, mime_type="application/json")
    admission_reference = _stored_reference(admission_object, root.object_id)
    bootstrap_bytes = (
        "# School-OS instance bootstrap\n\n"
        f"instance_manifest_object_id: {objects.get('instance.yaml', manifest_object).object_id}\n"
        f"installation_admission_object_id: {admission_object.object_id}\n"
    ).encode("utf-8")
    bootstrap_object = _create_or_adopt(storage, parent_id=root.object_id, name=BOOTSTRAP_PATH, data=bootstrap_bytes, mime_type="text/markdown")
    bootstrap_reference = _stored_reference(bootstrap_object, root.object_id)
    return recover_create_only_generation(
        storage, root_reference=root_reference, bootstrap_reference=bootstrap_reference,
    )


def extract_recovered_package(recovery: Mapping[str, Any], destination: Path) -> Path:
    """Verify an admitted archive/checksum pair before safe local extraction."""
    manifest = _require_mapping(recovery.get("manifest"), "recovered manifest")
    package = _require_mapping(manifest.get("package"), "recovered package")
    archive = recovery.get("package_archive")
    checksums = recovery.get("package_checksums")
    if not isinstance(archive, bytes) or not isinstance(checksums, bytes):
        raise InstallationError("recovery lacks exact admitted package bytes")
    if sha256_bytes(archive) != package.get("archive_sha256"):
        raise InstallationError("recovered archive bytes disagree with admitted hash")
    if sha256_bytes(checksums) != package.get("checksums_sha256"):
        raise InstallationError("recovered checksums bytes disagree with admitted hash")
    if _pinned_archive_name(checksums, package["archive_sha256"]) != package.get("archive_name"):
        raise InstallationError("recovered checksums archive name disagrees with admission")
    if destination.exists() or not destination.parent.is_dir():
        raise InstallationError("package extraction destination must be a new path")
    staging = Path(tempfile.mkdtemp(prefix="school-os-recovered-", dir=destination.parent))
    try:
        archive_path = staging / package["archive_name"]
        sums_path = staging / "SHA256SUMS"
        archive_path.write_bytes(archive)
        sums_path.write_bytes(checksums)
        errors = verify_release_archive(archive_path, sums_path, package["version"])
        if errors:
            raise InstallationError("recovered package verification failed: " + "; ".join(errors))
        with tarfile.open(archive_path, "r:gz") as bundle:
            for member in bundle.getmembers():
                target = staging / member.name
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                if not member.isfile():
                    raise InstallationError("recovered package has an unsupported member")
                target.parent.mkdir(parents=True, exist_ok=True)
                source = bundle.extractfile(member)
                if source is None:
                    raise InstallationError("recovered package member is unreadable")
                target.write_bytes(source.read())
        extracted = staging / f"School-OS-{package['version']}"
        verification = verify_extracted_tree(extracted, package["version"])
        if verification.inventory_sha256 != package["inventory_sha256"]:
            raise InstallationError("recovered package inventory hash disagrees")
        os.replace(extracted, destination)
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    shutil.rmtree(staging, ignore_errors=True)
    return destination
