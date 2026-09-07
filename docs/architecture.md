# Architecture

## Separation boundary

School-OS has two layers.

| Layer | Location | Authority |
|---|---|---|
| Reusable system | GitHub | Generic architecture, operations, schemas, templates, adapters, tests, and release metadata |
| Private instance | User-controlled Google Drive | Installed release, configuration, source catalog, task records, derived files, runtime cursors, and provider bindings |

GitHub publishes a versioned package. The user transports that package manually or through an optional connected agent. The Drive installation is pinned to one release and is the only system copy used by production runs.

The product purpose, personas, use cases, and priority order that drive this architecture are defined in `docs/product-principles.md`.

## Core and expansion boundary

The core architecture consists of canonical data meaning, system invariants, generic contracts, generic operation semantics, and release/upgrade behavior. Official source and releases are managed on GitHub; one private instance runs from its pinned installed release.

School-OS is intentionally expandable. Compatible expansion includes:

- a new runtime or provider adapter that implements an existing contract;
- a new tool integration that preserves canonical identities and data meaning;
- a new application, analysis, report, automation, or workflow built on canonical data and contracts; and
- household configuration or presentation customization that does not redefine core policy.

Compatible additions may be created for one private instance, may be stored and tracked within that School-OS instance, and do not become architectural forks merely because they are local or are not included in an official release. For example, an adapter for a different task manager is ordinary compatible expansion.

A proposed change crosses into core architectural divergence when it changes an invariant, redefines canonical data meaning, breaks a generic contract, bypasses required provenance or verification, or changes release/upgrade semantics incompatibly. Before making such a change, the agent must explain why compatible expansion cannot satisfy the request, warn that future official updates may be impaired, and obtain explicit user approval.

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

- Available substantive source information within the configured scope is never silently discarded; unsupported or unavailable content has an explicit coverage outcome.
- Every source-derived claim has provenance.
- Every catalog record has stable identity.
- Facts are atomic and independently classified.
- Source coverage accounts for substantive source content or explicitly records why no fact was produced.
- A finite unresolved request becomes a task; a standing routine is a guideline, not a task.
- Derived data is rebuildable from canonical data.
- External task-provider identities never replace canonical task identities.
- Core behavior is independent of any one agent runtime, storage provider, email provider, task manager, audio service, scheduler, or other application.
- Provider- and runtime-specific behavior stays behind adapters that implement stable core contracts. The adapter pattern is extensible and is not limited to the integrations currently implemented.
- Official and user-created adapters are judged by the same contracts and observed capabilities, not by their origin.
- An unfamiliar runtime is handled through observed capability discovery and declared degradation, never assumptions based only on its vendor or model name.
- Repeated decisions are encoded in contracts, decision tables, and ordered operations so correctness does not depend on conversational memory or unusually strong model reasoning.
- Routine execution reads only its declared dependencies and reuses canonical state so it remains token-efficient.
- The normal deployment assumes one or two parent users and low write concurrency. Add coordination complexity only for a concrete, evidenced risk and keep it scoped to the operation that needs it.
- New applications and workflows consume the canonical data layer and contracts rather than creating a parallel source of truth.
- System upgrades preserve private data, configuration, and compatible instance additions while validating them against the new release's contracts.
- Scheduled execution uses the Drive-installed release, never a live GitHub branch.

See `docs/instruction-ownership.md` for where each type of rule belongs.
