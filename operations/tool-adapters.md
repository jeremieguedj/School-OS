# Shared tool-semantic adapters

Use this operation to select, inspect or author the semantic mapping for a tool
used by School-OS. One tool has one shared semantic adapter for the meanings it
supports. Agents may reach that tool through different connectors, but they do
not fork its School-OS semantics by agent, connector SDK or transport envelope.

The [supplied mapping catalogue](../adapters/README.md) includes Drive, Gmail,
Google Sheets, Todoist and optional ElevenLabs. These are operating documents,
not connector implementations or evidence of live compatibility. Task operations
use [task-sync.md](task-sync.md) and [the data contract](../contracts/data.md).

## What the adapter owns

The adapter maps School-OS concepts to the tool's stable, user-visible or
documented meanings. Depending on the tool, this can include:

- what constitutes one source item, individual message, attachment candidate,
  task, sent output or generated artifact;
- which observed fields preserve original meaning, timezone, precision, roles,
  inventory scope and uncertainty;
- how listing continuation and exhaustion are represented;
- which parent-editable task fields can be read and updated under approved D5;
- how a task awaiting parent confirmation appears as a dedicated tool status or
  review section without becoming completed;
- what readback can establish about a requested update or send; and
- which semantics are unavailable, partial, delayed or unknown.

The adapter must project only supported observations into School-OS meanings.
Conflicting duplicate representations remain a boundary error, not a value to
choose silently. Optional provider handles may help retrieve the current target,
but cannot become canonical email/attachment identity or substitute for a
School-OS task identity.

## What stays with the connector and agent

The connector handles authentication, authorization, API/SDK calls, request
construction, transport, pagination tokens and provider envelopes. The adapter
does not store credentials or require one SDK. The executing agent selects its
authorized connector, applies the shared mapping, follows continuations, reasons
over school meaning, saves canonical data and validates results through available
authorized reads.

The agent interprets the actual connector result through the shared semantic
mapping. This does not require a new wrapper, projection module or code layer,
and it is not permission to create different canonical meanings for each agent.
If two connectors expose different capabilities, describe the supported,
unknown or unsupported operations for the current route while keeping the tool
adapter's meaning unchanged.

For completion review, the shared adapter must distinguish three meanings:
ordinary open work, **Completion detected — awaiting parent confirmation**, and
parent-confirmed completion. Use a dedicated native status or review section for the middle state,
depending on the tool’s capabilities and chosen mapping, while preserving the
task and its identity. A checked or completed
tool task means parent confirmation only when the configured D5 mapping and
readback establish that parent edit. If the tool supports neither status nor
section, preserve the pending state in canonical Drive data and report the gap.
Do not improvise a label, custom field or broader permission.

Also preserve explicit parent rejection through
`parent_state.completion_reviews`. Reusing the same source evidence must not
reopen a rejected review. State which observed parent action communicates
confirmation or rejection; moving a task or an absent status alone is not an
unambiguous rejection unless the selected mapping explicitly establishes it.

## Reuse an existing mapping

1. Read the operation's required concepts and the parent-selected tool.
2. Locate candidate supplied or extension mappings through the instance's
   readable entry point and existing D1 configuration.
3. Confirm that the mapping describes the required read, update and verification
   semantics and states its unsupported areas.
4. Confirm that this agent's connector can actually supply the mapped inputs and
   operations. Declared availability is not live qualification.
5. Reference the selected shared mapping from existing configuration. Do not
   copy it into an agent-named fork.

If several mappings conflict, stop and surface the conflict. These instructions
do not define mandatory filenames, identifiers, a precedence order or a new
registry that would automatically select one.

## Author a missing mapping

Use [tool-adapter-template.md](tool-adapter-template.md) as a writing guide.
Describe only semantics supported by trustworthy tool information available to
the agent. Keep the mapping implementation/API agnostic: name the concept and
the evidence the tool exposes, not hard-coded request syntax, credentials or a
single connector envelope.

Save a user-authored mapping under its declared `extensions` ownership and make
it discoverable through the existing configuration. A supplied official mapping
belongs with `system` materials and is changed only through the official project,
not by private setup. Preserve private provider/account details in instance
configuration or authorized credential stores, not in a reusable adapter.

Creating a mapping is authorized only where it preserves approved School-OS
meanings. Ask for architecture review before redefining identity, completeness,
task semantics, source custody, external-effect meaning or another invariant.
Do not use bodies, hashes, provider IDs or connector metadata to repair ambiguous
email/attachment identity. Do not title-match a task when its School-OS identity
is missing.

## Completion and limitations

A mapping is ready for later use when another capable agent can read it and
understand:

- the operations and concepts it covers;
- the observed inputs and their meanings;
- how completeness and verification are established;
- what remains unsupported or unknown; and
- which parts belong to the connector rather than the mapping.

For a task tool, this also includes the pending-confirmation presentation, the
parent completion action and the readback that can establish that action. See
[completion-review.md](completion-review.md) for the operating procedure.

This documentation result is not live qualification. An unknown connector may
fail to expose required concepts, complete listing or readback even when a sound
tool mapping exists. Leave the affected operation unsupported or unknown until
an authorized route can establish it; never promise that an adapter can fix the
connector.
