# Google Sheets task-provider adapter

Status: agent-operated reference procedure. A private instance agent may select
or create any suitable spreadsheet layout and maintain its provider-specific
configuration privately. School-OS neither requires the table below nor
performs native Sheet calls; the table is only a familiar default mapping.

## Representation

Each system-managed row has `Managed By = school-os` and a nonblank immutable
`Canonical Task ID`. The ID is the only identity lookup key. Titles, action
text, row number, position, and sort order never establish identity.

| Canonical dimension | Sheet column | Ownership |
|---|---|---|
| System marker | Managed By | System-managed |
| Immutable task ID | Canonical Task ID | System-managed and immutable |
| Canonical origin | Task Origin (`source` or `parent`) | System-managed |
| Action | Action | Parent-editable under core policy |
| Source-backed context | Task Context | System-managed |
| Source provenance | Source Link | System-managed |
| Logical entity/household group | Group | Parent-editable under core policy |
| Workflow state | Workflow State | System-managed |
| Provider completion/status | Status | Provider-owned except a core-authorized reopen/review patch |
| Source deadline | Source Due | System-managed evidence, distinct from parent plan |
| Parent working deadline | Parent Planned Due | Parent-editable |
| Parent progress | Parent Progress | Parent-editable |
| Qualifying completion note | Completion Comment | Parent-editable |

Additional columns and unrelated cells are provider-owned and are preserved.
The source deadline is never substituted for a parent planned date.

A row with no `Managed By` marker and no canonical ID and a nonempty `Action`
is an unbound parent candidate. It is excluded from the canonical projection,
never matched by title, and exposed with its exact observed cells through
`unbound_parent_candidates()`. After core has journaled a canonical
`origin: parent` task, it may call `claim_parent_candidate()` with that ID and
the candidate packet. The resulting guarded claim marks only that exact row;
recovery resolves the assigned canonical ID from a new complete snapshot, never
by title. A marker with no ID, an ID with no marker, a duplicate ID, an unknown
marker, or a missing required managed value is a corrupted/ambiguous managed
row and blocks the affected sync before a write.

Parent-origin rows use `Task Origin = parent`. Their source context and source
link may be blank because canonical core validates the parent origin, empty
source facts, and null source dates before the claim. The claim preserves
parent Action/Group/status/planned-date/progress/comment values and unrelated
cells. It does not infer or journal a canonical task.

## Agent task boundary

The instance agent implements `core/contracts/task-adapter.md` and owns all
Sheet-specific behavior. It must:

1. Read its entire configured task projection, including completed tasks and
   all mapped parent fields, and normalize it without exposing headers, ranges,
   formulas or row numbers as canonical fields. A paginated, truncated or
   otherwise incomplete read blocks mutation.
2. Resolve every managed item by canonical ID. Row locators are opaque,
   unstable guard material and never identity. Unbound parent candidates carry
   opaque candidate IDs and guard evidence.
3. For every high-level action, re-resolve the current row immediately
   before `batchUpdate` and compare the mutation's `guard_cells(columns)`:
   `Managed By`, `Canonical Task ID`, and the cached prior value of every cell
   the mutation will overwrite (plus every admission-packet cell for a claim).
   A mismatch blocks the write. Translate only changed header keys to observed
   numeric Sheet column indexes, then issue the smallest native request. Append
   returns the new locator; patch or claim returns the guarded target locator.
4. Keep formula-looking text literal, preserve unrelated cells and formatting,
   and change only fields authorized by the committed semantic action.
5. Read the exact target row after every mutation and return its normalized
   observation plus private receipt evidence. A missing or mismatched readback
   blocks binding/cursor advancement.

The adapter chooses its private provider-object representation, but it must be
stable enough to re-resolve the same canonical ID from a complete scoped
snapshot. Since Google Sheets may lack immutable row identity or atomic row
preconditions, the agent enforces the admitted single-writer scope and checks
its private row guard before each write. Sorting/insertion uncertainty blocks.
Readback is verification, not a claimed atomic precondition.

## Pull, patch, and verification rules

1. Read one complete configured scope snapshot at the start of each explicit
   sync. Do not use an earlier sync's snapshot as authority. A verified exact
   readback advances this sync's index; observed drift invalidates it and the
   runtime explicitly reloads before recovery.
   A complete empty snapshot alone does not establish that an earlier unknown
   append was not applied. The runtime may return `definitely_not_applied` for
   retry only with its declared post-consistency-window negative evidence.
2. Validate marker, required system fields, and canonical-ID uniqueness.
   Before a write, the runtime passes unchanged fields from the prior verified
   binding to `verify_expected_system_fields`; unexpected canonical ID, origin,
   Context, Source Link, Source Due, or Workflow State drift blocks. The planned
   canonical projection is supplied separately so only an explicit canonical
   change or a recovered already-applied write is accepted.
3. Build a canonical-ID projection. Generate only differing mapped cells; do
   not rewrite status, parent deadline/progress/comment, or unrelated cells
   during a system projection patch.
4. Apply the native mutation and read the exact row back. Compare every
   requested managed field before advancing a binding or cursor.
5. Preserve parent Action/Group edits according to the canonical reconciliation
   policy. Record the parent fields, status, and comment observations separately
   for the core policy rather than treating them as source facts.

Core persists a `task_create` intent containing the canonical ID, exact Sheet
projection, and projection hash in provider state before `create_task` is ever
called. Immediately before append, the runtime checkpoint callback persists and
exactly reads back the same intent as `unknown` with its next dispatch attempt.
Recovery searches the complete managed scope by canonical ID: it adopts
one exact row, blocks multiple or conflicting rows, and does not repeat an
unknown append after a merely empty snapshot.

`apply_parent_state` is available to the runtime only after core policy has
chosen an allowed status/reopen/review or parent-state update. `None` leaves a
field untouched; an empty string explicitly clears a parent progress or
completion-comment cell. It still requires exact row readback.

## Completion and comments

Completion is never inferred from blank cells, elapsed time, or an overdue
date. The selected policy requires a nonempty freeform parent completion
comment. A completed Sheet status without one must be returned to core as a
review/reopen case; the runtime uses the separate status and
`Completion Comment` observation and does not manufacture text.

When the selected connector exposes native Drive comments for a Sheet, its
comment bridge must re-resolve the canonical row immediately before lookup,
write, and readback; include canonical task ID, provider object ID, immutable
effect ID, current Sheet/range locator, quoted row text, and exact reminder text
in the native comment body/evidence; and verify exactly one exact matching
comment after a write. A native comment with no stable anchor may be used only
with that explicit identity evidence and must never be described as row-anchored.
Reads paginate to completion. If comment operations are unavailable,
the runtime records that capability as unavailable and blocks any operation
that requires a provider comment effect.
The same core checkpoint callback marks the occurrence-stable reminder intent
`unknown` and reads it back before `write_comment`. After interruption, one
exact comment is adopted; a transiently empty complete comment lookup blocks
rather than writing a second reminder.

## Required observed capabilities

Before an attended or scheduled mutation, the private capability profile for
the exact runtime/provider/authentication surface must establish the relevant
task capabilities: `tasks.read_identity`, `tasks.discover_configuration`,
`tasks.list_complete`, `tasks.read_comments`, `tasks.create`, `tasks.update`,
`tasks.write_comment`, and `tasks.verify`. The complete snapshot carries current
status and all mapped parent fields. Guarded `tasks.update` covers Action/Group
and the core-authorized status/reopen change; this adapter does not claim
separate activity, completed-list, move, complete, or reopen endpoints. Comment
lookup is complete/paginated when comment policy needs it, and every mutation
has exact row readback. Synthetic tests demonstrate only the
mapping behavior; they do not claim Google authentication, background
authorization, atomic version preconditions, or production conformance.

## Limitations and integration work

The generic projection supplies canonical ID, origin, source context/link/due,
workflow, and the initial action/group. The coordinated core path journals an
unbound parent row before claim, applies allowed parent edits to canonical
state from last-synchronized snapshots, and records completion separately from
workflow state. The adapter supplies guarded row packets and separate Sheet
observations; it never collapses source due, parent planned due, status, or
comments into one field.
