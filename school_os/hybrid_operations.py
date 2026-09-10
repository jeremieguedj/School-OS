"""Atomic operation/checkpoint publication inside the current state bundle."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from .bundles import BundleMemberReference, BundlePeerReference, resolve_peer
from .connected_storage import BundleTransactionStore, ConnectedStorageError
from .contracts import canonical_json_bytes
from .operations import validate_transition


class HybridOperationError(ValueError):
    """Raised when an operation boundary cannot be published atomically."""


_CHECKPOINT_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,191}$")


@dataclass(frozen=True)
class HybridCheckpointCommit:
    transaction: BundleTransactionStore
    checkpoint_peer: BundlePeerReference
    checkpoint_reference: BundleMemberReference
    operation_state_reference: BundleMemberReference


class HybridCheckpointPublisher:
    """Stage checkpoint/state peers together, then advance CURRENT once."""

    def __init__(
        self, transaction: BundleTransactionStore, *,
        state_schema: Mapping[str, Any], checkpoint_schema: Mapping[str, Any],
        operation_state_path: str = "state/operation-state.json",
    ) -> None:
        self.transaction = transaction
        self.state_schema = dict(state_schema)
        self.checkpoint_schema = dict(checkpoint_schema)
        self.operation_state_path = operation_state_path

    def commit(
        self, *, storage: Any, checkpoint: Mapping[str, Any],
        operation_state: Mapping[str, Any], serialization: Mapping[str, Any],
        required_phases: Sequence[str] = (),
    ) -> HybridCheckpointCommit:
        checkpoint_id = checkpoint.get("checkpoint_id")
        if not isinstance(checkpoint_id, str) or _CHECKPOINT_ID.fullmatch(checkpoint_id) is None:
            raise HybridOperationError("hybrid checkpoint identity is unsafe")
        checkpoint_path = f"state/operation-checkpoints/{checkpoint_id}.json"
        if checkpoint_path in self.transaction.working.entries:
            raise HybridOperationError("hybrid checkpoint identity already exists")
        prior_bytes = self.transaction.read(self.operation_state_path).data
        try:
            prior = json.loads(prior_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise HybridOperationError("hybrid operation state is not UTF-8 JSON") from exc
        if not isinstance(prior, dict) or canonical_json_bytes(prior) != prior_bytes:
            raise HybridOperationError("hybrid operation state is not canonical JSON")
        checkpoint_bytes = canonical_json_bytes(dict(checkpoint))
        state_bytes = canonical_json_bytes(dict(operation_state))
        validate_transition(
            prior, operation_state, checkpoint,
            state_schema=self.state_schema,
            checkpoint_schema=self.checkpoint_schema,
            required_phases=required_phases,
        )
        staged = self.transaction.stage(
            checkpoint_path, checkpoint_bytes, role="operation_checkpoint",
            media_type="application/json", schema_id="operation-checkpoint.schema.json",
        ).stage(self.operation_state_path, state_bytes)
        checkpoint_peer = staged.read(checkpoint_path).reference
        committed = staged.publish(storage, serialization)
        carrier = committed.working.recovery["state"]
        if (
            resolve_peer(checkpoint_peer, carrier) != checkpoint_bytes
            or committed.read(self.operation_state_path).data != state_bytes
        ):
            raise HybridOperationError("hybrid checkpoint publication readback differs")
        try:
            checkpoint_reference = committed.durable_reference(checkpoint_path)
            state_reference = committed.durable_reference(self.operation_state_path)
        except ConnectedStorageError as exc:
            raise HybridOperationError("hybrid publication did not become durable") from exc
        return HybridCheckpointCommit(
            committed, checkpoint_peer, checkpoint_reference, state_reference,
        )
