# Adapter contract

Adapters map generic contracts to a specific runtime/provider/auth combination.

## Boundaries

Core operations own:

- data meaning;
- source and task policy;
- classification rules;
- rendering/grouping requirements;
- validation and stop conditions.

Adapters own only:

- capability discovery;
- provider object discovery;
- operation invocation;
- field mapping;
- normalization and known limitations;
- provider-specific verification; and
- conservative failure behavior.

Adapters must not embed household values, canonical facts, task history, recipient addresses, private IDs, or secrets.

## Required adapter metadata

Every adapter declares:

- adapter ID and version;
- contract versions implemented;
- required authorization/scopes;
- supported capabilities and limits;
- normalized identity model;
- pagination and completeness behavior;
- mutation/readback behavior;
- idempotency or recovery behavior;
- supported upgrade coordination mode and version evidence (provider generation/revision token, or exact ID plus `modified_time` plus complete-byte SHA-256 under supervised operational single-writer rules);
- unsupported/lossy fields; and
- test profile(s) it supports.

The selected runtime/provider combination—not a vendor name alone—is the conformance unit.

## Phase resolution

A generic operation must not embed a household's adapter choice or provider
binding. At the start of a phase, it resolves the phase's private selector from
the integration configuration, reads the selected generic adapter, and then
reads only the private configuration/state declared by that adapter. For
example, task reconciliation resolves the active task-provider selector before
loading a task adapter; delivery resolves the selected mail adapter before
reading delivery state. The private daily-values document may point to daily
canonical records but never replaces this resolution chain.
