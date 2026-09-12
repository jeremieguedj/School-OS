#!/usr/bin/env python3
"""Synthetic architecture experiment, not a deployable School-OS runtime.

Semantic outputs are supplied by a separate fictional expectation fixture.
This checks state transitions and identity rules, not LLM comprehension,
connector fidelity, actual memory use or real provider execution.
"""

from __future__ import annotations

import copy
import hashlib
import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results"
FIXTURES = json.loads((ROOT / "source-fixtures.json").read_text())
EXPECTED = json.loads((ROOT / "semantic-expectations.json").read_text())
MESSAGES = {item["id"]: item for item in FIXTURES["messages"]}
CHECKS = []
WINDOWS = {"historical": ("2026-01-05T00:00:00Z", "2026-01-13T00:00:00Z"),
           "daily": ("2026-01-13T00:00:00Z", "2026-01-14T00:00:00Z")}
TEMP_QUANTUM = 8 * 1024 * 1024  # Scenario budget, not any vendor's VM capacity.


def in_scope(message, batch):
    start, end = (datetime.fromisoformat(x.replace("Z", "+00:00")) for x in WINDOWS[batch])
    received = datetime.fromisoformat(message["received_at"].replace("Z", "+00:00"))
    return message["account"] in {"source-account-a", "source-account-b"} and start <= received < end


def check(name, condition, detail=""):
    CHECKS.append({"name": name, "passed": bool(condition), "detail": detail})
    if not condition:
        raise AssertionError(name + ": " + detail)


def message_key(message):
    # Account is a stable logical source account, never a connector instance.
    return "gmail/" + message["account"] + "/" + message["provider_message_id"]


def part_key(message, part):
    if not part.get("id"):
        return None  # Filename, size, hash or an expiring locator is insufficient.
    return message_key(message) + "/part/" + part["id"]


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


class Model:
    def __init__(self):
        self.drive = {
            "instance": "synthetic-school-os",
            "release": "restart-design-simulation",
            "accounts": {"source-account-a": {"provider": "gmail"},
                         "source-account-b": {"provider": "gmail"}},
            "connections": {}, "defaults": {}, "jobs": {}, "runs": {},
            "sources": {}, "facts": {}, "actions": {}, "work": {},
            "coverage": {"historical": {"discovered": [], "complete": [],
                                         "pending": [], "enumeration_complete": False},
                         "daily": {"discovered": [], "complete": [], "pending": [],
                                   "enumeration_complete": False}},
        }
        self.external = {"schedules": {}, "sent": {}, "source_available":
                         {key: True for key in MESSAGES}, "restored_parts": []}
        self.temp = {}
        self.ledger = []
        self.operations = 0
        self.max_modeled_temp_quantum = 0
        self.modeled_read_quanta = 0

    def snap(self, label, outcome, actor="model"):
        self.ledger.append({
            "step": len(self.ledger) + 1, "label": label, "actor": actor,
            "outcome": outcome, "drive": copy.deepcopy(self.drive),
            "external": copy.deepcopy(self.external),
            "temporary_source_ids": sorted(self.temp),
        })

    def reset_agent(self):
        self.temp.clear()
        # Reconstruct canonical state from serialized records, not session objects.
        self.drive = json.loads(json.dumps(self.drive))

    def available_facts(self):
        return {key: fact for key, fact in self.drive["facts"].items()
                if any(self.drive["work"].get(p["source_key"], {}).get("status") in {"complete", "partial"}
                       for p in fact["provenance"])}

    def discover(self, batch, pages, complete=True):
        coverage = self.drive["coverage"][batch]
        for page in pages:
            for item_id in page:
                # Search can return thread-context items outside this scope.
                if not in_scope(MESSAGES[item_id], batch):
                    continue
                if item_id not in coverage["discovered"]:
                    coverage["discovered"].append(item_id)
                if item_id not in coverage["complete"] and item_id not in coverage["pending"]:
                    coverage["pending"].append(item_id)
        coverage["enumeration_complete"] = complete

    def ingest(self, item_id, actor, capabilities, stop=None, allow_write=True, corrupt_readback=False):
        self.operations += 1
        message = MESSAGES[item_id]
        oracle = EXPECTED["sources"][item_id]
        key = message_key(message)
        if not self.external["source_available"][item_id]:
            self.snap("source-unavailable:" + item_id, "No original retrieved; existing knowledge retained", actor)
            return "unavailable"
        previous = copy.deepcopy(self.drive["sources"].get(key, {}))
        read_ids = set(previous.get("read_parts", []))
        current_read = []
        for part in message["parts"]:
            requirement = "text" if item_id + "/" + part["id"] in self.external["restored_parts"] else part["read_requirement"]
            if requirement in capabilities and (part["size_bytes"] <= TEMP_QUANTUM or "chunked" in capabilities):
                current_read.append(part["id"])
                quantum = min(part["size_bytes"], TEMP_QUANTUM)
                self.max_modeled_temp_quantum = max(self.max_modeled_temp_quantum, quantum)
                self.modeled_read_quanta += max(1, (part["size_bytes"] + TEMP_QUANTUM - 1) // TEMP_QUANTUM)
        # The model stores only part IDs, never pretend raw files in Drive.
        # size_bytes and read_requirement express a hypothetical transfer gate.
        self.temp[item_id] = current_read
        if stop == "after-read":
            self.snap("interrupted-after-read:" + item_id, "Temporary material only; no accepted Drive update", actor)
            self.reset_agent()
            return "interrupted"
        if not allow_write:
            self.snap("write-approval-blocked:" + item_id, "No Drive checkpoint can be claimed while all writes are blocked", actor)
            self.reset_agent()
            return "blocked"
        read_ids.update(current_read)
        required = set(oracle["coverage"]["required_part_ids"])
        missing = sorted(required - read_ids)
        self.drive["work"][key] = {"status": "processing", "next": "Complete and verify this source update"}
        record = {
            "fixture_id": item_id, "source_account": message["account"],
            "provider_message_id": message["provider_message_id"],
            "thread_id": message["thread_id"], "version": message["version"],
            "received_at": message["received_at"], "read_parts": sorted(read_ids),
            "pending_parts": missing, "status": "complete" if not missing else "partial",
            "parts": {part_key(message, p): {"part_id": p["id"], "kind": p["kind"],
                       "filename": p.get("filename"), "size_bytes": p["size_bytes"],
                       "content_hash": p.get("content_hash")}
                      for p in message["parts"] if part_key(message, p)},
            "processed_by": actor,
        }
        self.drive["sources"][key] = record
        if stop == "after-source-index":
            self.snap("interrupted-after-source-index:" + item_id, "Catalog exists; interpretation remains pending", actor)
            self.reset_agent()
            return "interrupted"
        for fact in oracle["facts"]:
            if set(fact["part_ids"]) <= read_ids:
                prior = self.drive["facts"].get(fact["key"], {})
                provenance = copy.deepcopy(prior.get("provenance", []))
                occurrence = {"source_key": key, "source_version": message["version"],
                              "part_ids": fact["part_ids"]}
                if occurrence not in provenance:
                    provenance.append(occurrence)
                self.drive["facts"][fact["key"]] = {
                    **{name: copy.deepcopy(value) for name, value in fact.items() if name != "part_ids"},
                    "provenance": provenance}
        if stop == "after-facts":
            self.snap("interrupted-before-task-update:" + item_id, "Facts written; task work and verification remain pending", actor)
            self.reset_agent()
            return "interrupted"
        for action in oracle.get("actions", []):
            if not set(action["part_ids"]) <= read_ids:
                continue
            action_id = action["key"]
            old = self.drive["actions"].get(action_id, {})
            values = old if old.get("source_received_at", "") > message["received_at"] else action
            self.drive["actions"][action_id] = {
                **copy.deepcopy(values), "status": old.get("status", "open" if action.get("initial_status") == "preserve_existing_completion" else action.get("initial_status", "open")),
                "parent_planned_date": old.get("parent_planned_date"),
                "parent_completion_evidence": copy.deepcopy(old.get("parent_completion_evidence")),
                "source_received_at": max(old.get("source_received_at", ""), message["received_at"]),
                "supporting_sources": sorted(set(old.get("supporting_sources", [])) | {key}),
            }
        coverage = self.drive["coverage"][message["batch"]]
        if item_id in coverage["complete"]:
            coverage["complete"].remove(item_id)
        if item_id not in coverage["pending"]:
            coverage["pending"].append(item_id)
        self.drive["work"][key] = {"status": "verification-pending", "next": "Verify saved source and derived records"}
        if stop == "after-write":
            self.snap("write-response-lost:" + item_id, "Drive accepted; local response not acknowledged", actor)
            self.reset_agent()
            return "interrupted"
        observed = json.loads(json.dumps(self.drive["sources"][key]))
        if corrupt_readback:
            observed["read_parts"] = []
            if observed != record:
                self.drive["work"][key]["status"] = "verification-pending"
                if item_id in coverage["complete"]:
                    coverage["complete"].remove(item_id)
                if item_id not in coverage["pending"]:
                    coverage["pending"].append(item_id)
                self.snap("readback-mismatch:" + item_id, "No completion claim; retry reads saved target", actor)
                self.reset_agent()
                return "verification-pending"
        check("readback:" + actor + ":" + item_id,
              observed == record)
        if not missing:
            coverage["complete"].append(item_id)
            coverage["pending"].remove(item_id)
        self.drive["work"][key] = {"status": record["status"], "next":
            "Read missing parts: " + ", ".join(missing) if missing else "None"}
        self.temp.pop(item_id, None)
        self.snap("ingested:" + item_id, record["status"], actor)
        return record["status"]

    def create_job(self, job_id, actor, recipe, cadence, response_lost=False, blocked=False):
        self.drive["jobs"][job_id] = {
            "purpose": recipe, "executor": actor, "scheduler": actor + "-cloud-scheduler",
            "management_ref": None, "trigger": cadence, "timezone": "America/Los_Angeles",
            "bindings": {"sources": ["source-connection-a", "source-connection-b"]
                         if recipe == "catalog-new-mail" else [],
                         "sender": self.drive["defaults"]["sender"]},
            "input_scope": {"source_accounts": ["source-account-a", "source-account-b"],
                            "selection": "missed received-time intervals"}
                           if recipe == "catalog-new-mail" else {"canonical_knowledge": "instance"},
            "desired_status": "enabled", "observed_status": "unverified",
            "last_verified": None, "configuration_revision": 1,
        }
        if blocked:
            self.snap("schedule-blocked:" + job_id, "Intent saved; host approval pending; no external schedule", actor)
            return
        external_ref = "schedule-ref-" + job_id
        self.external["schedules"][external_ref] = {"job_id": job_id, "status": "enabled", "scheduler": actor + "-cloud-scheduler"}
        if not response_lost:
            self.drive["jobs"][job_id].update(management_ref=external_ref,
                observed_status="enabled", last_verified="simulation-step-" + str(len(self.ledger) + 1))
        self.snap("schedule-created:" + job_id,
                  "Response lost; schedule state unverified" if response_lost else "Provider state observed", actor)

    def reconcile_job(self, job_id, can_inspect):
        if not can_inspect:
            self.snap("schedule-inspection-unavailable:" + job_id,
                      "Report known configuration; live status unverified")
            return
        matches = [(ref, value) for ref, value in self.external["schedules"].items()
                   if value["job_id"] == job_id]
        if len(matches) == 1:
            ref, value = matches[0]
            self.drive["jobs"][job_id].update(management_ref=ref,
                observed_status=value["status"], last_verified="simulation-reconciled")
        self.snap("schedule-reconciled:" + job_id,
                  "Exactly one matching external schedule adopted" if len(matches) == 1 else "Unresolved: zero or multiple matches")

    def send(self, job_id, run_id, response_lost=False, can_inspect=True):
        if run_id in self.drive["runs"] and not can_inspect:
            self.snap("send-inspection-unavailable:" + run_id, "Existing pending effect not blindly repeated")
            return
        if run_id in self.external["sent"]:
            self.drive["runs"][run_id]["outcome"] = "sent-observed"
            self.drive["runs"][run_id]["message_ref"] = self.external["sent"][run_id]["message_ref"]
            self.snap("send-reconciled:" + run_id, "Existing effect adopted; no repeat send")
            return
        job = self.drive["jobs"][job_id]
        self.drive["runs"][run_id] = {
            "job_id": job_id, "configuration_revision": job["configuration_revision"],
            "generator": job["executor"], "scheduler": job["scheduler"],
            "sender": job["bindings"]["sender"], "output_id": "output-" + run_id,
            "outcome": "pending", "message_ref": None,
        }
        self.external["sent"][run_id] = {"message_ref": "sent-ref-" + run_id}
        if not response_lost:
            self.drive["runs"][run_id].update(outcome="sent-observed",
                message_ref=self.external["sent"][run_id]["message_ref"])
        self.snap("send:" + run_id, "Response lost" if response_lost else "Sent observed")


def identity_tests():
    for probe in FIXTURES.get("identity_probes", []):
        first = probe["first"]
        second = probe["second"]
        a, b = MESSAGES[first["message_id"]], MESSAGES[second["message_id"]]
        check(probe["id"] + ":message", (message_key(a) == message_key(b)) == probe["expected_same_message"])
        if "expected_same_part" in probe:
            ap = next(p for p in a["parts"] if p["id"] == first["part_id"])
            bp = next(p for p in b["parts"] if p["id"] == second["part_id"])
            ap, bp = copy.deepcopy(ap), copy.deepcopy(bp)
            if "retrieval_token" in first:
                ap["retrieval_token"] = first["retrieval_token"]
                bp["retrieval_token"] = second["retrieval_token"]
                check(probe["id"] + ":different-handles", ap["retrieval_token"] != bp["retrieval_token"])
            check(probe["id"] + ":part", (part_key(a, ap) == part_key(b, bp)) == probe["expected_same_part"])
    sample = copy.deepcopy(next(iter(MESSAGES.values())))
    original = message_key(sample)
    sample["connection"] = "replacement-connector"
    sample["adapter"] = "replacement-adapter"
    check("adapter-replacement-preserves-source-identity", message_key(sample) == original)
    part = {"filename": "same-name.pdf", "size_bytes": 12, "content_hash": "same-hash"}
    check("missing-part-identity-remains-unresolved", part_key(sample, part) is None)
    same = copy.deepcopy(sample)
    same["thread_id"] = "display-thread-changed"
    check("thread-not-source-identity", message_key(same) == original)
    boundary = copy.deepcopy(sample)
    boundary["received_at"] = WINDOWS["daily"][0]
    check("half-open-scope-boundary", not in_scope(boundary, "historical") and in_scope(boundary, "daily"))
    # Nested attached email headers never create another top-level received message.
    attached = {"id": "attached-email", "nested_message_id": sample["provider_message_id"]}
    check("attached-email-belongs-to-outer-message", part_key(sample, attached).startswith(original + "/part/"))
    twin_a, twin_b = {"id": "part-a", "content_hash": "identical"}, {"id": "part-b", "content_hash": "identical"}
    check("same-bytes-two-occurrences-stay-distinct", part_key(sample, twin_a) != part_key(sample, twin_b))
    other_mailbox = copy.deepcopy(sample)
    other_mailbox["account"] = "source-account-b"
    check("same-communication-in-two-mailboxes-keeps-two-sources", message_key(sample) != message_key(other_mailbox))


def main():
    OUT.mkdir(exist_ok=True)
    identity_tests()
    model = Model()
    model.drive["connections"] = {
        "source-connection-a": {"source_account": "source-account-a", "adapter": "gmail-read-route-a"},
        "source-connection-b": {"source_account": "source-account-b", "adapter": "gmail-read-route-b"},
        "sender-a": {"service": "gmail", "account": "sending-account-a"},
        "sender-b": {"service": "mail-service", "account": "sending-account-b"},
    }
    model.drive["defaults"]["sender"] = "sender-a"
    model.snap("setup", "Pinned instructions, accounts and configured tools; no raw archive", "work-cloud")
    historical = [x["id"] for x in MESSAGES.values() if x["batch"] == "historical"]
    daily = [x["id"] for x in MESSAGES.values() if x["batch"] == "daily"]
    check("fixture-has-historical-and-daily", len(historical) >= 12 and len(daily) >= 3)
    model.discover("historical", [historical[:5]], complete=False)
    model.snap("historical-enumeration-first-page", "First page saved; enumeration and reading incomplete")
    text_only = {"text", "structural", "metadata", "container"}
    all_reads = text_only | {"image_vision", "chunked"}
    first = historical[0]
    model.ingest(first, "work-cloud", text_only, stop="after-read")
    check("interrupted-temp-is-not-progress", message_key(MESSAGES[first]) not in model.drive["sources"])
    check("fresh-session-no-old-temp", not model.temp)
    model.ingest(first, "work-cloud-new-session", text_only)
    second = historical[1]
    model.ingest(second, "work-cloud-new-session", text_only, stop="after-write")
    count = len(model.drive["facts"])
    model.ingest(second, "work-cloud-recovery", text_only)
    check("lost-write-response-no-duplicate-facts", len(model.drive["facts"]) == count)
    model.ingest(first, "readback-fault-probe", text_only, corrupt_readback=True)
    check("bad-readback-does-not-complete-source", first in model.drive["coverage"]["historical"]["pending"])
    check("queries-do-not-publish-unverified-evidence", "dismissal-time" not in model.available_facts())
    model.ingest(first, "readback-recovery", text_only)
    model.snap("historical-cursor-expired", "Saved scope and known identities permit re-enumeration; no cursor-dependent loss")
    model.discover("historical", [historical[:5], historical[5:10], historical[10:]], complete=True)
    check("rescan-deduplicates-discovered-messages", len(model.drive["coverage"]["historical"]["discovered"]) == len(historical))
    model.ingest("mail-005", "interrupted-import-agent", text_only, stop="after-source-index")
    check("cataloged-does-not-mean-interpreted", "swimming-consent-required" not in model.available_facts())
    model.ingest("mail-005", "interrupted-import-agent", text_only, stop="after-facts")
    check("partial-update-not-published-as-task-complete", "swimming-consent" not in model.drive["actions"] and "swimming-consent-required" not in model.available_facts())
    # Daily registration begins before the historical backlog has completed.
    model.create_job("daily-catalog", "work-cloud", "catalog-new-mail", "daily 07:00")
    job_accounts = {model.drive["connections"][connection]["source_account"]
                    for connection in model.drive["jobs"]["daily-catalog"]["bindings"]["sources"]}
    check("daily-job-bindings-cover-selected-source-accounts", job_accounts ==
          set(model.drive["jobs"]["daily-catalog"]["input_scope"]["source_accounts"]) ==
          {MESSAGES[item_id]["account"] for item_id in daily})
    model.create_job("weekly-audio", "second-agent-cloud", "weekly-audio", "Friday 17:00", response_lost=True)
    model.reconcile_job("weekly-audio", can_inspect=False)
    check("unknown-schedule-not-falsely-enabled", model.drive["jobs"]["weekly-audio"]["observed_status"] == "unverified")
    count = len(model.external["schedules"])
    model.reconcile_job("weekly-audio", can_inspect=True)
    check("lost-schedule-response-no-duplicate", len(model.external["schedules"]) == count)
    # A shared-file write can block both results and their proposed checkpoint.
    before = digest(model.drive)
    model.ingest(historical[2], "spark-shared-file", text_only, allow_write=False)
    check("blocked-all-writes-no-fake-checkpoint", digest(model.drive) == before)
    for item_id in historical[2:]:
        model.ingest(item_id, "work-cloud", text_only)
    pending_before = list(model.drive["coverage"]["historical"]["pending"])
    check("unread-attachments-remain-pending", bool(pending_before))
    # The source filter ignores historical context returned in a daily thread search.
    model.drive["coverage"]["daily"]["trigger_at"] = "2026-01-14T15:00:00Z"  # 07:00 PST.
    model.drive["coverage"]["daily"]["requested_interval"] = WINDOWS["daily"]
    model.snap("missed-daily-invocation", "Next invocation covers the missed interval, not only today's received messages")
    model.discover("daily", [daily[:2] + [historical[0]], daily[2:]], complete=True)
    check("missed-run-catches-previous-day-sources", len(model.drive["coverage"]["daily"]["discovered"]) == len(daily))
    check("thread-results-rechecked-against-message-scope", historical[0] not in model.drive["coverage"]["daily"]["discovered"])
    model.snap("daily-enumeration", "Daily coverage kept separate from historical backlog")
    # Preserve a parent's existing state through a later source correction/reply.
    for event in FIXTURES["parent_events"]:
        parent_action = event["action_key"]
        model.drive["actions"][parent_action]["status"] = event["status"]
        model.drive["actions"][parent_action]["parent_completion_evidence"] = copy.deepcopy(event)
    model.drive["actions"]["museum-fee"]["parent_planned_date"] = "2026-01-18"
    model.snap("parent-completion-recorded", "Swimming consent explicitly completed; no inference from reminder")
    for item_id in daily:
        model.ingest(item_id, "work-cloud-scheduled", text_only)
    check("daily-does-not-close-historical-gaps", model.drive["coverage"]["historical"]["pending"] == pending_before)
    if model.drive["actions"]:
        check("parent-completion-preserved", model.drive["actions"]["swimming-consent"]["status"] == "completed")
        check("parent-completion-evidence-preserved", model.drive["actions"]["swimming-consent"]["parent_completion_evidence"] == FIXTURES["parent_events"][0])
    check("standing-guideline-not-a-task", "dismissal-time" not in model.drive["actions"])
    check("explicit-school-correction-applied", model.drive["actions"]["museum-fee"]["due"] == "2026-01-20")
    check("school-correction-keeps-old-fact", "museum-fee-original" in model.drive["facts"])
    model.ingest("mail-004", "historical-rescan-after-daily", text_only)
    check("old-message-replay-cannot-revert-correction", model.drive["actions"]["museum-fee"]["due"] == "2026-01-20")
    check("parent-planning-survives-source-replay", model.drive["actions"]["museum-fee"]["parent_planned_date"] == "2026-01-18")
    check("finite-decline-response-remains-action", "museum-response" in model.drive["actions"])
    check("optional-exhibition-no-invented-task", all("exhibition" not in k for k in model.drive["actions"]))
    check("unread-image-cannot-supply-fact", "garden-boots" not in model.drive["facts"])
    check("oversized-handbook-pending-without-route", "absence-report-time" not in model.drive["facts"])
    check("unread-club-table-cannot-supply-fact", "chess-club" not in model.drive["facts"])
    model.snap("cross-agent-query-before-attachment", {"answer": "Club timetable unread; time unknown",
               "source": "mail-010", "pending_part": "club-timetable"}, "cowork-cloud-reader")
    # Vision/chunked processing is an assumed alternative, not a certified app capability.
    for item_id in pending_before:
        model.ingest(item_id, "qualified-reading-route-assumed", all_reads)
    check("modeled-transfer-quanta-bounded", model.max_modeled_temp_quantum <= TEMP_QUANTUM)
    check("unavailable-remains-unread-despite-large-model", "chess-club" not in model.drive["facts"])
    model.external["restored_parts"].append("mail-010/club-timetable")
    model.ingest("mail-010", "alternative-source-reader-assumed", text_only)
    check("restored-attachment-adds-fact", "chess-club" in model.drive["facts"])
    for fact_id in ("menu-jan19", "menu-jan20"):
        check("repeated-content-retains-both-provenances:" + fact_id,
              len(model.drive["facts"][fact_id]["provenance"]) == 2)
    count = len(model.drive["sources"])
    before = digest(model.drive["facts"])
    model.ingest("mail-009", "replacement-connector-same-account", text_only)
    check("adapter-replay-keeps-catalog-and-evidence", len(model.drive["sources"]) == count and digest(model.drive["facts"]) == before)
    model.reset_agent()
    check("no-temporary-sources-after-processing", not model.temp)
    for query in EXPECTED.get("queries", []):
        if query["id"] == "query-club-before-read":
            continue  # The negative scenario was exercised before restoring access.
        keys = query.get("expected_fact_keys", [])
        available = [key for key in keys if key in model.available_facts()]
        check("query-evidence-present:" + query["id"], set(available) == set(keys))
        model.snap("cross-agent-query:" + query["id"], {
            "question": query["question"], "available_fact_keys": available,
            "missing_fact_keys": sorted(set(keys) - set(available)),
            "available_evidence": {key: model.drive["facts"][key] for key in available},
            "language_answer_generated": False,
            "status": "answerable-from-Drive" if len(available) == len(keys) else "coverage-gap",
        }, "cowork-cloud-reader")
    model.snap("known-jobs-query", {job_id: {k: value[k] for k in (
        "purpose", "executor", "scheduler", "management_ref", "observed_status", "last_verified")}
        for job_id, value in model.drive["jobs"].items()}, "another-connected-agent")
    check("multiple-agent-jobs-retained", len(model.drive["jobs"]) == 2)
    model.send("daily-catalog", "daily-run-001", response_lost=True)
    model.send("daily-catalog", "daily-run-001", can_inspect=False)
    check("send-without-inspection-stays-pending", model.drive["runs"]["daily-run-001"]["outcome"] == "pending")
    model.send("daily-catalog", "daily-run-001")
    check("lost-send-response-no-duplicate", len(model.external["sent"]) == 1)
    old_attribution = copy.deepcopy(model.drive["runs"]["daily-run-001"])
    model.drive["defaults"]["sender"] = "sender-b"
    check("default-change-does-not-rebind-job", model.drive["jobs"]["daily-catalog"]["bindings"]["sender"] == "sender-a")
    model.drive["jobs"]["daily-catalog"]["bindings"]["sender"] = "sender-b"
    model.drive["jobs"]["daily-catalog"]["configuration_revision"] += 1
    # Changing sender is a modeled provider-observed configuration update, not moving the scheduler.
    model.external["schedules"][model.drive["jobs"]["daily-catalog"]["management_ref"]]["sender"] = "sender-b"
    model.send("daily-catalog", "daily-run-002")
    check("old-output-attribution-survives-switch", model.drive["runs"]["daily-run-001"] == old_attribution)
    check("new-output-uses-new-binding", model.drive["runs"]["daily-run-002"]["sender"] == "sender-b")
    model.create_job("backup-recap", "backup-agent-cloud", "user-requested-additional-recap", "Sunday 18:00")
    check("adding-backup-job-keeps-existing-jobs", len(model.drive["jobs"]) == 3 and len(model.external["schedules"]) == 3)
    model.snap("output-attribution-query", copy.deepcopy(model.drive["runs"]), "another-connected-agent")
    model.drive["jobs"]["weekly-audio"]["desired_status"] = "paused"
    model.snap("unreachable-scheduler-pause-request", "Desired paused; last observed enabled; no claim provider stopped")
    check("desired-status-is-not-provider-state", model.drive["jobs"]["weekly-audio"]["observed_status"] == "enabled")
    model.external["source_available"][first] = False
    saved = digest(model.drive["facts"])
    model.ingest(first, "backup-agent-cloud", all_reads)
    check("source-deletion-preserves-cataloged-knowledge", digest(model.drive["facts"]) == saved)
    # An unknown product is not assumed to read/write because it is an agent.
    model.snap("unqualified-agent-surface", "Exact Drive read/write tools unknown: no simulated successful operation", "muse-or-unqualified-surface")
    model.snap("withdrawn-native-writer", "Native write availability conflicted: alternative route requires qualification", "grok-bot")
    check("no-source-text-stored-in-catalog", all("text" not in p for s in model.drive["sources"].values() for p in s["parts"].values()))
    model.snap("final", "Only processed knowledge and references retained; same-data concurrency was not modeled")
    expected_fact_keys = {fact["key"] for source in EXPECTED["sources"].values() for fact in source["facts"]}
    check("final-inventory-matches-supplied-oracle", set(model.drive["facts"]) == expected_fact_keys)
    check("all-fixture-sources-complete-after-assumed-recovery", all(source["status"] == "complete" for source in model.drive["sources"].values()))
    result = {
        "kind": "abstract-state-simulation-not-live-product-test",
        "semantic_quality_tested": False,
        "actual_connector_memory_or_timing_tested": False,
        "same_data_concurrent_writes_tested": False,
        "checks": CHECKS, "check_count": len(CHECKS),
        "all_passed": all(x["passed"] for x in CHECKS),
        "state_steps": len(model.ledger),
        "modeled_temp_quantum_budget_bytes": TEMP_QUANTUM,
        "max_modeled_temp_quantum_bytes": model.max_modeled_temp_quantum,
        "modeled_read_quanta": model.modeled_read_quanta,
        "fixture_hash": digest(FIXTURES), "expectation_hash": digest(EXPECTED),
        "final_counts": {key: len(model.drive[key]) for key in ("sources", "facts", "actions", "jobs", "runs")},
        "coverage": model.drive["coverage"],
    }
    for name, value in (("state-ledger.json", model.ledger), ("final-state.json", model.drive),
                        ("checks.json", result)):
        (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    lines = ["# Synthetic state ledger", "", "Generated by run_model.py. All states and effects are modeled; none are live provider observations.", "",
             "| Step | Event | Sources | Facts | Actions | Known jobs | Runs | Historical pending | Daily pending |",
             "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    for entry in model.ledger:
        d = entry["drive"]
        lines.append("| " + " | ".join(map(str, [entry["step"], entry["label"],
            *[len(d[k]) for k in ("sources", "facts", "actions", "jobs", "runs")],
            len(d["coverage"]["historical"]["pending"]), len(d["coverage"]["daily"]["pending"])])) + " |")
    (OUT / "state-ledger.md").write_text("\n".join(lines) + "\n")
    print(json.dumps({k: result[k] for k in ("kind", "check_count", "all_passed", "state_steps", "final_counts", "coverage")}, indent=2))


if __name__ == "__main__":
    main()
