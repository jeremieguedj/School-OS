# Daily-run operation

## Purpose

Process new relevant communications losslessly, reconcile private derived records and task state, then render and deliver the approved daily brief. The operation is standalone: current private files and provider state, never conversational memory, determine its behavior.

## Declared private dependencies

Resolve the routine's private dependencies by the exact reference to
`daily-run-personal-values.md` in the instance manifest. Do not discover a
dependency by filename when an exact reference is available. The full logical
file map is for onboarding, upgrades, recovery, and maintenance; routine daily
runs do not sweep it.

- **Routing and release:** instance manifest, active installed `release.yaml`, and this installed operation recipe.
- **Daily values:** the private daily-values document, containing only daily source/canonical references, household values, approved customization, and a runtime-profile reference.
- **Phase selectors:** private integration configuration selects the mail, task, runtime, scheduler, and optional audio adapter. Each phase then reads only the configuration/state declared by its selected adapter.
- **Control state:** operation state, runtime profile, mail discovery checkpoint, task-provider cursor and bindings, delivery ledger, and final run checkpoint.
- **Canonical data:** source-catalog folder and index, canonical task register, and the exact existing catalog records selected by source identity, all resolved from daily values or the current phase's adapter configuration.
- **Derived data:** rolling updates, recent guidelines, durable profiles/references, and the knowledge/run index.
- **Installed recipes:** `attachment-processing.md`, `task-sync.md`, and `brief-rendering.md` from the same active release.
- **Selected adapters:** runtime, mail, task provider, scheduler for a scheduler-issued execution, and optional audio.

The daily-values document must resolve, at minimum, the source checkpoint/catalog, canonical action register, guidelines, rolling updates, brief template, delivery state, and final run checkpoint. Each adapter selector must resolve before its phase begins. Missing or ambiguous references stop the affected run before provider access or writes.

Legacy prompts and adapters may be retained as migration evidence, but they are not behavioral dependencies of this operation and must not supply undeclared production rules.

## Required capabilities

Every capability below must be recorded as `available` in the capability profile for the exact runtime, provider authorization, and execution surface before writes are enabled:

```text
storage.scoped_list
storage.read_complete
storage.create_file
storage.replace_verified
storage.get_metadata
mail.search
mail.read_complete_message
mail.read_complete_thread
mail.list_attachments
mail.send
mail.verify_send
tasks.read_identity
tasks.discover_configuration
tasks.list_complete
tasks.read_comments
tasks.create
tasks.update
tasks.write_comment
tasks.verify
```

The task baseline above matches complete-snapshot reconciliation. The snapshot
must expose current status, Action, Group, planned due, progress, and completion
comment values for the entire configured scope. Core compares it with the last
durable parent snapshot; it does not claim unobserved intermediate activity.
`tasks.update` must cover guarded mapped-field updates, including Group and the
core-authorized status changes used for completion policy and reopen. The
selected adapter may declare additional required capabilities when its normal
snapshot omits current completed tasks or another required current field; those
adapter-specific additions do not become unconditional requirements for a
complete-snapshot adapter.

For a scheduler-issued run, `scheduler.inspect` and `scheduler.verify` are also required. Scheduler creation, cutover, pause, or replacement additionally requires `scheduler.ensure` and `scheduler.disable`. A qualified direct manual run requires no scheduler capability and invokes the same `school_os.daily.run_daily` sequence.

`mail.read_attachment` is conditionally required only when attachment extraction is attempted; otherwise record the explicit unavailable/unsupported outcome defined by `attachment-processing.md`. `audio.generate` and `audio.retrieve` are optional and apply only when audio is enabled. Optional failure must use the documented degradation and must never fabricate content or success.

Interactive evidence does not prove scheduled-surface conformance. If authentication, adapter selection, model/effort, or provider configuration changes, recheck the affected capabilities before the next side effect.

## Ordered phases

### 1. Preflight

1. Read the instance manifest, the private daily-values document, the exact
   profile-selection object and selected entrypoint profile, and the integration
   selectors needed for this run. Capture one local date in the configured
   timezone and bind it with the source scope, profile bytes, entrypoint, and
   delivery variant in the operation checkpoint scope.
2. Verify release version, installed reference, data compatibility, and completed migration state agree. Do not re-audit historical migrations on an unchanged routine release.
3. Validate the approved runtime-profile revision/fingerprint and resolve the selected adapter only when entering its phase. A mismatch requires setup/health validation before side effects.
4. Require operation admission and serialization evidence. A manual run uses its attended-single-writer evidence; a scheduled run uses verified scheduler/runtime serialization. Both invoke the same daily sequence. The scheduled runtime relies on its conformance record and need not require fresh run-now provenance. Do not create or wait for a separate Drive lease.
5. Require operation state and private policy to permit the intended reads, writes, provider actions, delivery, and cursor advancement. A cutover must use one supervised first-production run before ordinary recurring delivery is considered verified. When a scheduler exposes its authenticated **Run now** control only while the task is enabled, that single owner-approved supervised invocation may run with the one production schedule enabled; the schedule remains subject to full post-run verification before it is treated as normally active.
6. At a planned boundary, checkpoint the verified predecessor output and return
   `NEEDS_CONTINUATION`; do not describe later phases as complete. A resumed
   invocation uses the same operation ID with a new attempt ID, verifies the
   exact predecessor and matching release/configuration evidence, then begins
   at the next phase. Reconcile every pending or unknown effect before any
   repeated provider action.

### 2. Discover

1. Read the most recent successful mail checkpoint. If none exists, use the configured initial-overlap window. Otherwise search from the earlier of the persisted checkpoint and the configured safety overlap.
2. Build the provider query only from the private source-scope configuration
   and selected mail adapter. Exclude configured forbidden locations and
   content classes. When exact epoch-millisecond seed bounds are configured,
   use only adapter-owned widened provider predicates that cannot exclude a
   valid boundary hit; a competing date predicate in the private query blocks.
3. Paginate to completion, read every search hit in full, and admit it as a
   seed only when `seed_after_inclusive_ms <= internal_date <
   seed_before_exclusive_ms` for whichever optional bounds are present.
   Preserve the provider cursor/page evidence and deduplicate by immutable
   source conversation identity.
4. Fetch every ordered member of each selected conversation, including context
   outside the seed interval. If a declared record/message/page limit is
   reached, treat that source as incomplete, do not catalogue it, and do not
   advance its checkpoint.
5. Resolve an existing catalog record through stored conversation and ordered message identities, never filename or title matching. Preserve intentionally folded records.

### 3. Catalog

1. Compare current ordered immutable message identities with stored membership. Do not rewrite an unchanged complete record.
2. Preserve complete available source text verbatim, source metadata, attachment presence/outcomes, atomic facts, and ordered source-coverage decisions.
3. Apply `core/contracts/source-catalog.md`, `core/decision-tables/fact-flags.md`, and `core/operations/attachment-processing.md`. Every substantive source clause must map to a Fact or an explicit no-fact reason.
4. A new or refreshed Fact records its source message and configured local received date. Retain existing Fact IDs; append stable new IDs; never delete or renumber history.
5. For every changed record, replace the mapped raw UTF-8 Markdown file in place or create a genuinely new raw Markdown record. New records use the byte-counted v2 codec: parse each frame by declared UTF-8 byte length, never by headings or delimiters in the body. Before any dependent write, compare each framed message directly with the complete plaintext body returned by the mail adapter for the same immutable message ID, then read the persisted file back completely and compare its exact bytes with the intended Markdown bytes. Missing, reordered, truncated, normalized, substituted, or summarized source text fails the catalog phase. Never use a native Google Doc or compare persisted content only with an agent-authored draft as a substitute for these two independent checks.

### 4. Reconcile

1. Reconcile source-derived canonical tasks from unresolved action Facts while preserving parent-owned fields, provider bindings, completion history, and stable task IDs. Standing rules remain guidelines, never tasks.
2. Reconcile guidelines, rolling updates, and configured durable profiles mechanically from their Fact flags and provenance. Rolling updates use the inclusive configured local-date window, newest day first, and exclude actions and guidelines.
3. Update the source-catalog index only for verified record changes. Maintain one row per logical catalog record, including all intentionally folded source identities.
4. Update only derived files affected by verified canonical changes, except rolling updates, which are regenerated every successful run even when discovery finds nothing new.
5. Retain the small current-run delta for optional audio; never substitute the full rolling display window for that delta.

### 5. Task sync

Execute `task-sync.md` through the explicitly selected private task-provider configuration and installed adapter. Pull one complete current provider snapshot first, use immutable IDs and stored bindings, and compare parent fields/status with the durable prior snapshot without inventing unobserved historical events. Apply the configured completion-comment policy through guarded updates and complete comment reads, read back every canonical/provider write, and advance provider state only after the entire reconciliation verifies.

### 6. Brief and delivery

Execute `brief-rendering.md` from declared derived inputs; do not repeat source
discovery. Delivery configuration and state own recipients, template selection,
duplicate prevention, and send authorization. The ordinary configured variant
remains shared across entrypoints. A requested TEST variant is valid only when
it exactly equals the finite private value configured for that entrypoint;
manual and scheduled acceptance variants are distinct. Before sending, read
the delivery state and verify whether the same private delivery key already has
a recorded, verified Gmail message ID or a matching Sent message. If it does,
suppress the duplicate and report the existing delivery; otherwise send once.
Immediately verify provider acceptance or Sent visibility, then record the
verified message ID and delivery key. An unknown delivery outcome is terminal
for the run and must not be retried blindly.

### 7. Commit and report

1. Advance discovery/provider cursors only after every required canonical write and external effect has verified.
2. Write one concise final run checkpoint containing the bounded window, counts, attachment outcomes, Fact/derived/task changes, provider actions, optional degradation, every verified write, and delivery result.
3. If any required phase fails, preserve the last verified checkpoint, record the blocking phase without overstating progress, and leave later cursors/effects untouched.

An execution limit, environment loss, or handoff is not permission to skip
required work. Persist the next safe unit and recover from durable state in a
new invocation. Local extraction and working files are discardable and cannot
substitute for installed instructions, checkpoint evidence, or provider
readback.

A scheduled invocation must normally return `COMPLETE` after all seven required
phases and their readbacks, or `BLOCKED` after an observed tool, provider,
authorization, or source-integrity failure. A measured conservative budget
boundary may instead return `NEEDS_CONTINUATION` only after a verified durable
checkpoint, before the next minimum unit begins; a fresh attempt resumes from
that predecessor. Without that bounded exception, a scheduled invocation must not return after a successful intermediate phase.
Finishing because the agent has completed a working pass, consumed substantial
effort, or chosen to defer later phases is invalid. After a phase passes,
continue immediately to the next phase unless the measured durable boundary
applies.

The elapsed budget begins before capability and entrypoint admission. Its
conservative projection includes elapsed admission and checkpoint time, an
explicit reserve, and a measured nonnegative estimate for the next complete
phase. A missing estimate is not zero. The check runs only between phases: it
cannot preempt a phase or provider call already in progress, so phase bounds
and reserve must cover that practical limit. `NEEDS_CONTINUATION` is invalid
unless the continuation checkpoint was durably created and returned a concrete
reference. Resumption starts a new attempt after the verified predecessor and
retains the already completed phase history without replaying those phases.

## Cutover rule

Before first production activation, require a no-send/no-provider-write parity packet, a verified backup/rollback packet for the mutable private set, one verified schedule identity, and explicit user authorization. Prefer a paused schedule for the supervised first production execution. If the scheduler makes **Run now** unavailable while paused, enable only the verified production schedule for that one owner-approved supervised invocation, and do not treat the schedule as normally active until all Drive, task-provider, mail-delivery, ledger, and cursor readbacks succeed.
