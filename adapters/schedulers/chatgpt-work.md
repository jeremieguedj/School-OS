# ChatGPT Work scheduler adapter

Status: reference adapter only. It becomes production-capable only when paired
with a current private `observed` scheduled-surface conformance record.

## Invocation contract

- Store one stable private schedule identity.
- Invoke only the stable private Drive bootstrap reference plus the operation name; scheduler text does not own operational behavior.
- Record the configured local timezone and observed daylight-saving behavior.
- Record and verify the selected model and reasoning effort on the task's actual execution conversation.

## Required private conformance

Before activation, observe and record:

- background authorization for every Drive, mail, task, and optional audio capability required by the operation;
- schedule creation/update, inspection, run-now, pause/disable, resume, and readback behavior;
- exact invocation payload and bootstrap accessibility;
- timeout, retry, missed-run, notification, and overlap behavior;
- how a pending approval or authentication failure affects the run; and
- the durable evidence used to prove the schedule is disabled or enabled.

The private record contains account/task IDs and observations. This public adapter contains none.
The checked-in tests are synthetic and cannot substitute for that record.

## Safety and single writer

Only one schedule may target a mutating School-OS operation for an instance. Keep that schedule paused during migration, parity testing, and the supervised first production run. A separately qualified direct manual run is permitted only with the common operation state and either proven runtime serialization or a verified paused schedule plus an attended single-writer guard. It does not use scheduler evidence as a substitute for its own manual profile. A schedule run-now control, when observed, invokes the same installed operation and delivery policy as the regular cadence. If the platform cannot guarantee non-overlap, retain one configured production schedule and require serialization plus delivery-key lookup and Sent-mail verification; a delivery key alone is not an operation lock. Routine daily runs must not invent a separate Drive lease.

The scheduled runtime must not block merely because ChatGPT Work does not expose its invocation provenance to the invoked task; the observed scheduled profile and immutable scheduler prompt are the available admission evidence.

Inspect and read back the schedule after every create, update, pause, resume, or replacement. A duplicate identity, unknown status, stale model/effort, missing connector authorization, or unknown retry/overlap outcome blocks activation.

## Approval behavior

Connected-app actions may pause for user or workspace approval. Treat an approval pause as an incomplete run: preserve checkpoints and do not infer that the action occurred. Resume only from observed provider and private state after approval.
