"""Small filesystem and effect-sink fakes; none contact real providers."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from school_os.references import StoredObject


class FilesystemStorage:
    def __init__(self, root: Path, objects: dict[str, StoredObject]) -> None:
        self.root = root
        self.objects = objects

    def read(self, object_id: str) -> StoredObject | None:
        return self.objects.get(object_id)

    def list_scoped(self, parent_id: str) -> list[StoredObject]:
        return [object_ for object_ in self.objects.values() if object_.parent_id == parent_id]


@dataclass(frozen=True)
class FixtureMessage:
    message_id: str
    body: str


class FixtureMail:
    def __init__(self, messages: list[FixtureMessage] | None = None) -> None:
        self.messages = list(messages or [])

    def search(self) -> list[FixtureMessage]:
        return list(self.messages)


class FixtureTasks:
    def __init__(self) -> None:
        self.tasks: list[dict[str, str]] = []


class SendSink:
    def __init__(self) -> None:
        self.deliveries: list[bytes] = []

    def send(self, content: bytes) -> str:
        self.deliveries.append(content)
        return f"synthetic-send-{len(self.deliveries)}"
