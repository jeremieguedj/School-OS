"""Drive-generation task synchronization and guided provider switching.

Provider-native reads and writes remain the user's agent's responsibility.
These functions only validate normalized exchanges and publish canonical state
before or after one externally executed semantic action.
"""
from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .agent_tasks import (
    AgentTaskPlan, authorize_next_action, confirm_action,
    initialize_provider_state, plan_task_sync, validate_snapshot,
)
from .audio import merge_parent_task_delta
from .connected_storage import BundleTransactionStore, ConnectedStorageError
from .contracts import canonical_json_bytes, sha256_bytes, validate


class HybridTaskError(ValueError):
    """Raised when a task generation or guided switch cannot advance safely."""


_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,191}$")
_SELECTOR_PATH = "state/task-provider-selector.json"
_CANONICAL_PATH = "data/canonical-tasks.json"


@dataclass(frozen=True)
class HybridTaskAdvance:
    transaction: BundleTransactionStore
    provider_key: str
    provider_state: dict[str, Any]
    action: dict[str, Any] | None = None


def provider_state_path(binding_id: str) -> str:
    if not isinstance(binding_id, str) or _IDENTITY.fullmatch(binding_id) is None:
        raise HybridTaskError("task binding identity is not path-safe")
    return f"state/task-providers/{binding_id}.json"


def adapter_configuration_path(binding_id: str) -> str:
    if not isinstance(binding_id, str) or _IDENTITY.fullmatch(binding_id) is None:
        raise HybridTaskError("task binding identity is not path-safe")
    return f"state/task-adapters/{binding_id}.json"


def _json(transaction: BundleTransactionStore, path: str, label: str) -> dict[str, Any]:
    try:
        data = transaction.read(path).data
        value = json.loads(data.decode("utf-8"))
    except (ConnectedStorageError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HybridTaskError(f"{label} is unavailable or invalid") from exc
    if not isinstance(value, dict) or canonical_json_bytes(value) != data:
        raise HybridTaskError(f"{label} is not canonical JSON")
    return value


def _schemas(root: Path) -> dict[str, dict[str, Any]]:
    names = (
        "task.schema.json", "canonical-tasks.schema.json",
        "provider-state.schema.json", "task-adapter-snapshot.schema.json",
        "task-adapter-action.schema.json", "task-adapter-result.schema.json",
        "task-provider-selector.schema.json",
    )
    return {
        name: json.loads((root / "schemas" / name).read_text(encoding="utf-8"))
        for name in names
    }


def _selector(
    transaction: BundleTransactionStore, schemas: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    selector = _json(transaction, _SELECTOR_PATH, "task-provider selector")
    errors = validate(selector, dict(schemas["task-provider-selector.schema.json"]))
    if errors:
        raise HybridTaskError("task-provider selector is invalid: " + "; ".join(errors))
    return selector


def _binding(selector: Mapping[str, Any], provider_key: str) -> dict[str, Any]:
    binding = selector.get("bindings", {}).get(provider_key)
    required = {
        "adapter_configuration_path", "adapter_configuration_sha256",
        "adapter_contract_version", "adapter_id", "binding_id", "provider_id",
        "provider_state_path", "scope_sha256", "status",
    }
    if not isinstance(binding, Mapping) or set(binding) != required:
        raise HybridTaskError("task-provider binding is malformed")
    if binding.get("adapter_contract_version") != "agent-task-v1":
        raise HybridTaskError("task-provider binding uses an unsupported contract")
    if binding.get("provider_state_path") != provider_state_path(binding.get("binding_id")):
        raise HybridTaskError("task-provider binding state path is not identity-derived")
    if binding.get("adapter_configuration_path") != adapter_configuration_path(binding.get("binding_id")):
        raise HybridTaskError("task-provider adapter path is not identity-derived")
    return dict(binding)


def _operable_binding(
    selector: Mapping[str, Any], provider_key: str, binding: Mapping[str, Any],
) -> bool:
    if (
        provider_key == selector.get("selected_provider")
        and binding.get("status") == "active"
    ):
        return True
    switch = selector.get("switch")
    return bool(
        selector.get("status") == "switching"
        and isinstance(switch, Mapping)
        and switch.get("target_provider") == provider_key
        and binding.get("status") == "staging"
    )


def _require_operable_binding(
    selector: Mapping[str, Any], provider_key: str, binding: Mapping[str, Any],
) -> None:
    if not _operable_binding(selector, provider_key, binding):
        raise HybridTaskError(
            "task sync may address only the selected or staged provider"
        )


def _policy(value: Mapping[str, Any] | None) -> dict[str, Any]:
    if value is None:
        return {
            "completion_comment_required": True,
            "reopen_when_comment_missing": True,
            "missing_comment_reminder": "Completion needs a parent comment before it can be recorded.",
        }
    required = {
        "completion_comment_required", "reopen_when_comment_missing",
        "missing_comment_reminder",
    }
    if set(value) != required or not all(
        isinstance(value[key], bool)
        for key in ("completion_comment_required", "reopen_when_comment_missing")
    ) or not isinstance(value["missing_comment_reminder"], str):
        raise HybridTaskError("task completion policy is malformed")
    return dict(value)


def _plan(
    *, transaction: BundleTransactionStore, schemas: Mapping[str, Mapping[str, Any]],
    binding: Mapping[str, Any], snapshot: Mapping[str, Any],
    completion_policy: Mapping[str, Any] | None,
) -> AgentTaskPlan:
    register = _json(transaction, _CANONICAL_PATH, "canonical task register")
    state = _json(transaction, binding["provider_state_path"], "task-provider state")
    policy = _policy(completion_policy)
    return plan_task_sync(
        register, state, snapshot,
        task_schema=schemas["task.schema.json"],
        register_schema=schemas["canonical-tasks.schema.json"],
        provider_state_schema=schemas["provider-state.schema.json"],
        snapshot_schema=schemas["task-adapter-snapshot.schema.json"],
        action_schema=schemas["task-adapter-action.schema.json"],
        **policy,
    )


def plan_hybrid_task_sync(
    *, storage: Any, transaction: BundleTransactionStore, installed_root: Path,
    snapshot: Mapping[str, Any], serialization: Mapping[str, Any],
    provider_key: str | None = None,
    completion_policy: Mapping[str, Any] | None = None,
) -> HybridTaskAdvance:
    """Import one complete snapshot and publish pending semantic actions."""
    schemas = _schemas(installed_root)
    selector = _selector(transaction, schemas)
    key = provider_key or selector["selected_provider"]
    binding = _binding(selector, key)
    _require_operable_binding(selector, key, binding)
    before = _json(transaction, _CANONICAL_PATH, "canonical task register")
    plan = _plan(
        transaction=transaction, schemas=schemas, binding=binding,
        snapshot=snapshot, completion_policy=completion_policy,
    )
    try:
        delta = _json(transaction, "state/pending-run-delta.json", "pending run delta")
    except HybridTaskError:
        delta = {"schema_version": 1, "facts": [], "tasks": []}
    delta = merge_parent_task_delta(delta, before, plan.canonical_tasks)
    committed = (
        transaction
        .stage(_CANONICAL_PATH, canonical_json_bytes(plan.canonical_tasks))
        .stage(binding["provider_state_path"], canonical_json_bytes(plan.provider_state))
        .stage("state/pending-run-delta.json", canonical_json_bytes(delta), role="reconciliation_delta", media_type="application/json")
        .publish(storage, serialization)
    )
    return HybridTaskAdvance(committed, key, plan.provider_state)


def authorize_hybrid_task_action(
    *, storage: Any, transaction: BundleTransactionStore, installed_root: Path,
    serialization: Mapping[str, Any], provider_key: str | None = None,
) -> HybridTaskAdvance:
    """Publish one exact unknown action before exposing it for native dispatch."""
    schemas = _schemas(installed_root)
    selector = _selector(transaction, schemas)
    key = provider_key or selector["selected_provider"]
    binding = _binding(selector, key)
    _require_operable_binding(selector, key, binding)
    state = _json(transaction, binding["provider_state_path"], "task-provider state")
    authorized, action = authorize_next_action(
        state, action_schema=schemas["task-adapter-action.schema.json"],
        provider_state_schema=schemas["provider-state.schema.json"],
    )
    committed = transaction.stage(
        binding["provider_state_path"], canonical_json_bytes(authorized),
    ).publish(storage, serialization)
    return HybridTaskAdvance(committed, key, authorized, action)


def confirm_hybrid_task_action(
    *, storage: Any, transaction: BundleTransactionStore, installed_root: Path,
    result: Mapping[str, Any], serialization: Mapping[str, Any],
    provider_key: str | None = None,
) -> HybridTaskAdvance:
    """Validate normalized exact readback and publish confirmation only."""
    schemas = _schemas(installed_root)
    selector = _selector(transaction, schemas)
    key = provider_key or selector["selected_provider"]
    binding = _binding(selector, key)
    _require_operable_binding(selector, key, binding)
    register = _json(transaction, _CANONICAL_PATH, "canonical task register")
    state = _json(transaction, binding["provider_state_path"], "task-provider state")
    confirmation = confirm_action(
        register, state, result,
        register_schema=schemas["canonical-tasks.schema.json"],
        provider_state_schema=schemas["provider-state.schema.json"],
        action_schema=schemas["task-adapter-action.schema.json"],
        result_schema=schemas["task-adapter-result.schema.json"],
    )
    committed = (
        transaction
        .stage(_CANONICAL_PATH, canonical_json_bytes(confirmation.canonical_tasks))
        .stage(binding["provider_state_path"], canonical_json_bytes(confirmation.provider_state))
        .publish(storage, serialization)
    )
    return HybridTaskAdvance(committed, key, confirmation.provider_state)


def begin_hybrid_task_switch(
    *, storage: Any, transaction: BundleTransactionStore, installed_root: Path,
    target: Mapping[str, Any], target_snapshot: Mapping[str, Any],
    adapter_configuration: bytes | None, old_snapshot_sha256: str,
    serialization: Mapping[str, Any],
    completion_policy: Mapping[str, Any] | None = None,
) -> HybridTaskAdvance:
    """Stage a target projection while the old selected provider remains active."""
    schemas = _schemas(installed_root)
    selector = _selector(transaction, schemas)
    if selector["status"] != "bound" or selector["switch"] is not None:
        raise HybridTaskError("a guided task switch is already active or selector is unbound")
    old_key = selector["selected_provider"]
    old = _binding(selector, old_key)
    old_state = _json(transaction, old["provider_state_path"], "old task-provider state")
    if old["status"] != "active" or old_state.get("pending_actions"):
        raise HybridTaskError("old selected provider is not fully reconciled")
    if old_state.get("last_snapshot_sha256") != old_snapshot_sha256:
        raise HybridTaskError("guided switch lacks the exact final old-provider pull")
    required = {
        "provider_key", "provider_id", "adapter_id", "binding_id", "scope_sha256",
    }
    if set(target) != required or any(
        not isinstance(target.get(key), str) or not target[key] for key in required
    ):
        raise HybridTaskError("guided switch target binding is malformed")
    target_key = target["provider_key"]
    if target_key == old_key:
        raise HybridTaskError("guided switch target is already selected")
    target_state_path = provider_state_path(target["binding_id"])
    target_configuration_path = adapter_configuration_path(target["binding_id"])
    existing = selector["bindings"].get(target_key)
    staged = transaction
    if existing is None:
        if not isinstance(adapter_configuration, bytes) or not adapter_configuration:
            raise HybridTaskError("new switch target requires adapter configuration bytes")
        normalized = validate_snapshot(
            target_snapshot, schemas["task-adapter-snapshot.schema.json"],
        )
        for field in ("provider_id", "adapter_id", "binding_id", "scope_sha256"):
            if normalized[field] != target[field]:
                raise HybridTaskError(f"target snapshot {field} disagrees with binding")
        if normalized["tasks"] or normalized["unbound_candidates"]:
            raise HybridTaskError("new isolated switch target is not empty")
        target_state = initialize_provider_state(
            provider_id=target["provider_id"], adapter_id=target["adapter_id"],
            binding_id=target["binding_id"], scope_sha256=target["scope_sha256"],
        )
        configuration_sha256 = sha256_bytes(adapter_configuration)
        binding = {
            "adapter_configuration_path": target_configuration_path,
            "adapter_configuration_sha256": configuration_sha256,
            "adapter_contract_version": "agent-task-v1",
            "adapter_id": target["adapter_id"], "binding_id": target["binding_id"],
            "provider_id": target["provider_id"],
            "provider_state_path": target_state_path,
            "scope_sha256": target["scope_sha256"], "status": "staging",
        }
        staged = (
            staged
            .stage(
                target_configuration_path, adapter_configuration,
                role="task_adapter_configuration", media_type="application/json",
            )
            .stage(
                target_state_path, canonical_json_bytes(target_state),
                role="task_sync_state", media_type="application/json",
                schema_id="provider-state.schema.json",
            )
        )
    else:
        binding = _binding(selector, target_key)
        if binding["status"] != "dormant" or any(
            binding[field] != target[field]
            for field in ("provider_id", "adapter_id", "binding_id", "scope_sha256")
        ):
            raise HybridTaskError("dormant switch target binding disagrees")
        if adapter_configuration is not None and sha256_bytes(adapter_configuration) != binding["adapter_configuration_sha256"]:
            raise HybridTaskError("dormant switch target configuration differs")
        target_state = _json(staged, binding["provider_state_path"], "dormant task-provider state")
        binding["status"] = "staging"

    temporary_selector = {
        **selector,
        "bindings": {**selector["bindings"], target_key: binding},
        "status": "switching",
        "switch": {
            "switch_id": "task-switch-" + sha256_bytes(canonical_json_bytes({
                "old": old_key, "target": target_key,
                "old_snapshot_sha256": old_snapshot_sha256,
                "target_scope_sha256": target["scope_sha256"],
            })),
            "old_provider": old_key, "target_provider": target_key,
            "old_snapshot_sha256": old_snapshot_sha256,
            "phase": "staging",
        },
    }
    staged = staged.stage(_SELECTOR_PATH, canonical_json_bytes(temporary_selector))
    # Plan target projection before publishing the staging generation.
    register = _json(staged, _CANONICAL_PATH, "canonical task register")
    policy = _policy(completion_policy)
    plan = plan_task_sync(
        register, target_state, target_snapshot,
        task_schema=schemas["task.schema.json"],
        register_schema=schemas["canonical-tasks.schema.json"],
        provider_state_schema=schemas["provider-state.schema.json"],
        snapshot_schema=schemas["task-adapter-snapshot.schema.json"],
        action_schema=schemas["task-adapter-action.schema.json"],
        **policy,
    )
    if canonical_json_bytes(plan.canonical_tasks) != canonical_json_bytes(register) or plan.review_cases:
        raise HybridTaskError("staged or dormant target contains unselected parent changes")
    committed = staged.stage(
        binding["provider_state_path"], canonical_json_bytes(plan.provider_state),
    ).publish(storage, serialization)
    return HybridTaskAdvance(committed, target_key, plan.provider_state)


def activate_hybrid_task_switch(
    *, storage: Any, transaction: BundleTransactionStore, installed_root: Path,
    target_snapshot: Mapping[str, Any], serialization: Mapping[str, Any],
    completion_policy: Mapping[str, Any] | None = None,
) -> HybridTaskAdvance:
    """Verify the staged target completely, then publish the selector change."""
    schemas = _schemas(installed_root)
    selector = _selector(transaction, schemas)
    switch = selector.get("switch")
    if selector.get("status") != "switching" or not isinstance(switch, Mapping):
        raise HybridTaskError("no guided task switch is ready for activation")
    old_key, target_key = switch.get("old_provider"), switch.get("target_provider")
    if selector.get("selected_provider") != old_key:
        raise HybridTaskError("guided switch changed the selected provider before activation")
    old, target = _binding(selector, old_key), _binding(selector, target_key)
    if old["status"] != "active" or target["status"] != "staging":
        raise HybridTaskError("guided switch binding statuses are invalid")
    register = _json(transaction, _CANONICAL_PATH, "canonical task register")
    plan = _plan(
        transaction=transaction, schemas=schemas, binding=target,
        snapshot=target_snapshot, completion_policy=completion_policy,
    )
    if plan.actions or plan.review_cases or canonical_json_bytes(plan.canonical_tasks) != canonical_json_bytes(register):
        raise HybridTaskError("target projection is not exactly staged for activation")
    old["status"], target["status"] = "dormant", "active"
    activated = {
        **selector, "selected_provider": target_key, "status": "bound",
        "bindings": {**selector["bindings"], old_key: old, target_key: target},
        "switch": None,
    }
    committed = (
        transaction
        .stage(target["provider_state_path"], canonical_json_bytes(plan.provider_state))
        .stage(_SELECTOR_PATH, canonical_json_bytes(activated))
        .publish(storage, serialization)
    )
    return HybridTaskAdvance(committed, target_key, plan.provider_state)


def abort_hybrid_task_switch(
    *, storage: Any, transaction: BundleTransactionStore, installed_root: Path,
    serialization: Mapping[str, Any],
) -> BundleTransactionStore:
    """Leave the old provider active after a failed target preparation."""
    schemas = _schemas(installed_root)
    selector = _selector(transaction, schemas)
    switch = selector.get("switch")
    if selector.get("status") != "switching" or not isinstance(switch, Mapping):
        raise HybridTaskError("no guided task switch is active")
    old_key, target_key = switch.get("old_provider"), switch.get("target_provider")
    old, target = _binding(selector, old_key), _binding(selector, target_key)
    target_state = _json(
        transaction, target["provider_state_path"], "target task-provider state",
    )
    pending = target_state.get("pending_actions")
    if not isinstance(pending, list):
        raise HybridTaskError("target task-provider pending actions are malformed")
    if any(
        not isinstance(action, Mapping)
        or action.get("outcome") != "pending"
        or action.get("dispatch_attempt") != 0
        for action in pending
    ):
        raise HybridTaskError(
            "guided switch target has an action that may have reached the provider"
        )
    target_state = {**target_state, "pending_actions": []}
    old["status"], target["status"] = "active", "dormant"
    restored = {
        **selector, "selected_provider": old_key, "status": "bound",
        "bindings": {**selector["bindings"], old_key: old, target_key: target},
        "switch": None,
    }
    return (
        transaction
        .stage(target["provider_state_path"], canonical_json_bytes(target_state))
        .stage(_SELECTOR_PATH, canonical_json_bytes(restored))
        .publish(storage, serialization)
    )
