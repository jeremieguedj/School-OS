# School-OS

School-OS is a reusable, agent-operated system for turning school or family communications into a private, source-linked knowledge base, task register, and daily brief.

It is designed for this deployment model:

```text
GitHub tagged release -> user manually shares release with agent -> installed runtime in Google Drive -> manual/scheduled operations run from Drive
```

GitHub is the reusable upstream. A user's Google Drive contains the active installed release and all private configuration, source catalog, task history, and runtime state. A scheduled run must not depend on GitHub access.

## Principles

- Private data never belongs in this repository.
- The source catalog preserves facts, provenance, coverage, and raw source text according to the installed configuration.
- Derived summaries, guidelines, and task projections are regenerated from canonical records.
- The external task app is a user interaction surface; the canonical task record and history remain in the private instance.
- Providers and agent runtimes are selected explicitly through adapters and configuration.
- The package must be usable by a single agent without conversational memory or subagents.
- All write-capable operations follow the installed operation recipe and its verification requirements.

## Repository map

- [START-HERE.md](START-HERE.md) — neutral agent entry point.
- [PLAN.md](PLAN.md) — resumable implementation plan.
- [PROGRESS.md](PROGRESS.md) — current execution checkpoint.
- [core](core) — generic operations, contracts, and decision tables.
- [adapters](adapters) — runtime and provider mappings.
- [templates](templates) — synthetic private-instance starting files.
- [docs](docs) — architecture, privacy boundaries, onboarding, and deferred review.

## Current status

This repository is being built from an existing private deployment. It intentionally contains no real names, domains, email messages, Drive IDs, provider IDs, recipients, or secrets. It is not yet a released installer.
