#!/usr/bin/env python3
"""Build a reproducible School-OS release archive from an exact Git ref."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import subprocess
import sys
import tarfile
from pathlib import Path, PurePosixPath

# An extracted release is immutable; this CLI must not add __pycache__ files.
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from school_os.package import (
    ARTIFACT_RE,
    INVENTORY_NAME,
    SUMS_NAME,
    VERSION_RE,
    PackageError,
    inventory_bytes,
    is_output_artifact,
    release_version,
    safe_payload_path,
    verify_release_archive as verify_package_archive,
)

class BuildError(PackageError):
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
    try:
        return safe_payload_path(raw)
    except PackageError as exc:
        raise BuildError(str(exc).replace("package", "Git tree")) from exc


def _is_output_artifact(path: PurePosixPath) -> bool:
    return is_output_artifact(path)


def _release_version(payload: dict[str, tuple[bytes, int]]) -> str:
    try:
        return release_version(payload)
    except PackageError as exc:
        raise BuildError(str(exc)) from exc


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
    return inventory_bytes(payload)


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
    """Compatibility wrapper around the shared installed-package verifier."""
    return verify_package_archive(archive, sums, version)


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
