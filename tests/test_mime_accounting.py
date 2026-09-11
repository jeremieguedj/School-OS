from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from school_os.catalog import build_catalog_message, parse_v2_record, serialize_v2_record, verify_persisted_record
from school_os.importer import AttachmentOutcome, admit_exact_plaintext_representation
from school_os.mime_accounting import accounting_sha256, build_mime_accounting
from school_os.semantic import _packet_hash, semantic_packet_from_verified_record


def part(path: str, text: str, mime: str = "text/plain") -> dict:
    data = text.encode("utf-8")
    return {
        "part_id": path or "root", "provider_part_id": path, "role": "body",
        "selected_plaintext": False, "complete": True, "mime_type": mime,
        "charset": "utf-8", "content_transfer_encoding": "identity",
        "data": data, "provider_unicode": text,
        "raw_part_sha256": hashlib.sha256(data).hexdigest(),
        "raw_part_byte_length": len(data),
        "raw_part_locator": {"kind": "raw_part_bytes", "byte_start": 0, "byte_end": len(data)},
    }


def node(path: str, mime: str, multipart: bool) -> dict:
    return {
        "path": path, "mime_type": mime, "multipart": multipart,
        "content_disposition": None, "content_id_header": None,
        "related_start": None,
    }


class MimeAccountingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = json.loads((ROOT / "schemas" / "source-conversation.schema.json").read_text())

    def test_mixed_plain_units_are_preserved_and_padding_is_not_ambiguity(self) -> None:
        parts = [part("0", "First"), part("1", "Second"), part("2", "\r\n")]
        accounting, contents, primary = build_mime_accounting(
            message_id="m1", raw_message=b"raw",
            nodes=[node("", "multipart/mixed", True), *[
                node(str(index), "text/plain", False) for index in range(3)
            ]], parts=parts,
        )
        self.assertEqual("0", primary)
        self.assertEqual(["interpret", "interpret", "padding"], [item["disposition"] for item in contents])
        self.assertEqual([item["content_id"] for item in contents], accounting["content_order"])

    def test_alternative_uses_last_plain_presentation_and_only_exact_sibling_duplicate_is_collapsed(self) -> None:
        parts = [part("0", "Same"), part("1", "Same"), part("2", "New")]
        accounting, contents, primary = build_mime_accounting(
            message_id="m1", raw_message=b"raw",
            nodes=[node("", "multipart/alternative", True), *[
                node(str(index), "text/plain", False) for index in range(3)
            ]], parts=parts,
        )
        self.assertEqual("2", primary)
        self.assertEqual(["interpret", "duplicate_text", "interpret"], [item["disposition"] for item in contents])
        self.assertEqual("0", contents[1]["duplicate_of_part_id"])
        self.assertTrue(accounting["complete"])

    def test_custody_v2_roundtrip_keeps_primary_supplement_and_html_evidence(self) -> None:
        parts = [part("0", "Primary"), part("1", "More"), part("2", "<p>Evidence</p>", "text/html")]
        accounting, contents, primary = build_mime_accounting(
            message_id="m1", raw_message=b"raw-message",
            nodes=[node("", "multipart/mixed", True), node("0", "text/plain", False),
                   node("1", "text/plain", False), node("2", "text/html", False)],
            parts=parts,
        )
        for item in parts:
            item["selected_plaintext"] = item["part_id"] == primary
            if item["mime_type"] == "text/plain":
                item["mime_accounting_disposition"] = next(
                    value["disposition"] for value in contents if value["provider_part_id"] == item["provider_part_id"]
                )
        admission = admit_exact_plaintext_representation(parts, mime_tree_complete=True)
        message = build_catalog_message(
            message_id="m1", received_at="2026-09-09T08:00:00Z",
            received_date="2026-09-09", admission=admission,
            mime_accounting=accounting, mime_contents=contents,
        )
        conversation = {
            "schema_version": 3, "adapter_id": "mail", "conversation_id": "c1",
            "scope": {"fixed": True}, "pagination": {"completed": True},
            "messages": [message],
        }
        record_bytes = serialize_v2_record(conversation, self.schema)
        parsed = parse_v2_record(record_bytes)
        self.assertEqual(2, parsed.header["custody_version"])
        snapshot = {"schema_version": 1, "messages": [{
            "message_id": "m1", "accounting_sha256": accounting_sha256(accounting),
            "contents": [{"content_id": item["content_id"], "sha256": item["sha256"], "text": item["text"]} for item in contents],
        }]}
        verify_persisted_record(snapshot, record_bytes, record_bytes)
        packet = semantic_packet_from_verified_record(record_bytes, snapshot, max_segments=10, max_bytes=1000)
        self.assertEqual(2, packet.as_mapping()["schema_version"])
        self.assertEqual(["body", "body_supplement"], [item["content_kind"] for item in packet.segments])
        self.assertEqual(["html_evidence"], [item["content_kind"] for item in packet.evidence_segments])
        self.assertEqual(accounting_sha256(accounting), packet.mime_accounting[0]["accounting_sha256"])

    def test_html_only_message_is_custodied_without_inventing_plaintext(self) -> None:
        parts = [part("root", "<p>Only HTML</p>", "text/html")]
        parts[0]["provider_part_id"] = ""
        accounting, contents, primary = build_mime_accounting(
            message_id="m-html", raw_message=b"raw-html",
            nodes=[node("", "text/html", False)], parts=parts,
        )
        self.assertIsNone(primary)
        self.assertIsNone(accounting["primary_content_id"])
        message = build_catalog_message(
            message_id="m-html", received_at="2026-09-09T08:00:00Z",
            received_date="2026-09-09", admission=None,
            mime_accounting=accounting, mime_contents=contents,
        )
        record = parse_v2_record(serialize_v2_record({
            "schema_version": 3, "adapter_id": "mail", "conversation_id": "c-html",
            "scope": {"fixed": True}, "pagination": {"completed": True},
            "messages": [message],
        }, self.schema))
        self.assertEqual((), record.bodies)
        self.assertEqual(1, len(record.contents))

    def test_mime_accounting_and_extracted_pdf_use_distinct_content_sets(self) -> None:
        parts = [
            part("0", "Primary"),
            {
                **part("1", "", "application/pdf"),
                "role": "attachment",
                "provider_unicode": None,
            },
        ]
        accounting, contents, primary = build_mime_accounting(
            message_id="m-pdf", raw_message=b"raw-message",
            nodes=[
                node("", "multipart/mixed", True),
                node("0", "text/plain", False),
                node("1", "application/pdf", False),
            ],
            parts=parts,
        )
        parts[0]["selected_plaintext"] = True
        parts[0]["mime_accounting_disposition"] = "interpret"
        admission = admit_exact_plaintext_representation(
            parts, mime_tree_complete=True,
        )
        extracted = "Complete visible PDF text"
        original = b"%PDF-synthetic"
        outcome = AttachmentOutcome(
            attachment_id="pdf-1", outcome="extracted",
            mime_type="application/pdf",
            original_content_sha256=hashlib.sha256(original).hexdigest(),
            extracted_text_sha256=hashlib.sha256(extracted.encode()).hexdigest(),
            text=extracted,
            locator={
                "kind": "extracted_text_span", "byte_start": 0,
                "byte_end": len(extracted.encode()),
            },
            original_bytes_observed=True,
            read_evidence={
                "complete": True, "identity": "pdf-1",
                "mime_type": "application/pdf",
                "declared_byte_size": len(original),
                "observed_byte_size": len(original),
                "mode": "original_bytes",
                "locator": {"kind": "provider_attachment_download"},
                "version": None,
            },
            complete_units=("page:1",), unit_count=1,
            disposition_reason="complete bounded PDF extraction",
        )
        message = build_catalog_message(
            message_id="m-pdf", received_at="2026-09-09T08:00:00Z",
            received_date="2026-09-09", admission=admission,
            attachment_outcomes=(outcome,),
            mime_accounting=accounting, mime_contents=contents,
        )
        conversation = {
            "schema_version": 3, "adapter_id": "mail",
            "conversation_id": "c-pdf", "scope": {"fixed": True},
            "pagination": {"completed": True}, "messages": [message],
        }
        record_bytes = serialize_v2_record(conversation, self.schema)
        snapshot = {"schema_version": 1, "messages": [{
            "message_id": "m-pdf",
            "accounting_sha256": accounting_sha256(accounting),
            "contents": [{
                "content_id": item["content_id"],
                "sha256": item["sha256"], "text": item["text"],
            } for item in contents],
        }]}
        packet = semantic_packet_from_verified_record(
            record_bytes, snapshot, max_segments=10, max_bytes=1000,
        )
        self.assertEqual(
            ["body", "attachment"],
            [item["content_kind"] for item in packet.segments],
        )
        self.assertEqual(64, len(_packet_hash(packet)))


if __name__ == "__main__":
    unittest.main()
