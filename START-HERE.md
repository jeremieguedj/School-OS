# School-OS agent entry point

This is the neutral entry point for a fresh agent. It is intentionally thin.

## Determine the mode

1. Read `release.yaml` when working from a supplied release package.
2. Read `docs/product-principles.md`, `PLAN.md`, and `PROGRESS.md` when maintaining this repository.
3. For a private installed instance, begin from that instance's stable Drive bootstrap and instance manifest.
4. Select exactly one operation: onboarding, import, daily run, manual daily-brief request, task sync, brief generation, upgrade, audit, or maintenance.

## Product-context routing

Read `docs/product-principles.md` during onboarding and before making decisions about architecture, customization, integrations, adapters, capability degradation, or new applications. Routine scheduled operations should not reread it unless their selected operation recipe declares it; they remain governed by the installed recipes and contracts.

## Classify proposed changes

Before changing an installed instance or this reusable system, classify the request:

1. **Configuration or personalization** selects existing behavior without changing core policy.
2. **Compatible expansion** adds a conformant adapter, tool, application, analysis, automation, or workflow while preserving core invariants and contracts. It is normal School-OS evolution and does not make an instance a fork.
3. **Core architectural change** alters an invariant, canonical data meaning, a generic contract incompatibly, or release/upgrade behavior.

Proceed with the first two categories under the selected operation and ordinary user authorization. Before the third, explain why compatible expansion is insufficient, explicitly warn that the change may impair future official updates, and obtain the user's approval. Do not treat a user-created adapter as a core change merely because its provider is not included in the official release.

## Instruction hierarchy

For an installed instance, use this order:

1. Platform safety rules and the runtime's actual tool capabilities.
2. Direct user instruction for the current operation.
3. The selected installed operation recipe.
4. The installed release architecture and contracts.
5. Valid instance configuration and state.
6. Historical logs and derived files.

Configuration supplies instance values; it does not rewrite generic behavior. Adapters map generic contracts to a selected runtime or provider; they do not redefine core policy.

## Read narrowly

Read the selected operation recipe first, then only the dependencies it declares. Do not rely on conversational memory for current state. Stop before writes if required instructions, configuration, state, or capabilities are unavailable or conflict.

## Repository maintenance rule

Keep this file generic. Do not add private household details, provider IDs, domains, recipients, credentials, message content, or operational copies here.

## Repository development continuity

School-OS development must remain independent of any particular coding agent,
vendor, local workspace, or conversation. GitHub is the durable shared state
from which another agent must be able to resume the work.

When maintaining this repository:

1. Follow the current approved release plan and the specification it links.
   Keep milestone status in that release plan accurate; do not infer executable
   support from documentation alone.
2. On resumption, inspect the actual branch, working tree, implementation, and
   Git history, then reconcile the plan, specification, and progress log with
   that evidence before continuing.
3. Append `PROGRESS.md` after each meaningful work unit, before a handoff or
   planned stop, and when blocked. Record completed and unfinished work,
   validation evidence, relevant files, blockers, decisions, and the exact next
   action.
4. For every accepted repository change, run validation appropriate to the
   change, including the privacy scan before publishing; commit all and only
   accepted in-scope files; push the descriptive commit to the intended GitHub
   branch; and verify that the remote branch resolves to that commit before
   reporting the work complete.

Never leave accepted work only in a local working tree or unpushed commit. Never
publish private-instance data, credentials, or unrelated user changes. If
validation, GitHub authentication or authorization, the push, or remote
verification fails, preserve the local changes and report the work as incomplete
with the exact blocker.
