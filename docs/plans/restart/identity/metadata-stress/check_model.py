"""Bounded independent synthetic checks; all source fields are fictional.

Policy checks are reported separately from reproduced limitations. This is not
a real-mail accuracy estimate. External IDs are used only as deliberately
irrelevant test input, never as model evidence.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys

from model import addresses, flattened_recipients, flattened_sender, record, relation, resolve, source_date


def observation(**changes):
    item = {
        "account": "fictional-mailbox", "account_verified": True,
        "subject": "Museum visit", "sender": "school@example.org",
        "sent": source_date("Fri, 11 Sep 2026 09:00:00 +0000", "sent"),
        "received": source_date("Fri, 11 Sep 2026 09:00:03 +0000", "received"),
        "to": ["parent@example.org", "guardian@example.org"], "cc": [],
        "filenames": ["permission.pdf", "map.png", "map.png"],
        "filename_scope": "original_named_attachments", "filenames_complete": True,
    }
    item.update(copy.deepcopy(changes))
    return item


def main():
    checks = []
    limitations = []
    base = observation()
    catalog = [record("source-a", base)]

    def check(name, condition):
        checks.append({"case": name, "passed": bool(condition)})

    def decision(name, incoming, expected, records=None, **options):
        before = copy.deepcopy((incoming, records if records is not None else catalog))
        actual = resolve(incoming, records if records is not None else catalog, **options)
        check(name, actual["status"] == expected)
        checks[-1].update({"expected": expected, "actual": actual["status"]})
        assert before == (incoming, records if records is not None else catalog), "Input mutation"
        return actual

    # 38 policy checks, including an independently identified generated-name
    # counterexample that requires an explicit original-name provenance boundary.
    decision("repeat-exact-observation", base, "metadata_association")
    decision("equivalent-zoned-timestamp", observation(
        sent=source_date("Fri, 11 Sep 2026 02:00:00 -0700", "sent")), "metadata_association")
    decision("recipient-and-filename-order", observation(
        to=list(reversed(base["to"])), filenames=list(reversed(base["filenames"]))), "metadata_association")
    decision("optional-fields-unknown", observation(
        to=None, cc=None, received=None, filenames=None, filename_scope=None,
        filenames_complete=False), "metadata_association")
    empty = observation(filenames=[], filename_scope="original_named_attachments")
    decision("unknown-inventory-is-not-empty", observation(
        filenames=None, filenames_complete=False), "metadata_association", [record("empty", empty)])
    decision("recipient-roles-remain-distinct", observation(
        to=[], cc=base["to"]), "new_observation")
    decision("filename-multiplicity-preserved", observation(
        filenames=["permission.pdf", "map.png"]), "new_observation")
    decision("incompatible-inventory-scope", observation(
        filenames=["inline.png"], filename_scope="original-inline-inclusive"), "metadata_association")
    decision("generated-names-are-not-identity-evidence", observation(
        filenames=["temporary-b.pdf"], filename_scope="connector-generated-downloads"),
        "metadata_association", [record("generated", observation(
            filenames=["temporary-a.pdf"], filename_scope="connector-generated-downloads"))])
    no_zone = source_date("Fri, 11 Sep 2026 09:00:00", "sent")
    decision("missing-zone-is-unknown", observation(sent=no_zone, received=None), "needs_metadata")
    decision("invalid-date-is-unknown", observation(
        sent=source_date("invalid date", "sent"), received=None), "needs_metadata")
    minute = source_date("Fri, 11 Sep 2026 09:00 +0000", "sent")
    decision("minute-overlap-is-not-exact", observation(sent=minute, received=None), "needs_metadata")
    day = {"value": "2026-09-11T00:00:00+00:00", "precision": "day", "meaning": "sent", "zone_known": True}
    decision("utc-day-overlap-is-not-exact", observation(sent=day, received=None), "needs_metadata")
    decision("all-times-unavailable", observation(sent=None, received=None), "needs_metadata")
    decision("receipt-to-receipt-alternative", observation(sent=None), "metadata_association")
    decision("sent-never-substitutes-for-receipt", observation(
        sent=None, received={**base["sent"], "meaning": "received"}), "new_observation")
    decision("incorrect-timestamp-meaning-is-unknown", observation(
        sent={**base["sent"], "meaning": "received"}, received=None), "needs_metadata")
    twins = [record("source-a", base), record("source-b", base)]
    decision("visible-two-record-collision", base, "ambiguous_metadata", twins)
    check("catalog-order-does-not-select-a-winner", resolve(base, twins) == resolve(base, list(reversed(twins))))
    plus_sender = observation(sender="school+class@example.org")
    decision("sender-plus-tag-is-preserved", plus_sender, "new_observation")
    decision("reply-is-an-individual-message", observation(
        subject="Re: Museum visit", sender="parent@example.org",
        sent=source_date("Fri, 11 Sep 2026 09:14:00 +0000", "sent"),
        received=source_date("Fri, 11 Sep 2026 09:14:03 +0000", "received")), "new_observation")
    decision("original-reply-prefix-is-not-stripped-for-identity", observation(
        subject="Re: Museum visit"), "new_observation")
    decision("incomplete-lookup-cannot-associate", base, "lookup_incomplete", lookup_complete=False)
    decision("incomplete-lookup-cannot-create", observation(subject="Different subject"),
             "lookup_incomplete", lookup_complete=False)
    left = observation(received=None)
    right = observation(sent=source_date("Fri, 11 Sep 2026 09:00:40 +0000", "sent"), received=None)
    middle = observation(sent=minute, received=None)
    check("coarse-overlap-cannot-merge-exact-endpoints",
          relation(left, right) == "distinct_metadata"
          and resolve(middle, [record("left", left), record("right", right)])["status"] == "ambiguous_metadata"
          and relation(left, middle) == relation(middle, right) == "compatible_incomplete")
    with_ids = observation(provider_id="temporary-a", thread_id="thread-a", rfc_message_id="fictional@example.org",
                           body="Irrelevant fictional body", attachment_digest="irrelevant-digest")
    changed_ids = observation(provider_id="temporary-b", thread_id="thread-b", rfc_message_id=None,
                             body="Different irrelevant body", attachment_digest=None)
    original_inputs = copy.deepcopy((with_ids, changed_ids, catalog))
    check("external-ids-content-and-input-mutation",
          resolve(with_ids, catalog) == resolve(changed_ids, catalog) == resolve(base, catalog)
          and record("source-a", with_ids) == record("source-a", changed_ids) == catalog[0]
          and (with_ids, changed_ids, catalog) == original_inputs)
    check("fresh-json-session-preserves-association",
          resolve(json.loads(json.dumps(base)), json.loads(json.dumps(catalog))) == resolve(base, catalog))
    check("address-presentation-preserves-meaning",
          addresses(["School <school@EXAMPLE.ORG>"]) == ["school@example.org"]
          and addresses(["School <School@example.org>"]) == ["School@example.org"]
          and addresses(None) is None and addresses([]) == [])
    sender_presentations = [
        ("flattened-unquoted-school-label", "Example School office@example.org",
         '"Example School" <office@example.org>'),
        ("flattened-quoted-dotted-label", '"teacher.name" teacher@example.org',
         '"teacher.name" <teacher@example.org>'),
        ("flattened-quoted-parenthesized-label", '"Example School (Primary)" office@example.org',
         '"Example School (Primary)" <office@example.org>'),
        ("flattened-label-containing-an-address", '"staff@example.org" staff@example.org',
         '"staff@example.org" <staff@example.org>'),
    ]
    for name, flattened, header in sender_presentations:
        check(name, [flattened_sender(flattened)] == addresses(header)
              and flattened_sender(flattened) == flattened_sender(header))
    check("flattened-recipient-list-matches-rfc-header",
          flattened_recipients(['Example Parent parent@example.org', '"Second Parent" other@example.org'])
          == addresses('Example Parent <parent@example.org>, "Second Parent" <other@example.org>'))
    check("flattened-recipient-label-containing-comma",
          flattened_recipients(['"Family, Parent" parent@example.org'])
          == addresses('"Family, Parent" <parent@example.org>') == ["parent@example.org"])
    check("flattened-recipient-label-containing-address",
          flattened_recipients(['"parent@example.org" parent@example.org'])
          == addresses('"parent@example.org" <parent@example.org>') == ["parent@example.org"])
    check("empty-recipient-field-preserves-unknown-versus-empty",
          flattened_recipients(None) is None and addresses(None) is None
          and flattened_recipients([]) == flattened_recipients("") == addresses("") == addresses([]) == [])
    check("explicit-empty-rfc-recipient-groups",
          addresses("ExampleRecipients:;") == flattened_recipients("ExampleRecipients:;") == []
          and flattened_recipients(["ExampleRecipients:;", "Example Parent parent@example.org"])
          == ["parent@example.org"])
    check("malformed-recipient-text-does-not-become-empty",
          addresses("not an address") is None and flattened_recipients("not an address") is None
          and addresses("ExampleRecipients;") is None and flattened_recipients("ExampleRecipients;") is None)

    # These demonstrate a boundary failure; reproducing it is not a successful
    # identity result. The unseen occurrence label is truth outside model input.
    hidden_result = resolve(copy.deepcopy(base), catalog)
    limitations.append({
        "case": "distinct-hidden-occurrence-with-identical-metadata",
        "observed": hidden_result["status"],
        "risk": "false association if this observation is another physical delivery",
        "reproduced": hidden_result["status"] == "metadata_association",
    })

    def naive_sequential(truth_order):
        stored = []
        partitions = {}
        for occurrence in truth_order:
            incoming = copy.deepcopy(base)
            result = resolve(incoming, stored)
            if result["status"] == "new_observation":
                key = "assigned-" + str(len(stored) + 1)
                stored.append(record(key, incoming))
            else:
                key = result["record_ids"][0]
            partitions.setdefault(key, []).append(occurrence)
        return sorted(sorted(group) for group in partitions.values())

    forward = naive_sequential(["occurrence-a", "occurrence-b"])
    reverse = naive_sequential(["occurrence-b", "occurrence-a"])
    limitations.append({
        "case": "sequential-import-hides-visible-batch-multiplicity",
        "risk": "first record absorbs the second; later multi-candidate detection cannot recover multiplicity",
        "forward_groups": forward, "reverse_groups": reverse,
        "reproduced": forward == reverse == [["occurrence-a", "occurrence-b"]],
    })
    assert len(checks) == 38 and len(limitations) == 2
    report = {
        "scope": "fictional metadata-only policy checks, not live accuracy rates",
        "policy_checks": len(checks), "policy_passed": sum(item["passed"] for item in checks),
        "policy_failed": sum(not item["passed"] for item in checks),
        "limitations_reproduced": sum(item["reproduced"] for item in limitations),
        "checks": checks, "known_limitations": limitations,
        "unqualified": ["partial recipient lists", "local-calendar-day intervals across DST",
                        "actual cross-provider metadata access", "complete mailbox discovery"],
    }
    output = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if len(sys.argv) == 2:
        Path(sys.argv[1]).write_text(output)
    else:
        print(output, end="")
    return 1 if report["policy_failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
