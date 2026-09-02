# School-OS implementation plan

Status: active  
Execution model: resumable. Every completed phase is recorded in `PROGRESS.md`.

## Objective

Build a reusable, privacy-safe School-OS whose generic source is maintained in GitHub and whose installed runtime executes from a user's Google Drive. Private configuration, knowledge, task records, credentials, and runtime state never enter this repository.

The minimum transport path is manual: a user downloads a tagged release and shares it with an agent. GitHub access is optional for an agent and is never required by a scheduled production run.

## Frozen architecture baseline

The architecture is governed by the approved frozen plan of September 2, 2026:

- GitHub holds reusable system source.
- Each user installs a pinned release into Google Drive.
- Google Drive holds the active runtime plus all private configuration, data, and state.
- Scheduled/manual runs resolve a stable Drive bootstrap and execute only the active installed release.
- Core behavior is separate from runtime and provider adapters.
- Drive is the canonical task and knowledge record; a task provider is the user-facing interaction surface.
- The system is tool agnostic through explicit capability contracts and selected adapters.
- The core must work sequentially without GitHub access, subagents, or a specific AI vendor.

Deferred adversarial-review findings are captured separately in `docs/deferred-adversarial-review.md`. They must not change the frozen baseline without explicit approval.

## Execution phases

1. **Foundation** — create repository entry points, governance, plan/progress tracking, privacy rules, and a generic repository skeleton.
2. **Core contracts** — define the portable data, capability, and configuration contracts; establish one source of truth for each rule.
3. **Operations and templates** — create deterministic, agent-facing onboarding, daily-run, catalog, brief, task-sync, and upgrade recipes plus synthetic templates.
4. **Adapters** — establish the current reference adapters without embedding personal provider IDs, names, domains, or secrets.
5. **Release and validation** — add release metadata, synthetic fixtures, validation checklists, and manual-first installation/update instructions.
6. **Current-instance migration** — inventory the existing private Drive instance, create a private configuration mapping, install the first release alongside it, and shadow-validate it.
7. **Cutover** — only after explicit approval, switch scheduled execution to the installed bootstrap, verify production behavior, and retain rollback material.

## Guardrails

- Do not copy private Drive content, source emails, identifiers, secrets, or family-specific configuration into this repository.
- Do not modify the frozen architecture to incorporate deferred reviewer recommendations unless explicitly approved.
- Do not change the live private Drive system or its schedules during phases 1–5.
- Every repository change must be followed by a readback/verification step.
- Progress writes are append-only in intent: do not erase prior checkpoints.
- Use synthetic fixtures only.

## Completion criteria for the current execution

This execution is complete when phases 1–5 are implemented in the repository and the repository is ready for the private-instance inventory/migration phase. Phase 6 and production cutover require separate inspection and explicit confirmation because they touch private systems.
