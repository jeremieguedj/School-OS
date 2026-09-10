from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from school_os.adapters import Page
from school_os.bundles import BundleEntry, build_bundle, read_bundle
from school_os.connected_ingestion import ConnectedIngestionWorker
from school_os.connected_sources import ConnectedSourceAdapters
from school_os.hybrid_ingestion import (
    LocalIngestionStore, SourceByteCapture, publish_ingestion_result,
    stage_connected_ingestion, stage_ingestion,
)


def _part(data: bytes) -> dict[str, Any]:
    return {
        "part_id": "plain-1", "role": "body", "selected_plaintext": True,
        "complete": True, "mime_type": "text/plain", "charset": "utf-8",
        "content_transfer_encoding": "identity", "data": data,
        "raw_part_sha256": hashlib.sha256(data).hexdigest(),
        "raw_part_byte_length": len(data),
        "raw_part_locator": {"kind": "raw_part_bytes", "byte_start": 0, "byte_end": len(data)},
        "provider_unicode": data.decode("utf-8"),
    }


class Source:
    def search(self, _scope: dict[str, Any], token: str | None) -> Page:
        return Page(({
            "conversation_id": "thread-1", "byte_size": 1,
            "discovery_message_ids": ["message-1"],
        },), None) if token is None else Page((), None)

    def read_conversation(self, identity: str) -> dict[str, Any]:
        return {
            "conversation_id": identity,
            "messages": [{
                "message_id": "message-1", "received_at": "2026-09-08T08:00:00Z",
                "received_date": "2026-09-08", "gmail_internal_date_ms": 1788854400000,
                "mime_tree_complete": True, "parts": [_part(b"Exact source body")],
                "attachments": [], "html_parts": [],
            }],
        }

    def read_attachment(self, _message_id: str, _attachment_id: str) -> Any:
        raise AssertionError("no attachment")


class FakeTransaction:
    def __init__(self) -> None:
        self.working = type("Working", (), {"recovery": {}})()
        self.staged: dict[str, bytes] = {}

    def stage(self, path: str, data: bytes, **_kwargs: Any) -> "FakeTransaction":
        self.staged[path] = data
        return self


class HybridIngestionTests(unittest.TestCase):
    def test_connected_composer_binds_existing_extractors_for_direct_resources(self) -> None:
        resolved = SimpleNamespace(
            household={"timezone": "UTC"},
            source_scope={"max_thread_messages": 10, "adapter_id": "gmail-v1"},
            policies={"execution": {"max_records_per_unit": 5, "max_bytes_per_unit": 65_536}},
        )

        def inspect_worker(*, worker_factory: Any, **_kwargs: Any) -> str:
            worker = worker_factory(LocalIngestionStore())
            self.assertEqual(
                {"application/pdf", "image/gif", "image/jpeg", "image/png"},
                set(worker.resource_extractors),
            )
            self.assertIn("image/gif", worker.supported_attachment_mime_types)
            self.assertEqual(
                {"image/*"},
                set(worker.excluded_attachment_mime_types),
            )
            self.assertEqual(
                {"html_embedded"}, set(worker.excluded_resource_origins),
            )
            self.assertTrue(all(
                "temporarily disabled" in reason
                for reason in (
                    *worker.excluded_attachment_mime_types.values(),
                    *worker.excluded_resource_origins.values(),
                )
            ))
            return "staged"

        observed_byte_bounds: list[int] = []

        def adapter_factory(**kwargs: Any) -> ConnectedSourceAdapters:
            observed_byte_bounds.append(kwargs["bounds"].max_bytes)
            return ConnectedSourceAdapters(**kwargs)

        with patch(
            "school_os.hybrid_ingestion.ConnectedSourceAdapters",
            side_effect=adapter_factory,
        ), patch("school_os.hybrid_ingestion.stage_ingestion", side_effect=inspect_worker):
            result = stage_connected_ingestion(
                installed_root=ROOT,
                resolved=resolved,
                run_directory=ROOT,
                gmail=SimpleNamespace(peer=object()),
                semantic=object(),
                capture=SourceByteCapture(),
            )
        self.assertEqual("staged", result)
        self.assertEqual([65_536], observed_byte_bounds)

    def worker(self, store: LocalIngestionStore) -> ConnectedIngestionWorker:
        schemas = {
            name: json.loads((ROOT / "schemas" / name).read_text())
            for name in (
                "source-conversation.schema.json", "fact.schema.json",
                "extraction-result.schema.json",
            )
        }

        def interpret(packet: dict[str, Any]) -> dict[str, Any]:
            return {
                "candidates": [{
                    "segment_id": segment["segment_id"], "byte_start": 0,
                    "byte_end": len(segment["text"].encode()),
                    "candidate_kind": "statement", "category": "school",
                    "entity_scope": "household", "text": "Canonical wording",
                    "flags": {"is_update": True, "is_durable": False, "is_guideline": False, "is_action": False},
                } for segment in packet["segments"]],
                "coverage": [{
                    "segment_id": segment["segment_id"], "byte_start": 0,
                    "byte_end": len(segment["text"].encode()), "outcome": "fact",
                    "reason": "school statement",
                } for segment in packet["segments"]],
                "review_cases": [],
            }

        def audit(packet: dict[str, Any], interpreted: dict[str, Any]) -> dict[str, Any]:
            return {
                "packet_sha256": interpreted["packet_sha256"],
                "interpreted_sha256": interpreted["interpreted_sha256"],
                "coverage": [{
                    "segment_id": segment["segment_id"], "byte_start": 0,
                    "byte_end": len(segment["text"].encode()), "outcome": "fact",
                    "source_quote_sha256": hashlib.sha256(segment["text"].encode()).hexdigest(),
                    "interpreted_reason_sha256": hashlib.sha256(b"school statement").hexdigest(),
                    "audit_disposition": "accepted", "reason": "checked",
                } for segment in packet["segments"]],
                "facts": [{
                    "fact_id": fact["fact_id"],
                    "source_quote_sha256": hashlib.sha256(fact["source_quote"].encode()).hexdigest(),
                    "canonical_text_sha256": hashlib.sha256(fact["text"].encode()).hexdigest(),
                    "classification": {
                        "candidate_kind": "statement", "category": "school",
                        "entity_scope": "household", "flags": fact["flags"],
                    },
                    "audit_disposition": "accepted", "reason": "checked",
                } for fact in interpreted["facts"]],
                "source_outcomes": [],
            }

        return ConnectedIngestionWorker(
            source=Source(), store=store, adapter_id="gmail-v1",
            catalog_schema=schemas["source-conversation.schema.json"],
            fact_schema=schemas["fact.schema.json"],
            extraction_schema=schemas["extraction-result.schema.json"],
            interpreter=interpret, auditor=audit,
        )

    def test_stages_locally_then_publishes_real_source_member_references(self) -> None:
        staged = stage_ingestion(
            worker_factory=self.worker, scope={"query": "bounded"},
            max_records=5, max_bytes=16_384,
        )
        capture = SourceByteCapture()
        capture.raw_message("message-1", "thread-1", b"RFC2822 exact bytes")
        named = staged.store.named_artifacts()
        entries = {
            ("catalog/records/" + name if name.endswith(".md") else
             "semantic/interpretations/" + name if name.endswith(".interpretation.json") else
             "semantic/audits/" + name if name.endswith(".audit.json") else
             "facts/records/" + name if name.endswith(".facts.json") else
             {"discovery.json": "discovery/inventory.json", "index.json": "catalog/index-v1.json", "work.json": "state/source-work.json"}[name]):
            BundleEntry(item.data, "test", item.reference.mime_type)
            for name, item in named.items()
        }
        entries["raw/messages/" + hashlib.sha256(b"message-1").hexdigest() + ".eml"] = BundleEntry(
            b"RFC2822 exact bytes", "raw_gmail_message", "message/rfc822",
        )
        # Publication adds its own custody member, so construct the fake result
        # inside the patched call from the exact entries it is given.
        def publish(_storage: Any, *, recovery: Any, bundle_kind: str, identity: str, entries: Any) -> dict[str, Any]:
            data = build_bundle(
                bundle_kind=bundle_kind, identity=identity, instance_id="instance",
                package_sha256="a" * 64, settings_sha256="b" * 64,
                configuration_fingerprint="c" * 64, entries=entries,
            )
            verified = read_bundle(data, expected_kind="source")
            return {
                "bundle": verified, "bundle_bytes": data, "bundle_sha256": verified.sha256,
                "bundle_reference": {
                    "object_id": "source-1", "kind": "file",
                    "permitted_ancestor_id": "root", "mime_type": "application/x-tar",
                    "version": "1",
                },
                "identity": identity,
            }

        transaction = FakeTransaction()
        with patch("school_os.hybrid_ingestion.publish_hybrid_content_bundle", side_effect=publish):
            result = publish_ingestion_result(
                storage=object(), transaction=transaction, result=staged.result,
                staged=staged.store, capture=capture, identity="source-batch-000001",
            )
        self.assertEqual(2, result.catalog_index["schema_version"])
        row = result.catalog_index["records"][0]
        self.assertEqual("source-1", row["source_members"]["catalog"]["bundle_reference"]["object_id"])
        self.assertNotIn(b"school-os-local-stage", transaction.staged["data/source-catalog-index.json"])
        self.assertEqual(1, len(result.facts["facts"]))
        fact_id = result.facts["facts"][0]["fact_id"]
        self.assertEqual(row["record_id"], result.fact_indexes["by_fact_id"][fact_id]["record_id"])
        self.assertIn("data/facts.json", transaction.staged)
        self.assertIn("data/fact-indexes.json", transaction.staged)


if __name__ == "__main__":
    unittest.main()
