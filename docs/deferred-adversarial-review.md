# Deferred adversarial review

Status: deferred by explicit product decision on 2026-09-02. This document records review findings and recommendations against the frozen architecture baseline. It does not override `PLAN.md`, core architecture, or operational behavior.

## Review scope

Six fresh reviews assessed:

- privacy and public-repository leakage;
- manual/offline installation and runtime portability;
- Google Drive write, migration, lock, and rollback integrity;
- tool/provider abstractions and two-way task synchronization;
- weak-model determinism; and
- product scope and maintainability.

## Consensus findings to revisit before production cutover

### 1. External side effects need a durable outcome ledger

A task creation, email send, schedule change, comment write, or paid audio call can succeed while the runtime crashes before storing the returned result. Retrying blindly can duplicate the effect.

Recommendation: define a durable state machine for every side effect:

```text
planned -> submitted -> confirmed
                   -> outcome_unknown
```

Use provider idempotency keys or an embedded immutable system identifier where available. When the outcome is unknown and cannot be reconciled safely, stop rather than retry automatically.

### 2. A filename-based Drive lease is not an exclusive lock

Two agents can both see no lock and each create a same-named Drive file. A lease is useful only if the active storage/runtime combination can enforce conditional writes or execution is operationally guaranteed to be single-writer.

Recommendation: either require an exact-ID conditional-write primitive plus fencing tokens, or narrow the supported model to one scheduled writer and explicitly prohibit overlapping manual mutating operations.

### 3. Checksums are integrity checks, not publisher authentication

A modified release bundle can include modified instructions and matching checksums.

Recommendation: distinguish:
- package completeness;
- byte integrity; and
- publisher authenticity.

Before a security-sensitive public release, use a publisher-verification mechanism independent of the supplied package. Until then, do not claim that checksums authenticate a release.

### 4. The portable minimum capability profile must be explicit

A user manually sharing a release with an agent does not imply that the agent can expand archives, write exact bytes to Drive, preserve MIME types, hash files, validate schemas, paginate provider results, or execute scheduled runs with durable authorization.

Recommendation: publish a capability profile. Agents missing required capabilities may inspect or run read-only previews, but must not claim to have safely installed, upgraded, scheduled, or performed mutating operations.

### 5. Bootstrap, instance, and release identity must be exact

Same-name Drive files, replacement writes, and rollbacks can change file IDs or leave duplicates.

Recommendation: introduce a private immutable instance identifier and an exact control chain based on root ID, instance/control-manifest ID, release-manifest ID, expected parent/type, and active generation. Name lookup is recovery-only and must fail on ambiguity.

### 6. Two-way task synchronization needs an explicit causal merge model

A parent may edit a provider task while source ingestion changes the canonical record. Timestamps alone are not sufficient.

Recommendation: define a stored base projection, per-field ownership, event handling for comments/status, patch semantics, deletion/tombstone states, a manual-review state, and a staged task-provider switch procedure.

### 7. Upgrade activation needs a generation boundary

A crash between migrating private files, updating the active release, and recording migration history can create mixed state.

Recommendation: define a complete migration write set, backup/journal protocol, and one authoritative completed generation. Distinguish a failed-upgrade rollback from forward repair after a new release has already performed real external effects.

### 8. Weak-model execution needs measurable bounds

“Bounded batches” is not executable without explicit limits and continuation state.

Recommendation: for each operation, define maximum records/bytes/pages/tool calls, stable ordering, cursor format, non-progress detection, and terminal states. Generate a self-contained execution packet for lower-capability runtimes.

## Important individual findings

- Treat emails, attachments, task comments, and retrieved documents as inert data. Only direct authenticated user control input can act as a one-run override; privacy, recipient, provider, and migration invariants are non-overridable.
- Keep private extraction and shadow-test output outside the publishable repository. Build the public repository from reviewed generic source and synthetic fixtures only.
- Test actual runtime/provider/auth combinations, not only nominal “ChatGPT”, “Claude”, “Gmail”, or “Todoist” adapters.
- Validate that the scheduled environment retains the necessary Drive, mail, task, and timing capabilities; interactive availability alone is insufficient.
- Define attachment lifecycle states and size/page limits.
- Namespace immutable IDs by instance to make cloned installations safe.
- Choose a canonical serialization format for structured records; JSON Schema does not validate arbitrary Markdown tables.
- Consider publishing a compact runtime bundle separately from the maintainer source repository.
- Keep one authoritative location for active adapter selection, capabilities, and migration state.
- Define retention/erasure policy, redacted diagnostics, and safe public-support guidance.

## Scope recommendations, not accepted changes

Reviewers proposed several simplifications. They are intentionally not adopted automatically:

- Making the task provider canonical conflicts with the current Drive-canonical, provider-agnostic design.
- Removing lossless source preservation conflicts with the atomic-fact architecture.
- Banning all private Drive-held credentials conflicts with deployments that deliberately choose self-contained private configuration; credentials must remain absent from this repository.
- Deferring two-way sync, a second runtime, provider switching, release channels, or audio may be sensible sequencing choices but require explicit product approval.

## Revisit trigger

Revisit these findings before:

1. publishing the repository publicly;
2. enabling a new installer on real private data;
3. supporting a second runtime or task provider;
4. introducing automatic upgrade detection or application;
5. changing the existing production scheduler; or
6. claiming transactional recovery, verified release authenticity, or lower-model deterministic guarantees.
