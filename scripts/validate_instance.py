#!/usr/bin/env python3
"""Validate a School-OS instance manifest using only the Python standard library.

The YAML reader intentionally accepts only the mapping/scalar subset used by the
instance template. Rejecting aliases, tags, sequences, and duplicate keys keeps
validation predictable without adding a runtime YAML dependency.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


class ContractError(ValueError):
    """Raised when input cannot be parsed or violates the JSON Schema contract."""


def _parse_scalar(value: str, line_number: int) -> Any:
    if not value:
        return {}
    if value == "[]":
        return []
    if value == "{}":
        return {}
    if value == "null":
        return None
    if value in {"true", "false"}:
        return value == "true"
    if re.fullmatch(r"-?(?:0|[1-9][0-9]*)", value):
        return int(value)
    if value[0:1] in {'"', "'"}:
        try:
            return json.loads(value) if value.startswith('"') else value[1:-1]
        except (json.JSONDecodeError, IndexError) as exc:
            raise ContractError(f"line {line_number}: invalid quoted scalar") from exc
    if value.startswith(("[", "{", "&", "*", "!", "|", ">")):
        raise ContractError(f"line {line_number}: unsupported YAML construct")
    return value


def load_mapping_yaml(text: str) -> dict[str, Any]:
    """Parse a conservative mappings/sequences/scalars subset of YAML."""
    tokens: list[tuple[int, str, int]] = []
    for line_number, raw_line in enumerate(text.splitlines(), 1):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if "\t" in raw_line:
            raise ContractError(f"line {line_number}: tabs are not allowed")
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        if indent % 2:
            raise ContractError(f"line {line_number}: indentation must use two spaces")
        tokens.append((indent, raw_line.strip(), line_number))

    def parse_block(index: int, indent: int) -> tuple[Any, int]:
        if index >= len(tokens) or tokens[index][0] != indent:
            line = tokens[index][2] if index < len(tokens) else "end of file"
            raise ContractError(f"line {line}: unexpected indentation")
        is_sequence = tokens[index][1].startswith("- ")
        container: Any = [] if is_sequence else {}
        while index < len(tokens) and tokens[index][0] == indent:
            _current_indent, content, line_number = tokens[index]
            if is_sequence:
                if not content.startswith("- "):
                    raise ContractError(f"line {line_number}: cannot mix mappings and sequences")
                item = content[2:].strip()
                if not item:
                    if index + 1 >= len(tokens) or tokens[index + 1][0] != indent + 2:
                        raise ContractError(f"line {line_number}: empty sequence item")
                    value, index = parse_block(index + 1, indent + 2)
                    container.append(value)
                    continue
                container.append(_parse_scalar(item, line_number))
                index += 1
                continue
            if content.startswith("- "):
                raise ContractError(f"line {line_number}: cannot mix mappings and sequences")
            match = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_-]*):(?:[ ](.*))?", content)
            if not match:
                raise ContractError(f"line {line_number}: expected a mapping entry")
            key, raw_value = match.group(1), match.group(2)
            if key in container:
                raise ContractError(f"line {line_number}: duplicate key {key!r}")
            if raw_value:
                container[key] = _parse_scalar(raw_value, line_number)
                index += 1
                continue
            if index + 1 < len(tokens) and tokens[index + 1][0] == indent + 2:
                container[key], index = parse_block(index + 1, indent + 2)
            else:
                container[key] = {}
                index += 1
        if index < len(tokens) and tokens[index][0] > indent:
            raise ContractError(f"line {tokens[index][2]}: unexpected indentation")
        return container, index

    if not tokens:
        return {}
    if tokens[0][0] != 0:
        raise ContractError(f"line {tokens[0][2]}: root must not be indented")
    root, consumed = parse_block(0, 0)
    if consumed != len(tokens):
        raise ContractError(f"line {tokens[consumed][2]}: invalid document structure")
    if not isinstance(root, dict):
        raise ContractError("manifest root must be an object")
    return root


def _type_matches(value: Any, expected: str) -> bool:
    return {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "number": isinstance(value, (int, float)) and not isinstance(value, bool),
        "boolean": isinstance(value, bool),
        "null": value is None,
    }.get(expected, False)


def validate(value: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    """Validate the JSON Schema keywords used by School-OS schemas."""
    errors: list[str] = []
    declared_types = schema.get("type")
    if declared_types is not None:
        types = [declared_types] if isinstance(declared_types, str) else declared_types
        if not any(_type_matches(value, item) for item in types):
            return [f"{path}: expected {' or '.join(types)}"]
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: must be one of {schema['enum']!r}")
    if isinstance(value, dict):
        required = schema.get("required", [])
        errors.extend(f"{path}: missing required property {key!r}" for key in required if key not in value)
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            errors.extend(f"{path}: unexpected property {key!r}" for key in value if key not in properties)
        for key, item in value.items():
            if key in properties:
                errors.extend(validate(item, properties[key], f"{path}.{key}"))
    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append(f"{path}: requires at least {schema['minItems']} items")
        if schema.get("uniqueItems"):
            encoded = [json.dumps(item, sort_keys=True) for item in value]
            if len(set(encoded)) != len(encoded):
                errors.append(f"{path}: items must be unique")
        if "items" in schema:
            for index, item in enumerate(value):
                errors.extend(validate(item, schema["items"], f"{path}[{index}]"))
    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            errors.append(f"{path}: must not be empty")
        if "pattern" in schema and re.fullmatch(schema["pattern"], value) is None:
            errors.append(f"{path}: does not match required pattern")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path}: must be at least {schema['minimum']}")
    return errors


def load_manifest(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        value = json.loads(text)
        if not isinstance(value, dict):
            raise ContractError("manifest root must be an object")
        return value
    return load_mapping_yaml(text)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument(
        "--schema",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "schemas" / "instance.schema.json",
    )
    args = parser.parse_args(argv)
    try:
        manifest = load_manifest(args.manifest)
        schema = json.loads(args.schema.read_text(encoding="utf-8"))
        errors = validate(manifest, schema)
    except (OSError, json.JSONDecodeError, ContractError) as exc:
        print(f"invalid: {exc}", file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"valid: {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
