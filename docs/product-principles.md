# Product principles

## Purpose

School-OS gives parents a lossless, source-linked, efficient way to preserve and retrieve substantive information received from their children's schools across a school year and beyond. Google Drive is the source of truth for an instance's processed knowledge, source index, configuration, and operating history. School-OS provides a canonical data layer on which useful applications and workflows can be built; it is not limited to any one brief, task manager, or delivery channel.

## Decision authority

This document is the source of truth for product and design decisions. When a decision is not explicitly covered by an approved plan or specification, ground it in these principles and the core use cases below. Historical implementations, experiments, agent preferences and tool defaults do not supply missing product requirements. Direct user instructions take precedence; surface conflicts and update the relevant documents rather than silently changing the principles. Google Drive remains the separate source of truth for each instance's data and operating state.

Every new or changed architecture decision requires explicit user approval before adoption or implementation, including decisions presented as compatible extensions or implementation details that actually change system structure or behavior. Explain the concrete proposal, relevant principles, alternatives, tradeoffs and remaining unknowns, and record the user's decision in the active plan. Do not infer approval from silence, a general request to implement, or compliance with these principles. Already explicitly approved decisions may be implemented without asking again. Routine nonarchitectural implementation choices may proceed within approved scope, grounded in this document.

## People and agent roles

The primary human users are usually one or two parents or guardians managing school information for one or more children. Users choose how many agents they use: one agent, a replacement or backup, or several agents with different jobs. School-OS does not restrict that number. This is a small-household system; concurrent updates by multiple agents to the same canonical Drive data are explicitly outside the current scope. Do not build locks, leases, fencing, or concurrent-write conflict resolution for that edge case.

Agents interact with School-OS in distinct roles:

- a system-development agent maintains and improves the reusable School-OS package;
- an instance agent installs, operates, queries, or customizes a parent's private deployment; and
- a previously unknown runtime discovers its capabilities and selects compatible adapters before it performs an operation.

All three roles use the same product principles when making design or operational decisions.

An instance must be usable from managed or cloud agent applications with limited resources and temporary execution environments. It must not require a dedicated personal machine, a continuously running local process, or a coding CLI. A fresh capable agent starts from the instance on Drive and discovers the instructions, state, tools, and unfinished work it needs; the previous agent's conversation and local files are not required.

## Approved first-use setup direction — 2026-09-16

A core first-use path begins when a parent gives a new agent session one
agent-accessible link to a ZIP or School-OS folder containing a fresh, new,
unconfigured starter bundle and says only, “setup my schoolOS.” The agent must
discover the dedicated setup instructions through the bundle's `README.md`,
`START-HERE.md`, and `AGENTS.md` entry path. A Claude-specific entry file contains
only an `@AGENTS.md` import so the shared instructions remain authoritative. This
path must not require a filled developer trial prompt, repository history,
preloaded household data, or prior conversation.

The starter bundle is not yet a configured or persisted private instance, and
nothing has been ingested merely because the bundle was shared. The link provides
access to the bundle; it is not a credential, account authorization, or permission
for source ingestion or outbound effects. The setup request, later ingestion, and
any outbound action retain separate instructions and authorization boundaries.

During setup, the agent interviews the parent for the household, school, mailbox,
and tool choices needed to configure the instance. It explains known options and
capabilities available to that agent rather than assuming a fixed vendor list.
For selected tools, it reuses or creates the approved shared, API-agnostic
semantic adapters described below. This direction adds no new schema, runtime,
installer, migration system, or release-management engine.

## Approved setup and adapter direction — 2026-09-15

The user explicitly approved an agent-led setup interview. Ask which task tool the parent wants to use, explain known options available to the current agent, and establish the selected tool and relevant scope. A familiar vendor name does not establish access or support. If the desired tool is accessible but has no School-OS adapter yet, the agent may author the missing adapter within the approved School-OS meanings. A new architectural choice still requires explicit approval; this direction does not approve every possible tool mapping in advance.

A **School-OS tool adapter** is shared guidance mapping School-OS meanings and procedures to the selected tool's concepts and behavior. Maintain one reusable semantic mapping per tool so any capable agent with access to that tool can use the same guidance. For a task tool, that includes how approved task fields, parent edits, owned task identity, recurrence and synchronization correspond to the tool. The mapping must preserve the same canonical meaning across agents.

The agent's **connector** supplies access to the tool and owns API calls, authentication, SDK and transport details. The School-OS adapter is independent of that API implementation; it does not duplicate a provider wrapper for each agent or connector. Agents may use different connectors to apply the same tool guidance, but must check that their available route can carry out the required operation and verify its outcome. Provider handles and connector metadata remain replaceable access aids, not canonical identity or evidence of completion.

This explicitly distinguishes the current semantic use of “School-OS adapter” from older documents that used “adapter” for provider/API wrappers. It adds no central registry, installer, schema or write engine. The long-term tools/jobs visibility and automated lifecycle principles below remain product direction; their centralized D7 machinery and D8 upgrade, migration, compatibility and release-management machinery are explicitly deferred from the current MVP in the [active restart plan](plans/restart/PLAN.md#user-approved-mvp-revisions-2026-09-15). The fresh starter bundle and discoverable setup path above remain in scope.

## Approved completion review direction — 2026-09-15

When clear source evidence satisfies a specific task that is not already completed, record **“Completion detected — awaiting parent confirmation.”** Preserve the evidence, its source and the processing coverage that establishes what was actually read. Match the evidence to the same child, request and relevant context; related subject matter alone is insufficient. This state is distinct from completed. Source interpretation must not directly complete the task, and new evidence must not downgrade a task the parent already completed.

The chosen task tool's shared School-OS adapter uses a supported custom status or section to separate these candidates for review. The parent reviews the evidence and checks the confirmed tasks off, including checking off a reviewed group together. Approved D5 synchronization then reconciles and verifies completed state between Drive and the task app, preserving parent confirmation and source evidence separately. Unsupported tool presentation must remain visible; do not pretend that a completion checkbox represents an unconfirmed candidate.

This confirmation step is explicitly approved and needs no further architecture gate. Automatic closure may be considered after a later accuracy review, but no accuracy threshold, automatic promotion or future activation is approved. This direction does not expand source access to Sent mail or another unapproved source scope. Follow the [completion-review instructions](../operations/completion-review.md); the testing stop remains in force.

## Approved brief recipe direction — 2026-09-15

The daily brief begins as a template recipe. Users and agents may create any number of brief recipes and choose or adopt whichever they want. The supplied starter is a useful starting point, not a fixed selection policy for every brief. Recipe customization must preserve source accuracy, qualifications, honest coverage, original source-date meaning and the distinction between open, confirmation-pending and completed tasks.

The approved starter selects newly verified or substantively corrected information for the reporting interval, shows original school dates, and includes relevant open tasks. After complete relevant ingestion, it may use verified canonical knowledge and tasks when task-app synchronization fails, while plainly disclosing the failed sync and the limit on app-state freshness. It must not describe unknown app edits or outcomes as synchronized. This selection and disclosure behavior is approved for the starter; other chosen recipes may arrange or select information differently within the same product safeguards.

The ordinary daily brief still follows complete relevant ingestion. The later explicit Q7–Q9 approvals below settle the manual freshness conversation and optional audio policy; they are not inferred merely from recipe extensibility. Follow the [brief-recipe instructions](../operations/brief-recipes.md). This direction adds no recipe registry, selection precedence or scheduling mechanism. Development execution follows the separately recorded user authorization.

## Approved scope, ingestion and brief refinements — 2026-09-15

Knowledge and tasks must retain their real applicability: individual child,
family or school. Support a child's topic history and evolution without copying
one shared school statement to every child or duplicating one family obligation.
The user subsequently explicitly approved the concrete retained schema and
lookup/index architecture. The operational [data contract](../contracts/data.md)
records it. New canonical meaning or representation beyond that approved design
still needs explicit approval. The user rejected a linked-piece representation
for oversized record fields and delegated the page-budget choice. The current
contract therefore uses one 64 KiB encoded-page maximum and keeps each Knowledge
statement and required array on its owning record. Ordinary pagination occurs
between complete records. A later evidence-based increase changes that one shared
contract parameter for future writes; it adds no per-instance setting, new record
shape or required rewrite of valid smaller pages.

The daily input is all School-OS-pending mail in configured scope through run
start; mailbox read status is not ingestion. Each email has one outcome: fully
ingested or not ingested. Full ingestion includes its body and required
attachments, substantive extraction and verified persistence. A partial-email
processing workflow is outside MVP; missing material does not become completed.
Whole-scope discovery and honest source evidence remain necessary.

For a manual brief with known gaps, warn that knowledge could be outdated,
explain available freshness evidence and offer to ingest new mail first. The
parent may choose a clearly limited output now. Ordinary daily briefs still
require complete ingestion. Generated audio is not kept as a School-OS archive
once delivered to the parent. With configured audio, deliver it together with
the email; on audio failure send email alone with an explicit failure notice.

## Source and processing boundary

Raw emails, attachments, and other source material remain in their original source systems. School-OS does not maintain a duplicate raw-source archive on Drive. Download raw material temporarily into the agent's available execution environment only for processing, then discard the temporary material after verifying that the resulting knowledge, source references, and processing state have been saved. Here, local processing means the agent's execution environment; it does not imply a parent's physical computer.

The source index must identify the source account, original item, and relevant part or attachment accurately enough to retrieve and check it again when access permits. Stable source-account and item identities are independent of the current adapter or connection and must survive reconnection or adapter replacement; current retrieval locators are separate. Preserve substantive facts, instructions, qualifications, deadlines, and action requirements in canonical knowledge, rather than relying on summaries or source links alone. Record unread, unsupported, incomplete, or unavailable content explicitly. If an original is later deleted or becomes inaccessible, retain the processed knowledge and disclose the limit on source verification; preserving originals independently of their source system is not a product guarantee.

Canonical source and attachment record identities belong to School-OS. Critical decisions about identity, correctness, completion and recovery must not depend on the presence, format, permanence or cross-connector consistency of API/provider-specific parameters, identifiers or connector-generated metadata. Keep those details at the replaceable connector/access layer as access aids; their absence or change must not invalidate canonical knowledge or make unrelated operations fail. An agent may obtain a current provider handle through its connector to perform an operation, but that handle does not establish the target's identity or correctness. Shared School-OS adapter guidance preserves the required semantic checks independently of that access route.

Email identity and recovery must use source metadata only: the logical mailbox, original subject, sender, sending date/time, separately identified received date/time, To/Cc recipients, and original attachment filenames/count when comparably exposed. Preserve the meaning, timezone and precision of dates and the roles of addresses; do not substitute sending, receipt and observation times for one another. Do not inspect or compare message bodies, quoted text, HTML, MIME content structure, embedded images, attachment bytes, summaries or content fingerprints to establish email identity, attachment identity or thread association. There is no content-inspection fallback for ambiguous metadata. The installed procedure is the [metadata-only identity contract](../contracts/identity.md), derived from the approved restart recipe.

A directly embedded image that visibly carries substantive information may be
read once through an authorized least-stateful route during content processing.
Its meaning belongs to the parent Email body, with a descriptive body location;
it is not an Attachment Group. The remote locator is a replaceable access aid and
never identity evidence. Do not crawl, sign in, submit forms or retain the raw
image. Unsupported, inaccessible, unauthorized or uncertain access keeps the
whole Email not ingested. This content rule does not weaken the metadata-only
identity boundary above.

School-OS catalogs logical emails rather than requiring one record per provider entry or repeated search appearance. Reuse a logical email record when the sufficiently supported normalized metadata recipe agrees and there is no contradictory evidence. Different provider handles alone do not establish different logical emails, force duplicate records, or block ingestion. Preserve distinctions established by source metadata and keep genuinely ambiguous associations explicit. Existing duplicate catalog records must not be silently destructively merged. No single metadata field or field combination is guaranteed unique or universally available; this policy accepts the residual possibility of genuinely different emails sharing all permitted metadata. Do not promise zero identity errors or infer a product failure merely because the number of provider entries differs from the number of logical records.

Keep observed metadata alongside normalized comparison values. Normalize address presentation, domain case and recipient ordering while preserving local-part spelling and To/Cc roles. Decode and unfold subjects and treat outer whitespace as insignificant for comparison; preserve meaningful text and reply/forward prefixes. The original email Date is the primary source timestamp for identity, with its meaning, timezone and precision retained. Obtain a richer individual-message metadata view when a search timestamp is unclear; do not silently replace the source Date with an internal provider, receipt or observation timestamp. Missing fields remain unknown, and optional provider/RFC identifiers remain access aids only. A pending association must not erase prior knowledge or stop unrelated work.

Every attachment record belongs to its logical parent email. Locate attachments using that parent and the original filename when exposed; the same filename in different emails is not a collision. Repeated names within one email identify a candidate group whose members may be separate files or representations of one file. Preserve candidates and explicit processing coverage without selecting by permanent list position or treating different retrieval handles as proof of different documents. Unknown names or inventory scope leave attachment association or coverage unresolved without invalidating the parent email. Metadata agreement does not prove equal content or authorize marking unread material processed.

Catalog each individual message and reply separately. Thread grouping is an optional, inferred navigation aid based on metadata; it must not determine message identity, deduplication or processing completion. Content remains essential to extracting substantive school information, and is read for that purpose only after or alongside metadata cataloging, with separate processing coverage. Removing content from identity does not remove content processing or permit unread material to be marked processed.

Processing and startup must remain bounded as history grows. Read the relevant records and source items in manageable units, preserve progress on Drive, and retrieve an original again only when the operation needs it. Do not require loading the whole history or an arbitrarily large source into an agent's working environment.

Enumeration progress is durable instance data: record the mailbox, configured search scope, completed date windows and unfinished work separately from content-processing completion. Follow available continuation pages even after a short page. A temporary pagination token may accelerate an adapter but cannot be required for recovery; a fresh agent can repeat an unfinished window and reuse logical email records through metadata. Mark a window complete only when the available listing route establishes exhaustion. Narrower windows can reduce work but do not prove that a silently capped tool is complete.

## Current explicit MVP exceptions

The broader product direction below remains intentional. The user has explicitly
deferred general interrupted-canonical-write repair and the separate generic
record/save framework, centralized tools/jobs/register/scheduler management, and
automated upgrades, migrations, compatibility handling and release-management
machinery from this MVP. A distributable fresh starter bundle and discoverable,
agent-led setup are in scope; they do not constitute that deferred machinery.
These exceptions do not remove normal save/readback, durable source windows and
binary coverage, task synchronization, current output attribution, fresh-agent
queries or compatible extensions. Users and agents own nonconcurrent schedules
and normal environment resource management. No complete reset/write-repair
guarantee is made. Current operation recipes carry these boundaries without
requiring the development conversation.

## Tools, schedules, and operating visibility

Keep a durable instance register of known tools, adapters, connections, and scheduled jobs. Distinguish available or configured adapters from the currently selected adapter for a particular operation or job; an instance may use several adapters and schedulers at once. Record where each connection and scheduler is managed, the relevant provider references, supported capabilities, and when those capabilities or settings were last verified. Credentials remain in the appropriate authorized credential store.

For each known scheduled job, record its purpose, executing agent or runtime, scheduler location and management reference, trigger and timezone where applicable, input scope, selected adapters, and output destinations. Keep desired settings separate from externally observed status and its verification time: editing the register alone does not create, change, or stop an external schedule. Do not silently rebind existing jobs when a default adapter changes.

Record runs and resulting outputs with enough attribution to identify the responsible job, executing or generating agent, sending service or account, and delivery or artifact reference. A new agent must be able to explain which known job produced a particular brief and where that job is managed. The register describes known jobs and last observed state; it must not claim to enumerate unregistered jobs or guarantee that stale external observations are current.

## Core use cases

- Start from one agent-accessible link to a fresh, unconfigured School-OS ZIP or folder and the request “setup my schoolOS”; let a new agent discover the setup instructions, interview the parent, and configure and persist the private instance without repository history, preloaded household data, or a developer-authored trial prompt.
- Catalog communications and preserve their substantive information and provenance, with raw material retained only in its source system and temporary processing copies discarded.
- Query any information received from school, including historical facts, guidelines, deadlines, and action items.
- Let any agent connected to the instance and capable of reading its records answer: "What are the current known scheduled jobs, which agents run them, and where are they managed?" Report the recorded status, last verification, and any freshness or access limits; identify the job and sender responsible for a recorded brief when asked.
- Reconcile actionable requests into durable canonical tasks and synchronize them with a selected task application when configured.
- Produce recent-update briefs, including the currently implemented daily email brief and an optional audio brief when the runtime and selected service support it.
- Easily create new applications, automations, analyses, and workflows on top of the canonical School-OS data layer without redesigning ingestion or compromising provenance.
- Later update the private instance from an official release while retaining its private data, configuration, and compatible user-created adapters, applications, and workflows.

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

GitHub is the authoritative source for the official School-OS system and its latest published releases. For first setup, a typical parent gives a new agent one accessible link to a fresh starter ZIP or folder and asks it to set up School-OS; the agent need not receive repository history or connect to GitHub. That starter path is current scope and does not imply an installer. Production operations use the pinned installed system material rather than a live GitHub branch.

Automated upgrade, migration, compatibility and release-management machinery remains future work. A later lifecycle may let a parent give an official release to an agent and ask it to update the private instance while retaining private data, configuration and compatible extensions, but the current starter-bundle setup path does not claim that machinery.

The private instance is expected to evolve. A parent may work with an agent to add support for another task manager, delivery service, analysis, application, or workflow. An addition that follows the canonical data model, invariants, and applicable contracts is compatible system expansion and should not by itself prevent future system upgrades.

All new or changed architecture decisions require explicit approval under the decision authority above. Changing a core invariant, redefining canonical data meaning, changing a generic contract incompatibly, or altering release/upgrade behavior additionally requires explaining the consequence and warning that it may impair compatibility with future official releases. A conformant extension remains compatible expansion, but that classification does not waive approval for any new architecture decision it contains.

## Compatibility posture

School-OS is vendor-agnostic. Known environments used to improve compatibility include Claude Co-Work, Gemini Spark, Grok Bot, GPT Work, and Meta Muse, but these are examples rather than architectural dependencies or blanket compatibility guarantees. Conformance is established from observed capabilities for the exact runtime, authorization, provider, and execution surface.

The canonical instance lives on Google Drive, with adapters for selected email, task, scheduler, runtime, and audio tools. Those integrations form an extensible adapter pattern; they do not define a closed list of tools or application types that School-OS may support. These principles describe the intended product; an existing implementation is not evidence that every requirement is already supported.
