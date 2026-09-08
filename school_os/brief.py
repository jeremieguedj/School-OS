"""Deterministic daily-brief input assembly, rendering, and delivery ledger helpers."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime, timedelta, timezone as datetime_timezone
from html import escape
from pathlib import Path
import re
from typing import Any, Protocol
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .contracts import sha256_bytes, validate


class BriefError(ValueError):
    """Raised when a presentation input is incomplete or unsafe to render."""


class DeliveryPort(Protocol):
    def send(self, content: bytes) -> str: ...
    def find_delivery(self, content: bytes) -> list[str]: ...


_DATE_RE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}\Z")
_PLACEHOLDER_RE = re.compile(r"\{\{([A-Z][A-Z0-9_]*)\}\}")
_COLOR_RE = re.compile(r"#[0-9a-fA-F]{6}\Z")
_DEFAULT_THEME = {
    "accent": "#1f4b99", "news_banner": "#e6f4ea", "guidelines_banner": "#e8f0fe",
    "tasks_banner": "#e8eaed", "text": "#3c4043", "muted": "#5f6368",
}
_DEFAULT_LABELS = {
    "news": "What's new", "guidelines": "Recent school guidelines", "tasks": "Action items",
    "source": "Source", "task_link": "Link", "received": "Received",
    "empty_news": "Nothing new this week.",
    "empty_guidelines": "No new school guidelines this week.", "empty_tasks": "No open action items right now.",
}
_PARENT_ADDED_TASKS = "Parent-added tasks"


def _valid(value: Any, schema: Mapping[str, Any], label: str) -> None:
    errors = validate(value, dict(schema))
    if errors:
        raise BriefError(f"invalid {label}: " + "; ".join(errors))


def _date(value: Any, label: str) -> str:
    if not isinstance(value, str) or not _DATE_RE.fullmatch(value):
        raise BriefError(f"{label} must be an ISO local date")
    try:
        datetime.fromisoformat(value)
    except ValueError as exc:
        raise BriefError(f"{label} is not a calendar date") from exc
    return value


def _safe_url(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or any(character.isspace() for character in value):
        raise BriefError(f"{label} must be a non-empty ordinary URL")
    parsed = urlsplit(value)
    if parsed.scheme not in {"https", "http", "mailto"}:
        raise BriefError(f"{label} has an unsafe URL scheme")
    if parsed.scheme in {"https", "http"} and not parsed.netloc:
        raise BriefError(f"{label} lacks a URL host")
    if parsed.scheme == "mailto" and not parsed.path:
        raise BriefError(f"{label} lacks a mail recipient")
    return value


def _default_template() -> dict[str, Any]:
    root = Path(__file__).resolve().parents[1] / "templates" / "brief"
    return {
        "version": "default-v2",
        "html": (root / "default.html").read_text(encoding="utf-8"),
        "text": (root / "default.txt").read_text(encoding="utf-8"),
        "placeholders": {"BRIEF_CONTENT": {"kind": "content"}},
    }


def _theme(value: Mapping[str, Any] | None) -> dict[str, str]:
    candidate = dict(_DEFAULT_THEME if value is None else value)
    if set(candidate) != set(_DEFAULT_THEME):
        raise BriefError("theme must declare exactly the supported color settings")
    for name, color in candidate.items():
        if not isinstance(color, str) or not _COLOR_RE.fullmatch(color):
            raise BriefError(f"theme {name} must be a six-digit hex color")
    return candidate


def _labels(value: Mapping[str, Any] | None) -> dict[str, str]:
    candidate = {**_DEFAULT_LABELS, **dict(value or {})}
    unknown = set(value or {}) - set(_DEFAULT_LABELS)
    if unknown:
        raise BriefError("labels contain unsupported presentation settings")
    if any(not isinstance(text, str) or not text for text in candidate.values()):
        raise BriefError("labels must be non-empty strings")
    return candidate


def _entities(value: Sequence[Mapping[str, Any]]) -> tuple[list[dict[str, str]], dict[str, str]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or not value:
        raise BriefError("configured entities are required")
    entities: list[dict[str, str]] = []
    names: dict[str, str] = {}
    household_seen = False
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise BriefError("configured entity is malformed")
        entity_id, display_name, kind = item.get("entity_id"), item.get("display_name"), item.get("kind")
        if not all(isinstance(part, str) and part for part in (entity_id, display_name)) or kind not in {"child", "household"}:
            raise BriefError("configured entity lacks an ID, display name, or supported kind")
        if entity_id in names:
            raise BriefError("configured entity IDs must be unique")
        if kind == "household":
            if household_seen or index != len(value) - 1:
                raise BriefError("the one household entity must be last")
            household_seen = True
        elif household_seen:
            raise BriefError("children must precede the household entity")
        entities.append({"entity_id": entity_id, "display_name": display_name, "kind": kind})
        names[entity_id] = display_name
    if not household_seen:
        raise BriefError("configured entities require one household entity")
    return entities, names


def _local_day_from_gmail_internal_date(value: Any, timezone: str) -> tuple[str, str]:
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise BriefError("source record Gmail internal date must be milliseconds")
    try:
        milliseconds = int(value)
        zone = ZoneInfo(timezone)
        received = datetime.fromtimestamp(milliseconds / 1000, datetime_timezone.utc)
    except (ValueError, OverflowError, OSError, ZoneInfoNotFoundError) as exc:
        raise BriefError("source record Gmail internal date or timezone is invalid") from exc
    return received.astimezone(zone).date().isoformat(), received.isoformat().replace("+00:00", "Z")


def _source_metadata(fact: Mapping[str, Any], source_record_map: Mapping[str, Mapping[str, Any]], timezone: str) -> dict[str, Any]:
    fact_id = fact.get("fact_id")
    if not isinstance(fact_id, str) or fact_id not in source_record_map:
        raise BriefError("each presented Fact requires a verified source-record map entry")
    item = source_record_map[fact_id]
    if not isinstance(item, Mapping):
        raise BriefError("source-record map entry is malformed")
    required = ("record_id", "source_message_id", "gmail_internal_date_ms", "source_message_ordinal", "source_content_ordinal", "verified_link")
    if any(name not in item for name in required):
        raise BriefError("source-record map entry lacks verified message coordinates or link")
    if item["record_id"] != fact.get("record_id") or item["source_message_id"] != fact.get("source_message_id"):
        raise BriefError("source-record map entry does not match Fact provenance")
    if any(not isinstance(item[name], int) or item[name] < 0 for name in ("source_message_ordinal", "source_content_ordinal")):
        raise BriefError("source-record map ordinal must be a non-negative integer")
    received_date, received_at = _local_day_from_gmail_internal_date(item["gmail_internal_date_ms"], timezone)
    if fact.get("received_date") != received_date:
        raise BriefError("Fact received date must equal the configured-local Gmail internal date")
    return {"received_date": received_date, "source_received_at": received_at, "source_message_ordinal": item["source_message_ordinal"], "source_content_ordinal": item["source_content_ordinal"], "source_link": _safe_url(item["verified_link"], "verified source link")}


def _project_scope(scope: Any, scope_to_entity: Mapping[str, str], entity_names: Mapping[str, str]) -> str:
    if not isinstance(scope, str) or not scope:
        raise BriefError("canonical entity scope is required")
    entity_id = scope_to_entity.get(scope)
    if entity_id not in entity_names:
        raise BriefError("canonical entity scope has no configured brief projection")
    return entity_id


def _in_window(date: str, start: str, end: str) -> bool:
    return start <= date <= end


def build_brief_input(*, run_local_date: str, timezone: str, entities: Sequence[Mapping[str, Any]], scope_to_entity: Mapping[str, str], facts: Sequence[Mapping[str, Any]], source_record_map: Mapping[str, Mapping[str, Any]], current_guideline_selection: Sequence[Mapping[str, Any]] | None, unresolved_task_view: Mapping[str, Any], task_source_links: Mapping[str, str] | None = None, template: Mapping[str, Any] | None = None, labels: Mapping[str, Any] | None = None, theme: Mapping[str, Any] | None = None, input_hashes: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Build the v2 display contract from already-audited canonical views.

    Currentness and task resolution are explicit upstream selections. This
    renderer never guesses either from wording or workflow state.
    """
    end = _date(run_local_date, "run local date")
    try:
        start = (datetime.fromisoformat(end).date() - timedelta(days=6)).isoformat()
        ZoneInfo(timezone)
    except (ValueError, ZoneInfoNotFoundError) as exc:
        raise BriefError("configured timezone is invalid") from exc
    configured_entities, entity_names = _entities(entities)
    if set(scope_to_entity.values()) - set(entity_names):
        raise BriefError("scope projection references an unknown configured entity")
    if not isinstance(facts, Sequence) or isinstance(facts, (str, bytes)):
        raise BriefError("canonical Facts must be an array")
    facts_by_id: dict[str, Mapping[str, Any]] = {}
    metadata_by_id: dict[str, dict[str, Any]] = {}
    for fact in facts:
        if not isinstance(fact, Mapping) or not isinstance(fact.get("fact_id"), str) or fact["fact_id"] in facts_by_id:
            raise BriefError("canonical Facts require unique Fact IDs")
        if not isinstance(fact.get("text"), str) or not fact["text"] or not isinstance(fact.get("flags"), Mapping):
            raise BriefError("canonical Fact lacks verbatim text or flags")
        facts_by_id[fact["fact_id"]] = fact
        metadata_by_id[fact["fact_id"]] = _source_metadata(fact, source_record_map, timezone)

    eligible_news: list[tuple[tuple[Any, ...], dict[str, Any]]] = []
    for fact_id, fact in facts_by_id.items():
        flags = fact["flags"]
        if flags.get("is_update") is True and flags.get("is_action") is False and flags.get("is_guideline") is False:
            source = metadata_by_id[fact_id]
            if _in_window(source["received_date"], start, end):
                scope = fact.get("entity_scope")
                eligible_news.append(((source["received_date"], source["source_received_at"], source["source_message_ordinal"], source["source_content_ordinal"], fact_id), {"entity_scope": _project_scope(scope, scope_to_entity, entity_names), "scope_display": scope, "text": fact["text"], **source}))
    eligible_news.sort(key=lambda item: (-datetime.fromisoformat(item[0][0]).toordinal(), *item[0][1:]))
    news = [{**item, "order": index} for index, (_key, item) in enumerate(eligible_news)]

    if current_guideline_selection is None:
        raise BriefError("current guideline selection is required from the upstream canonical guideline view")
    if not isinstance(current_guideline_selection, Sequence) or isinstance(current_guideline_selection, (str, bytes)):
        raise BriefError("current guideline selection must be an array")
    guidelines: list[dict[str, Any]] = []
    selected_guidelines: set[str] = set()
    for index, selection in enumerate(current_guideline_selection):
        if not isinstance(selection, Mapping) or selection.get("is_current") is not True:
            raise BriefError("current guideline selection requires explicit is_current true")
        fact_id, latest_date = selection.get("fact_id"), selection.get("latest_source_received_date")
        if not isinstance(fact_id, str) or fact_id in selected_guidelines or fact_id not in facts_by_id:
            raise BriefError("current guideline selection must name each selected Fact once")
        fact = facts_by_id[fact_id]
        if fact["flags"].get("is_guideline") is not True:
            raise BriefError("current guideline selection references a non-guideline Fact")
        latest_date = _date(latest_date, "guideline latest source received date")
        if _in_window(latest_date, start, end):
            scope = fact.get("entity_scope")
            guidelines.append({"entity_scope": _project_scope(scope, scope_to_entity, entity_names), "scope_display": scope, "text": fact["text"], "received_date": latest_date, "source_link": _safe_url(selection.get("verified_link"), "current guideline verified link"), "order": index})
        selected_guidelines.add(fact_id)

    if not isinstance(unresolved_task_view, Mapping) or unresolved_task_view.get("selection") != "all_unresolved_finite":
        raise BriefError("unresolved task view must explicitly declare all_unresolved_finite")
    unresolved = unresolved_task_view.get("tasks")
    if not isinstance(unresolved, Sequence) or isinstance(unresolved, (str, bytes)):
        raise BriefError("unresolved task view must contain a task array")
    task_links = dict(task_source_links or {})
    tasks: list[dict[str, Any]] = []
    for index, task in enumerate(unresolved):
        if not isinstance(task, Mapping) or task.get("resolution") != "unresolved":
            raise BriefError("brief tasks require an explicit unresolved resolution")
        task_id, origin, action = task.get("task_id"), task.get("origin"), task.get("action")
        if not isinstance(task_id, str) or not task_id or origin not in {"source", "parent"} or not isinstance(action, str) or not action:
            raise BriefError("unresolved task is malformed")
        received_date = task.get("last_supporting_source_date")
        if received_date is not None:
            received_date = _date(received_date, "task last supporting source date")
        raw_link = task_links.get(task_id, task.get("source_link"))
        if origin == "source" and (received_date is None or raw_link is None):
            raise BriefError("source-origin unresolved task requires verified source date and link")
        if raw_link is not None:
            raw_link = _safe_url(raw_link, "task verified link")
        scope = task.get("entity_scope")
        tasks.append({"entity_scope": _project_scope(scope, scope_to_entity, entity_names), "scope_display": scope, "text": action, "received_date": received_date, "source_link": raw_link, "origin": origin, "order": index})

    result = {"schema_version": 2, "window": {"start": start, "end": end, "timezone": timezone}, "entity_order": [entity["entity_id"] for entity in configured_entities], "entities": configured_entities, "news": news, "guidelines": guidelines, "tasks": tasks, "labels": _labels(labels), "theme": _theme(theme), "template": dict(_default_template() if template is None else template), "input_hashes": dict(input_hashes or {})}
    _validate_v2(result)
    return result


def _validate_template(template: Any) -> dict[str, Any]:
    if not isinstance(template, Mapping) or set(template) != {"version", "html", "text", "placeholders"}:
        raise BriefError("template must declare version, html, text, and placeholder map")
    if not isinstance(template["version"], str) or not template["version"] or not all(isinstance(template[name], str) for name in ("html", "text")):
        raise BriefError("template version and bodies are required strings")
    mapping = template["placeholders"]
    if not isinstance(mapping, Mapping) or not mapping:
        raise BriefError("template requires a declared placeholder map")
    declared = set(mapping)
    if any(not isinstance(key, str) or not _PLACEHOLDER_RE.fullmatch("{{" + key + "}}") for key in declared):
        raise BriefError("template placeholder names are invalid")
    for body_name in ("html", "text"):
        occurrences = _PLACEHOLDER_RE.findall(template[body_name])
        if set(occurrences) != declared or len(occurrences) != len(declared):
            raise BriefError(f"template {body_name} must contain each declared placeholder exactly once")
    for key, rule in mapping.items():
        if not isinstance(rule, Mapping):
            raise BriefError(f"template placeholder {key} is malformed")
        kind = rule.get("kind")
        if kind in {"date", "content"}:
            if set(rule) != {"kind"}:
                raise BriefError(f"template placeholder {key} has unsupported settings")
        elif kind == "entries":
            if set(rule) - {"kind", "section", "entity_scope", "empty_text"} or rule.get("section") not in {"news", "guidelines", "tasks"} or not isinstance(rule.get("entity_scope"), str):
                raise BriefError(f"template placeholder {key} lacks a valid entry selection")
            if "empty_text" in rule and (not isinstance(rule["empty_text"], str) or not rule["empty_text"]):
                raise BriefError(f"template placeholder {key} has an invalid empty state")
        else:
            raise BriefError(f"template placeholder {key} has an unsupported kind")
    return dict(template)


def _validate_template_routes(template: Mapping[str, Any], value: Mapping[str, Any], entity_names: Mapping[str, str]) -> None:
    """Require every eligible item to have exactly one declared output route."""
    rules = list(template["placeholders"].values())
    content_rules = [rule for rule in rules if rule["kind"] == "content"]
    entry_rules = [rule for rule in rules if rule["kind"] == "entries"]
    if len(content_rules) > 1 or (content_rules and entry_rules):
        raise BriefError("template cannot combine duplicate full content with entry placeholders")
    if content_rules:
        return
    for section in ("news", "guidelines", "tasks"):
        for item in value[section]:
            matches = [rule for rule in entry_rules if rule["section"] == section and (rule["entity_scope"] == "*" or rule["entity_scope"] == item["entity_scope"])]
            if len(matches) != 1:
                raise BriefError(f"template does not route exactly one slot for eligible {section} item")


def _validate_v2(value: Mapping[str, Any]) -> None:
    required = {"schema_version", "window", "entity_order", "entities", "news", "guidelines", "tasks", "labels", "theme", "template", "input_hashes"}
    if set(value) != required or value.get("schema_version") != 2:
        raise BriefError("brief input v2 has an invalid shape")
    window = value["window"]
    if not isinstance(window, Mapping) or set(window) != {"start", "end", "timezone"}:
        raise BriefError("brief input window is malformed")
    start, end = _date(window["start"], "window start"), _date(window["end"], "window end")
    if start > end or (datetime.fromisoformat(end).date() - datetime.fromisoformat(start).date()).days != 6:
        raise BriefError("brief input window must be the inclusive seven local days")
    try:
        ZoneInfo(window["timezone"])
    except (TypeError, ZoneInfoNotFoundError) as exc:
        raise BriefError("brief input timezone is invalid") from exc
    entities, names = _entities(value["entities"])
    if value["entity_order"] != [entity["entity_id"] for entity in entities]:
        raise BriefError("brief entity order must equal configured entity order")
    _labels(value["labels"]); _theme(value["theme"]); template = _validate_template(value["template"])
    for rule in template["placeholders"].values():
        if rule["kind"] == "entries" and rule["entity_scope"] not in names and rule["entity_scope"] != "*":
            raise BriefError("template entry placeholder references an unknown entity")
    for section in ("news", "guidelines", "tasks"):
        items = value[section]
        if not isinstance(items, list):
            raise BriefError(f"brief {section} must be an array")
        orders: set[int] = set()
        for item in items:
            if not isinstance(item, Mapping) or set(item) - {"entity_scope", "scope_display", "text", "received_date", "source_link", "source_received_at", "source_message_ordinal", "source_content_ordinal", "origin", "order"}:
                raise BriefError(f"brief {section} item has unsupported fields")
            if item.get("entity_scope") not in names or not isinstance(item.get("scope_display"), str) or not item["scope_display"] or not isinstance(item.get("text"), str) or not item["text"]:
                raise BriefError(f"brief {section} item lacks configured scope or verbatim text")
            received_date = item.get("received_date")
            if received_date is not None:
                _date(received_date, f"brief {section} received date")
            if section != "tasks" and received_date is None:
                raise BriefError(f"brief {section} item requires a received date")
            link = item.get("source_link")
            if section in {"news", "guidelines"} and link is None:
                raise BriefError(f"brief {section} item requires a verified source link")
            if link is not None:
                _safe_url(link, f"brief {section} link")
            if section == "tasks" and item.get("origin") not in {"source", "parent"}:
                raise BriefError("brief task requires source or parent origin")
            if section == "tasks" and item.get("origin") == "source" and (received_date is None or link is None):
                raise BriefError("source-origin brief task requires a received date and verified link")
            order = item.get("order")
            if not isinstance(order, int) or order < 0 or order in orders:
                raise BriefError(f"brief {section} order must be a unique non-negative integer")
            orders.add(order)
    _validate_template_routes(template, value, names)


def _human_date(value: str) -> str:
    return datetime.fromisoformat(value).strftime("%B %-d, %Y")


def _ordered(items: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    return sorted(items, key=lambda item: (1 if item.get("received_date") is None else 0, "" if item.get("received_date") is None else -datetime.fromisoformat(item["received_date"]).toordinal(), item.get("order", 0)))


def _line(item: Mapping[str, Any], section: str, *, html_output: bool, labels: Mapping[str, str], entity_names: Mapping[str, str]) -> str:
    text, link = item["text"], item.get("source_link")
    label = labels["task_link"] if section == "tasks" else labels["source"]
    scope = item["scope_display"] if section == "guidelines" else None
    if scope == item["entity_scope"]:
        scope = entity_names[item["entity_scope"]]
    prefix = f"{scope}: " if scope else ""
    if html_output:
        rendered_prefix = f"<strong>{escape(scope)}:</strong> " if scope else ""
        suffix = f' &mdash; <a href="{escape(link, quote=True)}">{escape(label)}</a>' if link else ""
        return f"<li>{rendered_prefix}{escape(text)}{suffix}</li>"
    return f"- {prefix}{text}" + (f" — {label}: {link}" if link else "")


def _groups(items: Sequence[Mapping[str, Any]]) -> list[tuple[str | None, list[Mapping[str, Any]]]]:
    result: list[tuple[str | None, list[Mapping[str, Any]]]] = []
    for item in _ordered(items):
        date = item.get("received_date")
        if not result or result[-1][0] != date:
            result.append((date, [item]))
        else:
            result[-1][1].append(item)
    return result


def _empty_text(section: str, entity_id: str, labels: Mapping[str, str], entity_names: Mapping[str, str], rule: Mapping[str, Any] | None) -> str:
    if rule and rule.get("empty_text"):
        return rule["empty_text"]
    if section == "news":
        return labels["empty_news"]
    if section == "guidelines":
        return labels["empty_guidelines"]
    if entity_id != "*" and entity_names[entity_id] != "Family":
        return f"No open action items specific to {entity_names[entity_id]} right now."
    return labels["empty_tasks"]


def _render_entries(items: Sequence[Mapping[str, Any]], section: str, entity_id: str, *, html_output: bool, labels: Mapping[str, str], entity_names: Mapping[str, str], theme: Mapping[str, str], rule: Mapping[str, Any] | None = None) -> str:
    selected = list(items) if entity_id == "*" else [item for item in items if item["entity_scope"] == entity_id]
    if not selected:
        empty = _empty_text(section, entity_id, labels, entity_names, rule)
        return f'<ul style="margin:0; padding-left:16px; color:{theme["text"]}; font-size:15px; line-height:1.7;"><li>{escape(empty)}</li></ul>' if html_output else "- " + empty
    groups = _groups(selected)
    if html_output:
        pieces: list[str] = []
        for date, group in groups:
            heading = _PARENT_ADDED_TASKS if date is None else f"{labels['received']} {_human_date(date)}"
            pieces.append(f'<div style="font-size:11px; font-weight:600; color:{theme["muted"]}; margin:10px 0 3px 0;">{escape(heading)}</div>')
            pieces.append(f'<ul style="margin:0; padding-left:16px; color:{theme["text"]}; font-size:15px; line-height:1.7;">' + "".join(_line(item, section, html_output=True, labels=labels, entity_names=entity_names) for item in group) + "</ul>")
        return "".join(pieces)
    pieces = []
    for date, group in groups:
        heading = _PARENT_ADDED_TASKS if date is None else f"{labels['received']} {date}"
        pieces.append(heading + "\n" + "\n".join(_line(item, section, html_output=False, labels=labels, entity_names=entity_names) for item in group))
    return "\n".join(pieces)


def _render_content(value: Mapping[str, Any], *, html_output: bool) -> str:
    labels, theme, entities = value["labels"], value["theme"], value["entities"]
    names = {entity["entity_id"]: entity["display_name"] for entity in entities}
    pieces: list[str] = []
    for entity in entities:
        entity_id = entity["entity_id"]
        if entity["kind"] == "household":
            if html_output:
                pieces.append(f'<section style="padding:16px 16px 0 16px;"><div style="background-color:{theme["tasks_banner"]}; border-radius:8px; padding:10px 14px; color:{theme["text"]}; font-size:15px; font-weight:600;">{escape(names[entity_id])}</div><div style="font-size:12px; font-weight:600; color:{theme["muted"]}; text-transform:uppercase; letter-spacing:0.4px; margin:14px 0 6px 0;">{escape(labels["news"])}</div>' + _render_entries(value["news"], "news", entity_id, html_output=True, labels=labels, entity_names=names, theme=theme) + f'<div style="font-size:12px; font-weight:600; color:{theme["muted"]}; text-transform:uppercase; letter-spacing:0.4px; margin:14px 0 6px 0;">{escape(labels["tasks"])}</div>' + _render_entries(value["tasks"], "tasks", entity_id, html_output=True, labels=labels, entity_names=names, theme=theme) + "</section>")
            else:
                pieces.append(f"{names[entity_id]}\n{labels['news']}\n" + _render_entries(value["news"], "news", entity_id, html_output=False, labels=labels, entity_names=names, theme=theme))
                pieces.append(labels["tasks"] + "\n" + _render_entries(value["tasks"], "tasks", entity_id, html_output=False, labels=labels, entity_names=names, theme=theme))
            continue
        if html_output:
            pieces.append(f'<section style="padding:16px 16px 0 16px;"><div style="background-color:{theme["news_banner"]}; border-radius:8px; padding:10px 14px; color:{theme["text"]}; font-size:15px; font-weight:600;">{escape(names[entity_id])}</div><div style="font-size:12px; font-weight:600; color:{theme["muted"]}; text-transform:uppercase; letter-spacing:0.4px; margin:14px 0 6px 0;">{escape(labels["news"])}</div>' + _render_entries(value["news"], "news", entity_id, html_output=True, labels=labels, entity_names=names, theme=theme) + f'<div style="font-size:12px; font-weight:600; color:{theme["muted"]}; text-transform:uppercase; letter-spacing:0.4px; margin:14px 0 6px 0;">{escape(labels["tasks"])}</div>' + _render_entries(value["tasks"], "tasks", entity_id, html_output=True, labels=labels, entity_names=names, theme=theme) + "</section>")
        else:
            pieces.append(f"{names[entity_id]}\n{labels['news']}\n" + _render_entries(value["news"], "news", entity_id, html_output=False, labels=labels, entity_names=names, theme=theme))
            pieces.append(labels["tasks"] + "\n" + _render_entries(value["tasks"], "tasks", entity_id, html_output=False, labels=labels, entity_names=names, theme=theme))
    if html_output:
        pieces.append(f'<section style="padding:16px 16px 28px 16px;"><div style="background-color:{theme["guidelines_banner"]}; border-radius:8px; padding:10px 14px; color:{theme["text"]}; font-size:15px; font-weight:600;">{escape(labels["guidelines"])}</div><div style="margin-top:14px;">' + _render_entries(value["guidelines"], "guidelines", "*", html_output=True, labels=labels, entity_names=names, theme=theme) + "</div></section>")
    else:
        pieces.append(labels["guidelines"] + "\n" + _render_entries(value["guidelines"], "guidelines", "*", html_output=False, labels=labels, entity_names=names, theme=theme))
    return "".join(pieces) if html_output else "\n\n".join(pieces)


def _substitute(template: str, replacements: Mapping[str, str], label: str) -> str:
    rendered = _PLACEHOLDER_RE.sub(lambda match: replacements[match.group(1)], template)
    if _PLACEHOLDER_RE.search(rendered):
        raise BriefError(f"template {label} has unresolved placeholders")
    return rendered


def _render_v2(value: Mapping[str, Any]) -> dict[str, bytes]:
    _validate_v2(value)
    names = {entity["entity_id"]: entity["display_name"] for entity in value["entities"]}
    html_replacements: dict[str, str] = {}
    text_replacements: dict[str, str] = {}
    for name, rule in value["template"]["placeholders"].items():
        if rule["kind"] == "date":
            html_replacements[name], text_replacements[name] = escape(_human_date(value["window"]["end"])), value["window"]["end"]
        elif rule["kind"] == "content":
            html_replacements[name], text_replacements[name] = _render_content(value, html_output=True), _render_content(value, html_output=False)
        else:
            section, entity_id = rule["section"], rule["entity_scope"]
            html_replacements[name] = _render_entries(value[section], section, entity_id, html_output=True, labels=value["labels"], entity_names=names, theme=value["theme"], rule=rule)
            text_replacements[name] = _render_entries(value[section], section, entity_id, html_output=False, labels=value["labels"], entity_names=names, theme=value["theme"], rule=rule)
    return {"html": _substitute(value["template"]["html"], html_replacements, "html").encode("utf-8"), "text": _substitute(value["template"]["text"], text_replacements, "text").encode("utf-8")}


def _legacy_to_v2(value: Mapping[str, Any]) -> dict[str, Any]:
    """Keep schema-v1 fixtures readable while applying corrected grouping behavior."""
    order = value.get("entity_order")
    if not isinstance(order, list) or not all(isinstance(entity, str) and entity for entity in order):
        raise BriefError("legacy brief input has invalid entity order")
    entities = [{"entity_id": entity, "display_name": entity.replace("_", " ").title(), "kind": "household" if entity == "household" else "child"} for entity in order]
    if not entities or entities[-1]["kind"] != "household":
        raise BriefError("legacy brief input must end with household")
    sections: dict[str, list[dict[str, Any]]] = {}
    for section in ("news", "guidelines", "tasks"):
        converted = []
        for index, item in enumerate(value.get(section, [])):
            if not isinstance(item, Mapping):
                raise BriefError("legacy brief item is malformed")
            date = item.get("date")
            if date is not None:
                _date(date, "legacy brief date")
            converted.append({"entity_scope": item.get("entity_scope"), "scope_display": item.get("entity_scope"), "text": item.get("text"), "received_date": date, "source_link": item.get("source_link"), "origin": "source" if section == "tasks" else None, "order": index})
        sections[section] = converted
    result = {"schema_version": 2, "window": {"start": (datetime.fromisoformat(value["window"]["end"]).date() - timedelta(days=6)).isoformat(), "end": value["window"]["end"], "timezone": "UTC"}, "entity_order": order, "entities": entities, **sections, "labels": _labels(value.get("labels")), "theme": _theme(None if not value.get("theme") else value["theme"]), "template": _default_template(), "input_hashes": dict(value.get("input_hashes", {}))}
    _validate_v2(result)
    return result


def render_brief(value: Mapping[str, Any], schema: Mapping[str, Any]) -> dict[str, bytes]:
    _valid(value, schema, "brief input")
    if value.get("schema_version") == 2:
        return _render_v2(value)
    if value.get("schema_version") == 1:
        return _render_v2(_legacy_to_v2(value))
    raise BriefError("unsupported brief input schema version")


def delivery_key(instance_id: str, operation: str, window: str, variant: str) -> str:
    if not all((instance_id, operation, window, variant)):
        raise BriefError("delivery key inputs are required")
    return "delivery-" + sha256_bytes("\0".join((instance_id, operation, window, variant)).encode())


def begin_delivery(ledger: Mapping[str, Any], *, delivery_key: str, variant: str, content: bytes, recipients_fingerprint: str, ledger_schema: Mapping[str, Any]) -> dict[str, Any]:
    _valid(ledger, ledger_schema, "delivery ledger")
    if any(entry["delivery_key"] == delivery_key for entry in ledger["entries"]):
        raise BriefError("delivery key already exists")
    entry = {"delivery_key": delivery_key, "variant": variant, "content_sha256": sha256_bytes(content), "recipients_fingerprint": recipients_fingerprint, "outcome": "pending", "provider_message_id": None, "verification": {}}
    result = {"schema_version": 1, "entries": [*(ledger["entries"]), entry]}
    _valid(result, ledger_schema, "delivery ledger")
    return result


def recover_delivery(port: DeliveryPort, ledger: Mapping[str, Any], *, delivery_key: str, content: bytes, ledger_schema: Mapping[str, Any]) -> dict[str, Any]:
    _valid(ledger, ledger_schema, "delivery ledger")
    entries = [dict(entry) for entry in ledger["entries"]]
    matches = [entry for entry in entries if entry["delivery_key"] == delivery_key]
    if len(matches) != 1:
        raise BriefError("delivery recovery requires one durable intent")
    entry = matches[0]
    if entry["outcome"] == "confirmed":
        return {"schema_version": 1, "entries": entries}
    found = port.find_delivery(content)
    if len(found) != 1:
        raise BriefError("delivery lookup is ambiguous or inconclusive")
    entry.update({"outcome": "confirmed", "provider_message_id": found[0], "verification": {"provider_message_id": found[0]}})
    result = {"schema_version": 1, "entries": entries}
    _valid(result, ledger_schema, "delivery ledger")
    return result


def confirm_delivery(port: DeliveryPort, ledger: Mapping[str, Any], *, delivery_key: str, variant: str, content: bytes, recipients_fingerprint: str, ledger_schema: Mapping[str, Any]) -> dict[str, Any]:
    pending = begin_delivery(ledger, delivery_key=delivery_key, variant=variant, content=content, recipients_fingerprint=recipients_fingerprint, ledger_schema=ledger_schema)
    message_id = port.send(content)
    entries = [dict(entry) for entry in pending["entries"]]
    entries[-1].update({"outcome": "confirmed", "provider_message_id": message_id, "verification": {"provider_message_id": message_id}})
    result = {"schema_version": 1, "entries": entries}
    _valid(result, ledger_schema, "delivery ledger")
    return result
