# Daily school update

Run this recipe when the parent or their authorized agent job requests an ordinary
daily update. It composes ingestion, canonical tasks and the selected brief;
it does not create a scheduler or a separate run engine.

Read [startup](startup.md), [ingestion](ingestion.md), [task sync](task-sync.md)
when configured, and the selected [brief recipe](brief-recipes.md). Use the
installed [data contract](../contracts/data.md) and [identity rules](../contracts/identity.md)
for the records involved. Load relevant sections and bounded pages as needed.

## 1. Establish the request

Confirm the intended instance from its Drive entry point and internal identity.
Use the saved household/source scope, timezone and explicitly selected brief,
task and delivery preferences. Existing valid authorization and preferences do
not require another interview. A configured recipient alone does not authorize
sending; use the parent's request or an already authorized job's instruction.
Assume no simultaneous operation on the same instance.

Record the run-start instant and its time meaning in the operation's normal
source-window work. This is the finite input cutoff. Later arrivals belong to the
next run; a maximum record count or resource batch is not a completion boundary.
Do not adopt an unapproved central run/job register to hold this value.

## 2. Complete ingestion

Follow [ingestion](ingestion.md) for all relevant School-OS-not-ingested mail in
the configured scope through the cutoff. Include known earlier backlog and
unfinished discovery windows, regardless of Gmail read/unread flags. Discover
new mail from the last completed arrival boundary, including that boundary at
its actual precision, using the approved connector-time semantics and every
continuation page. An explicit initial import boundary limits the instance's
historical scope; do not claim older history has been ingested.

The executing agent chooses resource-sized batches and preserves ordinary
verified progress on Drive. Continue the same logical task until the agreed
input is complete. If capabilities or resources prevent completion, report the
blocker and leave truthful not-ingested/unfinished state. Do not present a
partial batch as a successfully completed daily run or send a normal daily brief
that conceals the gap. [Continuation](continuation.md) explains token loss and
missed windows without promising interrupted-write repair.

## 3. Reconcile tasks

Canonical task extraction and source-supported relationships are part of
successful ingestion. Preserve school deadlines separately from parent plans.
Clear evidence that fulfills an action becomes detected completion awaiting
parent confirmation; it never silently checks the task off.

When a task tool is selected and synchronization is authorized, use its shared
semantic adapter through this agent's connector. Perform [three-way sync](task-sync.md)
against the last verified shared values. Respect parent edits, supported recurrence
and confirmed/rejected completion review. Do not overwrite conflicts or treat a
missing app entry as parent completion. If there are no actions or changes, do
not manufacture an app write.

A failed external task-app synchronization does not erase verified canonical
information or reopen source ingestion. Report the app freshness/status limit in
the daily brief. A failure to save required canonical knowledge or tasks does
prevent claiming ingestion complete.

## 4. Check the daily gate

Before composing, inspect the saved evidence for the entire agreed scope:

- Discovery windows are complete under an actually supported listing route.
- Each required logical email and reply is fully ingested, with body and all
  required attachment content saved and checked.
- Knowledge, task state, source links and coverage were read back successfully.
- No known association, inventory or required-content gap is hidden behind a
  completed flag. The accepted late-indexing limitation remains disclosed when
  relevant; a live connector is not an unconditional completeness guarantee.

If the gate fails, report incomplete ingestion and its reason. A later explicitly
requested limited manual brief follows the separate freshness-and-choice rule;
it is not a relabeling that turns this daily operation into a success.

## 5. Compose, deliver and close

Use the chosen [brief recipe](brief-recipes.md). The supplied daily starter selects
newly verified/corrected information with original source dates and relevant open
or confirmation-pending tasks. Preserve exceptions, school timing, parent plans,
scope, source links and uncertainty. Another compatible parent-selected recipe may
change selection and presentation, not truth or the daily completeness gate.

If audio is properly configured and requested, prepare it and deliver it together
with the email. If audio fails, send the written brief with a clear audio-failure
notice when email sending is authorized. The executing agent checks uncertain
outcomes using its available authorized evidence and avoids blind duplicate sends.
Do not keep a canonical audio archive; discard accessible temporary audio only
after verified delivery through the chosen email/chat route.

Attribute the actual generating agent and sending service/account where observed.
Report the outcome, scope/cutoff and any task-app or optional-audio limit. A saved
brief draft is not a sent email; a sent email is not proof the parent read it.
Clean accessible temporary raw source copies after verified canonical persistence.
No scheduling, installer, recovery framework or unrelated instance operation is
implied by completion of this recipe.
