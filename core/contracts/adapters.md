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
- unsupported/lossy fields; and
- test profile(s) it supports.

The selected runtime/provider combination—not a vendor name alone—is the conformance unit.
