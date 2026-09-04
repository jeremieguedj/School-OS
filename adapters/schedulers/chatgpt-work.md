# ChatGPT Work scheduler adapter

Status: production-capable reference adapter when paired with a passing private scheduled-surface conformance record.

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

## Safety and single writer

Only one schedule may target a mutating School-OS operation for an instance. Keep that schedule paused during migration, parity testing, and the supervised first production run. A direct interactive mutating run is prohibited. An authenticated owner may request an immediate brief only through the schedule's observed run-now control, which invokes the same stable schedule identity and production prompt as the regular cadence. If the platform cannot guarantee non-overlap, retain one configured production schedule and require delivery-key lookup plus Sent-mail verification to suppress a duplicate send. Routine daily runs must not invent a separate Drive lease.

Inspect and read back the schedule after every create, update, pause, resume, or replacement. A duplicate identity, unknown status, stale model/effort, missing connector authorization, or unknown retry/overlap outcome blocks activation.

## Approval behavior

Connected-app actions may pause for user or workspace approval. Treat an approval pause as an incomplete run: preserve checkpoints and do not infer that the action occurred. Resume only from observed provider and private state after approval.
