"""Shared exact Drive artifact storage for connected School-OS workers."""

from __future__ import annotations

import base64
import binascii
import os
import tempfile
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol


class ConnectedStorageError(ValueError):
    """Raised when a connected Drive artifact cannot be trusted."""


@dataclass(frozen=True)
class DriveReference:
    """Exact Drive identity, scope, media type, content URL, and optional guard."""

    object_id: str
    parent_id: str
    mime_type: str
    url: str
    version: str | None = None

    def current(self) -> "DriveReference":
        """Return the same exact object identity without a stale write version."""
        return DriveReference(self.object_id, self.parent_id, self.mime_type, self.url)


@dataclass(frozen=True)
class StoredArtifact:
    """Complete bytes plus the current readback reference."""

    reference: DriveReference
    data: bytes


class ArtifactStore(Protocol):
    def read(self, reference: DriveReference) -> StoredArtifact: ...
    def read_named(self, parent: DriveReference, name: str) -> StoredArtifact | None: ...
    def write_immutable(self, parent: DriveReference, name: str, data: bytes, mime_type: str) -> StoredArtifact: ...
    def replace(self, reference: DriveReference, data: bytes, mime_type: str) -> StoredArtifact: ...


def _size(value: Any, label: str) -> int:
    if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    raise ConnectedStorageError(f"{label} lacks an exact byte size")


class CodexDriveArtifactStore:
    """Map the observed Codex Drive shapes to exact artifact read/write guards."""

    def __init__(self, drive: Any, *, scratch_directory: Path) -> None:
        self.drive, self.scratch_directory = drive, scratch_directory

    @staticmethod
    def _bytes(value: Any) -> bytes:
        if not isinstance(value, str):
            raise ConnectedStorageError("Drive fetch lacks base64 artifact bytes")
        try:
            return base64.b64decode(value, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise ConnectedStorageError("Drive fetch has invalid base64 artifact bytes") from exc

    def read(self, reference: DriveReference) -> StoredArtifact:
        metadata = self.drive.metadata(
            reference.object_id, fields="id,mimeType,parents,modifiedTime,size"
        )
        if (
            not isinstance(metadata, Mapping)
            or metadata.get("id") != reference.object_id
            or metadata.get("mime_type") != reference.mime_type
        ):
            raise ConnectedStorageError("Drive metadata disagrees with admitted artifact reference")
        parents = metadata.get("parent_ids")
        if not isinstance(parents, list) or parents != [reference.parent_id]:
            raise ConnectedStorageError("Drive artifact parent is not the admitted parent")
        version = metadata.get("modified_time")
        if not isinstance(version, str) or not version:
            raise ConnectedStorageError("Drive metadata lacks exact version evidence")
        if reference.version is not None and version != reference.version:
            raise ConnectedStorageError("Drive artifact version differs from admitted reference")
        fetched = self.drive.fetch(reference.url, raw=True, include_base64=True)
        if not isinstance(fetched, Mapping) or fetched.get("id") != reference.object_id:
            raise ConnectedStorageError("Drive fetch identity disagrees with admitted artifact reference")
        data = self._bytes(fetched.get("b64_string"))
        if _size(metadata.get("size"), "Drive metadata") != len(data):
            raise ConnectedStorageError("Drive metadata byte size disagrees with fetched bytes")
        if _size(fetched.get("file_size_bytes"), "Drive fetch") != len(data):
            raise ConnectedStorageError("Drive fetch byte size disagrees with fetched bytes")
        empty_marker = fetched.get("is_empty")
        if not isinstance(empty_marker, bool) or empty_marker != (len(data) == 0):
            raise ConnectedStorageError("Drive fetch empty marker disagrees with fetched bytes")
        current = DriveReference(
            reference.object_id, reference.parent_id, reference.mime_type,
            reference.url, version,
        )
        return StoredArtifact(current, data)

    def read_named(self, parent: DriveReference, name: str) -> StoredArtifact | None:
        listing = self.drive.list_folder(parent.url, top_k=1000)
        files = listing.get("files") if isinstance(listing, Mapping) else None
        if not isinstance(files, list):
            raise ConnectedStorageError("Drive folder listing is malformed")
        matches = [
            item for item in files
            if isinstance(item, Mapping) and item.get("title") == name
        ]
        if len(matches) > 1:
            raise ConnectedStorageError("Drive folder has ambiguous artifact name")
        if not matches:
            return None
        item = matches[0]
        if not all(
            isinstance(item.get(key), str) and item[key]
            for key in ("id", "mime_type", "url")
        ):
            raise ConnectedStorageError("Drive folder listing lacks exact artifact reference")
        parents = item.get("parent_ids")
        if parents is not None and parents != [parent.object_id]:
            raise ConnectedStorageError("Drive folder listing returned an artifact outside its parent")
        return self.read(DriveReference(
            item["id"], parent.object_id, item["mime_type"], item["url"], None,
        ))

    def _upload_bytes(
        self, name: str, data: bytes, mime_type: str, parent: DriveReference,
        existing_id: str | None = None,
    ) -> Mapping[str, Any]:
        if not isinstance(data, bytes) or not isinstance(mime_type, str) or not mime_type:
            raise ConnectedStorageError("Drive write requires exact bytes and a MIME type")
        self.scratch_directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        os.chmod(self.scratch_directory, 0o700)
        descriptor, raw_path = tempfile.mkstemp(prefix="artifact-", dir=self.scratch_directory)
        path = Path(raw_path)
        try:
            os.fchmod(descriptor, 0o600)
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            absolute_path = str(path.resolve(strict=True))
            result = (
                self.drive.update(existing_id, file_uri=absolute_path, mime_type=mime_type)
                if existing_id is not None
                else self.drive.upload(
                    absolute_path, file_name=name, mime_type=mime_type,
                    parent_folder_id=parent.object_id,
                )
            )
            if not isinstance(result, Mapping):
                raise ConnectedStorageError("Drive write result is malformed")
            return result
        finally:
            path.unlink(missing_ok=True)

    @staticmethod
    def _written_reference(
        result: Mapping[str, Any], parent: DriveReference, mime_type: str,
        expected_id: str | None = None,
    ) -> DriveReference:
        identifier = result.get("id")
        if (
            result.get("success") is not True
            or not isinstance(identifier, str) or not identifier
            or (expected_id is not None and identifier != expected_id)
        ):
            raise ConnectedStorageError("Drive write result has the wrong exact artifact identity")
        if result.get("mime_type") != mime_type:
            raise ConnectedStorageError("Drive write result has the wrong MIME type")
        parents = result.get("parent_ids")
        parent_id = result.get("parent_id")
        if parents is not None:
            parent_matches = parents == [parent.object_id]
        else:
            parent_matches = parent_id == parent.object_id
        if not parent_matches:
            raise ConnectedStorageError("Drive write result has the wrong parent")
        url = result.get("url")
        version = result.get("modified_time")
        if not isinstance(url, str) or not url:
            raise ConnectedStorageError("Drive write result lacks a readback URL")
        if version is not None and (not isinstance(version, str) or not version):
            raise ConnectedStorageError("Drive write result has invalid version evidence")
        return DriveReference(identifier, parent.object_id, mime_type, url, version)

    def write_immutable(
        self, parent: DriveReference, name: str, data: bytes, mime_type: str,
    ) -> StoredArtifact:
        existing = self.read_named(parent, name)
        if existing is not None:
            if existing.reference.mime_type != mime_type:
                raise ConnectedStorageError("immutable Drive artifact MIME type differs")
            if existing.data != data:
                raise ConnectedStorageError("immutable Drive artifact name already has different bytes")
            return existing
        reference = self._written_reference(
            self._upload_bytes(name, data, mime_type, parent), parent, mime_type,
        )
        readback = self.read(reference)
        if readback.data != data:
            raise ConnectedStorageError("new Drive artifact does not read back exactly")
        return readback

    def replace(
        self, reference: DriveReference, data: bytes, mime_type: str,
    ) -> StoredArtifact:
        if reference.mime_type != mime_type:
            raise ConnectedStorageError("Drive replacement MIME type differs from admitted reference")
        current = self.read(reference)
        parent = DriveReference(
            current.reference.parent_id, "", "application/vnd.google-apps.folder", ""
        )
        result = self._upload_bytes(
            "replacement", data, mime_type, parent, existing_id=reference.object_id,
        )
        written = self._written_reference(
            result, parent, mime_type, expected_id=reference.object_id,
        )
        readback = self.read(written)
        if readback.data != data:
            raise ConnectedStorageError("replaced Drive artifact does not read back exactly")
        return readback
