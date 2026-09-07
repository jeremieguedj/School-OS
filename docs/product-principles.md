# Product principles

## Purpose

School-OS gives parents a lossless, source-linked, efficient way to preserve and retrieve information received from their children's schools across a school year and beyond. It provides a canonical data layer on which useful applications and workflows can be built; it is not limited to any one brief, task manager, or delivery channel.

## People and agent roles

The primary human users are usually one or two parents or guardians managing school information for one or more children. This is a small-household system with a low expected risk of concurrent writers.

Agents interact with School-OS in distinct roles:

- a system-development agent maintains and improves the reusable School-OS package;
- an instance agent installs, operates, queries, or customizes a parent's private deployment; and
- a previously unknown runtime discovers its capabilities and selects compatible adapters before it performs an operation.

All three roles use the same product principles when making design or operational decisions.

## Core use cases

- Preserve communications and their provenance without silently losing substantive information.
- Query any information received from school, including historical facts, guidelines, deadlines, and action items.
- Reconcile actionable requests into durable canonical tasks and synchronize them with a selected task application when configured.
- Produce recent-update briefs, including the currently implemented daily email brief and an optional audio brief when the runtime and selected service support it.
- Easily create new applications, automations, analyses, and workflows on top of the canonical School-OS data layer without redesigning ingestion or compromising provenance.
- Install from a user-supplied packaged GitHub release and later update the private instance while retaining its private data, configuration, and compatible user-created adapters, applications, and workflows.

Email, task synchronization, and audio generation are reference applications of the data layer, not the boundary of the product.

## Design priorities

Apply these priorities when requirements or implementation choices compete:

1. **Losslessness and provenance.** Preserve complete available source information within the configured scope. Every source-derived claim must remain traceable, and unavailable or unsupported content must be represented explicitly rather than silently omitted.
2. **Deterministic behavior.** Use stable identities, explicit decision tables, ordered procedures, verification, and rebuildable derived data instead of relying on conversational memory or intuition.
3. **Simplicity.** Design for the normal one- or two-parent household. Do not introduce coordination or concurrency machinery without a concrete risk that justifies its operational cost.
4. **Efficient execution.** Make routine operations token-efficient and executable without unusually strong model reasoning. Read narrowly, reuse canonical records, and encode repeated decisions in contracts and recipes.
5. **Tool agnosticism.** Core business logic and canonical data must not depend on a particular agent runtime, storage provider, email provider, task manager, audio service, scheduler, or other application. Integrations implement stable contracts through adapters so tools can be selected, replaced, or newly discovered without redefining system behavior.
6. **Capability-led portability.** Detect the actual capabilities and limits of the runtime/provider combination. An unfamiliar agent must be able to discover what it can do, select conformant adapters, and declare supported degradation rather than guess from a vendor name.
7. **Extensibility from canonical data.** New applications should consume the existing contracts and canonical data. They must not create an incompatible parallel source of truth.
8. **Extensible and upgradable instances.** Users may expand their instance with new conformant adapters, tools, applications, and workflows. A compatible local addition is a normal part of School-OS, not a core fork, and later system upgrades should preserve it.

## Release and instance lifecycle

GitHub is the authoritative source for the official School-OS system and its latest published releases. A typical user does not need to connect an agent to GitHub: the user downloads the published release package, commonly a ZIP or other release archive, gives it to the agent, and asks the agent to install or upgrade the private instance. Production operations use the pinned installed release rather than a live GitHub branch.

The private instance is expected to evolve. A parent may work with an agent to add support for another task manager, delivery service, analysis, application, or workflow. An addition that follows the canonical data model, invariants, and applicable contracts is compatible system expansion and should not by itself prevent future system upgrades.

Changing a core invariant, redefining canonical data meaning, changing a generic contract incompatibly, or altering release/upgrade behavior is different from adding a conformant extension. Before making such an architectural change, an agent must warn the user that it may impair compatibility with future official releases, explain the consequence, and obtain explicit approval.

## Compatibility posture

School-OS is vendor-agnostic. Known environments used to improve compatibility include Claude Co-Work, Gemini Spark, GPT Work, and Meta Muse, but these are examples rather than architectural dependencies or blanket compatibility guarantees. Conformance is established from observed capabilities for the exact runtime, authorization, provider, and execution surface.

The current reference deployment uses Google Drive and includes adapters for selected email, task, scheduler, runtime, and audio tools. Those implementations establish an extensible adapter pattern; they do not define a closed list of tools or application types that School-OS may support.
