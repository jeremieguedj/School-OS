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

## Draft and published readback verification

Use `scripts/verify_release.py` after an operator has created a draft with the
existing GitHub release surface, and again after publication. The command is
read-only: it builds from the supplied local exact ref, reads the GitHub release
and annotated tag with `gh`, downloads the declared assets, and compares their
bytes. It neither creates tags/releases nor uploads, replaces, publishes, or
deletes assets.

For a candidate that still declares `status: unreleased`, draft verification is
allowed only as a preparation check and must explicitly request that status:

```sh
python3 scripts/verify_release.py verify-draft \
  --repo jeremieguedj/School-OS \
  --source-repo . \
  --ref 0123456789abcdef0123456789abcdef01234567 \
  --commit 0123456789abcdef0123456789abcdef01234567 \
  --version 0.1.0-alpha.13 \
  --manifest-status unreleased
```

Final publication requires a separately reviewed exact commit whose manifest
declares `status: released`, as required above. After it is published, rerun
the matching `verify-published` command with `--manifest-status released`.
Both modes reject a wrong ref/commit/version, missing, duplicate, or unexpected
assets, incorrect archive/checksum bytes, a lightweight/mismatched tag, or a
mutable published release. A failed check leaves the release unverified; never
replace assets or move an existing published tag to repair it.

After M4-006 has current acceptance evidence, the authorized release operator
uses an annotated (signed when supported) tag and a body file, never an inline
multiline shell argument. The following is a template only; it is not an
automatic publication path and must not be run for this unreleased candidate:

```sh
git tag -a v0.1.0-alpha.13 0123456789abcdef0123456789abcdef01234567 \
  -F /private/tmp/school-os-release-tag-message.txt
git push origin v0.1.0-alpha.13
python3 scripts/build_release.py \
  --repo . \
  --ref 0123456789abcdef0123456789abcdef01234567 \
  --version 0.1.0-alpha.13 \
  --output-dir /private/tmp/school-os-alpha.13-assets
gh release create v0.1.0-alpha.13 \
  /private/tmp/school-os-alpha.13-assets/school-os-0.1.0-alpha.13.tar.gz \
  /private/tmp/school-os-alpha.13-assets/SHA256SUMS \
  --repo jeremieguedj/School-OS \
  --draft --prerelease --verify-tag \
  --notes-file /private/tmp/school-os-release-notes.md
```

Read back the just-created draft with `verify-draft` before a separate publish
action. Do not use an overwrite option, delete/recreate a release, or replace
an asset; if any verification fails after publication, make a later version.

A source release is not a private-instance upgrade. Users choose when to transport and install it.
