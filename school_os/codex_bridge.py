"""Finite private-file bridge between School-OS and an authenticated Codex host.

The terminal protocol deliberately carries only request metadata and response
metadata.  Provider arguments and results remain in mode-0600 files below one
mode-0700 run directory.  This module never accepts a tool name from input.
"""

from __future__ import annotations

import json
import os
import re
import stat
import sys
import uuid
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TextIO

from .contracts import canonical_json_bytes, sha256_bytes


class BridgeError(ValueError):
    """Raised when a bridge request or response cannot be trusted."""


PROTOCOL = 1
MAX_REQUEST_BYTES = 2 * 1024 * 1024
MAX_RESPONSE_BYTES = 16 * 1024 * 1024
REQUEST_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


@dataclass(frozen=True)
class RequestSpec:
    required: frozenset[str]
    optional: frozenset[str] = frozenset()


@dataclass(frozen=True)
class HostBinding:
    """One reviewed host capability; callers never provide the tool name."""

    tool_name: str


# This is the complete executable request union.  Adding a provider operation
# requires a code review and a new fixed entry; callers cannot name tools.
REQUEST_SPECS: dict[str, RequestSpec] = {
    "drive.get_metadata": RequestSpec(frozenset({"fileId"}), frozenset({"fields", "supportsAllDrives"})),
    "drive.fetch": RequestSpec(frozenset({"url"}), frozenset({"download_raw_file", "include_base64", "raw_export_mime_type"})),
    "drive.list_folder": RequestSpec(frozenset({"url", "top_k"})),
    "drive.create_folder": RequestSpec(frozenset({"name"}), frozenset({"parent_folder"})),
    "drive.upload_file": RequestSpec(frozenset({"file_uri", "file_sha256", "file_size_bytes"}), frozenset({"file_name", "mime_type", "parent_folder_id"})),
    "drive.update_file": RequestSpec(frozenset({"fileId", "file_uri", "file_sha256", "file_size_bytes"}), frozenset({"mime_type", "name", "addParents", "removeParents"})),
    "gmail.search_ids": RequestSpec(frozenset(), frozenset({"query", "label_ids", "max_results", "next_page_token"})),
    "gmail.read": RequestSpec(frozenset({"message_id", "format"})),
    "gmail.read_thread": RequestSpec(frozenset({"thread_id"}), frozenset({"max_messages"})),
    "gmail.read_attachment": RequestSpec(frozenset({"message_id"}), frozenset({"attachment_id", "filename"})),
    "gmail.send": RequestSpec(frozenset({"to", "subject", "payload"}), frozenset({"cc", "bcc", "from_address", "reply_message_id", "reply_to", "response_fields", "classification_label_values"})),
    "sheets.get_metadata": RequestSpec(frozenset(), frozenset({"spreadsheet_id", "spreadsheet_url", "charts_only", "include_conditional_format_rules"})),
    "sheets.get_cells": RequestSpec(frozenset({"ranges"}), frozenset({"spreadsheet_id", "spreadsheet_url", "cell_fields"})),
    "sheets.batch_update": RequestSpec(frozenset({"requests"}), frozenset({"spreadsheet_id", "spreadsheet_url", "include_spreadsheet_in_response", "response_include_grid_data", "response_ranges", "image_uris"})),
    "comments.read_spreadsheet": RequestSpec(frozenset(), frozenset({"spreadsheet_id", "spreadsheet_url", "include_deleted", "page_size", "page_token"})),
    "comments.write_file": RequestSpec(frozenset(), frozenset({"id", "url", "comments", "replies", "resolutions"})),
    "semantic.interpret": RequestSpec(frozenset({"packet"})),
    "semantic.audit": RequestSpec(frozenset({"packet", "interpretation"})),
}

# Kept next to the request union so host dispatch cannot broaden independently
# from child validation.  These names describe the current connector surface;
# availability still requires operation-specific observed capability evidence.
HOST_BINDINGS: dict[str, HostBinding] = {
    "drive.get_metadata": HostBinding("mcp__codex_apps__google_drive_get_file_metadata"),
    "drive.fetch": HostBinding("mcp__codex_apps__google_drive_fetch"),
    "drive.list_folder": HostBinding("mcp__codex_apps__google_drive_list_folder"),
    "drive.create_folder": HostBinding("mcp__codex_apps__google_drive_create_folder"),
    "drive.upload_file": HostBinding("mcp__codex_apps__google_drive_upload_file"),
    "drive.update_file": HostBinding("mcp__codex_apps__google_drive_update_file"),
    "gmail.search_ids": HostBinding("mcp__codex_apps__gmail_search_email_ids"),
    "gmail.read": HostBinding("mcp__codex_apps__gmail_read_email"),
    "gmail.read_thread": HostBinding("mcp__codex_apps__gmail_read_email_thread"),
    "gmail.read_attachment": HostBinding("mcp__codex_apps__gmail_read_attachment"),
    "gmail.send": HostBinding("mcp__codex_apps__gmail_send_email"),
    "sheets.get_metadata": HostBinding("mcp__codex_apps__google_drive_get_spreadsheet_metadata"),
    "sheets.get_cells": HostBinding("mcp__codex_apps__google_drive_get_spreadsheet_cells"),
    "sheets.batch_update": HostBinding("mcp__codex_apps__google_drive_batch_update_spreadsheet"),
    "comments.read_spreadsheet": HostBinding("mcp__codex_apps__google_drive_get_spreadsheet_comments"),
    "comments.write_file": HostBinding("mcp__codex_apps__google_drive_bulk_update_file_comments"),
    "semantic.interpret": HostBinding("semantic.interpret"),
    "semantic.audit": HostBinding("semantic.audit"),
}

# Captured from the connected-host capability inventory.  Keep this finite
# evidence adjacent to the bindings: a request kind may not silently start
# targeting a spelling which was never advertised by the host.
CAPTURED_HOST_CAPABILITIES: frozenset[str] = frozenset({
    "mcp__codex_apps__google_drive_get_file_metadata",
    "mcp__codex_apps__google_drive_fetch",
    "mcp__codex_apps__google_drive_list_folder",
    "mcp__codex_apps__google_drive_create_folder",
    "mcp__codex_apps__google_drive_upload_file",
    "mcp__codex_apps__google_drive_update_file",
    "mcp__codex_apps__gmail_search_email_ids",
    "mcp__codex_apps__gmail_read_email",
    "mcp__codex_apps__gmail_read_email_thread",
    "mcp__codex_apps__gmail_read_attachment",
    "mcp__codex_apps__gmail_send_email",
    "mcp__codex_apps__google_drive_get_spreadsheet_metadata",
    "mcp__codex_apps__google_drive_get_spreadsheet_cells",
    "mcp__codex_apps__google_drive_batch_update_spreadsheet",
    "mcp__codex_apps__google_drive_get_spreadsheet_comments",
    "mcp__codex_apps__google_drive_bulk_update_file_comments",
})


def _nonempty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise BridgeError(f"{label} must be a nonempty string")
    return value


def _positive_int(value: Any, label: str, *, allow_zero: bool = False) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < (0 if allow_zero else 1):
        raise BridgeError(f"{label} must be a {'nonnegative' if allow_zero else 'positive'} integer")
    return value


def _string_list(value: Any, label: str) -> None:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        raise BridgeError(f"{label} must be a list of nonempty strings")


def _exactly_one(args: Mapping[str, Any], *keys: str) -> None:
    if sum(key in args for key in keys) != 1:
        raise BridgeError(f"exactly one of {', '.join(keys)} is required")


def _json_safe(value: Any, label: str) -> None:
    try:
        json.dumps(value, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise BridgeError(f"{label} is not finite JSON") from exc


def _validate_request(kind: str, args: Mapping[str, Any]) -> None:
    spec = REQUEST_SPECS.get(kind)
    if spec is None or kind not in HOST_BINDINGS:
        raise BridgeError(f"unexpected bridge request kind: {kind}")
    if not isinstance(args, Mapping):
        raise BridgeError("bridge request args must be an object")
    keys = set(args)
    if not spec.required <= keys or not keys <= spec.required | spec.optional:
        raise BridgeError(f"invalid argument keys for {kind}")
    for key in ("fileId", "message_id", "thread_id", "attachment_id", "url", "name", "file_name", "mime_type", "parent_folder", "parent_folder_id", "query", "next_page_token", "page_token", "from_address", "reply_message_id", "reply_to"):
        if key in args:
            _nonempty_string(args[key], f"{kind}.{key}")
    for key in ("top_k", "max_results", "max_messages", "page_size"):
        if key in args:
            _positive_int(args[key], f"{kind}.{key}")
    for key in ("label_ids", "addParents", "removeParents", "ranges", "response_ranges", "image_uris"):
        if key in args:
            _string_list(args[key], f"{kind}.{key}")
    for key in ("download_raw_file", "include_base64", "charts_only", "include_conditional_format_rules", "include_deleted", "include_spreadsheet_in_response", "response_include_grid_data"):
        if key in args and not isinstance(args[key], bool):
            raise BridgeError(f"{kind}.{key} must be boolean")
    if kind in {"drive.upload_file", "drive.update_file"}:
        raw_path = args.get("file_uri")
        if not isinstance(raw_path, str) or not Path(raw_path).is_absolute():
            raise BridgeError("Drive write file_uri must be an absolute local path")
        digest = args.get("file_sha256")
        if not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
            raise BridgeError("Drive write file_sha256 must be a lowercase SHA-256 digest")
        _positive_int(args.get("file_size_bytes"), "Drive write file_size_bytes", allow_zero=True)
    if kind in {"sheets.get_metadata", "comments.read_spreadsheet"}:
        _exactly_one(args, "spreadsheet_id", "spreadsheet_url")
    if kind == "sheets.get_cells":
        _exactly_one(args, "spreadsheet_id", "spreadsheet_url")
    if kind == "sheets.batch_update":
        _exactly_one(args, "spreadsheet_id", "spreadsheet_url")
        if not isinstance(args["requests"], list):
            raise BridgeError("sheets.batch_update.requests must be a list")
    if kind == "gmail.read" and args.get("format") not in {"full", "metadata", "minimal", "raw"}:
        raise BridgeError("gmail.read.format is not an admitted Gmail format")
    if kind == "gmail.send":
        for key in ("to", "cc", "bcc"):
            if key in args:
                _string_list(args[key], f"gmail.send.{key}")
        if not isinstance(args["payload"], Mapping):
            raise BridgeError("gmail.send.payload must be an object")
    if kind.startswith("semantic."):
        for key, value in args.items():
            if not isinstance(value, Mapping):
                raise BridgeError(f"{kind}.{key} must be an object")
    _json_safe(args, "bridge request args")


def _validate_result(kind: str, result: Any) -> None:
    """Reject malformed connector replies before they cross the bridge."""
    if not isinstance(result, Mapping):
        raise BridgeError(f"{kind} result must be an object")
    if kind == "drive.get_metadata":
        for key in ("id", "mime_type", "url", "title", "modified_time"):
            _nonempty_string(result.get(key), f"{kind} result.{key}")
        _string_list(result.get("parent_ids"), f"{kind} result.parent_ids")
        mime_type = result["mime_type"]
        if mime_type != "application/vnd.google-apps.folder":
            _positive_int(result.get("size"), f"{kind} result.size", allow_zero=True)
    elif kind == "drive.fetch":
        _nonempty_string(result.get("id"), f"{kind} result.id")
        encoded = result.get("b64_string")
        if not isinstance(encoded, str):
            raise BridgeError("drive.fetch result.b64_string must be a string")
        try:
            raw = __import__("base64").b64decode(encoded, validate=True)
        except Exception as exc:  # binascii.Error is intentionally not host-facing.
            raise BridgeError("drive.fetch result b64_string is invalid") from exc
        if _positive_int(result.get("file_size_bytes"), f"{kind} result.file_size_bytes", allow_zero=True) != len(raw):
            raise BridgeError("drive.fetch result byte length disagrees with base64")
        if not isinstance(result.get("is_empty"), bool) or result["is_empty"] != (len(raw) == 0):
            raise BridgeError("drive.fetch result empty marker disagrees with bytes")
    elif kind == "drive.list_folder":
        if not isinstance(result.get("files"), list):
            raise BridgeError("drive.list_folder result.files must be a list")
    elif kind in {"drive.upload_file", "drive.update_file"}:
        if result.get("success") is not True:
            raise BridgeError(f"{kind} result lacks success evidence")
        for key in ("id", "mime_type", "url", "modified_time"):
            _nonempty_string(result.get(key), f"{kind} result.{key}")
        _string_list(result.get("parent_ids"), f"{kind} result.parent_ids")
    elif kind == "gmail.search_ids":
        _string_list(result.get("message_ids"), f"{kind} result.message_ids")
        token = result.get("next_page_token")
        if token is not None:
            _nonempty_string(token, f"{kind} result.next_page_token")
    elif kind == "gmail.read_thread":
        if not isinstance(result.get("messages"), list):
            raise BridgeError("gmail.read_thread result.messages must be a list")
    elif kind == "comments.read_spreadsheet":
        if not isinstance(result.get("comments"), list):
            raise BridgeError("comments.read_spreadsheet result.comments must be a list")
    _json_safe(result, "host binding result")


class HostBindingDispatcher:
    """Dispatch an already-validated request to exactly one reviewed binding."""

    def __init__(self, run_directory: Path | None = None) -> None:
        self.run_directory = _verify_run_directory(run_directory) if run_directory is not None else None

    def _validate_private_write(self, args: Mapping[str, Any]) -> None:
        if self.run_directory is None:
            raise BridgeError("Drive writes require an admitted private run directory")
        raw_path = Path(str(args["file_uri"]))
        try:
            relative = raw_path.relative_to(self.run_directory)
            if any(part in {"", ".", ".."} for part in relative.parts):
                raise ValueError("non-canonical private file path")
            checked = self.run_directory
            for part in relative.parts:
                checked = checked / part
                if stat.S_ISLNK(checked.lstat().st_mode):
                    raise ValueError("private file path contains a symlink")
            status = raw_path.lstat()
            resolved = raw_path.resolve(strict=True)
            resolved.relative_to(self.run_directory)
        except (OSError, ValueError) as exc:
            raise BridgeError("Drive write file_uri escapes the private run directory") from exc
        if stat.S_ISLNK(status.st_mode) or not stat.S_ISREG(status.st_mode) or stat.S_IMODE(status.st_mode) != 0o600:
            raise BridgeError("Drive write must use a mode-0600 non-symlink regular private file")
        data = resolved.read_bytes()
        if len(data) != args["file_size_bytes"] or sha256_bytes(data) != args["file_sha256"]:
            raise BridgeError("Drive write file identity, size, or hash changed before effect")

    def dispatch(self, kind: str, args: Mapping[str, Any], invoke: Any) -> Any:
        _validate_request(kind, args)
        if not callable(invoke):
            raise BridgeError("host binding invoker is unavailable")
        if kind in {"drive.upload_file", "drive.update_file"}:
            self._validate_private_write(args)
        result = invoke(HOST_BINDINGS[kind].tool_name, dict(args))
        _validate_result(kind, result)
        return result


def _contained(path: Path, root: Path) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise BridgeError("bridge path escapes the private run directory") from exc
    return resolved


def create_run_directory(parent: Path, name: str | None = None) -> Path:
    """Create one private bridge run directory without broadening permissions."""
    parent.mkdir(parents=True, exist_ok=True)
    run_dir = parent / (name or f"school-os-bridge-{uuid.uuid4().hex}")
    run_dir.mkdir(mode=0o700)
    os.chmod(run_dir, 0o700)
    return run_dir.resolve()


def _verify_run_directory(run_dir: Path) -> Path:
    if stat.S_ISLNK(run_dir.lstat().st_mode):
        raise BridgeError("bridge run directory must not be a symlink")
    resolved = run_dir.resolve(strict=True)
    mode = stat.S_IMODE(resolved.stat().st_mode)
    if not resolved.is_dir() or mode != 0o700:
        raise BridgeError("bridge run directory must exist with mode 0700")
    return resolved


def _exclusive_write(path: Path, data: bytes) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb", closefd=False) as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    finally:
        os.close(descriptor)


def normalize_tool_result(value: Any) -> Any:
    """Return structured connector data from observed CallToolResult shapes.

    Tool-level metadata may accompany ``structuredContent.result`` and is not
    semantic authorization.  A connector without machine-readable structured
    content blocks instead of falling back to model-facing text blocks.
    """
    if not isinstance(value, Mapping):
        raise BridgeError("host tool response must be an object")
    if value.get("isError") is True:
        raise BridgeError("host tool returned an error; effect outcome is unknown")
    structured = value.get("structuredContent")
    if not isinstance(structured, Mapping):
        raise BridgeError("host tool response lacks structuredContent")
    if "result" in structured:
        structured = structured["result"]
    _json_safe(structured, "normalized host result")
    return structured


class JsonlPeer:
    """Synchronous one-request-at-a-time bridge peer for a persistent PTY."""

    def __init__(
        self,
        run_dir: Path,
        *,
        input_stream: TextIO = sys.stdin,
        output_stream: TextIO = sys.stdout,
        max_request_bytes: int = MAX_REQUEST_BYTES,
        max_response_bytes: int = MAX_RESPONSE_BYTES,
    ) -> None:
        self.run_dir = _verify_run_directory(run_dir)
        self.input_stream = input_stream
        self.output_stream = output_stream
        self.max_request_bytes = max_request_bytes
        self.max_response_bytes = max_response_bytes
        self._issued: set[str] = set()
        self._consumed: set[str] = set()

    def call(self, kind: str, args: Mapping[str, Any], *, request_id: str | None = None) -> Any:
        _validate_request(kind, args)
        identifier = request_id or uuid.uuid4().hex
        if REQUEST_ID.fullmatch(identifier) is None or identifier in self._issued:
            raise BridgeError("bridge request_id is invalid or replayed")
        self._issued.add(identifier)
        request = {"args": dict(args), "kind": kind, "protocol": PROTOCOL, "request_id": identifier}
        request_bytes = canonical_json_bytes(request)
        if len(request_bytes) > self.max_request_bytes:
            raise BridgeError("bridge request exceeds the configured byte bound")
        request_path = self.run_dir / f"{identifier}.request.json"
        response_path: Path | None = None
        _exclusive_write(request_path, request_bytes)
        try:
            print(
                "SCHOOL_OS_REQUEST", identifier, kind, sha256_bytes(request_bytes), request_path,
                file=self.output_stream, flush=True,
            )
            line = self.input_stream.readline()
            if not line:
                raise BridgeError("host bridge closed before returning a response control")
            try:
                control = json.loads(line)
            except json.JSONDecodeError as exc:
                raise BridgeError("host response control is not JSON") from exc
            if not isinstance(control, dict) or set(control) != {"request_id", "response_path", "sha256"}:
                raise BridgeError("host response control has an invalid shape")
            if control["request_id"] != identifier or identifier in self._consumed:
                raise BridgeError("host response control is mismatched or replayed")
            if not isinstance(control["response_path"], str) or not isinstance(control["sha256"], str):
                raise BridgeError("host response control fields are invalid")
            response_path = _contained(Path(control["response_path"]), self.run_dir)
            if response_path.name != f"{identifier}.response.json":
                raise BridgeError("host response path does not match request_id")
            status = response_path.stat()
            if not stat.S_ISREG(status.st_mode) or stat.S_IMODE(status.st_mode) != 0o600:
                raise BridgeError("host response must be a mode-0600 regular file")
            if status.st_size > self.max_response_bytes:
                raise BridgeError("host response exceeds the configured byte bound")
            response_bytes = response_path.read_bytes()
            if len(response_bytes) != status.st_size or sha256_bytes(response_bytes) != control["sha256"]:
                raise BridgeError("host response length or hash disagrees")
            try:
                response = json.loads(response_bytes)
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise BridgeError("host response is not UTF-8 JSON") from exc
            _json_safe(response, "host response")
            if not isinstance(response, dict) or set(response) not in (
                {"protocol", "request_id", "result"}, {"protocol", "request_id", "error"},
            ):
                raise BridgeError("host response wrapper has an invalid shape")
            if response["protocol"] != PROTOCOL or response["request_id"] != identifier:
                raise BridgeError("host response wrapper is mismatched")
            self._consumed.add(identifier)
            if "error" in response:
                if response["error"] != {"class": "tool_exception", "effect": "unknown"}:
                    raise BridgeError("host error wrapper is invalid")
                raise BridgeError("host tool exception has unknown effects; reconcile by readback")
            return response["result"]
        finally:
            request_path.unlink(missing_ok=True)
            if response_path is not None:
                response_path.unlink(missing_ok=True)

    def connector_call(self, kind: str, args: Mapping[str, Any], *, request_id: str | None = None) -> Any:
        return normalize_tool_result(self.call(kind, args, request_id=request_id))


@dataclass(frozen=True)
class CodexDrivePort:
    peer: JsonlPeer

    @staticmethod
    def _file_evidence(file_uri: str) -> dict[str, Any]:
        path = Path(file_uri)
        try:
            status = path.lstat()
            resolved = path.resolve(strict=True)
        except OSError as exc:
            raise BridgeError("Drive write source file is unavailable") from exc
        if stat.S_ISLNK(status.st_mode) or not stat.S_ISREG(status.st_mode) or stat.S_IMODE(status.st_mode) != 0o600:
            raise BridgeError("Drive write source must be a mode-0600 non-symlink regular file")
        data = resolved.read_bytes()
        return {"file_uri": str(resolved), "file_sha256": sha256_bytes(data), "file_size_bytes": len(data)}

    def metadata(self, file_id: str, *, fields: str) -> Any:
        return self.peer.connector_call("drive.get_metadata", {"fileId": file_id, "fields": fields})

    def fetch(self, url: str, *, raw: bool = True, include_base64: bool = True) -> Any:
        return self.peer.connector_call("drive.fetch", {"url": url, "download_raw_file": raw, "include_base64": include_base64})

    def list_folder(self, url: str, *, top_k: int) -> Any:
        result = self.peer.connector_call("drive.list_folder", {"url": url, "top_k": top_k})
        files = result.get("files") if isinstance(result, Mapping) else None
        if not isinstance(files, list) or len(files) >= top_k:
            raise BridgeError("Drive folder listing is invalid or reached its non-paginated cap")
        return result

    def create_folder(self, name: str, parent_folder: str) -> Any:
        return self.peer.connector_call("drive.create_folder", {"name": name, "parent_folder": parent_folder})

    def upload(self, file_uri: str, *, file_name: str, mime_type: str, parent_folder_id: str) -> Any:
        return self.peer.connector_call("drive.upload_file", {
            **self._file_evidence(file_uri), "file_name": file_name,
            "mime_type": mime_type, "parent_folder_id": parent_folder_id,
        })

    def update(self, file_id: str, *, file_uri: str, mime_type: str) -> Any:
        return self.peer.connector_call("drive.update_file", {
            "fileId": file_id, **self._file_evidence(file_uri), "mime_type": mime_type,
        })


@dataclass(frozen=True)
class CodexGmailPort:
    peer: JsonlPeer

    def search_ids(self, **arguments: Any) -> Any:
        return self.peer.connector_call("gmail.search_ids", arguments)

    def search_all_ids(self, **arguments: Any) -> tuple[str, ...]:
        token: str | None = None
        seen_tokens: set[str | None] = set()
        identities: list[str] = []
        while True:
            if token in seen_tokens:
                raise BridgeError("Gmail search pagination did not make progress")
            seen_tokens.add(token)
            page_args = dict(arguments)
            if token is not None:
                page_args["next_page_token"] = token
            page = self.search_ids(**page_args)
            page_ids = page.get("message_ids") if isinstance(page, Mapping) else None
            if not isinstance(page_ids, list) or any(not isinstance(item, str) or not item for item in page_ids):
                raise BridgeError("Gmail search returned invalid message identities")
            identities.extend(page_ids)
            token = page.get("next_page_token")
            if token is None:
                break
            if not isinstance(token, str) or not token:
                raise BridgeError("Gmail search returned an invalid next page token")
        return tuple(dict.fromkeys(identities))

    def read(self, message_id: str, format: str) -> Any:
        return self.peer.connector_call("gmail.read", {"message_id": message_id, "format": format})

    def read_thread(self, thread_id: str, *, max_messages: int) -> Any:
        result = self.peer.connector_call("gmail.read_thread", {"thread_id": thread_id, "max_messages": max_messages})
        messages = result.get("messages") if isinstance(result, Mapping) else None
        if not isinstance(messages, list) or len(messages) >= max_messages:
            raise BridgeError("Gmail thread is invalid or reached its bounded message cap")
        return result

    def read_attachment(self, message_id: str, attachment_id: str) -> Any:
        return self.peer.connector_call("gmail.read_attachment", {"message_id": message_id, "attachment_id": attachment_id})

    def send(self, request: Mapping[str, Any]) -> Any:
        return self.peer.connector_call("gmail.send", request)


@dataclass(frozen=True)
class CodexSheetsPort:
    peer: JsonlPeer

    def metadata(self, **arguments: Any) -> Any:
        return self.peer.connector_call("sheets.get_metadata", arguments)

    def cells(self, **arguments: Any) -> Any:
        return self.peer.connector_call("sheets.get_cells", arguments)

    def batch_update(self, **arguments: Any) -> Any:
        return self.peer.connector_call("sheets.batch_update", arguments)

    def comments(self, **arguments: Any) -> Any:
        return self.peer.connector_call("comments.read_spreadsheet", arguments)

    def all_comments(self, **arguments: Any) -> tuple[Mapping[str, Any], ...]:
        token: str | None = None
        seen_tokens: set[str | None] = set()
        comments: list[Mapping[str, Any]] = []
        while True:
            if token in seen_tokens:
                raise BridgeError("Sheet comment pagination did not make progress")
            seen_tokens.add(token)
            page_args = dict(arguments)
            if token is not None:
                page_args["page_token"] = token
            page = self.comments(**page_args)
            values = page.get("comments") if isinstance(page, Mapping) else None
            if not isinstance(values, list) or any(not isinstance(item, Mapping) for item in values):
                raise BridgeError("Sheet comment page is invalid")
            comments.extend(values)
            token = page.get("nextPageToken")
            if token is None:
                break
            if not isinstance(token, str) or not token:
                raise BridgeError("Sheet comment page token is invalid")
        return tuple(comments)

    def write_comments(self, **arguments: Any) -> Any:
        return self.peer.connector_call("comments.write_file", arguments)


@dataclass(frozen=True)
class CodexSemanticPort:
    peer: JsonlPeer

    def interpret(self, packet: Mapping[str, Any]) -> Any:
        return self.peer.call("semantic.interpret", {"packet": dict(packet)})

    def audit(self, packet: Mapping[str, Any], interpretation: Mapping[str, Any]) -> Any:
        return self.peer.call("semantic.audit", {"packet": dict(packet), "interpretation": dict(interpretation)})
