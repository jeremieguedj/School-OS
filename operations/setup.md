# First setup

Use this operation when a parent is starting an instance or selecting tools for
an existing instance. The outcome is a parent-approved configuration plus shared,
discoverable tool-semantic mappings for the selected tools. Setup does not prove
that live operations work or create a School-OS scheduler. Setup alone does not
authorize ingestion, sending or task updates. If the parent explicitly requests
an import or another operation at the same time, finish setup and then select and
run that separately authorized operation under its own instructions.

This is the one authoritative setup procedure. A new parent may provide only one
agent-accessible link to a fresh School-OS ZIP or folder and say “setup my
schoolOS.” That is enough to begin this procedure. It is not necessary to receive
a developer trial prompt, repository history, prior conversation or preloaded
household data.

Read [the data contract](../contracts/data.md#instance-configuration),
[Drive setup and storage](storage.md#bootstrap-an-instance) and the supplied
[shared mappings](../adapters/README.md). Use their concrete references and page
rules; do not copy an old instance or infer configuration from fictional examples.
Use the parent-supplied starter as the setup source. Do not inspect an ambient
development repository, another agent's transcript or a prior instance to
supplement it. Disclose inherited context instead of claiming bundle-only
discovery.

## 1. Discover the supplied material and establish instance state

1. Open the parent-supplied link with the agent's available file access. If it is
   a ZIP, unpack it in the agent's available temporary workspace so its root
   instructions can be read. Read the supplied `README.md`, `START-HERE.md` and
   `AGENTS.md`, then continue here at `system/operations/setup.md`. Do not require
   an installed-instance manifest before reading a fresh starter.
2. Recognize an unconfigured starter by its consumer root instructions, supplied
   reusable `system/` tree, empty `instance/` and `extensions/` areas, and absence
   of canonical instance configuration and IDs. The bundle's existence does not
   mean a private instance is configured, persisted or ingested. Do not fill its
   empty areas with examples or developer trial data.
3. Resolve the parent-selected permanent Drive location. If the supplied folder
   is already the intended location, use that explicit choice. Otherwise ask
   where the configured instance should live; do not treat the sharing link as
   the location choice, account credentials or provider authorization.
4. Before creating anything, check the selected location for an existing
   School-OS entry point and configuration. If one exists, classify it as an
   existing instance, read only its relevant D1 configuration, operation
   instructions and selected adapters, and preserve it. A changed link or
   different display name is not evidence that a second instance is needed.
5. For a genuinely new instance, plan or place only the supplied reusable starter
   material at the parent-selected location at this stage. Keep the supplied
   current instructions, contracts, helpers, principles and shared mappings in
   `system`; reserve `instance` for configuration and canonical pages and
   `extensions` for household-created recipes and mappings. Do not assign an
   instance ID, create configuration or bootstrap canonical roots until the
   interview and tool-selection steps below resolve the required choices. Normal
   operations need no development plans, studies, tests or prior chat. No retired
   installer, release manifest, migration or activation engine is involved.
6. Preserve every existing explicit household choice and user-created extension.
   Ask again only when a value is missing, conflicting or the parent asks to
   change it; do not add an automatic reconfirmation gate.
7. Classify the request as new setup, configuration change or support for a new
   tool. A conformant tool mapping is compatible expansion; new canonical meaning
   or incompatible behavior still needs explicit architecture approval.

Do not inventory connectors, packages, dependencies or unrelated applications
before the interview. First learn the outcomes the parent wants; capability
inspection in step 3 is then limited to relevant routes this agent can offer.

## 2. Interview the parent

Ask in ordinary language and resolve only values that are missing or changing.
At this stage collect the parent's needs and preliminary preferences; present
the options this agent can actually see in the next step before asking for the
final tool selection.

- Where should the configured School-OS instance live, if the supplied folder is
  not already the parent's explicit permanent location?
- Which parent/guardian is configuring the instance, and which children,
  schools/classes and household timezone are in scope?
- Which logical school mailboxes and school/date scope should School-OS use?
  Keep a logical source account separate from the current connection used to
  reach it.
- Does the parent want a task application, email delivery or optional audio?
  Record the need and any preferred tool; make the final selection after showing
  the available known options. Parent fields in a selected task app follow
  approved D5 behavior. Configured audio accompanies the email; a verified audio
  failure permits email alone with a failure notice. School-OS retains no audio
  archive after verified delivery.
- Which existing parent-managed agents or jobs will use the instance? Record only
  the inputs needed by their operation configuration. D7's centralized job and
  scheduler register is outside the MVP.
- Are there privacy, school-year, sender/domain or temporary-download limits the
  configured operation must observe?

Do not ask the parent to place credentials, tokens or secrets in Drive. Those
remain in each connector's authorized credential store. Do not infer a recipient,
mailbox, child or source scope from a sample.

## 3. Offer available options and obtain the final selection

List the relevant known options the current agent can actually access or offer,
alongside any explicit existing choice and the parent's preliminary preference.
Do not make the parent guess which integrations may exist. Explain material
limits, then ask the parent for the final tool/account selection. A vendor name
is not capability evidence. Use these phrases as descriptive labels in the
conversation or setup summary, not as a persisted enum, schema or new capability
registry:

- **Parent selected:** the parent chose this tool/account/scope.
- **Available now:** the current agent declares an authorized route for the
  operation, but it has not been live-qualified by setup.
- **Previously observed:** the instance contains an attributable prior result and
  its observation time; stale evidence is not a current guarantee.
- **Unknown:** the required meaning, completeness or permission cannot be
  established from available information.
- **Unsupported:** the current route explicitly cannot perform the operation.
- **Not selected:** an option exists but the parent did not choose it.

Describe evidence for this agent's current connection because another agent's
availability can differ. This does not require a durable per-agent capability
record. Keep the adapter itself shared: never create an “Agent A adapter” and an
“Agent B adapter” for the same tool semantics. Another agent may reuse the same
mapping through its own connector if that connector supplies the mapped concepts.

Setup inspection is not, by itself, a connector probe: do not send email, mutate
a task, read private source content merely to demonstrate access, or run a
schedule. Report declared and previously observed evidence honestly. A future
installed instance may perform separately authorized qualification under the
applicable operation. Repository development follows the publication prerequisite
and exact trial scope in the active plan; these instructions do not expand it.

Do not perform broad tool discovery after the interview. Inspect only the routes
needed for requested outcomes and the selected storage destination. If a route
cannot be inspected without a live effect, present it as unknown or unsupported.

## 4. Select or prepare one shared adapter per tool

For each selected source, storage, task, delivery or audio tool:

1. Look for a supplied mapping in the installed `system` material and compatible
   user-created mappings in `extensions`, using the current entry point and
   configuration references.
2. Inspect the candidate's documented semantic coverage, limitations and
   verification method. Do not choose the first provider search result or assume
   that matching names mean matching semantics.
3. If a conformant mapping covers the selected operations, reference it from the
   existing D1 configuration so later agents can discover it.
4. If no mapping exists, follow [tool-adapters.md](tool-adapters.md) and the
   [template](tool-adapter-template.md) to author one shared tool mapping under
   user-owned `extensions`. Do not edit official `system` files to add it.
5. If the connector cannot expose the required meaning or completeness, record
   the affected operation as unknown or unsupported. A mapping cannot repair
   missing source fields, permissions, pagination evidence or readback.

Authoring a conformant mapping for a selected tool is authorized compatible
expansion. It does not authorize new provider permissions, a source-identity
fallback, a new canonical field meaning, or live effects. Surface those separately
if the requested tool cannot fit the existing School-OS semantics.

## 5. Save and hand off

The parent's setup request authorizes the configuration and canonical bootstrap
writes needed here once the parent has selected their location and missing
choices. Do not ask again for a choice or write already authorized in this setup
conversation. External account authorization remains separate, and setup still
does not authorize source ingestion, task mutation, outbound delivery or a
schedule.

For a genuinely new instance, now follow the
[storage bootstrap procedure](storage.md#bootstrap-an-instance). Preserve usable
relative references and identify the supplied published revision in the readable
entry point.

Confine every persistent write to the parent-selected School-OS root. Before a
write, resolve that root and the intended relative destination. Afterward,
establish actual parent or ancestry from the connector response or an available
read/list operation, then read the complete content back and compare it with the
intended value. Wrong or unknown placement, or mismatched content, stops
dependent setup work. Preserve the response; do not create a second copy, move
an unknown object or delete evidence merely to continue.

Assign School-OS-owned UUIDs for the instance and new Entity, Topic and Membership
records using the data contract. Keep the parent-declared household, children,
schools/classes and their dated relationships; an unknown enrollment date stays
unknown. Names and current connection handles do not become record IDs.

Save `instance_id`, `household_entity_ref`, `household_timezone`, the selected
logical `source_accounts` and `entity_topic_roots` through the approved
configuration. Include `selected_task_projection`, `selected_brief_recipes` and
`authorized_destinations` only where applicable. Each source account retains its
logical mailbox, configured school scope, import boundary and selected shared
mail mapping. Keep private container handles and connection labels in instance
configuration; never put them in a reusable mapping or this repository.

Persist only the fields, records, roots and references defined by the current
data and storage contracts. Do not add a starter status, setup receipt, installer
manifest, migration marker, release-manager state or any other new schema merely
to record that setup ran.

Create the bounded family/page directories required for the selected configuration
using the storage procedure. Read the entry point, configuration and referenced
roots back. Check instance IDs, actual values, reference targets and page bounds;
an empty directory is complete only when that empty inventory is established.
Record each Drive folder/search scope and follow every supported provider
continuation to an explicit end. Provider listing continuation and School-OS
page continuation are separate checks. If exhaustive listing is unavailable,
verify the finite required bootstrap targets through known references and report
all other inventory as unknown; a short or empty list is not exhaustion evidence.
Make every selected adapter and user-created recipe discoverable from those
references. Do not report missing roots as an empty school history.

When changing an existing instance, change only authorized configuration and
preserve data and extensions. A new default does not silently move existing task
projections to another account or create/rebind an external job. Report any
separately needed task-tool switch instead of duplicating projections.

Report to the parent:

- the selected scope and tools;
- which adapter mapping each tool uses and whether it was supplied or added by
  the household;
- the descriptive evidence for the current agent's required operations;
- every unsupported or unknown operation and its practical effect;
- any placement or listing-exhaustion limit that prevents complete setup
  verification;
- unresolved product choices that prevent a default; and
- whether only setup occurred or the parent separately authorized another
  operation to follow it.
