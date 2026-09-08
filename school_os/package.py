"""Provider-independent verification for School-OS release payloads.

This module deliberately knows nothing about Git.  Development commands may
obtain a payload from a commit, but an installed package is verified only from
the archive, checksum, inventory, and extracted bytes it was given.
"""

from __future__ import annotations

import hashlib
import re
import tarfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from .contracts import ContractError, load_mapping, sha256_bytes


VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?$")
ARTIFACT_RE = re.compile(r"^school-os-.+\.tar\.gz$")
INVENTORY_NAME = "RELEASE-INVENTORY.sha256"
SUMS_NAME = "SHA256SUMS"


class PackageError(ValueError):
    """Raised when package bytes or identity evidence are invalid."""


@dataclass(frozen=True)
class PackageVerification:
    """Verified, transportable package identity evidence."""

    version: str
    archive_sha256: str | None
    inventory_sha256: str
    payload_hashes: tuple[tuple[str, str], ...]


def safe_payload_path(raw: str) -> PurePosixPath:
    """Validate a portable, relative package payload path."""
    path = PurePosixPath(raw)
    if not raw or raw.startswith("/") or "\\" in raw or any(part in {"", ".", ".."} for part in path.parts):
        raise PackageError(f"unsafe package path: {raw!r}")
    if ".git" in path.parts:
        raise PackageError(f"Git metadata is not packageable: {raw!r}")
    return path


def is_output_artifact(path: PurePosixPath) -> bool:
    return path.name in {INVENTORY_NAME, SUMS_NAME} or bool(ARTIFACT_RE.fullmatch(path.name))


def release_version(payload: dict[str, tuple[bytes, int]] | Path) -> str:
    """Read and validate the declared release version from payload bytes or a manifest."""
    try:
        if isinstance(payload, Path):
            value = load_mapping(payload)
            declared = value.get("system_version")
        else:
            declared = load_mapping_bytes(payload["release.yaml"][0]).get("system_version")
    except (KeyError, UnicodeDecodeError, OSError, ContractError) as exc:
        raise PackageError("release.yaml must be a UTF-8 mapping") from exc
    if not isinstance(declared, str) or not VERSION_RE.fullmatch(declared):
        raise PackageError("release.yaml does not declare a valid system_version")
    return declared


def load_mapping_bytes(data: bytes) -> dict[str, object]:
    """Load the small release manifest YAML subset from already-read bytes."""
    try:
        from .contracts import load_mapping_yaml

        return load_mapping_yaml(data.decode("utf-8"))
    except (UnicodeDecodeError, ContractError) as exc:
        raise PackageError("release manifest is not valid UTF-8 YAML") from exc


def inventory_bytes(payload: dict[str, tuple[bytes, int]] | dict[str, bytes]) -> bytes:
    """Return the deterministic inventory for payload files excluding the inventory itself."""
    items = ((path, value[0] if isinstance(value, tuple) else value) for path, value in payload.items())
    return "".join(f"{sha256_bytes(data)}  {path}\n" for path, data in sorted(items)).encode("utf-8")


def parse_inventory(data: bytes) -> dict[str, str]:
    """Parse an inventory strictly enough to make omissions and duplicates visible."""
    try:
        lines = data.decode("utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise PackageError(f"{INVENTORY_NAME} is not UTF-8") from exc
    entries: dict[str, str] = {}
    for line in lines:
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if not match:
            raise PackageError(f"invalid {INVENTORY_NAME} entry")
        digest, raw_path = match.groups()
        path = safe_payload_path(raw_path).as_posix()
        if path == INVENTORY_NAME or is_output_artifact(PurePosixPath(path)):
            raise PackageError(f"invalid {INVENTORY_NAME} path: {path!r}")
        if path in entries:
            raise PackageError(f"duplicate {INVENTORY_NAME} path: {path!r}")
        entries[path] = digest
    if not entries:
        raise PackageError(f"{INVENTORY_NAME} must contain at least one payload file")
    return entries


def _verification(version: str, archive_sha256: str | None, inventory: bytes) -> PackageVerification:
    entries = parse_inventory(inventory)
    return PackageVerification(
        version=version,
        archive_sha256=archive_sha256,
        inventory_sha256=sha256_bytes(inventory),
        payload_hashes=tuple(sorted(entries.items())),
    )


def verify_release_archive(archive: Path, sums: Path, version: str) -> list[str]:
    """Verify archive structure, release identity, inventory, and its checksum."""
    errors: list[str] = []
    if not VERSION_RE.fullmatch(version):
        return [f"invalid release version: {version!r}"]
    expected_root = f"School-OS-{version}"
    try:
        digest = sha256_bytes(archive.read_bytes())
        if sums.read_text(encoding="utf-8") != f"{digest}  {archive.name}\n":
            errors.append("SHA256SUMS does not match the archive")
        with tarfile.open(archive, "r:gz") as tar:
            regular: dict[str, bytes] = {}
            for member in tar.getmembers():
                path = PurePosixPath(member.name)
                if path.is_absolute() or ".." in path.parts or not path.parts or path.parts[0] != expected_root:
                    errors.append(f"unsafe or unexpected archive path: {member.name!r}")
                    continue
                if member.mtime != 0 or member.uid != 0 or member.gid != 0 or member.uname or member.gname:
                    errors.append(f"non-normalized metadata: {member.name!r}")
                if member.isfile():
                    extracted = tar.extractfile(member)
                    if extracted is None:
                        errors.append(f"unreadable regular file: {member.name!r}")
                    else:
                        relative = PurePosixPath(*path.parts[1:]).as_posix()
                        if relative in regular:
                            errors.append(f"duplicate archive path: {relative!r}")
                        regular[relative] = extracted.read()
                elif not member.isdir():
                    errors.append(f"unsupported archive member type: {member.name!r}")
        inventory = regular.pop(INVENTORY_NAME, None)
        if inventory is None:
            return errors + [f"missing {INVENTORY_NAME}"]
        if any(is_output_artifact(PurePosixPath(path)) for path in regular):
            errors.append("archive contains an output artifact")
        if inventory != inventory_bytes(regular):
            errors.append(f"{INVENTORY_NAME} is incomplete or has invalid checksums")
        try:
            if release_version({path: (data, 0o644) for path, data in regular.items()}) != version:
                errors.append("release.yaml version does not match archive version")
            _verification(version, digest, inventory)
        except PackageError as exc:
            errors.append(str(exc))
    except (OSError, tarfile.TarError) as exc:
        errors.append(f"archive verification failed: {exc}")
    return errors


def verify_extracted_tree(root: Path, version: str | None = None) -> PackageVerification:
    """Verify extracted package bytes without Git, network, or repository context."""
    try:
        root = root.resolve(strict=True)
    except OSError as exc:
        raise PackageError(f"cannot resolve extracted package root: {exc}") from exc
    if not root.is_dir():
        raise PackageError("extracted package root must be a directory")
    expected_version = version or release_version(root / "release.yaml")
    if root.name != f"School-OS-{expected_version}":
        raise PackageError("extracted package root does not match release version")
    files: dict[str, bytes] = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if path.is_symlink() or not path.is_file():
            if path.is_symlink():
                raise PackageError(f"extracted package must not contain symlinks: {relative}")
            continue
        safe = safe_payload_path(relative.as_posix()).as_posix()
        if safe == INVENTORY_NAME:
            continue
        if is_output_artifact(PurePosixPath(safe)):
            raise PackageError(f"extracted package contains an output artifact: {safe!r}")
        files[safe] = path.read_bytes()
    inventory_path = root / INVENTORY_NAME
    try:
        inventory = inventory_path.read_bytes()
    except OSError as exc:
        raise PackageError(f"missing {INVENTORY_NAME}") from exc
    if inventory != inventory_bytes(files):
        raise PackageError(f"{INVENTORY_NAME} is incomplete or has invalid checksums")
    if release_version({path: (data, 0o644) for path, data in files.items()}) != expected_version:
        raise PackageError("release.yaml version does not match extracted package version")
    return _verification(expected_version, None, inventory)
