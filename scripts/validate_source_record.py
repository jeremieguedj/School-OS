#!/usr/bin/env python3
"""Validate verbatim Gmail bodies embedded in a School-OS Markdown record."""

from __future__ import annotations

import re
from collections.abc import Mapping


RAW_SECTION = "## Raw message text (verbatim)"
MESSAGE_HEADING = re.compile(
    r"(?m)^### Message\s+\d+\s+of\s+\d+\s+—\s+id\s+`?([^`\s]+)`?\s*$"
)


def extract_raw_message_bodies(record: str) -> dict[str, str]:
    """Return exact message bodies from the canonical raw-message section."""
    if RAW_SECTION not in record:
        return {}
    raw = record.split(RAW_SECTION, 1)[1].lstrip("\n")
    matches = list(MESSAGE_HEADING.finditer(raw))
    bodies: dict[str, str] = {}
    for index, match in enumerate(matches):
        block_start = match.end()
        block_end = matches[index + 1].start() if index + 1 < len(matches) else len(raw)
        block = raw[block_start:block_end]
        if block.startswith("\n"):
            block = block[1:]
        separator = block.find("\n\n")
        if separator < 0:
            continue
        body = block[separator + 2 :]
        bodies[match.group(1)] = body
    return bodies


def validate_lossless_bodies(record: str, source_bodies: Mapping[str, str]) -> list[str]:
    """Compare catalogued bodies directly with complete adapter-returned bodies."""
    catalogued = extract_raw_message_bodies(record)
    errors: list[str] = []
    if list(catalogued) != list(source_bodies):
        errors.append(
            "ordered message IDs differ: "
            f"catalog={list(catalogued)!r}, source={list(source_bodies)!r}"
        )
    for message_id, source_body in source_bodies.items():
        if message_id not in catalogued:
            errors.append(f"message {message_id!r} is missing from the raw-message section")
        elif catalogued[message_id] != source_body:
            errors.append(f"message {message_id!r} body is not verbatim")
    return errors
