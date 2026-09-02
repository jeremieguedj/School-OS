# Release operation

## Purpose

Publish a reusable tagged source release without private-instance material.

## Required checks

1. Verify the working tree contains no private configuration, source content, credentials, IDs, task bindings, generated briefs, or diagnostics.
2. Run `python3 scripts/validate.py`; schema, reference, fixture, migration-idempotence, privacy, and adapter-conformance checks must all pass from a clean checkout.
3. Update `release.yaml`, changelog, compatibility metadata, and migration list. The tagged manifest must declare the tag's version and `status: released`.
4. Create an annotated `v<system_version>` tag for the reviewed commit. Sign it when supported; in every case, require the published tag to be protected against mutation by the release host. Build only from that exact commit with normalized archive metadata.
5. Build `school-os-<system_version>.tar.gz` with the root `School-OS-<system_version>/`. Generate its internal `RELEASE-INVENTORY.sha256` over every other regular payload file in bytewise path order.
6. Independently generate `SHA256SUMS` containing exactly the archive SHA-256 and filename. Verify the archive checksum, extract into an empty directory, reject unsafe or undeclared entries, and verify every inventory line and file.
7. Confirm the extracted `release.yaml`, tag, tagged commit, changelog, archive name, and release version agree. Rebuild from the tag and require a byte-identical archive.
8. Require the hosting provider's immutable-release control to be enabled before publication. Create the release as a draft, attach the archive and checksum asset, verify the complete draft, and only then publish it as one prerelease or release.
9. Read back the release metadata and require it to report immutable. A mutable or partially published release must be withdrawn from installation and superseded with a new version; never repair it in place.

A source release is not a private-instance upgrade. Users choose when to transport and install it.
