# Restart implementation decisions for approval

Updated 2026-09-15, revision 11: records the numbered-review answers and the
[concrete Q1/Q2 data/index proposal](DATA-ARCHITECTURE-PROPOSAL.md). Q3 run-start
scope, Q5 strict Date precision, Q6 binary email outcome and Q7–Q9 manual/audio
behavior are approved as recorded in the [active plan](../PLAN.md). The proposal's
new fields/index rules and the narrow Q4/Q6 discovery/reuse choices remain
unapproved. The generic records/write framework stays outside MVP.
**D1, query coverage, D3's minimal Python/shared-adapter direction and
D5 are approved; D4/D6 use the recorded agent-led direction. D2 repair, the
separate record/save framework, D7 and D8 are deferred.** The helper subset may
be authored within this scope; it is not a complete production implementation.
New architecture still requires explicit approval, without reopening a deferred
framework as a blanket prerequisite for retained operations.
Testing remains reserved to the user after publication of the implementation.

The [coverage map](COVERAGE.md) maps the complete product to deliverables. The
recommendations below now distinguish retained MVP work from the explicit D2,
D7 and D8 deferrals. They do not propose reducing it
to an identity model, a local CLI, or a single managed-agent demonstration.

The [detailed decision briefs](decision-briefs/README.md) explain the approved D3 direction
and D4–D8 through fictional emails, flows, parent-visible results, alternatives
and implications. Their additional recommendations are explicitly unapproved.
Written examples are not executed simulations or qualification evidence.

## Decision summary

| Decision | Recommendation | Main alternative | Approval |
|---|---|---|---|
| D1 Storage | Small JSON record pages and paged directories in Drive, with a readable bootstrap | Native Sheets tables, with separately bounded long text | Approved, 2026-09-14 |
| D2 Records and persistence | Earlier typed-record/write framework retained for later review | Agent/tool operations preserve already approved data meanings and verify actual saves | Repair and the separate records/ordinary-save framework outside MVP; query rule retained |
| D3 Execution and adapters | Minimal Python helpers; setup interview; one shared tool-semantic adapter per tool, reusable through each agent's connector | Agent-specific adapter forks or a provider SDK runtime are not selected | Approved explicitly, 2026-09-15; creation/reuse of missing conformant mappings included |
| D4 Ingestion | One logical run completes relevant unprocessed mail; the executing agent owns batching, resources and runtime continuity; School-OS supplies guidance | Former School-OS-managed per-run caps were rejected | Execution direction approved, 2026-09-15; run-start scope, strict Date threshold and binary email outcome approved; discovery/reuse details pending |
| D5 Knowledge and tasks | Source-supported claims, separate parent state, three-way sync; detected completion awaits parent confirmation in a supported status or section | Direct automatic closure is a future option, not selected | Approved explicitly, 2026-09-15, including the parent-confirmation amendment |
| D6 Briefs and effects | Executing agent verifies uncertain effects using available tools; validate complete ingestion before daily composition | Former generic persisted-effect engine is not selected | Verification/timing, starter selection/task-sync disclosure and recipe extensibility approved, 2026-09-15; manual freshness prompt, no audio archive and combined delivery/failure fallback approved |
| D7 Tools and schedules | User and agents manage their own jobs and select adapters from recipes; assume nonconcurrent use | Central register and scheduler control retained for possible later work | Outside MVP by explicit user direction, 2026-09-15 |
| D8 Packages and upgrades | Retain approved D1 separation so installation/upgrades can be added later | Original ZIP, activation, compatibility and migration machinery retained as future proposal | Outside MVP by explicit user direction, 2026-09-15 |

Metadata-only identity, source custody, unrestricted agent/job counts and the
exclusion of concurrent same-data writes remain approved. D7 defers centralized
management and register-backed visibility, not the ability to use several agents.
D8 defers lifecycle machinery, not D1’s approved separation. These are explicit
MVP exceptions to the broader product principles, which remain unchanged.

## MVP exception — interrupted writes

On 2026-09-14 the user decided to skip D2 for now and exclude interrupted-write
recovery from the MVP. The D2 write-intent discovery, reconciliation, partial-write
repair and automatic resumption procedure is deferred. Keep it as a future
proposal, not an MVP implementation or acceptance requirement.

This explicit MVP scope reduction supersedes the broader recovery requirement
for this feature. It does not rewrite the long-term product principles. The
approved query-coverage rule remains active, as do source custody, honest
incomplete coverage, normal verified persistence, bounded discovery/window
continuation and fresh-agent access to saved knowledge. The MVP cannot claim
that an interrupted set of canonical writes will be repaired or completed.

On 2026-09-15 the user also excluded the separately presented “open dependency
records and ordinary save” from the MVP. Do not implement its schema catalogue,
generic writer/verification/visibility framework or make approval of that package
a gate for retained work. Do not silently replace it with another framework.
Canonical Drive data, D1 storage rules, D5 meanings, source metadata/coverage,
owned identities and normal verified saving remain required. The agent and its
authorized tools carry out those operations from the agreed instructions. No
UUID format, locator schema or new canonical representation is approved by this
deferral. Surface a specific new architectural need if it actually arises; do
not demand the excluded framework as a whole in advance.

The 2026-09-15 directions supersede the former D4/D6/D7/D8 implementation
recommendations as stated in their sections. Do not restore the rejected batch
controller, deferred D2 repair, D7 register or D8 upgrader through another name.
The executing agent's own continuity and recovery are relied upon for its work;
canonical identity, verified knowledge and completion evidence still belong on
Drive. No blanket guarantee of complete environment-loss recovery is selected.

## D1 — Physical Drive layout and bounded access

Recommend a Drive folder for the instance containing a short human-readable
`START-HERE` document and three child areas: `system`, `instance`, `extensions`.
The bootstrap identifies the School-OS instance ID, installed release, logical
directory names and the procedure for locating them. A current Drive URL or ID
is an access aid; the logical instance/role identifiers inside retrieved records
are the evidence that an agent reached the intended records. A duplicate or
conflicting role is unresolved, never selected by the first provider result.

`system` holds versioned official package files. `extensions` holds separately
named user additions. `instance` holds configuration, indexes, data and work.
Canonical structured data is UTF-8 JSON, in bounded pages containing records of
one family. Each page declares its instance, family, School-OS page ID and schema
version. Ordinary values and stable identifiers are readable without Python.
There is no native Sheet required by the canonical storage contract.

Use paged directories with at most 100 entries per page. Source lookup is routed
by logical mailbox and the normalized UTC month of the original Date instant
(preserving the source Date, zone and precision); work/output history by recording
month. Tasks have a separately paged active-task directory. Knowledge has a
source/month directory and a rebuildable topic/entity directory. Directory
entries locate pages by School-OS IDs and optional current Drive handles. All
directories have explicit continuations; discovering another page does not
require a remembered provider token. Traversal stops at the operation budget
and saves remaining directory/work positions on Drive.
Unknown-date observations stay in a separately discoverable pending-work area.
Equivalent timezone presentations must reach the same source lookup partition.

Default page limit: 64 KiB encoded JSON. Long substantive text is split at
paragraph boundaries into numbered knowledge segments linked to the same claim;
no truncation or raw-source storage. A single oversized paragraph is segmented
without deleting text. The limits bound each transfer, not the total history.
Startup reads only the bootstrap, relevant configuration, selected operation,
selected bindings and a bounded unfinished-work page. Queries can traverse more
pages over multiple sessions and must report an unfinished search honestly.

Writes can add or update individual bounded pages. No whole-history download,
full-instance rewrite, local mirror, or permanent file-per-email requirement.
Adapter-provided query/search may accelerate lookups; it cannot supply missing
coverage evidence. A fresh agent can traverse the durable directory instead.

Grounding: P1, P3–P9; catalog, query, replacement and upgrade use cases.
Alternative: native Sheets rows/ranges, with a defined overflow representation
for long knowledge. Sheets can offer convenient native bounded reads; JSON
keeps nested evidence and explicit unknown values together. JSON access may be
less convenient in some managed connectors, and paged directories cost extra
reads/writes. Neither route is qualified here. Choosing JSON requires qualifying
file-content read/write and bounded folder listing in the actual target apps.
An incapable route remains unsupported; another conformant storage adapter may
be proposed later, without silently changing canonical formats.

## D2 — Canonical record meanings and write recovery

**Historical proposal, outside MVP.** Both interrupted canonical-write recovery
and the separately proposed records/ordinary-save framework are deferred. The
record inventory and ID/locator choices below are retained for possible later
review, not active implementation instructions or MVP approval prerequisites.
Only the separately approved query-coverage rule at the end of this section
remains an accepted D2 decision. See the [MVP exception](#mvp-exception--interrupted-writes).

Recommend independently assigned School-OS IDs for instances, source accounts,
emails, attachment groups/records, claims, tasks, jobs, runs, work and outputs.
IDs are opaque UUID strings generated once, never derived from provider IDs or
content. A capable runtime may generate them with its own tool; the optional
helper uses the standard library. Metadata normalization never renames records.

Use these typed record families. Fields marked optional may be unknown; omitted
information must not silently become an empty inventory or completed work.

| Family | Canonical content |
|---|---|
| Configuration | Instance/release/schema IDs; household entities and timezone; logical source accounts and source scope; budgets; operation defaults; user-authorized output destinations; extension declarations |
| Email | School-OS ID; mailbox ID; original observations and normalized allowed metadata; individually attributed sending/received dates with meaning, zone and precision; association state; source accessibility; links to coverage/work |
| Attachment | School-OS ID; parent email; original filename or unknown; same-parent candidate group; association uncertainty; original-inventory scope; separate processing coverage |
| Knowledge claim | School-OS ID; substantive statement and qualifications; entity/topic scope; evidence date/effective interval when known; source email/attachment/group reference and readable location; action disposition; evidence-supported correction/support/conflict relationships; verification state |
| Task | School-OS ID; source/parent origin; supporting claim IDs; action, context, school deadline and resolution; parent owner, planned date, progress and completion evidence; relationship history; selected projection bindings and last verified shared values |
| Discovery window | School-OS ID; mailbox and scope revision; boundary values/meaning/zone/precision; historical/daily track; unfinished/exhausted/unsupported state; exhaustion evidence and verification time |
| Processing coverage | School-OS ID; email/group/work reference; what was inventoried and read; unread/partial/unsupported/unavailable/verified disposition; qualifications and next action; verification time |
| Work/write intent | School-OS ID; operation and targets; intended bounded canonical changes; phase; affected record IDs; verified progress and remaining work; privacy-safe failure category |
| Tool/connection/adapter | School-OS ID; purpose and management location; capability declarations and observed limits; authorization location without credentials; last verification; current optional provider access references |
| Job | School-OS ID; purpose, executing runtime/agent, scheduler and management reference; trigger/timezone, source/input scope, selected adapters and output destinations; desired settings; separately observed state/time |
| Run/output/effect | School-OS ID; operation/job; executing and generating agent; selected bindings/configuration revision; canonical input references; effect intent and observed outcome; sending service/account; delivery or artifact reference; freshness/limitations |

Keep optional provider access aids in separate adapter-owned locator records,
referenced by School-OS IDs. They may be replaced or removed without invalidating
canonical meaning. Content locations such as page/section are provenance for
extraction, never email/attachment identity evidence. Attachment read candidates
get work-local School-OS references; their ordinal or tool handle is not promoted
to permanent attachment identity.

Recommend a small write-intent procedure, not an atomic whole-instance snapshot:

1. Save the intended bounded record changes and owned IDs in Drive work; verify
   readback of the intent before applying dependent writes.
   Work has a bootstrap-known folder and bounded unfinished-intent listing route.
   Intent/page creation is discoverable there even if its response or directory
   update was lost; recovery cannot require a UUID remembered only by the lost
   session. Unindexed pages remain discoverable in their known family folders.
2. Apply and read back each target by its School-OS ID and intended values.
   Incomplete or conflicting readback remains pending.
   A changed record carries its pending work ID and pending verification state
   in the same write as the changed values. Readers also check the referenced
   work's completion before accepting it, preventing an old verified marker
   from qualifying a partially changed record or relationship set.
3. Make source/claim relationships and lookup entries visible before marking the
   corresponding processing coverage verified. Readers use verified records.
4. Mark the work complete only after every required target and relationship is
   verified. Discard accessible temporary raw material then. On interruption,
   leave durable unfinished work and refetch raw material when needed.
5. A fresh agent reconciles the intent against current targets. Equal writes are
   adopted; missing targets are applied only after a complete bounded lookup;
   conflicts remain explicit. A lost intent-create response must itself be found
   and reconciled by operation/School-OS ID before another effect is attempted.

No locks, leases, conditional-write coordination, generation chain or content
hash for source identity is proposed. Private development receipt hashes and
packet-bound semantic expectations remain required by AGENTS; they are not
canonical source identity or instance recovery prerequisites.
If the selected adapter cannot establish complete lookup or
readback, it cannot claim completion. Internal sequence numbers may order a
single work item's steps; they are not source identities or concurrency guards.

Grounding: all priorities, especially P1/P2/P4/P9; all stateful use cases.
Alternatives: immutable whole-instance generations give one publication pointer
but require broader state packaging; an event engine offers replay at the cost
of replay/index maintenance. This proposal has simpler local repairs but more
partial states. Cross-record recovery and actual Drive consistency are unknown
until user-directed testing; no atomicity is assumed.

### Approved query-coverage rule

On 2026-09-14 the user explicitly said "Okay, make it so" after the recommendation
to check coverage alongside knowledge, finish missing processing only within
authorized scope, or answer with the limitation. This approves this rule only;
the record mechanisms remain undecided and interrupted-write recovery is now
deferred outside the MVP.

1. A question is answered from verified knowledge together with discovery and
   content-processing coverage for the source scope needed to support the answer.
   A completed write proves that its records saved; it does not prove that all
   potentially relevant emails or attachments were discovered and processed.
2. Unread or undiscovered material may contain relevant information. Do not
   exclude it merely because current knowledge, a subject, or an incomplete
   search does not show a connection to the question. A deadline tomorrow may
   have been communicated earlier; the deadline is not the email discovery date.
3. When missing processing could affect the answer, complete it only within the
   current authorization, available capabilities and operation budget. Otherwise
   answer from the verified information with an explicit account of the gap.
   A question does not authorize clearing the entire unrelated backlog or
   expanding processing beyond its authorized scope.
4. Do not claim a complete list, an exhaustive count, or absence of information
   when coverage does not support that claim. If a bounded coverage lookup itself
   remains unfinished or coverage is unknown, disclose that limit too. Preserve
   continuation on Drive; lack of a discovered pending item is not proof that
   none exists. Individual verified facts remain usable with source attribution.

Example: "What is due tomorrow?" finds two verified tasks, but yesterday's
processing is incomplete. If the missing processing cannot be completed within
scope, answer: "I found these two tasks in the processed information. Yesterday's
processing is incomplete, so this list may be missing something."

This rule serves P1 losslessness/provenance, P2 explicit reliable state and P4
bounded execution, especially U2 historical and current school queries. Requiring
all processing to finish before any answer is a credible alternative, but delays
useful answers when sources are unavailable or the budget is exhausted. The
approved rule permits useful qualified answers at the cost of coverage reads
and sometimes an incomplete result. Exact bounded coverage access still depends
on the pending record/adapter/query contracts. This rule does not restore the
deferred interrupted-write recovery procedure or approve recovery triggers.

## D3 — Runtime, adapter contracts and first supplied routes

**Approved direction, 2026-09-15:** use small Python standard-library routines
and start with the minimal set reasonably estimated to be useful. All remaining
work belongs to the agent and its actual tool operations. Recipes mention the
real script and relevant routine so a capable agent can use it for that step.
Do not build a larger runtime simply because the agent can execute code.

This extends the 2026-09-14 code-capability approval. The user's supplier
confirmation remains user-reported, not an independent qualification result.
There is no approved Python version pin, third-party dependency, provider SDK,
network requirement, CLI dependency or persistent process. The agent may use
its native tools alongside these small routines.

The initial implementation subset is
[`helpers/source_metadata.py`](../../../../helpers/source_metadata.py):

- `normalize_subject`: the approved source-subject normalization, preserving
  meaningful case, spacing and reply/forward prefixes. The caller must distinguish
  a known raw header from an already-decoded subject to avoid double decoding.
- `normalize_address_parts`: normalize already reliably extracted address parts;
  preserve local-part spelling/dots/plus tags and lowercase the domain. Parsing
  unknown connector/display forms remains with the agent/tool route.
- `utf8_size`: measure the exact text's UTF-8 byte length so the agent can respect
  D1 page limits. It does not choose record fields, serialize pages or write them.

These are pure local helpers, not canonical schemas, source identity decisions
or a provider adapter. Their local function arguments/results are ordinary
implementation interfaces, not a new persisted record contract. Preserve original
metadata outside the normalized return value. Do not convert unsupported helper
input into an invented source value or a reason to use content/provider IDs for
identity. No helper selects the pending Date sufficiency threshold or establishes
that content was processed.

The agent remains responsible for source discovery, actual metadata extraction,
Date meaning/precision, attachment/content reading, substantive interpretation,
canonical knowledge/tasks, source coverage, save/readback and external effects.
It also manages resources/continuation and follows D4/D6 completion obligations.
The [helper guide](../../../../helpers/README.md) names the routines and their
limits; operation instructions refer to that actual file rather than promising
an unspecified helper. A capable agent uses an applicable routine or carries
out the same approved procedure through its available tools. A routine's presence
does not establish that it is usable in every managed environment.

The user also explicitly approved a setup interview and **one shared semantic
adapter per external tool**. Offer the task tools known and available to the
executing agent, explain access/capability limits and ask which the parent wants.
If the chosen accessible tool lacks a mapping, author it within approved meanings
and save it as discoverable shared instance material. Creation of that conformant
mapping needs no repeat approval. Do not invent unsupported tool semantics.

An adapter maps School-OS logic to the tool's own concepts, such as parent planned
date, completion and task identity. It is independent of agent, connector, API,
SDK, authentication and transport. Each agent's connector supplies actual access
and API mechanics. Other capable agents reuse the same adapter, not a copied or
forked agent-specific mapping. A connector that cannot perform a required
operation remains limited; an adapter cannot create that capability.

Use existing D1 separation: supplied adapter instructions belong with system
material; user-created mappings with extensions, discoverable through existing
instance guidance/configuration. No new registry, precedence algorithm or
publication ecosystem is selected. See the reusable [setup](../../../../operations/setup.md),
[adapter procedure](../../../../operations/tool-adapters.md) and
[authoring template](../../../../operations/tool-adapter-template.md).
This supersedes previous wording treating a runtime/API wrapper as a School-OS
adapter. No centralized job register, scheduler, SDK runtime or writer is added;
specific new canonical/tool behavior still requires explicit approval.

For later developer connector evidence, retain [AGENTS](../../../../AGENTS.md)
privacy safeguards and complete private receipts. No live connector probing,
replay or private-source collection occurs now. The prepared helper checks are
written only; do not import, execute, compile or smoke-run the new helpers before
the user directs testing after the agreed code publication checkpoint.

Grounding: explicit repeatable source rules, simplicity, efficient execution,
capability-led portability and source independence. The small helper subset
supports those principles without becoming an orchestration or persistence
framework. The alternative of a larger program with provider SDKs would expand
dependencies and execution assumptions; it is not selected. Python availability,
input edge cases and actual agent use remain unqualified until directed testing.

## D4 — Production association, discovery and content coverage

### Approved execution direction, 2026-09-15

The user rejected a School-OS-managed partial daily run capped at 25 processing
appearances, 100 listing entries or 8 MiB per transfer. Those proposed application
ceilings and the associated batch/continuation manager are withdrawn from the MVP.
A single logical agent run must process all relevant unread/unprocessed emails
in its agreed scope. Reaching an agent-selected batch boundary is internal
progress, not successful completion or a reason to leave the remainder for a
later ordinary daily run.

The executing agent owns resource assessment, batch sizes, pagination sequencing,
working-context management and its runtime's continuation/recovery. School-OS
supplies [guidance](AGENT-EXECUTION-GUIDANCE.md), explicit source/coverage procedures
and completion obligations. It does not implement or manage an agent batch queue,
catch-up scheduler, per-run message cap or generic runtime recovery service.
The user explicitly relies on capable personal agents and their normal continuity;
named environments are context, not a new independent qualification claim.

The approved D1 page/directory limits remain: they bound individual data access,
not how much the logical run must finish. Raw material is processed in manageable
units and discarded after verified persistence. Search exhaustion, individual
reply coverage, attachments and semantic extraction cannot be replaced by a
count of provider entries or by a mailbox read flag. The agent must verify the
whole intended ingestion before daily brief composition under revised D6.
If access or content support prevents that, the task is blocked/incomplete, not
a successfully finished partial daily brief. D2 canonical-write repair remains
deferred; agent-owned runtime recovery does not implement that feature.

### Approved scope, precision and binary ingestion

Q3 approves all relevant School-OS-pending emails through run start, including
older not-ingested messages even if marked read in Gmail. Later arrivals belong
to the next run. The user rejected a full-history enumeration on every daily
run (Q4); a simpler live-window discovery proposal is still for approval. Source
window continuation, token-loss replay and following all pages remain required.
Live access is an operating expectation, not proof that an unknown connector
exposes every message or that search uses original Date rather than arrival time.

Q5 approves the stricter threshold: verified mailbox, original subject,
normalized sender and individual original Date with known timezone and declared
second-or-finer precision, no comparable contradiction and adequate lookup
coverage. Equivalent zoned instants agree; preserve original values and precision.
Use an available richer metadata read when needed; unresolved evidence stays
unresolved. Unknown optional fields do not manufacture duplicate emails. The
frozen Gmail provider-entry study does not qualify this policy.

Q6 approves a binary logical-email outcome: fully ingested or not ingested.
Full ingestion includes body and every required attachment candidate, substantive
extraction and verified persistence. Partial-email processing/resumption is not
an MVP workflow. Honest inventory/evidence remains necessary to justify full
completion; unread content cannot inherit a processed flag. The narrower rule
for reusing a full result on a later metadata match is still proposed in
[question 6](OPEN-QUESTIONS.md#q6-when-a-matching-email-appears-again-what-may-the-agent-safely-skip-reading).
No per-appearance ledger, generic writer or recovery engine is selected.

Grounding: losslessness/provenance, simple agent-led procedures, efficient bounded
access, managed-agent portability and independence from brittle identifiers.
The revised complete-run obligation is a required outcome, not an assertion that
a connector can expose inaccessible mail or that every source is supported.
Implementation and user-directed qualification remain separate.

## D5 — Substantive knowledge, queries and task reconciliation

**Approved explicitly, 2026-09-15:** the user said “Regarding D5, I approve the
plan.” This approves the D5 mechanisms below, including the 14-day recurrence
fallback and three-way synchronization; remaining record/runtime/adapter
contracts are dependencies, not reasons to ask for D5 approval again.

Use claim-level substantive records, preserving instructions, conditions,
exceptions, dates, applicability and explicit finite-action disposition. Related
claims can share a topic without losing independent source support. Repeated
content does not overwrite provenance. A correction needs an explicit evidenced
relationship; a later timestamp by itself does not replace a school rule.
Retain superseded claims and unresolved contradictions. Agent reasoning proposes
relationships and records its source-based justification.

Queries retrieve claims, qualifications, task state and coverage within bounded
directories. Answers cite sources through current access aids plus readable
source metadata and disclose unavailable originals, uncertain attachment mapping
or incomplete search. No source access is needed merely to repeat already saved
verified knowledge. If a question needs uncataloged detail, use an authorized
content route or explain the gap; do not invent it.
Apply the [approved query-coverage rule](#approved-query-coverage-rule) when
deciding whether the answer can claim completeness. D5 is now independently approved; the earlier query-rule approval remains valid.

Finite actionable requests create canonical tasks. Non-actionable guidelines do
not. A recurring required action remains an actionable canonical task with its
source recurrence, applicability interval and individual occurrence/completion
history. A capable task adapter may project recurrence; otherwise it projects
explicit occurrences within the configured planning horizon and records limits.
Default planning horizon is the next 14 days, with continuation kept on Drive.
Do not silently classify a required recurring response as mere guidance.
Tasks receive owned IDs once. A semantic task relationship requires the same
request/entity and compatible source context; title similarity alone is not
identity. Explicit corrections, reminders, completion and reopen evidence are
recorded separately. Replay does not reset parent completion or a planned date.
School deadlines remain source evidence, separate from parent working plans.

**Completion amendment approved explicitly, 2026-09-15:** when clear observed
evidence satisfies the correctly linked task, classify it as **Completion
detected — awaiting parent confirmation**. Preserve that state and its source
evidence on Drive; it is not completed. The shared tool adapter maps it to a
supported status or section so the parent can review these tasks and check them
off. The agent's connector executes and verifies the actual permitted updates.
Parent confirmation follows the existing D5 sync rules and makes it completed
on Drive and in the task tool when both updates are established. Do not downgrade
an already parent-confirmed task because a later receipt arrives. Ambiguous or
partial evidence cannot imply that the whole task was satisfied. If a route
cannot show the distinction, keep the canonical pending confirmation and report
the tool limitation; do not fake completion. See [the authored procedure](../../../../operations/completion-review.md).
Future direct automatic completion requires a later explicit decision after
accuracy is observed. No threshold, telemetry engine, polling job, new source
scope or automatic mode switch is adopted by this approval.

Preserve parent-editable owner, planned date, progress, completion and personal
notes. School action/context/deadline remain source-supported; a parent's proposed
change is a recorded override or conflict, not altered school evidence. Parent-
origin tasks can be added with their origin explicit. Reopening a completed task
requires explicit parent/source evidence, not absence from a provider snapshot.

For configured task apps, use the last verified shared values as a three-way
comparison: unchanged remote preserves canonical updates; unchanged canonical
accepts an allowed parent edit; agreeing edits converge; divergent same-field
edits await review. Deletion from the external app records a missing projection,
not canonical task deletion/completion. A selected adapter carries the School-OS
task ID in a managed field and verifies it on readback; current provider IDs only
locate that field. Missing identity yields reconciliation, never a title match.

Grounding: P1/P2/P5/P7/P9; queries, tasks and canonical-data applications.
Alternative: one-way task export is simpler but loses parent interaction; mutable
summary-only knowledge is compact but weakens provenance and corrections. This
proposal requires careful semantic judgments. Prepared independent expectations
must cover finite `is_action` disposition and cannot be copied from output.
No zero-action aggregate is accepted without source-supported justification.
For independent developer semantic expectations, retain the AGENTS requirement
to bind each expectation to the exact packet hash and ordered segment identities
and content hashes, and prepare the cross-packet zero-Fact rejection case.
These are private interpretation-audit bindings, never matching evidence or
canonical email/attachment identity. This does not authorize executing an audit.

## D6 — Brief selection, delivery, audio and unknown effects

### Approved agent verification and ingestion gate, 2026-09-15

The executing agent determines whether its authorized connectors/APIs/tools can
validate an uncertain action and uses the available means to inspect the actual
result. For example, inspect the sent message when checking an email send or
read the selected task application's saved task when checking its update. Merely
having a connector or receiving a generic error does not prove the action's
outcome. Report the evidence and any remaining inability to verify. Do not
blindly repeat an uncertain action. This uses the existing evidence discipline;
School-OS does not select the former generic persisted-effect intent/reconciliation
engine as its MVP implementation. No D2 partial-write repair is reinstated.

Before composing the daily brief, the agent first validates that **all intended
emails and content have been ingested**, with complete relevant discovery and
verified processing/persistence. Q3 approves the run-start cutoff for all School-OS-pending email in configured
scope. An agent's batch boundary is not this gate. If ingestion is blocked or
unverifiable, report the blocker rather than creating the normal daily brief
from a knowingly incomplete selection. This is stricter than a general knowledge
question: the approved query rule still allows a useful answer with coverage
limits. It is not permission to deliver a partial daily brief as complete.

This resolves the prior question of wait-versus-partial daily delivery. The user
and executing agent own schedules and runtime continuation under the D7 deferral.
The instruction does not itself approve actual sends, scheduled jobs or testing.

### Approved starter selection and extensible recipes, 2026-09-15

The user accepted the daily template's selection of newly verified or
substantively corrected knowledge, original source dates, relevant open tasks
and disclosure of failed task-app synchronization. This includes newly learned
older information and avoids presenting unchanged rereads as new. Preserve
parent-confirmed completion separately from completion detected awaiting review.
The brief must not imply the task app was synchronized when it was not.

School-OS supplies this daily recipe as a starting template. The user and agent
may create any number of compatible brief recipes and choose whichever suits the
request. For example, a household can define a weekly overview, an event brief
or an audio presentation. Content selection belongs to that chosen recipe;
source accuracy, honest coverage, task meaning and the ordinary daily complete-
ingestion gate remain requirements. Use existing D1 instruction/extension
locations and references. No recipe registry, field schema, precedence engine
or scheduler is introduced. See [brief recipes](../../../../operations/brief-recipes.md).

Historical import does not implicitly authorize sending a backlog. A completely
read action-free snapshot must not attempt a nonexistent task write.

### Approved manual freshness conversation and audio delivery

Q7 permits a limited manual brief after warning that knowledge may be outdated,
showing available last ingestion/discovery coverage and last source-email dates
(or unknowns), and asking whether the parent wants new email ingested first.
If the parent chooses now, send the authorized brief with a clear limitation.
Do not substitute a newest source timestamp for complete searched-through
coverage. The ordinary daily ingestion gate is unchanged.

Q8 rejects keeping an audio archive. Do not retain generated audio in canonical
Drive storage. After verified delivery to the parent by authorized email or chat,
discard accessible temporary processing copies. No provider-storage deletion or
replay history is promised.

Q9 requires configured audio to be prepared and delivered together with email.
If audio fails, send the email without it and include an explicit failure notice.
Audio narrates the same verified information and qualifications. Unknown effects
still require executing-agent verification; do not blindly send a second email.
No timeout, background retry mechanism or scheduler is introduced. The selected
capable tool/route and recipient come from setup or the authorized request.
Operation/output attribution remains; D7 register-backed history is deferred.

Grounding: source-linked useful briefs, clear completion evidence, simplicity,
capability-led agent reasoning and truthful external outcomes. Real readback,
eventual visibility and unattended permission remain unqualified. A sent-folder
observation can establish a sent item, not that a recipient read it. An agent
without sufficient evidence leaves the outcome unverified instead of assuming
failure or resending automatically. No exactly-once guarantee is claimed.

## D7 — Register, capability discovery and schedules

**Outside MVP by explicit user direction, 2026-09-15.** Do not implement the
centralized tools/connections/capability/job register, scheduler creation/change/
pause/reconciliation, pinned-job binding manager or register-backed known-job
and sender queries. The original proposal is retained in
[revision 6](https://github.com/jeremieguedj/School-OS/blob/62070ebf39f79bb316c0f009a1d9ba49be98f151/docs/plans/restart/implementation/ARCHITECTURE-PROPOSAL.md#d7--register-capability-discovery-and-schedules).

Users and their agents manage their own scheduled jobs. Each executing agent
reads the selected School-OS recipe, determines which adapters/capabilities it
needs, and manages its execution using the project rules. Several agents/jobs
may use the instance, on the explicit assumption that they do not operate on
the same Drive data concurrently. Do not implement locks, leases, a single-agent
slot or another scheduling service. Ordinary operation configuration and adapter
requirements remain necessary; they do not become a hidden substitute register.

This is a stated MVP exception to the product's broader tools/schedules/visibility
requirements and core known-jobs use case. Fresh agents can still use canonical
knowledge and applicable recipes, but the MVP cannot promise a centralized answer
about all known jobs, their live status or a historical job's sender.

## D8 — Package format, upgrades, extensions and legacy retirement

**Outside MVP by explicit user direction, 2026-09-15.** Defer the packaged
installer, ZIP builder/manifest machinery, version compatibility manager,
staging/activation/upgrader, migrations and managed extension-preservation
workflow. Keep their
[earlier proposal](https://github.com/jeremieguedj/School-OS/blob/62070ebf39f79bb316c0f009a1d9ba49be98f151/docs/plans/restart/implementation/ARCHITECTURE-PROPOSAL.md#d8--package-format-upgrades-extensions-and-legacy-retirement)
as future design, not MVP code or acceptance work.

The project must remain easy to extend with installation and upgrades later.
Use the already approved D1 separation of official system files, private instance
records and compatible additions; keep reusable recipes/contracts/code distinct
from household data. This direction does not approve a new directory schema,
manifest, version pin, migration or activation protocol. Basic Drive startup and
configuration remain necessary for the retained use cases; first-use setup follows the approved layout through agent/tool instructions;
any specific new architecture still needs approval. Do not silently substitute
a new installer for the deferred package design.

Repository preservation and continuity still apply: retain Git history and the
committed baseline tag before any retirement, keep principles/current design,
frozen evidence and privacy safeguards, and remove retired instructions only
within accepted implementation cleanup. The D8 deferral is not authorization to
delete unrelated or uncommitted material. The user-owned testing checkpoint
still follows publication of the agreed MVP code, not a package build or pilot.

## Approval record and next action

**D1 is approved.** The user explicitly replied "D1 approved" on 2026-09-14
after clarification that its JSON and directory limits apply per page, with
additional pages available as history grows. The [active plan](../PLAN.md)
records the full D1 approval scope. The user separately approved the
[query-coverage rule](#approved-query-coverage-rule) with "Okay, make it so";
this is not blanket approval of D2. The user subsequently **skipped D2 for now
and excluded interrupted-write recovery from the MVP**. Keep the retained D2
proposal deferred. The user approved required code-execution capability under
D3 and supplied confirmation of its availability from personal-agent suppliers.
That does not approve the rest of D3 or qualify particular runtime/adapter routes.
On 2026-09-15 the user approved D5, replaced D4's batch manager with
agent-managed complete-run execution, directed agent-led effect verification and
ingestion-before-brief under D6, and deferred D7/D8 from the MVP. The active plan
records these boundaries and the later Q3/Q5/Q6-outcome/Q7–Q9 approvals.
Resolve Q1/Q2 fields/indexes and Q4/Q6 discovery/reuse proposals before dependent
implementation.
The records/ordinary-save framework is excluded, not an MVP gate. Do not ask for
approved D5 mechanisms again or rebuild deferred infrastructure as a dependency.
Publish the agreed MVP code and continuity, verify the remote revision, then
stop for the user's testing direction. No test, simulation, replay, build, probe,
ingestion, scheduled operation or live qualification is authorized now.
