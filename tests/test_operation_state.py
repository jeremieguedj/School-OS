from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from school_os.operations import (  # noqa: E402
    OperationError,
    checkpoint_pointer,
    discover_recovery_chain,
    resume_from_chain,
    validate_checkpoint_chain,
    validate_operation_state,
    validate_transition,
)


class OperationStateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.state_schema = json.loads((ROOT / "schemas" / "operation-state.schema.json").read_text())
        cls.checkpoint_schema = json.loads((ROOT / "schemas" / "operation-checkpoint.schema.json").read_text())
        cls.idle = json.loads((ROOT / "templates" / "state" / "operation-state.json").read_text())

    def checkpoint(
        self,
        *,
        sequence: int = 0,
        predecessor: dict | None = None,
        attempt_id: str = "attempt-001",
        completed_phases: list[str] | None = None,
        remaining_work: dict | None = None,
        effects: list[dict] | None = None,
        blocker: dict | None = None,
    ) -> dict:
        return {
            "schema_version": 1,
            "checkpoint_id": f"checkpoint-{sequence:03d}",
            "operation_id": "daily-run-20260907",
            "attempt_id": attempt_id,
            "pinned_release": {"version": "0.1.0-alpha.13", "source_commit": "a" * 40},
            "scope": {"window": "2026-09-07"},
            "configuration_fingerprint": "b" * 64,
            "phase": "catalogue",
            "completed_phases": completed_phases or ["preflight"],
            "completed_units": ["preflight"],
            "remaining_work": remaining_work if remaining_work is not None else {"phase": "catalogue"},
            "artifacts": [],
            "effects": effects or [],
            "verification": {"readback": "synthetic"},
            "blocker": blocker,
            "predecessor": predecessor,
            "sequence": sequence,
        }

    def active_state(self, checkpoint: dict, status: str = "running") -> dict:
        return {
            "schema_version": 1,
            "status": status,
            "current_operation": {"operation_id": checkpoint["operation_id"], "attempt_id": checkpoint["attempt_id"]},
            "serialization": {"mode": "attended_single_writer", "evidence": {"actor": "synthetic"}},
            "checkpoint": checkpoint_pointer(checkpoint),
            "last_terminal": None,
        }

    def terminal_state(self, checkpoint: dict, status: str = "complete") -> dict:
        return {
            "schema_version": 1,
            "status": status,
            "current_operation": None,
            "serialization": None,
            "checkpoint": None,
            "last_terminal": {
                "operation_id": checkpoint["operation_id"],
                "status": status,
                "checkpoint": checkpoint_pointer(checkpoint),
                "reason": "all required evidence verified" if status == "complete" else "explicit cancellation",
            },
        }

    def test_template_is_an_empty_admission_pointer(self) -> None:
        validate_operation_state(self.idle, self.state_schema)

    def test_hybrid_content_bundle_artifact_reference_is_admitted(self) -> None:
        checkpoint = self.checkpoint()
        checkpoint["artifacts"] = [{
            "kind": "source_bundle",
            "identity": "source-000001",
            "reference": {
                "object_id": "drive-source-1",
                "kind": "file",
                "permitted_ancestor_id": "drive-root-1",
                "mime_type": "application/x-tar",
                "version": "2026-09-10T00:00:00Z",
            },
            "sha256": "c" * 64,
        }]
        validate_transition(
            self.idle,
            self.active_state(checkpoint),
            checkpoint,
            state_schema=self.state_schema,
            checkpoint_schema=self.checkpoint_schema,
        )

        invalid = copy.deepcopy(checkpoint)
        invalid["artifacts"][0]["reference"].pop("version")
        with self.assertRaises(OperationError):
            validate_transition(
                self.idle,
                self.active_state(invalid),
                invalid,
                state_schema=self.state_schema,
                checkpoint_schema=self.checkpoint_schema,
            )

    def test_legal_running_continuation_and_complete_transitions_validate(self) -> None:
        first = self.checkpoint()
        running = self.active_state(first)
        validate_transition(None, running, first, state_schema=self.state_schema, checkpoint_schema=self.checkpoint_schema)

        second = self.checkpoint(sequence=1, predecessor=checkpoint_pointer(first))
        continuation = self.active_state(second, "needs_continuation")
        validate_transition(running, continuation, second, state_schema=self.state_schema, checkpoint_schema=self.checkpoint_schema)

        resumed = self.checkpoint(
            sequence=2,
            predecessor=checkpoint_pointer(second),
            attempt_id="attempt-002",
        )
        resumed_running = self.active_state(resumed)
        validate_transition(
            continuation,
            resumed_running,
            resumed,
            state_schema=self.state_schema,
            checkpoint_schema=self.checkpoint_schema,
        )

        final = self.checkpoint(
            sequence=3,
            predecessor=checkpoint_pointer(resumed),
            attempt_id="attempt-002",
            completed_phases=["preflight", "catalogue"],
            remaining_work={},
            effects=[{"effect_id": "write-001", "kind": "storage.replace", "outcome": "confirmed", "verification": {"readback": "exact"}}],
        )
        complete = self.terminal_state(final)
        validate_transition(
            resumed_running,
            complete,
            final,
            state_schema=self.state_schema,
            checkpoint_schema=self.checkpoint_schema,
            required_phases=("preflight", "catalogue"),
        )
        validate_checkpoint_chain([first, second, resumed, final], self.checkpoint_schema)

    def test_illegal_skip_from_idle_to_complete_fails(self) -> None:
        checkpoint = self.checkpoint(completed_phases=["preflight", "catalogue"], remaining_work={})
        with self.assertRaisesRegex(OperationError, "illegal operation transition"):
            validate_transition(
                self.idle,
                self.terminal_state(checkpoint),
                checkpoint,
                state_schema=self.state_schema,
                checkpoint_schema=self.checkpoint_schema,
                required_phases=("preflight", "catalogue"),
            )

    def test_completion_with_pending_phase_or_effect_fails(self) -> None:
        first = self.checkpoint()
        running = self.active_state(first)
        pending_phase = self.checkpoint(sequence=1, predecessor=checkpoint_pointer(first), remaining_work={})
        with self.assertRaisesRegex(OperationError, "missing required phase"):
            validate_transition(
                running,
                self.terminal_state(pending_phase),
                pending_phase,
                state_schema=self.state_schema,
                checkpoint_schema=self.checkpoint_schema,
                required_phases=("preflight", "catalogue"),
            )
        pending_effect = self.checkpoint(
            sequence=1,
            predecessor=checkpoint_pointer(first),
            completed_phases=["preflight", "catalogue"],
            remaining_work={},
            effects=[{"effect_id": "send-001", "kind": "mail.send", "outcome": "unknown", "verification": {}}],
        )
        with self.assertRaisesRegex(OperationError, "pending or unknown effects"):
            validate_transition(
                running,
                self.terminal_state(pending_effect),
                pending_effect,
                state_schema=self.state_schema,
                checkpoint_schema=self.checkpoint_schema,
                required_phases=("preflight", "catalogue"),
            )

    def test_corrupt_predecessor_chain_fails(self) -> None:
        first = self.checkpoint()
        corrupt = self.checkpoint(sequence=1, predecessor={"checkpoint_id": first["checkpoint_id"], "sha256": "0" * 64})
        with self.assertRaisesRegex(OperationError, "predecessor reference/hash"):
            validate_checkpoint_chain([first, corrupt], self.checkpoint_schema)

    def test_terminal_and_active_state_shape_rejects_stale_admission_data(self) -> None:
        checkpoint = self.checkpoint(completed_phases=["preflight", "catalogue"], remaining_work={})
        terminal = self.terminal_state(checkpoint)
        terminal["checkpoint"] = checkpoint_pointer(checkpoint)
        with self.assertRaisesRegex(OperationError, "terminal state must clear"):
            validate_operation_state(terminal, self.state_schema)

    def test_recovery_selects_one_longest_chain_and_requires_a_new_attempt(self) -> None:
        first = self.checkpoint()
        paused_checkpoint = self.checkpoint(sequence=1, predecessor=checkpoint_pointer(first))
        paused = self.active_state(paused_checkpoint, "needs_continuation")
        chain = discover_recovery_chain([first, paused_checkpoint], first["operation_id"], self.checkpoint_schema)
        resumed = self.checkpoint(sequence=2, predecessor=checkpoint_pointer(paused_checkpoint), attempt_id="attempt-002")
        resume_from_chain(paused, chain, resumed, state_schema=self.state_schema, checkpoint_schema=self.checkpoint_schema)
        with self.assertRaisesRegex(OperationError, "new attempt_id"):
            resume_from_chain(paused, chain, self.checkpoint(sequence=2, predecessor=checkpoint_pointer(paused_checkpoint)), state_schema=self.state_schema, checkpoint_schema=self.checkpoint_schema)

    def test_ambiguous_longest_recovery_chain_blocks(self) -> None:
        first = self.checkpoint()
        left = self.checkpoint(sequence=1, predecessor=checkpoint_pointer(first))
        right = copy.deepcopy(left)
        right["checkpoint_id"] = "checkpoint-other"
        with self.assertRaisesRegex(OperationError, "ambiguous"):
            discover_recovery_chain([first, left, right], first["operation_id"], self.checkpoint_schema)

    def test_recovery_blocks_material_release_or_configuration_drift_and_cancel_with_unknown_effect(self) -> None:
        first = self.checkpoint()
        paused = self.active_state(first, "needs_continuation")
        chain = discover_recovery_chain([first], first["operation_id"], self.checkpoint_schema)
        resumed = self.checkpoint(sequence=1, predecessor=checkpoint_pointer(first), attempt_id="attempt-002")
        resume_from_chain(paused, chain, resumed, state_schema=self.state_schema, checkpoint_schema=self.checkpoint_schema, pinned_release=first["pinned_release"], configuration_fingerprint=first["configuration_fingerprint"])
        with self.assertRaisesRegex(OperationError, "release changed"):
            resume_from_chain(paused, chain, resumed, state_schema=self.state_schema, checkpoint_schema=self.checkpoint_schema, pinned_release={"version": "changed", "source_commit": "a" * 40})
        unknown = self.checkpoint(effects=[{"effect_id": "send", "kind": "mail.send", "outcome": "unknown", "verification": {}}])
        with self.assertRaisesRegex(OperationError, "pending or unknown"):
            validate_transition(self.active_state(unknown), self.terminal_state(unknown, "cancelled"), unknown, state_schema=self.state_schema, checkpoint_schema=self.checkpoint_schema)


if __name__ == "__main__":
    unittest.main()
