# Manual daily-brief request

## Goal

Let an authenticated owner ask for “Run the daily brief now” without creating a
second production sender or changing the next scheduled run.

## Invocation

This operation is a dispatcher, not an alternate implementation of
`daily-run.md`. The authenticated owner's request is authorization to create and
deliver that immediate brief. It must invoke the existing verified scheduler's
**run-now** control, so the actual execution uses the same stable schedule identity
and production prompt as a normal cadence-triggered run.

## Preconditions

1. Read the stable private bootstrap, instance manifest, the instance's
   `daily_run_personal_values_reference`, `operation_state`, capability profile,
   delivery state, and this recipe. The logical file map is an onboarding,
   upgrade, recovery, and maintenance artifact; the dispatcher does not sweep it.
2. Resolve exactly one active production schedule for the instance. Confirm its
   identity, production prompt, model/effort, timezone, and enabled state by
   readback.
3. Confirm the exact scheduled-surface capability profile records a successful
   run-now observation and its overlap behavior. Interactive capability evidence
   alone is insufficient.
4. Require the operation state to be idle. If a run is active, queued, stale, or
   ambiguous, do not dispatch another run.
5. Verify that the scheduler's run-now control targets the same stable schedule;
   never recreate, clone, or substitute a schedule to satisfy a manual request.

If the scheduler exposes **Run now** only while its task is enabled, an
owner-approved manual request may use that enabled task for the single
supervised first-production invocation. Normal recurring activation is not
considered verified until the resulting run has fully read back its writes and
delivery.

The selected scheduler must declare `scheduler.inspect`, `scheduler.verify`, and
`scheduler.run_now` as available for the exact observed run-now control.

## Dispatch

1. Invoke run-now once through the scheduler's authenticated control surface.
2. Read back the scheduler's accepted invocation or resulting run identity.
   Unknown dispatch outcome is terminal: do not press run-now again.
3. Do not read source mail, update Drive, synchronize tasks, reserve delivery,
   generate audio, or send mail in this dispatcher. Those effects belong only to
   the scheduled runtime executing `daily-run.md`.
4. Report the scheduler identity, invocation/run identity when observable, and
   whether the dispatch was accepted, blocked, or ambiguous.

## Resulting production run

The scheduler-issued run uses the normal preceding-window rule and the standard
daily-run and brief-rendering recipes. It creates its own durable run checkpoint
and delivery reservation. A successful immediate run does not modify the next
cadenced invocation. If the same local date already has a verified delivery, the
private delivery policy—not the dispatcher—decides whether the requested run is
suppressed or sent as an explicitly distinguished correction.

## Failure behavior

Fail before dispatch when the schedule is paused, ambiguous, not the configured
identity, lacks observed run-now behavior, has unknown overlap behavior, or the
operation is not idle. Never bypass these controls with a direct interactive
daily run.
