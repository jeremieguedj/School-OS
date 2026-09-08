from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from school_os.semantic import SemanticError, SemanticPacket, interpret_packet, validate_independent_audit


class SemanticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fact_schema = json.loads((ROOT / "schemas" / "fact.schema.json").read_text(encoding="utf-8"))
        cls.extraction_schema = json.loads((ROOT / "schemas" / "extraction-result.schema.json").read_text(encoding="utf-8"))

    def packet(self) -> SemanticPacket:
        return SemanticPacket(
            "record-001",
            "conversation-001",
            (
                {
                    "segment_id": "body-001", "content_id": "body", "source_message_id": "message-001",
                    "received_date": "2026-09-08", "text": "Return form",
                },
                {
                    "segment_id": "attachment-001", "content_id": "attachment-001", "source_message_id": "message-001",
                    "received_date": "2026-09-08", "text": "Bring lunch",
                    "attachment": {
                        "attachment_id": "attachment-001", "origin": "mime_attachment", "mime_type": "application/pdf",
                        "original_content_sha256": "a" * 64, "extracted_text_sha256": "b" * 64,
                        "locator": {"kind": "provider_page_region", "page": 1, "region": "body"},
                    },
                },
            ),
        )

    @staticmethod
    def live_interpreter(packet: dict) -> dict:
        assert packet["segments"][0]["text"] == "Return form"
        return {
            "candidates": [
                {"segment_id": "body-001", "byte_start": 0, "byte_end": 11, "candidate_kind": "action", "category": "school", "entity_scope": "household", "text": "Return form", "flags": {"is_update": False, "is_durable": False, "is_guideline": False, "is_action": True}},
                {"segment_id": "attachment-001", "byte_start": 0, "byte_end": 11, "candidate_kind": "guideline", "category": "school", "entity_scope": "household", "text": "Bring lunch", "flags": {"is_update": False, "is_durable": True, "is_guideline": True, "is_action": False}},
            ],
            "coverage": [
                {"segment_id": "body-001", "outcome": "covered", "reason": "action"},
                {"segment_id": "attachment-001", "outcome": "covered", "reason": "guideline"},
            ],
            "review_cases": [],
        }

    def test_live_packet_result_assigns_stable_provenance_and_accepts_audit(self) -> None:
        packet = self.packet()
        first = interpret_packet(packet, self.live_interpreter, fact_schema=self.fact_schema, extraction_schema=self.extraction_schema)
        second = interpret_packet(packet, self.live_interpreter, fact_schema=self.fact_schema, extraction_schema=self.extraction_schema)
        self.assertEqual(first["packet_sha256"], second["packet_sha256"])
        self.assertEqual([item["fact_id"] for item in first["facts"]], [item["fact_id"] for item in second["facts"]])
        self.assertEqual("attachment-001", first["facts"][1]["attachment"]["attachment_id"])
        validate_independent_audit(packet, first, {"packet_sha256": first["packet_sha256"], "segments": [{"segment_id": "body-001", "disposition": "accepted"}, {"segment_id": "attachment-001", "disposition": "accepted"}]})

    def test_rephrased_or_uncovered_semantic_output_fails_before_facts(self) -> None:
        def rephrasing(_packet: dict) -> dict:
            return {
                "candidates": [{"segment_id": "body-001", "byte_start": 0, "byte_end": 11, "candidate_kind": "action", "category": "school", "entity_scope": "household", "text": "Please return it", "flags": {"is_update": False, "is_durable": False, "is_guideline": False, "is_action": True}}],
                "coverage": [{"segment_id": "body-001", "outcome": "covered", "reason": "action"}],
                "review_cases": [],
            }
        with self.assertRaisesRegex(SemanticError, "coverage"):
            interpret_packet(self.packet(), rephrasing, fact_schema=self.fact_schema, extraction_schema=self.extraction_schema)

        def missing_span(_packet: dict) -> dict:
            result = self.live_interpreter(self.packet().as_mapping())
            result["candidates"][0]["text"] = "Return this"
            return result
        with self.assertRaisesRegex(SemanticError, "exact source span"):
            interpret_packet(self.packet(), missing_span, fact_schema=self.fact_schema, extraction_schema=self.extraction_schema)


if __name__ == "__main__":
    unittest.main()
