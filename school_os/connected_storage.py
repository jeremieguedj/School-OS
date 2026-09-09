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
from urllib.parse import parse_qsl, urlsplit

from .references import ReferenceStorage, StoredObject


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


_SCOPED_ITEM_TYPES = ("document", "image", "folder")
_SCOPED_PAGE_SIZE = 1000
_MAX_SCOPED_PAGES_PER_TYPE = 1000
_GOOGLE_DRIVE_HOSTS = frozenset({"drive.google.com", "docs.google.com"})


def _same_google_drive_object_url(expected: str, observed: str, object_id: str) -> bool:
    """Allow only Google's ``usp=drivesdk`` decoration on one exact object URL."""
    if expected == observed:
        return True
    if not all(isinstance(item, str) and item for item in (expected, observed, object_id)):
        return False
    expected_parts, observed_parts = urlsplit(expected), urlsplit(observed)
    if (
        expected_parts.scheme != "https" or observed_parts.scheme != "https"
        or expected_parts.netloc not in _GOOGLE_DRIVE_HOSTS
        or observed_parts.netloc != expected_parts.netloc
        or expected_parts.path != observed_parts.path
        or expected_parts.fragment != observed_parts.fragment
    ):
        return False
    path_parts = tuple(part for part in expected_parts.path.split("/") if part)
    try:
        object_index = path_parts.index("d") + 1
    except ValueError:
        return False
    if object_index >= len(path_parts) or path_parts[object_index] != object_id:
        return False

    def _meaningful_query(query: str) -> list[tuple[str, str]]:
        return [
            item for item in parse_qsl(query, keep_blank_values=True)
            if item != ("usp", "drivesdk")
        ]

    return _meaningful_query(expected_parts.query) == _meaningful_query(observed_parts.query)


def _complete_scoped_search(drive: Any, parent_id: str) -> tuple[dict[str, Any], ...]:
    """Exhaust every advertised metadata category for one exact Drive parent."""
    if not isinstance(parent_id, str) or not parent_id:
        raise ConnectedStorageError("Drive listing parent identity is required")
    items: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for item_type in _SCOPED_ITEM_TYPES:
        token: str | None = None
        seen_tokens: set[str] = set()
        for _page_number in range(_MAX_SCOPED_PAGES_PER_TYPE):
            page = drive.search_page(
                parent_id, item_type=item_type, topn=_SCOPED_PAGE_SIZE,
                page_token=token,
            )
            if (
                not isinstance(page, Mapping)
                or set(page) - {"results", "next_page_token"}
                or not isinstance(page.get("results"), list)
                or len(page["results"]) > _SCOPED_PAGE_SIZE
            ):
                raise ConnectedStorageError("Drive scoped search page is malformed")
            for value in page["results"]:
                if not isinstance(value, Mapping):
                    raise ConnectedStorageError("Drive scoped search member is malformed")
                identifier = value.get("id")
                title = value.get("title")
                if not isinstance(identifier, str) or not identifier or not isinstance(title, str) or not title:
                    raise ConnectedStorageError("Drive scoped search member lacks exact identity or title")
                if identifier in seen_ids:
                    raise ConnectedStorageError("Drive scoped search returned a duplicate object identity")
                seen_ids.add(identifier)
                items.append(dict(value))
            next_token = page.get("next_page_token")
            if next_token is None:
                break
            if not isinstance(next_token, str) or not next_token or next_token in seen_tokens:
                raise ConnectedStorageError("Drive scoped search continuation is invalid or repeated")
            seen_tokens.add(next_token)
            token = next_token
        else:
            raise ConnectedStorageError("Drive scoped search exceeded its finite page bound")
    return tuple(items)


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
        files = _complete_scoped_search(self.drive, parent.object_id)
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


class CodexDriveReferenceStorage(ReferenceStorage):
    """Expose exact Drive objects to admitted-generation recovery.

    This adapter intentionally supports direct ID reads, which is all package
    recovery needs. A name lookup is available only after the finite bridge
    exhausts every advertised scoped-search category and continuation token;
    malformed or repeated pagination evidence blocks completeness.
    """

    _FOLDER_MIME = "application/vnd.google-apps.folder"

    def __init__(self, drive: Any, *, expected_urls: Mapping[str, str] | None = None) -> None:
        self.drive = drive
        self.expected_urls = dict(expected_urls or {})
        self._urls: dict[str, str] = {}

    @staticmethod
    def _metadata(value: Any, object_id: str) -> tuple[str, tuple[str, ...], str | None, str, str, int]:
        if not isinstance(value, Mapping) or value.get("id") != object_id:
            raise ConnectedStorageError("Drive metadata disagrees with requested object identity")
        mime_type = value.get("mime_type")
        url = value.get("url")
        name = value.get("title")
        parents = value.get("parent_ids")
        version = value.get("modified_time")
        if not all(isinstance(item, str) and item for item in (mime_type, url, name, version)):
            raise ConnectedStorageError("Drive metadata lacks exact object fields")
        if not isinstance(parents, list) or any(not isinstance(item, str) or not item for item in parents):
            raise ConnectedStorageError("Drive metadata lacks exact parent evidence")
        size = 0 if mime_type == CodexDriveReferenceStorage._FOLDER_MIME else _size(value.get("size"), "Drive metadata")
        return mime_type, tuple(parents), version, url, name, size

    def _read_metadata(self, object_id: str) -> tuple[str, tuple[str, ...], str, str, str, int]:
        if not isinstance(object_id, str) or not object_id:
            raise ConnectedStorageError("Drive object ID is required")
        result = self._metadata(
            self.drive.metadata(object_id, fields="id,name,mimeType,parents,modifiedTime,size,webViewLink"), object_id,
        )
        self._urls[object_id] = result[3]
        return result

    def read(self, object_id: str) -> StoredObject | None:
        mime_type, parents, version, url, name, size = self._read_metadata(object_id)
        expected_url = self.expected_urls.get(object_id)
        if expected_url is not None and not _same_google_drive_object_url(expected_url, url, object_id):
            raise ConnectedStorageError("Drive metadata URL differs from the admitted object URL")
        kind = "folder" if mime_type == self._FOLDER_MIME else "file"
        if kind == "folder":
            return StoredObject(object_id, kind, parents[0] if len(parents) == 1 else None, parents, mime_type, version, name, None)
        fetched = self.drive.fetch(url, raw=True, include_base64=True)
        if not isinstance(fetched, Mapping) or fetched.get("id") != object_id:
            raise ConnectedStorageError("Drive fetch identity disagrees with metadata")
        data = CodexDriveArtifactStore._bytes(fetched.get("b64_string"))
        if _size(fetched.get("file_size_bytes"), "Drive fetch") != len(data) or size != len(data):
            raise ConnectedStorageError("Drive fetched byte size disagrees with metadata")
        if fetched.get("is_empty") is not (len(data) == 0):
            raise ConnectedStorageError("Drive fetch empty marker disagrees with bytes")
        return StoredObject(object_id, kind, parents[0] if len(parents) == 1 else None, parents, mime_type, version, name, data)

    def list_scoped(self, parent_id: str) -> list[StoredObject]:
        if not isinstance(parent_id, str) or not parent_id:
            raise ConnectedStorageError("Drive listing parent identity is required")
        parent = self.read(parent_id)
        if parent is None or parent.kind != "folder":
            raise ConnectedStorageError("Drive listing parent is not an exact folder")
        files = _complete_scoped_search(self.drive, parent_id)
        objects: list[StoredObject] = []
        for item in files:
            if not isinstance(item, Mapping):
                raise ConnectedStorageError("Drive listing member is malformed")
            identifier = item.get("id")
            parents = item.get("parent_ids")
            if not isinstance(identifier, str) or not identifier or parents != [parent_id]:
                raise ConnectedStorageError("Drive listing member lacks direct parent evidence")
            object_ = self.read(identifier)
            if object_ is None or object_.parent_id != parent_id:
                raise ConnectedStorageError("Drive listing member readback differs from listing")
            objects.append(object_)
        return objects
