# Autonomous remediation cycle results

Status: complete through the two authorized post-fix rounds. The remediation
package improved setup validation, but it did not produce repeatable end-to-end
setup across Sol, Gemini Spark, and ChatGPT Work. No post-fix route remained
eligible for ingestion at the close of the cycle. This is an incomplete
qualification with stronger gates, not a qualified School-OS release.

This report is privacy-safe. It excludes household data, source content,
provider and Drive identifiers, task URLs, request arguments, credentials, and
raw connector errors. The complete receipts remain in the admitted gitignored
private evidence tree.

## Executive result

The cycle compared four evidence sets:

1. the captured round-two baseline;
2. one new unchanged pre-fix round;
3. post-fix round A; and
4. post-fix round B.

The baseline and unchanged round established the failures that the remediation
package should address. The package was then implemented once, published once,
and held unchanged across both post-fix rounds.

| Round | Sol | Gemini Spark | ChatGPT Work | Passing setup gates |
| --- | --- | --- | --- | --- |
| Captured baseline | Failed | Failed/incomplete | Incomplete | 0/3 |
| Unchanged pre-fix | Passed | Failed | Incomplete | 1/3 |
| Post-fix A | Passed | Failed | Insufficient evidence | 1/3 |
| Post-fix B | Failed | Incomplete | Insufficient evidence | 0/3 |

No tested route completed the authorized seven-day ingestion in any of these
rounds. The pre-fix Sol route passed setup, but the separate ingestion message
was rejected before delivery. In post-fix A, Sol again passed setup, but the host
approval boundary blocked ingestion delivery. Every other route failed or
remained insufficient at setup. Common questions, source-semantic grading and
the 64/128/256 KiB private comparison were therefore unexercised.

## What was frozen before treatment

| Artifact | Rollback point |
| --- | --- |
| Product repository | `db68b12840aab3d0c94cfbb7d036a85f31b311f2` |
| Baseline tag/release | `school-os-autonomous-remediation-baseline-2026-09-17` |
| Website | Hosted version 25; source commit `708d46611cbf2175d4bc68b7c5cb53e96826083e` |

Repository/starter rollback and website rollback are separate. Restoring one
does not silently restore or publish the other. Trial instances are evidence;
they are not repaired, cleaned up, or reused.

## What changed

The authorized package implemented approved-architecture and
nonarchitectural treatments only. It:

- requires distinct existing Task root page IDs for Active Tasks and Completed
  Task history;
- rejects missing, duplicated, wrongly bound, or aliased reserved Task roles;
- checks immutable starter material before setup writes and again after setup;
- requires the configured entry point to be read back, used to derive the finite
  bootstrap manifest, and bound to an independent intended byte sequence;
- validates the finite canonical bootstrap from actual saved page bytes;
- strengthens evaluator receipt preflight, provider-response classification,
  exact source-oracle binding, continuation tracking, reference traversal, and
  export attribution;
- records browser-route isolation accurately without claiming separate accounts
  or Chrome profiles; and
- retains the 65,536-byte canonical page maximum and whole-record rule.

The integrated implementation is commit
`e83ce22b1e1a0083d32bab8aedcfdba79c072101`, tagged
`school-os-starter-2026-09-18-remediation`. Its 41-file starter archive is
117,680 bytes with SHA-256
`1f0fadfbc5a5852ea361b1184ff501bf5588281d355130729aedd6af38211680`.
Both post-fix rounds used those same bytes.

The prepared deterministic suite recorded 73 passes and Python compilation
passed before publication. Those checks establish local deterministic behavior
only. They do not qualify a managed agent, connector, Drive setup, ingestion,
query, or semantic result.

## Cross-round findings

### 1. Task-route aliasing was addressed at the approved boundary

The captured Sol baseline saved Active Tasks and Completed Task history under
one locator, and the checker incorrectly accepted it. The implementation now
requires two distinct existing Task roots and rejects a shared root. Sol and Work
used distinct roots whenever their later setup reached this gate. Spark B did
not create Task roots at all.

This supports the selected treatment without adding a new Task lifecycle field.
It does not prove that future continuation descendants remain disjoint; that
broader ownership rule stays in the architecture backlog.

### 2. An empty installed system can no longer support setup completion

In the unchanged pre-fix round, Spark saved a coherent instance graph while the
reusable `system/` tree was empty. Post-fix round A reproduced the omission, but
the independent setup gate failed it. Post-fix round B installed all immutable
system material correctly, then failed later setup stages.

The treatment therefore improved detection. It did not make Spark complete the
entire setup reliably.

### 3. Configured-entrypoint intent remains the clearest repeated evidence gap

Work A and Work B both saved substantial, structurally valid instances. In B,
the independent audit verified all immutable files, exact configuration values,
distinct Task roots, a valid 27-page bootstrap, and pages below the approved
maximum. Work also correctly stopped short of claiming final setup completion.

The decisive gap repeated: the run used one mutable working file as the source
for the configured `START-HERE.md` write, preserved no independent pre-write
byte expectation, and did not fetch the configured entry point back afterward.
The saved bytes cannot serve as their own proof of intended bytes. The gate
therefore remains `insufficient_evidence`.

The audit also found that a generic parent-scoped Drive search omitted children
that direct folder listing returned. Work had used direct folder listings and
did not rely on that incomplete search. The discrepancy limits exhaustive
negative inventory claims; it did not cause Work's setup decisions.

### 4. Post-fix Sol exposed a new date-meaning defect

Sol B installed and validated the finite setup successfully except for one
canonical source field: the import-boundary timezone label was saved as the ISO
instant suffix rather than the requested UTC timezone meaning. The timestamp,
precision, half-open boundaries, discovery window, entrypoint, installation,
29-page bootstrap, references, and page bounds otherwise passed.

Sol's retrospective traced the value to its local setup builder. Its checks
proved that generated bytes were persisted, but none compared that field's
meaning with the frozen parent answer. This is a new post-fix issue. No hotfix
was made between rounds or after the cycle.

### 5. Spark B stopped with a partial canonical graph

Spark B installed all 32 immutable starter files byte-for-byte, then spent an
extended period generating and uploading the canonical bootstrap. It was
stopped after remaining active without reaching setup completion.

Independent readback found the original unconfigured entry point and 15 saved
canonical pages. Configuration, Source Account, and Task roots were absent. Ten
of 20 observed page references were unresolved, and the required configured
interval was absent. No bootstrap validation was eligible to run because the
configured-entrypoint prerequisite failed.

Spark reported subagent path failure, one subagent timeout, shell-formatting
friction, and incomplete page batches. Its counts of 32 immutable files and 15
saved pages match independent readback. Its intended total page count and some
action-history claims remain provider self-report.

### 6. Provider and host boundaries still prevented eligible ingestion

The unchanged pre-fix Sol route and post-fix A Sol route each passed setup, but
their separate ingestion messages were blocked before delivery. No bypass was
attempted. This is a provider/host admission boundary, not evidence of a Gmail,
School-OS ingestion, or source-content failure.

The cycle therefore supplies no evidence about extraction quality, source-to-
knowledge fidelity, task classification, query quality, or the page-size
economics the user asked to measure. The 64 KiB limit remains the approved
starting point because no qualifying corpus reached that evaluation.

## Agent retrospectives and root-cause confidence

Retrospectives were requested in the exact retained conversations and limited
to observable actions, tool responses, and saved artifacts. Hidden reasoning
was neither requested nor accepted as evidence.

| Finding | Independent evidence | Agent account | Root-cause confidence |
| --- | --- | --- | --- |
| Baseline Task-root alias | Exact saved topology and validator result | Sol reported deliberate reuse of the general Task locator | High for immediate cause; representation choice was not inferred |
| Pre-fix empty `system/` | Assigned-root readback | Spark acknowledged treating the archive as sufficient | High for saved-state failure |
| Work missed interview | Later-visible exact conversation | Work reported read-only discovery ending at the interview | High for controller miss; provider mechanism unknown |
| Sol B timezone meaning | Exact canonical readback | Sol traced the value to its setup builder and identified checks that missed semantic comparison | High for immediate generation/check gap |
| Spark B partial setup | Exact installed files, entrypoint, pages and references | Spark reported failed/timed-out subagents and incomplete batches | High for incomplete saved state; moderate for provider cause |
| Work B missing intent evidence | Exact conversation plus independent saved-state audit | Work confirmed no independent intended-byte copy and no configured-entrypoint readback | High for evidence gap; internal reason unknown |

## Controller and evaluator incidents

These incidents are not counted as product failures unless an independent
product artifact also failed.

| Round | Incident | Treatment in grading |
| --- | --- | --- |
| Captured baseline | Spark wrong-composer task; Work interview missed during a browser hang | Unintended task excluded; Work graded pending/incomplete |
| Unchanged pre-fix | Early receipt writers failed; stale oracle rejected; image reads first failed local call validation | Unusable observations discarded; exact oracle rebuilt; only proven-no-effect reads retried |
| Post-fix A | Controller packet contained conflicting interval values; one capture needed correction; Work action was interrupted by provider review | Corrected before ingestion; saved state graded independently; no blind retry |
| Post-fix B | Interview answer omitted destination; duplicate Sol controller task; stale Spark clipboard task; one local read receipt lost before recovery | Invalid tasks stopped/excluded; destination supplied safely; evidence sink re-preflighted |

Post-fix browser routes used separate conversations, controllers, serial tab
operation, Drive roots and evidence areas. They shared the user's signed-in
Chrome profile, cookies, provider account state and unknown provider memory. No
account-level or browser-profile isolation is claimed.

## Principle and use-case coverage

| Principle or use case | What this cycle establishes | Remaining limit |
| --- | --- | --- |
| Drive as canonical shared memory | Saved setup state can be independently traversed and checked from Drive. | No tested ingestion or fresh-agent query qualified. |
| Fresh one-link setup | All routes discovered the starter and interview path. | Setup was not repeatable across the three target routes. |
| Agent-led, replaceable operation | Sol, Spark and Work each attempted the same semantic setup through their own capabilities. | Provider behavior and admission limits still diverge. |
| Bounded storage and retrieval | Every audited canonical page stayed below 65,536 bytes; finite references and continuations were checked. | No realistic Knowledge/Task corpus or size-cost comparison ran. |
| Truthful coverage and completion | The hard gate prevented incomplete setups from being called ready for ingestion. | General interrupted-write recovery remains outside MVP. |
| Metadata-only email identity | The installed contract and source oracle retained the approved rules. | No route ingested email, so live identity behavior was unexercised. |
| Knowledge and source-linked answers | Not exercised. | No common questions ran. |
| Canonical tasks and synchronization | Distinct canonical Task roots were checked. | No task extraction, completion review, or task-app synchronization ran. |
| Briefs and audio | Not exercised. | No output generation or delivery was authorized in this cycle. |
| Agent replacement and continuity | The starter and saved-state audits required no prior conversation as canonical memory. | No fresh agent queried a completed ingested instance. |

## Architecture backlog

The following remain unimplemented because they would select new architecture:

1. a persisted Task lifecycle discriminator or partition selector;
2. a persistent installation manifest or installed-state record; and
3. a possible rule requiring Task continuation descendants, not only their root
   pages, to have disjoint ownership.

Each proposal requires the user's explicit approval with alternatives and
tradeoffs before implementation. The observed cycle does not justify silently
adding any of them.

General interrupted-write repair, centralized job management, automated upgrade
and migration machinery, concurrent writers, task-app synchronization,
completion promotion, outbound delivery, audio, and scheduling also remain
outside this qualification.

## What is fixed and what remains

### Fixed or materially improved

- The Task-root alias is rejected by the helper and forbidden by setup/storage
  instructions.
- Empty or changed immutable installation material cannot satisfy the documented
  setup gate.
- Bootstrap validation is sequenced after configured-entrypoint derivation and
  uses actual saved canonical page bytes.
- Source-oracle, pagination, reference traversal, receipt, and export-evidence
  checks are stricter and preserve unknowns instead of converting them to empty
  or successful states.
- Browser isolation claims now match the isolation actually achieved.

### Still open

- Setup completion is not repeatable across the three routes.
- Work's configured-entrypoint intended-byte evidence gap repeated twice.
- Sol B introduced a timezone-meaning defect that its local checks did not catch.
- Spark B did not finish a complete, reference-resolved canonical bootstrap.
- Sol ingestion dispatch remains blocked by the host approval boundary.
- No ingestion, semantic retrieval, or page-size economics were qualified.
- Controller and local evidence-capture operation still produced contained
  mistakes that make efficiency comparisons unreliable.

## Stop and next action

The authorized autonomous cycle is complete. Do not fix the new post-fix issues,
repair trial instances, run another setup, or attempt ingestion from these
instances. The next action is joint review with the user.

After review, the smallest responsible next cycle would first decide whether the
Sol timezone defect, Spark incomplete-execution pattern, and Work exact-intent
evidence gap have supported nonarchitectural treatments. Any treatment that
adds persisted state, a new canonical selector, a recovery mechanism, or a new
Drive layout must return for explicit architecture approval before implementation.

