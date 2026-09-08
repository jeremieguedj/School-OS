# Google Sheets task-provider adapter

Status: selected alpha.13 reference adapter. A private instance selects one
spreadsheet, one visible sheet, a bounded task-table range, and the matching
runtime bridge. This adapter contains no private Drive IDs, sheet titles,
recipients, or credentials.

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

## Runtime packet boundary

`school_os.sheets` is provider-neutral deterministic mapping code. The selected
runtime performs authentication and native Google calls, then injects one
`GoogleSheetsRowsPort` implementation:

1. Convert a bounded native CellData/range response into
   `normalized_snapshot(scope, rows, complete=True)`. Each row includes its
   current opaque `row_id` locator and header-to-string cell map. It is not a
   stable identity. A paginated, truncated, or otherwise incomplete range uses
   `complete=False` and blocks mutation.
2. Create `GoogleSheetsTaskAdapter(...).begin_sync()` once per reconciliation
   and pass that sync session to the generic task reconciler. The session takes
   one complete snapshot and builds an in-memory canonical-ID index from it;
   verified exact-row reads update that index. A later reconciliation creates a
   new session. Its `NativeSheetMutation` candidates use
   `userEnteredValue.stringValue` for every value, including text beginning
   with `=`. This keeps formula-looking action/progress/comment text literal.
3. For every patch or claim, re-resolve the current row locator immediately
   before `batchUpdate` and compare the mutation's `guard_cells(columns)`:
   `Managed By`, `Canonical Task ID`, and the cached prior value of every cell
   the mutation will overwrite (plus every admission-packet cell for a claim).
   A mismatch blocks the write. Translate only changed header keys to observed
   numeric Sheet column indexes, then issue the smallest native request. Append
   returns the new locator; patch or claim returns the guarded target locator.
4. Read the exact target row with native CellData after every create, patch,
   comment effect, or core-authorized state update. Feed that normalized row to
   `read_exact`. A missing or mismatched readback blocks binding/cursor
   advancement.

The adapter's persisted provider object ID is a canonical-ID binding of the
form `sheets:canonical:<task-id>`, not a row number. A sync resolves that ID
from its complete scoped snapshot. Since Google Sheets exposes no immutable row
ID or atomic row-identity precondition here, the runtime must enforce the
configured admitted single-writer scope and re-check the identity guard before
each write. Concurrent sorting/insertion uncertainty blocks the operation. The
exact readback provides a second retargeting check; it is not claimed as an
atomic precondition.

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
called. Recovery searches the complete managed scope by canonical ID: it adopts
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

## Required observed capabilities

Before an attended or scheduled mutation, the private capability profile for
the exact runtime/provider/authentication surface must establish the relevant
task capabilities: scoped snapshot completeness, row identity/configuration
read, native create/update, status/reopen when selected, comment operations
when selected, and exact row readback. Synthetic tests demonstrate only the
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
