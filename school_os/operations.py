"""Deterministic validation for durable operation admission and checkpoints.

This module intentionally owns only the state-machine and immutable-chain
rules.  Provider writes, effect reconciliation, and daily phases are added by
later M2 tasks, but they must use these same validation gates.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from .contracts import canonical_json_bytes, sha256_bytes, validate


class OperationError(ValueError):
    """Raised when durable operation state is invalid or unsafe to advance."""


ACTIVE_STATUSES = frozenset({"running", "needs_continuation", "blocked"})
TERMINAL_STATUSES = frozenset({"complete", "cancelled"})
PENDING_EFFECT_OUTCOMES = frozenset({"pending", "unknown"})


@dataclass(frozen=True)
class RecoveryChain:
    """The one unambiguous, longest durable checkpoint chain for an operation."""

    operation_id: str
    checkpoints: tuple[dict[str, Any], ...]

    @property
    def tip(self) -> dict[str, Any]:
        return self.checkpoints[-1]


def checkpoint_sha256(checkpoint: Mapping[str, Any]) -> str:
    """Return the hash of the full canonical immutable checkpoint bytes."""
    return sha256_bytes(canonical_json_bytes(dict(checkpoint)))


def checkpoint_pointer(checkpoint: Mapping[str, Any]) -> dict[str, str]:
    """Return the durable pointer evidence for a checkpoint."""
    checkpoint_id = checkpoint.get("checkpoint_id")
    if not isinstance(checkpoint_id, str) or not checkpoint_id:
        raise OperationError("checkpoint must have a non-empty checkpoint_id")
    return {"checkpoint_id": checkpoint_id, "sha256": checkpoint_sha256(checkpoint)}


def _require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise OperationError(f"{label} must be an object")
    return value


def _raise_schema_errors(value: Any, schema: Mapping[str, Any], label: str) -> None:
    errors = validate(value, dict(schema))
    if errors:
        raise OperationError(f"invalid {label}: " + "; ".join(errors))


def validate_checkpoint(checkpoint: Mapping[str, Any], schema: Mapping[str, Any]) -> None:
    """Validate one checkpoint independently of any predecessor chain."""
    _raise_schema_errors(checkpoint, schema, "operation checkpoint")
    effect_ids = [effect["effect_id"] for effect in checkpoint["effects"]]
    if len(effect_ids) != len(set(effect_ids)):
        raise OperationError("operation checkpoint effect_id values must be unique")
    if checkpoint["blocker"] is not None and checkpoint["remaining_work"] == {}:
        raise OperationError("blocked checkpoint must retain the work needed for recovery")


def validate_checkpoint_chain(
    checkpoints: Sequence[Mapping[str, Any]], checkpoint_schema: Mapping[str, Any]
) -> None:
    """Validate a single exact predecessor chain in increasing sequence order."""
    if not checkpoints:
        raise OperationError("checkpoint chain must contain an admission checkpoint")
    operation_id: str | None = None
    previous: Mapping[str, Any] | None = None
    seen_ids: set[str] = set()
    for position, checkpoint in enumerate(checkpoints):
        validate_checkpoint(checkpoint, checkpoint_schema)
        checkpoint_id = checkpoint["checkpoint_id"]
        if checkpoint_id in seen_ids:
            raise OperationError("checkpoint chain contains duplicate checkpoint_id")
        seen_ids.add(checkpoint_id)
        if operation_id is None:
            operation_id = checkpoint["operation_id"]
        elif checkpoint["operation_id"] != operation_id:
            raise OperationError("checkpoint chain must retain one operation_id")
        if checkpoint["sequence"] != position:
            raise OperationError("checkpoint chain sequence must start at zero and increase by one")
        if previous is None:
            if checkpoint["predecessor"] is not None:
                raise OperationError("first checkpoint must not declare a predecessor")
        else:
            expected = checkpoint_pointer(previous)
            if checkpoint["predecessor"] != expected:
                raise OperationError("checkpoint predecessor reference/hash does not match verified predecessor")
        previous = checkpoint


def discover_recovery_chain(
    checkpoints: Sequence[Mapping[str, Any]], operation_id: str, checkpoint_schema: Mapping[str, Any]
) -> RecoveryChain:
    """Select one valid longest chain or fail rather than guessing after a reset."""
    candidates = [dict(item) for item in checkpoints if item.get("operation_id") == operation_id]
    if not candidates:
        raise OperationError("no checkpoint was found for the active operation")
    by_pointer: dict[tuple[str, str], dict[str, Any]] = {}
    successors: set[tuple[str, str]] = set()
    for checkpoint in candidates:
        validate_checkpoint(checkpoint, checkpoint_schema)
        pointer = checkpoint_pointer(checkpoint)
        key = (pointer["checkpoint_id"], pointer["sha256"])
        if key in by_pointer:
            raise OperationError("recovery checkpoint search found duplicate immutable pointers")
        by_pointer[key] = checkpoint
        predecessor = checkpoint["predecessor"]
        if predecessor is not None:
            successors.add((predecessor["checkpoint_id"], predecessor["sha256"]))
    leaves = [pointer for pointer in by_pointer if pointer not in successors]
    chains: list[list[dict[str, Any]]] = []
    for leaf in leaves:
        reversed_chain: list[dict[str, Any]] = []
        pointer: tuple[str, str] | None = leaf
        while pointer is not None:
            checkpoint = by_pointer.get(pointer)
            if checkpoint is None:
                reversed_chain = []
                break
            reversed_chain.append(checkpoint)
            predecessor = checkpoint["predecessor"]
            pointer = None if predecessor is None else (predecessor["checkpoint_id"], predecessor["sha256"])
        if reversed_chain:
            chain = list(reversed(reversed_chain))
            try:
                validate_checkpoint_chain(chain, checkpoint_schema)
            except OperationError:
                continue
            chains.append(chain)
    if not chains:
        raise OperationError("no valid immutable checkpoint chain was found")
    longest = max(len(chain) for chain in chains)
    winners = [chain for chain in chains if len(chain) == longest]
    if len(winners) != 1:
        raise OperationError("recovery checkpoint search is ambiguous at the longest chain")
    return RecoveryChain(operation_id, tuple(winners[0]))


def resume_from_chain(
    state: Mapping[str, Any], chain: RecoveryChain, checkpoint: Mapping[str, Any], *,
    state_schema: Mapping[str, Any], checkpoint_schema: Mapping[str, Any],
    pinned_release: Mapping[str, Any] | None = None, configuration_fingerprint: str | None = None,
) -> None:
    """Validate that a new attempt resumes the selected durable chain exactly."""
    validate_operation_state(state, state_schema)
    if state["status"] not in {"needs_continuation", "blocked"}:
        raise OperationError("only a paused or blocked operation may be resumed")
    current = _require_mapping(state["current_operation"], "current_operation")
    if current["operation_id"] != chain.operation_id:
        raise OperationError("recovery chain does not match the active operation")
    validate_checkpoint(checkpoint, checkpoint_schema)
    if checkpoint["operation_id"] != chain.operation_id:
        raise OperationError("resumed checkpoint must retain the active operation_id")
    if checkpoint["attempt_id"] == current["attempt_id"]:
        raise OperationError("resumption requires a new attempt_id")
    if checkpoint["predecessor"] != checkpoint_pointer(chain.tip):
        raise OperationError("resumed checkpoint must point to the recovered chain tip")
    if pinned_release is not None and chain.tip["pinned_release"] != dict(pinned_release):
        raise OperationError("recovery release changed and requires reconciliation")
    if configuration_fingerprint is not None and chain.tip["configuration_fingerprint"] != configuration_fingerprint:
        raise OperationError("recovery configuration changed and requires reconciliation")


def _validate_state_shape(state: Mapping[str, Any]) -> None:
    status = state["status"]
    current = state["current_operation"]
    serialization = state["serialization"]
    checkpoint = state["checkpoint"]
    terminal = state["last_terminal"]
    if status == "idle":
        if any(value is not None for value in (current, serialization, checkpoint, terminal)):
            raise OperationError("idle state must not retain an active or terminal operation pointer")
        return
    if status in ACTIVE_STATUSES:
        if not all(isinstance(value, Mapping) for value in (current, serialization, checkpoint)):
            raise OperationError(f"{status} state requires current operation, serialization, and checkpoint evidence")
        if terminal is not None:
            raise OperationError(f"{status} state must not retain a terminal summary")
        return
    if status in TERMINAL_STATUSES:
        if any(value is not None for value in (current, serialization, checkpoint)):
            raise OperationError("terminal state must clear active admission evidence")
        if not isinstance(terminal, Mapping):
            raise OperationError("terminal state requires a last_terminal summary")
        if terminal["status"] != status:
            raise OperationError("terminal summary status must match operation state")
        return
    raise OperationError(f"unsupported operation state status {status!r}")


def validate_operation_state(state: Mapping[str, Any], schema: Mapping[str, Any]) -> None:
    """Validate the durable admission pointer independent of a new transition."""
    _raise_schema_errors(state, schema, "operation state")
    _validate_state_shape(state)


def _operation_identity(state: Mapping[str, Any]) -> tuple[str, str] | None:
    current = state["current_operation"]
    if not isinstance(current, Mapping):
        return None
    return current["operation_id"], current["attempt_id"]


def _has_pending_effect(checkpoint: Mapping[str, Any]) -> bool:
    return any(effect["outcome"] in PENDING_EFFECT_OUTCOMES for effect in checkpoint["effects"])


def _terminal_pointer(state: Mapping[str, Any]) -> Mapping[str, Any]:
    terminal = _require_mapping(state["last_terminal"], "last_terminal")
    return _require_mapping(terminal["checkpoint"], "last_terminal.checkpoint")


def validate_transition(
    previous_state: Mapping[str, Any] | None,
    candidate_state: Mapping[str, Any],
    checkpoint: Mapping[str, Any],
    *,
    state_schema: Mapping[str, Any],
    checkpoint_schema: Mapping[str, Any],
    required_phases: Sequence[str] = (),
) -> None:
    """Validate one legal state transition bound to a verified checkpoint.

    ``required_phases`` is supplied by the selected operation recipe.  The
    state layer deliberately does not duplicate recipe phase policy.
    """
    if previous_state is not None:
        validate_operation_state(previous_state, state_schema)
    validate_operation_state(candidate_state, state_schema)
    validate_checkpoint(checkpoint, checkpoint_schema)

    previous_status = None if previous_state is None else previous_state["status"]
    target_status = candidate_state["status"]
    allowed = {
        None: {"running"},
        "idle": {"running"},
        "running": {"running", "needs_continuation", "blocked", "complete", "cancelled"},
        "needs_continuation": {"running", "blocked", "cancelled"},
        "blocked": {"running", "cancelled"},
        "complete": {"running"},
        "cancelled": {"running"},
    }
    if target_status not in allowed[previous_status]:
        raise OperationError(f"illegal operation transition {previous_status!r} -> {target_status!r}")

    checkpoint_identity = (checkpoint["operation_id"], checkpoint["attempt_id"])
    previous_identity = _operation_identity(previous_state) if previous_state is not None else None
    if target_status in ACTIVE_STATUSES:
        candidate_identity = _operation_identity(candidate_state)
        if candidate_identity != checkpoint_identity:
            raise OperationError("active operation identity must match checkpoint identity")
        if candidate_state["checkpoint"] != checkpoint_pointer(checkpoint):
            raise OperationError("active operation checkpoint pointer/hash does not match checkpoint bytes")
        if previous_status in {"running", "needs_continuation", "blocked"}:
            if previous_identity is None or previous_identity[0] != checkpoint_identity[0]:
                raise OperationError("resumed operation must retain its operation_id")
            if previous_status == "running" and previous_identity[1] != checkpoint_identity[1]:
                raise OperationError("running operation cannot change attempt_id")
            if previous_status in {"needs_continuation", "blocked"} and previous_identity[1] == checkpoint_identity[1]:
                raise OperationError("resumption requires a new attempt_id")
    else:
        terminal = _require_mapping(candidate_state["last_terminal"], "last_terminal")
        if terminal["operation_id"] != checkpoint["operation_id"]:
            raise OperationError("terminal summary operation_id must match checkpoint")
        if _terminal_pointer(candidate_state) != checkpoint_pointer(checkpoint):
            raise OperationError("terminal summary checkpoint pointer/hash does not match checkpoint bytes")
        if previous_identity is not None and previous_identity[0] != checkpoint_identity[0]:
            raise OperationError("terminal checkpoint must retain the active operation_id")

    if target_status == "needs_continuation" and not checkpoint["remaining_work"]:
        raise OperationError("needs_continuation requires explicit remaining_work")
    if target_status == "blocked" and checkpoint["blocker"] is None:
        raise OperationError("blocked transition requires specific blocker evidence")
    if target_status in TERMINAL_STATUSES:
        if _has_pending_effect(checkpoint):
            raise OperationError("terminal transition cannot leave pending or unknown effects")
        if target_status == "complete":
            missing = sorted(set(required_phases) - set(checkpoint["completed_phases"]))
            if missing:
                raise OperationError("complete transition is missing required phase(s): " + ", ".join(missing))
            if checkpoint["remaining_work"]:
                raise OperationError("complete transition cannot leave remaining_work")
            if checkpoint["blocker"] is not None:
                raise OperationError("complete transition cannot retain a blocker")
