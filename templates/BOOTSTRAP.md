# School-OS instance bootstrap

This file is private-instance routing only.

1. Read the adjacent/private instance manifest by the exact reference established during installation.
2. Resolve the active installed release and its exact operation-registry reference.
3. Read the registry, then resolve the requested operation's installed recipe by its registry path; never select a recipe by display name or filename search.
4. Read that release's `START-HERE.md`, then the resolved recipe and its declared private configuration/state dependencies.
5. Stop before writes if active release, manifest, configuration, or required capability status is missing or conflicting.

Do not place household details, provider IDs, source queries, recipients, or operational recipes in this bootstrap.
