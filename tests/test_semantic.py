from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from school_os.semantic import SemanticError, SemanticPacket, interpret_packet, validate_independent_audit
from school_os.contracts import canonical_json_bytes


class SemanticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fact_schema = json.loads((ROOT / "schemas" / "fact.schema.json").read_text(encoding="utf-8"))
        cls.extraction_schema = json.loads((ROOT / "schemas" / "extraction-result.schema.json").read_text(encoding="utf-8"))

    def packet(self) -> SemanticPacket:
        body = "Please return the signed form."
        attachment = "Bring lunch"
        provenance = {
            "outcome_id": "outcome-attachment-001", "attachment_id": "attachment-001", "content_id": "content-attachment", "source_message_id": "message-001",
            "origin": "mime_attachment", "outcome": "extracted", "mime_type": "application/pdf",
            "original_content_sha256": "a" * 64, "extracted_text_sha256": hashlib.sha256(attachment.encode()).hexdigest(),
            "locator": {"kind": "extracted_text_span", "byte_start": 0, "byte_end": len(attachment)},
            "complete_units": ["page:1"], "unit_count": 1,
            "disposition_reason": "complete attachment read and extraction",
        }
        return SemanticPacket(
            "record-001", "conversation-001", "c" * 64,
            (
                {
                    "segment_id": "body-001", "content_id": "content-body", "content_kind": "body",
                    "content_sha256": hashlib.sha256(body.encode()).hexdigest(), "source_message_id": "message-001",
                    "source_received_at": "2026-09-08T08:00:00-07:00", "received_date": "2026-09-08",
                    "source_message_ordinal": 0, "source_content_ordinal": 0, "text": body,
                },
                {
                    "segment_id": "attachment-001", "content_id": "content-attachment", "content_kind": "attachment",
                    "content_sha256": hashlib.sha256(attachment.encode()).hexdigest(), "source_message_id": "message-001",
                    "source_received_at": "2026-09-08T08:00:00-07:00", "received_date": "2026-09-08",
                    "source_message_ordinal": 0, "source_content_ordinal": 1, "text": attachment,
                    "source_provenance": provenance,
                },
            ),
            ({**provenance, "source_kind": "attachment"},),
        )

    @staticmethod
    def live_interpreter(packet: dict) -> dict:
        candidates = []
        coverage = []
        for segment in packet["segments"]:
            data = segment["text"].encode()
            if segment["content_kind"] == "body":
                candidates.append({"segment_id": segment["segment_id"], "byte_start": 0, "byte_end": len(data), "candidate_kind": "action", "category": "school", "entity_scope": "household", "text": "Return the signed form.", "flags": {"is_update": False, "is_durable": False, "is_guideline": False, "is_action": True}})
                coverage.append({"segment_id": segment["segment_id"], "byte_start": 0, "byte_end": len(data), "outcome": "fact", "reason": "finite request"})
            else:
                candidates.append({"segment_id": segment["segment_id"], "byte_start": 0, "byte_end": len(data), "candidate_kind": "guideline", "category": "school", "entity_scope": "household", "text": segment["text"], "flags": {"is_update": False, "is_durable": True, "is_guideline": True, "is_action": False}})
                coverage.append({"segment_id": segment["segment_id"], "byte_start": 0, "byte_end": len(data), "outcome": "fact", "reason": "standing instruction"})
        return {"candidates": candidates, "coverage": coverage, "review_cases": []}

    def accepted_audit(self, interpreted: dict) -> dict:
        # This fixture is independently stated from the interpreter: it names
        # the known source quotes, canonical wording, and expected classifications.
        expected = [
            ("body-001", b"Please return the signed form.", "Return the signed form.", "finite request", {"candidate_kind": "action", "category": "school", "entity_scope": "household", "flags": {"is_update": False, "is_durable": False, "is_guideline": False, "is_action": True}}),
            ("attachment-001", b"Bring lunch", "Bring lunch", "standing instruction", {"candidate_kind": "guideline", "category": "school", "entity_scope": "household", "flags": {"is_update": False, "is_durable": True, "is_guideline": True, "is_action": False}}),
        ]
        return {
            "packet_sha256": interpreted["packet_sha256"],
            "interpreted_sha256": interpreted["interpreted_sha256"],
            "coverage": [
                {"segment_id": segment_id, "byte_start": 0, "byte_end": len(quote), "outcome": "fact", "source_quote_sha256": hashlib.sha256(quote).hexdigest(), "interpreted_reason_sha256": hashlib.sha256(interpreted_reason.encode()).hexdigest(), "audit_disposition": "accepted", "reason": "source clause accounted for"}
                for segment_id, quote, _text, interpreted_reason, _classification in expected
            ],
            "facts": [
                {"fact_id": fact["fact_id"], "source_quote_sha256": hashlib.sha256(quote).hexdigest(), "canonical_text_sha256": hashlib.sha256(text.encode()).hexdigest(), "classification": classification, "audit_disposition": "accepted", "reason": "wording and classification are source-supported"}
                for fact, (_segment_id, quote, text, _interpreted_reason, classification) in zip(interpreted["facts"], expected)
            ],
            "source_outcomes": [
                {"outcome_id": outcome["outcome_id"], "outcome_sha256": hashlib.sha256(canonical_json_bytes(outcome)).hexdigest(), "audit_disposition": "accepted", "reason": "attachment read and extraction evidence verified"}
                for outcome in self.packet().source_outcomes
            ],
        }

    def test_live_result_keeps_exact_quote_but_allows_audited_canonical_wording(self) -> None:
        packet = self.packet()
        first = interpret_packet(packet, self.live_interpreter, fact_schema=self.fact_schema, extraction_schema=self.extraction_schema)
        second = interpret_packet(packet, self.live_interpreter, fact_schema=self.fact_schema, extraction_schema=self.extraction_schema)
        self.assertEqual(first, second)
        self.assertEqual("Please return the signed form.", first["facts"][0]["source_quote"])
        self.assertEqual("Return the signed form.", first["facts"][0]["text"])
        self.assertEqual("content-attachment", first["facts"][1]["attachment"]["content_id"])
        validate_independent_audit(packet, first, self.accepted_audit(first))

    def test_interpreter_cannot_mutate_packet_and_audit_binds_exact_result_and_classification(self) -> None:
        packet = self.packet()
        def mutating(value: dict) -> dict:
            value["segments"][1]["source_provenance"]["attachment_id"] = "forged"
            return self.live_interpreter(self.packet().as_mapping())
        result = interpret_packet(packet, mutating, fact_schema=self.fact_schema, extraction_schema=self.extraction_schema)
        self.assertEqual("attachment-001", result["facts"][1]["attachment"]["attachment_id"])
        audit = self.accepted_audit(result)
        audit["facts"][0]["classification"]["flags"]["is_action"] = False
        with self.assertRaisesRegex(SemanticError, "classification"):
            validate_independent_audit(packet, result, audit)
        audit = self.accepted_audit(result)
        audit["interpreted_sha256"] = "0" * 64
        with self.assertRaisesRegex(SemanticError, "exact interpreted artifact"):
            validate_independent_audit(packet, result, audit)
        audit = self.accepted_audit(result)
        audit["coverage"][0]["interpreted_reason_sha256"] = "0" * 64
        with self.assertRaisesRegex(SemanticError, "disposition reason"):
            validate_independent_audit(packet, result, audit)
        audit = self.accepted_audit(result)
        audit["source_outcomes"][0]["outcome_sha256"] = "0" * 64
        with self.assertRaisesRegex(SemanticError, "exact source outcome"):
            validate_independent_audit(packet, result, audit)

    def test_coverage_must_partition_every_exact_byte(self) -> None:
        def gap(packet: dict) -> dict:
            result = self.live_interpreter(packet)
            result["coverage"][0]["byte_start"] = 1
            result["candidates"][0]["byte_start"] = 1
            return result
        with self.assertRaisesRegex(SemanticError, "gap or overlap"):
            interpret_packet(self.packet(), gap, fact_schema=self.fact_schema, extraction_schema=self.extraction_schema)

    def test_faithfully_recorded_source_ambiguity_can_pass_audit_without_a_fact(self) -> None:
        text = "The deadline may change."
        packet = SemanticPacket("record-002", "conversation-002", "d" * 64, ({"segment_id": "body-002", "content_id": "content-body-2", "content_kind": "body", "content_sha256": hashlib.sha256(text.encode()).hexdigest(), "source_message_id": "message-002", "source_received_at": "2026-09-08T09:00:00-07:00", "received_date": "2026-09-08", "source_message_ordinal": 0, "source_content_ordinal": 0, "text": text},))
        def interpreter(value: dict) -> dict:
            length = len(value["segments"][0]["text"].encode())
            return {"candidates": [], "coverage": [{"segment_id": "body-002", "byte_start": 0, "byte_end": length, "outcome": "review", "reason": "source leaves the deadline unresolved"}], "review_cases": [{"segment_id": "body-002", "byte_start": 0, "byte_end": length, "reason": "source leaves the deadline unresolved"}]}
        result = interpret_packet(packet, interpreter, fact_schema=self.fact_schema, extraction_schema=self.extraction_schema)
        audit = {"packet_sha256": result["packet_sha256"], "interpreted_sha256": result["interpreted_sha256"], "coverage": [{"segment_id": "body-002", "byte_start": 0, "byte_end": len(text), "outcome": "review", "source_quote_sha256": hashlib.sha256(text.encode()).hexdigest(), "interpreted_reason_sha256": hashlib.sha256(b"source leaves the deadline unresolved").hexdigest(), "audit_disposition": "accepted", "reason": "uncertainty was preserved without a guessed fact"}], "facts": [], "source_outcomes": []}
        validate_independent_audit(packet, result, audit)
        self.assertEqual([], result["facts"])


if __name__ == "__main__":
    unittest.main()
