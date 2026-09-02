# Architecture

## Separation boundary

School-OS has two layers.

| Layer | Location | Authority |
|---|---|---|
| Reusable system | GitHub | Generic architecture, operations, schemas, templates, adapters, tests, and release metadata |
| Private instance | User-controlled Google Drive | Installed release, configuration, source catalog, task records, derived files, runtime cursors, and provider bindings |

GitHub publishes a versioned package. The user transports that package manually or through an optional connected agent. The Drive installation is pinned to one release and is the only system copy used by production runs.

## Private-instance areas

```text
instance root/
  BOOTSTRAP.md
  instance.yaml
  system/releases/<version>/
  config/
  data/
  state/
```

- `system/` contains managed release copies.
- `config/` contains household and integration choices.
- `data/` contains canonical source catalog, task register, provenance, and derived knowledge.
- `state/` contains cursors, bindings, delivery state, maintenance status, and progress.

## Core invariants

- Every source-derived claim has provenance.
- Every catalog record has stable identity.
- Facts are atomic and independently classified.
- Source coverage accounts for substantive source content or explicitly records why no fact was produced.
- A finite unresolved request becomes a task; a standing routine is a guideline, not a task.
- Derived data is rebuildable from canonical data.
- External task-provider identities never replace canonical task identities.
- Core behavior is independent of any one agent runtime or task provider.
- Scheduled execution uses the Drive-installed release, never a live GitHub branch.

See `docs/instruction-ownership.md` for where each type of rule belongs.
