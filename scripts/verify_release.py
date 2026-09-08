#!/usr/bin/env python3
"""Verify a GitHub draft or published release against exact local source bytes.

This command is deliberately read-only with respect to GitHub.  It builds the
two release assets from one local commit, reads a release/tag through ``gh``,
downloads the declared assets, and requires byte-for-byte agreement.  Release
creation, publishing, tag creation, and asset upload remain separate, explicit
operator actions.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from build_release import BuildError, build_release, verify_release_archive
from school_os.contracts import ContractError, load_mapping_yaml


class ReleaseVerificationError(RuntimeError):
    """The remote release is incomplete, ambiguous, or differs from the candidate."""


Runner = Callable[[list[str]], bytes]


def _run(command: list[str]) -> bytes:
    result = subprocess.run(command, capture_output=True, check=False)
    if result.returncode:
        detail = result.stderr.decode("utf-8", "replace").strip()
        raise ReleaseVerificationError(detail or f"command failed: {' '.join(command)}")
    return result.stdout


def _json(command: list[str], runner: Runner) -> dict[str, Any]:
    try:
        value = json.loads(runner(command).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ReleaseVerificationError("GitHub returned invalid JSON") from error
    if not isinstance(value, dict):
        raise ReleaseVerificationError("GitHub returned a non-object response")
    return value


def _manifest_status(archive: Path, version: str) -> str:
    try:
        with tarfile.open(archive, "r:gz") as package:
            member = package.extractfile(f"School-OS-{version}/release.yaml")
            if member is None:
                raise ReleaseVerificationError("candidate archive has no release.yaml")
            manifest = load_mapping_yaml(member.read().decode("utf-8"))
    except (OSError, tarfile.TarError, UnicodeDecodeError, ContractError) as error:
        raise ReleaseVerificationError(f"cannot read candidate release manifest: {error}") from error
    status = manifest.get("status")
    if not isinstance(status, str):
        raise ReleaseVerificationError("candidate release manifest has no status")
    return status


def candidate_assets(
    repo: Path, ref: str, commit: str, version: str, manifest_status: str,
) -> dict[str, bytes]:
    """Build and independently verify assets from exactly ``commit``."""
    resolved = _run(["git", "-C", str(repo), "rev-parse", "--verify", f"{ref}^{{commit}}"])
    if resolved.decode("ascii", "strict").strip() != commit:
        raise ReleaseVerificationError("candidate ref does not resolve to the declared commit")
    with tempfile.TemporaryDirectory() as temporary:
        output = Path(temporary)
        try:
            archive, sums, built_commit = build_release(repo, ref, version, output)
        except (BuildError, OSError) as error:
            raise ReleaseVerificationError(f"candidate build failed: {error}") from error
        if built_commit != commit:
            raise ReleaseVerificationError("release builder returned a different candidate commit")
        errors = verify_release_archive(archive, sums, version)
        if errors:
            raise ReleaseVerificationError("candidate package verification failed: " + "; ".join(errors))
        if _manifest_status(archive, version) != manifest_status:
            raise ReleaseVerificationError(
                f"candidate release manifest status is not {manifest_status!r}"
            )
        return {archive.name: archive.read_bytes(), sums.name: sums.read_bytes()}


def _asset_names(release: dict[str, Any], expected: set[str]) -> None:
    assets = release.get("assets")
    if not isinstance(assets, list):
        raise ReleaseVerificationError("release has no asset inventory")
    names: list[str] = []
    for asset in assets:
        if not isinstance(asset, dict) or not isinstance(asset.get("name"), str):
            raise ReleaseVerificationError("release asset inventory has an invalid entry")
        names.append(asset["name"])
    if len(names) != len(set(names)):
        raise ReleaseVerificationError("release asset inventory has duplicate names")
    actual = set(names)
    if actual != expected:
        missing = sorted(expected - actual)
        unexpected = sorted(actual - expected)
        detail = []
        if missing:
            detail.append("missing " + ", ".join(missing))
        if unexpected:
            detail.append("unexpected " + ", ".join(unexpected))
        raise ReleaseVerificationError("release assets do not match candidate: " + "; ".join(detail))


def _release_metadata(release: dict[str, Any], *, tag: str, commit: str, draft: bool) -> None:
    if release.get("tagName") != tag:
        raise ReleaseVerificationError("release tag does not match candidate version")
    if release.get("targetCommitish") != commit:
        raise ReleaseVerificationError("release target commit does not match candidate commit")
    if release.get("isDraft") is not draft:
        state = "draft" if draft else "published"
        raise ReleaseVerificationError(f"release is not the expected {state} state")
    if not draft and release.get("isImmutable") is not True:
        raise ReleaseVerificationError("published release is not immutable")


def _verified_tag(repo: str, tag: str, commit: str, runner: Runner) -> None:
    ref = _json(["gh", "api", f"repos/{repo}/git/ref/tags/{tag}"], runner)
    object_ref = ref.get("object")
    if not isinstance(object_ref, dict) or object_ref.get("type") != "tag" or not isinstance(object_ref.get("sha"), str):
        raise ReleaseVerificationError("release tag is not an annotated tag")
    annotated = _json(["gh", "api", f"repos/{repo}/git/tags/{object_ref['sha']}"], runner)
    target = annotated.get("object")
    if not isinstance(target, dict) or target.get("type") != "commit" or target.get("sha") != commit:
        raise ReleaseVerificationError("annotated tag does not resolve to the candidate commit")


def verify_remote_release(
    *, repo: str, version: str, commit: str, expected_assets: dict[str, bytes], draft: bool,
    runner: Runner = _run,
) -> None:
    """Require metadata, annotated tag, asset inventory, and downloaded bytes to agree."""
    tag = f"v{version}"
    release = _json(
        [
            "gh", "release", "view", tag, "--repo", repo,
            "--json", "tagName,targetCommitish,isDraft,isPrerelease,isImmutable,assets",
        ],
        runner,
    )
    _release_metadata(release, tag=tag, commit=commit, draft=draft)
    _asset_names(release, set(expected_assets))
    _verified_tag(repo, tag, commit, runner)
    with tempfile.TemporaryDirectory() as temporary:
        destination = Path(temporary)
        runner(["gh", "release", "download", tag, "--repo", repo, "--dir", str(destination)])
        downloaded = {path.name: path.read_bytes() for path in destination.iterdir() if path.is_file()}
    if set(downloaded) != set(expected_assets):
        raise ReleaseVerificationError("downloaded release assets do not match the declared inventory")
    for name, expected in expected_assets.items():
        if downloaded[name] != expected:
            raise ReleaseVerificationError(f"downloaded asset bytes differ from candidate: {name}")


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)
    for name, draft, default_status in (("verify-draft", True, "unreleased"), ("verify-published", False, "released")):
        command = subcommands.add_parser(name)
        command.set_defaults(draft=draft)
        command.add_argument("--repo", required=True, help="GitHub owner/repository")
        command.add_argument("--source-repo", type=Path, default=Path.cwd())
        command.add_argument("--ref", required=True, help="local immutable candidate ref")
        command.add_argument("--commit", required=True, help="full candidate commit SHA")
        command.add_argument("--version", required=True)
        command.add_argument("--manifest-status", default=default_status, choices=("unreleased", "released"))
    return parser.parse_args()


def main() -> int:
    args = _arguments()
    try:
        if args.command == "verify-published" and args.manifest_status != "released":
            raise ReleaseVerificationError("a published release candidate must declare status: released")
        expected = candidate_assets(args.source_repo, args.ref, args.commit, args.version, args.manifest_status)
        verify_remote_release(
            repo=args.repo, version=args.version, commit=args.commit, expected_assets=expected, draft=args.draft,
        )
    except ReleaseVerificationError as error:
        print(f"release verification failed: {error}", file=sys.stderr)
        return 1
    print(f"verified {'draft' if args.draft else 'published'} release v{args.version} at {args.commit}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
