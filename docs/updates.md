# Updates

## Discovering updates

An agent without GitHub access cannot independently discover a remote release. The required baseline is:

1. The user learns of a release through GitHub notifications or another channel.
2. The user downloads and shares the versioned archive and its separate `SHA256SUMS` asset.
3. The agent verifies the archive checksum, complete internal payload inventory, and captured immutable source identity before comparing `release.yaml` to the private installed instance manifest.
4. The agent previews and, after approval, performs the journaled upgrade operation.

A connected agent may optionally check release metadata, but daily production runs remain independent of that connectivity.

## Upgrade rules

- Never execute a live source branch.
- Reject a draft, mutable, unprotected, partially published, or identity/checksum-inconsistent release.
- Never overwrite the current installed release in place.
- Stage the new version separately.
- Read back staged files; reject undeclared files; validate every inventory checksum and compatibility.
- Select one verified coordination mode for the complete upgrade: `native_conditional`, or the narrower `supervised_operational_single_writer` fallback when the provider exposes no write precondition.
- Journal the source identity, checksums, phases, coordination mode, and version evidence. Version evidence is a provider generation/revision token plus SHA-256, or, in supervised single-writer mode only, exact file ID plus `modified_time` plus complete-byte SHA-256.
- Back up only declared private migration targets. Create each generation-specific backup under the upgrade ID with create-only semantics, record its exact returned ID, and verify its complete readback checksum.
- In native mode, atomically bind the expected provider version to every update. In supervised single-writer mode, verify all mutating schedules are paused, permit one identified actor, explicitly prohibit every concurrent mutator for the bounded window, and compare the exact target's full SHA-256 and `modified_time` immediately before each exact-ID update.
- Keep a conditionally updated journal in native mode. In supervised single-writer mode, use create-only, append-only per-phase checkpoint files linked by exact predecessor ID and checksum.
- Activate only after validation passes.
- Activate last and read back the active control file and installed manifest immediately. Keep the production schedule paused through the supervised first production run.
- Restore only from the journaled backup generation after the same selected-mode guard passes, then verify the pre-migration checksum. If identity, guard, or write outcome is ambiguous, stop for manual recovery.
- Record the result, including a failure or rollback result, in private state.

See `core/operations/system-upgrade.md`.
