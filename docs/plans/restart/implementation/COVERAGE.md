# Whole-project restart coverage

Prepared 2026-09-14 from the [product principles](../../../product-principles.md),
[active plan](../PLAN.md), [metadata recipe](../identity/METADATA-RECIPE.md) and
[historical lifecycle scenarios](../SIMULATION.md). The lifecycle model's
mechanisms and old runtime do not supply missing architecture approvals.

Status: requirements mapped; [D1](ARCHITECTURE-PROPOSAL.md) **approved explicitly
on 2026-09-14**. The [query-coverage rule](ARCHITECTURE-PROPOSAL.md#approved-query-coverage-rule)
is also explicitly approved; remaining D2 and D3–D8 are pending. Dependency columns
retain all relevant decisions, including approved choices. No replacement production capability is claimed implemented or
tested. Test scenarios may be prepared without execution. No required area has
been removed or deferred from the whole-project implementation handoff.

## Deliverables and approval dependencies

The paths below are intended new artifacts, not assertions that they exist or
approval of the mechanisms they would contain. A path/name choice is routine;
any new canonical meaning, dependency or runtime behavior still needs approval.

| ID / required area | Existing approved design | Concrete new deliverables | Dependencies | Implementation / testing |
|---|---|---|---|---|
| T1 Installation/startup | Supplied pinned package; Drive startup/configuration; actual capability discovery | Release manifest; `operations/install.md`, `startup.md`; configuration contract; installation and selection helpers | D1–D3, D7–D8 | Pending / not run |
| T2 Canonical data/custody | Drive knowledge/tasks/indexes/coverage/work; originals at source; bounded access and verified persistence | Record contracts; Drive adapter; bounded directories; record preparation/write-recovery helpers; temporary processing procedure | D1–D3 | Pending / not run |
| T3 Historical/daily ingestion | Current logical-email recipe; individual replies; parent-bound attachments; separate windows and processing coverage | New isolated development model; metadata normalizer; `operations/import.md`, `daily.md`, `process-content.md`; source adapter and window/coverage helpers | D1–D4 | Development model prepared; production pending / not run |
| T4 Knowledge/queries | Substantive facts and provenance; approved checks of discovery/content coverage; scoped completion or explicit answer limitations | Knowledge/relationship contract; extraction/query recipes; bounded query planning, coverage checks and source-reference helpers | D1–D5; query-coverage rule approved | Pending / not run |
| T5 Tasks/synchronization | Canonical actionable requests; parent state; selected task application | Task/parent-state contract; reconciliation and synchronization recipes/helpers; task adapter routes | D2–D3, D5–D6 | Pending / not run |
| T6 Briefs/delivery | Recent/daily email; supported optional audio; canonical inputs and attribution | Brief selection/composition; email/audio adapters; effect recovery and output records | D2–D3, D5–D6 | Pending / not run |
| T7 Tools/schedules | Any number of agents/jobs; management locations; operation/job bindings; desired versus observed settings | Register/capability/job contracts; discovery, binding, schedule-management and known-job/sender query recipes | D1–D3, D6–D7 | Pending / not run |
| T8 Recovery/replacement | Drive-only durable continuation; no prior conversation/local file/provider token prerequisite | `operations/resume.md`; unfinished-work selection; partial-write/unknown-effect handling; missed-window recovery | D1–D4, D6–D8 | Pending / not run |
| T9 Extensions/upgrades | Canonical-data applications; private data/configuration/compatible extensions survive updates | Extension manifest/guide; version compatibility rules; staged upgrade/recovery recipes; package builder | D1–D3, D8 | Pending / not run |
| T10 Development/portability | Simple instructions/code/adapters; limited managed environments; useful private failure evidence | Generic entry point; optional helper package; adapter templates; prepared tests/fixtures; qualification limitations and repository continuity | D3, D8; other decisions for their dependent components | Preparation in progress / not run |

## Every design priority

| Priority | Required deliverables | Concrete obligation carried into implementation | Approvals |
|---|---|---|---|
| P1 Losslessness and provenance | T2–T6, T8 | Keep substantive information and qualifications; preserve source support; expose unread/partial/unsupported/unavailable material; do not archive raw sources | D1–D6 |
| P2 Deterministic behavior | T1–T9 | Owned IDs; explicit decisions; independent state and verification; recovery without conversation; source-grounded semantic relationships | D1–D8 |
| P3 Simplicity | T1–T3, T7–T10 | Small records and adapters; ordinary household operation; no locks, leases, global agent singleton or concurrency engine | D1–D3, D7–D8 |
| P4 Efficient execution | T1–T4, T6, T8 | Narrow startup; bounded record/content transfers, lookups and work; history may be traversed over several runs | D1–D4, D6 |
| P5 Tool agnosticism | T2, T5–T7, T9–T10 | Stable canonical meaning; replaceable access aids and adapters; per-operation/job selection | D1–D3, D5–D8 |
| P6 Capability-led portability | T1, T3, T5–T8, T10 | Discover actual operations/limits; scoped unsupported states; no required personal computer, persistent process or coding CLI | D1, D3–D4, D6–D8 |
| P7 Extensibility from canonical data | T2, T4–T7, T9 | Applications consume the same claims/tasks/source links; no parallel incompatible authority | D1–D3, D5–D8 |
| P8 Extensible/upgradable instances | T1, T7, T9–T10 | Preserve private data/configuration and compatible additions across versioned installation updates | D1–D3, D7–D8 |
| P9 Independence from brittle technical details | T1–T3, T5–T8 | Source-metadata identity, owned IDs, durable windows, replaceable handles; no content/provider identity fallback | D1–D8 |

## Every core use case

| Use case | Implementation coverage | Evidence to prepare for later user-directed testing |
|---|---|---|
| U1 Catalog communications and substantive information | T2–T3, T8 | Historical/daily messages, replies, metadata presentation, attachments/images, qualifications, incomplete work and verified cleanup |
| U2 Query school information across history | T2, T4, T8 | Current/superseded facts; guidelines/deadlines; source access lost; unread material could matter; incomplete coverage lookup; scoped completion or qualified answer without false exhaustive/absence claims |
| U3 Query known jobs, agents, locations and brief sender | T4, T6–T7 | Multiple jobs/runtimes; stale observed status; inaccessible scheduler; attribution preserved after defaults change |
| U4 Reconcile canonical tasks and synchronize selected app | T2, T5, T8 | Finite actions versus guidelines; source corrections; parent completion/plans; conflicts; missing projection; unknown write and replacement adapter |
| U5 Recent/daily email and optional audio briefs | T4–T8 | Late-processed information; no new actions; stale task sync; unsupported audio; lost delivery response; output attribution |
| U6 Add applications, automations, analyses and workflows | T2, T7, T9–T10 | Independent application uses canonical records; several bindings/jobs; compatible extension retained |
| U7 Install/upgrade a supplied package | T1, T8–T10 | Fresh install; interruption; fresh-agent startup; compatible upgrade retains private state/additions; incompatible migration stays explicit |

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
| Tools/schedules/visibility | Known tools and actual management locations; credentials elsewhere; default/job bindings; desired/observed distinction; verification time; historical run/output/sender attribution | T6–T8; D2–D3, D6–D7 |
| Release/instance lifecycle | GitHub official package; user supplies archive; installed pin; extensions normal and preserved; architectural changes still need approval | T1, T9–T10; D1–D3, D8 |
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

The whole-code handoff requires every T1–T10 implementation item accounted for,
accepted code committed/pushed, the exact remote commit verified, current
continuity documents and a clear **implemented but untested** report. This
preparation/approval checkpoint is not that handoff. Any blocked publication or
missing architectural approval is reported rather than replaced with testing.
