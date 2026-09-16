# Continue missed or interrupted ingestion

Use this procedure to continue an authorized logical ingestion run or start its
next authorized run. It relies on readable Drive records and original sources,
not the previous agent, conversation, local download directory or pagination
token. Read [ingestion](ingestion.md), [identity](../contracts/identity.md) and
[storage](storage.md). This is ordinary continuation, not an interrupted-write
repair engine or a scheduling service.

## Reconstruct the work from Drive

1. Resolve the instance entry point, current source scope, logical mailbox,
   import boundary and selected source/Drive semantic adapters. Verify current
   authorized access. A newly connected account with a similar display name is
   not automatically the same logical mailbox.
2. Traverse the relevant bounded discovery and source directories, following
   continuations. Find unfinished windows and known in-scope `not_ingested`
   emails. Resolve references through the data and storage contracts. An
   inaccessible directory or unfinished lookup leaves the work inventory
   incomplete; do not equate it with no pending work.
3. For a continued run, retain its declared scope and run-start cutoff. For a
   newly requested daily run, fix a new cutoff at its start and include known
   older pending work through it. Add arrival windows from the last completed
   boundary, including that boundary at its actual precision. Do not use a
   maximum original sending Date as a substitute for discovery progress.
4. Read only the relevant window, source and coverage pages as needed. Use
   ordinary references to locate existing Knowledge and Tasks; do not load the
   whole household history to rediscover the plan.

The agent manages adaptive resource use and may read chunks within the logical
run. There is no School-OS message cap, fixed batch scheduler or partial-success
quota. If the current agent cannot finish, save normal progress that it can
verify and state the concrete unfinished scope. Do not call that run complete.

## Replay an unfinished window when a token is unavailable

Saved tokens are replaceable access aids. If the selected route cannot use one,
repeat the saved unfinished interval using its mailbox, scope, time meaning,
bounds and inclusivity:

1. Restart listing that interval through a supported route.
2. Follow every continuation, including after short or empty pages.
3. For each individual message, perform the metadata association and complete
   relevant index lookup. Reuse the owned Email ID when supported.
4. Reuse a saved verified `fully_ingested` result unless explicit new or
   contradictory inventory/coverage evidence challenges it. A different
   provider handle or unknown optional metadata alone does not reopen it.
5. Process known `not_ingested` emails as whole emails. Finish all relevant
   newly discovered messages and preserve unresolved associations.
6. Save normal progress and mark discovery complete only when the selected
   route establishes exhaustion. Separately establish whole-email ingestion
   completion before finishing the logical run.

For example, if September 1–3 is complete and September 4 is unfinished, the
fresh agent can repeat September 4. It need not reproduce the old token, page
number, search-result order or provider-entry count. Metadata-based reuse and
canonical coverage prevent those access details from defining completion.

## Continue whole-email processing honestly

A `not_ingested` email needs the complete required body and attachment work
under [extraction](extraction.md). Saved candidate observations can explain a
blocker, but they are not a per-part resume contract. Do not promote the email
because an earlier agent said it read a body or because some Knowledge exists.

Preserve previously verified Knowledge and parent task state while reconciling
the whole source again. A new school acknowledgment may support a completion
review; it still cannot replace parent confirmation. If required material is
unavailable, retain the whole-email outcome and report the specific limitation.
An expired attachment locator calls for supported source retrieval, not a new
canonical attachment identity or a guess from its filename.

## Respect the persistence boundary

Normal page writes and readback are described in
[storage](storage.md#normal-save-sequence). They are independent operations.
Interruption can leave a canonical page, catalogue, locator or derived index
out of step. The retained MVP does not guarantee discovering or repairing every
such condition, and it does not provide atomic cross-page saves.

Use the existing bounded read/fallback procedure when it can establish the
current state. A stale hint is not proof that a record is absent. Do not blindly
create another Email, Knowledge record or Task after an uncertain write, or
invent a generic journal, rollback, schema migration or repair process. If the
state needed for safe continuation cannot be established, preserve the available
evidence, identify the affected scope and ask for a specific resolution rather
than claiming recovery succeeded.

A source read error, unknown write outcome and proven provider rejection are
different observations. Describe only what the available evidence establishes.
Do not infer throttling from a generic failure. Follow repository privacy
instructions during development; operating records must not leak credentials
or raw private connector errors into shared documentation.

## Missed runs and reporting

An authorized later run fills the interval after the last completed arrival
boundary plus known unfinished windows and email backlog. It does not need a
School-OS scheduler or a history of prior agent conversations. The approved
arrival-window policy can miss older material that becomes visible only behind
an already completed boundary. Disclose that limit when relevant; an explicit
historical rescan can revisit those dates. Do not add a full-history daily scan
or fixed overlap as an unapproved recovery policy.

At a handoff, report:

- the verified instance/mailbox and authorized scope;
- the fixed cutoff and discovery windows complete or still unfinished;
- known `not_ingested` or unresolved items, with precise blocking reasons;
- normal saved references needed to find that work, including any known stale
  index or uncertain persistence state; and
- the next supported action and any tool capability still missing.

Drive is the durable work description; a handoff paragraph is a convenience,
not the sole copy. Do not promise an automatic wake-up, parallel updater or
unrequested send. An ordinary daily brief waits for complete ingestion.
Separately authorized limited queries or the parent-chosen manual brief path
must describe their gaps and never change the ingestion result to complete.
