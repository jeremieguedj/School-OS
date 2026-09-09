"""One durable connected canonical-task reconciliation phase.

The worker composes audited persisted Fact artifacts, the accepted canonical
merge engine, and a selected task adapter.  It is deliberately not a daily CLI:
one call performs one recoverable reconciliation pass and reports whether a
second pass is required for a journaled claim/create/reminder effect.
"""
from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from .connected_storage import ArtifactStore, DriveReference, StoredArtifact
from .contracts import canonical_json_bytes
from .tasks import (
    ProviderReconciliation, reconcile_canonical_tasks,
    reconcile_provider_tasks, serialize_canonical_tasks, unresolved_tasks,
)


class ConnectedTaskError(ValueError):
    """Raised when the durable connected task phase cannot establish evidence."""


def _json_object(data: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ConnectedTaskError(f"{label} is not UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise ConnectedTaskError(f"{label} must be a JSON object")
    return value


def _read_exact(store: ArtifactStore, reference: DriveReference, label: str) -> StoredArtifact:
    artifact = store.read(reference)
    if artifact.reference.object_id != reference.object_id or artifact.reference.parent_id != reference.parent_id:
        raise ConnectedTaskError(f"{label} readback has the wrong durable artifact identity")
    return artifact


def _replace_exact(store: ArtifactStore, reference: DriveReference, data: bytes, label: str) -> StoredArtifact:
    artifact = store.replace(reference, data, "application/json")
    if artifact.reference.object_id != reference.object_id or artifact.data != data:
        raise ConnectedTaskError(f"{label} durable write did not read back exact bytes")
    return artifact


def _fact_artifact_facts(artifact: StoredArtifact) -> list[dict[str, Any]]:
    value = _json_object(artifact.data, "audited Fact artifact")
    facts = value.get("facts")
    if not isinstance(facts, list) or any(not isinstance(item, Mapping) for item in facts):
        raise ConnectedTaskError("audited Fact artifact lacks a fact array")
    record_id = value.get("record_id")
    if record_id is not None and (not isinstance(record_id, str) or not record_id):
        raise ConnectedTaskError("audited Fact artifact has an invalid record identity")
    copied = [dict(item) for item in facts]
    if record_id is not None and any(item.get("record_id") != record_id for item in copied):
        raise ConnectedTaskError("audited Fact artifact record identity disagrees with a Fact")
    return copied


def unresolved_finite_task_selection(
    register: Mapping[str, Any], *, task_source_links: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Emit every eligible current task with provenance for the brief builder.

    Parent origin is explicit canonical data, never a fallback for malformed
    source evidence.  The result intentionally preserves an absent source date
    and URL for the approved undated parent-added presentation.
    """
    selected: list[dict[str, Any]] = []
    verified_links = dict(task_source_links or {})
    for task in sorted(unresolved_tasks(register), key=lambda item: item["task_id"]):
        origin = task.get("origin")
        if origin == "source":
            if not isinstance(task.get("last_supporting_source_date"), str) or not task["last_supporting_source_date"]:
                raise ConnectedTaskError("unresolved source task lacks its required latest supporting date")
            link = verified_links.get(task["task_id"])
            if not isinstance(link, str) or not link:
                raise ConnectedTaskError("unresolved source task lacks a verified provenance link")
        elif origin == "parent":
            if task.get("source_opened_date") is not None or task.get("source_link") is not None or task.get("source_facts"):
                raise ConnectedTaskError("parent-origin task carries invented source provenance")
            link = None
        else:
            raise ConnectedTaskError("canonical task has an unsupported origin")
        if task.get("workflow_state") not in {"needs_action", "waiting_external", "needs_review"}:
            raise ConnectedTaskError("unresolved task is not a finite actionable workflow item")
        selected.append({
            "task_id": task["task_id"], "origin": origin, "action": task["action"],
            "entity_scope": task["entity_scope"], "resolution": "unresolved",
            "last_supporting_source_date": task["last_supporting_source_date"],
            "source_link": link, "source_facts": list(task["source_facts"]),
        })
    return {"selection": "all_unresolved_finite", "tasks": selected}


@dataclass(frozen=True)
class ConnectedTaskResult:
    canonical_tasks: StoredArtifact
    provider_state: StoredArtifact
    reconciliation: ProviderReconciliation
    brief_tasks: dict[str, Any]
    continuation_required: bool


@dataclass(frozen=True)
class ConnectedTaskReconcileResult:
    """The canonical-only handoff from ``reconcile`` to ``task_sync``."""

    canonical_tasks: StoredArtifact
    brief_tasks: dict[str, Any]


class ConnectedTaskWorker:
    """Persist source-canonical state before provider advancement and read back.

    The adapter instance must be a new sync session for this call.  Callers pass
    exact admitted artifacts, so this worker never discovers private files by
    name and never accepts a connector-provided ``verified`` flag as evidence.
    """

    def __init__(
        self, *, store: ArtifactStore, fact_schema: Mapping[str, Any], task_schema: Mapping[str, Any],
        register_schema: Mapping[str, Any], provider_state_schema: Mapping[str, Any],
    ) -> None:
        self.store = store
        self.fact_schema = dict(fact_schema)
        self.task_schema = dict(task_schema)
        self.register_schema = dict(register_schema)
        self.provider_state_schema = dict(provider_state_schema)

    def reconcile(
        self, *, facts: Sequence[DriveReference], canonical_tasks: DriveReference,
        task_source_links: Mapping[str, str] | None = None,
        source_disposition: Mapping[str, Any] | None = None,
    ) -> ConnectedTaskReconcileResult:
        """Persist audited Fact reconciliation without touching a task provider."""
        if not facts:
            if not isinstance(source_disposition, Mapping) or source_disposition.get("verified") is not True or source_disposition.get("phase_complete") is not True or source_disposition.get("remaining_work") != {}:
                raise ConnectedTaskError("empty Fact input requires a verified complete upstream source disposition")
        collected: list[dict[str, Any]] = []
        seen_fact_ids: set[str] = set()
        for reference in facts:
            artifact = _read_exact(self.store, reference, "Fact artifact")
            for fact in _fact_artifact_facts(artifact):
                fact_id = fact.get("fact_id")
                if not isinstance(fact_id, str) or not fact_id or fact_id in seen_fact_ids:
                    raise ConnectedTaskError("audited Fact artifacts have duplicate or missing Fact IDs")
                seen_fact_ids.add(fact_id)
                collected.append(fact)
        # Reconciliation is the explicit mutable-pointer readmission boundary.
        # A fresh process may hold a stale reference from its last checkpoint.
        register_artifact = _read_exact(self.store, canonical_tasks.current(), "canonical task register")
        register = _json_object(register_artifact.data, "canonical task register")
        source_reconciled = reconcile_canonical_tasks(
            register, collected, fact_schema=self.fact_schema, task_schema=self.task_schema,
            register_schema=self.register_schema,
        )
        canonical_artifact = _replace_exact(
            # The first replacement must use the version just observed above,
            # rather than a caller's pre-reset checkpoint reference.  A new
            # process deliberately begins from ``current()`` so it can recover
            # durable state without trusting a stale mutable write version.
            self.store, register_artifact.reference,
            serialize_canonical_tasks(source_reconciled, self.register_schema), "canonical task register",
        )
        return ConnectedTaskReconcileResult(
            canonical_artifact,
            unresolved_finite_task_selection(source_reconciled, task_source_links=task_source_links),
        )

    def task_sync(
        self, *, canonical_tasks: DriveReference, provider_state: DriveReference,
        provider: Any, task_source_links: Mapping[str, str] | None = None,
    ) -> ConnectedTaskResult:
        """Synchronize one verified canonical register without rereading Facts.

        The caller supplies the exact reference emitted by :meth:`reconcile`.
        Recovery/readmission belongs to that preceding phase; this provider-only
        phase must not silently weaken its canonical handoff version.
        """
        register_artifact = _read_exact(self.store, canonical_tasks, "canonical task register")
        state_artifact = _read_exact(self.store, provider_state.current(), "provider state")
        register = _json_object(register_artifact.data, "canonical task register")
        state = _json_object(state_artifact.data, "provider state")

        canonical_pointer = register_artifact.reference
        provider_pointer = state_artifact.reference
        durable_state = state

        def checkpoint_effect(effect: Mapping[str, Any]) -> Mapping[str, Any]:
            nonlocal durable_state, provider_pointer
            effect_id = effect.get("effect_id")
            if not isinstance(effect_id, str) or not effect_id:
                raise ConnectedTaskError("effect checkpoint lacks its immutable identity")
            intents = durable_state.get("effect_intents", [])
            if not isinstance(intents, list):
                raise ConnectedTaskError("provider state effect journal is malformed")
            changed = False
            replaced: list[dict[str, Any]] = []
            for item in intents:
                if not isinstance(item, Mapping):
                    raise ConnectedTaskError("provider state effect journal item is malformed")
                if item.get("effect_id") == effect_id:
                    replaced.append(dict(effect)); changed = True
                else:
                    replaced.append(dict(item))
            if not changed:
                raise ConnectedTaskError("pre-dispatch effect is absent from durable provider state")
            durable_state = {**durable_state, "effect_intents": replaced}
            written = _replace_exact(self.store, provider_pointer, canonical_json_bytes(durable_state), "pre-dispatch provider state")
            provider_pointer = written.reference
            durable_state = _json_object(written.data, "pre-dispatch provider state")
            matched = [item for item in durable_state.get("effect_intents", []) if item.get("effect_id") == effect_id]
            if len(matched) != 1 or matched[0] != dict(effect):
                raise ConnectedTaskError("pre-dispatch provider checkpoint did not read back the exact effect")
            return dict(matched[0])

        reconciliation = reconcile_provider_tasks(
            provider, register, state, task_schema=self.task_schema,
            register_schema=self.register_schema, provider_state_schema=self.provider_state_schema,
            checkpoint_effect_intent=checkpoint_effect,
        )
        # The returned canonical register (including binding/lifecycle evidence)
        # remains the first half of every post-provider checkpoint.
        canonical_artifact = _replace_exact(
            self.store, canonical_pointer,
            serialize_canonical_tasks(reconciliation.tasks, self.register_schema), "reconciled canonical task register",
        )
        provider_artifact = _replace_exact(
            self.store, provider_pointer, canonical_json_bytes(reconciliation.provider_state), "reconciled provider state",
        )
        return ConnectedTaskResult(
            canonical_artifact, provider_artifact, reconciliation,
            unresolved_finite_task_selection(reconciliation.tasks, task_source_links=task_source_links),
            bool(reconciliation.provider_state.get("claim_intents") or reconciliation.provider_state.get("effect_intents")),
        )

    def run_once(
        self, *, facts: Sequence[DriveReference], canonical_tasks: DriveReference,
        provider_state: DriveReference, provider: Any,
        task_source_links: Mapping[str, str] | None = None,
        source_disposition: Mapping[str, Any] | None = None,
    ) -> ConnectedTaskResult:
        """Compatibility composition of the explicit canonical and provider phases."""
        reconciled = self.reconcile(
            facts=facts, canonical_tasks=canonical_tasks,
            task_source_links=task_source_links, source_disposition=source_disposition,
        )
        return self.task_sync(
            canonical_tasks=reconciled.canonical_tasks.reference,
            provider_state=provider_state, provider=provider,
            task_source_links=task_source_links,
        )
