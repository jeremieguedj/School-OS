"""Durable exact-once delivery intent and provider readback verification."""

from __future__ import annotations

import base64
import json
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from email import policy
from email.message import Message
from email.parser import BytesParser
from email.utils import getaddresses
from typing import Any, Optional

from .contracts import canonical_json_bytes, sha256_bytes


class DeliveryError(ValueError):
    """Raised when a delivery effect is pending, ambiguous, or not exact."""


def _is_mp3(value: bytes) -> bool:
    return value.startswith(b"ID3") or (
        len(value) >= 2 and value[0] == 0xFF and value[1] & 0xE0 == 0xE0
    )


@dataclass(frozen=True)
class ExactAudioAttachment:
    """One exact verified MP3 attachment for the MVP brief."""

    filename: str
    data: bytes

    @classmethod
    def build(cls, *, filename: str, data: bytes) -> "ExactAudioAttachment":
        if (
            not isinstance(filename, str) or not filename or filename != filename.strip()
            or filename != filename.rsplit("/", 1)[-1]
            or not filename.lower().endswith(".mp3")
        ):
            raise DeliveryError("audio attachment requires one safe .mp3 filename")
        if not isinstance(data, bytes) or not data or not _is_mp3(data):
            raise DeliveryError("audio attachment requires nonempty MP3 bytes")
        return cls(filename=filename, data=data)

    def intent(self) -> dict[str, Any]:
        return {
            "filename": self.filename,
            "mime_type": "audio/mpeg",
            "sha256": sha256_bytes(self.data),
            "size_bytes": len(self.data),
        }


def _addresses(values: Iterable[str], label: str, *, allow_empty: bool = False) -> tuple[str, ...]:
    result = tuple(value.strip().lower() for value in values)
    if (not result and not allow_empty) or any(not value or "@" not in value for value in result) or len(set(result)) != len(result):
        raise DeliveryError(f"{label} must contain unique nonempty addresses")
    return result


@dataclass(frozen=True)
class ExactDeliveryRequest:
    key: str
    variant: str
    to: tuple[str, ...]
    cc: tuple[str, ...]
    bcc: tuple[str, ...]
    subject: str
    text: bytes
    html: bytes
    audio: ExactAudioAttachment | None

    @classmethod
    def build(
        cls, *, key: str, variant: str, to: Iterable[str], cc: Iterable[str] = (),
        bcc: Iterable[str] = (), subject: str, text: bytes, html: bytes,
        audio: ExactAudioAttachment | None = None,
    ) -> "ExactDeliveryRequest":
        if not key or not variant or not subject or f"[School-OS:{key}]" not in subject:
            raise DeliveryError("delivery requires a key, variant, and exact subject key marker")
        if not isinstance(text, bytes) or not isinstance(html, bytes):
            raise DeliveryError("delivery bodies must be exact bytes")
        if audio is not None and not isinstance(audio, ExactAudioAttachment):
            raise DeliveryError("delivery audio must be an exact verified attachment")
        return cls(
            key, variant, _addresses(to, "To"),
            _addresses(cc, "CC", allow_empty=True),
            _addresses(bcc, "BCC", allow_empty=True), subject, text, html, audio,
        )

    def intent(self) -> dict[str, Any]:
        return {
            **self.base_intent(),
            "audio": self.audio.intent() if self.audio is not None else None,
        }

    def base_intent(self) -> dict[str, Any]:
        """Exact delivery fields known before the optional audio call."""
        return {
            "bcc": list(self.bcc), "cc": list(self.cc), "html_sha256": sha256_bytes(self.html),
            "key": self.key, "subject": self.subject, "text_sha256": sha256_bytes(self.text),
            "to": list(self.to), "variant": self.variant,
        }

    @property
    def base_fingerprint(self) -> str:
        return sha256_bytes(canonical_json_bytes(self.base_intent()))

    @property
    def fingerprint(self) -> str:
        return sha256_bytes(canonical_json_bytes(self.intent()))

    def gmail_args(self) -> dict[str, Any]:
        """Return the exact installed Gmail connector request, without IDs."""
        try:
            text = self.text.decode("utf-8")
            html = self.html.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise DeliveryError("Gmail delivery bodies must be strict UTF-8") from exc
        alternative = {
            "mime_type": "multipart/alternative",
            "parts": [
                {"body": {"content": text}, "charset": "utf-8", "content_disposition": "inline", "mime_type": "text/plain"},
                {"body": {"content": html}, "charset": "utf-8", "content_disposition": "inline", "mime_type": "text/html"},
            ],
        }
        payload: dict[str, Any] = alternative
        if self.audio is not None:
            payload = {
                "mime_type": "multipart/mixed",
                "parts": [
                    alternative,
                    {
                        "body": {
                            "base64_url_content": base64.urlsafe_b64encode(
                                self.audio.data
                            ).decode("ascii").rstrip("=")
                        },
                        "content_disposition": "attachment",
                        "filename": self.audio.filename,
                        "mime_type": "audio/mpeg",
                    },
                ],
            }
        result: dict[str, Any] = {
            "payload": payload,
            "response_fields": ["id", "thread_id", "label_ids"],
            "subject": self.subject,
            "to": ", ".join(self.to),
        }
        if self.cc:
            result["cc"] = ", ".join(self.cc)
        if self.bcc:
            result["bcc"] = ", ".join(self.bcc)
        return result


def _header_addresses(message: Message, name: str) -> tuple[str, ...]:
    return tuple(address.lower() for _, address in getaddresses(message.get_all(name, [])) if address)


def verify_sent_message(
    request: ExactDeliveryRequest, observation: Mapping[str, Any],
    expected_provider_message_id: str,
) -> str:
    """Verify one returned Gmail ID against labels, recipients, marker, and MIME."""
    identity = observation.get("id")
    raw = observation.get("raw")
    labels = observation.get("label_ids")
    if not isinstance(identity, str) or not identity or not isinstance(raw, bytes):
        raise DeliveryError("delivery readback lacks exact identity or raw MIME bytes")
    if identity != expected_provider_message_id:
        raise DeliveryError("delivery readback provider identity disagrees")
    if not isinstance(labels, (list, tuple)) or "SENT" not in labels:
        raise DeliveryError("delivery readback is not labeled SENT")
    message = BytesParser(policy=policy.default).parsebytes(raw)
    if message.get("Subject") != request.subject or f"[School-OS:{request.key}]" not in request.subject:
        raise DeliveryError("delivery subject or key marker disagrees")
    for header, expected in (("To", request.to), ("Cc", request.cc), ("Bcc", request.bcc)):
        if sorted(_header_addresses(message, header)) != sorted(expected):
            raise DeliveryError(f"delivery {header} recipients disagree")
    parts: dict[str, list[bytes]] = {"text/plain": [], "text/html": []}
    attachments: list[tuple[str | None, str, bytes]] = []
    for part in message.walk():
        content_type = part.get_content_type()
        disposition = part.get_content_disposition()
        if disposition == "attachment":
            payload = part.get_payload(decode=True)
            if not isinstance(payload, bytes):
                raise DeliveryError("delivery MIME attachment is unavailable")
            attachments.append((part.get_filename(), content_type, payload))
        elif content_type in parts:
            payload = part.get_payload(decode=True)
            if not isinstance(payload, bytes):
                raise DeliveryError("delivery MIME body is unavailable")
            parts[content_type].append(payload)
    if parts["text/plain"] != [request.text] or parts["text/html"] != [request.html]:
        raise DeliveryError("delivery MIME bodies disagree with intended exact bytes")
    expected_attachments = [] if request.audio is None else [
        (request.audio.filename, "audio/mpeg", request.audio.data)
    ]
    if attachments != expected_attachments:
        raise DeliveryError("delivery MIME attachment disagrees with intended exact bytes")
    return identity


Persist = Callable[[Mapping[str, Any]], None]
ReadLedger = Callable[[], Optional[Mapping[str, Any]]]
Send = Callable[[ExactDeliveryRequest], Mapping[str, Any]]
ReadSent = Callable[[str], Mapping[str, Any]]
SearchSent = Callable[[Optional[str]], tuple[Iterable[Mapping[str, Any]], Optional[str]]]


def _persist_exact(persist: Persist, read: ReadLedger, candidate: Mapping[str, Any], label: str) -> dict[str, Any]:
    expected = dict(candidate)
    persist(expected)
    observed = read()
    if not isinstance(observed, Mapping) or canonical_json_bytes(dict(observed)) != canonical_json_bytes(expected):
        raise DeliveryError(f"{label} did not read back exactly")
    return expected


def reserve_delivery(
    request: ExactDeliveryRequest, *, audio_planned: bool,
    read_ledger: ReadLedger, persist_ledger: Persist,
) -> dict[str, Any]:
    """Durably reserve one delivery before attempting its optional audio."""
    if request.audio is not None:
        raise DeliveryError("delivery must be reserved before audio exists")
    candidate = {
        "audio": {"status": "pending" if audio_planned else "not_requested"},
        "base_fingerprint": request.base_fingerprint,
        "base_intent": request.base_intent(),
        "schema_version": 1,
        "status": "reserved",
    }
    current = read_ledger()
    if current is None:
        return _persist_exact(
            persist_ledger, read_ledger, candidate, "delivery reservation",
        )
    if not _exactly(current, candidate):
        raise DeliveryError("delivery key already has a different reservation or effect")
    return dict(current)


def record_reserved_audio(
    request: ExactDeliveryRequest, *, outcome: str,
    read_ledger: ReadLedger, persist_ledger: Persist,
) -> dict[str, Any]:
    """Record the single audio outcome before the send effect is authorized."""
    if outcome not in {"verified", "skipped_empty", "unavailable", "failed"}:
        raise DeliveryError("audio outcome is unsupported")
    current = read_ledger()
    if (
        not isinstance(current, Mapping) or current.get("status") != "reserved"
        or current.get("base_fingerprint") != request.base_fingerprint
        or current.get("base_intent") != request.base_intent()
    ):
        raise DeliveryError("audio outcome has no matching delivery reservation")
    prior_audio = current.get("audio")
    if not isinstance(prior_audio, Mapping) or prior_audio.get("status") != "pending":
        raise DeliveryError("reserved audio has already reached a terminal outcome")
    if outcome == "verified":
        if request.audio is None:
            raise DeliveryError("verified audio outcome lacks exact MP3 bytes")
        audio = {"status": "verified", **request.audio.intent()}
    else:
        if request.audio is not None:
            raise DeliveryError("failed or skipped audio outcome cannot attach bytes")
        audio = {"status": outcome}
    candidate = {**dict(current), "audio": audio}
    return _persist_exact(
        persist_ledger, read_ledger, candidate, "reserved audio outcome",
    )


def _effect(request: ExactDeliveryRequest, outcome: str, provider_message_id: str | None = None) -> dict[str, Any]:
    return {
        "effect": "mail.send", "fingerprint": request.fingerprint, "key": request.key,
        "outcome": outcome, "provider_message_id": provider_message_id,
    }


def _exactly(value: Mapping[str, Any] | None, expected: Mapping[str, Any]) -> bool:
    return isinstance(value, Mapping) and canonical_json_bytes(dict(value)) == canonical_json_bytes(dict(expected))


def deliver_exact(
    request: ExactDeliveryRequest, *, read_ledger: ReadLedger, persist_ledger: Persist,
    persist_effect_checkpoint: Persist, read_effect_checkpoint: ReadLedger,
    send: Send, read_sent: ReadSent, search_sent: SearchSent,
) -> dict[str, Any]:
    """Send once after durable intent, or reconcile one exact unknown effect."""
    current = read_ledger()
    reservation: dict[str, Any] | None = None
    if current is not None:
        if current.get("status") == "reserved":
            if (
                current.get("base_fingerprint") != request.base_fingerprint
                or current.get("base_intent") != request.base_intent()
            ):
                raise DeliveryError("delivery reservation differs from send intent")
            audio = current.get("audio")
            if not isinstance(audio, Mapping) or audio.get("status") == "pending":
                raise DeliveryError("delivery audio outcome is not terminal")
            if audio.get("status") == "verified":
                if request.audio is None or dict(audio) != {
                    "status": "verified", **request.audio.intent(),
                }:
                    raise DeliveryError("verified audio reservation differs from send attachment")
            elif request.audio is not None or audio.get("status") not in {
                "not_requested", "skipped_empty", "unavailable", "failed",
            }:
                raise DeliveryError("delivery audio disposition differs from send intent")
            if read_effect_checkpoint() is not None:
                raise DeliveryError("reserved delivery unexpectedly has an effect checkpoint")
            reservation = dict(current)
            current = None
        else:
            if current.get("fingerprint") != request.fingerprint or current.get("intent") != request.intent():
                raise DeliveryError("delivery key already exists with different exact intent")
    if current is not None:
        if current.get("status") == "confirmed":
            identity = current.get("provider_message_id")
            if not isinstance(identity, str):
                raise DeliveryError("confirmed delivery ledger lacks provider identity")
            verify_sent_message(request, read_sent(identity), identity)
            observed_effect = read_effect_checkpoint()
            pending_effect = _effect(request, "pending")
            confirmed_effect = _effect(request, "confirmed", identity)
            if observed_effect is not None and not (
                _exactly(observed_effect, pending_effect) or _exactly(observed_effect, confirmed_effect)
            ):
                raise DeliveryError("delivery effect checkpoint disagrees with confirmed intent")
            if not _exactly(observed_effect, confirmed_effect):
                _persist_exact(
                    persist_effect_checkpoint, read_effect_checkpoint, confirmed_effect,
                    "confirmed send checkpoint",
                )
            return {"outcome": "suppressed", "provider_message_id": identity, "ledger": dict(current)}
        if current.get("status") != "pending":
            raise DeliveryError("delivery ledger has an unsupported state")
        observed_effect = read_effect_checkpoint()
        pending_effect = _effect(request, "pending")
        if observed_effect is not None:
            if not _exactly(observed_effect, pending_effect):
                raise DeliveryError("pending delivery effect checkpoint disagrees")
            return _reconcile(
                request, current, read_ledger, persist_ledger,
                persist_effect_checkpoint, read_effect_checkpoint, read_sent, search_sent,
            )
        _persist_exact(
            persist_effect_checkpoint, read_effect_checkpoint, pending_effect,
            "pending send checkpoint",
        )
        pending = dict(current)
    else:
        pending = {
            "fingerprint": request.fingerprint, "intent": request.intent(), "provider_message_id": None,
            "schema_version": 1, "status": "pending",
        }
        if reservation is not None:
            pending["reservation"] = reservation
        pending = _persist_exact(persist_ledger, read_ledger, pending, "pending delivery ledger")
        _persist_exact(
            persist_effect_checkpoint, read_effect_checkpoint, _effect(request, "pending"),
            "pending send checkpoint",
        )

    try:
        response = send(request)
    except Exception as exc:
        raise DeliveryError("send outcome is unknown; reconcile before any retry") from exc
    identity = response.get("id") if isinstance(response, Mapping) else None
    if not isinstance(identity, str) or not identity:
        raise DeliveryError("send outcome is unknown; provider identity is unavailable")
    verify_sent_message(request, read_sent(identity), identity)
    confirmed = dict(pending)
    confirmed.update({"status": "confirmed", "provider_message_id": identity})
    _persist_exact(persist_ledger, read_ledger, confirmed, "confirmed delivery ledger")
    _persist_exact(
        persist_effect_checkpoint, read_effect_checkpoint, _effect(request, "confirmed", identity),
        "confirmed send checkpoint",
    )
    return {"outcome": "confirmed", "provider_message_id": identity, "ledger": confirmed}


def _reconcile(
    request: ExactDeliveryRequest, pending: Mapping[str, Any], read_ledger: ReadLedger,
    persist_ledger: Persist, persist_effect_checkpoint: Persist,
    read_effect_checkpoint: ReadLedger, read_sent: ReadSent, search_sent: SearchSent,
) -> dict[str, Any]:
    matches: list[str] = []
    token: str | None = None
    seen: set[str | None] = set()
    while True:
        if token in seen:
            raise DeliveryError("Sent lookup pagination did not make progress")
        seen.add(token)
        items, next_token = search_sent(token)
        for item in items:
            identity = item.get("id") if isinstance(item, Mapping) else None
            if not isinstance(identity, str) or not identity:
                raise DeliveryError("Sent lookup returned an invalid candidate")
            try:
                verify_sent_message(request, read_sent(identity), identity)
            except DeliveryError:
                continue
            matches.append(identity)
        if next_token is None:
            break
        if not isinstance(next_token, str) or not next_token:
            raise DeliveryError("Sent lookup returned an invalid next page token")
        token = next_token
    if len(matches) != 1:
        raise DeliveryError(f"unknown delivery reconciliation found {len(matches)} exact matches")
    confirmed = dict(pending)
    confirmed.update({"status": "confirmed", "provider_message_id": matches[0]})
    _persist_exact(persist_ledger, read_ledger, confirmed, "reconciled delivery ledger")
    _persist_exact(
        persist_effect_checkpoint, read_effect_checkpoint,
        _effect(request, "confirmed", matches[0]), "reconciled send checkpoint",
    )
    return {"outcome": "reconciled", "provider_message_id": matches[0], "ledger": confirmed}
