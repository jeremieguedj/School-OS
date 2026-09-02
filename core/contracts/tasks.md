# Canonical task contract

## Authority

The private Drive task register is canonical for task identity, source provenance, durable history, and synchronization decisions. The selected task provider is the parent-facing interaction projection.

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
- projection status.

Provider identifiers are private state and never replace `task_id`.

## Required semantics

- A finite, unresolved source request becomes a task.
- A standing routine/rule is a guideline, not a task.
- A task may receive parent edits through the selected provider only when the adapter and operation policy allow that field.
- Source due dates are evidence; parent planned dates are working plans.
- Provider-created tasks without source evidence are allowed but must remain distinguishable from source-derived tasks.
- Completion history is append-only in intent. The configured completion-comment policy belongs to the core task operation and private policy configuration.
- Absence, silence, elapsed time, and overdue status do not prove completion.

## Projection

The task operation must use immutable task identity and stored bindings; it must not establish identity through title matching. Provider grouping and workflow are separate logical dimensions. An adapter declares its representation limits and verifies every managed write.
