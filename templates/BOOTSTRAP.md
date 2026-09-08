# School-OS instance bootstrap

This file is private-instance routing only.

1. Read the immutable installation-admission receipt by the exact reference established during installation, then verify its content-manifest ID and hash.
2. Read the admitted content manifest and the private instance manifest by their exact references; reject incomplete or unadmitted generations.
3. Resolve and read the content manifest's exact admitted archive and
   `SHA256SUMS` references. Verify both stored hashes and the checksum line,
   safely extract the pinned archive, then verify its complete internal
   inventory before importing or executing any installed module. A fresh host
   must not consult a live repository or an unadmitted staging file.
4. Resolve the active installed release and its exact operation-registry reference.
5. Read the registry, then resolve the requested operation's installed recipe by its registry path; never select a recipe by display name or filename search.
6. Read that release's `START-HERE.md`, then the resolved recipe and its declared private configuration/state dependencies.
7. Stop before writes if active release, admission, package, manifest, configuration, or required capability status is missing or conflicting.

Do not place household details, provider IDs, source queries, recipients, or operational recipes in this bootstrap.
