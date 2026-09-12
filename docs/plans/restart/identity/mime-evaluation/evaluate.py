#!/usr/bin/env python3
"""Measure the existing recipe; failed identity decisions are results, not hidden.

This is an analysis instrument, not a replacement runtime or claimed repair.
The separate generator supplies delivery truth. Neither the MIME adapter nor
the existing resolver receives occurrence/communication labels.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import random
import subprocess
import sys

from adapter import observe

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus"
EXPERIMENT = HERE.parent / "experiment.py"
spec = importlib.util.spec_from_file_location("original_recipe", EXPERIMENT)
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)
ASSOCIATION = "content-match-occurrence-unverified"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def serialized(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def resolve(incoming, records):
    before = copy.deepcopy(records)
    try:
        result = model.resolve(incoming, records)
    except Exception as exc:
        result = {"status": "error", "exception_type": type(exc).__name__, "record_ids": []}
    assert before == records, "Resolution mutated its input catalog"
    return result


def category(truth, status, same_communication):
    if status == "error":
        return "error"
    if truth == "same_occurrence":
        if status == ASSOCIATION:
            return "correct_content_association_occurrence_unverified"
        if status == "new-observation":
            return "false_split"
        return "positive_abstention"
    if truth == "indistinguishable_occurrence":
        if status == ASSOCIATION:
            return "association_only_cannot_identify_delivery"
        if status == "new-observation":
            return "unsupported_distinction"
        return "unresolved_indistinguishable_delivery"
    if status == ASSOCIATION:
        if same_communication:
            return "known_distinct_delivery_content_association"
        return "incorrect_content_association"
    if status == "new-observation":
        return "correct_distinction"
    return "negative_abstention"


def run():
    manifest = json.loads((CORPUS / "manifest.json").read_text())
    fixtures = {entry["observation_id"]: entry for entry in manifest["observations"]}
    witnesses, coverage = {}, {}
    for name, entry in fixtures.items():
        assert sha(CORPUS / entry["file"]) == entry["raw_sha256"], "Fixture bytes changed after truth was bound"
        # Truth is deliberately removed before observation extraction.
        public_input = {k: v for k, v in entry.items() if k not in
                        {"occurrence_id", "communication_id", "indistinguishable_group", "rationale"}}
        witnesses[name], coverage[name] = observe(public_input, CORPUS)

    counts = defaultdict(Counter)
    matrix, notable, targeted, external_id_checks = [], [], [], 0
    for pair in manifest["pairs"]:
        for incoming_name, stored_name in ((pair["left"], pair["right"]),
                                           (pair["right"], pair["left"])):
            incoming, stored = witnesses[incoming_name], witnesses[stored_name]
            records = [model.record("sos-source-reference", stored)]
            result = resolve(incoming, records)
            same_communication = (fixtures[incoming_name]["communication_id"] ==
                                  fixtures[stored_name]["communication_id"])
            graded = category(pair["truth"], result["status"], same_communication)
            counts[pair["truth"]][graded] += 1
            row = {"incoming": incoming_name, "stored": stored_name,
                   "truth": pair["truth"], "same_communication": same_communication,
                   "status": result["status"], "classification": graded}
            matrix.append(row)
            if graded in {"false_split", "incorrect_content_association", "error", "unsupported_distinction"}:
                notable.append(row)
            if pair.get("targeted"):
                targeted.append(row)
            # Independent, contradictory external handles cannot change results.
            altered = copy.deepcopy(incoming)
            altered_records = copy.deepcopy(records)
            for index, item in enumerate([altered, altered_records[0]["witness"]]):
                for field in ("alias", "rfc_message_id", "in_reply_to", "thread"):
                    item[field] = "fixture-access-hint-" + str(index)
            assert resolve(altered, altered_records) == result, "External identifier changed source-evidence decision"
            external_id_checks += 1

    # Stable known catalog: one *independently known* occurrence per record.
    # Truth selects this grading setup, never informs the resolver itself.
    representatives = {}
    for name in sorted(fixtures):
        occurrence = fixtures[name]["occurrence_id"]
        if occurrence not in representatives:
            representatives[occurrence] = name
    reference_catalog = [model.record("sos-source-" + str(i + 1), witnesses[name])
                         for i, name in enumerate(representatives.values())]
    exact_order_changes, semantic_order_changes = [], []
    roundtrip_ok = True
    for name, witness in witnesses.items():
        original = resolve(witness, reference_catalog)
        reversed_result = resolve(witness, list(reversed(reference_catalog)))
        if original != reversed_result:
            exact_order_changes.append(name)
        if (original["status"], sorted(original["record_ids"])) != (
                reversed_result["status"], sorted(reversed_result["record_ids"])):
            semantic_order_changes.append(name)
        roundtrip_ok &= original == resolve(json.loads(json.dumps(witness)),
                                           json.loads(json.dumps(reference_catalog)))

    # This replay models only the documented identity decisions. A content
    # association groups reuse of known content; it does NOT merge deliveries,
    # send replies, create tasks, or mark semantic processing complete.
    def ingest(order):
        catalog, associated, pending, history = [], defaultdict(list), [], []
        for name in order:
            decision = resolve(witnesses[name], catalog)
            if decision["status"] == "new-observation":
                own_id = "sos-source-" + str(len(catalog) + 1)
                catalog.append(model.record(own_id, witnesses[name]))
                associated[own_id].append(name)
            elif decision["status"] == ASSOCIATION:
                associated[decision["record_ids"][0]].append(name)
            else:
                pending.append(name)
            history.append({"observation": name, "decision": decision["status"],
                            "accepted_content_records": len(catalog), "pending": len(pending)})
        # One explicit replay after richer reads; no unbounded retry loop.
        still_pending = []
        for name in pending:
            decision = resolve(witnesses[name], catalog)
            if decision["status"] == ASSOCIATION:
                associated[decision["record_ids"][0]].append(name)
            else:
                still_pending.append(name)
        groups = sorted(sorted(names) for names in associated.values())
        return {"groups_ignoring_arbitrary_own_id_assignment": groups,
                "pending": sorted(still_pending), "history": history}

    names = sorted(fixtures)
    shuffled = names[:]
    random.Random(17).shuffle(shuffled)
    replays = {"forward": ingest(names), "reverse": ingest(list(reversed(names))), "shuffled": ingest(shuffled)}
    signatures = [(value["groups_ignoring_arbitrary_own_id_assignment"], value["pending"])
                  for value in replays.values()]
    positive_total = sum(counts["same_occurrence"].values())
    positive_matches = counts["same_occurrence"]["correct_content_association_occurrence_unverified"]
    decided = sum(row["status"] in {ASSOCIATION, "new-observation"} for row in matrix)
    return {"kind": "raw-synthetic-mime-evaluation-of-existing-recipe",
            "bindings": {"experiment_sha256": sha(EXPERIMENT), "adapter_sha256": sha(HERE / "adapter.py"),
                         "generator_sha256": sha(HERE / "generator.py"), "manifest_sha256": sha(CORPUS / "manifest.json"),
                         "evaluator_sha256": sha(Path(__file__))},
            "observation_count": len(fixtures), "unordered_pair_count": len(manifest["pairs"]),
            "directed_comparison_count": len(matrix), "counts": dict(counts),
            "automatic_positive_association_recall": {"numerator": positive_matches, "denominator": positive_total},
            "automatic_decision_coverage": {"numerator": decided, "denominator": len(matrix)},
            "unexpected_decisions": notable, "targeted_comparisons": targeted,
            "determinism": {"catalog_order_changes_serialized_output_for": exact_order_changes,
                            "catalog_order_changes_status_or_candidate_set_for": semantic_order_changes,
                            "json_roundtrip_preserves_decisions": roundtrip_ok,
                            "external_id_mutation_checks": external_id_checks,
                            "ingestion_grouping_and_pending_equal_in_three_orders": all(x == signatures[0] for x in signatures)},
            "coverage": list(coverage.values()), "replays": replays,
            "raw_bytes_retained_in_witnesses": False,
            "remote_resources_fetched": False, "pdf_or_image_semantics_extracted": False,
            "live_agent_connector_or_drive_state_tested": False,
            "pair_matrix": matrix}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fingerprint", action="store_true")
    args = parser.parse_args()
    result = run()
    fingerprint = hashlib.sha256(serialized(result).encode()).hexdigest()
    if args.fingerprint:
        print(fingerprint)
        return
    fresh = []
    for seed, zone in (("0", "UTC"), ("1", "America/Los_Angeles"), ("17", "UTC")):
        child = subprocess.run([sys.executable, str(Path(__file__)), "--fingerprint"],
                               env={**os.environ, "PYTHONHASHSEED": seed, "TZ": zone},
                               capture_output=True, text=True, check=True, timeout=60)
        fresh.append({"hash_seed": seed, "timezone": zone, "same_results": child.stdout.strip() == fingerprint})
    result["determinism"]["fresh_processes"] = fresh
    # Separate compact report from full pair audit, retaining every measured pair.
    matrix = result.pop("pair_matrix")
    (HERE / "pair-results.json").write_text(json.dumps(matrix, indent=2) + "\n")
    (HERE / "results.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({key: result[key] for key in ("observation_count", "unordered_pair_count",
          "directed_comparison_count", "counts", "automatic_positive_association_recall",
          "automatic_decision_coverage", "determinism")}, indent=2))


if __name__ == "__main__":
    main()
