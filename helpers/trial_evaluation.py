"""Private-trial evidence and evaluation helpers.

These standard-library helpers perform local preparation and analysis only.
They make no provider calls, choose no trial scope, and never turn an unknown
remote effect into success or failure. Callers must keep raw inputs and outputs
inside an admitted gitignored private directory and publish only sanitized
aggregates.
"""

import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import stat


PAGE_MAX_BYTES = 65_536
COMPARISON_LIMITS = (65_536, 131_072, 262_144)

CANONICAL_ID_FIELDS = {
    "configuration": "instance_id",
    "source_account": "source_account_id",
    "entity": "entity_id",
    "topic": "topic_id",
    "membership": "membership_id",
    "email": "email_id",
    "attachment_group": "attachment_group_id",
    "ingestion_coverage": "coverage_id",
    "discovery_window": "window_id",
    "knowledge": "knowledge_id",
    "task": "task_id",
}
DERIVED_FAMILIES = {
    "record_locator", "page_catalogue", "entity_index", "topic_index",
    "incoming_relationship_index", "index_coverage",
}
_SAFE_OPERATION_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,95}\Z")


class EvaluationError(ValueError):
    """A sanitized local validation error."""


def _strict_json_bytes(value):
    try:
        return json.dumps(
            value, ensure_ascii=False, allow_nan=False,
            separators=(",", ":"),
        ).encode("utf-8", errors="strict")
    except (TypeError, ValueError, UnicodeError) as exc:
        raise EvaluationError("Value is not strict UTF-8 JSON") from exc


def _check_private_directory(directory):
    root = Path(directory)
    if root.is_symlink() or not root.is_dir():
        raise EvaluationError("Receipt sink must be a real directory")
    info = root.stat()
    if hasattr(os, "getuid") and info.st_uid != os.getuid():
        raise EvaluationError("Receipt sink must be owned by the current user")
    if stat.S_IMODE(info.st_mode) & 0o077:
        raise EvaluationError("Receipt sink must not grant group or world access")
    return root


def preflight_private_receipt_sink(directory):
    """Create/check an owner-only sink and verify synthetic write/read/delete.

    The caller must first choose a path covered by the repository's admitted
    private ignore rule. This function does not inspect Git or dispatch any
    provider operation.
    """
    root = Path(directory)
    if root.exists():
        root = _check_private_directory(root)
    else:
        root.mkdir(mode=0o700, parents=True)
        root = _check_private_directory(root)
    probe = root / (".receipt-preflight-" + secrets.token_hex(12))
    payload = secrets.token_bytes(48)
    descriptor = None
    try:
        descriptor = os.open(probe, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "wb") as handle:
            descriptor = None
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        if stat.S_IMODE(probe.stat().st_mode) & 0o077:
            raise EvaluationError("Synthetic receipt was not owner-only")
        if probe.read_bytes() != payload:
            raise EvaluationError("Synthetic receipt readback differed")
    finally:
        if descriptor is not None:
            os.close(descriptor)
        try:
            probe.unlink()
        except FileNotFoundError:
            pass
    return {"status": "ready", "owner_only": True, "write_read_delete": "verified"}


def save_private_receipt(directory, operation_id, payload):
    """Exclusively save and read back one complete raw receipt as mode 0600."""
    root = _check_private_directory(directory)
    if not isinstance(operation_id, str) or not _SAFE_OPERATION_ID.fullmatch(operation_id):
        raise EvaluationError("Operation ID must be a local safe token")
    if not isinstance(payload, bytes):
        raise TypeError("Receipt payload must be the exact bytes observed")
    target = root / (operation_id + ".receipt")
    descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        try:
            target.unlink()
        except FileNotFoundError:
            pass
        raise
    observed = target.read_bytes()
    if observed != payload:
        raise EvaluationError("Receipt readback differed")
    return {
        "receipt_state": "saved_verified",
        "private_path": str(target),
        "byte_count": len(observed),
        "sha256": hashlib.sha256(observed).hexdigest(),
    }


def classify_connector_observation(*, dispatch_state, provider_state, receipt_state):
    """Keep dispatch, provider response, and local receipt evidence separate."""
    allowed_dispatch = {"not_dispatched", "dispatched", "unknown"}
    allowed_provider = {
        "response_observed", "exception_observed", "no_response_observed", "unknown",
    }
    allowed_receipt = {"saved_verified", "failed", "not_attempted", "unknown"}
    if dispatch_state not in allowed_dispatch:
        raise EvaluationError("Unsupported dispatch state")
    if provider_state not in allowed_provider:
        raise EvaluationError("Unsupported provider state")
    if receipt_state not in allowed_receipt:
        raise EvaluationError("Unsupported receipt state")
    if receipt_state == "failed":
        classification = "evaluator_receipt_failure"
    elif dispatch_state == "not_dispatched":
        classification = "local_validation_or_dispatch_stop"
    elif provider_state == "exception_observed":
        classification = "provider_or_connector_exception_observed"
    elif provider_state == "no_response_observed":
        classification = "transport_no_response_observed"
    elif provider_state == "response_observed" and receipt_state == "saved_verified":
        classification = "response_preserved_pending_interpretation"
    else:
        classification = "unknown"
    return {
        "dispatch_state": dispatch_state,
        "provider_state": provider_state,
        "receipt_state": receipt_state,
        "classification": classification,
    }


def _page_ref(targets, value, origin, *, hint=False):
    if isinstance(value, str):
        targets.append({"page_id": value, "origin": origin, "hint": hint})
    else:
        raise EvaluationError("Contract page reference has an unknown shape")


def _record_ref(targets, value, origin):
    if not isinstance(value, dict) or not isinstance(value.get("family"), str) or not isinstance(value.get("id"), str):
        raise EvaluationError("Contract record reference has an unknown shape")
    targets.append({"family": value["family"], "id": value["id"], "origin": origin})
    if "page_hint" in value:
        if not isinstance(value["page_hint"], str):
            raise EvaluationError("Contract page hint has an unknown shape")
        return {"page_id": value["page_hint"], "origin": origin + ".page_hint", "hint": True}
    return None


def _list(value, label):
    if not isinstance(value, list):
        raise EvaluationError(label + " must be a complete array")
    return value


def _extract_exact_continuation(continuation, hard, origin):
    if not isinstance(continuation, dict):
        raise EvaluationError("Continuation has an unknown shape")
    if continuation == {"state": "exhausted"}:
        return
    if (
        set(continuation) == {"state", "next_page_id"}
        and continuation.get("state") == "continues"
        and isinstance(continuation.get("next_page_id"), str)
        and continuation["next_page_id"]
    ):
        _page_ref(hard, continuation["next_page_id"], origin + ".next_page_id")
        return
    raise EvaluationError(
        "Continuation must be exactly exhausted or continues with one next page"
    )


def _extract_required_continuation(page, hard):
    if "continuation" not in page:
        raise EvaluationError("Derived page requires continuation")
    _extract_exact_continuation(page["continuation"], hard, "continuation")


def _extract_record_references(family, record, origin):
    refs, hints = [], []
    def add(value, suffix):
        hint = _record_ref(refs, value, origin + suffix)
        if hint:
            hints.append(hint)
    def add_many(value, suffix):
        for index, item in enumerate(_list(value, origin + suffix)):
            add(item, suffix + "[" + str(index) + "]")

    if family == "configuration":
        add(record.get("household_entity_ref"), ".household_entity_ref")
        add_many(record.get("source_accounts"), ".source_accounts")
    elif family == "topic":
        add_many(record.get("broader_topic_refs"), ".broader_topic_refs")
    elif family == "membership":
        add(record.get("subject_ref"), ".subject_ref")
        add(record.get("container_ref"), ".container_ref")
        add_many(record.get("evidence_refs"), ".evidence_refs")
    elif family == "email":
        add(record.get("source_account_ref"), ".source_account_ref")
        add_many(record.get("association", {}).get("pending_candidate_refs"), ".association.pending_candidate_refs")
        add(record.get("coverage_ref"), ".coverage_ref")
    elif family == "attachment_group":
        add(record.get("email_ref"), ".email_ref")
        for ci, candidate in enumerate(_list(record.get("candidates"), origin + ".candidates")):
            evidence = candidate.get("ingestion_evidence", {})
            if "knowledge_refs" in evidence:
                add_many(evidence["knowledge_refs"], ".candidates[" + str(ci) + "].ingestion_evidence.knowledge_refs")
    elif family == "ingestion_coverage":
        add(record.get("email_ref"), ".email_ref")
        body = record.get("body_ingestion_evidence", {})
        if "knowledge_refs" in body:
            add_many(body["knowledge_refs"], ".body_ingestion_evidence.knowledge_refs")
        inventory = record.get("attachment_inventory", {})
        if "group_refs" in inventory:
            add_many(inventory["group_refs"], ".attachment_inventory.group_refs")
        add_many(record.get("required_attachment_group_refs"), ".required_attachment_group_refs")
    elif family == "discovery_window":
        add(record.get("source_account_ref"), ".source_account_ref")
        add_many(record.get("school_refs"), ".school_refs")
    elif family == "knowledge":
        scope = record.get("scope", {})
        add(scope.get("anchor_ref"), ".scope.anchor_ref")
        if "listed_entity_refs" in scope:
            add_many(scope["listed_entity_refs"], ".scope.listed_entity_refs")
        for ei, link in enumerate(_list(record.get("entity_links"), origin + ".entity_links")):
            add(link.get("ref"), ".entity_links[" + str(ei) + "].ref")
        topic_refs = record.get("topic_refs")
        if isinstance(topic_refs, list):
            add_many(topic_refs, ".topic_refs")
        for si, source in enumerate(_list(record.get("source_refs"), origin + ".source_refs")):
            add(source.get("email_ref"), ".source_refs[" + str(si) + "].email_ref")
            if source.get("part") == "attachment":
                add(source.get("attachment_group_ref"), ".source_refs[" + str(si) + "].attachment_group_ref")
        for ri, relation in enumerate(_list(record.get("relationships"), origin + ".relationships")):
            add(relation.get("target_ref"), ".relationships[" + str(ri) + "].target_ref")
            add_many(relation.get("evidence_refs"), ".relationships[" + str(ri) + "].evidence_refs")
    elif family == "task":
        add(record.get("scope_ref"), ".scope_ref")
        add_many(record.get("source_context_refs"), ".source_context_refs")
        add(record.get("completion_subject_ref"), ".completion_subject_ref")
        beneficiaries = record.get("beneficiary_refs")
        if isinstance(beneficiaries, list):
            add_many(beneficiaries, ".beneficiary_refs")
        add_many(record.get("supporting_knowledge_refs"), ".supporting_knowledge_refs")
        if "series_ref" in record:
            add(record["series_ref"], ".series_ref")
        reviews = record.get("parent_state", {}).get("completion_reviews", [])
        for ri, review in enumerate(_list(reviews, origin + ".parent_state.completion_reviews")):
            add_many(review.get("evidence_refs"), ".parent_state.completion_reviews[" + str(ri) + "].evidence_refs")
    return refs, hints


def _extract_page(page):
    family = page.get("family")
    hard, hints, records = [], [], []
    if family in DERIVED_FAMILIES:
        _extract_required_continuation(page, hard)
    elif "continuation" in page:
        raise EvaluationError("Canonical page cannot declare page continuation")
    if family in CANONICAL_ID_FIELDS:
        for index, record in enumerate(_list(page.get("records"), "records")):
            record_refs, record_hints = _extract_record_references(family, record, "records[" + str(index) + "]")
            records.extend(record_refs)
            hints.extend(record_hints)
            if family == "configuration":
                roots = record.get("entity_topic_roots")
                if not isinstance(roots, dict):
                    raise EvaluationError("Configuration roots have an unknown shape")
                for key in (
                    "entity_directory_page_id", "membership_directory_page_id",
                    "topic_directory_page_id", "entity_index_directory_page_id",
                    "topic_index_directory_page_id",
                    "incoming_relationship_index_directory_page_id",
                    "index_coverage_directory_page_id",
                ):
                    _page_ref(hard, roots.get(key), "records[" + str(index) + "].entity_topic_roots." + key)
            if family == "discovery_window":
                observed = record.get("observed_email_refs")
                if not isinstance(observed, dict):
                    raise EvaluationError("Discovery-window references have an unknown shape")
                for pi, value in enumerate(_list(observed.get("source_index_page_ids"), "observed_email_refs.source_index_page_ids")):
                    _page_ref(hard, value, "records[" + str(index) + "].observed_email_refs.source_index_page_ids[" + str(pi) + "]")
                if "continuation" not in observed:
                    raise EvaluationError("Discovery-window references require continuation")
                _extract_exact_continuation(
                    observed["continuation"],
                    hard,
                    "records[" + str(index) + "].observed_email_refs.continuation",
                )
    elif family == "record_locator":
        for index, entry in enumerate(_list(page.get("entries"), "entries")):
            _page_ref(hard, entry.get("page_id"), "entries[" + str(index) + "].page_id")
    elif family == "page_catalogue":
        for index, entry in enumerate(_list(page.get("entries"), "entries")):
            _page_ref(hard, entry.get("canonical_page_id"), "entries[" + str(index) + "].canonical_page_id")
    elif family in {"entity_index", "topic_index"}:
        for index, entry in enumerate(_list(page.get("entries"), "entries")):
            if "buckets" in entry:
                for bi, bucket in enumerate(_list(entry["buckets"], "entries.buckets")):
                    for pi, value in enumerate(_list(bucket.get("page_ids"), "entries.buckets.page_ids")):
                        _page_ref(hard, value, "entries[" + str(index) + "].buckets[" + str(bi) + "].page_ids[" + str(pi) + "]")
            elif "record_ref" in entry:
                hint = _record_ref(records, entry["record_ref"], "entries[" + str(index) + "].record_ref")
                if hint:
                    hints.append(hint)
            else:
                raise EvaluationError("Index entry has an unknown required shape")
    elif family == "incoming_relationship_index":
        for index, entry in enumerate(_list(page.get("entries"), "entries")):
            if "page_ids" in entry:
                for pi, value in enumerate(_list(entry["page_ids"], "entries.page_ids")):
                    _page_ref(hard, value, "entries[" + str(index) + "].page_ids[" + str(pi) + "]")
            elif "from_ref" in entry:
                hint = _record_ref(records, entry["from_ref"], "entries[" + str(index) + "].from_ref")
                if hint:
                    hints.append(hint)
            else:
                raise EvaluationError("Relationship-index entry has an unknown shape")
    elif family == "index_coverage":
        for index, entry in enumerate(_list(page.get("entries"), "entries")):
            _page_ref(hard, entry.get("canonical_page_id"), "entries[" + str(index) + "].canonical_page_id")
    else:
        raise EvaluationError("Page family is outside the approved contract")
    return hard, hints, records


def audit_contract_references(pages, root_page_ids):
    """Traverse already-read pages using only contract-defined reference fields."""
    page_map, duplicate_ids, conflicting_ids, diagnostics = {}, [], [], []
    for index, page in enumerate(_list(pages, "pages")):
        if not isinstance(page, dict) or not isinstance(page.get("page_id"), str):
            diagnostics.append({"kind": "unknown_page_shape", "page_index": index})
            continue
        page_id = page["page_id"]
        if page_id in page_map:
            duplicate_ids.append(page_id)
            if _strict_json_bytes(page_map[page_id]) != _strict_json_bytes(page):
                conflicting_ids.append(page_id)
        else:
            page_map[page_id] = page

    queue = list(_list(root_page_ids, "root_page_ids"))
    visited, hard_edges, hint_edges, record_refs = set(), {}, {}, []
    unresolved, unresolved_hints = [], []
    while queue:
        page_id = queue.pop(0)
        if page_id in visited:
            continue
        page = page_map.get(page_id)
        if page is None:
            unresolved.append({"page_id": page_id, "origin": "root_or_hard_reference"})
            continue
        visited.add(page_id)
        try:
            hard, hints, refs = _extract_page(page)
        except EvaluationError as exc:
            diagnostics.append({"kind": "unknown_required_shape", "page_id": page_id, "reason": str(exc)})
            continue
        hard_edges[page_id] = [item["page_id"] for item in hard]
        hint_edges[page_id] = [item["page_id"] for item in hints]
        record_refs.extend({**item, "from_page_id": page_id} for item in refs)
        for item in hard:
            if item["page_id"] in page_map:
                queue.append(item["page_id"])
            else:
                unresolved.append({**item, "from_page_id": page_id})
        for item in hints:
            if item["page_id"] in page_map:
                queue.append(item["page_id"])
            else:
                unresolved_hints.append({**item, "from_page_id": page_id})

    record_index = {}
    for page_id in visited:
        page = page_map[page_id]
        family = page.get("family")
        id_field = CANONICAL_ID_FIELDS.get(family)
        if not id_field:
            continue
        for record in page.get("records", []):
            if isinstance(record, dict) and isinstance(record.get(id_field), str):
                key = (family, record[id_field])
                record_index.setdefault(key, []).append(page_id)
    unresolved_records = [ref for ref in record_refs if (ref["family"], ref["id"]) not in record_index]

    cycles = []
    def visit(node, stack, active):
        if node in active:
            start = stack.index(node)
            cycles.append(stack[start:] + [node])
            return
        active.add(node)
        stack.append(node)
        for target in hard_edges.get(node, []):
            if target in visited:
                visit(target, stack, active)
        stack.pop()
        active.remove(node)
    for root in root_page_ids:
        if root in visited:
            visit(root, [], set())

    incomplete = bool(unresolved or unresolved_records or diagnostics or duplicate_ids or cycles)
    return {
        "status": "incomplete" if incomplete else "complete",
        "visited_page_ids": sorted(visited),
        "unresolved_page_references": unresolved,
        "unresolved_page_hints": unresolved_hints,
        "unresolved_record_references": unresolved_records,
        "duplicate_page_ids": sorted(set(duplicate_ids)),
        "conflicting_page_ids": sorted(set(conflicting_ids)),
        "cycles": cycles,
        "diagnostics": diagnostics,
    }


def bind_report_artifact(binding, artifact_bytes):
    """Grade a local export as task-bound, visible-output-only, or unbound."""
    if not isinstance(binding, dict) or not isinstance(artifact_bytes, bytes):
        raise TypeError("Binding must be an object and artifact must be bytes")
    task = binding.get("task_alias")
    events = binding.get("events", {})
    prompt_seen = events.get("prompt", {}).get("observed") is True
    final_seen = events.get("final_response", {}).get("observed") is True
    same_task = bool(task) and all(
        events.get(name, {}).get("task_alias") == task
        for name in ("prompt", "final_response", "export_action")
    )
    export_seen = events.get("export_action", {}).get("observed") is True
    receipt = events.get("provider_receipt", {})
    receipt_bound = receipt.get("state") == "saved_verified" and receipt.get("task_alias") == task
    expected = binding.get("artifact", {}).get("sha256")
    digest_matches = isinstance(expected, str) and hashlib.sha256(artifact_bytes).hexdigest() == expected
    if same_task and prompt_seen and final_seen and export_seen and receipt_bound and digest_matches:
        status, usable = "task_bound", "downloaded_artifact"
    elif final_seen:
        status, usable = "visible_output_only", "visible_response"
    else:
        status, usable = "unbound", "none"
    return {"status": status, "authoritative_evidence": usable, "digest_matches": digest_matches}


def evaluate_image_expectation(binding, reviewed_artifact_bytes):
    """Require independently reviewed pixels/rendering before image grading."""
    if not isinstance(binding, dict) or not isinstance(reviewed_artifact_bytes, bytes):
        raise TypeError("Binding must be an object and reviewed artifact must be bytes")
    expected = binding.get("reviewed_artifact_sha256")
    digest_matches = isinstance(expected, str) and hashlib.sha256(reviewed_artifact_bytes).hexdigest() == expected
    evidence = binding.get("visible_evidence", {})
    expectation = binding.get("expectation", {})
    exact_view = evidence.get("kind") in {"exact_pixels", "faithful_private_rendering"}
    portions = evidence.get("portions_reviewed")
    independent = (
        expectation.get("basis") == "independent_visual_review"
        and expectation.get("authored_before_tested_output") is True
        and expectation.get("tested_output_used") is False
    )
    ocr = binding.get("ocr", {})
    ocr_ok = ocr.get("used") is not True or ocr.get("label") == "derived_evidence"
    grounded = digest_matches and exact_view and isinstance(portions, list) and bool(portions) and independent and ocr_ok
    return {
        "status": "grounded" if grounded else "evaluation_limitation",
        "image_specific_finding_allowed": grounded,
        "digest_matches": digest_matches,
    }


def measure_canonical_page(raw_page_bytes):
    """Measure exact readback bytes without treating reserialization as evidence."""
    if not isinstance(raw_page_bytes, bytes):
        raise TypeError("Canonical page input must be exact bytes")
    try:
        page = json.loads(raw_page_bytes.decode("utf-8", errors="strict"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise EvaluationError("Canonical page is not valid UTF-8 JSON") from exc
    if not isinstance(page, dict):
        raise EvaluationError("Canonical page root must be an object")
    records = page.get("records", [])
    if not isinstance(records, list):
        records = []
    compact_sizes = [len(_strict_json_bytes(record)) for record in records]
    return {
        "page_bytes": len(raw_page_bytes),
        "family": page.get("family"),
        "record_count": len(records),
        "largest_compact_record_bytes": max(compact_sizes, default=0),
        "packing_percent_of_64_kib": round(len(raw_page_bytes) * 100 / PAGE_MAX_BYTES, 3),
        "within_64_kib": len(raw_page_bytes) <= PAGE_MAX_BYTES,
    }


def pack_evaluation_group(records, group_key, candidate_max_bytes):
    """Pack ordered complete records into explicitly noncanonical pages."""
    if candidate_max_bytes not in COMPARISON_LIMITS:
        raise EvaluationError("Candidate maximum must be 64, 128, or 256 KiB")
    records = _list(records, "records")
    if not isinstance(group_key, dict):
        raise TypeError("Group key must be an object")
    pages, overflows, current = [], [], []
    def encoded(items, number):
        return _strict_json_bytes({
            "evaluation_only": "noncanonical_page_size_comparison",
            "candidate_max_bytes": candidate_max_bytes,
            "group_key": group_key,
            "page_number": number,
            "records": items,
        })
    for index, record in enumerate(records):
        proposed = current + [record]
        page_number = len(pages) + 1
        if len(encoded(proposed, page_number)) <= candidate_max_bytes:
            current = proposed
            continue
        if current:
            pages.append(encoded(current, page_number))
            current = []
            page_number = len(pages) + 1
        single = encoded([record], page_number)
        if len(single) > candidate_max_bytes:
            overflows.append({"record_index": index, "required_page_bytes": len(single)})
        else:
            current = [record]
    if current:
        pages.append(encoded(current, len(pages) + 1))
    return {
        "candidate_max_bytes": candidate_max_bytes,
        "pages": pages,
        "page_byte_counts": [len(page) for page in pages],
        "record_count": len(records),
        "packed_record_count": sum(len(json.loads(page)["records"]) for page in pages),
        "overflows": overflows,
    }


def compare_page_candidates(records, group_key):
    """Prepare matched 64/128/256 KiB noncanonical candidates."""
    return {
        str(limit): pack_evaluation_group(records, group_key, limit)
        for limit in COMPARISON_LIMITS
    }
