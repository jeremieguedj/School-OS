# Remaining foundation — records and normal saving

Status: **undecided dependency; D2 interrupted-write recovery remains outside MVP.** This explanatory note does not reopen the deferred recovery design. It explains the smaller record and ordinary-write choices needed by the remaining decisions. No schema or write mechanism is approved here.

## Why this still appears in the guide

D1 approved many bounded JSON pages on Drive. D2 originally bundled two subjects: what records mean, and how to repair interrupted writes. You skipped D2 and excluded interrupted-write recovery from the MVP. The system still needs to know what goes inside its knowledge, task, coverage and operation-configuration records. D7 now defers
the centralized tools/jobs register; D8 defers package/upgrade machinery.

For example, a deadline must not accidentally become a parent's preferred working date. Defining those fields is necessary even if the MVP does not resume a half-written update.

## A fictional example from email to saved information

> From: Cedar School Office <office@example.org>
>
> Subject: Museum permission
>
> Please return Robin's permission slip by September 19 at 17:00. If Robin is not attending, reply to us instead.

The parent says: “I'll do it on September 17.” A conceptual representation would keep these meanings separate:

| Information | Illustrative saved meaning |
|---|---|
| Email/source reference | The original mailbox, sender, subject and Date, with replaceable access information. |
| Knowledge | The school's permission request, deadline, and alternative for non-attendance, linked to the email. |
| Canonical task | The action to respond to that request, linked to the supporting knowledge. |
| Parent state | Planned date September 17; completion not yet established. |
| Coverage | What source content was actually read and what resulting data was verified as saved. |

These are readable labels, not an exact approved JSON schema. Multiple records can occupy a bounded page; a record type does not mean one whole-app file.

## The earlier inventory, narrowed for the MVP

| Record area from the earlier proposal | Its purpose |
|---|---|
| Configuration | Retain children/classes, timezone, source scope and selected operation/destinations as needed. Do not revive School-OS per-run resource quotas or a package manager. |
| Email | Allowed original/normalized metadata, association state and coverage links. |
| Attachment/group | Parent email, original filename, candidate group and independent read coverage. |
| Knowledge | Substantive claims, qualifications, source support and relationships. |
| Task/parent state | Required action, school deadline, parent owner/planning/completion and synchronization state. |
| Discovery window | Search scope, time meaning and evidence that listing is unfinished or exhausted. |
| Processing coverage | What has been read, what is incomplete and what has been verified. |
| Work/progress | Normally saved discovery/coverage progress remains; agent batch queues and runtime resource orchestration are not School-OS features. D2 write repair is deferred. |
| Tool/connection/adapter register | Deferred with D7. Operation configuration and adapter requirements remain, without a central management register. |
| Job register | Deferred with D7. The user and agents manage their schedules. |
| Operation/output evidence | Retained minimum source/result attribution remains to shape. D6 assigns uncertain-action verification to the executing agent; no general persisted-effect engine or D7 job-history requirement. |
| Provider locator | Replaceable access handles for records identified by School-OS IDs. |

The proposed UUID format, separate locator-record representation and exact fields remain undecided. School-OS-owned identity and provider handles as access aids are already part of the approved direction.

## What normal saving needs to establish

On a successful, uninterrupted operation, the agent must persist the intended substantive knowledge, source links and coverage, then verify what saved before treating it as complete or discarding temporary raw material. That existing requirement does not dictate a particular new transaction or recovery system.

The remaining ordinary-write contract must specify which records and links constitute a successful operation, how readback establishes that, and how consumers distinguish supported verified information from unknown or incomplete information. It must also state the MVP's limitations if writing fails. Choosing a failure policy or partial-update visibility mechanism is architecture, not a routine coding choice.

We have not approved “retry everything,” “discard partial writes,” a manual repair engine, or automatic reconstruction. This note does not adopt any of them. The MVP cannot promise repair/resumption of interrupted canonical writes, and D6 agent verification must not quietly restore that guarantee. D8 is now deferred.

## Recommended review boundary — still unapproved

Present a small, separate proposal containing the minimum fields for the retained features and the successful-write/readback contract. Keep D2's durable write-intent repair machinery outside that proposal. This makes it possible to assess the data the MVP actually needs without treating recovery as a prerequisite for every design discussion.

Alternatives include approving the broader original record catalogue, or defining separate schemas as each operation is implemented. A broader catalogue resolves more upfront but is harder to review; isolated per-operation definitions risk inconsistent meanings unless they share a canonical contract. The recommendation is one small shared contract for the MVP, but its contents have not been selected here.

Before dependent production code, approve the minimum fields and relationships, ID/locator representation, normal verification/visibility rules, and explicit unsupported failure outcomes. No dependent code or tests are implemented by these examples.
