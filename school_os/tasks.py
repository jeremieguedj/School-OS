"""Deterministic canonical task reconciliation and derived knowledge."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .contracts import canonical_json_bytes, sha256_bytes, validate


class TaskError(ValueError):
    """Raised when source facts cannot safely build canonical task state."""


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
