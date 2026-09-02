# Release operation

## Purpose

Publish a reusable tagged source release without private-instance material.

## Required checks

1. Verify the working tree contains no private configuration, source content, credentials, IDs, task bindings, generated briefs, or diagnostics.
2. Run schema, reference, fixture, and adapter-conformance checks available for the release.
3. Update `release.yaml`, changelog, compatibility metadata, and migration list.
4. Build the declared release asset from the selected tagged source.
5. Record file inventory/checksum data according to the release manifest.
6. Publish a tagged release and release notes.

A source release is not a private-instance upgrade. Users choose when to transport and install it.
