# School-OS restart: current plan and artifacts

Updated 2026-09-14. Start here when resuming the restart. The current design is
documented; a production replacement and cross-agent handoff are not yet
implemented or qualified. Earlier experiments and the retired runtime are
evidence, not an instruction to rebuild their architecture.

The coordinator is now working on `codex/restart-school-os`. The
[whole-project coverage map](implementation/COVERAGE.md) is complete;
[architecture decisions D1–D8](implementation/ARCHITECTURE-PROPOSAL.md) await
explicit approval. [Fictional scenarios and proposed tests](implementation/TESTING-PROPOSAL.md)
are preparation only. This is an architecture checkpoint, not the whole-code
handoff or the start of testing.
The [new isolated development model](identity/revised-model/README.md) and its
fictional checks are also authored but unexecuted; frozen studies stay unchanged.

For a guided review, open the [HTML architecture decision guide](implementation/architecture-guide.html).
It explains the proposal with an overview, examples and expandable detail.
The written proposal remains authoritative; the guide records no approvals.

The [product principles](../../product-principles.md#decision-authority) are the
source of truth and grounding for uncovered decisions. Every new or changed
architecture decision requires explicit user approval before adoption or
implementation. The next coordinator must stop after publishing the agreed new
project code; the user personally manages and oversees testing. No tests or
pilots start automatically. The [Astra handoff](ASTRA-HANDOFF.md) is the copyable
prompt for that session.

The assignment covers the [whole project](PLAN.md#whole-project-implementation-scope):
installation, ingestion, knowledge, tasks, queries, briefs, tools/schedules,
recovery, agent replacement and extensible upgrades. Email identity is one
component with a detailed revised recipe. Requirements and lifecycle design
exist across these areas; exact architecture choices, implementation and real
agent qualification are distinct remaining work.

## Current direction

Google Drive is the durable home for processed school knowledge, source and
attachment references, coverage, configuration, unfinished work and the known
tools/jobs/runs register. Original emails and attachments stay in their source
systems and are downloaded temporarily for processing. An agent reads the
instance's relevant records, selects available adapters, performs bounded work,
verifies persistence and leaves sufficient state for another session or agent.

Logical email identity uses normalized source metadata and School-OS-owned
record IDs. Attachments belong to their parent email; replies use their own
original Date. Simple normalization and resumable search windows address the
observed presentation and pagination issues. Provider entries are not an
independent count of logical emails. Content processing has separate coverage
and is never an identity fallback.

Users may have multiple agents and jobs. Known schedules retain their location,
executing agent, selected adapters, scope, verification and output attribution.
Concurrent updates to the same Drive data remain outside scope. No dedicated
personal computer or coding CLI is required by the target architecture.

## Current authority and reading order

| Artifact | What it contains | Status |
|---|---|---|
| [Product principles](../../product-principles.md) | Product purpose, core use cases, source custody, portable agents, metadata-only identity, processing coverage and job visibility | Current product authority; updated with approved clarifications |
| [Restart plan](PLAN.md) | Approved architecture choices, development sequence, qualification milestones and remaining limits | Current work plan; implementation milestones remain open |
| [Astra coordinator handoff](ASTRA-HANDOFF.md) | Reading order, delegation, architecture approval and mandatory code-to-testing handoff | Current next-session prompt; no testing authorization |
| [Metadata and ingestion recipe](identity/METADATA-RECIPE.md) | Logical-email reuse, address/subject normalization, original Date, parent-bound attachment groups, replies and window-based recovery | Current detailed design; not a claim of implemented behavior |
| [Corrected live-email findings](identity/metadata-stress/README.md) | Actual Gmail observations, original experiment results and the corrected interpretation of their product significance | Empirical evidence with explicit limitations |
| [Root plan](../../../PLAN.md) and [progress log](../../../PROGRESS.md) | Active-plan routing, decisions, completed work and exact next actions | Repository continuity; older log entries preserve their historical interpretation |

## Evidence artifacts and their limits

| Artifact | Evidence retained | How to use it |
|---|---|---|
| [Live study protocol](identity/metadata-stress/PROTOCOL.md) | Privacy boundary, sampling, metadata-only inputs, snapshot grading and injected stresses | Read before interpreting numeric outcomes |
| [Collection aggregates](identity/metadata-stress/collection-results.json) | 127 read-only calls, 632 observed Gmail entries, address/filename/date/pagination observations | Source observations; no private email values |
| [Evaluation results](identity/metadata-stress/results.json) | Frozen baseline scores, collision projections, reply replay and code/data hashes | Scores use provider-entry references; they are not measured logical-email error rates |
| [Policy checks](identity/metadata-stress/policy-results.json) and [reproduction checks](identity/metadata-stress/validation-results.json) | 38 fictional checks, two reproduced limitations, and repeatability across two Python environments | Reproduce the earlier baseline; passing does not qualify the revised plan |
| [Model](identity/metadata-stress/model.py), [evaluator](identity/metadata-stress/evaluate.py) and [checks](identity/metadata-stress/check_model.py) | Reusable development code bound to the original results | Frozen, development-only instruments; not an installed runtime or parent dependency |
| [Lifecycle simulation](SIMULATION.md) and [state ledger](simulation/results/state-ledger.md) | Historical setup, ingestion, interruption, daily jobs, knowledge/task state, attribution and another agent's queries | Scenario coverage; its original identity implementation is superseded |
| [Agent/connector identity research](identity/REPORT.md) | Provider-versus-connector distinctions, earlier live probe and primary-source research | Research evidence; follow the current recipe rather than superseded content-assisted proposals |
| [Historical MIME evaluation](identity/mime-evaluation/README.md) | Original content-assisted matching behavior and its limits | Retained history; content/MIME matching is outside the current identity design |

Complete Gmail receipts and per-observation audits stay in ignored private
development storage. They are not public artifacts and are not a proposed raw
email archive for a parent's instance. The retired [architecture document](../../architecture.md)
and older release plans are also historical implementation context.

## What was corrected

The study combined two separately exposed Gmail entries with agreeing metadata.
It did not establish that they were different logical emails or that school
information was lost. Its original provider-entry scoring remains reproducible,
but does not define the product's identity requirement. Repeated filenames were
within parent emails and may include alternate representations. Address cleanup
was already implemented in the experiment; subject trimming is now approved for
the next revision. Timestamp changes were not observed. Thread grouping is
optional, and short pages with continuation require continued enumeration.

The next implementation covers the whole-project checklist, including a revised
small development model, with new architecture decisions approved before
implementation. A finished identity model alone is not the completed project.
Publish the agreed project code and stop for the user to direct testing.
Actual file/table layout, attachment-group processing, complete discovery,
scheduling, fresh-session handoff and execution cost remain qualification work;
the proposed managed-agent/Drive pilot is not authorized to start automatically.
