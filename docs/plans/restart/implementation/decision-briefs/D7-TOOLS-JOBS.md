# D7 — Tools, connections, agents and scheduled jobs

Status: explanatory proposal, 2026-09-15. D7 is **not approved**. The
[active plan](../../PLAN.md) is the approval ledger; the
[D7 proposal](../ARCHITECTURE-PROPOSAL.md#d7--register-capability-discovery-and-schedules)
is the starting recommendation. All examples below are invented descriptions,
not executed scenarios or observations of a supplier's service.

The intended result is straightforward: a parent or a replacement agent can
find out what School-OS is configured to do, where each job is managed, which
accounts it uses, and who produced a particular brief. Reading that register
does not give the reader control of every external service.

## The different things being recorded

Consider a fictional household receiving this school email:

> Juniper School — Autumn trip permission
> Please return the permission form by 18 September. Bring a packed lunch.

The household wants a morning cataloging job and an evening email brief. These
terms describe different parts of that arrangement:

| Term | Meaning in the example |
|---|---|
| Tool | An available operation, such as reading an email, writing a Drive file or listing a scheduler's jobs. |
| Source account | The parent's logical school mailbox. It remains the same mailbox when the parent reconnects it through another agent. |
| Connection | The current authorized access to an account or service inside an agent application. Its credentials remain in that application's authorized store. |
| Adapter | School-OS instructions/code translating its required operations into the tools exposed by a particular connection. A Gmail adapter is not the mailbox itself. |
| Agent/runtime | The actor and execution environment doing the work, such as the household's morning managed agent. |
| Job | The durable description of recurring work: purpose, schedule, agent, selected connections/adapters, scope and destination. |
| Run | One attempt to perform that job, such as the morning attempt on 16 September. |
| Output | A result of a run, such as an email brief or audio artifact, with its generating agent and sending service recorded. |

The ability to execute code is already required. The user's report that personal
agent suppliers support it is not independent evidence that any particular
connection can read school attachments, write Drive data or send unattended.

## What is already decided, and what D7 adds

The [product principles](../../../../product-principles.md) already require a
Drive register, unrestricted agent/job counts, operation-specific selections,
management locations, verification freshness and output attribution. D1 already
supplies bounded Drive pages. D7 proposes how capability discovery and scheduler
management use those foundations. Exact record fields, adapter contracts and
ordinary-write behavior still need their remaining approvals.

Recommend distinguishing declared capability from observed capability for the
actual agent, adapter and connection combination. For example:

| Register observation | What the parent may conclude |
|---|---|
| Agent exposes a send-email tool | A possible delivery route exists. |
| A particular account previously sent a verified brief | That combination worked at the recorded time. |
| Scheduler launches an agent | Launch worked; unattended Drive writes or email sending are not thereby established. |
| Another agent can read the register | It can explain known jobs, even without permission to edit their schedulers. |

Capability discovery begins with available tool descriptions and configured
connections. Qualification of actual effects belongs to later user-directed
testing. Unknown capability remains unknown.

## A proposed successful setup and run

The parent requests: “Catalog school mail each morning and send the evening
brief to my chosen address.” The following is the proposed flow after the
relevant architecture and operation authorizations exist:

1. The agent reads the Drive bootstrap, relevant configuration and known jobs.
   It checks whether this work is already registered before proposing another
   schedule.
2. It identifies the source mailbox, Drive connection, delivery account and
   suitable scheduler. It records what each route supports and where its
   connection or schedule is managed.
3. It presents concrete job settings: purpose, timezone, time, school scope,
   processing budget, selected adapters and output destination. A timezone is
   part of the schedule; “every morning” alone is insufficient.
4. Under the still-pending D6/D7 rules, it requests the external schedule and
   reads back the resulting settings. The Drive register separates what was
   requested from what the scheduler actually reported.
5. At a later launch, the job starts from Drive and the installed instructions.
   It reads the trip email using the selected source route. School information,
   source references and coverage belong in Drive; the email remains at its
   source. The brief application uses the saved information under D5/D6.
6. The run and any output record the job, executing/generating agent, selected
   bindings, sender account/service and verification time. An unsuccessful run
   does not become a successful delivery merely because it launched.

An illustrative parent-facing result would be:

> Morning catalog: managed in Agent A's scheduler; configured for 07:30 in the
> household timezone. Evening brief: managed in Agent B's scheduler; configured
> for 18:00. Both schedules were observed enabled on 15 September at 16:00.
> Unattended operation has not yet been qualified.

Those times illustrate separate jobs, not an approved scheduling default or a
guarantee that runs cannot overlap. Several agents can use the same instance in
turn. Same-data concurrent writes remain outside scope; this proposal adds no
locks, leases or conflict-resolution service.

## Changing a default is different from changing a job

Suppose the evening brief uses Delivery Account A. The parent later makes
Account B the default for new manual briefs.

| Before | After changing only the default |
|---|---|
| Manual brief default: Account A | New manual briefs select Account B. |
| Evening job binding: Account A | The evening job still selects Account A. |
| Yesterday's output sender: Account A | Yesterday's attribution remains Account A. |

Moving the evening job requires an explicit job change and external readback.
The register must show whether that change is requested, confirmed or unresolved.
This protects the parent's chosen bindings and makes historical outputs
understandable after agents or accounts change.

The same distinction applies to pausing. If the parent requests a pause while
the managing scheduler is inaccessible, the useful answer is:

> Pause requested. I could not inspect or change Agent B's schedule. Its last
> observed state was enabled yesterday at 16:00; treat it as potentially active.
> The schedule is managed in Agent B's scheduler.

Editing the desired state in Drive must not produce “Paused” as a statement of
external fact. The precise request/readback/outcome procedure depends on D6,
which is pending.

## Answering “Who sent this?”

Suppose the parent asks a fresh Agent C about the trip-permission brief. Agent C
reads the output attribution and associated job/run from Drive. It could answer:

> The recorded evening-brief job generated this update in Agent B and sent it
> through Delivery Account A. The job is managed in Agent B's scheduler. This
> identifies the recorded output; I have not checked the scheduler's current
> settings.

Agent C does not infer the sender from today's default, invent an unregistered
job, or claim current status from an old observation. Missing output attribution
must be reported as missing. A readable register is useful even when its reader
cannot control the originating agent.

## Budget exhaustion and interruption remain distinct

Bounded discovery windows and saved unfinished work are approved requirements.
The rule for when scheduled work resumes is still undecided. Recommend, for
review, that an existing job's next scheduled launch considers its saved
unfinished windows before claiming to be current. An alternative is a separate
continuation job; another is a parent-requested continuation. The former adds
delay, the second adds schedule/authorization complexity, and the third adds
parent effort. Ordering, budgets and follow-up creation need explicit approval.

This continuation concerns successfully saved progress. D2 interrupted
canonical-write repair is excluded from the MVP. D6's proposal to persist intent
before schedule changes cannot assume that an interrupted set of Drive writes
will be repaired. D7 cannot promise reliable reconciliation of every partially
recorded job until that dependency is resolved. It must not reinstate D2 through
the scheduler design.

## Choices to approve

Recommend approving the capability/register procedure, separate job bindings,
and desired-versus-observed management flow described above, subject to explicit
resolution of their minimum record/write and D6 dependencies. The existing
multi-agent/job requirement does not need reapproval.

Credible alternatives are manual scheduler setup with the agent recording and
checking the settings, or adapter-driven setup with external readback. Manual
setup can support tools lacking schedule-write access, but asks more of the
parent. Adapter-driven setup is more convenient where authorized but needs
reliable management tools. A single mandatory scheduler is simpler to support
but conflicts with the approved freedom to use several agents and jobs.

Approval is still needed for automatic scheduler mutations, the precise
capability evidence contract, continuation timing/ordering, and treatment of
uncertain schedule changes when Drive recording is incomplete. Actual scheduler
access, readback fidelity, unattended permissions and execution limits remain
unqualified. No schedule, send, probe or test is authorized by this brief.
