"""Small provider-neutral interfaces for the connected daily path.

These protocols deliberately describe only provider I/O. They do not select an
adapter, interpret school content, or encode household policy. Concrete
adapters establish an effect outcome by their own documented readback.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal, Protocol


EffectOutcome = Literal["confirmed", "definitely_not_applied", "unknown"]


@dataclass(frozen=True)
class ReadResult:
    """A complete provider object read with identity and version evidence."""

    data: bytes
    identity: str
    kind: str
    parent: str | None
    mime_type: str | None
    version: str | None


@dataclass(frozen=True)
class Page:
    """One complete-or-continuable provider listing page."""

    items: tuple[Mapping[str, Any], ...]
    next_page_token: str | None


@dataclass(frozen=True)
class EffectResult:
    """The only normalized mutation outcome accepted by core recovery code."""

    outcome: EffectOutcome
    identity: str | None
    verification: Mapping[str, Any]


class StoragePort(Protocol):
    def read(self, reference: str) -> ReadResult: ...

    def list_scoped(self, parent: str, page_token: str | None) -> Page: ...

    def create(self, parent: str, name: str, data: bytes, mime_type: str) -> EffectResult: ...

    def replace(self, reference: str, data: bytes, expected_version: str | None = None) -> EffectResult: ...


class MailPort(Protocol):
    def search(self, scope: Mapping[str, Any], page_token: str | None) -> Page: ...

    def read_conversation(self, identity: str) -> Mapping[str, Any]: ...

    def read_attachment(self, identity: str) -> ReadResult: ...

    def send(self, request: Mapping[str, Any]) -> EffectResult: ...

    def find_delivery(self, lookup: Mapping[str, Any]) -> Page: ...


class TaskPort(Protocol):
    def read_snapshot(self, scope: Mapping[str, Any], page_token: str | None) -> Page: ...

    def read_completed(self, scope: Mapping[str, Any], page_token: str | None) -> Page: ...

    def read_activity(self, scope: Mapping[str, Any], page_token: str | None) -> Page: ...

    def read_comments(self, provider_id: str, page_token: str | None) -> Page: ...

    def read_task(self, provider_id: str) -> Mapping[str, Any] | None: ...

    def find_by_canonical_id(self, task_id: str) -> Page: ...

    def create_task(self, candidate: Mapping[str, Any]) -> EffectResult: ...

    def apply_patch(self, provider_id: str, patch: Mapping[str, Any]) -> EffectResult: ...

    def write_comment(self, provider_id: str, comment: Mapping[str, Any]) -> EffectResult: ...


class SchedulerPort(Protocol):
    def inspect(self, schedule_reference: str) -> Mapping[str, Any]: ...

    def trigger(self, schedule_reference: str) -> EffectResult: ...
