# D6 — Useful briefs and honest delivery status

Prepared 2026-09-15. **D6 remains proposed, not approved.** This brief explains
[the current D6 proposal](../ARCHITECTURE-PROPOSAL.md#d6--brief-selection-delivery-audio-and-unknown-effects)
with wholly fictional examples. No email, audio, task change, simulation or test
has been executed.

There are two decisions: what belongs in a recent update, and how to handle an
external action whose outcome is uncertain. A missing tool response establishes
neither success nor failure.

## “New to School-OS” can be older than today's email

Imagine a configured daily brief for fictional Maple School. Its reporting
interval ends at 18:00 on September 15, 2026, in America/Los_Angeles. Three
message bodies have been processed; listing has another unfinished page,
and one newsletter attachment remains unread.

| Fictional source | What the source says | What happened in this illustration |
|---|---|---|
| September 10, “Chess club places” | Book by noon on September 18 | First processed and verified on September 15 |
| September 15, “Museum departure correction” | The September 25 bus leaves at 08:20, replacing 08:40 | Correction processed and verified on September 15 |
| September 15, “Swimming reminder” | Bring kit on Wednesday; see the attached newsletter | Body processed; attachment not yet read |

The proposal selects updates by when knowledge was **first verified or
substantively corrected on Drive**. It still shows the original school dates.
The chess deadline therefore appears, labeled as newly processed older mail.
A source-Date-only brief might miss it even though the parent has never seen
it in School-OS.

An unchanged reread is not a new announcement. A real correction deserves an
update. Claim relationships depend on pending D5; verification-time fields
depend on the minimum record design still to approve.

Historical import does not automatically email a large backlog. Delivery needs
an explicit request or configured job. A manual “recent update” uses an explicit
reporting interval. These selection and delivery rules are proposed D6 behavior.

## What the parent might receive

This is illustrative email copy, with readable fictional source references:

> **School update — September 15**
>
> **Newly processed:** Chess booking is due September 18 at noon. This comes
> from “Chess club places,” sent September 10 and processed today.
>
> **Correction:** The museum bus leaves at 08:20 on September 25, replacing
> 08:40. Source: today's “Museum departure correction.”
>
> **Upcoming:** Swimming kit is needed tomorrow. Consent for the museum visit
> is due September 18 at noon; your planned completion date is September 16.
> Sources: “Swimming reminder” and the previously saved trip notice.
>
> **Coverage:** Three message bodies were processed. Another listing
> page and the newsletter attachment remain unfinished. This update may omit
> other news or required actions. Task-app synchronization has not yet been
> verified; the tasks above use the saved School-OS state.

Available source links would accompany these names in a real output. Relevant
guidelines and qualifications belong alongside tasks.

The approved query-coverage rule prevents “These are all your deadlines” when
discovery, content processing or the bounded coverage lookup is incomplete.
An unread older message could contain tomorrow's deadline. The parent still
receives useful verified information with the limitation visible.

Task-sync failure would not erase canonical tasks or automatically prevent a
knowledge brief. If the relevant snapshot has been completely read and contains
no required actions, the proposed flow proceeds to composition without trying
to authorize a nonexistent task write. No-new-actions does not mean no news.

## Proposed email and optional audio flow

1. Read the selected job or manual request, reporting interval, destinations
   and bindings. Read relevant verified knowledge, tasks and coverage in bounded
   portions using the approved D1 layout.
2. Assemble the selected information and its qualifications. Identify unfinished
   retrieval or processing instead of silently treating the selection as complete.
3. Prepare the intended email and record its reporting occurrence, inputs,
   destination and attribution. The proposed occurrence uses the job/operation,
   interval and variant so a repeat run can look for the same intended output.

The prepared information can feed two output branches. Email sends the rendered
brief. Optional supported audio narrates the same selected information, including
qualifications and coverage limits. Each branch uses the proposed effect
procedure: save the intended action, dispatch it and verify the observed result.
Sent-folder evidence can verify a sent message; it does not prove the parent
received or read it. Record the verification basis and limits.

Durable effect records depend on the unresolved decision below. The approved
code-capability requirement selects no language, personal computer or coding CLI.

The audio proposal saves generated audio on Drive as a **derived output**, with
its canonical inputs and attribution, until the parent explicitly deletes it.
It does not put original school attachments on Drive. This provides later
listening and an attributable artifact, but uses storage and requires deletion
management. Unsupported audio is disclosed; the email can remain usable.
Whether to wait for audio or deliver email first needs a concrete ordering choice
before implementation; this brief does not silently choose one.

## Who created and sent this particular brief?

A job, its executing agent, its generating agent and its sender can differ.
For example, a managed scheduler starts “Daily school brief”; Agent Birch runs
the operation; Agent Cedar composes its text; the family's selected email
service sends it. If one agent performs both roles, both identify that agent.

The proposed saved output records include the job/operation, reporting interval,
executing and generating agents, selected configuration and adapters, sending
service/account, destination, artifact or delivery reference and verification
time. A later change of default sender must not rewrite this historical record.

“Who sent yesterday's update?” can be answered from saved attribution without
scheduler access. Claims about current live status need fresh evidence; D7's
register mechanisms remain pending.

## A missing response does not mean nothing happened

Suppose a send call returns a generic error. The email service might have sent
the message and lost the response, or never accepted it. The error alone does
not establish either outcome, a timeout, or a rate limit.

The proposed common procedure is to save and verify the intended action and an
owned effect reference, record dispatch outcome as unknown before dispatch,
then reconcile what the external service actually shows. A School-OS marker,
where supported, and a complete relevant read can help establish the result.
Provider IDs remain replaceable access aids.

| Uncertain action | Why blind repetition is unsafe | Parent-visible result while unresolved |
|---|---|---|
| Create the consent task | A second attempt could create a duplicate task | “Task-app update outcome unknown; the canonical task remains available.” |
| Send the daily brief | The first email may already be in the inbox | “Delivery is unconfirmed. I have not sent another copy.” |
| Generate audio | Another request could create another artifact or charge | “Audio generation outcome unknown; no second request made.” |

For a send, inspect the relevant sent-output evidence if the selected route
supports it. For tasks, read the target state and School-OS task identity. For
audio, inspect the generated job/artifact when possible. Output verification
does not authorize using school-email bodies for source identity.

An empty or incomplete search is not proof of failure, especially when results
can appear later. If the outcome cannot be established, retain “unknown” and
stop that effect. The proposed retry rule requires evidence it was not applied,
or an explicit parent decision after explaining the duplicate risk. This cannot
promise exactly-once behavior for every service.

## The unresolved dependency after D2 was skipped

The user excluded **interrupted canonical-write recovery** from the MVP. That
decision stands. D6 nevertheless proposes persisted intent/outcome records so
an agent can recognize an uncertain external action. D6 is not automatically
approved or excluded by D2's deferral.

Before implementing that procedure, decide the minimum external-effect record,
ordinary verified save path, and behavior if its own save is interrupted. The
present proposal cannot quietly assume D2's intent discovery and partial-write
repair. Nor can it quietly drop unknown-send handling from the assignment.

A **possible narrower design, still new and unapproved**, is a protocol limited
to external-effect intentions and observed outcomes, without general repair of
arbitrary canonical writes. Its precise boundary needs a separate proposal and
approval. Another choice is an explicit MVP limitation requiring parent-directed
handling when continuity cannot be established. That would be a conscious scope
decision, not a reason to retry unknown effects automatically.

## Choices still needing approval

Approve or revise verification-time recency, outstanding-task selection,
reporting-occurrence identity, audio retention and unknown-outcome/retry
mechanisms. Resolve the persistence dependency and email/audio ordering before
implementation. The duties to disclose gaps and preserve attribution are
already approved; their proposed record mechanisms remain undecided.

Alternatives are source-Date-only recency and configurable audio retention.
They trade simpler selection or lower storage for missed late-processed
information or less output history. Automatic retries trade convenience for
duplicates or extra audio costs; they do not resolve an unknown outcome.

Searchable service evidence, eventual visibility, audio retrieval, attribution
and unattended authorization remain unqualified. D3 adapter contracts, D5 input
meaning and D7 job bindings remain dependencies. These written examples establish
no successful delivery, implementation result or permission to test.
