"""Bounded, lossless import helpers for complete synthetic mail scopes."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from .adapters import Page, ReadResult
from .contracts import sha256_bytes


class ImportError(ValueError):
    """Raised when a complete import scope cannot safely continue."""


@dataclass(frozen=True)
class Enumeration:
    """Complete scope evidence, including every page and duplicate disposition."""

    conversations: tuple[dict[str, Any], ...]
    page_tokens: tuple[str | None, ...]
    dispositions: tuple[dict[str, str], ...]


@dataclass(frozen=True)
class ImportBatch:
    """One bounded, stable subset and the exact work remaining after it."""

    conversations: tuple[dict[str, Any], ...]
    completed_ids: tuple[str, ...]
    remaining_ids: tuple[str, ...]
    byte_count: int


@dataclass(frozen=True)
class AttachmentOutcome:
    """Visible attachment result; ``text`` is present only after exact reading."""

    attachment_id: str
    outcome: str
    content_sha256: str | None
    text: str | None


@dataclass(frozen=True)
class SourceAdmission:
    """One fail-closed decision before a message can enter a source record."""

    outcome: str
    reason: str
    plaintext: bytes | None


def _conversation_id(value: Mapping[str, Any]) -> str:
    identity = value.get("conversation_id")
    if not isinstance(identity, str) or not identity:
        raise ImportError("enumerated conversation has no immutable conversation_id")
    return identity


def admit_exact_plaintext_representation(parts: Sequence[Mapping[str, Any]]) -> SourceAdmission:
    """Accept one complete UTF-8 plain part or return a non-admitting outcome.

    The alpha.13 catalog owns only one exact plaintext representation. It must
    not choose among alternative MIME bodies, decoding rules, attachments, or
    rendered resources whose bytes have no canonical source representation.
    Callers may record the returned outcome in private scope evidence, but only
    ``admitted`` is eligible for a source/catalog/index write.
    """
    if len(parts) != 1:
        return SourceAdmission("unsupported", "multiple available MIME representations", None)
    part = parts[0]
    if not isinstance(part, Mapping):
        return SourceAdmission("manual_review", "MIME part metadata is malformed", None)
    if part.get("complete") is not True:
        return SourceAdmission("manual_review", "MIME part is incomplete", None)
    if part.get("mime_type") != "text/plain":
        return SourceAdmission("unsupported", "only text/plain has an approved source representation", None)
    charset = part.get("charset")
    if not isinstance(charset, str) or charset.lower() != "utf-8":
        return SourceAdmission("unsupported", "plain-text charset is not UTF-8", None)
    if part.get("content_transfer_encoding") != "identity":
        return SourceAdmission("unsupported", "content-transfer decoding has no approved exact contract", None)
    data = part.get("data")
    if not isinstance(data, bytes):
        return SourceAdmission("manual_review", "plain-text bytes are unavailable", None)
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return SourceAdmission("unsupported", "plain-text bytes are not valid UTF-8", None)
    return SourceAdmission("admitted", "one complete exact UTF-8 plain-text representation", data)


def enumerate_conversations(
    search: Callable[[str | None], Page], *, start_page_token: str | None = None
) -> Enumeration:
    """Read every page once and retain one deterministically ordered identity set."""
    token = start_page_token
    seen_tokens: set[str | None] = set()
    by_id: dict[str, dict[str, Any]] = {}
    tokens: list[str | None] = []
    dispositions: list[dict[str, str]] = []
    while True:
        if token in seen_tokens:
            raise ImportError("enumeration page token repeated before completion")
        seen_tokens.add(token)
        tokens.append(token)
        page = search(token)
        for item in page.items:
            copied = dict(item)
            identity = _conversation_id(copied)
            if identity in by_id:
                dispositions.append({"conversation_id": identity, "outcome": "duplicate"})
                continue
            by_id[identity] = copied
            dispositions.append({"conversation_id": identity, "outcome": "included"})
        if page.next_page_token is None:
            break
        token = page.next_page_token
    return Enumeration(
        tuple(by_id[identity] for identity in sorted(by_id)), tuple(tokens), tuple(dispositions)
    )


def next_import_batch(
    conversations: Sequence[Mapping[str, Any]], *, completed_ids: Sequence[str],
    max_records: int, max_bytes: int,
) -> ImportBatch:
    """Select the next whole records without truncation or cursor guesswork."""
    if max_records < 1 or max_bytes < 1:
        raise ImportError("import limits must be at least one record and one byte")
    completed = set(completed_ids)
    ordered = sorted((dict(item) for item in conversations), key=_conversation_id)
    ids = [_conversation_id(item) for item in ordered]
    if len(ids) != len(set(ids)):
        raise ImportError("import batch input has duplicate immutable conversation IDs")
    selected: list[dict[str, Any]] = []
    used_bytes = 0
    for item in ordered:
        identity = _conversation_id(item)
        if identity in completed:
            continue
        size = item.get("byte_size")
        if not isinstance(size, int) or size < 0:
            raise ImportError("import conversation is missing exact byte_size evidence")
        if size > max_bytes:
            raise ImportError("oversized single conversation cannot be truncated")
        if len(selected) == max_records or used_bytes + size > max_bytes:
            break
        selected.append(item)
        used_bytes += size
    selected_ids = {_conversation_id(item) for item in selected}
    new_completed = tuple(sorted(completed | selected_ids))
    remaining = tuple(identity for identity in ids if identity not in new_completed)
    return ImportBatch(tuple(selected), new_completed, remaining, used_bytes)


def process_attachments(
    attachments: Sequence[Mapping[str, Any]], *, read_attachment: Callable[[str], ReadResult],
    supported_mime_types: Sequence[str], max_bytes: int,
) -> tuple[AttachmentOutcome, ...]:
    """Extract configured UTF-8 attachments or retain a precise non-inference outcome."""
    if max_bytes < 1:
        raise ImportError("attachment byte limit must be positive")
    supported = set(supported_mime_types)
    outcomes: list[AttachmentOutcome] = []
    seen: set[str] = set()
    for attachment in attachments:
        attachment_id = attachment.get("attachment_id")
        mime_type = attachment.get("mime_type")
        byte_size = attachment.get("byte_size")
        if not isinstance(attachment_id, str) or not attachment_id:
            raise ImportError("attachment has no immutable attachment_id")
        if attachment_id in seen:
            outcomes.append(AttachmentOutcome(attachment_id, "duplicate", None, None))
            continue
        seen.add(attachment_id)
        if not isinstance(mime_type, str) or mime_type not in supported:
            outcomes.append(AttachmentOutcome(attachment_id, "unsupported", None, None))
            continue
        if not isinstance(byte_size, int) or byte_size < 0 or byte_size > max_bytes:
            outcomes.append(AttachmentOutcome(attachment_id, "manual_review", None, None))
            continue
        try:
            result = read_attachment(attachment_id)
        except OSError:
            outcomes.append(AttachmentOutcome(attachment_id, "inaccessible", None, None))
            continue
        if result.identity != attachment_id or result.mime_type != mime_type or len(result.data) != byte_size:
            outcomes.append(AttachmentOutcome(attachment_id, "inaccessible", None, None))
            continue
        try:
            text = result.data.decode("utf-8")
        except UnicodeDecodeError:
            outcomes.append(AttachmentOutcome(attachment_id, "unsupported", None, None))
            continue
        outcomes.append(AttachmentOutcome(attachment_id, "extracted", sha256_bytes(result.data), text))
    return tuple(outcomes)
