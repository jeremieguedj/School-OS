"""Deterministic immutable bundles for Drive-canonical logical state."""

from __future__ import annotations

import io
import json
import re
import tarfile
from dataclasses import dataclass
from pathlib import PurePosixPath
from types import MappingProxyType
from typing import Any, Mapping

from .contracts import canonical_json_bytes, sha256_bytes


class BundleError(ValueError):
    """Raised when bundle bytes are unsafe, non-canonical, or inconsistent."""


BUNDLE_FORMAT = "school-os-bundle-v1"
MANIFEST_PATH = "BUNDLE-MANIFEST.json"
MAX_ENTRY_COUNT = 10_000
MAX_PATH_CODEPOINTS = 256
_LOWER_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_SAFE_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_LIMITS = {
    "state": (32 * 1024 * 1024, 8 * 1024 * 1024),
    "source": (64 * 1024 * 1024, 32 * 1024 * 1024),
    "output": (64 * 1024 * 1024, 32 * 1024 * 1024),
}


@dataclass(frozen=True)
class BundleEntry:
    """One exact logical member and its interpretation metadata."""

    data: bytes
    role: str
    media_type: str
    schema_id: str | None = None


@dataclass(frozen=True)
class VerifiedBundle:
    """A fully verified manifest and immutable member byte mapping."""

    manifest: Mapping[str, Any]
    entries: Mapping[str, bytes]
    sha256: str


@dataclass(frozen=True)
class BundleMemberReference:
    """Exact physical bundle plus one declared logical member identity."""

    bundle_reference: Mapping[str, Any]
    bundle_sha256: str
    entry_path: str
    entry_sha256: str
    byte_length: int

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "BundleMemberReference":
        if not isinstance(value, Mapping) or set(value) != {
            "bundle_reference", "bundle_sha256", "entry_path", "entry_sha256",
            "byte_length",
        }:
            raise BundleError("bundle member reference has an unsupported shape")
        physical = value.get("bundle_reference")
        if not isinstance(physical, Mapping) or set(physical) - {
            "object_id", "kind", "permitted_ancestor_id", "mime_type", "version",
        }:
            raise BundleError("bundle member physical reference is malformed")
        if (
            physical.get("kind") != "file"
            or not all(isinstance(physical.get(key), str) and physical[key] for key in (
                "object_id", "permitted_ancestor_id", "mime_type", "version",
            ))
        ):
            raise BundleError("bundle member physical reference is incomplete")
        length = value.get("byte_length")
        if isinstance(length, bool) or not isinstance(length, int) or length < 0:
            raise BundleError("bundle member reference has an invalid byte length")
        return cls(
            MappingProxyType(dict(physical)),
            _required_hash(value.get("bundle_sha256"), "bundle member bundle hash"),
            _safe_path(value.get("entry_path")),
            _required_hash(value.get("entry_sha256"), "bundle member entry hash"),
            length,
        )

    def as_mapping(self) -> dict[str, Any]:
        return {
            "bundle_reference": dict(self.bundle_reference),
            "bundle_sha256": self.bundle_sha256,
            "byte_length": self.byte_length,
            "entry_path": self.entry_path,
            "entry_sha256": self.entry_sha256,
        }


@dataclass(frozen=True)
class BundlePeerReference:
    """Carrier-relative member evidence safe to store inside the same bundle."""

    entry_path: str
    entry_sha256: str
    byte_length: int
    media_type: str

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "BundlePeerReference":
        if not isinstance(value, Mapping) or set(value) != {
            "entry_path", "entry_sha256", "byte_length", "media_type",
        }:
            raise BundleError("bundle peer reference has an unsupported shape")
        length = value.get("byte_length")
        if isinstance(length, bool) or not isinstance(length, int) or length < 0:
            raise BundleError("bundle peer reference has an invalid byte length")
        return cls(
            _safe_path(value.get("entry_path")),
            _required_hash(value.get("entry_sha256"), "bundle peer member hash"),
            length,
            _required_text(value.get("media_type"), "bundle peer media type"),
        )

    def as_mapping(self) -> dict[str, Any]:
        return {
            "byte_length": self.byte_length,
            "entry_path": self.entry_path,
            "entry_sha256": self.entry_sha256,
            "media_type": self.media_type,
        }


def _safe_path(value: str) -> str:
    if not isinstance(value, str) or not value or len(value) > MAX_PATH_CODEPOINTS:
        raise BundleError("bundle member path is empty or exceeds its bound")
    if "\\" in value or value.startswith("/") or value.endswith("/"):
        raise BundleError("bundle member path is not a relative file path")
    parts = value.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise BundleError("bundle member path has an unsafe component")
    if value == MANIFEST_PATH:
        raise BundleError("logical entries cannot replace the bundle manifest")
    try:
        encoded_parts = [part.encode("utf-8") for part in parts]
    except UnicodeEncodeError as exc:
        raise BundleError("bundle member path is not valid UTF-8") from exc
    if len(encoded_parts[-1]) > 100 or len("/".join(parts[:-1]).encode("utf-8")) > 155:
        raise BundleError("bundle member path exceeds deterministic ustar limits")
    if PurePosixPath(value).as_posix() != value:
        raise BundleError("bundle member path is not canonical")
    return value


def _required_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise BundleError(f"{label} must be a nonempty string")
    return value


def _required_hash(value: Any, label: str) -> str:
    if not isinstance(value, str) or _LOWER_SHA256.fullmatch(value) is None:
        raise BundleError(f"{label} must be a lowercase SHA-256")
    return value


def _tar_info(name: str, size: int) -> tarfile.TarInfo:
    info = tarfile.TarInfo(name)
    info.type = tarfile.REGTYPE
    info.mode = 0o644
    info.size = size
    info.mtime = 0
    info.uid = info.gid = 0
    info.uname = info.gname = ""
    return info


def build_bundle(
    *, bundle_kind: str, identity: str, instance_id: str,
    package_sha256: str, settings_sha256: str,
    configuration_fingerprint: str, entries: Mapping[str, BundleEntry],
    predecessor: Mapping[str, str] | None = None,
) -> bytes:
    """Build deterministic ustar bytes after validating every logical member."""
    if bundle_kind not in _LIMITS:
        raise BundleError("bundle kind is unsupported")
    if _SAFE_IDENTITY.fullmatch(identity) is None:
        raise BundleError("bundle identity is unsafe")
    _required_text(instance_id, "instance ID")
    _required_hash(package_sha256, "package hash")
    _required_hash(settings_sha256, "settings hash")
    _required_hash(configuration_fingerprint, "configuration fingerprint")
    if not isinstance(entries, Mapping) or not entries or len(entries) > MAX_ENTRY_COUNT:
        raise BundleError("bundle requires a bounded nonempty entry mapping")
    maximum_bundle, maximum_member = _LIMITS[bundle_kind]
    manifest_entries: list[dict[str, Any]] = []
    normalized: dict[str, BundleEntry] = {}
    for raw_path, entry in entries.items():
        path = _safe_path(raw_path)
        if path in normalized:
            raise BundleError("bundle member paths must be unique")
        if not isinstance(entry, BundleEntry) or not isinstance(entry.data, bytes):
            raise BundleError(f"bundle member {path} lacks exact bytes")
        if len(entry.data) > maximum_member:
            raise BundleError(f"bundle member {path} exceeds its byte bound")
        role = _required_text(entry.role, f"bundle member {path} role")
        media_type = _required_text(entry.media_type, f"bundle member {path} media type")
        if entry.schema_id is not None:
            _required_text(entry.schema_id, f"bundle member {path} schema ID")
        normalized[path] = entry
        manifest_entries.append({
            "byte_length": len(entry.data),
            "media_type": media_type,
            "path": path,
            "role": role,
            "schema_id": entry.schema_id,
            "sha256": sha256_bytes(entry.data),
        })
    predecessor_value: dict[str, str] | None = None
    if predecessor is not None:
        if not isinstance(predecessor, Mapping) or set(predecessor) != {"identity", "sha256"}:
            raise BundleError("bundle predecessor has an unsupported shape")
        predecessor_value = {
            "identity": _required_text(predecessor["identity"], "predecessor identity"),
            "sha256": _required_hash(predecessor["sha256"], "predecessor hash"),
        }
    manifest = {
        "bundle_format": BUNDLE_FORMAT,
        "bundle_kind": bundle_kind,
        "configuration_fingerprint": configuration_fingerprint,
        "entries": sorted(manifest_entries, key=lambda item: item["path"]),
        "identity": identity,
        "instance_id": instance_id,
        "package_sha256": package_sha256,
        "predecessor": predecessor_value,
        "schema_version": 1,
        "settings_sha256": settings_sha256,
    }
    manifest_bytes = canonical_json_bytes(manifest)
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w", format=tarfile.USTAR_FORMAT) as archive:
        archive.addfile(_tar_info(MANIFEST_PATH, len(manifest_bytes)), io.BytesIO(manifest_bytes))
        for path in sorted(normalized):
            data = normalized[path].data
            archive.addfile(_tar_info(path, len(data)), io.BytesIO(data))
    result = buffer.getvalue()
    if len(result) > maximum_bundle:
        raise BundleError("bundle exceeds its total byte bound")
    return result


def _parse_manifest(data: bytes, expected_kind: str | None) -> dict[str, Any]:
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BundleError("bundle manifest is not UTF-8 JSON") from exc
    if not isinstance(value, dict) or canonical_json_bytes(value) != data:
        raise BundleError("bundle manifest is not canonical JSON")
    required = {
        "bundle_format", "bundle_kind", "configuration_fingerprint", "entries",
        "identity", "instance_id", "package_sha256", "predecessor",
        "schema_version", "settings_sha256",
    }
    if set(value) != required or value["schema_version"] != 1 or value["bundle_format"] != BUNDLE_FORMAT:
        raise BundleError("bundle manifest has an unsupported shape or version")
    kind = value["bundle_kind"]
    if kind not in _LIMITS or (expected_kind is not None and kind != expected_kind):
        raise BundleError("bundle kind disagrees with the expected kind")
    if _SAFE_IDENTITY.fullmatch(value.get("identity", "")) is None:
        raise BundleError("bundle manifest identity is unsafe")
    _required_text(value["instance_id"], "bundle instance ID")
    _required_hash(value["package_sha256"], "bundle package hash")
    _required_hash(value["settings_sha256"], "bundle settings hash")
    _required_hash(value["configuration_fingerprint"], "bundle configuration fingerprint")
    predecessor = value["predecessor"]
    if predecessor is not None:
        if not isinstance(predecessor, dict) or set(predecessor) != {"identity", "sha256"}:
            raise BundleError("bundle predecessor has an unsupported shape")
        _required_text(predecessor["identity"], "bundle predecessor identity")
        _required_hash(predecessor["sha256"], "bundle predecessor hash")
    if not isinstance(value["entries"], list) or not value["entries"] or len(value["entries"]) > MAX_ENTRY_COUNT:
        raise BundleError("bundle manifest has an invalid entry inventory")
    return value


def read_bundle(data: bytes, *, expected_kind: str | None = None) -> VerifiedBundle:
    """Verify deterministic bundle structure, inventory, bounds, bytes, and hashes."""
    if not isinstance(data, bytes) or len(data) < 1024 or len(data) % 512:
        raise BundleError("bundle bytes are missing or not a complete tar record")
    if expected_kind is not None and expected_kind not in _LIMITS:
        raise BundleError("expected bundle kind is unsupported")
    absolute_limit = max(limit[0] for limit in _LIMITS.values())
    if len(data) > absolute_limit:
        raise BundleError("bundle exceeds the maximum supported byte bound")
    try:
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:", format=tarfile.USTAR_FORMAT) as archive:
            members = archive.getmembers()
            if not members or len(members) > MAX_ENTRY_COUNT + 1:
                raise BundleError("bundle member count is invalid")
            names = [member.name for member in members]
            if names[0] != MANIFEST_PATH or len(names) != len(set(names)):
                raise BundleError("bundle manifest is missing, displaced, or duplicated")
            if names[1:] != sorted(names[1:]):
                raise BundleError("bundle members are not deterministically ordered")
            for member in members:
                if not member.isreg() or member.mode != 0o644 or member.uid != 0 or member.gid != 0 or member.mtime != 0:
                    raise BundleError("bundle member has unsupported type or metadata")
                if member.uname or member.gname:
                    raise BundleError("bundle member has platform-specific owner metadata")
            manifest_file = archive.extractfile(members[0])
            if manifest_file is None:
                raise BundleError("bundle manifest bytes are unavailable")
            manifest = _parse_manifest(manifest_file.read(), expected_kind)
            maximum_bundle, maximum_member = _LIMITS[manifest["bundle_kind"]]
            if len(data) > maximum_bundle:
                raise BundleError("bundle exceeds its kind byte bound")
            declared = manifest["entries"]
            if len(declared) != len(members) - 1:
                raise BundleError("bundle inventory does not cover every member")
            expected_paths = [item.get("path") if isinstance(item, dict) else None for item in declared]
            if expected_paths != sorted(names[1:]):
                raise BundleError("bundle inventory paths disagree with archive members")
            output: dict[str, bytes] = {}
            for descriptor, member in zip(declared, members[1:]):
                if not isinstance(descriptor, dict) or set(descriptor) != {
                    "byte_length", "media_type", "path", "role", "schema_id", "sha256",
                }:
                    raise BundleError("bundle inventory entry has an unsupported shape")
                path = _safe_path(descriptor["path"])
                _required_text(descriptor["role"], f"bundle member {path} role")
                _required_text(descriptor["media_type"], f"bundle member {path} media type")
                if descriptor["schema_id"] is not None:
                    _required_text(descriptor["schema_id"], f"bundle member {path} schema ID")
                length = descriptor["byte_length"]
                if isinstance(length, bool) or not isinstance(length, int) or length < 0 or length > maximum_member:
                    raise BundleError(f"bundle member {path} has an invalid byte length")
                digest = _required_hash(descriptor["sha256"], f"bundle member {path} hash")
                if member.name != path or member.size != length:
                    raise BundleError(f"bundle member {path} length disagrees with its inventory")
                stream = archive.extractfile(member)
                if stream is None:
                    raise BundleError(f"bundle member {path} bytes are unavailable")
                member_data = stream.read(maximum_member + 1)
                if len(member_data) != length or sha256_bytes(member_data) != digest:
                    raise BundleError(f"bundle member {path} bytes disagree with its inventory")
                output[path] = member_data
            last = members[-1]
            logical_end = last.offset_data + ((last.size + 511) // 512) * 512
            if len(data) < logical_end + 1024 or any(data[logical_end:]):
                raise BundleError("bundle has nonzero trailing or incomplete end records")
    except (tarfile.TarError, OSError) as exc:
        raise BundleError(f"bundle tar structure is invalid: {exc}") from exc
    return VerifiedBundle(
        MappingProxyType(manifest), MappingProxyType(output), sha256_bytes(data),
    )


def member_reference(
    bundle_reference: Mapping[str, Any], bundle: VerifiedBundle, entry_path: str,
) -> BundleMemberReference:
    """Create a member reference only from one already-verified bundle."""
    path = _safe_path(entry_path)
    data = bundle.entries.get(path)
    if data is None:
        raise BundleError("bundle does not contain the requested member")
    return BundleMemberReference.from_mapping({
        "bundle_reference": dict(bundle_reference),
        "bundle_sha256": bundle.sha256,
        "byte_length": len(data),
        "entry_path": path,
        "entry_sha256": sha256_bytes(data),
    })


def resolve_member(reference: BundleMemberReference, bundle: VerifiedBundle) -> bytes:
    """Resolve exact member bytes without inventing a member-level provider ID."""
    if bundle.sha256 != reference.bundle_sha256:
        raise BundleError("bundle member reference names different physical bytes")
    data = bundle.entries.get(reference.entry_path)
    if data is None:
        raise BundleError("bundle member is absent")
    if len(data) != reference.byte_length or sha256_bytes(data) != reference.entry_sha256:
        raise BundleError("bundle member bytes disagree with their exact reference")
    return data


def peer_reference(bundle: VerifiedBundle, entry_path: str) -> BundlePeerReference:
    """Create a non-durable peer reference using the verified carrier inventory."""
    path = _safe_path(entry_path)
    descriptors = bundle.manifest.get("entries")
    descriptor = next(
        (
            item for item in descriptors or []
            if isinstance(item, Mapping) and item.get("path") == path
        ),
        None,
    )
    data = bundle.entries.get(path)
    if descriptor is None or data is None:
        raise BundleError("bundle does not contain the requested peer member")
    return BundlePeerReference.from_mapping({
        "byte_length": len(data),
        "entry_path": path,
        "entry_sha256": sha256_bytes(data),
        "media_type": descriptor.get("media_type"),
    })


def resolve_peer(reference: BundlePeerReference, bundle: VerifiedBundle) -> bytes:
    """Resolve a peer only with its verified enclosing bundle as the carrier."""
    data = bundle.entries.get(reference.entry_path)
    if data is None:
        raise BundleError("bundle peer member is absent")
    descriptor = next(
        (
            item for item in bundle.manifest.get("entries", [])
            if isinstance(item, Mapping) and item.get("path") == reference.entry_path
        ),
        None,
    )
    if (
        descriptor is None
        or descriptor.get("media_type") != reference.media_type
        or len(data) != reference.byte_length
        or sha256_bytes(data) != reference.entry_sha256
    ):
        raise BundleError("bundle peer member disagrees with its carrier-relative reference")
    return data
