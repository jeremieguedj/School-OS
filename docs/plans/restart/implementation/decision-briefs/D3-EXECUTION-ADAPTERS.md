# D3 — Small helpers and shared tool guidance; the agent does the rest

**Approved MVP direction, 2026-09-15:** a School-OS agent can execute code, and the project starts with the **minimal estimated reusable routines in Python’s standard library**. The agent and its authorized tools do everything else. A recipe names the actual helper file and callable when that routine applies, so the agent uses it for repeatable mechanical work rather than recreating the rule each time. This does not choose a Python version, provider SDK, direct network route, persistent service or entire fixed adapter set. The [active plan](../../PLAN.md) records the decision; the broader [D3 proposal](../ARCHITECTURE-PROPOSAL.md#d3--runtime-adapter-contracts-and-first-supplied-routes) is historical where it asks for another language/code-boundary approval gate.

**Additional explicit approval, 2026-09-15:** setup includes an interview about the parent's task-tool choice and known options available to the current agent. A missing School-OS adapter may be authored when the selected tool is accessible. School-OS keeps **one shared semantic mapping per tool**, reusable by any capable agent with access to that tool. Each agent's connector handles APIs, authentication, SDKs and transport; the School-OS mapping is independent of that implementation. This is now recorded in the [product principles](../../../../product-principles.md#approved-setup-and-adapter-direction--2026-09-15), not a new decision awaiting approval.

All examples here are fictional written illustrations, not executed runs or qualification. No specific managed agent, provider connection, attachment reader or Drive route has been tested by this brief. User-reported code capability is the accepted prerequisite, but it does not prove the other tools that an operation needs.

## One narrow split of work

| School-OS supplies | Executing agent and authorized tools do |
|---|---|
| Readable operation recipes that identify source scope, completion/coverage checks, approved source-metadata identity rules and the relevant helper call | Discover the actual available tools/permissions; read source material; choose internal batch size and maintain its own run continuity; interpret school meaning; decide and execute authorized effects; verify outcomes |
| A setup interview and one shared School-OS semantic adapter for each supported tool | Explain available choices, establish the parent's selection, reuse the selected tool's adapter and use the current agent's connector to carry out its guidance; author a missing mapping within approved behavior when the tool is accessible |
| Small standard-library routines for repeated, deterministic transformations | Obtain the observed input fields, apply the helper only when its preconditions hold, preserve originals and unknowns, and use provider-specific access aids only to retrieve data |
| Approved D1 bounded JSON pages and directory shape; D5 claim/task meanings; separate coverage obligations | Save source-linked knowledge, canonical tasks and coverage on Drive; verify ordinary successful saving before temporary raw cleanup; report incomplete or unsupported work honestly |

The project is **not** a resident application that orchestrates every provider. It provides small reliable operations and instructions; the agent conducts the task. D4 now requires one logical ingestion run to complete relevant School-OS-pending mail, with the agent choosing its own paging/resources. D6 makes the executing agent validate uncertain external effects through its authorized connectors or APIs. D5’s source-supported claims, finite/recurring tasks and parent-state separation are approved, rather than a new D3 code boundary to approve again. D2 interrupted canonical-write repair, D7 centralized job/register machinery and D8 packaging/upgrades are outside this MVP.

## Setup starts with the parent's tool choice

The [operation guide](../../../../../operations/README.md) and [setup instructions](../../../../../operations/setup.md) make the first-use flow explicit. The agent asks what task application the parent wants, explains known options that it can actually access, and establishes the relevant account or task scope. It does not assume that every named tool is connected or select a preferred vendor without the parent's choice. A tool the parent already uses can be a sensible option when the current agent has the required authorized access.

If shared guidance already exists for that tool, the agent reads and reuses it. If it does not, the [tool-adapter instructions](../../../../../operations/tool-adapters.md) and [adapter template](../../../../../operations/tool-adapter-template.md) guide authoring a missing mapping. Access to the tool makes that work possible; it does not prove every needed feature is supported. The agent preserves approved meanings, states unsupported behavior and seeks approval only for a genuinely new architectural decision. It need not ask again to adopt the already approved D5 task behavior or this reuse model.

For example, a fictional parent chooses the task app already available to their agent. The School-OS guidance explains where the parent's planned date belongs, how it stays distinct from the school deadline, how the owned School-OS task ID is carried, and how parent completion returns to Drive through approved three-way reconciliation. These meanings remain the same if the parent later uses a different agent to access that same task app. A particular field, recurrence feature or readback route cannot be claimed supported until the available tool route establishes it.

## Shared meaning is separate from tool access

Read the following flow from top to bottom:

```text
School-OS meaning: source-supported tasks and separate parent decisions
        ↓
Shared adapter for the chosen tool: map those meanings to its concepts
        ↓
Current agent: follow the recipe and mapping; assess access and results
        ↓
That agent's connector: API calls, authentication, SDK and transport
        ↓
Selected task tool: the actual entry, edit or observed result
```

The **School-OS adapter** answers “what does this field or action mean for School-OS in this tool?” The **connector** answers “how can this agent read or change it?” A replacement agent can use a different connector while following the same shared mapping. School-OS does not need a second semantic adapter merely because the connector's API spelling or authentication method differs.

Provider handles can help the connector locate the current entry. They do not replace the owned School-OS task identity or prove that an action succeeded. The agent still verifies the actual relevant result through its authorized means and exposes uncertainty. If its connector lacks a required operation, a shared mapping cannot create that capability; the affected work remains unsupported or incomplete through that route.

Older architecture documents sometimes called a provider/API wrapper an “adapter.” That is not the School-OS deliverable selected here. The reusable deliverable is readable semantic guidance; tool access belongs to the agent's connector. The shared instructions and template are authored project material, not a central capability register, installation framework, persisted schema or qualified vendor adapter. Their existence does not complete the remaining ingestion, task, query or brief implementation.

## What the first helpers are for

A small [source_metadata.py](../../../../../helpers/source_metadata.py) helper is authored as **unexecuted implementation material**, not a qualified installed runtime. Its pure callables are:

| Callable | Narrow responsibility | What it cannot decide |
|---|---|---|
| `normalize_subject` | With known raw-header versus decoded representation, normalize subject presentation without double decoding; trim outer whitespace and preserve meaningful text | Whether two email bodies are equal, or whether a subject alone identifies an email |
| `normalize_address_parts` | Normalize **already reliably extracted** local/domain address parts under the approved rule, preserving local-part spelling | Extract a trustworthy address from every arbitrary connector display string or infer missing To/Cc roles |
| `utf8_size` | Measure a text value’s encoded UTF-8 size to support D1’s bounded JSON-page work | Truncate substantive material, choose a whole-history limit, or certify a provider transfer route |

The [helper guide](../../../../../helpers/README.md) and [agent guidance](../AGENT-EXECUTION-GUIDANCE.md#use-the-actual-helper-when-it-applies) name the file, callables and input limits. For instance: “If the source route has supplied reliable sender local and domain parts supported by the helper, use `normalize_address_parts`.” If a helper is unavailable or does not cover an input, the agent can use an available tool or follow the same approved procedure. A helper's limited coverage does not redefine canonical identity or make the whole operation unsupported. Preserve unresolved observations instead of inventing evidence when neither route can establish the required meaning.

These are local function interfaces, not a persisted record schema, tool semantic mapping or connector implementation. The code and its prepared checks have not been executed, tested or installed. Further helpers should be added only when repeated work justifies them under approved behavior.

## A fictional school email through the split

> From: Cedar School Office (office@example.org)
>
> Subject: Museum permission
>
> Original Date: 15 Sep 2031 09:14:27 −0700
>
> Return Robin’s permission slip by September 19 at 17:00. Bring a packed lunch unless Robin receives a school meal.

The agent reads its authorized mailbox using whatever conformant source route is actually available. A connector supplies observed metadata, including the original Date with its stated meaning, zone and precision. The agent uses the applicable subject/address helper on **well-formed observed inputs**; the helper does not invent a missing Date or decide logical-email identity by itself. The approved metadata-only recipe governs association, while D4’s exact automatic threshold remains pending. The agent then temporarily reads the content, preserves the meal exception and deadline as source-supported information under approved D5, saves coverage separately, verifies normal persistence and discards accessible temporary raw copies. A parent could receive a source-linked answer, but this written sequence does not prove any connector can perform it.

The agent does not require Python to decide whether a later school email cancels the visit or changes only the departure time. That is source-grounded semantic reasoning under D5. Nor does the helper select a permanent provider ID, source-message body hash or thread grouping as identity evidence. If original metadata is incomplete, the association or affected coverage remains explicit instead of becoming a fabricated success.

## Remaining scope and limits

Actual connector routes still need to expose the required operations and meanings: Drive bounded list/read/write and ordinary readback; individual source metadata, content and attachments; task snapshot/apply/readback where configured; and email/audio output where selected. A Gmail, Todoist, Sheets or ElevenLabs name is not a compatibility guarantee. This brief does **not** approve shipping every previously listed vendor adapter, making direct network calls from Python, or requiring a particular SDK or credential arrangement. The approved shared mapping can be reused through the agent’s existing authorized connector. Connector envelope conflicts, unknown capability and missing transport responses cannot be normalized into invented success.

There is no separate language or code-versus-agent boundary approval to request for the minimal helper direction just chosen. New canonical meanings, incompatible adapter contracts or materially different runtime dependencies still require explicit approval under the [product decision authority](../../../../product-principles.md#decision-authority). There is also no standalone record/write-framework gate: the user excluded that deliverable from MVP, as explained in the [records note](RECORDS-AND-NORMAL-WRITES.md). Saving and verification still happen. No tests, scripts, connector probes, builds or live operations are authorized here.
