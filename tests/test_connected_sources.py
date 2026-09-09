from __future__ import annotations

import base64
import io
import os
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))

from school_os.connected_sources import ConnectedSourceAdapters, ConnectedSourcesError, SourceHostHelpers
from school_os.codex_bridge import HostBindingDispatcher
from school_os.contracts import sha256_bytes
from PIL import Image
from pypdf import PdfWriter


def _png() -> bytes:
    output = io.BytesIO()
    Image.new("RGBA", (1, 1), (1, 2, 3, 255)).save(output, format="PNG")
    return output.getvalue()


PNG = _png()


class Peer:
    def __init__(self, run_directory: Path) -> None:
        self.run_directory = run_directory
        self.attachment: dict[str, object] | None = None
        self.fetch: dict[str, object] | None = None
        self.image_response: dict[str, object] | None = None
        self.calls: list[str] = []

    def connector_call(self, kind: str, _args: dict[str, object]) -> object:
        self.calls.append(kind)
        if kind == "gmail.read_attachment":
            return self.attachment
        if kind == "resource.fetch_https":
            return self.fetch
        raise AssertionError(kind)

    def call(self, kind: str, args: dict[str, object]) -> object:
        self.calls.append(kind)
        if kind != "extract.image":
            raise AssertionError(kind)
        self.image_response = {
            "source_id": args["source_id"], "mime_type": args["mime_type"],
            "original_sha256": args["original_sha256"], "byte_length": args["byte_length"],
            "width": args["width"], "height": args["height"], "complete": True, "text": "Visible school notice",
        }
        return self.image_response


class ConnectedSourcesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.run = Path(self.temporary.name) / "run"
        self.run.mkdir(mode=0o700)
        os.chmod(self.run, 0o700)
        self.peer = Peer(self.run)
        self.adapter = ConnectedSourceAdapters(peer=self.peer, run_directory=self.run)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_attachment_file_and_https_response_preserve_exact_original_bytes(self) -> None:
        attachment = self.run / "attachment.bin"
        attachment.write_bytes(PNG)
        os.chmod(attachment, 0o600)
        self.peer.attachment = {
            "message_id": "m1", "attachment_id": "a1", "mime_type": "image/png",
            "byte_size": len(PNG), "file_uri": str(attachment),
        }
        read = self.adapter.gmail_attachment("m1", "a1", mime_type="image/png", declared_byte_size=len(PNG))
        self.assertEqual(PNG, read.original_bytes)
        self.assertEqual(sha256_bytes(PNG), read.read_locator["sha256"])

        url = "https://assets.example/notice.png"
        self.peer.fetch = {
            "requested_url": url, "final_url": url, "redirect_chain": [url],
            "status_code": 200, "mime_type": "image/png", "content_encoding": "identity", "declared_content_length": len(PNG),
            "bytes_read": len(PNG), "eof": True, "complete": True,
            "b64_string": base64.b64encode(PNG).decode("ascii"),
        }
        resource = self.adapter.fetch_https(url)
        self.assertEqual(PNG, resource.data)
        self.assertEqual((url,), resource.redirect_chain)

    def test_image_request_revalidates_bytes_and_returns_one_complete_unit(self) -> None:
        extracted = self.adapter.extract_image(source_id="attachment-a1", data=PNG, mime_type="image/png")
        self.assertEqual("Visible school notice", extracted.text)
        self.assertEqual(("image:1",), extracted.complete_units)
        self.assertEqual({"kind": "provider_page_region", "page": 1, "region": "full_image"}, extracted.locator)
        self.assertFalse(any(self.run.iterdir()))

    def test_incomplete_or_identity_mismatched_host_bytes_fail_closed(self) -> None:
        url = "https://assets.example/notice.png"
        self.peer.fetch = {
            "requested_url": url, "final_url": url, "redirect_chain": [url],
            "status_code": 200, "mime_type": "image/png", "content_encoding": "identity", "declared_content_length": len(PNG),
            "bytes_read": len(PNG), "eof": True, "complete": False,
            "b64_string": base64.b64encode(PNG).decode("ascii"),
        }
        with self.assertRaisesRegex(ConnectedSourcesError, "complete bounded"):
            self.adapter.fetch_https(url)

        class BadPeer(Peer):
            def call(self, kind: str, args: dict[str, object]) -> object:
                response = super().call(kind, args)
                assert isinstance(response, dict)
                response["original_sha256"] = "0" * 64
                return response
        bad = ConnectedSourceAdapters(peer=BadPeer(self.run), run_directory=self.run)
        with self.assertRaisesRegex(ConnectedSourcesError, "exact identity"):
            bad.extract_image(source_id="attachment-a1", data=PNG, mime_type="image/png")

    def test_host_helper_rechecks_the_contained_original_before_viewing(self) -> None:
        path = self.run / "image.png"
        path.write_bytes(PNG)
        os.chmod(path, 0o600)
        observed: list[dict[str, object]] = []
        helper = SourceHostHelpers(
            fetch_https_impl=lambda args: args,
            extract_image_impl=lambda args: observed.append(dict(args)) or {"ok": True},
            run_directory=self.run,
        )
        helper.dispatch("extract.image", {
            "path": str(path), "source_id": "source-1", "mime_type": "image/png",
            "original_sha256": sha256_bytes(PNG), "byte_length": len(PNG), "width": 1, "height": 1,
        })
        self.assertEqual(1, len(observed))
        with self.assertRaisesRegex(ConnectedSourcesError, "different original"):
            helper.dispatch("extract.image", {
                "path": str(path), "source_id": "source-1", "mime_type": "image/png",
                "original_sha256": "0" * 64, "byte_length": len(PNG), "width": 1, "height": 1,
            })
        with self.assertRaisesRegex(ConnectedSourcesError, "unsupported shape"):
            helper.dispatch("extract.image", {
                "path": str(path), "source_id": "source-1", "mime_type": "image/png",
                "original_sha256": sha256_bytes(PNG), "byte_length": len(PNG), "width": 1, "height": 1,
                "unbounded": True,
            })

    def test_pdf_renders_each_page_through_the_bounded_image_callback(self) -> None:
        output = io.BytesIO()
        writer = PdfWriter()
        writer.add_blank_page(width=72, height=72)
        writer.add_blank_page(width=72, height=72)
        writer.write(output)
        extracted = self.adapter.extract_pdf(source_id="attachment-pdf", data=output.getvalue())
        self.assertEqual(("page:1", "page:2"), extracted.complete_units)
        self.assertEqual(2, extracted.unit_count)
        self.assertEqual("extracted_text_span", extracted.locator["kind"])
        self.assertEqual(["extract.image", "extract.image"], self.peer.calls)

    def test_host_dispatch_union_exposes_only_the_two_named_source_helpers(self) -> None:
        calls: list[tuple[str, dict[str, object]]] = []
        result = HostBindingDispatcher().dispatch(
            "resource.fetch_https",
            {"url": "https://assets.example/file.pdf", "max_bytes": 1024, "max_redirects": 1, "timeout_ms": 1000},
            lambda name, args: calls.append((name, args)) or {"structuredContent": {"result": {"ok": True}}},
        )
        self.assertTrue(result["structuredContent"]["result"]["ok"])
        self.assertEqual("resource.fetch_https", calls[0][0])


if __name__ == "__main__":
    unittest.main()
