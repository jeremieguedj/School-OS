# Canonical task contract

## Authority

The private Drive `canonical-tasks.json` register is canonical for task identity,
source provenance, durable history, and synchronization decisions. The selected
task provider is the parent-facing interaction projection. The Markdown table
template is a legacy/readable view, never a second task authority.

## Logical task

A canonical task contains:

- immutable `task_id`;
- action text;
- concise source-backed context;
- entity scope;
- workflow state;
- owner;
- source-opened date and last supporting-source date;
- source deadline and parent-planned deadline as separate fields;
- source link and supporting Fact IDs;
- latest parent progress;
- provider bindings;
- lifecycle/completion history; and
- current `unresolved`/`completed` resolution and projection status.

Provider identifiers are private state and never replace `task_id`.
Parent-origin task IDs are newly issued in the durable admission intent. A
provider row locator, title, or current cell content never becomes task identity.

The register is canonical UTF-8 JSON. Its entries are ordered by immutable task
ID and can be rebuilt from verified Facts. Source-created task IDs derive only
from the opening action Fact ID. A title match never merges records; later task
support requires an explicit validated relationship in the reconciliation path.
Each source task retains its opening projection and compact ordered relationship
evidence in canonical projection state. Normal reconciliation may therefore
submit only newly verified relationship Facts; it does not have to resend the
opening Fact or every prior support/correction/completion/reopen Fact.

All editable task tools implement the provider-neutral
[agent-managed task projection contract](task-adapter.md). The user's instance
agent owns provider-native reads, writes, layout and readback. School-OS owns
the normalized comparison, canonical changes and durable action authorization.

## Required semantics

- A finite, unresolved source request becomes a task.
- A standing routine/rule is a guideline, not a task.
- A task may receive parent edits through the selected provider only when the adapter and operation policy allow that field.
- Source due dates are evidence; parent planned dates are working plans.
- Provider-created tasks without source evidence are allowed but must remain distinguishable from source-derived tasks.
- Completion history is append-only in intent. The configured completion-comment policy belongs to the core task operation and private policy configuration.
- Before dispatching a missing-comment reminder, the runtime must durably mark
  and exactly read back that occurrence-stable effect intent as `unknown`. After
  an interrupted dispatch, one exact comment is adopted; an empty complete
  comment lookup does not authorize a duplicate write without explicit
  `definitely_not_applied` evidence.
- Source support, correction, completion, and reopen relations are applied in
  stable source/message/content chronology. Fact ID is only the final ordering
  tie. Last-support date is monotonic, and contradictory changes at one source
  coordinate block for review.
- The durable source projection is the common base for source-owned Action,
  Context, Group, and Source Due changes. A source-only change applies, an
  accepted parent-only Action/Group edit remains canonical, equal changes
  converge, and divergent source/parent values block for explicit review before
  canonical mutation or provider projection.
- Source Fact IDs, compact relationship evidence, and lifecycle events merge
  idempotently and append-only across calls. Omitting older Facts from one
  incremental call never removes them, lowers last-support date, or silently
  changes the current resolution.
- Only an unresolved action projects as a new provider task or appears in a
  task brief. A later explicit reopen restores eligibility.
- Absence, silence, elapsed time, and overdue status do not prove completion.

## Projection

The task operation must use immutable task identity and stored bindings; it must not establish identity through title matching. Each provider has at most one binding per canonical task, and each provider object is bound globally at most once. Provider grouping and workflow are separate logical dimensions. An adapter declares its representation limits and verifies every managed write.

Before creating a missing provider task, persist a `task_create` effect intent
containing the canonical task ID, exact managed projection, and projection hash.
Immediately before every initial or evidence-authorized retry dispatch, update
that exact intent to `unknown`, increment its dispatch attempt, and durably read
it back through the operation's checkpoint callback. Creation occurs only after
that pre-dispatch readback. If the process stops after provider acceptance, a
complete canonical-ID lookup may adopt exactly one exact match;
multiple or conflicting matches block. Zero matches remains unknown and cannot
be retried unless the adapter returns explicit `definitely_not_applied`
evidence after its declared consistency window.
