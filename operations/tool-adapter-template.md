# Tool-semantic adapter — writing template

Use these headings to describe one tool's mapping to existing School-OS
semantics. Replace bracketed guidance with concise factual text. This template
does not prescribe a filename, persisted schema, identifier, code generator,
provider API, connector implementation or Drive registry.

## Purpose and ownership

- **Tool and parent-facing purpose:** [What tool is being mapped and for which
  School-OS operations?]
- **Ownership:** [Supplied School-OS material in `system`, or a named
  household/user extension in `extensions`.]
- **Scope:** [Concepts covered. State explicitly what is not covered.]
- **Authority:** [Approved School-OS meanings this mapping preserves.]

Do not put credentials, household source content, private account references or
connector request examples in the reusable mapping.

## Concept map

For each concept required by the selected operation, document:

| School-OS concept | Tool meaning/observation | Required distinctions and unknowns |
|---|---|---|
| [Example: individual source message] | [Tool concept that represents it] | [Original versus received/observed time; thread summary is not message coverage] |
| [Example: attachment candidate] | [Tool-observed candidate] | [Original filename provenance, repeated names, inventory completeness] |
| [Example: canonical task projection] | [Tool task concept] | [School action/deadline versus parent plan/completion; School-OS identity support] |

Add only rows the tool supports. Do not invent a field to make the table look
complete.

## Read and list semantics

Describe:

- the observable scope of a read or listing;
- how another page and listing exhaustion are represented;
- which values are original observations versus connector display metadata;
- how missing, explicit empty, partial and unavailable values differ; and
- what evidence is needed before School-OS may call the read complete.

If a connector may silently cap or summarize results, mark complete enumeration
unsupported unless another authorized route supplies exhaustion evidence.

## Update semantics

For each supported update, describe the intended tool-visible change and the
School-OS meaning that must remain unchanged. Include allowed parent-editable
fields where relevant. State how missing targets, conflicting edits, deletion and
unsupported fields are represented.

The adapter describes semantics; the connector performs the authorized request.
Do not embed credentials, SDK calls, retry loops or an agent-specific workflow.

### Completion review mapping

When the tool projects School-OS tasks, describe how it can present
**Completion detected — awaiting parent confirmation** without marking the task
complete. Map this meaning to a suitable dedicated native status or review
section, depending on the tool’s capabilities and chosen mapping. Preserve
the task’s identity and parent-editable fields. Also describe how the parent marks the projected task complete and how
the connector can read that choice for the next D5 three-way synchronization.

Do not map the pending-confirmation meaning to the tool's completed state. Do
not invent fallback labels, tags, custom fields, identifiers or permissions. If
neither a suitable status nor section is available, mark the projection
unsupported: School-OS keeps the pending review in Drive and reports the tool
gap. This table is a semantic mapping, not a requirement for a connector wrapper
or a new canonical task-state schema.

## Verification semantics

Describe what authorized tool read can verify after an update, send or generation:

- the relevant target and scope of the verification read;
- which intended values must agree;
- what the observation proves and does not prove; and
- visibility delay, partial search or missing-marker limitations.

A generic success response, provider receipt, empty search or missing transport
response is not automatically canonical verification. The executing agent uses
available evidence and does not blindly repeat an unknown external effect.

## Connector boundary

State the concepts a connector must supply to use this mapping. Authentication,
permissions, API/SDK behavior, transport, pagination tokens and provider envelope
handling remain connector responsibilities. The agent interprets the actual
connector result through this mapping; no mandatory wrapper or projection code
is implied. Describe current capability evidence in the setup report, or in
existing configuration only where that configuration already calls for it. Do
not create a per-agent record requirement or fork this adapter for each agent.

## Unsupported, unknown and failure behavior

List every known semantic gap. Distinguish:

- **unsupported:** the route explicitly lacks the operation or meaning;
- **unknown:** available information cannot establish it;
- **incomplete:** some observed scope or content remains; and
- **conflict:** two comparable observed values disagree.

Say how the agent reports the affected operation without fabricating completion.
Do not infer throttling, authorization failure, timeout or applied effect from a
generic connector error.

## Reuse and discovery

Explain how the existing readable entry point and D1 configuration refer to this
shared mapping so another capable agent can find it. Name no new registry or
precedence rule. If another mapping conflicts, require explicit resolution rather
than first-match selection.

## Qualification status

State the source of each claim: supplied documentation, parent selection,
declared connector capability or separately authorized observed evidence. Record
the observation time where relevant. Clearly say that authoring this mapping is
not live qualification and does not authorize a probe, source read or effect.
