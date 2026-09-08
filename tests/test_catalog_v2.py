from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from school_os.catalog import CatalogError, parse_v2_record, serialize_v2_record, stable_record_id, validate_source_to_record, verify_persisted_record  # noqa: E402


class CatalogV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = json.loads((ROOT / "schemas" / "source-conversation.schema.json").read_text())

    def conversation(self) -> dict:
        return {
            "schema_version": 1,
            "adapter_id": "synthetic-mail-v1",
            "conversation_id": "conversation-001",
            "scope": {"folder": "synthetic"},
            "pagination": {"completed": True, "pages": ["page-1"]},
            "messages": [
                {"message_id": "message-001", "received_at": "2026-09-07T08:00:00-07:00", "body": "# A heading inside source\n<!-- school-os-message not a frame -->\n\nFinal line", "attachments": []},
                {"message_id": "message-002", "received_at": "2026-09-07T08:01:00-07:00", "body": "Unicode: café\nno final newline", "attachments": [{"attachment_id": "attachment-001"}]},
            ],
        }

    def source_bodies(self, conversation: dict) -> dict[str, str]:
        return {message["message_id"]: message["body"] for message in conversation["messages"]}

    def test_byte_counted_frames_round_trip_delimiter_like_bodies_exactly(self) -> None:
        conversation = self.conversation()
        first = serialize_v2_record(conversation, self.schema)
        second = serialize_v2_record(conversation, self.schema)
        self.assertEqual(first, second)
        parsed = parse_v2_record(first)
        self.assertEqual(list(self.source_bodies(conversation).items()), list(parsed.bodies))
        self.assertEqual([], validate_source_to_record(first, self.source_bodies(conversation)))

    def test_source_and_persisted_comparisons_are_independent(self) -> None:
        conversation = self.conversation()
        intended = serialize_v2_record(conversation, self.schema)
        verify_persisted_record(self.source_bodies(conversation), intended, intended)
        with self.assertRaisesRegex(CatalogError, "intended-to-persisted"):
            verify_persisted_record(self.source_bodies(conversation), intended, intended + b"\n")
        source = self.source_bodies(conversation)
        source["message-001"] = "rewritten"
        with self.assertRaisesRegex(CatalogError, "source-to-record"):
            verify_persisted_record(source, intended, intended)

    def test_truncated_or_reordered_frames_fail_closed(self) -> None:
        conversation = self.conversation()
        record = serialize_v2_record(conversation, self.schema)
        with self.assertRaisesRegex(CatalogError, "shorter"):
            parse_v2_record(record[:-1])
        reversed_source = dict(reversed(list(self.source_bodies(conversation).items())))
        self.assertIn("ordered message IDs differ", validate_source_to_record(record, reversed_source))

    def test_record_identity_uses_immutable_adapter_and_conversation_identity(self) -> None:
        conversation = self.conversation()
        record = parse_v2_record(serialize_v2_record(conversation, self.schema))
        self.assertEqual(stable_record_id("synthetic-mail-v1", "conversation-001"), record.header["record_id"])
        self.assertNotEqual(record.header["record_id"], stable_record_id("synthetic-mail-v1", "conversation-002"))


if __name__ == "__main__":
    unittest.main()
