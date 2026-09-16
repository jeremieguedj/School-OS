# D4 — One complete ingestion outcome per email

The latest numbered-review answers approve the run-start input scope (Q3),
strict original-Date threshold (Q5) and binary email outcome (Q6). The agent
owns its resources and batches. School-OS supplies instructions and completion
rules, not a batch controller. This is authored design, not a tested connector.
The [active plan](../../PLAN.md) records authority; the
[current questions](../OPEN-QUESTIONS.md) separate remaining proposals.

## What the daily run must finish

Process all relevant School-OS-pending emails in the configured mailbox/school
and import scope through the start of this run, including earlier emails not
fully ingested. Later arrivals belong to the next run. A parent opening an email
in Gmail does not process it for School-OS; an unread Gmail email might already
be fully ingested. The mailbox icon is not the progress record.

For example, the run starts at 06:00. It handles a pending message from yesterday
and all in-scope arrivals through 06:00. A message arriving at 06:05 belongs to
the next run. The agent may use any practical internal batches, but a finished
batch cannot turn the full task into a completed partial run.

## The ingestion flow

1. Read authorized configuration and the saved discovery windows. Establish the
   run-start cutoff and known not-ingested emails.
2. Discover the declared scope using the selected tool route. Follow all
   continuation pages, even after a short page. Revisit unfinished windows if
   a token is lost. Source handles remain replaceable access aids.
3. Associate each individual email or reply using the metadata recipe. Require
   original Date with known timezone and second-or-finer precision, verified
   mailbox, subject, sender, complete relevant lookup and no comparable
   contradiction. Unknown optional fields are not mismatches. Seek a richer
   metadata read or preserve uncertainty; do not invent missing seconds/zone.
4. Read the body and all required attachment material. Same-parent repeated
   filenames remain candidate groups; never select the first by list position
   or use bytes, body text or hashes as source identity evidence.
5. Extract substantive knowledge and action requirements, preserve sources and
   qualifications, save on Drive and check persistence.
6. Mark the logical email **fully ingested** only once the entire required email
   work is complete. Otherwise it is **not ingested**. There is no supported
   partially-ingested email workflow or per-part resumption engine in MVP.
7. After complete discovery and all required emails are fully ingested, the
   ordinary daily brief may be composed. A blocker is reported as incomplete.

## A complete-email example

A fictional school email says “Return museum consent by Friday”; its attachment
contains the consent instructions and a lunch exception. The agent reads both,
preserves the complete instruction and exception, saves the knowledge and task
with their source, and verifies the save. Only then is that email fully ingested.
If the required attachment cannot be read, the outcome is not ingested; the MVP
does not claim the body-only work completes the email or present a partial-PDF
continuation workflow. The attachment requirement itself remains in scope.

A later reply correcting the deadline has its own original Date and ingestion
outcome. It does not inherit the earlier message's completed state. Corrected
knowledge retains the source and explicit correction relationship.

## Live discovery: a simpler proposal, not yet adopted

The user rejected full-history enumeration on every daily run as overkill.
Recommend normal live discovery from the last completed arrival-time boundary
through run start, plus unfinished windows and known not-ingested backlog.
Include the prior boundary at the connector's actual precision so a boundary
item can be safely encountered again; use metadata association for reuse.
Do not add a fixed seven-day overlap or automatic full-history rescan.

The selected route must explain which source time it searches, timezone and
boundary semantics; original sending Date remains the identity timestamp.
If it lacks the required search/continuation capability, report the limitation
or use a supported authorized route rather than silently substituting semantics.
This proposal accepts the MVP limit that older material becoming newly visible
before an already-completed boundary is not automatically rediscovered. Live
access alone does not eliminate that possibility. The parent can explicitly
request a historical rescan. This narrower tradeoff needs a Q4 decision.

## A completed email seen again: the remaining narrow choice

The binary outcome is approved. Recommend that a unique, supported metadata
match to a fully ingested logical email reuses that completed result and skips
content reading, unless explicit new or contradictory inventory/coverage
information challenges completion. A different provider handle or unknown
optional metadata alone would not reopen it. A reply is a different email.

That exact reuse rule remains for approval under Q6. It favors simple logical
email reuse, while accepting the metadata recipe's residual indistinguishable-
email risk. It cannot detect content changes hidden behind unchanged allowed
metadata. Always rereading would cost more and is not proposed as a new engine.
Neither option may mark newly identified unread material complete. Retain actual
source/attachment evidence needed to justify the binary result without inventing
a per-appearance record framework.

## Boundaries and later qualification

Discovery and email completion remain different: all found emails being fully
ingested does not prove every email was found. Counts of provider entries are
not logical-email ground truth. Unsupported content, incomplete listings and
unknown association must stay visible. Source originals remain in the mailbox;
discard temporary processing copies after verified persistence.

The frozen studies remain unchanged and do not qualify the new design. No test,
simulation, model replay, connector probe, ingestion or scheduled job ran. Q1/Q2
persisted shapes, Q4 discovery and Q6 completed-email reuse await approval before
dependent implementation. D2 write repair and its generic framework stay deferred.
