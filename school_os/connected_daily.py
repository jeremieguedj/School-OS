"""Concrete seven-phase connected daily composition for an admitted instance."""

from __future__ import annotations

import base64
import binascii
import json
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from .brief import build_brief_input, delivery_key, render_brief
from .connected_ingestion import (
    CodexGmailSourceAdapter, CodexSemanticCallbacks, ConnectedIngestionWorker,
    DiscoveryResult, IngestionArtifacts, IngestionResult,
)
from .connected_profiles import readmit_capability_profile, select_capability_profile
from .connected_sheets import CodexSheetsTaskPort, GoogleSheetsScope
from .connected_sources import ConnectedSourceAdapters
from .connected_storage import (
    ArtifactStore, CodexDriveArtifactStore, CodexDriveReferenceStorage,
    DriveReference, StoredArtifact,
)
from .connected_tasks import (
    ConnectedTaskReconcileResult, ConnectedTaskWorker,
    unresolved_finite_task_selection,
)
from .contracts import canonical_json_bytes, load_mapping_yaml, sha256_bytes, validate
from .daily import PHASES, OperationResult, run_daily
from .delivery import ExactDeliveryRequest, deliver_exact
from .gmail_source import GmailMimeNormalizer
from .install import FILE_MAP_PATH, OPERATION_STATE_PATH, parse_daily_values
from .operations import (
    RecoveryChain, checkpoint_pointer, discover_recovery_chain, resume_from_chain,
    validate_checkpoint, validate_operation_state, validate_transition,
)
from .sheets import GoogleSheetsTaskAdapter
from .tasks import build_derived_knowledge


class ConnectedDailyError(ValueError):
    """Raised when an installed connected run cannot prove its next step."""


REQUIRED_CAPABILITIES = (
    "storage.read_complete", "storage.write_guarded", "mail.search",
    "mail.read_complete", "mail.send", "tasks.list_complete", "tasks.write_guarded",
)


def _json(data: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ConnectedDailyError(f"{label} is not UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise ConnectedDailyError(f"{label} must be a JSON object")
    return value


def _schema(root: Path, name: str) -> dict[str, Any]:
    return _json((root / "schemas" / name).read_bytes(), f"schema {name}")


def _validated(value: Any, root: Path, schema: str, label: str) -> None:
    errors = validate(value, _schema(root, schema))
    if errors:
        raise ConnectedDailyError(f"invalid {label}: " + "; ".join(errors))


def _reference_mapping(reference: DriveReference) -> dict[str, Any]:
    return {
        "object_id": reference.object_id, "parent_id": reference.parent_id,
        "mime_type": reference.mime_type, "url": reference.url,
        "version": reference.version,
    }


def _artifact_mapping(artifact: StoredArtifact) -> dict[str, Any]:
    return {**_reference_mapping(artifact.reference), "sha256": sha256_bytes(artifact.data), "byte_length": len(artifact.data)}


def _artifact_from_mapping(store: ArtifactStore, value: Any, label: str) -> StoredArtifact:
    expected = {"object_id", "parent_id", "mime_type", "url", "version", "sha256", "byte_length"}
    if not isinstance(value, Mapping) or set(value) != expected:
        raise ConnectedDailyError(f"{label} has an unsupported durable artifact shape")
    if not all(isinstance(value.get(key), str) and value[key] for key in ("object_id", "parent_id", "mime_type", "url", "version")):
        raise ConnectedDailyError(f"{label} lacks an exact durable reference")
    if isinstance(value.get("byte_length"), bool) or not isinstance(value.get("byte_length"), int) or value["byte_length"] < 0:
        raise ConnectedDailyError(f"{label} lacks an exact byte length")
    artifact = store.read(DriveReference(
        value["object_id"], value["parent_id"], value["mime_type"], value["url"], value["version"],
    ))
    if len(artifact.data) != value["byte_length"] or sha256_bytes(artifact.data) != value.get("sha256"):
        raise ConnectedDailyError(f"{label} differs from its checkpointed bytes")
    return artifact


def _require_keys(value: Mapping[str, Any], expected: set[str], label: str) -> None:
    if set(value) != expected:
        raise ConnectedDailyError(f"{label} has unsupported fields")


def _scope(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ConnectedDailyError("source scope must be an object")
    required = {"schema_version", "adapter_id", "query", "label_ids", "max_results", "max_thread_messages"}
    optional = {"seed_after_inclusive_ms", "seed_before_exclusive_ms"}
    if not required <= set(value) or set(value) - required - optional:
        raise ConnectedDailyError("source scope has unsupported fields")
    if (
        value["schema_version"] != 1 or not all(isinstance(value[key], str) and value[key] for key in ("adapter_id", "query"))
        or not isinstance(value["label_ids"], list) or any(not isinstance(item, str) or not item for item in value["label_ids"])
        or any(isinstance(value[key], bool) or not isinstance(value[key], int) or value[key] < 1 for key in ("max_results", "max_thread_messages"))
    ):
        raise ConnectedDailyError("source scope is malformed or unbounded")
    for key in optional:
        bound = value.get(key)
        if bound is not None and (
            isinstance(bound, bool) or not isinstance(bound, int) or bound < 0
        ):
            raise ConnectedDailyError("source seed bounds must be nonnegative epoch milliseconds")
    start, end = value.get("seed_after_inclusive_ms"), value.get("seed_before_exclusive_ms")
    if start is not None and end is not None and start >= end:
        raise ConnectedDailyError("source seed interval must have positive width")
    return dict(value)


def _delivery_configuration(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ConnectedDailyError("delivery configuration must be an object")
    required = {"schema_version", "variant", "to", "cc", "bcc", "subject_prefix"}
    if not required <= set(value) or set(value) - required - {"test_variants"}:
        raise ConnectedDailyError("delivery configuration has unsupported fields")
    if value["schema_version"] != 1 or not all(isinstance(value[key], str) and value[key] for key in ("variant", "subject_prefix")):
        raise ConnectedDailyError("delivery configuration has invalid identity fields")
    for key in ("to", "cc", "bcc"):
        if not isinstance(value[key], list) or any(not isinstance(item, str) or not item for item in value[key]):
            raise ConnectedDailyError("delivery recipient lists are malformed")
    if not value["to"]:
        raise ConnectedDailyError("delivery configuration requires a To recipient")
    variants = value.get("test_variants")
    if variants is not None:
        if (
            not isinstance(variants, Mapping)
            or set(variants) != {"manual", "scheduled"}
            or any(not isinstance(item, str) or not item for item in variants.values())
            or len(set(variants.values())) != 2
            or value["variant"] in variants.values()
        ):
            raise ConnectedDailyError("delivery TEST variants must be two distinct finite entrypoint values")
    return dict(value)


def _selected_delivery(value: Mapping[str, Any], entrypoint: str, requested: str | None) -> dict[str, Any]:
    """Select only the ordinary variant or the configured TEST variant for this entrypoint."""
    delivery = dict(value)
    if requested is None:
        return delivery
    variants = delivery.get("test_variants")
    if not isinstance(variants, Mapping) or variants.get(entrypoint) != requested:
        raise ConnectedDailyError("requested delivery variant is not the configured TEST variant for this entrypoint")
    delivery["variant"] = requested
    return delivery


def validate_connected_seed_payloads(payloads: Mapping[str, Mapping[str, Any]], package_root: Path) -> None:
    """Validate private setup bytes that have finite installed runtime shapes."""
    decoded = {role: item.get("data") for role, item in payloads.items()}
    _scope(_json(decoded["source_scope"], "source scope"))
    _delivery_configuration(_json(decoded["delivery_configuration"], "delivery configuration"))
    _validated(_json(decoded["runtime_profile"], "runtime profile"), package_root, "capability-profile.schema.json", "runtime profile")
    register = _json(decoded["canonical_action_register"], "canonical register")
    provider = _json(decoded["task_sync_state"], "task provider state")
    _validated(register, package_root, "canonical-tasks.schema.json", "canonical register")
    _validated(provider, package_root, "provider-state.schema.json", "task provider state")
    exact_empty = {
        "source_checkpoint": {"schema_version": 1, "eligible_cursor": None},
        "source_catalog_index": {"schema_version": 1, "records": []},
        "guidelines": {"schema_version": 1, "guidelines": []},
        "rolling_updates": {"schema_version": 1, "rolling_updates": []},
        "delivery_state": {"schema_version": 1, "deliveries": {}, "effects": {}},
        "final_run_checkpoint": {"schema_version": 1, "last_run": None},
    }
    for role, expected in exact_empty.items():
        if _json(decoded[role], role.replace("_", " ")) != expected:
            raise ConnectedDailyError(f"fresh setup {role} is not its exact empty state")
    if register["tasks"] or provider["bindings"] or provider.get("claim_intents") or provider.get("effect_intents") or provider["cursor"] is not None:
        raise ConnectedDailyError("fresh setup task state is not empty")
    template = _json(decoded["brief_template"], "brief template")
    _require_keys(template, {"version", "html", "text", "placeholders"}, "brief template")
    if not all(isinstance(template[key], str) and template[key] for key in ("version", "html", "text")) or not isinstance(template["placeholders"], dict):
        raise ConnectedDailyError("brief template is malformed")


@dataclass
class _ResolvedInstance:
    root: DriveReference
    file_map: dict[str, DriveReference]
    profile: dict[str, Any]
    profile_artifact: StoredArtifact
    source_scope: dict[str, Any]
    delivery: dict[str, Any]
    sheet_scope: GoogleSheetsScope
    household: dict[str, Any]
    policies: dict[str, Any]
    daily_values: dict[str, Any]
    instance: dict[str, Any]
    brief_template: dict[str, Any]
    configuration_fingerprint: str


class _Resolver:
    def __init__(self, *, root: Path, recovery: Mapping[str, Any], drive: Any) -> None:
        self.package_root, self.recovery, self.drive = root, recovery, drive
        self.reference_storage = CodexDriveReferenceStorage(drive)
        manifest = recovery.get("manifest")
        if not isinstance(manifest, Mapping):
            raise ConnectedDailyError("runtime document lacks an admitted manifest")
        self.manifest = dict(manifest)
        root_mapping = self.manifest.get("instance_root_reference")
        if not isinstance(root_mapping, Mapping):
            raise ConnectedDailyError("admitted manifest lacks its instance root")
        self.root_id = root_mapping.get("object_id")
        if not isinstance(self.root_id, str) or not self.root_id:
            raise ConnectedDailyError("admitted instance root identity is invalid")
        self.root = self._drive_reference(root_mapping, "folder", "instance root", require_direct=False)

    def _drive_reference(self, value: Any, kind: str, label: str, *, require_direct: bool = True, allow_stale_version: bool = False) -> DriveReference:
        if not isinstance(value, Mapping) or value.get("kind") != kind or value.get("permitted_ancestor_id") != self.root_id:
            raise ConnectedDailyError(f"{label} is not an admitted {kind} reference")
        object_id = value.get("object_id")
        if not isinstance(object_id, str) or not object_id:
            raise ConnectedDailyError(f"{label} lacks an object identity")
        item = self.reference_storage.read(object_id)
        if item is None or item.kind != kind or (not allow_stale_version and item.version != value.get("version")):
            raise ConnectedDailyError(f"{label} metadata/version disagrees with its reference")
        if require_direct and item.parent_id != self.root_id:
            raise ConnectedDailyError(f"{label} is not directly contained by the instance root")
        url = self.reference_storage._urls.get(object_id)
        if not isinstance(url, str) or not url:
            raise ConnectedDailyError(f"{label} lacks an exact Drive URL")
        return DriveReference(object_id, item.parent_id or "", item.mime_type or "application/octet-stream", url, item.version)

    def _managed(self, path: str) -> bytes:
        files = self.manifest.get("files")
        record = files.get(path) if isinstance(files, Mapping) else None
        if not isinstance(record, Mapping) or not isinstance(record.get("object_reference"), Mapping):
            raise ConnectedDailyError(f"admitted manifest does not contain {path}")
        reference = record["object_reference"]
        item = self.reference_storage.read(reference["object_id"])
        if item is None or item.data is None or item.version != reference.get("version") or sha256_bytes(item.data) != record.get("sha256"):
            raise ConnectedDailyError(f"admitted managed file readback disagrees for {path}")
        return item.data

    def resolve(self, *, entrypoint: str, delivery_variant: str | None = None) -> _ResolvedInstance:
        instance = load_mapping_yaml(self._managed("instance.yaml").decode("utf-8"))
        household = load_mapping_yaml(self._managed("config/household.yaml").decode("utf-8"))
        policies = load_mapping_yaml(self._managed("config/policies.yaml").decode("utf-8"))
        integrations = load_mapping_yaml(self._managed("config/integrations.yaml").decode("utf-8"))
        daily_bytes = self._managed("config/daily-run-personal-values.md")
        daily_values = parse_daily_values(daily_bytes)
        file_map_bytes = self._managed(FILE_MAP_PATH)
        file_map_value = load_mapping_yaml(file_map_bytes.decode("utf-8"))
        if file_map_value.get("mapping_status") != "configured" or not isinstance(file_map_value.get("files"), Mapping):
            raise ConnectedDailyError("installed file map is not fully configured")
        _validated(instance, self.package_root, "instance.schema.json", "instance")
        _validated(household, self.package_root, "household.schema.json", "household")
        _validated(policies, self.package_root, "policies.schema.json", "policies")
        _validated(integrations, self.package_root, "integrations.schema.json", "integrations")
        _validated(daily_values, self.package_root, "daily-values.schema.json", "daily values")
        mutable_roles = {
            "operation_state", "source_checkpoint", "current_index", "source_catalog_index",
            "canonical_tasks", "guidelines", "rolling_updates", "task_sync_state",
            "delivery_state", "final_run_checkpoint",
            "capability_profile", "durable_profiles",
        }
        references = {
            role: self._drive_reference(
                mapping, "folder" if role in {"source_catalog_folder", "operation_checkpoints_folder"} else "file",
                f"file map {role}", allow_stale_version=role in mutable_roles,
            )
            for role, mapping in file_map_value["files"].items()
        }
        for role, mapping in daily_values["references"].items():
            if references[{"canonical_action_register": "canonical_tasks", "runtime_profile": "capability_profile"}.get(role, role)].object_id != mapping.get("object_id"):
                raise ConnectedDailyError(f"daily values reference disagrees with file map for {role}")
        store = CodexDriveArtifactStore(self.drive, scratch_directory=self.package_root.parent / "artifact-scratch")
        profile, profile_artifact, _profile_selection = select_capability_profile(
            store, references["durable_profiles"], entrypoint=entrypoint,
            profile_schema=_schema(self.package_root, "capability-profile.schema.json"),
        )
        delivery_reference = self._drive_reference(
            integrations["mail"]["delivery_configuration_reference"], "file", "delivery configuration"
        )
        delivery = _selected_delivery(_delivery_configuration(
            _json(store.read(delivery_reference).data, "delivery configuration")
        ), entrypoint, delivery_variant)
        source_reference = self._drive_reference(integrations["mail"]["source_scope_reference"], "file", "source scope")
        if source_reference.object_id != references["family_scope"].object_id:
            raise ConnectedDailyError("integration source scope disagrees with file map")
        source_scope = _scope(_json(store.read(source_reference).data, "source scope"))
        selector = _json(store.read(references["active_task_provider"]).data, "task provider selector")
        _require_keys(selector, {"schema_version", "spreadsheet_id", "spreadsheet_url", "sheet_id", "sheet_title", "first_row", "last_row", "first_column", "last_column"}, "task provider selector")
        sheet_scope = GoogleSheetsScope(**{key: value for key, value in selector.items() if key != "schema_version"})
        brief_template = _json(store.read(references["brief_template"]).data, "brief template")
        _validated(profile, self.package_root, "capability-profile.schema.json", "runtime profile")
        fingerprint = sha256_bytes(canonical_json_bytes({
            "instance": instance, "household": household, "policies": policies,
            "daily_values": daily_values, "source_scope": source_scope,
            "delivery": delivery, "sheet_scope": selector,
            "profile_sha256": sha256_bytes(profile_artifact.data),
        }))
        return _ResolvedInstance(self.root, references, profile, profile_artifact, source_scope, delivery, sheet_scope, household, policies, daily_values, instance, brief_template, fingerprint)


def readmit_connected_profile(
    *, installed_root: Path, recovery: Mapping[str, Any], run_directory: Path,
    drive: Any, entrypoint: str, profile_data: bytes,
) -> dict[str, Any]:
    """Adopt one observed entrypoint profile without replacing the installed generation."""
    resolver = _Resolver(root=installed_root, recovery=recovery, drive=drive)
    file_map = load_mapping_yaml(resolver._managed(FILE_MAP_PATH).decode("utf-8"))
    files = file_map.get("files")
    if file_map.get("mapping_status") != "configured" or not isinstance(files, Mapping):
        raise ConnectedDailyError("installed file map is not fully configured")
    selection = resolver._drive_reference(
        files.get("durable_profiles"), "file", "capability-profile selection",
        allow_stale_version=True,
    )
    store = CodexDriveArtifactStore(drive, scratch_directory=run_directory / "profile-scratch")
    return readmit_capability_profile(
        store, instance_root=resolver.root, selection_reference=selection,
        entrypoint=entrypoint, profile_data=profile_data,
        profile_schema=_schema(installed_root, "capability-profile.schema.json"),
        required_capabilities=REQUIRED_CAPABILITIES,
    )


class _CheckpointManager:
    def __init__(self, *, store: ArtifactStore, listing: CodexDriveReferenceStorage, state: DriveReference,
                 folder: DriveReference, operation_id: str, attempt_id: str, entrypoint: str,
                 release: Mapping[str, str], fingerprint: str, scope: Mapping[str, Any], schemas: Mapping[str, Mapping[str, Any]], serialization_mode: str) -> None:
        self.store, self.listing, self.state_ref, self.folder = store, listing, state, folder
        self.operation_id, self.attempt_id, self.entrypoint = operation_id, attempt_id, entrypoint
        self.release, self.fingerprint, self.scope = dict(release), fingerprint, dict(scope)
        self.serialization_mode = serialization_mode
        self.state_schema, self.checkpoint_schema = schemas["state"], schemas["checkpoint"]
        state_artifact = store.read(state.current())
        self.state_ref, self.state = state_artifact.reference, _json(state_artifact.data, "operation state")
        validate_operation_state(self.state, self.state_schema)
        objects = listing.list_scoped(folder.object_id)
        candidates = []
        for item in objects:
            if item.kind == "file" and item.data is not None and item.name.startswith(f"{operation_id}-checkpoint-"):
                candidates.append(_json(item.data, "operation checkpoint"))
        self.chain = discover_recovery_chain(candidates, operation_id, self.checkpoint_schema) if candidates else None
        self.sequence = 0 if self.chain is None else self.chain.tip["sequence"] + 1
        self.predecessor = None if self.chain is None else checkpoint_pointer(self.chain.tip)
        self.completed: list[str] = [] if self.chain is None else list(self.chain.tip["completed_phases"])
        self.resume_after: str | None = None
        self.durable_predecessor_output: dict[str, Any] | None = None
        if self.chain is None:
            if self.state["status"] in {"running", "needs_continuation", "blocked"}:
                raise ConnectedDailyError("another admitted operation is active without this recovery chain")
            return
        recovered_scope = self.chain.tip.get("scope")
        if not isinstance(recovered_scope, Mapping):
            raise ConnectedDailyError("recovery chain lacks exact operation inputs")
        requested_inputs = {key: value for key, value in self.scope.items() if key != "run_local_date"}
        recovered_inputs = {key: value for key, value in recovered_scope.items() if key != "run_local_date"}
        if requested_inputs != recovered_inputs or not isinstance(recovered_scope.get("run_local_date"), str):
            raise ConnectedDailyError("recovery operation inputs differ from the admitted scope")
        self.scope = dict(recovered_scope)
        for checkpoint in self.chain.checkpoints:
            if checkpoint["pinned_release"] != self.release or checkpoint["configuration_fingerprint"] != self.fingerprint:
                raise ConnectedDailyError("recovery release or configuration changed and requires reconciliation")
            if checkpoint["scope"] != self.scope:
                raise ConnectedDailyError("recovery operation inputs differ from the admitted scope")
        if self.state["status"] not in {"running", "needs_continuation", "blocked"}:
            raise ConnectedDailyError("operation recovery chain is not the active durable operation")
        current = self.state.get("current_operation")
        if not isinstance(current, Mapping) or current.get("operation_id") != operation_id or self.state.get("checkpoint") != checkpoint_pointer(self.chain.tip):
            raise ConnectedDailyError("operation state does not identify the verified recovery-chain tip")
        if current.get("attempt_id") == attempt_id:
            raise ConnectedDailyError("operation recovery requires a new attempt identity")
        if self.state["status"] == "running":
            self._record_hard_stop(current["attempt_id"])
        self.completed = list(self.chain.tip["completed_phases"])
        for checkpoint in reversed(self.chain.checkpoints):
            output = checkpoint.get("verification", {}).get("phase_output")
            if isinstance(output, Mapping) and output.get("verified") is True:
                self.resume_after = checkpoint["phase"]
                self.durable_predecessor_output = dict(output)
                break
        if self.resume_after is None or self.durable_predecessor_output is None:
            raise ConnectedDailyError("recovery chain lacks a verified durable phase output")
        self._admit_resume()

    def _record_hard_stop(self, prior_attempt_id: str) -> None:
        """Turn the abandoned running attempt into the existing blocked state."""
        if self.serialization_mode != "attended_single_writer":
            raise ConnectedDailyError("hard-stop recovery requires the attended single-writer mode")
        completed = list(self.chain.tip["completed_phases"])
        failed_phase = PHASES[len(completed)] if len(completed) < len(PHASES) else self.chain.tip["phase"]
        checkpoint = {
            "schema_version": 1, "checkpoint_id": f"{self.operation_id}-checkpoint-{self.sequence:04d}",
            "operation_id": self.operation_id, "attempt_id": prior_attempt_id,
            "pinned_release": self.release, "scope": self.scope,
            "configuration_fingerprint": self.fingerprint, "phase": failed_phase,
            "completed_phases": completed, "completed_units": [],
            "remaining_work": {"phase": failed_phase, "recovery": "hard_process_stop"},
            "artifacts": [], "effects": [],
            "verification": {"hard_process_stop": True, "attended_single_writer": True},
            "blocker": {"kind": "hard_process_stop", "phase": failed_phase},
            "predecessor": self.predecessor, "sequence": self.sequence,
        }
        validate_checkpoint(checkpoint, self.checkpoint_schema)
        artifact = self.store.write_immutable(
            self.folder, f"{self.operation_id}-checkpoint-{self.sequence:04d}.json",
            canonical_json_bytes(checkpoint), "application/json",
        )
        if artifact.data != canonical_json_bytes(checkpoint):
            raise ConnectedDailyError("hard-stop recovery checkpoint did not read back exactly")
        pointer = checkpoint_pointer(checkpoint)
        candidate = {
            "schema_version": 1, "status": "blocked",
            "current_operation": {"operation_id": self.operation_id, "attempt_id": prior_attempt_id},
            "serialization": self.state["serialization"], "checkpoint": pointer, "last_terminal": None,
        }
        self._write_state(candidate, checkpoint)
        self.chain = RecoveryChain(self.operation_id, (*self.chain.checkpoints, checkpoint))
        self.predecessor, self.sequence = pointer, self.sequence + 1

    def _admit_resume(self) -> None:
        """Persist the new attempt before any resumed phase can fail or make an effect."""
        if self.chain is None or self.resume_after is None or self.durable_predecessor_output is None:
            raise ConnectedDailyError("resume admission lacks its durable predecessor")
        resume_work_phase = self.resume_after
        if self.durable_predecessor_output.get("phase_complete") is True:
            position = PHASES.index(self.resume_after)
            resume_work_phase = PHASES[position + 1] if position + 1 < len(PHASES) else self.resume_after
        checkpoint = {
            "schema_version": 1, "checkpoint_id": f"{self.operation_id}-checkpoint-{self.sequence:04d}",
            "operation_id": self.operation_id, "attempt_id": self.attempt_id,
            "pinned_release": self.release, "scope": self.scope,
            "configuration_fingerprint": self.fingerprint, "phase": self.resume_after,
            "completed_phases": list(self.completed),
            "completed_units": list(self.durable_predecessor_output.get("completed_units", [])),
            "remaining_work": {"phase": resume_work_phase, "recovery": "new_attempt"},
            "artifacts": [], "effects": list(self.chain.tip.get("effects", [])),
            "verification": {
                "phase_output": dict(self.durable_predecessor_output),
                "resume_admission": {"predecessor_attempt_id": self.chain.tip["attempt_id"]},
            },
            "blocker": None, "predecessor": self.predecessor, "sequence": self.sequence,
        }
        validate_checkpoint(checkpoint, self.checkpoint_schema)
        artifact = self.store.write_immutable(
            self.folder, f"{self.operation_id}-checkpoint-{self.sequence:04d}.json",
            canonical_json_bytes(checkpoint), "application/json",
        )
        if artifact.data != canonical_json_bytes(checkpoint):
            raise ConnectedDailyError("resume admission checkpoint did not read back exactly")
        resume_from_chain(
            self.state, self.chain, checkpoint, state_schema=self.state_schema,
            checkpoint_schema=self.checkpoint_schema, pinned_release=self.release,
            configuration_fingerprint=self.fingerprint,
        )
        pointer = checkpoint_pointer(checkpoint)
        candidate = {
            "schema_version": 1, "status": "running",
            "current_operation": {"operation_id": self.operation_id, "attempt_id": self.attempt_id},
            "serialization": {"mode": self.serialization_mode, "evidence": {"entrypoint": self.entrypoint}},
            "checkpoint": pointer, "last_terminal": None,
        }
        self._write_state(candidate, checkpoint)
        self.chain = RecoveryChain(self.operation_id, (*self.chain.checkpoints, checkpoint))
        self.predecessor, self.sequence = pointer, self.sequence + 1

    def _write_state(self, candidate: dict[str, Any], checkpoint: dict[str, Any], required: tuple[str, ...] = ()) -> None:
        previous = self.state
        validate_transition(previous, candidate, checkpoint, state_schema=self.state_schema, checkpoint_schema=self.checkpoint_schema, required_phases=required)
        written = self.store.replace(self.state_ref, canonical_json_bytes(candidate), self.state_ref.mime_type)
        if written.data != canonical_json_bytes(candidate):
            raise ConnectedDailyError("operation state did not read back exactly")
        self.state_ref, self.state = written.reference, candidate

    def persist(self, phase: str, result: Mapping[str, Any], outcome: str = "running") -> str:
        if result.get("phase_complete", True) is True and phase not in self.completed:
            self.completed.append(phase)
        checkpoint = {
            "schema_version": 1, "checkpoint_id": f"{self.operation_id}-checkpoint-{self.sequence:04d}",
            "operation_id": self.operation_id, "attempt_id": self.attempt_id,
            "pinned_release": self.release, "scope": self.scope,
            "configuration_fingerprint": self.fingerprint, "phase": phase,
            "completed_phases": list(self.completed), "completed_units": list(result.get("completed_units", [])),
            "remaining_work": dict(result.get("remaining_work", {})), "artifacts": [],
            "effects": list(result.get("effects", [])), "verification": {"phase_output": dict(result)},
            "blocker": None, "predecessor": self.predecessor, "sequence": self.sequence,
        }
        validate_checkpoint(checkpoint, self.checkpoint_schema)
        name = f"{self.operation_id}-checkpoint-{self.sequence:04d}.json"
        artifact = self.store.write_immutable(self.folder, name, canonical_json_bytes(checkpoint), "application/json")
        if artifact.data != canonical_json_bytes(checkpoint):
            raise ConnectedDailyError("operation checkpoint did not read back exactly")
        pointer = checkpoint_pointer(checkpoint)
        if self.state["status"] in {"needs_continuation", "blocked"}:
            if self.chain is None:
                raise ConnectedDailyError("paused operation lacks a recovery chain")
            resume_from_chain(
                self.state, self.chain, checkpoint, state_schema=self.state_schema,
                checkpoint_schema=self.checkpoint_schema, pinned_release=self.release,
                configuration_fingerprint=self.fingerprint,
            )
        candidate = {
            "schema_version": 1, "status": "running",
            "current_operation": {"operation_id": self.operation_id, "attempt_id": self.attempt_id},
            "serialization": {"mode": self.serialization_mode, "evidence": {"entrypoint": self.entrypoint}},
            "checkpoint": pointer, "last_terminal": None,
        }
        self._write_state(candidate, checkpoint)
        self.predecessor, self.sequence = pointer, self.sequence + 1
        return artifact.reference.url

    def complete(self, result: OperationResult) -> str:
        checkpoint = {
            "schema_version": 1, "checkpoint_id": f"{self.operation_id}-checkpoint-{self.sequence:04d}",
            "operation_id": self.operation_id, "attempt_id": self.attempt_id,
            "pinned_release": self.release, "scope": self.scope,
            "configuration_fingerprint": self.fingerprint, "phase": "commit",
            "completed_phases": list(PHASES), "completed_units": [], "remaining_work": {},
            "artifacts": [], "effects": [],
            "verification": {"outcome": result.outcome, "completed_phases": list(result.completed_phases)},
            "blocker": None, "predecessor": self.predecessor, "sequence": self.sequence,
        }
        validate_checkpoint(checkpoint, self.checkpoint_schema)
        artifact = self.store.write_immutable(self.folder, f"{self.operation_id}-checkpoint-{self.sequence:04d}.json", canonical_json_bytes(checkpoint), "application/json")
        if artifact.data != canonical_json_bytes(checkpoint):
            raise ConnectedDailyError("terminal operation checkpoint did not read back exactly")
        pointer = checkpoint_pointer(checkpoint)
        state = {
            "schema_version": 1, "status": "complete", "current_operation": None,
            "serialization": None, "checkpoint": None,
            "last_terminal": {"operation_id": self.operation_id, "status": "complete", "checkpoint": pointer, "reason": result.reason},
        }
        self._write_state(state, checkpoint, PHASES)
        return artifact.reference.url

    def block(self, phase: str, error: Exception, *, effects: list[dict[str, Any]] | None = None) -> str | None:
        if self.state.get("status") != "running":
            return None
        checkpoint = {
            "schema_version": 1, "checkpoint_id": f"{self.operation_id}-checkpoint-{self.sequence:04d}",
            "operation_id": self.operation_id, "attempt_id": self.attempt_id,
            "pinned_release": self.release, "scope": self.scope,
            "configuration_fingerprint": self.fingerprint, "phase": phase,
            "completed_phases": list(self.completed), "completed_units": [],
            "remaining_work": {"phase": phase}, "artifacts": [], "effects": list(effects or []),
            "verification": {"error_class": type(error).__name__},
            "blocker": {"kind": "phase_failure", "phase": phase},
            "predecessor": self.predecessor, "sequence": self.sequence,
        }
        validate_checkpoint(checkpoint, self.checkpoint_schema)
        artifact = self.store.write_immutable(
            self.folder, f"{self.operation_id}-checkpoint-{self.sequence:04d}.json",
            canonical_json_bytes(checkpoint), "application/json",
        )
        pointer = checkpoint_pointer(checkpoint)
        state = {
            "schema_version": 1, "status": "blocked",
            "current_operation": {"operation_id": self.operation_id, "attempt_id": self.attempt_id},
            "serialization": self.state["serialization"], "checkpoint": pointer, "last_terminal": None,
        }
        self._write_state(state, checkpoint)
        return artifact.reference.url


def _reference_from_mapping(value: Any, label: str) -> DriveReference:
    expected = {"object_id", "parent_id", "mime_type", "url", "version"}
    if not isinstance(value, Mapping) or set(value) != expected or not all(
        isinstance(value.get(key), str) and value[key]
        for key in expected
    ):
        raise ConnectedDailyError(f"{label} lacks an exact checkpointed reference")
    return DriveReference(
        value["object_id"], value["parent_id"], value["mime_type"], value["url"], value["version"],
    )


def _restore_daily_state(
    *, manager: _CheckpointManager, store: ArtifactStore,
    ingestion: ConnectedIngestionWorker,
    mutable: dict[str, DriveReference], max_bytes: int,
) -> dict[str, Any]:
    """Re-admit the exact persisted handoffs needed after the verified chain tip."""
    if manager.chain is None:
        return {}
    outputs: dict[str, dict[str, Any]] = {}
    for checkpoint in manager.chain.checkpoints:
        output = checkpoint.get("verification", {}).get("phase_output")
        if isinstance(output, Mapping) and output.get("verified") is True:
            outputs[checkpoint["phase"]] = dict(output)
    context: dict[str, Any] = {}
    discovered = outputs.get("discover")
    if discovered is not None:
        inventory = _artifact_from_mapping(store, discovered.get("discovery_inventory"), "discovery inventory")
        identities = discovered.get("conversation_ids")
        if not isinstance(identities, list) or any(not isinstance(item, str) or not item for item in identities):
            raise ConnectedDailyError("checkpointed discovery identities are malformed")
        context["discovery"] = DiscoveryResult(
            inventory, discovered.get("scope_sha256"), tuple(identities),
        )
    catalog = outputs.get("catalog")
    if catalog is not None:
        work = _artifact_from_mapping(store, catalog.get("source_work"), "source work")
        index = _artifact_from_mapping(store, catalog.get("catalog_index"), "catalog index")
        discovery = _artifact_from_mapping(store, catalog.get("discovery_inventory"), "catalog discovery")
        records: list[IngestionArtifacts] = []
        for record in catalog.get("records", []):
            if not isinstance(record, Mapping) or set(record) != {"catalog", "interpretation", "audit", "facts"}:
                raise ConnectedDailyError("checkpointed catalog record bundle is malformed")
            records.append(IngestionArtifacts(*(
                _artifact_from_mapping(store, record[key], f"catalog {key}")
                for key in ("catalog", "interpretation", "audit", "facts")
            )))
        completed_units = catalog.get("completed_units", [])
        remaining = catalog.get("remaining_work", {})
        if (
            not isinstance(completed_units, list)
            or any(not isinstance(item, str) or not item for item in completed_units)
            or not isinstance(remaining, Mapping)
        ):
            raise ConnectedDailyError("checkpointed catalog continuation is malformed")
        result = IngestionResult(
            True, catalog.get("phase_complete") is True, tuple(completed_units), dict(remaining),
            work, index, tuple(records), discovery,
            None if catalog.get("proposed_source_cursor") is None else dict(catalog["proposed_source_cursor"]),
        )
        context["work"], context["catalog"] = work, result
        mutable["source_catalog_index"] = index.reference
    reconcile = outputs.get("reconcile")
    task_sync = outputs.get("task_sync")
    if reconcile is not None:
        if task_sync is None:
            canonical = _artifact_from_mapping(store, reconcile.get("canonical_tasks"), "reconciled canonical tasks")
            mutable["canonical_tasks"] = canonical.reference
        mutable["guidelines"] = _artifact_from_mapping(store, reconcile.get("guidelines"), "guidelines").reference
        mutable["rolling_updates"] = _artifact_from_mapping(store, reconcile.get("rolling_updates"), "rolling updates").reference
    if task_sync is not None:
        canonical = _artifact_from_mapping(store, task_sync.get("canonical_tasks"), "task-synced canonical tasks")
        provider = _artifact_from_mapping(store, task_sync.get("provider_state"), "task provider state")
        mutable["canonical_tasks"], mutable["task_sync_state"] = canonical.reference, provider.reference
        completed = task_sync.get("completed_units", [])
        if not isinstance(completed, list) or any(not isinstance(item, str) or not item for item in completed):
            raise ConnectedDailyError("checkpointed task continuation is malformed")
        context["task_completed_units"] = list(completed)
    if catalog is not None and catalog.get("phase_complete") is True and reconcile is not None:
        view = ingestion.current_catalog_view(
            catalog_parent=mutable["source_catalog_folder"],
            index_reference=mutable["source_catalog_index"], max_bytes=max_bytes,
        )
        register = _json(store.read(mutable["canonical_tasks"]).data, "checkpointed canonical tasks")
        brief_tasks = unresolved_finite_task_selection(register, task_source_links=view.task_source_links)
        context.update({
            "view": view,
            "reconciled": ConnectedTaskReconcileResult(store.read(mutable["canonical_tasks"]), brief_tasks),
            "brief_tasks": brief_tasks,
        })
    delivered = outputs.get("brief_delivery")
    if delivered is not None:
        state_reference = _reference_from_mapping(delivered.get("delivery_state"), "delivery state")
        mutable["delivery_state"] = state_reference
        delivery = delivered.get("delivery")
        if not isinstance(delivery, Mapping):
            raise ConnectedDailyError("checkpointed delivery result is malformed")
        context.update({
            "delivery": dict(delivery),
            "brief_input": _artifact_from_mapping(store, delivered.get("brief_input"), "brief input"),
            "brief_html": _artifact_from_mapping(store, delivered.get("brief_html"), "brief HTML"),
            "brief_text": _artifact_from_mapping(store, delivered.get("brief_text"), "brief text"),
        })
    return context


class ConnectedDailyRuntime:
    """Resolve one admitted instance and execute its concrete connected stages."""

    def __init__(self, *, installed_root: Path, recovery: Mapping[str, Any], run_directory: Path,
                 drive: Any, gmail: Any, sheets: Any, semantic: Any) -> None:
        self.root, self.recovery, self.run_directory = installed_root, dict(recovery), run_directory
        self.drive, self.gmail, self.sheets, self.semantic = drive, gmail, sheets, semantic

    def run(self, *, entrypoint: str, operation_id: str, attempt_id: str,
            scheduler_admitted: bool = False, delivery_variant: str | None = None) -> OperationResult:
        instance = _Resolver(root=self.root, recovery=self.recovery, drive=self.drive).resolve(
            entrypoint=entrypoint, delivery_variant=delivery_variant,
        )
        store = CodexDriveArtifactStore(self.drive, scratch_directory=self.run_directory / "artifact-scratch")
        listing = CodexDriveReferenceStorage(self.drive)
        normalizer = GmailMimeNormalizer(instance.household["timezone"])
        source_bytes = ConnectedSourceAdapters(peer=self.gmail.peer, run_directory=self.run_directory)
        source = CodexGmailSourceAdapter(
            self.gmail, max_thread_messages=instance.source_scope["max_thread_messages"],
            normalize_message=normalizer.normalize,
            normalize_attachment=lambda message_id, attachment_id, raw: source_bytes.gmail_attachment(
                message_id, attachment_id, mime_type=raw["mime_type"], declared_byte_size=raw["size_bytes"],
            ),
        )
        callbacks = CodexSemanticCallbacks(self.semantic)
        ingestion = ConnectedIngestionWorker(
            source=source, store=store, adapter_id=instance.source_scope["adapter_id"],
            catalog_schema=_schema(self.root, "source-conversation.schema.json"),
            fact_schema=_schema(self.root, "fact.schema.json"),
            extraction_schema=_schema(self.root, "extraction-result.schema.json"),
            interpreter=callbacks.interpret, auditor=callbacks.audit,
            supported_attachment_mime_types=("text/plain", "application/pdf", "image/png", "image/jpeg"),
            attachment_extractors={
                "application/pdf": lambda item: source_bytes.extract_pdf(source_id=item.identity, data=item.data or b""),
                "image/png": lambda item: source_bytes.extract_image(source_id=item.identity, data=item.data or b"", mime_type=item.mime_type),
                "image/jpeg": lambda item: source_bytes.extract_image(source_id=item.identity, data=item.data or b"", mime_type=item.mime_type),
            },
            resource_fetcher=source_bytes.fetch_https,
            max_attachment_bytes=instance.policies["execution"]["max_bytes_per_unit"],
            max_resource_bytes=instance.policies["execution"]["max_bytes_per_unit"],
        )
        task_worker = ConnectedTaskWorker(
            store=store, fact_schema=_schema(self.root, "fact.schema.json"),
            task_schema=_schema(self.root, "task.schema.json"),
            register_schema=_schema(self.root, "canonical-tasks.schema.json"),
            provider_state_schema=_schema(self.root, "provider-state.schema.json"),
        )
        release = {
            "version": self.recovery["manifest"]["package"]["version"],
            "source_commit": self.recovery["manifest"]["package"]["source_identity"]["commit"],
        }
        local_date = datetime.now(ZoneInfo(instance.household["timezone"])).date().isoformat()
        manager = _CheckpointManager(
            store=store, listing=listing, state=instance.file_map["operation_state"],
            folder=instance.file_map["operation_checkpoints_folder"], operation_id=operation_id,
            attempt_id=attempt_id, entrypoint=entrypoint, release=release,
            fingerprint=instance.configuration_fingerprint,
            scope={
                "source_scope_sha256": sha256_bytes(canonical_json_bytes(instance.source_scope)),
                "entrypoint": entrypoint,
                "profile_sha256": sha256_bytes(instance.profile_artifact.data),
                "delivery_variant": instance.delivery["variant"],
                "run_local_date": local_date,
            },
            schemas={"state": _schema(self.root, "operation-state.schema.json"), "checkpoint": _schema(self.root, "operation-checkpoint.schema.json")},
            serialization_mode=instance.policies["execution"]["serialization_mode"],
        )
        mutable = dict(instance.file_map)
        context = _restore_daily_state(
            manager=manager, store=store, ingestion=ingestion,
            mutable=mutable, max_bytes=instance.policies["execution"]["max_bytes_per_unit"],
        )
        current_phase = "preflight"

        def preflight(_previous: Mapping[str, Any]) -> dict[str, Any]:
            nonlocal current_phase
            current_phase = "preflight"
            return {"verified": True, "phase_complete": True, "configuration_fingerprint": instance.configuration_fingerprint}

        def discover(_previous: Mapping[str, Any]) -> dict[str, Any]:
            nonlocal current_phase
            current_phase = "discover"
            result = ingestion.discover(
                scope={
                    key: instance.source_scope[key]
                    for key in (
                        "query", "label_ids", "max_results",
                        "seed_after_inclusive_ms", "seed_before_exclusive_ms",
                    )
                    if key in instance.source_scope
                },
                discovery_parent=instance.root,
                discovery_name=f"state/runs/{operation_id}-discovery.json",
            )
            context["discovery"] = result
            return result.as_stage_result()

        def catalog(_previous: Mapping[str, Any]) -> dict[str, Any]:
            nonlocal current_phase
            current_phase = "catalog"
            discovery = context.get("discovery")
            if discovery is None:
                raise ConnectedDailyError("catalog lacks its verified discovery artifact")
            work = context.get("work")
            if work is None:
                initial = canonical_json_bytes({"schema_version": 1, "discovery_sha256": None, "completed_conversation_ids": [], "units": []})
                name = f"state/runs/{operation_id}-source-work.json"
                work = store.read_named(instance.root, name)
                if work is None:
                    work = store.write_immutable(instance.root, name, initial, "application/json")
            result = ingestion.catalog(
                discovery_reference=discovery.inventory.reference,
                catalog_parent=mutable["source_catalog_folder"], index_reference=mutable["source_catalog_index"],
                work_reference=work.reference, max_records=instance.policies["execution"]["max_records_per_unit"],
                max_bytes=instance.policies["execution"]["max_bytes_per_unit"],
            )
            context["work"], mutable["source_catalog_index"] = result.work, result.index.reference
            context["catalog"] = result
            return result.as_stage_result()

        def reconcile(_previous: Mapping[str, Any]) -> dict[str, Any]:
            nonlocal current_phase
            current_phase = "reconcile"
            catalog_result = context.get("catalog")
            if catalog_result is None or not catalog_result.phase_complete:
                raise ConnectedDailyError("reconcile requires a complete catalog phase")
            view = ingestion.current_catalog_view(
                catalog_parent=mutable["source_catalog_folder"], index_reference=mutable["source_catalog_index"],
                max_bytes=instance.policies["execution"]["max_bytes_per_unit"],
            )
            result = task_worker.reconcile(
                facts=[item.facts.reference for item in view.artifacts], canonical_tasks=mutable["canonical_tasks"],
                task_source_links=view.task_source_links, source_disposition=catalog_result.as_stage_result(),
            )
            mutable["canonical_tasks"] = result.canonical_tasks.reference
            derived = build_derived_knowledge(
                view.facts, fact_schema=_schema(self.root, "fact.schema.json"), task_schema=_schema(self.root, "task.schema.json"),
            )
            guidelines = store.replace(mutable["guidelines"].current(), canonical_json_bytes({"schema_version": 1, "guidelines": derived["guidelines"]}), mutable["guidelines"].mime_type)
            mutable["guidelines"] = guidelines.reference
            rolling = store.replace(mutable["rolling_updates"].current(), canonical_json_bytes({"schema_version": 1, "rolling_updates": derived["rolling_updates"]}), mutable["rolling_updates"].mime_type)
            mutable["rolling_updates"] = rolling.reference
            context.update({"view": view, "reconciled": result, "brief_tasks": result.brief_tasks})
            return {
                "verified": True, "phase_complete": True,
                "canonical_tasks": _artifact_mapping(result.canonical_tasks),
                "guidelines": _artifact_mapping(guidelines), "rolling_updates": _artifact_mapping(rolling),
            }

        def task_sync(_previous: Mapping[str, Any]) -> dict[str, Any]:
            nonlocal current_phase
            current_phase = "task_sync"
            reconciled = context.get("reconciled")
            view = context.get("view")
            if reconciled is None or view is None:
                raise ConnectedDailyError("task sync lacks its exact reconcile handoff")
            native = CodexSheetsTaskPort(self.sheets, instance.sheet_scope)
            provider = GoogleSheetsTaskAdapter(instance.sheet_scope.adapter_scope, native, comments=native).begin_sync()
            result = task_worker.task_sync(
                canonical_tasks=mutable["canonical_tasks"],
                provider_state=mutable["task_sync_state"], provider=provider,
                task_source_links=view.task_source_links,
            )
            mutable["canonical_tasks"], mutable["task_sync_state"] = result.canonical_tasks.reference, result.provider_state.reference
            context["task_result"], context["brief_tasks"] = result, result.brief_tasks
            completed_units = context.setdefault("task_completed_units", [])
            completed_units.append(
                f'task-sync-{len(completed_units) + 1}:{result.canonical_tasks.reference.version}:{result.provider_state.reference.version}'
            )
            return {
                "verified": True, "phase_complete": not result.continuation_required,
                "completed_units": list(completed_units),
                "remaining_work": {"provider_reconciliation": True} if result.continuation_required else {},
                "canonical_tasks": _artifact_mapping(result.canonical_tasks),
                "provider_state": _artifact_mapping(result.provider_state),
            }

        def brief_delivery(_previous: Mapping[str, Any]) -> dict[str, Any]:
            nonlocal current_phase
            current_phase = "brief_delivery"
            view, brief_tasks = context.get("view"), context.get("brief_tasks")
            if view is None or brief_tasks is None:
                raise ConnectedDailyError("brief lacks all-current catalog and task views")
            today = manager.scope["run_local_date"]
            entities = [
                {"entity_id": item["entity_id"], "display_name": item["display_name"], "kind": "household" if item["type"] == "shared" else "child"}
                for item in sorted(instance.household["entities"], key=lambda item: item["sort_order"])
            ]
            scope_to_entity = {item["entity_id"]: item["entity_id"] for item in entities}
            value = build_brief_input(
                run_local_date=today, timezone=instance.household["timezone"], entities=entities,
                scope_to_entity=scope_to_entity, facts=view.facts, source_record_map=view.source_record_map,
                current_guideline_selection=view.current_guideline_selection,
                unresolved_task_view=brief_tasks, task_source_links=view.task_source_links,
                template=instance.brief_template,
                input_hashes={"catalog_index": sha256_bytes(view.index.data), "canonical_tasks": sha256_bytes(store.read(mutable["canonical_tasks"]).data)},
            )
            rendered = render_brief(value, _schema(self.root, "brief-input.schema.json"))
            brief_input = store.write_immutable(instance.root, f"state/runs/{operation_id}-brief-input.json", canonical_json_bytes(value), "application/json")
            brief_html = store.write_immutable(instance.root, f"state/runs/{operation_id}-brief.html", rendered["html"], "text/html")
            brief_text = store.write_immutable(instance.root, f"state/runs/{operation_id}-brief.txt", rendered["text"], "text/plain")
            key = delivery_key(instance.instance["instance_id"], "daily-run", today, instance.delivery["variant"])
            request = ExactDeliveryRequest.build(
                key=key, variant=instance.delivery["variant"], to=instance.delivery["to"], cc=instance.delivery["cc"], bcc=instance.delivery["bcc"],
                subject=f'{instance.delivery["subject_prefix"]} [School-OS:{key}]', text=rendered["text"], html=rendered["html"],
            )
            context["delivery_key"] = key
            state_artifact = store.read(mutable["delivery_state"].current())
            mutable["delivery_state"] = state_artifact.reference
            state = _json(state_artifact.data, "delivery state")
            if set(state) != {"schema_version", "deliveries", "effects"} or state.get("schema_version") != 1 or not isinstance(state["deliveries"], dict) or not isinstance(state["effects"], dict):
                raise ConnectedDailyError("delivery state has an unsupported shape")

            def persist(section: str, candidate: Mapping[str, Any]) -> None:
                nonlocal state
                state = {**state, section: {**state[section], key: dict(candidate)}}
                written = store.replace(mutable["delivery_state"], canonical_json_bytes(state), mutable["delivery_state"].mime_type)
                mutable["delivery_state"] = written.reference
                state = _json(written.data, "delivery state readback")

            def sent(identity: str) -> dict[str, Any]:
                raw = self.gmail.read(identity, "raw")
                if not isinstance(raw, Mapping) or raw.get("id") != identity or not isinstance(raw.get("raw"), str):
                    raise ConnectedDailyError("Gmail Sent readback is malformed")
                try:
                    data = base64.b64decode(raw["raw"] + "=" * (-len(raw["raw"]) % 4), altchars=b"-_", validate=True)
                except (binascii.Error, ValueError) as exc:
                    raise ConnectedDailyError("Gmail Sent raw MIME is invalid") from exc
                return {"id": identity, "raw": data, "label_ids": raw.get("label_ids")}

            def search(token: str | None):
                args = {"query": f'in:sent "[School-OS:{key}]"', "label_ids": ["SENT"], "max_results": 100}
                if token is not None:
                    args["next_page_token"] = token
                page = self.gmail.search_ids(**args)
                if not isinstance(page, Mapping) or not isinstance(page.get("message_ids"), list):
                    raise ConnectedDailyError("Gmail Sent search is malformed")
                return tuple({"id": identity} for identity in page["message_ids"]), page.get("next_page_token")

            result = deliver_exact(
                request, read_ledger=lambda: state["deliveries"].get(key),
                persist_ledger=lambda value: persist("deliveries", value),
                read_effect_checkpoint=lambda: state["effects"].get(key),
                persist_effect_checkpoint=lambda value: persist("effects", value),
                send=lambda exact: self.gmail.send(exact.gmail_args()), read_sent=sent, search_sent=search,
            )
            context.update({"delivery": result, "brief_input": brief_input, "brief_html": brief_html, "brief_text": brief_text})
            effect_outcome = "confirmed" if result["outcome"] in {"confirmed", "reconciled", "suppressed"} else "unknown"
            return {
                "verified": True, "phase_complete": True,
                "brief_input": _artifact_mapping(brief_input), "brief_html": _artifact_mapping(brief_html), "brief_text": _artifact_mapping(brief_text),
                "delivery_state": _reference_mapping(mutable["delivery_state"]), "delivery": {key: value for key, value in result.items() if key != "ledger"},
                "effects": [{"effect_id": key, "kind": "mail.send", "outcome": effect_outcome, "verification": {"provider_message_id": result["provider_message_id"]}}],
            }

        def commit(_previous: Mapping[str, Any]) -> dict[str, Any]:
            nonlocal current_phase
            current_phase = "commit"
            catalog_result, delivery = context.get("catalog"), context.get("delivery")
            if catalog_result is None or catalog_result.proposed_cursor is None or delivery is None or delivery.get("outcome") not in {"confirmed", "reconciled", "suppressed"}:
                raise ConnectedDailyError("commit requires complete catalog cursor and exact delivery")
            evidence = canonical_json_bytes({
                "schema_version": 1, "operation_id": operation_id, "attempt_id": attempt_id,
                "outcome": "COMPLETE", "catalog_index": _reference_mapping(mutable["source_catalog_index"]),
                "canonical_tasks": _reference_mapping(mutable["canonical_tasks"]),
                "provider_state": _reference_mapping(mutable["task_sync_state"]),
                "delivery": {key: value for key, value in delivery.items() if key != "ledger"},
                "proposed_source_cursor": catalog_result.proposed_cursor,
            })
            final = store.replace(mutable["final_run_checkpoint"].current(), evidence, mutable["final_run_checkpoint"].mime_type)
            mutable["final_run_checkpoint"] = final.reference
            cursor_bytes = canonical_json_bytes(catalog_result.proposed_cursor)
            cursor = store.replace(mutable["source_checkpoint"].current(), cursor_bytes, mutable["source_checkpoint"].mime_type)
            mutable["source_checkpoint"] = cursor.reference
            return {"verified": True, "phase_complete": True, "final_evidence": _artifact_mapping(final), "source_cursor": _artifact_mapping(cursor)}

        stages = {
            "preflight": preflight, "discover": discover, "catalog": catalog,
            "reconcile": reconcile, "task_sync": task_sync,
            "brief_delivery": brief_delivery, "commit": commit,
        }
        try:
            result = run_daily(
                profile=instance.profile, capability_schema=_schema(self.root, "capability-profile.schema.json"),
                entrypoint=entrypoint, operation_id=operation_id, attempt_id=attempt_id,
                stages=stages, required_capabilities=REQUIRED_CAPABILITIES,
                scheduler_admission=(lambda: scheduler_admitted), checkpoint=manager.persist,
                resume_after=manager.resume_after,
                durable_predecessor_output=manager.durable_predecessor_output,
            )
        except Exception as exc:
            effects = []
            if current_phase == "brief_delivery" and isinstance(context.get("delivery_key"), str):
                effects = [{
                    "effect_id": context["delivery_key"], "kind": "mail.send", "outcome": "unknown",
                    "verification": {"reconciliation_required": True},
                }]
            manager.block(current_phase, exc, effects=effects)
            raise
        if result.outcome == "COMPLETE":
            manager.complete(result)
        return result
