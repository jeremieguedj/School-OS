from __future__ import annotations

import json
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "synthetic-fixtures" / "alpha13"
sys.path.insert(0, str(ROOT))

from school_os.brief import confirm_delivery, render_brief
from school_os.catalog import parse_v2_record, serialize_v2_record, verify_persisted_record
from school_os.contracts import canonical_json_bytes, sha256_bytes
from school_os.daily import PHASES, run_daily
from school_os.tasks import build_derived_knowledge, reconcile_canonical_tasks, reconcile_provider_tasks, serialize_canonical_tasks
from tests.support.fakes import FixtureTasks, SendSink


class ConnectedDailyRunTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = json.loads((FIXTURE / "connected-daily-run.json").read_text(encoding="utf-8"))
        cls.schemas = {
            name: json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))
            for name in (
                "brief-input.schema.json", "canonical-tasks.schema.json",
                "capability-profile.schema.json", "delivery-ledger.schema.json",
                "fact.schema.json", "provider-state.schema.json",
                "source-conversation.schema.json", "task.schema.json",
            )
        }

    def _profile(self) -> dict[str, Any]:
        profile = json.loads((ROOT / "templates" / "state" / "capability-profile.json").read_text(encoding="utf-8"))
        profile["profile_id"] = "synthetic-connected-manual"
        profile["runtime_adapter"] = "runtimes/synthetic.md"
        profile["runtime_selector"] = {"model": "synthetic", "reasoning_effort": "none"}
        profile["selected_adapters"] = {"mail": "mail/synthetic.md", "tasks": "tasks/synthetic.md", "scheduler": None, "audio": None}
        profile["adapter_versions"] = {"runtime": "1", "mail": "1", "tasks": "1", "scheduler": None}
        profile["verified_at"] = "2026-09-07T08:00:00-07:00"
        profile["authentication"] = {"status": "available", "verified_at": "2026-09-07T08:00:00-07:00", "recheck_trigger": "synthetic"}
        profile["network_paths"] = {name: {"status": "available" if name != "scheduler" else "not_required"} for name in profile["network_paths"]}
        profile["observations"] = {name: {"status": "available"} for name in profile["observations"]}
        profile["limits"] = {"max_records_per_unit": 1, "max_bytes_per_unit": 65536}
        profile["capabilities"] = [
            {"capability_id": capability, "status": "available", "verification": {"fixture": True}, "degradation": "stop_before_side_effects"}
            for capability in ("storage.read_complete", "mail.search", "tasks.list_complete")
        ]
        profile["scheduler_behavior"] = None
        profile["conformant_operations"] = ["daily-run"]
        return profile

    def _installed_candidate(self, base: Path) -> Path:
        output = base / "release"
        built = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "build_release.py"), "--repo", str(ROOT), "--ref", "HEAD", "--version", "0.1.0-alpha.13", "--output-dir", str(output)],
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(0, built.returncode, built.stderr)
        archive = output / "school-os-0.1.0-alpha.13.tar.gz"
        with tarfile.open(archive, "r:gz") as package:
            package.extractall(base)
        extracted = base / "School-OS-0.1.0-alpha.13"
        answers = json.loads((FIXTURE / "answers.json").read_text(encoding="utf-8"))
        answers["package_root"] = str(extracted)
        answers["package_archive"] = str(archive)
        answers["package_source_identity"]["commit"] = subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True, capture_output=True, check=True,
        ).stdout.strip()
        answers_path = base / "answers.json"
        references_path = base / "references.json"
        answers_path.write_text(json.dumps(answers), encoding="utf-8")
        references_path.write_bytes((FIXTURE / "references.json").read_bytes())
        candidate = base / "instance"
        installed = subprocess.run(
            [sys.executable, str(extracted / "scripts" / "scaffold_instance.py"), "--answers", str(answers_path), "--references", str(references_path), "--output", str(candidate)],
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(0, installed.returncode, installed.stderr)
        return candidate

    @staticmethod
    def _write_checked(path: Path, data: bytes, writes: list[str]) -> dict[str, str]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        persisted = path.read_bytes()
        if persisted != data:
            raise AssertionError(f"readback changed {path.name}")
        writes.append(path.name)
        return {"path": str(path), "sha256": sha256_bytes(persisted)}

    def _run(self, *, tamper_catalog: bool = False) -> tuple[Any, dict[str, Any], list[str], SendSink, FixtureTasks]:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        base = Path(temporary.name)
        candidate = self._installed_candidate(base)
        work = base / "run"
        writes: list[str] = []
        sink = SendSink()
        provider = FixtureTasks()
        state: dict[str, Any] = {}

        def preflight(_previous: dict[str, Any]) -> dict[str, Any]:
            manifest = (candidate / "state" / "installation-manifest.json").read_bytes()
            state["candidate_manifest_sha256"] = sha256_bytes(manifest)
            return {"verified": True, "artifacts": {"candidate_manifest": state["candidate_manifest_sha256"]}}

        def discover(previous: dict[str, Any]) -> dict[str, Any]:
            self.assertIn("candidate_manifest", previous["artifacts"])
            artifact = self._write_checked(work / "discovery.json", canonical_json_bytes(self.fixture["conversation"]), writes)
            return {"verified": True, "artifacts": {**previous["artifacts"], "discovery": artifact}}

        def catalog(previous: dict[str, Any]) -> dict[str, Any]:
            conversation = json.loads(Path(previous["artifacts"]["discovery"]["path"]).read_text(encoding="utf-8"))
            intended = serialize_v2_record(conversation, self.schemas["source-conversation.schema.json"])
            artifact = self._write_checked(work / "catalog.md", intended, writes)
            verify_persisted_record({message["message_id"]: message["body"] for message in conversation["messages"]}, intended, Path(artifact["path"]).read_bytes())
            return {"verified": True, "artifacts": {**previous["artifacts"], "catalog": artifact}}

        def reconcile(previous: dict[str, Any]) -> dict[str, Any]:
            catalog_artifact = previous["artifacts"]["catalog"]
            if tamper_catalog:
                Path(catalog_artifact["path"]).write_bytes(b"substituted intermediate artifact")
            if sha256_bytes(Path(catalog_artifact["path"]).read_bytes()) != catalog_artifact["sha256"]:
                raise AssertionError("catalog artifact hash changed before reconciliation")
            record = parse_v2_record(Path(catalog_artifact["path"]).read_bytes())
            facts = []
            for template in self.fixture["facts"]:
                fact = dict(template)
                fact["record_id"] = record.header["record_id"]
                facts.append(fact)
            facts_artifact = self._write_checked(work / "facts.json", canonical_json_bytes({"facts": facts}), writes)
            derived = build_derived_knowledge(facts, fact_schema=self.schemas["fact.schema.json"], task_schema=self.schemas["task.schema.json"])
            register = reconcile_canonical_tasks({"schema_version": 1, "tasks": []}, facts, fact_schema=self.schemas["fact.schema.json"], task_schema=self.schemas["task.schema.json"], register_schema=self.schemas["canonical-tasks.schema.json"])
            tasks_artifact = self._write_checked(work / "canonical-tasks.json", serialize_canonical_tasks(register, self.schemas["canonical-tasks.schema.json"]), writes)
            knowledge_artifact = self._write_checked(work / "knowledge.json", canonical_json_bytes({"guidelines": derived["guidelines"], "rolling_updates": derived["rolling_updates"]}), writes)
            return {"verified": True, "artifacts": {**previous["artifacts"], "facts": facts_artifact, "tasks": tasks_artifact, "knowledge": knowledge_artifact}}

        def task_sync(previous: dict[str, Any]) -> dict[str, Any]:
            register = json.loads(Path(previous["artifacts"]["tasks"]["path"]).read_text(encoding="utf-8"))
            reconciled = reconcile_provider_tasks(provider, register, {"provider_id": "synthetic", "adapter_id": "synthetic-tasks", "provider_revision": None, "bindings": [], "cursor": None, "cursor_evidence": {}, "verified_readback": {}}, task_schema=self.schemas["task.schema.json"], register_schema=self.schemas["canonical-tasks.schema.json"], provider_state_schema=self.schemas["provider-state.schema.json"])
            provider_artifact = self._write_checked(work / "provider-state.json", canonical_json_bytes(reconciled.provider_state), writes)
            return {"verified": True, "artifacts": {**previous["artifacts"], "provider_state": provider_artifact}}

        def brief_delivery(previous: dict[str, Any]) -> dict[str, Any]:
            knowledge = json.loads(Path(previous["artifacts"]["knowledge"]["path"]).read_text(encoding="utf-8"))
            register = json.loads(Path(previous["artifacts"]["tasks"]["path"]).read_text(encoding="utf-8"))
            brief_input = {"schema_version": 1, "window": {"end": "2026-09-07"}, "entity_order": ["child_1", "household"], "news": [{"date": "2026-09-07", "entity_scope": "child_1", "text": item["text"]} for item in knowledge["rolling_updates"]], "guidelines": [{"date": "2026-09-07", "entity_scope": "child_1", "text": item["text"]} for item in knowledge["guidelines"]], "tasks": [{"date": task["source_opened_date"], "entity_scope": task["entity_scope"], "text": task["action"], "source_link": task["source_link"]} for task in register["tasks"]], "labels": {"news": "News", "guidelines": "Guidelines", "tasks": "Action Items"}, "theme": {}, "input_hashes": {"tasks": previous["artifacts"]["tasks"]["sha256"]}}
            rendered = render_brief(brief_input, self.schemas["brief-input.schema.json"])
            html = self._write_checked(work / "brief.html", rendered["html"], writes)
            text = self._write_checked(work / "brief.txt", rendered["text"], writes)
            ledger = confirm_delivery(sink, {"schema_version": 1, "entries": []}, delivery_key="daily-20260907-normal", variant="normal", content=rendered["html"], recipients_fingerprint="a" * 64, ledger_schema=self.schemas["delivery-ledger.schema.json"])
            ledger_artifact = self._write_checked(work / "delivery-ledger.json", canonical_json_bytes(ledger), writes)
            return {"verified": True, "artifacts": {**previous["artifacts"], "brief_html": html, "brief_text": text, "delivery_ledger": ledger_artifact}}

        def commit(previous: dict[str, Any]) -> dict[str, Any]:
            ledger = json.loads(Path(previous["artifacts"]["delivery_ledger"]["path"]).read_text(encoding="utf-8"))
            if ledger["entries"][0]["outcome"] != "confirmed":
                raise AssertionError("cursors cannot advance without confirmed delivery")
            hashes = {name: value["sha256"] for name, value in previous["artifacts"].items() if isinstance(value, dict)}
            evidence = self._write_checked(work / "final-evidence.json", canonical_json_bytes({"outcome": "COMPLETE", "delivery_key": ledger["entries"][0]["delivery_key"], "artifact_hashes": hashes}), writes)
            cursors = self._write_checked(work / "eligible-cursors.json", canonical_json_bytes({"discovery": "page-1", "provider": "synthetic", "final_evidence_sha256": evidence["sha256"]}), writes)
            return {"verified": True, "artifacts": {**previous["artifacts"], "final_evidence": evidence, "cursors": cursors}}

        result = run_daily(profile=self._profile(), capability_schema=self.schemas["capability-profile.schema.json"], entrypoint="manual", operation_id="synthetic-daily-001", attempt_id="synthetic-attempt-001", stages={"preflight": preflight, "discover": discover, "catalog": catalog, "reconcile": reconcile, "task_sync": task_sync, "brief_delivery": brief_delivery, "commit": commit})
        return result, state, writes, sink, provider

    def test_installed_manual_run_uses_actual_predecessor_artifacts(self) -> None:
        result, state, writes, sink, provider = self._run()
        self.assertEqual("COMPLETE", result.outcome)
        self.assertEqual(PHASES, result.completed_phases)
        self.assertEqual(1, len(sink.deliveries))
        self.assertEqual(["list", "create", "read"], provider.calls)
        self.assertEqual("eligible-cursors.json", writes[-1])
        artifacts = result.outputs["commit"]["artifacts"]
        self.assertIn("candidate_manifest", artifacts)
        self.assertEqual(state["candidate_manifest_sha256"], artifacts["candidate_manifest"])
        self.assertEqual(self.fixture["expected_artifact_sha256"], {name: value["sha256"] for name, value in artifacts.items() if isinstance(value, dict)})

    def test_substituted_catalog_artifact_blocks_before_task_or_delivery(self) -> None:
        with self.assertRaisesRegex(AssertionError, "catalog artifact hash changed"):
            self._run(tamper_catalog=True)


if __name__ == "__main__":
    unittest.main()
