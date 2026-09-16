# School-OS operations

These are reusable instructions for agents operating a School-OS instance. They
are authored guidance, not evidence that any connector, tool or provider route
has been qualified.

For an existing instance, begin from its readable Drive entry point and selected
configuration. For first setup, use the supplied School-OS materials and the
parent-selected Drive location, check for an existing instance, then create the
approved D1 bootstrap and areas only when none exists. Follow the
[product principles](../docs/product-principles.md),
the approved [metadata identity recipe](../docs/plans/restart/identity/METADATA-RECIPE.md)
and the installed operation that matches the parent's request. A capable agent
uses the actual small helper named by a recipe when it applies; see the
[helper guide](../helpers/README.md). The agent and its authorized tools perform
the rest of the operation.

## Start here

- [First setup](setup.md): interview the parent, record the selected scope and
  inspect the current agent's available tools.
- [Tool adapters](tool-adapters.md): select an existing shared semantic mapping
  or author a missing conformant mapping for one tool.
- [Tool-adapter template](tool-adapter-template.md): the generic headings and
  questions a new mapping should answer.
- [Completion review](completion-review.md): preserve clear completion evidence,
  ask the parent to confirm it, and synchronize confirmed completion under D5.
- [Brief recipes](brief-recipes.md): create, select and use parent-chosen brief
  formats without changing source truth, coverage or task meanings.

## Operating boundary

A **tool-semantic adapter** explains how one tool's concepts and observable
results map to School-OS operations. It is shared by every capable agent and
connector that reaches that tool. It does not contain credentials, make API or
SDK calls, own transport, or fork for a particular agent. The connector remains
responsible for authentication, API/SDK access, transport and its provider
envelope.

Supplied School-OS operation material and supplied adapters belong with official
materials in D1's `system` area. A parent or agent's compatible addition belongs
under its declared ownership in `extensions`. The instance's existing readable
entry point and D1 configuration make the selected adapter discoverable; these
instructions create no new registry, mandatory filename, precedence rule,
identifier format, schema or Drive area.

An adapter cannot make a connector reveal information or perform an operation it
does not support. Keep unsupported, unavailable and unknown behavior explicit.
Do not infer capability from an agent or vendor name, and do not treat a generic
error as success, authorization failure, rate limiting or a safe retry.

The parent may use several agents and tools, but simultaneous updates to the same
canonical Drive data remain outside scope. No operation here creates a central
job manager, scheduler, package installer, provider SDK or persistence framework.
All execution and live qualification remain subject to the repository's testing
and authorization boundaries.

[Prepared review cases](prepared-review-cases.md) contain fictional inputs and
expected outcomes for later user-directed testing. They have not been run.
