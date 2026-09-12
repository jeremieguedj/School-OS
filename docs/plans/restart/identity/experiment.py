#!/usr/bin/env python3
"""Small synthetic identity experiment; not a connector or production runtime.

Inputs are normalized observations supplied by the fixture. This experiment
does not establish that any app supplies complete bodies or accurate metadata.
Raw fictional text is transient; saved witnesses contain only its digest.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

OUT = Path(__file__).with_name("experiment-results.json")


def observe(body="Bring boots.", **changes):
    item = {
        "account": "synthetic-mailbox-a", "account_verified": True,
        "sender": "school@example.org", "sent_at": "2026-01-05T09:00:00Z",
        "received_at": "2026-01-05T09:00:02Z",
        "subject": "Garden morning", "to": ["parent@example.org"], "cc": [],
        "rfc_message_id": "message-a@example.org", "in_reply_to": None,
        "alias": ["gmail-api-message", "synthetic-provider-a"],
        "thread": "synthetic-thread-a", "profile": "decoded-text-lf-v1",
        "body_complete": True, "attachment_inventory_complete": True,
        "attachments": [],
    }
    item.update(changes)
    # Only line-ending representation is equated. No whitespace collapsing,
    # quote stripping, summarization, HTML rendering or semantic hashing.
    item["body_digest"] = hashlib.sha256(body.replace("\r\n", "\n").encode()).hexdigest()
    return item


def complete(item):
    return (item["body_complete"] and item["attachment_inventory_complete"]
            and all(part.get("digest") for part in item["attachments"]))


def payload(item):
    if not complete(item):
        return None
    # Preserve multiplicity; equal attachment bytes are not an occurrence ID.
    return (item["profile"], item["body_digest"],
            tuple((x["name"], x["mime"], x["digest"]) for x in item["attachments"]))


SOURCE_FIELDS = ("sender", "sent_at", "received_at", "subject", "to", "cc")


def comparable_value(item, field):
    found = item.get(field)
    if found is None:
        return None
    if field in {"to", "cc"}:
        return sorted(found)  # Preserve role and multiplicity, not display order.
    if field in {"sent_at", "received_at"}:
        # Fixture supplies precise zoned dates. Unknown precision remains a
        # separate missing observation; a production recipe may compare ranges.
        return datetime.fromisoformat(found.replace("Z", "+00:00")).astimezone(timezone.utc)
    return found


def header_match(a, b):
    return all(a.get(field) is not None and comparable_value(a, field) ==
               comparable_value(b, field) for field in SOURCE_FIELDS)


def comparable_conflict(a, b):
    for field in SOURCE_FIELDS:
        av, bv = comparable_value(a, field), comparable_value(b, field)
        if av is not None and bv is not None and av != bv:
            return True
    return (complete(a) and complete(b) and a["profile"] == b["profile"]
            and payload(a) != payload(b))


def resolve(incoming, records, candidate_lookup_complete=True):
    """Return evidence disposition without overwriting any catalog record."""
    if not incoming["account_verified"]:
        return {"status": "account-unverified", "record_ids": []}
    scoped = [r for r in records if r["witness"]["account"] == incoming["account"]]
    # Native IDs, RFC identifiers, citations and thread handles are deliberately
    # excluded from identity decisions, even when documented stable. They can
    # help an adapter retrieve a candidate, outside this resolver.
    if not candidate_lookup_complete:
        return {"status": "lookup-incomplete", "record_ids": []}
    equivalent = [r for r in scoped if header_match(incoming, r["witness"])
                  and payload(incoming) is not None
                  and payload(incoming) == payload(r["witness"])
                  and not comparable_conflict(incoming, r["witness"])]
    if len(equivalent) > 1:
        return {"status": "ambiguous-occurrence", "record_ids": [r["record_id"] for r in equivalent]}
    if len(equivalent) == 1:
        return {"status": "content-match-occurrence-unverified", "record_ids": [equivalent[0]["record_id"]]}
    unresolved = [r for r in scoped if not comparable_conflict(incoming, r["witness"])]
    if unresolved or not complete(incoming) or not header_match(incoming, incoming):
        return {"status": "needs-more-evidence", "record_ids": [r["record_id"] for r in unresolved]}
    return {"status": "new-observation", "record_ids": []}


def record(identifier, witness):
    return {"record_id": identifier, "witness": copy.deepcopy(witness)}


def main():
    results = []
    baseline = observe()
    original = record("sos-source-001", baseline)

    def case(name, incoming, expected, records=None, lookup=True):
        records = copy.deepcopy(records if records is not None else [original])
        before = copy.deepcopy(records)
        actual = resolve(incoming, records, lookup)
        assert actual["status"] == expected, (name, actual, expected)
        assert records == before, "Resolution may not overwrite canonical state"
        stripped = copy.deepcopy(incoming)
        stripped_records = copy.deepcopy(records)
        for observation in [stripped] + [r["witness"] for r in stripped_records]:
            for field in ("alias", "rfc_message_id", "in_reply_to", "thread"):
                observation[field] = None
        assert resolve(stripped, stripped_records, lookup) == actual, "External IDs must not decide identity"
        results.append({"case": name, "expected": expected, "actual": actual,
                        "catalog_unchanged": records == before, "external_id_erasure_preserves_decision": True, "passed": True})

    case("native-id-does-not-decide-acceptance", observe(), "content-match-occurrence-unverified")
    case("changed-provider-id", observe(alias=["gmail-api-message", "new-handle"]), "content-match-occurrence-unverified")
    case("provider-id-absent", observe(alias=None), "content-match-occurrence-unverified")
    case("provider-and-rfc-ids-both-absent", observe(alias=None, rfc_message_id=None), "content-match-occurrence-unverified")
    case("connector-switched", observe(alias=["other-connector", "opaque-handle"]), "content-match-occurrence-unverified")
    case("thread-id-changed", observe(thread="different-thread"), "content-match-occurrence-unverified")
    case("thread-id-alone-insufficient", observe(alias=None, rfc_message_id=None, body_complete=False), "needs-more-evidence")
    case("same-rfc-id-does-not-hide-new-body", observe("Bring sandals.", alias=None), "new-observation")
    case("same-native-id-cannot-hide-distinct-body", observe("Bring sandals."), "new-observation")
    case("same-native-id-cannot-hide-distinct-sender", observe(sender="other@example.org"), "new-observation")
    case("same-spelling-other-namespace-not-authority", observe("Bring sandals.", alias=["search-citation", "synthetic-provider-a"]), "new-observation")
    case("incomplete-catalog-lookup", observe(alias=None), "lookup-incomplete", lookup=False)
    case("snippet-only-is-not-full-body", observe(alias=None, body_complete=False), "needs-more-evidence")
    case("unknown-attachment-inventory", observe(alias=None, attachment_inventory_complete=False), "needs-more-evidence")
    case("html-versus-plain-projection-needs-bridge", observe(alias=None, profile="html-rendered-v2"), "needs-more-evidence")
    case("unknown-sender-date-does-not-become-empty", observe(alias=None, sent_at=None), "needs-more-evidence")
    case("unknown-source-account", observe(account_verified=False), "account-unverified")
    case("same-content-other-mailbox-keeps-provenance-separate", observe(account="synthetic-mailbox-b"), "new-observation")
    case("reply-with-parent-quote-is-new", observe("Yes.\n> Bring boots.", alias=None,
         rfc_message_id="reply@example.org", in_reply_to="message-a@example.org",
         sent_at="2026-01-05T10:00:00Z"), "new-observation")
    case("identical-short-reply-later-is-new", observe("Bring boots.", alias=None,
         rfc_message_id=None, sent_at="2026-01-06T09:00:00Z"), "new-observation")
    case("quoted-history-must-not-be-stripped", observe("Bring boots.\n> Bring sandals.", alias=None), "new-observation")
    case("significant-whitespace-is-not-collapsed", observe("Bring  boots.", alias=None), "new-observation")
    twin = record("sos-source-002", observe(alias=["gmail-api-message", "second-copy"]))
    case("indistinguishable-copies-without-locator", observe(alias=None), "ambiguous-occurrence", [original, twin])
    case("known-id-does-not-resolve-content-ambiguity", observe(), "ambiguous-occurrence", [original, twin])
    collision = record("sos-source-003", observe())
    case("duplicate-alias-in-index", observe(), "ambiguous-occurrence", [original, collision])
    line_record = record("sos-source-lines", observe("Line one\r\nLine two"))
    case("line-ending-representation-only", observe("Line one\nLine two", alias=None),
         "content-match-occurrence-unverified", [line_record])
    a = {"name": "menu.pdf", "mime": "application/pdf", "digest": "synthetic-menu-content"}
    b = {"name": "menu.pdf", "mime": "application/pdf", "digest": "synthetic-procedure-content"}
    attached = record("sos-source-attachments", observe(attachments=[a]))
    case("same-filename-different-attachment-content", observe(alias=None, attachments=[b]), "new-observation", [attached])
    case("duplicate-attachment-multiplicity-preserved", observe(alias=None, attachments=[a, a]), "new-observation", [attached])
    missing = {**a, "digest": None}
    case("unread-attachment-cannot-prove-equality", observe(alias=None, attachments=[missing]), "needs-more-evidence", [attached])
    case("changed-rfc-id-does-not-decide-identity", observe(alias=None, rfc_message_id="MESSAGE-A@example.org"), "content-match-occurrence-unverified")
    citation = record("sos-source-citation", observe(alias=["search-citation", "result-0"]))
    case("reused-citation-cannot-decide-acceptance", observe("Changed hidden body.",
         alias=["search-citation", "result-0"], body_complete=False), "needs-more-evidence", [citation])
    never_ids = record("sos-source-no-external-ids", observe(alias=None, rfc_message_id=None))
    case("neither-stored-nor-incoming-message-ever-had-ids", observe(alias=None, rfc_message_id=None),
         "content-match-occurrence-unverified", [never_ids])
    two_recipients = record("sos-source-recipients", observe(to=["a@example.org", "b@example.org"]))
    case("recipient-order-is-not-identity", observe(alias=None, to=["b@example.org", "a@example.org"]),
         "content-match-occurrence-unverified", [two_recipients])
    case("attachment-source-name-preserved", observe(alias=None, attachments=[{**a, "name": "procedure.pdf"}]),
         "new-observation", [attached])

    case("received-date-does-not-mean-sender-date", observe(received_at="2026-01-06T09:00:02Z"), "new-observation")
    case("timezone-presentation-is-normalized", observe(received_at="2026-01-05T01:00:02-08:00"), "content-match-occurrence-unverified")
    case("cc-role-is-preserved", observe(to=[], cc=["parent@example.org"]), "new-observation")
    case("missing-received-time-needs-another-recipe", observe(received_at=None), "needs-more-evidence")
    # Persistence uses a School-OS-owned identifier, independent of provider ID.
    persisted = json.loads(json.dumps([never_ids]))
    again = resolve(observe(alias=None, rfc_message_id=None), persisted)
    assert again["record_ids"] == ["sos-source-no-external-ids"]
    assert all("body" not in r["witness"] for r in persisted)
    other_progress = resolve(observe(sender="different@example.org", alias=None), persisted)
    assert other_progress["status"] == "new-observation"
    result = {
        "kind": "synthetic-source-information-identity-matching",
        "provider_rfc_thread_or_citation_ids_used_in_identity_decisions": False,
        "cases": results, "case_count": len(results), "all_passed": True,
        "json_roundtrip_keeps_school_os_id_with_no_stored_or_incoming_message_ids": True,
        "raw_body_retained_in_catalog": False,
        "independent_resolver_call_succeeds_after_an_unresolved_case": True,
        "live_source_enumeration_or_adapter_normalization_tested": False,
        "exact_occurrence_proven_without_distinguishing_evidence": False,
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "cases"}, indent=2))


if __name__ == "__main__":
    main()
