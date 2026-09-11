"""Deterministic current-delta manifest construction for the audio worker."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .contracts import canonical_json_bytes


class AudioManifestError(ValueError):
    """Raised when canonical delta or private voice routing is incomplete."""


def merge_parent_task_delta(
    delta: Mapping[str, Any], before: Mapping[str, Any], after: Mapping[str, Any],
) -> dict[str, Any]:
    """Accumulate changed parent-origin canonical tasks without duplicating IDs."""
    fact_delta, task_delta = _delta(delta)
    before_tasks = before.get("tasks") if isinstance(before, Mapping) else None
    after_tasks = after.get("tasks") if isinstance(after, Mapping) else None
    if not isinstance(before_tasks, list) or not isinstance(after_tasks, list):
        raise AudioManifestError("canonical task registers are malformed")
    prior = {
        item.get("task_id"): item for item in before_tasks
        if isinstance(item, Mapping) and isinstance(item.get("task_id"), str)
    }
    current = {
        item.get("task_id"): item for item in after_tasks
        if isinstance(item, Mapping) and isinstance(item.get("task_id"), str)
    }
    if len(prior) != len(before_tasks) or len(current) != len(after_tasks):
        raise AudioManifestError("canonical task registers repeat an identity")
    accumulated = {item["task_id"]: dict(item) for item in task_delta}
    for task_id, task in current.items():
        if task.get("origin") != "parent":
            continue
        previous = prior.get(task_id)
        if previous is None:
            accumulated[task_id] = {"task_id": task_id, "delta_kind": "new"}
        elif canonical_json_bytes(task) != canonical_json_bytes(previous):
            accumulated.setdefault(task_id, {"task_id": task_id, "delta_kind": "changed"})
    return {
        "schema_version": 1, "facts": fact_delta,
        "tasks": [accumulated[key] for key in sorted(accumulated)],
    }


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AudioManifestError(f"{label} must be a nonempty string")
    return value


def _configuration(value: Mapping[str, Any]) -> dict[str, Any]:
    required = {"voices", "opening_tag", "closing_tag", "groups"}
    if not isinstance(value, Mapping) or set(value) != required:
        raise AudioManifestError("audio routing configuration has an unsupported shape")
    voices = value["voices"]
    if (
        not isinstance(voices, Mapping) or "narrator" not in voices
        or any(not isinstance(role, str) or not role or not isinstance(identity, str) or not identity for role, identity in voices.items())
    ):
        raise AudioManifestError("audio routing requires explicit voice IDs")
    for field in ("opening_tag", "closing_tag"):
        tag = _text(value[field], f"audio {field}")
        if not tag.startswith("[") or not tag.endswith("]"):
            raise AudioManifestError(f"audio {field} must be one bracketed tag")
    groups = value["groups"]
    if not isinstance(groups, Mapping) or not groups:
        raise AudioManifestError("audio routing requires configured canonical groups")
    normalized_groups: dict[str, Any] = {}
    for scope, route in groups.items():
        if not isinstance(scope, str) or not scope or not isinstance(route, Mapping) or set(route) != {"subject_label", "voice_role", "dialogue_tags"}:
            raise AudioManifestError("audio group route has an unsupported shape")
        voice_role = _text(route["voice_role"], "audio group voice_role")
        if voice_role not in voices:
            raise AudioManifestError("audio group references an unconfigured voice role")
        tags = route["dialogue_tags"]
        if not isinstance(tags, Mapping) or set(tags) != {"news", "guideline", "action"}:
            raise AudioManifestError("audio group must declare every dialogue section tag")
        if any(not isinstance(tag, str) or not tag.startswith("[") or not tag.endswith("]") for tag in tags.values()):
            raise AudioManifestError("audio group dialogue tags must be bracketed")
        normalized_groups[scope] = {
            "subject_label": _text(route["subject_label"], "audio group subject_label"),
            "voice_role": voice_role, "dialogue_tags": dict(tags),
        }
    return {
        "voices": dict(voices), "opening_tag": value["opening_tag"],
        "closing_tag": value["closing_tag"], "groups": normalized_groups,
    }


def _delta(value: Mapping[str, Any]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    if not isinstance(value, Mapping) or set(value) != {"schema_version", "facts", "tasks"} or value.get("schema_version") != 1:
        raise AudioManifestError("current reconciliation delta has an unsupported shape")
    result: list[list[dict[str, str]]] = [[], []]
    for position, (field, identity) in enumerate((("facts", "fact_id"), ("tasks", "task_id"))):
        values = value[field]
        if not isinstance(values, list):
            raise AudioManifestError(f"audio delta {field} must be an array")
        seen: set[str] = set()
        for item in values:
            if not isinstance(item, Mapping) or set(item) != {identity, "delta_kind"}:
                raise AudioManifestError(f"audio delta {field} item is malformed")
            identifier = _text(item[identity], f"audio delta {identity}")
            if identifier in seen or item["delta_kind"] not in {"new", "changed"}:
                raise AudioManifestError(f"audio delta {field} identity/kind is invalid")
            seen.add(identifier)
            result[position].append({identity: identifier, "delta_kind": item["delta_kind"]})
    return result[0], result[1]


def build_audio_manifest(
    *, run_date: str, window: Mapping[str, Any], delta: Mapping[str, Any],
    facts: Sequence[Mapping[str, Any]], canonical_tasks: Mapping[str, Any],
    source_threads: Mapping[str, str], configuration: Mapping[str, Any],
) -> dict[str, Any]:
    """Build exact worker input from explicit, already-persisted canonical delta."""
    config = _configuration(configuration)
    if not isinstance(window, Mapping) or set(window) != {"start", "end"}:
        raise AudioManifestError("audio window must contain exact start and end")
    fact_delta, task_delta = _delta(delta)
    facts_by_id = {
        item.get("fact_id"): item for item in facts
        if isinstance(item, Mapping) and isinstance(item.get("fact_id"), str)
    }
    if len(facts_by_id) != len(facts):
        raise AudioManifestError("canonical Facts contain malformed or duplicate identities")
    tasks = canonical_tasks.get("tasks") if isinstance(canonical_tasks, Mapping) else None
    if not isinstance(tasks, list):
        raise AudioManifestError("canonical task register is malformed")
    tasks_by_id = {
        item.get("task_id"): item for item in tasks
        if isinstance(item, Mapping) and isinstance(item.get("task_id"), str)
    }
    if len(tasks_by_id) != len(tasks):
        raise AudioManifestError("canonical tasks contain malformed or duplicate identities")

    records: list[dict[str, Any]] = []
    for selected in fact_delta:
        fact = facts_by_id.get(selected["fact_id"])
        if fact is None:
            raise AudioManifestError("audio delta references an unknown Fact")
        flags = fact.get("flags")
        if not isinstance(flags, Mapping):
            raise AudioManifestError("audio Fact lacks classification flags")
        section = "action" if flags.get("is_action") is True else "guideline" if flags.get("is_guideline") is True else "news"
        scope = fact.get("entity_scope")
        route = config["groups"].get(scope)
        source_tid = source_threads.get(fact.get("record_id"))
        if route is None or not isinstance(source_tid, str) or not source_tid:
            raise AudioManifestError("audio Fact lacks configured group or source thread")
        records.append({
            "delta_kind": selected["delta_kind"], "section": section,
            "voice_role": route["voice_role"],
            "dialogue_tag": route["dialogue_tags"][section],
            "subject_label": route["subject_label"],
            "spoken_text": _text(fact.get("text"), "audio Fact canonical text"),
            "source_tid": source_tid, "fact_or_row_id": selected["fact_id"],
        })
    for selected in task_delta:
        task = tasks_by_id.get(selected["task_id"])
        if task is None:
            raise AudioManifestError("audio delta references an unknown canonical task")
        scope = task.get("entity_scope")
        route = config["groups"].get(scope)
        if route is None:
            raise AudioManifestError("audio task lacks a configured group")
        source_tid = "parent:" + selected["task_id"]
        source_facts = task.get("source_facts")
        if isinstance(source_facts, list) and source_facts:
            source_fact = facts_by_id.get(source_facts[-1])
            if source_fact is None or source_fact.get("record_id") not in source_threads:
                raise AudioManifestError("audio task source provenance is unavailable")
            source_tid = source_threads[source_fact["record_id"]]
        records.append({
            "delta_kind": selected["delta_kind"], "section": "action",
            "voice_role": route["voice_role"],
            "dialogue_tag": route["dialogue_tags"]["action"],
            "subject_label": route["subject_label"],
            "spoken_text": _text(task.get("action"), "audio task canonical action"),
            "source_tid": source_tid, "fact_or_row_id": selected["task_id"],
        })
    return {
        "voices": config["voices"], "opening_tag": config["opening_tag"],
        "closing_tag": config["closing_tag"], "run_date": _text(run_date, "audio run_date"),
        "window": {"start": _text(window["start"], "audio window start"), "end": _text(window["end"], "audio window end")},
        "records": records,
    }
