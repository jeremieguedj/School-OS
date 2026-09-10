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


class ConnectorToolError(BridgeError):
    """A connector failure with safe diagnostics and exact private evidence."""

    def __init__(
        self, *, diagnostics: Mapping[str, Any], evidence_path: Path,
        evidence_sha256: str,
    ) -> None:
        self.diagnostics = dict(diagnostics)
        self.evidence_path = evidence_path
        self.evidence_sha256 = evidence_sha256
        summary = json.dumps(self.diagnostics, sort_keys=True, separators=(",", ":"))
        super().__init__(
            "host tool exception has unknown effects; "
            f"diagnostics={summary}; exact private connector evidence="
            f"{evidence_path} sha256={evidence_sha256}; reconcile by readback"
        )


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
    "drive.search_page": RequestSpec(
        frozenset({"parent_id", "item_type", "topn"}),
        frozenset({"page_token"}),
    ),
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
    "resource.fetch_https": RequestSpec(frozenset({"url", "max_bytes", "max_redirects", "timeout_ms"})),
    "extract.image": RequestSpec(frozenset({"path", "source_id", "mime_type", "original_sha256", "byte_length", "width", "height"})),
}

# Kept next to the request union so host dispatch cannot broaden independently
# from child validation.  These names describe the current connector surface;
# availability still requires operation-specific observed capability evidence.
HOST_BINDINGS: dict[str, HostBinding] = {
    "drive.get_metadata": HostBinding("mcp__codex_apps__google_drive_get_file_metadata"),
    "drive.fetch": HostBinding("mcp__codex_apps__google_drive_fetch"),
    "drive.search_page": HostBinding("mcp__codex_apps__google_drive_search"),
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
    # These labels are explicit local-host routes, not connector tool names.
    "resource.fetch_https": HostBinding("school_os.source_host.fetch_https"),
    "extract.image": HostBinding("school_os.source_host.view_image_original"),
}

# Captured from the connected-host capability inventory.  Keep this finite
# evidence adjacent to the bindings: a request kind may not silently start
# targeting a spelling which was never advertised by the host.
CAPTURED_HOST_CAPABILITIES: frozenset[str] = frozenset({
    "mcp__codex_apps__google_drive_get_file_metadata",
    "mcp__codex_apps__google_drive_fetch",
    "mcp__codex_apps__google_drive_search",
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


def _nullable_string(value: Any, label: str) -> None:
    if value is not None:
        _nonempty_string(value, label)


def _mime_payload(value: Any) -> None:
    """Validate the finite structured MIME form used by the Gmail binding."""
    if not isinstance(value, Mapping):
        raise BridgeError("gmail.send.payload must be an object")
    mime_type = value.get("mime_type")
    _nonempty_string(mime_type, "gmail.send.payload.mime_type")
    has_body, has_parts = "body" in value, "parts" in value
    if has_body == has_parts:
        raise BridgeError("gmail.send.payload requires exactly one of body or parts")
    if has_body:
        body = value["body"]
        if not isinstance(body, Mapping) or set(body) != {"content"} or not isinstance(body["content"], str):
            raise BridgeError("gmail.send.payload.body must contain one string content")
        return
    parts = value["parts"]
    if not isinstance(parts, list) or not parts:
        raise BridgeError("gmail.send.payload.parts must be a nonempty list")
    for part in parts:
        if not isinstance(part, Mapping) or not {"mime_type", "body"} <= set(part):
            raise BridgeError("gmail.send.payload part is malformed")
        _nonempty_string(part["mime_type"], "gmail.send.payload part MIME type")
        body = part["body"]
        if not isinstance(body, Mapping) or set(body) != {"content"} or not isinstance(body["content"], str):
            raise BridgeError("gmail.send.payload part body is malformed")
        for key in ("charset", "content_disposition"):
            if key in part:
                _nonempty_string(part[key], f"gmail.send.payload part.{key}")


def _comment_operations(args: Mapping[str, Any]) -> None:
    _exactly_one(args, "id", "url")
    total = 0
    for key in ("comments", "replies", "resolutions"):
        if key not in args:
            continue
        values = args[key]
        if not isinstance(values, list) or any(not isinstance(item, Mapping) or not item for item in values):
            raise BridgeError(f"comments.write_file.{key} must be nonempty objects")
        for item in values:
            if key == "comments":
                allowed = {"content", "anchor", "quoted_text", "sheet_cell_range", "slide_number"}
                if set(item) - allowed or "content" not in item:
                    raise BridgeError("comments.write_file.comments item has an invalid shape")
                _nonempty_string(item["content"], "comments.write_file.comments content")
                for optional in ("anchor", "quoted_text", "sheet_cell_range"):
                    if optional in item and item[optional] is not None:
                        _nonempty_string(item[optional], f"comments.write_file.comments {optional}")
                if "slide_number" in item and item["slide_number"] is not None:
                    _positive_int(item["slide_number"], "comments.write_file.comments slide_number")
            elif key == "replies":
                if set(item) != {"comment_id", "content"}:
                    raise BridgeError("comments.write_file.replies item has an invalid shape")
                _nonempty_string(item["comment_id"], "comments.write_file.replies comment_id")
                _nonempty_string(item["content"], "comments.write_file.replies content")
            else:
                if set(item) - {"comment_id", "reply_content"} or "comment_id" not in item:
                    raise BridgeError("comments.write_file.resolutions item has an invalid shape")
                _nonempty_string(item["comment_id"], "comments.write_file.resolutions comment_id")
                if "reply_content" in item and item["reply_content"] is not None:
                    _nonempty_string(item["reply_content"], "comments.write_file.resolutions reply_content")
        total += len(values)
    if not 1 <= total <= 20:
        raise BridgeError("comments.write_file requires 1 through 20 operations")


def _decimal_size(value: Any, label: str, *, allow_none: bool = False) -> int | None:
    if value is None and allow_none:
        return None
    if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    raise BridgeError(f"{label} must be an exact nonnegative decimal size")


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
    for key in ("fileId", "parent_id", "item_type", "message_id", "thread_id", "attachment_id", "filename", "url", "name", "file_name", "mime_type", "parent_folder", "parent_folder_id", "query", "next_page_token", "page_token", "from_address", "reply_message_id", "reply_to", "fields", "cell_fields", "spreadsheet_id", "spreadsheet_url"):
        if key in args:
            _nonempty_string(args[key], f"{kind}.{key}")
    for key in ("top_k", "topn", "max_results", "max_messages", "page_size"):
        if key in args:
            _positive_int(args[key], f"{kind}.{key}")
    for key in ("label_ids", "ranges", "response_ranges"):
        if key in args:
            _string_list(args[key], f"{kind}.{key}")
    for key in ("download_raw_file", "include_base64", "charts_only", "include_conditional_format_rules", "include_deleted", "include_spreadsheet_in_response", "response_include_grid_data"):
        if key in args and not isinstance(args[key], bool):
            raise BridgeError(f"{kind}.{key} must be boolean")
    if "supportsAllDrives" in args and args["supportsAllDrives"] is not None and not isinstance(args["supportsAllDrives"], bool):
        raise BridgeError("drive.get_metadata.supportsAllDrives must be boolean or null")
    if kind == "drive.search_page":
        if re.fullmatch(r"[A-Za-z0-9_-]+", args["parent_id"]) is None:
            raise BridgeError("drive.search_page.parent_id is not a Drive object ID")
        if args["item_type"] not in {"document", "image", "folder"}:
            raise BridgeError("drive.search_page.item_type is not an advertised paginated category")
        if args["topn"] > 1000:
            raise BridgeError("drive.search_page.topn exceeds the finite page bound")
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
        if not isinstance(args["requests"], list) or not args["requests"] or any(not isinstance(item, Mapping) or not item for item in args["requests"]):
            raise BridgeError("sheets.batch_update.requests must be nonempty operation objects")
        if "image_uris" in args:
            _nonempty_string(args["image_uris"], "sheets.batch_update.image_uris")
    if kind == "drive.update_file":
        for key in ("addParents", "removeParents"):
            if key in args:
                _nullable_string(args[key], f"drive.update_file.{key}")
    if kind == "gmail.read" and args.get("format") not in {"full", "metadata", "minimal", "raw"}:
        raise BridgeError("gmail.read.format is not an admitted Gmail format")
    if kind == "gmail.read_attachment":
        _exactly_one(args, "attachment_id", "filename")
    if kind == "gmail.send":
        for key in ("to", "cc", "bcc"):
            if key in args:
                _nonempty_string(args[key], f"gmail.send.{key}")
        _mime_payload(args["payload"])
        if "response_fields" in args:
            _string_list(args["response_fields"], "gmail.send.response_fields")
            if not set(args["response_fields"]) <= {
                "id", "thread_id", "label_ids", "snippet", "history_id",
                "internal_date", "payload", "size_estimate",
                "classification_label_values",
            }:
                raise BridgeError("gmail.send.response_fields contains an unadvertised field")
        if "classification_label_values" in args:
            classifications = args["classification_label_values"]
            if not isinstance(classifications, list):
                raise BridgeError("gmail.send.classification_label_values must be an array")
            for classification in classifications:
                if not isinstance(classification, Mapping) or set(classification) - {"label_id", "fields"} or "label_id" not in classification:
                    raise BridgeError("gmail.send.classification_label_values has an invalid label shape")
                _nonempty_string(classification["label_id"], "gmail.send classification label_id")
                if "fields" in classification and classification["fields"] is not None:
                    fields = classification["fields"]
                    if not isinstance(fields, list):
                        raise BridgeError("gmail.send classification fields must be an array")
                    for field in fields:
                        if not isinstance(field, Mapping) or set(field) - {"field_id", "selection"} or "field_id" not in field:
                            raise BridgeError("gmail.send classification field has an invalid shape")
                        _nonempty_string(field["field_id"], "gmail.send classification field_id")
                        if "selection" in field and field["selection"] is not None:
                            _nonempty_string(field["selection"], "gmail.send classification selection")
    if kind == "comments.write_file":
        _comment_operations(args)
    if kind.startswith("semantic."):
        for key, value in args.items():
            if not isinstance(value, Mapping):
                raise BridgeError(f"{kind}.{key} must be an object")
    if kind == "extract.image":
        raw_path = args.get("path")
        if not isinstance(raw_path, str) or not Path(raw_path).is_absolute():
            raise BridgeError("image extraction path must be an absolute local path")
    if kind == "resource.fetch_https":
        url = args.get("url")
        if not isinstance(url, str) or not url.startswith("https://"):
            raise BridgeError("resource fetch requires an HTTPS URL")
    _json_safe(args, "bridge request args")


def _validate_result(kind: str, result: Any, args: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Reject malformed connector replies before they cross the bridge."""
    if not isinstance(result, Mapping):
        raise BridgeError(f"{kind} result must be an object")
    normalized = dict(result)
    if kind == "drive.get_metadata":
        for key in ("id", "mime_type", "url", "title", "modified_time"):
            _nonempty_string(result.get(key), f"{kind} result.{key}")
        _string_list(result.get("parent_ids"), f"{kind} result.parent_ids")
        mime_type = result["mime_type"]
        if mime_type != "application/vnd.google-apps.folder":
            normalized["size"] = _decimal_size(result.get("size"), f"{kind} result.size")
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
    elif kind == "drive.search_page":
        if set(result) - {"results", "next_page_token"} or not isinstance(result.get("results"), list):
            raise BridgeError("drive.search_page result has an unsupported page shape")
        for item in result["results"]:
            if not isinstance(item, Mapping):
                raise BridgeError("drive.search_page result member must be an object")
            _nonempty_string(item.get("id"), "drive.search_page result member.id")
            _nonempty_string(item.get("title"), "drive.search_page result member.title")
        token = result.get("next_page_token")
        if token is not None:
            _nonempty_string(token, "drive.search_page result.next_page_token")
    elif kind == "drive.create_folder":
        if result.get("success") is not True:
            raise BridgeError("drive.create_folder result lacks success evidence")
        for key in ("id", "parent_id", "title", "url"):
            _nonempty_string(result.get(key), f"drive.create_folder result.{key}")
    elif kind == "drive.upload_file":
        if result.get("success") is not True:
            raise BridgeError(f"{kind} result lacks success evidence")
        for key in ("id", "mime_type", "url", "parent_id"):
            _nonempty_string(result.get(key), f"{kind} result.{key}")
    elif kind == "drive.update_file":
        if result.get("success") is not True:
            raise BridgeError(f"{kind} result lacks success evidence")
        for key in ("id", "mime_type", "url", "modified_time"):
            _nonempty_string(result.get(key), f"{kind} result.{key}")
        _string_list(result.get("parent_ids"), f"{kind} result.parent_ids")
        if "size" in result:
            normalized["size"] = _decimal_size(result["size"], f"{kind} result.size", allow_none=True)
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
        _nonempty_string(result.get("spreadsheetId"), "comments.read_spreadsheet result.spreadsheetId")
        if result.get("nextPageToken") is not None:
            _nonempty_string(result["nextPageToken"], "comments.read_spreadsheet result.nextPageToken")
    elif kind == "comments.write_file":
        for key in ("created_comments", "created_replies", "resolved_comments"):
            values = result.get(key)
            if not isinstance(values, list) or any(not isinstance(item, Mapping) for item in values):
                raise BridgeError(f"comments.write_file result.{key} must be an object array")
            for item in values:
                _nonempty_string(item.get("id"), f"comments.write_file result.{key} item.id")
        _nonempty_string(result.get("fileId"), "comments.write_file result.fileId")
        total = _positive_int(result.get("total_operations"), "comments.write_file result.total_operations")
        expected_total = sum(len(args.get(key, [])) for key in ("comments", "replies", "resolutions")) if args is not None else None
        if expected_total is not None and total != expected_total:
            raise BridgeError("comments.write_file result total_operations disagrees with request")
    elif kind == "gmail.send":
        _nonempty_string(result.get("id"), "gmail.send result.id")
        for key in ("thread_id", "snippet", "history_id", "internal_date"):
            if key in result and result[key] is not None:
                _nonempty_string(result[key], f"gmail.send result.{key}")
        if "label_ids" in result and result["label_ids"] is not None:
            _string_list(result["label_ids"], "gmail.send result.label_ids")
        if "payload" in result and result["payload"] is not None and not isinstance(result["payload"], Mapping):
            raise BridgeError("gmail.send result.payload must be an object or null")
        if "size_estimate" in result and result["size_estimate"] is not None:
            _positive_int(result["size_estimate"], "gmail.send result.size_estimate", allow_zero=True)
    elif kind == "sheets.batch_update":
        _nonempty_string(result.get("spreadsheetId"), "sheets.batch_update result.spreadsheetId")
        if not isinstance(result.get("replies"), list):
            raise BridgeError("sheets.batch_update result.replies must be a list")
    _json_safe(result, "host binding result")
    return normalized


_GMAIL_ATTACHMENT_RESULT_KEYS = frozenset({
    "attachment_id", "content", "content_truncated", "extraction_file_uri",
    "file_uri", "filename", "images", "message_id", "mime_type", "size_bytes",
})
_GMAIL_ATTACHMENT_TRANSPORT_KEYS = frozenset({
    "__attachments__", "download_url", "file_id",
})
_GMAIL_ATTACHMENT_DISPLAY_FILE_KEYS = frozenset({
    "display_files_from_actions_ext", "id", "mime_type", "name", "source",
})


def _validate_gmail_attachment_transport(
    transport: Mapping[str, Any], declared: Mapping[str, Any],
) -> None:
    """Validate, but never forward, the connector's private display metadata."""
    file_uri = declared.get("file_uri")
    if not isinstance(file_uri, Mapping):
        raise BridgeError("Gmail attachment transport metadata lacks declared file_uri")
    if transport.get("download_url") != file_uri.get("download_url"):
        raise BridgeError("Gmail attachment transport download_url conflicts with file_uri")
    if transport.get("file_id") != file_uri.get("file_id"):
        raise BridgeError("Gmail attachment transport file_id conflicts with file_uri")
    attachments = transport.get("__attachments__")
    if not isinstance(attachments, list) or not 1 <= len(attachments) <= 10:
        raise BridgeError("Gmail attachment transport __attachments__ is malformed")
    for item in attachments:
        if not isinstance(item, Mapping) or set(item) != _GMAIL_ATTACHMENT_DISPLAY_FILE_KEYS:
            raise BridgeError("Gmail attachment transport display file is malformed")
        if not isinstance(item.get("display_files_from_actions_ext"), bool):
            raise BridgeError("Gmail attachment transport display flag is malformed")
        for key in ("id", "mime_type", "name", "source"):
            _nonempty_string(item.get(key), f"Gmail attachment transport display file.{key}")


def _normalize_gmail_attachment_envelope(result: Mapping[str, Any]) -> dict[str, Any]:
    """Project either observed connector envelope onto the declared contract."""
    outer = dict(result)
    if "structuredContent" not in outer:
        return outer
    nested = outer.pop("structuredContent")
    if (
        not isinstance(nested, Mapping)
        or set(outer) - _GMAIL_ATTACHMENT_RESULT_KEYS
    ):
        raise BridgeError("Gmail attachment redundant envelope is malformed")
    candidate = nested.get("result", nested)
    if (
        not isinstance(candidate, Mapping)
        or set(candidate) - _GMAIL_ATTACHMENT_RESULT_KEYS - _GMAIL_ATTACHMENT_TRANSPORT_KEYS
    ):
        raise BridgeError("Gmail attachment redundant envelope conflicts with declared fields")
    declared_candidate = {
        key: value for key, value in candidate.items()
        if key in _GMAIL_ATTACHMENT_RESULT_KEYS
    }
    if declared_candidate != outer:
        raise BridgeError("Gmail attachment redundant envelope conflicts with declared fields")
    transport = {
        key: value for key, value in candidate.items()
        if key in _GMAIL_ATTACHMENT_TRANSPORT_KEYS
    }
    if transport:
        if set(transport) != _GMAIL_ATTACHMENT_TRANSPORT_KEYS:
            raise BridgeError("Gmail attachment transport metadata is incomplete")
        _validate_gmail_attachment_transport(transport, outer)
    return outer


_CONNECTOR_DIAGNOSTIC_KEYS = frozenset({
    "stage", "invocation_began", "provider_response_observed", "http_status",
    "reason", "domain", "retry_after", "connector_code", "evidence_code",
})
_SAFE_ERROR_TOKEN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")
_STATUS_TEXT = re.compile(
    r"\b(?:HTTP(?:\s+status)?|status(?:\s+code)?)\s*[:=]?\s*([45][0-9]{2})\b",
    re.IGNORECASE,
)
_REASON_TEXT = re.compile(
    r"\b(?:error[ _-]?reason|reason)\s*[:=]?\s*['\"]?([A-Za-z][A-Za-z0-9_.-]{0,127})",
    re.IGNORECASE,
)
_RETRY_AFTER_TEXT = re.compile(
    r"\bretry[-_ ]after\s*[:=]?\s*['\"]?([0-9]{1,8})",
    re.IGNORECASE,
)


def _safe_error_token(value: Any) -> str | None:
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        return None
    token = str(value)
    return token if _SAFE_ERROR_TOKEN.fullmatch(token) else None


def _connector_error_diagnostics(
    value: Any, *, stage: str, provider_response_observed: bool,
) -> dict[str, Any]:
    """Extract only privacy-safe machine fields from an untrusted connector error."""
    diagnostics: dict[str, Any] = {
        "stage": stage,
        "invocation_began": True,
        "provider_response_observed": provider_response_observed,
        "http_status": None,
        "reason": None,
        "domain": None,
        "retry_after": None,
        "connector_code": None,
        "evidence_code": {
            "provider_response": "connector_error_result",
            "response_normalization": "connector_result_rejected",
            "transport": "connector_invocation_exception",
        }[stage],
    }
    texts: list[str] = []
    nodes: list[Any] = [value]
    visited = 0
    while nodes and visited < 10000:
        node = nodes.pop()
        visited += 1
        if isinstance(node, Mapping):
            for key, item in node.items():
                lower = str(key).lower()
                if lower in {"status", "status_code", "http_status"}:
                    token = _safe_error_token(item)
                    if token is not None and token.isdigit() and 400 <= int(token) <= 599:
                        if diagnostics["http_status"] is None:
                            diagnostics["http_status"] = int(token)
                    elif token is not None and diagnostics["connector_code"] is None:
                        diagnostics["connector_code"] = token
                elif lower in {"reason", "error_reason"}:
                    token = _safe_error_token(item)
                    if token is not None and diagnostics["reason"] is None:
                        diagnostics["reason"] = token
                elif lower in {"domain", "error_domain"}:
                    token = _safe_error_token(item)
                    if token is not None and diagnostics["domain"] is None:
                        diagnostics["domain"] = token
                elif lower in {"retry_after", "retry-after"}:
                    token = _safe_error_token(item)
                    if token is not None and diagnostics["retry_after"] is None:
                        diagnostics["retry_after"] = token
                elif lower in {"code", "error_code"}:
                    token = _safe_error_token(item)
                    if token is not None and diagnostics["connector_code"] is None:
                        diagnostics["connector_code"] = token
                    if (
                        token is not None and token.isdigit()
                        and 400 <= int(token) <= 599
                        and diagnostics["http_status"] is None
                    ):
                        diagnostics["http_status"] = int(token)
                if lower == "text" and isinstance(item, str):
                    texts.append(item[:4096])
                nodes.append(item)
        elif isinstance(node, list):
            nodes.extend(node)
    for text in texts:
        if diagnostics["http_status"] is None and (match := _STATUS_TEXT.search(text)):
            diagnostics["http_status"] = int(match.group(1))
        if diagnostics["reason"] is None and (match := _REASON_TEXT.search(text)):
            diagnostics["reason"] = match.group(1)
        if diagnostics["retry_after"] is None and (match := _RETRY_AFTER_TEXT.search(text)):
            diagnostics["retry_after"] = match.group(1)
    return diagnostics


def _connector_failure_evidence(
    *, request_id: str, kind: str, stage: str, raw_result: Any,
    provider_response_observed: bool, exception: Exception,
) -> tuple[bytes, dict[str, Any]]:
    """Build an exact private receipt plus its privacy-safe public diagnosis."""
    diagnostics = _connector_error_diagnostics(
        raw_result, stage=stage,
        provider_response_observed=provider_response_observed,
    )
    raw_sha256: str | None = None
    if raw_result is not None:
        try:
            raw_sha256 = sha256_bytes(canonical_json_bytes(raw_result))
        except (TypeError, ValueError):
            raw_result = {
                "unserializable_type": type(raw_result).__name__,
                "representation": repr(raw_result),
            }
            raw_sha256 = sha256_bytes(canonical_json_bytes(raw_result))
    receipt = {
        "schema_version": 1,
        "request_id": request_id,
        "kind": kind,
        "diagnostics": diagnostics,
        "raw_connector_result_sha256": raw_sha256,
        "raw_connector_result": raw_result,
        "private_exception": {
            "type": type(exception).__name__,
            "message": str(exception),
        },
    }
    return canonical_json_bytes(receipt), diagnostics


def _read_connector_failure_evidence(
    path: Path, *, request_id: str, kind: str,
) -> tuple[dict[str, Any], str]:
    try:
        status = path.lstat()
        resolved = path.resolve(strict=True)
    except OSError as exc:
        raise BridgeError("connector failure evidence is unavailable") from exc
    if (
        stat.S_ISLNK(status.st_mode)
        or not stat.S_ISREG(status.st_mode)
        or stat.S_IMODE(status.st_mode) != 0o600
    ):
        raise BridgeError("connector failure evidence must be a mode-0600 regular file")
    data = resolved.read_bytes()
    if len(data) > MAX_RESPONSE_BYTES:
        raise BridgeError("connector failure evidence exceeds the configured byte bound")
    try:
        receipt = json.loads(data)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BridgeError("connector failure evidence is not UTF-8 JSON") from exc
    required = {
        "schema_version", "request_id", "kind", "diagnostics",
        "raw_connector_result_sha256", "raw_connector_result", "private_exception",
    }
    if (
        not isinstance(receipt, Mapping)
        or set(receipt) != required
        or receipt.get("schema_version") != 1
        or receipt.get("request_id") != request_id
        or receipt.get("kind") != kind
        or not isinstance(receipt.get("diagnostics"), Mapping)
        or set(receipt["diagnostics"]) != _CONNECTOR_DIAGNOSTIC_KEYS
    ):
        raise BridgeError("connector failure evidence wrapper is invalid")
    diagnostics = receipt["diagnostics"]
    stage = diagnostics.get("stage")
    response_observed = diagnostics.get("provider_response_observed")
    if (
        stage not in {"provider_response", "response_normalization", "transport"}
        or not isinstance(diagnostics.get("invocation_began"), bool)
        or diagnostics["invocation_began"] is not True
        or not isinstance(response_observed, bool)
        or not isinstance(receipt.get("private_exception"), Mapping)
        or set(receipt["private_exception"]) != {"type", "message"}
        or any(not isinstance(receipt["private_exception"].get(key), str) for key in ("type", "message"))
    ):
        raise BridgeError("connector failure evidence diagnostics are invalid")
    raw_result = receipt["raw_connector_result"]
    raw_sha256 = receipt["raw_connector_result_sha256"]
    if raw_result is None:
        if raw_sha256 is not None:
            raise BridgeError("connector failure evidence raw hash is invalid")
    elif (
        not isinstance(raw_sha256, str)
        or re.fullmatch(r"[0-9a-f]{64}", raw_sha256) is None
        or sha256_bytes(canonical_json_bytes(raw_result)) != raw_sha256
    ):
        raise BridgeError("connector failure evidence raw hash disagrees")
    expected_diagnostics = _connector_error_diagnostics(
        raw_result, stage=stage, provider_response_observed=response_observed,
    )
    if dict(diagnostics) != expected_diagnostics:
        raise BridgeError("connector failure evidence diagnostics disagree with raw result")
    return expected_diagnostics, sha256_bytes(data)


class HostBindingDispatcher:
    """Dispatch an already-validated request to exactly one reviewed binding."""

    def __init__(self, run_directory: Path | None = None, *, source_helpers: Any | None = None) -> None:
        self.run_directory = _verify_run_directory(run_directory) if run_directory is not None else None
        self.source_helpers = source_helpers

    def _private_file_bytes(
        self, raw_value: Any, *, evidence: Mapping[str, Any] | None, label: str,
    ) -> bytes:
        if self.run_directory is None:
            raise BridgeError(f"{label} requires an admitted private run directory")
        if not isinstance(raw_value, str) or not Path(raw_value).is_absolute():
            raise BridgeError(f"{label} must be an absolute local path")
        raw_path = Path(raw_value)
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
            raise BridgeError(f"{label} escapes the private run directory") from exc
        if stat.S_ISLNK(status.st_mode) or not stat.S_ISREG(status.st_mode) or stat.S_IMODE(status.st_mode) != 0o600:
            raise BridgeError(f"{label} must use a mode-0600 non-symlink regular private file")
        data = resolved.read_bytes()
        if evidence is not None and (
            len(data) != evidence["file_size_bytes"] or sha256_bytes(data) != evidence["file_sha256"]
        ):
            raise BridgeError("Drive write file identity, size, or hash changed before effect")
        return data

    def _host_snapshot(self, data: bytes) -> Path:
        if self.run_directory is None:
            raise BridgeError("host snapshot requires an admitted private run directory")
        snapshot = self.run_directory / f"host-snapshot-{uuid.uuid4().hex}"
        _exclusive_write(snapshot, data)
        return snapshot

    @staticmethod
    def _native_tool_result(value: Any) -> Any:
        """Consume the one native CallToolResult shape accepted by dispatch."""
        if not isinstance(value, Mapping) or value.get("isError") is True:
            raise BridgeError("host tool returned an error; effect outcome is unknown")
        structured = value.get("structuredContent")
        if not isinstance(structured, Mapping):
            raise BridgeError("host tool response lacks structuredContent.result")
        result = structured.get("result", structured)
        _json_safe(result, "normalized host result")
        return result
    def dispatch(self, kind: str, args: Mapping[str, Any], invoke: Any) -> Any:
        _validate_request(kind, args)
        if kind in {"resource.fetch_https", "extract.image"}:
            if self.source_helpers is None:
                raise BridgeError("finite source host helpers are unavailable")
            result = self.source_helpers.dispatch(kind, dict(args))
            _json_safe(result, "source host helper result")
            return result
        if not callable(invoke):
            raise BridgeError("host binding invoker is unavailable")
        native_args = dict(args)
        snapshots: list[Path] = []
        if kind == "drive.search_page":
            native_args = {
                "special_filter_query_str": f"'{args['parent_id']}' in parents and trashed = false",
                "item_type": args["item_type"], "topn": args["topn"],
            }
            if "page_token" in args:
                native_args["page_token"] = args["page_token"]
        if kind in {"drive.upload_file", "drive.update_file"}:
            data = self._private_file_bytes(
                args["file_uri"], evidence=args, label="Drive write file_uri",
            )
            snapshot = self._host_snapshot(data)
            snapshots.append(snapshot)
            native_args["file_uri"] = str(snapshot)
            native_args.pop("file_sha256")
            native_args.pop("file_size_bytes")
        if kind == "sheets.batch_update" and "image_uris" in args:
            snapshot = self._host_snapshot(self._private_file_bytes(
                args["image_uris"], evidence=None, label="Sheets image_uris",
            ))
            snapshots.append(snapshot)
            native_args["image_uris"] = str(snapshot)
        try:
            result = self._native_tool_result(invoke(HOST_BINDINGS[kind].tool_name, native_args))
            if kind == "gmail.read_attachment":
                result = _normalize_gmail_attachment_envelope(result)
            return _validate_result(kind, result, args)
        finally:
            for snapshot in snapshots:
                snapshot.unlink(missing_ok=True)

    def dispatch_request_file(
        self, *, request_id: str, kind: str, request_sha256: str,
        request_path: Path, invoke: Any,
    ) -> dict[str, str]:
        """Run one complete child request through the mandatory host boundary.

        The host must use this entrypoint (or an exact implementation of it),
        rather than reading ``request.args`` and invoking a connector directly.
        It binds the terminal control to the private request file, performs all
        argument stripping/snapshotting/result validation in :meth:`dispatch`,
        and writes the only response shape consumed by :class:`JsonlPeer`.
        """
        if self.run_directory is None:
            raise BridgeError("host request dispatch requires an admitted private run directory")
        if REQUEST_ID.fullmatch(request_id) is None or not isinstance(request_sha256, str) or re.fullmatch(r"[0-9a-f]{64}", request_sha256) is None:
            raise BridgeError("host request control has invalid identity or hash")
        path = _contained(request_path, self.run_directory)
        if path.parent != self.run_directory or path.name != f"{request_id}.request.json":
            raise BridgeError("host request path does not match request_id")
        try:
            status = path.lstat()
        except OSError as exc:
            raise BridgeError("host request file is unavailable") from exc
        if stat.S_ISLNK(status.st_mode) or not stat.S_ISREG(status.st_mode) or stat.S_IMODE(status.st_mode) != 0o600:
            raise BridgeError("host request must be a mode-0600 non-symlink regular file")
        if status.st_size > MAX_REQUEST_BYTES:
            raise BridgeError("host request exceeds the configured byte bound")
        request_bytes = path.read_bytes()
        if len(request_bytes) != status.st_size or sha256_bytes(request_bytes) != request_sha256:
            raise BridgeError("host request length or hash disagrees")
        try:
            request = json.loads(request_bytes)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise BridgeError("host request is not UTF-8 JSON") from exc
        expected = {"args", "kind", "protocol", "request_id"}
        if (
            not isinstance(request, Mapping) or set(request) != expected
            or request.get("protocol") != PROTOCOL
            or request.get("request_id") != request_id
            or request.get("kind") != kind
            or not isinstance(request.get("args"), Mapping)
        ):
            raise BridgeError("host request wrapper disagrees with terminal control")
        native_attempted = False
        provider_response_observed = False
        native_result: Any = None

        def guarded_invoke(tool_name: str, native_args: Mapping[str, Any]) -> Any:
            nonlocal native_attempted, provider_response_observed, native_result
            native_attempted = True
            native_result = invoke(tool_name, native_args)
            provider_response_observed = True
            return native_result

        try:
            result = self.dispatch(kind, request["args"], guarded_invoke)
            response_value: dict[str, Any] = {
                "protocol": PROTOCOL, "request_id": request_id, "result": result,
            }
        except Exception as exc:
            if not native_attempted:
                raise
            if not provider_response_observed:
                stage = "transport"
            elif isinstance(native_result, Mapping) and native_result.get("isError") is True:
                stage = "provider_response"
            else:
                stage = "response_normalization"
            evidence_bytes, _diagnostics = _connector_failure_evidence(
                request_id=request_id,
                kind=kind,
                stage=stage,
                raw_result=native_result if provider_response_observed else None,
                provider_response_observed=provider_response_observed,
                exception=exc,
            )
            evidence_path = self.run_directory / f"{request_id}.connector-error.json"
            _exclusive_write(evidence_path, evidence_bytes)
            # Once native dispatch is attempted, an exception cannot authorize
            # retry.  The child must reconcile the effect by provider readback.
            response_value = {
                "protocol": PROTOCOL, "request_id": request_id,
                "error": {"class": "tool_exception", "effect": "unknown"},
            }
        response_bytes = canonical_json_bytes(response_value)
        response_path = self.run_directory / f"{request_id}.response.json"
        _exclusive_write(response_path, response_bytes)
        return {
            "request_id": request_id, "response_path": str(response_path),
            "sha256": sha256_bytes(response_bytes),
        }


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
                evidence_path = self.run_dir / f"{identifier}.connector-error.json"
                if evidence_path.exists():
                    diagnostics, evidence_sha256 = _read_connector_failure_evidence(
                        evidence_path, request_id=identifier, kind=kind,
                    )
                    raise ConnectorToolError(
                        diagnostics=diagnostics,
                        evidence_path=evidence_path,
                        evidence_sha256=evidence_sha256,
                    )
                raise BridgeError("host tool exception has unknown effects; reconcile by readback")
            return response["result"]
        finally:
            request_path.unlink(missing_ok=True)
            if response_path is not None:
                response_path.unlink(missing_ok=True)

    def connector_call(self, kind: str, args: Mapping[str, Any], *, request_id: str | None = None) -> Any:
        # The mandatory host dispatcher is the sole connector-envelope
        # normalization boundary.  JSONL carries only its validated raw result.
        return self.call(kind, args, request_id=request_id)


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

    def search_page(
        self, parent_id: str, *, item_type: str, topn: int,
        page_token: str | None = None,
    ) -> Any:
        args = {"parent_id": parent_id, "item_type": item_type, "topn": topn}
        if page_token is not None:
            args["page_token"] = page_token
        return self.peer.connector_call("drive.search_page", args)

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


@dataclass(frozen=True)
class CodexSourceHostPort:
    """Finite byte/image host calls used by ``connected_sources`` only."""

    peer: JsonlPeer

    def fetch_https(self, *, url: str, max_bytes: int, max_redirects: int, timeout_ms: int) -> Any:
        return self.peer.call("resource.fetch_https", {
            "url": url, "max_bytes": max_bytes, "max_redirects": max_redirects,
            "timeout_ms": timeout_ms,
        })

    def extract_image(self, **arguments: Any) -> Any:
        return self.peer.call("extract.image", arguments)
