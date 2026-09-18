"""Prepared fictional evaluator checks.

Last run locally on 2026-09-18 as part of the 73-test prepared-check suite. No
connector, browser, Drive instance, mailbox, or private trial artifact is used.
"""

import hashlib
import json
from pathlib import Path
import stat
import tempfile
import unittest

from helpers.trial_evaluation import (
    audit_contract_references,
    authorize_bound_followup,
    authorize_single_no_dispatch_retry,
    bind_report_artifact,
    classify_connector_observation,
    compare_page_candidates,
    evaluate_image_expectation,
    pack_evaluation_group,
    preflight_private_receipt_sink,
    preflight_source_oracle,
    resolve_controller_observations,
    save_private_receipt,
    validate_call_schema,
)


FIXTURES = Path(__file__).parents[2] / "examples" / "evaluation"


class TrialEvaluationChecks(unittest.TestCase):
    def _controller_binding(self):
        return {
            "provider_alias": "provider_fictional",
            "task_alias": "task_fictional",
            "conversation_alias": "conversation_fictional",
            "route_alias": "route_fictional",
            "root_alias": "root_fictional",
        }

    def _controller_observation(self, **changes):
        observation = {
            "binding": self._controller_binding(),
            "stage": "setup_interview",
            "state": "awaiting_user_input",
            "composer_scope": "bound_task",
            "response_kind": "final_response",
            "sequence": 2,
        }
        observation.update(changes)
        return observation

    def _round_manifest_bytes(self, interval=None):
        return json.dumps({
            "round_alias": "round_fictional",
            "source_interval": interval or {
                "start": "2031-09-09T17:53:48Z",
                "end": "2031-09-16T17:53:48Z",
                "timezone": "UTC",
                "precision": "second",
                "boundary": "[start,end)",
            },
        }, separators=(",", ":")).encode("utf-8")

    def _source_input_bytes(self, aliases=None):
        aliases = aliases or ["query_fictional_one", "query_fictional_two"]
        return json.dumps({
            "source_scope_alias": "source_fictional",
            "enumeration_query_aliases": aliases,
        }, separators=(",", ":")).encode("utf-8")

    def _source_oracle(self, manifest_bytes, source_input_bytes=None):
        source_input_bytes = source_input_bytes or self._source_input_bytes()
        interval = json.loads(manifest_bytes)["source_interval"]
        aliases = json.loads(source_input_bytes)["enumeration_query_aliases"]
        chains = []
        for number, alias in enumerate(aliases):
            first_receipt = (
                "fictional enumeration chain " + str(number) + " page one"
            ).encode("utf-8")
            second_receipt = (
                "fictional enumeration chain " + str(number) + " page two"
            ).encode("utf-8")
            token = "fictional-token-" + str(number) + "-2"
            chains.append({
                "query_alias": alias,
                "pages": [
                    {
                        "request_token": None,
                        "observed_next_token": token,
                        "receipt_bytes": first_receipt,
                        "receipt_sha256": hashlib.sha256(first_receipt).hexdigest(),
                    },
                    {
                        "request_token": token,
                        "observed_next_token": None,
                        "receipt_bytes": second_receipt,
                        "receipt_sha256": hashlib.sha256(second_receipt).hexdigest(),
                    },
                ],
            })
        return {
            "round_manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
            "source_input_sha256": hashlib.sha256(source_input_bytes).hexdigest(),
            "source_interval": interval,
            "enumeration_chains": chains,
            "entries": [
                {
                    "source_alias": "at_start",
                    "arrival_timestamp": {
                        "value": interval["start"],
                        "timezone": interval["timezone"],
                        "precision": interval["precision"],
                        "meaning": "received",
                    },
                },
                {
                    "source_alias": "at_end",
                    "arrival_timestamp": {
                        "value": interval["end"],
                        "timezone": interval["timezone"],
                        "precision": interval["precision"],
                        "meaning": "arrival",
                    },
                },
            ],
        }

    def _report_binding(self, artifact):
        task = "fictional-work-route"
        digest = hashlib.sha256(artifact).hexdigest()
        return {
            "task_alias": task,
            "events": {
                "prompt": {"observed": True, "task_alias": task},
                "final_response": {"observed": True, "task_alias": task},
                "export_action": {"observed": True, "task_alias": task},
                "provider_receipt": {
                    "state": "saved_verified",
                    "task_alias": task,
                    "artifact_sha256": digest,
                    "artifact_byte_count": len(artifact),
                },
            },
            "artifact": {"sha256": digest, "byte_count": len(artifact)},
        }

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

    def test_followup_requires_exact_binding_stage_and_task_composer(self):
        binding = self._controller_binding()
        allowed = ["awaiting_user_input"]
        result = authorize_bound_followup(
            expected_binding=binding,
            expected_stage="setup_interview",
            observations=[self._controller_observation()],
            allowed_states=allowed,
        )
        self.assertTrue(result["authorized"])

        top_level = self._controller_observation(composer_scope="top_level")
        self.assertEqual(authorize_bound_followup(
            expected_binding=binding,
            expected_stage="setup_interview",
            observations=[top_level],
            allowed_states=allowed,
        )["reason"], "composer_not_bound_to_task")

        wrong_route = self._controller_observation()
        wrong_route["binding"] = {**binding, "route_alias": "another_route"}
        self.assertEqual(authorize_bound_followup(
            expected_binding=binding,
            expected_stage="setup_interview",
            observations=[wrong_route],
            allowed_states=allowed,
        )["reason"], "binding_mismatch")

        self.assertEqual(authorize_bound_followup(
            expected_binding=binding,
            expected_stage="ingestion",
            observations=[self._controller_observation()],
            allowed_states=allowed,
        )["reason"], "stage_mismatch")

    def test_later_final_response_supersedes_running_snapshot(self):
        running = self._controller_observation(
            state="active", response_kind="running_snapshot", sequence=1,
        )
        final = self._controller_observation(
            state="awaiting_user_input", response_kind="final_response", sequence=2,
        )
        result = resolve_controller_observations([running, final])
        self.assertEqual(result["state"], "awaiting_user_input")
        self.assertEqual(result["superseded_running_snapshots"], 1)

    def test_empty_observation_history_is_explicitly_unavailable(self):
        result = resolve_controller_observations([])
        self.assertEqual(result["state"], "controller_observation_unavailable")
        self.assertIsNone(result["current"])

    def test_only_one_proven_no_dispatch_retry_is_authorized(self):
        binding = self._controller_binding()
        opening = b"fictional starter link  setup my schoolOS"
        opening_sha256 = hashlib.sha256(opening).hexdigest()
        initial = {
            "attempt_kind": "initial",
            "binding": binding,
            "opening_message_sha256": opening_sha256,
            "dispatch_state": "not_dispatched",
            "effect_state": "no_effect_proven",
            "evidence_state": "saved_verified",
        }
        result = authorize_single_no_dispatch_retry(
            [initial],
            expected_binding=binding,
            expected_opening_message_bytes=opening,
        )
        self.assertTrue(result["authorized"])
        self.assertEqual(result["next_attempt_kind"], "proven_no_dispatch_retry")
        retry = {
            "attempt_kind": "proven_no_dispatch_retry",
            "binding": binding,
            "opening_message_sha256": opening_sha256,
        }
        result = authorize_single_no_dispatch_retry(
            [initial, retry],
            expected_binding=binding,
            expected_opening_message_bytes=opening,
        )
        self.assertFalse(result["authorized"])
        self.assertEqual(result["state"], "single_retry_already_used")

    def test_retry_is_blocked_when_no_dispatch_is_not_proven(self):
        binding = self._controller_binding()
        opening = b"fictional starter link  setup my schoolOS"
        initial = {
            "attempt_kind": "initial",
            "binding": binding,
            "opening_message_sha256": hashlib.sha256(opening).hexdigest(),
            "dispatch_state": "unknown",
            "effect_state": "unknown",
            "evidence_state": "saved_verified",
        }
        result = authorize_single_no_dispatch_retry(
            [initial],
            expected_binding=binding,
            expected_opening_message_bytes=opening,
        )
        self.assertFalse(result["authorized"])
        self.assertEqual(result["state"], "no_dispatch_not_proven")

    def test_retry_is_blocked_when_opening_message_differs(self):
        binding = self._controller_binding()
        intended = b"fictional starter link  setup my schoolOS"
        changed = b"fictional starter link  setup my schoolOS please"
        initial = {
            "attempt_kind": "initial",
            "binding": binding,
            "opening_message_sha256": hashlib.sha256(changed).hexdigest(),
            "dispatch_state": "not_dispatched",
            "effect_state": "no_effect_proven",
            "evidence_state": "saved_verified",
        }
        result = authorize_single_no_dispatch_retry(
            [initial],
            expected_binding=binding,
            expected_opening_message_bytes=intended,
        )
        self.assertFalse(result["authorized"])
        self.assertEqual(result["state"], "opening_message_mismatch")

    def test_call_schema_rejects_query_object_when_string_is_required(self):
        signature = {
            "required": {"query": "string"},
            "optional": {"page_token": "string"},
        }
        result = validate_call_schema(signature, {"query": {"text": "school"}})
        self.assertEqual(result["status"], "invalid")
        self.assertEqual(result["diagnostics"][0]["code"], "wrong_argument_type")

    def test_call_schema_rejects_attachment_read_without_required_message_id(self):
        signature = {
            "required": {"message_id": "string", "attachment_id": "string"},
            "optional": {},
        }
        result = validate_call_schema(signature, {"attachment_id": "attachment_fictional"})
        self.assertEqual(result["status"], "invalid")
        self.assertEqual(
            result["diagnostics"],
            [{
                "code": "missing_required_argument",
                "path": "arguments.message_id",
            }],
        )

    def test_call_schema_enforces_declared_locator_exclusivity(self):
        signature = {
            "required": {"query": "string"},
            "optional": {"message_id": "string", "thread_id": "string"},
            "mutually_exclusive": [["message_id", "thread_id"]],
        }
        invalid = validate_call_schema(signature, {
            "query": "school",
            "message_id": "message_fictional",
            "thread_id": "thread_fictional",
        })
        self.assertEqual(invalid["status"], "invalid")
        self.assertEqual(
            invalid["diagnostics"][0]["code"],
            "mutually_exclusive_arguments",
        )
        self.assertEqual(
            validate_call_schema(signature, {"query": "school"})["status"],
            "valid",
        )

    def test_call_schema_rejects_nonstring_argument_name(self):
        result = validate_call_schema(
            {"required": {}, "optional": {"query": "string"}},
            {1: "not a JSON argument name"},
        )
        self.assertEqual(result["status"], "invalid")
        self.assertEqual(result["diagnostics"][0]["code"], "invalid_argument_name")

    def test_source_oracle_uses_exact_half_open_boundary(self):
        manifest = self._round_manifest_bytes()
        source_input = self._source_input_bytes()
        oracle = self._source_oracle(manifest, source_input)
        oracle["entries"].append({
            "source_alias": "same_start_different_supported_zone_and_precision",
            "arrival_timestamp": {
                "value": "2031-09-09T10:53:48.000-07:00",
                "timezone": "-07:00",
                "precision": "millisecond",
                "meaning": "received",
            },
        })
        result = preflight_source_oracle(oracle, manifest, source_input)
        self.assertEqual(result["status"], "ready")
        self.assertEqual(
            [item["source_alias"] for item in result["in_scope_entries"]],
            ["at_start", "same_start_different_supported_zone_and_precision"],
        )
        self.assertEqual(
            [item["source_alias"] for item in result["excluded_entries"]],
            ["at_end"],
        )

    def test_source_oracle_cannot_be_reused_for_another_manifest_or_interval(self):
        manifest = self._round_manifest_bytes()
        source_input = self._source_input_bytes()
        oracle = self._source_oracle(manifest, source_input)
        other = self._round_manifest_bytes({
            "start": "2031-09-10T17:53:48Z",
            "end": "2031-09-17T17:53:48Z",
            "timezone": "UTC",
            "precision": "second",
            "boundary": "[start,end)",
        })
        self.assertEqual(
            preflight_source_oracle(oracle, other, source_input)["reason"],
            "round_manifest_mismatch",
        )

        exact_bytes_different_interval = self._round_manifest_bytes()
        rebound = self._source_oracle(exact_bytes_different_interval, source_input)
        rebound["source_interval"] = {
            **rebound["source_interval"],
            "start": "2031-09-10T17:53:48Z",
        }
        self.assertEqual(
            preflight_source_oracle(
                rebound, exact_bytes_different_interval, source_input,
            )["reason"],
            "source_interval_mismatch",
        )

    def test_source_oracle_requires_exhaustion_and_comparable_arrival_time(self):
        manifest = self._round_manifest_bytes()
        source_input = self._source_input_bytes()
        oracle = self._source_oracle(manifest, source_input)
        oracle["enumeration_chains"][1]["pages"][-1][
            "observed_next_token"
        ] = "more-results"
        self.assertEqual(
            preflight_source_oracle(oracle, manifest, source_input)["reason"],
            "enumeration_chain_not_exhausted",
        )

        oracle = self._source_oracle(manifest, source_input)
        del oracle["entries"][0]["arrival_timestamp"]
        self.assertEqual(
            preflight_source_oracle(oracle, manifest, source_input)["reason"],
            "comparable_arrival_timestamp_missing",
        )

    def test_source_oracle_rejects_tampered_or_missing_receipt(self):
        manifest = self._round_manifest_bytes()
        source_input = self._source_input_bytes()
        oracle = self._source_oracle(manifest, source_input)
        oracle["enumeration_chains"][0]["pages"][0]["receipt_bytes"] = b"tampered"
        self.assertEqual(
            preflight_source_oracle(oracle, manifest, source_input)["reason"],
            "enumeration_receipt_digest_mismatch",
        )

        oracle = self._source_oracle(manifest, source_input)
        del oracle["enumeration_chains"][0]["pages"][0]["receipt_bytes"]
        self.assertEqual(
            preflight_source_oracle(oracle, manifest, source_input)["reason"],
            "enumeration_receipt_missing",
        )

    def test_source_oracle_rejects_source_input_mismatch(self):
        manifest = self._round_manifest_bytes()
        original = self._source_input_bytes()
        changed = self._source_input_bytes(["query_fictional_changed"])
        oracle = self._source_oracle(manifest, original)
        self.assertEqual(
            preflight_source_oracle(oracle, manifest, changed)["reason"],
            "source_input_mismatch",
        )

    def test_source_oracle_requires_every_query_chain_once(self):
        manifest = self._round_manifest_bytes()
        source_input = self._source_input_bytes()
        oracle = self._source_oracle(manifest, source_input)
        oracle["enumeration_chains"].pop()
        self.assertEqual(
            preflight_source_oracle(oracle, manifest, source_input)["reason"],
            "required_enumeration_query_alias_missing",
        )

        oracle = self._source_oracle(manifest, source_input)
        oracle["enumeration_chains"].append(dict(oracle["enumeration_chains"][0]))
        self.assertEqual(
            preflight_source_oracle(oracle, manifest, source_input)["reason"],
            "duplicate_enumeration_query_alias",
        )

    def test_source_oracle_rejects_whitespace_only_query_alias(self):
        manifest = self._round_manifest_bytes()
        source_input = self._source_input_bytes(["   "])
        oracle = {
            "round_manifest_sha256": hashlib.sha256(manifest).hexdigest(),
            "source_input_sha256": hashlib.sha256(source_input).hexdigest(),
        }
        with self.assertRaisesRegex(ValueError, "unique nonempty"):
            preflight_source_oracle(oracle, manifest, source_input)

    def test_source_interval_shape_is_exact(self):
        manifest = self._round_manifest_bytes()
        source_input = self._source_input_bytes()
        oracle = self._source_oracle(manifest, source_input)
        oracle["source_interval"]["provider_hint"] = "not part of the binding"
        with self.assertRaisesRegex(ValueError, "exact interval fields"):
            preflight_source_oracle(oracle, manifest, source_input)

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
        binding = self._report_binding(artifact)
        self.assertEqual(bind_report_artifact(binding, artifact)["status"], "task_bound")
        binding["events"]["export_action"]["observed"] = False
        self.assertEqual(bind_report_artifact(binding, artifact)["status"], "visible_output_only")

    def test_report_digest_or_byte_count_mismatch_uses_visible_output_only(self):
        artifact = b"fictional task-bound report"
        binding = self._report_binding(artifact)
        binding["events"]["provider_receipt"]["artifact_sha256"] = "0" * 64
        result = bind_report_artifact(binding, artifact)
        self.assertEqual(result["status"], "visible_output_only")
        self.assertFalse(result["digest_matches"])

        binding = self._report_binding(artifact)
        binding["events"]["provider_receipt"]["artifact_byte_count"] += 1
        result = bind_report_artifact(binding, artifact)
        self.assertEqual(result["status"], "visible_output_only")
        self.assertFalse(result["byte_count_matches"])

    def test_report_missing_exact_receipt_binding_uses_visible_output_only(self):
        artifact = b"fictional task-bound report"
        binding = self._report_binding(artifact)
        del binding["events"]["provider_receipt"]["artifact_sha256"]
        del binding["events"]["provider_receipt"]["artifact_byte_count"]
        result = bind_report_artifact(binding, artifact)
        self.assertEqual(result["status"], "visible_output_only")
        self.assertFalse(result["receipt_artifact_bound"])

    def test_report_boolean_receipt_byte_count_is_not_an_integer_binding(self):
        artifact = b"x"
        binding = self._report_binding(artifact)
        binding["events"]["provider_receipt"]["artifact_byte_count"] = True
        result = bind_report_artifact(binding, artifact)
        self.assertEqual(result["status"], "visible_output_only")
        self.assertFalse(result["byte_count_matches"])

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
