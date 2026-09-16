# D3 — How the agent, code and connected tools work together

Status: **code-execution capability approved; the choices below remain proposals.** This brief explains the [current D3 proposal](../ARCHITECTURE-PROPOSAL.md#d3--runtime-adapter-contracts-and-first-supplied-routes). All messages and results here are fictional written examples, not executed simulations or qualification evidence.

## What you have already decided

A School-OS agent must be able to execute code. You have confirmed that capability with major personal-agent suppliers. We accept that as the basis for the requirement; we have not run supplier probes or qualified specific integrations.

That lets the project use small programs for repeatable mechanical work. It does not select Python, a particular SDK, or a permanent server. The agent can run code in its temporary managed environment. The canonical information remains on Drive when that environment disappears.

## The remaining proposal in ordinary language

Give the agent three complementary things:

1. **An operation recipe:** readable instructions for the task, what it may read/change, and when it may call something complete.
2. **Small callable code:** mechanical operations such as normalizing addresses, comparing allowed metadata, preparing a bounded JSON page, or selecting a directory page.
3. **Adapters:** a thin translation between School-OS requests and the tools available in this particular agent environment.

Under the approved D4 direction, the executing agent also owns resource use,
internal batching and continuation until its logical run is complete; the project
provides advice rather than a batch controller. The agent still reads school
information and reasons about meaning. A program can normalize a date reliably; that does not mean a date parser can decide whether a school email cancels a trip or merely corrects the departure time. D5 covers those meanings.

The candidate implementation language is Python using its standard library. That language/dependency choice remains unapproved. The optional in-memory development model already in the repository is preparation, not a decision that Python must be the installed runtime.

## A fictional email moving through the system

> From: Cedar School Office <office@example.org>
>
> To: Alex Vale <alex@example.org>
>
> Subject: Museum visit — permission required
>
> Original Date: 15 Sep 2031 09:14:27 -0700
>
> Please return Robin's permission slip by September 19 at 17:00. Bring a packed lunch on the visit. If Robin is not attending, reply to the office instead.

Assume the agent is authorized to process this mailbox and the relevant metadata/content routes are available. The proposed flow is:

| Step | Who does it | What happens |
|---|---|---|
| 1 | Agent following the recipe | Reads the installed operation, configuration and the relevant saved scope on Drive. |
| 2 | Source adapter | Asks the selected mailbox tool for individual original metadata and reports the fields actually exposed. |
| 3 | Small code routine | Normalizes address presentation and date representation while preserving originals and uncertainty. |
| 4 | Agent + approved identity procedure | Uses allowed metadata to associate the email. It does not use the body to establish identity. D4's exact sufficiency threshold is still pending. |
| 5 | Source adapter and agent | Obtains the content temporarily; the agent extracts the deadline, lunch instruction and alternative reply condition. |
| 6 | Record preparation code + agent | Prepares the intended knowledge/task/coverage values. Their minimum schema and normal-write contract still need approval. |
| 7 | Drive adapter | Performs authorized writes and readback according to that eventual contract. |
| 8 | Agent following the recipe | Reports supported results and remaining gaps; removes accessible temporary raw copies after verified persistence. |

An illustrative parent-facing result is: “The permission response is due September 19 at 17:00. Robin needs a packed lunch; if not attending, reply to the school instead.” The source link and metadata support that answer. This example does not prove an installed adapter can perform the steps.

## What an adapter actually changes

Imagine one tool calls the sender field `from`, while another places the sender in a nested result. School-OS should not require every operation recipe to understand both envelopes. The adapter exposes the same agreed meaning: the observed original sender, whether it was supplied, and any relevant uncertainty.

The labels in this illustration are conceptual, not an approved JSON schema:

| Adapter reports | Why it matters |
|---|---|
| Original Date, including its meaning and precision | A result-list timestamp might mean something else. |
| Inventory scope | Two returned attachments do not establish that only two exist. |
| More results available | A short page can still have a continuation. |
| Content unread or unsupported | Metadata access does not establish that an image was read. |
| Write outcome unknown | Losing the response is not proof of success or failure. |

If a wrapper supplies two contradictory versions of a declared value, the adapter must not silently choose one. It reports the boundary problem. Connector display fields and provider handles are not canonical identity.

## Two agents can execute code and still differ

**Agent Pine** can execute the selected language and use a connected mailbox reader. Its code environment cannot make direct network requests. **Agent Birch** can execute code and has a different mailbox connection. Neither description establishes all required School-OS capabilities.

One candidate design lets the agent call its authorized native tool, then pass the returned data to small code routines. Another calls the provider directly from code through an SDK. The first reduces direct authentication and networking assumptions; the second can make some repeated operations more uniform but introduces network, credential and dependency requirements.

The current recommendation favors small code plus replaceable adapters and existing authorized tool access. The precise boundary between native calls and executable adapter code must be approved for each supported route; code execution alone does not settle it.

If a connection can list subject lines but cannot expose individual original Dates, the installation must describe that limitation. It cannot invent missing fields because the supplier confirmed code execution. It also must not require the parent to keep a laptop running as a workaround.

## Which integrations are currently proposed?

| Area | Candidate supplied route | What remains uncertain |
|---|---|---|
| Canonical storage | Drive JSON files | Bounded file reads/writes/listing and readback behavior. |
| Email source and delivery | Gmail | Individual metadata, attachment access, listing semantics and delivery evidence. |
| Task application | Google Sheets and Todoist projections | Stable School-OS marker storage, supported parent fields and readback. |
| Scheduling | Deferred from the MVP under D7 | Users and agents own their jobs; no School-OS scheduler contract/controller is required. |
| Runtime profiles | ChatGPT Work and Claude managed environments as initial examples | Exact operation mapping for each execution surface. |
| Optional audio | ElevenLabs | Generation, artifact retrieval, authorized delivery and outcome evidence. |

The retained integration rows are a proposed starting set, not a closed vendor list or a compatibility certificate. D7 scheduler management and D8 package machinery are deferred, not prerequisites. Unknown capable agents and conformant extensions remain possible. Requiring both task adapters initially versus selecting one affects delivery scope and still needs a decision.

## Implications, alternatives and unknowns

| Choice | Practical implication | Credible alternative |
|---|---|---|
| Small standard-library Python routines | Simple package and few code dependencies, if target environments support the selected version. | JavaScript or another commonly supported language; requires a concrete portability/packaging decision. |
| Agent recipes plus mechanical code | The agent handles source meaning; code handles repeatable transformations. | A larger application runtime that orchestrates more of the operation; more dependency and integration surface. |
| Use existing authorized connections through adapters | Credentials stay in their authorized stores and providers remain replaceable. | Direct provider SDKs from code; more uniform low-level APIs, but new networking/authentication/library requirements. |
| Preserve incomplete results explicitly | A missing capability limits the affected operation without becoming an invented success. | Requiring the entire proposed integration set before any use; simpler admission, but less useful supported operation. |

These choices serve repeatable behavior, simplicity, bounded execution, tool independence and managed-agent portability. Actual execution limits, installed languages, file access, network access and adapter fidelity remain for the user-directed qualification phase. No tests have run.

## Decisions still needed

- Which language and dependency policy should the shipped code use? Current candidate: small Python standard-library routines.
- Which steps belong in code, and which remain agent/tool operations? Approve the concrete callable contracts before dependent implementation.
- Which initial provider/runtime routes should ship, and what explicitly limited operation is acceptable when a capability is missing?
- How will these routines use the minimum record and ordinary-write contract after D2's recovery deferral? That dependency remains undecided.

The requirement that agents can execute code is settled. These implementation contracts are not.
