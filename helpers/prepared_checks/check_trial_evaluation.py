"""Prepared fictional evaluator checks; NOT RUN.

Execution belongs to the user's authorized testing phase. No connector, browser,
Drive instance, mailbox, or private trial artifact is used by these checks.
"""

import hashlib
import json
from pathlib import Path
import stat
import tempfile
import unittest

from helpers.trial_evaluation import (
    audit_contract_references,
    bind_report_artifact,
    classify_connector_observation,
    compare_page_candidates,
    evaluate_image_expectation,
    pack_evaluation_group,
    preflight_private_receipt_sink,
    save_private_receipt,
)


FIXTURES = Path(__file__).parents[2] / "examples" / "evaluation"


class TrialEvaluationChecks(unittest.TestCase):
    def test_receipt_sink_preflight_and_exact_private_receipt(self):
        with tempfile.TemporaryDirectory() as parent:
            sink = Path(parent) / "private-receipts"
            self.assertEqual(preflight_private_receipt_sink(sink)["status"], "ready")
            result = save_private_receipt(sink, "fictional-read-001", b"complete-envelope")
            self.assertEqual(result["receipt_state"], "saved_verified")
            self.assertEqual(stat.S_IMODE(Path(result["private_path"]).stat().st_mode), 0o600)
            self.assertEqual(Path(result["private_path"]).read_bytes(), b"complete-envelope")

    def test_sink_failure_does_not_become_provider_failure(self):
        result = classify_connector_observation(
            dispatch_state="dispatched",
            provider_state="response_observed",
            receipt_state="failed",
        )
        self.assertEqual(result["classification"], "evaluator_receipt_failure")

    def test_nested_reference_fixture_has_exact_complete_visit_set(self):
        fixture = json.loads((FIXTURES / "reference-traversal.json").read_text())
        result = audit_contract_references(fixture["pages"], fixture["root_page_ids"])
        self.assertEqual(result["status"], fixture["expected"]["status"])
        self.assertEqual(result["visited_page_ids"], fixture["expected"]["visited_page_ids"])
        self.assertEqual(len(result["unresolved_page_references"]), 0)
        self.assertEqual(len(result["unresolved_record_references"]), 0)

    def test_missing_nested_target_is_incomplete_not_empty(self):
        fixture = json.loads((FIXTURES / "reference-traversal.json").read_text())
        fixture["pages"] = fixture["pages"][:1]
        result = audit_contract_references(fixture["pages"], fixture["root_page_ids"])
        self.assertEqual(result["status"], "incomplete")
        self.assertEqual(len(result["unresolved_page_references"]), 2)

    def test_every_derived_family_requires_continuation(self):
        for family in (
            "record_locator",
            "page_catalogue",
            "entity_index",
            "topic_index",
            "incoming_relationship_index",
            "index_coverage",
        ):
            with self.subTest(family=family):
                page = {
                    "instance_id": "inst_fictional",
                    "family": family,
                    "page_id": "page_fictional_" + family,
                    "schema_version": "1",
                    "content_revision": 1,
                    "entries": [],
                }
                result = audit_contract_references([page], [page["page_id"]])
                self.assertEqual(result["status"], "incomplete")
                self.assertEqual(result["diagnostics"][0]["kind"], "unknown_required_shape")

    def test_exhausted_continuation_cannot_name_a_next_page(self):
        for family in (
            "record_locator",
            "page_catalogue",
            "entity_index",
            "topic_index",
            "incoming_relationship_index",
            "index_coverage",
        ):
            with self.subTest(family=family):
                page = {
                    "instance_id": "inst_fictional",
                    "family": family,
                    "page_id": "page_fictional_" + family,
                    "schema_version": "1",
                    "content_revision": 1,
                    "entries": [],
                    "continuation": {
                        "state": "exhausted",
                        "next_page_id": "page_fictional_forbidden_next",
                    },
                }
                result = audit_contract_references([page], [page["page_id"]])
                self.assertEqual(result["status"], "incomplete")
                self.assertEqual(result["diagnostics"][0]["kind"], "unknown_required_shape")

    def test_continues_requires_exact_nonempty_next_page_shape(self):
        page = {
            "instance_id": "inst_fictional",
            "family": "record_locator",
            "page_id": "page_fictional_locator",
            "schema_version": "1",
            "content_revision": 1,
            "entries": [],
            "continuation": {"state": "continues"},
        }
        result = audit_contract_references([page], [page["page_id"]])
        self.assertEqual(result["status"], "incomplete")
        self.assertEqual(result["diagnostics"][0]["kind"], "unknown_required_shape")

    def test_discovery_window_requires_exact_nested_continuation_shape(self):
        invalid_cases = {
            "exhausted_with_next": {
                "state": "exhausted",
                "next_page_id": "page_fictional_forbidden_next",
            },
            "continues_without_next": {"state": "continues"},
            "continues_with_extra_key": {
                "state": "continues",
                "next_page_id": "page_fictional_next",
                "extra": "not allowed",
            },
            "exhausted_with_extra_key": {
                "state": "exhausted",
                "extra": "not allowed",
            },
        }
        for label, continuation in invalid_cases.items():
            with self.subTest(label=label):
                page = {
                    "instance_id": "inst_fictional",
                    "family": "discovery_window",
                    "page_id": "page_fictional_window",
                    "schema_version": "1",
                    "content_revision": 1,
                    "records": [
                        {
                            "window_id": "window_fictional",
                            "source_account_ref": {
                                "family": "source_account",
                                "id": "source_account_fictional",
                            },
                            "school_refs": [],
                            "observed_email_refs": {
                                "source_index_page_ids": [],
                                "continuation": continuation,
                            },
                        }
                    ],
                }
                result = audit_contract_references([page], [page["page_id"]])
                self.assertEqual(result["status"], "incomplete")
                self.assertEqual(result["diagnostics"][0]["kind"], "unknown_required_shape")

    def test_discovery_window_requires_nested_continuation_field(self):
        page = {
            "instance_id": "inst_fictional",
            "family": "discovery_window",
            "page_id": "page_fictional_window",
            "schema_version": "1",
            "content_revision": 1,
            "records": [
                {
                    "window_id": "window_fictional",
                    "source_account_ref": {
                        "family": "source_account",
                        "id": "source_account_fictional",
                    },
                    "school_refs": [],
                    "observed_email_refs": {"source_index_page_ids": []},
                }
            ],
        }
        result = audit_contract_references([page], [page["page_id"]])
        self.assertEqual(result["status"], "incomplete")
        self.assertEqual(result["diagnostics"][0]["kind"], "unknown_required_shape")

    def test_report_requires_same_task_receipt_and_exact_bytes(self):
        artifact = b"fictional task-bound report"
        task = "fictional-work-route"
        binding = {
            "task_alias": task,
            "events": {
                "prompt": {"observed": True, "task_alias": task},
                "final_response": {"observed": True, "task_alias": task},
                "export_action": {"observed": True, "task_alias": task},
                "provider_receipt": {"state": "saved_verified", "task_alias": task},
            },
            "artifact": {"sha256": hashlib.sha256(artifact).hexdigest()},
        }
        self.assertEqual(bind_report_artifact(binding, artifact)["status"], "task_bound")
        binding["events"]["export_action"]["observed"] = False
        self.assertEqual(bind_report_artifact(binding, artifact)["status"], "visible_output_only")

    def test_image_expectation_requires_independent_visible_pixels(self):
        pixels = b"fictional exact pixel bytes"
        binding = {
            "reviewed_artifact_sha256": hashlib.sha256(pixels).hexdigest(),
            "visible_evidence": {"kind": "exact_pixels", "portions_reviewed": ["full image"]},
            "expectation": {
                "basis": "independent_visual_review",
                "authored_before_tested_output": True,
                "tested_output_used": False,
            },
            "ocr": {"used": False},
        }
        self.assertEqual(evaluate_image_expectation(binding, pixels)["status"], "grounded")
        binding["visible_evidence"] = {"kind": "unavailable", "portions_reviewed": []}
        self.assertEqual(
            evaluate_image_expectation(binding, pixels)["status"],
            "evaluation_limitation",
        )

    def test_near_limit_rollover_keeps_records_whole(self):
        first = {"knowledge_id": "knowledge_fictional_large", "statement": "cedar " * 9_900}
        second = {"knowledge_id": "knowledge_fictional_next", "statement": "school " * 1_100}
        result = pack_evaluation_group(
            [first, second],
            {"canonical_family": "knowledge", "route": "fictional-2026-09"},
            65_536,
        )
        self.assertEqual(result["record_count"], 2)
        self.assertEqual(result["packed_record_count"], 2)
        self.assertEqual(result["overflows"], [])
        self.assertEqual(len(result["pages"]), 2)
        reconstructed = []
        for page in result["pages"]:
            self.assertLessEqual(len(page), 65_536)
            reconstructed.extend(json.loads(page)["records"])
        self.assertEqual(reconstructed, [first, second])

    def test_all_candidate_limits_use_the_same_ordered_records(self):
        records = [{"task_id": "task_fictional_1"}, {"task_id": "task_fictional_2"}]
        candidates = compare_page_candidates(records, {"canonical_family": "task"})
        self.assertEqual(set(candidates), {"65536", "131072", "262144"})
        for result in candidates.values():
            reconstructed = []
            for page in result["pages"]:
                reconstructed.extend(json.loads(page)["records"])
            self.assertEqual(reconstructed, records)
