#!/usr/bin/env python3
"""Conservative privacy scan for tracked School-OS source files."""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path


PRIVATE_NEEDLES_ENV = "SCHOOL_OS_PRIVATE_NEEDLES"
EMAIL_RE = re.compile(r"(?i)(?<![A-Z0-9._%+-])([A-Z0-9._%+-]+)@([A-Z0-9.-]+\.[A-Z]{2,})(?![A-Z0-9.-])")
DRIVE_URL_RE = re.compile(r"(?i)https?://(?:drive|docs)\.google\.com(?:/|\b)")
GITHUB_URL_RE = re.compile(r"(?i)https?://(?:www\.)?github\.com/[^\s)\]>]+")
TOKEN_RE = re.compile(r"(?<![A-Za-z0-9_-])[A-Za-z0-9_-]{25,}(?![A-Za-z0-9_-])")
PRIVATE_KEY_RE = re.compile(r"-{5}BEGIN (?:RSA |EC |OPENSSH )?PRIVATE" + r" KEY-{5}")
CREDENTIAL_ASSIGNMENT_RE = re.compile(
    r"(?im)\b(?:api[_-]?key|client[_-]?secret|access[_-]?token|refresh[_-]?token|password|passwd)"
    r"\b\s*[:=]\s*[\"']?([^\s\"'#]{8,})"
)
KNOWN_TOKEN_RES = (
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b"),
    re.compile(r"\bxox[baprs]-[0-9A-Za-z-]{20,}\b"),
)
RESERVED_EMAIL_DOMAINS = {"example.com", "example.invalid", "example.net", "example.org"}
PLACEHOLDER_MARKERS = ("REPLACE", "SYNTHETIC", "EXAMPLE", "REDACTED", "NOT_CONFIGURED")


def _line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _violation(path: str, text: str, offset: int, category: str) -> str:
    return f"{path}:{_line_number(text, offset)}: privacy violation ({category})"


def _looks_like_drive_id(token: str) -> bool:
    return (
        any(character.islower() for character in token)
        and any(character.isupper() for character in token)
        and any(character.isdigit() for character in token)
    )


def _is_placeholder(value: str) -> bool:
    upper = value.upper()
    return any(marker in upper for marker in PLACEHOLDER_MARKERS) or value.startswith(("$", "<", "{"))


def scan_text(path: str, text: str, private_needles: tuple[str, ...] = ()) -> list[str]:
    """Return non-secret-bearing diagnostics for high-confidence privacy leaks."""
    violations: list[str] = []
    for match in DRIVE_URL_RE.finditer(text):
        violations.append(_violation(path, text, match.start(), "Google Drive/Docs URL"))
    for match in EMAIL_RE.finditer(text):
        domain = match.group(2).lower()
        if domain not in RESERVED_EMAIL_DOMAINS and not domain.endswith(".example"):
            violations.append(_violation(path, text, match.start(), "email address"))
    github_masked = GITHUB_URL_RE.sub(lambda match: " " * len(match.group(0)), text)
    for match in TOKEN_RE.finditer(github_masked):
        if _looks_like_drive_id(match.group(0)):
            violations.append(_violation(path, text, match.start(), "Drive-like identifier"))
    for match in PRIVATE_KEY_RE.finditer(text):
        violations.append(_violation(path, text, match.start(), "private-key marker"))
    for pattern in KNOWN_TOKEN_RES:
        for match in pattern.finditer(text):
            violations.append(_violation(path, text, match.start(), "credential token"))
    for match in CREDENTIAL_ASSIGNMENT_RE.finditer(text):
        if not _is_placeholder(match.group(1)):
            violations.append(_violation(path, text, match.start(), "credential assignment"))
    for index, needle in enumerate(private_needles, 1):
        if len(needle) < 4:
            continue
        start = text.find(needle)
        if start >= 0:
            violations.append(_violation(path, text, start, f"configured private needle {index}"))
    return violations


def configured_private_needles(environment: dict[str, str] | None = None) -> tuple[str, ...]:
    source = os.environ if environment is None else environment
    return tuple(item for item in source.get(PRIVATE_NEEDLES_ENV, "").splitlines() if item)


def scan_tracked_files(repo: Path, private_needles: tuple[str, ...] | None = None) -> list[str]:
    """Scan UTF-8 working-tree content for paths already tracked by Git."""
    result = subprocess.run(
        ["git", "-C", str(repo), "ls-files", "-z"],
        capture_output=True,
        check=False,
    )
    if result.returncode:
        detail = result.stderr.decode("utf-8", "replace").strip()
        return [f"privacy scan could not list tracked files: {detail}"]
    needles = configured_private_needles() if private_needles is None else private_needles
    violations: list[str] = []
    for raw_path in result.stdout.split(b"\0"):
        if not raw_path:
            continue
        try:
            relative = raw_path.decode("utf-8")
        except UnicodeDecodeError:
            violations.append("tracked path is not valid UTF-8")
            continue
        path = repo / relative
        if path.is_symlink():
            violations.append(f"{relative}: tracked symlink is not privacy-scannable")
            continue
        try:
            data = path.read_bytes()
        except OSError as exc:
            violations.append(f"{relative}: privacy scan read failed: {exc}")
            continue
        if b"\0" in data:
            continue
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            continue
        violations.extend(scan_text(relative, text, needles))
    return violations
