# School-OS restart: current plan and artifacts

Updated 2026-09-15. Start here when resuming the restart. The current design is
documented; a production replacement and cross-agent handoff are not yet
implemented or qualified. Earlier experiments and the retired runtime are
evidence, not an instruction to rebuild their architecture.

The coordinator remains on `codex/restart-school-os`. The
[coverage map](implementation/COVERAGE.md) separates original whole-product scope
from current MVP delivery. D1, query coverage, D3’s minimal Python standard-library
helpers with agent/tool operations, and D5 are approved. On 2026-09-15 the user replaced School-OS-managed
batching with executing-agent guidance and complete logical-run ingestion,
required agent-led uncertain-effect verification and ingestion-before-brief,
and deferred D7 tools/jobs management and D8 packaged lifecycle. D2 canonical
repair and the separately proposed records/ordinary-save framework are deferred. The [active plan](PLAN.md) records exact approval
boundaries and remaining choices; the excluded record/save framework is not a
prerequisite for retained work. The product principles retain the broader
long-term scope; these explicit MVP exceptions take precedence for delivery.

[Fictional scenarios and proposed tests](implementation/TESTING-PROPOSAL.md) and
the [isolated development model](identity/revised-model/README.md) are authored
preparation only. Frozen studies stay unchanged. No tests or models were run.
The [minimal helpers](../../../helpers/README.md) are authored with prepared
checks, not executed. This subset/documentation checkpoint is not the whole-code
handoff or start of testing.

For a guided review, open the [HTML architecture decision guide](implementation/architecture-guide.html).
Its [single numbered section](implementation/architecture-guide.html#open-questions)
and [decision inventory](implementation/OPEN-QUESTIONS.md) now record the user's
Q3/Q5/Q7–Q9 decisions and binary email outcome. The
[concrete data/index proposal](implementation/DATA-ARCHITECTURE-PROPOSAL.md)
explains child/family/school scope and history queries. Its fields/indexes and
the narrow Q4/Q6 discovery/reuse rules await approval; other decisions are settled.
The [new operating instructions](../../../operations/README.md) cover the
approved setup interview, reusable tool-semantic adapters and parent confirmation
of detected completion. Agent-specific connectors own API/access mechanics;
these instructions and their review cases are authored, not executed.

The [architecture in practice page](implementation/architecture-in-practice.html)
shows the layers, Drive structure, processing coverage and seven step-by-step
household scenarios. It separates approved behavior from fictional values and
approved detected-completion review, manual freshness conversation and audio policy. It is explanatory
material, not an executed simulation or an implementation claim.
The [agent execution guidance](implementation/AGENT-EXECUTION-GUIDANCE.md) gives
resource-management advice without implementing an agent batch controller.
The guide mirrors the approval status; the written proposal and active-plan
approval ledger remain authoritative.

The [product principles](../../product-principles.md#decision-authority) are the
source of truth and grounding for uncovered decisions. Every new or changed
architecture decision requires explicit user approval before adoption or
implementation. The next coordinator must stop after publishing the agreed new
project code; the user personally manages and oversees testing. No tests or
pilots start automatically. The [Astra handoff](ASTRA-HANDOFF.md) is the copyable
prompt for that session.

The assignment covers the [whole project](PLAN.md#whole-project-implementation-scope):
retained ingestion, knowledge/tasks, queries, briefs, basic Drive startup and
agent recipes, subject to the explicit D2/D7/D8 MVP deferrals. Email identity is one
component with a detailed revised recipe. Requirements and lifecycle design
exist across these areas; exact architecture choices, implementation and real
agent qualification are distinct remaining work.

## Current direction

Google Drive is the durable home for processed school knowledge, source and
attachment references, coverage, configuration and normally saved unfinished work.
The centralized tools/jobs/runs register is deferred from the MVP. Original emails and attachments stay in their source
systems and are downloaded temporarily for processing. An agent reads the
instance's relevant records, selects usable adapters, manages its own processing
resources and verifies the complete intended ingestion before a daily brief.
Normally saved canonical knowledge remains available to another capable agent;
School-OS does not promise generic recovery of interrupted canonical writes.

Logical email identity uses normalized source metadata and School-OS-owned
record IDs. Attachments belong to their parent email; replies use their own
original Date. Simple normalization and resumable search windows address the
observed presentation and pagination issues. Provider entries are not an
independent count of logical emails. Content processing has separate coverage
and is never an identity fallback.

Users may have multiple agents and jobs. Users and agents manage them outside
School-OS; each run follows its recipe and selects the necessary adapters. The
MVP assumes they do not operate concurrently on the same Drive data and provides
no schedule register, scheduler controller or locking mechanism. No dedicated
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

The next implementation covers the retained MVP checklist, with the explicit
deferrals and new architecture decisions recorded before dependent code. A finished identity model alone is not the completed project.
Publish the agreed project code and stop for the user to direct testing.
Actual file/table layout, attachment-group processing, complete discovery,
scheduling, fresh-session handoff and execution cost remain qualification work;
the proposed managed-agent/Drive pilot is not authorized to start automatically.


## Final approval and documentation snapshot

The user has explicitly approved all remaining published Q1/Q2, Q4 and Q6
recommendations. Earlier proposal/pending language in historical review material
records the discussion at that time, not a remaining approval gate. The active
[plan](PLAN.md#current-execution-authorization) records the final authority and
three isolated post-publication ingestion/audit trials. Those trials supersede
the earlier requirement to wait for subsequent testing direction; unrelated
qualification and outbound effects remain unauthorized.

The requested **OrgoS Restart Documentation** snapshot preserves all tracked
documentation, decisions, architecture, plans, source history and frozen evidence
before restart implementation cleanup. See [the snapshot guide](DOCUMENTATION-SNAPSHOT.md).
