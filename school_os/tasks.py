"""Deterministic canonical task reconciliation and derived knowledge."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass
from typing import Protocol
from typing import Any
from uuid import uuid4

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


def parent_task_id() -> str:
    """Issue an immutable identity before a mutable provider row is claimed."""
    return "task-parent-" + uuid4().hex


def parent_task_from_provider(
    provider_id: str, row: Mapping[str, Any], *, task_id: str | None = None
) -> dict[str, Any]:
    """Build a source-free parent task from an explicitly admitted row packet."""
    if "managed_by" in row and row.get("managed_by") != "parent":
        raise TaskError("provider row is not an explicit parent-origin task candidate")
    object_id = row.get("provider_object_id") or row.get("row_id")
    action, group = row.get("title") or row.get("action"), row.get("group")
    if not isinstance(object_id, str) or not object_id or not isinstance(action, str) or not action or not isinstance(group, str) or not group:
        raise TaskError("parent-origin task candidate lacks immutable row, action, or group")
    return {
        "task_id": task_id or parent_task_id(), "origin": "parent", "action": action,
        "task_context": "", "entity_scope": group, "workflow_state": "needs_action", "owner": None,
        "source_opened_date": None, "last_supporting_source_date": None, "source_due": None,
        "parent_planned_due": row.get("parent_planned_due"), "source_link": None, "source_facts": [],
        "latest_progress": row.get("parent_progress") or row.get("progress"), "provider_bindings": [],
        "lifecycle_history": [], "projection_state": {"resolution": "unresolved"},
        "resolution": "unresolved", "revision": 1,
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
    source_projection = {
        "action": fact["text"], "task_context": fact["category"],
        "entity_scope": fact["entity_scope"], "source_due": fact.get("source_due"),
    }
    return {
        "task_id": canonical_task_id(fact["fact_id"]), "origin": "source", "action": fact["text"],
        "task_context": fact["category"], "entity_scope": fact["entity_scope"], "workflow_state": "needs_action",
        "owner": None, "source_opened_date": fact["received_date"], "last_supporting_source_date": fact["received_date"],
        "source_due": fact.get("source_due"), "parent_planned_due": None, "source_link": f"{fact['record_id']}#{fact['fact_id']}",
        "source_facts": [fact["fact_id"]], "latest_progress": None, "provider_bindings": [], "lifecycle_history": [],
        "projection_state": {"resolution": "unresolved", "source_projection": source_projection},
        "resolution": "unresolved", "revision": 1, "last_modified_evidence": {},
    }


def _source_order(fact: Mapping[str, Any]) -> tuple[Any, ...]:
    """Order source evidence chronologically, using Fact ID only as a final tie."""
    return (
        fact.get("source_received_at") or fact["received_date"],
        fact["record_id"],
        fact.get("source_message_ordinal", 0),
        fact.get("source_content_ordinal", 0),
        fact["source_byte_start"],
        fact["fact_id"],
    )


def _source_coordinate(fact: Mapping[str, Any]) -> tuple[Any, ...]:
    return _source_order(fact)[:-1]


def _resolution(task: Mapping[str, Any]) -> str:
    value = task.get("resolution", task.get("projection_state", {}).get("resolution"))
    if value is None:
        value = "unresolved"
        for event in task.get("lifecycle_history", []):
            if event.get("kind") in {"source_completion", "parent_completion"}:
                value = "completed"
            elif event.get("kind") in {"source_reopen", "parent_reopen", "reopened_missing_completion_comment"}:
                value = "unresolved"
    if value not in {"unresolved", "completed"}:
        raise TaskError("canonical task has an invalid resolution")
    return value


def _set_resolution(task: dict[str, Any], value: str) -> None:
    task["resolution"] = value
    task["projection_state"] = {**task.get("projection_state", {}), "resolution": value}


def unresolved_tasks(register: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Return the current task-view inputs without discarding completed history."""
    return [
        deepcopy(dict(task)) for task in register.get("tasks", [])
        if _resolution(task) == "unresolved"
    ]


def _mark_changed(task: dict[str, Any], before: Mapping[str, Any], evidence: Mapping[str, Any]) -> None:
    ignored = {"revision", "last_modified_evidence"}
    if any(task.get(key) != before.get(key) for key in set(task) | set(before) if key not in ignored):
        task["revision"] = int(before.get("revision", 1)) + 1
        task["last_modified_evidence"] = {
            **dict(before.get("last_modified_evidence", {})), **dict(evidence)
        }


def _apply_source_facts(
    task: dict[str, Any], opening: Mapping[str, Any], relations: Sequence[Mapping[str, Any]]
) -> None:
    """Apply the current ordered source view without replaying old corrections over parents."""
    prior_fact_ids = set(task.get("source_facts", []))
    initial = {
        "action": opening["text"], "task_context": opening["category"],
        "entity_scope": opening["entity_scope"], "source_due": opening.get("source_due"),
    }
    old_source = dict(task.get("projection_state", {}).get("source_projection", {}))
    if not old_source:
        old_source = dict(initial)
        for fact in relations:
            if fact["fact_id"] in prior_fact_ids:
                old_source.update(fact["task_relation"]["changed_source_fields"])
    desired = dict(initial)
    resolution = "unresolved"
    coordinate_changes: dict[tuple[Any, ...], dict[str, Any]] = {}
    coordinate_lifecycle: dict[tuple[Any, ...], str] = {}
    for fact in relations:
        changed = dict(fact["task_relation"]["changed_source_fields"])
        coordinate = _source_coordinate(fact)
        prior_at_coordinate = coordinate_changes.setdefault(coordinate, {})
        for field, value in changed.items():
            if field in prior_at_coordinate and prior_at_coordinate[field] != value:
                raise TaskError("conflicting source relations share one source coordinate")
            prior_at_coordinate[field] = value
        desired.update(changed)
        relation = fact["task_relation"]["relation"]
        if relation in {"completion", "reopen"}:
            prior_relation = coordinate_lifecycle.get(coordinate)
            if prior_relation is not None and prior_relation != relation:
                raise TaskError("conflicting lifecycle relations share one source coordinate")
            coordinate_lifecycle[coordinate] = relation
        if relation == "completion":
            resolution = "completed"
        elif relation == "reopen":
            resolution = "unresolved"

    for field, value in desired.items():
        if old_source.get(field) != value:
            task[field] = value
    task["projection_state"] = {
        **task.get("projection_state", {}), "source_projection": desired
    }
    task["source_facts"] = list(dict.fromkeys(
        [opening["fact_id"], *(fact["fact_id"] for fact in relations)]
    ))
    dates = [opening["received_date"], *(fact["received_date"] for fact in relations)]
    task["last_supporting_source_date"] = max(dates)

    prior_source_event_ids = {
        event.get("event_id") for event in task.get("lifecycle_history", [])
        if event.get("kind") in {"source_completion", "source_reopen"}
    }
    source_events: list[dict[str, Any]] = []
    for fact in relations:
        relation = fact["task_relation"]["relation"]
        if relation not in {"completion", "reopen"}:
            continue
        event_id = "event-" + sha256_bytes(
            (relation + "\0" + task["task_id"] + "\0" + fact["fact_id"]).encode("utf-8")
        )
        source_events.append({
            "event_id": event_id, "kind": "source_" + relation,
            "fact_id": fact["fact_id"], "received_date": fact["received_date"],
            "changed_source_fields": dict(fact["task_relation"]["changed_source_fields"]),
            "source_order": list(_source_order(fact)),
        })
    non_source_events = [
        deepcopy(event) for event in task.get("lifecycle_history", [])
        if event.get("kind") not in {"source_completion", "source_reopen"}
    ]
    task["lifecycle_history"] = [*source_events, *non_source_events]
    if not non_source_events or any(event["event_id"] not in prior_source_event_ids for event in source_events):
        _set_resolution(task, resolution)


def build_derived_knowledge(facts: Sequence[Mapping[str, Any]], *, fact_schema: Mapping[str, Any], task_schema: Mapping[str, Any]) -> dict[str, Any]:
    validate_facts(facts, fact_schema)
    ordered = sorted(facts, key=_source_order)
    openings = [fact for fact in ordered if fact["flags"]["is_action"] and not fact.get("task_relation")]
    tasks = [_task_from_fact(fact) for fact in openings]
    by_id = {task["task_id"]: (task, opening) for task, opening in zip(tasks, openings)}
    grouped: dict[str, list[Mapping[str, Any]]] = {task_id: [] for task_id in by_id}
    for fact in ordered:
        relation = fact.get("task_relation")
        if relation:
            if relation["target_task_id"] not in grouped:
                raise TaskError("source relation has an unknown target task ID")
            grouped[relation["target_task_id"]].append(fact)
    for task_id, (task, opening) in by_id.items():
        _apply_source_facts(task, opening, grouped[task_id])
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
        existing_by_id[task["task_id"]] = deepcopy(dict(task))
    validate_facts(facts, fact_schema)
    ordered = sorted(facts, key=_source_order)
    openings = {
        canonical_task_id(fact["fact_id"]): fact for fact in ordered
        if fact["flags"]["is_action"] and not fact.get("task_relation")
    }
    relations: dict[str, list[Mapping[str, Any]]] = {task_id: [] for task_id in openings}
    for fact in ordered:
        relation = fact.get("task_relation")
        if relation:
            target = relation["target_task_id"]
            if target not in openings:
                raise TaskError("source relation has an unknown target task ID")
            relations[target].append(fact)
    for task_id, opening in openings.items():
        if task_id not in existing_by_id:
            task = _task_from_fact(opening)
            _apply_source_facts(task, opening, relations[task_id])
            existing_by_id[task_id] = task
            continue
        task = existing_by_id[task_id]
        if task["origin"] != "source":
            raise TaskError("source relation cannot target a parent-origin task")
        before = deepcopy(task)
        _apply_source_facts(task, opening, relations[task_id])
        _mark_changed(task, before, {"kind": "source_reconciliation", "source_fact_count": len(task["source_facts"])})
    result = {"schema_version": 1, "tasks": [existing_by_id[key] for key in sorted(existing_by_id)]}
    _validate_task_bindings(result["tasks"])
    _validated(result, register_schema, "canonical task register")
    return result


def serialize_canonical_tasks(register: Mapping[str, Any], register_schema: Mapping[str, Any]) -> bytes:
    _validated(register, register_schema, "canonical task register")
    return canonical_json_bytes(register)


def managed_projection(task: Mapping[str, Any]) -> dict[str, Any]:
    """The complete desired projection, including reconciled parent-editable fields."""
    return {
        "canonical_task_id": task["task_id"], "origin": task["origin"],
        "title": task["action"], "group": task["entity_scope"],
        "description": task["task_context"], "workflow_state": task["workflow_state"],
        "source_link": task["source_link"] or "", "source_due": task["source_due"] or "",
    }


def create_projection(task: Mapping[str, Any]) -> dict[str, Any]:
    return managed_projection(task)


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
        providers: set[str] = set()
        for binding in task["provider_bindings"]:
            pair = (binding.get("provider_id"), binding.get("provider_object_id"))
            if not all(isinstance(value, str) and value for value in pair):
                raise TaskError("canonical task has an invalid provider binding")
            if pair[0] in providers:
                raise TaskError("canonical task has multiple bindings for one provider")
            if pair in pairs:
                raise TaskError("duplicate provider binding")
            providers.add(pair[0])
            pairs.add(pair)


def _projection_hash(projection: Mapping[str, Any]) -> str:
    return sha256_bytes(canonical_json_bytes(dict(projection)))


def recover_task_comment(provider: TaskProviderPort, provider_object_id: str, effect_id: str, text: str) -> Mapping[str, Any]:
    """Adopt one immutable comment after a lost response; never blindly repeat it."""
    matches = [dict(comment) for comment in provider.find_comments(provider_object_id, effect_id)]
    if len(matches) > 1:
        raise TaskError("multiple provider comments match one immutable effect ID")
    if matches:
        if matches[0].get("text") != text:
            raise TaskError("provider comment effect ID has unexpected text")
        return matches[0]
    written = dict(provider.write_comment(provider_object_id, effect_id, text))
    matches = [dict(comment) for comment in provider.find_comments(provider_object_id, effect_id)]
    if len(matches) != 1 or matches[0] != written or matches[0].get("text") != text:
        raise TaskError("provider comment readback does not establish one immutable effect")
    return matches[0]


def reconcile_provider_tasks(
    provider: TaskProviderPort,
    register: Mapping[str, Any],
    provider_state: Mapping[str, Any],
    *, task_schema: Mapping[str, Any], register_schema: Mapping[str, Any], provider_state_schema: Mapping[str, Any],
    completion_comment_required: bool = True,
    missing_comment_reminder: str = "Completion needs a parent comment before it can be recorded.",
) -> ProviderReconciliation:
    """Reconcile one complete snapshot with durable intents and field-level three-way rules."""
    _validated(register, register_schema, "canonical task register")
    if completion_comment_required and not missing_comment_reminder.strip():
        raise TaskError("missing-comment policy requires nonempty generic reminder text")
    input_state = {
        **deepcopy(dict(provider_state)),
        "claim_intents": deepcopy(list(provider_state.get("claim_intents", []))),
        "effect_intents": deepcopy(list(provider_state.get("effect_intents", []))),
    }
    _validated(input_state, provider_state_schema, "provider state")
    tasks = {task["task_id"]: deepcopy(dict(task)) for task in register["tasks"]}
    if len(tasks) != len(register["tasks"]):
        raise TaskError("duplicate canonical task ID")
    original_tasks = {task_id: deepcopy(task) for task_id, task in tasks.items()}
    _validate_task_bindings(list(tasks.values()))
    provider_id = input_state["provider_id"]
    snapshot = [dict(item) for item in provider.list_tasks()]
    by_canonical: dict[str, dict[str, Any]] = {}
    by_object: dict[str, dict[str, Any]] = {}
    for item in snapshot:
        canonical_id, object_id = item.get("canonical_task_id"), item.get("provider_object_id")
        if canonical_id is None:
            continue
        if not isinstance(canonical_id, str) or not canonical_id or not isinstance(object_id, str) or not object_id:
            raise TaskError("provider task has invalid canonical identity")
        if canonical_id in by_canonical:
            raise TaskError("multiple provider tasks match one canonical task ID")
        if object_id in by_object:
            raise TaskError("provider snapshot repeats one immutable object ID")
        by_canonical[canonical_id] = item
        by_object[object_id] = item
    previous = {item["task_id"]: deepcopy(dict(item)) for item in input_state["bindings"]}
    if len(previous) != len(input_state["bindings"]) or len({item["provider_object_id"] for item in input_state["bindings"]}) != len(input_state["bindings"]):
        raise TaskError("provider bindings are not unique")
    effects: list[dict[str, Any]] = []
    review_cases: list[dict[str, Any]] = []
    pending = {item["task_id"]: deepcopy(dict(item)) for item in input_state["claim_intents"]}
    preexisting_pending = set(pending)
    if len(pending) != len(input_state["claim_intents"]):
        raise TaskError("duplicate parent claim intent")
    effect_intents = {item["effect_id"]: deepcopy(dict(item)) for item in input_state["effect_intents"]}
    if len(effect_intents) != len(input_state["effect_intents"]):
        raise TaskError("duplicate task effect intent")

    # Either half of an interrupted canonical-task/claim-intent checkpoint can
    # reconstruct the other from immutable admission evidence before mutation.
    for intent in pending.values():
        task_id = intent["task_id"]
        if task_id not in tasks:
            candidate_task = intent.get("task")
            if not isinstance(candidate_task, Mapping) or candidate_task.get("task_id") != task_id:
                raise TaskError("parent claim intent lacks recoverable canonical task evidence")
            tasks[task_id] = deepcopy(dict(candidate_task))
            original_tasks[task_id] = deepcopy(tasks[task_id])
        if tasks[task_id]["origin"] != "parent":
            raise TaskError("parent claim intent references a non-parent task")

    candidates = list(getattr(provider, "unbound_parent_candidates", lambda: [])())
    candidate_packets: list[tuple[Any, dict[str, Any], str]] = []
    for candidate in candidates:
        packet = {
            "row_id": getattr(candidate, "row_id", None),
            "action": getattr(candidate, "action", None),
            "group": getattr(candidate, "group", None),
            "status": getattr(candidate, "status", None),
            "parent_planned_due": getattr(candidate, "parent_planned_due", None),
            "parent_progress": getattr(candidate, "parent_progress", None),
            "completion_comment": getattr(candidate, "completion_comment", None),
            "expected_cells": deepcopy(dict(getattr(candidate, "expected_cells", {}))),
        }
        fingerprint = sha256_bytes(canonical_json_bytes({key: value for key, value in packet.items() if key != "row_id"}))
        candidate_packets.append((candidate, packet, fingerprint))

    claimed_rows: set[str | None] = set()
    for task_id, intent in pending.items():
        if task_id in by_canonical:
            continue
        intended = intent.get("candidate", {})
        matches = [
            entry for entry in candidate_packets
            if entry[1]["row_id"] == intended.get("row_id")
            and entry[2] == intended.get("fingerprint")
        ]
        if not matches:
            matches = [entry for entry in candidate_packets if entry[2] == intended.get("fingerprint")]
        if len(matches) != 1:
            raise TaskError("parent claim intent cannot recover one exact candidate")
        claimed_rows.add(matches[0][1]["row_id"])
    for task_id, task in list(tasks.items()):
        if task["origin"] != "parent" or task_id in pending or task_id in by_canonical:
            continue
        if any(binding.get("provider_id") == provider_id for binding in task["provider_bindings"]):
            continue
        admission = task.get("last_modified_evidence", {}).get("parent_admission")
        if not isinstance(admission, Mapping):
            raise TaskError("unbound parent task lacks recoverable admission intent")
        matches = [entry for entry in candidate_packets if entry[2] == admission.get("candidate_fingerprint")]
        preferred = [entry for entry in matches if entry[1]["row_id"] == admission.get("admitted_row_id")]
        chosen = preferred or matches
        if len(chosen) != 1:
            raise TaskError("parent task admission evidence does not resolve one unbound candidate")
        _, packet, fingerprint = chosen[0]
        pending[task_id] = {
            "task_id": task_id, "provider_object_id": "unclaimed:" + task_id,
            "candidate": {**packet, "fingerprint": fingerprint}, "task": deepcopy(task),
        }
        claimed_rows.add(packet["row_id"])
        effects.append({"kind": "parent_claim_intent", "intent": deepcopy(pending[task_id]), "outcome": "recovered"})

    for _, packet, fingerprint in candidate_packets:
        if packet["row_id"] in claimed_rows:
            continue
        task = parent_task_from_provider(provider_id, packet)
        task["last_modified_evidence"] = {
            "parent_admission": {
                "provider_id": provider_id,
                "admitted_row_id": packet["row_id"],
                "candidate_fingerprint": fingerprint,
            }
        }
        tasks[task["task_id"]] = task
        pending[task["task_id"]] = {
            "task_id": task["task_id"], "provider_object_id": "unclaimed:" + task["task_id"],
            "candidate": {**packet, "fingerprint": fingerprint}, "task": deepcopy(task),
        }
        claimed_rows.add(packet["row_id"])
        effects.append({"kind": "parent_claim_intent", "intent": deepcopy(pending[task["task_id"]]), "outcome": "journaled"})

    for task_id, intent in list(pending.items()):
        if task_id not in preexisting_pending:
            continue  # caller persists this intent before a guarded provider claim
        current = by_canonical.get(task_id)
        if current is None:
            intended = intent["candidate"]
            candidates_for_intent = [
                entry for entry in candidate_packets
                if entry[1]["row_id"] == intended.get("row_id")
                and entry[2] == intended.get("fingerprint")
            ]
            if not candidates_for_intent:
                candidates_for_intent = [entry for entry in candidate_packets if entry[2] == intended.get("fingerprint")]
            if len(candidates_for_intent) != 1:
                raise TaskError("parent claim intent cannot recover one exact candidate")
            candidate = candidates_for_intent[0][0]
            claim = getattr(provider, "claim_parent_candidate", None)
            if claim is None:
                continue
            current = dict(claim(candidate, canonical_task_id=task_id, workflow_state=tasks[task_id]["workflow_state"]))
            by_canonical[task_id] = current
            effects.append({"kind": "parent_claim", "intent": intent, "outcome": "confirmed", "provider_object_id": current["provider_object_id"]})
        _bind(tasks[task_id], provider_id, current["provider_object_id"])
        pending.pop(task_id)

    # Managed IDs are never admitted from the provider snapshot on their own.
    unknown = set(by_canonical) - set(tasks)
    if unknown:
        raise TaskError("provider snapshot contains an unknown managed canonical task ID")

    for task_id, prior in previous.items():
        if task_id not in tasks:
            raise TaskError("provider state binding references an unknown canonical task")
        canonical_bindings = [binding for binding in tasks[task_id]["provider_bindings"] if binding.get("provider_id") == provider_id]
        if canonical_bindings and canonical_bindings[0].get("provider_object_id") != prior["provider_object_id"]:
            raise TaskError("canonical and provider-state bindings disagree")
        current = by_canonical.get(task_id)
        if current is not None and current["provider_object_id"] != prior["provider_object_id"]:
            raise TaskError("provider snapshot and durable binding disagree")

    # Recover each previously journaled completion-policy effect in exact order.
    for effect_id in list(effect_intents):
        intent = effect_intents[effect_id]
        task_id, object_id = intent["task_id"], intent["provider_object_id"]
        if task_id not in tasks or by_canonical.get(task_id, {}).get("provider_object_id") != object_id:
            raise TaskError("task effect intent does not resolve its canonical provider object")
        recover_task_comment(provider, object_id, effect_id, intent["text"])
        apply_state = getattr(provider, "apply_parent_state", None)
        if apply_state is None:
            raise TaskError("completion without comment needs a reopen-capable provider")
        reopened = dict(apply_state(object_id, status="open"))
        exact = provider.read_task(object_id)
        if exact is None or str(dict(exact).get("status", "")).lower() != "open":
            raise TaskError("missing-comment reopen readback is not open")
        by_canonical[task_id] = dict(exact)
        event = {
            "event_id": effect_id, "kind": "reopened_missing_completion_comment",
            "provider_object_id": object_id, "occurrence": intent["occurrence"],
            "reminder_text": intent["text"],
        }
        if not any(value.get("event_id") == effect_id for value in tasks[task_id]["lifecycle_history"]):
            tasks[task_id]["lifecycle_history"] = [*tasks[task_id]["lifecycle_history"], event]
        _set_resolution(tasks[task_id], "unresolved")
        effects.append({"kind": "reopen_reminder", "intent": deepcopy(intent), "outcome": "confirmed", "provider_object_id": object_id})
        effect_intents.pop(effect_id)

    bindings: list[dict[str, Any]] = []
    for task_id in sorted(tasks):
        if task_id in pending:
            continue
        task = tasks[task_id]
        before = deepcopy(task)
        _set_resolution(task, _resolution(task))
        projection = managed_projection(task)
        current = by_canonical.get(task_id)
        conflicts: set[str] = set()
        intent = {"task_id": task_id, "projection_sha256": _projection_hash(projection)}
        if current is None:
            if any(binding.get("provider_id") == provider_id for binding in task["provider_bindings"]):
                raise TaskError("durably bound provider task is absent from the complete snapshot")
            if _resolution(task) == "completed":
                _mark_changed(task, before, {"kind": "provider_reconciliation", "provider_id": provider_id})
                continue
            current = dict(provider.create_task(create_projection(task)))
            effect_kind = "create"
        else:
            prior_binding = previous.get(task_id)
            prior_managed = dict(prior_binding.get("last_managed_projection", {})) if prior_binding else {}
            if prior_binding:
                verify = getattr(provider, "verify_expected_system_fields", None)
                if verify is not None:
                    verify({task_id: prior_managed}, {task_id: projection})
            system_fields = ("canonical_task_id", "origin", "description", "workflow_state", "source_link", "source_due")
            for field in system_fields:
                remote = current.get(field)
                local = projection[field]
                if not prior_binding:
                    if remote != local:
                        raise TaskError("managed provider state lacks a verified common baseline")
                else:
                    base = prior_managed.get(field)
                    if remote not in {base, local}:
                        raise TaskError("unexpected system-managed provider drift")

            parent_map = (
                ("title", "action"), ("group", "entity_scope"),
                ("parent_planned_due", "parent_planned_due"),
                ("parent_progress", "latest_progress"),
            )
            prior_parent = prior_binding.get("last_parent_snapshot", {}) if prior_binding else {}
            for remote_field, canonical_field in parent_map:
                remote_present, remote = _snapshot_value(_parent_snapshot(current), remote_field)
                base_present, base = _snapshot_value(prior_parent, remote_field)
                local = task[canonical_field]
                if not remote_present:
                    continue
                if not prior_binding:
                    if remote != local:
                        if task["origin"] == "parent":
                            task[canonical_field] = remote
                        else:
                            raise TaskError("parent-editable provider state lacks a verified common baseline")
                elif local == remote:
                    pass
                elif local == base:
                    if remote_field in {"title", "group"} and (not isinstance(remote, str) or not remote):
                        raise TaskError("parent edit cleared a required task field")
                    task[canonical_field] = remote
                elif remote == base:
                    pass
                else:
                    conflicts.add(remote_field)
                    review_cases.append({
                        "task_id": task_id, "reason": "simultaneous canonical and parent field changes",
                        "field": remote_field, "base": base, "canonical": local, "provider": remote,
                    })
            projection = managed_projection(task)
            patch = {
                key: value for key, value in projection.items()
                if current.get(key) != value and key not in conflicts
            }
            current = dict(provider.apply_patch(current["provider_object_id"], patch)) if patch else current
            effect_kind = "patch" if patch else "adopt"
        object_id = current.get("provider_object_id")
        if not isinstance(object_id, str) or not object_id:
            raise TaskError("provider operation did not return an immutable object ID")
        actual = provider.read_task(object_id)
        if actual is None:
            raise TaskError("provider task readback is unavailable")
        actual = dict(actual)
        if any(actual.get(key) != value for key, value in projection.items() if key not in conflicts):
            raise TaskError("provider task readback does not match managed projection")
        prior = previous.get(task_id, {}).get("last_parent_snapshot", {})
        status_present, status = _snapshot_value(_parent_snapshot(actual), "status")
        comment_present, comment = _snapshot_value(_parent_snapshot(actual), "completion_comment")
        old_status_present, old_status = _snapshot_value(prior, "status")
        is_complete = status_present and isinstance(status, str) and status.lower() in {"completed", "complete", "done"}
        was_complete = old_status_present and isinstance(old_status, str) and old_status.lower() in {"completed", "complete", "done"}
        if is_complete and not was_complete:
            occurrence = 1 + sum(
                1 for event in task["lifecycle_history"]
                if event.get("kind") in {"parent_completion", "reopened_missing_completion_comment"}
            )
            if completion_comment_required and (not comment_present or not isinstance(comment, str) or not comment.strip()):
                effect_id = "event-" + sha256_bytes(
                    f"reopen-reminder\0{task_id}\0{object_id}\0{occurrence}".encode("utf-8")
                )
                effect_intents[effect_id] = {
                    "effect_id": effect_id, "kind": "reopen_missing_completion_comment",
                    "task_id": task_id, "provider_object_id": object_id,
                    "occurrence": occurrence, "text": missing_comment_reminder,
                }
                review_cases.append({"task_id": task_id, "reason": "completion requires a nonempty parent comment"})
                effects.append({"kind": "reopen_reminder_intent", "intent": deepcopy(effect_intents[effect_id]), "outcome": "journaled"})
            else:
                retained_comment = comment if isinstance(comment, str) else ""
                event_id = "event-" + sha256_bytes(
                    f"parent-completion\0{task_id}\0{object_id}\0{occurrence}".encode("utf-8")
                )
                if not any(event.get("event_id") == event_id for event in task["lifecycle_history"]):
                    task["lifecycle_history"] = [*task["lifecycle_history"], {"event_id": event_id, "kind": "parent_completion", "provider_object_id": object_id, "status": status, "comment": retained_comment, "occurrence": occurrence}]
                _set_resolution(task, "completed")
        elif status_present and was_complete and not is_complete:
            reopen_occurrence = 1 + sum(
                1 for event in task["lifecycle_history"] if event.get("kind") == "parent_reopen"
            )
            event_id = "event-" + sha256_bytes(
                f"parent-reopen\0{task_id}\0{object_id}\0{reopen_occurrence}".encode("utf-8")
            )
            if not any(event.get("event_id") == event_id for event in task["lifecycle_history"]):
                task["lifecycle_history"] = [*task["lifecycle_history"], {
                    "event_id": event_id, "kind": "parent_reopen",
                    "provider_object_id": object_id, "status": status,
                    "occurrence": reopen_occurrence,
                }]
            _set_resolution(task, "unresolved")
        task["projection_state"] = {**task["projection_state"], "provider_status": status if status_present else None}
        _bind(task, provider_id, object_id)
        next_snapshot = _parent_snapshot(actual)
        for field in conflicts:
            if field in prior:
                next_snapshot[field] = deepcopy(prior[field])
        if any(intent_value["task_id"] == task_id for intent_value in effect_intents.values()):
            for field in ("status", "completion_comment"):
                if field in prior:
                    next_snapshot[field] = deepcopy(prior[field])
                else:
                    next_snapshot.pop(field, None)
        bindings.append({"task_id": task_id, "provider_object_id": object_id, "status": "verified", "last_managed_projection": projection, "projection_sha256": _projection_hash(projection), "last_parent_snapshot": next_snapshot, "verified_readback": {"provider_object_id": object_id}})
        effects.append({"kind": effect_kind, "intent": intent, "outcome": "confirmed", "provider_object_id": object_id})
        _mark_changed(task, original_tasks.get(task_id, before), {"kind": "provider_reconciliation", "provider_id": provider_id, "provider_object_id": object_id})
    _validate_task_bindings(list(tasks.values()))
    # Retain durable bindings for resolved tasks that intentionally have no row mutation.
    bound_ids = {binding["task_id"] for binding in bindings}
    for task_id, prior in previous.items():
        if task_id not in bound_ids and task_id in tasks:
            bindings.append(deepcopy(prior))
    bindings.sort(key=lambda value: value["task_id"])
    state = {"provider_id": provider_id, "adapter_id": input_state["adapter_id"], "provider_revision": input_state.get("provider_revision"), "bindings": bindings, "claim_intents": [pending[key] for key in sorted(pending)], "effect_intents": [effect_intents[key] for key in sorted(effect_intents)], "cursor": input_state["cursor"], "cursor_evidence": {"pulled": True, "count": len(snapshot)}, "verified_readback": {"bindings": len(bindings)}}
    _validated(state, provider_state_schema, "provider state")
    result = {"schema_version": register["schema_version"], "tasks": [tasks[key] for key in sorted(tasks)]}
    for task in result["tasks"]:
        _validated(task, task_schema, "canonical task")
    _validated(result, register_schema, "canonical task register")
    return ProviderReconciliation(result, state, tuple(effects), tuple(review_cases))
