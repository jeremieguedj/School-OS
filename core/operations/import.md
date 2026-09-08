# Historical import operation

## Purpose

Optionally backfill a private source catalog without changing the meaning of the daily-run operation.

## Procedure

1. Read import scope, source inclusion policy, catalog state, and selected mail adapter.
2. Capture a fixed date window. Enumerate every scoped provider page to its
   terminal token, recording each requested page token and every immutable
   conversation identity. Retain a visible `included` or `duplicate`
   disposition for each observed item; a repeated page token, missing identity,
   or incomplete page evidence blocks rather than sampling the scope.
3. Sort unique immutable conversation IDs deterministically. Select a batch
   only from exact whole-record byte evidence and configured record/byte limits.
   Never split or truncate a single conversation; an oversized single record is
   blocked with its identity. Checkpoint the completed IDs and exact remaining
   IDs after verified writes, so a resumed batch selects the same next records.
4. Create/refresh source records through the source-catalog contract. Process
   declared attachments through `attachment-processing.md` and persist their
   explicit outcome with the source record.
5. Reconcile derived private data only after verified source batches.
6. Do not send a daily brief or mutate the task provider unless the user explicitly authorizes those separate operations.
7. Record completed and blocked source identities, enumeration evidence, and
   the next remaining identity in private import state.

Import is resumable and idempotent by source identity.

No-new-message daily discovery is different from an empty import scope: the
daily operation still regenerates required rolling and brief outputs from its
declared durable inputs, then verifies those outputs before commit.
