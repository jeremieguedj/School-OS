# Detailed architecture decision briefs

Prepared 2026-09-15 for review. These are explanatory artifacts with fictional
email examples, step-by-step flows, implications, alternatives and open choices.
No example was executed. They do not approve architecture or qualify behavior.

Start with the [viewable guide](../architecture-guide.html#detailed-briefs).
Each Markdown brief also has a readable HTML companion:

| Decision | Plain-language subject | Detailed brief | Viewable page |
|---|---|---|---|
| D4 | Finding and reading mail; when a run stops | [D4](D4-INGESTION.md) | [Read D4](D4-INGESTION.html) |
| D5 | School information, corrections, tasks and parent edits | [D5](D5-KNOWLEDGE-TASKS.md) | [Read D5](D5-KNOWLEDGE-TASKS.html) |
| D6 | Brief selection, audio and uncertain delivery | [D6](D6-BRIEFS-EFFECTS.md) | [Read D6](D6-BRIEFS-EFFECTS.html) |
| D7 | Tools, accounts, agents, jobs and attribution | [D7](D7-TOOLS-JOBS.md) | [Read D7](D7-TOOLS-JOBS.html) |
| D8 | Installation, upgrades and compatible extensions | [D8](D8-INSTALL-UPGRADES.md) | [Read D8](D8-INSTALL-UPGRADES.html) |
| Remaining D3 | How code and connected tools work together | [D3](D3-EXECUTION-ADAPTERS.md) | [Read remaining D3](D3-EXECUTION-ADAPTERS.html) |
| Undecided dependency | Minimum records and ordinary verified saves | [Records](RECORDS-AND-NORMAL-WRITES.md) | [Read the dependency](RECORDS-AND-NORMAL-WRITES.html) |

D1, the query-coverage rule and the agent code-execution prerequisite remain
approved. D2 interrupted canonical-write recovery remains outside the MVP.
The [active plan](../../PLAN.md#current-coordinator-checkpoint--architecture-approval-pending)
is the approval ledger; the [architecture proposal](../ARCHITECTURE-PROPOSAL.md)
and [product principles](../../../../product-principles.md) supply the design context.

The expanded explanation makes these missing decisions visible before coding:

- D4/D6/D7: who launches continuation, total catch-up budget, daily freshness,
  unfinished-work escalation and whether a brief waits or reports partial coverage.
- D6: email/audio ordering and the exact boundary for unknown external effects
  after D2's exclusion.
- D8: installation/upgrade interruption behavior without silently restoring D2.
- Remaining D3 and minimum records: executable contracts, supplied routes and
  normal save/verification semantics still need concrete approval.

The options in the briefs support review. Unspecified numeric budgets, policies,
schemas and follow-up mechanisms are not approved by an explanation request.
All required implementation areas remain open with the explicit D2 exception;
this documentation checkpoint is not the whole-project code handoff.
