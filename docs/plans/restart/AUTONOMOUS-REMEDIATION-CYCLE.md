# Autonomous remediation and qualification cycle

Status: the user has authorized this complete cycle: preserve the published
baseline, run one new unchanged pre-fix round, perform evidence-bound
retrospectives and independent audits, select and implement only treatments that
stay within approved architecture or are routine nonarchitectural work, publish
one new immutable starter, run two independent post-fix rounds without an
intervening fix, publish the final cross-round analysis and self-contained
website brief, and stop. The authorized tests and eligible nonarchitectural fixes
do not require another readiness or implementation approval. A treatment that
would make a new or changed architecture decision is the only additional
approval gate.

This plan is the execution authority for this cycle. The current
[restart plan](PLAN.md), [trial protocol](TRIAL-PROTOCOL.md),
[product principles](../../product-principles.md),
[round-two results](ROUND-2-TRIAL-RESULTS.md), and
[round-two retrospective](ROUND-2-ROOT-CAUSE-RETRO.md) remain the governing
contracts and baseline evidence. Where those documents retain an earlier
review-stop, this later, specific authorization supersedes that stop only for the
sequence and effects named here. It does not broaden source scope or authorize
brief delivery, audio, task-application writes, mailbox mutation, schedules,
cleanup of earlier instances, or unrelated qualification work.

## Exact baseline and frozen inputs

The cycle begins from this immutable public snapshot:

| Baseline item | Exact value |
| --- | --- |
| Source commit | `db68b12840aab3d0c94cfbb7d036a85f31b311f2` |
| Immutable tag and release | `school-os-autonomous-remediation-baseline-2026-09-17` |
| Website baseline | Hosted version 25; local site source commit `708d46611cbf2175d4bc68b7c5cb53e96826083e` |

Before the first new route starts, verify and record that the remote tag and
release resolve to the source commit, identify the exact starter asset, and bind
its downloaded bytes to an asset name, byte count and SHA-256 digest. A mismatch
is a publication-provenance failure and stops the new round before setup; it is
not permission to rebuild or silently replace the baseline. Website version 25
is the frozen public presentation baseline. Its local site source tree is clean
at the commit recorded above. Later website publication must identify the new
deployed version and preserve both version 25 and that source commit as the
rollback boundary. Repository/starter rollback and website rollback remain
separate operations: restoring product source does not silently redeploy a site,
and restoring the site does not alter the product repository.

The prior round and its retrospective are already captured. They remain the
current-round baseline and are not replayed, rewritten, cleaned up or regraded:

- zero of three round-two setup gates passed;
- Sol persisted a Task-route collision that the bootstrap checker accepted;
- Spark visibly crossed the setup-only boundary, while Gmail dispatch remained
  unproven and a separate controller routing incident remained unresolved;
- Work reached the expected interview, but the controller missed the response,
  no answers were supplied and setup remained pending; and
- ingestion, source-semantic comparison, common questions and the page-size
  comparison were unexercised.

The new unchanged pre-fix round uses the baseline commit and the exact starter
bytes from the baseline release. No product, starter, setup instruction,
evaluator treatment or provider-specific coaching may change before or during
that round.

All eligible ingestion runs use the already fixed received/arrival interval
`[2026-09-09T17:53:48Z, 2026-09-16T17:53:48Z)`: start inclusive, end exclusive,
UTC, with the source route's actual supported precision recorded. The configured
mailbox, sender/source scope, household answers and common questions remain the
same across eligible routes and rounds. A tested route learns this interval and
source scope only in its separate ingestion request after setup passes.

## Fixed execution boundary

The coordinator owns the round ledger, architecture classification, repository
integration, publication, final comparison and stop decision. Bounded workers,
when useful, must use Sol; do not use Astra workers. The coordinator may run at
most three bounded workers and must keep browser controllers isolated. Tested
route agents and independent evaluators must not receive another route's
transcript, saved output, retrospective, oracle or expected answer.

Every round uses the same three route types:

1. one fresh context-free Sol route with no inherited conversation;
2. one fresh Gemini Spark conversation in the user's signed-in Chrome profile;
3. one fresh ChatGPT Work conversation in that same signed-in Chrome profile.

Each route gets a distinct fresh conversation or task, controller, browser tab
where applicable, Drive root and private evidence directory. Operate the shared
browser UI serially through one coordinator-controlled lease; provider tasks may
continue processing while another route is idle, but no controller may type,
navigate, inspect or use app-global controls while another holds the lease.
Record the task identity before answering an interview or sending a follow-up.
Spark and Work necessarily share browser cookies, signed-in account state,
visible app state and unknown provider memory. Report those limits and never
claim browser-profile, account-level or provider-memory isolation.

The opening request is the ordinary one-link request: the exact immutable
starter link plus “setup my schoolOS.” Give configuration and destination answers
only through the ordinary interview. Direct each route to disregard earlier
School-OS instances and confine every persistent write to its assigned root and
descendants. Do not erase or modify earlier instances to enforce that scope.

Setup is a hard gate for ingestion. The tested agent's completion claim, its own
validation and the mere presence of files do not pass the gate. An independent
saved-state audit must establish the intended ancestry, complete readback,
contract-valid bootstrap, required role and route separation, bounded pages,
reference resolution and truthful completeness. A route that fails or remains
incomplete receives no source interval, mailbox request, common questions or
page-size request. Continue the other independent routes when safe.

Mailbox access is read-only. Do not change read/unread state, labels, folders or
messages; do not delete or send mail. Canonical Tasks may be saved only inside
the route's isolated Drive instance. External task-application writes, outbound
School-OS briefs, audio generation or delivery, and schedules are excluded. The
final website brief is a sanitized development report, not a household brief or
School-OS delivery action.

The installed canonical page maximum remains 65,536 encoded UTF-8 bytes, with
whole records. Any 64/128/256 KiB comparison follows the existing private,
noncanonical evaluation procedure and does not change the installed maximum.
Changing that maximum or introducing a split-record representation is an
architecture-changing treatment.

## Evidence and independence rules

Before any source or Drive dispatch for a route, create its admitted gitignored
private evidence directory with owner-only directory permissions. Preflight the
receipt sink by writing, reading back and deleting harmless synthetic content.
Every real connector response envelope or thrown exception is preserved before
normalization in a mode-0600 file. Record dispatch, provider response and local
receipt persistence as separate states. A sink failure before dispatch stops the
operation; a sink failure after dispatch is an evaluator failure and proves
neither provider success nor provider failure.

Private evidence may contain the minimum real source and connector material
needed for audit. It stays outside Git, patches, terminal output, public website
content and chat. Public findings exclude household data, source content,
provider or folder IDs, task URLs, request arguments, credentials and raw errors.
Use privacy-safe aliases and private receipt paths. A hash may bind private
developer evidence; it is never canonical email or attachment identity.

One evaluator independent of the tested routes must bind a frozen source oracle
to the exact authorized interval: enumerate the interval, follow available
continuation, review the substantive body and required attachments, and preserve
the supporting receipts before comparing tested output. Every later round reuses
that exact closed-interval oracle. Re-enumerate or reread source only when receipt
integrity is insufficient, the source becomes unavailable, or concrete evidence
shows that the closed interval or source projection changed; record that bounded
recheck as a method event. This avoids repeated whole-corpus source I/O and
comparison drift while every route's saved state is still audited independently.
Expectations cover claims, qualifications, applicability, date role and
precision, deadlines, finite/conditional/recurring actions, independent
completion units, corrections and supported completion evidence. A fact-free or
action-free expectation needs a source-supported reason. Provider-entry counts
are observations, not counts of logical emails.

Image-specific expectations require prior independent inspection of the exact
pixels or a faithful private rendering. Record which page, frame or crop was
reviewed and label OCR as derived. Missing or unreadable pixels remove the
unsupported image finding rather than becoming a product failure.

The saved-state auditor follows the exact installed bootstrap, configuration and
contract. Traverse every explicit continuation, nested bucket page ID, source
window root, locator, catalogue, coverage reference and supported fallback.
Record unresolved required references, advisory hints, unknown shapes,
duplicate or conflicting IDs, cycles and exhaustion. A short list without an
explicit end marker does not establish exhaustive inventory. An unknown shape or
unfinished reference traversal makes the audit incomplete, not empty.

For a passing setup, issue the fixed ingestion request once. Audit the resulting
state against the independent source expectations; do not accept a tested
agent's self-audit as the oracle. Then run the same source-grounded common
questions and, where the canonical corpus permits it, the existing 64/128/256
KiB private comparison. Grade actual retrieval traces, saved records, source
links, qualifications, omissions and limits. Mark unobservable metrics and
unexercised stages as such; do not estimate them as facts.

A downloaded route report is evidence only when the observed prompt, final
response, explicit export action, supported receipt and exact received bytes all
bind it to that route. Otherwise grade the visible response and disclose the
artifact limit.

## Required issue record

Every observed issue, including a product defect, tested-agent decision,
provider/connector failure, evaluator incident, inefficiency or unverified
effect, gets one stable issue ID and one evidence packet before treatment. A
packet is complete only when it records:

1. the earliest proven divergence and all independent observations that support
   it, with private receipt references;
2. the provider's concise retrospective decision summary when available,
   requested as an explanation tied to visible actions or artifacts and never as
   hidden chain-of-thought;
3. the coordinator's inference, an explicit confidence level and the evidence
   that connects the observations to that inference;
4. remaining unknowns and claims that the evidence does not establish;
5. cause classification across product/specification, tested-agent decision,
   product implementation, provider/connector, and evaluator/controller;
6. the relevant product principles, approved contracts and prior decisions;
7. treatment classification, selected treatment or backlog disposition;
8. the exact reviewed file diff for an implemented treatment, or `none` with a
   reason for an unimplemented or external issue;
9. validation actually run and its result, clearly separated from unexecuted
   checks and publication hygiene;
10. an exact rollback point that restores the pre-treatment repository and
    published artifact state; and
11. the later verification result in post-fix round A and post-fix round B,
    including `unexercised`, `inconclusive` or `regressed` where appropriate.

Do not infer a common cause from a similar final symptom. Provider retrospective
claims may corroborate observations but do not independently prove dispatch,
tool effects, internal decisions or technical cause. The issue packet, treatment
matrix and final report must keep observations, provider claims, inference and
controller incidents distinct.

## Treatment classification and authority

Classify every proposed treatment before editing:

| Class | Meaning | Authority in this cycle |
| --- | --- | --- |
| A — approved-architecture implementation | Corrects implementation, validation, instructions or fixtures so they enforce an already explicit approved contract or architecture decision without selecting a new representation or meaning. | Authorized to implement and validate. |
| B — nonarchitectural | Repairs evaluator/controller behavior, diagnostics, privacy handling, test coverage, wording, deterministic checks or another routine implementation detail without changing a product invariant, canonical meaning, generic contract or lifecycle behavior. | Authorized to implement and validate. |
| C — architecture-changing | Selects or changes a canonical representation, invariant, data meaning, generic contract, source/identity rule, page model, release/upgrade behavior or other system structure not already explicitly approved. | Backlog and escalate with a concrete proposal; do not implement without explicit user approval. |
| D — no product treatment | Evidence supports a provider limitation, isolated tested-agent error, environmental incident or unknown cause for which a repository change is unsupported. | Preserve, report and improve only authorized class A/B evaluation controls when justified. |

Class A requires a citation to the exact prior approval and an explanation of why
the change merely realizes it. If that argument depends on choosing among two
plausible persisted representations or changes behavior beyond the approved
contract, classify it as C. A test that freezes a new behavior can make an
architecture decision as surely as production text can; classification applies
to tests, examples and instructions as well as code.

## Phased execution

### Phase 0 — preserve the captured baseline

1. Verify the exact baseline source, tag/release and starter bytes described
   above. Record website version 25.
2. Freeze links to the round-two results and retrospective as captured baseline
   evidence. Before opening a new route, finish the baseline root-cause inventory:
   revisit each exact retained provider conversation when safely accessible,
   stabilize one issue packet for every already observed Sol, Spark and Work
   divergence, and record a provider summary or explicit `unavailable` only after
   the accessible evidence is exhausted. This supplements the baseline without
   replaying, regrading, repairing or rewriting it. In particular, Work's missed
   interview is proven, while the controller observation failure's technical
   cause remains `unknown` unless new retained evidence establishes it.
3. Create the public privacy-safe round ledger and the private companion ledger.
   Preassign route aliases, fresh roots and evidence directories for the new
   pre-fix round without opening source scope to a tested route.
4. Record the frozen interview answer sheet, fixed interval, common questions,
   source-audit procedure and evaluator revision. The answer sheet remains
   private and is supplied only in response to the ordinary interview.

Exit when provenance, inputs, isolation and evidence sinks are verified. There
is no approval pause at this exit.

### Phase 1 — run one new unchanged pre-fix round

Run fresh Sol, Spark and Work routes from the baseline starter. Use new
conversations, controllers, tabs, Drive roots and evidence directories. Browser
operations are serialized. Do not modify the baseline product or evaluator
method after the first route starts.

For each route:

1. send only the one-link setup request;
2. answer the ordinary interview in the verified route-specific composer;
3. wait for setup to complete or reach a proven terminal blocker;
4. independently audit the saved setup;
5. if and only if that audit passes, send the separate fixed seven-day read-only
   ingestion request;
6. independently audit source-to-saved semantics, then run the common questions
   and eligible page-size comparison; and
7. freeze the route result, receipts and unknowns before another treatment is
   considered.

An unaffected route continues after another route fails. No defect found in this
phase is repaired during the phase. The round closes only when all three routes
have a terminal result or a stop rule below has made further execution unsafe or
unverifiable.

### Phase 2 — evidence-bound retrospectives and audits

For each route, compare observable UI/tool chronology, saved-state readback and
independent source expectations. Ask the tested provider, in the exact retained
conversation when safely accessible, for a concise account of the earliest
decision that produced each divergence, what contract or input it used, what it
validated, and which actions or effects it can substantiate. State explicitly
that hidden reasoning is neither requested nor accepted as evidence.

Create or complete one issue packet per distinct divergence. Independently audit
all finite referenced saved state and the source-to-saved result for every route
that passed setup. Do not broaden the audit to another route's root or treat a
provider's absence claim as exhaustive without the underlying action record or
readback. Retrospectives are read-only except for their conversation messages and
private local receipt capture.

Exit when each issue has proven observations, provider summary or an explicit
`unavailable`, inference confidence, unknowns and cause classification. Do not
select fixes inside a provider conversation.

### Phase 3 — build the cohesive treatment matrix

Synthesize the captured round-two evidence and the unchanged pre-fix round into
one matrix. Group issues only when the independent evidence supports a shared
failure boundary. Map every treatment to the product principles, current
contract, affected routes and expected observable behavior. State dependencies,
conflicts and the smallest responsible boundary so the package remains cohesive
instead of accumulating route-specific prompt patches.

Classify each treatment A, B, C or D. Backlog every class C item with the concrete
proposal, principle grounding, alternatives, tradeoffs, compatibility effect and
unknowns needed for a user architecture decision. Do not include class C changes
in the implementation set. Select all supported class A and B treatments; class
D issues receive no speculative product fix.

The matrix is a required implementation input. Its completion is not a new
approval gate for class A/B work. If a class C decision blocks one otherwise
inseparable treatment, backlog that dependent treatment and continue every
independent authorized class A/B treatment.

### Phase 4 — implement and validate the authorized treatment set

Create a rollback point at the exact baseline source commit, then apply the
selected class A/B treatments at their smallest responsible boundaries. Preserve
the approved architecture, the 64 KiB maximum, canonical meanings, source
identity rules, setup/ingestion separation and MVP deferrals. Do not repair or
rewrite trial instances.

For every issue, capture its exact file diff and bind it to the treatment ledger.
Review the combined diff for interaction effects and update active documentation
so the contract, operation recipe, helper and meaningful fictional regression
case agree. Run validation appropriate to the actual treatment, including
focused deterministic regression checks and the full applicable local suite
when shared helpers or contracts change. Run compilation, document-link,
whitespace and privacy checks as applicable. Local validation establishes only
the behavior it exercises; it is not provider or product qualification.

Inspect repository hooks and CI before publication and do not bypass them.
Resolve failures within the selected class A/B scope or record the treatment as
incomplete. For each completed treatment, record the exact pre-treatment rollback
point and the exact integrated revision that contains the reviewed diff.

### Phase 5 — publish one new immutable starter

Publish the complete reviewed class A/B package as one exact repository revision.
Commit and push only accepted in-scope public files, verify the remote branch at
that revision, build the starter from those exact committed bytes, and verify
its inventory and privacy properties. Publish one new immutable tag/release and
starter asset. Record source revision, tag, release URL, asset name, byte count,
SHA-256 digest and file inventory, then download the release asset afresh and
verify an exact byte match.

The published revision and starter bytes are frozen for both post-fix rounds.
Publication and local checks do not qualify setup, Drive, Gmail, provider or
semantic behavior. Do not begin post-fix testing if source revision, tag, release
and downloaded asset do not agree exactly.

### Phase 6 — post-fix round A

Run the same three route types with the new immutable starter and entirely fresh
conversations, controllers, tabs, Drive roots and evidence directories. Reuse
the frozen interview choices, fixed source interval, source expectation method,
common questions and evaluation procedure. Enforce the setup hard gate for each
route and perform the same independent saved-state and source-semantic audits as
in the pre-fix round.

Complete the round ledger and each issue's round-A verification result. Preserve
new defects as new issue packets. Do not modify the product, starter, prompts,
fixtures, evaluator rules or failed instances after round A starts.

### Phase 7 — post-fix round B with no between-round fixes

After round A reaches terminal results, start a second independent set of fresh
Sol, Spark and Work routes using the exact same published source revision and
starter bytes. Use new conversations, controllers, tabs, Drive roots and evidence
directories. Keep the fixed interval, private answer sheet, common questions,
source expectations and evaluator revision unchanged.

No code, documentation, starter, prompt, controller behavior or evaluation-rule
fix may be introduced between rounds A and B. An operational intervention needed
to preserve safety or collect evidence must be recorded and cannot silently
change the method. A new defect remains evidence for the final analysis and a
future backlog; it does not trigger a hotfix or replacement round.

Complete every original and newly observed issue's round-B verification result.
Two passes support repeatability only within these exact routes, accounts,
permissions, inputs and observed conditions; they do not establish blanket
vendor compatibility.

### Phase 8 — final cross-round analysis, website brief and stop

Compare the captured prior round, the new unchanged pre-fix round, post-fix round
A and post-fix round B. Separate implementation, local validation, exercised
behavior, passes, failures, regressions, inconclusive outcomes and unexercised
capabilities. Analyze each route independently before making a cross-route claim.
Report whether every implemented treatment changed its targeted observable,
whether the result repeated in both post-fix rounds, and whether a regression or
new failure appeared elsewhere.

Publish a privacy-safe repository report and a self-contained page on the
existing owner-private architecture website. The website brief must use the
same hierarchy, plain language and decision altitude as the restart planning
pages. It must be understandable without this conversation or the coordinator's
private reasoning. For every issue, present the observed symptom, independent
evidence, tested agent's concise account, coordinator inference and confidence,
treatment class and rationale, exact diff or backlog decision, rollback point,
post-fix A and B outcomes, remaining risk and next step. It must also state:

- the exact baseline and post-fix source revisions, release tags, starter asset
  names, sizes and digests;
- website baseline version 25 and the final deployed website version;
- the fixed interval and complete route/round matrix;
- the setup gate result and every dependent stage's status for each route;
- independent saved-state and source-semantic findings;
- proven observations, provider decision summaries, inference confidence and
  unknowns without hidden chain-of-thought;
- the treatment classification and rationale, exact public diffs, validation,
  rollback points and both later verification results;
- browser/profile and evidence limits, interventions and invalidated comparisons;
- product-principle and T01-T19 coverage; and
- architecture backlog, unresolved provider/controller issues and all remaining
  unexercised scope.

Verify the site deployment reports success and inspect the published page for
the required sections, privacy, links and displayed revision values. Record that
publication hygiene separately from functional validation. Then stop. Do not
begin another fix, cleanup, retry, trial series, source expansion or architecture
implementation from findings in the final report.

## Stop and escalation rules

These rules are terminal for the affected operation or route unless they say to
continue independent work. They do not create another routine approval gate.

- **New or changed architecture:** stop the dependent treatment before editing.
  Add a class C backlog entry with a concrete recommendation, principle
  grounding, alternatives, tradeoffs, compatibility impact and unknowns. Request
  explicit user approval only if that architecture treatment must enter this
  cycle. Continue independent class A/B work. If the unresolved decision prevents
  a truthful cohesive release, finish the evidence and report, then stop the
  cycle without publishing a post-fix starter.
- **Privacy or receipt integrity:** stop before dispatch when the private sink,
  permissions or redaction boundary is not verified. After a dispatch with lost
  receipt, preserve the evaluator failure, verify any possible remote effect by
  a safe read, and stop the affected operation if evidence cannot be restored.
  Any suspected public disclosure of private material stops publication and all
  dependent work until containment and a privacy-safe review are complete.
- **Uncertain writes or effects:** never retry a write or send blindly. Use an
  available safe read to establish the effect. One identical launch or read retry
  is permitted only when evidence proves no dispatch and no effect. If effect
  remains unknown, stop the affected route and report `unknown`; do not infer
  success, failure, throttling, authentication error or timeout from a generic
  error.
- **Cross-route contamination:** stop all affected routes, preserve the evidence
  and mark their comparison invalid. Do not copy outputs, oracles or context to
  repair the comparison and do not silently substitute a replacement route. The
  unaffected routes may finish, but no aggregate claim may use contaminated
  results.
- **Inability to verify setup:** setup fails or remains incomplete. Do not send
  the ingestion request or any dependent question or size request.
- **Inability to verify source or saved effects:** keep the relevant email,
  inventory, write or answer incomplete or inconclusive. Continue only checks
  whose independence and safety do not rely on that effect. No empty inventory,
  full ingestion, exhaustive answer or successful treatment may be inferred.
- **Method drift or between-round change:** stop the affected comparison. After
  post-fix round A starts, any product, starter, prompt or evaluator-rule change
  ends the planned A/B repeatability claim; preserve results and move the new
  treatment to the backlog.

## Round ledger template

Keep private route identifiers and receipt paths in the private companion. The
public ledger uses aliases and privacy-safe summaries.

| Field | Required entry |
| --- | --- |
| Round | Captured baseline / unchanged pre-fix / post-fix A / post-fix B |
| Round status | Planned / running / complete / stopped / invalidated |
| Product revision | Exact source commit |
| Starter provenance | Tag/release, asset name, size, SHA-256, verified download result |
| Evaluator revision | Exact public revision plus private procedure version |
| Fixed source scope | Interval, boundary semantics, timezone, precision and privacy-safe mailbox/sender-scope alias |
| Route | Sol / Gemini Spark / ChatGPT Work |
| Isolation | Fresh task alias, controller alias, tab alias, Drive-root alias, evidence-area alias; private IDs only in companion |
| Browser constraint | Shared-profile disclosure and lease/intervention record |
| Receipt sink | Preflight result, mode-0600 result and private receipt index |
| Setup | Start/end, interview completed, claim, saved-state audit result and blocker |
| Ingestion | Requested only after setup pass; dispatch, coverage and terminal result |
| Independent audit | Source reference, saved reference traversal, exhaustion and semantic result |
| Questions | Set version, retrieval trace result and grading summary |
| Page-size evaluation | Canonical maximum, candidate statuses and observed measures |
| Interventions | Exact prompt/controller/provider intervention and reason |
| Issues | Stable issue IDs and evidence-packet status |
| Outcome | Passed / failed / incomplete / inconclusive / invalidated, with unknowns |
| Excluded effects | Mailbox mutation, external task write, outbound brief/audio and schedule all confirmed unexercised or recorded as an incident |

## Treatment and rollback ledger template

| Field | Required entry |
| --- | --- |
| Issue ID and title | Stable cross-round identifier |
| First observed | Round, route and earliest proven divergence |
| Proven observations | Privacy-safe facts plus private receipt references |
| Provider decision summary | Concise supported retrospective or `unavailable`; no hidden reasoning |
| Inference | Coordinator conclusion and confidence |
| Unknowns | Effects, causes or scope not established |
| Cause classification | Product/specification, tested agent, implementation, provider/connector, evaluator/controller |
| Principle/contract grounding | Exact approved rule and affected use case |
| Treatment class | A / B / C / D |
| Disposition | Implemented treatment, architecture backlog or no product treatment |
| Expected observable | Specific result that later rounds can verify |
| Exact file diff | Reviewed paths and exact diff/commit binding, or `none` with reason |
| Validation | Commands/checks actually run, result and limits |
| Rollback point | Exact pre-treatment commit/tag and treatment commit or revert boundary |
| Publication binding | Integrated source revision and starter tag/digest |
| Post-fix A | Pass / fail / regression / inconclusive / unexercised, with evidence |
| Post-fix B | Pass / fail / regression / inconclusive / unexercised, with evidence |
| Final conclusion | Repeated, partially supported, not supported, regressed or backlogged |

## Completion condition

The cycle is complete only when the baseline is bound, the new unchanged pre-fix
round has terminal results, route retrospectives and independent audits are
recorded, every issue is classified, every selected class A/B treatment has an
exact diff/validation/rollback record, one immutable post-fix starter is
published and verified, both unchanged post-fix rounds have terminal results,
and the repository report and self-contained website brief are published and
verified. A stop rule may instead end the cycle as incomplete; that outcome must
name the exact completed phases, preserved evidence, unknowns and blocked next
action. In either case, the coordinator stops after the final report and does not
start another remediation loop.
