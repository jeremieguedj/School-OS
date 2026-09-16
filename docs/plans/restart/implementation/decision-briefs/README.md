# Architecture briefs and current MVP scope

Updated 2026-09-15 with the user's decisions and scope reductions. These briefs
explain the approved direction, remaining choices and deferred features in plain
English. Their fictional examples are written illustrations; none was executed.
An explanation is not architecture approval or product qualification.

Start with the [viewable guide](../architecture-guide.html#detailed-briefs).
Each Markdown brief also has a readable HTML companion:

| Decision | Plain-language subject | Detailed brief | Viewable page |
|---|---|---|---|
| D4 | Agent-owned complete-run processing and resource batching | [D4](D4-INGESTION.md) | [Read D4](D4-INGESTION.html) |
| D5 | Approved knowledge, corrections, tasks and parent edits | [D5](D5-KNOWLEDGE-TASKS.md) | [Read D5](D5-KNOWLEDGE-TASKS.html) |
| D6 | Agent verification and ingestion before the brief | [D6](D6-BRIEFS-EFFECTS.md) | [Read D6](D6-BRIEFS-EFFECTS.html) |
| D7 deferred | Agent-owned schedules; no MVP central job manager | [D7](D7-TOOLS-JOBS.md) | [Read D7](D7-TOOLS-JOBS.html) |
| D8 deferred | Package/upgrade management deferred; preserve D1 separation | [D8](D8-INSTALL-UPGRADES.md) | [Read D8](D8-INSTALL-UPGRADES.html) |
| D3 approved direction | Minimal Python helpers; otherwise agent and tools | [D3](D3-EXECUTION-ADAPTERS.md) | [Read D3](D3-EXECUTION-ADAPTERS.html) |
| Deferred framework | Existing data/save obligations without a framework gate | [Records](RECORDS-AND-NORMAL-WRITES.md) | [Read the scope note](RECORDS-AND-NORMAL-WRITES.html) |

The current scope is:

- **D1, query coverage and the code-execution prerequisite:** remain approved.
  The Drive layout does not approve a record schema or installer.
- **D4:** agents own completion of the requested run and use resource-aware
  batching as guidance. Batching is not an arbitrary School-OS rule to abandon
  the daily task after one batch. Remaining specifics need their own approval.
- **D5:** approved. Its knowledge, task and parent-state behavior remains in scope.
- **D6:** agent verification and ingestion before brief generation are approved
  directions. Remaining detailed choices are still pending; removing D7 does
  not remove verification or allow unknown effects to be called successful.
- **D2:** interrupted canonical-write recovery is deferred. The separately
  approved query rule and ordinary verified saves remain required. The separate
  records/ordinary-save framework is outside MVP, not an approval gate.
- **D7:** centralized tools/jobs registration and scheduler management are
  deferred. Users and capable agents own schedules and execution, read School-OS
  recipes and select the adapters needed for each operation. The MVP assumes
  no concurrent use of the same Drive data and introduces no locks.
- **D8:** packaged installation, version/upgrade/migration/compatibility and
  extension-management machinery are deferred. D1's separation remains, and
  first-use operations follow approved D1 through the agent and tools.

The [active plan](../../PLAN.md#current-coordinator-checkpoint--architecture-approval-pending)
is the approval ledger; the [architecture proposal](../ARCHITECTURE-PROPOSAL.md)
and [product principles](../../../../product-principles.md) supply the design context.

D3’s minimal Python standard-library/agent-tool direction is approved. The
[actual helper guide](../../../../../helpers/README.md) names the authored
routines and prepared unexecuted checks. Remaining D4/D6 choices still need
review. Do not restore the excluded records/ordinary-save framework, recovery,
central scheduler or upgrade manager as hidden dependencies. Specific new
architecture still needs explicit approval; routine work follows approved meanings.

Earlier D7/D8 proposals are historical context, not current implementation gates.
Their deferral explicitly narrows the original whole-project assignment; the
broader principles are not silently rewritten. Repository/history/privacy
safeguards remain. Implementation and later qualification must be reported
separately. The code-publication handoff and mandatory stop before user-directed
testing remain in force.
