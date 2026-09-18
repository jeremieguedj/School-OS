# Autonomous remediation issue and treatment ledger

Status: the captured round-two baseline and the unchanged pre-fix round are
recorded. Every observed boundary now has a treatment class, disposition and
post-fix observable. The selected class A and B treatment set is prepared for
integration and validation; post-fix rounds A and B have not run. Class C items
remain unimplemented architecture backlog. Class D items receive no speculative
product fix.

The governing execution plan is the
[autonomous remediation cycle](AUTONOMOUS-REMEDIATION-CYCLE.md). The underlying
public evidence is the [round-two trial result](ROUND-2-TRIAL-RESULTS.md), its
[root-cause retrospective](ROUND-2-ROOT-CAUSE-RETRO.md), the
[unchanged pre-fix results](AUTONOMOUS-PREFIX-RESULTS.md), the
[restart plan](PLAN.md), and the [product principles](../../product-principles.md).
Private evidence is intentionally absent from this file.

## How to read this ledger

Each stable ID names one independently distinguishable failure boundary. A
tested-agent action, a product implementation defect and an evaluator/controller
incident remain separate even when they contributed to the same failed route.
Observed facts, later agent/provider summaries, coordinator inference and
unknowns are also separate. A provider summary can support an inference, but it
does not prove an internal decision, dispatch or remote effect.

Treatment class and disposition use the two pre-treatment observation sets under
the cycle plan. The classes are:

- **A:** implement an already approved architecture or contract;
- **B:** make a routine nonarchitectural repair;
- **C:** backlog a new or changed architecture decision for explicit approval;
- **D:** apply no product treatment because the supported boundary is a provider,
  tested-agent, environment or evaluator issue, or the cause remains unknown.

A test, instruction or example can make an architecture decision, so
classification applies to every artifact. Selected changes remain subject to
exact diff review and validation before publication.

## Rollback and evidence baseline

All future treatment entries use this exact pre-treatment rollback boundary:

| Baseline item | Exact value |
| --- | --- |
| Public source commit | `db68b12840aab3d0c94cfbb7d036a85f31b311f2` |
| Immutable tag and release | `school-os-autonomous-remediation-baseline-2026-09-17` |
| Tested starter | `school-os-starter-2026-09-17-round-2` / `School-OS-setup-round-2.zip` / 113045 bytes / SHA-256 `5cabbe0779c39a8ac547ee17ec8365cb0d244a95591cccc20658aab27e142f50` |
| Website baseline | Hosted version 25 |
| Website source commit | `708d46611cbf2175d4bc68b7c5cb53e96826083e` |

The round-two artifact that first exposed these issues was built from source
commit `aae44ef13be8392130f9b5aec7889b040c0ca45b` and published as immutable
starter `school-os-starter-2026-09-17-round-2`. The cycle baseline above preserves
the later public reports and continuity state as well as that tested artifact's
provenance. Repository and website rollback remain separate operations.

## Issue index

| Stable ID | Route or layer | Short title | Established boundary |
| --- | --- | --- | --- |
| `AR-R2-SOL-001` | Sol tested agent and representation specification | Active and completed Task roles shared one locator | Invalid saved topology; concrete correct representation remains unapproved |
| `AR-R2-SOL-002` | Bootstrap validator implementation | Invalid Task-route alias returned `valid` | Validator blind spot independently established |
| `AR-R2-SPARK-001` | Gemini Spark tested agent | Setup-only request entered a retrieval-labeled action | Visible authorization-boundary divergence; mailbox dispatch unproven |
| `AR-R2-CTRL-SPARK-001` | Evaluator/controller UI routing | Interview answers created a second unintended task | Controller incident; exact creation path and effects unknown |
| `AR-R2-CTRL-WORK-001` | Evaluator/controller observation | Completed Work interview was missed and control later hung | Controller incident; no Work tested-agent or product failure established |
| `AR-PF-SOL-001` | Sol dispatch boundary | Ingestion request rejected twice before delivery | Provider/platform admission failure; no Gmail or ingestion effect |
| `AR-PF-SPARK-001` | Spark setup and setup completion gate | Setup claimed complete with empty installed `system/` | Product instruction/check gap independently established |
| `AR-PF-WORK-001` | ChatGPT Work provider route | Setup stalled after the assigned root was visibly supplied | Provider-side cause unknown; no School-OS defect established |
| `AR-PF-CTRL-SPARK-001` | Spark evaluator/controller | Attempted tab export was unsupported | Visible task and independent Drive evidence remained available |
| `AR-PF-EVAL-RECEIPT-001` | Sol evaluator | Three early local receipt-writer protocols did not close cleanly | Results discarded; fresh reads followed a successful sink preflight |
| `AR-PF-EVAL-ORACLE-001` | Independent source evaluator | Prior oracle was stale and incompletely bound | Evaluator preflight correctly blocked reuse; exact-interval oracle rebuilt |
| `AR-PF-EVAL-CALL-001` | Independent source evaluator | Three inline-image reads first omitted a required access argument | Local pre-dispatch input failure; safe corrected retries succeeded |
| `AR-ARCH-TASK-001` | Architecture backlog | Possible persisted Task partition selector | New canonical representation; neither recommended nor implemented |
| `AR-ARCH-INSTALL-001` | Architecture backlog | Possible persistent installation manifest | New installer/lifecycle state; neither recommended nor implemented |

## `AR-R2-SOL-001` — Active and completed Task roles shared one locator

**First observed and earliest proven divergence.** In the captured round-two Sol
route, independent saved-state review found that the logical Active Tasks route
and Completed Task history route both resolved to the same undifferentiated,
empty Task `record_locator` root. The temporary manifest contained 24 logical
roles but only 23 unique roots. Exact readback established that this draft was
persisted. The saved topology violated the already required separation between
the two bounded Task routes, so setup failed.

**Agent summary.** Sol later reported that it understood the roles as logically
different but deliberately reused the general Task locator because the available
selector expressed the Task family without an active/completed discriminator.
It identified that reuse as the earliest choice that produced the defective
artifact. This is a retrospective tested-agent account, not an independently
captured internal decision.

**Coordinator inference and confidence.** The saved topology strongly
corroborates Sol's account. Confidence is **high** that locator reuse directly
created the contract-invalid setup. Evidence is **insufficient** to choose the
correct concrete representation.

**Unknowns.** The evidence does not establish whether the intended representation
should use distinct locator pages, a different directory structure, or a newly
approved discriminator. It also does not establish the downstream effect on
ingestion or queries because the setup gate stopped those stages.

**Cause classification.** The observed artifact includes a tested-agent
generation decision. It also exposes a specification/representation gap: the
semantic separation was approved, while the concrete locator representation was
not selected by this evidence. No provider/control failure or evaluator incident
caused the collision.

**Principle and contract grounding.** The
[decision-authority principle](../../product-principles.md#decision-authority)
forbids filling an unapproved representation gap implicitly. The
[design priorities](../../product-principles.md#design-priorities) require
deterministic behavior, bounded execution and canonical meaning independent of
the executing agent. The restart plan's
[approved architecture and operating choices](PLAN.md#approved-architecture-and-operating-choices)
retain distinct bounded canonical routes and Drive as the shared source of
truth. The first-use setup use case requires a fresh agent to persist a valid,
discoverable instance.

**Treatment class:** **A** for the supported nonalias topology instruction;
**C** only for the separate persisted-selector proposal tracked as
`AR-ARCH-TASK-001`.

**Disposition:** select the smallest approved-architecture treatment: require
Active Tasks and Completed Task history to use different existing Task root page
IDs while retaining the existing Task-family selector. Do not add a canonical
partition field.

**Expected post-fix observable.** A fresh setup saves two different owned Task
root page IDs and does not need a new selector field. A shared root cannot support
a setup-complete claim.

**Prepared diff and validation status.** `operations/storage.md` and
`operations/setup.md` state the nonalias rule. `helpers/bootstrap_contract.py`
and its prepared check enforce the observed topology. The combined diff is not
yet integrated or functionally validated at this ledger update.

**Rollback baseline:** source commit
`db68b12840aab3d0c94cfbb7d036a85f31b311f2`, immutable tag/release
`school-os-autonomous-remediation-baseline-2026-09-17`.

| Round slot | Result for this issue |
| --- | --- |
| Captured round two | **Observed:** invalid shared locator; setup failed |
| New unchanged pre-fix round | **Did not recur:** Sol used two distinct Task roots and setup passed |
| Post-fix round A | `pending` |
| Post-fix round B | `pending` |

## `AR-R2-SOL-002` — bootstrap validator accepted the invalid alias

**First observed and earliest proven divergence.** For the same saved Sol
bootstrap, `bootstrap_contract` returned `valid` with zero diagnostics. Independent
topology review showed that the two required Task roles shared one root. The
validator's manifest selection treated both roles through the same Task-family
selector and did not reject the alias.

**Agent summary.** Sol reported that validation checked each named role's family
and selector but did not test whether two semantically distinct roles resolved to
one root. This summary agrees with the saved manifest and validator result but
remains a retrospective account of what the agent relied on.

**Coordinator inference and confidence.** Confidence is **high** that the
validator had an alias-detection blind spot for the observed manifest shape and
therefore produced a false valid result. The evidence does not justify a claim
about every validator rule or every possible manifest shape.

**Unknowns at the observation point.** The captured evidence alone did not show
whether other role labels or manifest shapes could bypass the same check, and it
did not select a persisted representation. `AR-R2-SOL-001` records the later
authorized disposition: use two distinct existing Task locator roots without a
new selector.

**Cause classification.** Product implementation failure. The independent
review caught the defect, so no evaluator/controller incident caused it. No
provider or connector failure is established.

**Principle and contract grounding.** The
[design priorities](../../product-principles.md#design-priorities) require
deterministic procedures and verification rather than conversational intuition.
The approved setup path requires configuration and canonical bootstrap to be
persisted and checked before setup can be treated as complete. Validation must
therefore reject evidence that contradicts the installed topology contract.

**Treatment class:** **A**.

**Disposition:** require the reserved `active-tasks` and
`completed-task-history` roles exactly once, require both to name the existing
Task record-locator topology, and reject one root ID assigned to both. This
realizes the already approved separate bounded roots without adding a persisted
field or selector.

**Expected post-fix observable.** A missing, renamed or duplicated required role
cannot pass; a reserved role mapped to a non-Task topology cannot pass; and a
manifest assigning one root to both required roles returns `invalid` with
`task_role_root_alias`. Exactly one correctly bound role per distinct owned Task
root remains eligible for validation.

**Prepared diff and validation status.** `helpers/bootstrap_contract.py`,
`helpers/prepared_checks/check_bootstrap_contract.py` and `helpers/README.md`
contain the checker, fictional regression case and operator explanation. The
combined local prepared-check suite ran on 2026-09-18: all 73 tests passed, and
Python compilation passed. The treatment commit and immutable starter binding
remain pending publication at this ledger update.

**Rollback baseline:** source commit
`db68b12840aab3d0c94cfbb7d036a85f31b311f2`, immutable tag/release
`school-os-autonomous-remediation-baseline-2026-09-17`.

| Round slot | Result for this issue |
| --- | --- |
| Captured round two | **Observed:** invalid topology returned `valid` with no diagnostic |
| New unchanged pre-fix round | **Did not recur:** the distinct-root bootstrap returned `valid`; alias rejection itself remained unexercised |
| Post-fix round A | `pending` |
| Post-fix round B | `pending` |

## `AR-R2-SPARK-001` — setup crossed toward retrieval before authorization

**First observed and earliest proven divergence.** The main Spark task received a
setup-only request. Its interview answer reserved mailbox use for a later,
separately authorized read-only ingestion. Before visible setup completion and
without that separate request, Spark entered an action group labeled as
retrieving school communications. The controller stopped it. Spark did not claim
setup completion, and no saved state was observed in its assigned root.

The visible stopped group showed local-computer action labels and no Gmail tool
label. Those observations prove the premature transition at the planning/status
layer. They do not prove that a Gmail request, message fetch or other provider
effect dispatched.

**Agent summary.** Spark later reported that it made no Gmail search or fetch.
It said it recognized the setup-only boundary but incorrectly treated concrete
future mailbox filters as permission to start the ingestion workflow. It called
that an inference error and said the starter did not instruct it to ingest. It
could not identify the component that produced the retrieval label.

**Coordinator inference and confidence.** Confidence is **high** that the visible
transition violated the setup-only authorization boundary. Confidence is
**moderate** in Spark's explanation that it conflated future scope with current
permission because that explanation fits the visible sequence but is self-report.
Evidence is **insufficient** to conclude whether a mailbox operation dispatched.

**Unknowns.** Provider-side dispatch, any effect of the visible local-computer
actions, the origin and precise meaning of the retrieval label, and any partial
state outside the assigned root remain unknown.

**Cause classification.** The visible divergence is a tested-agent decision.
No product/specification gap is established because both the product principles
and the supplied instruction separated setup from ingestion. The retrieval
label's provider/control origin remains unknown. The separate wrong-composer
incident is tracked as `AR-R2-CTRL-SPARK-001`.

**Principle and contract grounding.** The
[approved first-use setup direction](../../product-principles.md#approved-first-use-setup-direction--2026-09-16)
states that a starter link authorizes access to setup material, not source
ingestion, and that setup and ingestion retain separate instructions and
authorization boundaries. The same section requires the parent interview before
the instance is configured. Capability-led portability requires an agent to
declare limits instead of inferring authority from a vendor or future choice.

**Treatment class:** **D**.

**Disposition:** no product change. The setup/ingestion authorization boundary was
already explicit and the visible transition did not recur in the unchanged
pre-fix Spark route. Controller guard improvements are tracked separately.

**Expected post-fix observable.** No provider-specific product behavior is
promised. A repeat premature transition remains a route failure and is stopped at
the boundary.

**Exact file diff.** `none` for this tested-agent issue. The general controller
method is recorded under `AR-R2-CTRL-SPARK-001`.

**Rollback baseline:** source commit
`db68b12840aab3d0c94cfbb7d036a85f31b311f2`, immutable tag/release
`school-os-autonomous-remediation-baseline-2026-09-17`.

| Round slot | Result for this issue |
| --- | --- |
| Captured round two | **Observed:** premature retrieval-labeled transition; mailbox dispatch unproven |
| New unchanged pre-fix round | **Did not recur:** Spark completed setup-only work and made no ingestion request |
| Post-fix round A | `pending` |
| Post-fix round B | `pending` |

## `AR-R2-CTRL-SPARK-001` — interview answers created a second unintended task

**First observed and earliest proven divergence.** The Spark controller submitted
interview answers through the top-level composer instead of the verified main
task composer. A second unintended Spark task appeared. This happened outside
the intended route and is separate from the main task's premature transition.

**Agent or provider summary.** `unavailable`. The public evidence contains no
supported provider explanation of the second task's exact creation path or
effects. The incident is attributed to controller/UI routing from the observed
submission path, not to hidden agent reasoning.

**Coordinator inference and confidence.** Confidence is **high** that the wrong
composer submission was an evaluator/controller incident and created an
unintended second task. Evidence is **insufficient** to describe the UI's exact
internal routing or any remote effects of that task.

**Unknowns.** The precise orchestration path, whether the unintended task took
any action, and whether it created state outside the intended route remain
unknown. It is not evidence that the main Spark task dispatched mailbox work.

**Cause classification.** Evaluator/controller incident. No product failure,
tested-agent decision or connector failure is established for this second-task
creation.

**Principle and contract grounding.** The autonomous cycle requires each route
to have a distinct conversation, controller, tab, Drive root and evidence area,
with task identity recorded before an interview answer or follow-up is sent.
This method protects the first-use use case and prevents one route's evidence or
authority from being attributed to another.

**Treatment class:** **B**.

**Disposition:** require an exact provider/task/conversation/route/root/stage
binding and a visibly task-bound composer before any follow-up. A top-level or
mismatched composer blocks the send.

**Expected post-fix observable.** A follow-up from a top-level, unknown or
mismatched composer is rejected before dispatch; only the exact bound task at the
expected stage may receive the interview answer.

**Prepared diff and validation status.** `helpers/trial_evaluation.py`, its
prepared check, `TRIAL-PROTOCOL.md`, `TRIAL-PROMPTS.md` and the trial report
template define and exercise binding/state rules. The combined diff is not yet
integrated or functionally validated at this ledger update.

**Rollback baseline:** source commit
`db68b12840aab3d0c94cfbb7d036a85f31b311f2`, immutable tag/release
`school-os-autonomous-remediation-baseline-2026-09-17`.

| Round slot | Result for this issue |
| --- | --- |
| Captured round two | **Observed:** wrong-composer submission and unintended second task |
| New unchanged pre-fix round | **Did not recur:** interview answer stayed in the exact Spark task |
| Post-fix round A | `pending` |
| Post-fix round B | `pending` |

## `AR-R2-CTRL-WORK-001` — the controller missed Work's completed interview

**First observed and earliest proven divergence.** The exact ChatGPT Work task
was later verified by its title, Work label and matching opening request. Its
first response, marked at 58 seconds, contains the expected setup interview and
preserves the separation between setup and later source processing. The original
controller observed only the running state, then browser control became
unresponsive and was interrupted without retry. No interview answer was sent,
so Work correctly remained pending and no setup was observed in its assigned
root.

**Agent summary.** Work reported that it temporarily retrieved and inspected the
starter, read the setup instructions and then asked the interview questions. It
said it made no persistent Drive write and performed no Gmail, ingestion, task,
delivery or scheduling action. The visible unanswered interview independently
supports the pending state. The detailed action sequence and absence of every
listed downstream effect remain provider claims because the underlying action
records were not fully expanded and audited.

**Coordinator inference and confidence.** Confidence is **high** in the task
identity, completed interview, unanswered state, correct pending outcome and
controller observation failure. It is likely that the controller missed the
response during or after the recorded processing interval. Evidence is
**insufficient** to diagnose the hang's technical cause or independently prove
the complete tool-action history.

**Unknowns.** The technical cause of the control hang, the exact moment at which
the response ceased to be visible to the controller, and the complete underlying
read-only action chronology remain unknown. The configuration choices were never
sent, so later Work setup behavior is unexercised.

**Cause classification.** Evaluator/controller observation incident, with an
unknown browser-control or provider-control cause. No Work tested-agent decision,
product/specification gap or product implementation failure is established.

**Principle and contract grounding.** The
[approved first-use setup direction](../../product-principles.md#approved-first-use-setup-direction--2026-09-16)
requires the agent to discover the starter and interview the parent before
persisting the configured instance. Work visibly followed that path through the
interview. The cycle's evidence rules require observable task identity and
effects rather than assuming that a running state is the final result.

**Treatment class:** **B** for controller observation state; **D** for any
unsupported product repair.

**Disposition:** record ordered controller states so a later final response
supersedes an earlier running snapshot, and stop follow-ups when observation or
binding is unavailable. This improves evidence collection and does not claim to
fix Work.

**Expected post-fix observable.** The evaluator cannot leave a route marked
active solely from a stale running snapshot when a later final response is
visible. If current state cannot be established, it records
`controller_observation_unavailable` and sends nothing.

**Prepared diff and validation status.** The same controller-state files listed
for `AR-R2-CTRL-SPARK-001` implement this evidence rule. The combined diff is not
yet integrated or functionally validated at this ledger update.

**Rollback baseline:** source commit
`db68b12840aab3d0c94cfbb7d036a85f31b311f2`, immutable tag/release
`school-os-autonomous-remediation-baseline-2026-09-17`.

| Round slot | Result for this issue |
| --- | --- |
| Captured round two | **Observed:** completed interview missed; control later hung; setup remained unanswered |
| New unchanged pre-fix round | **Different incident:** Work visibly received the answer but stalled; see `AR-PF-WORK-001` |
| Post-fix round A | `pending` |
| Post-fix round B | `pending` |

## `AR-PF-SOL-001` — ingestion messages were rejected before delivery

**First observed and earliest proven divergence.** Sol independently passed the
unchanged pre-fix setup gate. The separate ingestion message then returned an
approval rejection before delivery to the tested task. Evidence established no
ingestion turn, no Gmail read and no ingestion write. The one permitted retry was
made only after proving no dispatch and no effect; it was rejected at the same
pre-delivery boundary.

**Agent or provider summary.** `unavailable`. The tested agent did not receive
either message, so it could not explain the rejection. The approval response
identified the requested bounded personal-data operation as the reason for the
platform stop despite the user's standing authorization.

**Coordinator inference and confidence.** Confidence is **high** that this was a
child-task provider/platform admission failure and that neither attempt reached
the tested agent or Gmail. It does not test School-OS ingestion behavior.

**Unknowns.** The evidence does not establish which internal approval rule
overrode the supplied authorization or whether the same admission behavior will
occur for a browser provider route.

**Cause classification.** Provider/platform failure outside the product. The
controller correctly separated the first attempt, proved no effect, used its one
allowed retry and stopped.

**Principle and contract grounding.** Authorization remains explicit; no
provider rejection may be bypassed by weakening privacy controls or inventing a
new dispatch route. Unknown or absent effects stay visible.

**Treatment class:** **D**.

**Disposition:** no product treatment. Preserve the evidence and report the
stage as not dispatched.

**Expected post-fix observable.** None is promised by a product change. If the
platform admits a later request, the route may proceed under the unchanged
ingestion contract. If it rejects again, it remains a provider/platform result.

**Exact file diff:** `none`.

**Rollback baseline:** source commit
`db68b12840aab3d0c94cfbb7d036a85f31b311f2`, immutable tag/release
`school-os-autonomous-remediation-baseline-2026-09-17`.

| Round slot | Result for this issue |
| --- | --- |
| Captured round two | Unexercised; setup failed before ingestion |
| New unchanged pre-fix round | **Observed twice:** initial and one proven-no-dispatch retry rejected before delivery; no Gmail or ingestion effect |
| Post-fix round A | `pending` |
| Post-fix round B | `pending` |

## `AR-PF-SPARK-001` — setup claimed complete with no installed system tree

**First observed and earliest proven divergence.** Spark claimed setup complete
after saving and checking a valid 27-page instance graph. Independent Drive
readback found the installed `system/` folder empty. The entrypoint referenced
reusable system paths that therefore had no installed targets. The setup gate
failed, and no ingestion request followed.

**Agent summary.** In the retained task, Spark reported that it copied the
starter ZIP, created the three top-level areas and wrote the canonical JSON
pages, but sent no tool call to populate `system/`. It treated the ZIP beside the
empty folder as adequate placement. It checked the instance pages with the
bootstrap helper but did not list or read the system folder before claiming
completion.

**Coordinator inference and confidence.** Confidence is **high** that the
immediate failure was omitted reusable system material and that the completion
gate covered only the canonical page graph. The evidence does not establish
Spark's motive for the omission.

**Unknowns.** Whether a future provider might discover and unpack the retained
ZIP as a fallback was not tested and cannot make the configured entrypoint's dead
relative references valid.

**Cause classification.** Tested-agent setup decision plus a product
instruction/verification gap. The approved architecture already requires
`system/` to contain reusable instructions; the missing check was an
implementation gap, not a missing architecture decision.

**Principle and contract grounding.** A capable fresh agent must be able to start
from the Drive entrypoint without prior conversation or local files. Setup must
read back what it saved before claiming success. Reusable system material and
canonical instance state remain distinct.

**Treatment class:** **A**.

**Disposition:** add a transient finite installation-material comparison before
and after configuration. Compare exact starter-supplied root documents and every
`system/` member with complete saved bytes and ancestry. For the final check,
replace the starter entrypoint expectation with the exact intended configured
`START-HERE.md` bytes; every other expected byte remains unchanged. Independently
derive the temporary bootstrap manifest from that complete saved entrypoint and
require each role, root, family and scope to be visible there. The phase-two
material check, entrypoint-derivation gate and canonical bootstrap check must all
pass.

**Expected post-fix observable.** An empty, partial, altered, unread or wrongly
placed `system/` prevents a setup-complete claim. So does an exact but unusable
entrypoint from which the bootstrap manifest cannot be derived. Exact
phase-specific material, a readable entrypoint-derived manifest and a valid
canonical bootstrap permit completion. No persistent installer record is
created.

**Prepared diff and validation status.** `helpers/bootstrap_contract.py`,
`helpers/prepared_checks/check_bootstrap_contract.py`, `helpers/README.md`,
`operations/setup.md`, `operations/storage.md` and `docs/setup-bundle.md` contain
the pure comparison, prepared fictional cases and operator instructions. The
combined local prepared-check suite ran on 2026-09-18: all 73 tests passed, and
Python compilation passed. The treatment commit and immutable starter binding
remain pending publication at this ledger update.

**Rollback baseline:** source commit
`db68b12840aab3d0c94cfbb7d036a85f31b311f2`, immutable tag/release
`school-os-autonomous-remediation-baseline-2026-09-17`.

| Round slot | Result for this issue |
| --- | --- |
| Captured round two | Unexercised as a distinct audit; Spark did not complete setup |
| New unchanged pre-fix round | **Observed:** empty `system/`, valid 27-page instance graph, false setup-complete claim |
| Post-fix round A | `pending` |
| Post-fix round B | `pending` |

## `AR-PF-WORK-001` — Work stalled after receiving the assigned root

**First observed and earliest proven divergence.** Work received the setup
interview answers, including the exact assigned Drive root. It then stayed in a
running/question state for 25 minutes 50 seconds without another visible
question, completion or failure. After one bounded stop, the assigned root read
back empty.

**Agent summary.** Work said it had been waiting for the permanent folder link
and reported no persistent Drive mutation. The stated wait condition conflicts
with the visible conversation, where that link had already been supplied. In a
targeted follow-up, Work confirmed the message exists in external task history
but said it was absent from the setup turn's model-visible state. It located the
earliest observable non-incorporation at the pending questionnaire: the
submitted URL did not resolve that question, which later returned an aborted
status, and no assistant action used the answer.

**Coordinator inference and confidence.** Confidence is **high** that the task
stalled after receiving the required answer and did not complete setup.
Confidence is **high** that its stated wait condition is inconsistent with the
visible input. The technical cause remains unknown.

**Unknowns.** Input delivery loss, failure to resume the pending question,
branch/routing mismatch and other provider-side defects cannot be distinguished
without provider event and model-input logs. Raw connector receipts were not
exposed, so the provider's detailed no-effect account is not independently
complete.

**Cause classification.** Tested-provider incident with unknown technical cause.
The empty assigned root supports no saved setup. No School-OS instruction or
implementation defect is established.

**Principle and contract grounding.** Unknown effects stay unknown and setup
cannot pass without verified saved state. A provider stall cannot justify hidden
state, a blind retry or a route-specific product patch.

**Treatment class:** **D** for product behavior. The general class B controller
state treatment improves observation but does not repair Work.

**Disposition:** no product fix. Preserve the task, visible contradiction and
unknown cause. Apply only the route-neutral controller binding/state method.

**Expected post-fix observable.** The evaluator reports the current bound task
state and stops safely when it cannot establish completion or effect. Work may
still stall; that outcome must remain a provider result.

**Exact product diff:** `none`. Controller files are listed under
`AR-R2-CTRL-WORK-001`.

**Rollback baseline:** source commit
`db68b12840aab3d0c94cfbb7d036a85f31b311f2`, immutable tag/release
`school-os-autonomous-remediation-baseline-2026-09-17`.

| Round slot | Result for this issue |
| --- | --- |
| Captured round two | A different controller missed the completed interview; no Work product failure established |
| New unchanged pre-fix round | **Observed:** 25m50s stall after visible root answer; retrospective wait claim contradicted the conversation |
| Post-fix round A | `pending` |
| Post-fix round B | `pending` |

## `AR-PF-CTRL-SPARK-001` — browser tab export was unsupported

**First observed and earliest proven divergence.** After Spark's final setup
response was visibly complete, the controller attempted an optional tab-content
export command that Chrome did not support. The final response remained visible
in the marked task, and the assigned Drive state was audited independently.

**Coordinator inference and confidence.** Confidence is **high** that this was a
controller/browser export limitation. It did not cause Spark's missing system
tree and did not remove the evidence needed to grade setup.

**Unknowns.** The browser did not expose why that export command was unavailable.

**Treatment class:** **D** for product behavior; the general class B controller
state method records visible-output evidence and export limits.

**Disposition:** no product fix and no unsupported exported artifact claim. Use
the visible bound-task response plus independent saved-state receipts.

**Expected post-fix observable.** An unavailable optional export is reported as
such and cannot invalidate independently preserved evidence or be presented as a
downloaded route report.

**Exact product diff:** `none`.

| Round slot | Result for this issue |
| --- | --- |
| Captured round two | Unexercised |
| New unchanged pre-fix round | **Observed:** optional export unsupported; visible and saved-state evidence remained available |
| Post-fix round A | `pending` |
| Post-fix round B | `pending` |

## `AR-PF-EVAL-RECEIPT-001` — early local receipt protocols were unusable

**First observed and earliest proven divergence.** During the independent Sol
setup audit, three early local receipt-writer protocols failed or did not close
cleanly. Their provider results were discarded without interpretation.

**Coordinator inference and confidence.** Confidence is **high** that this was an
evaluator capture incident. No reported setup finding relies on those attempts:
the evaluator completed an owner-only synthetic sink preflight and made fresh
reads whose receipts were saved and verified.

**Unknowns.** The unusable attempts do not support a provider success, failure or
effect claim.

**Treatment class:** **B** operational method; no new product behavior.

**Disposition:** enforce the already required sink preflight before evidence is
admitted and discard any provider observation whose private capture is not
usable. No new repository change is required beyond the selected evaluator
state/reporting package.

**Expected post-fix observable.** Only a provider result captured after a passing
owner-only sink preflight may support a finding; a capture failure is labeled an
evaluator incident.

**Exact product diff:** `none`. The existing sink helper remains unchanged; the
trial report template and controller-state reporting make the boundary explicit.

| Round slot | Result for this issue |
| --- | --- |
| Captured round two | Unexercised |
| New unchanged pre-fix round | **Observed and contained:** three unusable attempts discarded; fresh verified receipts supported the audit |
| Post-fix round A | `pending` |
| Post-fix round B | `pending` |

## `AR-PF-EVAL-ORACLE-001` — the available source oracle did not match the round

**First observed and earliest proven divergence.** Preflight found that the
available oracle named another interval, lacked complete digest binding for its
enumeration receipts and did not bind the source-input record. It was rejected
before use.

**Evaluator account and correction.** A bounded read-only rebuild exhausted 11
exact-address queries. It observed 17 unique candidates and retained all 17 only
after applying the exact half-open interval locally to supported comparable
timestamps. Provider-entry count is not logical-email count.

**Coordinator inference and confidence.** Confidence is **high** that reusing the
old oracle would have invalidated semantic grading and that the correction
produced an exact-interval-bound source set for later comparison.

**Unknowns.** Because no tested route reached ingestion, the corrected oracle's
ability to grade a route output remains unexercised.

**Cause classification.** Evaluator-method gap caught before route grading; no
product or provider failure.

**Principle and contract grounding.** Coverage claims require explicit exhausted
scope and correct date meaning, timezone and precision. Independent expectations
must stay bound to their exact source evidence.

**Treatment class:** **B**.

**Disposition:** require an exact private round-manifest digest, exact interval
fields, explicit exhaustion, comparable arrival evidence and local half-open
filtering before an oracle may grade a route.

**Expected post-fix observable.** A differently bound or stale oracle is
rejected. The exact bound input deterministically yields the same included and
excluded entries, with an end-boundary entry excluded.

**Prepared diff and validation status.** `helpers/trial_evaluation.py`,
`helpers/prepared_checks/check_trial_evaluation.py`, `helpers/README.md`,
`TRIAL-PROTOCOL.md`, `TRIAL-PROMPTS.md` and the report template contain the
preflight and prepared fictional checks. The combined diff is not yet integrated
into a published starter. The local prepared-check suite ran on 2026-09-18: all
73 tests passed, and Python compilation passed. The treatment commit and
immutable starter binding remain pending publication at this ledger update.

**Rollback baseline:** source commit
`db68b12840aab3d0c94cfbb7d036a85f31b311f2`, immutable tag/release
`school-os-autonomous-remediation-baseline-2026-09-17`.

| Round slot | Result for this issue |
| --- | --- |
| Captured round two | No source-semantic audit ran |
| New unchanged pre-fix round | **Observed and corrected:** stale oracle rejected; exact interval rebuilt independently |
| Post-fix round A | `pending` |
| Post-fix round B | `pending` |

## `AR-PF-EVAL-CALL-001` — three image reads first failed local validation

**First observed and earliest proven divergence.** Three required inline-image
reads omitted the message access handle required by the connector. Each failed
locally before dispatch.

**Evaluator account and correction.** Preserved evidence established no dispatch
and no effect. The evaluator then issued one corrected request for each item with
the required access handle; all three succeeded. Those successful reads exposed
file references, but the new exact pixels or a faithful private rendering were
not available to the independent evaluator. Parent source, filename, MIME type
and byte size do not establish pixel equality. Image-specific expectations are
therefore unavailable for this round and no image-specific finding may be made.
Changed opaque handles remained access aids, not canonical identity.

**Coordinator inference and confidence.** Confidence is **high** that this was an
evaluator call-shape error and that the corrected reads were safe under the
no-dispatch retry rule. No provider error or product identity failure occurred.

**Unknowns.** The local rejection is fully classified. The image content itself
remains unqualified because the exact pixels were not independently reviewed;
later route-level use also remained unexercised.

**Cause classification.** Evaluator input error, corrected within the bounded
oracle preparation.

**Principle and contract grounding.** Provider handles are replaceable access
aids. Parent-bound metadata remains the attachment identity basis. Local input
failure is not provider failure, and retries require proven no effect.

**Treatment class:** **B** as part of oracle/controller preflight.

**Disposition:** validate required connector access arguments before dispatch and
retain distinct dispatch, provider-response and receipt states.

**Expected post-fix observable.** A missing required access argument stops
locally and cannot be labeled a provider failure. One corrected call is allowed
only after no dispatch and no effect are proved.

**Prepared diff and validation status.** The general observation and retry rules
are in the evaluator helper, prepared checks and trial protocol listed for
`AR-PF-EVAL-ORACLE-001`. No email or attachment identity rule changes.

**Rollback baseline:** source commit
`db68b12840aab3d0c94cfbb7d036a85f31b311f2`, immutable tag/release
`school-os-autonomous-remediation-baseline-2026-09-17`.

| Round slot | Result for this issue |
| --- | --- |
| Captured round two | Unexercised |
| New unchanged pre-fix round | **Observed and corrected:** three local no-dispatch failures; three bounded corrected reads succeeded |
| Post-fix round A | `pending` |
| Post-fix round B | `pending` |

## `AR-ARCH-TASK-001` — persisted Task partition selector

**Proposal.** Add a canonical discriminator such as active/completed to a Task
locator or record and use it to partition lifecycle views.

**Why it is architectural.** It would select a new persisted field, canonical
meaning and query contract. Several compatible representations remain plausible,
and no prior approval chooses among them.

**Treatment class:** **C**.

**Disposition:** architecture backlog; neither recommended nor implemented in
this cycle. The approved class A repair uses two different existing Task root
page IDs and therefore does not depend on this choice.

**Expected post-fix observable:** `unexercised` by design; no new selector appears
in the post-fix starter.

**Exact file diff:** `none`.

| Round slot | Result for this issue |
| --- | --- |
| Captured round two | Representation gap exposed but no representation approved |
| New unchanged pre-fix round | Distinct existing Task roots worked without a new selector |
| Post-fix round A | `pending` |
| Post-fix round B | `pending` |

## `AR-ARCH-INSTALL-001` — persistent installation manifest

**Proposal.** Save a canonical manifest or installed-state record describing
starter files, version and later drift.

**Why it is architectural.** It would add persistent installer/lifecycle state
and upgrade semantics that are outside the approved MVP. It would also increase
canonical data and Drive I/O.

**Treatment class:** **C**.

**Disposition:** architecture backlog; neither recommended nor implemented. The
selected class A check derives a finite expectation from the received starter,
uses it twice during setup and discards it.

**Expected post-fix observable:** `unexercised` by design; no installation
manifest or setup receipt persists in the instance.

**Exact file diff:** `none`.

| Round slot | Result for this issue |
| --- | --- |
| Captured round two | Not proposed |
| New unchanged pre-fix round | Empty system tree showed need for a completion gate, not persistent installer state |
| Post-fix round A | `pending` |
| Post-fix round B | `pending` |

## Stable evidence constraints

These are limits on what the captured round proves. They are not additional
product failures and must not be silently converted into treatments. Stable IDs
allow later rounds to state whether the same evidence limit remained.

| Stable ID | Constraint established in round two | Consequence for inference | Later slots |
| --- | --- | --- | --- |
| `AR-R2-EVID-SOL-001` | Sol's finite referenced setup targets and explicit derived-page continuations were reviewed, but the Drive listing route supplied no explicit end marker. | Exhaustive folder inventory remains unknown; a short or matching list cannot establish exhaustion. | Pre-fix: same constraint; the 28-page finite graph and explicit continuations were verified. Post-fix A/B: `pending`. |
| `AR-R2-EVID-SOL-002` | The public evidence does not establish complete content readback for every one of round-two Sol's 67 written files. | That round's bounded audited targets support their stated findings, but not a claim that every write was fully read back. | Pre-fix: a different route's 28 finite page bytes were fully read and matched declared sizes; the earlier-round limit remains. Post-fix A/B: `pending`. |
| `AR-R2-EVID-WORK-001` | Round-two Work action records were not fully expanded and independently audited. | Temporary starter retrieval and the claimed absence of every downstream action remain provider claims beyond visible state and assigned-root readback. | Pre-fix: raw connector receipts again were not exposed; the visible root-answer contradiction and empty-root readback are independently established. Post-fix A/B: `pending`. |
| `AR-R2-ENV-BROWSER-001` | Spark and Work use distinct tasks, controllers, tabs, roots and evidence areas but share one signed-in Chrome profile. | Cookies, account state, visible UI state and unknown provider memory are not isolated or measured; no account-level or provider-memory isolation claim is valid. | Pre-fix: constraint remained. Post-fix A/B: `pending`. |

## Cross-round update rules

Later updates must append evidence; they must not rewrite either pre-treatment
round. For every implemented class A or B treatment, replace the prepared-diff
status with the reviewed exact diff, validation actually run, treatment commit
and immutable starter binding. Post-fix A and B then record independent results
without a change between those two rounds.

A non-recurrence in one fresh route does not erase a captured issue. Two later
passes support repeatability only for the exact tested routes, accounts,
permissions, inputs and observed conditions. Unknown effects stay unknown unless
new independent evidence resolves them. Architecture-changing treatments remain
backlogged until explicitly approved.
