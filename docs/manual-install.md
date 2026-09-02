# Manual-first installation

This is the required baseline installation route. It does not assume that the agent can connect to GitHub.

## User supplies the package

1. Download both `school-os-<version>.tar.gz` and `SHA256SUMS` from the same immutable tagged School-OS release.
2. Share both assets with the agent. If retrieval was performed by a different trusted tool, also preserve its evidence that the release was immutable and that the protected tag, commit, and version agreed.
3. If the agent cannot expand archives, extract the release first and place the extracted release folder in the target Google Drive or otherwise make every package file readable to the agent.
4. Tell the agent the target Drive root and that it should run the onboarding operation.

The agent must reject an unpinned branch/archive, a mutable or unprotected release, a missing checksum asset, a mismatched archive checksum, or a package whose complete internal inventory does not verify.

## Agent installation

The agent follows `core/operations/onboarding.md` from the supplied release:

1. Verifies `SHA256SUMS`, safely extracts the archive, and verifies every entry in `RELEASE-INVENTORY.sha256` with no undeclared files.
2. Reads `START-HERE.md` and `release.yaml`, and requires the manifest version/status to match the immutable source identity.
3. Collects selected integration choices.
4. Validates the actual capability profile.
5. Creates the private Drive instance and copies the release into its versioned `system/` area with readback checksum verification.
6. Records the package checksum, inventory checksum, tag, commit, and verification evidence in private state.
7. Creates private configuration and state from templates.
8. Runs a no-send validation.
9. Waits for approval before initial import, external sync, delivery, or scheduling.

## Recurring operation

After successful installation, the scheduler receives only the stable private Drive bootstrap reference and operation name. It runs from the installed Drive release and does not need GitHub access.
