# School-OS trial root-cause review

Status: local evidence review complete. Work’s diagnostic response is generating.
Spark’s diagnostic prompt has not been dispatched: the app refused a fresh
isolated worker, and the user’s choice about a coordinator-led fallback is pending.
No product or instance changes are authorized. This report reuses frozen source
expectations, final saved readbacks and preserved answers. The local review
performed no new source access or functional test. See [trial results](TRIAL-RESULTS.md)
for the full attempts, scope and evidence limitations.

## Causal standard

“Earliest proven divergent stage” means the first retained artifact where source meaning and output demonstrably differ. It does not reveal an internal reasoning step or establish why the tested model produced that record. A provider retrospective can be compared with this matrix later, but its post-hoc narrative is not independent cause evidence unless it binds to preserved input bytes, tool results or intermediate records.

The strongest cross-cutting conclusion is that persistence succeeded while meaning failed. Work’s current pages have one instance lineage, resolving references, matching revisions and no observed 64 KiB problem. Those results prove that bytes were written and can be read. They do not prove that action disposition, completion unit or deadline agrees with the source. Q2 is the clearest example: the Email is marked `fully_ingested` and its body evidence `processed_saved_verified`, yet the source-body response deadline is absent from Knowledge, Task and answer.

## Work failure matrix

| Finding | Expected meaning | Saved data | Answer result | Earliest proven divergence | Cause status |
| --- | --- | --- | --- | --- | --- |
| W-ING-001 external-image source | Interpret the in-scope image when supported, or retain an explicit incomplete source | `not_ingested`, body not processed, no linked Knowledge | No direct frozen question; Q7 retains incomplete coverage | Source extraction did not complete | The incomplete state and omission are confirmed. Whether scope, capability, access or content caused it is unknown. |
| W-ING-002 noncanonical guidance promoted | Keep guidance as Knowledge; no canonical Task | Knowledge says finite; finite child Task saved | Unexercised by the seven questions | Knowledge semantic extraction | Wrong canonical meaning is confirmed; why guidance became an obligation is unknown. |
| W-ING-003 explicit no-action source | `action_disposition: none`; no Task | Knowledge says finite; finite child Task saved | Unexercised by the seven questions | Knowledge semantic extraction | Wrong canonical meaning is confirmed; no evidence supports a motive or heuristic. |
| W-ING-004 recurring family process | Recurring-series meaning and ongoing family completion unit | Knowledge finite; Task finite with child completion subject | Unexercised by the seven questions | Knowledge for recurrence; Task derivation for completion subject | Two saved semantic divergences are confirmed. Their internal mechanism is unknown. |
| W-ING-005 conditional action | Conditional Knowledge and Task kind | Knowledge and Task say finite; prose still contains the condition | Q2 preserves the condition; its failure is the separate deadline omission | Knowledge semantic extraction | Typed-condition loss is confirmed. It did not by itself cause Q2’s wrong deadline answer. |
| W-ING-006 individual completion | Separate completion for each applicable child | Knowledge stays conditional; Task completion subject is household | Q5 passes from prose/applicability, without repairing the Task | Task derivation | Completion-unit collapse is confirmed; a shared household heuristic is only a hypothesis. |
| W-ING-007 second individual completion | Separate completion for each applicable person/child | Knowledge stays finite; Task completion subject is household | Q1 passes its requested facts, without repairing the Task | Task derivation | Second source-bound collapse is confirmed; it remains a separate finding instance. |
| W-ING-008 / Q2 deadline | Preserve response deadline separately from event timing and answer with it | Source marked fully ingested; Knowledge has only event start/end and Task only event start | Fail: answer says response deadline is absent or unknown | Knowledge semantic extraction before Task/query | Canonical ingestion omission is confirmed. There is no evidence of failure to retrieve a correctly saved deadline. |
| Q7 citation weakness | Qualified negative conclusion with direct readable source coverage | Saved relationship/index pages support no positive correction chain; one source remains incomplete | Qualified pass: conclusion/limit correct, but expected source records are not all cited directly | Answer composition and citation selection | Citation weakness is confirmed. Actual records read during the query are unknown without a trace. |

A private evidence matrix retains source/saved/answer bindings, precise instruction references, competing hypotheses and the evidence needed to distinguish them. Personal source details remain outside this public report.

## Q2 classification

Q2 is an upstream ingestion omission exposed by a downstream question. The frozen source support comes from the selected message body, not the sent/received Date header or evaluator inference. Its preserved response object matches the frozen private developer hash. The linked final Knowledge contains `event_start` and `event_end`; the linked Task contains `event_start`. No response deadline appears in their statement, qualifications, date fields, action, context or `school_timing`.

The answer is wrong against source, but consistent with what was retained. Without an independent query trace, this review cannot establish exactly which pages Work read. That missing trace does not affect the proven upstream omission: no correct saved deadline existed to retrieve. The exact source and saved-record bindings are retained privately.

## Instructions that should have prevented the Work divergences

The installed Work system files were independently byte-matched to the starter. The relevant public instructions are explicit:

- `operations/extraction.md:46-61` requires conditions, scope, deadlines, recurrence and action disposition to remain distinct.
- `operations/extraction.md:97-112` requires the true independent completion unit, permits a Task only when the source establishes action and forbids manufacturing a Task for a no-action source.
- `operations/extraction.md:133-145` requires ordinary readback against substantive source meaning before saving `fully_ingested`.
- `operations/knowledge.md:10-25` requires every substantive date/condition and an independent `none`/`finite`/`conditional`/`recurring` disposition.
- `operations/knowledge.md:38-44` says source original Date, effective date and deadline are not interchangeable.
- `operations/knowledge.md:66-76` requires the independent completion unit and recurring-series/occurrence meaning.
- `operations/query.md:4-39` requires canonical/source resolution, semantic fallback, relationship traversal and coverage qualification.
- `operations/query.md:101-103` requires the primary readable source and every additional source affecting confidence, qualification or relationship meaning.

The existence of these instructions rules out “the contract never said to preserve it” for the six Task findings and the Q2 deadline omission. It does not prove whether the tested model read a particular section at the decisive moment, misunderstood it, lost meaning during record generation or skipped the semantic comparison. Distinguishing those possibilities requires model-visible inputs, source-to-record proposals, write/readback comparisons and operation traces. A retrospective statement alone is hypothesis evidence.

## External-image source

W-ING-001 should remain an explicit incomplete-input outcome rather than be relabeled as a proven connector or product defect. The saved coverage truthfully says that the email was not ingested. Work reported that the source depended on an external HTML image and inferred that following it was outside mailbox-only scope. The frozen packet did not expressly prohibit such links, and Work did not bind the decision to a named attachment rule. No preserved fetch attempt establishes whether the link was reachable, whether pixels were available, or whether a supported image route existed.

The missing Knowledge is material to ingestion completeness, but the cause stays unresolved among scope interpretation, tool capability, access failure and source content. A decisive diagnosis would require the exact link-fetch request/result or exception, the applied route/scope rule and model-visible image interpretation evidence. None should be reconstructed from memory.

## Q7 citation weakness

Q7’s substantive conclusion is supported within the saved scope: no explicit correction/replacement chain was found, conflicting dates were not promoted to a correction, and the answer disclosed the not-ingested source. All three cited file identities resolve in the final Work snapshot. The weakness is provenance granularity: page-level citations do not directly cover every frozen source record supporting a completeness-sensitive negative conclusion.

This divergence first appears in final citation selection, not in the core answer. It is not evidence that the expected records were never retrieved; the candidate’s six retrieval-evidence links and read/stop narrative are self-report, not an operation trace. Provider query read count, timing and model-visible bytes remain unknown.

## Three intended routes, with repeat attempts kept separate

| Intended route | Original attempt | Separate repeat attempt | Current route-level conclusion |
| --- | --- | --- | --- |
| Fresh Sol | Core setup verified with limits; ingestion saved 17 Email, 21 Knowledge and 10 Task records; seven material findings; questions six pass and one qualified pass | None | Persistence worked, but one substantive source was omitted despite all 17 being marked fully ingested and six Task semantics diverged. Query retrieval was broad: 83 file reads plus six folder listings. |
| Gemini Spark | Setup failed with a bootstrap mismatch; a current object was independently found outside the assigned folder; ingestion/questions unexercised | Second fresh attempt also failed setup: invalid catalogue-root meaning left required routes unreachable/missing; ingestion blocked | No Spark ingestion or question result exists. The two setup failures are separate attempts under one intended route. |
| ChatGPT Work | Launch failed before interview with a UI network error of unknown cause; setup/ingestion/questions unexercised | Setup passed; ingestion saved 17 Emails, 17 Knowledge and 10 Tasks, with 16 fully ingested and one not ingested; eight material findings; questions five pass, one qualified, one fail | The repeat demonstrates structural setup and persistence, but fails semantic ingestion. The original launch failure remains separate and unexplained. |

Fresh Sol’s opening was not a clean bundle-only discovery test. Its action log shows it read the repository `START-HERE.md` and repository `operations/setup.md` before downloading and reading the ZIP. That repository-before-ZIP exposure contaminates the setup-isolation claim. It does not invalidate the later independent comparison of frozen source expectations to the 17/21/10 saved records.

Fresh Sol and second-attempt Work both saved ten Tasks and share the same high-level six-category Task failure pattern: two unsupported canonical Tasks, recurring/conditional type loss and two independent-completion collapses. Work’s recurring-action finding additionally narrows the ongoing family process to a child completion subject; that extra narrowing is not established for Sol. This repeated high-level pattern is material across the two saved ingestion outputs. It does not prove a shared hidden mechanism. Fresh Sol also omitted one substantive source while claiming all 17 fully ingested. Work more honestly kept its external-image source `not_ingested`, but separately overstated completeness for the Q2 source by marking it fully ingested after dropping its deadline.

Answer results also show that query prose can compensate for canonical defects. Fresh Sol answered six questions correctly and one with qualification despite seven saved semantic findings. Work passed Q1 and Q3–Q6 and recovered some conditions/scope from prose despite Task defects, but failed Q2 because the deadline was absent upstream. Correct prose does not repair the canonical page.

## Evaluator and transport events excluded from product cause

- Two Work entry responses were lost by early evaluator receipt-sink versions. The later controlled repeat is preserved. This explains the difference between 62 attempted reads and 60 receipts; it is not a connector failure.
- The evaluator initially overlooked nested index bucket references. Contract review corrected the interpretation and all 24 referenced pages/55 refs were checked. The withdrawn intermediate conclusion is not a Work defect.
- Work question observation/download timed out without a returned browser receipt. The exact local candidate is provenance-qualified. That limitation does not create the Q2 source contradiction or Q7’s observable citation set.
- Fresh Sol’s initial sandbox DNS failure, broad tool discovery and truncated dependency read are environment/execution observations. They are not semantic root causes.
- Two frozen-source search receipts are missing and fresh JPEG pixels were not model-visible to the evaluator. Those limits constrain discovery/image qualification; none of the seven questions depends on the JPEG pixels.

## Evidence boundary

This review confirms output divergence, not mental process. The most useful provider retrospective would identify, with preserved bindings, the exact source bytes visible for each failed item; the Knowledge/Task proposal before write; any defaulting or transformation; the readback used for semantic verification; and the query records actually retrieved. Claims such as “context overload,” “instruction ambiguity,” “the model chose the obvious action,” or “the connector could not fetch the image” remain hypotheses until they align with those artifacts.

## Provider diagnostic follow-up

Work’s existing task was reopened at its exact saved URL after the previous tab handle became unavailable. The controller verified the prior setup/ingestion/question history, confirmed no earlier diagnostic prompt, submitted the prepared prompt once and observed the response begin. It remains in progress.

Spark’s diagnostic prompt has not been dispatched. Fresh isolated worker creation was denied by the app’s retained-agent limit, including after another worker finished. Reusing the Work reviewer would conflict with the user’s controller-context separation rule. A question is pending about whether the coordinator may conduct this read-only follow-up directly with Spark-only evidence. No new trial or provider task has been created.

Retrospective provider explanations will be distinguished from causes established by retained evidence. No fixes, fresh ingestion or question replay are authorized.
