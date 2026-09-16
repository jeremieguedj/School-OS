# Completion review

Use this procedure when newly processed source evidence clearly shows that a
linked School-OS task's requested outcome has been satisfied. The evidence does
not complete the task. It classifies the task as **Completion detected —
awaiting parent confirmation** so the parent can review it and check it off.

This procedure uses approved D5 task identity, relationships and field-level
three-way synchronization. It adds no task identifier, JSON schema, polling
service, state machine or provider-specific rule. It also does not authorize a
source read or tool write by itself; perform only the operation the parent has
requested through already authorized tools and configured synchronization.

Use [the data contract](../contracts/data.md), [storage](storage.md) and
[task synchronization](task-sync.md) for actual records, saves and parent edits.

## Meaning of the review state

Completion evidence is strong enough only when it establishes the requested
outcome for the exact linked task, child and school context. For example, an
explicit source acknowledgment that the school received the named form may
satisfy a task to submit that form. A related reminder, a draft, a sent-message
listing, a similar title or evidence of only one required part does not by itself establish
that the specific obligation has been satisfied.

Do not turn this into a numeric confidence threshold. Source meaning, the task's
finite or conditional completion condition, and any unresolved contradiction
remain visible. Ambiguous or partial evidence may be saved as a source fact and
linked for later review, but it must not be presented as fully satisfying the
task.

The parent-confirmation state is not canonical completion. It tells the parent:

- School-OS found clear evidence that appears to satisfy this task;
- the evidence is linked and available for review; and
- the parent must still choose whether to mark the task complete.

## Agent procedure

### 1. Read the source evidence within ingestion

Read the individual email's complete required body and attachment material and
establish the evidence before deciding that it fulfills a Task. Preserve the
original source meaning, time precision, child and school context, and any
uncertainty. Apply this review while composing and saving the email's Knowledge
and Tasks; it does not require a pre-existing `fully_ingested` flag. The ingestion
operation sets that flag only after all required Knowledge, Tasks, source links
and coverage are saved and read back. No completed partial email is claimed.

Do not start an automatic monitor, poll for status, or search sent mail unless
that source scope is already requested and authorized. If required material is
unread, describe the gap and keep the email not ingested. Do not use absence from
a partial read as proof that the task is unfinished or satisfied.

### 2. Link the evidence to the exact task

Interpret what the source actually says, then follow the existing School-OS
relationship to the exact child request and canonical task. Use the task's
School-OS identity and configured projection mapping. Do not infer identity from
a matching or similar title, and do not treat a provider task ID as canonical
School-OS identity.

Compare the evidence with the task's own completion condition. If it is
ambiguous, partial, refers to another child or request, or conflicts with an
edited task field, keep the task out of the completion-review state and surface
the issue for review.

### 3. Preserve evidence and pending confirmation in Drive

Save the source evidence as source-linked Knowledge. Add its typed evidence
references and actual detection time to an approved
`parent_state.completion_reviews` entry with `state: awaiting_confirmation`.
This records **Completion detected — awaiting parent confirmation**, while
leaving `parent_state.completed` false.
Preserve the evidence needed for the parent to understand why it was flagged,
then perform the normal save readback required by the operation.

Read prior review decisions before adding the entry. The same evidence already
awaiting, confirmed or rejected does not create another suggestion. Materially
new evidence may justify a new awaiting entry with its own references, without
erasing a rejected decision. Keep `completion_reviews` as one complete array on
the owning Task record. If the complete Task cannot fit on an otherwise empty
page under the data contract's current maximum, do not truncate reviews, split
the field, or claim a partial save. Report the observed encoded bytes and
required minimum page size, and leave the affected completion-review operation
incomplete.

If the canonical task is already parent-confirmed complete, retain and link the
later evidence as appropriate, but do not reopen or downgrade the task merely
because a later receipt or acknowledgment arrived.

### 4. Present the review state in the task tool

Perform this step only when a task projection is selected and task-app
synchronization is authorized. An ingestion-only operation saves the canonical
review above and reports it; it does not update an app or wait for parent
confirmation before the email can finish ingestion. With no selected task tool,
the canonical review is still available through School-OS queries and briefs.

Read the selected shared tool-semantic adapter. Through the agent's authorized
connector, project the pending-confirmation meaning in an appropriate supported form:

1. a dedicated native status that means awaiting parent confirmation; or
2. a dedicated review section that lets the parent review and check off all
   flagged tasks while preserving task identity and parent-editable fields.

The shared adapter maps the semantic state; the connector owns authentication,
API or SDK access, request construction and transport. Do not fork the adapter
for the executing agent.

Read the task back and verify its identity, review placement or status, and the
parent-visible evidence reference allowed by the mapping. A generic success
response does not establish the projection. If the outcome is unknown, reconcile
it before repeating a write.

If the tool has neither a suitable status nor section, or the authorized
connector cannot project or verify it, leave the Drive task awaiting parent
confirmation and report the specific gap. Do not substitute an unapproved label,
tag, custom field, completion value or new app permission.

### 5. Accept the parent's decision through D5 synchronization

The parent reviews the flagged task and its evidence in the configured task
tool. When the parent checks the task complete, the next authorized D5 three-way
synchronization reads that parent edit, compares Drive, the prior synchronized
base and the current app value, and writes unconflicted parent-confirmed
completion to canonical Drive data. Verify both sides according to the selected
adapter and normal write procedure.

Mark the relevant awaiting review `confirmed` with the observed decision time
when that parent confirmation is established. If the parent rejects the
suggestion, retain its evidence and change that review to `rejected`, preserving
the decision time and any parent explanation. Keep the Task open unless a
separate supported parent decision changes it. If the tool cannot express
rejection unambiguously, accept it through an explicit parent instruction; never
infer it merely from moving a row, an absent task or a hidden section.

If Drive and the app contain contradictory edits to the same field, do not pick
one silently. Preserve both observations and ask for review under D5 conflict
handling. A missing projection or provider deletion is not proof of completion.

## Edge cases to preserve

- **Partial evidence:** save the observed fact and relationship, but do not flag
  the task as fully satisfied.
- **Ambiguous identity:** do not title-match or guess which child request the
  evidence satisfies.
- **Contradictory task edit:** keep the conflict visible for parent review; do
  not overwrite either side as a routine completion update.
- **Later evidence for a completed task:** add the evidence without downgrading
  the parent's confirmed completion.
- **Unavailable tool presentation:** keep the Drive review state, report the
  gap, and wait for a supported route rather than inventing a fallback.
- **Unknown write outcome:** reconcile through an authorized read; do not blindly
  repeat the external effect.

## Deferred automation

Direct automatic completion may be considered only after the household has
observed the accuracy of this review flow and explicitly approves a later
architecture decision. This procedure introduces no accuracy threshold,
monitoring engine, automatic status polling, sent-mail discovery or unattended
completion rule.
