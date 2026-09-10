"""Deterministic, lossless accounting for one reconciled MIME message tree.

This module deliberately separates two questions which older ingestion code
collapsed into one: which plaintext part is the convenient presentation body,
and which MIME leaves are source evidence.  The former is an alias; the latter
is a complete inventory with exactly one disposition per node.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from typing import Any

from .catalog import stable_content_id
from .contracts import canonical_json_bytes, sha256_bytes


MIME_ACCOUNTING_POLICY = "mime-accounting-v1"


class MimeAccountingError(ValueError):
    """Raised when a reconciled MIME tree cannot be accounted for exactly."""


def _sort_key(path: str) -> tuple[int, ...]:
    return () if path == "" else tuple(int(item) for item in path.split("."))


def raw_message_member_path(message_id: str) -> str:
    """Return the portable bundle-member path for exact raw message bytes."""
    if not isinstance(message_id, str) or not message_id:
        raise MimeAccountingError("raw message identity is required")
    return f"raw/messages/{sha256_bytes(message_id.encode('utf-8'))}.eml"


def accounting_sha256(value: Mapping[str, Any]) -> str:
    """Hash one complete accounting object without embedding a circular hash."""
    return sha256_bytes(canonical_json_bytes(dict(value)))


def _primary_candidate(
    path: str, nodes: Mapping[str, Mapping[str, Any]], plain: Mapping[str, Mapping[str, Any]],
) -> str | None:
    node = nodes[path]
    if not node["multipart"]:
        return path if path in plain else None
    children = node["children"]
    candidates = [candidate for child in children if (candidate := _primary_candidate(child, nodes, plain)) is not None]
    if not candidates:
        return None
    mime_type = node["mime_type"]
    if mime_type == "multipart/alternative":
        substantive = [item for item in candidates if plain[item]["provider_unicode"].strip()]
        return (substantive or candidates)[-1]
    if mime_type == "multipart/related":
        start = node.get("related_start")
        if start:
            matches = [
                child for child in children
                if nodes[child].get("content_id_header") == start
            ]
            if len(matches) != 1:
                raise MimeAccountingError("multipart/related start does not identify exactly one child")
            selected = _primary_candidate(matches[0], nodes, plain)
            if selected is None:
                raise MimeAccountingError("multipart/related root has no plaintext presentation")
            return selected
        first = _primary_candidate(children[0], nodes, plain)
        if first is not None:
            return first
    substantive = [item for item in candidates if plain[item]["provider_unicode"].strip()]
    return (substantive or candidates)[0]


def build_mime_accounting(
    *, message_id: str, raw_message: bytes,
    nodes: Sequence[Mapping[str, Any]], parts: Sequence[Mapping[str, Any]],
) -> tuple[dict[str, Any], tuple[dict[str, Any], ...], str | None]:
    """Account for every MIME node and return contents plus primary part ID.

    ``nodes`` must describe the reconciled raw/full tree. ``parts`` must carry
    the exact decoded Unicode and raw-part custody already proved by the Gmail
    normalizer.  This function performs no format-specific body parsing.
    """
    if not isinstance(raw_message, bytes) or not raw_message:
        raise MimeAccountingError("exact nonempty raw message bytes are required")
    node_map: dict[str, dict[str, Any]] = {}
    for raw_node in nodes:
        node = dict(raw_node)
        path = node.get("path")
        if not isinstance(path, str) or path in node_map:
            raise MimeAccountingError("MIME node paths are missing or duplicate")
        if not isinstance(node.get("mime_type"), str) or not node["mime_type"]:
            raise MimeAccountingError("MIME node lacks a type")
        if not isinstance(node.get("multipart"), bool):
            raise MimeAccountingError("MIME node lacks structural evidence")
        node_map[path] = node
    if "" not in node_map:
        raise MimeAccountingError("MIME tree lacks its root node")
    ordered_paths = sorted(node_map, key=_sort_key)
    for path in ordered_paths:
        node = node_map[path]
        children = [
            candidate for candidate in ordered_paths
            if candidate and candidate.rpartition(".")[0] == path
            or path == "" and candidate and "." not in candidate
        ]
        node["children"] = children
        if node["multipart"] != bool(children):
            raise MimeAccountingError("MIME node structure is incomplete")

    by_path: dict[str, dict[str, Any]] = {}
    for raw_part in parts:
        part = dict(raw_part)
        path = part.get("provider_part_id")
        if not isinstance(path, str) or path not in node_map or node_map[path]["multipart"]:
            raise MimeAccountingError("MIME leaf part does not match the reconciled tree")
        if path in by_path:
            raise MimeAccountingError("MIME leaf part identity is duplicate")
        by_path[path] = part
    leaves = [path for path in ordered_paths if not node_map[path]["multipart"]]
    if set(by_path) != set(leaves):
        raise MimeAccountingError("MIME leaf inventory is incomplete")

    plain = {
        path: part for path, part in by_path.items()
        if part.get("mime_type") == "text/plain" and part.get("role") == "body"
    }
    primary_path = _primary_candidate("", node_map, plain) if plain else None

    # Exact duplicates may be collapsed semantically only among siblings in
    # the same multipart/alternative. Their bytes remain independently stored.
    representatives: dict[tuple[str, str], str] = {}
    contents: list[dict[str, Any]] = []
    content_by_path: dict[str, str] = {}
    for path in leaves:
        part = by_path[path]
        mime_type = part.get("mime_type")
        role = part.get("role")
        if mime_type not in {"text/plain", "text/html"} or role != "body":
            continue
        text = part.get("provider_unicode")
        if not isinstance(text, str):
            raise MimeAccountingError("text MIME leaf lacks exact provider Unicode")
        parent = path.rpartition(".")[0] if "." in path else ""
        if mime_type == "text/plain":
            kind = "body" if path == primary_path else "body_supplement"
            disposition = "padding" if not text.strip() else "interpret"
            duplicate_of = None
            if node_map[parent]["mime_type"] == "multipart/alternative" and disposition == "interpret":
                key = (parent, sha256_bytes(text.encode("utf-8")))
                duplicate_of = representatives.get(key)
                if duplicate_of is None:
                    representatives[key] = path
                else:
                    disposition = "duplicate_text"
            identity_kind = "body" if kind == "body" else "mime_text"
        else:
            kind = "html_evidence"
            disposition = "html_evidence"
            duplicate_of = None
            identity_kind = "mime_html"
        part_id = part.get("part_id")
        if not isinstance(part_id, str) or not part_id:
            raise MimeAccountingError("text MIME leaf lacks normalized part identity")
        content_id = stable_content_id(message_id, identity_kind, part_id)
        encoded = text.encode("utf-8")
        custody = {
            "selected_part_id": part_id,
            "provider_part_id": path,
            "declared_charset": part.get("charset"),
            "content_transfer_encoding": part.get("content_transfer_encoding"),
            "raw_part_sha256": part.get("raw_part_sha256"),
            "raw_part_byte_length": part.get("raw_part_byte_length"),
            "raw_part_locator": deepcopy(part.get("raw_part_locator")),
            "provider_unicode_sha256": sha256_bytes(encoded),
            "plaintext_sha256": sha256_bytes(encoded),
            "plaintext_byte_length": len(encoded),
            "complete": True,
        }
        item = {
            "content_id": content_id,
            "source_part_id": part_id,
            "provider_part_id": path,
            "content_kind": kind,
            "mime_type": mime_type,
            "disposition": disposition,
            "duplicate_of_part_id": duplicate_of,
            "sha256": sha256_bytes(encoded),
            "byte_length": len(encoded),
            "text": text,
            "custody": custody,
        }
        contents.append(item)
        content_by_path[path] = content_id

    accounting_nodes: list[dict[str, Any]] = []
    for path in ordered_paths:
        node = node_map[path]
        item = {
            "path": path,
            "parent_path": None if path == "" else (path.rpartition(".")[0] if "." in path else ""),
            "mime_type": node["mime_type"],
            "multipart": node["multipart"],
            "content_disposition": node.get("content_disposition"),
            "content_id_header": node.get("content_id_header"),
        }
        if node["multipart"]:
            item["disposition"] = "structural"
            item["children"] = list(node["children"])
        elif path in content_by_path:
            content = next(value for value in contents if value["content_id"] == content_by_path[path])
            item["disposition"] = content["disposition"]
            item["content_id"] = content["content_id"]
        else:
            item["disposition"] = "external_attachment"
        accounting_nodes.append(item)
    primary_content_id = content_by_path[primary_path] if primary_path is not None else None
    accounting = {
        "policy": MIME_ACCOUNTING_POLICY,
        "complete": True,
        "root_path": "",
        "primary_content_id": primary_content_id,
        "content_order": [item["content_id"] for item in contents],
        "raw_message": {
            "member_path": raw_message_member_path(message_id),
            "sha256": sha256_bytes(raw_message),
            "byte_length": len(raw_message),
        },
        "nodes": accounting_nodes,
    }
    return accounting, tuple(contents), by_path[primary_path]["part_id"] if primary_path is not None else None


def validate_mime_accounting(message: Mapping[str, Any]) -> None:
    """Validate accounting/content/body aliases without reinterpreting MIME."""
    accounting = message.get("mime_accounting")
    contents = message.get("mime_contents")
    if not isinstance(accounting, Mapping) or accounting.get("policy") != MIME_ACCOUNTING_POLICY or accounting.get("complete") is not True:
        raise MimeAccountingError("source message lacks complete MIME accounting")
    if not isinstance(contents, list) or not contents:
        raise MimeAccountingError("source message lacks MIME content inventory")
    ids: list[str] = []
    by_id: dict[str, Mapping[str, Any]] = {}
    by_part: dict[str, Mapping[str, Any]] = {}
    for item in contents:
        if not isinstance(item, Mapping):
            raise MimeAccountingError("MIME content item is malformed")
        content_id = item.get("content_id")
        text = item.get("text")
        part_id = item.get("source_part_id")
        provider_part_id = item.get("provider_part_id")
        if (
            not isinstance(content_id, str) or not content_id or content_id in by_id
            or not isinstance(part_id, str) or not part_id or part_id in by_part
            or not isinstance(provider_part_id, str) or not isinstance(text, str)
        ):
            raise MimeAccountingError("MIME content identity or text is invalid")
        encoded = text.encode("utf-8")
        if item.get("sha256") != sha256_bytes(encoded) or item.get("byte_length") != len(encoded):
            raise MimeAccountingError("MIME content bytes disagree with custody")
        custody = item.get("custody")
        raw_length = custody.get("raw_part_byte_length") if isinstance(custody, Mapping) else None
        raw_locator = custody.get("raw_part_locator") if isinstance(custody, Mapping) else None
        if (
            not isinstance(custody, Mapping)
            or custody.get("selected_part_id") != part_id
            or custody.get("provider_part_id") != provider_part_id
            or not isinstance(custody.get("declared_charset"), str) or not custody["declared_charset"]
            or not isinstance(custody.get("content_transfer_encoding"), str) or not custody["content_transfer_encoding"]
            or not isinstance(custody.get("raw_part_sha256"), str) or len(custody["raw_part_sha256"]) != 64
            or not isinstance(raw_length, int) or raw_length < 0
            or not isinstance(raw_locator, Mapping) or raw_locator.get("kind") != "raw_part_bytes"
            or raw_locator.get("byte_start") != 0 or raw_locator.get("byte_end") != raw_length
            or custody.get("provider_unicode_sha256") != sha256_bytes(encoded)
            or custody.get("plaintext_sha256") != sha256_bytes(encoded)
            or custody.get("plaintext_byte_length") != len(encoded)
            or custody.get("complete") is not True
        ):
            raise MimeAccountingError("MIME content provider custody disagrees")
        if item.get("disposition") not in {"interpret", "padding", "duplicate_text", "html_evidence"}:
            raise MimeAccountingError("MIME content has an unsupported disposition")
        if item.get("content_kind") not in {"body", "body_supplement", "html_evidence"}:
            raise MimeAccountingError("MIME content has an unsupported kind")
        if (
            item.get("content_kind") == "html_evidence"
            and (item.get("mime_type") != "text/html" or item.get("disposition") != "html_evidence")
            or item.get("content_kind") != "html_evidence" and item.get("mime_type") != "text/plain"
        ):
            raise MimeAccountingError("MIME content kind and type disagree")
        ids.append(content_id)
        by_id[content_id] = item
        by_part[part_id] = item
    if accounting.get("content_order") != ids:
        raise MimeAccountingError("MIME accounting content order disagrees")
    primary = by_id.get(accounting.get("primary_content_id"))
    if primary is None:
        if accounting.get("primary_content_id") is not None or message.get("body") is not None or message.get("body_custody") is not None:
            raise MimeAccountingError("absent MIME primary must have null body aliases")
    elif primary.get("content_kind") != "body" or message.get("body") != primary.get("text"):
        raise MimeAccountingError("primary body alias differs from MIME content")
    body_custody = message.get("body_custody")
    if primary is not None and (not isinstance(body_custody, Mapping) or body_custody.get("content_id") != primary.get("content_id")):
        raise MimeAccountingError("primary body custody differs from MIME content")
    nodes = accounting.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        raise MimeAccountingError("MIME accounting lacks node inventory")
    paths: list[str] = []
    node_content_ids: list[str] = []
    for node in nodes:
        if not isinstance(node, Mapping) or not isinstance(node.get("path"), str) or node["path"] in paths:
            raise MimeAccountingError("MIME accounting node identity is invalid")
        if node.get("disposition") not in {
            "structural", "interpret", "padding", "duplicate_text",
            "html_evidence", "external_attachment",
        }:
            raise MimeAccountingError("MIME accounting node disposition is invalid")
        if node.get("content_id") is not None:
            node_content_ids.append(node["content_id"])
        paths.append(node["path"])
    if paths[0] != accounting.get("root_path") or accounting.get("root_path") != "":
        raise MimeAccountingError("MIME accounting root is invalid")
    if node_content_ids != ids:
        raise MimeAccountingError("MIME node dispositions do not account for every content item")
    for item in contents:
        duplicate = item.get("duplicate_of_part_id")
        if item.get("disposition") == "duplicate_text":
            representative = by_part.get(duplicate)
            if representative is None or representative.get("sha256") != item.get("sha256"):
                raise MimeAccountingError("duplicate MIME content lacks an exact representative")
        elif duplicate is not None:
            raise MimeAccountingError("non-duplicate MIME content names a representative")
    raw = accounting.get("raw_message")
    if not isinstance(raw, Mapping) or raw.get("member_path") != raw_message_member_path(message.get("message_id")):
        raise MimeAccountingError("MIME accounting raw-message reference is invalid")
    if not isinstance(raw.get("byte_length"), int) or raw["byte_length"] < 1 or not isinstance(raw.get("sha256"), str) or len(raw["sha256"]) != 64 or any(char not in "0123456789abcdef" for char in raw["sha256"]):
        raise MimeAccountingError("MIME accounting raw-message custody is invalid")
