# Task-sync operation

## Purpose

Synchronize the canonical private task register with exactly one explicitly selected task provider.

## Procedure

1. Read the canonical task register, group configuration, selected provider configuration, sync state, and adapter.
2. Validate the required task table/schema, provider binding, group mapping, workflow mapping, and binding uniqueness.
3. Pull provider changes before pushing canonical changes.
4. Resolve managed tasks through immutable system IDs and stored bindings, never title matching.
5. Apply only fields declared provider-editable by the selected policy and adapter. Preserve source facts, source links, canonical IDs, and task history.
6. Enforce the configured completion-comment policy. Completion evidence/history is written to the canonical record.
7. Project missing or changed canonical tasks to the provider, preserving unrelated provider-owned fields.
8. Read back every provider and private write.
9. Advance provider cursors and bindings only after reconciliation succeeds.

## Grouping

The generic system owns the ordered configured-entity groups plus the shared/household group. The adapter maps that logical grouping and workflow state to the provider's available constructs without redefining the grouping policy.

## Failure behavior

If identity, field mapping, provider access, or a conflict is ambiguous, preserve canonical state, mark the task for review according to private policy, and do not guess.
