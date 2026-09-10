from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from school_os.codex_bridge import (  # noqa: E402
    BridgeError, HostBindingDispatcher, JsonlPeer, create_run_directory,
    normalize_tool_result,
)
from school_os.contracts import canonical_json_bytes, sha256_bytes  # noqa: E402


class CodexBridgeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.run_dir = create_run_directory(self.base, "run")

    def response(self, request_id: str, result: object) -> tuple[Path, str]:
        path = self.run_dir / f"{request_id}.response.json"
        data = canonical_json_bytes({"protocol": 1, "request_id": request_id, "result": result})
        path.write_bytes(data)
        os.chmod(path, 0o600)
        return path, sha256_bytes(data)

    def test_private_file_round_trip_consumes_dispatcher_validated_result(self) -> None:
        path, digest = self.response("r1", {"id": "file-1"})
        control = json.dumps({"request_id": "r1", "response_path": str(path), "sha256": digest}) + "\n"
        output = io.StringIO()
        peer = JsonlPeer(self.run_dir, input_stream=io.StringIO(control), output_stream=output)
        self.assertEqual({"id": "file-1"}, peer.connector_call("drive.get_metadata", {"fileId": "file-1"}, request_id="r1"))
        self.assertRegex(output.getvalue(), r"^SCHOOL_OS_REQUEST r1 drive\.get_metadata [0-9a-f]{64} ")
        self.assertFalse(path.exists())
        self.assertFalse((self.run_dir / "r1.request.json").exists())

    def test_rejects_arbitrary_kind_bad_args_mismatch_hash_wrapper_and_replay(self) -> None:
        peer = JsonlPeer(self.run_dir, input_stream=io.StringIO(), output_stream=io.StringIO())
        with self.assertRaisesRegex(BridgeError, "unexpected"):
            peer.call("tools.execute", {}, request_id="bad")
        with self.assertRaisesRegex(BridgeError, "argument keys"):
            peer.call("drive.get_metadata", {"fileId": "x", "tool_name": "evil"}, request_id="bad-args")

        path, digest = self.response("right", {})
        wrong = json.dumps({"request_id": "wrong", "response_path": str(path), "sha256": digest}) + "\n"
        with self.assertRaisesRegex(BridgeError, "mismatched"):
            JsonlPeer(self.run_dir, input_stream=io.StringIO(wrong), output_stream=io.StringIO()).call("drive.get_metadata", {"fileId": "x"}, request_id="right")

        path, _ = self.response("hash", {})
        bad_hash = json.dumps({"request_id": "hash", "response_path": str(path), "sha256": "0" * 64}) + "\n"
        with self.assertRaisesRegex(BridgeError, "hash"):
            JsonlPeer(self.run_dir, input_stream=io.StringIO(bad_hash), output_stream=io.StringIO()).call("drive.get_metadata", {"fileId": "x"}, request_id="hash")

        path = self.run_dir / "shape.response.json"
        data = canonical_json_bytes({"protocol": 1, "request_id": "shape", "result": {}, "verified": True})
        path.write_bytes(data); os.chmod(path, 0o600)
        control = json.dumps({"request_id": "shape", "response_path": str(path), "sha256": sha256_bytes(data)}) + "\n"
        with self.assertRaisesRegex(BridgeError, "wrapper"):
            JsonlPeer(self.run_dir, input_stream=io.StringIO(control), output_stream=io.StringIO()).call("drive.get_metadata", {"fileId": "x"}, request_id="shape")

    def test_response_writer_handles_large_exact_payload_and_rejects_truncation(self) -> None:
        payload = canonical_json_bytes({"protocol": 1, "request_id": "large", "result": {"raw": "Z" * 1048500}})
        path = self.run_dir / "large.response.json"
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "write_host_response.py"), str(self.run_dir), str(path), str(len(payload))],
            input=payload, capture_output=True, check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr.decode())
        self.assertEqual(payload, path.read_bytes())
        self.assertEqual(0o600, path.stat().st_mode & 0o777)
        truncated = self.run_dir / "truncated.response.json"
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "write_host_response.py"), str(self.run_dir), str(truncated), "10"],
            input=b"short", capture_output=True, check=False,
        )
        self.assertNotEqual(0, result.returncode)
        self.assertFalse(truncated.exists())

    def test_host_dispatch_script_preserves_the_reviewed_binding_boundary(self) -> None:
        request_id = "dispatch-1"
        request = {
            "args": {"parent_id": "root", "item_type": "folder", "topn": 100},
            "kind": "drive.search_page",
            "protocol": 1,
            "request_id": request_id,
        }
        request_path = self.run_dir / f"{request_id}.request.json"
        request_bytes = canonical_json_bytes(request)
        request_path.write_bytes(request_bytes)
        os.chmod(request_path, 0o600)
        native_result_path = self.run_dir / f"{request_id}.native-result.json"
        native_result = canonical_json_bytes({
            "content": [],
            "structuredContent": {
                "result": {"results": [], "next_page_token": None},
            },
        })
        native_result_path.write_bytes(native_result)
        os.chmod(native_result_path, 0o600)
        control = json.dumps({
            "request_id": request_id,
            "native_result_path": str(native_result_path),
            "sha256": sha256_bytes(native_result),
        }) + "\n"
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "dispatch_host_request.py"),
                "--run-dir", str(self.run_dir),
                "--request-id", request_id,
                "--kind", "drive.search_page",
                "--request-sha256", sha256_bytes(request_bytes),
                "--request-path", str(request_path),
            ],
            input=control,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        lines = result.stdout.splitlines()
        self.assertRegex(lines[0], r"^SCHOOL_OS_NATIVE_REQUEST dispatch-1 [0-9a-f]{64} ")
        response_control = json.loads(lines[-1])
        response = json.loads(Path(response_control["response_path"]).read_text())
        self.assertEqual({"results": [], "next_page_token": None}, response["result"])
        self.assertFalse(native_result_path.exists())
        self.assertFalse((self.run_dir / f"{request_id}.native-request.json").exists())

    def test_host_dispatch_script_accepts_the_observed_flat_connector_envelope(self) -> None:
        request_id = "dispatch-flat"
        request = {
            "args": {"parent_id": "root", "item_type": "folder", "topn": 100},
            "kind": "drive.search_page",
            "protocol": 1,
            "request_id": request_id,
        }
        request_path = self.run_dir / f"{request_id}.request.json"
        request_bytes = canonical_json_bytes(request)
        request_path.write_bytes(request_bytes)
        os.chmod(request_path, 0o600)
        native_result_path = self.run_dir / f"{request_id}.native-result.json"
        native_result = canonical_json_bytes({
            "content": [],
            "structuredContent": {"results": [], "next_page_token": None},
        })
        native_result_path.write_bytes(native_result)
        os.chmod(native_result_path, 0o600)
        control = json.dumps({
            "request_id": request_id,
            "native_result_path": str(native_result_path),
            "sha256": sha256_bytes(native_result),
        }) + "\n"
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "dispatch_host_request.py"),
                "--run-dir", str(self.run_dir),
                "--request-id", request_id,
                "--kind", "drive.search_page",
                "--request-sha256", sha256_bytes(request_bytes),
                "--request-path", str(request_path),
            ],
            input=control,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        response_control = json.loads(result.stdout.splitlines()[-1])
        response = json.loads(Path(response_control["response_path"]).read_text())
        self.assertEqual({"results": [], "next_page_token": None}, response["result"])

    def test_tool_exception_wrapper_is_unknown_and_cannot_authorize_success(self) -> None:
        path = self.run_dir / "error.response.json"
        data = canonical_json_bytes({"protocol": 1, "request_id": "error", "error": {"class": "tool_exception", "effect": "unknown"}})
        path.write_bytes(data); os.chmod(path, 0o600)
        control = json.dumps({"request_id": "error", "response_path": str(path), "sha256": sha256_bytes(data)}) + "\n"
        with self.assertRaisesRegex(BridgeError, "unknown effects"):
            JsonlPeer(self.run_dir, input_stream=io.StringIO(control), output_stream=io.StringIO()).call("drive.get_metadata", {"fileId": "x"}, request_id="error")

    def test_flat_structured_content_is_accepted_but_text_only_is_not(self) -> None:
        self.assertEqual({"id": "flat"}, normalize_tool_result({
            "structuredContent": {"id": "flat"}, "content": [], "_meta": {"trace": "ignored"},
        }))
        with self.assertRaisesRegex(BridgeError, "lacks structuredContent"):
            normalize_tool_result({"content": [{"type": "text", "text": '{"id":"unsafe"}'}]})

    def test_attachment_dispatch_accepts_only_an_exact_redundant_structured_envelope(self) -> None:
        attachment = {
            "attachment_id": "attachment-1",
            "content": [],
            "content_truncated": False,
            "extraction_file_uri": None,
            "file_uri": {
                "download_url": "https://files.example/attachment-1",
                "file_id": "file-1",
                "file_name": "notice.pdf",
                "mime_type": "application/pdf",
            },
            "filename": "notice.pdf",
            "images": [],
            "message_id": "message-1",
            "mime_type": "application/pdf",
            "size_bytes": 42,
        }
        dispatcher = HostBindingDispatcher()
        args = {"message_id": "message-1", "attachment_id": "attachment-1"}
        observed = {**attachment, "structuredContent": dict(attachment)}
        self.assertEqual(
            attachment,
            dispatcher.dispatch(
                "gmail.read_attachment", args,
                lambda _tool, _args: {"content": [], "structuredContent": observed},
            ),
        )
        nested = {**attachment, "structuredContent": {"result": dict(attachment)}}
        self.assertEqual(
            attachment,
            dispatcher.dispatch(
                "gmail.read_attachment", args,
                lambda _tool, _args: {"content": [], "structuredContent": nested},
            ),
        )
        conflicting = dict(attachment)
        conflicting["filename"] = "other.pdf"
        with self.assertRaisesRegex(BridgeError, "conflicts"):
            dispatcher.dispatch(
                "gmail.read_attachment", args,
                lambda _tool, _args: {
                    "content": [],
                    "structuredContent": {
                        **attachment, "structuredContent": conflicting,
                    },
                },
            )
        with self.assertRaisesRegex(BridgeError, "malformed"):
            dispatcher.dispatch(
                "gmail.read_attachment", args,
                lambda _tool, _args: {
                    "content": [],
                    "structuredContent": {
                        **attachment, "unexpected": True,
                        "structuredContent": dict(attachment),
                    },
                },
            )

    def test_semantic_response_rejects_nonfinite_json(self) -> None:
        path = self.run_dir / "nan.response.json"
        data = b'{"protocol":1,"request_id":"nan","result":{"score":NaN}}\n'
        path.write_bytes(data)
        os.chmod(path, 0o600)
        control = json.dumps({
            "request_id": "nan", "response_path": str(path), "sha256": sha256_bytes(data),
        }) + "\n"
        peer = JsonlPeer(self.run_dir, input_stream=io.StringIO(control), output_stream=io.StringIO())
        with self.assertRaisesRegex(BridgeError, "not finite JSON"):
            peer.call("semantic.interpret", {"packet": {}}, request_id="nan")


if __name__ == "__main__":
    unittest.main()
