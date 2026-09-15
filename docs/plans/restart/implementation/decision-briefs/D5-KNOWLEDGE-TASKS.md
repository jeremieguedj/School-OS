# D5 — Remembering school information and managing tasks

Prepared 2026-09-15. **D5 remains proposed, not approved.** This brief explains
[the current D5 proposal](../ARCHITECTURE-PROPOSAL.md#d5--substantive-knowledge-queries-and-task-reconciliation)
through wholly fictional correspondence. No operations or tests were executed.

The decision is how School-OS preserves school information, identifies required
actions and respects parent edits across apps. It serves losslessness,
provenance and useful applications built on the same canonical knowledge.

## A school email contains more than a task title

Imagine Maya attends fictional Maple School. All dates below are in 2026;
deadlines use the school's stated local time, America/Los_Angeles.

**Email A — “Year 4 September notices,” September 14, 08:00 −07:00**

> Our museum visit is Friday, September 25. Return consent by noon on Friday,
> September 18, and pay $12 by Monday, September 21. Bring a nut-free packed
> lunch unless your child receives a school meal; we will provide those meals.
> Bring swimming kit every Wednesday from September 16 through October 21.
> The office is open from 08:00 to 16:00 on weekdays.

The proposal saves substantive statements, called **claims**, with their
conditions and sources. A brief summary could lose the lunch exception,
swimming requirement or office hours. A claim remains open to correction.

| Information in the email | Proposed treatment |
|---|---|
| Museum visit on September 25 | A dated fact, linked to this email |
| Return consent by September 18 at noon | A one-time task with its school deadline |
| Pay $12 by September 21 | A separate one-time task with amount and deadline |
| Bring lunch unless receiving a school meal | A conditional trip-day action; preserve the exception and nut-free requirement |
| Swimming kit each Wednesday through October 21 | A recurring required action, including the end date |
| Office opening hours | Searchable information; no task merely to “know the hours” |

If School-OS does not know whether Maya receives school meals, it retains that
uncertainty. It cannot silently drop the lunch action or state that it definitely
applies. Likewise, the nut-free qualification remains attached to the lunch
instruction rather than disappearing from a short task title.

The proposed flow is: read the available content, preserve its substantive
meaning and provenance, identify required actions, relate them to existing
tasks, save and verify the results, then synchronize a configured task app.
Source-email identity still follows the approved metadata recipe. Reading
content to understand a request does not turn content into identity evidence.

## Corrections change the answer without erasing the past

**Email B — “Correction: museum payment,” September 15**

> The payment deadline in yesterday's notice was incorrect. Please pay by
> Wednesday, September 23. All other instructions are unchanged.

School-OS would retain both statements and record why September 23 replaces
September 21 for this payment. Consent and lunch instructions remain unchanged.
An old-email replay must not reverse the correction.

Now suppose **Email C — “Museum payment reminder,” September 16** says:

> Please pay for the museum visit by Tuesday, September 22.

It does not explain whether this is a replacement deadline, an earlier requested
payment date or a mistake. Under the proposal, a later timestamp alone does not
settle that question. Both statements remain available with a conflict.

The parent would see something like:

> Museum payment: $12. The correction says September 23; the later reminder
> says September 22. The school deadline needs clarification. Your planned
> payment date remains September 17.

The parent can choose a payment plan or explicit override while the school
conflict remains recorded. Their choice cannot rewrite school evidence.
Nothing here authorizes contacting the school automatically.

## The school deadline and the parent's plan are different

For consent, School-OS would keep the school's September 18 noon deadline.
Alex can choose to complete it on September 16 and assign it to Blair. Changing
that planned date does not rewrite what the school requested.

If Blair records completion on September 16, the task retains that parent state
and its evidence. A reminder arriving on September 17 adds provenance; it does
not automatically reopen the task. An explicit new request or evidence that
consent must be resubmitted is different and needs an explained relationship.

The parent can also create a personal task, such as “Ask Maya which lunch she
wants.” Its parent origin is explicit; it is not attributed to the school.

For swimming, the proposal retains the whole September–October requirement and
each occurrence's completion. If the selected task app supports the required
recurrence, its adapter may use it. Otherwise, the proposed default prepares
explicit occurrences for the **next 14 days**, with continuation on Drive.
Starting September 15 exposes September 16 and 23; it does not discard later
Wednesdays. Completing September 16 does not complete the whole series.
The recurrence mechanism and 14-day default still require approval.

## Synchronization compares three versions

The proposal compares the last verified shared values with today's Drive task
and app task, field by field. The following examples start with an open task;
they are separate from the completed-task example above. This adds no concurrent
Drive-write infrastructure.

**Example without a conflict:** the last shared consent task had owner Alex and
planned date September 16. A parent changes the date through School-OS and the
owner through the task app.

| Field | Last shared | Now on Drive | Now in the task app | Proposed result |
|---|---|---|---|---|
| Owner | Alex | Alex | Blair | Blair |
| Planned date | September 16 | September 17 | September 16 | September 17 |

Each changed field has one clear new value. The combined result preserves both
edits. The school deadline is still September 18 at noon.

**Example with a conflict:** starting from planned date September 16, one parent
changes it to September 17 through School-OS and another changes it to
September 18 in the app. Both differ from the baseline and from each other.
The proposed result is a visible choice, not an arbitrary winner:

> Consent has two planned dates: September 17 on Drive and September 18 in the
> task app. Choose the date to keep. The school deadline remains noon on
> September 18.

Other unconflicted fields remain usable. The exact conflict representation is
part of the still-pending record design.

Deleting an app task does not prove the school request was cancelled or
completed. School-OS would show a missing app entry while retaining the canonical
task. It must not silently recreate or delete it without the agreed handling.
The proposed adapter carries a School-OS task ID in a managed field and verifies
it. If that identity is missing, title similarity alone cannot safely reconnect
the task. Exact adapter support remains unqualified.

## What is saved and what a question can honestly answer

Under approved D1, the proposed knowledge and tasks would live in bounded JSON
pages on Drive. The remaining record definitions are not approved merely by
choosing that storage format.

| Proposed saved information | Purpose |
|---|---|
| Statements, qualifications, applicability and source references | Answer later questions without depending on a short summary |
| Supporting, correcting and conflicting relationships | Explain why a current answer differs from an earlier notice |
| Tasks, recurrence and occurrence history | Preserve required actions and their meaning |
| Parent owner, plan, progress and completion evidence | Preserve household decisions separately from school facts |
| Last verified shared values and projection binding | Distinguish later app edits from later canonical edits |

Raw emails and attachments remain at their sources. Temporary processing copies
are discarded after normal verified persistence. This brief does not restore
the interrupted canonical-write recovery excluded from the MVP.

The **already approved query-coverage rule** applies independently of D5. On
September 17, suppose consent remains open and the parent asks “What is due
tomorrow?”, but an earlier newsletter remains unread:

> Consent is due tomorrow at noon, according to “Year 4 September notices.”
> An earlier newsletter is still unread, so this may not be the complete list.

School-OS checks discovery and content coverage; a subject cannot establish that
unread material is irrelevant. Missing processing stays within authorization,
capability and budget. Verified facts remain usable with completeness limits.
An unavailable original limits rechecking without erasing saved knowledge.

## Choices still needing approval

The recommendation remains source-linked claims and explicit relationships,
separate parent fields, recurring tasks with a 14-day fallback horizon, and
field-level three-way synchronization.

Summary records are smaller but more easily
lose qualifications and correction history. One-way task export is simpler but
cannot faithfully bring parent edits back. App-native recurrence alone avoids
creating individual occurrences, but depends on the selected app's capabilities.
Asking the parent about every edit avoids automatic merges but adds routine work.

Approval is needed for those D5 mechanisms, including missing app entries and
identity handling. The minimum record/ordinary-write design and remaining D3
adapter contracts are separate dependencies; D6 still owns unknown external
write outcomes. Semantic interpretation, recurrence mappings and answer quality
remain untested. Code capability does not establish them. Testing remains reserved.
