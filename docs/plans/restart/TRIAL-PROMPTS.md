# Realistic first-use trial handoff

Status: the user explicitly directed all three tests and uploads to start.
Use this handoff for the current trials; preserve the no-repair boundary inside
each round.
The user requested a normal new-user setup, not a developer-authored trial prompt.
The [protocol](TRIAL-PROTOCOL.md) belongs to the evaluator; it is not an attachment
for the agent being tested. The [earlier guided prompts](TRIAL-PROMPTS-GUIDED-HISTORICAL.md)
remain historical evidence only.

## The complete opening message

Send the same published fresh starter ZIP link and these words to each new session:

```text
{{PUBLISHED_STARTER_ZIP_LINK}}
setup my schoolOS
```

Nothing else belongs in the opening message: no repository paths, 17-file reading
list, private filled configuration, developer plan, expected answers, prior trial
transcript, evaluator protocol or special route wrapper. The ZIP contains the
reusable School-OS instructions and an empty, unconfigured instance area. It
contains neither household values nor preallocated canonical record IDs.

Use one new context-free **Sol** worker, one new Gemini Spark session, and one new
ChatGPT Work session, when the user directs testing to start. Never reuse a worker
that participated in development or a previous trial. Do not use Astra workers.
Record any platform-injected instructions or local repository visibility as an
environment difference; a context-free launch alone does not prove identical
harnesses. Do not secretly supplement a struggling agent's setup instructions.

Spark and ChatGPT Work use the user's existing signed-in Chrome profile. Keep
their conversations, controllers, serially operated tabs, Drive destinations and
private evidence separate. Record the shared profile, cookies/account state and
any unknown provider memory as methodology limits; do not claim account-level
isolation. Any detected cross-route contamination invalidates the comparison.

Before every message after the opening request, the evaluator verifies the exact
provider, provider task, conversation, route, assigned Drive root, current stage
and task-bound composer against the private round manifest. Never send through a
top-level composer or an unverified/mismatched task composer. Record the current
state as `active`, `awaiting_user_input`, `completed`,
`approval_blocked_before_delivery`, `dispatched_unknown_effect` or
`controller_observation_unavailable`. A later final response replaces an earlier
running snapshot as the current observation. If control is unavailable, stop the
follow-up instead of guessing that the task is still running or has failed.

Only one identical launch retry is available, and only after preserved evidence
proves no dispatch and no effect. Label it `proven_no_dispatch_retry` and keep it
separate from the initial attempt. Unknown dispatch or effect blocks retry.

## What should happen without coaching

1. The agent opens the link and reads the starter folder's entry documents.
2. README, START-HERE or AGENTS points it to `system/operations/setup.md`.
   `CLAUDE.md` contains only `@AGENTS.md`; no separate Claude procedure exists.
3. The agent interviews the parent for the missing household/school, timezone,
   source scope, Drive destination and tool choices. It explains options actually
   available to that agent and reuses known explicit answers.
4. It uses the shared School-OS mapping for a selected tool, or authors a missing
   conformant mapping. Its own connector supplies access/API operations.
5. It establishes the private instance in the chosen location, saves the current
   instructions and approved configuration, and checks actual saved values.
6. It reports setup success or a precise blocker and explains that ingestion has
   not happened merely because setup is complete.

Discovering and following that sequence is the behavior under evaluation. A
failed download, missing instruction discovery, unnecessary question, unsafe
assumption or unverified save is recorded as observed, not repaired silently.

## Interview answers and isolation

The coordinator holds a private answer sheet, using the same household and source
choices for all routes. Supply an answer only when the agent asks for it; do not
transfer the filled sheet. Respect any required permission for disclosing private
information to an external provider. Previous private-upload rejection is not
permission to paste the same information through another channel.

When asked for the destination, provide that route's distinct fresh child folder
under School OS tests and state: keep all persistent Drive writes inside this
folder; disregard previous School-OS instances and never read, edit or delete
them. Preserve old failed trial folders and unknown effects. New trials receive
new folders, not reused failed roots. If necessary, give this isolation instruction
before the first write; record it as a scope answer/intervention, not product
instruction. Do not let the agent guess a destination from another instance.

Answer tool preferences honestly. For these ingestion trials, no external task-app
updates, email sends, audio generation, mailbox changes or scheduled jobs are
permitted. Canonical tasks inside the assigned instance are in scope. A tool may
be selected/configured without exercising its outbound effects.

## Separate ingestion request after setup

After actual setup readback, give a normal scoped request to ingest the in-scope school
emails in the common seven-day interval, including required attachments, using
read-only mailbox access. State the exact received/arrival-time start and end,
timezone and boundary meaning. Those inputs are interview/request context, not
an extra implementation manual. All routes use the same package revision and
interval; record both privately before starting the series.

Use the installed ingestion recipe. A connector limitation must remain visible;
do not supply hidden extraction shortcuts or evaluator expectations. Before the
ingestion request, preflight the independent oracle against the exact private
round-manifest bytes. The manifest and oracle must agree on the same
`[start,end)` interval, timezone and precision; discovery continuation must be
explicitly exhausted; every candidate must have a supported comparable
arrival/received timestamp; and the evaluator applies the boundary locally. The
prior source oracle supports only its exact manifest and interval. Reject it for
any other interval and prepare a newly bound independent oracle.

Evaluator-only preflight stays out of the agent prompt. Before any source or
Drive dispatch, verify the owner-only private receipt sink and validate the
proposed call arguments against that route's exact callable signature. Keep an
invalid call local; do not dispatch it or relabel it as a provider error. Bind the
oracle to exact private source-input bytes and require one independently
exhausted, receipt-backed pagination chain for every private query alias declared
there. During audit, traverse the contract-defined nested references and
continuations rather than a remembered field list. Use downloaded reports only
when the same-task export receipt's artifact digest and byte count both match the
artifact metadata and downloaded bytes. Use image-specific expectations only
after independent review of the exact pixels or a faithful private rendering.

## Questions and page-size evaluation come later

After ingestion, ask the same small set of independently source-grounded questions
against each agent's saved canonical data. Ask for sources, freshness limits and
an observable account of which saved information supports the answer, not hidden
reasoning. Never supply expected answers. Preserve detailed private traces only
through authorized channels.

The evaluator then applies the [page-size comparison](TRIAL-PROTOCOL.md#page-size-measurement-and-narrow-comparison):
64 KiB canonical pages, whole-record overflow evidence, and a private noncanonical
64/128/256 KiB comparison. This evaluation request comes after the ordinary
product flow; it must not turn the initial setup prompt into a test manual.
No missing capability, unobserved cost or unexercised size is reported as passed.
