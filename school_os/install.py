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
from pathlib import Path
from typing import Any, Protocol

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
MANAGED_PATHS = (
    "instance.yaml",
    "config/household.yaml",
    "config/integrations.yaml",
    "config/policies.yaml",
    "config/daily-run-personal-values.md",
    FILE_MAP_PATH,
    OPERATION_STATE_PATH,
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


class CreateOnlyStorage(ReferenceStorage, Protocol):
    """Storage surface for installation generations that may never replace bytes."""

    def create_file(self, parent_id: str, name: str, data: bytes, mime_type: str) -> StoredObject: ...


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
    operation_state = {
        "checkpoint": None,
        "current_operation": None,
        "last_terminal": None,
        "schema_version": 1,
        "serialization": None,
        "status": "idle",
    }
    _validated(operation_state, package_root, "operation-state.schema.json", "operation state")
    file_map = {
        "schema_version": 1,
        "mapping_status": "partially_configured",
        "files": {
            "capability_profile": {},
            "operation_state": returned_references[OPERATION_STATE_PATH],
            "operation_checkpoints_folder": {},
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
        OPERATION_STATE_PATH: canonical_json_bytes(operation_state),
    }
    if any(_contains_placeholder(load_mapping_yaml(data.decode("utf-8"))) for path, data in files.items() if path.endswith(".yaml")) or b"REPLACE_WITH_" in files["config/daily-run-personal-values.md"]:
        raise InstallationError("candidate contains an unresolved placeholder")
    manifest = {
        "schema_version": 2,
        "verification_status": "candidate",
        "package": package,
        "instance_root_reference": instance_root,
        "files": {
            path: {"object_reference": returned_references[path], "sha256": sha256_bytes(data)}
            for path, data in sorted(files.items())
        },
    }
    _validated(manifest, package_root, "installation-manifest.schema.json", "installation manifest")
    return files, manifest


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


def install_create_only_generation(
    storage: CreateOnlyStorage, *, root_reference: dict[str, Any], package: dict[str, Any], payloads: dict[str, bytes],
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
    if not payloads or any(not path or data is None for path, data in payloads.items()):
        raise InstallationError("create-only generation requires final non-empty payload mapping")
    objects: dict[str, StoredObject] = {}
    for path, data in sorted(payloads.items()):
        objects[path] = _create_or_adopt(storage, parent_id=root.object_id, name=path, data=data, mime_type="application/octet-stream")
    manifest = {
        "schema_version": 2,
        "verification_status": "candidate",
        "package": package,
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
    return {"manifest": manifest, "manifest_reference": manifest_reference, "admission": admission, "admission_reference": admission_reference, "bootstrap_reference": bootstrap_reference}
