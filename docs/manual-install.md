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
4. Schema-validates the setup capability profile. Capabilities that setup did
   not actually exercise may truthfully remain `unknown`; setup is not daily-run
   qualification.
5. Creates the private Drive instance and stores the exact release archive and
   `SHA256SUMS` as create-only admitted installation artifacts alongside the
   private payloads. It records their returned IDs and reads both back before
   admitting the content manifest.
6. Records the package checksum, inventory checksum, tag, commit, and verification evidence in private state.
7. Creates private configuration and state from templates.
8. Runs a no-send validation.
9. Waits for approval before initial import, external sync, delivery, or scheduling.

## Capability-profile readmission

After the required capabilities have been observed on an actual execution
surface, use the extracted release's `scripts/readmit_connected_profile.py`
with the admitted instance document, the exact observed profile JSON, its
matching `manual` or `scheduled` entrypoint, the private run directory, and the
host JSONL relay. The command rejects non-observed or nonconformant profiles,
creates an immutable exact-byte profile, updates the existing profile-selection
object by exact ID and current version, and reads both back. Manual and
scheduled observations remain separate; qualify and readmit each one on its
actual surface before using that entrypoint.

An instance installed from commit `127219b81980710a8cf8965fe1d44e91287961e9`
can adopt this correction without another empty-root setup. On its first
readmission, the command recognizes the legacy single-profile form at the
existing `durable_profiles` ID, preserves those bytes as an immutable profile,
and guardedly converts that same object into the two-entrypoint selector. It
does not replace the installation manifest, canonical data, task state,
delivery state, or source state.

## Recurring operation

After successful installation, the scheduler receives only the stable private
Drive bootstrap reference and operation name. A reset host follows the admitted
archive/checksum references, verifies and extracts that pinned package, and runs
without the original local files or GitHub access.
