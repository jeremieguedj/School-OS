"""Deterministic canonical task reconciliation and derived knowledge."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Protocol
from typing import Any

from .contracts import canonical_json_bytes, sha256_bytes, validate


class TaskError(ValueError):
    """Raised when source facts cannot safely build canonical task state."""


class TaskProviderPort(Protocol):
    """Minimal task surface for pull-first, identity-safe synchronization."""
    def list_tasks(self) -> Sequence[Mapping[str, Any]]: ...
    def create_task(self, candidate: Mapping[str, Any]) -> Mapping[str, Any]: ...
    def read_task(self, provider_object_id: str) -> Mapping[str, Any] | None: ...
    def apply_patch(self, provider_object_id: str, patch: Mapping[str, Any]) -> Mapping[str, Any]: ...
    def find_comments(self, provider_object_id: str, effect_id: str) -> Sequence[Mapping[str, Any]]: ...
    def write_comment(self, provider_object_id: str, effect_id: str, text: str) -> Mapping[str, Any]: ...


@dataclass(frozen=True)
class ProviderReconciliation:
    tasks: dict[str, Any]
    provider_state: dict[str, Any]
    effects: tuple[dict[str, Any], ...]
    review_cases: tuple[dict[str, Any], ...]


def canonical_task_id(opening_fact_id: str) -> str:
    if not opening_fact_id:
        raise TaskError("opening action Fact ID is required")
    return "task-" + sha256_bytes(opening_fact_id.encode("utf-8"))


def _validated(value: Any, schema: Mapping[str, Any], label: str) -> None:
    errors = validate(value, dict(schema))
    if errors:
        raise TaskError(f"invalid {label}: " + "; ".join(errors))


def validate_facts(facts: Sequence[Mapping[str, Any]], fact_schema: Mapping[str, Any]) -> None:
    seen: set[str] = set()
    for fact in facts:
        _validated(fact, fact_schema, "Fact")
        if fact["fact_id"] in seen:
            raise TaskError("duplicate Fact ID")
        if fact["source_byte_end"] <= fact["source_byte_start"]:
            raise TaskError("Fact source byte range must be non-empty")
        if fact["flags"]["is_action"] and fact["flags"]["is_guideline"]:
            raise TaskError("a guideline cannot be an action")
        seen.add(fact["fact_id"])


def _task_from_fact(fact: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "task_id": canonical_task_id(fact["fact_id"]), "origin": "source", "action": fact["text"],
        "task_context": fact["category"], "entity_scope": fact["entity_scope"], "workflow_state": "needs_action",
        "owner": None, "source_opened_date": fact["received_date"], "last_supporting_source_date": fact["received_date"],
        "source_due": None, "parent_planned_due": None, "source_link": f"{fact['record_id']}#{fact['fact_id']}",
        "source_facts": [fact["fact_id"]], "latest_progress": None, "provider_bindings": [], "lifecycle_history": [],
        "projection_state": {}, "revision": 1, "last_modified_evidence": {},
    }


def build_derived_knowledge(facts: Sequence[Mapping[str, Any]], *, fact_schema: Mapping[str, Any], task_schema: Mapping[str, Any]) -> dict[str, Any]:
    validate_facts(facts, fact_schema)
    ordered = sorted(facts, key=lambda fact: fact["fact_id"])
    tasks = [_task_from_fact(fact) for fact in ordered if fact["flags"]["is_action"]]
    for task in tasks:
        _validated(task, task_schema, "canonical task")
    entry = lambda fact: {"fact_id": fact["fact_id"], "record_id": fact["record_id"], "text": fact["text"]}
    return {"schema_version": 1, "guidelines": [entry(fact) for fact in ordered if fact["flags"]["is_guideline"]], "rolling_updates": [entry(fact) for fact in ordered if fact["flags"]["is_update"] and not fact["flags"]["is_action"] and not fact["flags"]["is_guideline"]], "tasks": tasks}


def reconcile_canonical_tasks(existing: Mapping[str, Any], facts: Sequence[Mapping[str, Any]], *, fact_schema: Mapping[str, Any], task_schema: Mapping[str, Any], register_schema: Mapping[str, Any]) -> dict[str, Any]:
    _validated(existing, register_schema, "canonical task register")
    existing_by_id: dict[str, dict[str, Any]] = {}
    for task in existing["tasks"]:
        _validated(task, task_schema, "canonical task")
        if task["task_id"] in existing_by_id:
            raise TaskError("duplicate canonical task ID")
        existing_by_id[task["task_id"]] = dict(task)
    derived = build_derived_knowledge(facts, fact_schema=fact_schema, task_schema=task_schema)
    for task in derived["tasks"]:
        existing_by_id.setdefault(task["task_id"], task)
    result = {"schema_version": 1, "tasks": [existing_by_id[key] for key in sorted(existing_by_id)]}
    _validated(result, register_schema, "canonical task register")
    return result


def serialize_canonical_tasks(register: Mapping[str, Any], register_schema: Mapping[str, Any]) -> bytes:
    _validated(register, register_schema, "canonical task register")
    return canonical_json_bytes(register)


def managed_projection(task: Mapping[str, Any]) -> dict[str, Any]:
    """Return only system-owned provider fields; parent fields are excluded."""
    return {
        "canonical_task_id": task["task_id"], "title": task["action"],
        "description": task["task_context"], "group": task["entity_scope"],
        "workflow_state": task["workflow_state"], "source_link": task["source_link"],
    }


def _projection_hash(projection: Mapping[str, Any]) -> str:
    return sha256_bytes(canonical_json_bytes(dict(projection)))


def recover_task_comment(provider: TaskProviderPort, provider_object_id: str, effect_id: str, text: str) -> Mapping[str, Any]:
    """Adopt one immutable comment after a lost response; never blindly repeat it."""
    matches = [dict(comment) for comment in provider.find_comments(provider_object_id, effect_id)]
    if len(matches) > 1:
        raise TaskError("multiple provider comments match one immutable effect ID")
    if matches:
        return matches[0]
    written = dict(provider.write_comment(provider_object_id, effect_id, text))
    matches = [dict(comment) for comment in provider.find_comments(provider_object_id, effect_id)]
    if len(matches) != 1 or matches[0] != written:
        raise TaskError("provider comment readback does not establish one immutable effect")
    return matches[0]


def reconcile_provider_tasks(
    provider: TaskProviderPort,
    register: Mapping[str, Any],
    provider_state: Mapping[str, Any],
    *, task_schema: Mapping[str, Any], register_schema: Mapping[str, Any], provider_state_schema: Mapping[str, Any],
) -> ProviderReconciliation:
    """Pull first, then write only verified managed projections by canonical ID."""
    _validated(register, register_schema, "canonical task register")
    _validated(provider_state, provider_state_schema, "provider state")
    for task in register["tasks"]:
        _validated(task, task_schema, "canonical task")
    snapshot = [dict(item) for item in provider.list_tasks()]
    by_canonical: dict[str, dict[str, Any]] = {}
    for item in snapshot:
        canonical_id = item.get("canonical_task_id")
        object_id = item.get("provider_object_id")
        if not isinstance(canonical_id, str) or not isinstance(object_id, str):
            continue
        if canonical_id in by_canonical:
            raise TaskError("multiple provider tasks match one canonical task ID")
        by_canonical[canonical_id] = item
    bindings: list[dict[str, Any]] = []
    effects: list[dict[str, Any]] = []
    review_cases: list[dict[str, Any]] = []
    previous_bindings = {binding["task_id"]: binding for binding in provider_state["bindings"]}
    for task in register["tasks"]:
        projection = managed_projection(task)
        task_id = task["task_id"]
        current = by_canonical.get(task_id)
        intent = {"task_id": task_id, "projection_sha256": _projection_hash(projection)}
        if current is None:
            created = dict(provider.create_task(projection))
            object_id = created.get("provider_object_id")
            if not isinstance(object_id, str):
                raise TaskError("provider create did not return an immutable object ID")
            effect_kind = "create"
        else:
            object_id = current["provider_object_id"]
            previous = previous_bindings.get(task_id, {})
            previous_projection = previous.get("last_managed_projection", {})
            if all(current.get(field) == value for field, value in projection.items()):
                created = current
                effect_kind = "adopt"
            else:
                for field in ("title", "group"):
                    if (
                        field in previous_projection
                        and current.get(field) != previous_projection[field]
                        and current.get(field) != projection[field]
                    ):
                        projection.pop(field)
                        review_cases.append({"task_id": task_id, "field": field, "reason": "parent-owned provider edit preserved"})
                if all(current.get(field) == value for field, value in projection.items()):
                    created = current
                    effect_kind = "adopt"
                else:
                    created = dict(provider.apply_patch(object_id, projection))
                    effect_kind = "patch"
        readback = provider.read_task(object_id)
        if readback is None:
            raise TaskError("provider task readback is unavailable")
        actual = dict(readback)
        if any(actual.get(key) != value for key, value in projection.items()):
            raise TaskError("provider task readback does not match managed projection")
        bindings.append({"task_id": task_id, "provider_object_id": object_id, "status": "verified", "last_managed_projection": projection, "projection_sha256": _projection_hash(projection), "verified_readback": {"provider_object_id": object_id}})
        effects.append({"kind": effect_kind, "intent": intent, "outcome": "confirmed", "provider_object_id": object_id})
    if len({binding["task_id"] for binding in bindings}) != len(bindings):
        raise TaskError("provider bindings are not unique")
    state = {"provider_id": provider_state["provider_id"], "adapter_id": provider_state["adapter_id"], "provider_revision": provider_state.get("provider_revision"), "bindings": bindings, "cursor": provider_state["cursor"], "cursor_evidence": {"pulled": True, "count": len(snapshot)}, "verified_readback": {"bindings": len(bindings)}}
    _validated(state, provider_state_schema, "provider state")
    return ProviderReconciliation(dict(register), state, tuple(effects), tuple(review_cases))
