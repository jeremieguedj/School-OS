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
- Journal the source identity, checksums, generations/revisions, phases, and evidence.
- Back up only declared private migration targets, using generation-specific names and verified checksums.
- Use conditional writes so a source changed after backup cannot be silently overwritten.
- Activate only after validation passes.
- Restore only from the journaled backup generation and verify the pre-migration checksum.
- Record the result, including a failure or rollback result, in private state.

See `core/operations/system-upgrade.md`.
