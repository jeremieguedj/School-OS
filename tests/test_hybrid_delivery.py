from __future__ import annotations

import base64
import json
import unittest
from email.message import EmailMessage
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from school_os.bundles import BundleEntry
from school_os.connected_storage import BundleTransactionStore
from school_os.contracts import canonical_json_bytes, sha256_bytes
from school_os.delivery import DeliveryError, ExactDeliveryRequest
from school_os.hybrid_delivery import (
    _request, authorize_hybrid_audio, deliver_hybrid_email,
    prepare_hybrid_delivery, record_hybrid_audio,
)
from school_os.hybrid_preview import CurrentBrief, HybridPreviewError, _source_context
from school_os.install import install_hybrid_generation, recover_hybrid_generation
from school_os.operations import checkpoint_pointer
from tests.test_bundles import HybridStorage, package_fixture


ROOT = Path(__file__).resolve().parents[1]


def raw_message(request: ExactDeliveryRequest) -> bytes:
    message = EmailMessage()
    message["To"] = ", ".join(request.to)
    message["Subject"] = request.subject
    message.set_content(request.text.decode(), cte="8bit")
    message.add_alternative(request.html.decode(), subtype="html", cte="8bit")
    if request.audio:
        message.add_attachment(
            request.audio.data, maintype="audio", subtype="mpeg",
            filename=request.audio.filename,
        )
    return message.as_bytes()


class Gmail:
    def __init__(self, raw: bytes):
        self.raw = raw
        self.sends = 0

    def send(self, _args):
        self.sends += 1
        return {"id": "message-1"}

    def read(self, identity, format):
        assert identity == "message-1" and format == "raw"
        return {
            "id": identity, "label_ids": ["SENT"],
            "raw": base64.urlsafe_b64encode(self.raw).decode().rstrip("="),
        }

    def search_ids(self, **_args):
        return {"message_ids": ["message-1"], "next_page_token": None}


class LostResponseGmail(Gmail):
    def send(self, _args):
        self.sends += 1
        raise OSError("synthetic response loss after acceptance")


class HybridDeliveryTests(unittest.TestCase):
    serialization = {
        "mode": "attended_single_writer",
        "evidence": {
            "actor_id": "test", "attempt_id": "test",
            "scheduler_inactive": True, "competing_mutators_excluded": True,
            "observed_at": "2026-09-10T00:00:00Z",
        },
    }

    def setup_run(self):
        checkpoint = {
            "schema_version": 1, "checkpoint_id": "op-checkpoint-0000",
            "operation_id": "op", "attempt_id": "attempt",
            "pinned_release": {"version": "1.2.3-alpha.1", "source_commit": "1" * 40},
            "scope": {"entrypoint": "manual", "operation_mode": "delivery"},
            "configuration_fingerprint": "c" * 64, "phase": "task_sync",
            "completed_phases": ["preflight", "discover", "catalog", "reconcile", "task_sync"],
            "completed_units": ["thread-1"], "remaining_work": {"phase": "brief_delivery"},
            "artifacts": [], "effects": [],
            "verification": {"phase_output": {"proposed_source_cursor": {"cursor": "one"}}},
            "blocker": None, "predecessor": None, "sequence": 0,
        }
        operation_state = {
            "schema_version": 1, "status": "running",
            "current_operation": {"operation_id": "op", "attempt_id": "attempt"},
            "serialization": {"mode": "attended_single_writer", "evidence": {"entrypoint": "manual"}},
            "checkpoint": checkpoint_pointer(checkpoint), "last_terminal": None,
        }
        entries = {
            "state/operation-state.json": BundleEntry(canonical_json_bytes(operation_state), "operation_state", "application/json"),
            "state/operation-checkpoints/op-checkpoint-0000.json": BundleEntry(canonical_json_bytes(checkpoint), "operation_checkpoint", "application/json"),
            "state/delivery-state.json": BundleEntry(canonical_json_bytes({"schema_version": 1, "deliveries": {}, "effects": {}}), "delivery_state", "application/json"),
            "state/source-checkpoint.json": BundleEntry(canonical_json_bytes({"schema_version": 1, "eligible_cursor": None}), "source_checkpoint", "application/json"),
            "state/final-run-checkpoint.json": BundleEntry(canonical_json_bytes({"schema_version": 1, "last_run": None}), "final_run_checkpoint", "application/json"),
            "state/pending-run-delta.json": BundleEntry(canonical_json_bytes({"schema_version": 1, "facts": [{"fact_id": "fact-1", "delta_kind": "new"}], "tasks": []}), "reconciliation_delta", "application/json"),
            "data/facts.json": BundleEntry(canonical_json_bytes({"schema_version": 1, "facts": [{"fact_id": "fact-1", "record_id": "record-1", "entity_scope": "child-a", "text": "Exact update.", "flags": {"is_update": True, "is_durable": False, "is_guideline": False, "is_action": False}}]}), "canonical_facts", "application/json"),
            "data/canonical-tasks.json": BundleEntry(canonical_json_bytes({"schema_version": 1, "tasks": []}), "canonical_tasks", "application/json"),
        }
        archive, package = package_fixture()
        storage = HybridStorage()
        recovery = install_hybrid_generation(
            storage,
            root_reference={"object_id": "root", "kind": "folder", "permitted_ancestor_id": "root", "mime_type": "application/vnd.google-apps.folder", "version": "root-v1"},
            package=package, package_bytes=archive,
            settings_bytes=b"schema_version: 1\n", instance_id="instance",
            state_entries=entries, configuration_fingerprint="c" * 64,
            runtime={"implementation": "CPython", "python_version": "3.12.14", "dependency_fingerprint": "d" * 64},
        )
        transaction = BundleTransactionStore.from_recovery(recovery)
        resolved = SimpleNamespace(
            state=transaction, instance={"instance_id": "instance"},
            delivery={"variant": "manual-test", "to": ["parent@example.invalid"], "cc": [], "bcc": [], "subject_prefix": "School"},
            policies={"audio": {"enabled": True}},
            source_scope={"seed_after_inclusive_ms": 0, "seed_before_exclusive_ms": 86_400_000},
            household={"timezone": "UTC"}, configuration_fingerprint="c" * 64,
        )
        return storage, resolved

    def test_full_ordered_bundle_delivery_with_exact_audio_and_cursor_last(self):
        storage, resolved = self.setup_run()
        brief = CurrentBrief(
            {"schema_version": 2}, b"<p>Exact HTML</p>\n", b"Exact text\n",
            {"source_threads": {"record-1": "thread-1"}},
        )
        with patch("school_os.hybrid_delivery.render_current_brief", return_value=brief):
            prepared = prepare_hybrid_delivery(
                storage=storage, resolved=resolved, installed_root=ROOT,
                local_day="2026-09-10", output_identity="brief-output",
                serialization=self.serialization,
            )
        resolved.state = prepared.transaction
        ledger = json.loads(resolved.state.read("state/delivery-state.json").data)
        self.assertEqual("reserved", ledger["deliveries"][prepared.delivery_key]["status"])
        self.assertEqual("pending", ledger["deliveries"][prepared.delivery_key]["audio"]["status"])
        config = {
            "voices": {"narrator": "n", "voice_a": "a"},
            "opening_tag": "[open]", "closing_tag": "[close]",
            "groups": {"child-a": {"subject_label": "Student A", "voice_role": "voice_a", "dialogue_tags": {"news": "[news]", "guideline": "[guide]", "action": "[action]"}}},
        }
        with patch("school_os.hybrid_delivery._source_context", return_value={"source_threads": {"record-1": "thread-1"}}):
            authorized = authorize_hybrid_audio(
                storage=storage, resolved=resolved, installed_root=ROOT,
                local_day="2026-09-10", configuration=config,
                serialization=self.serialization,
            )
        self.assertTrue(authorized.audio_call_required)
        resolved.state = authorized.transaction
        recorded = record_hybrid_audio(
            storage=storage, resolved=resolved, installed_root=ROOT,
            outcome="verified", serialization=self.serialization,
            audio_identity="audio-output", filename="Daily Brief.mp3",
            audio_bytes=b"ID3exact-audio",
        )
        resolved.state = recorded.transaction
        record = json.loads(resolved.state.read("state/runs/op/delivery.json").data)
        expected = _request(storage, record)
        gmail = Gmail(raw_message(expected))
        delivered = deliver_hybrid_email(
            storage=storage, gmail=gmail, resolved=resolved,
            installed_root=ROOT, serialization=self.serialization,
        )
        self.assertEqual(1, gmail.sends)
        final_state = json.loads(delivered.transaction.read("state/operation-state.json").data)
        self.assertEqual("complete", final_state["status"])
        cursor = json.loads(delivered.transaction.read("state/source-checkpoint.json").data)
        self.assertEqual({"cursor": "one"}, cursor["eligible_cursor"])
        final = json.loads(delivered.transaction.read("state/final-run-checkpoint.json").data)
        self.assertEqual("verified", final["audio_outcome"])

    def test_lost_send_response_recovers_from_drive_without_second_send(self):
        storage, resolved = self.setup_run()
        resolved.policies = {"audio": {"enabled": False}}
        brief = CurrentBrief(
            {"schema_version": 2}, b"<p>Exact HTML</p>\n", b"Exact text\n",
            {"source_threads": {"record-1": "thread-1"}},
        )
        with patch("school_os.hybrid_delivery.render_current_brief", return_value=brief):
            prepared = prepare_hybrid_delivery(
                storage=storage, resolved=resolved, installed_root=ROOT,
                local_day="2026-09-10", output_identity="brief-lost",
                serialization=self.serialization,
            )
        resolved.state = prepared.transaction
        record = json.loads(resolved.state.read("state/runs/op/delivery.json").data)
        expected = _request(storage, record)
        lost = LostResponseGmail(raw_message(expected))
        with self.assertRaisesRegex(DeliveryError, "outcome is unknown"):
            deliver_hybrid_email(
                storage=storage, gmail=lost, resolved=resolved,
                installed_root=ROOT, serialization=self.serialization,
            )
        self.assertEqual(1, lost.sends)

        prior_recovery = resolved.state.working.recovery
        recovered = recover_hybrid_generation(
            storage,
            root_reference=prior_recovery["bootstrap"]["root_reference"],
            bootstrap_reference=prior_recovery["bootstrap_reference"],
        )
        resolved.state = BundleTransactionStore.from_recovery(recovered)
        reconciliation = Gmail(raw_message(expected))
        delivered = deliver_hybrid_email(
            storage=storage, gmail=reconciliation, resolved=resolved,
            installed_root=ROOT, serialization=self.serialization,
        )
        self.assertEqual(0, reconciliation.sends)
        state = json.loads(delivered.transaction.read("state/operation-state.json").data)
        self.assertEqual("complete", state["status"])

    def test_same_source_hash_cannot_name_conflicting_drive_objects(self):
        physical = {
            "kind": "file", "permitted_ancestor_id": "root",
            "mime_type": "application/x-tar", "version": "v1",
        }
        rows = []
        for identity in ("source-a", "source-b"):
            rows.append({
                "source_members": {
                    "catalog": {
                        "bundle_sha256": "a" * 64,
                        "bundle_reference": {"object_id": identity, **physical},
                    },
                },
            })
        documents = {
            "data/source-catalog-index.json": canonical_json_bytes({
                "schema_version": 2, "records": rows,
            }),
            "data/facts.json": canonical_json_bytes({"schema_version": 1, "facts": []}),
        }
        transaction = SimpleNamespace(
            read=lambda path: SimpleNamespace(data=documents[path]),
        )
        with self.assertRaisesRegex(HybridPreviewError, "conflicting physical references"):
            _source_context(transaction, SimpleNamespace(read=lambda _identity: None))


if __name__ == "__main__":
    unittest.main()
