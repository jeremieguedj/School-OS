#!/usr/bin/env python3
"""Deterministically add atomic Fact references to a legacy rolling stream.

The command accepts a synthetic/private JSON plan on stdin or by filename and
prints a JSON result. It never writes the rolling file; callers must separately
perform backup, verified replacement, and readback.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


HEADING_RE = re.compile(r"^## (\d{4}-\d{2}-\d{2})$")
BULLET_RE = re.compile(
    r"^- (?P<group>[^:]+): (?P<text>.+?) \[TID:(?P<source>[^\]]+)\]"
    r"(?: \[Facts:(?P<facts>[^\]]+)\])?$"
)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass(frozen=True)
class Fact:
    fact_id: str
    source_id: str
    scope: tuple[str, ...]
    text: str
    is_update: bool
    is_guideline: bool
    is_action: bool
    received_day: str | None = None
    record_received_dates: tuple[str, ...] = ()

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> "Fact":
        scope = value.get("scope", [])
        if isinstance(scope, str):
            scope = [part.strip() for part in scope.split(",")]
        dates = value.get("record_received_dates", [])
        if isinstance(dates, str):
            dates = [dates]
        return cls(
            fact_id=value["fact_id"],
            source_id=value["source_id"],
            scope=tuple(scope),
            text=value["text"],
            is_update=value.get("is_update", False),
            is_guideline=value.get("is_guideline", False),
            is_action=value.get("is_action", False),
            received_day=value.get("received_day"),
            record_received_dates=tuple(dates),
        )


def normalize_presentation(text: str) -> str:
    text = re.sub(r"^`[^`]+`\s*:\s*", "", text.strip())
    text = re.sub(r"(?<!\\)(?:\*\*|__|[*_`])", "", text)
    return " ".join(text.split())


def projected_group(fact: Fact, config: dict[str, Any]) -> str | None:
    scope = [item for item in fact.scope if item]
    if scope == ["unscoped"] or not scope:
        return config.get("unscoped_update_group")
    scope_groups = config.get("scope_groups", {})
    if any(item not in scope_groups for item in scope):
        return None
    if len(set(scope)) > 1:
        return config.get("shared_group")
    return scope_groups[scope[0]]


def effective_day(fact: Fact) -> tuple[str | None, bool]:
    if fact.received_day:
        return (fact.received_day, False) if DATE_RE.fullmatch(fact.received_day) else (None, False)
    if len(fact.record_received_dates) == 1 and DATE_RE.fullmatch(fact.record_received_dates[0]):
        return fact.record_received_dates[0], True
    return None, False


def fact_is_eligible(fact: Fact, *, source: str, day: str, group: str, text: str, config: dict[str, Any]) -> bool:
    fact_day, _fallback = effective_day(fact)
    return (
        fact.source_id == source
        and fact.is_update
        and not fact.is_guideline
        and not fact.is_action
        and fact_day == day
        and projected_group(fact, config) == group
        and normalize_presentation(fact.text) == normalize_presentation(text)
    )


def migrate(rolling: str, facts: list[Fact], config: dict[str, Any]) -> dict[str, Any]:
    """Return a complete candidate or the byte-identical blocked input."""
    source_ids = {fact.source_id for fact in facts}
    fact_by_id = {fact.fact_id: fact for fact in facts}
    if len(fact_by_id) != len(facts):
        return {"status": "blocked", "output": rolling, "exceptions": [{"reason": "duplicate_fact_id"}]}
    output: list[str] = []
    exceptions: list[dict[str, Any]] = []
    day: str | None = None
    migrated = skipped = fallback_count = 0
    for line_number, line in enumerate(rolling.splitlines(keepends=True), 1):
        bare = line.rstrip("\r\n")
        ending = line[len(bare):]
        heading = HEADING_RE.fullmatch(bare)
        if heading:
            day = heading.group(1)
            output.append(line)
            continue
        if not bare.startswith("- "):
            output.append(line)
            continue
        bullet = BULLET_RE.fullmatch(bare)
        if not bullet or day is None:
            exceptions.append({"line": line_number, "reason": "malformed_legacy_bullet"})
            output.append(line)
            continue
        source = bullet.group("source")
        group = bullet.group("group")
        text = bullet.group("text")
        existing = bullet.group("facts")
        eligible = [
            fact for fact in facts
            if fact_is_eligible(fact, source=source, day=day, group=group, text=text, config=config)
        ]
        if existing:
            ids = [item.strip() for item in existing.split(",") if item.strip()]
            valid = bool(ids) and len(ids) == len(set(ids)) and all(
                item in fact_by_id and fact_by_id[item] in eligible for item in ids
            )
            if not valid:
                exceptions.append({"line": line_number, "source_id": source, "reason": "invalid_existing_fact_references", "fact_ids": ids})
            else:
                skipped += 1
            output.append(line)
            continue
        if source not in source_ids:
            exceptions.append({"line": line_number, "source_id": source, "reason": "source_not_found", "candidate_fact_ids": []})
            output.append(line)
            continue
        if len(eligible) != 1:
            exceptions.append({
                "line": line_number,
                "source_id": source,
                "reason": "zero_matches" if not eligible else "ambiguous_matches",
                "candidate_fact_ids": [fact.fact_id for fact in eligible],
            })
            output.append(line)
            continue
        fact = eligible[0]
        _fact_day, used_fallback = effective_day(fact)
        fallback_count += int(used_fallback)
        output.append(f"{bare} [Facts:{fact.fact_id}]{ending}")
        migrated += 1
    if exceptions:
        return {"status": "blocked", "output": rolling, "exceptions": exceptions}
    return {
        "status": "migrated",
        "output": "".join(output),
        "exceptions": [],
        "migrated_bullets": migrated,
        "idempotently_skipped_bullets": skipped,
        "record_date_fallbacks": fallback_count,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", nargs="?", type=Path, help="JSON plan; stdin when omitted")
    args = parser.parse_args(argv)
    try:
        raw = args.plan.read_text(encoding="utf-8") if args.plan else sys.stdin.read()
        plan = json.loads(raw)
        result = migrate(plan["rolling"], [Fact.from_mapping(item) for item in plan["facts"]], plan["config"])
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        print(f"invalid migration plan: {exc}", file=sys.stderr)
        return 2
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0 if result["status"] == "migrated" else 1


if __name__ == "__main__":
    raise SystemExit(main())
