"""Subprocess fixture proving mutable recovery without in-memory references."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from school_os.adapters import Page
from school_os.connected_ingestion import (
    ConnectedIngestionError,
    ConnectedIngestionWorker,
    DriveReference,
    StoredArtifact,
)
from school_os.contracts import canonical_json_bytes

def part(data: bytes) -> dict[str, Any]:
    return {
        "part_id": "plain", "role": "body", "selected_plaintext": True,
        "complete": True, "mime_type": "text/plain", "charset": "utf-8",
        "content_transfer_encoding": "identity", "data": data,
        "raw_part_sha256": hashlib.sha256(data).hexdigest(),
        "raw_part_byte_length": len(data),
        "raw_part_locator": {"kind": "raw_part_bytes", "byte_start": 0, "byte_end": len(data)},
        "provider_unicode": data.decode("utf-8"),
    }


class Source:
    def search(self, _scope: dict[str, Any], token: str | None) -> Page:
        if token is not None:
            return Page((), None)
        return Page(tuple({
            "conversation_id": identity, "byte_size": 1,
            "discovery_message_ids": [f"{identity}-message"],
        } for identity in ("thread-1", "thread-2")), None)

    def read_conversation(self, identity: str) -> dict[str, Any]:
        body = {"thread-1": b"First", "thread-2": b"Second"}[identity]
        return {
            "conversation_id": identity,
            "messages": [{
                "message_id": f"{identity}-message",
                "received_at": "2026-09-08T08:00:00Z", "received_date": "2026-09-08",
                "mime_tree_complete": True, "parts": [part(body)],
                "attachments": [], "html_parts": [],
            }],
        }

    def read_attachment(self, _message_id: str, _attachment_id: str) -> Any:
        raise AssertionError("fixture has no attachments")


class DiskStore:
    def __init__(self, directory: Path) -> None:
        self.directory = directory
        self.directory.mkdir(parents=True, exist_ok=True)
        self.manifest_path = directory / "manifest.json"
        if self.manifest_path.exists():
            self.manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        else:
            self.manifest = {"counter": 1, "objects": {}, "names": {}}

    def _save(self) -> None:
        self.manifest_path.write_text(json.dumps(self.manifest, sort_keys=True), encoding="utf-8")

    def seed(self, reference: DriveReference, data: bytes) -> None:
        self.manifest["objects"][reference.object_id] = {
            "parent_id": reference.parent_id, "mime_type": reference.mime_type,
            "url": reference.url, "version": reference.version,
        }
        (self.directory / f"{reference.object_id}.bin").write_bytes(data)
        self._save()

    def read(self, reference: DriveReference) -> StoredArtifact:
        value = self.manifest["objects"][reference.object_id]
        if reference.parent_id != value["parent_id"] or reference.mime_type != value["mime_type"]:
            raise ConnectedIngestionError("disk fixture identity mismatch")
        if reference.version is not None and reference.version != value["version"]:
            raise ConnectedIngestionError("disk fixture stale version")
        current = DriveReference(
            reference.object_id, value["parent_id"], value["mime_type"],
            value["url"], value["version"],
        )
        return StoredArtifact(current, (self.directory / f"{reference.object_id}.bin").read_bytes())

    def read_named(self, parent: DriveReference, name: str) -> StoredArtifact | None:
        identifier = self.manifest["names"].get(f"{parent.object_id}\0{name}")
        if identifier is None:
            return None
        value = self.manifest["objects"][identifier]
        return self.read(DriveReference(
            identifier, value["parent_id"], value["mime_type"], value["url"], value["version"]
        ))

    def _write(
        self, parent_id: str, name: str, data: bytes, mime_type: str,
        identifier: str | None = None,
    ) -> StoredArtifact:
        self.manifest["counter"] += 1
        identifier = identifier or f"object-{self.manifest['counter']}"
        version = str(self.manifest["counter"])
        current = DriveReference(
            identifier, parent_id, mime_type, f"https://drive.test/{identifier}", version
        )
        self.manifest["objects"][identifier] = {
            "parent_id": parent_id, "mime_type": mime_type,
            "url": current.url, "version": version,
        }
        self.manifest["names"][f"{parent_id}\0{name}"] = identifier
        (self.directory / f"{identifier}.bin").write_bytes(data)
        self._save()
        return StoredArtifact(current, data)

    def write_immutable(
        self, parent: DriveReference, name: str, data: bytes, mime_type: str,
    ) -> StoredArtifact:
        existing = self.read_named(parent, name)
        if existing is not None:
            if existing.reference.mime_type != mime_type or existing.data != data:
                raise ConnectedIngestionError("disk fixture immutable mismatch")
            return existing
        return self._write(parent.object_id, name, data, mime_type)

    def replace(
        self, reference: DriveReference, data: bytes, mime_type: str,
    ) -> StoredArtifact:
        current = self.read(reference)
        return self._write(
            current.reference.parent_id, "mutable", data, mime_type,
            identifier=reference.object_id,
        )


def interpreter(packet: dict[str, Any]) -> dict[str, Any]:
    return {
        "candidates": [{
            "segment_id": segment["segment_id"], "byte_start": 0,
            "byte_end": len(segment["text"].encode()), "candidate_kind": "statement",
            "category": "school", "entity_scope": "household", "text": "Canonical",
            "flags": {"is_update": True, "is_durable": False, "is_guideline": False, "is_action": False},
        } for segment in packet["segments"]],
        "coverage": [{
            "segment_id": segment["segment_id"], "byte_start": 0,
            "byte_end": len(segment["text"].encode()), "outcome": "fact",
            "reason": "school statement",
        } for segment in packet["segments"]],
        "review_cases": [],
    }


def auditor(packet: dict[str, Any], interpreted: dict[str, Any]) -> dict[str, Any]:
    return {
        "packet_sha256": interpreted["packet_sha256"],
        "interpreted_sha256": interpreted["interpreted_sha256"],
        "coverage": [{
            "segment_id": segment["segment_id"], "byte_start": 0,
            "byte_end": len(segment["text"].encode()), "outcome": "fact",
            "source_quote_sha256": hashlib.sha256(segment["text"].encode()).hexdigest(),
            "interpreted_reason_sha256": hashlib.sha256(b"school statement").hexdigest(),
            "audit_disposition": "accepted", "reason": "checked",
        } for segment in packet["segments"]],
        "facts": [{
            "fact_id": fact["fact_id"],
            "source_quote_sha256": hashlib.sha256(fact["source_quote"].encode()).hexdigest(),
            "canonical_text_sha256": hashlib.sha256(fact["text"].encode()).hexdigest(),
            "classification": {
                "candidate_kind": "statement", "category": "school",
                "entity_scope": "household", "flags": fact["flags"],
            },
            "audit_disposition": "accepted", "reason": "checked",
        } for fact in interpreted["facts"]],
        "source_outcomes": [],
    }


def main(directory: Path) -> None:
    store = DiskStore(directory)
    index = DriveReference("index", "root", "application/json", "https://drive.test/index", "1")
    state = DriveReference("state", "root", "application/json", "https://drive.test/state", "1")
    if "index" not in store.manifest["objects"]:
        store.seed(index, canonical_json_bytes({"schema_version": 1, "records": []}))
        store.seed(state, canonical_json_bytes({"schema_version": 1, "completed_conversation_ids": [], "units": []}))
    schemas = {
        name: json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))
        for name in ("source-conversation.schema.json", "fact.schema.json", "extraction-result.schema.json")
    }
    worker = ConnectedIngestionWorker(
        source=Source(), store=store, adapter_id="gmail-connected",
        catalog_schema=schemas["source-conversation.schema.json"],
        fact_schema=schemas["fact.schema.json"],
        extraction_schema=schemas["extraction-result.schema.json"],
        interpreter=interpreter, auditor=auditor,
    )
    catalog_parent = DriveReference(
        "catalog", "root", "application/vnd.google-apps.folder", "https://drive.test/catalog", "1"
    )
    discovery = worker.discover(
        scope={"query": "bounded"}, discovery_parent=catalog_parent,
        discovery_name="runs/fresh-process/discovery.json",
    )
    result = worker.catalog(
        discovery_reference=discovery.inventory.reference, catalog_parent=catalog_parent,
        index_reference=index, work_reference=state, max_records=1, max_bytes=4096,
    )
    print(json.dumps({
        "completed": list(result.completed_units), "written": len(result.artifacts),
        "index_version": result.index.reference.version,
        "state_version": result.work.reference.version,
    }, sort_keys=True))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
