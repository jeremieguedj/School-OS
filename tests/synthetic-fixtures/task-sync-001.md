# Synthetic task-sync fixture 001

## Canonical task

| ID | Action | Task context | Entity scope | Workflow state | Source due | Parent planned due |
|---|---|---|---|---|---|---|
| T-001 | Return the signed activity form. | The form is required for the upcoming activity. | child_1 | needs_action | 2026-01-09 | — |

## Provider events

1. Parent moves the task to the household group.
2. Parent adds the comment: `Form returned at drop-off.`
3. Parent completes the task.

## Expected reconciliation

- Keep canonical ID `T-001`.
- Update entity scope only if the configured group-move policy permits the explicit parent move.
- Record the freeform comment verbatim as progress/completion evidence.
- Accept completion because a non-system non-empty parent comment exists.
- Preserve the immutable source deadline.
- Preserve source provenance and completion history.
