# Restart implementation decisions for approval

Updated 2026-09-15, revision 6: adds detailed decision walkthroughs and identifies
unresolved completion, scheduling and MVP recovery dependencies. No new approval.
**D1, query-coverage rule and D3 code-execution requirement approved; D2 skipped;
remaining D3 and D4–D8 pending.** No
production code depends on these choices yet. Approval of requirements in the
[active plan](../PLAN.md) does not approve these mechanisms. Approval of this
document would authorize the choices stated here, not unspecified later changes.
Testing remains reserved to the user after publication of the implementation.

The [coverage map](COVERAGE.md) maps the complete product to deliverables. The
recommendations below serve that whole scope. They do not propose reducing it
to an identity model, a local CLI, or a single managed-agent demonstration.

The [detailed decision briefs](decision-briefs/README.md) explain remaining D3
and D4–D8 through fictional emails, flows, parent-visible results, alternatives
and implications. Their additional recommendations are explicitly unapproved.
Written examples are not executed simulations or qualification evidence.

## Decision summary

| Decision | Recommendation | Main alternative | Approval |
|---|---|---|---|
| D1 Storage | Small JSON record pages and paged directories in Drive, with a readable bootstrap | Native Sheets tables, with separately bounded long text | Approved, 2026-09-14 |
| D2 Records and persistence | Retained proposal: typed records and verified small write intents | Immutable whole-instance generations or an event engine | Review deferred; interrupted-write recovery outside MVP; query rule remains approved |
| D3 Execution and adapters | Code-capable agents required; exact code/runtime and adapter contracts remain proposed | Earlier support for agents without code execution is superseded | Code-execution requirement approved, 2026-09-14; remaining D3 pending |
| D4 Ingestion | Exact zoned original Date for automatic association; bounded received-time discovery where supported; process appearances independently | Admit coarser Dates automatically; reuse content coverage from metadata alone | Pending |
| D5 Knowledge and tasks | Source-supported claims and explicit relationships; parent fields separate; three-way task-field reconciliation | Mutable summaries and one-way task export | Pending |
| D6 Briefs and effects | Persist intent before external effects, reconcile unknown outcomes, brief selection by newly verified knowledge | Retry uncertain sends; source-Date-only brief selection | Pending |
| D7 Tools and schedules | Capability and binding register; externally managed jobs with desired/observed state | One fixed scheduler/runtime | Pending |
| D8 Packages and upgrades | Versioned ZIP, isolated official/instance/extension areas, staged pin changes | In-place replacement or migration on every update | Pending |

No option proposes changing metadata-only identity, source custody, unrestricted
agent/job counts, or the exclusion of concurrent same-data writes. Those are
already approved and are not being resubmitted for approval.

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

D2 also bundled record schemas, UUID representation and locator structure.
Skipping its review does not approve those choices or remove the canonical
knowledge/tasks/configuration/register requirements. Present the minimum record
and ordinary-write design separately before dependent code; do not substitute a
new persistence mechanism silently. Continue with D4 after recording the D3
code-execution requirement; remaining D3 contracts are still pending.

Remaining D3 and D4–D8 remain proposals. References to D2 intents in external-effect handling,
installation and upgrades must be reconciled during their review; they cannot
silently restore the deferred recovery mechanism. This exclusion does not itself
decide D6's unknown-send/task outcomes or D8's upgrade behavior. No tests are
authorized by this scope change.

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

**Deferred review.** Interrupted canonical-write recovery below is outside the
MVP by explicit user direction. The record inventory and ID/locator choices are
retained undecided; they are not adopted through D1 or through this deferral.
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

**Approved requirement, 2026-09-14:** a School-OS agent must be able to execute
code in its available execution environment. The user reports having confirmed
this capability with all major personal-agent suppliers. Record that as
user-reported supplier confirmation, not an independently observed qualification
result. Do not require a supported operating path for agents that cannot execute
code. The earlier D3 proposal to accommodate such agents is superseded.

This requirement does not select Python or another language, versions, libraries,
SDKs, code entry points, or runtime/provider contracts. It does not require every
operation to use code, a dedicated personal computer, persistent local process,
or coding CLI. The agent still reasons over explicit procedures and uses
replaceable adapters. No capability probes or tests are authorized here.

The remaining proposal is authoritative Markdown operation recipes and JSON
contracts/examples, with small callable code for normalization, record
preparation and bounded planning. Python standard-library helpers remain a
candidate implementation choice awaiting approval. Record and ordinary-write
mechanisms remain undecided, and D2 interrupted-write recovery stays outside
the MVP. Instructions must explain the selected code and tool operations clearly.

Generic adapter operations cover storage list/read/write, source enumeration,
individual metadata/content/attachment reading, task snapshot/apply/readback,
email delivery/lookup, audio generation/retrieval, and scheduler management/readback.
Each operation returns a small contract with observed data, scope/completeness,
capability limits and outcome. Tool envelopes and provider aliases are projected
at the adapter boundary; conflicting duplicated fields remain errors. Unknown
capabilities and transport-with-no-response stay distinct from provider errors.
No inferred throttle, authorization failure or successful write from a generic
error. Credentials remain in the runtime's authorized store.

Ship initial adapter procedures and mapping helpers for Drive JSON storage,
Gmail source/email, Google Sheets and Todoist task projections, a generic managed
scheduler plus ChatGPT Work and Claude managed-runtime profiles, and ElevenLabs
optional audio. Profiles declare required operations and unsupported/unknown
states; naming a vendor is not a capability or qualification claim. Runtime tool
names are supplied by discovered mappings, not embedded as canonical contracts.
Unknown runtimes can supply the same operations. Local Codex is a development
surface, not a required household runtime. No live adapter probes occur now.

For future developer live connector defects, follow [AGENTS](../../../../AGENTS.md)
exactly: preserve the complete raw result or exception before normalization in
a mode-0600 file under an admitted gitignored private run directory. Retain the
complete observed topology and private evidence for later user-directed replay.
Installed agents persist sanitized failure/coverage facts and source access
references on Drive; this proposal adds no installed raw-error archive. Raw
processing material follows the temporary-source policy. An inability to export
a diagnostic receipt is explicit, never fabricated evidence of an outcome.
Public diagnostics follow AGENTS' privacy-safe allowlist. Private development
receipts are not prerequisites for canonical installed-instance recovery.

Grounding: P2–P9; install, all applications, extensions and agent replacement.
The approved code capability supports repeatable mechanical operations across
personal-agent environments. The earlier alternative of native-tool-only support
would avoid requiring code capability but adds a second operating path; the user
has selected code-capable agents. The tradeoff is a capability prerequisite,
without a chosen language or execution contract yet. Exact file/network access,
libraries, limits and adapter behavior remain unqualified. A mandatory persistent
runtime service is neither required nor approved. Provider-specific contract
changes will be surfaced if they change this architecture.

## D4 — Production association, discovery and content coverage

Implement the current metadata recipe unchanged in its approved meaning.
The remaining exact acceptance threshold needs a decision: recommend automatic
reuse/new-record creation only with verified mailbox, original subject, normalized
sender and the individual original Date with known timezone and second-or-finer
declared precision. Equivalent zoned instants agree. Preserve every original
precision and never invent missing seconds. Minute/day evidence, missing timezone
or unclear time meaning can narrow candidates but remains pending after one
available richer metadata read. Received time supports comparison; it never
replaces the original Date. Optional comparable contradictory metadata prevents
reuse. Multiple compatible existing records remain unresolved.

Alternative: allow agreeing minute-precision Dates or permit source-grounded
agent judgment in more cases. That can reduce pending work, but would require
an explicit decision table for what sufficient evidence means. The historical
second-resolution evaluator is not approval of this production threshold.

For discovery, recommend separate historical and daily tracks over half-open
windows in a declared source search-time basis. Prefer documented received-time
listing for arrival discovery, while using original Date only for identity.
Never relabel a provider's internal timestamp as received time. If the adapter
only offers another understood listing basis, record that basis and its limits.
Default historical window is seven days; daily overlap is seven days; start
date/school scope and timezone are instance configuration. Catch up all missed
windows under the budget. Newly imported older mail requires a supported change
route or explicitly requested historical rescan; overlap does not promise it.

Default run budget is 25 individual-message processing observations, 100 listing
entries and 8 MiB per content transfer, stopping sooner when the runtime limit
requires it. These are configurable planning ceilings, not throughput claims.
Continuation follows every available page, including short pages, until explicit
exhaustion or a saved unfinished window. An unavailable token causes replay.

Processing each discovered appearance is separate from associating its logical
email. Recommend reading each appearance admitted for processing even when its
metadata reuses an existing record; retained knowledge is reconciled semantically.
Do not declare new unread material processed from a prior matching record.
This may repeat work in overlap/replay and is an explicit efficiency tradeoff.
Do not introduce body hashes or provider-entry IDs to avoid it.
Discovery and content work advance separately: persist an inventory-pass work
record and its admitted observations before spending the processing budget;
finish its pending content work before starting another overlap pass over the
same completed discovery interval. A replayed unfinished listing follows its
continuations through the old prefix to new work within the listing budget.
If the budget cannot reach new work, narrow the unfinished time window where
possible or record a no-progress/budget limitation for review. Do not loop on the
same prefix or claim exhaustion from narrowing. Work/pass IDs describe saved
processing assignments, not permanent provider-entry identities.

For same-parent/same-name attachments, retain the candidate group and read all
available candidates within the current bounded inventory pass. Preserve facts
with group-qualified provenance if exact attachment association is unavailable;
report that limitation. Coverage states what this pass actually read and the
scope of the inventory. A later reordered/changed/uncertain inventory does not
inherit per-candidate completion from position, handle or matching name. Unnamed
images and unsupported/oversized content remain visible work. Content structure
may guide extraction and reading, but never identity or thread association.

Grounding: P1–P6/P9; catalog, historical/daily processing and recovery. Remaining
unknowns: available metadata precision, complete listing bases, delayed indexing,
candidate reading and real transfer limits. The fictional model will illustrate
these decisions separately from frozen studies; it cannot qualify adapters.

### Open completion and continuation choices

D4's proposed limits apply per execution/transfer, not to total stored history
or a guaranteed daily completion quota. A run can end with successfully saved
unfinished work. A saved backlog does not launch another execution. The current
proposal does not select an automatic continuation trigger, daily aggregate
budget, freshness target, no-progress escalation or brief timing policy.
Resolve these with D6/D7 before promising a daily service outcome. The
[D4 brief](decision-briefs/D4-INGESTION.md) explains the 40-admitted/25-read/15-unread
case and alternatives. Its added policy directions remain proposals, not a
change to the existing 25-per-run draft or an approval of deferred D2 repair.

## D5 — Substantive knowledge, queries and task reconciliation

Recommend claim-level substantive records, preserving instructions, conditions,
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
deciding whether the answer can claim completeness. Its approval does not
approve the other D5 knowledge/task mechanisms.

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

Recommend parent-editable owner, planned date, progress, completion and personal
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

Recommend selecting a daily/recent update by the interval when knowledge was
first verified or substantively corrected in Drive. Display original school
dates separately; late-processed historical information is labeled as such.
Include relevant outstanding tasks and disclose incomplete ingestion. Historical
import does not automatically deliver a backlog: delivery is an explicit
operation or configured job. A manual recent brief takes an explicit interval.
Task-sync failure is disclosed and does not erase canonical tasks or automatically
block a knowledge brief; a completely read action-free snapshot proceeds directly
to brief composition.

Email contains source-linked substantive updates, relevant guidelines and tasks;
optional audio narrates the same selected canonical information. Save generated
audio as a derived output artifact on Drive with input references and attribution;
keep it until the parent explicitly deletes it. Raw email/attachment custody is
unchanged. Unsupported audio is disclosed and email remains usable.

Recommend one external-effect procedure for task writes, schedule changes, email
and audio requests: persist and verify intended operation, owned effect ID,
targets and exact intended projection; mark dispatch outcome unknown durably
before dispatch; then reconcile observed output. Provider receipt alone is not
canonical verification. Use School-OS markers where supported and complete
provider reads of relevant target content to adopt a single matching result.
If outcome cannot be established, retain unknown and stop that effect. Retry
only with evidence it was not applied, or a parent's explicit decision after
the duplicate risk is explained. No blind resend after a timeout or empty search.

The brief occurrence is identified by job/operation plus requested reporting
interval and variant. A repeat run reconciles that occurrence before sending.
Save historical job, generator, selected configuration, sender service/account,
destination, artifact/delivery reference and verification time with each output.
Changing defaults never rewrites that attribution.

Grounding: P1/P2/P5/P6/P9; briefs, task applications and sender queries.
Alternatives: source-Date-only recency misses newly processed old information;
automatic retry improves apparent availability but risks duplicate effects.
Unknown: services' searchable evidence, eventual visibility, audio artifacts and
unattended authorization. No guarantee of exactly-once external effects.

## D7 — Register, capability discovery and schedules

Recommend capability entries per actual runtime/adapter/connection combination,
with supported/unsupported/unknown disposition, observed limits, authorization
location and verification time. Discovery starts with declared tools and user
bindings; testing them is a separate authorized activity. A scheduled operation
needs known authorization for its required effects; a job launching does not
prove unattended write capability.

Store operation defaults separately from pinned per-job bindings. Job creation,
change and pause use the D6 effect procedure. Desired settings stay pending until
the external scheduler is inspected and the observed settings recorded. There
is no single active-agent slot and no automatic job rebinding on default changes.
Each scheduled prompt names the Drive bootstrap, installed operation, scope,
budget and output destinations. Missed invocations recover from Drive windows,
not a scheduler's remembered conversation or local process.

A fresh reader can list known jobs, runtime, location, trigger, bindings, outputs,
last observed status and verification freshness. It can identify a recorded
brief's generator and sender without management access to that scheduler. It
must not claim discovery of unknown/unregistered jobs or live verification from
stale register values.

Grounding: P3–P9; known-jobs/sender query, automation and replacement.
Alternative: one fixed scheduler simplifies configuration but violates the user's
choice of agents/jobs. Actual schedule control and unattended permissions remain
unknown per runtime; the initial package includes the procedures and contracts,
with qualifications left explicitly unestablished.

## D8 — Package format, upgrades, extensions and legacy retirement

Recommend a ZIP containing a release manifest, readable entry point, operation
recipes, versioned record/adapter contracts, default configuration examples,
code artifacts subject to remaining D3 decisions, reference adapter mappings,
extension guide and license.
An optional standard-library builder writes that archive; it will be prepared
but not executed during this implementation phase. Package hashes verify
official package integrity; private developer receipt/expectation hashes retain
their separate AGENTS role. None becomes source identity or thread association.

The manifest records package version, compatible schema/contract major versions,
file inventory and qualification status. The initial restart remains explicitly
unqualified. Installation from a supplied archive saves official files and
configuration, verifies their persistence, then activates the bootstrap pin.
No live GitHub access is required for routine installed operation.

Recommend semantic major/minor/patch versions for package/contracts. Additive
optional fields can be compatible; changing meaning or required fields needs a
major version and separately approved migration. Compatible extensions declare
their supported contract major version, own namespace and file inventory under
`extensions`. Upgrades must not overwrite private data/configuration/extensions.

Upgrade stages a new official version, records a Drive upgrade intent, checks
declared compatibility and verifies copied files before changing the installed
pin. The prior package stays available. If interruption precedes activation,
continue the prior pin and retain pending upgrade work; if activation outcome is
unknown, read the bootstrap and reconcile. Rolling back code after incompatible
data changes is not promised. This restart does not migrate retired instances:
provide clear fresh-install and migration-not-yet-authorized instructions, not
an implicit import or destructive rewrite.

Retire old runtime/instruction/schema/template/adapter/test trees from active use
after the preserved baseline tag. Keep current principles, restart design and
frozen studies, history, continuity and privacy safeguards. Historical documents
link to baseline source where they refer to removed files. Update generic entry
points to prevent retired instructions being selected. Preserve the existing CI
triggers and prepare a replacement `scripts/validate.py` entry point for the new
nonempty test inventory, refusing an empty/unknown suite. Prepare it without
execution. Recheck actual hooks, final CI and remote PR state before publishing
the dedicated branch/tag; do not open a PR or dispatch the workflow in this phase.
The preserved baseline is tag `restart-baseline-2026-09-14`, targeting
`39d752c364a1cf404e5a6fc5739148b7d35a6b35`. Frozen executable/result bytes stay
unchanged; a local tag alone does not establish its publication.

Grounding: P3/P6–P9; supplied-package install/upgrade and compatible expansion.
Alternative: in-place overwrites are smaller but harder to recover and risk
extensions; migration on every update imposes needless work. Unknown: initial
archive handling in managed apps and compatibility in practice. Preparing the
builder and upgrade procedures does not qualify or execute them.

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
Continue with D4–D8; resolve remaining D3 and the minimum record and
ordinary-write design before its dependent implementation. A partial
approval releases only its independent scope. Any new choice not covered above
returns for approval rather than being labeled an
implementation detail. No testing permission is requested by this proposal.
