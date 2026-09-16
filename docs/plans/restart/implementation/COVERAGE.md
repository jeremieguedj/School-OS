# Whole-project restart coverage

Updated 2026-09-15 from the [product principles](../../../product-principles.md),
[active plan](../PLAN.md), [metadata recipe](../identity/METADATA-RECIPE.md) and
[historical lifecycle scenarios](../SIMULATION.md). The lifecycle model's
mechanisms and old runtime do not supply missing architecture approvals.

Status: requirements mapped; D1, the
[query-coverage rule](ARCHITECTURE-PROPOSAL.md#approved-query-coverage-rule),
D3 code-execution capability, **small Python standard-library routines and a
minimal reusable helper set**, and **D5 in full** are approved. Recipes point to
the actual scripts; the agent and its tools perform the remaining work. The
separate records/ordinary-save framework is now outside MVP, alongside the
earlier exclusions below; it is not an approval gate for MVP coding. D4's
remaining cutoff/identity choices and D6's remaining content/audio choices are
still pending. New architecture cannot be invented through generic delegation.
Supplier capability availability is user-reported, not independently qualified.
Helper authoring is separate from whole-project implementation and testing.

## Current execution direction and explicit MVP exclusions

The [active plan](../PLAN.md) governs these explicit changes; the long-term
product principles remain unchanged. The original whole-project checklist must
not be reported fully delivered without naming the exclusions.

| Decision | Current scope |
|---|---|
| D2 | Interrupted canonical-write repair remains outside MVP. The separate records/ordinary-save framework and its prerequisite review are also deferred: do not introduce a schema/write engine or reinstate that gate. Canonical Drive data, D1/D5 meanings, normal agent verification, coverage and cleanup remain required. |
| D3 helpers | Small Python standard-library routines and a minimal reusable helper set are approved. Recipes refer to actual scripts; the agent/tools handle the rest. Extra dependencies, new runtime mechanisms or new canonical architecture are not approved by implication. |
| D4 | One logical ingestion run completes all relevant unprocessed mail in its authorized scope. The actual agent manages adaptive resource chunks and resource recovery using School-OS guidance. Former School-OS per-run caps and batch/continuation scheduling are rejected. Remaining identity/discovery/content policy choices are not blanket-approved. |
| D5 | Approved in full: substantive claims and relationships; parent fields and state; finite/recurring tasks; native recurrence or a 14-day occurrence fallback; three-way reconciliation and missing projections. Preserve those meanings without requiring the deferred records/save framework. |
| D6 | The agent validates uncertain actions using its available authorized means. Complete ingestion is required before an ordinary daily brief. A blocked logical run reports the blocker, not a normal partial daily brief. Remaining recency/content/audio choices are not blanket-approved; no fixed School-OS intent/recovery engine is inferred. |
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

## Deliverables and approval dependencies

The paths below are intended new artifacts, not assertions that they exist or
approval of the mechanisms they would contain. A path/name choice is routine;
any new canonical meaning, dependency or runtime behavior still needs approval.

| ID / required area | Existing approved design | Concrete new deliverables | Dependencies | Implementation / testing |
|---|---|---|---|---|
| T1 Setup/startup | D1 entry point/separated areas; code-capable agents and configured source scope | Minimum setup/startup instructions; agent checks its capabilities; recipes point to supplied helpers | D1/code/helpers approved; setup instructions still to author; no records-framework gate | Pending; D8 package installer deferred / not run |
| T2 Canonical data/custody | Canonical Drive knowledge/tasks/indexes/coverage; originals at source; normal verified saves | Agent instructions preserving D1/D5 meanings, bounded pages, normal verification and temporary cleanup; `utf8_size` supports byte accounting | D1/D5/helpers approved; framework explicitly deferred; no substitute write engine | Helper authoring only; full operation pending / not run |
| T3 Historical/daily ingestion | Metadata recipe and separate coverage; one logical run with agent-managed resource work | Subject/address-parts helpers; import/daily/content recipes; source adapters and blocker guidance | Approved recipe/mechanical helpers; remaining D4 cutoff/identity choices pending | Isolated model and minimal helper authoring; full ingestion pending / not run |
| T4 Knowledge/queries | D5 claims/relationships; query coverage checks and limited answers | Extraction/query recipes; agent-led retrieval/save/verification under approved meanings | D1/D5/query rule approved; no records/save-framework prerequisite | Pending / not run |
| T5 Tasks/synchronization | D5 tasks, parent fields, recurrence and three-way reconciliation | Reconciliation/sync recipes; selected task routes; agent validates uncertain effects | D5 approved; actual new adapter architecture still needs approval; no schema-engine gate | Pending / not run |
| T6 Briefs/delivery | Complete ingestion before ordinary daily brief; agent checks uncertain effects | Brief/email/audio recipes; honest outcomes and attribution | Completion/validation approved; remaining D6 content/recency/audio choices pending | Pending / not run |
| T7 Tools/schedules | Users/agents own nonconcurrent scheduling and recipe-based adapter selection | Instructions for choosing supported adapters; no central register/control | D7 exclusion explicit; new adapter architecture not implied by helper approval | Central register, control and known-job query deferred / not run |
| T8 Continuation/replacement | Saved source/content progress and fresh-agent access; agent owns resource recovery | Token-loss replay/missed-input/fresh-agent guidance; explicit blockers; no batch scheduler | Approved direction; remaining D4 choices pending; no records-framework gate | Pending; D2 canonical-write repair deferred / not run |
| T9 Extensions/upgrades | Approved D1 separation preserves future official/private/extension support | Preserve separated storage roles; canonical-data consumers remain possible | D1 approved; D8 installer/upgrade/compatibility/migration excluded from MVP | D8 capabilities deferred, not delivered / not run |
| T10 Development/portability | Code-capable agents; small stdlib Python routines and recipes; private developer evidence | Minimal helpers, named script references, prepared helper checks and lifecycle scenarios; limits and continuity | Minimal helper scope approved; new dependencies/architecture require separate approval | Helper/check authoring; whole-project implementation incomplete / not run |

## Every design priority

Decision references identify dependencies; the current-scope table above
controls what is approved, unresolved or explicitly outside MVP.

| Priority | Required deliverables | Concrete obligation carried into implementation | Approvals |
|---|---|---|---|
| P1 Losslessness and provenance | T2–T6, T8 | Keep substantive information and qualifications; preserve source support; expose unread/partial/unsupported/unavailable material; do not archive raw sources | D1–D6 |
| P2 Deterministic behavior | T1–T9 | Explicit procedures and mechanical helpers; normal agent verification and source-grounded relationships; no deferred repair/framework claim | Current approvals and explicit framework/D2/D7/D8 exclusions |
| P3 Simplicity | T1–T3, T7–T10 | Minimal helpers and agent-owned work; no schema/write engine, locks, central scheduler/register or concurrency subsystem | D1/helpers/execution direction approved; explicit exclusions |
| P4 Efficient execution | T1–T4, T6, T8 | Narrow startup/storage access; agent-adapted chunks within one logical run; former School-OS message/listing/transfer caps are not success boundaries | D1 and revised D4/D6 direction; remaining contracts pending |
| P5 Tool agnosticism | T2, T5–T7, T9–T10 | Approved canonical meanings; agent-selected recipe adapters and replaceable access aids; centralized bindings deferred | D1/D5/helpers approved; remaining D6 choices and any new architecture pending |
| P6 Capability-led portability | T1, T3, T5–T8, T10 | Small stdlib helpers; agent checks actual authorized operations and limits; no personal machine/daemon/CLI requirement | Code/helpers/execution direction approved; exact runtime qualification remains unestablished |
| P7 Extensibility from canonical data | T2, T4–T7, T9 | Same substantive claims/tasks/source links; no parallel authority; no deferred framework or D7/D8 machinery introduced | D1/D5 approved; genuinely new canonical architecture requires approval |
| P8 Extensible/upgradable instances | T1, T7, T9–T10 | Preserve approved D1 separation for future support; package installation/update/compatibility guarantees are explicitly not MVP claims | D1 approved; D8 deferred |
| P9 Independence from brittle technical details | T1–T3, T5–T8 | Source-metadata identity, owned IDs, durable windows, replaceable handles; no content/provider identity fallback | D1–D8 |

## Every core use case

| Use case | Implementation coverage | Evidence to prepare for later user-directed testing |
|---|---|---|
| U1 Catalog communications and substantive information | T2–T3, T8 | Complete logical ingestion across agent-managed resource work; historical/daily replies, attachments, qualifications, blockers and normal verified cleanup; S32 |
| U2 Query school information across history | T2, T4, T8 | Current/superseded facts; guidelines/deadlines; source access lost; unread material could matter; incomplete coverage lookup; scoped completion or qualified answer without false exhaustive/absence claims |
| U3 Query known jobs, agents, locations and brief sender | T6–T7 | Central known-job query deferred with D7; preserve supported output attribution without requiring a central register or deferred records framework |
| U4 Reconcile canonical tasks and synchronize selected app | T2, T5, T8 | Finite actions versus guidelines; source corrections; parent completion/plans; conflicts; missing projection; unknown write and replacement adapter |
| U5 Recent/daily email and optional audio briefs | T4–T8 | Complete-ingestion gate and blocker reporting; S33; agent-validated uncertain outcomes; recency/audio contracts still pending |
| U6 Add applications, automations, analyses and workflows | T2, T7, T9–T10 | Canonical-data use remains the direction; user/agent scheduling is external; D1 separation retained; package compatibility enforcement deferred |
| U7 Install/upgrade a supplied package | T1, T9–T10 | D8 package installer/upgrades/compatibility/migrations deferred; minimum setup requires a separate decision |

## Other mandatory principle sections

| Principle section | Requirements beyond the numbered priorities | Deliverables / approvals |
|---|---|---|
| Purpose | School-year and historical substantive data layer; applications are consumers, not its boundary | T2, T4; D1–D2, D5 |
| Decision authority | Explicit user approval of every new/changed architecture; existing approvals retained; surface contradictions | Active plan approval ledger; applies to D1–D8 and any later new choices |
| People and agent roles | Developer, instance operator and unknown runtime; one/two parents and multiple children; any number of agents/jobs; no same-data concurrent writes | T1, T7–T10; D1–D3, D7–D8 |
| Source and processing boundary | Source custody; temporary processing; complete substantive extraction; honest source deletion limits | T2–T4, T8; D1–D4 |
| Metadata meaning | Verified logical mailbox; observed plus normalized values; preserve local-part spelling, To/Cc roles and meaningful subject text; source Date meaning/zone/precision; no identity fallback | T2–T3; D2–D4; exact current recipe remains authoritative |
| Logical email/reply identity | Reuse supported logical metadata; provider-entry counts are not ground truth; each reply has its own Date and coverage; optional navigation grouping | T2–T3; D2–D4 |
| Attachment identity and coverage | Parent plus original filename; same-parent groups and unnamed/incomparable inventories; no position/handle/content identity; unread candidate cannot inherit completion | T2–T3, T8; D2–D4 |
| Bounded discovery | Persist scope and date semantics; follow continuation after short pages; unfinished-window replay without token; listing exhaustion independent of processing completeness | T2–T3, T8; D1–D4 |
| Tools/schedules/visibility | Long-term central visibility is not an MVP claim: D7 register/control excluded; user/agents schedule nonconcurrently and select adapters from recipes; credentials remain outside canonical data | T6–T8; D7 exclusion; specific new adapter architecture and remaining D6 choices |
| Release/instance lifecycle | Long-term supplied-package lifecycle retained in principles; D8 delivery deferred; D1 separated areas remain; minimum setup not yet chosen | T1, T9–T10; D1 approved, D8 excluded |
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
