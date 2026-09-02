# System-upgrade operation

## Purpose

Install a user-supplied newer release into a private Drive instance without relying on live GitHub access.

## Procedure

1. Read the supplied release manifest, current private instance manifest, active release, schema version, capability profile, and migration log.
2. Compare versions and compatibility. Present the proposed system files, migrations, behavioral changes, and rollback material.
3. Require explicit user approval.
4. Ensure no mutating operation is active according to the instance's supported coordination method.
5. Stage the new release in a separate versioned Drive location. Read it back and verify the installation.
6. Back up exactly the private files declared by migrations.
7. Execute migrations in order, reading and verifying every private write.
8. Run no-external-write validation for the new release.
9. Activate the new release only after required validation passes.
10. Record the installed version, migration result, and verification outcome in private state.

On failure, leave the old release active. Restore only through the instance's declared recovery procedure; never claim rollback succeeded without verification.
