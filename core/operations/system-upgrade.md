# System-upgrade operation

## Purpose

Install a user-supplied newer release into a private Drive instance without relying on live GitHub access.

## Procedure

1. Read the supplied release manifest, archive `SHA256SUMS`, internal `RELEASE-INVENTORY.sha256`, verified source identity, current private instance manifest, active release, schema version, capability profile, migration log, and upgrade journal.
2. Require the release-integrity capabilities. Verify the immutable release record and tag/commit identity when connected; otherwise require previously captured verification evidence transported with the package. Verify the archive before extraction, reject unsafe entries, then verify the complete extracted inventory. Any mismatch is blocking.
3. Compare versions and compatibility. Present the proposed system files, migrations, behavioral changes, required capabilities, and exact rollback set.
4. Require explicit user approval and create a unique upgrade journal entry containing the old and proposed versions, source identity, package checksum, inventory checksum, planned migrations, affected private files, and initial phase. Read it back before proceeding. Every later journal append must itself use a conditional write and verified readback.
5. Use `coordination.ensure_idle` to ensure no mutating operation is active according to the instance's supported coordination method.
6. Stage the new release in a new versioned Drive location with create-only semantics. Read it back, reject additional files, verify every payload checksum, and record the staged generation/revision identifiers.
7. For every private file declared by a migration, record its pre-migration generation/revision and SHA-256, create a generation-specific backup with create-only semantics, then read it back and verify its checksum. Do not start any migration until the entire rollback set passes this gate.
8. Execute migrations in order. Before each write, require the target generation/revision and checksum still match the journal; after each write, read back the new generation/revision and checksum and append the result to the journal. A conflict or unverifiable write stops activation.
9. Run migration idempotence checks and no-external-write validation for the staged release. Record each check and its evidence in the journal.
10. Activate only by a conditional write against the previously journaled active-release generation/revision. Read back the active pointer and installed manifest, reverify their checksums, and mark the journal complete.

On failure before an activation attempt, leave the old release active and append the failure phase and evidence to the journal. If migration writes occurred, restore only the journaled generation-specific backups: require the current target generation/revision and checksum to equal the failed migration's recorded post-write value, restore conditionally, read back, and require the restored checksum to equal the pre-migration checksum. If an activation write was attempted but its result cannot be read back, treat active state as unknown and stop for manual recovery. If any precondition or verification fails, stop for manual recovery. Never claim rollback succeeded without checksum and readback evidence.
