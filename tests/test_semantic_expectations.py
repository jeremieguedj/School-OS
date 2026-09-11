from __future__ import annotations

import hashlib
import unittest

from school_os.semantic_expectations import (
    SemanticExpectationError, semantic_packet_binding,
    validate_semantic_expectation,
)


def _packet(record: str, text: str) -> dict:
    digest = hashlib.sha256(text.encode()).hexdigest()
    return {
        "schema_version": 2,
        "record_id": record,
        "conversation_id": "conversation-" + record,
        "catalog_record_sha256": hashlib.sha256(record.encode()).hexdigest(),
        "segments": [{
            "segment_id": "segment-" + record,
            "content_id": "content-" + record,
            "content_kind": "body",
            "content_sha256": digest,
            "source_message_id": "message-" + record,
            "source_received_at": "2026-09-10T10:00:00Z",
            "received_date": "2026-09-10",
            "source_message_ordinal": 0,
            "source_content_ordinal": 0,
            "text": text,
        }],
        "source_outcomes": [],
        "mime_accounting": [],
        "evidence_segments": [],
    }


class SemanticExpectationTests(unittest.TestCase):
    def test_zero_fact_expectation_is_bound_to_exact_packet(self) -> None:
        first = _packet("one", "No qualifying update.")
        second = _packet("two", "A different source packet.")
        expectation = {
            "schema_version": 1,
            "binding": semantic_packet_binding(first),
            "candidates": [],
        }
        self.assertEqual([], validate_semantic_expectation(first, expectation)["candidates"])
        with self.assertRaisesRegex(SemanticExpectationError, "different packet"):
            validate_semantic_expectation(second, expectation)

    def test_binding_detects_segment_text_tampering(self) -> None:
        packet = _packet("one", "Exact source bytes.")
        expectation = {
            "schema_version": 1,
            "binding": semantic_packet_binding(packet),
            "candidates": [],
        }
        packet["segments"][0]["text"] = "Changed source bytes."
        with self.assertRaisesRegex(SemanticExpectationError, "identity disagrees"):
            validate_semantic_expectation(packet, expectation)

    def test_unknown_expectation_fields_are_rejected(self) -> None:
        packet = _packet("one", "Exact source bytes.")
        expectation = {
            "schema_version": 1,
            "binding": semantic_packet_binding(packet),
            "candidates": [],
            "fallback": "accept-any-packet",
        }
        with self.assertRaisesRegex(SemanticExpectationError, "unsupported shape"):
            validate_semantic_expectation(packet, expectation)


if __name__ == "__main__":
    unittest.main()
