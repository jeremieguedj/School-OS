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


def parent_task_id(provider_id: str, provider_object_id: str) -> str:
    """Stable identity assigned before a guarded parent-row claim."""
    if not provider_id or not provider_object_id:
        raise TaskError("parent task identity requires provider and object IDs")
    return "task-" + sha256_bytes(
        f"parent\0{provider_id}\0{provider_object_id}".encode("utf-8")
    )


def parent_task_from_provider(provider_id: str, row: Mapping[str, Any]) -> dict[str, Any]:
    """Build a source-free parent task from an explicitly admitted row packet."""
    if "managed_by" in row and row.get("managed_by") != "parent":
        raise TaskError("provider row is not an explicit parent-origin task candidate")
    object_id = row.get("provider_object_id") or row.get("row_id")
    action, group = row.get("title") or row.get("action"), row.get("group")
    if not isinstance(object_id, str) or not object_id or not isinstance(action, str) or not action or not isinstance(group, str) or not group:
        raise TaskError("parent-origin task candidate lacks immutable row, action, or group")
    return {
        "task_id": parent_task_id(provider_id, object_id), "origin": "parent", "action": action,
        "task_context": "", "entity_scope": group, "workflow_state": "needs_action", "owner": None,
        "source_opened_date": None, "last_supporting_source_date": None, "source_due": None,
        "parent_planned_due": row.get("parent_planned_due"), "source_link": None, "source_facts": [],
        "latest_progress": row.get("parent_progress") or row.get("progress"), "provider_bindings": [],
        "lifecycle_history": [], "projection_state": {}, "revision": 1,
        "last_modified_evidence": {"parent_candidate_row_id": object_id},
    }


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
        attachment = fact.get("attachment")
        if attachment and attachment["locator"]["kind"] == "extracted_text_span":
            locator = attachment["locator"]
            if (locator["byte_start"], locator["byte_end"]) != (fact["source_byte_start"], fact["source_byte_end"]):
                raise TaskError("attachment Fact span must equal its extracted-text locator")
        relation = fact.get("task_relation")
        if relation and relation["relation"] == "support" and relation["changed_source_fields"]:
            raise TaskError("support relation cannot claim changed source fields")
        seen.add(fact["fact_id"])


def _task_from_fact(fact: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "task_id": canonical_task_id(fact["fact_id"]), "origin": "source", "action": fact["text"],
        "task_context": fact["category"], "entity_scope": fact["entity_scope"], "workflow_state": "needs_action",
        "owner": None, "source_opened_date": fact["received_date"], "last_supporting_source_date": fact["received_date"],
        "source_due": fact.get("source_due"), "parent_planned_due": None, "source_link": f"{fact['record_id']}#{fact['fact_id']}",
        "source_facts": [fact["fact_id"]], "latest_progress": None, "provider_bindings": [], "lifecycle_history": [],
        "projection_state": {}, "revision": 1, "last_modified_evidence": {},
    }


def build_derived_knowledge(facts: Sequence[Mapping[str, Any]], *, fact_schema: Mapping[str, Any], task_schema: Mapping[str, Any]) -> dict[str, Any]:
    validate_facts(facts, fact_schema)
    ordered = sorted(facts, key=lambda fact: fact["fact_id"])
    tasks = [_task_from_fact(fact) for fact in ordered if fact["flags"]["is_action"] and not fact.get("task_relation")]
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
        existing_by_id[task["task_id"]] = {key: (list(value) if isinstance(value, list) else dict(value) if isinstance(value, Mapping) else value) for key, value in task.items()}
    derived = build_derived_knowledge(facts, fact_schema=fact_schema, task_schema=task_schema)
    for task in derived["tasks"]:
        existing_by_id.setdefault(task["task_id"], task)
    for fact in sorted(facts, key=lambda item: item["fact_id"]):
        relation = fact.get("task_relation")
        if not relation:
            continue
        task = existing_by_id.get(relation["target_task_id"])
        if task is None:
            raise TaskError("source relation has an unknown target task ID")
        if task["origin"] != "source":
            raise TaskError("source relation cannot target a parent-origin task")
        if fact["fact_id"] not in task["source_facts"]:
            task["source_facts"] = [*task["source_facts"], fact["fact_id"]]
        task["last_supporting_source_date"] = fact["received_date"]
        for field in ("action", "task_context", "entity_scope", "source_due"):
            if field in relation["changed_source_fields"]:
                task[field] = relation["changed_source_fields"][field]
        if relation["relation"] in {"completion", "reopen"}:
            event_id = "event-" + sha256_bytes((relation["relation"] + "\0" + task["task_id"] + "\0" + fact["fact_id"]).encode("utf-8"))
            if not any(event.get("event_id") == event_id for event in task["lifecycle_history"]):
                task["lifecycle_history"] = [*task["lifecycle_history"], {"event_id": event_id, "kind": "source_" + relation["relation"], "fact_id": fact["fact_id"], "received_date": fact["received_date"], "changed_source_fields": dict(relation["changed_source_fields"])}]
    result = {"schema_version": 1, "tasks": [existing_by_id[key] for key in sorted(existing_by_id)]}
    _validate_task_bindings(result["tasks"])
    _validated(result, register_schema, "canonical task register")
    return result


def serialize_canonical_tasks(register: Mapping[str, Any], register_schema: Mapping[str, Any]) -> bytes:
    _validated(register, register_schema, "canonical task register")
    return canonical_json_bytes(register)


def managed_projection(task: Mapping[str, Any]) -> dict[str, Any]:
    """Source-owned fields; action/group remain parent-editable canonical fields."""
    return {
        "canonical_task_id": task["task_id"], "origin": task["origin"],
        "description": task["task_context"], "workflow_state": task["workflow_state"],
        "source_link": task["source_link"] or "", "source_due": task["source_due"] or "",
    }


def create_projection(task: Mapping[str, Any]) -> dict[str, Any]:
    return {**managed_projection(task), "title": task["action"], "group": task["entity_scope"]}


def _parent_snapshot(item: Mapping[str, Any]) -> dict[str, Any]:
    fields = ("title", "group", "parent_planned_due", "parent_progress", "workflow_state", "status", "completion_comment")
    return {field: {"present": field in item, "value": item.get(field)} for field in fields}


def _snapshot_value(snapshot: Mapping[str, Any], field: str) -> tuple[bool, Any]:
    cell = snapshot.get(field, {})
    return bool(cell.get("present")), cell.get("value")


def _bind(task: dict[str, Any], provider_id: str, object_id: str) -> None:
    bindings = [dict(value) for value in task["provider_bindings"] if value.get("provider_id") != provider_id]
    bindings.append({"provider_id": provider_id, "provider_object_id": object_id})
    task["provider_bindings"] = bindings


def _validate_task_bindings(tasks: Sequence[Mapping[str, Any]]) -> None:
    pairs: set[tuple[str, str]] = set()
    for task in tasks:
        for binding in task["provider_bindings"]:
            pair = (binding.get("provider_id"), binding.get("provider_object_id"))
            if not all(isinstance(value, str) and value for value in pair):
                raise TaskError("canonical task has an invalid provider binding")
            if pair in pairs:
                raise TaskError("duplicate provider binding")
            pairs.add(pair)


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
    """Reconcile an exact provider snapshot without title matching or row identity."""
    _validated(register, register_schema, "canonical task register")
    input_state = {**dict(provider_state), "claim_intents": list(provider_state.get("claim_intents", []))}
    _validated(input_state, provider_state_schema, "provider state")
    tasks = {task["task_id"]: {key: (list(value) if isinstance(value, list) else dict(value) if isinstance(value, Mapping) else value) for key, value in task.items()} for task in register["tasks"]}
    _validate_task_bindings(list(tasks.values()))
    provider_id = input_state["provider_id"]
    snapshot = [dict(item) for item in provider.list_tasks()]
    by_canonical: dict[str, dict[str, Any]] = {}
    for item in snapshot:
        canonical_id, object_id = item.get("canonical_task_id"), item.get("provider_object_id")
        if canonical_id is None:
            continue
        if not isinstance(canonical_id, str) or not canonical_id or not isinstance(object_id, str) or not object_id:
            raise TaskError("provider task has invalid canonical identity")
        if canonical_id in by_canonical:
            raise TaskError("multiple provider tasks match one canonical task ID")
        by_canonical[canonical_id] = item
    previous = {item["task_id"]: dict(item) for item in input_state["bindings"]}
    if len(previous) != len(input_state["bindings"]) or len({item["provider_object_id"] for item in input_state["bindings"]}) != len(input_state["bindings"]):
        raise TaskError("provider bindings are not unique")
    effects: list[dict[str, Any]] = []
    review_cases: list[dict[str, Any]] = []
    pending = {item["task_id"]: dict(item) for item in input_state["claim_intents"]}
    preexisting_pending = set(pending)
    if len(pending) != len(input_state["claim_intents"]):
        raise TaskError("duplicate parent claim intent")
    candidates = list(getattr(provider, "unbound_parent_candidates", lambda: [])())
    by_row = {getattr(candidate, "row_id", None): candidate for candidate in candidates}
    for candidate in candidates:
        task = parent_task_from_provider(provider_id, {"row_id": getattr(candidate, "row_id", None), "action": getattr(candidate, "action", None), "group": getattr(candidate, "group", None), "parent_planned_due": getattr(candidate, "parent_planned_due", None), "parent_progress": getattr(candidate, "parent_progress", None)})
        if task["task_id"] not in tasks and task["task_id"] not in pending:
            tasks[task["task_id"]] = task
            pending[task["task_id"]] = {"task_id": task["task_id"], "provider_object_id": "pending:" + getattr(candidate, "row_id"), "candidate": {"row_id": getattr(candidate, "row_id")}}
            effects.append({"kind": "parent_claim_intent", "intent": dict(pending[task["task_id"]]), "outcome": "journaled"})
    for task_id, intent in list(pending.items()):
        if task_id not in preexisting_pending:
            continue  # caller persists this intent before a guarded provider claim
        current = by_canonical.get(task_id)
        if current is None:
            candidate = by_row.get(intent["candidate"]["row_id"])
            claim = getattr(provider, "claim_parent_candidate", None)
            if candidate is None:
                raise TaskError("parent claim intent cannot recover an absent exact candidate")
            if claim is None:
                continue
            current = dict(claim(candidate, canonical_task_id=task_id, workflow_state=tasks[task_id]["workflow_state"]))
            by_canonical[task_id] = current
            effects.append({"kind": "parent_claim", "intent": intent, "outcome": "confirmed", "provider_object_id": current["provider_object_id"]})
        _bind(tasks[task_id], provider_id, current["provider_object_id"])
        pending.pop(task_id)
    bindings: list[dict[str, Any]] = []
    for task_id in sorted(tasks):
        if task_id in pending:
            continue
        task = tasks[task_id]
        projection = managed_projection(task)
        current = by_canonical.get(task_id)
        intent = {"task_id": task_id, "projection_sha256": _projection_hash(projection)}
        if current is None:
            current = dict(provider.create_task(create_projection(task)))
            effect_kind = "create"
        else:
            patch = {key: value for key, value in projection.items() if current.get(key) != value and (key in current or key not in {"origin", "source_due"})}
            current = dict(provider.apply_patch(current["provider_object_id"], patch)) if patch else current
            effect_kind = "patch" if patch else "adopt"
        object_id = current.get("provider_object_id")
        if not isinstance(object_id, str) or not object_id:
            raise TaskError("provider operation did not return an immutable object ID")
        actual = provider.read_task(object_id)
        if actual is None:
            raise TaskError("provider task readback is unavailable")
        actual = dict(actual)
        if any(actual.get(key) != value for key, value in projection.items() if key in actual or key not in {"origin", "source_due"}):
            raise TaskError("provider task readback does not match managed projection")
        prior = previous.get(task_id, {}).get("last_parent_snapshot", {})
        for source, target in (("title", "action"), ("group", "entity_scope"), ("parent_planned_due", "parent_planned_due"), ("parent_progress", "latest_progress")):
            present, value = _snapshot_value(_parent_snapshot(actual), source)
            old_present, old_value = _snapshot_value(prior, source)
            if present and (not old_present or value != old_value):
                if source in {"title", "group"} and (not isinstance(value, str) or not value):
                    raise TaskError("parent edit cleared a required task field")
                task[target] = value
        present, workflow = _snapshot_value(_parent_snapshot(actual), "workflow_state")
        old_present, old_workflow = _snapshot_value(prior, "workflow_state")
        if present and workflow != old_workflow:
            if workflow not in {"needs_action", "waiting_external", "needs_review"}:
                raise TaskError("parent workflow state is invalid")
            task["workflow_state"] = workflow
        status_present, status = _snapshot_value(_parent_snapshot(actual), "status")
        comment_present, comment = _snapshot_value(_parent_snapshot(actual), "completion_comment")
        if status_present and isinstance(status, str) and status.lower() in {"completed", "complete", "done"}:
            if not comment_present or not isinstance(comment, str) or not comment.strip():
                effect_id = "event-" + sha256_bytes(("reopen-reminder\0" + task_id + "\0" + object_id).encode("utf-8"))
                if not any(event.get("event_id") == effect_id for event in task["lifecycle_history"]):
                    apply_state = getattr(provider, "apply_parent_state", None)
                    if apply_state is None:
                        raise TaskError("completion without comment needs a reopen-capable provider")
                    apply_state(object_id, status="open")
                    recover_task_comment(provider, object_id, effect_id, "Completion needs a parent comment before it can be recorded.")
                    task["lifecycle_history"] = [*task["lifecycle_history"], {"event_id": effect_id, "kind": "reopened_missing_completion_comment", "provider_object_id": object_id}]
                    effects.append({"kind": "reopen_reminder", "intent": {"task_id": task_id, "effect_id": effect_id}, "outcome": "confirmed", "provider_object_id": object_id})
                review_cases.append({"task_id": task_id, "reason": "completion requires a nonempty parent comment"})
            else:
                event_id = "event-" + sha256_bytes(("parent-completion\0" + task_id + "\0" + object_id + "\0" + comment).encode("utf-8"))
                if not any(event.get("event_id") == event_id for event in task["lifecycle_history"]):
                    task["lifecycle_history"] = [*task["lifecycle_history"], {"event_id": event_id, "kind": "parent_completion", "provider_object_id": object_id, "status": status, "comment": comment}]
        task["projection_state"] = {**task["projection_state"], "provider_status": status if status_present else None}
        _bind(task, provider_id, object_id)
        bindings.append({"task_id": task_id, "provider_object_id": object_id, "status": "verified", "last_managed_projection": projection, "projection_sha256": _projection_hash(projection), "last_parent_snapshot": _parent_snapshot(actual), "verified_readback": {"provider_object_id": object_id}})
        effects.append({"kind": effect_kind, "intent": intent, "outcome": "confirmed", "provider_object_id": object_id})
    _validate_task_bindings(list(tasks.values()))
    state = {"provider_id": provider_id, "adapter_id": input_state["adapter_id"], "provider_revision": input_state.get("provider_revision"), "bindings": bindings, "claim_intents": [pending[key] for key in sorted(pending)], "cursor": input_state["cursor"], "cursor_evidence": {"pulled": True, "count": len(snapshot)}, "verified_readback": {"bindings": len(bindings)}}
    _validated(state, provider_state_schema, "provider state")
    result = {"schema_version": register["schema_version"], "tasks": [tasks[key] for key in sorted(tasks)]}
    for task in result["tasks"]:
        _validated(task, task_schema, "canonical task")
    _validated(result, register_schema, "canonical task register")
    return ProviderReconciliation(result, state, tuple(effects), tuple(review_cases))
