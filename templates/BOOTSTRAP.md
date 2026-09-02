# School-OS instance bootstrap

This file is private-instance routing only.

1. Read the adjacent/private instance manifest by the reference established during installation.
2. Resolve the active installed release.
3. Read that release's `START-HERE.md`.
4. Read the requested operation and its declared private configuration/state dependencies.
5. Stop before writes if active release, manifest, configuration, or required capability status is missing or conflicting.

Do not place household details, provider IDs, source queries, recipients, or operational recipes in this bootstrap.
