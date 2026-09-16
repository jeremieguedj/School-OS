# Page-size assessment

**Status:** decided by the user-delegated size assessment, 2026-09-16. No probe,
ingestion, model replay, or functional test was run. The linked-piece direction
was rejected; the existing single page maximum remains in force.

## Recommendation

Keep **64 KiB encoded UTF-8 as the single page maximum**. Split collections of
ordinary records across more pages under the existing paging rules. One complete
canonical record must fit on one page. If it does not, retention blocks with the
exact observed size and private source evidence. Do not truncate it, split its
fields, create linked pieces, or store a fallback raw blob.

This keeps one rule and adds no record family, reference form, configuration
field, registry, soft target, or reconstruction logic. The evidence says normal
processed records are likely small, while no real-instance overflow distribution
justifies increasing every allowed page now. A larger maximum could increase
irrelevant context and whole-page rewrite/readback cost on routes that expose the
whole file.

If actual whole-record sizes or trial I/O/query results justify more room, change
the one maximum in the shared installed data contract to 128 or 256 KiB. Existing
pages, Knowledge and Task IDs, locators, catalogues, `page_hint` behavior,
continuations, revisions, and indexes remain valid; no eager migration is needed.
All readers and writers must consult the updated installed contract. An old agent
may reject a valid page above its known limit, and a vendor connector may still
fail, so a future increase is simple structurally but not universally compatible.

## Why 64 KiB remains the current maximum

The current 64 KiB cap is reasonable for ordinary records, although there is no
observed real-instance distribution establishing a universal safe limit. The
largest fictional page in `examples/data` is the 6,941-byte Knowledge page,
about 10.6% of the current cap. Those examples illustrate readable shapes; they
do not represent real school-mail or attachment sizes. The 88,839-byte scenario
fixture is an aggregate test document, not one canonical page.

School-OS stores processed meaning per claim and per independently completable
task. It does not copy raw emails or long attachments into Drive. A long PDF
should normally produce multiple focused Knowledge claims and any corresponding
Tasks, each retaining its scope, qualifications, dates, and source evidence.
That semantic boundary makes ordinary records much smaller than raw inputs.
Outliers can still arise from unusually qualified claims, accumulated
relationships, parent notes, completion reviews, or sync evidence. That
possibility is a reason to measure, not evidence for a speculative larger limit.

Bytes are not tokens. As a rough English-only planning heuristic, compact ASCII
JSON at 64, 128, and 256 KiB might be on the order of 16k, 32k, and 64k tokens
respectively. This is not a limit or a prediction. Non-English text uses
different UTF-8 byte counts and tokenization; JSON escaping and repeated field
names also change the ratio. Official OpenAI guidance says character-based token
estimates can be inaccurate and that exact counts include request structure and
model-specific behavior ([OpenAI token counting](https://developers.openai.com/api/docs/guides/token-counting)).

## Retrieval, cost, and I/O

The page cap is not a model-context setting. A capable agent may download a JSON
file to temporary code storage, parse it, and place only selected records in
model context. Another connector may inject the entire file into context. A
third may index and retrieve chunks. Therefore Drive bytes, connector transfer
bytes, model-visible tokens, billed tokens, and useful evidence are separate
measurements.

Larger pages can reduce Drive file reads and catalogue entries during a complete
scan. They can also transfer more irrelevant records for a targeted query and
make every whole-page update and verification readback larger. Keeping one
64 KiB maximum preserves the simpler current tradeoff. If a real record exceeds
it, one future maximum increase is simpler than linked reads and reconstruction.

Retrieval quality depends more on routing and filtering than on the nominal
context window. The current entity/topic indexes and record locators select a
page, not a byte range within it. A larger densely packed page would expose more
distractors if the connector supplies the whole page. The original *Lost in the
Middle* experiments found that additional distractor documents and relevant
information position affected older models, but those results do not prove that
the current managed agents will degrade at 256 KiB
([Liu et al.](https://arxiv.org/abs/2307.03172)). The current bound limits this
risk while the trials measure current behavior.

Public product limits do not answer the connector question. Gemini Apps accepts
large uploads and warns that exceeding the context window can omit connections
or details; this does not show that a 256 KiB page has that effect
([Google](https://support.google.com/gemini/answer/14903178?hl=en-CA)). Claude's
Drive connector can read several file types and says aggregate files added to a
chat must fit the conversation context, without documenting its per-read transfer
or filtering granularity
([Anthropic](https://support.claude.com/en/articles/10166901-use-google-workspace-connectors)).
Official ChatGPT Work guidance says usage depends on model, environment,
reasoning/speed settings, task complexity, tools and frequency; tokens measure
information read and written, while actual billing depends on the workspace's
agreement, credits and settings
([OpenAI](https://learn.chatgpt.com/docs/enterprise/chatgpt-work-usage-and-cost)).
File bytes therefore do not establish token use, credits or invoice impact. No
cited product limit proves that a managed connector will reliably read or filter
a larger Drive JSON page.

For the named products, the resulting evidence status is specific: ChatGPT Work
has current usage guidance but no documented School-OS Drive-page retrieval
granularity; the Gemini source describes Gemini Apps generally, not a Spark
per-page read guarantee; Claude documents an aggregate conversation-context
condition, not a file-read limit; and no reliable current public documentation
reviewed here establishes Grok Bot's Drive-page transfer or context behavior.
Those route properties remain unknown until observed in an authorized trial.

## Measurements for the three authorized trials

Add the following observations to each isolated trial protocol. This prepares
evaluation; it does not start testing or expand trial authority.

1. After each intended write and actual readback, record privately the exact
   UTF-8 bytes of the serialized page, page family, record count, largest record
   size, and packing percentage against 64 KiB. For whole-record size, publish
   only aggregated, privacy-safe values: count, minimum, median, maximum,
   percentage above 64 and 128 KiB, and p90/p95/p99 only when the sample size
   makes those percentiles meaningful. For actual canonical page size, publish
   the same supported summaries without implying that a conforming page can
   exceed the current maximum.
2. Independently compare every saved Knowledge claim and Task with source-bound
   expectations. Report missing, merged, duplicated, overbroad, or unsupported
   meaning. A zero-action source needs source-grounded justification. This
   measures semantic completeness, not raw-text preservation.
3. For each write, readback, and query, record observable Drive/tool calls,
   pages requested, bytes returned when exposed, errors and retries, and elapsed
   time. Record model-visible or billed input tokens only when the product
   exposes them; otherwise mark them **unknown**, never estimate them from bytes.
4. Use the already planned source-grounded retrieval questions, including facts
   near the beginning, middle, and end of any large page and questions requiring
   one versus several records. Score source-supported answer completeness,
   qualification preservation, query-scope exhaustion, irrelevant records
   surfaced, citations/evidence traces, and end-to-end latency.
5. From the final serialized records, compute counterfactual page counts and
   total page bytes for 64, 128, and 256 KiB packing, preserving family and route
   boundaries. This is offline sizing analysis, not an alternate ingestion run;
   it cannot establish retrieval quality or product cost.
6. For the current three trials, report these fields separately for ChatGPT
   Work, Gemini Spark, and the fresh context-free worker: access route used,
   whether filtering occurred before model context, exact token visibility,
   maximum successful page observed, and all unknowns. Apply the same checklist
   to Claude Cowork and Grok Bot only if later qualification of those products
   is authorized. Do not infer one product's behavior from another's.

The requested evaluation uses the prepared, marked noncanonical 64, 128, and
256 KiB comparison pages in the same instance, built from the same already-
ingested records, and asks the same source-grounded questions after full
publication. It does not reread the source or create another instance. Record
whether each larger page was actually transferred, filtered and exposed to the
model. If no larger page is actually exercised, report 128 and 256 KiB as
**unexercised** rather than treating the absence of failure as validation.

Revisit the cap when a source-supported whole record exceeds 64 KiB or trial
measurements show that a 128 or 256 KiB maximum would materially improve I/O or
query behavior without unacceptable route-specific cost. The next decision
should use preserved record and route evidence rather than adding a speculative
overflow format.
