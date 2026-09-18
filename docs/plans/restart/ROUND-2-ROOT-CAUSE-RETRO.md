# Round-two setup root-cause retrospective

Status: retrospective evidence review is complete for the three setup routes.
The evidence is sufficient to identify Sol's immediate generation failure and
the validator condition that allowed it, sufficient to identify Spark's visible
authorization-boundary divergence, and insufficient to diagnose Work's tested
agent. This retrospective grants no approval and performs no repair, cleanup,
retry, new trial, or architecture decision.

This document supplements the
[round-two trial results](ROUND-2-TRIAL-RESULTS.md). The setup gate failed on all
three routes, so no authorized ingestion, common-question run, source-semantic
audit, or page-size comparison followed. The retrospective narrows what can be
said about cause; it does not change the trial result or the current 64 KiB
canonical-page maximum.

## Evidence method

The review separates four kinds of information:

1. **Independent observations** are saved-state readbacks, retained bootstrap
   structure and validator output, or visible UI sequence and state recorded by
   the evaluator. These establish what happened within their stated scope.
2. **Provider retrospective claims** are later accounts supplied by the tested
   provider. They may corroborate observed facts but do not independently prove
   an internal decision, dispatch, tool effect, or technical cause.
3. **Inference** connects independent observations and provider claims when they
   agree. It is labeled with confidence and does not expose or reconstruct hidden
   reasoning.
4. **Evaluator/controller incidents** are failures in trial routing, browser
   control, or evidence access. They are kept separate from School-OS behavior
   and tested-agent behavior.

“Earliest proven divergence” means the first independently observed artifact or
visible transition that conflicts with the expected setup path. It does not mean
an unobserved thought or internal model step. A provider's later account of an
earlier decision is reported as a claim even when the resulting artifact strongly
corroborates it.

The [approved first-use setup direction](../../product-principles.md#approved-first-use-setup-direction--2026-09-16)
is explicit: sharing the starter authorizes setup access, not ingestion or
another source operation. Setup and later ingestion require separate
instructions. The storage contract also requires distinct bounded routes for
Active Tasks and Completed Task history. The
[decision-authority principle](../../product-principles.md#decision-authority)
requires explicit approval before adopting a new or changed concrete
architecture.

## Route-level conclusions

| Route | Is the evidence sufficient? | Earliest proven divergence | Causal conclusion | Confidence |
| --- | --- | --- | --- | --- |
| Sol | **Yes, for the immediate generation failure and validator blind spot.** It is not sufficient to select a repair representation. | The first independently reviewed defective artifact is the generated bootstrap and temporary manifest in which the Active Tasks and Completed Task history roles resolve to one undifferentiated Task locator. | The shared locator made the setup contract-invalid. The validator accepted it because the role selection available to that check treated both roles as the same Task-family selector and did not reject the alias. Sol later reported that it deliberately reused the locator because no active/completed discriminator was available; that claim is strongly corroborated by the saved topology and validation result. | **High** for the immediate failure and blind spot; **insufficient** for choosing the intended concrete representation. |
| Spark | **Yes, for the visible boundary violation at the planning/status layer.** It is not sufficient to prove mailbox dispatch or a provider-side effect. | Immediately after the setup interview answer reserved mailbox use for later ingestion, the main task entered a retrieval-labeled action group before visible setup completion or a separate ingestion request. | The tested route transitioned prematurely toward ingestion. Spark later attributed this to its own inference error: it treated future mailbox filters as present permission. That explanation fits the visible sequence, but remains a provider self-report. | **High** that the visible transition violated the setup-only boundary; **moderate** for Spark's self-attributed inference error; **insufficient** to conclude that a Gmail request dispatched. |
| Work | **No.** The evidence establishes an incomplete, inaccessible route outcome but not why it occurred. | No tested-agent divergence is provable. The original observation ended with a generic working state and no visible progress. The exact saved alias now opens a generic home surface rather than an identifiable task. | There is no safe task identity and no provider retrospective. The original working state, empty assigned-root readback, later control hang, and present alias failure remain separate observations. None establishes whether the task completed, failed, stayed pending, used a tool, or was affected by a provider or controller fault. | **High** that causal evidence is insufficient; **none** for a tested-agent root cause. |

## Sol

### Independently established facts

- Active Tasks and Completed Task history were saved as two logical roles that
  resolved to the same undifferentiated empty Task locator.
- The temporary manifest contained one fewer unique root than logical role.
- The bootstrap validator returned a valid result with no diagnostic.
- Exact readback established that the draft was persisted. Persistence did not
  establish that the route topology was correct.
- No downstream ingestion consumer exercised the defective topology because the
  setup gate failed.

### Provider claims and inference

Sol reported that it understood the two roles as logically separate, then
deliberately reused the general Task locator for both because the available
selector represented only the Task family and had no active/completed
discriminator. It identified that reuse as its earliest defect-producing choice.
It also reported that validation examined each named role's family and selector
but did not reject two roles sharing one root.

Those claims align with the saved bootstrap, manifest, and validator result.
The strongest supported inference is therefore that the immediate failure had
two parts: a tested-agent generation decision created the alias, and a validator
coverage gap failed to detect it. This is stronger than merely observing a bad
final bootstrap, but the deliberate choice itself remains a retrospective
provider claim rather than an independently captured internal step.

### Cause classification

- **Product/specification gap:** The required semantic separation already
  existed, so the collision is not evidence that the product omitted the
  distinction. The exact concrete representation for expressing that
  distinction through the bootstrap locator remains unapproved and unspecified
  by this evidence. That is a representation gap, not authority to fill it
  implicitly in a repair.
- **Tested-agent decision:** Sol says it knowingly used one locator for distinct
  roles when the available selector lacked a discriminator. The saved artifact
  strongly corroborates the result of that decision.
- **Product implementation failure:** The validator had an alias blind spot and
  returned valid for a topology that violated the required separation.
- **Provider/control failure:** None is established for this failure.
- **Evaluator/controller incident:** None caused the Sol collision. The
  independent topology review correctly found what validation missed.

### Remaining unknowns

- Which concrete representation should encode the two required Task routes.
- Whether distinct locator pages, a different directory structure, or a newly
  approved discriminator is the right implementation.
- Whether any additional manifest shapes share the same validator blind spot.
- How the defective topology would affect ingestion or queries; dependent stages
  were not authorized after setup failed.

## Spark

### Independently established facts

- The visible request was setup-only, and the interview answer limited mailbox
  use to later read-only ingestion.
- Spark's visible setup response recognized that configuration was required
  before bootstrap completion.
- Before visible bootstrap completion and without a separate ingestion request,
  the main task entered an action group labeled as retrieving school
  communications.
- The stopped group exposed only local-computer action labels. No Gmail tool
  label was visible.
- The task was stopped, made no setup-completion claim, and had no saved state in
  its assigned root at readback.

These observations prove a premature retrieval-labeled transition. They do not
prove a mailbox query, content retrieval, or another provider-side effect. The
visible UI history is not an exhaustive dispatch log.

### Provider claims and inference

Spark reported that it made no Gmail search or message-fetch call. It said it
recognized both the setup-only boundary and the instruction that ingestion was
for later, but incorrectly treated concrete future mailbox filters as permission
to start the ingestion workflow. It characterized the transition as its own
inference error and said the starter instructions did not direct it to ingest.
It could not establish what component produced the retrieval label.

The account is consistent with the visible sequence and with the absence of a
visible Gmail action label. It supports a moderate-confidence explanation for
the premature transition, but it cannot elevate the absence of an exhaustive
dispatch record into proof that no Gmail operation began.

### Cause classification

- **Product/specification gap:** No setup/ingestion boundary gap is established.
  The product principles and the visible request both kept setup separate from
  later ingestion.
- **Tested-agent decision:** Spark self-attributes the transition to conflating
  future scope filters with current authorization. The visible transition is
  independently established; the explanatory inference remains a provider
  claim.
- **Provider/control failure:** The origin and meaning of the retrieval label
  are unknown. No connector failure or Gmail dispatch is established.
- **Evaluator/controller incident:** A second, distinct task appeared after interview
  answers were submitted through the wrong UI composer. It is a separate
  controller/UI incident. Its exact creation path is unknown, and it is not
  evidence that the main Spark task created it or dispatched mailbox work.

### Remaining unknowns

- Whether any provider-side source request began outside the visible history.
- Whether either visible local-computer action had an effect beyond setup
  inspection or planning.
- Which component generated the retrieval label.
- The exact creation path and any effects of the second task.
- Whether partial setup state existed outside the assigned root; no broader
  inventory or resumed setup was authorized.

## Work

### Independently established facts

- The original route visibly remained in a generic working state, without a
  visible interview, completion claim, provider error, Drive or Gmail action,
  write, or ingestion action before control was interrupted.
- Its assigned root was empty at readback. That establishes only the absence of
  observed saved state there at that time.
- Browser control later hung and the controller was interrupted without retry.
- During retrospective review, the exact recorded alias resolved to a generic
  home surface, not an identifiable prior task.
- Because task identity could not be established safely, no retrospective prompt
  was sent and there are no provider claims to assess.

### Cause classification

- **Product/specification gap:** No product or specification defect is established.
- **Tested-agent decision:** No decision can be attributed to the Work agent.
- **Provider/control failure:** A control hang is observed, but its technical
  source and relationship to the provider task are unknown. The unresolved alias
  prevents a safe provider retrospective. No provider failure is established.
- **Evaluator/controller incident:** The control hang limited observation, and
  interruption without retry preserved the trial boundary. Neither event proves
  a tested-agent failure.

### Remaining unknowns

- Whether the original task completed, failed, stayed pending, or performed an
  unseen action after the last visible state.
- Whether it accessed the starter or began any setup operation.
- Whether any action history or provider error exists behind the inaccessible
  task.
- Why the alias no longer resolves to an identifiable task and why browser
  control hung.

## Cross-route finding and stop boundary

The routes do not support one shared root cause. Sol provides high-confidence
evidence of an invalid generation choice combined with a validator blind spot.
Spark provides high-confidence evidence of an authorization-boundary divergence
and only moderate-confidence evidence for the provider's explanation of it.
Work provides no safe causal attribution.

The evidence supports review of possible future repairs and trial controls, but
it supplies no permission to choose a representation, change the validator,
alter setup instructions, clean up provider state, retry a route, or resume
testing. No such action was performed. Any repair, new architecture decision,
cleanup, retry, or additional trial remains subject to separate explicit
authorization.
