# D7 — Agents own execution; centralized job management is deferred

Updated 2026-09-15 to record the user's MVP scope decision. D7's centralized
tools/jobs register and scheduler-management mechanisms are **outside the MVP**.
They are no longer pending prerequisites for building the current project.
The [active plan](../../PLAN.md) records this exception to the broader
[product principles](../../../../product-principles.md).

Users and their capable agents own schedules and execution. School-OS supplies
the relevant operation recipes and adapter requirements. An agent reads the
recipe, selects suitable available adapters and manages the work. It does not
need a School-OS scheduler or job registry to start an operation.

## What the agent still needs

For a fictional request, “Read this week's Juniper School mail and prepare my
brief,” the agent still needs to know:

- Which source account and school/date scope the user means.
- Where the School-OS instance is on Drive and which operation recipe applies.
- Which available connections and adapters can read the source, save processed
  information, handle attachments and perform any authorized delivery.
- Which capabilities are missing and what that means for completion.

These are operation-level requirements. Removing a central tools/jobs register
does not remove source configuration, adapter contracts or authorized account
selection. A source mailbox is still distinct from the connection currently
used to access it; reconnecting an account must not redefine source identity.

The approved code-execution prerequisite remains. The user's report of supplier
support does not independently qualify a particular runtime or adapter.

## A simple execution example

The parent arranges a daily task in their chosen agent application. That
application owns when the task starts. Once launched, the agent:

1. Reads the relevant School-OS instructions and operation configuration.
2. Selects the adapters needed for the authorized source and Drive work.
3. Ingests the relevant school information, managing resource use through
   batches while working toward completion of the requested run.
4. Follows D6's approved direction to ingest before preparing the brief and
   verify the operation's effects. It reports actual limits rather than
   inventing successful processing or delivery.

This is a written example, not an executed schedule. D4's resource guidance is
for the agent to manage the complete run; it is not a School-OS rule that ends
the daily task after an arbitrary batch. Remaining D4/D6 specifics are reviewed
in their own briefs. The example does not approve a new continuation service,
automatic follow-up job or persistence mechanism.

## What is deferred

The MVP does not build a centralized inventory of tools, agents, jobs and their
management locations. It does not create, change or pause external schedules
through a School-OS scheduler-management subsystem, or reconcile scheduler
settings against a desired state stored in a registry. It does not promise that
any fresh agent can enumerate known jobs or identify their managing scheduler
by reading such a registry.

Schedule questions belong with the user and agent application that manages the
schedule. Fresh-agent access to saved school knowledge remains in scope; it
does not imply access to another application's schedules. Operation evidence
needed for D6 verification remains in scope under D6. Deferring the registry
does not authorize unverified sends or treating unknown effects as successful.

## Multiple agents and the remaining boundaries

The user may use any number of capable agents. The MVP assumes they do not
access the same Drive data concurrently. Users and agents manage their execution
accordingly; School-OS adds no locks, leases or conflict-resolution machinery.

D2 interrupted canonical-write recovery also remains deferred. Agent ownership
of execution does not promise repair of partially saved data. Normal verified
saves, honest coverage, bounded discovery progress and the approved
query-coverage rule remain required, with minimum records and ordinary-write
contracts still needing their own decisions.

The former D7 proposal is historical design context, not an MVP implementation
instruction. Reintroducing centralized job management later would require an
explicit scope and architecture decision. No schedule, probe, test or live
effect is authorized by this scope update.
