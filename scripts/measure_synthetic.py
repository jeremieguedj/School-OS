#!/usr/bin/env python3
"""Measure existing synthetic alpha.13 operation paths without providers."""
from __future__ import annotations

import json
import math
import platform
import sys
import tarfile
import tempfile
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from time import monotonic, perf_counter_ns
from typing import Any, Callable

# An extracted release is immutable; this CLI must not add __pycache__ files.
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "synthetic-fixtures" / "alpha13"
sys.path.insert(0, str(ROOT))

from school_os.adapters import Page  # noqa: E402
from school_os.brief import confirm_delivery, render_brief  # noqa: E402
from school_os.catalog import build_catalog_message, parse_v2_record, serialize_v2_record, verify_persisted_record  # noqa: E402
from school_os.contracts import canonical_json_bytes, sha256_bytes  # noqa: E402
from school_os.daily import PHASES, run_daily  # noqa: E402
from school_os.importer import admit_exact_plaintext_representation, enumerate_conversations, next_import_batch  # noqa: E402
from school_os.install import scaffold_instance, validate_candidate  # noqa: E402
from school_os.package import verify_release_archive  # noqa: E402
from school_os.tasks import build_derived_knowledge, reconcile_canonical_tasks, reconcile_provider_tasks, serialize_canonical_tasks  # noqa: E402
from scripts.build_release import build_release  # noqa: E402
from tests.support.fakes import FixtureMail, FixtureMessage, FixtureTasks, SendSink  # noqa: E402


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def measured(name: str, payload: dict[str, Any], operation: Callable[[], dict[str, Any]]) -> dict[str, Any]:
    started = perf_counter_ns()
    result = operation()
    return {
        "name": name,
        "elapsed_ns": perf_counter_ns() - started,
        "input_bytes": len(canonical_json_bytes(payload)),
        "output_bytes": len(canonical_json_bytes(result["result"])),
        **result,
    }


def prepare_package(base: Path) -> tuple[Path, Path, str]:
    archive, sums, commit = build_release(ROOT, "HEAD", "0.1.0-alpha.13", base / "release")
    errors = verify_release_archive(archive, sums, "0.1.0-alpha.13")
    if errors:
        raise RuntimeError("release verification failed: " + "; ".join(errors))
    with tarfile.open(archive, "r:gz") as package:
        package.extractall(base)
    return base / "School-OS-0.1.0-alpha.13", archive, commit


def profile() -> dict[str, Any]:
    value = read_json(ROOT / "templates/state/capability-profile.json")
    value.update({
        "profile_id": "synthetic-measurement-manual",
        "runtime_adapter": "runtimes/synthetic.md",
        "runtime_selector": {"model": "synthetic", "reasoning_effort": "none"},
        "selected_adapters": {"mail": "mail/synthetic.md", "tasks": "tasks/synthetic.md", "scheduler": None, "audio": None},
        "adapter_versions": {"runtime": "1", "mail": "1", "tasks": "1", "scheduler": None},
        "verified_at": "2026-09-08T00:00:00-07:00",
        "authentication": {"status": "available", "verified_at": "2026-09-08T00:00:00-07:00", "recheck_trigger": "synthetic"},
        "limits": {"max_records_per_unit": 1, "max_bytes_per_unit": 65536},
        "scheduler_behavior": None,
        "conformant_operations": ["daily-run"],
    })
    value["network_paths"] = {key: {"status": "not_required" if key == "scheduler" else "available"} for key in value["network_paths"]}
    value["observations"] = {key: {"status": "available"} for key in value["observations"]}
    value["capabilities"] = [
        {"capability_id": key, "status": "available", "verification": {"fixture": True}, "degradation": "stop_before_side_effects"}
        for key in ("storage.read_complete", "mail.search", "tasks.list_complete")
    ]
    return value


class ReplayClock:
    """Feed measured component durations to the runner's injected clock."""
    def __init__(self, admission_ns: int) -> None:
        self.elapsed_ns = 0
        self.admission_ns = admission_ns
        self.calls = 0

    def __call__(self) -> float:
        self.calls += 1
        if self.calls == 2:
            self.elapsed_ns += self.admission_ns
        return self.elapsed_ns / 1_000_000_000

    def advance(self, elapsed_ns: int) -> None:
        self.elapsed_ns += elapsed_ns


class DailyHarness:
    """Exercise the connected fixture through the real daily helper functions."""
    def __init__(self, root: Path, candidate: Path) -> None:
        self.root = root
        self.candidate = candidate
        self.fixture = read_json(FIXTURE / "connected-daily-run.json")
        self.schemas = {name: read_json(ROOT / "schemas" / name) for name in (
            "brief-input.schema.json", "canonical-tasks.schema.json", "capability-profile.schema.json",
            "delivery-ledger.schema.json", "fact.schema.json", "provider-state.schema.json",
            "source-conversation.schema.json", "task.schema.json",
        )}
        self.provider = FixtureTasks()
        self.sink = SendSink()
        self.register: dict[str, Any] = {"schema_version": 1, "tasks": []}
        self.provider_state: dict[str, Any] = {
            "provider_id": "synthetic", "adapter_id": "synthetic-tasks", "provider_revision": None,
            "bindings": [], "cursor": None, "cursor_evidence": {}, "verified_readback": {},
        }
        self.artifacts: dict[str, dict[str, str]] = {}
        self.run_number = 0

    @staticmethod
    def call(calls: Counter[str], name: str, function: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        calls[name] += 1
        return function(*args, **kwargs)

    def write(self, name: str, data: bytes, calls: Counter[str]) -> dict[str, str]:
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        persisted = path.read_bytes()
        if persisted != data:
            raise AssertionError(f"readback changed {name}")
        calls["storage.write_readback"] += 1
        return {"path": str(path), "sha256": sha256_bytes(persisted)}

    def stages(self, *, new_message: bool, delivery_key: str, calls: Counter[str], units: list[str], phase_times: dict[str, int], clock: ReplayClock | None) -> dict[str, Callable[[dict[str, Any]], dict[str, Any]]]:
        conversation = self.fixture["conversation"]
        messages = [FixtureMessage(conversation["messages"][0]["message_id"], conversation["messages"][0]["body"])] if new_message else []
        mail = FixtureMail(messages)

        def preflight(_: dict[str, Any]) -> dict[str, Any]:
            manifest = self.call(calls, "install.validate_candidate", validate_candidate, self.candidate, ROOT)
            return {"verified": True, "artifacts": dict(self.artifacts), "manifest_file_count": len(manifest["files"])}

        def discover(_: dict[str, Any]) -> dict[str, Any]:
            calls["provider_fake.mail.search"] += 1
            found = mail.search()
            if found:
                messages = []
                for index, message in enumerate(found):
                    source = conversation["messages"][index]
                    raw = message.body.encode("utf-8")
                    admission = self.call(
                        calls, "importer.admit_exact_plaintext_representation",
                        admit_exact_plaintext_representation,
                        ({
                            "part_id": "plain-1", "role": "body",
                            "selected_plaintext": True, "complete": True,
                            "mime_type": "text/plain", "charset": "utf-8",
                            "content_transfer_encoding": "identity", "data": raw,
                            "raw_part_sha256": sha256_bytes(raw),
                            "raw_part_byte_length": len(raw),
                            "raw_part_locator": {"kind": "raw_part_bytes", "byte_start": 0, "byte_end": len(raw)},
                            "provider_unicode": message.body,
                        },),
                        mime_tree_complete=True,
                    )
                    messages.append(self.call(
                        calls, "catalog.build_catalog_message", build_catalog_message,
                        message_id=message.message_id,
                        received_at=source["received_at"],
                        received_date=source["received_at"][:10],
                        admission=admission,
                    ))
                discovered = {
                    **conversation,
                    "schema_version": 2,
                    "messages": messages,
                }
                self.artifacts["discovery"] = self.write(f"run-{self.run_number}/discovery.json", canonical_json_bytes(discovered), calls)
            return {"verified": True, "artifacts": dict(self.artifacts), "new_conversations": len(found)}

        def catalog(previous: dict[str, Any]) -> dict[str, Any]:
            if previous["new_conversations"]:
                discovered = read_json(Path(self.artifacts["discovery"]["path"]))
                data = self.call(calls, "catalog.serialize_v2_record", serialize_v2_record, discovered, self.schemas["source-conversation.schema.json"])
                self.artifacts["catalog"] = self.write(f"run-{self.run_number}/catalog.md", data, calls)
            if "catalog" not in self.artifacts:
                raise AssertionError("no-new-message run requires an existing catalog")
            data = Path(self.artifacts["catalog"]["path"]).read_bytes()
            self.call(calls, "catalog.verify_persisted_record", verify_persisted_record, {item["message_id"]: item["body"] for item in conversation["messages"]}, data, data)
            return {"verified": True, "artifacts": dict(self.artifacts), "new_records": previous["new_conversations"]}

        def reconcile(_: dict[str, Any]) -> dict[str, Any]:
            record = self.call(calls, "catalog.parse_v2_record", parse_v2_record, Path(self.artifacts["catalog"]["path"]).read_bytes())
            facts = [{**item, "record_id": record.header["record_id"]} for item in self.fixture["facts"]]
            derived = self.call(calls, "tasks.build_derived_knowledge", build_derived_knowledge, facts, fact_schema=self.schemas["fact.schema.json"], task_schema=self.schemas["task.schema.json"])
            self.register = self.call(calls, "tasks.reconcile_canonical_tasks", reconcile_canonical_tasks, self.register, facts, fact_schema=self.schemas["fact.schema.json"], task_schema=self.schemas["task.schema.json"], register_schema=self.schemas["canonical-tasks.schema.json"])
            task_bytes = self.call(calls, "tasks.serialize_canonical_tasks", serialize_canonical_tasks, self.register, self.schemas["canonical-tasks.schema.json"])
            self.artifacts["tasks"] = self.write(f"run-{self.run_number}/canonical-tasks.json", task_bytes, calls)
            self.artifacts["knowledge"] = self.write(f"run-{self.run_number}/knowledge.json", canonical_json_bytes({"guidelines": derived["guidelines"], "rolling_updates": derived["rolling_updates"]}), calls)
            return {"verified": True, "artifacts": dict(self.artifacts), "fact_count": len(facts)}

        def task_sync(_: dict[str, Any]) -> dict[str, Any]:
            result = self.call(calls, "tasks.reconcile_provider_tasks", reconcile_provider_tasks, self.provider, self.register, self.provider_state, task_schema=self.schemas["task.schema.json"], register_schema=self.schemas["canonical-tasks.schema.json"], provider_state_schema=self.schemas["provider-state.schema.json"])
            self.register = result.tasks
            task_bytes = self.call(calls, "tasks.serialize_canonical_tasks", serialize_canonical_tasks, self.register, self.schemas["canonical-tasks.schema.json"])
            self.artifacts["tasks"] = self.write(f"run-{self.run_number}/canonical-tasks.json", task_bytes, calls)
            persisted_register = read_json(Path(self.artifacts["tasks"]["path"]))
            binding_count = sum(len(task["provider_bindings"]) for task in persisted_register["tasks"])
            if binding_count < 1:
                raise AssertionError("persisted canonical register lost the provider binding")
            self.provider_state = result.provider_state
            self.artifacts["provider_state"] = self.write(f"run-{self.run_number}/provider-state.json", canonical_json_bytes(self.provider_state), calls)
            return {"verified": True, "artifacts": dict(self.artifacts), "provider_effects": len(result.effects), "canonical_provider_bindings": binding_count}

        def brief_delivery(_: dict[str, Any]) -> dict[str, Any]:
            knowledge = read_json(Path(self.artifacts["knowledge"]["path"]))
            brief_input = {
                "schema_version": 1, "window": {"end": "2026-09-08"}, "entity_order": ["child_1", "household"],
                "news": [{"date": "2026-09-07", "entity_scope": "child_1", "text": item["text"]} for item in knowledge["rolling_updates"]],
                "guidelines": [{"date": "2026-09-07", "entity_scope": "child_1", "text": item["text"]} for item in knowledge["guidelines"]],
                "tasks": [{"date": item["source_opened_date"], "entity_scope": item["entity_scope"], "text": item["action"], "source_link": item["source_link"]} for item in self.register["tasks"]],
                "labels": {"news": "News", "guidelines": "Guidelines", "tasks": "Action Items"}, "theme": {},
                "input_hashes": {"tasks": self.artifacts["tasks"]["sha256"]},
            }
            rendered = self.call(calls, "brief.render_brief", render_brief, brief_input, self.schemas["brief-input.schema.json"])
            self.artifacts["brief_html"] = self.write(f"run-{self.run_number}/brief.html", rendered["html"], calls)
            deliveries = len(self.sink.deliveries)
            ledger = self.call(calls, "brief.confirm_delivery", confirm_delivery, self.sink, {"schema_version": 1, "entries": []}, delivery_key=delivery_key, variant="normal", content=rendered["html"], recipients_fingerprint="a" * 64, ledger_schema=self.schemas["delivery-ledger.schema.json"])
            calls["provider_fake.delivery.send"] += len(self.sink.deliveries) - deliveries
            self.artifacts["delivery_ledger"] = self.write(f"run-{self.run_number}/delivery-ledger.json", canonical_json_bytes(ledger), calls)
            return {"verified": True, "artifacts": dict(self.artifacts), "delivery_count": len(self.sink.deliveries)}

        def commit(_: dict[str, Any]) -> dict[str, Any]:
            hashes = {name: item["sha256"] for name, item in self.artifacts.items()}
            self.artifacts["final_evidence"] = self.write(f"run-{self.run_number}/final-evidence.json", canonical_json_bytes({"outcome": "COMPLETE", "artifact_hashes": hashes}), calls)
            return {"verified": True, "artifacts": dict(self.artifacts), "committed": True}

        functions = {"preflight": preflight, "discover": discover, "catalog": catalog, "reconcile": reconcile, "task_sync": task_sync, "brief_delivery": brief_delivery, "commit": commit}
        wrapped = {}
        for phase, function in functions.items():
            def invoke(previous: dict[str, Any], phase: str = phase, function: Callable[[dict[str, Any]], dict[str, Any]] = function) -> dict[str, Any]:
                started = perf_counter_ns()
                output = function(previous)
                elapsed = perf_counter_ns() - started
                phase_times[phase] = phase_times.get(phase, 0) + elapsed
                if clock:
                    clock.advance(elapsed)
                units.append(phase)
                return output
            wrapped[phase] = invoke
        return wrapped

    def run(self, *, new_message: bool, operation_id: str, attempt_id: str, delivery_key: str, resume_after: str | None = None, predecessor: dict[str, Any] | None = None, max_elapsed_ms: int | None = None, estimates: dict[str, int] | None = None, clock: ReplayClock | None = None) -> dict[str, Any]:
        self.run_number += 1
        calls: Counter[str] = Counter()
        units: list[str] = []
        phase_times: dict[str, int] = {}
        checkpoint_time = 0
        checkpoints: list[str] = []

        def checkpoint(phase: str, result: dict[str, Any], outcome: str) -> str:
            nonlocal checkpoint_time
            started = perf_counter_ns()
            path = self.root / f"checkpoints/{operation_id}-{attempt_id}-{len(checkpoints) + 1}.json"
            data = canonical_json_bytes({"phase": phase, "outcome": outcome, "result": result})
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            if path.read_bytes() != data:
                raise AssertionError("checkpoint readback changed bytes")
            elapsed = perf_counter_ns() - started
            checkpoint_time += elapsed
            if clock:
                clock.advance(elapsed)
            calls["storage.checkpoint_write_readback"] += 1
            checkpoints.append(str(path))
            return str(path)

        task_start = len(self.provider.calls)
        delivery_start = len(self.sink.deliveries)
        started = perf_counter_ns()
        result = run_daily(
            profile=profile(), capability_schema=self.schemas["capability-profile.schema.json"], entrypoint="manual",
            operation_id=operation_id, attempt_id=attempt_id,
            stages=self.stages(new_message=new_message, delivery_key=delivery_key, calls=calls, units=units, phase_times=phase_times, clock=clock),
            resume_after=resume_after, durable_predecessor_output=predecessor, checkpoint=checkpoint,
            max_elapsed_ms=max_elapsed_ms, estimated_phase_ms=estimates,
            monotonic_clock=clock if clock else monotonic,
        )
        elapsed = perf_counter_ns() - started
        task_calls = self.provider.calls[task_start:]
        for name in task_calls:
            calls[f"provider_fake.tasks.{name}"] += 1
        summary = {
            "outcome": result.outcome, "attempt_id": result.attempt_id, "current_phase": result.current_phase,
            "completed_phases": list(result.completed_phases),
            "phase_outputs": {phase: {key: value for key, value in output.items() if key != "artifacts"} for phase, output in result.outputs.items()},
            "artifact_hashes": {name: value["sha256"] for name, value in self.artifacts.items()},
        }
        return {
            "elapsed_ns": elapsed, "result": summary, "raw_result": asdict(result),
            "helper_calls": dict(sorted(calls.items())),
            "provider_fake_calls": calls["provider_fake.mail.search"] + len(task_calls) + len(self.sink.deliveries) - delivery_start,
            "completed_units": units, "phase_elapsed_ns": phase_times,
            "checkpoint_elapsed_ns": checkpoint_time,
            "checkpoint_references": [Path(path).name for path in checkpoints],
            "_last_checkpoint": read_json(Path(checkpoints[-1])) if checkpoints else None,
        }


def daily_measurement(name: str, payload: dict[str, Any], harness: DailyHarness, **kwargs: Any) -> dict[str, Any]:
    evidence = harness.run(**kwargs)
    raw_result = evidence.pop("raw_result")
    return {
        "name": name, "elapsed_ns": evidence.pop("elapsed_ns"),
        "input_bytes": len(canonical_json_bytes(payload)),
        "output_bytes": len(canonical_json_bytes(raw_result)),
        **evidence, "repeated_units": [],
    }


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="school-os-measure-") as temporary:
        base = Path(temporary)
        package_root, archive, commit = prepare_package(base)
        answers = read_json(FIXTURE / "answers.json")
        references = read_json(FIXTURE / "references.json")
        answers.update({"package_root": str(package_root), "package_archive": str(archive)})
        answers["package_source_identity"]["commit"] = commit
        candidate = base / "instance"

        onboarding = measured("onboarding", {"answers": answers, "references": references}, lambda: {
            "helper_calls": {"install.scaffold_instance": 1, "install.validate_candidate": 1},
            "provider_fake_calls": 0,
            "completed_units": list(scaffold_instance(answers, references, candidate)["files"]),
            "repeated_units": [], "result": validate_candidate(candidate, package_root),
        })
        onboarding["result"] = {
            "verification_status": onboarding["result"]["verification_status"],
            "managed_file_count": len(onboarding["result"]["files"]),
            "managed_file_hashes": {name: item["sha256"] for name, item in onboarding["result"]["files"].items()},
        }

        import_fixture = read_json(FIXTURE / "import-pages.json")
        pages = {page["token"]: page for page in import_fixture["pages"]}
        import_calls: Counter[str] = Counter()
        def import_operation() -> dict[str, Any]:
            def search(token: str | None) -> Page:
                import_calls["provider_fake.mail.search_page"] += 1
                page = pages[token]
                return Page(tuple(page["items"]), page["next_page_token"])
            enumeration = enumerate_conversations(search)
            import_calls["importer.enumerate_conversations"] += 1
            first = next_import_batch(enumeration.conversations, completed_ids=(), max_records=1, max_bytes=10)
            second = next_import_batch(enumeration.conversations, completed_ids=first.completed_ids, max_records=1, max_bytes=10)
            import_calls["importer.next_import_batch"] += 2
            first_ids = [item["conversation_id"] for item in first.conversations]
            second_ids = [item["conversation_id"] for item in second.conversations]
            return {
                "helper_calls": {key: value for key, value in sorted(import_calls.items()) if not key.startswith("provider_fake")},
                "provider_fake_calls": import_calls["provider_fake.mail.search_page"],
                "completed_units": first_ids + second_ids,
                "repeated_units": sorted(set(first_ids) & set(second_ids)),
                "result": {"enumeration": asdict(enumeration), "first_batch": asdict(first), "second_batch": asdict(second)},
            }
        bounded = measured("bounded_import", import_fixture, import_operation)

        harness = DailyHarness(base / "daily", candidate)
        update = daily_measurement("daily_update", harness.fixture, harness, new_message=True, operation_id="synthetic-update", attempt_id="attempt-1", delivery_key="daily-update")
        no_new = daily_measurement("no_new_message", {"conversation_ids": [], "prior_artifact_hashes": update["result"]["artifact_hashes"]}, harness, new_message=False, operation_id="synthetic-no-new", attempt_id="attempt-1", delivery_key="daily-no-new")
        update.pop("_last_checkpoint")
        no_new.pop("_last_checkpoint")

        recovery = DailyHarness(base / "recovery", candidate)
        estimates = {phase: max(1, math.ceil(update["phase_elapsed_ns"][phase] / 1_000_000)) for phase in PHASES}
        overhead = max(0, update["elapsed_ns"] - sum(update["phase_elapsed_ns"].values()) - update["checkpoint_elapsed_ns"])
        budget = math.ceil(overhead / 1_000_000) + estimates["preflight"] + 1
        clock = ReplayClock(overhead)
        interrupted = daily_measurement("interrupted", {"conversation": recovery.fixture["conversation"], "budget_ms": budget, "estimates_ms": estimates}, recovery, new_message=True, operation_id="synthetic-recovery", attempt_id="attempt-1", delivery_key="daily-recovery", max_elapsed_ms=budget, estimates=estimates, clock=clock)
        if interrupted["result"]["outcome"] != "NEEDS_CONTINUATION":
            raise AssertionError("measured budget did not produce NEEDS_CONTINUATION")
        continuation = interrupted.pop("_last_checkpoint")
        resumed = daily_measurement("fresh_attempt_resume", {"checkpoint": continuation, "prior_attempt_id": "attempt-1"}, recovery, new_message=True, operation_id="synthetic-recovery", attempt_id="attempt-2", delivery_key="daily-recovery", resume_after=interrupted["result"]["current_phase"], predecessor=continuation["result"])
        resumed.pop("_last_checkpoint")
        resumed["evidence_scope"] = "same-process continuation under a new attempt ID; fresh-process and environment-reset recovery remain separate M3/M4-009 evidence"
        repeated = sorted(set(interrupted["completed_units"]) & set(resumed["completed_units"]))
        interrupted["repeated_units"] = repeated
        resumed["repeated_units"] = repeated

        bounded["result"] = {
            "page_tokens": list(bounded["result"]["enumeration"]["page_tokens"]),
            "dispositions": list(bounded["result"]["enumeration"]["dispositions"]),
            "first_batch_ids": [item["conversation_id"] for item in bounded["result"]["first_batch"]["conversations"]],
            "second_batch_ids": [item["conversation_id"] for item in bounded["result"]["second_batch"]["conversations"]],
            "remaining_ids": list(bounded["result"]["second_batch"]["remaining_ids"]),
        }
        for operation in (update, no_new, interrupted, resumed):
            detail = operation["result"]
            phase_evidence = {
                phase: values
                for phase, values in detail["phase_outputs"].items()
                if any(key in values for key in ("new_conversations", "new_records", "provider_effects", "delivery_count", "committed"))
            }
            operation["result"] = {
                "outcome": detail["outcome"], "attempt_id": detail["attempt_id"],
                "current_phase": detail["current_phase"], "completed_phases": detail["completed_phases"],
                "phase_evidence": phase_evidence, "artifact_count": len(detail["artifact_hashes"]),
            }
            references = operation.pop("checkpoint_references")
            operation["checkpoint_count"] = len(references)
            if detail["outcome"] == "NEEDS_CONTINUATION":
                operation["continuation_checkpoint_reference"] = references[-1]

        baseline = {
            "schema_version": 2,
            "command": "PYTHONPATH=. python3 scripts/measure_synthetic.py",
            "environment": {"python_implementation": platform.python_implementation(), "python_version": platform.python_version(), "platform": platform.platform()},
            "method": "perf_counter_ns around each named existing synthetic operation; canonical JSON lengths of serialized operation inputs and raw outputs; top-level helper and provider-fake calls counted at invocation; package build/extraction excluded from operation timings",
            "unavailable": {"model_tokens": None, "host_deadline_ns": None},
            "budget_rule_evidence": {
                "source_operation": "daily_update", "phase_estimates_ms": estimates,
                "observed_admission_and_checkpoint_overhead_ns": overhead,
                "max_elapsed_ms": budget, "reserve_ms": 0,
                "clock": "injected monotonic replay of measured component durations",
                "practical_limit": "the boundary check runs only between complete phases and cannot preempt an in-progress phase or provider call",
            },
            "operations": [onboarding, bounded, update, no_new, interrupted, resumed],
            "evidence_scope": "Synthetic helper and provider-fake behavior only; this does not establish observed runtime or provider conformance.",
            "refresh_policy": "Regenerate after integration when source/task helper code changes.",
        }
        print(json.dumps(baseline, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
