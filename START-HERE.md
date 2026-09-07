# School-OS agent entry point

This is the neutral entry point for a fresh agent. It is intentionally thin.

## Determine the mode

1. Read `release.yaml` when working from a supplied release package.
2. Read `docs/product-principles.md`, `PLAN.md`, and `PROGRESS.md` when maintaining this repository.
3. For a private installed instance, begin from that instance's stable Drive bootstrap and instance manifest.
4. Select exactly one operation: onboarding, import, daily run, manual daily-brief request, task sync, brief generation, upgrade, audit, or maintenance.

## Product-context routing

Read `docs/product-principles.md` during onboarding and before making decisions about architecture, customization, integrations, adapters, capability degradation, or new applications. Routine scheduled operations should not reread it unless their selected operation recipe declares it; they remain governed by the installed recipes and contracts.

## Core-change approval guard

Keep local integrations, applications, workflows, and household customization outside the managed installed release whenever the existing contracts allow it. Before changing School-OS core architecture or editing a managed release file, explicitly warn the user that the change may create a local fork and impair future upgrades, explain why an adapter, configuration, or external application cannot meet the need, and obtain explicit approval. Never describe a modified managed release as an unchanged official release.

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
