from __future__ import annotations

import base64
import hashlib
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from school_os.gmail_source import GmailMimeNormalizer, GmailSourceError, decode_raw_rfc2822
from school_os.importer import admit_exact_plaintext_representation, discover_direct_html_resources


def encoded(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def headers(mime: str, *, charset: str | None = None, transfer: str | None = None, disposition: str | None = None) -> list[dict[str, str]]:
    content_type = mime if charset is None else f'{mime}; charset="{charset}"'
    result = [{"name": "Content-Type", "value": content_type}]
    if transfer is not None:
        result.append({"name": "Content-Transfer-Encoding", "value": transfer})
    if disposition is not None:
        result.append({"name": "Content-Disposition", "value": disposition})
    return result


def leaf(part_id: str, mime: str, content: str | None, size: int, *, charset: str | None = "utf-8", filename: str = "", attachment_id: str | None = None, supported: bool | None = None, transfer: str = "base64") -> dict:
    return {
        "part_id": "" if part_id == "root" else part_id, "mime_type": mime, "filename": filename,
        "headers": headers(mime, charset=charset, transfer=transfer, disposition=f"attachment; filename={filename}" if attachment_id or filename else None),
        "body": {"size": size, "base64_url_content": None, "content": content, "attachment_id": attachment_id},
        "read_attachment_supported": supported, "parts": None,
    }


def full(payload: dict, *, identifier: str = "message-1", thread: str = "thread-1", date: str = "1777969800000") -> dict:
    return {"id": identifier, "thread_id": thread, "internal_date": date, "payload": payload}


def raw(value: bytes, *, identifier: str = "message-1", thread: str = "thread-1") -> dict:
    return {"id": identifier, "thread_id": thread, "raw": encoded(value)}


class GmailMimeNormalizerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.normalizer = GmailMimeNormalizer("America/Los_Angeles")

    def test_raw_rfc2822_accepts_only_canonical_urlsafe_padding(self) -> None:
        source = b"f"
        padded = base64.urlsafe_b64encode(source).decode("ascii")
        self.assertTrue(padded.endswith("="))
        self.assertEqual(source, decode_raw_rfc2822(padded))
        self.assertEqual(source, decode_raw_rfc2822(padded.rstrip("=")))
        for invalid in ("not+url", "Zg===", "Zg=Z", "Zg=\n"):
            with self.subTest(invalid=invalid):
                with self.assertRaisesRegex(GmailSourceError, "base64url"):
                    decode_raw_rfc2822(invalid)

    def test_normalizes_complete_multipart_plain_html_and_attachment_with_exact_custody(self) -> None:
        plain_transport = b"Y2Fmw6k="
        html_transport = (
            b"PGltZyBzcmM9Imh0dHBz"
            b"Oi8vYXNzZXRzLmV4YW1w"
            b"bGUvbm90aWNlLnBuZyI+"
        )
        attachment_transport = b"JVBERi0xLjQK"
        source = (
            b"From: school@example.invalid\r\n"
            b"Content-Type: multipart/mixed; boundary=outer\r\n\r\n"
            b"--outer\r\nContent-Type: multipart/alternative; boundary=alt\r\n\r\n"
            b"--alt\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Transfer-Encoding: base64\r\n\r\n" + plain_transport +
            b"\r\n--alt\r\nContent-Type: text/html; charset=utf-8\r\nContent-Transfer-Encoding: base64\r\n\r\n" + html_transport +
            b"\r\n--alt--\r\n--outer\r\nContent-Type: application/pdf\r\nContent-Disposition: attachment; filename=form.pdf\r\nContent-Transfer-Encoding: base64\r\n\r\n" + attachment_transport +
            b"\r\n--outer--\r\n"
        )
        payload = {
            "part_id": "", "mime_type": "multipart/mixed", "filename": "", "headers": headers("multipart/mixed"),
            "body": {"size": 0, "base64_url_content": None, "content": None, "attachment_id": None}, "read_attachment_supported": None,
            "parts": [{
                "part_id": "0", "mime_type": "multipart/alternative", "filename": "", "headers": headers("multipart/alternative"),
                "body": {"size": 0, "base64_url_content": None, "content": None, "attachment_id": None}, "read_attachment_supported": None,
                "parts": [
                    leaf("0.0", "text/plain", "café", len("café".encode())),
                    leaf("0.1", "text/html", '<img src="https://assets.example/notice.png">', len('<img src="https://assets.example/notice.png">'.encode())),
                ],
            }, leaf("1", "application/pdf", None, 9, charset=None, filename="form.pdf", attachment_id="attachment-1", supported=True)],
        }
        result = self.normalizer.normalize(full(payload), raw(source))
        self.assertEqual("2026-05-05T08:30:00Z", result["received_at"])
        self.assertEqual("2026-05-05", result["received_date"])
        self.assertEqual(1777969800000, result["gmail_internal_date_ms"])
        self.assertEqual(["0.0", "0.1", "1"], [part["part_id"] for part in result["parts"]])
        plain = result["parts"][0]
        self.assertTrue(plain["selected_plaintext"])
        self.assertEqual(plain_transport, plain["data"])
        self.assertEqual(hashlib.sha256(plain_transport).hexdigest(), plain["raw_part_sha256"])
        self.assertEqual("café", plain["provider_unicode"])
        self.assertEqual("admitted", admit_exact_plaintext_representation(result["parts"], mime_tree_complete=result["mime_tree_complete"]).outcome)
        self.assertEqual(1, len(result["html_parts"]))
        self.assertEqual("0.1", result["html_parts"][0]["part_id"])
        self.assertEqual(1, len(discover_direct_html_resources("message-1", result["html_parts"][0])))
        self.assertEqual([{
            "attachment_id": "attachment-1", "mime_type": "application/pdf", "byte_size": 9,
            "filename": "form.pdf", "read_attachment_supported": True, "part_id": "1", "source_part_ordinal": 2,
        }], result["attachments"])

    def test_qp_charset_decoding_and_configured_local_date_are_exact(self) -> None:
        transport = b"caf=E9"
        source = (
            b"Content-Type: text/plain; charset=iso-8859-1\r\n"
            b"Content-Transfer-Encoding: quoted-printable\r\n\r\n" + transport
        )
        payload = leaf("root", "text/plain", "café", 4, charset="iso-8859-1", transfer="quoted-printable")
        result = self.normalizer.normalize(full(payload, date="1777968000000"), raw(source))
        self.assertEqual("2026-05-05T08:00:00Z", result["received_at"])
        self.assertEqual("2026-05-05", result["received_date"])
        self.assertEqual(1777968000000, result["gmail_internal_date_ms"])
        self.assertEqual(transport, result["parts"][0]["data"])

    def test_rejects_id_thread_raw_base64_ambiguous_plaintext_and_provider_mismatch(self) -> None:
        source = b"Content-Type: text/plain; charset=utf-8\r\nContent-Transfer-Encoding: base64\r\n\r\naGVsbG8="
        payload = leaf("root", "text/plain", "hello", 5)
        with self.assertRaisesRegex(GmailSourceError, "identity"):
            self.normalizer.normalize(full(payload), raw(source, identifier="other"))
        with self.assertRaisesRegex(GmailSourceError, "base64url"):
            self.normalizer.normalize(full(payload), {"id": "message-1", "thread_id": "thread-1", "raw": "not+url"})
        with self.assertRaisesRegex(GmailSourceError, "decoded byte size|provider content"):
            self.normalizer.normalize(full(leaf("root", "text/plain", "different", 9)), raw(source))

        multipart = (
            b"Content-Type: multipart/alternative; boundary=x\r\n\r\n"
            b"--x\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Transfer-Encoding: base64\r\n\r\nYQ=="
            b"\r\n--x\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Transfer-Encoding: base64\r\n\r\nYg==\r\n--x--\r\n"
        )
        alternative = {
            "part_id": "", "mime_type": "multipart/alternative", "filename": "", "headers": headers("multipart/alternative"),
            "body": {"size": 0, "base64_url_content": None, "content": None, "attachment_id": None}, "read_attachment_supported": None,
            "parts": [leaf("0", "text/plain", "a", 1), leaf("1", "text/plain", "b", 1)],
        }
        with self.assertRaisesRegex(GmailSourceError, "unique"):
            self.normalizer.normalize(full(alternative), raw(multipart))

    def test_attachment_never_uses_filename_as_an_identity_and_html_must_be_exact(self) -> None:
        attachment_raw = (
            b"Content-Type: application/pdf\r\nContent-Disposition: attachment; filename=form.pdf\r\n"
            b"Content-Transfer-Encoding: base64\r\n\r\nJVBERg=="
        )
        attachment = leaf("root", "application/pdf", None, 4, charset=None, filename="form.pdf", attachment_id=None, supported=True)
        with self.assertRaisesRegex(GmailSourceError, "attachment_id"):
            self.normalizer.normalize(full(attachment), raw(attachment_raw))

        html_raw = b"Content-Type: text/html; charset=utf-8\r\nContent-Transfer-Encoding: base64\r\n\r\nPHA+eDwvcD4="
        html = leaf("root", "text/html", "<p>different</p>", 8)
        with self.assertRaisesRegex(GmailSourceError, "provider content"):
            self.normalizer.normalize(full(html), raw(html_raw))

    def test_rejects_incomplete_raw_tree_and_conflicting_multipart_node_type(self) -> None:
        incomplete = (
            b"Content-Type: multipart/mixed; boundary=x\r\n\r\n"
            b"--x\r\nContent-Type: text/plain; charset=utf-8\r\n"
            b"Content-Transfer-Encoding: base64\r\n\r\naGVsbG8="
        )
        multipart = {
            "part_id": "", "mime_type": "multipart/mixed", "filename": "", "headers": headers("multipart/mixed"),
            "body": {"size": 0, "base64_url_content": None, "content": None, "attachment_id": None}, "read_attachment_supported": None,
            "parts": [leaf("0", "text/plain", "hello", 5)],
        }
        with self.assertRaisesRegex(GmailSourceError, "defects|incomplete"):
            self.normalizer.normalize(full(multipart), raw(incomplete))
        closed = incomplete + b"\r\n--x--\r\n"
        multipart["mime_type"] = "multipart/related"
        multipart["headers"] = headers("multipart/related")
        with self.assertRaisesRegex(GmailSourceError, "structure or type"):
            self.normalizer.normalize(full(multipart), raw(closed))

    def test_rejects_conflicting_attachment_metadata_and_headers(self) -> None:
        source = (
            b"Content-Type: multipart/mixed; boundary=x\r\n\r\n"
            b"--x\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Transfer-Encoding: base64\r\n\r\naGk=\r\n"
            b"--x\r\nContent-Type: application/pdf\r\nContent-Disposition: attachment; filename=actual.pdf\r\n"
            b"Content-Transfer-Encoding: base64\r\n\r\nJVBERg==\r\n--x--\r\n"
        )
        payload = {
            "part_id": "", "mime_type": "multipart/mixed", "filename": "", "headers": headers("multipart/mixed"),
            "body": {"size": 0, "base64_url_content": None, "content": None, "attachment_id": None}, "read_attachment_supported": None,
            "parts": [
                leaf("0", "text/plain", "hi", 2),
                leaf("1", "application/pdf", None, 999, charset=None, filename="different.pdf", attachment_id="att-1", supported=True),
            ],
        }
        with self.assertRaisesRegex(GmailSourceError, "technical headers|decoded byte size"):
            self.normalizer.normalize(full(payload), raw(source))

    def test_reconciles_headers_and_keeps_inline_binary_parts_visible(self) -> None:
        latin1 = (
            b"Content-Type: text/plain; charset=iso-8859-1\r\n"
            b"Content-Transfer-Encoding: quoted-printable\r\n\r\ncaf=E9"
        )
        with self.assertRaisesRegex(GmailSourceError, "technical headers"):
            self.normalizer.normalize(full(leaf("root", "text/plain", "café", 4)), raw(latin1))

        source = (
            b"Content-Type: multipart/related; boundary=x\r\n\r\n"
            b"--x\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Transfer-Encoding: base64\r\n\r\naGk=\r\n"
            b"--x\r\nContent-Type: image/png\r\nContent-Disposition: inline\r\n"
            b"Content-Transfer-Encoding: base64\r\n\r\niVBORw0KGgo=\r\n--x--\r\n"
        )
        binary = leaf("1", "image/png", None, 8, charset=None, attachment_id="inline-1", supported=True)
        binary["headers"] = headers("image/png", charset=None, transfer="base64", disposition="inline")
        binary["body"]["base64_url_content"] = "iVBORw0KGgo="
        payload = {
            "part_id": "", "mime_type": "multipart/related", "filename": "", "headers": headers("multipart/related"),
            "body": {"size": 0, "base64_url_content": None, "content": None, "attachment_id": None}, "read_attachment_supported": None,
            "parts": [leaf("0", "text/plain", "hi", 2), binary],
        }
        normalized = self.normalizer.normalize(full(payload), raw(source))
        self.assertEqual(["inline-1"], [item["attachment_id"] for item in normalized["attachments"]])
        self.assertEqual("attachment", normalized["parts"][1]["role"])

        payload["parts"][1]["body"]["attachment_id"] = None
        with self.assertRaisesRegex(GmailSourceError, "attachment_id"):
            self.normalizer.normalize(full(payload), raw(source))

    def test_full_thread_keeps_provider_order_and_requires_exact_raw_membership(self) -> None:
        first_raw = b"Content-Type: text/plain; charset=utf-8\r\nContent-Transfer-Encoding: base64\r\n\r\nb25l"
        second_raw = b"Content-Type: text/plain; charset=utf-8\r\nContent-Transfer-Encoding: base64\r\n\r\ndHdv"
        first = full(leaf("root", "text/plain", "one", 3), identifier="message-1")
        second = full(leaf("root", "text/plain", "two", 3), identifier="message-2")
        thread = {"id": "thread-1", "messages": [first, second]}
        normalized = self.normalizer.normalize_thread(thread, {"message-1": raw(first_raw), "message-2": raw(second_raw, identifier="message-2")})
        self.assertEqual([0, 1], [item["source_message_ordinal"] for item in normalized["messages"]])
        with self.assertRaisesRegex(GmailSourceError, "no exact raw"):
            self.normalizer.normalize_thread(thread, {"message-1": raw(first_raw)})


if __name__ == "__main__":
    unittest.main()
