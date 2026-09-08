"""Shared sequential daily-operation runner for manual and scheduled entrypoints."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from .capabilities import qualify_execution


class DailyError(ValueError):
    """Raised when a required daily phase cannot safely complete."""


PHASES = (
    "preflight",
    "discover",
    "catalog",
    "reconcile",
    "task_sync",
    "brief_delivery",
    "commit",
)
Stage = Callable[[Mapping[str, Any]], Mapping[str, Any]]


@dataclass(frozen=True)
class OperationResult:
    """A terminal in-memory result; durable checkpoints remain adapter-owned."""

    outcome: str
    operation_id: str
    attempt_id: str
    entrypoint: str
    current_phase: str
    checkpoint_reference: str | None
    reason: str
    completed_phases: tuple[str, ...]
    outputs: dict[str, dict[str, Any]]


def run_daily(
    *,
    profile: dict[str, Any],
    capability_schema: dict[str, Any],
    entrypoint: str,
    operation_id: str,
    attempt_id: str,
    stages: Mapping[str, Stage],
    scheduler_admission: Callable[[], bool] | None = None,
    resume_after: str | None = None,
    durable_predecessor_output: Mapping[str, Any] | None = None,
    stop_after: str | None = None,
    checkpoint: Callable[[str, Mapping[str, Any], str], str | None] | None = None,
    require_progress_after_resume: bool = False,
) -> OperationResult:
    """Run every required phase once, passing verified predecessor output onward.

    Admission is capability-led before a stage can run. A scheduled entrypoint
    has one additional scheduler-admission gate; direct manual runs never
    inspect or request scheduler capability. Individual stages own their
    persisted artifacts and return ``verified: true`` only after readback.
    """
    if not operation_id or not attempt_id:
        raise DailyError("daily operation and attempt identities are required")
    qualify_execution(profile, capability_schema, operation="daily-run", entrypoint=entrypoint)
    if entrypoint == "scheduled" and (
        scheduler_admission is None or not scheduler_admission()
    ):
        raise DailyError("scheduled entrypoint requires verified scheduler admission")

    if resume_after is not None and resume_after not in PHASES:
        raise DailyError("unknown daily resume phase")
    if stop_after is not None and stop_after not in PHASES:
        raise DailyError("unknown planned daily stop phase")
    start = 0 if resume_after is None else PHASES.index(resume_after) + 1
    if start and durable_predecessor_output is None:
        raise DailyError("resumption requires durable predecessor output")
    outputs: dict[str, dict[str, Any]] = {}
    previous: Mapping[str, Any] = durable_predecessor_output or {}
    for phase in PHASES[start:]:
        stage = stages.get(phase)
        if stage is None:
            raise DailyError(f"missing required daily phase: {phase}")
        result = dict(stage(previous))
        if result.get("verified") is not True:
            raise DailyError(f"daily phase is not verified: {phase}")
        if start and require_progress_after_resume and result.get("progressed") is False:
            raise DailyError("resumed operation made no progress at its minimum unit")
        outputs[phase] = result
        previous = result
        checkpoint_reference = checkpoint(phase, result, "running") if checkpoint else None
        if phase == stop_after:
            return OperationResult(
                outcome="NEEDS_CONTINUATION", operation_id=operation_id, attempt_id=attempt_id,
                entrypoint=entrypoint, current_phase=phase, checkpoint_reference=checkpoint_reference,
                reason="planned boundary after verified phase", completed_phases=tuple(PHASES[: PHASES.index(phase) + 1]),
                outputs=outputs,
            )

    return OperationResult(
        outcome="COMPLETE",
        operation_id=operation_id,
        attempt_id=attempt_id,
        entrypoint=entrypoint,
        current_phase="commit",
        checkpoint_reference=None,
        reason="all required daily phases verified",
        completed_phases=PHASES,
        outputs=outputs,
    )
