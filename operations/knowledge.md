# Retain knowledge without losing meaning

Use this procedure after source discovery and content reading establish
substantive information. Follow [the retained data contract](../contracts/data.md)
and [bounded storage procedure](storage.md). Source discovery completeness,
email ingestion, canonical Knowledge, and Tasks are separate outcomes.

## Author a Knowledge record

1. Preserve each substantive claim, instruction, exception, condition, date,
   uncertainty, and action requirement. Keep wording lossless enough that
   another agent does not need the raw message to recover meaning. Author the
   statement as one complete string, and keep qualifications and relationships
   as complete arrays on the same owning Knowledge record. Do not truncate or
   invent a field-splitting format. If the complete record exceeds the data
   contract's current page maximum even on an otherwise empty page, report its
   observed encoded bytes and required minimum page size, and do not mark the
   source fully ingested.
2. Choose `knowledge_kind` from the source meaning:
   - `fact` for a supported proposition;
   - `guideline` for a rule or condition that may remain applicable;
   - `update` for an announced state or plan change;
   - `observation` for a dated report, assessment, or description.
3. Set `action_disposition` independently: `none`, `finite`, `conditional`, or
   `recurring`. Do not create a Task for non-actionable information.
4. Assign one true-scope anchor and applicability:
   - `anchor_only` for that household, person, school, class, or child;
   - `listed_entities` only with the complete named Entity list;
   - `members_at_effective_time` only with the applicable Membership role.
   Store school- or household-wide meaning once. Do not copy it under children.
5. Add entity links with explicit roles such as `subject`, `reporter`, or
   `school_context`. A Robin trend needs Robin as anchor, listed entity, or
   subject; school context or a sibling subject is not direct Robin evidence.
6. Resolve topics to stable IDs. Co-tag supported specific, broad, and purpose
   concepts. For example, fractions feedback can carry `fractions`, `math`, and
   `teacher-feedback`. Preserve unresolved classification explicitly instead of
   inventing an alias.
7. Cite all source parts and readable extraction locations. Mark exactly one
   primary source for routing. Source references do not replace Email ingestion
   coverage.
8. Preserve every date with its own meaning and precision. An observation date,
   source original Date, effective date, deadline, and membership interval are
   not interchangeable.
9. Record qualifications and uncertainty explicitly. Empty qualifications mean
   the agent assessed and found none.
10. Add only evidenced relationships from the newer record to an older record.
    Each link needs evidence and a justification.

## Distinguish correction from development

- Use `corrects` only when evidence says the earlier claim was wrong.
- Use `replaces` when a later rule or plan supersedes an earlier one from a
  stated point forward.
- Use `conflicts_with` for unresolved disagreement.
- Use `supports` for additional evidence.
- Leave both observations unlinked when they describe valid states at different
  times. Improvement from autumn difficulty to spring independence is a trend,
  not automatically a correction.

Keep the outgoing relationship on the newer Knowledge record. Emit the derived
incoming lookup so a query beginning with the older record can find the later
relationship.

## Derive a Task when action exists

1. Determine the independent completion unit from the source. One household
   submission for siblings produces one household Task; one submission per child
   produces separate Tasks.
2. Link every source-derived Task to its supporting Knowledge. Keep Knowledge's
   source evidence separate from parent planning and completion state.
3. Set scope, completion subject, and complete beneficiary inventory. Use an
   explicit unknown inventory if the source does not establish all beneficiaries.
4. Preserve source timing in `school_timing` when applicable. Do not fabricate
   school fields for a parent-created personal Task.
5. For recurrence, retain the `recurring_series` rule and create independent
   `recurring_occurrence` Tasks for the selected 14-day projection.
6. Preserve all existing `parent_state` values when source knowledge changes.
   Source evidence cannot overwrite owner, planned date, progress, completion,
   notes, or review decisions.
7. Clear evidence of satisfaction creates an `awaiting_confirmation` completion
   review while `completed` remains false. Ambiguous or partial evidence does
   not. Parent confirmation or rejection changes the review state. The same
   rejected evidence cannot reopen it; later receipts cannot downgrade a
   completed Task.
8. Synchronize supported shared task fields through the selected adapter using
   the School-OS Task ID marker and three-way comparison of canonical state,
   last verified shared state, and newly observed remote state. Preserve a
   conflict or capability gap; never title-match or treat an uncertain effect as
   success.

## Save and index

1. Route Knowledge by its primary source original-Date month, even when its
   semantic observation/effective date is earlier.
2. Write/read back canonical Knowledge and Task pages using the normal save
   sequence.
3. Emit Entity Index entries for scope anchors, listed entities, entity links,
   and Task scope/completion subject/beneficiaries.
4. Emit Topic Index entries for Knowledge only, using semantic time buckets.
   Use every overlapping month, plus `open_interval` or `unknown_interval` when
   required.
5. Emit incoming relationship entries for each outgoing relationship.
6. Advance index coverage only after every required derived entry is written
   and read back.
7. Save `fully_ingested` only after the Email body and all required attachments
   have been processed and all resulting Knowledge has been saved and verified.
   Otherwise the Email remains `not_ingested`; do not persist a partial resume
   state.

## Before discarding accessible source material

Confirm that substantive claims, qualifications, scope, dates, topics, source
locations, action disposition, relationships, and Tasks were all retained and
read back. Confirm attachment requirement and email-level ingestion state.
Temporary source cleanup follows the ingestion procedure only after
verified persistence.
