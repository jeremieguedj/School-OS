# Historical import operation

## Purpose

Optionally backfill a private source catalog without changing the meaning of the daily-run operation.

## Procedure

1. Read import scope, source inclusion policy, catalog state, and selected mail adapter.
2. Capture a fixed date window and deterministic source ordering.
3. Process in bounded batches with durable private checkpoints.
4. Create/refresh source records through the source-catalog contract.
5. Reconcile derived private data only after verified source batches.
6. Do not send a daily brief or mutate the task provider unless the user explicitly authorizes those separate operations.
7. Record completed and blocked source identities in private import state.

Import is resumable and idempotent by source identity.
