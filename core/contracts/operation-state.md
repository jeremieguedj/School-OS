# Operation state and checkpoints

`state/operation-state.json` is the private admission pointer for one active
mutating operation. It is never proof of serialization by itself: an active
pointer records verified `native_conditional`, `runtime_serialized`, or
`attended_single_writer` evidence.

Every durable checkpoint is create-only. Its canonical UTF-8 JSON bytes end in
one newline; a successor records the predecessor checkpoint ID and SHA-256 of
those exact bytes. A pointer update is permitted only after the new checkpoint
has been read back and its chain has validated.

The legal transitions are enforced by `school_os.operations`:

- no active operation, `complete`, or `cancelled` to `running` after admission;
- `running` to a verified bounded checkpoint, `needs_continuation`, `blocked`,
  `complete`, or `cancelled`;
- `needs_continuation` or `blocked` to `running` only under a new attempt with
  recovery and serialization evidence; and
- terminal states only after pending or unknown effects are resolved.

Completion additionally requires every recipe-declared phase, no remaining
work, no blocker, and no pending/unknown effect. A cancelled operation keeps a
durable terminal checkpoint and never implies rollback. The legacy YAML state
file is an alpha.12 migration input, not active new-install state.
