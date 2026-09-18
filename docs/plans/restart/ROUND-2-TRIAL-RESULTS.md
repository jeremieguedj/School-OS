# Round-two setup and ingestion trial results

Status: trial execution and bounded evidence review are complete. The result is
**0 of 3 setup gates passed**. Because setup was the required gate, the series
produced **0 ingestion runs, 0 common-question runs, no source-semantic audit,
and no meaningful 64/128/256 KiB comparison**. This report records the observed
outcomes without repairing, cleaning up, retrying, or replacing any route.

## Executive result

The published round-two implementation did not qualify the first-use setup path
on any of the three routes.

- Sol discovered the starter, completed the parent interview, wrote and read
  back an extensive setup, and claimed success. Independent review nevertheless
  found a contract-breaking route collision: Active Tasks and Completed Task
  history point to one undifferentiated empty Task `record_locator` root. The
  temporary manifest contained 24 logical roles but only 23 unique roots. The
  bootstrap checker returned `valid` with zero diagnostics because its manifest
  selector could not distinguish those two Task roles. Setup therefore failed.
- Spark received the exact opening request and the interview answers, but began
  retrieving school mail before setup had completed and without an ingestion
  request, despite an explicit instruction not to ingest yet. The controller
  stopped it. A separate controller/UI routing mistake created a second
  unintended Spark task, which also began ingestion activity and was stopped.
  Spark made no setup-completion claim, and its assigned Drive root reads back as
  empty.
- Work received the exact opening request on a verified fresh surface. Its only
  visible state was `Working` / `Stop answering`. It showed no interview,
  completion claim, error, Drive or Gmail action, write, or ingestion. Browser
  control later hung, including a final app lookup for about 1,012 seconds. The
  controller was interrupted without retry. Its assigned Drive root reads back
  as empty, and the provider task's state after the last visible `Working` state
  is unknown.

The one structural defect observed in Sol and the browser-route failures prevent
any claim of product qualification, provider compatibility, ingestion quality,
query quality, or page-size economics. The existing 64 KiB canonical maximum
remains unchanged pending later evidence.

## Release and method

The tested implementation and artifact were fixed before the series:

| Item | Exact value |
| --- | --- |
| Implementation source commit | `aae44ef13be8392130f9b5aec7889b040c0ca45b` |
| Continuity head | `61e0579f91e76e3737ba6c45790425cedb42d21b` |
| Immutable starter tag | `school-os-starter-2026-09-17-round-2` |
| Starter ZIP size | 113,045 bytes |
| Starter ZIP SHA-256 | `5cabbe0779c39a8ac547ee17ec8365cb0d244a95591cccc20658aab27e142f50` |

The local deterministic suite passed 46 of 46 checks, and compilation, privacy,
and diff checks passed. Those results establish publication hygiene and local
deterministic behavior only; they are not product qualification.

One identical Drive-hosted ZIP was used with three distinct fresh Drive roots.
The same fixed seven-day interval and the same household and source choices were
reserved for all routes, but the interval could be supplied for ingestion only
after that route passed independent setup review. No route passed that gate.

Sol ran as the fresh supervised agent route. Spark and Work used separate fresh
conversations, controllers, tabs, assigned Drive roots, and evidence areas. The
browser routes shared the user's existing signed-in Chrome profile. Cookies,
account state, visible task lists, and unknown provider memory were therefore
shared environmental constraints; this method does not claim browser-profile,
account-level, UI-state, or provider-memory isolation. Browser interaction was
kept route-specific, and no other visible task was opened.

The evidence review stayed within the assigned roots and preserved only
privacy-safe findings here. It did not expose personal names, addresses, source
content, provider identifiers, folder identifiers, task URLs, or raw connector
errors.

## Route comparison

| Route | Observable setup progress | Independent saved-state result | Gate | Dependent stages |
| --- | --- | --- | --- | --- |
| Sol | Discovered the starter, interviewed the parent, locally validated, wrote 67 files including 35 bootstrap/canonical JSON pages, and claimed setup success. | Fifty-five Drive reads produced 55 responses and 55 owner-only mode-0600 receipts, with no connector errors. Review verified ancestry, expected structure and system files, configuration scope, 35 unique JSON pages, and 31 derived pages whose explicit continuations were exhausted. The largest page was 5,327 bytes; the largest page had 10 entries; no reviewed page was duplicated or over the limit. Active Tasks and Completed Task history nevertheless shared one empty Task locator root. | **Failed** | No ingestion request; no ingestion, questions, semantic audit, or size comparison. |
| Spark | Received the exact opening prompt and interview answers. It began mail retrieval before authorization and was stopped. It did not claim setup completion. | Assigned root readback was empty. A controller/UI routing mistake also created a second unintended Spark task, which began ingestion activity and was stopped. | **Failed / incomplete** | No authorized ingestion request or run; no questions, semantic audit, or size comparison. |
| Work | Received the exact opening prompt on a verified fresh surface. The only visible provider state was `Working` / `Stop answering`. | Assigned root readback was empty. Browser-control calls hung; the controller was interrupted without retry. | **Failed / incomplete** | No interview, setup claim, visible provider action, ingestion request or run, questions, semantic audit, or size comparison. |

Sol's successful writes and readbacks do not override the invalid task-route
topology. Spark's attempted mail retrieval is an observed authorization-boundary
violation, not an authorized ingestion run. Empty assigned roots establish only
the absence of observed saved state in those roots at readback time.

## Observed failures and cause boundaries

| Observation | Proven from available evidence | Unknown or not established |
| --- | --- | --- |
| Sol Task route collision | The two required logical roles resolve to one undifferentiated empty Task locator root. The temporary manifest has 24 logical roles and 23 unique roots. The storage contract requires separate bounded Active Task and Completed Task history routes. | No downstream ingestion effect was exercised. The trial does not establish how a repaired instance would behave. |
| Sol bootstrap validation blind spot | `bootstrap_contract` returned `valid` with zero diagnostics because the manifest selector cannot distinguish the two Task roles represented by the same family selector. Independent topology review caught the failure. | No broader claim is made about every validator rule or every possible manifest shape. |
| Sol Drive inventory | Every finite referenced target used for the gate was reviewed, including explicit continuations in the derived pages. | The Drive listing route exposed no explicit end marker, so exhaustive folder inventory remains unknown. A short or matching listing is not proof of exhaustion. |
| Spark premature source activity | The main Spark task began retrieving school mail before setup completion and without an ingestion request, despite the explicit setup-only instruction. It was stopped. | The reason Spark disregarded the boundary is unknown. The trial does not attribute it to hidden reasoning, a specific product defect, provider memory, or a connector failure. Effects outside the assigned root remain unknown. |
| Spark second task | The controller sent interview answers through the top-level composer by mistake, creating a second unintended task. That task also began ingestion activity and was stopped. | This routing mistake is evaluator/controller behavior and is not evidence that School-OS or Spark created the second task autonomously. Methodological or provider effects outside the assigned root remain unknown. |
| Work stall | The fresh Work surface accepted the opening prompt and remained visibly working. Control calls later hung, including one app lookup for about 1,012 seconds, after which the controller was interrupted. | The evidence does not establish whether the provider task completed, failed, remained active, or performed an unseen action after the last visible state. It also does not establish the cause of the control hang. |

No hidden chain of thought or retrospective provider explanation was used as
evidence. Conclusions are limited to visible UI state, saved-state readback, and
the preserved operation receipts described above.

## Effect on T01-T19 qualification

| Treatment | Round-two qualification result |
| --- | --- |
| T01 — finite bootstrap validation | **Failed.** The checker accepted a bootstrap whose Active Task and Completed Task history roles shared one root. This is the decisive Sol setup-gate failure. |
| T02 — source-to-saved semantic comparison | **Unexercised.** No ingestion passed the setup gate. |
| T03 — action classification and completion units | **Unexercised.** No source-derived Knowledge or Tasks were produced. |
| T04 — date value and meaning checks | **Unexercised.** No ingestion corpus was produced. |
| T05 — bounded query planning | **Unexercised.** No common questions ran. |
| T06 — claim-level canonical/source citations | **Unexercised.** No common questions ran. |
| T07 — substantive embedded-image handling | **Unexercised.** No authorized ingestion ran. |
| T08 — fresh setup from supplied bundle and parent answers | **Partially exercised; not qualified.** Sol discovered and used the starter and interview, but its saved setup was invalid. Spark did not finish setup, and Work did not reach an interview. |
| T09 — outcomes-first interview and relevant capability inspection | **Partially exercised.** Sol completed the interview and Spark received interview answers; Work did not. No route completed a valid setup, so the treatment is not qualified end to end. |
| T10 — write placement and full readback | **Partially evidenced; not qualified.** Sol's audited targets had verified ancestry and content within its selected root, but the supplied evidence does not establish a complete content readback for every one of the 67 written files. Spark and Work wrote nothing observable to their assigned roots. |
| T11 — identical immutable starter provenance | **Passed for artifact publication and route input.** The three routes received the identical Drive-hosted ZIP bound to the exact size and digest above. This is an artifact-provenance result, not setup or product qualification. |
| T12 — one retry only after proving no dispatch/effect | **Unexercised.** No compliant launch retry was performed. The unintended second Spark task was a controller mistake and does not count as an authorized retry. |
| T13 — explicit listing exhaustion | **Partially exercised.** Finite referenced targets and explicit page continuations were checked. Full Drive listing exhaustion stayed correctly unknown because the route provided no end marker. |
| T14 — private receipt-sink preflight and receipt preservation | **Passed for the Sol setup audit.** The owner-only sink preflight passed, and 55 dispatched Drive reads produced 55 responses and 55 mode-0600 receipts with no connector errors. Spark and Work did not reach comparable setup audits, so this does not qualify their routes. |
| T15 — contract-defined reference traversal | **Partially exercised.** The Sol audit traversed the referenced setup topology and exposed the Task-route collision. A valid installed instance and dependent ingestion topology were unavailable. |
| T16 — task-bound report provenance | **Unexercised.** No downloaded route report was used or graded. |
| T17 — disclosed browser isolation | **Method partially achieved with a controller incident.** Spark and Work used distinct conversations, controllers, tabs, roots, and evidence areas in one shared signed-in profile. The Spark top-level-composer mistake is reported separately. Account and provider-memory isolation remain unclaimed. |
| T18 — independently grounded image expectations | **Unexercised.** No image-dependent expectation or ingestion audit ran. |
| T19 — retained 64 KiB canonical pages and 64/128/256 KiB evaluation | **Unexercised as a size comparison.** Sol's 5,327-byte maximum is setup-only evidence and says nothing about canonical knowledge-page economics. |

The matrix distinguishes a treatment's local implementation or evaluator use
from end-to-end product qualification. T11 and the bounded parts of T10, T14,
and T15 do not compensate for the failed setup gates.

## Product-principle and use-case coverage

| Principle or use case | Evidence from this series |
| --- | --- |
| One-link first-use setup | Exercised on three routes; **0/3 passed**. Sol reached an invalid persisted setup, Spark crossed the ingestion boundary before setup, and Work did not progress observably beyond working state. |
| Deterministic, discoverable Drive topology | Failed in Sol at the Task-route distinction. The validator's zero-diagnostic `valid` result did not match the independently reviewed contract topology. |
| Losslessness and provenance | Not assessed. There was no authorized ingestion corpus or source-semantic comparison. |
| Bounded, efficient execution | Setup-page bounds were observed in Sol, but ingestion, selective retrieval, model-visible bytes, tokens, cost, and accumulated-history behavior were not measured. |
| Tool agnosticism and capability-led portability | Three execution surfaces were attempted, but none completed valid setup. No compatibility claim follows. |
| Canonical task handling and task synchronization | Canonical task-route setup failed in Sol. Task extraction, completion review, and external task synchronization were unexercised; external task writes were outside scope. |
| Querying school information | Unexercised because no route reached the common-question stage. |
| Briefs, audio, schedules, extensions, and lifecycle | Outside this trial's execution scope and unexercised. |

The series therefore covers the first-use gate and selected setup/evaluation
mechanics only. It does not cover the product's substantive school-information,
task, query, brief, automation, extension, or upgrade use cases.

## Page-size conclusion and other unexercised scope

Sol's largest reviewed setup page was 5,327 encoded bytes with at most 10
entries. That sample contains setup state, not the ordered canonical Knowledge
and Task records required for the size study. It cannot answer whether 64, 128,
or 256 KiB changes page packing, Drive operations, retrieval breadth, answer
quality, model-visible context, tokens, latency, or cost.

The 64/128/256 KiB comparison therefore has no round-two result. Preserve the
current 65,536-byte canonical maximum. No later increase is supported by this
evidence.

Also unexercised were source discovery exhaustion, logical-email association,
body and attachment processing, embedded-image semantics, ingestion coverage,
Knowledge and Task semantic preservation, correction relationships, source-date
meaning, independent completion units, query citation quality, source-grounded
answer accuracy, task-provider synchronization, outbound briefs, audio,
schedules, and provider behavior near any page-size limit.

## Proposed decisions for joint review

These are proposals only. They require user approval before implementation,
cleanup, retry, or another trial series.

1. **Repair the T01 Task-route discriminator.** Make the temporary manifest and
   `bootstrap_contract` validation distinguish the Active Task route from
   Completed Task history even though both use the Task canonical family. Reject
   a bootstrap when those two required logical roles resolve to the same
   undifferentiated root.
2. **Add a focused deterministic regression case.** Exercise the exact Task-role
   alias observed here and require a non-valid result with a specific diagnostic.
   Preserve the current architecture of two separate bounded routes rather than
   changing the storage contract to accept the collision.
3. **Tighten the browser setup handoff and controller guard.** Before supplying
   interview answers, verify that the composer belongs to the intended fresh
   provider task. Keep the separate ingestion request unavailable until the
   independent setup gate passes, and stop immediately on premature source
   activity. Treat this as evaluator/controller hardening separately from the
   product defect.
4. **Decide whether to authorize one bounded Work follow-up.** Before any retry,
   inspect the preserved task and assigned root to establish the observable
   dispatch/effect state. If that cannot be established, retain the outcome as
   unknown rather than resubmitting. Any retry should use explicit controller
   watchdog bounds and a fresh, separately recorded authorization.
5. **Publish a new immutable starter only after the approved repair passes local
   validation.** Then run setup-only gates on fresh roots first. Send the fixed
   seven-day ingestion request to a route only after its saved-state review
   passes. Preserve failed instances and do not clean them up as part of the
   retest.
6. **Keep the 64 KiB limit.** Revisit 64/128/256 KiB only after a valid route has
   produced a real canonical ingestion corpus that can be repacked and queried
   under the authorized evaluation procedure.

The first two proposals repair a proven validator coverage gap within the
already approved separate-route design. The remaining proposals govern
evaluation control and the scope of a possible later retest; they do not infer
that Spark or Work caused the Sol defect.

## Evidence limits

- The report is privacy-safe and intentionally omits raw source material, account
  and provider identifiers, task and folder URLs, request arguments, and raw
  errors.
- Sol's 55 successful Drive responses and receipts establish the bounded reads
  described here. They do not prove an exhaustive provider folder inventory,
  because the listing route supplied no explicit exhaustion marker.
- Empty Spark and Work root readbacks do not prove that no provider-side or
  out-of-scope effect occurred. Spark's effects outside the assigned root and
  Work's final task state remain unknown.
- Existing task titles were visible in the shared browser profile. No other task
  was opened. Shared cookies, account state, UI state, and provider memory were
  not isolated or measured.
- The controller's top-level-composer mistake is a methodological incident. It is
  not attributed to product or provider behavior.
- The Work control hang is an observed controller/UI failure. Its technical
  cause and the provider task's final state are not established.
- The local 46/46 suite and publication checks are not substitutes for Drive,
  connector, provider, or semantic qualification.

## Exact stop boundary

Testing stopped at the setup gate. No ingestion request was sent to any route.
The premature Spark activity was stopped and is not counted as an ingestion run.
No common questions were issued, no source-semantic audit was performed, and no
64/128/256 KiB comparison was created.

No product or instance fix, cleanup, retry loop, replacement route, outbound
effect, mailbox mutation, external task-application write, brief delivery, audio
generation, or schedule was performed. Failed and uncertain states remain
preserved. The next action is joint review of these findings and explicit user
approval for any repair, cleanup, retry, or additional testing.
