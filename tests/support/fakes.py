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
        self.calls: list[str] = []

    def list_tasks(self) -> list[dict[str, str]]:
        self.calls.append("list")
        return [dict(task) for task in self.tasks]

    def create_task(self, candidate: dict[str, str]) -> dict[str, str]:
        self.calls.append("create")
        task = {**candidate, "provider_object_id": f"synthetic-task-{len(self.tasks) + 1}"}
        self.tasks.append(task)
        return dict(task)

    def read_task(self, provider_object_id: str) -> dict[str, str] | None:
        self.calls.append("read")
        return next((dict(task) for task in self.tasks if task["provider_object_id"] == provider_object_id), None)

    def apply_patch(self, provider_object_id: str, patch: dict[str, str]) -> dict[str, str]:
        self.calls.append("patch")
        for task in self.tasks:
            if task["provider_object_id"] == provider_object_id:
                task.update(patch)
                return dict(task)
        raise KeyError(provider_object_id)


class SendSink:
    def __init__(self) -> None:
        self.deliveries: list[bytes] = []

    def send(self, content: bytes) -> str:
        self.deliveries.append(content)
        return f"synthetic-send-{len(self.deliveries)}"
