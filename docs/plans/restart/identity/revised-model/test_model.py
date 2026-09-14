"""Prepared fictional checks. Not executed during the implementation phase.

Labels and expectations are authored here independently of model decisions.
No live provider entry is used as a logical-email ground-truth label.
"""

from dataclasses import replace
import json
import unittest

from model import (
    AttachmentInventory, AttachmentReadPass, Catalog, DateObservation,
    LogicalEmail, Observation, ReadCandidate, Recipients, WindowProgress,
    WindowScope, normalize, normalize_address, normalize_subject,
)


MONDAY = DateObservation("Mon, 14 Sep 2026 09:00:00 -0700", "original_date", "second")
MONDAY_UTC = DateObservation("Mon, 14 Sep 2026 16:00:00 +0000", "original_date", "second")
REPLY = DateObservation("Mon, 14 Sep 2026 11:20:00 -0700", "original_date", "second")
LATER_REPLY = DateObservation("Tue, 15 Sep 2026 08:15:00 -0700", "original_date", "second")


def email(**changes):
    original = Observation(
        mailbox_id="household-mailbox-a", mailbox_verified=True,
        subject="School update", sender="Example School <office@example.org>",
        original_date=MONDAY,
        to=Recipients(("Parent <parent@example.net>",)),
        cc=Recipients(()),
    )
    return replace(original, **changes)


# The labels specify the fictional story, not a projection of observed handles.
LOGICAL_LABELS = (
    ("original-notice", email(access_hints=("temporary-result-a",))),
    ("original-notice", email(subject=" School update ",
                              sender="Example School office@EXAMPLE.ORG",
                              original_date=MONDAY_UTC,
                              access_hints=("replacement-result-z",))),
    ("first-reply", email(subject="Re: School update", original_date=REPLY)),
    ("second-reply", email(subject="Re: School update", original_date=LATER_REPLY)),
    ("different-recipient-notice", email(to=Recipients(("another@example.net",)))),
)


class MetadataExamples(unittest.TestCase):
    def test_authored_logical_labels_not_provider_entry_counts(self):
        catalog, assigned = Catalog(), {}
        for ordinal, (label, observation) in enumerate(LOGICAL_LABELS):
            result = catalog.admit(observation, "school-email-" + str(ordinal))
            if label in assigned:
                self.assertEqual(result.status, "reuse")
                self.assertEqual(result.record_id, assigned[label])
            else:
                self.assertEqual(result.status, "new")
                assigned[label] = result.record_id
        self.assertEqual(len(catalog.records), 4)

    def test_normalization_preserves_observed_subject_address_and_dates(self):
        observed = email(subject=" =?utf-8?q?School_update?= ",
                         sender="Example School office@EXAMPLE.ORG")
        catalog = Catalog()
        catalog.admit(observed, "school-email-original")
        catalog.admit(email(original_date=MONDAY_UTC))
        record = catalog.records["school-email-original"]
        self.assertEqual(record.observations[0].subject, " =?utf-8?q?School_update?= ")
        self.assertEqual(record.observations[0].sender, "Example School office@EXAMPLE.ORG")
        self.assertEqual(record.observations[0].original_date, MONDAY)
        self.assertEqual(record.observations[1].original_date, MONDAY_UTC)
        self.assertEqual(record.comparisons[0].subject, "School update")
        self.assertEqual(record.comparisons[0].sender, "office@example.org")

    def test_subject_unfolding_does_not_remove_meaningful_text(self):
        self.assertEqual(normalize_subject(" School\r\n update "), "School update")
        self.assertEqual(normalize_subject("Re: School  update"), "Re: School  update")
        self.assertNotEqual(normalize_subject("school update"), "School update")
        self.assertNotEqual(normalize_subject("Fwd: School update"), "School update")

    def test_address_local_part_case_dots_and_plus_tags_are_preserved(self):
        self.assertEqual(normalize_address("Office.Name+News@EXAMPLE.ORG"),
                         "Office.Name+News@example.org")
        self.assertNotEqual(normalize_address("Office@example.org"),
                            normalize_address("office@example.org"))
        self.assertIsNone(normalize_address("first@example.org second@example.org"))

    def test_complete_recipient_order_is_irrelevant_but_roles_are_preserved(self):
        first = email(to=Recipients(("a@example.net", "b@EXAMPLE.NET")))
        second = email(to=Recipients(("b@example.net", "a@example.net")))
        catalog = Catalog()
        catalog.admit(first, "school-email-a")
        self.assertEqual(catalog.admit(second).status, "reuse")
        moved_role = email(to=Recipients(("a@example.net",)),
                           cc=Recipients(("b@example.net",)))
        self.assertEqual(catalog.admit(moved_role, "school-email-b").status, "new")

    def test_unknown_recipient_list_is_not_an_explicit_empty_list(self):
        self.assertIsNone(normalize(email(to=None)).to)
        self.assertIsNone(normalize(email(to=Recipients(("partial@example.net",), False))).to)
        self.assertEqual(normalize(email(to=Recipients(()))).to, ())
        catalog = Catalog()
        catalog.admit(email(), "school-email-a")
        self.assertEqual(catalog.admit(email(to=None)).status, "reuse")
        self.assertEqual(catalog.admit(email(to=Recipients(())), "school-email-b").status, "new")

    def test_each_reply_has_its_own_date_and_record(self):
        catalog = Catalog()
        original = catalog.admit(email(), "school-email-original")
        first = catalog.admit(email(subject="Re: School update", original_date=REPLY),
                              "school-email-first-reply")
        later = catalog.admit(email(subject="Re: School update", original_date=LATER_REPLY),
                              "school-email-later-reply")
        self.assertEqual(len({original.record_id, first.record_id, later.record_id}), 3)
        self.assertEqual(catalog.records[first.record_id].observations[0].original_date, REPLY)

    def test_different_mailboxes_preserve_separate_source_provenance(self):
        catalog = Catalog()
        catalog.admit(email(), "school-email-a")
        result = catalog.admit(email(mailbox_id="household-mailbox-b"), "school-email-b")
        self.assertEqual(result.status, "new")

    def test_unsupported_date_views_remain_pending_without_production_threshold_claim(self):
        views = (
            None,
            DateObservation("Mon, 14 Sep 2026 09:00 -0700", "original_date", "minute"),
            DateObservation("Mon, 14 Sep 2026 09:00:00", "original_date", "second"),
            DateObservation("Mon, 14 Sep 2026 09:00:00 -0000", "original_date", "second"),
            DateObservation("Mon, 14 Sep 2026 09:00:00 -0700", "unknown", "second"),
            DateObservation("not a date", "original_date", "second"),
        )
        for date in views:
            with self.subTest(date=date):
                catalog = Catalog()
                catalog.admit(email(), "school-email-a")
                result = catalog.admit(email(original_date=date), "unused-owned-id")
                self.assertEqual(result.status, "pending")
                self.assertEqual(tuple(catalog.records), ("school-email-a",))

    def test_received_time_cannot_substitute_for_missing_original_date(self):
        received = DateObservation("Mon, 14 Sep 2026 16:00:00 +0000", "received", "second")
        self.assertEqual(Catalog().admit(email(original_date=None, received_date=received)).status,
                         "pending")
        self.assertIsNone(normalize(email(received_date=MONDAY)).received)

    def test_incomplete_lookup_and_unverified_mailbox_cannot_create_records(self):
        catalog = Catalog()
        self.assertEqual(catalog.admit(email(), "unused-id", lookup_complete=False).status,
                         "pending")
        self.assertEqual(catalog.admit(email(mailbox_verified=False), "unused-id").status,
                         "pending")
        for mailbox_id in ("", "   "):
            self.assertEqual(catalog.admit(email(mailbox_id=mailbox_id), "unused-id").status,
                             "pending")
        self.assertEqual(catalog.records, {})

    def test_existing_duplicate_records_are_not_silently_merged_or_selected(self):
        observed = email()
        catalog = Catalog({
            "school-email-a": LogicalEmail("school-email-a", [observed], [normalize(observed)]),
            "school-email-b": LogicalEmail("school-email-b", [observed], [normalize(observed)]),
        })
        result = catalog.admit(observed)
        self.assertEqual(result.status, "pending")
        self.assertEqual(result.candidate_ids, ("school-email-a", "school-email-b"))
        self.assertEqual(len(catalog.records), 2)

    def test_identical_permitted_metadata_exposes_the_accepted_information_limit(self):
        # Independent fictional story labels say these were different notices.
        # No permitted observation distinguishes them. This is a LIMIT example,
        # not a claim that successful policy execution establishes true identity.
        story_labels = ("distinct-fictional-notice-one", "distinct-fictional-notice-two")
        self.assertNotEqual(*story_labels)
        catalog = Catalog()
        catalog.admit(email(), "school-email-one")
        result = catalog.admit(email(access_hints=("different-access-hint",)))
        self.assertEqual(result.status, "reuse")
        self.assertEqual(result.record_id, "school-email-one")

    def test_optional_original_attachment_metadata_compares_only_equal_scopes(self):
        inventory = AttachmentInventory(("menu.pdf", "menu.pdf", "form.pdf"), True, "named", True)
        catalog = Catalog()
        catalog.admit(email(attachments=inventory), "school-email-a")
        reordered = replace(inventory, names=("form.pdf", "menu.pdf", "menu.pdf"))
        self.assertEqual(catalog.admit(email(attachments=reordered)).status, "reuse")
        self.assertEqual(catalog.admit(email(attachments=None)).status, "reuse")
        other_scope = replace(inventory, names=("inline.png",), scope="inline")
        self.assertEqual(catalog.admit(email(attachments=other_scope)).status, "reuse")
        fewer = replace(inventory, names=("menu.pdf", "form.pdf"))
        self.assertEqual(catalog.admit(email(attachments=fewer), "school-email-b").status, "new")

    def test_absent_incomplete_or_generated_inventory_is_not_empty(self):
        unknown = (
            None,
            AttachmentInventory(("download-1.pdf",), False, "named", True),
            AttachmentInventory(("menu.pdf",), True, "named", False),
            AttachmentInventory(("",), True, "named", True),
        )
        for inventory in unknown:
            self.assertIsNone(normalize(email(attachments=inventory)).attachment_names)
        empty = AttachmentInventory((), True, "named", True)
        self.assertEqual(normalize(email(attachments=empty)).attachment_names, ())


class AttachmentCoverageExamples(unittest.TestCase):
    def test_same_name_groups_are_parent_bound_and_members_do_not_inherit_reading(self):
        first = AttachmentReadPass("work-one", "school-email-a", "named", True,
                                   [ReadCandidate("work-one:red", "menu.pdf"),
                                    ReadCandidate("work-one:blue", "menu.pdf")])
        second = AttachmentReadPass("work-two", "school-email-b", "named", True,
                                    [ReadCandidate("work-two:green", "menu.pdf")])
        self.assertEqual(len(first.groups()[("school-email-a", "menu.pdf")]), 2)
        self.assertNotIn(("school-email-a", "menu.pdf"), second.groups())
        first.record_read("work-one:red")
        self.assertEqual(first.candidates[1].state, "unread")
        self.assertFalse(first.declared_inventory_read)
        first.record_read("work-one:blue")
        self.assertTrue(first.declared_inventory_read)
        self.assertFalse(second.declared_inventory_read)

    def test_a_fresh_inventory_pass_does_not_adopt_candidate_positions_or_names(self):
        previous = AttachmentReadPass("work-old", "school-email-a", "named", True,
                                      [ReadCandidate("work-old:one", "menu.pdf")])
        previous.record_read("work-old:one")
        new_pass = AttachmentReadPass("work-new", "school-email-a", "named", True,
                                      [ReadCandidate("work-new:two", "menu.pdf"),
                                       ReadCandidate("work-new:one", "menu.pdf")])
        self.assertFalse(new_pass.all_exposed_candidates_read)
        self.assertEqual([candidate.state for candidate in new_pass.candidates], ["unread", "unread"])

    def test_unknown_names_or_inventory_scope_leave_honest_coverage(self):
        work = AttachmentReadPass("work-unknown", "school-email-a", None, False,
                                  [ReadCandidate("work-unknown:image", None)])
        self.assertIn(("school-email-a", None), work.groups())
        work.record_read("work-unknown:image")
        self.assertTrue(work.all_exposed_candidates_read)
        self.assertFalse(work.declared_inventory_read)


class WindowExamples(unittest.TestCase):
    def scope(self, track="historical"):
        return WindowScope("household-mailbox-a", "fictional-school-scope",
                           "2026-09-14", "2026-09-15", "declared-search-date",
                           "UTC", "day", track)

    def test_short_page_with_continuation_does_not_complete_a_window(self):
        work = WindowProgress(self.scope())
        work.observe_page(("school-email-a",), continuation_available=True,
                          exhaustion_established=False)
        self.assertEqual(work.enumeration, "unfinished")
        self.assertEqual(work.resume_instruction(), "repeat-window")

    def test_absence_of_a_token_or_results_alone_does_not_prove_exhaustion(self):
        work = WindowProgress(self.scope())
        work.observe_page((), continuation_available=False, exhaustion_established=False)
        self.assertEqual(work.enumeration, "unfinished")

    def test_serialized_unfinished_window_replays_without_provider_token(self):
        catalog, work = Catalog(), WindowProgress(self.scope())
        first = catalog.admit(email(), "school-email-a")
        work.observe_page((first.record_id,), continuation_available=True,
                          exhaustion_established=False)
        restored = WindowProgress.from_snapshot(json.loads(json.dumps(work.snapshot())))
        self.assertEqual(restored.scope, work.scope)
        self.assertEqual(restored.resume_instruction(), "repeat-window")
        repeated = catalog.admit(email(access_hints=("replacement-hint",)))
        later = catalog.admit(email(original_date=REPLY), "school-email-b")
        restored.observe_page((repeated.record_id, later.record_id),
                              continuation_available=False, exhaustion_established=True)
        self.assertEqual(restored.observed_email_ids, ["school-email-a", "school-email-b"])
        self.assertEqual(restored.enumeration, "exhausted")
        self.assertEqual(len(catalog.records), 2)

    def test_daily_discovery_does_not_complete_historical_or_content_work(self):
        historical, daily = WindowProgress(self.scope()), WindowProgress(self.scope("daily"))
        unread = AttachmentReadPass("content-work", "school-email-a", "named", True,
                                    [ReadCandidate("content-work:document", "guide.pdf")])
        daily.observe_page(("school-email-a",), continuation_available=False,
                           exhaustion_established=True)
        self.assertEqual(daily.enumeration, "exhausted")
        self.assertEqual(historical.enumeration, "unfinished")
        self.assertFalse(unread.declared_inventory_read)

    def test_contradictory_exhaustion_claim_is_rejected(self):
        work = WindowProgress(self.scope())
        with self.assertRaises(ValueError):
            work.observe_page((), continuation_available=True, exhaustion_established=True)
        self.assertEqual(work.enumeration, "unfinished")


if __name__ == "__main__":
    unittest.main()
