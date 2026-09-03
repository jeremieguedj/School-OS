# Migration of an existing private deployment

This document prepares, but does not itself authorize, migration of a live School-OS-style private Drive system.

## Required sequence

1. Create a private inventory of current files, parent folders, roles, references, and schedules.
2. Classify each private file as reusable system logic, configuration, canonical data, derived data, state, or duplicate/historical material.
3. Extract only reviewed generic rules into this repository.
4. Build synthetic fixtures independently of live private content.
5. Verify that the supplied tag resolves to the package commit and that `release.yaml` declares the same installable version with `status: released`.
6. Install the first release alongside the existing system without moving live canonical data.
7. Map existing private files through private state.
8. Run every manifest-declared migration in shadow mode first. Unresolved deterministic-mapping exceptions block activation.
   If private state records that a migration already completed, validate the current target and migration idempotence; do not apply it a second time merely because a newer release still declares it.
9. Run old and new operations in no-send/no-provider-write shadow mode against the same bounded input window.
10. Compare catalog, source coverage, derived results, task decisions, and brief output.
11. Obtain explicit approval before changing any live scheduled operation.
12. Disable the old scheduler before enabling a new bootstrap-based scheduler, and verify the supervised first production run.

Before steps 6–8, verify the supplied release's immutable source identity, archive checksum, and complete payload inventory. Private upgrade state must retain the exact release identity, backup references, and recovery verification evidence. In `native_conditional` mode, target version evidence is the provider generation/revision token plus the complete-byte SHA-256 before and after each write. In the bounded `supervised_operational_single_writer` mode, target version evidence is the exact file ID, observed `modified_time`, and complete-byte SHA-256 before and after each write. The latter is valid only while the attended no-concurrent-mutators guard remains verified.

The repository must not receive the private inventory, mapping, exception records, or shadow outputs.
