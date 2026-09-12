#!/usr/bin/env python3
"""Measure synthetic input-boundary limitations in the prepared identity model.

This script does not repair the matcher, parse MIME, or claim that deliberately
out-of-contract inputs were covered by its original 38 cases. All source data is
fictional. It imports only the adjacent experiment and runs fresh subprocesses
of itself for the timezone check. The interval demonstration is separate from
the existing matcher: that matcher does not perform overlap-based merging.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time


EXPERIMENT = Path(__file__).resolve().parent.parent / "experiment.py"


def load_experiment():
    spec = importlib.util.spec_from_file_location("prepared_identity", EXPERIMENT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def timezone_child():
    """Set process timezone before the existing datetime comparison executes."""
    if not hasattr(time, "tzset"):
        return {"supported": False, "reason": "time-tzset-unavailable"}
    time.tzset()
    model = load_experiment()
    original = model.record("sos-source-a", model.observe())
    incoming = model.observe(received_at="2026-01-05T09:00:02")
    return {
        "supported": True,
        "process_timezone": os.environ["TZ"],
        "incoming_received_at_has_timezone": False,
        "result": model.resolve(incoming, [original]),
    }


def timezone_observation(zone):
    environment = dict(os.environ)
    environment["TZ"] = zone
    result = subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), "--timezone-child"],
        env=environment, capture_output=True, text=True, timeout=10, check=True,
    )
    return json.loads(result.stdout)


def interval_demonstration():
    # Half-open intervals in seconds within one fictional UTC minute. The broad
    # observation reports only minute precision; it is not a precise instant.
    intervals = {
        "precise-first": [2, 3],
        "minute-only": [0, 60],
        "precise-second": [48, 49],
    }

    def overlaps(left, right):
        a, b = intervals[left], intervals[right]
        return max(a[0], b[0]) < min(a[1], b[1])

    left = overlaps("precise-first", "minute-only")
    right = overlaps("minute-only", "precise-second")
    endpoints = overlaps("precise-first", "precise-second")
    return {
        "kind": "separate-mathematical-demonstration",
        "existing_matcher_performs_this_merge": False,
        "intervals_seconds_within_one_minute": intervals,
        "first_overlaps_broad": left,
        "broad_overlaps_second": right,
        "first_overlaps_second": endpoints,
        "overlap_is_transitive_in_this_example": not (left and right and not endpoints),
        "risk": "Treating overlap as identity could merge two distinct precise deliveries through a partial observation.",
        "required_policy": "Retain partial evidence without turning overlap into an equivalence or automatic merge.",
    }


def run():
    model = load_experiment()
    original = model.record("sos-source-a", model.observe())
    twin = model.record("sos-source-b", model.observe())
    baseline = model.resolve(model.observe(), [original])
    display = model.resolve(model.observe(sender="School <school@example.org>"), [original])
    minute = model.resolve(model.observe(received_at="2026-01-05T09:00:00Z"), [original])
    utc = timezone_observation("UTC")
    pacific = timezone_observation("America/Los_Angeles")
    try:
        malformed = {"returned": model.resolve(model.observe(received_at="Jan 5"), [original])}
    except Exception as exc:
        # Source data is synthetic, but the complete exception is unnecessary.
        malformed = {"raised_exception_type": type(exc).__name__}
    ordered = model.resolve(model.observe(), [original, twin])
    reversed_order = model.resolve(model.observe(), [twin, original])
    zones_supported = utc["supported"] and pacific["supported"]
    same_zone_result = utc["result"] == pacific["result"] if zones_supported else None
    checks = [
        {
            "case": "sender-display-name-projection",
            "fixture_relationship": "Same fictional sender address; only display-name presentation changes.",
            "baseline": baseline,
            "changed_presentation": display,
            "decision_unchanged": display == baseline,
            "boundary_requirement": "Parse address roles before comparison; a display name is not a different mailbox.",
            "scope": "The original model assumes a normalized sender string; it does not implement this normalization.",
        },
        {
            "case": "minute-precision-projection",
            "fixture_relationship": "Same fictional receipt displayed at minute precision; an adapter incorrectly represents it as a precise instant.",
            "baseline": baseline,
            "rounded_presentation": minute,
            "decision_unchanged": minute == baseline,
            "boundary_requirement": "Preserve precision and abstain when it cannot distinguish candidates; do not fabricate zero seconds.",
            "scope": "The original model assumes precise zoned timestamps and has no precision field.",
        },
        {
            "case": "timezone-less-projection-in-fresh-processes",
            "observations": [utc, pacific],
            "process_timezone_independent": same_zone_result,
            "boundary_requirement": "An unknown timezone must remain unknown instead of inheriting the agent environment's timezone.",
            "scope": "The original prepared fixtures always supply a timezone; this input is outside that contract.",
        },
        {
            "case": "malformed-received-timestamp",
            "observation": malformed,
            "returns_scoped_unresolved_result": "returned" in malformed and malformed["returned"]["status"] == "needs-more-evidence",
            "boundary_requirement": "Malformed source evidence must produce a scoped unresolved item instead of terminating unrelated processing.",
            "scope": "Input validation or normalization must handle this before or within a production resolver.",
        },
        {
            "case": "catalog-record-order",
            "original_order": ordered,
            "reversed_order": reversed_order,
            "exact_output_equal": ordered == reversed_order,
            "status_and_candidate_set_equal": ordered["status"] == reversed_order["status"] and set(ordered["record_ids"]) == set(reversed_order["record_ids"]),
            "boundary_requirement": "Sort candidate record IDs if byte-stable serialized results are required; do not mistake this ordering difference for a changed identity decision.",
            "scope": "This distinguishes exact output determinism from semantic decision determinism.",
        },
    ]
    return {
        "kind": "synthetic-prepared-matcher-boundary-measurements",
        "experiment_sha256": hashlib.sha256(EXPERIMENT.read_bytes()).hexdigest(),
        "check_count": len(checks),
        "checks": checks,
        "interval_bridge_demonstration": interval_demonstration(),
        "live_connector_or_private_source_accessed": False,
        "mime_parsing_tested_by_this_script": False,
        "production_recipe_repaired_by_this_script": False,
        "interpretation": "These measurements expose boundary limitations and reporting distinctions; they are not passing robustness assertions or estimates of real-world error rates.",
        "primary_source_notes": [
            {
                "url": "https://www.rfc-editor.org/rfc/rfc2046.html",
                "section": "5.1.3 and 5.1.4",
                "note": "Original mixed and alternative MIME order can matter; connector listing order is a different concept.",
            },
            {
                "url": "https://www.rfc-editor.org/rfc/rfc2387.html",
                "section": "3",
                "note": "A related multipart has an interrelated structure and a root selected by start or the first part.",
            },
            {
                "url": "https://www.rfc-editor.org/rfc/rfc2392.html",
                "section": "2",
                "note": "Limited alternative contexts can contain duplicate Content-ID values; a global unique-ID assumption is insufficient.",
            },
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--timezone-child", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    result = timezone_child() if args.timezone_child else run()
    serialized = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.write_text(serialized)
    print(serialized, end="")


if __name__ == "__main__":
    main()
