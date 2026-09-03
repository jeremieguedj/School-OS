# System-upgrade operation

## Purpose

Install a user-supplied newer release into a private Drive instance without relying on live GitHub access.

## Required capabilities and execution surface

Run this operation only from an attended `interactive` execution surface. The private capability profile must identify the exact runtime, provider authorization, and selected adapters used for the upgrade; record `system-upgrade` as a conformant operation; and record every capability below as `available` with an actual interactive-surface probe, relevant limits, and fail-closed degradation:

```text
storage.scoped_list
storage.read_complete
storage.create_file
storage.replace_verified
storage.get_metadata
storage.copy_verified
release.read_package
release.verify_sha256
release.verify_inventory
release.verify_source_identity
coordination.ensure_idle
```

When the instance has, or may have, a schedule capable of mutating it, `scheduler.inspect` and `scheduler.verify` are also required. `scheduler.disable` is required when the operation must pause or disable such a schedule rather than merely verify it is already paused. The inspected schedule identity and paused/disabled readback belong in the attended upgrade evidence.

`storage.restore_verified` is required only when the operation promises automatic rollback. Without it, backups and recovery evidence remain mandatory, but any required restore is manual recovery and the operation must not claim automatic rollback.

Missing, unavailable, stale, scheduled-only, or ambiguous required capability evidence stops before the first write. A scheduled `run-now` observation may support scheduler conformance, but it does not replace the attended interactive profile required to perform an upgrade.

## Procedure

1. Read the supplied release manifest, archive `SHA256SUMS`, internal `RELEASE-INVENTORY.sha256`, verified source identity, current private instance manifest, active release, schema version, capability profile, migration log, and upgrade journal.
2. Require the release-integrity capabilities. Verify the immutable release record and tag/commit identity when connected; otherwise require previously captured verification evidence transported with the package. Verify the archive before extraction, reject unsafe entries, then verify the complete extracted inventory. Any mismatch is blocking.
3. Compare versions and compatibility. Present the proposed system files, migrations, behavioral changes, required capabilities, and exact rollback set.
4. Require explicit user approval and select exactly one verified coordination mode from the `coordination.ensure_idle` capability evidence: `native_conditional` or `supervised_operational_single_writer`. Record the mode in the upgrade journal; the existing capability entry's verification and limits fields carry this observation, so no new private-state schema field is implied.
5. Use `coordination.ensure_idle` to ensure no mutating operation is active. In `supervised_operational_single_writer` mode, additionally verify every schedule capable of mutating this exact instance is paused or disabled and read back that state; identify one upgrade actor; prohibit all other manual mutating runs; and obtain an explicit no-concurrent-mutators guard covering direct Drive edits, agents, automations, and provider operations for the bounded upgrade window. Any unknown actor, schedule, or status blocks the first write.
6. Create the first unique journal checkpoint with create-only semantics. It contains the old and proposed versions, source identity, package checksum, inventory checksum, planned migrations, affected private files, coordination mode, actor, guard evidence, and initial phase. Read it back before proceeding. In `native_conditional` mode, later journal appends use conditional writes and verified readback. In `supervised_operational_single_writer` mode, never replace a shared journal file: create one uniquely identified, append-only checkpoint per phase, referencing the exact predecessor checkpoint ID and SHA-256, then read it back completely and verify its checksum.
7. Stage the new release in a new versioned Drive location with create-only semantics. Read it back, reject additional files, verify every payload checksum, and record the exact created file IDs plus provider version tokens when available. When a provider exposes no usable generation/revision token, the authoritative staged-file evidence is the exact file ID, observed `modified_time`, and SHA-256 of the complete bytes.
8. For every private file declared by a migration, record its pre-migration version evidence and create a generation-specific backup with create-only semantics. Version evidence is either a provider generation/revision token and SHA-256, or, only in `supervised_operational_single_writer` mode, the exact target file ID, observed `modified_time`, and SHA-256 of the complete bytes. Key the backup to that evidence and the upgrade ID, record the exact created backup ID, read the backup back completely, and verify its SHA-256. Do not start any migration until the entire rollback set passes this gate.
9. Execute migrations in order. When private state already records a migration complete, validate its current target and idempotence, record the verified skip, and do not back up or rewrite that target merely because the newer release still declares the migration. For a migration that must run, `native_conditional` mode preserves the existing rule: before each write, require the target generation/revision and checksum still match the journal and bind that version precondition to the write. In `supervised_operational_single_writer` mode, immediately before every update, fetch the exact target ID's metadata and complete bytes and require both `modified_time` and SHA-256 to match the journaled pre-write evidence; then replace only that exact ID. After every write in either mode, immediately read back the exact target completely, compute its SHA-256, capture the new version evidence, and write the next verified journal checkpoint. Any drift, ambiguous identity, unknown outcome, or unverifiable readback stops activation.
10. Run migration idempotence checks and no-external-write validation for the staged release. Record each check and its evidence in the journal.
11. Activate last, only after every prior gate passes. In `native_conditional` mode, bind the journaled active-release generation/revision to the activation write. In `supervised_operational_single_writer` mode, immediately before activation re-fetch the exact active-control file ID, `modified_time`, and complete bytes; require both timestamp and SHA-256 to match the journal; then replace only that exact ID under the still-active no-concurrent-mutators guard. Immediately read back the active control file and installed manifest completely, reverify their identity and SHA-256 values, and create/read back the completed journal checkpoint. Keep all schedules paused until a separate supervised production run passes its own cutover gate.

On failure before an activation attempt, leave the old release active and write the failure phase and evidence to the journal using the selected mode. If migration writes occurred, restore only the journaled generation-specific backups. In `native_conditional` mode, require the current target generation/revision and checksum to equal the failed migration's recorded post-write value and bind that version to the restore. In `supervised_operational_single_writer` mode, keep the exclusive guard active, immediately re-fetch the exact target ID and require its current `modified_time` and complete-byte SHA-256 to equal the recorded post-write evidence before restoring that exact ID. Immediately read back the restore and require its SHA-256 to equal the pre-migration checksum. If the guard lapses, any identity or evidence is ambiguous, the connector cannot restore and verify the exact target, or an activation write cannot be read back, stop for manual recovery and treat active state as unknown when applicable. Never claim automatic rollback without `storage.restore_verified`, and never claim rollback succeeded without exact-ID, checksum, and readback evidence.

## Coordination-mode boundary

`supervised_operational_single_writer` is not a simulated conditional write. It is a narrower deployment mode whose safety depends on verified operational exclusivity for the entire upgrade, exact-ID targeting, immediate pre-write content/metadata comparison, create-only evidence, and immediate readback. It is unavailable for unattended upgrades or when another mutator cannot be ruled out. Native conditional writes remain preferred whenever the storage adapter exposes a precondition that is atomically bound to the mutation.
