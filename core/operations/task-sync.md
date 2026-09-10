# Task-sync operation

## Purpose

Synchronize the canonical private task register with exactly one explicitly selected task provider.

## Procedure

1. Resolve the active task-provider selector from private integration
   configuration. Ask the user's instance agent to execute the selected adapter
   procedure and return one complete normalized snapshot under
   `task-adapter.md`. School-OS does not interpret the provider's layout or call
   native task-tool operations.
2. Validate the required task table/schema, provider binding, group mapping, workflow mapping, and binding uniqueness.
3. Pull the complete normalized provider snapshot before planning canonical
   projection changes. The executable reconciliation resolves only immutable
   canonical IDs and first commits imported parent changes plus the exact next
   provider-neutral action. Only then may the user agent translate that action
   into native operations. It returns exact normalized readback before core
   advances a binding or cursor.
   The snapshot includes current completion/status and every mapped parent field
   in scope. Comparison with the durable prior snapshot establishes the observed
   current transition only; do not invent or claim intermediate activity that
   the provider did not expose.
4. Resolve managed tasks through immutable system IDs and stored bindings, never title matching.
5. Compare each parent-editable field against the last common snapshot. A
   local-only change projects, a parent-only change is admitted, equal changes
   are adopted, and divergent changes become explicit review cases without an
   overwrite. Workflow and every other system-managed field are excluded from
   parent pull and must pass the full prior-projection drift check.
   Apply the same three-way rule to a new source Action/Group value using the
   task's prior `source_projection` as common base. A divergent accepted-parent
   and new-source value blocks here, before provider projection.
6. Enforce the configured completion-comment policy. Before a missing-comment
   reminder or reopen, persist its exact occurrence-stable effect ID, canonical
   and provider object IDs, and reminder text. Immediately before reminder
   dispatch, checkpoint and exactly read back that intent as `unknown` with an
   incremented dispatch attempt. Recovery adopts one exact comment; a zero-match
   unknown lookup blocks unless the adapter proves `definitely_not_applied`.
   It then reopens and performs exact readback even when the provider is already
   open. A later completion after a verified reopen is a new occurrence.
7. For each missing unresolved task, first return and persist its `task_create`
   intent without invoking the provider. On continuation, first use the bounded
   effect-checkpoint callback to persist and exactly read back that intent as
   `unknown` with an incremented dispatch attempt, then create from it. Reconcile
   an interrupted dispatch by
   complete canonical-ID lookup, adopting one exact match and blocking zero,
   multiple, or conflicting matches. Retry a zero-match intent only after the
   adapter supplies explicit `definitely_not_applied` evidence. Preserve
   unrelated provider-owned fields for changed tasks.
8. Persist and verify both the returned canonical task register and provider
   state. For parent admission, persist the issued canonical task and complete
   candidate evidence before the claim intent; either half can reconstruct the
   other before any row create/claim. Read back every provider and private write.
9. Advance provider cursors and bindings only after reconciliation succeeds.

## Grouping

The generic system owns the ordered configured-entity groups plus the shared/household group. The adapter maps that logical grouping and workflow state to the provider's available constructs without redefining the grouping policy.

## Failure behavior

If identity, field mapping, provider access, or a conflict is ambiguous, preserve canonical state, mark the task for review according to private policy, and do not guess. Unknown managed canonical IDs and inconsistent canonical/provider binding state block. A single empty provider snapshot is not proof that an unknown create was not applied.
