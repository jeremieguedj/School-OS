# Changelog

## 0.1.0-alpha.7 — 2026-09-02

- Preserved native conditional upgrade behavior and added a bounded `supervised_operational_single_writer` fallback for storage connectors without atomic write preconditions.
- Required exact-ID targeting, paused schedules, one actor, an explicit no-concurrent-mutators guard, immediate full-content SHA-256 and `modified_time` prechecks, and immediate readback.
- Added create-only generation-specific backups and append-only per-phase journal checkpoints for the fallback, with guarded restore and manual-recovery semantics.
- Declared the attended interactive system-upgrade capability set, including conditional scheduler and restore requirements, and aligned private-migration version evidence with both coordination modes.
- Preserved data schema version 1 and the existing architecture; this is a storage capability and upgrade-contract correction only.

## 0.1.0-alpha.6 — 2026-09-02

- Declared the complete private dependency and operation-specific capability set for production daily runs.
- Added a private scheduled-surface capability-profile contract and executable conformance validation.
- Completed the ChatGPT Work runtime and scheduler adapter contracts, including model/effort, approval, overlap, and readback gates.
- Preserved data schema version 1 and Migration 0001; this release changes control-plane completeness only and does not rewrite private canonical data.

## 0.1.0-alpha.5 — 2026-09-02

- Defined a version-derived source artifact, complete payload checksum inventory, and archive checksum asset.
- Required source identity and immutable-release verification before installation.
- Added fail-closed upgrade journal, backup-generation, checksum, activation, and rollback gates.
- Added continuous integration for the repository validation harness.

## 0.1.0-alpha.4 — release candidate

- Added a fail-closed, singular-record-date fallback for legacy Facts that predate per-Fact local received dates.
- Added a synthetic fixture for the permitted fallback behavior.

## 0.1.0-alpha.3 — release candidate

- Corrected the rolling-provenance migration to use configured group projection rather than comparing raw entity scope with a displayed group.
- Added a synthetic fixture for multi-entity and unscoped updates projected to the shared group.

## 0.1.0-alpha.2 — release candidate

- Corrected the release manifest/schema contract so the packaged manifest is installable and schema-valid.
- Added deterministic migration of legacy rolling updates from source-only provenance to atomic Fact references.
- Added synthetic migration input and expected-output fixtures.
- Required tag, commit, manifest version, and released status agreement during existing-instance migration.

## 0.1.0-alpha.1 — non-installable packaging dry run

- Published tag pointed to a manifest that still declared `0.1.0-dev` and `unreleased`; installers must reject it.

## Unreleased foundation

- Established generic GitHub/Drive separation architecture.
- Added manual-first installation and Drive-hosted runtime model.
- Added provider-neutral source-catalog, task, capability, adapter, and release contracts.
- Added reference templates for Gmail, Todoist, ChatGPT Work, Claude, scheduler, and optional audio integration.
- Added synthetic fixtures and privacy boundaries.
