# Agent execution guidance for the revised MVP

Status: retained execution instructions authored from the approved Q1–Q9
architecture and the user's D4/D6 directions. They are untested. Q10's exact
oversized-value segment representation remains pending and blocks a complete MVP.
This document specifies outcomes and gives resource-management advice. It does
not implement a batch controller, scheduler, environment-recovery engine or
canonical-write repair system. D3 now selects minimal Python standard-library
helpers and otherwise agent/tool work. The separate records/ordinary-save
framework is excluded, not a prerequisite; preserve approved data meanings and
normal verification. The [active plan](../PLAN.md) records Q10 and the publication
boundary; there are no remaining Q1–Q9 decisions.

## Authoritative operation routes

Use the current retained files rather than historical proposals: read
[`contracts/data.md`](../../../../contracts/data.md) and
[`contracts/identity.md`](../../../../contracts/identity.md), then select the
needed procedure from [`operations/README.md`](../../../../operations/README.md).
Startup and storage use [`startup.md`](../../../../operations/startup.md) and
[`storage.md`](../../../../operations/storage.md); source work uses
[`ingestion.md`](../../../../operations/ingestion.md),
[`extraction.md`](../../../../operations/extraction.md) and
[`continuation.md`](../../../../operations/continuation.md); knowledge and tasks
use [`knowledge.md`](../../../../operations/knowledge.md),
[`query.md`](../../../../operations/query.md) and
[`task-sync.md`](../../../../operations/task-sync.md); ordinary daily composition
uses [`daily.md`](../../../../operations/daily.md) and the selected brief recipe.
Shared tool meanings live under [`adapters/`](../../../../adapters/README.md).
The [data examples](../../../../examples/data/README.md) and
[ingestion examples](../../../../examples/ingestion/README.md) are fictional and
illustrative, not execution evidence.

## Responsibility

School-OS supplies its data meanings, identity/coverage rules and operation
recipes. The user's executing agent owns the practical execution: choose usable
tools/adapters, assess actual resource limits, organize batches and continue
until the operation's complete scope is processed. One logical daily run may
involve many tool calls, code invocations and internal batches.

A batch boundary is not the daily task's completion boundary. There is no
School-OS rule to stop successfully after 25 emails or 100 listing results, no
fixed 8 MiB application transfer ceiling, and no School-OS-managed queue that
reschedules the rest. Actual tool/runtime limits still matter. The approved D1
limits on individual canonical pages and directory pages remain in effect.

The MVP relies on the capable executing agent retaining normal task continuity
and using its own continuation/recovery facilities. School-OS does not guarantee
recovery from every complete environment reset or repair interrupted canonical
writes. Canonical processed knowledge, source references and verified coverage
still belong on Drive; conversation or local files do not establish canonical
identity or completion. Another capable agent can read already saved knowledge.

## Before processing

For first setup, follow the [parent interview](../../../../operations/setup.md):
offer task tools known and available to this agent, state limitations and let the
parent choose. Follow [adapter creation/reuse](../../../../operations/tool-adapters.md)
when the selected accessible tool needs a mapping. One shared adapter per tool
holds School-OS-to-tool semantics; each agent's connector supplies API access,
authentication, transport and actual calls. Do not fork the adapter per agent or
confuse a missing mapping with missing connector capabilities. Use the shared
mapping again on later operations and from fresh agents.

- Read the selected recipe, configured school/source scope and relevant Drive
  state. Do not load all historical knowledge merely to begin a daily operation.
- Establish the approved daily scope: all relevant School-OS-pending school mail
  within the configured source/import scope through the start of the run,
  including older unfinished work. Later arrivals belong to the next run.
  The mailbox's read/unread icon does not determine School-OS processing.
  This finite cutoff is not a message quota or an agent batch boundary.
- Identify the source metadata/content, Drive persistence, task and delivery
  operations actually needed. Use existing authorized capabilities; do not infer
  them merely from an agent supplier's name or from code-execution capability.
- The user and agents manage schedules and avoid concurrent operation on the
  same instance data. School-OS adds no scheduler register or locking service.

## Use the actual helper when it applies

The initial helper script is
[`helpers/source_metadata.py`](../../../../helpers/source_metadata.py), documented
in [its guide](../../../../helpers/README.md). It is authored but untested; the
current development session must not run it. During later authorized operation,
an agent with suitable execution access can use these pure routines:

| Recipe step | Actual callable | Required boundary |
|---|---|---|
| Prepare subject comparison | `normalize_subject` | Supply the observed subject with its known `raw_header` or `decoded` representation; retain the original separately. Do not infer representation from encoded-looking text. Unsupported input stays explicit, never lossy-decoded into a guessed identity. |
| Prepare address comparison | `normalize_address_parts` | Supply already reliably extracted local part and domain. It does not parse an arbitrary display label, infer an address or discard local-part spelling. |
| Respect D1 page size | `utf8_size` | Measure the exact final text intended for the page. It does not create records, serialize JSON, split pages or save them. |

These helpers perform mechanical steps of approved rules. They do not decide
email identity or whether processing is complete. Dates, recipient roles,
source account, discovery, attachment reading, meaning, tasks, saving/readback
and external actions remain agent/tool operations. Follow the same approved
procedure through available tools when a helper is not applicable; do not invent
new semantics or require a new execution/persistence framework.

## Approved identity threshold and ingestion outcome

Automatic logical-email association requires verified mailbox, original subject,
normalized sender and the individual message's original Date with a known
timezone and second-or-finer precision, adequate relevant index lookup, and no
contradictory comparable evidence. Use an available richer metadata view when
the listing cannot establish those facts. If the required evidence remains
inadequate, keep the association unresolved; do not invent seconds or a timezone,
substitute received/provider time for original Date, or use content as identity.
Unknown optional metadata is not a contradiction or a reason to create a duplicate.
Several compatible logical records remain ambiguous. The helpers alone do not
establish this threshold or qualify any connector.

The logical email's ingestion outcome is binary: **fully_ingested** or
**not_ingested**. Mark it fully ingested only after the body and required
attachment material have been read, their substantive information extracted,
and the resulting knowledge, source references and actual coverage saved and
checked. Required attachments remain in scope. If those conditions are not met,
the email is not ingested; do not call a processed body a completed partial email.
This sets the outcome's meaning, not a new persisted field layout.

The agent may read material in resource-sized chunks, but those internal steps
do not create a supported partial-email completion or part-by-part resume
workflow. Preserve honest evidence of what was and was not read; a blocked or
unknown result must not become fully ingested. The MVP does not promise repair
of interrupted canonical writes.

A unique supported metadata match may reuse a previously saved and verified
`fully_ingested` result under the approved rule in
[`contracts/identity.md`](../../../../contracts/identity.md). Skip content only
when that canonical coverage is verified and no explicit new or contradictory
inventory/coverage evidence exists. Metadata alone never proves prior processing;
`not_ingested`, absent/unverifiable coverage or new required material requires
whole-email ingestion.

## Advice for managing resources

Choose practical batch sizes for the current tools, context, memory and time
limits. Start modestly where limits are uncertain; adapt from observed behavior.
This is advice for the agent, not a mandatory batch-size algorithm or threshold.

Keep only the current source material and necessary canonical pages in temporary
working storage. Preserve useful normally saved progress and accurate coverage
on Drive with the already approved data meanings and source/coverage distinctions. Leave enough room
to verify persistence before releasing temporary raw copies. Do not use a local
processing cache as the only record of completion.

Use the agent's own means to retain the task and continue through its batches.
A local code-process restart need not end the logical run if the executing agent
can continue. If an interrupted write has an uncertain result, inspect what can
be established and report the limitation; this guidance does not authorize
inventing or promising a general canonical repair protocol.

Follow source pagination after short pages when continuation is available. Keep
discovery progress separate from content coverage. Lost temporary tokens permit
replaying a saved unfinished window; allowed metadata supports logical-email
association, but a match cannot prove unread content was processed. Use source
metadata only for email/reply/attachment identity. Read content to extract its
substantive information, qualifications and actions.

Process all available required attachment candidates with honest inventory and
read coverage. For large material, use an available supported reading route
within actual limits. Q10's persisted segment shape is not approved. Until it is
integrated, an oversized substantive value blocks retention and full ingestion.
Do not invent a segmentation capability, truncate school information or mark
unsupported content complete. Lack of access or usable content support is a
blocker to full ingestion, not a reason to silently omit it.

## Task evidence and selected brief recipes

Follow [completion review](../../../../operations/completion-review.md) when
clear observed evidence satisfies a linked task: save detected completion awaiting
parent confirmation, use the shared adapter's status/section mapping and accept
actual parent confirmation through D5 sync. Do not report the detected state as
completed.

Follow the [chosen brief recipe](../../../../operations/brief-recipes.md). The
daily starter includes newly verified/corrected information, original source
dates and relevant open tasks, disclosing failed task-app sync. Users and agents
may author and choose any number of compatible recipes. This does not relax the
ordinary daily coverage gate below. The approved manual limited-brief path has
its own disclosure and parent-choice step.

## Completion before the daily brief

Before composing the ordinary daily brief, verify that the entire agreed input
scope has been discovered and processed, that required source/attachment coverage
is complete, and that extracted knowledge/tasks/source links are saved and
verified by the executing agent against the intended saved values. Tool-call success, matching
metadata, provider entry counts and finished batches do not independently prove
this result.

When more work remains, continue within the same logical task using the agent's
own resource-management facilities. When a real access, resource or content
blocker prevents completion, report that the ingestion task is incomplete and
what blocks it. Do not compose the ordinary daily brief from a knowingly
incomplete input selection. The exact alert channel/automation is not specified
by this instruction and is not a new School-OS notification service.

This does not prevent answering a separate knowledge question with verified
facts and an explicit limitation under the already approved query-coverage rule.
A qualified answer to a question is different from declaring the daily ingestion
and brief complete.

## Manual briefs and configured audio

For a manual brief with known gaps or uncertain freshness, warn that saved
knowledge may be outdated. State the latest relevant source date available in
verified knowledge and the known ingestion freshness, identifying either as
unknown when necessary. Do not call the latest saved source the latest email
the school actually sent unless discovery supports that claim. Ask whether the
parent wants fresh mail ingested first or wants the current verified information
now with those limits. Honor an existing explicit choice rather than asking
again. Send the limited brief only when the parent chooses that option; include
the freshness warning and material gaps in the output. If the parent chooses
ingestion first, process within the authorized scope and capabilities before
composing. Neither path makes an incomplete ordinary daily run complete.

When audio is configured for an email brief, prepare the written brief and its
audio for delivery together. If audio generation or availability is verified to
have failed, send the authorized text email with an explicit audio-failure
notice. An unknown generation or send result is not a verified failure; apply
the uncertain-action rule below before deciding what happened. Do not add a
timeout, deadline, scheduler or blind resend to force an outcome.

Keep no canonical audio archive. After verifying audio delivery to the authorized
email or chat destination, discard the accessible temporary audio copy. Retain
truthful source/output attribution as required, without retaining audio bytes
on Drive. Do not claim to erase provider-managed copies or the copy delivered
to the parent. Audio selection does not itself authorize a recipient, send or
generation operation, and no actual audio route is qualified by this guidance.

## Checking an uncertain external action

The executing agent assesses whether it has authorized tools/API access to
inspect the result. Use those means when available. Examples include inspecting
the actual sent email or reading the saved task and its School-OS identity in
the selected application. Explain the evidence and what it establishes.

An exposed send tool does not guarantee a usable sent-message lookup. A generic
error establishes neither success nor failure. Incomplete/empty search results
may not prove non-application. Where evidence is insufficient, keep the result
unverified and surface the limitation; do not blindly resend or recreate it.
The agent judges and explains what its evidence establishes; no new central
evidence-threshold or retry service is required. New canonical record/adapter
meanings still need approval. No durable School-OS effect engine or exactly-once
guarantee is selected.

## Development boundary

These instructions are authored deliverables, not an executed recipe or proof of
supplier capability. No early tests, simulations, probes, ingestion, sends or
schedules are authorized. An accepted incomplete checkpoint may be published with
Q10 and the untested state explicit, but it does not satisfy the trial prerequisite.
After Q10 is approved and integrated, publish the complete retained MVP and verify
its exact remote revision. Then conduct only the three already authorized isolated
seven-day school-email ingestion trials: a fresh context-free worker, Gemini Spark
and ChatGPT Work, each in a separate new instance. That sequence needs no new
permission round; it does not authorize outbound briefs, personal task-app writes,
schedules, unrelated qualification or changes to existing instances.
