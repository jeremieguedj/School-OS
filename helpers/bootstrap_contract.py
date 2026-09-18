"""Pure validation for a finite School-OS bootstrap readback.

The caller chooses the temporary route manifest and supplies the exact bytes
already read back from storage.  This module performs no I/O and retains no
state.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any


SUPPORTED_SCHEMA_VERSIONS = frozenset({"1"})
MAX_PAGE_BYTES = 65_536
MAX_ENTRIES = 100

CANONICAL_FAMILIES = frozenset(
    {
        "configuration",
        "source_account",
        "entity",
        "topic",
        "membership",
        "email",
        "attachment_group",
        "ingestion_coverage",
        "discovery_window",
        "knowledge",
        "task",
    }
)
DERIVED_FAMILIES = frozenset(
    {
        "record_locator",
        "page_catalogue",
        "entity_index",
        "topic_index",
        "incoming_relationship_index",
        "index_coverage",
    }
)
APPROVED_FAMILIES = CANONICAL_FAMILIES | DERIVED_FAMILIES
SOURCE_ROUTED_FAMILIES = frozenset(
    {"email", "attachment_group", "ingestion_coverage", "knowledge"}
)
ROOT_FIELDS = {
    "entity_directory_page_id": ("record_locator", {"canonical_family": "entity"}),
    "membership_directory_page_id": (
        "record_locator",
        {"canonical_family": "membership"},
    ),
    "topic_directory_page_id": ("record_locator", {"canonical_family": "topic"}),
    "entity_index_directory_page_id": (
        "entity_index",
        {"directory_key": "entity_index_root"},
    ),
    "topic_index_directory_page_id": (
        "topic_index",
        {"directory_key": "topic_index_root"},
    ),
    "incoming_relationship_index_directory_page_id": (
        "incoming_relationship_index",
        {"directory_key": "incoming_relationship_index_root"},
    ),
    "index_coverage_directory_page_id": ("index_coverage", {}),
}
_MONTH_RE = re.compile(r"^[0-9]{4}-(0[1-9]|1[0-2])$")


class _DuplicateKey(ValueError):
    pass


def _object_without_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKey("duplicate JSON object key")
        result[key] = value
    return result


@dataclass(frozen=True)
class _Reference:
    source_page_id: str
    target_page_id: str
    path: str
    expected_family: str | None = None
    expected_selector: Mapping[str, Any] | None = None


class _Diagnostics:
    def __init__(self) -> None:
        self.items: list[dict[str, str]] = []
        self.has_invalid = False
        self.has_insufficient = False

    def add(self, status: str, code: str, path: str, message: str) -> None:
        if status == "invalid":
            self.has_invalid = True
        else:
            self.has_insufficient = True
        self.items.append(
            {"status": status, "code": code, "path": path, "message": message}
        )

    def result(self) -> dict[str, object]:
        status = (
            "invalid"
            if self.has_invalid
            else "insufficient_evidence"
            if self.has_insufficient
            else "valid"
        )
        return {
            "status": status,
            "diagnostics": sorted(
                self.items,
                key=lambda item: (
                    item["status"],
                    item["code"],
                    item["path"],
                    item["message"],
                ),
            ),
        }


def _contains_null(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, list):
        return any(_contains_null(item) for item in value)
    if isinstance(value, dict):
        return any(_contains_null(item) for item in value.values())
    return False


def _selector(page: Mapping[str, Any]) -> dict[str, Any]:
    for key in ("locator_key", "route", "directory_key", "index_key"):
        if key in page:
            return {key: page[key]}
    return {}


def _valid_expected(expected: Any) -> bool:
    if not isinstance(expected, dict) or not isinstance(expected.get("family"), str):
        return False
    family = expected["family"]
    if family not in APPROVED_FAMILIES:
        return False
    selector_keys = set(expected) - {"family"}
    permitted: set[str]
    if family == "record_locator":
        permitted = {"locator_key"}
    elif family == "page_catalogue":
        permitted = {"route"}
    elif family in {"entity_index", "topic_index", "incoming_relationship_index"}:
        permitted = {"directory_key", "index_key"}
    else:
        permitted = set()
    return len(selector_keys) <= 1 and selector_keys <= permitted


def _continuation_target(
    continuation: Any, path: str, diagnostics: _Diagnostics
) -> str | None:
    if not isinstance(continuation, dict):
        diagnostics.add("invalid", "invalid_continuation", path, "continuation must be an object")
        return None
    if continuation == {"state": "exhausted"}:
        return None
    if (
        set(continuation) == {"state", "next_page_id"}
        and continuation.get("state") == "continues"
        and isinstance(continuation.get("next_page_id"), str)
        and continuation["next_page_id"]
    ):
        return continuation["next_page_id"]
    diagnostics.add(
        "invalid",
        "invalid_continuation",
        path,
        "continuation must be exhausted or name one next page",
    )
    return None


def _validate_continuation(
    page: Mapping[str, Any], page_id: str, diagnostics: _Diagnostics
) -> str | None:
    return _continuation_target(
        page.get("continuation"), f"pages.{page_id}.continuation", diagnostics
    )


def _required_string(
    value: Any, path: str, code: str, message: str, diagnostics: _Diagnostics
) -> str | None:
    if not isinstance(value, str) or not value:
        diagnostics.add("invalid", code, path, message)
        return None
    return value


def _validate_family_shape(
    page: Mapping[str, Any], page_id: str, diagnostics: _Diagnostics
) -> None:
    family = page.get("family")
    path = f"pages.{page_id}"
    if family in CANONICAL_FAMILIES:
        if not isinstance(page.get("records"), list):
            diagnostics.add("invalid", "missing_records", path, "canonical page requires records")
        if "entries" in page or "continuation" in page:
            diagnostics.add(
                "invalid",
                "canonical_page_has_directory_fields",
                path,
                "canonical page cannot use directory entries or continuation",
            )
        return

    entries = page.get("entries")
    if not isinstance(entries, list):
        diagnostics.add("invalid", "missing_entries", path, "derived page requires entries")
    elif len(entries) > MAX_ENTRIES:
        diagnostics.add(
            "invalid",
            "entry_limit_exceeded",
            f"{path}.entries",
            "page contains more than 100 entries",
        )
    if "records" in page:
        diagnostics.add("invalid", "derived_page_has_records", path, "derived page cannot use records")
    _validate_continuation(page, page_id, diagnostics)

    if family == "record_locator":
        key = page.get("locator_key")
        if (
            not isinstance(key, dict)
            or set(key) != {"canonical_family"}
            or key.get("canonical_family") not in CANONICAL_FAMILIES
        ):
            diagnostics.add(
                "invalid", "invalid_locator_key", f"{path}.locator_key", "locator key must name a canonical family"
            )
    elif family == "page_catalogue":
        route = page.get("route")
        if not isinstance(route, dict):
            diagnostics.add("invalid", "invalid_catalogue_route", f"{path}.route", "catalogue route must be an object")
        else:
            canonical_family = route.get("canonical_family")
            source_month = route.get("source_month")
            valid_month = source_month == "pending" or (
                isinstance(source_month, str) and _MONTH_RE.fullmatch(source_month)
            )
            if (
                set(route) != {"canonical_family", "source_account_id", "source_month"}
                or canonical_family not in SOURCE_ROUTED_FAMILIES
                or not isinstance(route.get("source_account_id"), str)
                or not route.get("source_account_id")
                or not valid_month
            ):
                diagnostics.add(
                    "invalid",
                    "invalid_catalogue_route",
                    f"{path}.route",
                    "catalogue route must name an approved source family, account, and month or pending route",
                )
    elif family == "entity_index":
        if page.get("directory_key") != "entity_index_root" and not isinstance(page.get("index_key"), dict):
            diagnostics.add("invalid", "invalid_index_key", path, "entity index requires its root or index key")
    elif family == "topic_index":
        if page.get("directory_key") != "topic_index_root" and not isinstance(page.get("index_key"), dict):
            diagnostics.add("invalid", "invalid_index_key", path, "topic index requires its root or index key")
    elif family == "incoming_relationship_index":
        if page.get("directory_key") != "incoming_relationship_index_root" and not isinstance(page.get("index_key"), dict):
            diagnostics.add("invalid", "invalid_index_key", path, "incoming relationship index requires its root or index key")
    elif family == "index_coverage" and _selector(page):
        diagnostics.add("invalid", "unexpected_route_key", path, "index coverage has no route key")


def _page_references(
    page: Mapping[str, Any], diagnostics: _Diagnostics
) -> list[_Reference]:
    page_id = page["page_id"]
    family = page["family"]
    references: list[_Reference] = []
    continuation = page.get("continuation")
    if isinstance(continuation, dict) and continuation.get("state") == "continues":
        target = continuation.get("next_page_id")
        if isinstance(target, str):
            references.append(
                _Reference(page_id, target, "continuation.next_page_id", family, _selector(page))
            )

    if family == "configuration":
        records = page.get("records") if isinstance(page.get("records"), list) else []
        if len(records) != 1:
            diagnostics.add(
                "invalid",
                "invalid_configuration_record_count",
                f"pages.{page_id}.records",
                "configuration page must contain exactly one configuration record",
            )
        for record_number, record in enumerate(records):
            record_path = f"pages.{page_id}.records[{record_number}]"
            if not isinstance(record, dict):
                diagnostics.add(
                    "invalid",
                    "invalid_configuration_record",
                    record_path,
                    "configuration record must be an object",
                )
                continue
            roots = record.get("entity_topic_roots") if isinstance(record, dict) else None
            if not isinstance(roots, dict):
                diagnostics.add(
                    "invalid",
                    "invalid_configuration_roots",
                    f"{record_path}.entity_topic_roots",
                    "configuration requires an entity_topic_roots object",
                )
                continue
            for field, (expected_family, selector) in ROOT_FIELDS.items():
                target = _required_string(
                    roots.get(field),
                    f"{record_path}.entity_topic_roots.{field}",
                    "invalid_configuration_root",
                    "required configuration root must be a non-empty page ID string",
                    diagnostics,
                )
                if target is None:
                    continue
                expected_selector = (
                    {"locator_key": selector}
                    if expected_family == "record_locator"
                    else selector
                )
                references.append(
                    _Reference(
                        page_id,
                        target,
                        f"records[{record_number}].entity_topic_roots.{field}",
                        expected_family,
                        expected_selector,
                    )
                )
    elif family == "record_locator":
        canonical_family = page.get("locator_key", {}).get("canonical_family")
        entries = page.get("entries") if isinstance(page.get("entries"), list) else []
        for number, entry in enumerate(entries):
            entry_path = f"pages.{page_id}.entries[{number}]"
            if not isinstance(entry, dict):
                diagnostics.add("invalid", "invalid_locator_entry", entry_path, "locator entry must be an object")
                continue
            _required_string(
                entry.get("record_id"),
                f"{entry_path}.record_id",
                "invalid_locator_record_id",
                "locator record_id must be a non-empty string",
                diagnostics,
            )
            target = _required_string(
                entry.get("page_id"),
                f"{entry_path}.page_id",
                "invalid_locator_target",
                "locator page_id must be a non-empty string",
                diagnostics,
            )
            if target is not None:
                references.append(
                    _Reference(page_id, target, f"entries[{number}].page_id", canonical_family, {})
                )
    elif family == "page_catalogue":
        canonical_family = page.get("route", {}).get("canonical_family")
        entries = page.get("entries") if isinstance(page.get("entries"), list) else []
        for number, entry in enumerate(entries):
            entry_path = f"pages.{page_id}.entries[{number}]"
            if not isinstance(entry, dict):
                diagnostics.add("invalid", "invalid_catalogue_entry", entry_path, "catalogue entry must be an object")
                continue
            target = _required_string(
                entry.get("canonical_page_id"),
                f"{entry_path}.canonical_page_id",
                "invalid_catalogue_target",
                "catalogue canonical_page_id must be a non-empty string",
                diagnostics,
            )
            if entry.get("canonical_family") != canonical_family:
                diagnostics.add(
                    "invalid",
                    "invalid_catalogue_target_family",
                    f"{entry_path}.canonical_family",
                    "catalogue entry family must match its route",
                )
            revision = entry.get("content_revision")
            if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
                diagnostics.add(
                    "invalid",
                    "invalid_catalogue_target_revision",
                    f"{entry_path}.content_revision",
                    "catalogue target revision must be a positive integer",
                )
            _required_string(
                entry.get("drive_access_aid"),
                f"{entry_path}.drive_access_aid",
                "invalid_catalogue_access_aid",
                "catalogue drive_access_aid must be a non-empty string",
                diagnostics,
            )
            if target is not None:
                references.append(
                    _Reference(
                        page_id,
                        target,
                        f"entries[{number}].canonical_page_id",
                        canonical_family,
                        {},
                    )
                )
    elif family in {"entity_index", "topic_index"} and "directory_key" in page:
        entries = page.get("entries") if isinstance(page.get("entries"), list) else []
        for entry_number, entry in enumerate(entries):
            entry_path = f"pages.{page_id}.entries[{entry_number}]"
            if not isinstance(entry, dict):
                diagnostics.add("invalid", "invalid_index_directory_entry", entry_path, "index directory entry must be an object")
                continue
            lookup_id = _required_string(
                entry.get("lookup_id"),
                f"{entry_path}.lookup_id",
                "invalid_index_lookup_id",
                "index lookup_id must be a non-empty string",
                diagnostics,
            )
            buckets = entry.get("buckets")
            if not isinstance(buckets, list):
                diagnostics.add("invalid", "invalid_index_buckets", f"{entry_path}.buckets", "index buckets must be an array")
                continue
            for bucket_number, bucket in enumerate(buckets):
                bucket_path = f"{entry_path}.buckets[{bucket_number}]"
                if not isinstance(bucket, dict):
                    diagnostics.add("invalid", "invalid_index_bucket", bucket_path, "index bucket must be an object")
                    continue
                time_bucket = _required_string(
                    bucket.get("time_bucket"),
                    f"{bucket_path}.time_bucket",
                    "invalid_index_time_bucket",
                    "index time_bucket must be a non-empty string",
                    diagnostics,
                )
                page_ids = bucket.get("page_ids")
                if not isinstance(page_ids, list):
                    diagnostics.add("invalid", "invalid_index_targets", f"{bucket_path}.page_ids", "index page_ids must be an array")
                    continue
                key_name = "entity_id" if family == "entity_index" else "topic_id"
                expected = {"index_key": {key_name: lookup_id, "time_bucket": time_bucket}}
                for page_number, value in enumerate(page_ids):
                    target = _required_string(
                        value,
                        f"{bucket_path}.page_ids[{page_number}]",
                        "invalid_index_target",
                        "index target must be a non-empty page ID string",
                        diagnostics,
                    )
                    if target is not None:
                        references.append(
                            _Reference(
                                page_id,
                                target,
                                f"entries[{entry_number}].buckets[{bucket_number}].page_ids[{page_number}]",
                                family,
                                expected,
                            )
                        )
    elif family == "incoming_relationship_index" and "directory_key" in page:
        entries = page.get("entries") if isinstance(page.get("entries"), list) else []
        for entry_number, entry in enumerate(entries):
            entry_path = f"pages.{page_id}.entries[{entry_number}]"
            if not isinstance(entry, dict):
                diagnostics.add("invalid", "invalid_index_directory_entry", entry_path, "index directory entry must be an object")
                continue
            target_knowledge_id = _required_string(
                entry.get("target_knowledge_id"),
                f"{entry_path}.target_knowledge_id",
                "invalid_index_lookup_id",
                "target_knowledge_id must be a non-empty string",
                diagnostics,
            )
            page_ids = entry.get("page_ids")
            if not isinstance(page_ids, list):
                diagnostics.add("invalid", "invalid_index_targets", f"{entry_path}.page_ids", "index page_ids must be an array")
                continue
            expected = {"index_key": {"target_knowledge_id": target_knowledge_id}}
            for page_number, value in enumerate(page_ids):
                target = _required_string(
                    value,
                    f"{entry_path}.page_ids[{page_number}]",
                    "invalid_index_target",
                    "index target must be a non-empty page ID string",
                    diagnostics,
                )
                if target is not None:
                    references.append(
                        _Reference(
                            page_id,
                            target,
                            f"entries[{entry_number}].page_ids[{page_number}]",
                            family,
                            expected,
                        )
                    )
    elif family == "index_coverage":
        entries = page.get("entries") if isinstance(page.get("entries"), list) else []
        for number, entry in enumerate(entries):
            entry_path = f"pages.{page_id}.entries[{number}]"
            if not isinstance(entry, dict):
                diagnostics.add("invalid", "invalid_index_coverage_entry", entry_path, "index coverage entry must be an object")
                continue
            target = _required_string(
                entry.get("canonical_page_id"),
                f"{entry_path}.canonical_page_id",
                "invalid_index_target",
                "index coverage target must be a non-empty page ID string",
                diagnostics,
            )
            expected_family = entry.get("canonical_family")
            if expected_family not in CANONICAL_FAMILIES:
                diagnostics.add("invalid", "invalid_index_target_family", f"{entry_path}.canonical_family", "index coverage must name a canonical family")
            if target is not None:
                references.append(
                    _Reference(page_id, target, f"entries[{number}].canonical_page_id", expected_family, {})
                )
    elif family == "discovery_window":
        records = page.get("records") if isinstance(page.get("records"), list) else []
        for record_number, record in enumerate(records):
            record_path = f"pages.{page_id}.records[{record_number}]"
            if not isinstance(record, dict):
                diagnostics.add("invalid", "invalid_discovery_window_record", record_path, "Discovery Window record must be an object")
                continue
            observed = record.get("observed_email_refs") if isinstance(record, dict) else None
            if not isinstance(observed, dict):
                diagnostics.add("invalid", "invalid_observed_email_refs", f"{record_path}.observed_email_refs", "Discovery Window requires observed_email_refs")
                continue
            page_ids = observed.get("source_index_page_ids")
            if not isinstance(page_ids, list):
                diagnostics.add("invalid", "invalid_observed_email_targets", f"{record_path}.observed_email_refs.source_index_page_ids", "source_index_page_ids must be an array")
            else:
                for page_number, value in enumerate(page_ids):
                    target = _required_string(
                        value,
                        f"{record_path}.observed_email_refs.source_index_page_ids[{page_number}]",
                        "invalid_observed_email_target",
                        "observed Email target must be a non-empty page ID string",
                        diagnostics,
                    )
                    if target is None:
                        continue
                    references.append(
                        _Reference(
                            page_id,
                            target,
                            f"records[{record_number}].observed_email_refs.source_index_page_ids[{page_number}]",
                            "record_locator",
                            {"locator_key": {"canonical_family": "email"}},
                        )
                    )
            continuation_target = _continuation_target(
                observed.get("continuation"),
                f"{record_path}.observed_email_refs.continuation",
                diagnostics,
            )
            if continuation_target is not None:
                references.append(
                    _Reference(
                        page_id,
                        continuation_target,
                        f"records[{record_number}].observed_email_refs.continuation.next_page_id",
                        "record_locator",
                        {"locator_key": {"canonical_family": "email"}},
                    )
                )
    return references


def check_bootstrap(
    contract_revision: str,
    instance_id: str,
    manifest: Mapping[str, object],
    page_bytes: Iterable[bytes],
) -> dict[str, object]:
    """Validate one caller-selected finite bootstrap readback.

    ``manifest`` has ``routes`` containing ``role``, ``root_page_id``, and an
    ``expected`` object.  ``expected`` contains ``family`` and, for routed
    families, the exact ``locator_key``, ``route``, ``directory_key``, or
    ``index_key`` expected on that root.  The return value has ``status`` equal
    to ``valid``, ``invalid``, or ``insufficient_evidence`` and deterministic
    structured ``diagnostics``.
    """

    diagnostics = _Diagnostics()
    if not isinstance(contract_revision, str) or not contract_revision:
        diagnostics.add("insufficient_evidence", "missing_contract_revision", "contract_revision", "contract revision is required")
    elif contract_revision not in SUPPORTED_SCHEMA_VERSIONS:
        diagnostics.add("insufficient_evidence", "unsupported_contract_revision", "contract_revision", "this helper does not support the requested contract revision")
    if not isinstance(instance_id, str) or not instance_id:
        diagnostics.add("insufficient_evidence", "missing_instance_id", "instance_id", "instance identity is required")

    routes = manifest.get("routes") if isinstance(manifest, Mapping) else None
    if not isinstance(routes, list) or not routes:
        diagnostics.add("insufficient_evidence", "invalid_manifest", "manifest.routes", "finite route manifest is required")
        routes = []

    parsed_pages: dict[str, dict[str, Any]] = {}
    raw_by_page_id: dict[str, bytes] = {}
    try:
        supplied_blobs = list(page_bytes)
    except TypeError:
        supplied_blobs = []
        diagnostics.add("insufficient_evidence", "invalid_page_bytes", "page_bytes", "page bytes must be iterable")

    for number, raw in enumerate(supplied_blobs):
        path = f"page_bytes[{number}]"
        if not isinstance(raw, bytes):
            diagnostics.add("insufficient_evidence", "non_bytes_readback", path, "readback must be exact bytes")
            continue
        if len(raw) > MAX_PAGE_BYTES:
            diagnostics.add("invalid", "page_size_exceeded", path, "encoded page exceeds 65,536 bytes")
        try:
            text = raw.decode("utf-8", "strict")
            page = json.loads(text, object_pairs_hook=_object_without_duplicate_keys)
        except UnicodeDecodeError:
            diagnostics.add("invalid", "invalid_utf8", path, "page is not strict UTF-8")
            continue
        except _DuplicateKey:
            diagnostics.add("invalid", "duplicate_json_key", path, "page contains a duplicate JSON object key")
            continue
        except json.JSONDecodeError:
            diagnostics.add("invalid", "invalid_json", path, "page is not valid JSON")
            continue
        if not isinstance(page, dict):
            diagnostics.add("invalid", "invalid_page_shape", path, "page must be a JSON object")
            continue
        page_id = page.get("page_id")
        if not isinstance(page_id, str) or not page_id:
            diagnostics.add("invalid", "missing_page_id", path, "page_id must be a non-empty string")
            continue
        if page_id in parsed_pages:
            code = "duplicate_page_id" if raw == raw_by_page_id[page_id] else "conflicting_page_id"
            diagnostics.add("invalid", code, f"pages.{page_id}", "page_id appears more than once")
            continue
        parsed_pages[page_id] = page
        raw_by_page_id[page_id] = raw

    for page_id, page in parsed_pages.items():
        path = f"pages.{page_id}"
        if page.get("instance_id") != instance_id:
            diagnostics.add("invalid", "instance_id_mismatch", f"{path}.instance_id", "page instance does not match expected instance")
        if page.get("schema_version") != contract_revision:
            diagnostics.add("invalid", "schema_version_mismatch", f"{path}.schema_version", "page schema does not match expected revision")
        if page.get("family") not in APPROVED_FAMILIES:
            diagnostics.add("invalid", "unknown_family", f"{path}.family", "page family is not approved")
            continue
        revision = page.get("content_revision")
        if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
            diagnostics.add("invalid", "invalid_content_revision", f"{path}.content_revision", "content revision must be a positive integer")
        if _contains_null(page):
            diagnostics.add("invalid", "null_value", path, "canonical and routing pages cannot contain null")
        _validate_family_shape(page, page_id, diagnostics)

    roots: list[str] = []
    seen_roles: set[str] = set()
    for number, route in enumerate(routes):
        path = f"manifest.routes[{number}]"
        if not isinstance(route, dict):
            diagnostics.add("insufficient_evidence", "invalid_manifest_route", path, "manifest route must be an object")
            continue
        role = route.get("role")
        root_page_id = route.get("root_page_id")
        expected = route.get("expected")
        if not isinstance(role, str) or not role or role in seen_roles:
            diagnostics.add("insufficient_evidence", "invalid_manifest_role", f"{path}.role", "role must be a unique non-empty string")
        else:
            seen_roles.add(role)
        if not isinstance(root_page_id, str) or not root_page_id:
            diagnostics.add("insufficient_evidence", "invalid_manifest_root", f"{path}.root_page_id", "root page ID is required")
            continue
        roots.append(root_page_id)
        if not _valid_expected(expected):
            diagnostics.add("insufficient_evidence", "invalid_manifest_expectation", f"{path}.expected", "expected family and route key are required")
            continue
        page = parsed_pages.get(root_page_id)
        if page is None:
            diagnostics.add("insufficient_evidence", "missing_root_readback", f"{path}.root_page_id", "manifest root was not supplied")
            continue
        if page.get("family") != expected["family"]:
            diagnostics.add("invalid", "manifest_family_mismatch", path, "root family differs from the finite manifest")
        expected_selector = {key: value for key, value in expected.items() if key != "family"}
        if _selector(page) != expected_selector:
            diagnostics.add("invalid", "manifest_route_mismatch", path, "root route key differs from the finite manifest")

    references: list[_Reference] = []
    for page in parsed_pages.values():
        references.extend(_page_references(page, diagnostics))
    edges: dict[str, list[str]] = {page_id: [] for page_id in parsed_pages}
    for reference in references:
        target = parsed_pages.get(reference.target_page_id)
        reference_path = f"pages.{reference.source_page_id}.{reference.path}"
        if target is None:
            diagnostics.add("insufficient_evidence", "missing_referenced_readback", reference_path, "referenced page was not supplied")
            continue
        edges[reference.source_page_id].append(reference.target_page_id)
        if reference.expected_family and target.get("family") != reference.expected_family:
            diagnostics.add("invalid", "referenced_family_mismatch", reference_path, "referenced page has the wrong family")
        if reference.expected_selector is not None and _selector(target) != dict(reference.expected_selector):
            diagnostics.add("invalid", "referenced_route_mismatch", reference_path, "referenced page has the wrong route key")

    reachable: set[str] = set()

    def visit(page_id: str) -> None:
        if page_id in reachable or page_id not in parsed_pages:
            return
        reachable.add(page_id)
        for target in edges.get(page_id, []):
            visit(target)

    for root in roots:
        visit(root)
    for page_id in sorted(set(parsed_pages) - reachable):
        diagnostics.add("invalid", "unmanifested_page", f"pages.{page_id}", "supplied page is not reachable from a manifest root")

    state: dict[str, int] = {}

    def detect_cycle(page_id: str) -> None:
        state[page_id] = 1
        for target in edges.get(page_id, []):
            if state.get(target) == 1:
                diagnostics.add("invalid", "page_reference_cycle", f"pages.{page_id}", "page-reference graph contains a cycle")
            elif state.get(target, 0) == 0:
                detect_cycle(target)
        state[page_id] = 2

    for root in roots:
        if root in parsed_pages and state.get(root, 0) == 0:
            detect_cycle(root)
    return diagnostics.result()
