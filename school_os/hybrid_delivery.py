"""Bundle-native ordered brief, audio, and exact Gmail delivery."""
from __future__ import annotations

import base64
import binascii
import json
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from .audio import build_audio_manifest
from .bundles import BundleEntry, BundleMemberReference, member_reference, read_bundle, resolve_member
from .brief import delivery_key
from .contracts import canonical_json_bytes, sha256_bytes
from .connected_storage import ConnectedStorageError
from .delivery import (
    ExactAudioAttachment, ExactDeliveryRequest, deliver_exact,
    record_reserved_audio, reserve_delivery,
)
from .hybrid_preview import (
    _publish, _source_context, _tip, render_current_brief,
)
from .install import publish_hybrid_content_bundle


class HybridDeliveryError(ValueError):
    """Raised when the ordered final delivery chain cannot advance safely."""


@dataclass(frozen=True)
class HybridDeliveryAdvance:
    transaction: Any
    checkpoint: dict[str, Any]
    delivery_key: str
    audio_manifest: bytes | None = None
    audio_call_required: bool = False
    result: dict[str, Any] | None = None


def _json(transaction: Any, path: str, label: str) -> dict[str, Any]:
    try:
        data = transaction.read(path).data
        value = json.loads(data.decode("utf-8"))
    except (ConnectedStorageError, KeyError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HybridDeliveryError(f"{label} is unavailable or invalid") from exc
    if not isinstance(value, dict) or canonical_json_bytes(value) != data:
        raise HybridDeliveryError(f"{label} is not canonical JSON")
    return value


def _delivery_state(transaction: Any) -> dict[str, Any]:
    value = _json(transaction, "state/delivery-state.json", "delivery state")
    if (
        set(value) != {"schema_version", "deliveries", "effects"}
        or value.get("schema_version") != 1
        or not isinstance(value["deliveries"], dict)
        or not isinstance(value["effects"], dict)
    ):
        raise HybridDeliveryError("delivery state has an unsupported shape")
    return value


def _run_path(operation_id: str) -> str:
    if not isinstance(operation_id, str) or not operation_id or "/" in operation_id or ".." in operation_id:
        raise HybridDeliveryError("delivery operation identity is unsafe")
    return f"state/runs/{operation_id}/delivery.json"


def _entry_reference(output: Mapping[str, Any], path: str) -> dict[str, Any]:
    return member_reference(output["bundle_reference"], output["bundle"], path).as_mapping()


def _load_entry(storage: Any, mapping: Mapping[str, Any]) -> bytes:
    reference = BundleMemberReference.from_mapping(mapping)
    physical = reference.bundle_reference
    observed = storage.read(physical["object_id"])
    if (
        observed is None or observed.data is None
        or observed.parent_id != physical["permitted_ancestor_id"]
        or observed.mime_type != physical["mime_type"]
        or observed.version != physical["version"]
        or sha256_bytes(observed.data) != reference.bundle_sha256
    ):
        raise HybridDeliveryError("delivery output bundle provider readback disagrees")
    bundle = read_bundle(observed.data, expected_kind="output")
    return resolve_member(reference, bundle)


def _request(storage: Any, record: Mapping[str, Any]) -> ExactDeliveryRequest:
    required = {
        "schema_version", "operation_id", "entrypoint", "key", "variant",
        "subject", "to", "cc", "bcc", "brief", "audio",
    }
    if not isinstance(record, Mapping) or set(record) != required or record.get("schema_version") != 1:
        raise HybridDeliveryError("delivery run record has an unsupported shape")
    brief = record["brief"]
    if not isinstance(brief, Mapping) or set(brief) != {"input", "html", "text"}:
        raise HybridDeliveryError("delivery run brief references are malformed")
    audio = None
    if record["audio"] is not None:
        value = record["audio"]
        if not isinstance(value, Mapping) or set(value) != {"filename", "reference"}:
            raise HybridDeliveryError("delivery run audio reference is malformed")
        audio = ExactAudioAttachment.build(
            filename=value["filename"], data=_load_entry(storage, value["reference"]),
        )
    return ExactDeliveryRequest.build(
        key=record["key"], variant=record["variant"], to=record["to"],
        cc=record["cc"], bcc=record["bcc"], subject=record["subject"],
        text=_load_entry(storage, brief["text"]),
        html=_load_entry(storage, brief["html"]), audio=audio,
    )


def prepare_hybrid_delivery(
    *, storage: Any, resolved: Any, installed_root: Path, local_day: str,
    output_identity: str, serialization: Mapping[str, Any],
) -> HybridDeliveryAdvance:
    """Render, validate, store, and durably reserve before any audio call."""
    transaction = resolved.state
    state, prior = _tip(transaction)
    if (
        prior.get("scope", {}).get("operation_mode") != "delivery"
        or prior.get("remaining_work") != {"phase": "brief_delivery"}
        or "task_sync" not in prior.get("completed_phases", [])
    ):
        raise HybridDeliveryError("operation is not ready for final delivery reservation")
    current = render_current_brief(
        storage=storage, resolved=resolved, installed_root=installed_root,
        local_day=local_day,
    )
    input_bytes = canonical_json_bytes(current.brief_input)
    output = publish_hybrid_content_bundle(
        storage, recovery=transaction.working.recovery,
        bundle_kind="output", identity=output_identity,
        entries={
            "brief/input.json": BundleEntry(input_bytes, "brief_input", "application/json", "brief-input.schema.json"),
            "brief/rendered.html": BundleEntry(current.html, "brief_html", "text/html"),
            "brief/rendered.txt": BundleEntry(current.text, "brief_text", "text/plain"),
        },
    )
    key = delivery_key(
        resolved.instance["instance_id"], "daily-run", local_day,
        resolved.delivery["variant"],
    )
    request = ExactDeliveryRequest.build(
        key=key, variant=resolved.delivery["variant"], to=resolved.delivery["to"],
        cc=resolved.delivery["cc"], bcc=resolved.delivery["bcc"],
        subject=f'{resolved.delivery["subject_prefix"]} [School-OS:{key}]',
        text=current.text, html=current.html,
    )
    ledger = _delivery_state(transaction)
    working_delivery = ledger["deliveries"].get(key)

    def read_ledger() -> Mapping[str, Any] | None:
        return working_delivery

    def persist_ledger(value: Mapping[str, Any]) -> None:
        nonlocal working_delivery
        working_delivery = dict(value)

    reserve_delivery(
        request, audio_planned=resolved.policies["audio"]["enabled"],
        read_ledger=read_ledger, persist_ledger=persist_ledger,
    )
    ledger = {**ledger, "deliveries": {**ledger["deliveries"], key: working_delivery}}
    operation_id = prior["operation_id"]
    record = {
        "schema_version": 1, "operation_id": operation_id,
        "entrypoint": prior["scope"]["entrypoint"], "key": key,
        "variant": resolved.delivery["variant"], "subject": request.subject,
        "to": list(request.to), "cc": list(request.cc), "bcc": list(request.bcc),
        "brief": {
            "input": _entry_reference(output, "brief/input.json"),
            "html": _entry_reference(output, "brief/rendered.html"),
            "text": _entry_reference(output, "brief/rendered.txt"),
        },
        "audio": None,
    }
    transaction = (
        transaction
        .stage("state/delivery-state.json", canonical_json_bytes(ledger))
        .stage(_run_path(operation_id), canonical_json_bytes(record), role="delivery_run", media_type="application/json")
    )
    advanced = _publish(
        transaction=transaction, storage=storage, prior_state=state, prior=prior,
        resolved=resolved, installed_root=installed_root, serialization=serialization,
        phase="brief_delivery", completed=list(prior["completed_phases"]),
        remaining={"phase": "audio_manifest" if resolved.policies["audio"]["enabled"] else "send"},
        verification={
            "verified": True, "phase_complete": False, "delivery_reserved": True,
            "delivery_sent": False, "brief_input_sha256": sha256_bytes(input_bytes),
            "brief_html_sha256": sha256_bytes(current.html),
            "brief_text_sha256": sha256_bytes(current.text),
        }, effects=[], artifacts=[{
            "kind": "output_bundle", "identity": output_identity,
            "reference": dict(output["bundle_reference"]), "sha256": output["bundle_sha256"],
        }],
    )
    return HybridDeliveryAdvance(advanced.transaction, advanced.checkpoint, key)


def _window(resolved: Any) -> dict[str, str]:
    start = resolved.source_scope.get("seed_after_inclusive_ms")
    end = resolved.source_scope.get("seed_before_exclusive_ms")
    if not isinstance(start, int) or not isinstance(end, int):
        raise HybridDeliveryError("audio requires exact frozen source bounds")
    zone = ZoneInfo(resolved.household["timezone"])
    return {
        "start": datetime.fromtimestamp(start / 1000, timezone.utc).astimezone(zone).isoformat(),
        "end": datetime.fromtimestamp(end / 1000, timezone.utc).astimezone(zone).isoformat(),
    }


def authorize_hybrid_audio(
    *, storage: Any, resolved: Any, installed_root: Path, local_day: str,
    configuration: Mapping[str, Any], serialization: Mapping[str, Any],
) -> HybridDeliveryAdvance:
    """Persist exact delta/manifest and one unknown audio intent before dispatch."""
    transaction = resolved.state
    state, prior = _tip(transaction)
    if prior.get("remaining_work") != {"phase": "audio_manifest"}:
        raise HybridDeliveryError("delivery is not ready to authorize audio")
    operation_id = prior["operation_id"]
    record = _json(transaction, _run_path(operation_id), "delivery run")
    delta = _json(transaction, "state/pending-run-delta.json", "pending run delta")
    facts = _json(transaction, "data/facts.json", "canonical Facts")
    tasks = _json(transaction, "data/canonical-tasks.json", "canonical tasks")
    source = _source_context(transaction, storage)
    manifest = build_audio_manifest(
        run_date=local_day, window=_window(resolved), delta=delta,
        facts=facts["facts"], canonical_tasks=tasks,
        source_threads=source["source_threads"], configuration=configuration,
    )
    manifest_bytes = canonical_json_bytes(manifest)
    ledger = _delivery_state(transaction)
    request = _request(storage, record)
    current = ledger["deliveries"].get(record["key"])
    if not manifest["records"]:
        def persist(value: Mapping[str, Any]) -> None:
            nonlocal current
            current = dict(value)
        record_reserved_audio(
            request, outcome="skipped_empty",
            read_ledger=lambda: current, persist_ledger=persist,
        )
        ledger = {**ledger, "deliveries": {**ledger["deliveries"], record["key"]: current}}
        transaction = (
            transaction
            .stage("state/delivery-state.json", canonical_json_bytes(ledger))
            .stage(
                f"state/runs/{operation_id}/current-delta.json",
                canonical_json_bytes(delta), role="reconciliation_delta",
                media_type="application/json",
            )
            .stage(
                f"state/runs/{operation_id}/audio-manifest.json",
                manifest_bytes, role="audio_manifest", media_type="application/json",
            )
        )
        remaining = {"phase": "send"}
        effects: list[dict[str, Any]] = []
        required = False
    else:
        effect_id = "audio-effect-" + sha256_bytes(canonical_json_bytes({
            "operation_id": operation_id, "manifest_sha256": sha256_bytes(manifest_bytes),
        }))
        attempt = {
            "schema_version": 1, "effect_id": effect_id,
            "manifest_sha256": sha256_bytes(manifest_bytes), "outcome": "unknown",
        }
        transaction = transaction.stage(
            f"state/runs/{operation_id}/current-delta.json", canonical_json_bytes(delta),
            role="reconciliation_delta", media_type="application/json",
        ).stage(
            f"state/runs/{operation_id}/audio-manifest.json", manifest_bytes,
            role="audio_manifest", media_type="application/json",
        ).stage(
            f"state/runs/{operation_id}/audio-attempt.json", canonical_json_bytes(attempt),
            role="audio_attempt", media_type="application/json",
        )
        remaining = {"phase": "audio_result"}
        effects = [{"effect_id": effect_id, "kind": "audio.generate", "outcome": "unknown", "verification": {"manifest_sha256": sha256_bytes(manifest_bytes)}}]
        required = True
    advanced = _publish(
        transaction=transaction, storage=storage, prior_state=state, prior=prior,
        resolved=resolved, installed_root=installed_root, serialization=serialization,
        phase="brief_delivery", completed=list(prior["completed_phases"]),
        remaining=remaining,
        verification={"verified": True, "phase_complete": False, "delta_sha256": sha256_bytes(canonical_json_bytes(delta)), "audio_manifest_sha256": sha256_bytes(manifest_bytes), "audio_call_required": required},
        effects=effects,
    )
    return HybridDeliveryAdvance(
        advanced.transaction, advanced.checkpoint, record["key"],
        manifest_bytes, required,
    )


def record_hybrid_audio(
    *, storage: Any, resolved: Any, installed_root: Path, outcome: str,
    serialization: Mapping[str, Any], audio_identity: str | None = None,
    filename: str | None = None, audio_bytes: bytes | None = None,
) -> HybridDeliveryAdvance:
    """Record the one audio outcome; verified bytes become an immutable output bundle."""
    transaction = resolved.state
    state, prior = _tip(transaction)
    if prior.get("remaining_work") != {"phase": "audio_result"}:
        raise HybridDeliveryError("delivery has no authorized unresolved audio attempt")
    operation_id = prior["operation_id"]
    record = _json(transaction, _run_path(operation_id), "delivery run")
    attempt_path = f"state/runs/{operation_id}/audio-attempt.json"
    attempt = _json(transaction, attempt_path, "audio attempt")
    if attempt.get("outcome") != "unknown":
        raise HybridDeliveryError("audio attempt already has a terminal outcome")
    ledger = _delivery_state(transaction)
    attachment = None
    artifact = None
    if outcome == "verified":
        if not all(isinstance(value, str) and value for value in (audio_identity, filename)) or not isinstance(audio_bytes, bytes):
            raise HybridDeliveryError("verified audio requires exact identity, filename, and bytes")
        attachment = ExactAudioAttachment.build(filename=filename, data=audio_bytes)
        output = publish_hybrid_content_bundle(
            storage, recovery=transaction.working.recovery,
            bundle_kind="output", identity=audio_identity,
            entries={"audio/brief.mp3": BundleEntry(audio_bytes, "brief_audio", "audio/mpeg")},
        )
        record = {**record, "audio": {"filename": filename, "reference": _entry_reference(output, "audio/brief.mp3")}}
        artifact = {"kind": "output_bundle", "identity": audio_identity, "reference": dict(output["bundle_reference"]), "sha256": output["bundle_sha256"]}
    elif outcome not in {"failed", "unavailable"} or any(value is not None for value in (audio_identity, filename, audio_bytes)):
        raise HybridDeliveryError("audio terminal outcome is malformed")
    request = ExactDeliveryRequest.build(
        key=record["key"], variant=record["variant"], to=record["to"], cc=record["cc"], bcc=record["bcc"],
        subject=record["subject"], text=_load_entry(storage, record["brief"]["text"]), html=_load_entry(storage, record["brief"]["html"]), audio=attachment,
    )
    current = ledger["deliveries"].get(record["key"])
    def persist(value: Mapping[str, Any]) -> None:
        nonlocal current
        current = dict(value)
    record_reserved_audio(
        request, outcome=outcome, read_ledger=lambda: current, persist_ledger=persist,
    )
    ledger = {**ledger, "deliveries": {**ledger["deliveries"], record["key"]: current}}
    attempt = {**attempt, "outcome": outcome}
    if attachment is not None:
        attempt.update(attachment.intent())
    transaction = (
        transaction.stage("state/delivery-state.json", canonical_json_bytes(ledger))
        .stage(_run_path(operation_id), canonical_json_bytes(record))
        .stage(attempt_path, canonical_json_bytes(attempt))
    )
    advanced = _publish(
        transaction=transaction, storage=storage, prior_state=state, prior=prior,
        resolved=resolved, installed_root=installed_root, serialization=serialization,
        phase="brief_delivery", completed=list(prior["completed_phases"]),
        remaining={"phase": "send"},
        verification={"verified": True, "phase_complete": False, "audio_outcome": outcome, "audio_sha256": None if attachment is None else sha256_bytes(attachment.data)},
        effects=[{"effect_id": attempt["effect_id"], "kind": "audio.generate", "outcome": "confirmed", "verification": {"audio_outcome": outcome}}],
        artifacts=[] if artifact is None else [artifact],
    )
    return HybridDeliveryAdvance(advanced.transaction, advanced.checkpoint, record["key"])


def deliver_hybrid_email(
    *, storage: Any, gmail: Any, resolved: Any, installed_root: Path,
    serialization: Mapping[str, Any],
) -> HybridDeliveryAdvance:
    """Persist exact send boundaries, verify Sent, advance cursor, and commit."""
    transaction = resolved.state
    state, prior = _tip(transaction)
    if prior.get("remaining_work") != {"phase": "send"}:
        raise HybridDeliveryError("delivery is not ready for the email effect")
    operation_id = prior["operation_id"]
    record = _json(transaction, _run_path(operation_id), "delivery run")
    request = _request(storage, record)
    delivery_state = _delivery_state(transaction)
    key = record["key"]

    def persist(section: str, value: Mapping[str, Any]) -> None:
        nonlocal transaction, delivery_state
        delivery_state = {**delivery_state, section: {**delivery_state[section], key: dict(value)}}
        transaction = transaction.stage(
            "state/delivery-state.json", canonical_json_bytes(delivery_state),
        ).publish(storage, serialization)
        delivery_state = _delivery_state(transaction)

    def sent(identity: str) -> dict[str, Any]:
        raw = gmail.read(identity, "raw")
        if not isinstance(raw, Mapping) or raw.get("id") != identity or not isinstance(raw.get("raw"), str):
            raise HybridDeliveryError("Gmail Sent readback is malformed")
        try:
            data = base64.b64decode(raw["raw"] + "=" * (-len(raw["raw"]) % 4), altchars=b"-_", validate=True)
        except (binascii.Error, ValueError) as exc:
            raise HybridDeliveryError("Gmail Sent raw MIME is invalid") from exc
        return {"id": identity, "raw": data, "label_ids": raw.get("label_ids")}

    def search(token: str | None):
        args = {"query": f'in:sent "[School-OS:{key}]"', "label_ids": ["SENT"], "max_results": 100}
        if token is not None:
            args["next_page_token"] = token
        page = gmail.search_ids(**args)
        if not isinstance(page, Mapping) or not isinstance(page.get("message_ids"), list):
            raise HybridDeliveryError("Gmail Sent search is malformed")
        return tuple({"id": identity} for identity in page["message_ids"]), page.get("next_page_token")

    result = deliver_exact(
        request,
        read_ledger=lambda: delivery_state["deliveries"].get(key),
        persist_ledger=lambda value: persist("deliveries", value),
        read_effect_checkpoint=lambda: delivery_state["effects"].get(key),
        persist_effect_checkpoint=lambda value: persist("effects", value),
        send=lambda exact: gmail.send(exact.gmail_args()), read_sent=sent,
        search_sent=search,
    )
    # Ledger callbacks may have advanced CURRENT several times. Continue from
    # their exact current transaction, while the operation checkpoint remains
    # the prior safe boundary.
    cursor_checkpoint = _json(
        transaction, f"state/operation-checkpoints/{operation_id}-checkpoint-0000.json",
        "catalog checkpoint",
    )
    cursor = cursor_checkpoint["verification"]["phase_output"]["proposed_source_cursor"]
    audio_status = result["ledger"].get("reservation", {}).get("audio", {}).get("status")
    final = {
        "schema_version": 1, "operation_id": operation_id,
        "attempt_id": prior["attempt_id"], "outcome": "DELIVERY_CONFIRMED",
        "delivery_key": key, "provider_message_id": result["provider_message_id"],
        "audio_outcome": audio_status, "eligible_cursor": cursor,
    }
    transaction = (
        transaction
        .stage("state/source-checkpoint.json", canonical_json_bytes({"schema_version": 1, "eligible_cursor": cursor}))
        .stage("state/final-run-checkpoint.json", canonical_json_bytes(final))
        .stage("state/pending-run-delta.json", canonical_json_bytes({"schema_version": 1, "facts": [], "tasks": []}))
    )
    advanced = _publish(
        transaction=transaction, storage=storage, prior_state=state, prior=prior,
        resolved=resolved, installed_root=installed_root, serialization=serialization,
        phase="commit",
        completed=[*prior["completed_phases"], "brief_delivery", "commit"],
        remaining={},
        verification={"verified": True, "phase_complete": True, "outcome": "DELIVERY_CONFIRMED", "eligible_cursor_advanced": True, "provider_message_id": result["provider_message_id"], "audio_outcome": audio_status},
        effects=[{"effect_id": key, "kind": "mail.send", "outcome": "confirmed", "verification": {"provider_message_id": result["provider_message_id"]}}],
        terminal=True,
        required_phases=("preflight", "discover", "catalog", "reconcile", "task_sync", "brief_delivery", "commit"),
        terminal_reason="verified agent-operated exact delivery complete",
    )
    return HybridDeliveryAdvance(
        advanced.transaction, advanced.checkpoint, key, result=result,
    )
