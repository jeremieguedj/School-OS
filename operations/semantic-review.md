# Compare source meaning with saved meaning

Use this procedure for every email body and required attachment candidate before
the parent Email may become `fully_ingested`. It is a temporary agent reasoning
step over material already being processed and the ordinary saved-state readback.
It creates no new Drive record, schema, cache, queue, transaction or second-model
review service.

Read [extraction](extraction.md), [knowledge and tasks](knowledge.md), the
[data contract](../contracts/data.md), and the applicable source and storage
adapters. Keep raw source material temporary and private under the normal
ingestion boundary.

## 1. Describe the source before checking generated records

While the source is visible, make a temporary checklist that preserves every
substantive unit independently:

- the statement, request, guideline, observation, correction or negation;
- all conditions, exceptions, qualifications and uncertainty;
- the true household, child, school or class applicability;
- each date/time with its meaning, precision and stated timezone;
- `none`, `finite`, `conditional` or `recurring` action disposition;
- the actual condition, recurrence rule and lifecycle when action exists;
- each independently completable unit and its beneficiaries; and
- the exact Email body or Attachment Group location that supports it.

Do not derive this checklist from generated Knowledge, Tasks, titles, counts or a
previous run. Importance alone does not create an obligation. One household
submission is one completion unit; separate submissions per child are separate
units. Original Email Date, response deadline, event timing, effective timing,
recurrence timing and parent planning are distinct roles.

## 2. Save through the ordinary procedures

Author Knowledge and applicable Tasks under [knowledge](knowledge.md), then use
the [normal save sequence](storage.md#normal-save-sequence). This review does not
replace page identity, bounds, reference, index or readback checks. It adds the
source-meaning comparison that structural persistence alone cannot establish.

## 3. Compare the actual saved readback

Read the complete saved Knowledge and applicable Tasks back from Drive. Compare
them against the temporary checklist, item by item:

1. Every substantive statement remains present without a changed meaning.
2. Every condition, exception, qualification and uncertainty remains attached
   to the claim or action it qualifies.
3. Scope, listed entities, beneficiaries and completion subjects match the
   source. Shared information is not duplicated per child.
4. Each source date is present under the correct role with no invented year,
   time, timezone or precision.
5. `action_disposition` agrees with the source. Information or optional guidance
   creates no source-derived Task.
6. Finite, conditional and recurring lifecycle remains distinct. A recurring
   series is not flattened into one finite Task.
7. The Task inventory has exactly the independently completable units supported
   by the source: no missing, merged, duplicate or unsupported Task.
8. Every material item has a readable source reference and location. A directly
   embedded substantive remote image uses its parent Email body and descriptive
   location under the approved bounded-image rule.

Counts, matching JSON bytes, valid references and fluent summaries cannot replace
these comparisons. If the source supports no action, explicitly establish why an
empty Task result is correct.

## 4. Decide coverage and clean up

Any missing, changed, overbroad, unsupported or unresolved meaning fails the
review. Keep the whole Email `not_ingested`, retain accurate verified canonical
information, and correct the still-open operation only when authorized. Do not
certify a partial meaning because its files are structurally valid.

When the comparison passes for the body and every required attachment candidate,
continue the other whole-email coverage conditions in [ingestion](ingestion.md).
Only their combined success permits `fully_ingested`. Discard the temporary
checklist with other processing material after verified persistence. It never
becomes canonical state or a recovery record.
