# Operation state and checkpoints

`state/operation-state.json` is the private admission pointer for one active
mutating operation. It is never proof of serialization by itself: an active
pointer records verified `native_conditional`, `runtime_serialized`, or
`attended_single_writer` evidence.

Every durable checkpoint is create-only. Its canonical UTF-8 JSON bytes end in
one newline; a successor records the predecessor checkpoint ID and SHA-256 of
those exact bytes. A pointer update is permitted only after the new checkpoint
has been read back and its chain has validated.

After a reset or uncertain pointer update, recovery searches the scoped durable
checkpoints for the active operation and accepts only one valid longest
predecessor chain. Equal longest chains, duplicate immutable pointers, a missing
predecessor, or a hash mismatch are `BLOCKED`; it never chooses a branch by
recency or filename. A planned stop is `needs_continuation`, not completion.
Its next invocation keeps the operation ID, uses a new attempt ID, points to the
exact recovered tip, and requires matching pinned-release and configuration
fingerprint evidence (or explicit reconciliation before progress resumes).

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

Checkpoint before and after every consequential provider effect, after every
verified bounded unit, and before a known limit, handoff, or planned pause.
Unknown effects must be reconciled from durable intent plus complete provider
readback; they prevent completion and cancellation and are never blindly
retried. The durable checkpoint stores compact identity, hash, outcome, and
reference evidence rather than source or rendered-content bytes.

Legacy individually stored artifacts retain their compact string reference.
Under the admitted hybrid layout, a source or output bundle artifact instead
records its bundle kind, stable bundle identity, exact physical Drive object
reference, and whole-bundle SHA-256. The physical reference must include the
file ID, sole permitted instance-root ancestor, MIME type, and provider version;
omitting any of that evidence blocks the checkpoint before state publication.
