from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from school_os.catalog import CatalogError, recover_catalog_index, serialize_v2_record, stable_record_id
from school_os.contracts import canonical_json_bytes


class CatalogWriteRecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = json.loads((ROOT / "schemas" / "source-conversation.schema.json").read_text())

    def conversation(self) -> dict:
        return {"schema_version": 1, "adapter_id": "synthetic-mail", "conversation_id": "orphaned-001", "scope": {}, "pagination": {"completed": True}, "messages": [{"message_id": "message-001", "received_at": "2026-09-07T08:00:00-07:00", "body": "Return the form", "attachments": []}]}

    def facts(self) -> list[dict]:
        return [{"fact_id": "fact-stable-001", "record_id": stable_record_id("synthetic-mail", "orphaned-001")}]

    def test_record_write_before_index_is_adopted_once_without_fact_renumbering(self) -> None:
        conversation = self.conversation()
        intended = serialize_v2_record(conversation, self.schema)
        with tempfile.TemporaryDirectory() as temporary:
            record_path = Path(temporary) / "record.md"
            index_path = Path(temporary) / "index.json"
            record_path.write_bytes(intended)  # fault: storage write succeeded before index/pointer write
            recovered = recover_catalog_index({"message-001": "Return the form"}, intended, record_path.read_bytes(), {"schema_version": 1, "records": []}, self.facts())
            index_path.write_bytes(canonical_json_bytes(recovered.index))
            replay = recover_catalog_index({"message-001": "Return the form"}, intended, record_path.read_bytes(), json.loads(index_path.read_text()), self.facts())
            self.assertEqual(recovered.index, replay.index)
            self.assertEqual(["fact-stable-001"], replay.index["records"][0]["fact_ids"])
            self.assertEqual(1, len(replay.index["records"]))

    def test_corrupt_or_conflicting_orphan_blocks_without_index_change(self) -> None:
        intended = serialize_v2_record(self.conversation(), self.schema)
        index = {"schema_version": 1, "records": []}
        with self.assertRaisesRegex(CatalogError, "intended-to-persisted"):
            recover_catalog_index({"message-001": "Return the form"}, intended, intended + b"x", index, self.facts())
        with self.assertRaisesRegex(CatalogError, "does not link"):
            recover_catalog_index({"message-001": "Return the form"}, intended, intended, index, [{"fact_id": "fact-stable-001", "record_id": "other"}])


if __name__ == "__main__":
    unittest.main()
