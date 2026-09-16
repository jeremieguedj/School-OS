# School-OS restart architecture and simulation

Status: the user approved the corrected interpretation and operating choices on
2026-09-14. The current [metadata recipe](identity/METADATA-RECIPE.md) defines
logical-email reuse, normalization, parent-bound attachment lookup and durable
search-window recovery. Implementation and managed-agent qualification remain
pending. The [artifact guide](README.md) separates current authority from frozen
experiments and historical proposals.

## Current coordinator checkpoint — architecture approval pending

Latest published instruction/documentation subset:
`087c061507731bac997624936dc6610ef0674f19` on `codex/restart-school-os`, verified
against the remote branch. The existing architecture website now reflects these
setup, shared-adapter, parent-confirmation and brief-recipe approvals, with D1
storage diagrams and retrieval/save walkthroughs. Publication succeeded. No
functional tests ran; this is not the whole-project implementation handoff.
Next: resolve the still-pending D4 scope/identity/discovery and D6 audio/manual
limited-brief choices while continuing independent approved implementation.
The testing phase remains stopped until the user's subsequent direction.


The 2026-09-14 implementation session remains in the existing repository directory
on `codex/restart-school-os`. Its clean starting revision was
`39d752c364a1cf404e5a6fc5739148b7d35a6b35`. The annotated preservation tag
`restart-baseline-2026-09-14` targets that committed pre-cleanup baseline.
The old runtime has not been adopted as the new foundation or removed yet.

The [whole-project coverage map](implementation/COVERAGE.md) reconciles all nine
design priorities, seven core use cases, other mandatory principle sections and
ten implementation areas. Requirements are already established; the remaining
blocker is approval of concrete architecture, not renewed product discovery.

The [architecture proposal, revision 9](implementation/ARCHITECTURE-PROPOSAL.md)
records recommendations and explicit decisions. **D1, query coverage, D3 minimal
Python standard-library helpers with agent/tool operations, and D5 are approved. D4/D6 now use the approved agent-led directions
below. D2 interrupted-write recovery, D7 and D8 are outside the MVP. Remaining
named D4/D6 choices remain pending; the separate record/save framework is
also outside MVP and must not be reinstated as an approval gate.**
On 2026-09-14 the user explicitly replied "D1 approved"
after the explanation of multiple JSON pages and per-page capacity limits.
Approval releases only work whose architecture dependencies are also approved.
The [HTML decision guide](implementation/architecture-guide.html) provides a
readable walkthrough of the decisions and mirrors this approval ledger; the
ledger here remains authoritative.
The [architecture in practice page](implementation/architecture-in-practice.html)
adds diagrams and seven fictional household walkthroughs. It makes the following
two specific policies visible. The first is now explicitly approved as amended
below; the second remains pending. No operation was executed:

- **Approved: detected completion requires parent confirmation.** The user
  approved clear source-supported detection for the correctly linked task,
  amending the earlier automatic-closure proposal. Record the distinct canonical
  state **Completion detected — awaiting parent confirmation** and supporting
  evidence; do not mark the task completed. The shared tool adapter maps this
  meaning to a supported task status or section, making the tasks easy for the
  parent to review and check off. Each agent's connector performs the actual
  permitted tool updates and readback. Parent confirmation then follows approved
  D5 synchronization to completed on Drive and in the task tool. Already confirmed
  completion is not downgraded by a later acknowledgment; ambiguous, partial or
  conflicting evidence cannot establish that the whole obligation is satisfied.
  If the tool cannot represent the distinction, preserve it on Drive and report
  the limitation rather than displaying completed. The instruction implementation
  is [completion review](../../../operations/completion-review.md).
  Automatic final completion may be considered later after accuracy is observed,
  but no automatic promotion, accuracy threshold or monitoring infrastructure is
  approved now. Existing source scope remains; this does not authorize searching
  Sent mail, background monitoring or additional account permissions.
- **Manual briefs with incomplete coverage:** the approved complete-ingestion
  gate explicitly governs ordinary daily briefs; the qualified-query rule does
  not by itself authorize a partial manual email send. Recommend permitting a
  clearly qualified manual brief only when the parent explicitly requests that
  output despite known gaps. Alternatively require complete relevant ingestion
  before every manual send. The first supports useful parent-directed access;
  the second is simpler but can delay useful output. Disclosure and task-app
  freshness must remain explicit. The complete-coverage fresh-agent example
  assumes usable authorized routes and does not establish provider support.

The completion amendment changes D5 as explicitly directed. The record/write framework remains
outside MVP; these are specific product-policy choices, not a reinstated schema
gate. No scenario, helper, connector operation or test was executed.

| Decision | Proposal subject | Approval status |
|---|---|---|
| D1 | Physical Drive layout, bounded pages and directories | Approved explicitly, 2026-09-14 |
| D2 | Earlier canonical-record and write framework | Repair and separate records/ordinary-save framework outside MVP; existing data meanings and query rule retained |
| D3 | Minimal Python helpers; shared tool-semantic adapters and agent-specific connectors | Approved explicitly, 2026-09-15, including setup interview, creation and reuse of missing tool mappings; no runtime version pin/SDK selected |
| D4 | Complete logical run; agent owns resources/batching; School-OS supplies guidance | Direction approved, 2026-09-15; finite scope/cutoff and remaining identity/discovery choices pending |
| D5 | Knowledge, tasks, parent synchronization and detected-completion review | Approved explicitly, 2026-09-15; detected completion awaits parent confirmation, represented by tool status or section |
| D6 | Agent verification, complete daily ingestion and extensible brief recipes | Verification/timing and starter selection/task-sync disclosure approved, 2026-09-15; any number of user/agent-created recipes allowed; audio and manual limited-brief choices pending |
| D7 | Capabilities/tools/jobs register and scheduler management | Deferred outside MVP, 2026-09-15; user and agents own nonconcurrent jobs |
| D8 | Packaged installation, compatibility and upgrades | Deferred outside MVP, 2026-09-15; preserve D1 separation for future work |

**D1 approval scope:** adopt revision 2 D1 in full: a readable Drive bootstrap;
`system`, `instance`, and `extensions` areas; multiple UTF-8 JSON record pages
with the specified headers and routing; paged directories with explicit
continuations; a default 64 KiB encoded-JSON limit per page and at most 100
entries per directory page; lossless long-text segmentation; bounded startup,
traversal and writes. These are per-page limits, not a fixed cap on total
instance history: more pages can be added. Drive capacity and practical access
cost remain constraints to qualify later. Exact record meanings, recovery,
adapter contracts and the other D2–D8 mechanisms are not approved by D1.
No production implementation or qualification is claimed by this approval.

**Query-coverage approval scope:** on 2026-09-14 the user explicitly said
"Okay, make it so" in response to the proposed rule to check processing coverage
alongside saved knowledge, complete missing processing only within authorized
scope, or disclose the gap in the answer. Adopt the
[query-coverage rule](implementation/ARCHITECTURE-PROPOSAL.md#approved-query-coverage-rule):
check discovery and content coverage as well as verified records; never assume
unread material is irrelevant; respect capability and work bounds; qualify
answers when processing or coverage lookup is incomplete. A verified fact may
be reported, but exhaustive lists, counts and absence claims require supporting
coverage. This does not require clearing all pending work before answering.
It does not approve the remaining D2 mechanisms, D3–D8, or any daily-run recovery
trigger/ordering rule. Required record and adapter contracts remain undecided.

### Approved brief templates and household recipes, 2026-09-15

The user accepted the proposed daily selection and task-freshness direction,
clarifying that School-OS starts with a **template recipe** and users and their
agents may create as many brief recipes as they want and adopt whichever they
choose. The starter daily template includes newly verified or substantively
corrected information, original source dates, relevant open tasks and disclosure
of failed task-app synchronization. Detected-completion tasks remain visibly
awaiting parent confirmation. This is a starter selection, not a universal
fixed brief or an immutable report format.

Adopt reusable, discoverable compatible household recipes within the existing
D1 system/instance/extensions separation. No new recipe schema, registry,
selection-precedence engine or scheduler is approved or required. Each agent
reads the chosen recipe and uses shared tool mappings through its own connectors.
Source accuracy, task-state distinctions, coverage honesty and the complete
agreed ingestion gate for an ordinary daily brief remain binding.
The authored [brief-recipe guidance](../../../operations/brief-recipes.md)
implements this direction as agent instructions, not as an executed briefing run.
Audio retention/ordering and the explicit manual-brief exception for known gaps
remain pending; accepting a starter selection does not decide them.

### User-approved MVP exception — interrupted writes

On 2026-09-14 the user explicitly decided to skip D2 for now and stated that
interrupted-write recovery is not part of the MVP. Defer the proposed durable
write-intent discovery/reconciliation/repair/resumption mechanism and its
acceptance scenarios. Preserve its design and prepared cases for future work.

This is an explicit scope reduction from the initial whole-project assignment
and the broader recovery direction in the product principles. The user direction
takes precedence for the MVP; the principles themselves remain unchanged.
The MVP must not claim to repair or complete interrupted canonical writes.
Normal verified persistence, honest incomplete coverage, the approved query rule,
bounded discovery/window continuation and fresh-agent access to saved knowledge
remain in scope. D6 now relies on executing-agent verification; D8 upgrades are separately
deferred. Neither may silently reinstate a School-OS D2 repair engine.

The user subsequently also excluded the separate records/ordinary-save dependency
from the MVP on 2026-09-15. Do not require that framework, a generic writer or its
schema catalogue before retained work. This deferral does not delete canonical
Drive knowledge/tasks/configuration/coverage or approve a replacement format.
Preserve existing D1/D5/source/coverage meanings and normal agent verification;
new architecture still requires approval if a specific need arises. Do not
recreate a blanket record-framework approval gate under another label.

**D3 approval scope, 2026-09-14:** the user explicitly requires an agent to be
able to execute code and reports confirmation from all major personal-agent
suppliers. Adopt code-execution capability as a prerequisite; the earlier
proposal to support agents without it is superseded. The confirmation is
user-reported, not an independently observed runtime/adapter qualification.
That initial decision selected no language. The later 2026-09-15 direction now
selects **small Python standard-library routines**, a minimal estimated helper
set and otherwise agent/tool operations. Recipes must name the actual script
and applicable step; agents use it when suitable. No Python version pin, external
library, provider SDK, persistent process, personal computer or coding CLI is
selected. No supplier probe or functional execution is authorized.

### Minimal helpers and record-framework deferral, 2026-09-15

The user said to assume small standard-library Python routines, begin with the
minimal useful code set and leave all other work with agents/tools, with actual
scripts mentioned in the instructions. The user also said to keep “open dependency
records and ordinary save” outside MVP. Adopt both directions explicitly.

The initial bounded code deliverable is
[`helpers/source_metadata.py`](../../../helpers/source_metadata.py), with
subject normalization, normalization of reliably extracted address parts, and
UTF-8 text-size measurement. It implements mechanical pieces of approved rules;
it does not match emails, infer dates, define persisted records, write Drive,
schedule batches or repair writes. Its [guide](../../../helpers/README.md) and
[prepared checks](../../../helpers/prepared_checks/check_source_metadata.py)
are part of the authored deliverable. They are unexecuted and unqualified.

The agent follows the recipes for discovery, content interpretation, tasks,
Drive saves/readback and effects. Existing approved data meanings and persistence
verification remain; the separate record/schema/ordinary-save framework is not
an MVP feature or prerequisite. This does not permit silently adopting a new
schema, UUID/locator scheme or persistence engine. Address only a specific new
architecture need if retained implementation exposes one.

Independent approved preparation includes fictional lifecycle scenarios, a
[proposed testing sequence](implementation/TESTING-PROPOSAL.md), and a new
[development-only metadata model](identity/revised-model/README.md) in a separate
directory. Its code and fictional checks are authored, not executed. These are not a
replacement runtime, canonical schema or managed-agent qualification. Every
functional test, model run, simulation, build and live operation remains stopped.

### User-approved MVP revisions, 2026-09-15

After the detailed review, the user explicitly directed:

- **D4:** reject a School-OS-managed partial run and its fixed 25-processing,
  100-listing and 8 MiB application ceilings. One logical run must process all
  relevant unread mail. The capable executing agent owns adaptive resource use,
  batching, continuation and its own runtime recovery, with School-OS advice and
  guidance. School-OS does not implement/manage that batching. D1 bounded data
  access, source custody, honest coverage and source-metadata identity remain.
  The user relies on normal agent continuity; full environment-reset recovery
  and School-OS canonical-write repair are not MVP guarantees. This is an explicit
  MVP qualification of the broader fresh-agent recovery direction, not a new
  dependence on chat/provider handles as canonical identity or completion proof.
- **D5:** “Regarding D5, I approve the plan.” Adopt the complete D5 proposal as
  presented in revision 6: source-linked claims and evidence-based relationships,
  finite/conditional/recurring actions with the 14-day projection fallback,
  separate parent planning/completion, and field-level three-way task sync.
  The separate record/save framework is now deferred. Preserve approved meanings
  through agent instructions; do not ask for D5 behavior approval again.
- **D6:** the executing agent assesses its available means and validates uncertain
  external actions with its authorized connectors/APIs. Do not select the former
  general School-OS persisted-effect engine. First validate that all intended
  mail/content is ingested, then create the daily brief. A real blocker remains
  an incomplete operation and must be reported; a partial normal daily brief
  cannot substitute for the required completed ingestion. The approved qualified
  knowledge-query rule remains separate. Selection by verification time, audio
  retention/order and specific new output meanings are not blanket-approved;
  no record/save framework is an MVP prerequisite.
- **D7:** remove the centralized tools/capability/jobs register, scheduler control,
  binding manager and register-backed known-job/sender queries from the MVP.
  Users and agents manage their own jobs, read recipes and select needed adapters.
  Assume no concurrent operation on the same Drive data; do not add locks or a
  replacement scheduler. Operation configuration/capability needs remain required.
- **D8:** defer packaged installation and upgrade/compatibility/migration machinery.
  Keep the project ready for later lifecycle work using approved D1 separation of
  system, instance and extensions; do not adopt another package/activation design.
  Usable Drive startup/configuration remains necessary through agent instructions
  following approved D1; any new architecture still needs a specific decision. Repository preservation/cleanup continuity
  and the testing stop remain required.

These directions explicitly reduce the original whole-project MVP scope,
particularly the tools/schedules/visibility and packaged-lifecycle core use cases.
The broader product principles remain unchanged. Do not claim full original
T1–T10/U1–U7 delivery when the deferred areas are absent. The
[coverage map](implementation/COVERAGE.md) separates retained and deferred work.

The [agent execution guidance](implementation/AGENT-EXECUTION-GUIDANCE.md) and
[updated briefs](implementation/decision-briefs/README.md) describe these boundaries.
They are authored instructions and review artifacts, not executed validation.

**Pending daily boundary:** recommend all relevant school mail not yet fully
processed by School-OS through run start, including backlog and attachments, even
if already marked read in the mailbox; later arrivals belong to the next run.
The coordinator asked for explicit approval. This defines a finite snapshot
without chasing new arrivals forever; a later cutoff captures more arrivals but
can extend work. No answer is recorded yet. This interpretation/cutoff must not
be adopted silently. Remaining D4 precision/search/repeated-appearance details,
D6 audio/manual limited-brief and specific remaining architecture choices remain pending.
D3’s minimal Python/agent split is approved; the record/save framework is deferred. Existing source-metadata and coverage invariants remain authoritative.

Exact next action: resolve the finite daily scope/cutoff and those remaining
MVP choices with the user, without rebuilding deferred infrastructure or
reopening the excluded record/save framework. Continue approved helper and
instruction work independently; do not execute it.
Implement approved retained deliverables and prepare their unexecuted checks.
Commit/push the agreed MVP code and continuity, verify the exact remote revision,
then stop for the user's testing direction. This architecture/document update is
not the completed code handoff or authorization to test.

## Decision authority and user checkpoints

### Approved setup interview and shared tool adapters, 2026-09-15

The user confirmed the coordinator's restatement and directed the relevant
changes. Adopt the following architecture, without asking for this approval again:

- First setup interviews the parent about the task tool they want. Offer known
  options available to that executing agent, explaining relevant capability and
  access limits rather than presenting a fixed universal list or silently
  selecting a tool. Reuse prior explicit choices instead of repeating questions.
- One shared School-OS adapter per external tool maps School-OS meanings and
  procedures to the tool's own concepts. Its logic is independent of agent,
  connector, API implementation, SDK, authentication and transport mechanics.
- Each agent uses its own authorized connector to execute the required tool
  operations. A missing operation remains an explicit limitation; authoring an
  adapter does not create an unavailable connector or capability.
- If the chosen tool is accessible but lacks a School-OS mapping, the agent can
  author a conformant adapter. This is authorized within existing meanings;
  genuinely new architecture still needs explicit approval. Do not require a
  separate approval merely because a new tool mapping is being authored.
- Keep the adapter discoverable in the shared Drive instance, using approved D1
  separation for supplied system material and user-created extensions. A second
  agent accessing that tool reuses the same semantic mapping through its own
  connector. Do not fork the adapter per agent or introduce a D7-style register.

The authored [operation instructions](../../../operations/README.md),
[setup interview](../../../operations/setup.md),
[adapter creation/reuse procedure](../../../operations/tool-adapters.md) and
[adapter authoring template](../../../operations/tool-adapter-template.md)
implement the instruction portion of this direction. They have not been run.
No concrete vendor mapping, source access, task write or compatibility
qualification is established by their existence.

This supersedes earlier current-document wording that conflated an adapter with
an agent/runtime/API wrapper. Retired `core/contracts/adapters.md` and runtime
adapter files remain historical evidence, not a foundation. Applicable privacy,
response-evidence and unknown-effect safeguards still govern connector handling.
The [architecture walkthrough](implementation/architecture-in-practice.html)
now explains the approved storage layout in detail and traces each scenario's
reads and writes. Explanatory JSON labels are illustrative, not adoption of the
deferred record framework or a new persisted field schema.

The [product principles](../../product-principles.md#decision-authority) are the
source of truth for product/design decisions and the grounding for any decision
not explicitly covered by an approved specification. Direct user instructions
take precedence. Old code, historical plans and tool defaults are evidence, not
authority to fill a gap with a new requirement.

Every new or changed architecture decision requires explicit user approval
before adoption or implementation. Present a concrete proposal with its
principle/use-case grounding, alternatives, tradeoffs and unknowns, then record
the decision and the user's explicit approval in this plan. Principles compliance
does not itself grant approval. Existing explicit approvals remain valid;
routine nonarchitectural implementation choices may proceed within their scope.
Continue independent approved work while an architectural choice is pending.

The next coordinator's implementation phase ends when the agreed new project
code and continuity documents are committed, pushed and the remote revision
verified. **Stop there and check in with the user.** The user personally manages
and oversees the testing phase. Do not execute tests, simulations, replay
experiments, connector probes, pilots, ingestion or schedules before the user's
subsequent direction. Preparing test code, fictional fixtures and a proposed
testing sequence is allowed; executing them is not. Publication hygiene (diff,
privacy, document-link, Git status and remote-revision checks) remains required.
Report the code as implemented but untested, with no qualification claim.
Inspect applicable hooks and CI before publishing the new code. Do not trigger
testing indirectly or silently disable checks; bring any conflict between
publication and the reserved testing phase to the user before proceeding.

These checkpoints supersede older automatic transitions into experiments,
managed-agent pilots or release qualification. The
[copyable Astra handoff](ASTRA-HANDOFF.md) carries the same boundaries.

## Approved architecture and operating choices

Read the broader baseline below subject to the explicit current MVP revisions
above. In particular, the tools/jobs register and packaged lifecycle are deferred;
resource batching belongs to the executing agent, and D2 repair is excluded.

- Google Drive holds the instance's instructions/configuration, processed
  knowledge and tasks, source/attachment index and coverage, unfinished work,
  and tools/jobs/runs register. The physical layout is now approved in
  [D1](implementation/ARCHITECTURE-PROPOSAL.md#d1--physical-drive-layout-and-bounded-access):
  multiple bounded JSON pages and paged directories under a readable bootstrap
  and the `system`, `instance`, and `extensions` areas. Qualification of actual
  storage adapters belongs to the user-directed testing phase.
- Raw emails and attachments remain in their source systems. Temporary downloads
  support processing and are discarded after verified persistence. Startup and
  routine work read relevant records in bounded units as history grows.
- Agents use simple adapters for available tools and reason over explicit source
  metadata and operating procedures. No required permanent provider ID, token,
  prior conversation, dedicated personal machine or coding CLI is introduced.
- Catalog logical emails. Reuse a record when the sufficiently supported
  normalized metadata recipe agrees without contradictory evidence. Different
  provider entries or repeated appearances alone neither require duplicate
  records nor prove a product failure. Preserve distinctions supported by source
  metadata and unresolved mappings; do not silently merge existing catalog data.
- Normalize address presentation, domain case and recipient ordering; preserve
  local-part spelling and To/Cc roles. Decode/unfold subjects and trim outer
  whitespace while retaining original observations and meaningful subject text.
- Use each individual message's original Date as the primary identity timestamp,
  preserving meaning, zone and precision. Obtain a richer metadata view for an
  unclear search time. Received and internal timestamps cannot silently replace
  that Date. Thread grouping remains optional navigation; every reply has its
  own record, attachments and processing coverage.
- Bind attachment records to their parent logical email. Parent ID plus original
  filename locates a candidate or same-parent candidate group. Preserve relevant
  candidates and coverage; different retrieval handles do not prove different
  documents, and filename agreement does not mark unread material processed.
- Enumerate bounded search windows through all available continuation pages,
  including after short pages. Persist completed windows and unfinished work on
  Drive independently of content-processing status. A fresh agent can repeat an
  unfinished window without a saved pagination token or local state.
- Allow any number of agents and registered jobs. Record each job's purpose,
  executing agent, scheduler location, selected adapters, input/output scope and
  last verified status, plus run/output attribution. Any capable agent reading
  Drive can answer which known jobs exist and who generated a brief. Concurrent
  updates to the same Drive data remain outside scope.

## Whole-project implementation scope

This original whole-product checklist is retained for traceability. The current
MVP implements only its retained areas under the explicit D2/D7/D8 deferrals and
D4/D6 agent-led direction above; it must not be represented as all delivered.

The restart covers the complete reusable School-OS project described by the
product principles and core use cases. Email identity is one component, with the
most recently refined procedure; completing its development model alone does
not complete the restart. The earlier wording "agreed initial project-code
scope" did not enumerate that full scope and must not be used to narrow it.

The [current MVP revisions](#user-approved-mvp-revisions-2026-09-15) and
[D2 exception](#user-approved-mvp-exception--interrupted-writes) remove central
D7 management, D8 lifecycle machinery and interrupted canonical-write repair from
current delivery. The original checklist below is traceability, not a direction
to implement those deferred mechanisms. The coverage map states the retained work.

The following is a delivery checklist drawn from existing requirements, not
approval of new schemas, storage layouts, contracts or runtime mechanisms.

| Area | Required coverage in the new project |
|---|---|
| Installation and startup | User-supplied package, Drive entry point, instance configuration, source/scope selection and discovery of the current agent's capabilities. |
| Canonical data and source custody | Processed knowledge, tasks, source/attachment references, coverage and unfinished work on Drive; bounded access and temporary raw processing with verified persistence before cleanup. |
| Historical and daily ingestion | Bounded enumeration and continuation, the current logical-email/attachment recipe, individual replies, content extraction, explicit unread/unsupported material, and independent historical/daily progress. |
| Knowledge and queries | Substantive facts, qualifications, instructions, corrections, deadlines and provenance; queries from a fresh capable agent with honest missing-evidence and source-access limits. |
| Tasks and synchronization | Canonical actionable requests and parent task state, with synchronization to the selected task application when configured. |
| Briefs and delivery | Recent-update and daily email briefs, optional audio when supported, and run/output attribution using the canonical knowledge and tasks. |
| Tools, adapters and schedules | Known connections and capabilities, selected adapters per operation/job, scheduler locations, desired versus observed settings, verification freshness, and known-job/sender queries. |
| Continuation and agent replacement | Durable bounded discovery/window progress and fresh-agent access without previous conversations, local files or mandatory provider tokens; explicit missing capabilities/coverage. Interrupted canonical-write repair/resumption is deferred outside MVP. |
| Extensions and upgrades | New applications and compatible adapters can use the canonical data layer; package/update procedures preserve private data, configuration and compatible customizations. |
| Development and portability | Clear agent instructions and simple supporting code/adapters for limited managed/cloud environments; useful failure evidence retained without rebuilding the retired machinery by default. |

Before dependent implementation, reconcile every product principle and core use
case with its existing design, intended deliverables and any unresolved
architectural approval. Record implemented/prepared status and later testing
status separately. The historical lifecycle simulation supplies scenarios and
evidence; its superseded identity rules and unapproved mechanisms are not a
production specification.

Bring missing architecture decisions to the user rather than guessing. Report
any capability blocker or proposed scope reduction explicitly; do not silently
defer a core use case or present an isolated model as the finished project.
An intermediate implementation slice may support development velocity, but it
does not redefine the final code handoff unless the user explicitly agrees.
All test execution remains in the user-directed phase. Placing live scheduling,
Drive operations or upgrade checks there does not defer their required project
instructions/code out of the implementation scope.

## Corrected interpretation of the live study

The [study](identity/metadata-stress/README.md) made 127 read-only calls covering
632 Gmail entries, with individual header reads for 92 and 17 independent repeat
reads. Its matching pair may represent one logical email. The 92-entry/91-record
replay disagreed with a provider-entry grading reference; it did not establish
lost school information or a product false positive. Requiring a School-OS record
per provider entry was stronger than the product objective.

Repeated filenames occurred within 42 individual parent emails and may include
alternate representations. Address handling was repaired in the study; subject
trimming is now approved but absent from the frozen evaluator. All compared
timestamps agreed; unknown search-time semantics and injected rounding remain
capability/test questions, not observed timestamp changes. Thread-grouping
disagreement is not an ingestion failure. Short pages with continuation provide
the concrete enumeration lesson.

The original code, receipts and JSON counts remain unchanged. Read the corrected
report before interpreting `wrong_association` or the earlier pass/failure totals.

## Implementation phase: stop before testing

- [x] Reconcile product principles, current recipe, test interpretation and
  artifact authority with the approved decisions.
- [x] Reconcile the whole-project delivery checklist above against every product
  principle and core use case, retaining existing approvals and identifying
  precise unresolved architecture choices for the user.
- [x] Prepare a [small development model in a new revision](identity/revised-model/README.md), preserving the frozen
  study. Cover repeated observations of one logical email, contradictory source
  metadata, normalizable subjects/addresses, each reply's own Date, same-parent
  attachment groups and interrupted window replay. Supply independent logical
  labels for fictional cases; leave unknown live logical relationships ungraded
  rather than assuming provider-entry differences are product errors. Report
  residual indistinguishability honestly without adding content-based identity.
  Code/checks are authored only; no model or test execution occurred. Its limited
  Date fixture domain does not approve the production threshold in D4.
- [ ] Implement the whole-project delivery scope above with the explicit MVP
  interrupted-write-recovery exception, under the approved
  architecture. Obtain approval for unresolved architectural choices before
  their dependent code; do not silently decide the Drive file/table layout.
  Prepare a proposed test inventory and fixtures without running them.
- [ ] Publish the agreed code and updated continuity documents. Report the
  exact revision, coverage of every deliverable, pending decisions, known risks, tests not
  run and proposed testing sequence. Stop and await the user's direction.

## User-directed testing phase: not authorized to start automatically

The following is a proposed qualification backlog, not permission to execute it.
The user selects the scope, order, environment and timing. Include the revised
model's fictional cases above in that testing plan. Test evidence may motivate
architecture changes, but those changes still require explicit user approval.

- [ ] Prove one bounded historical-to-daily slice in an actual managed agent:
  discover individual messages and original Dates, normalize/index them, read
  source content and relevant attachments temporarily, persist knowledge/tasks
  and coverage to Drive, verify readback and discard temporary material. Measure
  startup/read/write cost for the user-approved layout; propose any architectural
  revision for approval before changing it. Explicitly retain unsupported or
  incomplete items.
- [ ] Exercise interruption and continuation through Drive: completed windows,
  unfinished enumeration, pending content, and a lost/expired pagination token.
  Repeat the unfinished window without duplicating already associated logical
  records or inheriting another attachment candidate's completion status.
- [ ] Register and exercise a daily catalog job in a supported managed scheduler.
  Save its location, agent, adapters, scope, last verification and run attribution.
  A saved registration alone must not be treated as proof an external job exists.
- [ ] Start a fresh session in a second managed agent using the Drive instance.
  Query existing school information and known jobs, resume unfinished work, and
  catalog a later reply. The previous conversation, local files and provider
  pagination token are unavailable. Preserve existing job bindings and attribution.
- [ ] Check the slice against every product principle and core use case, then
  expand supported adapters from observed capabilities. Qualify task-sync/brief
  applications on the same canonical state; record unsupported routes and limits.

Within the phase the user has authorized, advance through one reviewable slice
at a time. Reuse evidence, fix demonstrated
problems at the smallest responsible boundary, and measure tool calls, approvals,
elapsed work and recovery effort. Do not rebuild the retired runtime, develop
parallel storage engines or require every vendor to pass before learning from the
first slice. This plan does not initiate live writes, migrations or scheduled jobs.

## Remaining limits

Metadata cannot prove unique physical delivery or equal content. The accepted
policy tolerates indistinguishable logical-email candidates without a record per
provider handle. Exact attachment mapping inside same-name groups, unsupported
inline content, complete discovery through capped tools, actual Drive operations,
managed scheduling, handoff and sustained capacity still need qualification.
Incomplete work stays visible and scoped; none of these unknowns justify an
automatic content/provider-ID fallback or an unbounded retry loop.

## Historical raw-MIME evaluation

The 38-case prepared-observation experiment did not parse raw email or establish
false-positive/negative rates. The user explicitly requested checking the new
recipe's robustness and determinism for threads, attachments and HTML images.

- [x] Generate independently labeled fictional raw MIME with presentation
  variants, replies, attachments, CID/data/remote images and incomplete views.
- [x] Evaluate the existing recipe against those observations; report incorrect
  associations, false splits and abstentions separately, with denominators.
- [x] Check repeated execution, catalog/input order and uncertainty handling.
- [x] Document failures, proposed mitigations and remaining live qualification;
  validate and publish this development analysis without changing the runtime.

The former next step of repairing content/MIME matching is superseded by the
metadata-only design above. Keep the old failing matcher and its results
reproducible as historical evidence.

## Earlier message-identity research

The user challenged the assumption that a provider message ID can be the
canonical source key and explicitly requested a quick sub-agent Gmail test,
deep research across agent/harness surfaces, and a provider-ID-independent
identification design wherever guarantees are absent or uncertain.

- [x] Run a bounded read-only test of existing messages and individual replies,
  preserving private receipts before interpretation and publishing only counts.
- [x] Separate provider contracts, sender-created mail headers, connector
  handles, thread IDs and agent-tool references in primary-source research.
- [x] Design durable School-OS-owned identities with multiple optional matching
  witnesses, conservative ambiguity handling and no mandatory raw archive.
  The subsequent explicit product principle makes source information the sole
  basis for identity/acceptance decisions; external identifiers are access aids.
- [x] Exercise missing/changing IDs, replies, reformatting and indistinguishable
  duplicate cases in a small synthetic experiment.
- [x] Update design authority and continuity and validate the accepted changes.
  Apply the repository commit/push procedure and verify the remote revision
  before reporting the handoff complete.

## Authority and scope

The user retired the previous implementation as the foundation for a restart.
The current product authority is `docs/product-principles.md`, including the
explicitly requested source-residency, tool/job inventory, unrestricted agent
choice and deferred concurrent-write policies. This work updates design documentation and preserves prior synthetic and bounded
read-only metadata evidence. It does not modify the installed
runtime, migrate a private instance, create schedules, send messages or publish
a release.

Earlier recovery and release plans remain historical evidence. They do not
require this design exercise to rebuild a package or create a live test root.
The restart is not backward-compatible by implication: future runtime and
migration work must implement the new principles explicitly rather than claim
that the old runtime already conforms.

## Work units

- [x] Update product principles with the authorized operating choices.
- [x] Build fictional communications and independent semantic expectations.
- [x] Simulate setup, historical ingestion, interruption, daily cataloging,
  scheduling, another agent's queries, job inventory, attribution and switching.
- [x] Exercise detailed message, reply, thread and attachment identities.
- [x] Preserve system-state snapshots and test results; distinguish modeled
  outcomes from real connector/model capabilities.
- [x] Review failures against primary documentation for managed/cloud agents.
- [x] Document conclusions, remaining capability tests and scope exclusions.
- [x] Run appropriate repository checks and privacy checks. Publish the accepted
  files through the repository continuity procedure; verify the remote revision
  before reporting this handoff complete.

## Simulation boundaries

The original lifecycle Python exercise is a development analysis instrument, not
a School-OS runtime or a dependency that a parent or agent must install. Its
communications, accounts, jobs and effects are fictional; the separate Gmail
study uses private read-only observations. Supplied semantic expectations model
correct interpretation; successful model execution cannot certify an LLM's
ability to discover those facts or a real connector's fidelity.

The production target is a managed/cloud agent application with Drive access,
not a dedicated personal computer running a coding CLI. Tool support,
authentication, approvals, temporary storage and scheduled execution must be
qualified on the actual app. Unknown capabilities remain explicit.

Multiple agents and jobs are supported. Simultaneous updates to the same Drive
data are excluded from the current scope; this simulation must not add locks,
leases, fencing or a conflict-resolution engine to address that edge case.
