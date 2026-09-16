# First setup

Use this operation when a parent is starting an instance or selecting tools for
an existing instance. The outcome is a parent-approved configuration plus shared,
discoverable tool-semantic mappings for the selected tools. Setup does not prove
that live operations work or create a School-OS scheduler. Setup alone does not
authorize ingestion, sending or task updates. If the parent explicitly requests
an import or another operation at the same time, finish setup and then select and
run that separately authorized operation under its own instructions.

## 1. Establish whether the instance is new or existing

1. Ask for the parent-selected Drive location and the supplied School-OS
   materials. Do not assume a new instance already has a readable entry point.
2. Check the selected location for an existing School-OS entry point and instance
   before creating anything. If one exists, read only its relevant D1
   configuration, operation instructions and selected adapters.
3. For a genuinely new instance, use the supplied School-OS materials to create
   the approved D1 bootstrap and `system`, `instance` and `extensions` areas at
   the parent-selected location. Save the minimum setup configuration and verify
   ordinary readback before presenting the instance as ready.
4. Preserve every existing explicit household choice and user-created extension.
   Ask again only when a value is missing, conflicting or the parent asks to
   change it; do not add an automatic reconfirmation gate.
5. Classify the request as new setup, configuration change or support for a new
   tool. A conformant tool mapping is compatible expansion; new canonical meaning
   or incompatible behavior still needs explicit architecture approval.

## 2. Interview the parent

Ask in ordinary language and resolve only values that are missing or changing.
At this stage collect the parent's needs and preliminary preferences; present
the options this agent can actually see in the next step before asking for the
final tool selection.

- Which parent/guardian is configuring the instance, and which children,
  schools/classes and household timezone are in scope?
- Which logical school mailboxes and school/date scope should School-OS use?
  Keep a logical source account separate from the current connection used to
  reach it.
- Does the parent want a task application, email delivery or optional audio?
  Record the need and any preferred tool; make the final selection after showing
  the available known options. Parent fields in a selected task app follow
  approved D5 behavior. Audio selection, ordering and retention follow an
  approved configuration when one exists; do not invent an unresolved default.
- Which existing parent-managed agents or jobs will use the instance? Record only
  the inputs needed by their operation configuration. D7's centralized job and
  scheduler register is outside the MVP.
- Are there privacy, school-year, sender/domain or temporary-download limits the
  configured operation must observe?

Do not ask the parent to place credentials, tokens or secrets in Drive. Those
remain in each connector's authorized credential store. Do not infer a recipient,
mailbox, child or source scope from a sample.

## 3. Offer available options and obtain the final selection

Offer relevant known options the current agent can see, alongside any explicit
existing choice and the parent's preliminary preference. Explain material limits,
then ask the parent for the final tool/account selection. A vendor name is not
capability evidence. Use these phrases as descriptive labels in the conversation
or setup summary, not as a persisted enum, schema or new capability registry:

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
applicable operation. During current repository development, all such execution
remains stopped until the user's testing direction.

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

Save the confirmed household/source/output choices in the existing D1 instance
configuration and make each selected adapter discoverable from that configuration
and the readable entry point. Save user-authored mappings with their extension
ownership. Use ordinary agent readback to confirm the values saved before calling
setup complete. This is normal verification, not a new write framework.

Report to the parent:

- the selected scope and tools;
- which adapter mapping each tool uses and whether it was supplied or added by
  the household;
- the descriptive evidence for the current agent's required operations;
- every unsupported or unknown operation and its practical effect;
- unresolved product choices that prevent a default; and
- whether only setup occurred or the parent separately authorized another
  operation to follow it.
