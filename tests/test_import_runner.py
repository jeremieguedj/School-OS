from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from school_os.adapters import Page, ReadResult
from school_os.catalog import serialize_v2_record, validate_source_to_record, verify_persisted_record
from school_os.importer import AttachmentExtraction, AttachmentRead, DirectResourceRead, ImportError, admit_exact_plaintext_representation, discover_direct_html_resources, enumerate_conversations, next_import_batch, process_attachments, process_direct_html_resources, require_complete_message_coverage, require_message_source_coverage


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

    def test_policy_excluded_image_attachment_is_never_read(self) -> None:
        outcome, = process_attachments(
            ({
                "attachment_id": "image-attachment",
                "source_message_id": "message-1",
                "content_id": "banner-image",
                "mime_type": "image/webp",
                "byte_size": 4096,
            },),
            read_attachment=lambda _identity: self.fail(
                "policy-excluded image must not be fetched"
            ),
            supported_mime_types=(),
            excluded_mime_types={
                "image/*": "image ingestion is temporarily disabled",
            },
            max_bytes=8192,
        )
        self.assertEqual("excluded_by_policy", outcome.outcome)
        self.assertEqual("image/webp", outcome.mime_type)
        self.assertEqual("message-1", outcome.source_message_id)
        self.assertEqual("banner-image", outcome.content_id)
        self.assertIsNone(outcome.original_content_sha256)
        self.assertIsNone(outcome.extracted_text_sha256)
        self.assertIsNone(outcome.text)
        self.assertIsNone(outcome.read_evidence)
        require_complete_message_coverage(b"complete body", (outcome,), ())

    def test_policy_excluded_embedded_image_is_never_fetched(self) -> None:
        html = b'<img src="https://assets.example/banner.png">'
        resources = discover_direct_html_resources(
            "message-1",
            {
                "part_id": "html-1", "role": "body",
                "selected_plaintext": False, "complete": True,
                "mime_type": "text/html", "charset": "utf-8",
                "content_transfer_encoding": "identity",
                "data": html,
                "raw_part_sha256": __import__("hashlib").sha256(html).hexdigest(),
                "raw_part_byte_length": len(html),
                "raw_part_locator": {
                    "kind": "raw_part_bytes", "byte_start": 0,
                    "byte_end": len(html),
                },
                "provider_unicode": html.decode("utf-8"),
            },
        )
        self.assertEqual(1, len(resources))
        outcome, = process_direct_html_resources(
            resources,
            fetch_resource=lambda _url: self.fail(
                "policy-excluded embedded image must not be fetched"
            ),
            extractors={"image/png": lambda _read: self.fail(
                "policy-excluded embedded image must not be extracted"
            )},
            excluded_resources={
                resources[0].resource_id:
                    "image ingestion is temporarily disabled",
            },
            max_bytes=8192,
            max_redirects=0,
        )
        self.assertEqual("html_embedded", outcome.resource.origin)
        self.assertEqual("excluded_by_policy", outcome.outcome)
        self.assertIsNone(outcome.original_content_sha256)
        self.assertIsNone(outcome.text)
        require_complete_message_coverage(b"complete body", (), (outcome,))

    def test_selected_plaintext_admission_decodes_strictly_and_round_trips_catalogue(self) -> None:
        def part(data: bytes, *, part_id: str = "body", encoding: str = "identity", charset: str = "utf-8") -> dict:
            return {
                "part_id": part_id, "role": "body", "selected_plaintext": True,
                "complete": True, "mime_type": "text/plain", "charset": charset,
                "content_transfer_encoding": encoding, "data": data,
                "raw_part_sha256": __import__("hashlib").sha256(data).hexdigest(),
                "raw_part_byte_length": len(data),
                "raw_part_locator": {"kind": "raw_part_bytes", "byte_start": 0, "byte_end": len(data)},
                "provider_unicode": __import__("school_os.importer", fromlist=["_decode_declared_charset", "_decode_transport"])._decode_declared_charset(__import__("school_os.importer", fromlist=["_decode_transport"])._decode_transport(data, encoding), charset).decode("utf-8"),
            }

        admissions = (
            admit_exact_plaintext_representation((part(b"Exact\r\n"),), mime_tree_complete=True),
            admit_exact_plaintext_representation((part(b"caf=E9", encoding="quoted-printable", charset="iso-8859-1"),), mime_tree_complete=True),
            admit_exact_plaintext_representation((part(b"Y2Fmw6k=", encoding="base64"),), mime_tree_complete=True),
            admit_exact_plaintext_representation((
                part(b"Plain alternative"),
                {"part_id": "html", "role": "body", "selected_plaintext": False, "complete": True, "mime_type": "text/html", "charset": "utf-8", "content_transfer_encoding": "identity", "data": b"<p>Plain alternative</p>"},
                {"part_id": "attachment", "role": "attachment", "selected_plaintext": False, "complete": True, "mime_type": "application/pdf", "charset": "binary", "content_transfer_encoding": "base64", "data": b"cGRm"},
            ), mime_tree_complete=True),
        )
        self.assertEqual(["admitted"] * 4, [item.outcome for item in admissions])
        self.assertEqual([b"Exact\r\n", "café".encode("utf-8"), "café".encode("utf-8"), b"Plain alternative"], [item.plaintext for item in admissions])
        self.assertEqual("body", admissions[3].selected_part_id)

        literal = part("\ufffd".encode("utf-8"))
        self.assertEqual("admitted", admit_exact_plaintext_representation((literal,), mime_tree_complete=True).outcome)
        self.assertNotEqual("admitted", admit_exact_plaintext_representation(({**literal, "provider_unicode": "\ufffdx"},), mime_tree_complete=True).outcome)
        seven_bit = part(b"x", encoding="7bit")
        seven_bit.update({"data": b"\xff", "raw_part_sha256": __import__("hashlib").sha256(b"\xff").hexdigest(), "raw_part_byte_length": 1, "raw_part_locator": {"kind": "raw_part_bytes", "byte_start": 0, "byte_end": 1}})
        self.assertNotEqual("admitted", admit_exact_plaintext_representation((seven_bit,), mime_tree_complete=True).outcome)

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
        def selected_part(data: bytes = b"same", **updates) -> dict:
            value = {"part_id": "body", "role": "body", "selected_plaintext": True, "complete": True, "mime_type": "text/plain", "charset": "utf-8", "content_transfer_encoding": "identity", "data": data, "raw_part_sha256": __import__("hashlib").sha256(data).hexdigest(), "raw_part_byte_length": len(data), "raw_part_locator": {"kind": "raw_part_bytes", "byte_start": 0, "byte_end": len(data)}, "provider_unicode": data.decode("utf-8", errors="replace")}
            value.update(updates)
            return value
        selected = selected_part()
        cases = (
            (selected, {"part_id": "other", "role": "body", "selected_plaintext": False, "complete": True, "mime_type": "text/plain", "charset": "utf-8", "content_transfer_encoding": "identity", "data": b"other"}),
            ({"part_id": "html", "role": "body", "selected_plaintext": False, "complete": True, "mime_type": "text/html", "charset": "utf-8", "content_transfer_encoding": "identity", "data": b"<p>only</p>"},),
            ({**selected, "complete": False},),
            (selected_part(b"not*base64", content_transfer_encoding="base64"),),
            (selected_part(b"\xff", charset="utf-8"),),
            (selected_part(b"bad=Q", content_transfer_encoding="quoted-printable"),),
            ({**selected, "data": None},),
        )
        outcomes = [admit_exact_plaintext_representation(parts, mime_tree_complete=True) for parts in cases]
        outcomes.append(admit_exact_plaintext_representation((selected,), mime_tree_complete=False))
        self.assertTrue(all(outcome.outcome in {"unsupported", "manual_review"} for outcome in outcomes))
        self.assertTrue(all(outcome.plaintext is None for outcome in outcomes))
        self.assertEqual(outcomes[0], admit_exact_plaintext_representation(cases[0], mime_tree_complete=True))

    def test_selected_pdf_or_image_extraction_requires_a_provenance_locator(self) -> None:
        raw = {"agenda": b"%PDF-raw", "image": b"\xff\xd8\xffraw!!", "bad": b"%PDF-b"}

        def read_attachment(identity: str) -> ReadResult | AttachmentRead:
            mime = "application/pdf" if identity in {"agenda", "bad"} else "image/jpeg"
            if identity == "image":
                return AttachmentRead(
                    identity, mime, True, len(raw[identity]), None,
                    AttachmentExtraction("Image text", {"kind": "extracted_text_span", "byte_start": 0, "byte_end": 10}, ("image:1",), 1),
                    {"kind": "provider_attachment", "identity": identity}, "1",
                )
            return ReadResult(raw[identity], identity, "file", None, mime, "1")

        def pdf(result: ReadResult) -> AttachmentExtraction:
            if result.identity == "bad":
                return AttachmentExtraction("Incomplete", {"kind": "extracted_text_span", "byte_start": 0, "byte_end": 10}, ("page:1",), 2)
            return AttachmentExtraction("Return form", {"kind": "provider_page_region", "page": 1, "region": "body"}, ("page:1",), 1)

        outcomes = process_attachments(
            (
                {"attachment_id": "agenda", "mime_type": "application/pdf", "byte_size": 8},
                {"attachment_id": "image", "mime_type": "image/jpeg", "byte_size": 8},
                {"attachment_id": "bad", "mime_type": "application/pdf", "byte_size": 6},
            ),
            read_attachment=read_attachment,
            supported_mime_types=("application/pdf", "image/jpeg"),
            max_bytes=20,
            extractors={"application/pdf": pdf},
        )
        self.assertEqual(["extracted", "extracted", "manual_review"], [item.outcome for item in outcomes])
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
            "raw_part_sha256": __import__("hashlib").sha256(html).hexdigest(),
            "raw_part_byte_length": len(html),
            "raw_part_locator": {"kind": "raw_part_bytes", "byte_start": 0, "byte_end": len(html)},
            "provider_unicode": html.decode("utf-8"),
        }
        resources = discover_direct_html_resources("message-001", html_part)
        self.assertEqual(["html_embedded", "html_linked"], [item.origin for item in resources])
        self.assertEqual(resources, discover_direct_html_resources("message-001", html_part))
        self.assertEqual(64, len(resources[0].html_part_sha256))
        self.assertNotEqual(resources[0].resource_id, resources[1].resource_id)

        encoded_html = __import__("base64").b64encode(html)
        encoded_part = {
            **html_part,
            "content_transfer_encoding": "base64",
            "data": encoded_html,
            "raw_part_sha256": __import__("hashlib").sha256(encoded_html).hexdigest(),
            "raw_part_byte_length": len(encoded_html),
            "raw_part_locator": {"kind": "raw_part_bytes", "byte_start": 0, "byte_end": len(encoded_html)},
        }
        encoded_resources = discover_direct_html_resources("message-001", encoded_part)
        self.assertEqual(__import__("hashlib").sha256(encoded_html).hexdigest(), encoded_resources[0].html_part_sha256)
        self.assertEqual(__import__("hashlib").sha256(html).hexdigest(), encoded_resources[0].html_decoded_sha256)

        css_html = (
            b'<style>.plain { color: black } .font { src: url("https://assets.example/font.woff2") } '
            b'.hero { background-image: url("https://assets.example/hero.png") }</style>'
            b'<div style="background: url(\'https://assets.example/second.png\')">x</div>'
        )
        css_part = {
            **html_part,
            "data": css_html,
            "raw_part_sha256": __import__("hashlib").sha256(css_html).hexdigest(),
            "raw_part_byte_length": len(css_html),
            "raw_part_locator": {"kind": "raw_part_bytes", "byte_start": 0, "byte_end": len(css_html)},
            "provider_unicode": css_html.decode("utf-8"),
        }
        css_resources = discover_direct_html_resources("message-001", css_part)
        self.assertEqual(["style", "style"], [item.attribute for item in css_resources])
        self.assertEqual(2, len(css_resources))
        for invalid_css in (
            b'<style>@import "https://assets.example/theme.css";</style>',
            b'<div style="background: url(http://assets.example/hero.png)">x</div>',
            b'<div style="background: url(\'https://assets.example/hero.png\")">x</div>',
        ):
            invalid_part = {
                **html_part,
                "data": invalid_css,
                "raw_part_sha256": __import__("hashlib").sha256(invalid_css).hexdigest(),
                "raw_part_byte_length": len(invalid_css),
                "raw_part_locator": {"kind": "raw_part_bytes", "byte_start": 0, "byte_end": len(invalid_css)},
                "provider_unicode": invalid_css.decode("utf-8"),
            }
            with self.assertRaisesRegex(ImportError, "unrecognized resource-bearing"):
                discover_direct_html_resources("message-001", invalid_part)

        payloads = {
            "https://assets.example/notice.png": DirectResourceRead(
                "https://assets.example/notice.png", ("https://assets.example/notice.png",),
                b"\x89PNG\r\n\x1a\nsource", "image/png", 200, True, True, 14, 14,
            ),
            "https://assets.example/form.pdf": DirectResourceRead(
                "https://cdn.example/form.pdf", ("https://assets.example/form.pdf", "https://cdn.example/form.pdf"),
                b"%PDF-1.7 source", "application/pdf", 200, True, True, 15, 15,
            ),
        }

        def extract_image(_read: DirectResourceRead) -> AttachmentExtraction:
            return AttachmentExtraction("Image statement", {"kind": "extracted_text_span", "byte_start": 0, "byte_end": 15}, ("image:1",), 1)

        def extract_pdf(_read: DirectResourceRead) -> AttachmentExtraction:
            return AttachmentExtraction("PDF statement", {"kind": "provider_page_region", "page": 1, "region": "body"}, ("page:1",), 1)

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
            discover_direct_html_resources("message-001", {**html_part, "data": b'<img src="http://assets.example/notice.png">', "raw_part_sha256": __import__("hashlib").sha256(b'<img src="http://assets.example/notice.png">').hexdigest(), "raw_part_byte_length": len(b'<img src="http://assets.example/notice.png">'), "raw_part_locator": {"kind": "raw_part_bytes", "byte_start": 0, "byte_end": len(b'<img src="http://assets.example/notice.png">')}, "provider_unicode": '<img src="http://assets.example/notice.png">'})
        blocked = process_direct_html_resources(
            resources[:1],
            fetch_resource=lambda _url: DirectResourceRead("https://assets.example/notice.png", ("https://assets.example/notice.png",), b"not an image", "image/png", 200, True, True, 12, 12),
            extractors={"image/png": extract_image},
            max_bytes=64,
            max_redirects=0,
        )
        self.assertEqual("manual_review", blocked[0].outcome)
        gif = (
            b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff"
            b"!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00"
            b"\x00\x02\x02D\x01\x00;"
        )
        gif_outcome = process_direct_html_resources(
            resources[:1],
            fetch_resource=lambda _url: DirectResourceRead(
                "https://assets.example/notice.png",
                ("https://assets.example/notice.png",), gif, "image/gif",
                200, True, True, len(gif), len(gif),
            ),
            extractors={"image/gif": extract_image},
            max_bytes=64,
            max_redirects=0,
        )
        self.assertEqual("extracted", gif_outcome[0].outcome)
        mislabeled_png = process_direct_html_resources(
            resources[:1],
            fetch_resource=lambda _url: DirectResourceRead(
                "https://assets.example/notice.png",
                ("https://assets.example/notice.png",),
                b"\x89PNG\r\n\x1a\nsource", "image/gif",
                200, True, True, 14, 14,
            ),
            extractors={"image/png": extract_image},
            max_bytes=64,
            max_redirects=0,
        )
        self.assertEqual("extracted", mislabeled_png[0].outcome)
        self.assertEqual("image/gif", mislabeled_png[0].fetch_evidence["declared_mime_type"])
        self.assertEqual("image/png", mislabeled_png[0].fetch_evidence["verified_mime_type"])
        with self.assertRaisesRegex(ImportError, "coverage"):
            require_message_source_coverage(b"", blocked)
        with self.assertRaisesRegex(ImportError, "attachment coverage"):
            require_complete_message_coverage(b"body", (process_attachments(({"attachment_id": "missing", "mime_type": "text/plain", "byte_size": 1},), read_attachment=lambda _id: (_ for _ in ()).throw(OSError()), supported_mime_types=("text/plain",), max_bytes=4)[0],), outcomes)


if __name__ == "__main__":
    unittest.main()
