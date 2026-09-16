# Whole-project restart coverage

Updated 2026-09-15 from the [product principles](../../../product-principles.md),
[active plan](../PLAN.md), [metadata recipe](../identity/METADATA-RECIPE.md) and
[historical lifecycle scenarios](../SIMULATION.md). The lifecycle model's
mechanisms and old runtime do not supply missing architecture approvals.

The [consolidated question list](OPEN-QUESTIONS.md) covers known remaining choices.
Q1 and Q2 expose concrete retained-data and lookup gaps, not a requirement for
D2's excluded generic framework. Q6 still lacks the exact read-reuse evidence
rule. Those three need detailed proposals before final approval. The other six
recommendations remain unapproved. Publication of this review is documentation,
not a complete MVP handoff or functional qualification.

Status: requirements mapped; D1, the
[query-coverage rule](ARCHITECTURE-PROPOSAL.md#approved-query-coverage-rule),
D3 code-execution capability, **small Python standard-library routines and a
minimal reusable helper set**, and **D5 in full** are approved. On 2026-09-15 the
user also approved the setup interview and **one shared semantic adapter per
tool**, reusable across agents with tool access; the current agent's connector
owns APIs, authentication, SDKs and transport. An accessible tool's missing
School-OS mapping may be authored within approved meanings. Recipes point to
the actual scripts; the agent and its tools perform the remaining work. The
user also approved **“Completion detected — awaiting parent confirmation”** for
clear evidence satisfying a specific unfinished task. Candidates remain
uncompleted in a supported task-tool status or section until the parent checks
them off; D5 sync then reconciles completed state. This is an approved retained
feature, not another pending architecture decision. Users and agents may create
and choose any number of brief recipes. The starter's newly verified/corrected
selection, original dates, relevant open tasks and failed task-sync disclosure
are approved as template behavior, not a universal brief policy. The
separate records/ordinary-save framework is now outside MVP, alongside the
earlier exclusions below; it is not an approval gate for MVP coding. D4's
remaining cutoff/identity choices and D6's manual incomplete-brief exception/audio choices are
still pending. New architecture cannot be invented through generic delegation.
Supplier capability availability is user-reported, not independently qualified.
Helper and operation-instruction authoring are separate from whole-project
implementation, vendor qualification and testing.

## Current execution direction and explicit MVP exclusions

The [active plan](../PLAN.md) governs these explicit changes; the long-term
product principles remain unchanged. The original whole-project checklist must
not be reported fully delivered without naming the exclusions.

| Decision | Current scope |
|---|---|
| D2 | Interrupted canonical-write repair remains outside MVP. The separate records/ordinary-save framework and its prerequisite review are also deferred: do not introduce a schema/write engine or reinstate that gate. Canonical Drive data, D1/D5 meanings, normal agent verification, coverage and cleanup remain required. |
| D3 helpers | Small Python standard-library routines and a minimal reusable helper set are approved. Recipes refer to actual scripts; the agent/tools handle the rest. Extra dependencies, new runtime mechanisms or new canonical architecture are not approved by implication. |
| D3 setup/adapters | Setup interviews the parent about their task-tool choice and explains known options available to the current agent. Reuse one shared, API-independent School-OS semantic mapping per tool; author a missing mapping when the tool is accessible. Agent connectors own API/authentication/SDK/transport. New architectural choices still need specific approval. |
| D4 | One logical ingestion run completes all relevant unprocessed mail in its authorized scope. The actual agent manages adaptive resource chunks and resource recovery using School-OS guidance. Former School-OS per-run caps and batch/continuation scheduling are rejected. Remaining identity/discovery/content policy choices are not blanket-approved. |
| D5 | Approved in full: substantive claims and relationships; parent fields and state; finite/recurring tasks; native recurrence or a 14-day occurrence fallback; three-way reconciliation and missing projections. Added 2026-09-15: clear task-satisfying evidence enters “Completion detected — awaiting parent confirmation”; the parent checks off reviewed candidates, then D5 sync completes Drive/app state. No automatic closure, downgrade of completed tasks or extra approval gate for this state. Preserve meanings without the deferred records/save framework. |
| D6 | The agent validates uncertain actions using its available authorized means. Complete ingestion is required before an ordinary daily brief. Users and agents may create and choose any number of brief recipes. The approved starter selects newly verified/corrected information, shows original dates and relevant open tasks, and discloses failed task sync while using verified canonical state. This is template behavior, not universal selection policy. The manual incomplete-brief exception and audio remain pending; no recipe registry or fixed effect engine is inferred. |
| D7 | Centralized tools/jobs/capabilities register and scheduling control are outside MVP. Users and agents own nonconcurrent scheduling and select adapters from recipes. No replacement School-OS scheduler or registry is introduced. |
| D8 | Package installer, upgrades, compatibility and migrations are deferred. D1's approved system/instance/extensions separation preserves room for future support; it is not proof of upgrade capability. First-use agent instructions follow approved D1; new architecture still requires approval. |

Bounded D1 pages and narrow storage access remain approved; their per-page
limits are not a cap on the total mail processed by a logical run. Actual
resource/authorization limits remain real: if the agent cannot finish, it must
show incomplete coverage and a blocked outcome rather than claim success or
silently schedule a School-OS batch. Agent resource recovery does not promise
the deferred repair of interrupted canonical writes.

The approved query rule still permits a limited answer to a question, with
coverage disclosed. That permission does not override the new complete-ingestion
gate for an ordinary daily brief. Raw-source custody and normal verified
persistence/cleanup remain required throughout.

Deferring a framework does not defer substantive knowledge, tasks, provenance,
coverage or their normal save/readback. Routine implementation within the
approved meanings may proceed. A proposed new canonical meaning, adapter
contract or architecture still requires explicit approval; it must not be
introduced as a substitute framework under a different name.

## Minimal helper authoring checkpoint

The approved helper-authoring work is limited to
[helpers/source_metadata.py](../../../../helpers/source_metadata.py):
`normalize_subject`, `normalize_address_parts` for already extracted address
parts, and `utf8_size`. The associated
[prepared checks](../../../../helpers/prepared_checks/check_source_metadata.py)
are authored for later user-directed execution. No check has run.

These are mechanical helpers, not a complete address parser, identity matcher,
Drive persistence engine, ingestion runtime or school-information application.
Recipes must identify the real script and the agent/tool work surrounding it.
Their authoring does not complete T1–T10 or qualify a managed environment.

## Setup and shared-adapter instruction checkpoint

The authored operation instructions are
[operations/README.md](../../../../operations/README.md),
[setup.md](../../../../operations/setup.md),
[tool-adapters.md](../../../../operations/tool-adapters.md) and
[tool-adapter-template.md](../../../../operations/tool-adapter-template.md).
They cover the parent interview, currently available tool options, selection,
reuse and authoring of a missing shared semantic mapping. A replacement agent
with authorized access to the same tool reuses the same School-OS mapping while
using its own connector implementation.

This is the approved setup/adapter direction expressed as instructions and a
template. It is not an installed instance, an implemented task-sync operation,
a supplied qualified vendor adapter, or a claim that any current connector can
carry out the whole operation. No registry, installer, record schema, generic
write engine or API wrapper is added. D7/D8 deferrals remain explicit.

## Completion-review instruction checkpoint

The [completion-review operation](../../../../operations/completion-review.md)
expresses the approved confirmation-pending behavior. It retains clear evidence
for the specific task, with source references and independent content coverage,
and uses the shared task adapter's supported custom status or section to keep
candidates visibly separate from completed tasks. The parent may review and
check off a group together; ordinary approved D5 reconciliation then saves and
verifies completed state. Existing parent completion must not be downgraded.

This authored instruction is retained MVP work, not a deferred feature or a new
approval gate. It is unexecuted, and no actual task tool or detection accuracy is
qualified. Future automatic closure is only a possibility after later review;
no fixed accuracy threshold or automatic promotion is approved. Sent-mail source
scope is not expanded by this direction. The remaining full synchronization and
ingestion implementation, and the user-controlled testing phase, are separate.

## Brief-recipe instruction checkpoint

The [brief-recipe instructions](../../../../operations/brief-recipes.md) express
the approved extensibility: users and agents may create any number of recipes
and choose or adopt whichever they want. The daily starter selects newly verified
or substantively corrected information for the reporting interval, keeps original
school dates visible, includes relevant open tasks and discloses failed task sync
without pretending that current app state is known. Confirmation-pending tasks
remain distinct from completed tasks. The starter's selection is not a fixed
policy imposed on every recipe.

All recipes preserve source accuracy, qualifications and truthful coverage.
The complete-ingestion gate still applies to the ordinary daily brief. The
museum-notice/unread-newsletter story in the [D6 brief](decision-briefs/D6-BRIEFS-EFFECTS.md#the-manual-incomplete-brief-exception-is-still-a-proposal)
explains a proposed explicit parent-request exception; it does not approve that
exception. Audio policy also remains pending. The authored guidance introduces
no recipe schema, registry, precedence or scheduling mechanism and has not been
executed. It is a subset of the required delivery implementation.

## Deliverables and approval dependencies

The checkpoint sections identify authored files. Other deliverables below remain
required work, not assertions that they exist or approval of the mechanisms they
would contain. A path/name choice is routine; any new canonical meaning,
dependency or runtime behavior still needs approval.

| ID / required area | Existing approved design | Concrete new deliverables | Dependencies | Implementation / testing |
|---|---|---|---|---|
| T1 Setup/startup | D1 entry point/separated areas; code-capable agents; approved parent interview, available tool choices and shared adapter reuse | `operations/README.md` and `setup.md`; agent establishes task-tool choice/access, uses or authors a mapping, and follows D1 startup/configuration instructions | Setup/shared semantic adapter direction approved, 2026-09-15; no records-framework gate or new installer/registry | Setup/adapter instructions authored; complete usable startup implementation remains pending; D8 package installer deferred / not run |
| T2 Canonical data/custody | Canonical Drive knowledge/tasks/indexes/coverage; originals at source; normal verified saves | Agent instructions preserving D1/D5 meanings, bounded pages, normal verification and temporary cleanup; `utf8_size` supports byte accounting | D1/D5/helpers approved; specific retained field/link proposal Q1 still owed; framework explicitly deferred; no substitute write engine | Helper authoring only; full operation pending / not run |
| T3 Historical/daily ingestion | Metadata recipe and separate coverage; one logical run with agent-managed resource work | Subject/address-parts helpers; import/daily/content recipes; source adapters and blocker guidance | Approved recipe/mechanical helpers; remaining D4 cutoff/identity choices pending | Isolated model and minimal helper authoring; full ingestion pending / not run |
| T4 Knowledge/queries | D5 claims/relationships; query coverage checks and limited answers | Extraction/query recipes; agent-led retrieval/save/verification under approved meanings | D1/D5/query rule approved; no records/save-framework prerequisite | Concrete Q1/Q2 examples still owed; full operation pending / not run |
| T5 Tasks/synchronization | D5 tasks, parent fields, recurrence and three-way reconciliation; one shared tool mapping; clear task-satisfying evidence requires parent confirmation before completion | `operations/tool-adapters.md`, `tool-adapter-template.md` and `completion-review.md`; separate uncompleted candidates in supported status/section; parent checks reviewed tasks off; full reconciliation/sync recipes still required | D5, semantic-adapter reuse/authoring and confirmation-pending behavior approved; no extra state/schema approval gate; automatic closure and new source scope are not approved | Mapping/template and completion-review instructions authored; full sync operation and actual vendor mappings not delivered or qualified; detection accuracy unestablished / not run |
| T6 Briefs/delivery | Complete ingestion before ordinary daily brief; agent checks uncertain effects; users/agents create and choose any number of recipes; approved starter selection and failed-sync disclosure | `operations/brief-recipes.md`; starter uses newly verified/corrected knowledge, original dates and relevant open tasks with task-state distinctions; remaining delivery/audio instructions and honest outcomes/attribution | Gate/verification, recipe extensibility and starter behavior approved; manual incomplete-brief exception and audio pending; no recipe framework/registry | Brief-recipe guidance authored; full delivery implementation incomplete and unqualified / not run |
| T7 Tools/schedules | Approved setup choice and cross-agent reuse of per-tool semantic mappings; users/agents own nonconcurrent scheduling | `operations/setup.md` and `tool-adapters.md` guide tool choice and mapping reuse/authoring; connectors supply actual access | Setup/adapter architecture approved separately from helpers; D7 central register/control remains excluded | Selection/reuse instructions authored; no qualified vendor coverage claim; central register, control and known-job query deferred / not run |
| T8 Continuation/replacement | Saved source/content progress and fresh-agent access; agent owns resource recovery | Token-loss replay/missed-input/fresh-agent guidance; explicit blockers; no batch scheduler | Approved direction; remaining D4 choices pending; no records-framework gate | Pending; D2 canonical-write repair deferred / not run |
| T9 Extensions/upgrades | Approved D1 separation preserves future official/private/extension support | Preserve separated storage roles; canonical-data consumers remain possible | D1 approved; D8 installer/upgrade/compatibility/migration excluded from MVP | D8 capabilities deferred, not delivered / not run |
| T10 Development/portability | Code-capable agents; small stdlib Python routines; shared semantic tool guidance independent of each connector; private developer evidence | Minimal helpers and prepared checks; `operations/README.md`, setup/adapter guidance/template; actual script references, lifecycle scenarios, limits and continuity | Minimal helpers and setup/shared-adapter direction approved; new dependencies/architecture still require separate approval | Helpers/checks and instruction subset authored; actual vendor routes unqualified; whole-project implementation incomplete / not run |

## Every design priority

Decision references identify dependencies; the current-scope table above
controls what is approved, unresolved or explicitly outside MVP.

| Priority | Required deliverables | Concrete obligation carried into implementation | Approvals |
|---|---|---|---|
| P1 Losslessness and provenance | T2–T6, T8 | Keep substantive information and qualifications; preserve source support; expose unread/partial/unsupported/unavailable material; do not archive raw sources | D1–D6 |
| P2 Deterministic behavior | T1–T9 | Explicit procedures and mechanical helpers; normal agent verification and source-grounded relationships; no deferred repair/framework claim | Current approvals and explicit framework/D2/D7/D8 exclusions |
| P3 Simplicity | T1–T3, T7–T10 | Minimal helpers and agent-owned work; no schema/write engine, locks, central scheduler/register or concurrency subsystem | D1/helpers/execution direction approved; explicit exclusions |
| P4 Efficient execution | T1–T4, T6, T8 | Narrow startup/storage access; agent-adapted chunks within one logical run; former School-OS message/listing/transfer caps are not success boundaries | D1 and revised D4/D6 direction; remaining contracts pending |
| P5 Tool agnosticism | T1–T2, T5–T7, T9–T10 | One shared School-OS semantic mapping per tool preserves approved canonical meanings across agents; each connector owns API/authentication/SDK/transport and replaceable handles; no per-agent duplicate mapping or central bindings manager | D1/D5/helpers and setup/shared-adapter direction approved; remaining D6 choices and genuinely new architecture pending |
| P6 Capability-led portability | T1, T3, T5–T8, T10 | Interview uses options accessible to the current agent; a replacement agent reuses the same tool mapping but checks its own authorized route and limits; small stdlib helpers; no personal machine/daemon/CLI requirement | Code/helpers/execution and setup/adapter direction approved; mapping reuse does not establish actual connector or runtime qualification |
| P7 Extensibility from canonical data | T2, T4–T7, T9 | Same substantive claims/tasks/source links; any number of user/agent-created brief recipes may be chosen without changing data authority or hiding coverage; no recipe registry or deferred D7/D8 machinery introduced | D1/D5 and brief-recipe extensibility approved; genuinely new canonical architecture requires approval |
| P8 Extensible/upgradable instances | T1, T7, T9–T10 | Preserve approved D1 separation for future support; package installation/update/compatibility guarantees are explicitly not MVP claims | D1 approved; D8 deferred |
| P9 Independence from brittle technical details | T1–T3, T5–T8 | Source-metadata identity, owned IDs, durable windows, replaceable handles; no content/provider identity fallback | D1–D8 |

## Every core use case

| Use case | Implementation coverage | Evidence to prepare for later user-directed testing |
|---|---|---|
| U1 Catalog communications and substantive information | T2–T3, T8 | Complete logical ingestion across agent-managed resource work; historical/daily replies, attachments, qualifications, blockers and normal verified cleanup; S32 |
| U2 Query school information across history | T2, T4, T8 | Current/superseded facts; guidelines/deadlines; source access lost; unread material could matter; incomplete coverage lookup; scoped completion or qualified answer without false exhaustive/absence claims |
| U3 Query known jobs, agents, locations and brief sender | T6–T7 | Central known-job query deferred with D7; preserve supported output attribution without requiring a central register or deferred records framework |
| U4 Reconcile canonical tasks and synchronize selected app | T2, T5, T8 | Finite actions versus guidelines; source corrections; parent completion/plans; clear task-specific evidence becomes confirmation-pending, never directly completed; own source coverage; supported status/section; parent-reviewed group completion through D5 sync; no downgrade of existing completion; conflicts, missing projection, unknown write and replacement adapter. All later checks remain unexecuted. |
| U5 Recent/daily email and optional audio briefs | T4–T8 | Complete-ingestion gate and blocker reporting; S33; approved starter selection of newly verified/corrected information, original dates and relevant open tasks; honest failed-sync disclosure and pending/completed distinctions; arbitrary chosen recipes preserve accuracy/coverage; agent-validated uncertain outcomes. Manual incomplete-brief exception and audio remain pending; checks unexecuted. |
| U6 Add applications, automations, analyses and workflows | T2, T6–T7, T9–T10 | Any number of user/agent-authored brief recipes may be chosen from the same canonical data; no recipe registry or precedence added; user/agent scheduling remains external; D1 separation retained; package compatibility enforcement deferred |
| U7 Install/upgrade a supplied package | T1, T9–T10 | D8 package installer/upgrades/compatibility/migrations deferred; approved setup interview and shared-adapter instructions do not deliver packaged lifecycle support |

## Other mandatory principle sections

| Principle section | Requirements beyond the numbered priorities | Deliverables / approvals |
|---|---|---|
| Purpose | School-year and historical substantive data layer; applications are consumers, not its boundary | T2, T4; D1–D2, D5 |
| Decision authority | Explicit user approval of every new/changed architecture; existing approvals retained; surface contradictions | Active plan approval ledger; applies to D1–D8 and any later new choices |
| People and agent roles | Developer, instance operator and unknown runtime; one/two parents and multiple children; any number of agents/jobs; no same-data concurrent writes | T1, T7–T10; D1–D3, D7–D8 |
| Approved setup and adapter direction, 2026-09-15 | Interview the parent; explain currently accessible tool options; reuse or author a shared per-tool semantic mapping; agents use their own connector implementations without changing School-OS meaning | T1, T5, T7, T10; setup/shared-adapter architecture explicitly approved; instruction subset authored and untested |
| Approved completion review direction, 2026-09-15 | Clear evidence satisfying a specific task creates a confirmation-pending candidate; parent confirmation completes it through D5 sync; preserve evidence/coverage and already-completed state; no automatic promotion or Sent-scope expansion | T2, T4–T5; confirmation-pending direction explicitly approved; completion-review instructions authored and unexecuted |
| Approved brief recipe direction, 2026-09-15 | Any number of user/agent-created recipes can be chosen; approved starter selection/sync disclosure is not universal policy; preserve accurate sources/dates, honest coverage and task-state distinctions; ordinary daily ingestion gate remains | T4–T6, T10; recipe extensibility/starter approved; guidance authored and unexecuted; manual incomplete-brief exception/audio pending |
| Source and processing boundary | Source custody; temporary processing; complete substantive extraction; honest source deletion limits | T2–T4, T8; D1–D4 |
| Metadata meaning | Verified logical mailbox; observed plus normalized values; preserve local-part spelling, To/Cc roles and meaningful subject text; source Date meaning/zone/precision; no identity fallback | T2–T3; D2–D4; exact current recipe remains authoritative |
| Logical email/reply identity | Reuse supported logical metadata; provider-entry counts are not ground truth; each reply has its own Date and coverage; optional navigation grouping | T2–T3; D2–D4 |
| Attachment identity and coverage | Parent plus original filename; same-parent groups and unnamed/incomparable inventories; no position/handle/content identity; unread candidate cannot inherit completion | T2–T3, T8; D2–D4 |
| Bounded discovery | Persist scope and date semantics; follow continuation after short pages; unfinished-window replay without token; listing exhaustion independent of processing completeness | T2–T3, T8; D1–D4 |
| Tools/schedules/visibility | Long-term central visibility is not an MVP claim: D7 register/control excluded; user/agents schedule nonconcurrently and reuse selected semantic mappings through their own connectors; credentials remain outside canonical data | T6–T8; shared-adapter direction approved; D7 exclusion and remaining D6 choices |
| Release/instance lifecycle | Long-term supplied-package lifecycle retained in principles; D8 delivery deferred; D1 separated areas remain; approved setup interview and adapter-selection guidance authored | T1, T9–T10; D1/setup direction approved, D8 excluded |
| Compatibility posture | Runtime/vendor names are examples, not compatibility promises; exact route qualification is independent of prepared implementation | T1, T7, T10; D3, D7–D8 |

## Repository evidence and instruction conflicts

The session began with a clean tree on `codex/mvp-recovery` at
`39d752c364a1cf404e5a6fc5739148b7d35a6b35`, equal to the local remote-tracking
revision. Work remains in the current directory on `codex/restart-school-os`.
The annotated `restart-baseline-2026-09-14` tag preserves that committed baseline.
Local creation of the tag is not a claim that the tag has been published.

| Retired instruction or mechanism | Conflict / treatment |
|---|---|
| Old README and source-catalog contract permit/require raw source text | Current source custody retains raw material at its source; replace active instructions, preserve baseline history |
| Old Gmail/source catalog requires full raw MIME, inventories and hashes for identity/acceptance | Current metadata recipe controls association; content processing remains substantive, separate and coverage-aware |
| Old operation state requires immutable hash-chain generations and critical exact provider references | No carry-forward authority; D1–D2 propose a replacement for explicit approval |
| Old update/release contracts require conditional writes or coordinated writers | Same-data concurrency is excluded; do not rebuild this infrastructure |
| Old instruction-ownership document points to retired architecture as active invariant owner | Current product principles and approved restart plan govern |
| Historical simulation proposes a live pilot to select physical layout and includes a reproduction command | User approval precedes dependent implementation; all execution waits for the subsequent testing direction |
| Old AGENTS evidence rules call for replay/focused tests before rebuilding | Preserve the privacy/evidence safeguards; no replay/build/test is authorized now |
| Legacy release operation mandates full repository validation | Publication hygiene only in this phase; no full validator, package build or indirect test execution |

The frozen Gmail model, code/results and study interpretation stay unchanged.
Its provider-entry comparisons did not establish distinct logical-email loss.
The historical lifecycle simulation supplies scenarios, not current identity,
production storage or semantic-accuracy qualification.

## Publication and testing gate

Inspected local hooks: no configured `core.hooksPath`; only inactive sample hooks
in `.git/hooks`. The tracked workflow runs `scripts/validate.py` on pull requests,
pushes to `main`, and manual dispatch. That script builds/verifies packages and
executes tests, so it must not run now. Recheck hooks, final CI and remote PR state
before publishing. An ordinary push to a new restart branch without an open PR
does not match the inspected workflow triggers. Do not create a PR or dispatch
the workflow in this phase; do not silently disable checks.

The whole-code handoff requires every T1–T10 item accounted for with the explicit
D2/records-framework/D7/D8 exclusions and remaining D4/D6 decisions and any specific new architecture named,
accepted code committed/pushed, the exact remote commit verified, current
continuity documents and a clear **implemented but untested** report. This
preparation/approval checkpoint is not that handoff. Any blocked publication or
missing architectural approval is reported rather than replaced with testing.
