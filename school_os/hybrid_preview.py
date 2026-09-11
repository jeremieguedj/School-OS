"""Tracked hybrid continuation through an agent-operated unsent preview."""
from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .agent_tasks import (
    AgentTaskPlan, authorize_next_action, confirm_action, plan_task_sync,
)
from .audio import merge_parent_task_delta
from .brief import build_brief_input, render_brief
from .bundles import BundleEntry, BundleMemberReference, read_bundle, resolve_member
from .catalog import parse_v2_record
from .connected_storage import BundleTransactionStore
from .connected_tasks import unresolved_finite_task_selection
from .contracts import canonical_json_bytes, sha256_bytes
from .hybrid_operations import HybridCheckpointPublisher
from .install import publish_hybrid_content_bundle
from .operations import checkpoint_pointer
from .tasks import (
    build_derived_knowledge, canonical_task_id, reconcile_canonical_tasks,
    unresolved_tasks,
)


class HybridPreviewError(ValueError):
    """Raised when the installed preview cannot safely advance."""


@dataclass(frozen=True)
class PreviewAdvance:
    transaction: BundleTransactionStore
    checkpoint: dict[str, Any]
    action: dict[str, Any] | None = None


@dataclass(frozen=True)
class PreviewFinish:
    transaction: BundleTransactionStore
    checkpoint: dict[str, Any]
    evidence: dict[str, Any]
    output_bundle: Mapping[str, Any]


@dataclass(frozen=True)
class CurrentBrief:
    brief_input: dict[str, Any]
    html: bytes
    text: bytes
    source: dict[str, Any]


def _json(data: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HybridPreviewError(f"{label} is not UTF-8 JSON") from exc
    if not isinstance(value, dict) or canonical_json_bytes(value) != data:
        raise HybridPreviewError(f"{label} is not canonical JSON")
    return value


def _schemas(root: Path) -> dict[str, dict[str, Any]]:
    names = (
        "fact.schema.json", "task.schema.json", "canonical-tasks.schema.json",
        "provider-state.schema.json", "task-adapter-snapshot.schema.json",
        "task-adapter-action.schema.json", "task-adapter-result.schema.json",
        "brief-input.schema.json", "operation-state.schema.json",
        "operation-checkpoint.schema.json",
    )
    return {name: json.loads((root / "schemas" / name).read_text(encoding="utf-8")) for name in names}


def _tip(transaction: BundleTransactionStore) -> tuple[dict[str, Any], dict[str, Any]]:
    state = _json(transaction.read("state/operation-state.json").data, "operation state")
    if state.get("status") != "running" or not isinstance(state.get("checkpoint"), Mapping):
        raise HybridPreviewError("preview requires one running admitted operation")
    path = "state/operation-checkpoints/" + state["checkpoint"]["checkpoint_id"] + ".json"
    checkpoint = _json(transaction.read(path).data, "operation checkpoint")
    if checkpoint_pointer(checkpoint) != state["checkpoint"]:
        raise HybridPreviewError("operation state does not select the exact checkpoint")
    return state, checkpoint


def _publish(
    *, transaction: BundleTransactionStore, storage: Any,
    prior_state: Mapping[str, Any], prior: Mapping[str, Any],
    resolved: Any, installed_root: Path, serialization: Mapping[str, Any],
    phase: str, completed: list[str], remaining: Mapping[str, Any],
    verification: Mapping[str, Any], effects: list[dict[str, Any]],
    terminal: bool = False, artifacts: list[dict[str, Any]] | None = None,
    required_phases: tuple[str, ...] = (),
    terminal_reason: str = "verified agent-operated unsent preview complete",
) -> PreviewAdvance:
    sequence = int(prior["sequence"]) + 1
    operation_id = prior["operation_id"]
    checkpoint = {
        "schema_version": 1,
        "checkpoint_id": f"{operation_id}-checkpoint-{sequence:04d}",
        "operation_id": operation_id,
        "attempt_id": prior["attempt_id"],
        "pinned_release": deepcopy_json(prior["pinned_release"]),
        "scope": deepcopy_json(prior["scope"]),
        "configuration_fingerprint": resolved.configuration_fingerprint,
        "phase": phase, "completed_phases": completed,
        "completed_units": list(prior.get("completed_units", [])),
        "remaining_work": dict(remaining), "artifacts": artifacts or [],
        "effects": effects, "verification": dict(verification),
        "blocker": None, "predecessor": checkpoint_pointer(prior),
        "sequence": sequence,
    }
    pointer = checkpoint_pointer(checkpoint)
    if terminal:
        candidate = {
            "schema_version": 1, "status": "complete",
            "current_operation": None, "serialization": None,
            "checkpoint": None,
            "last_terminal": {
                "operation_id": operation_id, "status": "complete",
                "checkpoint": pointer,
                "reason": terminal_reason,
            },
        }
    else:
        active = prior_state["current_operation"]
        candidate = {
            "schema_version": 1, "status": "running",
            "current_operation": deepcopy_json(active),
            "serialization": {
                "mode": serialization["mode"],
                "evidence": {"entrypoint": prior["scope"].get("entrypoint", "manual")},
            },
            "checkpoint": pointer, "last_terminal": None,
        }
    schemas = _schemas(installed_root)
    commit = HybridCheckpointPublisher(
        transaction,
        state_schema=schemas["operation-state.schema.json"],
        checkpoint_schema=schemas["operation-checkpoint.schema.json"],
    ).commit(
        storage=storage, checkpoint=checkpoint, operation_state=candidate,
        serialization=serialization, required_phases=required_phases,
    )
    return PreviewAdvance(commit.transaction, checkpoint)


def deepcopy_json(value: Any) -> Any:
    """Copy only JSON data and reject nonportable values."""
    return json.loads(json.dumps(value, sort_keys=True, separators=(",", ":")))


def _source_context(
    transaction: BundleTransactionStore, storage: Any,
) -> dict[str, Any]:
    catalog_index = _json(transaction.read("data/source-catalog-index.json").data, "source catalog index")
    facts_doc = _json(transaction.read("data/facts.json").data, "canonical Facts")
    facts = facts_doc.get("facts")
    if not isinstance(facts, list):
        raise HybridPreviewError("canonical Facts document lacks its array")
    source_refs: dict[str, dict[str, Any]] = {}
    for row in catalog_index.get("records", []):
        catalog = row["source_members"]["catalog"]
        source_hash = catalog["bundle_sha256"]
        source_reference = catalog["bundle_reference"]
        known = source_refs.get(source_hash)
        if known is not None and canonical_json_bytes(known) != canonical_json_bytes(source_reference):
            raise HybridPreviewError(
                "one source bundle hash is paired with conflicting physical references"
            )
        source_refs[source_hash] = source_reference
    bundles: dict[str, Any] = {}
    for source_hash, source_reference in sorted(source_refs.items()):
        source_object = storage.read(source_reference["object_id"])
        if (
            source_object is None or source_object.parent_id != source_reference["permitted_ancestor_id"]
            or source_object.mime_type != source_reference["mime_type"]
            or source_object.version != source_reference["version"]
            or source_object.data is None or sha256_bytes(source_object.data) != source_hash
        ):
            raise HybridPreviewError("source bundle exact provider readback disagrees")
        bundles[source_hash] = read_bundle(source_object.data, expected_kind="source")
    source_record_map: dict[str, dict[str, Any]] = {}
    task_source_links: dict[str, str] = {}
    guideline_selection: list[dict[str, Any]] = []
    facts_by_record: dict[str, list[dict[str, Any]]] = {}
    source_threads: dict[str, str] = {}
    for fact in facts:
        facts_by_record.setdefault(fact["record_id"], []).append(fact)
    for row in sorted(catalog_index["records"], key=lambda item: item["record_id"]):
        members = row["source_members"]
        source_hash = members["catalog"]["bundle_sha256"]
        source_reference = members["catalog"]["bundle_reference"]
        bundle = bundles.get(source_hash)
        if bundle is None:
            raise HybridPreviewError("catalog row references an unavailable source bundle")
        for key in ("catalog", "interpretation", "audit", "facts"):
            resolve_member(BundleMemberReference.from_mapping(members[key]), bundle)
        catalog = resolve_member(BundleMemberReference.from_mapping(members["catalog"]), bundle)
        if sha256_bytes(catalog) != row["record_sha256"]:
            raise HybridPreviewError("catalog record hash differs from current index")
        parsed = parse_v2_record(catalog)
        if parsed.header["record_id"] != row["record_id"]:
            raise HybridPreviewError("catalog identity differs from current index")
        conversation_id = parsed.header.get("conversation_id")
        if not isinstance(conversation_id, str) or not conversation_id:
            raise HybridPreviewError("catalog lacks its immutable conversation identity")
        source_threads[row["record_id"]] = conversation_id
        by_message = {item["message_id"]: item for item in parsed.header["messages"]}
        record_facts = sorted(facts_by_record.get(row["record_id"], []), key=lambda item: item["fact_id"])
        if sorted(row["fact_ids"]) != [item["fact_id"] for item in record_facts]:
            raise HybridPreviewError("catalog Fact inventory differs from canonical Facts")
        for fact in record_facts:
            message = by_message[fact["source_message_id"]]
            if message["received_at"] != fact["source_received_at"]:
                raise HybridPreviewError("Fact source timestamp differs from catalog")
            link = (
                "https://" + "drive.google.com/file/d/" + source_reference["object_id"]
                + "/view#" + fact["fact_id"]
            )
            source_record_map[fact["fact_id"]] = {
                "record_id": fact["record_id"],
                "source_message_id": fact["source_message_id"],
                "gmail_internal_date_ms": message["gmail_internal_date_ms"],
                "source_message_ordinal": fact["source_message_ordinal"],
                "source_content_ordinal": fact["source_content_ordinal"],
                "verified_link": link,
            }
            if fact["flags"]["is_action"] and not fact.get("task_relation"):
                task_source_links[canonical_task_id(fact["fact_id"])] = link
            if fact["flags"]["is_guideline"]:
                guideline_selection.append({
                    "fact_id": fact["fact_id"], "is_current": True,
                    "latest_source_received_date": fact["received_date"],
                    "verified_link": link,
                })
    return {
        "facts": facts, "catalog_index": catalog_index,
        "source_record_map": source_record_map,
        "task_source_links": task_source_links,
        "guideline_selection": guideline_selection,
        "source_threads": source_threads,
    }


def plan_preview_tasks(
    *, storage: Any, resolved: Any, installed_root: Path,
    snapshot: Mapping[str, Any], serialization: Mapping[str, Any],
) -> PreviewAdvance:
    """Commit canonical imports and pending semantic actions before dispatch."""
    transaction = resolved.state
    state, prior = _tip(transaction)
    if prior.get("remaining_work") != {"phase": "reconcile"}:
        raise HybridPreviewError("preview is not at the admitted reconcile boundary")
    schemas = _schemas(installed_root)
    source = _source_context(transaction, storage)
    prior_register = _json(transaction.read("data/canonical-tasks.json").data, "canonical tasks")
    register = reconcile_canonical_tasks(
        prior_register,
        source["facts"], fact_schema=schemas["fact.schema.json"],
        task_schema=schemas["task.schema.json"],
        register_schema=schemas["canonical-tasks.schema.json"],
    )
    provider_state = _json(
        transaction.read(resolved.task_binding["provider_state_path"]).data,
        "task provider state",
    )
    plan: AgentTaskPlan = plan_task_sync(
        register, provider_state, snapshot,
        task_schema=schemas["task.schema.json"],
        register_schema=schemas["canonical-tasks.schema.json"],
        provider_state_schema=schemas["provider-state.schema.json"],
        snapshot_schema=schemas["task-adapter-snapshot.schema.json"],
        action_schema=schemas["task-adapter-action.schema.json"],
    )
    derived = build_derived_knowledge(
        source["facts"], fact_schema=schemas["fact.schema.json"],
        task_schema=schemas["task.schema.json"],
    )
    try:
        delta = _json(transaction.read("state/pending-run-delta.json").data, "pending run delta")
    except HybridPreviewError:
        delta = {"schema_version": 1, "facts": [], "tasks": []}
    delta = merge_parent_task_delta(delta, prior_register, plan.canonical_tasks)
    transaction = (
        transaction
        .stage("data/canonical-tasks.json", canonical_json_bytes(plan.canonical_tasks))
        .stage(resolved.task_binding["provider_state_path"], canonical_json_bytes(plan.provider_state))
        .stage("data/guidelines.json", canonical_json_bytes({"schema_version": 1, "guidelines": derived["guidelines"]}))
        .stage("data/rolling-updates.json", canonical_json_bytes({"schema_version": 1, "rolling_updates": derived["rolling_updates"]}))
        .stage("state/pending-run-delta.json", canonical_json_bytes(delta), role="reconciliation_delta", media_type="application/json")
    )
    remaining = {"phase": "task_sync"}
    if plan.actions:
        remaining["pending_action_count"] = len(plan.actions)
    effects = [{
        "effect_id": item["effect_id"], "kind": item["kind"],
        "outcome": item["outcome"], "verification": {},
    } for item in plan.actions]
    advanced = _publish(
        transaction=transaction, storage=storage, prior_state=state, prior=prior,
        resolved=resolved, installed_root=installed_root, serialization=serialization,
        phase="reconcile", completed=["preflight", "discover", "catalog", "reconcile"],
        remaining=remaining,
        verification={
            "verified": True, "phase_complete": True,
            "canonical_task_count": len(plan.canonical_tasks["tasks"]),
            "pending_action_count": len(plan.actions),
            "review_case_count": len(plan.review_cases),
            "provider_snapshot_sha256": plan.provider_state["last_snapshot_sha256"],
        }, effects=effects,
    )
    return advanced


def authorize_preview_action(
    *, storage: Any, resolved: Any, installed_root: Path,
    serialization: Mapping[str, Any],
) -> PreviewAdvance:
    """Make one action authorization current before exposing it to the agent."""
    transaction = resolved.state
    state, prior = _tip(transaction)
    schemas = _schemas(installed_root)
    provider_state = _json(transaction.read(resolved.task_binding["provider_state_path"]).data, "task provider state")
    authorized_state, action = authorize_next_action(
        provider_state,
        action_schema=schemas["task-adapter-action.schema.json"],
        provider_state_schema=schemas["provider-state.schema.json"],
    )
    transaction = transaction.stage(
        resolved.task_binding["provider_state_path"], canonical_json_bytes(authorized_state),
    )
    advanced = _publish(
        transaction=transaction, storage=storage, prior_state=state, prior=prior,
        resolved=resolved, installed_root=installed_root, serialization=serialization,
        phase="task_sync", completed=["preflight", "discover", "catalog", "reconcile"],
        remaining={"phase": "task_sync", "pending_action_count": len(authorized_state["pending_actions"])},
        verification={
            "verified": True, "phase_complete": False,
            "pre_dispatch": True, "effect_id": action["effect_id"],
            "dispatch_attempt": action["dispatch_attempt"],
        },
        effects=[{
            "effect_id": action["effect_id"], "kind": action["kind"],
            "outcome": "unknown", "verification": action["verification"],
        }],
    )
    return PreviewAdvance(advanced.transaction, advanced.checkpoint, action)


def confirm_preview_action(
    *, storage: Any, resolved: Any, installed_root: Path,
    result: Mapping[str, Any], serialization: Mapping[str, Any],
) -> PreviewAdvance:
    """Validate agent readback and commit confirmation without another effect."""
    transaction = resolved.state
    state, prior = _tip(transaction)
    schemas = _schemas(installed_root)
    register = _json(transaction.read("data/canonical-tasks.json").data, "canonical tasks")
    provider_state = _json(transaction.read(resolved.task_binding["provider_state_path"]).data, "task provider state")
    confirmation = confirm_action(
        register, provider_state, result,
        register_schema=schemas["canonical-tasks.schema.json"],
        provider_state_schema=schemas["provider-state.schema.json"],
        action_schema=schemas["task-adapter-action.schema.json"],
        result_schema=schemas["task-adapter-result.schema.json"],
    )
    transaction = (
        transaction
        .stage("data/canonical-tasks.json", canonical_json_bytes(confirmation.canonical_tasks))
        .stage(resolved.task_binding["provider_state_path"], canonical_json_bytes(confirmation.provider_state))
    )
    remaining = len(confirmation.remaining_actions)
    outcome = result["outcome"]
    complete = outcome == "confirmed" and remaining == 0
    advanced = _publish(
        transaction=transaction, storage=storage, prior_state=state, prior=prior,
        resolved=resolved, installed_root=installed_root, serialization=serialization,
        phase="task_sync",
        completed=["preflight", "discover", "catalog", "reconcile"] + (["task_sync"] if complete else []),
        remaining={"phase": "brief_delivery"} if complete else {
            "phase": "task_sync", "pending_action_count": remaining,
        },
        verification={
            "verified": outcome == "confirmed", "phase_complete": complete,
            "effect_id": result["effect_id"], "outcome": outcome,
            "remaining_action_count": remaining,
        },
        effects=[{
            "effect_id": result["effect_id"], "kind": prior["effects"][0]["kind"],
            "outcome": outcome, "verification": dict(result.get("evidence", {})),
        }],
    )
    return advanced


def render_current_brief(
    *, storage: Any, resolved: Any, installed_root: Path, local_day: str,
) -> CurrentBrief:
    """Render current canonical state through the one installed brief recipe."""
    transaction = resolved.state
    schemas = _schemas(installed_root)
    source = _source_context(transaction, storage)
    register = _json(transaction.read("data/canonical-tasks.json").data, "canonical tasks")
    provider_state = _json(transaction.read(resolved.task_binding["provider_state_path"]).data, "task provider state")
    if provider_state.get("pending_actions"):
        raise HybridPreviewError("preview cannot render with pending task actions")
    brief_tasks = unresolved_finite_task_selection(
        register, task_source_links=source["task_source_links"],
    )
    entities = [{
        "entity_id": item["entity_id"], "display_name": item["display_name"],
        "kind": "household" if item["type"] == "shared" else "child",
    } for item in sorted(resolved.household["entities"], key=lambda item: item["sort_order"])]
    entity_ids = {item["entity_id"] for item in entities}
    shared = resolved.household["grouping"]["shared_group_id"]
    scopes = {fact["entity_scope"] for fact in source["facts"]} | {
        task["entity_scope"] for task in unresolved_tasks(register)
    }
    scope_to_entity = {scope: scope if scope in entity_ids else shared for scope in scopes}
    brief_input = build_brief_input(
        run_local_date=local_day, timezone=resolved.household["timezone"],
        entities=entities, scope_to_entity=scope_to_entity,
        facts=source["facts"], source_record_map=source["source_record_map"],
        current_guideline_selection=source["guideline_selection"],
        unresolved_task_view=brief_tasks,
        task_source_links=source["task_source_links"],
        template=resolved.brief_template,
        input_hashes={
            "catalog_index": sha256_bytes(transaction.read("data/source-catalog-index.json").data),
            "canonical_tasks": sha256_bytes(transaction.read("data/canonical-tasks.json").data),
        },
    )
    rendered = render_brief(brief_input, schemas["brief-input.schema.json"])
    return CurrentBrief(brief_input, rendered["html"], rendered["text"], source)


def finish_preview(
    *, storage: Any, resolved: Any, installed_root: Path,
    local_day: str, output_identity: str, serialization: Mapping[str, Any],
) -> PreviewFinish:
    """Render/store an unsent brief, advance the source cursor last, and finish."""
    transaction = resolved.state
    state, prior = _tip(transaction)
    if prior.get("remaining_work") != {"phase": "brief_delivery"} or "task_sync" not in prior.get("completed_phases", []):
        raise HybridPreviewError("preview is not ready for render")
    current = render_current_brief(
        storage=storage, resolved=resolved, installed_root=installed_root,
        local_day=local_day,
    )
    brief_input = current.brief_input
    rendered = {"html": current.html, "text": current.text}
    input_bytes = canonical_json_bytes(brief_input)
    output = publish_hybrid_content_bundle(
        storage, recovery=transaction.working.recovery,
        bundle_kind="output", identity=output_identity,
        entries={
            "brief/input.json": BundleEntry(input_bytes, "brief_input", "application/json", "brief-input.schema.json"),
            "brief/rendered.html": BundleEntry(rendered["html"], "brief_html", "text/html"),
            "brief/rendered.txt": BundleEntry(rendered["text"], "brief_text", "text/plain"),
        },
    )
    output_refs = {
        path: {
            "bundle_reference": dict(output["bundle_reference"]),
            "bundle_sha256": output["bundle_sha256"], "entry_path": path,
            "entry_sha256": sha256_bytes(data), "byte_length": len(data),
        }
        for path, data in {
            "brief/input.json": input_bytes,
            "brief/rendered.html": rendered["html"],
            "brief/rendered.txt": rendered["text"],
        }.items()
    }
    operation_id = prior["operation_id"]
    first = _json(
        transaction.read(f"state/operation-checkpoints/{operation_id}-checkpoint-0000.json").data,
        "catalog checkpoint",
    )
    cursor = first["verification"]["phase_output"]["proposed_source_cursor"]
    evidence = {
        "schema_version": 1, "operation_id": operation_id,
        "attempt_id": prior["attempt_id"], "outcome": "PREVIEW_READY",
        "delivery_reserved": False, "delivery_sent": False,
        "eligible_cursor": cursor, "brief": output_refs,
        "canonical_task_count": len(register["tasks"]),
        "provider_binding_count": len(provider_state["bindings"]),
    }
    transaction = (
        transaction
        .stage("state/source-checkpoint.json", canonical_json_bytes({"schema_version": 1, "eligible_cursor": cursor}))
        .stage("state/final-run-checkpoint.json", canonical_json_bytes(evidence))
    )
    advanced = _publish(
        transaction=transaction, storage=storage, prior_state=state, prior=prior,
        resolved=resolved, installed_root=installed_root, serialization=serialization,
        phase="commit",
        completed=["preflight", "discover", "catalog", "reconcile", "task_sync", "brief_delivery", "commit"],
        remaining={},
        verification={
            "verified": True, "phase_complete": True,
            "outcome": "PREVIEW_READY", "delivery_reserved": False,
            "delivery_sent": False, "eligible_cursor_advanced": True,
            "brief_input_sha256": sha256_bytes(input_bytes),
            "brief_html_sha256": sha256_bytes(rendered["html"]),
            "brief_text_sha256": sha256_bytes(rendered["text"]),
        }, effects=[], terminal=True,
        artifacts=[{
            "kind": "output_bundle", "identity": output_identity,
            "reference": dict(output["bundle_reference"]),
            "sha256": output["bundle_sha256"],
        }],
        required_phases=("preflight", "discover", "catalog", "reconcile", "task_sync", "brief_delivery", "commit"),
    )
    return PreviewFinish(advanced.transaction, advanced.checkpoint, evidence, output)
