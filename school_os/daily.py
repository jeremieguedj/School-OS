"""Shared sequential daily-operation runner for manual and scheduled entrypoints."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from math import ceil, isfinite
from time import monotonic
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


def _nonnegative_int(value: Any, label: str, *, positive: bool = False) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < (1 if positive else 0):
        requirement = "positive" if positive else "nonnegative"
        raise DailyError(f"{label} must be a {requirement} integer")
    return value


def _elapsed_ms(started: float, monotonic_clock: Callable[[], float]) -> int:
    current = monotonic_clock()
    if (
        isinstance(started, bool)
        or isinstance(current, bool)
        or not isinstance(started, (int, float))
        or not isinstance(current, (int, float))
        or not isfinite(started)
        or not isfinite(current)
        or current < started
    ):
        raise DailyError("daily monotonic clock returned invalid elapsed evidence")
    return ceil((current - started) * 1000)


def _durable_checkpoint_reference(
    checkpoint: Callable[[str, Mapping[str, Any], str], str | None] | None,
    phase: str,
    result: Mapping[str, Any],
    outcome: str,
) -> str:
    if checkpoint is None:
        raise DailyError("NEEDS_CONTINUATION requires a durable checkpoint")
    reference = checkpoint(phase, result, outcome)
    if not isinstance(reference, str) or not reference:
        raise DailyError("NEEDS_CONTINUATION requires a durable checkpoint reference")
    return reference


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
    max_elapsed_ms: int | None = None,
    estimated_phase_ms: Mapping[str, int] | None = None,
    monotonic_clock: Callable[[], float] = monotonic,
    reserve_ms: int = 0,
) -> OperationResult:
    """Run every required phase once, passing verified predecessor output onward.

    Admission is capability-led before a stage can run. A scheduled entrypoint
    has one additional scheduler-admission gate; direct manual runs never
    inspect or request scheduler capability. Individual stages own their
    persisted artifacts and return ``verified: true`` only after readback.
    """
    started = monotonic_clock()
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
    if max_elapsed_ms is not None:
        max_elapsed_ms = _nonnegative_int(
            max_elapsed_ms, "daily elapsed budget", positive=True
        )
        if not isinstance(estimated_phase_ms, Mapping):
            raise DailyError("daily budget requires measured next-phase estimates")
    reserve_ms = _nonnegative_int(reserve_ms, "daily budget reserve")
    start = 0 if resume_after is None else PHASES.index(resume_after) + 1
    if start and durable_predecessor_output is None:
        raise DailyError("resumption requires durable predecessor output")
    if start and durable_predecessor_output.get("verified") is not True:
        raise DailyError("resumption requires verified durable predecessor output")
    outputs: dict[str, dict[str, Any]] = {}
    previous: Mapping[str, Any] = durable_predecessor_output or {}
    for phase in PHASES[start:]:
        stage = stages.get(phase)
        if stage is None:
            raise DailyError(f"missing required daily phase: {phase}")
        if max_elapsed_ms is not None:
            if phase not in estimated_phase_ms:
                raise DailyError("daily budget requires a measured next-phase estimate")
            estimate = _nonnegative_int(
                estimated_phase_ms[phase], "daily phase estimate"
            )
            elapsed_ms = _elapsed_ms(started, monotonic_clock)
        else:
            estimate = 0
            elapsed_ms = 0
        if max_elapsed_ms is not None and elapsed_ms + estimate + reserve_ms >= max_elapsed_ms:
            if not outputs:
                raise DailyError("daily budget cannot complete the next minimum unit")
            prior_phase = PHASES[PHASES.index(phase) - 1]
            reference = _durable_checkpoint_reference(
                checkpoint, prior_phase, previous, "needs_continuation"
            )
            _elapsed_ms(started, monotonic_clock)
            return OperationResult(
                "NEEDS_CONTINUATION", operation_id, attempt_id, entrypoint,
                prior_phase, reference, "measured budget boundary before next phase",
                tuple(PHASES[: PHASES.index(phase)]), outputs,
            )
        result = dict(stage(previous))
        if result.get("verified") is not True:
            raise DailyError(f"daily phase is not verified: {phase}")
        if start and require_progress_after_resume and result.get("progressed") is False:
            raise DailyError("resumed operation made no progress at its minimum unit")
        outputs[phase] = result
        previous = result
        checkpoint_reference = checkpoint(phase, result, "running") if checkpoint else None
        if phase == stop_after:
            checkpoint_reference = _durable_checkpoint_reference(
                checkpoint, phase, result, "needs_continuation"
            )
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
