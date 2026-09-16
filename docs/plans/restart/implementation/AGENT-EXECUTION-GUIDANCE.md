# Agent execution guidance for the revised MVP

Status: instructions grounded in the user's explicit 2026-09-15 D4/D6 directions.
This document specifies outcomes and gives resource-management advice. It does
not implement a batch controller, scheduler, environment-recovery engine or
canonical-write repair system. Exact record, adapter and first-use contracts
remain subject to the [active plan](../PLAN.md).

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

- Read the selected recipe, configured school/source scope and relevant Drive
  state. Do not load all historical knowledge merely to begin a daily operation.
- Establish the intended work scope. The proposal to include all School-OS-pending
  school mail through run start, including backlog, is awaiting approval. Do not
  silently adopt that cutoff, another cutoff or the mailbox's unread flag as the
  sole definition. Mailbox read/unread state is not evidence of School-OS coverage.
- Identify the source metadata/content, Drive persistence, task and delivery
  operations actually needed. Use existing authorized capabilities; do not infer
  them merely from an agent supplier's name or from code-execution capability.
- The user and agents manage schedules and avoid concurrent operation on the
  same instance data. School-OS adds no scheduler register or locking service.

## Advice for managing resources

Choose practical batch sizes for the current tools, context, memory and time
limits. Start modestly where limits are uncertain; adapt from observed behavior.
This is advice for the agent, not a mandatory batch-size algorithm or threshold.

Keep only the current source material and necessary canonical pages in temporary
working storage. Preserve useful normally saved progress and accurate coverage
on Drive under the eventual approved record/write contract. Leave enough room
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
within actual limits. Do not invent a segmentation capability, truncate school
information or mark unsupported content complete. Lack of access or usable
content support is a blocker to full ingestion, not a reason to silently omit it.

## Completion before the daily brief

Before composing the ordinary daily brief, verify that the entire agreed input
scope has been discovered and processed, that required source/attachment coverage
is complete, and that extracted knowledge/tasks/source links are saved and
verified under the approved normal-write contract. Tool-call success, matching
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
supplier capability. No tests, simulations, probes, ingestion, sends or schedules
are authorized. After publishing the agreed MVP implementation, stop and let the
user direct testing.
