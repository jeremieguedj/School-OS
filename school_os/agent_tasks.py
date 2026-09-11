"""Provider-neutral task exchange for an agent-operated editable projection.

This module never calls a task provider.  It validates a complete normalized
snapshot, imports permitted parent changes, emits finite semantic actions, and
validates the agent's exact normalized readback.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from .contracts import canonical_json_bytes, sha256_bytes, validate
from .tasks import parent_task_from_provider


CONTRACT_VERSION = "agent-task-v1"
ACTION_KINDS = frozenset({
    "create_task", "claim_task", "update_task_fields",
    "set_task_resolution", "write_system_comment",
})
NORMALIZED_FIELDS = (
    "canonical_task_id", "origin", "action", "task_context", "entity_scope",
    "workflow_state", "source_link", "source_due", "parent_planned_due",
    "latest_progress", "resolution", "completion_comment",
)
OPTIONAL_FIELDS = frozenset({
    "source_link", "source_due", "parent_planned_due", "latest_progress",
    "completion_comment",
})
COMMENT_FIELDS = frozenset({"comment_id", "kind", "text", "effect_id"})
PARENT_FIELDS = {
    "action": "action",
    "entity_scope": "entity_scope",
    "parent_planned_due": "parent_planned_due",
    "latest_progress": "latest_progress",
}
SYSTEM_FIELDS = frozenset({
    "canonical_task_id", "origin", "task_context", "workflow_state",
    "source_link", "source_due",
})


class AgentTaskError(ValueError):
    """Raised when an agent task exchange cannot be trusted."""


@dataclass(frozen=True)
class AgentTaskPlan:
    canonical_tasks: dict[str, Any]
    provider_state: dict[str, Any]
    actions: tuple[dict[str, Any], ...]
    review_cases: tuple[dict[str, Any], ...]


@dataclass(frozen=True)
class AgentTaskConfirmation:
    canonical_tasks: dict[str, Any]
    provider_state: dict[str, Any]
    remaining_actions: tuple[dict[str, Any], ...]


def _validated(value: Any, schema: Mapping[str, Any], label: str) -> None:
    errors = validate(value, dict(schema))
    if errors:
        raise AgentTaskError(f"invalid {label}: " + "; ".join(errors))


def _hash(value: Any) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def _required_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise AgentTaskError(f"{label} must be a nonempty string")
    return value


def _normalized_task(value: Mapping[str, Any], *, require_object_id: bool) -> dict[str, Any]:
    allowed = set(NORMALIZED_FIELDS) | {
        "provider_object_id", "provider_revision", "observation_sha256",
        "comment_evidence",
    }
    if set(value) - allowed:
        raise AgentTaskError("normalized provider task contains provider-specific fields")
    required = set(NORMALIZED_FIELDS) | {"provider_revision", "observation_sha256", "comment_evidence"}
    if require_object_id:
        required.add("provider_object_id")
    missing = required - set(value)
    if missing:
        raise AgentTaskError("normalized provider task omits required fields: " + ", ".join(sorted(missing)))
    result = {field: value.get(field) for field in NORMALIZED_FIELDS}
    for field in ("canonical_task_id", "origin", "action", "entity_scope", "workflow_state", "resolution"):
        _required_text(result[field], f"normalized task {field}")
    if not isinstance(result["task_context"], str):
        raise AgentTaskError("normalized task context must be a string")
    if result["origin"] not in {"source", "parent"}:
        raise AgentTaskError("normalized task origin is invalid")
    if result["workflow_state"] not in {"needs_action", "waiting_external", "needs_review"}:
        raise AgentTaskError("normalized task workflow state is invalid")
    if result["resolution"] not in {"unresolved", "completed"}:
        raise AgentTaskError("normalized task resolution is invalid")
    for field in OPTIONAL_FIELDS:
        if result[field] is not None and not isinstance(result[field], str):
            raise AgentTaskError(f"normalized optional field {field} is not string or null")
    object_id = value.get("provider_object_id")
    if require_object_id:
        result["provider_object_id"] = _required_text(object_id, "provider object identity")
    elif object_id is not None:
        result["provider_object_id"] = _required_text(object_id, "provider object identity")
    revision = value.get("provider_revision")
    if revision is not None and (not isinstance(revision, str) or not revision):
        raise AgentTaskError("provider revision must be nonempty or null")
    result["provider_revision"] = revision
    comments = deepcopy(value.get("comment_evidence"))
    if not isinstance(comments, list):
        raise AgentTaskError("normalized comment evidence must be an array")
    comment_ids: set[str] = set()
    for comment in comments:
        if not isinstance(comment, Mapping) or set(comment) != COMMENT_FIELDS:
            raise AgentTaskError("normalized comment evidence is malformed")
        comment_id = _required_text(comment.get("comment_id"), "normalized comment identity")
        if comment_id in comment_ids:
            raise AgentTaskError("normalized comment evidence repeats an identity")
        comment_ids.add(comment_id)
        if comment.get("kind") not in {"parent", "system"}:
            raise AgentTaskError("normalized comment evidence kind is invalid")
        if not isinstance(comment.get("text"), str):
            raise AgentTaskError("normalized comment evidence text must be a string")
        effect_id = comment.get("effect_id")
        if effect_id is not None and (not isinstance(effect_id, str) or not effect_id):
            raise AgentTaskError("normalized comment effect identity is invalid")
        if comment["kind"] == "system" and effect_id is None:
            raise AgentTaskError("normalized system comment lacks its effect identity")
        if comment["kind"] == "parent" and effect_id is not None:
            raise AgentTaskError("normalized parent comment cannot claim a system effect identity")
    result["comment_evidence"] = comments
    observed_hash = value.get("observation_sha256")
    expected_hash = _hash({key: result[key] for key in result if key != "observation_sha256"})
    if observed_hash != expected_hash:
        raise AgentTaskError("normalized task observation hash disagrees")
    result["observation_sha256"] = observed_hash
    return result


def normalized_observation(value: Mapping[str, Any]) -> dict[str, Any]:
    """Return one strict normalized provider task with a computed hash."""
    base = deepcopy(dict(value))
    base.pop("observation_sha256", None)
    base["observation_sha256"] = _hash(base)
    return _normalized_task(base, require_object_id=True)


def validate_snapshot(snapshot: Mapping[str, Any], schema: Mapping[str, Any]) -> dict[str, Any]:
    value = deepcopy(dict(snapshot))
    _validated(value, schema, "task-adapter snapshot")
    collections = value["collections"]
    names: set[str] = set()
    for collection in collections:
        if not isinstance(collection, Mapping) or set(collection) != {
            "name", "complete", "next_page_token", "item_count",
        }:
            raise AgentTaskError("snapshot collection evidence is malformed")
        name = _required_text(collection.get("name"), "snapshot collection name")
        if name in names or collection.get("complete") is not True or collection.get("next_page_token") is not None:
            raise AgentTaskError("task snapshot is duplicate, truncated, or incomplete")
        if not isinstance(collection.get("item_count"), int) or isinstance(collection.get("item_count"), bool) or collection["item_count"] < 0:
            raise AgentTaskError("snapshot collection count is invalid")
        names.add(name)
    if "tasks" not in names:
        raise AgentTaskError("task snapshot lacks its complete task collection")
    tasks = [_normalized_task(item, require_object_id=True) for item in value["tasks"]]
    ids = [item["provider_object_id"] for item in tasks]
    canonical = [item["canonical_task_id"] for item in tasks]
    if len(ids) != len(set(ids)) or len(canonical) != len(set(canonical)):
        raise AgentTaskError("task snapshot repeats an immutable provider or canonical identity")
    candidates: list[dict[str, Any]] = []
    for candidate in value["unbound_candidates"]:
        if not isinstance(candidate, Mapping) or set(candidate) != {
            "candidate_id", "provider_object_id", "action", "entity_scope",
            "parent_planned_due", "latest_progress", "completion_comment", "guard",
        }:
            raise AgentTaskError("unbound parent candidate is malformed")
        _required_text(candidate.get("candidate_id"), "parent candidate identity")
        _required_text(candidate.get("action"), "parent candidate action")
        _required_text(candidate.get("entity_scope"), "parent candidate entity scope")
        if not isinstance(candidate.get("guard"), Mapping):
            raise AgentTaskError("parent candidate lacks opaque guard evidence")
        candidates.append(deepcopy(dict(candidate)))
    if len({item["candidate_id"] for item in candidates}) != len(candidates):
        raise AgentTaskError("task snapshot repeats a parent candidate identity")
    value["tasks"], value["unbound_candidates"] = tasks, candidates
    return value


def _projection(
    task: Mapping[str, Any], current: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "canonical_task_id": task["task_id"],
        "origin": task["origin"],
        "action": task["action"],
        "task_context": task["task_context"],
        "entity_scope": task["entity_scope"],
        "workflow_state": task["workflow_state"],
        "source_link": task.get("source_link"),
        "source_due": task.get("source_due"),
        "parent_planned_due": task.get("parent_planned_due"),
        "latest_progress": task.get("latest_progress"),
        "resolution": task.get("resolution", task.get("projection_state", {}).get("resolution", "unresolved")),
        # Completion comments are parent evidence, never a system-managed field.
        "completion_comment": current.get("completion_comment") if current else None,
    }


def _snapshot_field(binding: Mapping[str, Any] | None, field: str) -> tuple[bool, Any]:
    if binding is None:
        return False, None
    stored = binding.get("last_parent_snapshot", {}).get(field)
    if isinstance(stored, Mapping):
        return bool(stored.get("present")), stored.get("value")
    if field in binding.get("last_parent_snapshot", {}):
        return True, stored
    return False, None


def _parent_snapshot(remote: Mapping[str, Any]) -> dict[str, Any]:
    return {
        field: {"present": True, "value": remote.get(field)}
        for field in (*PARENT_FIELDS, "resolution", "completion_comment")
    }


def _set_resolution(task: dict[str, Any], resolution: str) -> None:
    task["resolution"] = resolution
    task["projection_state"] = {
        **deepcopy(dict(task.get("projection_state", {}))),
        "resolution": resolution,
    }


def _lifecycle_event(
    *, kind: str, task: Mapping[str, Any], remote: Mapping[str, Any],
    occurrence: int, comment: str | None = None,
) -> dict[str, Any]:
    identity = {
        "kind": kind, "task_id": task["task_id"],
        "provider_object_id": remote["provider_object_id"],
        "occurrence": occurrence,
    }
    event = {
        "event_id": "event-" + _hash(identity), "kind": kind,
        "provider_object_id": remote["provider_object_id"],
        "occurrence": occurrence,
    }
    if comment is not None:
        event["comment"] = comment
    return event


def _mark_task_changed(task: dict[str, Any], before: Mapping[str, Any], evidence: Mapping[str, Any]) -> None:
    if any(task.get(key) != before.get(key) for key in task if key not in {"revision", "last_modified_evidence"}):
        task["revision"] = int(before.get("revision", 1)) + 1
        task["last_modified_evidence"] = {
            **deepcopy(dict(before.get("last_modified_evidence", {}))), **deepcopy(dict(evidence)),
        }


def _action(
    *, kind: str, task: Mapping[str, Any], state: Mapping[str, Any],
    canonical_sha256: str, snapshot_sha256: str,
    expected: Mapping[str, Any] | None, desired: Mapping[str, Any],
    allowed_changes: Sequence[str],
    postconditions: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if kind not in ACTION_KINDS:
        raise AgentTaskError("unsupported semantic task action")
    exact_postconditions = deepcopy(dict(postconditions)) if postconditions is not None else {
        key: deepcopy(value) for key, value in desired.items()
    }
    identity = {
        "provider_id": state["provider_id"], "binding_id": state["binding_id"],
        "scope_sha256": state["scope_sha256"], "task_id": task["task_id"],
        "kind": kind, "desired_sha256": _hash(desired),
        "postconditions_sha256": _hash(exact_postconditions),
    }
    return {
        "schema_version": 1, "contract_version": CONTRACT_VERSION,
        "effect_id": "task-effect-" + _hash(identity), "kind": kind,
        "task_id": task["task_id"], "provider_id": state["provider_id"],
        "adapter_id": state["adapter_id"], "binding_id": state["binding_id"],
        "scope_sha256": state["scope_sha256"],
        "canonical_sha256": canonical_sha256,
        "provider_base_sha256": snapshot_sha256,
        "expected": deepcopy(dict(expected)) if expected is not None else None,
        "desired": deepcopy(dict(desired)),
        "allowed_changes": sorted(set(allowed_changes)),
        "postconditions": exact_postconditions,
        "outcome": "pending", "dispatch_attempt": 0, "verification": {},
    }


def initialize_provider_state(
    *, provider_id: str, adapter_id: str, binding_id: str, scope_sha256: str,
) -> dict[str, Any]:
    for value, label in ((provider_id, "provider"), (adapter_id, "adapter"), (binding_id, "binding")):
        _required_text(value, label + " identity")
    if len(scope_sha256) != 64:
        raise AgentTaskError("provider scope hash is invalid")
    return {
        "provider_id": provider_id, "adapter_id": adapter_id,
        "provider_revision": None, "bindings": [], "cursor": None,
        "cursor_evidence": {}, "verified_readback": {},
        "binding_id": binding_id, "scope_sha256": scope_sha256,
        "pending_actions": [], "confirmed_actions": [], "review_cases": [],
    }


def plan_task_sync(
    register: Mapping[str, Any], provider_state: Mapping[str, Any],
    snapshot: Mapping[str, Any], *, task_schema: Mapping[str, Any],
    register_schema: Mapping[str, Any], provider_state_schema: Mapping[str, Any],
    snapshot_schema: Mapping[str, Any], action_schema: Mapping[str, Any],
    completion_comment_required: bool = True,
    reopen_when_comment_missing: bool = True,
    missing_comment_reminder: str = "Completion needs a parent comment before it can be recorded.",
) -> AgentTaskPlan:
    """Import one complete snapshot and plan actions without provider calls."""
    _validated(register, register_schema, "canonical task register")
    state = deepcopy(dict(provider_state))
    state.setdefault("pending_actions", [])
    state.setdefault("confirmed_actions", [])
    state.setdefault("review_cases", [])
    if state["pending_actions"]:
        raise AgentTaskError("pending task actions must be reconciled before a fresh snapshot")
    if completion_comment_required and reopen_when_comment_missing and not missing_comment_reminder.strip():
        raise AgentTaskError("missing-comment policy requires a nonempty reminder")
    snap = validate_snapshot(snapshot, snapshot_schema)
    for field in ("provider_id", "adapter_id", "binding_id", "scope_sha256"):
        if snap[field] != state.get(field):
            raise AgentTaskError(f"task snapshot {field} disagrees with selected binding")
    tasks = {item["task_id"]: deepcopy(dict(item)) for item in register["tasks"]}
    if len(tasks) != len(register["tasks"]):
        raise AgentTaskError("canonical task register repeats an identity")
    remote = {item["canonical_task_id"]: item for item in snap["tasks"]}
    unknown = set(remote) - set(tasks)
    if unknown:
        raise AgentTaskError("provider snapshot contains an unknown managed canonical identity")
    bindings = {item["task_id"]: deepcopy(dict(item)) for item in state["bindings"]}
    if len(bindings) != len(state["bindings"]):
        raise AgentTaskError("provider state repeats a canonical binding")
    reviews: list[dict[str, Any]] = []
    policy_actions: dict[str, dict[str, Any]] = {}

    for candidate in snap["unbound_candidates"]:
        parent = parent_task_from_provider(
            state["provider_id"], {
                "provider_object_id": candidate.get("provider_object_id") or candidate["candidate_id"],
                "title": candidate["action"], "group": candidate["entity_scope"],
                "parent_planned_due": candidate["parent_planned_due"],
                "parent_progress": candidate["latest_progress"], "managed_by": "parent",
            },
        )
        parent["last_modified_evidence"] = {
            "parent_admission": {
                "provider_id": state["provider_id"],
                "candidate_id": candidate["candidate_id"],
                "candidate_sha256": _hash(candidate),
            }
        }
        tasks[parent["task_id"]] = parent

    for task_id, task in tasks.items():
        current = remote.get(task_id)
        if current is None:
            continue
        prior = bindings.get(task_id)
        if prior is not None and prior["provider_object_id"] != current["provider_object_id"]:
            raise AgentTaskError("provider snapshot object identity disagrees with durable binding")
        before = deepcopy(task)
        for remote_field, canonical_field in PARENT_FIELDS.items():
            remote_value = current[remote_field]
            base_present, base = _snapshot_field(prior, remote_field)
            local = task.get(canonical_field)
            if prior is None or not base_present:
                if remote_value != local:
                    if task["origin"] == "parent":
                        task[canonical_field] = remote_value
                    else:
                        reviews.append({
                            "task_id": task_id, "field": remote_field,
                            "reason": "provider state lacks a verified common base",
                            "base": None, "canonical": local, "provider": remote_value,
                        })
            elif local == remote_value:
                continue
            elif local == base:
                if remote_field in {"action", "entity_scope"} and not remote_value:
                    reviews.append({
                        "task_id": task_id, "field": remote_field,
                        "reason": "parent cleared a required field", "base": base,
                        "canonical": local, "provider": remote_value,
                    })
                else:
                    task[canonical_field] = remote_value
            elif remote_value != base:
                reviews.append({
                    "task_id": task_id, "field": remote_field,
                    "reason": "simultaneous canonical and parent changes",
                    "base": base, "canonical": local, "provider": remote_value,
                })
        base_present, base_resolution = _snapshot_field(prior, "resolution")
        local_resolution = task.get("resolution", task.get("projection_state", {}).get("resolution", "unresolved"))
        remote_resolution = current["resolution"]
        if prior is None or not base_present:
            if remote_resolution != local_resolution:
                reviews.append({
                    "task_id": task_id, "field": "resolution",
                    "reason": "provider resolution lacks a verified common base",
                    "base": None, "canonical": local_resolution,
                    "provider": remote_resolution,
                })
        elif local_resolution == remote_resolution:
            pass
        elif local_resolution == base_resolution:
            if remote_resolution == "completed":
                comment = current.get("completion_comment")
                if completion_comment_required and (not isinstance(comment, str) or not comment.strip()):
                    if not reopen_when_comment_missing:
                        reviews.append({
                            "task_id": task_id, "field": "completion_comment",
                            "reason": "completion requires a nonempty parent comment",
                            "base": None, "canonical": None, "provider": comment,
                        })
                    else:
                        occurrence = 1 + sum(
                            event.get("kind") in {
                                "parent_completion", "reopened_missing_completion_comment",
                            }
                            for event in task.get("lifecycle_history", [])
                        )
                        policy_actions[task_id] = {
                            "current": deepcopy(current),
                            "occurrence": occurrence,
                            "reminder": missing_comment_reminder,
                        }
                else:
                    occurrence = 1 + sum(
                        event.get("kind") in {
                            "parent_completion", "reopened_missing_completion_comment",
                        }
                        for event in task.get("lifecycle_history", [])
                    )
                    event = _lifecycle_event(
                        kind="parent_completion", task=task, remote=current,
                        occurrence=occurrence, comment=comment if isinstance(comment, str) else "",
                    )
                    if not any(item.get("event_id") == event["event_id"] for item in task.get("lifecycle_history", [])):
                        task["lifecycle_history"] = [*task.get("lifecycle_history", []), event]
                    _set_resolution(task, "completed")
            else:
                occurrence = 1 + sum(
                    event.get("kind") == "parent_reopen"
                    for event in task.get("lifecycle_history", [])
                )
                event = _lifecycle_event(
                    kind="parent_reopen", task=task, remote=current,
                    occurrence=occurrence,
                )
                if not any(item.get("event_id") == event["event_id"] for item in task.get("lifecycle_history", [])):
                    task["lifecycle_history"] = [*task.get("lifecycle_history", []), event]
                _set_resolution(task, "unresolved")
        elif remote_resolution != base_resolution:
            reviews.append({
                "task_id": task_id, "field": "resolution",
                "reason": "simultaneous canonical and parent changes",
                "base": base_resolution, "canonical": local_resolution,
                "provider": remote_resolution,
            })
        if any(item["task_id"] == task_id for item in reviews):
            task["workflow_state"] = "needs_review"
        _mark_task_changed(task, before, {
            "kind": "agent_provider_reconciliation",
            "provider_id": state["provider_id"],
            "snapshot_sha256": _hash(snap),
        })

    canonical = {"schema_version": register["schema_version"], "tasks": [tasks[key] for key in sorted(tasks)]}
    for task in canonical["tasks"]:
        _validated(task, task_schema, "canonical task")
    _validated(canonical, register_schema, "canonical task register")
    canonical_sha = _hash(canonical)
    snapshot_sha = _hash(snap)
    actions: list[dict[str, Any]] = []
    review_ids = {item["task_id"] for item in reviews}
    candidates_by_id = {item["candidate_id"]: item for item in snap["unbound_candidates"]}
    for task in canonical["tasks"]:
        task_id = task["task_id"]
        if task_id in review_ids:
            continue
        if task_id in policy_actions:
            policy = policy_actions[task_id]
            current = policy["current"]
            desired = _projection(task, current)
            reminder = _action(
                kind="write_system_comment", task=task, state=state,
                canonical_sha256=canonical_sha, snapshot_sha256=snapshot_sha,
                expected=current, desired=desired,
                allowed_changes=("comment_evidence",),
                postconditions={"system_comment": {"text": policy["reminder"]}},
            )
            reminder["postconditions"]["system_comment"]["effect_id"] = reminder["effect_id"]
            reopen_desired = {**desired, "resolution": "unresolved"}
            reopen = _action(
                kind="set_task_resolution", task=task, state=state,
                canonical_sha256=canonical_sha, snapshot_sha256=snapshot_sha,
                expected={
                    "provider_object_id": current["provider_object_id"],
                    "canonical_task_id": task_id,
                    "resolution": "completed",
                },
                desired=reopen_desired, allowed_changes=("resolution",),
                postconditions={"resolution": "unresolved"},
            )
            reopen["verification"] = {
                "completion_policy": "reopen_missing_completion_comment",
                "occurrence": policy["occurrence"],
                "reminder_effect_id": reminder["effect_id"],
            }
            actions.extend((reminder, reopen))
            continue
        current = remote.get(task_id)
        desired = _projection(task, current)
        if current is None:
            if task.get("resolution", "unresolved") == "completed":
                continue
            admission = task.get("last_modified_evidence", {}).get("parent_admission", {})
            candidate_id = admission.get("candidate_id") if task["origin"] == "parent" else None
            candidate = candidates_by_id.get(candidate_id)
            kind = "claim_task" if candidate is not None else "create_task"
            expected = {"candidate": candidate} if candidate is not None else None
            actions.append(_action(
                kind=kind, task=task, state=state, canonical_sha256=canonical_sha,
                snapshot_sha256=snapshot_sha, expected=expected, desired=desired,
                allowed_changes=NORMALIZED_FIELDS,
            ))
            continue
        differing = [
            field for field in NORMALIZED_FIELDS
            if field != "completion_comment" and current[field] != desired[field]
        ]
        non_resolution = [field for field in differing if field != "resolution"]
        if non_resolution:
            actions.append(_action(
                kind="update_task_fields", task=task, state=state,
                canonical_sha256=canonical_sha, snapshot_sha256=snapshot_sha,
                expected=current, desired=desired, allowed_changes=non_resolution,
                postconditions={field: desired[field] for field in non_resolution},
            ))
        if "resolution" in differing:
            actions.append(_action(
                kind="set_task_resolution", task=task, state=state,
                canonical_sha256=canonical_sha, snapshot_sha256=snapshot_sha,
                expected={
                    "provider_object_id": current["provider_object_id"],
                    "canonical_task_id": task_id,
                    "resolution": current["resolution"],
                },
                desired=desired, allowed_changes=("resolution",),
                postconditions={"resolution": desired["resolution"]},
            ))
        if not differing:
            bindings[task_id] = {
                "task_id": task_id, "provider_object_id": current["provider_object_id"],
                "status": current["resolution"],
                "last_managed_projection": desired,
                "projection_sha256": _hash(desired),
                "last_parent_snapshot": _parent_snapshot(current),
                "verified_readback": {
                    "capture_id": snap["capture_id"],
                    "observation_sha256": current["observation_sha256"],
                },
            }
    for action in actions:
        _validated(action, action_schema, "task-adapter action")
    state.update({
        "bindings": [bindings[key] for key in sorted(bindings)],
        "last_snapshot": snap, "last_snapshot_sha256": snapshot_sha,
        "provider_revision": snap["capture_id"],
        "pending_actions": actions,
        "review_cases": [*state["review_cases"], *reviews],
        "cursor_evidence": {
            "proposed_cursor": snap["proposed_cursor"],
            "capture_id": snap["capture_id"], "complete": True,
        },
        "verified_readback": {"snapshot_sha256": snapshot_sha, "task_count": len(snap["tasks"])},
    })
    _validated(state, provider_state_schema, "provider state")
    return AgentTaskPlan(canonical, state, tuple(actions), tuple(reviews))


def authorize_next_action(
    provider_state: Mapping[str, Any], *, action_schema: Mapping[str, Any],
    provider_state_schema: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Mark one exact pending action unknown before the agent may dispatch it."""
    state = deepcopy(dict(provider_state))
    actions = state.get("pending_actions", [])
    if not isinstance(actions, list) or not actions:
        raise AgentTaskError("provider state has no pending action to authorize")
    action = deepcopy(dict(actions[0]))
    if action.get("outcome") not in {"pending", "definitely_not_applied"}:
        raise AgentTaskError("unknown task action requires reconciliation, not dispatch")
    action["outcome"] = "unknown"
    action["dispatch_attempt"] = int(action.get("dispatch_attempt", 0)) + 1
    action["verification"] = {
        **deepcopy(dict(action.get("verification", {}))),
        "dispatch_checkpoint": {
            "effect_id": action["effect_id"],
            "dispatch_attempt": action["dispatch_attempt"],
            "desired_sha256": _hash(action["desired"]),
        },
    }
    state["pending_actions"] = [action, *deepcopy(actions[1:])]
    _validated(action, action_schema, "authorized task-adapter action")
    _validated(state, provider_state_schema, "authorized provider state")
    return state, action


def confirm_action(
    register: Mapping[str, Any], provider_state: Mapping[str, Any],
    result: Mapping[str, Any], *, register_schema: Mapping[str, Any],
    provider_state_schema: Mapping[str, Any], action_schema: Mapping[str, Any],
    result_schema: Mapping[str, Any],
) -> AgentTaskConfirmation:
    """Validate one agent result and advance a synchronized base only on proof."""
    _validated(register, register_schema, "canonical task register")
    state = deepcopy(dict(provider_state))
    if not state.get("pending_actions"):
        raise AgentTaskError("task result has no pending authorization")
    action = deepcopy(dict(state["pending_actions"][0]))
    _validated(action, action_schema, "pending task action")
    response = deepcopy(dict(result))
    _validated(response, result_schema, "task-adapter result")
    for field in ("effect_id", "provider_id", "adapter_id", "binding_id", "scope_sha256"):
        if response[field] != action[field]:
            raise AgentTaskError(f"task result {field} disagrees with authorization")
    if action["outcome"] != "unknown":
        raise AgentTaskError("task action was not durably authorized for dispatch")
    if response["outcome"] != "confirmed":
        action["outcome"] = response["outcome"]
        action["verification"] = deepcopy(response["evidence"])
        state["pending_actions"][0] = action
        _validated(state, provider_state_schema, "unconfirmed provider state")
        return AgentTaskConfirmation(deepcopy(dict(register)), state, tuple(state["pending_actions"]))
    if not isinstance(response.get("readback"), Mapping):
        raise AgentTaskError("confirmed task action lacks normalized exact readback")
    readback = _normalized_task(response["readback"], require_object_id=True)
    desired = action["desired"]
    for field, expected in action["postconditions"].items():
        if field == "system_comment":
            matches = [
                item for item in readback["comment_evidence"]
                if item.get("kind") == "system"
                and item.get("effect_id") == expected.get("effect_id")
                and item.get("text") == expected.get("text")
            ]
            if len(matches) != 1:
                raise AgentTaskError("confirmed task action lacks one exact system comment")
        elif readback.get(field) != expected:
            raise AgentTaskError(f"confirmed task action fails postcondition {field}")
    tasks = {item["task_id"]: deepcopy(dict(item)) for item in register["tasks"]}
    task = tasks.get(action["task_id"])
    if task is None:
        raise AgentTaskError("task action references an absent canonical task")
    before_task = deepcopy(task)
    if action["kind"] == "set_task_resolution":
        _set_resolution(task, readback["resolution"])
        policy = action.get("verification", {}).get("completion_policy")
        if policy == "reopen_missing_completion_comment":
            occurrence = action["verification"].get("occurrence")
            event = {
                "event_id": action["effect_id"],
                "kind": "reopened_missing_completion_comment",
                "provider_object_id": readback["provider_object_id"],
                "occurrence": occurrence,
                "reminder_effect_id": action["verification"].get("reminder_effect_id"),
            }
            if not any(item.get("event_id") == event["event_id"] for item in task.get("lifecycle_history", [])):
                task["lifecycle_history"] = [*task.get("lifecycle_history", []), event]
    existing = [
        item for item in task["provider_bindings"]
        if item.get("provider_id") != state["provider_id"]
    ]
    existing.append({
        "provider_id": state["provider_id"],
        "provider_object_id": readback["provider_object_id"],
    })
    task["provider_bindings"] = existing
    _mark_task_changed(task, before_task, {
        "kind": "agent_task_action_confirmation",
        "provider_id": state["provider_id"],
        "effect_id": action["effect_id"],
    })
    bindings = {item["task_id"]: deepcopy(dict(item)) for item in state["bindings"]}
    bindings[action["task_id"]] = {
        "task_id": action["task_id"],
        "provider_object_id": readback["provider_object_id"],
        "status": readback["resolution"],
        "last_managed_projection": _projection(task, readback),
        "projection_sha256": _hash(_projection(task, readback)),
        "last_parent_snapshot": _parent_snapshot(readback),
        "verified_readback": {
            "effect_id": action["effect_id"],
            "observation_sha256": readback["observation_sha256"],
            "evidence": deepcopy(response["evidence"]),
        },
    }
    receipt = {
        "effect_id": action["effect_id"], "outcome": "confirmed",
        "provider_object_id": readback["provider_object_id"],
        "observation_sha256": readback["observation_sha256"],
    }
    state.update({
        "bindings": [bindings[key] for key in sorted(bindings)],
        "pending_actions": deepcopy(state["pending_actions"][1:]),
        "confirmed_actions": [*state.get("confirmed_actions", []), receipt],
    })
    if not state["pending_actions"]:
        state["cursor"] = state.get("cursor_evidence", {}).get("proposed_cursor")
    confirmed = {"schema_version": register["schema_version"], "tasks": [tasks[key] for key in sorted(tasks)]}
    _validated(confirmed, register_schema, "confirmed canonical task register")
    _validated(state, provider_state_schema, "confirmed provider state")
    return AgentTaskConfirmation(confirmed, state, tuple(state["pending_actions"]))
