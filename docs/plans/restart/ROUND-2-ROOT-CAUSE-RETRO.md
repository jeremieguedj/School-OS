# Round-two setup root-cause retrospective

Status: retrospective evidence review is complete for the three setup routes.
The evidence is sufficient to identify Sol's immediate generation failure and
the validator condition that allowed it, sufficient to identify Spark's visible
authorization-boundary divergence, and sufficient to establish that Work
followed the expected setup path through an unanswered interview. The Work
trial stopped because the controller did not observe that response; its
technical failure remains unknown. This retrospective grants no approval and
performs no repair, cleanup, retry, new trial, or architecture decision.

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
| Work | **Yes, for the route outcome and expected setup behavior through the interview.** It is not sufficient to independently verify every claimed read-only tool action or diagnose the controller hang. | No tested-agent divergence is established. The verified task contains the expected setup interview after a 58-second processing interval, and no answer was supplied. The divergence is in trial observation: the original controller exposed only the running state and then hung rather than capturing the response. | Work remained correctly pending for required configuration answers. The gate did not pass because the interview was unanswered and no setup persisted. Work retrospectively reports successful temporary starter discovery with no persistent or downstream effect; the visible unanswered interview independently supports pending status, while the detailed tool history remains a provider claim. | **High** for task identity, interview, unanswered state, pending outcome, and controller observation failure; **insufficient** for the hang's technical cause or a complete independent audit of tool actions. |

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

- The exact prior task was verified by its title, Work label, and opening setup
  prompt.
- Its first response is marked as taking 58 seconds and visibly contains the
  expected setup interview. The questions cover the required configuration and
  optional tool choices, and the response preserves the separation between
  setup and later source processing or effects.
- No interview answer appears before the authorized retrospective request.
- The original controller observed only the running state before browser control
  became unresponsive and was interrupted without retry.
- The assigned root was empty at readback. That is consistent with an unanswered
  setup interview and establishes that no setup was observed there at that time.

### Provider claims and inference

Work reports that it retrieved the fresh starter into temporary workspace,
unpacked it, read the governing setup instructions, and then asked the interview
questions. It says the read-only metadata, retrieval, and local inspection steps
succeeded. It also says it made no persistent Drive write and performed no
Gmail, ingestion, task, delivery, or scheduling action. Work classifies the
setup as pending for configuration answers and reports no provider or tool
limitation.

The visible unanswered interview independently supports the pending
classification and expected setup behavior through that point. The underlying
action records were not fully expanded and audited, so the detailed read-only
tool sequence and the absence of every listed downstream action remain provider
claims. The original running state is consistent with the recorded 58-second
processing interval. It is likely that the controller missed the response while
or after processing completed, but that inference does not establish the
technical cause of the control failure.

### Cause classification

- **Product/specification gap:** None is established. The visible interview and
  separation of setup from later effects follow the expected product path.
- **Tested-agent decision:** No failure is established. Work asked for the
  required configuration and remained pending when no answer was supplied.
- **Provider/control failure:** The browser-control hang and missed response are
  established as observation failures. Their technical cause is unknown, and no
  provider or tool limitation is independently established.
- **Evaluator/controller incident:** The original controller stopped with only
  the running state and did not capture the interview response. That observation
  failure caused the route to stop before the parent interview could continue.

### Remaining unknowns

- The technical cause of the original controller hang and missed response.
- Whether fully expanding and auditing every action record would independently
  reproduce Work's description of its read-only discovery steps and absence of
  downstream actions.
- What configuration choices would have been supplied; the retrospective did
  not answer the interview or resume setup.

## Cross-route finding and stop boundary

The routes do not support one shared root cause. Sol provides high-confidence
evidence of an invalid generation choice combined with a validator blind spot.
Spark provides high-confidence evidence of an authorization-boundary divergence
and only moderate-confidence evidence for the provider's explanation of it.
Work provides high-confidence evidence of expected setup behavior through an
unanswered interview and a separate controller observation failure. It does not
provide evidence of a Work tested-agent or product failure, and the control
failure's technical cause remains unknown.

The evidence supports review of possible future repairs and trial controls, but
it supplies no permission to choose a representation, change the validator,
alter setup instructions, clean up provider state, retry a route, or resume
testing. No such action was performed. Any repair, new architecture decision,
cleanup, retry, or additional trial remains subject to separate explicit
authorization.
