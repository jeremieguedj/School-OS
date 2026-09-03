#!/usr/bin/env python3
"""Run the complete dependency-free School-OS repository validation suite."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from build_release import BuildError, build_release, verify_release_archive
from privacy_scan import scan_tracked_files
from validate_instance import ContractError, load_manifest, validate


ROOT = Path(__file__).resolve().parents[1]


def validate_schema_documents() -> list[str]:
    errors: list[str] = []
    for path in sorted((ROOT / "schemas").glob("*.schema.json")):
        try:
            schema = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{path.relative_to(ROOT)}: invalid JSON: {exc}")
            continue
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            errors.append(f"{path.relative_to(ROOT)}: unsupported or missing $schema")
        if schema.get("type") != "object":
            errors.append(f"{path.relative_to(ROOT)}: root type must be object")
    return errors


def validate_manifests() -> list[str]:
    errors: list[str] = []
    pairs = (
        (ROOT / "templates" / "instance.yaml", ROOT / "schemas" / "instance.schema.json"),
        (
            ROOT / "templates" / "state" / "capability-profile.json",
            ROOT / "schemas" / "capability-profile.schema.json",
        ),
        (ROOT / "release.yaml", ROOT / "schemas" / "release.schema.json"),
    )
    for manifest_path, schema_path in pairs:
        try:
            manifest = load_manifest(manifest_path)
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            errors.extend(
                f"{manifest_path.relative_to(ROOT)} {error}" for error in validate(manifest, schema)
            )
        except (OSError, json.JSONDecodeError, ContractError) as exc:
            errors.append(f"{manifest_path.relative_to(ROOT)}: {exc}")
    return errors


def validate_release_package() -> list[str]:
    """Smoke-build the exact committed ref; release status is intentionally irrelevant."""
    try:
        release_text = subprocess.run(
            ["git", "-C", str(ROOT), "show", "HEAD:release.yaml"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        match = re.search(r"(?m)^system_version:[ \t]*([^#\s]+)", release_text)
        if not match:
            return ["HEAD:release.yaml does not declare system_version"]
        with tempfile.TemporaryDirectory() as temporary:
            archive, sums, _commit = build_release(ROOT, "HEAD", match.group(1), Path(temporary))
            return verify_release_archive(archive, sums, match.group(1))
    except (BuildError, OSError, subprocess.CalledProcessError) as exc:
        return [f"release package smoke check failed: {exc}"]


def main() -> int:
    errors = (
        validate_schema_documents()
        + validate_manifests()
        + scan_tracked_files(ROOT)
        + validate_release_package()
    )
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"],
        cwd=ROOT,
        check=False,
    )
    if result.returncode:
        return result.returncode
    print("validated: JSON schemas, template manifests, and executable tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
