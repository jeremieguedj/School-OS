from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from school_os.adapters import Page, ReadResult
from school_os.importer import ImportError, admit_exact_plaintext_representation, enumerate_conversations, next_import_batch, process_attachments


class ImportRunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = json.loads((ROOT / "tests" / "synthetic-fixtures" / "alpha13" / "import-pages.json").read_text(encoding="utf-8"))

    def test_complete_multi_page_enumeration_accounts_for_every_item(self) -> None:
        pages = {page["token"]: page for page in self.fixture["pages"]}

        def search(token: str | None) -> Page:
            page = pages[token]
            return Page(tuple(page["items"]), page["next_page_token"])

        result = enumerate_conversations(search)
        self.assertEqual((None, "page-2"), result.page_tokens)
        self.assertEqual(["conversation-001", "conversation-002", "conversation-003"], [item["conversation_id"] for item in result.conversations])
        self.assertEqual(["included", "included", "included", "duplicate"], [item["outcome"] for item in result.dispositions])
        with self.assertRaisesRegex(ImportError, "repeated"):
            enumerate_conversations(lambda _token: Page((), "again"))

    def test_bounded_batches_resume_stably_without_truncating_one_conversation(self) -> None:
        conversations = [item for page in self.fixture["pages"] for item in page["items"] if item["conversation_id"] != "conversation-003" or page["token"] is None]
        first = next_import_batch(conversations, completed_ids=(), max_records=2, max_bytes=10)
        second = next_import_batch(conversations, completed_ids=first.completed_ids, max_records=2, max_bytes=10)
        self.assertEqual(["conversation-001", "conversation-002"], [item["conversation_id"] for item in first.conversations])
        self.assertEqual(["conversation-003"], [item["conversation_id"] for item in second.conversations])
        self.assertEqual((), second.remaining_ids)
        with self.assertRaisesRegex(ImportError, "cannot be truncated"):
            next_import_batch(conversations, completed_ids=("conversation-001", "conversation-002"), max_records=2, max_bytes=6)

    def test_supported_text_attachment_is_exact_and_unsupported_content_is_visible(self) -> None:
        contents = {"attachment-text": b"Bring forms"}

        def read_attachment(identity: str) -> ReadResult:
            return ReadResult(contents[identity], identity, "file", None, "text/plain", "1")

        outcomes = process_attachments(self.fixture["attachments"], read_attachment=read_attachment, supported_mime_types=("text/plain",), max_bytes=20)
        self.assertEqual(["extracted", "unsupported", "manual_review"], [item.outcome for item in outcomes])
        self.assertEqual("Bring forms", outcomes[0].text)
        self.assertIsNone(outcomes[1].text)
        self.assertIsNone(outcomes[2].text)

    def test_source_admission_blocks_alternative_or_unsupported_mime_content_before_catalogue(self) -> None:
        accepted = admit_exact_plaintext_representation(({
            "complete": True, "mime_type": "text/plain", "charset": "UTF-8", "content_transfer_encoding": "identity", "data": b"Exact\r\n",
        },))
        self.assertEqual("admitted", accepted.outcome)
        self.assertEqual(b"Exact\r\n", accepted.plaintext)

        equivalent_alternatives = (
            {"complete": True, "mime_type": "text/plain", "charset": "utf-8", "content_transfer_encoding": "identity", "data": b"same"},
            {"complete": True, "mime_type": "text/html", "charset": "utf-8", "content_transfer_encoding": "identity", "data": b"same"},
        )
        first = admit_exact_plaintext_representation(equivalent_alternatives)
        replay = admit_exact_plaintext_representation(equivalent_alternatives)
        self.assertEqual(("unsupported", "multiple available MIME representations", None), (first.outcome, first.reason, first.plaintext))
        self.assertEqual(first, replay)

        for parts in (
            tuple(reversed(equivalent_alternatives)),
            equivalent_alternatives + ({"complete": True, "mime_type": "image/png", "charset": "utf-8", "content_transfer_encoding": "identity", "data": b"image"},),
            ({"complete": True, "mime_type": "text/plain", "charset": "utf-8", "content_transfer_encoding": "quoted-printable", "data": b"text"},),
            ({"complete": True, "mime_type": "text/plain", "charset": "windows-1252", "content_transfer_encoding": "identity", "data": b"text"},),
            ({"complete": True, "mime_type": "text/plain", "charset": "utf-8", "content_transfer_encoding": "identity", "data": b"text"}, {"complete": True, "mime_type": "application/pdf", "charset": "utf-8", "content_transfer_encoding": "identity", "data": b"attachment"}),
        ):
            outcome = admit_exact_plaintext_representation(parts)
            self.assertIn(outcome.outcome, {"unsupported", "manual_review"})
            self.assertIsNone(outcome.plaintext)


if __name__ == "__main__":
    unittest.main()
