# Release contract

## Source release

A source release is a tagged, immutable version of the reusable repository. A production instance must never execute an unpinned source branch.

An installable source release has all of the following, derived from `system_version`:

- an annotated tag named `v<system_version>` that resolves to the source commit used for the build and is signed or protected against mutation by the release host;
- a release asset named `school-os-<system_version>.tar.gz` whose single root directory is `School-OS-<system_version>/`;
- a `RELEASE-INVENTORY.sha256` file inside that root, containing the SHA-256 and relative POSIX path of every other regular payload file, sorted bytewise by path; and
- a separate `SHA256SUMS` release asset containing exactly the archive asset's SHA-256 and filename.

The inventory excludes itself and must not contain absolute paths, parent traversal, duplicate paths, links, devices, or files outside the package root. Packaging metadata such as timestamps, ownership, permissions, and file order must be normalized so the asset can be rebuilt reproducibly from the tagged commit.

The tag, release record, and assets are created as one publication unit and then made immutable using the hosting provider's release immutability control. A release that is draft, mutable, missing either asset, or whose tag, commit, manifest version, manifest status, archive checksum, or payload inventory disagrees is not installable. Moving a published tag or replacing an asset is forbidden; corrections require a new version.

## Installed release

An installed release is a managed copy under the private Drive instance's `system/releases/<version>/` area. It is the runtime authority for that instance.

Installation preserves the supplied archive checksum, payload inventory, verified tag/commit identity, and retrieval time in private instance state. The staged copy is valid only when every regular file matches the inventory and no undeclared file is present.

## Version fields

- `system_version`: reusable package version.
- `data_schema_version`: private data structure version.
- `adapter_contract_version`: version of a declared abstract adapter contract.

## Transport modes

1. Manual package: user downloads a tagged release asset and shares it with an agent.
2. Connected retrieval: an authorized agent retrieves that same pinned release.

GitHub connectivity is optional transport only. Production runs read the installed release from Drive.

## Update behavior

An upgrade stages a new installed release, validates compatibility and integrity, executes only declared migrations, verifies results, and activates the new release only after success. The installed instance records its current active version, exact source identity, package and inventory checksums, backup generations, migration history, coordination mode, and verification evidence privately.

For a provider with native conditional writes, version evidence is its generation/revision token plus the complete-byte SHA-256. For the bounded `supervised_operational_single_writer` fallback, version evidence is the exact file ID, observed `modified_time`, and complete-byte SHA-256. The fallback does not weaken release integrity, backup, exact-ID targeting, readback, or manual-recovery requirements; it substitutes verified operational exclusivity only for a provider write precondition that the selected connector does not expose.
