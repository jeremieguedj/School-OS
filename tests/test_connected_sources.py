from __future__ import annotations

import base64
import email.message
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))

from school_os.connected_sources import (
    BoundedHttpsFetcher, ConnectedSourceAdapters, ConnectedSourcesError,
    SourceBounds, SourceHostHelpers,
)
from school_os.codex_bridge import HostBindingDispatcher
from school_os.contracts import canonical_json_bytes, sha256_bytes
from scripts.run_source_host import complete_image as complete_host_image
from scripts.run_source_host import prepare as prepare_host_request


PNG = base64.b64decode(
    "".join((
        "iVBORw0K", "GgoAAAAN", "SUhEUgAA", "AAEAAAAB", "CAQAAAC1",
        "HAwCAAAA", "C0lEQVR4", "2mNk+A8A", "AQUBAScY", "42YAAAAA",
        "SUVORK5C", "YII=",
    ))
)
PDF = b"%PDF-1.7\n% dependency-free synthetic parser input\n"


class FakeBox:
    def __init__(self, width: float, height: float) -> None:
        self.left = 0
        self.bottom = 0
        self.right = width
        self.top = height


class FakeIndirect:
    def __init__(self, value: object) -> None:
        self.value = value

    def get_object(self) -> object:
        return self.value


class FakePage(dict):
    def __init__(self, width: float = 72, height: float = 72) -> None:
        super().__init__()
        self.mediabox = FakeBox(width, height)
        self.cropbox = FakeBox(width, height)


class FakeReader:
    def __init__(self, pages: list[FakePage], *, embedded: bool = False) -> None:
        self.is_encrypted = False
        self.pages = pages
        root: dict[str, object] = {}
        if embedded:
            root["/Names"] = FakeIndirect({"/EmbeddedFiles": object()})
        self.trailer = {"/Root": FakeIndirect(root)}


class FakeResponse:
    def __init__(self, status: int, headers: list[tuple[str, str]], body: bytes) -> None:
        self.status = status
        self.headers = email.message.Message()
        for name, value in headers:
            self.headers[name] = value
        self.body = body
        self.offset = 0

    def read(self, size: int) -> bytes:
        chunk = self.body[self.offset:self.offset + size]
        self.offset += len(chunk)
        return chunk


class FakeConnection:
    def __init__(self, response: FakeResponse) -> None:
        self.response = response
        self.request_args: tuple[object, ...] | None = None
        self.sock = None

    def request(self, *args: object, **kwargs: object) -> None:
        self.request_args = args + (kwargs,)

    def getresponse(self) -> FakeResponse:
        return self.response

    def close(self) -> None:
        pass


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
        raise AssertionError(kind)

    def call(self, kind: str, args: dict[str, object]) -> object:
        self.calls.append(kind)
        if kind == "resource.fetch_https":
            return self.fetch
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
        self.image_probe = patch("school_os.connected_sources._image_details", return_value=(1, 1))
        self.image_probe.start()
        self.addCleanup(self.image_probe.stop)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_attachment_file_and_https_response_preserve_exact_original_bytes(self) -> None:
        download_url = "https://files.example/attachment.png"
        self.peer.attachment = {
            "message_id": "m1", "attachment_id": "a1", "mime_type": "image/png",
            "filename": "notice.png", "size_bytes": len(PNG),
            "content": [{"preview": "not evidence"}], "images": [], "content_truncated": True,
            "file_uri": {"download_url": download_url, "file_id": "f1", "file_name": "notice.png", "mime_type": "image/png"},
            "extraction_file_uri": {"download_url": "https://files.example/extraction.json", "file_id": "e1", "mime_type": "application/json"},
        }
        self.peer.fetch = {
            "requested_url": download_url, "final_url": download_url, "redirect_chain": [download_url],
            "status_code": 200, "mime_type": "image/png", "content_encoding": "identity",
            "declared_content_length": len(PNG), "bytes_read": len(PNG), "eof": True,
            "complete": True, "b64_string": base64.b64encode(PNG).decode("ascii"),
        }
        read = self.adapter.gmail_attachment("m1", "a1", mime_type="image/png", declared_byte_size=len(PNG))
        self.assertEqual(PNG, read.original_bytes)
        self.assertEqual(sha256_bytes(PNG), read.read_locator["sha256"])
        self.assertTrue(read.read_locator["provider_preview_ignored"])
        self.assertEqual(["gmail.read_attachment", "resource.fetch_https"], self.peer.calls)

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

    def test_concrete_https_fetcher_enforces_redirect_eof_limit_and_public_dns(self) -> None:
        responses = [
            FakeResponse(302, [("Location", "https://cdn.example/file")], b""),
            FakeResponse(200, [("Content-Type", "image/png"), ("Content-Length", str(len(PNG)))], PNG),
        ]
        connections: list[FakeConnection] = []

        def factory(_host: str, _port: int, _address: str, _timeout: float) -> FakeConnection:
            connection = FakeConnection(responses.pop(0))
            connections.append(connection)
            return connection

        resolver = lambda *_args, **_kwargs: [(2, 1, 6, "", ("93.184.216.34", 443))]
        fetch = BoundedHttpsFetcher(resolver=resolver, connection_factory=factory)
        result = fetch({"url": "https://assets.example/file", "max_bytes": len(PNG), "max_redirects": 1, "timeout_ms": 1000})
        self.assertEqual(["https://assets.example/file", "https://cdn.example/file"], result["redirect_chain"])
        self.assertEqual(base64.b64encode(PNG).decode("ascii"), result["b64_string"])
        self.assertEqual("identity", connections[0].request_args[-1]["headers"]["Accept-Encoding"])

        overflow = BoundedHttpsFetcher(
            resolver=resolver,
            connection_factory=lambda *_args: FakeConnection(FakeResponse(200, [("Content-Type", "image/png")], PNG + b"x")),
        )
        with self.assertRaisesRegex(ConnectedSourcesError, "byte bound"):
            overflow({"url": "https://assets.example/file", "max_bytes": len(PNG), "max_redirects": 0, "timeout_ms": 1000})

        private = BoundedHttpsFetcher(
            resolver=lambda *_args, **_kwargs: [(2, 1, 6, "", ("127.0.0.1", 443))],
            connection_factory=lambda *_args: self.fail("private DNS must block before connect"),
        )
        with self.assertRaisesRegex(ConnectedSourcesError, "public address"):
            private({"url": "https://localhost/file", "max_bytes": 10, "max_redirects": 0, "timeout_ms": 1000})

        short = BoundedHttpsFetcher(
            resolver=resolver,
            connection_factory=lambda *_args: FakeConnection(FakeResponse(200, [("Content-Type", "image/png"), ("Content-Length", "99")], PNG)),
        )
        with self.assertRaisesRegex(ConnectedSourcesError, "declared byte length"):
            short({"url": "https://assets.example/file", "max_bytes": 100, "max_redirects": 0, "timeout_ms": 1000})

        clock_values = iter((0.0, 2.0))
        expired = BoundedHttpsFetcher(
            resolver=resolver, connection_factory=lambda *_args: self.fail("deadline must block before connect"),
            clock=lambda: next(clock_values),
        )
        with self.assertRaisesRegex(ConnectedSourcesError, "deadline"):
            expired({"url": "https://assets.example/file", "max_bytes": 100, "max_redirects": 0, "timeout_ms": 1000})

        redirect_limited = BoundedHttpsFetcher(
            resolver=resolver,
            connection_factory=lambda *_args: FakeConnection(FakeResponse(302, [("Location", "https://cdn.example/file")], b"")),
        )
        with self.assertRaisesRegex(ConnectedSourcesError, "redirect"):
            redirect_limited({"url": "https://assets.example/file", "max_bytes": 100, "max_redirects": 0, "timeout_ms": 1000})

    def test_host_helper_rechecks_the_contained_original_before_viewing(self) -> None:
        path = self.run / "image.png"
        path.write_bytes(PNG)
        os.chmod(path, 0o600)
        helper = SourceHostHelpers(run_directory=self.run)
        args = {
            "path": str(path), "source_id": "source-1", "mime_type": "image/png",
            "original_sha256": sha256_bytes(PNG), "byte_length": len(PNG), "width": 1, "height": 1,
        }
        handoff = helper.prepare_image(args)
        self.assertEqual({"path": handoff["stable_copy"]["path"], "detail": "original"}, handoff["arguments"])
        result = helper.complete_image(handoff, "Visible school notice")
        self.assertEqual(sha256_bytes(PNG), result["original_sha256"])
        helper.cleanup_image(handoff)
        with self.assertRaisesRegex(ConnectedSourcesError, "different original"):
            helper.prepare_image({
                "path": str(path), "source_id": "source-1", "mime_type": "image/png",
                "original_sha256": "0" * 64, "byte_length": len(PNG), "width": 1, "height": 1,
            })
        with self.assertRaisesRegex(ConnectedSourcesError, "unsupported shape"):
            helper.prepare_image({
                "path": str(path), "source_id": "source-1", "mime_type": "image/png",
                "original_sha256": sha256_bytes(PNG), "byte_length": len(PNG), "width": 1, "height": 1,
                "unbounded": True,
            })

    def test_host_owned_image_copy_must_stay_byte_and_inode_stable(self) -> None:
        path = self.run / "image.png"
        path.write_bytes(PNG)
        os.chmod(path, 0o600)
        helper = SourceHostHelpers(self.run)
        handoff = helper.prepare_image({
            "path": str(path), "source_id": "source-1", "mime_type": "image/png",
            "original_sha256": sha256_bytes(PNG), "byte_length": len(PNG), "width": 1, "height": 1,
        })
        stable = Path(handoff["stable_copy"]["path"])
        stable.write_bytes(PNG + b"changed")
        with self.assertRaisesRegex(ConnectedSourcesError, "changed between"):
            helper.complete_image(handoff, "invented text")
        helper.cleanup_image(handoff)

    def test_pdf_renders_each_page_through_the_bounded_image_callback(self) -> None:
        def fake_run(command: list[str], **_kwargs: object) -> None:
            Path(command[-1] + ".png").write_bytes(PNG)

        reader = FakeReader([FakePage(), FakePage()])
        with patch("school_os.connected_sources._pdf_reader", return_value=reader), patch(
            "school_os.connected_sources.subprocess.run", side_effect=fake_run,
        ):
            extracted = self.adapter.extract_pdf(source_id="attachment-pdf", data=PDF)
        self.assertEqual(("page:1", "page:2"), extracted.complete_units)
        self.assertEqual(2, extracted.unit_count)
        self.assertEqual("extracted_text_span", extracted.locator["kind"])
        self.assertEqual(["extract.image", "extract.image"], self.peer.calls)

    def test_pdf_passes_precomputed_dimension_and_pixel_scale_to_renderer(self) -> None:
        bounds = SourceBounds(max_image_dimension=100, max_image_pixels=5_000)
        adapter = ConnectedSourceAdapters(peer=self.peer, run_directory=self.run, bounds=bounds)
        commands: list[list[str]] = []

        def fake_run(command: list[str], **_kwargs: object) -> None:
            commands.append(command)
            Path(command[-1] + ".png").write_bytes(PNG)

        with patch("school_os.connected_sources._pdf_reader", return_value=FakeReader([FakePage(720, 360)])), patch(
            "school_os.connected_sources.subprocess.run", side_effect=fake_run,
        ):
            adapter.extract_pdf(source_id="pdf", data=PDF)
        self.assertIn("-scale-to", commands[0])
        scale = int(commands[0][commands[0].index("-scale-to") + 1])
        self.assertLessEqual(scale, 100)
        self.assertLessEqual(scale * (scale // 2), 5_000)

    def test_pdf_rejects_oversized_page_box_before_renderer(self) -> None:
        with patch("school_os.connected_sources._pdf_reader", return_value=FakeReader([FakePage(20_000, 72)])), patch(
            "school_os.connected_sources.subprocess.run",
        ) as renderer:
            with self.assertRaisesRegex(ConnectedSourcesError, "pre-render"):
                self.adapter.extract_pdf(source_id="pdf", data=PDF)
        renderer.assert_not_called()

    def test_pdf_rejects_aggregate_pixel_plan_before_first_render(self) -> None:
        adapter = ConnectedSourceAdapters(
            peer=self.peer, run_directory=self.run,
            bounds=SourceBounds(max_image_pixels=1, max_image_dimension=1, max_pdf_rendered_pixels=1),
        )
        reader = FakeReader([FakePage(), FakePage()])
        with patch("school_os.connected_sources._pdf_reader", return_value=reader), patch(
            "school_os.connected_sources.subprocess.run",
        ) as renderer:
            with self.assertRaisesRegex(ConnectedSourcesError, "aggregate pre-render"):
                adapter.extract_pdf(source_id="pdf", data=PDF)
        renderer.assert_not_called()

    def test_pdf_rejects_embedded_files_without_reading_hidden_payload(self) -> None:
        with patch("school_os.connected_sources._pdf_reader", return_value=FakeReader([FakePage()], embedded=True)), patch(
            "school_os.connected_sources.subprocess.run",
        ) as renderer:
            with self.assertRaisesRegex(ConnectedSourcesError, "embedded files"):
                self.adapter.extract_pdf(source_id="pdf", data=PDF)
        renderer.assert_not_called()

    def test_module_import_is_dependency_free_and_missing_decoders_fail_closed(self) -> None:
        command = """
from school_os.connected_sources import ConnectedSourcesError, _image_details, _pdf_reader
for call in (
    lambda: _image_details(b'\\x89PNG\\r\\n\\x1a\\n', 'image/png', max_pixels=1, max_dimension=1),
    lambda: _pdf_reader(b'%PDF-1.7\\n'),
):
    try:
        call()
    except ConnectedSourcesError as exc:
        assert 'selected runtime lacks the qualified' in str(exc)
    else:
        raise AssertionError('optional decoder unexpectedly available under -S')
"""
        result = subprocess.run(
            [sys.executable, "-S", "-c", command], cwd=ROOT,
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr)

    def test_host_dispatch_union_exposes_only_the_two_named_source_helpers(self) -> None:
        url = "https://assets.example/file.pdf"
        raw = {"requested_url": url}
        helper = SourceHostHelpers(self.run, fetch_https_impl=lambda _args: raw)
        result = HostBindingDispatcher(source_helpers=helper).dispatch(
            "resource.fetch_https",
            {"url": url, "max_bytes": 1024, "max_redirects": 1, "timeout_ms": 1000},
            lambda _name, _args: self.fail("finite helpers must not use connector invocation"),
        )
        self.assertEqual(raw, result)

    def test_executable_image_host_loop_assembles_exact_bridge_response(self) -> None:
        image_path = self.run / "source.png"
        image_path.write_bytes(PNG)
        os.chmod(image_path, 0o600)
        request = {
            "protocol": 1, "request_id": "request-1", "kind": "extract.image",
            "args": {"path": str(image_path), "source_id": "source-1", "mime_type": "image/png", "original_sha256": sha256_bytes(PNG), "byte_length": len(PNG), "width": 1, "height": 1},
        }
        request_path = self.run / "request-1.request.json"
        request_bytes = canonical_json_bytes(request)
        request_path.write_bytes(request_bytes)
        os.chmod(request_path, 0o600)
        action = prepare_host_request(self.run, request_path, sha256_bytes(request_bytes))
        self.assertEqual("view_image", action["action"])
        self.assertEqual("original", action["arguments"]["detail"])
        view_result = self.run / "request-1.view-result.json"
        view_result.write_text(json.dumps({"detail": "original", "text": "Visible school notice"}), encoding="utf-8")
        os.chmod(view_result, 0o600)
        completed = complete_host_image(self.run, Path(action["state_path"]), view_result)
        response = json.loads(Path(completed["control"]["response_path"]).read_bytes())
        self.assertEqual("Visible school notice", response["result"]["text"])
        self.assertEqual(sha256_bytes(PNG), response["result"]["original_sha256"])

    def test_executable_https_host_loop_returns_raw_helper_result(self) -> None:
        url = "https://assets.example/source.png"
        request = {
            "protocol": 1, "request_id": "request-https", "kind": "resource.fetch_https",
            "args": {"url": url, "max_bytes": 1024, "max_redirects": 1, "timeout_ms": 1000},
        }
        request_path = self.run / "request-https.request.json"
        request_bytes = canonical_json_bytes(request)
        request_path.write_bytes(request_bytes)
        os.chmod(request_path, 0o600)
        raw = {
            "requested_url": url, "final_url": url, "redirect_chain": [url], "status_code": 200,
            "mime_type": "image/png", "content_encoding": "identity", "declared_content_length": len(PNG),
            "bytes_read": len(PNG), "eof": True, "complete": True,
            "b64_string": base64.b64encode(PNG).decode("ascii"),
        }
        helper = SourceHostHelpers(self.run, fetch_https_impl=lambda _args: raw)
        completed = prepare_host_request(self.run, request_path, sha256_bytes(request_bytes), helpers=helper)
        response = json.loads(Path(completed["control"]["response_path"]).read_bytes())
        self.assertEqual(raw, response["result"])
        self.assertNotIn("structuredContent", response["result"])


if __name__ == "__main__":
    unittest.main()
