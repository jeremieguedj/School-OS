#!/usr/bin/env python3
"""Evaluate private live observations; write only aggregate, non-source outputs.

No live tools are called here. Provider identities are a separate private
snapshot grading reference, never model inputs. Default output is stdout with
aggregate counts only. A private detailed audit binds every trial to observations.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import copy
from datetime import datetime, timezone
import hashlib
import itertools
import json
import os
from pathlib import Path
import random
import sys

from model import addresses, decode_subject, flattened_recipients, flattened_sender, record, related, resolve, source_date, sufficient, time_range

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def private_write(path, value):
    descriptor = os.open(str(path), os.O_CREAT | os.O_TRUNC | os.O_WRONLY, 0o600)
    with os.fdopen(descriptor, "w") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")
    os.chmod(str(path), 0o600)


def normalize(row, account_verified):
    senders = addresses(row.get("sender_raw")) if row["source_route"] == "metadata" else None
    sender = (senders[0] if senders and len(senders) == 1 else None) if row["source_route"] == "metadata" else flattened_sender(row.get("sender_raw"))
    recipients = addresses if row["source_route"] == "metadata" else flattened_recipients
    # Only a source Date header has established sent semantics in this study.
    # Neither observed search equality nor Gmail internal_date supplies receipt
    # semantics or a substitute sent time to the matcher.
    sent = source_date(row.get("sent_raw")) if row.get("sent_semantics") == "rfc_date" else None
    return {"account": row.get("mailbox"), "account_verified": account_verified,
            "subject": decode_subject(row.get("subject")),
            "sender": sender,
            "sent": sent, "received": None,
            "to": recipients(row.get("to_raw")), "cc": recipients(row.get("cc_raw")),
            # Exposed search lists have unknown complete/original scope. Retain
            # those observations for separate diagnostics, not identity evidence.
            "filenames": None, "filename_scope": None, "filenames_complete": False}


def grade(status, intended_record=None, reference_ids=None):
    if status["status"] == "metadata_association":
        return "correct_association" if intended_record in status["record_ids"] else "wrong_association"
    if status["status"] == "new_observation":
        return "correct_distinct" if intended_record is None else "false_split"
    return "abstention"


def parse_observed_time(value):
    """Diagnostic equality only; assigns no timestamp semantics to a witness."""
    if value is None:
        return None
    try:
        string = str(value)
        if string.replace(".", "", 1).isdigit():
            number = float(string)
            return number / 1000 if number > 100000000000 else number
        parsed = datetime.fromisoformat(string.replace("Z", "+00:00"))
        return parsed.timestamp() if parsed.tzinfo is not None else None
    except (ValueError, OverflowError, TypeError):
        return None


def collision_counts(rows, key):
    groups = defaultdict(set)
    for source, row in rows:
        value = key(row)
        if value is not None:
            groups[value].add(source)
    repeated = [values for values in groups.values() if len(values) > 1]
    return {"groups_with_multiple_reference_messages": len(repeated),
            "reference_messages_in_collision_groups": sum(map(len, repeated)),
            "distinct_message_pairs_in_collision_groups": sum(len(x) * (len(x)-1)//2 for x in repeated)}


def run(root):
    observations_path, oracle_path = root / "observations.json", root / "oracle.json"
    observations = json.loads(observations_path.read_text())
    oracle = json.loads(oracle_path.read_text())
    assert isinstance(observations, list) and isinstance(oracle, dict)
    # This run's collector verifies its one connected account with get_profile.
    verified_path = root / "account-verified.json"
    verified = json.loads(verified_path.read_text())["account_verified"] is True
    by_id = {row["observation_id"]: row for row in observations}
    normalized = {name: normalize(row, verified) for name, row in by_id.items()}
    first_metadata, first_search = {}, {}
    metadata_observations, search_observations = [], []
    for row in observations:
        name = row["observation_id"]
        provider = oracle[name]["provider_message_id"]
        if row["source_route"] == "metadata":
            first_metadata.setdefault(provider, name)
            metadata_observations.append(name)
        elif row["source_route"] == "search":
            first_search.setdefault(provider, name)
            search_observations.append(name)
    own_ids = {provider: "source-" + str(i+1) for i, provider in enumerate(first_metadata)}
    catalog = [record(own_ids[provider], normalized[name]) for provider, name in first_metadata.items()]
    audit, metrics = [], defaultdict(Counter)

    def trial(profile, incoming, records, expected, observation=None, complete=True):
        before = copy.deepcopy(records)
        answer = resolve(incoming, records, complete)
        assert records == before, "Matcher mutated its input catalog"
        result = grade(answer, expected)
        metrics[profile][result] += 1
        audit.append({"profile": profile, "observation_id": observation,
                      "result": answer, "grade": result, "expected_record": expected})
        return answer

    for name in metadata_observations:
        provider = oracle[name]["provider_message_id"]
        profile = "live_first_metadata_self_replay" if first_metadata[provider] == name else "live_repeat_metadata_read"
        trial(profile, normalized[name], catalog, own_ids[provider], name)
    paired_search = [name for name in search_observations if oracle[name]["provider_message_id"] in own_ids]
    for name in paired_search:
        trial("live_search_against_header_catalog", normalized[name], catalog,
              own_ids[oracle[name]["provider_message_id"]], name)
    for provider, name in first_metadata.items():
        held_out = [entry for entry in catalog if entry["record_id"] != own_ids[provider]]
        trial("live_distinct_message_leave_one_out", normalized[name], held_out, None, name)

    # Negative pairs include actual same-subject/sender/time near-neighbours;
    # all-pairs metrics are not interpreted as independent population trials.
    pair_counts, hard_counts = Counter(), Counter()
    for (pa, a), (pb, b) in itertools.combinations(first_metadata.items(), 2):
        result = resolve(normalized[a], [record(own_ids[pb], normalized[b])])
        outcome = grade(result, None)
        pair_counts[outcome] += 1
        if (normalized[a]["subject"], normalized[a]["sender"]) == (normalized[b]["subject"], normalized[b]["sender"]):
            hard_counts[outcome] += 1

    # Stress profiles are deliberately modified observations of real source
    # metadata. They are not observed connector defects or additional live reads.
    mutation_counts = Counter()
    for provider, name in first_metadata.items():
        base = normalized[name]
        if not sufficient(base):
            mutation_counts["base_not_eligible"] += 1
            continue
        expected = own_ids[provider]
        variants = {}
        changed = copy.deepcopy(base)
        changed["to"] = list(reversed(changed["to"])) if changed["to"] is not None else None
        changed["cc"] = list(reversed(changed["cc"])) if changed["cc"] is not None else None
        variants["recipient_order"] = changed
        changed = copy.deepcopy(base)
        changed.update(to=None, cc=None, filenames=None, filenames_complete=False)
        variants["optional_fields_absent"] = changed
        for precision in ("minute", "day"):
            changed = copy.deepcopy(base)
            span = time_range(base.get("sent"), "sent")
            if span is None:
                continue
            date = datetime.fromtimestamp(span[0], timezone.utc)
            date = date.replace(second=0, microsecond=0) if precision == "minute" else date.replace(hour=0, minute=0, second=0, microsecond=0)
            changed["sent"] = {"value": date.isoformat(), "precision": precision, "meaning": "sent", "zone_known": True}
            variants["sent_rounded_" + precision] = changed
        for variant in ("unknown_zone", "malformed_time", "unknown_time_meaning"):
            changed = copy.deepcopy(base)
            if changed["sent"] is None:
                continue
            if variant == "unknown_zone": changed["sent"]["zone_known"] = False
            if variant == "malformed_time": changed["sent"]["value"] = "not-a-date"
            if variant == "unknown_time_meaning": changed["sent"]["meaning"] = "unknown"
            variants[variant] = changed
        for profile, changed in variants.items():
            trial("injected_" + profile, changed, catalog, expected, name)
            mutation_counts[profile] += 1
        trial("injected_incomplete_lookup", base, catalog, expected, name, complete=False)
        # Deliberately expose two catalog records with identical allowed metadata.
        trial("injected_visible_collision", base,
              [record("collision-a", base), record("collision-b", base)], expected, name)
        # The other occurrence is hidden: same metadata, distinct grading label.
        trial("injected_hidden_collision_singleton", base, [record("collision-a", base)], None, name)

    order_equal, json_equal, ids_irrelevant = True, True, True
    shuffled = copy.deepcopy(catalog)
    random.Random(17).shuffle(shuffled)
    for name in metadata_observations:
        base = normalized[name]
        original = resolve(base, catalog)
        order_equal &= original == resolve(base, list(reversed(catalog))) == resolve(base, shuffled)
        json_equal &= original == resolve(json.loads(json.dumps(base)), json.loads(json.dumps(catalog)))
        changed = {**base, "provider_message_id": "changed", "thread_id": "changed", "rfc_id": "changed"}
        ids_irrelevant &= original == resolve(changed, catalog)

    # Independent message coverage replay, two temporal parts within the frozen
    # sample. Neither order nor provider thread references informs the resolver.
    ordered = sorted(first_metadata, key=lambda p: (
        (time_range(normalized[first_metadata[p]].get("sent"), "sent") or (float("inf"),))[0], own_ids[p]))
    boundary = len(ordered)//2
    historical, daily = ordered[:boundary], ordered[boundary:]
    historical_catalog = [record(own_ids[p], normalized[first_metadata[p]]) for p in historical]
    daily_counts, old_thread_daily = Counter(), Counter()
    earlier_threads = {oracle[first_metadata[p]].get("provider_thread_id") for p in historical}
    for provider in daily:
        name = first_metadata[provider]
        result = resolve(normalized[name], historical_catalog)
        daily_counts[grade(result, None)] += 1
        if oracle[name].get("provider_thread_id") in earlier_threads:
            old_thread_daily[grade(result, None)] += 1
        if result["status"] == "new_observation":
            historical_catalog.append(record(own_ids[provider], normalized[name]))
    resumed = json.loads(json.dumps(historical_catalog))
    daily_replay_counts = Counter()
    for provider in daily:
        daily_replay_counts[grade(resolve(normalized[first_metadata[provider]], resumed), own_ids[provider])] += 1

    # Deliberately exercise already-known threads even when none spans the
    # global sample midpoint. The earliest *observed* message is the initial
    # catalog, not a claim to have fetched the thread's actual original.
    thread_sources = defaultdict(list)
    for provider, name in first_metadata.items():
        reference_thread = oracle[name].get("provider_thread_id")
        if reference_thread:
            thread_sources[reference_thread].append(provider)
    thread_replay = Counter()
    for providers in thread_sources.values():
        if len(providers) < 2:
            continue
        providers.sort(key=lambda p: ((time_range(normalized[first_metadata[p]].get("sent"), "sent") or (float("inf"),))[0], own_ids[p]))
        initial = providers[0]
        prior = [record(own_ids[initial], normalized[first_metadata[initial]])]
        thread_replay["previously_seen_threads"] += 1
        for provider in providers[1:]:
            incoming = normalized[first_metadata[provider]]
            outcome = resolve(incoming, prior)
            thread_replay[grade(outcome, None)] += 1
            if outcome["status"] == "new_observation":
                prior.append(record(own_ids[provider], incoming))

    # Compare optional pairwise related-correspondence suggestions with Gmail's
    # snapshot grouping only. Disagreement is not proof either grouping is true.
    thread_counts = Counter()
    all_sources = dict(first_search)
    all_sources.update(first_metadata)
    for (pa, a), (pb, b) in itertools.combinations(all_sources.items(), 2):
        ta, tb = oracle[a].get("provider_thread_id"), oracle[b].get("provider_thread_id")
        if not ta or not tb:
            continue
        proposed = related(normalized[a], normalized[b])
        same = ta == tb
        if proposed or same:
            thread_counts[("suggested_" if proposed else "not_suggested_") + ("same_provider_thread" if same else "different_provider_threads")] += 1

    field_counts = Counter()
    for name in first_metadata.values():
        value = normalized[name]
        field_counts["metadata_rows"] += 1
        for key in ("subject", "sender", "sent", "to", "cc"):
            field_counts[key + "_present"] += value.get(key) is not None
        field_counts["sufficient_for_automatic_route"] += sufficient(value)
    diagnostic_dates = Counter()
    cross_route_metadata = Counter()
    for provider, name in first_metadata.items():
        search_name = first_search.get(provider)
        if not search_name:
            continue
        for field in ("subject", "sender", "to", "cc"):
            first, second = normalized[name].get(field), normalized[search_name].get(field)
            if first is None or second is None:
                cross_route_metadata[field+"_incomparable"] += 1
            else:
                cross_route_metadata[field+"_equal" if first == second else field+"_different"] += 1
        header = time_range(normalized[name].get("sent"), "sent")
        search_time = parse_observed_time(by_id[search_name].get("untyped_time_raw"))
        internal = parse_observed_time(by_id[name].get("provider_internal_date_raw"))
        diagnostic_dates["paired"] += 1
        if header is not None and search_time is not None:
            diagnostic_dates["search_equal_source_date" if abs(search_time-header[0]) < .001 else "search_differs_source_date"] += 1
        if search_time is not None and internal is not None:
            diagnostic_dates["search_equal_internal_date" if abs(search_time-internal) < .001 else "search_differs_internal_date"] += 1
        if header is not None and internal is not None:
            diagnostic_dates["source_date_equal_internal_date" if abs(header[0]-internal) < .001 else "source_date_differs_internal_date"] += 1

    attachment_counts = Counter()
    search_repeats = defaultdict(list)
    for name in search_observations:
        search_repeats[oracle[name]["provider_message_id"]].append(name)
    attachment_repeat_checks = Counter()
    for provider, name in first_search.items():
        row = by_id[name]
        filenames, inline = row.get("attachment_names"), row.get("inline_names")
        attachment_counts["messages_with_exposed_named_attachment_list"] += filenames is not None
        attachment_counts["messages_with_named_attachments"] += bool(filenames)
        attachment_counts["messages_with_inline_names"] += bool(inline)
        attachment_counts["named_attachment_entries"] += len(filenames or [])
        attachment_counts["inline_name_entries"] += len(inline or [])
        attachment_counts["messages_with_repeated_attachment_names"] += bool(filenames and len(set(filenames)) < len(filenames))
        attachment_counts["messages_with_repeated_inline_names"] += bool(inline and len(set(inline)) < len(inline))
        for again in search_repeats[provider][1:]:
            later = by_id[again]
            attachment_repeat_checks["comparisons"] += 1
            for label, left, right in (("named", filenames, later.get("attachment_names")),
                                       ("inline", inline, later.get("inline_names"))):
                if left is None or right is None:
                    attachment_repeat_checks[label+"_incomparable_missing_list"] += 1
                else:
                    attachment_repeat_checks[label+"_comparable_pairs"] += 1
                    attachment_repeat_checks[label+"_multiset_equal"] += sorted(left) == sorted(right)

    metadata_rows = [(provider, normalized[name]) for provider, name in first_metadata.items()]
    collision_profiles = {}
    for precision, divisor in (("second", 1), ("minute", 60), ("day_utc", 86400)):
        def key(row, divisor=divisor):
            span = time_range(row.get("sent"), "sent")
            return (row.get("subject"), row.get("sender"), int(span[0]//divisor)) if span else None
        collision_profiles["subject_sender_sent_"+precision] = collision_counts(metadata_rows, key)
    collision_profiles["subject_sender_only"] = collision_counts(metadata_rows, lambda r: (r.get("subject"),r.get("sender")))
    search_rows = [(provider, by_id[name]) for provider, name in first_search.items()]
    collision_profiles["search_subject_sender_untyped_timestamp"] = collision_counts(
        search_rows, lambda r: (decode_subject(r.get("subject")), flattened_sender(r.get("sender_raw")), str(r.get("untyped_time_raw")))
        if r.get("untyped_time_raw") is not None else None)

    private_write(root / "evaluation-audit.json", audit)
    result = {"kind": "live-metadata-only-development-stress-test",
              "bindings": {"observations_sha256": sha(observations_path), "oracle_sha256": sha(oracle_path),
                           "model_sha256": sha(HERE/"model.py"), "evaluator_sha256": sha(Path(__file__))},
              "sample": {"observations": len(observations), "distinct_reference_messages": len(all_sources),
                         "search_observations": len(search_observations), "metadata_observations": len(metadata_observations),
                         "distinct_header_read_messages": len(first_metadata), "paired_search_observations": len(paired_search)},
              "identity_trials": dict(metrics), "negative_pairs": dict(pair_counts), "same_subject_sender_negative_pairs": dict(hard_counts),
              "date_header_availability": dict(field_counts), "timestamp_diagnostics_only": dict(diagnostic_dates),
              "cross_route_metadata": dict(cross_route_metadata),
              "collision_profiles": collision_profiles, "attachment_metadata": dict(attachment_counts),
              "repeated_attachment_list_observations": dict(attachment_repeat_checks),
              "thread_grouping_snapshot_comparison": dict(thread_counts),
              "historical_daily_simulation": {"historical_messages":len(historical), "daily_messages":len(daily),
                                             "daily_results":dict(daily_counts), "daily_in_previously_seen_threads":dict(old_thread_daily),
                                             "saved_catalog_record_count":len(resumed), "daily_json_restart_replay":dict(daily_replay_counts)},
              "targeted_existing_thread_replay": dict(thread_replay),
              "invariance": {"catalog_order":bool(order_equal), "json_roundtrip":bool(json_equal), "external_ids_irrelevant":bool(ids_irrelevant)},
              "body_or_attachment_bytes_used": False, "provider_ids_used_by_matcher": False,
              "provider_snapshot_ids_used_for_private_test_construction_pairing_and_grading": True,
              "untyped_search_time_used_as_sent_or_received": False,
              "live_whole_mailbox_discovery_qualified": False, "cross_vendor_agents_qualified": False,
              "live_scheduled_job_or_drive_instance_used": False}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private-root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = run(args.private_root)
    except Exception as exc:
        # Full diagnosis stays private. Never print an exception that might
        # contain a source field, provider locator or private request argument.
        import traceback
        private_write(args.private_root/"evaluation-error.json", {"traceback":traceback.format_exc()})
        print(json.dumps({"evaluation_failed":True,"exception_type":type(exc).__name__}))
        raise SystemExit(1)
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
