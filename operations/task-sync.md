# Synchronize parent tasks

Use this operation for an authorized task synchronization or a task edit the
parent asks School-OS to make. Read the selected task-tool mapping, the instance
configuration, [data contract](../contracts/data.md), [storage procedure](storage.md)
and the relevant canonical Tasks. Drive remains canonical. The task app is the
parent's interaction surface; a successful tool call alone is not synchronization.
This procedure assumes no concurrent updates to the same Drive data and creates
no locks, scheduler, retry service or interrupted-write repair protocol.

## Establish scope and identity

1. Resolve the selected task projection and authorized account/container from
   configuration. Preserve the parent's existing choice. No selected projection
   means canonical tasks remain usable on Drive; do not create an app binding.
2. Read the relevant active Tasks and explicitly requested history. Read the
   selected tool's supported parent fields, managed identity location, completion
   review presentation and complete-listing/readback requirements.
3. Locate an existing projection using its replaceable access aid, then verify
   the exact School-OS `task_id` stored in the supported managed tool field.
   If the aid fails, use a complete authorized lookup for that marker. Titles,
   child names, row positions and provider IDs alone cannot establish identity.
4. Zero results prove a missing projection only when the lookup scope is complete.
   Multiple copies of the same marker are ambiguous: preserve the canonical Task
   and ask which projection to retain; never merge or delete them automatically.
   An incomplete lookup leaves the binding unknown. Neither outcome authorizes
   a replacement create.
5. A previously projected task deleted from the app remains on Drive. Report its
   missing projection and obtain the parent's choice before recreating it or
   changing canonical disposition. Deletion is not completion or cancellation.

For a genuinely new canonical Task, an authorized configured synchronization may
create its first projection after establishing that none exists. Save the
canonical Task before creating the app task. Include its owned ID in the chosen
managed field, then read the new task back and verify that ID and intended values.
If create has an unknown outcome, reconcile it before any repeat.

## Preserve the two kinds of task information

School-owned information includes the action, qualifications, source context,
school timing, condition, recurrence and supporting Knowledge. Parent-owned
information includes owner, planned date, progress, completion and personal notes.
Read both, but never turn an app due-date edit into a changed school deadline.
Publish corrected school evidence without erasing the parent's plan or completion.
An ordinary reminder adds evidence; it does not reopen an already completed Task.

Match one independently completed obligation, its completion subject and relevant
source context before adding or updating a Task. A once-per-household request
creates one household Task with the children as beneficiaries. A per-child form
requires separate Tasks linked to the shared Knowledge. Ambiguous action matching
needs review, not a title-based merge. Parent-created Tasks use
`origin: parent_created`; do not invent school Knowledge or school timing.

Only import parent-created app tasks inside the parent-authorized synchronization
scope. A task without a School-OS marker is not automatically an existing Task
whose marker disappeared. Establish whether the parent is adding a new personal
Task before assigning an owned ID and binding it. Leave unrelated app tasks alone.

## Compare three values, field by field

For each supported parent field, compare **B**, its last verified shared value
from `task_sync`; **C**, the current canonical value; and **R**, the freshly read
remote value. Normalize only equivalent values under the selected mapping.
An absent or unread field is unknown, not a clear, false or empty value.

| Evidence | Action |
|---|---|
| C = B and R = B | Preserve the field. |
| C differs from B; R = B | Project C to the app. |
| C = B; R differs from B | Accept R as the parent edit on Drive. |
| C = R, both differ from B | Preserve the agreed value on both sides. |
| C and R differ from B and each other | Preserve the base and both observations; ask the parent which value to retain. |
| No verified base, missing field or incomplete read | Do not infer an edit direction. Establish the intended initial value or resolve the uncertainty first. |

A deliberate parent clearing is an edit only when the mapping establishes that
meaning. Do not translate an omitted connector cell into a deleted note. Treat a
notes collection as one field unless the selected mapping supports an already
approved finer comparison; do not silently merge contradictory prose.

The rule applies separately to owner, planned date, progress, completed state and
personal notes. Source-derived completion review follows
[completion review](completion-review.md): awaiting confirmation is not completed.
Explicit parent confirmation/rejection remains distinguishable from source
detection. If an app exposes only a completion checkbox, it cannot also pretend
to expose a rejected review decision; accept that decision through an explicit
parent instruction when needed.

For a conflict, report the Task, field, prior value, Drive value and app value in
ordinary language. Other unconflicted fields may synchronize. Use the approved
`task_sync` observations and `projection_state: conflict`; retain each conflicting
field's original comparison base until the parent resolves it. Do not mark the
entire projection verified merely because another field succeeded.

## Write and verify

1. Re-read the exact identified app target before changing it if the earlier
   read no longer supports the planned update. A new parent edit means recompute
   that field's comparison; it is not permission to overwrite it.
2. Save accepted parent edits and source corrections to the bounded canonical
   Task pages under the storage procedure. Preserve unrelated records and fields.
3. Apply only the authorized, unconflicted changes through the connector. Preserve
   unrelated app content and fields outside the selected mapping.
4. Read back the changed app task and its School-OS marker. Compare actual values,
   including explicit clears and review status/section, with the intended result.
5. For verified fields, update `last_verified_shared_values` and
   `last_observed_remote_values`; retain the actual observation time in
   `last_verified_at`. Save the evidence on the Task and read the page back. This
   final readback does not require another timestamp write.
6. Report synchronized fields, conflicts, missing/unsupported projections and
   remaining uncertainty. Use the contract's existing projection states. A
   connector error is not evidence that a write failed or succeeded.

If a write outcome is unknown, inspect the current authorized target and values
before repeating it. A stale or incomplete read cannot establish failure. If the
outcome cannot be established, preserve the uncertainty and stop dependent effects.
These ordinary checks do not promise repair after interrupted canonical writes.

## Recurring and conditional obligations

Keep a `recurring_series` Task with the source pattern, start/end conditions and
applicability. Each `recurring_occurrence` has its own Task ID, `series_ref`, timing
and parent state. Completing an occurrence never completes every future occurrence.

Use native recurrence only when the selected mapping and current connector can
preserve the source pattern and independently observe the needed occurrence
history. A task that merely rolls to its next date does not prove which school
occurrence was completed. Otherwise project explicit occurrences for the next
14 days under D5, using the series and already recorded occurrence timing to avoid
duplicates. Keep existing overdue/uncompleted occurrences and the complete series;
the projection horizon never discards later obligations or creates a new schedule.
The next authorized synchronization extends the projection from the saved series.

For conditional tasks, retain the condition and any unknown household fact. Do not
drop an obligation or claim it applies when its condition is unresolved. A parent
plan can coexist with an unresolved school condition.

## Fictional comparison

The last shared consent Task has owner Avery and planned date September 17.
Drive now has September 18; the app now assigns Blair. Synchronize Blair and
September 18 while retaining the school's September 20 deadline. If the app also
changed the planned date to September 19, ask which planned date to keep. A
school receipt then creates a review candidate; only the parent's completion
confirms the Task. These are written examples, not executed checks.
