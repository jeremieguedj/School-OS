#!/usr/bin/env python3
"""Build a reproducible School-OS release archive from an exact Git ref."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import re
import subprocess
import sys
import tarfile
from pathlib import Path, PurePosixPath


VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?$")
ARTIFACT_RE = re.compile(r"^school-os-.+\.tar\.gz$")
INVENTORY_NAME = "RELEASE-INVENTORY.sha256"
SUMS_NAME = "SHA256SUMS"


class BuildError(RuntimeError):
    """Raised when a ref cannot be packaged safely and deterministically."""


def _git(repo: Path, *args: str, input_data: bytes | None = None) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        input=input_data,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        detail = result.stderr.decode("utf-8", "replace").strip()
        raise BuildError(detail or f"git {' '.join(args)} failed")
    return result.stdout


def _safe_payload_path(raw: str) -> PurePosixPath:
    path = PurePosixPath(raw)
    if not raw or raw.startswith("/") or "\\" in raw or any(part in {"", ".", ".."} for part in path.parts):
        raise BuildError(f"unsafe Git tree path: {raw!r}")
    if ".git" in path.parts:
        raise BuildError(f"Git metadata path is not packageable: {raw!r}")
    return path


def _is_output_artifact(path: PurePosixPath) -> bool:
    return path.name in {INVENTORY_NAME, SUMS_NAME} or bool(ARTIFACT_RE.fullmatch(path.name))


def _release_version(payload: dict[str, tuple[bytes, int]]) -> str:
    try:
        text = payload["release.yaml"][0].decode("utf-8")
    except (KeyError, UnicodeDecodeError) as exc:
        raise BuildError("the selected ref must contain a UTF-8 release.yaml") from exc
    match = re.search(r"(?m)^system_version:[ \t]*([^#\s]+)[ \t]*(?:#.*)?$", text)
    if not match:
        raise BuildError("release.yaml does not declare system_version")
    return match.group(1)


def read_ref_payload(repo: Path, ref: str) -> tuple[str, dict[str, tuple[bytes, int]]]:
    """Return commit ID and regular tracked files from ``ref``."""
    commit = _git(repo, "rev-parse", "--verify", f"{ref}^{{commit}}").decode().strip()
    tree = _git(repo, "ls-tree", "-r", "-z", commit)
    payload: dict[str, tuple[bytes, int]] = {}
    for record in tree.split(b"\0"):
        if not record:
            continue
        metadata, separator, raw_path = record.partition(b"\t")
        if not separator:
            raise BuildError("unexpected git ls-tree output")
        try:
            mode, object_type, object_id = metadata.decode("ascii").split()
            path_text = raw_path.decode("utf-8")
        except (UnicodeDecodeError, ValueError) as exc:
            raise BuildError("release paths and tree metadata must be UTF-8/ASCII") from exc
        path = _safe_payload_path(path_text)
        if _is_output_artifact(path):
            continue
        if object_type != "blob" or mode not in {"100644", "100755"}:
            raise BuildError(f"only regular files are allowed in releases: {path_text!r} ({mode} {object_type})")
        payload[path.as_posix()] = (_git(repo, "cat-file", "blob", object_id), 0o755 if mode == "100755" else 0o644)
    return commit, payload


def _inventory(payload: dict[str, tuple[bytes, int]]) -> bytes:
    return "".join(
        f"{hashlib.sha256(data).hexdigest()}  {path}\n"
        for path, (data, _mode) in sorted(payload.items())
    ).encode("utf-8")


def _tar_info(name: str, *, mode: int, size: int = 0, directory: bool = False) -> tarfile.TarInfo:
    info = tarfile.TarInfo(name + ("/" if directory and not name.endswith("/") else ""))
    info.type = tarfile.DIRTYPE if directory else tarfile.REGTYPE
    info.mode = mode
    info.size = 0 if directory else size
    info.mtime = 0
    info.uid = info.gid = 0
    info.uname = info.gname = ""
    return info


def build_release(repo: Path, ref: str, version: str, output_dir: Path) -> tuple[Path, Path, str]:
    """Build an archive and SHA256SUMS, returning their paths and commit ID."""
    repo = repo.resolve()
    if not VERSION_RE.fullmatch(version):
        raise BuildError(f"invalid release version: {version!r}")
    commit, payload = read_ref_payload(repo, ref)
    declared = _release_version(payload)
    if declared != version:
        raise BuildError(f"requested version {version!r} does not match release.yaml version {declared!r}")
    payload[INVENTORY_NAME] = (_inventory(payload), 0o644)

    output_dir.mkdir(parents=True, exist_ok=True)
    archive = output_dir / f"school-os-{version}.tar.gz"
    root = f"School-OS-{version}"
    with archive.open("wb") as raw_file:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw_file, mtime=0, compresslevel=9) as gzip_file:
            with tarfile.open(fileobj=gzip_file, mode="w", format=tarfile.GNU_FORMAT) as tar:
                directories = {root}
                for path in payload:
                    parent = PurePosixPath(root, path).parent
                    while parent.as_posix() != ".":
                        directories.add(parent.as_posix())
                        if parent.as_posix() == root:
                            break
                        parent = parent.parent
                for directory in sorted(directories):
                    tar.addfile(_tar_info(directory, mode=0o755, directory=True))
                for path, (data, mode) in sorted(payload.items()):
                    name = PurePosixPath(root, path).as_posix()
                    tar.addfile(_tar_info(name, mode=mode, size=len(data)), io.BytesIO(data))

    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    sums = output_dir / SUMS_NAME
    sums.write_text(f"{digest}  {archive.name}\n", encoding="utf-8")
    return archive, sums, commit


def verify_release_archive(archive: Path, sums: Path, version: str) -> list[str]:
    """Verify archive path safety, normalized members, inventory, and checksum."""
    errors: list[str] = []
    expected_root = f"School-OS-{version}"
    actual_digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    expected_sum = f"{actual_digest}  {archive.name}\n"
    if sums.read_text(encoding="utf-8") != expected_sum:
        errors.append("SHA256SUMS does not match the archive")
    with tarfile.open(archive, "r:gz") as tar:
        members = tar.getmembers()
        regular: dict[str, bytes] = {}
        for member in members:
            path = PurePosixPath(member.name)
            if path.is_absolute() or ".." in path.parts or not path.parts or path.parts[0] != expected_root:
                errors.append(f"unsafe or unexpected archive path: {member.name!r}")
            if member.mtime != 0 or member.uid != 0 or member.gid != 0 or member.uname or member.gname:
                errors.append(f"non-normalized metadata: {member.name!r}")
            if member.isfile():
                extracted = tar.extractfile(member)
                if extracted is None:
                    errors.append(f"unreadable regular file: {member.name!r}")
                else:
                    regular[PurePosixPath(*path.parts[1:]).as_posix()] = extracted.read()
            elif not member.isdir():
                errors.append(f"unsupported archive member type: {member.name!r}")
    inventory = regular.pop(INVENTORY_NAME, None)
    if inventory is None:
        errors.append(f"missing {INVENTORY_NAME}")
        return errors
    expected_inventory = _inventory({path: (data, 0o644) for path, data in regular.items()})
    if inventory != expected_inventory:
        errors.append(f"{INVENTORY_NAME} is incomplete or has invalid checksums")
    if any(_is_output_artifact(PurePosixPath(path)) for path in regular):
        errors.append("archive contains an output artifact")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--ref", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        archive, sums, commit = build_release(args.repo, args.ref, args.version, args.output_dir)
        errors = verify_release_archive(archive, sums, args.version)
    except (BuildError, OSError, tarfile.TarError) as exc:
        print(f"build failed: {exc}", file=sys.stderr)
        return 1
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"built: {archive} ({commit})")
    print(f"checksums: {sums}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
