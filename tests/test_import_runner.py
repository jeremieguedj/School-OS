from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from school_os.adapters import Page, ReadResult
from school_os.catalog import serialize_v2_record, validate_source_to_record, verify_persisted_record
from school_os.importer import AttachmentExtraction, DirectResourceRead, ImportError, admit_exact_plaintext_representation, discover_direct_html_resources, enumerate_conversations, next_import_batch, process_attachments, process_direct_html_resources, require_message_source_coverage


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
        self.assertEqual(outcomes[0].original_content_sha256, outcomes[0].extracted_text_sha256)
        self.assertEqual({"kind": "extracted_text_span", "byte_start": 0, "byte_end": 11}, outcomes[0].locator)
        self.assertIsNone(outcomes[1].text)
        self.assertIsNone(outcomes[2].text)

    def test_selected_plaintext_admission_decodes_strictly_and_round_trips_catalogue(self) -> None:
        def part(data: bytes, *, part_id: str = "body", encoding: str = "identity", charset: str = "utf-8") -> dict:
            return {
                "part_id": part_id, "role": "body", "selected_plaintext": True,
                "complete": True, "mime_type": "text/plain", "charset": charset,
                "content_transfer_encoding": encoding, "data": data,
            }

        admissions = (
            admit_exact_plaintext_representation((part(b"Exact\r\n"),)),
            admit_exact_plaintext_representation((part(b"caf=E9", encoding="quoted-printable", charset="iso-8859-1"),)),
            admit_exact_plaintext_representation((part(b"Y2Fmw6k=", encoding="base64"),)),
            admit_exact_plaintext_representation((
                part(b"Plain alternative"),
                {"part_id": "html", "role": "body", "selected_plaintext": False, "complete": True, "mime_type": "text/html", "charset": "utf-8", "content_transfer_encoding": "identity", "data": b"<p>Plain alternative</p>"},
                {"part_id": "attachment", "role": "attachment", "selected_plaintext": False, "complete": True, "mime_type": "application/pdf", "charset": "binary", "content_transfer_encoding": "base64", "data": b"cGRm"},
            )),
        )
        self.assertEqual(["admitted"] * 4, [item.outcome for item in admissions])
        self.assertEqual([b"Exact\r\n", "café".encode("utf-8"), "café".encode("utf-8"), b"Plain alternative"], [item.plaintext for item in admissions])
        self.assertEqual("body", admissions[3].selected_part_id)

        body = admissions[1].plaintext.decode("utf-8")
        conversation = {
            "schema_version": 1, "adapter_id": "synthetic-mail", "conversation_id": "decoded-001",
            "scope": {"fixed": True}, "pagination": {"completed": True},
            "messages": [{"message_id": "message-001", "received_at": "2026-09-08T00:00:00Z", "body": body, "attachments": []}],
        }
        schema = json.loads((ROOT / "schemas" / "source-conversation.schema.json").read_text(encoding="utf-8"))
        intended = serialize_v2_record(conversation, schema)
        self.assertEqual([], validate_source_to_record(intended, {"message-001": body}))
        verify_persisted_record({"message-001": body}, intended, intended)

    def test_source_admission_blocks_ambiguous_lossy_or_incomplete_mime_before_catalogue(self) -> None:
        selected = {"part_id": "body", "role": "body", "selected_plaintext": True, "complete": True, "mime_type": "text/plain", "charset": "utf-8", "content_transfer_encoding": "identity", "data": b"same"}
        cases = (
            (selected, {"part_id": "other", "role": "body", "selected_plaintext": False, "complete": True, "mime_type": "text/plain", "charset": "utf-8", "content_transfer_encoding": "identity", "data": b"other"}),
            ({"part_id": "html", "role": "body", "selected_plaintext": False, "complete": True, "mime_type": "text/html", "charset": "utf-8", "content_transfer_encoding": "identity", "data": b"<p>only</p>"},),
            ({**selected, "complete": False},),
            ({**selected, "content_transfer_encoding": "base64", "data": b"not*base64"},),
            ({**selected, "charset": "utf-8", "data": b"\xff"},),
            ({**selected, "content_transfer_encoding": "quoted-printable", "data": b"bad=Q"},),
            ({**selected, "data": None},),
        )
        outcomes = [admit_exact_plaintext_representation(parts) for parts in cases]
        outcomes.append(admit_exact_plaintext_representation((selected,), mime_tree_complete=False))
        self.assertTrue(all(outcome.outcome in {"unsupported", "manual_review"} for outcome in outcomes))
        self.assertTrue(all(outcome.plaintext is None for outcome in outcomes))
        self.assertEqual(outcomes[0], admit_exact_plaintext_representation(cases[0]))

    def test_selected_pdf_or_image_extraction_requires_a_provenance_locator(self) -> None:
        raw = {"agenda": b"%PDF-raw", "image": b"jpeg-raw", "bad": b"broken"}

        def read_attachment(identity: str) -> ReadResult:
            mime = "application/pdf" if identity in {"agenda", "bad"} else "image/jpeg"
            return ReadResult(raw[identity], identity, "file", None, mime, "1")

        def pdf(result: ReadResult) -> AttachmentExtraction:
            return AttachmentExtraction("Return form", {"kind": "provider_page_region", "page": 1, "region": "body"})

        def image(_result: ReadResult) -> AttachmentExtraction:
            return AttachmentExtraction("Image text", {"kind": "extracted_text_span", "byte_start": 0, "byte_end": 10})

        outcomes = process_attachments(
            (
                {"attachment_id": "agenda", "mime_type": "application/pdf", "byte_size": 8},
                {"attachment_id": "image", "mime_type": "image/jpeg", "byte_size": 8, "original_bytes_observed": False},
                {"attachment_id": "bad", "mime_type": "application/pdf", "byte_size": 6},
            ),
            read_attachment=read_attachment,
            supported_mime_types=("application/pdf", "image/jpeg"),
            max_bytes=20,
            extractors={"application/pdf": pdf, "image/jpeg": image},
        )
        self.assertEqual(["extracted", "extracted", "extracted"], [item.outcome for item in outcomes])
        self.assertNotEqual(outcomes[0].original_content_sha256, outcomes[0].extracted_text_sha256)
        self.assertIsNone(outcomes[1].original_content_sha256)
        self.assertEqual("provider_page_region", outcomes[0].locator["kind"])

    def test_direct_html_resources_are_bounded_inventory_not_html_body_text(self) -> None:
        html = (
            b'<p>ignored as body text</p><img src="https://assets.example/notice.png">'
            b'<a href="https://assets.example/form.pdf">form</a>'
        )
        html_part = {
            "part_id": "html-1", "complete": True, "mime_type": "text/html",
            "charset": "utf-8", "content_transfer_encoding": "identity", "data": html,
        }
        resources = discover_direct_html_resources("message-001", html_part)
        self.assertEqual(["html_embedded", "html_linked"], [item.origin for item in resources])
        self.assertEqual(resources, discover_direct_html_resources("message-001", html_part))
        self.assertEqual(64, len(resources[0].html_part_sha256))
        self.assertNotEqual(resources[0].resource_id, resources[1].resource_id)

        payloads = {
            "https://assets.example/notice.png": DirectResourceRead(
                "https://assets.example/notice.png", ("https://assets.example/notice.png",),
                b"\x89PNG\r\n\x1a\nsource", "image/png",
            ),
            "https://assets.example/form.pdf": DirectResourceRead(
                "https://cdn.example/form.pdf", ("https://assets.example/form.pdf", "https://cdn.example/form.pdf"),
                b"%PDF-1.7 source", "application/pdf",
            ),
        }

        def extract_image(_read: DirectResourceRead) -> AttachmentExtraction:
            return AttachmentExtraction("Image statement", {"kind": "extracted_text_span", "byte_start": 0, "byte_end": 15})

        def extract_pdf(_read: DirectResourceRead) -> AttachmentExtraction:
            return AttachmentExtraction("PDF statement", {"kind": "provider_page_region", "page": 1, "region": "body"})

        outcomes = process_direct_html_resources(
            resources,
            fetch_resource=lambda url: payloads[url],
            extractors={"image/png": extract_image, "application/pdf": extract_pdf},
            max_bytes=64,
            max_redirects=1,
        )
        self.assertEqual(["extracted", "extracted"], [item.outcome for item in outcomes])
        self.assertEqual("html_embedded", outcomes[0].resource.origin)
        self.assertNotEqual(outcomes[0].original_content_sha256, outcomes[0].extracted_text_sha256)
        self.assertEqual("provider_page_region", outcomes[1].locator["kind"])
        require_message_source_coverage(b"", outcomes)

        with self.assertRaisesRegex(ImportError, "direct HTTPS"):
            discover_direct_html_resources("message-001", {**html_part, "data": b'<img src="http://assets.example/notice.png">'})
        blocked = process_direct_html_resources(
            resources[:1],
            fetch_resource=lambda _url: DirectResourceRead("https://assets.example/notice.png", ("https://assets.example/notice.png",), b"not an image", "image/png"),
            extractors={"image/png": extract_image},
            max_bytes=64,
            max_redirects=0,
        )
        self.assertEqual("manual_review", blocked[0].outcome)
        with self.assertRaisesRegex(ImportError, "coverage"):
            require_message_source_coverage(b"", blocked)


if __name__ == "__main__":
    unittest.main()
