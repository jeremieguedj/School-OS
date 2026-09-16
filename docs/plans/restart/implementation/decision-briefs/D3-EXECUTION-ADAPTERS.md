# D3 — Small Python helpers; the agent does the rest

**Approved MVP direction, 2026-09-15:** a School-OS agent can execute code, and the project starts with the **minimal estimated reusable routines in Python’s standard library**. The agent and its authorized tools do everything else. A recipe names the actual helper file and callable when that routine applies, so the agent uses it for repeatable mechanical work rather than recreating the rule each time. This does not choose a Python version, provider SDK, direct network route, persistent service or entire fixed adapter set. The [active plan](../../PLAN.md) records the decision; the broader [D3 proposal](../ARCHITECTURE-PROPOSAL.md#d3--runtime-adapter-contracts-and-first-supplied-routes) is historical where it asks for another language/code-boundary approval gate.

All examples here are fictional written illustrations, not executed runs or qualification. No specific managed agent, provider connection, attachment reader or Drive route has been tested by this brief. User-reported code capability is the accepted prerequisite, but it does not prove the other tools that an operation needs.

## One narrow split of work

| School-OS supplies | Executing agent and authorized tools do |
|---|---|
| Readable operation recipes that identify source scope, completion/coverage checks, approved source-metadata identity rules and the relevant helper call | Discover the actual available tools/permissions; read source material; choose internal batch size and maintain its own run continuity; interpret school meaning; decide and execute authorized effects; verify outcomes |
| Small standard-library routines for repeated, deterministic transformations | Obtain the observed input fields, apply the helper only when its preconditions hold, preserve originals and unknowns, and use provider-specific access aids only to retrieve data |
| Approved D1 bounded JSON pages and directory shape; D5 claim/task meanings; separate coverage obligations | Save source-linked knowledge, canonical tasks and coverage on Drive; verify ordinary successful saving before temporary raw cleanup; report incomplete or unsupported work honestly |

The project is **not** a resident application that orchestrates every provider. It provides small reliable operations and instructions; the agent conducts the task. D4 now requires one logical ingestion run to complete relevant School-OS-pending mail, with the agent choosing its own paging/resources. D6 makes the executing agent validate uncertain external effects through its authorized connectors or APIs. D5’s source-supported claims, finite/recurring tasks and parent-state separation are approved, rather than a new D3 code boundary to approve again. D2 interrupted canonical-write repair, D7 centralized job/register machinery and D8 packaging/upgrades are outside this MVP.

## What the first helpers are for

A small [source_metadata.py](../../../../../helpers/source_metadata.py) helper is authored as **unexecuted implementation material**, not a qualified installed runtime. Its pure callables are:

| Callable | Narrow responsibility | What it cannot decide |
|---|---|---|
| `normalize_subject` | With known raw-header versus decoded representation, normalize subject presentation without double decoding; trim outer whitespace and preserve meaningful text | Whether two email bodies are equal, or whether a subject alone identifies an email |
| `normalize_address_parts` | Normalize **already reliably extracted** local/domain address parts under the approved rule, preserving local-part spelling | Extract a trustworthy address from every arbitrary connector display string or infer missing To/Cc roles |
| `utf8_size` | Measure a text value’s encoded UTF-8 size to support D1’s bounded JSON-page work | Truncate substantive material, choose a whole-history limit, or certify a provider transfer route |

The [helper guide](../../../../../helpers/README.md) and [agent guidance](../AGENT-EXECUTION-GUIDANCE.md#use-the-actual-helper-when-it-applies) name the file, callables and input limits. For instance: “If the source route has supplied reliable sender local and domain parts supported by the helper, use `normalize_address_parts`.” If a helper is unavailable or does not cover an input, the agent can use an available tool or follow the same approved procedure. A helper's limited coverage does not redefine canonical identity or make the whole operation unsupported. Preserve unresolved observations instead of inventing evidence when neither route can establish the required meaning.

These are local function interfaces, not a persisted record schema or provider adapter contract. The code and its prepared checks have not been executed, tested or installed. Further helpers should be added only when repeated work justifies them under approved behavior.

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

Actual provider routes still need to expose the required operations and meanings: Drive bounded list/read/write and ordinary readback; individual source metadata, content and attachments; task snapshot/apply/readback where configured; and email/audio output where selected. A Gmail, Todoist, Sheets or ElevenLabs name is not a compatibility guarantee. This brief does **not** approve shipping every previously listed adapter, making direct network calls from Python, or requiring a particular SDK or credential arrangement. A route can use the agent’s existing authorized connector when that is the available means. Connector envelope conflicts, unknown capability and missing transport responses cannot be normalized into invented success.

There is no separate language or code-versus-agent boundary approval to request for the minimal helper direction just chosen. New canonical meanings, incompatible adapter contracts or materially different runtime dependencies still require explicit approval under the [product decision authority](../../../../product-principles.md#decision-authority). There is also no standalone record/write-framework gate: the user excluded that deliverable from MVP, as explained in the [records note](RECORDS-AND-NORMAL-WRITES.md). Saving and verification still happen. No tests, scripts, connector probes, builds or live operations are authorized here.
