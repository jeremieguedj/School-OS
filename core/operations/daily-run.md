# Daily-run operation

## Purpose

Process new relevant communications losslessly, reconcile private derived records and task state, then render and deliver the approved daily brief.

## Ordered phases

1. **Preflight** — read the instance manifest, selected release, configuration, required capability profile, state, and current operation lock. Capture one run timestamp in the configured timezone.
2. **Discover** — query only configured sources using the persisted overlap/cursor rules. Deduplicate by immutable source identity.
3. **Catalog** — fetch complete candidate records, compare them with stored source membership, preserve raw available text, create/refresh atomic facts, source coverage, and attachment outcomes.
4. **Reconcile** — rebuild or update only the derived files affected by the verified catalog changes: updates, guidelines, durable profiles, index, and canonical tasks.
5. **Task sync** — execute `task-sync.md` through the explicitly selected adapter.
6. **Brief** — execute `brief-rendering.md`. The brief renderer reads declared private derived inputs; it does not repeat source discovery.
7. **Commit/report** — advance cursors only after every required write and side effect has been verified. Record a concise private run result.

## Invariants

- Work from the private source catalog before consulting external source mail for known catalogued material.
- Read only bounded relevant records, never all historical data by default.
- Preserve source provenance in every generated fact/update/task.
- Do not claim a source, attachment, provider event, write, or message was processed without observed verification.
- On a required failure, preserve the last verified checkpoint and report the blocking phase.
