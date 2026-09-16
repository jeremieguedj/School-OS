# Agent instructions

Read [START-HERE.md](START-HERE.md) first and select the actual context.

## Parent setup or instance operation

If a parent supplied a fresh School-OS ZIP or folder link and said “setup my
schoolOS,” follow the one authoritative [setup procedure](operations/setup.md),
packaged at `system/operations/setup.md`. Discover and read the fresh starter
before expecting an instance ID, configuration or installed bootstrap. The
starter's `instance/` and `extensions/` areas are initially empty. Ask only for
missing household, school, mailbox, location and tool choices, show the actual
options available to this agent, and preserve choices already made.

The link is access to system material, not a credential or authorization for
ingestion, task mutations, outbound messages or schedules. Keep setup and those
later operations under their separate instructions and authority. Use current
shared API-agnostic semantic adapters or author a conformant missing mapping as
the setup procedure allows. Persist and read back only the current approved
configuration and canonical bootstrap; do not invent a setup schema, installer
state or prefilled identity.

For an existing configured instance, use its readable entry point and
[startup procedure](operations/startup.md). Preserve its data, explicit choices
and extensions. Do not apply the repository-development workflow below to an
ordinary parent setup or operation.

## Repository development

When maintaining this repository, follow
[development continuity](START-HERE.md#repository-development-continuity) and the
[current restart plan](docs/plans/restart/PLAN.md). The snapshot
`orgos-restart-documentation` preserves the former instructions and implementation.

## Development and evidence

The new project uses the approved restart contract and agent-led operations.
Retired packet validators, generation runtimes, provider-derived IDs and the old
release builder are historical evidence, not implementation dependencies.

For School-OS repository development and the specifically authorized ingestion
trials:

1. Keep private instance material out of Git, patches, terminal output and chat.
   Preserve complete connector receipts or thrown exceptions before normalization
   in mode-0600 files under an admitted gitignored private directory. Publish only
   synthetic examples and privacy-safe findings. Do not log real message content,
   provider IDs, URLs, request arguments, credentials or unsanitized errors.
2. Classify failures from evidence: local validation, dispatch, transport/no
   response, provider error, or response normalization. A generic error is not
   proof of throttling, auth failure, timeout, failure of a write, or success.
3. Inspect complete response topology, types and conflicting duplicated values
   before repairing a connector interpretation. Keep connector envelopes and
   display metadata separate from canonical source evidence. Derive fictional
   fixtures for observed shapes; a fixture invented from memory is not evidence.
4. Distinguish supported equivalent empty forms from absent/unknown source data.
   Do not normalize a missing inventory into a known-empty one. Compare actual
   readback with intended values; echoed write requests are not readback proof.
5. Preserve future failures and verification evidence privately. Normal reports
   may include stage, response-observed state, supported status/reason, retry
   advice and a private receipt path. If no reason/status is supplied, record
   that absence. Unknown effects require available verification, not blind retry.
6. Bind independent semantic expectations to the exact source evidence reviewed.
   Developer receipt hashes may bind audit evidence privately; never use content
   hashes as canonical email/attachment identity. Keep the expectation independent
   of the tested agent's generated output; an empty extraction is a substantive
   claim requiring source evidence, not a reusable default.
7. Independently compare the saved knowledge/task inventory against the source
   expectations, including finite, conditional and recurring action dispositions,
   scope, qualifications and correction relationships. A self-audit copied from
   output is insufficient. A zero-action result requires justification and must
   not manufacture a task-provider action merely to advance a brief operation.
8. Follow the active plan's execution boundary. Prepare meaningful fictional
   checks without running them before implementation publication. Subsequent
   testing authority covers only the named isolated ingestion/audit trials;
   it does not authorize every historical suite, schedule or provider effect.
   When a defect needs a repair, preserve the exact evidence and ensure the
   targeted recheck is within authorization before executing it. Never report
   an unexecuted check or a publication-hygiene check as functional validation.

Do not adopt a new architecture while fixing a failure. Escalate a new decision
with a concrete recommendation and tradeoffs; continue independent approved work.
The coordinator owns Git/publication and manages at most three bounded workers.
