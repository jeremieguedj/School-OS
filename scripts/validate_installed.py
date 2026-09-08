#!/usr/bin/env python3
"""Validate an extracted School-OS package without Git or repository tests."""

from __future__ import annotations

import argparse
import json
import sys
import tarfile
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from school_os.contracts import ContractError, load_mapping, validate
from school_os.package import PackageError, verify_extracted_tree, verify_release_archive
from school_os.references import ReferenceError, load_operation_registry


def validate_installed(root: Path, *, candidate_test: bool) -> list[str]:
    """Validate managed package bytes and installed recipes using no Git surface."""
    errors: list[str] = []
    try:
        verification = verify_extracted_tree(root)
        manifest = load_mapping(root / "release.yaml")
        release_schema = json.loads((root / "schemas" / "release.schema.json").read_text(encoding="utf-8"))
        errors.extend(validate(manifest, release_schema))
        if manifest.get("system_version") != verification.version:
            errors.append("release manifest version disagrees with package identity")
        if manifest.get("status") == "unreleased" and not candidate_test:
            errors.append("unreleased package requires --candidate-test")
        for schema_path in sorted((root / "schemas").glob("*.schema.json")):
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema" or schema.get("type") != "object":
                errors.append(f"invalid schema document: {schema_path.relative_to(root)}")
        load_operation_registry(
            root / "core" / "operations" / "registry.json",
            root / "schemas" / "operation-registry.schema.json",
            root,
        )
    except (OSError, json.JSONDecodeError, ContractError, PackageError, ReferenceError) as exc:
        errors.append(str(exc))
    return errors


def _archive_root(archive: Path, temporary: Path) -> Path:
    version = archive.name.removeprefix("school-os-").removesuffix(".tar.gz")
    sums = archive.with_name("SHA256SUMS")
    errors = verify_release_archive(archive, sums, version)
    if errors:
        raise PackageError("; ".join(errors))
    with tarfile.open(archive, "r:gz") as package:
        package.extractall(temporary)
    return temporary / f"School-OS-{version}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package_or_root", type=Path)
    parser.add_argument("--candidate-test", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.package_or_root.is_file():
            with tempfile.TemporaryDirectory() as temporary:
                errors = validate_installed(_archive_root(args.package_or_root, Path(temporary)), candidate_test=args.candidate_test)
        else:
            errors = validate_installed(args.package_or_root, candidate_test=args.candidate_test)
    except (OSError, tarfile.TarError, PackageError) as exc:
        errors = [str(exc)]
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"valid installed package: {args.package_or_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
