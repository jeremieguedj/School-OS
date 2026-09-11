# Agent-managed task projection specification

- Status: approved architecture; implementation specification
- Written: 2026-09-10
- Authority: the recovery MVP plan and the user-approved agent-managed,
  two-way task-projection decision
- Scope: the selected editable task projection; Drive remains canonical

## Purpose

School-OS owns canonical task meaning and synchronization decisions, but it
does not own a Google Sheet layout, Todoist request sequence, or any other
provider's native operations. The user's instance agent reads and operates the
selected task tool through a finite semantic interface. Google Sheets and
Todoist are two implementations of the same interface.

The interface is two-way. Every synchronization reads a complete scoped
projection first, imports supported parent changes into canonical Drive state,
then asks the agent to apply guarded high-level actions. A provider is never a
second source of canonical identity or history.

## Ownership boundary

School-OS owns:

- stable canonical task IDs, source provenance and lifecycle history;
- the complete normalized task vocabulary and provider-neutral policies;
- last-synchronized base/local/remote comparison;
- parent additions, edits, comments, completion and reopen admission;
- durable `needs_review` conflicts that preserve all contested values;
- selected-provider state, switch sequencing and dormant bindings;
- stable effect identities, pre-dispatch authorization, result validation and
  synchronized-base advancement; and
- Drive checkpoints and recovery after local-state deletion.

The user's agent and its private instance adapter own:

- authentication, tool discovery and native API/connector calls;
- provider pagination and evidence that the configured scope is complete;
- Sheet tabs, columns, ranges, formulas, formatting, row relocation and
  literal-value safeguards;
- Todoist projects, sections, labels, descriptions, comments and lifecycle
  endpoints;
- translation between native provider values and normalized task fields;
- guarded native mutations, exact native readback and private raw receipts;
  and
- native partial-effect and error classification.

The agent must not issue canonical IDs, select a provider, resolve a conflict,
decide completion policy, or claim synchronization merely because a native
call returned success.

## Finite exchange

The installed package exposes exactly three task-adapter operations:

```text
read_snapshot(request) -> task-adapter-snapshot
apply_action(committed_action) -> task-adapter-result
reconcile_action(committed_action) -> task-adapter-result
```

These are semantic host operations, not dynamic provider tool names. Their
JSON schemas are `task-adapter-snapshot.schema.json`,
`task-adapter-action.schema.json`, and `task-adapter-result.schema.json`.
Unknown fields are rejected. Private native receipts remain in the admitted
private run directory and are referenced only by a privacy-safe path and hash.

A normalized managed task contains provider object identity, canonical task
identity, origin, action, context, entity scope, workflow state, source link,
source due, parent planned due, latest progress, resolution, parent comment or
completion evidence, and provider revision or a normalized observation hash.
Provider-specific labels, headers, locators and request bodies never enter the
canonical vocabulary.

Comment evidence is an ordered array of exact
`{comment_id, kind, text, effect_id}` records. Parent comments use
`kind: parent` with a null effect ID; School-OS-authored comments use
`kind: system` with their exact committed effect ID. Missing or duplicated
comment identities, a system comment without its effect, or a parent comment
claiming a system effect are blocking normalization failures.

Named optional values use one canonical null representation. Missing native
values may normalize to null only for those named optional fields. An omitted
required field never means unchanged. Required strings remain nonempty.

### Complete snapshot

One read request binds a request ID, provider ID, adapter ID, binding ID and
scope hash. Its response repeats those values and supplies a capture ID/time,
normalized managed tasks, unbound parent candidates, lifecycle/comment
evidence, a proposed cursor, collection-completeness evidence, and private
receipt references.

Completeness is provider-specific but its semantic result is fixed:

- Sheets covers the entire configured editable task projection, including
  completed rows and every mapped parent-editable field.
- Todoist covers the complete scoped active set, the required completed and
  activity overlap, directly resolved known bindings when necessary, and all
  relevant paginated comments.
- No required collection may retain an unconsumed continuation token or report
  truncation. Duplicate canonical IDs, duplicate immutable provider IDs, a
  wrong scope/request, or incomplete evidence blocks before mutation.

An unbound parent candidate has an opaque candidate ID, an immutable provider
ID when the provider supplies one, normalized candidate values, and
adapter-owned guard evidence. A Sheet row number is only a locator. Core must
commit the candidate and issued canonical task ID before authorizing a claim.

### High-level actions

The action vocabulary is deliberately small:

```text
create_task
claim_task
update_task_fields
set_task_resolution
write_system_comment
```

Every action binds an immutable effect ID, provider/binding/scope, canonical
task ID, committed canonical and provider-base hashes, expected prior
normalized state, exact desired fields and postconditions, allowed changes,
and dispatch attempt. A newly selected provider receives the current parent
planned date, progress and resolution as well as source provenance and identity.
Unrelated provider fields must be preserved.

The agent translates a logical group or workflow state to provider-native
constructs. School-OS never mentions Sheet headers/A1 ranges or Todoist
section/label operations in an action.

### Result and readback

The result repeats request/effect/binding/scope identities and reports one of
`confirmed`, `definitely_not_applied`, or `unknown`. A confirmed result includes
the exact normalized native readback and guard/postcondition evidence. Core
recomputes observation hashes and verifies every semantic postcondition.
`verified: true` alone is never sufficient.

One semantic action may need several native calls. The agent exposes any
partial outcome and fresh normalized state rather than retrying the whole
action or claiming atomicity. A remaining native mutation requires a new
committed authorization based on the new observation.

## Reconciliation and durability

Task synchronization is a state machine, not an adapter callback that performs
writes while reconciliation is still in memory:

```text
complete normalized snapshot
  -> pure canonical/provider comparison
  -> commit canonical imports, observation, conflicts and pending action
  -> commit the exact next action as unknown with dispatch_attempt + 1
  -> user's agent performs or reconciles that one action
  -> validate normalized exact readback
  -> commit confirmation, binding and new synchronized base
```

Only a `CURRENT.json` generation that already contains the imported parent
changes and exact action authorization may precede the external mutation.
Locally staged output never authorizes an effect.

The provider comparison uses each binding's last synchronized normalized
snapshot. Parent-only changes are imported; canonical-only changes project;
equal changes converge. Divergent changes record field/base/local/remote,
retain the old common base, set the canonical workflow to `needs_review`, and
emit no destructive action for that task. Source-versus-parent divergence uses
the task's durable source projection and receives the same durable review
treatment.

The provider-state schema stores normalized observations and hashes, pending
finite actions, confirmed receipts, parent admission evidence and dormant
bases. It must not contain an untyped workflow program.

## Recovery

Every action kind uses the same pre-dispatch boundary.

| Current durable evidence | Allowed continuation |
|---|---|
| Pending and never dispatched | Commit it as unknown with the next attempt, then dispatch once. |
| Unknown create | Perform a complete canonical-ID lookup and adopt one exact match. |
| Unknown create with no match | Stay unknown unless qualified negative evidence proves no effect. |
| Multiple or conflicting matches | Block without choosing or creating. |
| Unknown update, claim or resolution | Read the exact scoped object and compare prior/intended normalized states. |
| Provider already equals the intended state | Publish confirmation only; do not repeat the mutation. |
| Guard drift | Return a fresh observation and rerun import/reconciliation before another write. |
| Confirmed reminder with reopen unfinished | Continue with a separately authorized reopen action. |
| Local files deleted | Recover the current Drive bundle and resolve pending/unknown actions first. |

A zero-result lookup does not prove an uncertain create or comment was not
applied. Effect IDs include provider binding/scope, canonical task identity,
semantic operation and desired-state hash so they cannot cross providers.

## Binding and switching

The five-file Drive installation remains unchanged and initially has an unbound
task selector. The user's agent prepares an isolated projection and returns a
complete normalized empty/expected snapshot plus a hash-bound private adapter
configuration reference. School-OS validates and commits that binding; it does
not create headers, choose a layout or interpret the private configuration.

A guided switch performs:

1. complete read and canonical reconciliation of the old selected provider;
2. commit of its final base and a bounded switch record;
3. complete target read and guarded target staging while the old selector stays
   active;
4. target readback and binding commit; and
5. one selector publication making the target active and the old binding
   dormant.

Any target failure leaves the old provider selected. Switching back reuses the
dormant mapping and compares current dormant state with its retained dormant
base. Unexpected dormant edits become review cases; they are not silently
imported or overwritten. Ordinary runs never write two projections.

## Active implementation and archived references

`school_os.agent_tasks` implements schema validation and provider-neutral state
transitions. `school_os.hybrid_tasks` persists those transitions through the
existing bundled checkpoint boundary. The installed
`scripts/run_hybrid_task_sync.py` supports both admitted manual and scheduled
surfaces; `scripts/run_hybrid_task_switch.py` is the attended guided-switch
surface. A provider may be operated only while selected/active or while it is
the named staging target. A dormant binding cannot authorize or confirm an
effect, and switch abort discards only actions whose zero dispatch count proves
they never reached the provider. `school_os.hybrid_preview` provides the
tracked installed continuation from committed ingestion through task exchange,
rendered unsent output and cursor-last completion.

`adapters/tasks/google-sheets.md` and `adapters/tasks/todoist.md` are agent
procedures. The former may describe a familiar default table but no fixed layout
is part of the generic contract. The latter retains complete active/completed/
activity/comment reads, canonical markers, parent due-date separation,
unrelated-label preservation and exact readback.

The existing fixed-layout Python Sheet mapper and its tests remain Git history
and reference evidence. Active hybrid setup/runtime must not import or construct
it, and the frozen package must exclude archived provider executables.

## Implementation order and acceptance

1. Add the schemas and pure normalized validation/state transitions. **Done.**
2. Give create, claim, update, resolution and system-comment actions one durable
   authorization/result protocol.
   **Done.**
3. Replace Sheet-specific hybrid setup/resolution with an opaque selected task
   binding and agent-owned private configuration reference.
   **Done.**
4. Add tracked hybrid task/preview continuation and cursor-last completion.
   **Done.**
5. Rewrite the task adapter documents as agent procedures and exclude archived
   executables from the release payload. **Done.**
6. Prove focused identity, completeness, conflict, interruption, null
   normalization, switch and recovery cases; then run the complete repository
   and installed-package validation. **Repository proof complete; exact committed
   package proof pending.**
7. Build an exact package and execute one new four-day, image-excluded live
   journey: five-file install, cold recovery, agent-prepared isolated Sheet
   binding, source ingestion, canonical task commit, guarded agent action and
   readback, stored deterministic HTML/text, cursor-last `PREVIEW_READY`, and a
   second cold recovery.

The preview reserves no delivery, sends no email, calls no audio provider and
creates no scheduler. It does not replace the final 14-day Sheets/Todoist/
switch/manual/scheduled acceptance chain.
