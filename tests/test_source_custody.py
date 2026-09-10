from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from school_os.catalog import CatalogError, build_catalog_message, parse_v2_record, serialize_v2_record, stable_content_id, verified_catalog_contents, verify_persisted_record
from school_os.contracts import canonical_json_bytes
from school_os.importer import AttachmentExtraction, AttachmentRead, DirectResourcePolicyExclusion, DirectResourceRead, ImportError, admit_exact_plaintext_representation, discover_direct_html_resources, process_attachments, process_direct_html_resources, require_complete_message_coverage
from school_os.semantic import interpret_packet, semantic_packet_from_verified_record, validate_independent_audit


class SourceCustodyIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = json.loads((ROOT / "schemas" / "source-conversation.schema.json").read_text())
        cls.fact_schema = json.loads((ROOT / "schemas" / "fact.schema.json").read_text())
        cls.extraction_schema = json.loads((ROOT / "schemas" / "extraction-result.schema.json").read_text())

    @staticmethod
    def mime_part(part_id: str, mime_type: str, data: bytes, *, selected: bool = False) -> dict:
        return {
            "part_id": part_id, "role": "body", "selected_plaintext": selected,
            "complete": True, "mime_type": mime_type, "charset": "utf-8",
            "content_transfer_encoding": "identity", "data": data,
            "raw_part_sha256": hashlib.sha256(data).hexdigest(), "raw_part_byte_length": len(data),
            "raw_part_locator": {"kind": "raw_part_bytes", "byte_start": 0, "byte_end": len(data)},
            "provider_unicode": data.decode("utf-8"),
        }

    def test_admission_outcomes_survive_catalog_frames_and_build_bounded_packet(self) -> None:
        body_bytes = b"Please return the form."
        admission = admit_exact_plaintext_representation((self.mime_part("plain-1", "text/plain", body_bytes, selected=True),), mime_tree_complete=True)

        pdf_text = "Page one notice.\nPage eight deadline."
        pdf_units = tuple(f"page:{index}" for index in range(1, 9))
        attachments = process_attachments(
            ({"attachment_id": "attachment-pdf", "content_id": "pdf-content", "source_message_id": "message-1", "mime_type": "application/pdf", "byte_size": 2048},),
            read_attachment=lambda identity: AttachmentRead(
                identity, "application/pdf", True, 2048, None,
                AttachmentExtraction(pdf_text, {"kind": "extracted_text_span", "byte_start": 0, "byte_end": len(pdf_text.encode())}, pdf_units, 8),
                {"kind": "provider_attachment", "identity": identity}, "provider-version-1",
            ),
            supported_mime_types=("application/pdf",), max_bytes=4096,
        )
        self.assertEqual("extracted", attachments[0].outcome)
        self.assertIsNone(attachments[0].original_content_sha256)
        self.assertEqual(8, attachments[0].unit_count)

        html = b'<img src="https://assets.example/notice.png">'
        resources = discover_direct_html_resources("message-1", self.mime_part("html-1", "text/html", html))
        image = b"\x89PNG\r\n\x1a\nimage"
        resource_outcomes = process_direct_html_resources(
            resources,
            fetch_resource=lambda url: DirectResourceRead(url, (url,), image, "image/gif", 200, True, True, len(image), len(image)),
            extractors={"image/png": lambda _read: AttachmentExtraction("Image notice", {"kind": "extracted_text_span", "byte_start": 0, "byte_end": 12}, ("image:1",), 1)},
            max_bytes=1024, max_redirects=0,
        )
        require_complete_message_coverage(admission.plaintext or b"", attachments, resource_outcomes)

        message = build_catalog_message(
            message_id="message-1", received_at="2026-09-08T08:00:00-07:00", received_date="2026-09-08",
            admission=admission, attachment_outcomes=attachments, resource_outcomes=resource_outcomes,
        )
        conversation = {"schema_version": 2, "adapter_id": "synthetic-mail", "conversation_id": "conversation-1", "scope": {"fixed": True}, "pagination": {"completed": True}, "messages": [message]}
        record_bytes = serialize_v2_record(conversation, self.schema)
        verify_persisted_record({"message-1": body_bytes.decode()}, record_bytes, record_bytes)
        record = parse_v2_record(record_bytes)
        entries = verified_catalog_contents(record)
        self.assertEqual(["body", "attachment", "resource"], [entry["content_kind"] for entry in entries])
        self.assertEqual([body_bytes.decode(), pdf_text, "Image notice"], [entry["text"] for entry in entries])
        packet = semantic_packet_from_verified_record(record_bytes, {"message-1": body_bytes.decode()}, max_segments=3, max_bytes=256)
        self.assertEqual([0, 1, 2], [segment["source_content_ordinal"] for segment in packet.segments])
        self.assertEqual(record.record_sha256, packet.catalog_record_sha256)
        self.assertEqual(stable_content_id("message-1", "attachment", "attachment-pdf"), packet.segments[1]["content_id"])
        self.assertEqual(resources[0].resource_id, packet.segments[2]["source_provenance"]["resource_id"])
        self.assertEqual(hashlib.sha256(html).hexdigest(), packet.segments[2]["source_provenance"]["html_part_sha256"])
        self.assertEqual(hashlib.sha256(html).hexdigest(), packet.segments[2]["source_provenance"]["html_decoded_sha256"])
        self.assertEqual("image/gif", packet.segments[2]["source_provenance"]["fetch_evidence"]["declared_mime_type"])
        self.assertEqual("image/png", packet.segments[2]["source_provenance"]["fetch_evidence"]["verified_mime_type"])

        def interpreter(value: dict) -> dict:
            candidates = []
            coverage = []
            for segment in value["segments"]:
                byte_length = len(segment["text"].encode())
                candidates.append({
                    "segment_id": segment["segment_id"], "byte_start": 0,
                    "byte_end": byte_length, "candidate_kind": "statement",
                    "category": "school", "entity_scope": "household",
                    "text": segment["text"],
                    "flags": {"is_update": True, "is_durable": False, "is_guideline": False, "is_action": False},
                })
                coverage.append({
                    "segment_id": segment["segment_id"], "byte_start": 0,
                    "byte_end": byte_length, "outcome": "fact",
                    "reason": "source statement",
                })
            return {"candidates": candidates, "coverage": coverage, "review_cases": []}

        interpreted = interpret_packet(
            packet, interpreter, fact_schema=self.fact_schema,
            extraction_schema=self.extraction_schema,
        )
        classification = {
            "candidate_kind": "statement", "category": "school",
            "entity_scope": "household",
            "flags": {"is_update": True, "is_durable": False, "is_guideline": False, "is_action": False},
        }
        audit = {
            "packet_sha256": interpreted["packet_sha256"],
            "interpreted_sha256": interpreted["interpreted_sha256"],
            "coverage": [{
                "segment_id": segment["segment_id"], "byte_start": 0,
                "byte_end": len(segment["text"].encode()), "outcome": "fact",
                "source_quote_sha256": segment["content_sha256"],
                "interpreted_reason_sha256": hashlib.sha256(b"source statement").hexdigest(),
                "audit_disposition": "accepted", "reason": "exact source statement accounted for",
            } for segment in packet.segments],
            "facts": [{
                "fact_id": fact["fact_id"],
                "source_quote_sha256": hashlib.sha256(fact["source_quote"].encode()).hexdigest(),
                "canonical_text_sha256": hashlib.sha256(fact["text"].encode()).hexdigest(),
                "classification": classification, "audit_disposition": "accepted",
                "reason": "wording and classification independently verified",
            } for fact in interpreted["facts"]],
            "source_outcomes": [{
                "outcome_id": outcome["outcome_id"],
                "outcome_sha256": hashlib.sha256(canonical_json_bytes(outcome)).hexdigest(),
                "audit_disposition": "accepted", "reason": "read and extraction custody independently verified",
            } for outcome in packet.source_outcomes],
        }
        validate_independent_audit(packet, interpreted, audit)
        self.assertEqual(["body", "mime_attachment", "html_embedded"], [
            "body" if "attachment" not in fact else fact["attachment"]["origin"]
            for fact in interpreted["facts"]
        ])

        changed = json.loads(json.dumps(conversation))
        changed["messages"][0]["body"] = "substituted"
        with self.assertRaisesRegex(CatalogError, "provider Unicode"):
            serialize_v2_record(changed, self.schema)

        changed = json.loads(json.dumps(conversation))
        changed["messages"][0]["resources"][0]["fetch_evidence"]["bytes_read"] = 1
        with self.assertRaisesRegex(CatalogError, "fetch evidence"):
            serialize_v2_record(changed, self.schema)

        changed = json.loads(json.dumps(conversation))
        changed["messages"][0]["attachments"][0]["complete_units"][-1] = "page:7"
        with self.assertRaisesRegex(CatalogError, "unit evidence"):
            serialize_v2_record(changed, self.schema)

        with self.assertRaisesRegex(CatalogError, "shorter|trailing|expected"):
            parse_v2_record(record_bytes[:-1])

    def test_incomplete_fetch_or_pdf_units_cannot_be_catalogued_as_extracted(self) -> None:
        html = b'<a href="https://assets.example/form.pdf">form</a>'
        resources = discover_direct_html_resources("message-1", self.mime_part("html-1", "text/html", html))
        payload = b"%PDF-content"
        incomplete_fetch = process_direct_html_resources(
            resources,
            fetch_resource=lambda url: DirectResourceRead(url, (url,), payload, "application/pdf", 200, True, False, len(payload), len(payload)),
            extractors={"application/pdf": lambda _read: AttachmentExtraction("Page", {"kind": "provider_page_region", "page": 1, "region": "body"}, ("page:1",), 1)},
            max_bytes=1024, max_redirects=0,
        )
        self.assertEqual("manual_review", incomplete_fetch[0].outcome)

        policy_excluded = process_direct_html_resources(
            resources,
            fetch_resource=lambda url: (_ for _ in ()).throw(
                DirectResourcePolicyExclusion(
                    "declared content length exceeds selected byte bound",
                    final_url=url, redirect_chain=(url,),
                    fetch_evidence={
                        "status_code": 200, "complete": False, "eof": False,
                        "bytes_read": 0, "declared_content_length": 2048,
                        "declared_mime_type": "application/pdf",
                        "verified_mime_type": None, "selected_max_bytes": 1024,
                    },
                )
            ),
            extractors={}, max_bytes=1024, max_redirects=0,
        )
        self.assertEqual("excluded_by_policy", policy_excluded[0].outcome)
        self.assertEqual((resources[0].url,), policy_excluded[0].redirect_chain)
        require_complete_message_coverage(b"body", (), policy_excluded)
        admission = admit_exact_plaintext_representation(
            (self.mime_part("plain-1", "text/plain", b"body", selected=True),),
            mime_tree_complete=True,
        )
        message = build_catalog_message(
            message_id="message-1", received_at="2026-09-08T08:00:00Z",
            received_date="2026-09-08", admission=admission,
            resource_outcomes=policy_excluded,
        )
        record = serialize_v2_record({
            "schema_version": 2, "adapter_id": "synthetic-mail",
            "conversation_id": "conversation-1", "scope": {"fixed": True},
            "pagination": {"completed": True}, "messages": [message],
        }, self.schema)
        self.assertEqual(
            "excluded_by_policy",
            parse_v2_record(record).header["messages"][0]["resources"][0]["outcome"],
        )

        missing_page = process_attachments(
            ({"attachment_id": "attachment-pdf", "source_message_id": "message-1", "mime_type": "application/pdf", "byte_size": 100},),
            read_attachment=lambda identity: AttachmentRead(identity, "application/pdf", True, 100, None, AttachmentExtraction("Pages", {"kind": "extracted_text_span", "byte_start": 0, "byte_end": 5}, ("page:1",), 2), {"kind": "provider_attachment", "identity": identity}),
            supported_mime_types=("application/pdf",), max_bytes=1024,
        )
        self.assertEqual("manual_review", missing_page[0].outcome)
        with self.assertRaisesRegex(ImportError, "attachment coverage"):
            require_complete_message_coverage(b"body", missing_page, ())
if __name__ == "__main__":
    unittest.main()
