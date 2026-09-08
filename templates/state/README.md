# Private runtime state

Runtime state stores private file references, source cursors, task-provider bindings, delivery history, operation checkpoints, and migration history.

For new installs, `operation-state.json` is the guarded admission pointer. It
contains either no operation (`idle`), one active operation with serialization
and checkpoint evidence, or a terminal summary. Each checkpoint is an
immutable create-only JSON object in `operation-checkpoints/`; its predecessor
pointer and SHA-256 must match the exact canonical bytes of the preceding
checkpoint. `operation-checkpoint.json` is a structural template for the first
admission checkpoint; the runner replaces its generic values and never mutates
an accepted checkpoint. The legacy `operation-state.yaml` remains a migration
input only until M4 verifies Migration 0002.

State is not reusable source code and must never be copied into the GitHub repository.
