"""Fail-closed capability qualification and conservative execution planning."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .contracts import validate


class CapabilityError(ValueError):
    """Raised with the named capability or observation blocking execution."""


MANUAL_DAILY_REQUIREMENTS = ("storage.read_complete", "mail.search", "tasks.list_complete")
SCHEDULED_REQUIREMENTS = ("scheduler.inspect", "scheduler.verify")
UNKNOWN_RECORD_LIMIT = 1
UNKNOWN_BYTE_LIMIT = 65536


@dataclass(frozen=True)
class ExecutionPlan:
    operation: str
    entrypoint: str
    max_records_per_unit: int
    max_bytes_per_unit: int
    required_capabilities: tuple[str, ...]


def _available(profile: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for record in profile["capabilities"]:
        capability_id = record["capability_id"]
        if capability_id in result:
            raise CapabilityError(f"duplicate capability: {capability_id}")
        result[capability_id] = record
    return result


def qualify_execution(
    profile: dict[str, Any], schema: dict[str, Any], *, operation: str, entrypoint: str,
    required_capabilities: Iterable[str] = MANUAL_DAILY_REQUIREMENTS,
    requested_records: int | None = None, requested_bytes: int | None = None,
) -> ExecutionPlan:
    """Return bounded plan, or a specific blocker, without contacting providers."""
    errors = validate(profile, schema)
    if errors:
        raise CapabilityError("invalid capability profile: " + "; ".join(errors))
    if entrypoint not in {"manual", "scheduled"}:
        raise CapabilityError(f"unknown entrypoint: {entrypoint}")
    if profile["execution_surface"] != entrypoint:
        raise CapabilityError(f"execution surface is {profile['execution_surface']!r}, expected {entrypoint!r}")
    if operation not in profile["conformant_operations"]:
        raise CapabilityError(f"operation is not declared conformant: {operation}")
    if profile["authentication"]["status"] != "available":
        raise CapabilityError(f"authentication is {profile['authentication']['status']!r}")
    observations = profile["observations"]
    for name in ("local_execution", "storage_read_complete", "pagination", "file_transfer"):
        if observations[name].get("status") != "available":
            raise CapabilityError(f"required observation is not available: {name}")
    for name in ("storage", "mail", "tasks"):
        if profile["network_paths"][name].get("status") != "available":
            raise CapabilityError(f"required network path is not available: {name}")
    requirements = tuple(required_capabilities) + (SCHEDULED_REQUIREMENTS if entrypoint == "scheduled" else ())
    available = _available(profile)
    for capability_id in requirements:
        record = available.get(capability_id)
        if record is None:
            raise CapabilityError(f"missing required capability: {capability_id}")
        if record["status"] != "available":
            raise CapabilityError(f"required capability is {record['status']!r}: {capability_id}")
    if entrypoint == "scheduled":
        if profile["evidence_class"] != "observed":
            raise CapabilityError("scheduled execution requires observed-surface evidence")
        if profile["selected_adapters"]["scheduler"] is None or profile["scheduler_behavior"] is None:
            raise CapabilityError("scheduled execution requires scheduler evidence")
        if profile["network_paths"]["scheduler"].get("status") != "available":
            raise CapabilityError("required network path is not available: scheduler")
    limits = profile["limits"]
    record_cap = limits["max_records_per_unit"] or UNKNOWN_RECORD_LIMIT
    byte_cap = limits["max_bytes_per_unit"] or UNKNOWN_BYTE_LIMIT
    return ExecutionPlan(operation, entrypoint, min(requested_records or record_cap, record_cap), min(requested_bytes or byte_cap, byte_cap), requirements)
