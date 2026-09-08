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

## Executable core boundary

`school_os.adapters` defines the narrow Python structural protocols used by
the synthetic connected path: storage reads/listing/create/replace; complete
mail discovery, reads, send, and delivery lookup; task snapshot/read/write
calls; and optional scheduler inspection/triggering. Its `ReadResult`, `Page`,
and `EffectResult` records normalize only identity, pagination, bytes, version,
and outcome evidence. `EffectResult.outcome` is exactly `confirmed`,
`definitely_not_applied`, or `unknown`; accepted requests alone are never
confirmation. A caller retries only the definitely-not-applied case and routes
unknown effects through reconciliation.

These protocols make no Markdown provider mapping executable and do not select
a provider. A concrete adapter still supplies the documented readback that
establishes a confirmed effect. The checked-in fakes are synthetic behavioral
evidence only, never production conformance.

## Adapter origin and extensibility

An adapter may ship in an official release or be created by a user and their agent for one private instance. Both are first-class School-OS adapters when they implement the applicable contract, declare the required metadata, pass capability validation, and preserve core invariants. Conformance depends on behavior and evidence, not on who created the adapter or whether its provider is already known upstream.

Adding a conformant adapter for a different runtime, storage service, mail provider, task manager, scheduler, audio service, or future integration is compatible system expansion; it does not by itself change the core architecture or make the instance a fork. The instance must record and select the adapter through its normal configuration and file mapping so another agent and a later upgrade can identify it.

If an integration cannot be implemented without changing a core invariant or breaking an existing generic contract, treat that proposal as a core architectural change rather than labeling it an adapter. Explain the update-compatibility consequence and obtain explicit user approval before proceeding.

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
