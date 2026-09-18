#!/usr/bin/env python3
"""Build the static, unconfigured School-OS starter ZIP from one Git commit."""

from __future__ import annotations

import argparse
import os
import posixpath
import re
import subprocess
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit

from privacy_scan import configured_private_needles, scan_text


TOP_DIRECTORY = "School-OS"
REVISION_TOKEN = "{{SOURCE_REVISION}}"
GITHUB_BLOB_ROOT = "https://github.com/jeremieguedj/School-OS/blob"

ROOT_TEMPLATES = {
    "README.md": "distribution/root/README.md",
    "START-HERE.md": "distribution/root/START-HERE.md",
    "AGENTS.md": "distribution/root/AGENTS.md",
    "CLAUDE.md": "distribution/root/CLAUDE.md",
}

SYSTEM_SOURCES = (
    "docs/product-principles.md",
    "operations/README.md",
    "operations/brief-recipes.md",
    "operations/completion-review.md",
    "operations/continuation.md",
    "operations/daily.md",
    "operations/extraction.md",
    "operations/ingestion.md",
    "operations/knowledge.md",
    "operations/query.md",
    "operations/semantic-review.md",
    "operations/setup.md",
    "operations/startup.md",
    "operations/storage.md",
    "operations/task-sync.md",
    "operations/tool-adapter-template.md",
    "operations/tool-adapters.md",
    "contracts/data.md",
    "contracts/identity.md",
    "helpers/README.md",
    "helpers/bootstrap_contract.py",
    "helpers/source_metadata.py",
    "adapters/README.md",
    "adapters/elevenlabs.md",
    "adapters/gmail.md",
    "adapters/google-drive.md",
    "adapters/google-sheets.md",
    "adapters/todoist.md",
)

DIRECTORY_MEMBERS = (
    "School-OS/",
    "School-OS/system/",
    "School-OS/system/docs/",
    "School-OS/system/operations/",
    "School-OS/system/contracts/",
    "School-OS/system/helpers/",
    "School-OS/system/adapters/",
    "School-OS/instance/",
    "School-OS/extensions/",
)

MARKDOWN_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+[^)]*)?\)")
REVISION_RE = re.compile(r"[0-9a-fA-F]{40}")


class BundleError(RuntimeError):
    """A static bundle input or output failed validation."""


def run_git(repo: Path, *arguments: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(repo), *arguments],
        capture_output=True,
        check=False,
    )
    if result.returncode:
        detail = result.stderr.decode("utf-8", "replace").strip()
        raise BundleError(detail or f"git {' '.join(arguments)} failed")
    return result.stdout


def resolve_revision(repo: Path, supplied: str) -> str:
    if not REVISION_RE.fullmatch(supplied):
        raise BundleError("--revision must be one exact 40-character commit SHA")
    resolved = run_git(repo, "rev-parse", "--verify", f"{supplied}^{{commit}}")
    revision = resolved.decode("ascii", "strict").strip().lower()
    if revision != supplied.lower():
        raise BundleError("--revision did not resolve to the exact supplied commit")
    return revision


def read_commit_file(repo: Path, revision: str, source_path: str) -> bytes:
    listing = run_git(repo, "ls-tree", revision, "--", source_path)
    line = listing.decode("utf-8", "strict").rstrip("\n")
    if not line:
        raise BundleError(f"required source is absent at {revision}: {source_path}")
    metadata, listed_path = line.split("\t", 1)
    mode, object_type, _object_id = metadata.split(" ", 2)
    if listed_path != source_path or object_type != "blob" or mode not in {"100644", "100755"}:
        raise BundleError(f"required source is not a regular tracked file: {source_path}")
    return run_git(repo, "show", f"{revision}:{source_path}")


def pinned_development_links(member: str, text: str, revision: str) -> str:
    replacements: dict[str, str] = {}
    if member == "School-OS/system/docs/product-principles.md":
        replacements[
            "plans/restart/PLAN.md#user-approved-mvp-revisions-2026-09-15"
        ] = (
            f"{GITHUB_BLOB_ROOT}/{revision}/docs/plans/restart/PLAN.md"
            "#user-approved-mvp-revisions-2026-09-15"
        )
    if member == "School-OS/system/helpers/README.md":
        replacements["prepared_checks/check_source_metadata.py"] = (
            f"{GITHUB_BLOB_ROOT}/{revision}/helpers/prepared_checks/"
            "check_source_metadata.py"
        )
        replacements["prepared_checks/check_bootstrap_contract.py"] = (
            f"{GITHUB_BLOB_ROOT}/{revision}/helpers/prepared_checks/"
            "check_bootstrap_contract.py"
        )
        replacements["prepared_checks/check_trial_evaluation.py"] = (
            f"{GITHUB_BLOB_ROOT}/{revision}/helpers/prepared_checks/"
            "check_trial_evaluation.py"
        )
        replacements["../examples/evaluation/README.md"] = (
            f"{GITHUB_BLOB_ROOT}/{revision}/examples/evaluation/README.md"
        )
        replacements["(trial_evaluation.py)"] = (
            f"({GITHUB_BLOB_ROOT}/{revision}/helpers/trial_evaluation.py)"
        )
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def prepare_payloads(repo: Path, revision: str) -> dict[str, bytes]:
    payloads: dict[str, bytes] = {}
    for target_name, source_path in ROOT_TEMPLATES.items():
        raw = read_commit_file(repo, revision, source_path)
        text = raw.decode("utf-8", "strict")
        if target_name == "README.md":
            if text.count(REVISION_TOKEN) != 1:
                raise BundleError("consumer README must contain one source-revision token")
            text = text.replace(REVISION_TOKEN, revision)
        elif REVISION_TOKEN in text:
            raise BundleError(f"unexpected source-revision token in {source_path}")
        payloads[f"{TOP_DIRECTORY}/{target_name}"] = text.encode("utf-8")

    for source_path in SYSTEM_SOURCES:
        member = f"{TOP_DIRECTORY}/system/{source_path}"
        raw = read_commit_file(repo, revision, source_path)
        text = raw.decode("utf-8", "strict")
        text = pinned_development_links(member, text, revision)
        payloads[member] = text.encode("utf-8")
    return payloads


def validate_members(payloads: dict[str, bytes], revision: str) -> None:
    expected = {
        *(f"{TOP_DIRECTORY}/{name}" for name in ROOT_TEMPLATES),
        *(f"{TOP_DIRECTORY}/system/{path}" for path in SYSTEM_SOURCES),
    }
    actual = set(payloads)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise BundleError(f"bundle member mismatch; missing={missing!r}, extra={extra!r}")
    if payloads[f"{TOP_DIRECTORY}/CLAUDE.md"] != b"@AGENTS.md\n":
        raise BundleError("consumer CLAUDE.md must be exactly '@AGENTS.md\\n'")
    if revision.encode("ascii") not in payloads[f"{TOP_DIRECTORY}/README.md"]:
        raise BundleError("consumer README does not identify the source revision")
    for member in actual:
        path = PurePosixPath(member)
        if path.is_absolute() or ".." in path.parts or path.parts[0] != TOP_DIRECTORY:
            raise BundleError(f"unsafe bundle member path: {member}")
        if REVISION_TOKEN.encode("ascii") in payloads[member]:
            raise BundleError(f"unresolved source-revision token in {member}")


def validate_privacy(payloads: dict[str, bytes]) -> None:
    needles = configured_private_needles()
    violations: list[str] = []
    for member, raw in sorted(payloads.items()):
        text = raw.decode("utf-8", "strict")
        violations.extend(scan_text(member, text, needles))
    if violations:
        raise BundleError("bundle privacy scan failed:\n" + "\n".join(violations))


def validate_links(payloads: dict[str, bytes]) -> None:
    file_members = set(payloads)
    for member, raw in sorted(payloads.items()):
        if not member.endswith(".md"):
            continue
        text = raw.decode("utf-8", "strict")
        for target in MARKDOWN_LINK_RE.findall(text):
            parsed = urlsplit(target)
            if parsed.scheme in {"http", "https", "mailto"}:
                continue
            if parsed.scheme or parsed.netloc or target.startswith("/"):
                raise BundleError(f"unsupported link target in {member}: {target}")
            if not parsed.path:
                continue
            resolved = posixpath.normpath(
                posixpath.join(posixpath.dirname(member), parsed.path)
            )
            if not resolved.startswith(f"{TOP_DIRECTORY}/") or resolved not in file_members:
                raise BundleError(f"unresolved relative link in {member}: {target}")


def zip_info(name: str, *, directory: bool) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.create_system = 3
    info.compress_type = zipfile.ZIP_STORED if directory else zipfile.ZIP_DEFLATED
    if directory:
        info.external_attr = (0o40755 << 16) | 0x10
    else:
        info.external_attr = 0o100644 << 16
    return info


def verify_archive(path: Path, payloads: dict[str, bytes]) -> None:
    expected_names = [*DIRECTORY_MEMBERS, *sorted(payloads)]
    with zipfile.ZipFile(path, "r") as archive:
        actual_names = [info.filename for info in archive.infolist()]
        if actual_names != expected_names:
            raise BundleError("written ZIP does not contain the exact allowed members")
        bad_member = archive.testzip()
        if bad_member is not None:
            raise BundleError(f"written ZIP failed its CRC check: {bad_member}")
        for directory in DIRECTORY_MEMBERS:
            if not archive.getinfo(directory).is_dir() or archive.read(directory) != b"":
                raise BundleError(f"written ZIP directory entry is invalid: {directory}")
        for member, intended in payloads.items():
            if archive.read(member) != intended:
                raise BundleError(f"written ZIP content differs from intended bytes: {member}")


def write_bundle(output: Path, payloads: dict[str, bytes]) -> None:
    if output.suffix.lower() != ".zip":
        raise BundleError("--output must name a .zip file")
    if output.exists():
        raise BundleError(f"output already exists: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            prefix=f".{output.name}.", suffix=".tmp", dir=output.parent, delete=False
        ) as temporary:
            temporary_path = Path(temporary.name)
        with zipfile.ZipFile(
            temporary_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
        ) as archive:
            for directory in DIRECTORY_MEMBERS:
                archive.writestr(zip_info(directory, directory=True), b"")
            for member in sorted(payloads):
                archive.writestr(zip_info(member, directory=False), payloads[member])
        verify_archive(temporary_path, payloads)
        os.replace(temporary_path, output)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build one fresh, unconfigured School-OS starter ZIP."
    )
    parser.add_argument("--revision", required=True, help="exact committed 40-character SHA")
    parser.add_argument("--output", required=True, type=Path, help="new ZIP output path")
    return parser.parse_args()


def main() -> int:
    arguments = parse_args()
    repo = Path(__file__).resolve().parents[1]
    revision = resolve_revision(repo, arguments.revision)
    payloads = prepare_payloads(repo, revision)
    validate_members(payloads, revision)
    validate_privacy(payloads)
    validate_links(payloads)
    write_bundle(arguments.output.resolve(), payloads)
    print(f"created {arguments.output} from {revision}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
