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

Every capability below must be recorded as `available` in the capability profile for the exact runtime, provider authorization, and **scheduled execution surface** before production writes are enabled:

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
tasks.list_completed
tasks.read_activity
tasks.read_comments
tasks.create
tasks.update
tasks.move
tasks.complete
tasks.reopen
tasks.write_comment
tasks.verify
```

For a scheduler-issued run, `scheduler.inspect` and `scheduler.verify` are also required. Scheduler creation, cutover, pause, or replacement additionally requires `scheduler.ensure` and `scheduler.disable`. A user-requested immediate run is scheduler-issued only when `manual-daily-run.md` invokes the same verified schedule through its observed run-now control; an ad-hoc interactive execution is not a production sender.

`mail.read_attachment` is conditionally required only when attachment extraction is attempted; otherwise record the explicit unavailable/unsupported outcome defined by `attachment-processing.md`. `audio.generate` and `audio.retrieve` are optional and apply only when audio is enabled. Optional failure must use the documented degradation and must never fabricate content or success.

Interactive evidence does not prove scheduled-surface conformance. If authentication, adapter selection, model/effort, or provider configuration changes, recheck the affected capabilities before the next side effect.

## Ordered phases

### 1. Preflight

1. Read the instance manifest, the private daily-values document, the routine runtime-profile header, and the integration selectors needed for this run. Capture one timestamp in the configured timezone.
2. Verify release version, installed reference, data compatibility, and completed migration state agree. Do not re-audit historical migrations on an unchanged routine release.
3. Validate the approved runtime-profile revision/fingerprint and resolve the selected adapter only when entering its phase. A mismatch requires setup/health validation before side effects.
4. Require an idle operation state. Exactly one verified schedule is the production sender for an instance, and a user-requested run-now invocation must use that same schedule. An idle state is sufficient for a routine run: do not create or wait for a separate Drive lease.
5. Require operation state and private policy to permit the intended reads, writes, provider actions, delivery, and cursor advancement. A cutover must use one supervised first-production run before ordinary recurring delivery is considered verified. When a scheduler exposes its authenticated **Run now** control only while the task is enabled, that single owner-approved supervised invocation may run with the one production schedule enabled; the schedule remains subject to full post-run verification before it is treated as normally active.

### 2. Discover

1. Read the most recent successful mail checkpoint. If none exists, use the configured initial-overlap window. Otherwise search from the earlier of the persisted checkpoint and the configured safety overlap.
2. Build the provider query only from the private source-scope configuration and selected mail adapter. Exclude configured forbidden locations and content classes.
3. Paginate to completion, preserve the provider cursor/page evidence, and deduplicate by immutable source conversation identity.
4. Fetch each candidate conversation completely in source order. If a declared record/message/page limit is reached, treat that source as incomplete, do not catalogue it, and do not advance its checkpoint.
5. Resolve an existing catalog record through stored conversation and ordered message identities, never filename or title matching. Preserve intentionally folded records.

### 3. Catalog

1. Compare current ordered immutable message identities with stored membership. Do not rewrite an unchanged complete record.
2. Preserve complete available source text verbatim, source metadata, attachment presence/outcomes, atomic facts, and ordered source-coverage decisions.
3. Apply `core/contracts/source-catalog.md`, `core/decision-tables/fact-flags.md`, and `core/operations/attachment-processing.md`. Every substantive source clause must map to a Fact or an explicit no-fact reason.
4. A new or refreshed Fact records its source message and configured local received date. Retain existing Fact IDs; append stable new IDs; never delete or renumber history.
5. For every changed record, replace the mapped file in place or create a genuinely new record, then read it back completely and compare it with the intended bytes/content before any dependent write.

### 4. Reconcile

1. Reconcile source-derived canonical tasks from unresolved action Facts while preserving parent-owned fields, provider bindings, completion history, and stable task IDs. Standing rules remain guidelines, never tasks.
2. Reconcile guidelines, rolling updates, and configured durable profiles mechanically from their Fact flags and provenance. Rolling updates use the inclusive configured local-date window, newest day first, and exclude actions and guidelines.
3. Update the source-catalog index only for verified record changes. Maintain one row per logical catalog record, including all intentionally folded source identities.
4. Update only derived files affected by verified canonical changes, except rolling updates, which are regenerated every successful run even when discovery finds nothing new.
5. Retain the small current-run delta for optional audio; never substitute the full rolling display window for that delta.

### 5. Task sync

Execute `task-sync.md` through the explicitly selected private task-provider configuration and installed adapter. Pull provider changes first, use immutable IDs and stored bindings, apply the configured completion-comment policy, read back every canonical/provider write, and advance provider state only after the entire reconciliation verifies.

### 6. Brief and delivery

Execute `brief-rendering.md` from declared derived inputs; do not repeat source discovery. Delivery configuration and state own recipients, template selection, duplicate prevention, and send authorization. Before sending, read the delivery state and verify whether the same private delivery key already has a recorded, verified Gmail message ID or a matching Sent message. If it does, suppress the duplicate and report the existing delivery; otherwise send once. Immediately verify provider acceptance or Sent visibility, then record the verified message ID and delivery key. An unknown delivery outcome is terminal for the run and must not be retried blindly.

### 7. Commit and report

1. Advance discovery/provider cursors only after every required canonical write and external effect has verified.
2. Write one concise final run checkpoint containing the bounded window, counts, attachment outcomes, Fact/derived/task changes, provider actions, optional degradation, every verified write, and delivery result.
3. If any required phase fails, preserve the last verified checkpoint, record the blocking phase without overstating progress, and leave later cursors/effects untouched.

## Cutover rule

Before first production activation, require a no-send/no-provider-write parity packet, a verified backup/rollback packet for the mutable private set, one verified schedule identity, and explicit user authorization. Prefer a paused schedule for the supervised first production execution. If the scheduler makes **Run now** unavailable while paused, enable only the verified production schedule for that one owner-approved supervised invocation, and do not treat the schedule as normally active until all Drive, task-provider, mail-delivery, ledger, and cursor readbacks succeed.
