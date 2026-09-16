# Whole-project restart coverage

Updated 2026-09-15 from the [product principles](../../../product-principles.md),
[active plan](../PLAN.md), [metadata recipe](../identity/METADATA-RECIPE.md) and
[historical lifecycle scenarios](../SIMULATION.md). The lifecycle model's
mechanisms and old runtime do not supply missing architecture approvals.

Status: requirements mapped; D1, the
[query-coverage rule](ARCHITECTURE-PROPOSAL.md#approved-query-coverage-rule),
D3 code-execution capability and **D5 in full** are approved. The user's
2026-09-15 directions revise D4/D6 and narrow D7/D8 as recorded below. Exact
record/ordinary-write design, minimum setup, remaining D3 contracts and the
unapproved parts of D4/D6 still need decisions before dependent code. Supplier
code-capability availability is user-reported, not independently qualified.
No replacement production capability is claimed implemented or tested.

## Current execution direction and explicit MVP exclusions

The [active plan](../PLAN.md) governs these explicit changes; the long-term
product principles remain unchanged. The original whole-project checklist must
not be reported fully delivered without naming the exclusions.

| Decision | Current scope |
|---|---|
| D2 | Interrupted canonical-write discovery/repair/reconciliation remains outside MVP. Normal verified persistence remains required; minimum record/ordinary-write definitions remain undecided. |
| D4 | One logical ingestion run completes all relevant unprocessed mail in its authorized scope. The actual agent manages adaptive resource chunks and resource recovery using School-OS guidance. Former School-OS per-run caps and batch/continuation scheduling are rejected. Remaining identity/discovery/content policy choices are not blanket-approved. |
| D5 | Approved in full: substantive claims and relationships; parent fields and state; finite/recurring tasks; native recurrence or a 14-day occurrence fallback; three-way task-field reconciliation and missing-projection handling. Exact record and adapter definitions remain dependencies. |
| D6 | The agent validates uncertain actions using its available authorized means. Complete ingestion is required before an ordinary daily brief. A blocked logical run reports the blocker, not a normal partial daily brief. Remaining recency/audio/record contracts are not blanket-approved; no fixed School-OS intent/recovery engine is inferred. |
| D7 | Centralized tools/jobs/capabilities register and scheduling control are outside MVP. Users and agents own nonconcurrent scheduling and select adapters from recipes. No replacement School-OS scheduler or registry is introduced. |
| D8 | Package installer, upgrades, compatibility and migrations are deferred. D1's approved system/instance/extensions separation preserves room for future support; it is not proof of upgrade capability. Minimum setup remains undecided. |

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

## Deliverables and approval dependencies

The paths below are intended new artifacts, not assertions that they exist or
approval of the mechanisms they would contain. A path/name choice is routine;
any new canonical meaning, dependency or runtime behavior still needs approval.

| ID / required area | Existing approved design | Concrete new deliverables | Dependencies | Implementation / testing |
|---|---|---|---|---|
| T1 Setup/startup | D1 Drive entry point and separated areas; code-capable agents and configured source scope | Minimum setup/startup instructions and configuration contract; agent checks its actual capabilities | D1/code capability approved; minimum setup, record definitions and remaining D3 pending | Pending; D8 package installer deferred / not run |
| T2 Canonical data/custody | Drive knowledge/tasks/indexes/coverage; originals at source; bounded access and verified normal persistence | Record contracts; Drive adapter; bounded directories; record preparation and ordinary-write procedure; temporary processing procedure | D1, undecided record/ordinary-write design, D3 | Pending; interrupted-write recovery excluded from MVP / not run |
| T3 Historical/daily ingestion | Current metadata recipe and separate content coverage; one logical run completes relevant unprocessed mail, using agent-managed resource work | Metadata normalizer; import/daily/content recipes; source adapters; guidance for adaptive resource work and honest blockers; no School-OS batch scheduler | D1 and execution direction approved; remaining D3/D4 and records pending | Isolated model prepared; production pending / not run |
| T4 Knowledge/queries | D5 substantive claims/relationships; approved discovery/content coverage checks and limited answers | Knowledge contract; extraction/query recipes; bounded retrieval and source-reference helpers | D1/D5/query rule approved; records and remaining D3 pending | Pending / not run |
| T5 Tasks/synchronization | D5 finite/recurring tasks, parent fields, three-way reconciliation and missing projections | Task contract; reconciliation/sync recipes; task adapter routes; agent validation of uncertain effects | D5 approved; records, remaining D3 and D6 contracts pending | Pending / not run |
| T6 Briefs/delivery | Complete ingestion before ordinary daily brief; agent checks uncertain effects with authorized means | Completion gate; brief composition/email/audio recipes and adapters; honest output status and attributable records | Completion/validation direction approved; recency/audio/output contracts and remaining D3 pending | Pending / not run |
| T7 Tools/schedules | Users/agents own nonconcurrent scheduling and recipe-based adapter selection | Recipe instructions for choosing supported adapters; no central register/control subsystem | D7 exclusion explicit; remaining D3 adapters pending | Central register, control and known-job query deferred / not run |
| T8 Continuation/replacement | Saved source-window/content progress and fresh-agent access; actual agent owns resource recovery | Guidance for token-loss replay, missed input and fresh-agent reading; explicit blockers; no School-OS continuation scheduler | D1/execution direction approved; record and remaining D3/D4 details pending | Pending; D2 canonical-write repair deferred / not run |
| T9 Extensions/upgrades | Approved D1 separation preserves future official/private/extension support | Preserve separated storage roles; canonical-data consumers remain possible | D1 approved; D8 installer/upgrade/compatibility/migration excluded from MVP | D8 capabilities deferred, not delivered / not run |
| T10 Development/portability | Code-capable agents; simple instructions/code/adapters; limited environments; private developer evidence | Entry point; code/runtime contracts after approval; adapter recipes; prepared in-scope scenarios; limits and continuity | Code capability approved; remaining D3 and record/setup choices pending | Preparation in progress / not run |

## Every design priority

Decision references identify dependencies; the current-scope table above
controls what is approved, unresolved or explicitly outside MVP.

| Priority | Required deliverables | Concrete obligation carried into implementation | Approvals |
|---|---|---|---|
| P1 Losslessness and provenance | T2–T6, T8 | Keep substantive information and qualifications; preserve source support; expose unread/partial/unsupported/unavailable material; do not archive raw sources | D1–D6 |
| P2 Deterministic behavior | T1–T9 | Owned IDs, explicit decisions, normal verification and source-grounded relationships; no claim of deferred write repair, registry control or upgrade recovery | Current approvals, subject to D2/D7/D8 exclusions |
| P3 Simplicity | T1–T3, T7–T10 | Small records/adapters; agent-owned resource work; no locks, leases, global agent singleton, central scheduler/register or concurrency engine | D1 and current execution direction; D2/D7/D8 exclusions |
| P4 Efficient execution | T1–T4, T6, T8 | Narrow startup/storage access; agent-adapted chunks within one logical run; former School-OS message/listing/transfer caps are not success boundaries | D1 and revised D4/D6 direction; remaining contracts pending |
| P5 Tool agnosticism | T2, T5–T7, T9–T10 | Stable canonical meaning; replaceable access aids/adapters selected from recipes by the agent; centralized job binding deferred | D1/D5 approved; remaining D3/D6 pending; D7/D8 excluded |
| P6 Capability-led portability | T1, T3, T5–T8, T10 | Agent checks actual authorized operations/limits; reports blockers; no required personal computer, persistent process or coding CLI | D1/code capability/execution direction approved; remaining D3/D4/D6 contracts pending |
| P7 Extensibility from canonical data | T2, T4–T7, T9 | Applications consume the same claims/tasks/source links; no parallel incompatible authority; D7/D8 machinery deferred | D1/D5 approved; remaining records/adapters pending |
| P8 Extensible/upgradable instances | T1, T7, T9–T10 | Preserve approved D1 separation for future support; package installation/update/compatibility guarantees are explicitly not MVP claims | D1 approved; D8 deferred |
| P9 Independence from brittle technical details | T1–T3, T5–T8 | Source-metadata identity, owned IDs, durable windows, replaceable handles; no content/provider identity fallback | D1–D8 |

## Every core use case

| Use case | Implementation coverage | Evidence to prepare for later user-directed testing |
|---|---|---|
| U1 Catalog communications and substantive information | T2–T3, T8 | Complete logical ingestion across agent-managed resource work; historical/daily replies, attachments, qualifications, blockers and normal verified cleanup; S32 |
| U2 Query school information across history | T2, T4, T8 | Current/superseded facts; guidelines/deadlines; source access lost; unread material could matter; incomplete coverage lookup; scoped completion or qualified answer without false exhaustive/absence claims |
| U3 Query known jobs, agents, locations and brief sender | T6–T7 | Centralized known-job query deferred with D7; per-output attribution remains subject to D6 record decisions, without promising a central register |
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
| Tools/schedules/visibility | Long-term central visibility is not an MVP claim: D7 register/control excluded; user/agents schedule nonconcurrently and select adapters from recipes; credentials remain outside canonical data | T6–T8; D7 exclusion; remaining D3/D6 contracts |
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
D2/D7/D8 exclusions and remaining minimum-setup/contract decisions named,
accepted code committed/pushed, the exact remote commit verified, current
continuity documents and a clear **implemented but untested** report. This
preparation/approval checkpoint is not that handoff. Any blocked publication or
missing architectural approval is reported rather than replaced with testing.
