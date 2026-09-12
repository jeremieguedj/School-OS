# Product principles

## Purpose

School-OS gives parents a lossless, source-linked, efficient way to preserve and retrieve substantive information received from their children's schools across a school year and beyond. Google Drive is the source of truth for an instance's processed knowledge, source index, configuration, and operating history. School-OS provides a canonical data layer on which useful applications and workflows can be built; it is not limited to any one brief, task manager, or delivery channel.

## People and agent roles

The primary human users are usually one or two parents or guardians managing school information for one or more children. Users choose how many agents they use: one agent, a replacement or backup, or several agents with different jobs. School-OS does not restrict that number. This is a small-household system; concurrent updates by multiple agents to the same canonical Drive data are explicitly outside the current scope. Do not build locks, leases, fencing, or concurrent-write conflict resolution for that edge case.

Agents interact with School-OS in distinct roles:

- a system-development agent maintains and improves the reusable School-OS package;
- an instance agent installs, operates, queries, or customizes a parent's private deployment; and
- a previously unknown runtime discovers its capabilities and selects compatible adapters before it performs an operation.

All three roles use the same product principles when making design or operational decisions.

An instance must be usable from managed or cloud agent applications with limited resources and temporary execution environments. It must not require a dedicated personal machine, a continuously running local process, or a coding CLI. A fresh capable agent starts from the instance on Drive and discovers the instructions, state, tools, and unfinished work it needs; the previous agent's conversation and local files are not required.

## Source and processing boundary

Raw emails, attachments, and other source material remain in their original source systems. School-OS does not maintain a duplicate raw-source archive on Drive. Download raw material temporarily into the agent's available execution environment only for processing, then discard the temporary material after verifying that the resulting knowledge, source references, and processing state have been saved. Here, local processing means the agent's execution environment; it does not imply a parent's physical computer.

The source index must identify the source account, original item, and relevant part or attachment accurately enough to retrieve and check it again when access permits. Stable source-account and item identities are independent of the current adapter or connection and must survive reconnection or adapter replacement; current retrieval locators are separate. Preserve substantive facts, instructions, qualifications, deadlines, and action requirements in canonical knowledge, rather than relying on summaries or source links alone. Record unread, unsupported, incomplete, or unavailable content explicitly. If an original is later deleted or becomes inaccessible, retain the processed knowledge and disclose the limit on source verification; preserving originals independently of their source system is not a product guarantee.

Canonical source and attachment record identities belong to School-OS. Critical decisions about identity, correctness, completion and recovery must not depend on the presence, format, permanence or cross-connector consistency of API/provider-specific parameters, identifiers or connector-generated metadata. Keep those details inside replaceable adapters as access aids; their absence or change must not invalidate canonical knowledge or make unrelated operations fail. An adapter may obtain a current provider handle to perform an operation, but that handle does not establish the target's identity or correctness.

Identify and recover sources through their own observable information and content, using a documented reasoning procedure that combines the available evidence. For email, use the original subject, received date/time, sender, To/Cc recipients, attachment filenames and relevant body/attachment content or conversation context. Preserve the meaning, timezone and precision of dates and the roles of addresses; do not substitute sender date, receipt time or observation time for one another. No single field, field combination, provider ID, RFC Message-ID header or content fingerprint is a universally unique or mandatory key. Account for missing fields, repeated names, identical content and connector presentation differences. Optional identifiers may accelerate search, but must not decide identity or acceptance. Distinguish a corroborated content association from proof of a particular physical message occurrence, and preserve ambiguity when the available source evidence cannot distinguish candidates. An unresolved lookup must not erase prior knowledge, silently merge different sources, or stop unrelated work.

Processing and startup must remain bounded as history grows. Read the relevant records and source items in manageable units, preserve progress on Drive, and retrieve an original again only when the operation needs it. Do not require loading the whole history or an arbitrarily large source into an agent's working environment.

## Tools, schedules, and operating visibility

Keep a durable instance register of known tools, adapters, connections, and scheduled jobs. Distinguish available or configured adapters from the currently selected adapter for a particular operation or job; an instance may use several adapters and schedulers at once. Record where each connection and scheduler is managed, the relevant provider references, supported capabilities, and when those capabilities or settings were last verified. Credentials remain in the appropriate authorized credential store.

For each known scheduled job, record its purpose, executing agent or runtime, scheduler location and management reference, trigger and timezone where applicable, input scope, selected adapters, and output destinations. Keep desired settings separate from externally observed status and its verification time: editing the register alone does not create, change, or stop an external schedule. Do not silently rebind existing jobs when a default adapter changes.

Record runs and resulting outputs with enough attribution to identify the responsible job, executing or generating agent, sending service or account, and delivery or artifact reference. A new agent must be able to explain which known job produced a particular brief and where that job is managed. The register describes known jobs and last observed state; it must not claim to enumerate unregistered jobs or guarantee that stale external observations are current.

## Core use cases

- Catalog communications and preserve their substantive information and provenance, with raw material retained only in its source system and temporary processing copies discarded.
- Query any information received from school, including historical facts, guidelines, deadlines, and action items.
- Let any agent connected to the instance and capable of reading its records answer: "What are the current known scheduled jobs, which agents run them, and where are they managed?" Report the recorded status, last verification, and any freshness or access limits; identify the job and sender responsible for a recorded brief when asked.
- Reconcile actionable requests into durable canonical tasks and synchronize them with a selected task application when configured.
- Produce recent-update briefs, including the currently implemented daily email brief and an optional audio brief when the runtime and selected service support it.
- Easily create new applications, automations, analyses, and workflows on top of the canonical School-OS data layer without redesigning ingestion or compromising provenance.
- Install from a user-supplied packaged GitHub release and later update the private instance while retaining its private data, configuration, and compatible user-created adapters, applications, and workflows.

Email, task synchronization, and audio generation are reference applications of the data layer, not the boundary of the product.

## Design priorities

Apply these priorities when requirements or implementation choices compete:

1. **Losslessness and provenance.** Preserve complete available substantive source information within the configured scope as processed knowledge, with an accurate source index. Losslessness does not require a duplicate archive of raw emails or attachments. Every source-derived claim must remain traceable, and unread, incomplete, unavailable, or unsupported content must be represented explicitly rather than silently omitted.
2. **Deterministic behavior.** Use stable identities, explicit decision tables, ordered procedures, verification, and rebuildable derived data instead of relying on conversational memory or intuition.
3. **Simplicity.** Design for the normal one- or two-parent household while allowing the user's choice of agents and jobs. Concurrent writes to the same canonical data are outside the current scope. Prefer simple adapters and avoid infrastructure whose operational cost is not justified by a supported use case.
4. **Efficient execution.** Make routine operations token-efficient and executable without unusually strong model reasoning. Read narrowly, reuse canonical records, encode repeated decisions in contracts and recipes, and bound temporary downloads and processing independently of accumulated history.
5. **Tool agnosticism.** Core business logic and canonical data meaning must not depend on a particular agent runtime, storage provider, email provider, task manager, audio service, scheduler, or other application. Drive is the instance's canonical home; integrations implement stable contracts through adapters so tools can be selected, replaced, or newly discovered without redefining system behavior. Record the active selection at its appropriate operation or job scope.
6. **Capability-led portability.** Detect the actual capabilities and limits of the runtime/provider combination, including its managed or cloud execution environment. An unfamiliar agent must be able to discover what it can do, select conformant adapters, and declare supported degradation rather than guess from a vendor name. No supported core use case may depend exclusively on a dedicated personal machine or coding CLI.
7. **Extensibility from canonical data.** New applications should consume the existing contracts and canonical data. They must not create an incompatible parallel source of truth.
8. **Extensible and upgradable instances.** Users may expand their instance with new conformant adapters, tools, applications, and workflows. A compatible local addition is a normal part of School-OS, not a core fork, and later system upgrades should preserve it.
9. **Independence from brittle technical details.** Critical paths and recovery must rely on durable School-OS state and the source's own information and meaning. API/provider-specific parameters, IDs and connector metadata are replaceable implementation details, not prerequisites for canonical correctness or continuity. Missing or changed details should trigger another supported access route or a clearly scoped unresolved item, not a failure of the instance. Use agent reasoning to apply explicit, source-grounded procedures rather than assume uniform technical behavior across tools.

## Release and instance lifecycle

GitHub is the authoritative source for the official School-OS system and its latest published releases. A typical user does not need to connect an agent to GitHub: the user downloads the published release package, commonly a ZIP or other release archive, gives it to the agent, and asks the agent to install or upgrade the private instance. Production operations use the pinned installed release rather than a live GitHub branch.

The private instance is expected to evolve. A parent may work with an agent to add support for another task manager, delivery service, analysis, application, or workflow. An addition that follows the canonical data model, invariants, and applicable contracts is compatible system expansion and should not by itself prevent future system upgrades.

Changing a core invariant, redefining canonical data meaning, changing a generic contract incompatibly, or altering release/upgrade behavior is different from adding a conformant extension. Before making such an architectural change, an agent must warn the user that it may impair compatibility with future official releases, explain the consequence, and obtain explicit approval.

## Compatibility posture

School-OS is vendor-agnostic. Known environments used to improve compatibility include Claude Co-Work, Gemini Spark, Grok Bot, GPT Work, and Meta Muse, but these are examples rather than architectural dependencies or blanket compatibility guarantees. Conformance is established from observed capabilities for the exact runtime, authorization, provider, and execution surface.

The canonical instance lives on Google Drive, with adapters for selected email, task, scheduler, runtime, and audio tools. Those integrations form an extensible adapter pattern; they do not define a closed list of tools or application types that School-OS may support. These principles describe the intended product; an existing implementation is not evidence that every requirement is already supported.
