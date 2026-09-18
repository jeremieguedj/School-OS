# Unchanged pre-fix round results

Status: complete for the three setup routes and the independent source-oracle
preparation. One route passed setup but could not receive the separate ingestion
request. Two routes failed or remained incomplete at the setup gate. Therefore
no tested route ingested mail, no route-level source-to-saved audit ran, no common
question was asked, and no page-size comparison ran.

This round used the product and starter without a repair. It supplies the second
pre-treatment observation set required by the
[autonomous remediation cycle](AUTONOMOUS-REMEDIATION-CYCLE.md). The earlier
[round-two results](ROUND-2-TRIAL-RESULTS.md) and
[root-cause retrospective](ROUND-2-ROOT-CAUSE-RETRO.md) remain a separate first
observation set. Neither round's failure is erased by a later non-recurrence.

## Exact tested baseline

| Item | Exact value |
| --- | --- |
| Preserved public source baseline | `db68b12840aab3d0c94cfbb7d036a85f31b311f2` |
| Baseline rollback tag/release | `school-os-autonomous-remediation-baseline-2026-09-17` |
| Tested starter source revision | `aae44ef13be8392130f9b5aec7889b040c0ca45b` |
| Tested immutable starter release | `school-os-starter-2026-09-17-round-2` |
| Tested asset | `School-OS-setup-round-2.zip` |
| Exact byte count | `113045` |
| SHA-256 | `5cabbe0779c39a8ac547ee17ec8365cb0d244a95591cccc20658aab27e142f50` |
| Fixed source interval | `[2026-09-09T17:53:48Z, 2026-09-16T17:53:48Z)`; UTC; start inclusive and end exclusive |

The downloaded starter bytes matched the immutable asset binding. Each route
used a fresh task or conversation, a fresh assigned Drive root, a separate
controller and a separate private evidence area. Gemini Spark and ChatGPT Work
used the same signed-in Chrome profile, so cookies, account state and unknown
provider memory were shared and remain a methodology limit. No cross-route
content transfer was observed.

## Result at a glance

| Route | Setup result | Earliest blocking boundary | Ingestion and dependent stages |
| --- | --- | --- | --- |
| Sol | **Passed.** An independent audit validated the finite 24-role bootstrap, 28 exact page readbacks, distinct Task roots, all reached references, and the 64 KiB limit. | The separate ingestion message was rejected before delivery by the child-task approval surface. After evidence proved no dispatch and no effect, the one allowed identical retry was also rejected before delivery. | **Not dispatched.** No Gmail read and no ingestion write. Semantic audit, questions and page-size comparison unexercised. |
| Gemini Spark | **Failed.** Spark claimed setup complete. Independent audit found a coherent 27-page instance graph and distinct Task roots, but `system/` was empty. The entrypoint's reusable-system links therefore had no installed targets. | Spark treated the starter ZIP beside an empty `system/` folder as sufficient installation material. The JSON bootstrap validator did not cover reusable system files. | Blocked by setup gate. No ingestion request, source read, semantic audit, questions or page-size comparison. |
| ChatGPT Work | **Incomplete.** The interview was answered, including the exact assigned root, but the task remained in `Working` for 25 minutes 50 seconds without another question, completion or visible failure. | After the bounded stop, Work said it had been waiting for the folder link. That account conflicts with the visible conversation, which already contained the link. The provider did not explain why it failed to recognize the supplied answer. | Blocked by setup gate. No ingestion request, source read, semantic audit, questions or page-size comparison. |

## Sol route

### What was independently established

The tested Sol agent discovered the starter, completed the parent interview and
claimed setup success. The independent auditor checked the saved state rather
than accepting that claim. It read the configured entrypoint and every finite
contract reference reached from it. The audit found:

- 24 entrypoint roles, including two different Task root page IDs;
- 28 unique JSON pages, all beneath the assigned instance location;
- eight unique catalogue routes and the required locator-family set;
- exact filename/page-ID and declared-byte-size agreement;
- no duplicate page ID, cycle, unresolved required reference or oversized page;
- a maximum observed page size of 7,549 UTF-8 bytes; and
- `check_bootstrap` returning `valid` with no diagnostic for this saved graph.

The connector's folder-list response had no explicit end marker. The audit
therefore proves the finite entrypoint graph and its explicit continuations, not
an exhaustive inventory of every object that might exist in the folder. Three
early local receipt-writer attempts did not close cleanly; their provider results
were discarded without interpretation. The reported findings use fresh reads
captured only after a successful owner-only sink preflight.

### Why ingestion did not run

The coordinator then attempted to deliver the separately authorized, fixed
seven-day read-only ingestion request. The child-task approval surface rejected
the message before delivery. Preserved evidence showed that the tested task did
not receive an ingestion turn, Gmail was not read and no ingestion effect
occurred. Under the one-retry rule, the coordinator made one identical retry and
included the user's explicit standing authorization. The same approval surface
again rejected it before delivery.

This is a provider/platform admission failure outside the tested School-OS
agent's reasoning and outside the product contract. It is not evidence that
School-OS ingestion failed, succeeded, or reached Gmail. It receives no product
fix.

## Gemini Spark route

### What was independently established

Spark visibly claimed that setup was configured and verified and that no mailbox
ingestion had occurred. Independent readback found a valid 27-page canonical
instance graph. The configuration, household references, source-account routes,
four catalogue families per configured source/month, topic/entity/membership
locators and two distinct Task roots were internally consistent.

The same audit found the decisive failure: the installed `system/` folder was
empty. Spark had placed the ZIP and created the folder structure, but had not
persisted the reusable operations, contracts, adapters and helpers under their
documented relative paths. A fresh agent following the entrypoint would encounter
links whose installed targets were absent. The setup gate therefore failed even
though the JSON graph itself passed.

### Evidence-bound retrospective

In the exact retained Spark conversation, Spark reported that it treated the
starter ZIP beside the empty `system/` folder as adequate placement. It verified
the JSON pages and ran the JSON bootstrap checker, but did not list or read back
the contents of `system/`. It recognized that no tool call had populated those
files and that the bootstrap checker did not inspect them.

That account agrees with the independent saved-state audit. Confidence is
**high** that the immediate failure was omission of the reusable system tree and
that the existing completion gate failed to detect it. Evidence does not
establish whether the omission arose from an I/O optimization, an interpretation
of the setup wording, or another internal motive.

## ChatGPT Work route

### What was independently established

The exact Work task received the ordinary one-link setup request, presented the
expected interview, and received the frozen interview answers. The assigned
Drive root was included visibly in that answer. The task then stayed in
`Asking questions` / `Working` for 25 minutes 50 seconds. No further question,
completion response or visible failure appeared. Because a Drive effect was
initially unknown, the controller did not retry or send an ingestion request.

After that bounded observation period, the controller stopped the still-running
turn once and asked for a retrospective without asking Work to resume setup or
use tools. The assigned root was empty on independent readback.

### Evidence-bound retrospective

Work said it was waiting for the permanent destination folder link and reported
no persistent Drive mutation. The first statement conflicts with the visible
conversation: the exact assigned link had already been supplied in the second
user message. In a targeted follow-up, Work confirmed that the message exists in
the external task history but said it was absent from the model-visible state of
the setup turn. It identified the earliest observable non-incorporation as the
pending second questionnaire failing to resolve with the submitted URL and
later returning an aborted status, with no subsequent assistant action using the
answer.

Confidence is **high** that the route stalled after receiving the required
answer and never completed setup. Confidence is **high** that the provider's
stated wait condition is inconsistent with visible task state. The technical
cause remains unknown: the available evidence cannot distinguish input delivery
loss, a pending-question continuation failure, branch/routing mismatch, or
another provider-side defect. Provider event and model-input logs would be
needed to separate those mechanisms. Raw connector receipts were not exposed in
the retrospective, so its detailed no-effect account remains a provider claim
beyond the independently empty assigned-root readback.

## Independent source-oracle preparation

The first oracle preflight correctly rejected the earlier local oracle. Its
expectations covered a different interval, its enumeration receipts were not
fully digest-bound, and its source-input record was not bound into the oracle
manifest. Reusing it would have made later semantic grading unsound.

The evaluator then performed only the bounded correction needed for the exact
authorized interval. It exhausted 11 exact-address source queries, deduplicated
17 observed candidates, and retained all 17 after applying the half-open interval
locally to supported received/arrival timestamps. These are provider-entry
observations, not a claim that 17 distinct logical emails exist.

Three required inline-image reads initially failed local input validation because
the request omitted the message access handle required by that connector. The
failures occurred before dispatch. Only after no dispatch and no effect were
proved did the evaluator retry each read with the required access handle; all
three reads succeeded. The connector exposed file references but did not expose
the new exact pixels or a faithful private rendering to the independent
evaluator. Parent source, original filename, MIME type and byte size do not prove
pixel equality. Image-specific expectations are therefore unavailable for this
round and no image-specific finding may be made. Changed opaque provider handles
remain replaceable access aids and are not canonical image or email identity.

The corrected oracle is private, exact-interval-bound and independent of tested
route output. No tested route reached ingestion, so it was not used to grade a
route's saved knowledge or tasks in this round.

## Cohesive authorized treatment set

The two pre-treatment rounds support four changes at already approved or purely
evaluation boundaries. They are one package because setup must first install and
validate a usable instance, and the evaluator must then deliver later stages to
the exact bound task and grade them against the exact bound source interval.

| Treatment | Class | Supported problem | Selected change | Exact post-fix observable |
| --- | --- | --- | --- | --- |
| Enforce distinct Task roots | **A** | Round two saved Active Tasks and Completed Task history at one root and the validator accepted it. | Require the reserved `active-tasks` and `completed-task-history` roles exactly once, bind each to the existing Task record-locator topology, and reject one root ID assigned to both. | Missing, renamed, duplicated or wrongly bound Task roles cannot pass; a shared root returns `invalid` with a stable alias diagnostic; two correctly bound distinct roots may validate without adding a persisted discriminator. |
| Verify installed starter material | **A** | Pre-fix Spark claimed success with an empty `system/` tree. | Compare the finite starter-supplied root documents and `system/` files with complete saved bytes and ancestry immediately after placement. At the final gate, compare against a second exact expectation containing the intended configured `START-HERE.md` bytes and the unchanged original bytes for all other material. Independently derive every bootstrap role, root, family and scope from the complete saved entrypoint before running the canonical bootstrap check. | Missing, altered, unread or wrongly placed material prevents setup success. So does an exact but unusable entrypoint. Phase-two material, entrypoint derivation and canonical bootstrap must all pass. |
| Bind controller follow-ups and task state | **B** | Earlier controllers used a wrong composer or missed a final response; the new Work route remained running without a proven terminal result. | Before every follow-up, compare provider, task, conversation, route, root, stage and task-bound composer with the private round manifest. Preserve distinct states for active, awaiting input, completed, approval-blocked, unknown effect and unavailable observation. Permit only one separately recorded retry after proven no dispatch and no effect. | No follow-up can be sent through a top-level or mismatched composer; a later final response supersedes a running snapshot; unknown dispatch blocks retry. |
| Bind and preflight the source oracle | **B** | The available oracle described the wrong interval and incomplete receipt binding; three image reads first used an incomplete local call shape. | Bind the oracle to the exact private round-manifest bytes, exact `[start,end)` fields, explicit continuation exhaustion and comparable timestamps; apply boundaries locally. Validate required connector access arguments before dispatch and treat local rejection separately from provider failure. | A stale or differently bound oracle is rejected; an exact exhausted oracle returns the same locally filtered set; missing required access arguments stop before dispatch and cannot be reported as provider failure. |

The precise file list and later validation binding belong in the
[issue and treatment ledger](AUTONOMOUS-REMEDIATION-ISSUES.md). The treatment set
does not change email identity, record schemas, the 64 KiB maximum, canonical
meaning, provider handles, setup/ingestion authority, or the MVP recovery scope.

## Issues receiving no product change

- The two pre-delivery Sol ingestion rejections are an isolated provider/platform
  admission result. They do not justify weakening authorization, changing the
  ingestion recipe or inventing a different dispatch route.
- Work's stall and contradictory wait account have no supported School-OS defect.
  Controller-state hardening preserves better evidence but does not claim to fix
  Work.
- Spark's earlier premature retrieval-labeled transition did not recur in this
  round. The product's setup/ingestion boundary was already explicit, so no
  provider-specific prompt patch is selected.
- Chrome did not support the controller's optional Spark tab export. The final
  response remained visible and independent Drive evidence was preserved, so the
  limitation receives no product fix and no downloaded-artifact claim.
- Local receipt-protocol and incomplete connector-call incidents are evaluator
  events. Their evidence was discarded or safely retried only when no dispatch
  was established; neither becomes a School-OS source result.

## Architecture backlog, not implemented

Two possible persisted mechanisms are deliberately excluded from the treatment
set:

1. **A persisted Task partition selector.** A new canonical field distinguishing
   active from completed Task records could encode the split inside one locator
   model. That would select a new persisted representation and require explicit
   architecture approval. It is unnecessary for the approved correction, which
   uses two different existing Task roots, so it is neither recommended nor
   implemented.
2. **A persistent installation manifest or installed-state record.** Saving a
   manifest could support later drift and upgrade checks, but it would add
   canonical installer state and lifecycle meaning deferred from the MVP. The
   selected finite comparison is transient. A persistent manifest is neither
   recommended nor implemented.

## Unexercised stages and limits

Across all three tested routes, the following remained unexercised:

- Gmail ingestion and logical email/reply/attachment identity during ingestion;
- canonical knowledge and Task extraction from the fixed source interval;
- source-to-saved semantic comparison and task-disposition audit;
- coverage-supported fact and trend questions;
- 64/128/256 KiB noncanonical page comparison;
- task-app synchronization, completion-review projection and parent confirmation;
- manual or scheduled briefs, outbound email, audio generation or delivery; and
- scheduling, upgrades, concurrent operation and interrupted-write recovery.

No mailbox state was changed. No external task item, outbound message, audio,
schedule or cleanup operation was created. The pre-fix round supports treatment
selection and an immutable post-fix starter; it does not qualify ingestion or
the whole School-OS MVP.
