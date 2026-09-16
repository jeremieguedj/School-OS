# Todoist — optional parent task surface

Use only for the parent's selected account/project with a connector that can
read and update the required meanings. Follow
[task synchronization](../operations/task-sync.md) and
[completion review](../operations/completion-review.md). Todoist remains a
projection; Drive retains canonical Tasks and school evidence.

## Task identity and mapped fields

Todoist supplies task descriptions and project sections. Those product concepts
support this semantic mapping only when the current connector exposes their
complete read/update behavior. They do not establish connector support.
[Descriptions](https://www.todoist.com/help/todoist/features/add-a-task-description-in-todoist-rOryWIHn)
and [project sections](https://www.todoist.com/help/todoist/get-started/get-started-with-todoist-OgNNJR).

| School-OS meaning | Selected Todoist meaning |
|---|---|
| Owned Task identity | Exact School-OS Task ID in a clearly identified managed part of the description; preserve it alongside the canonical reference. |
| Action/context/school timing | Task title plus managed descriptive context; school deadline remains distinct from the parent's planned date. |
| Parent planned date | The selected editable task date, with its actual date/time meaning retained. |
| Owner | Assignee only when the configured project and connector can express/read the selected household person. Otherwise owner remains canonical and the limitation is disclosed. |
| Personal notes | The selected parent-editable description portion, preserved separately from the managed identity/source portion. |
| Confirmed completion | Readable completed task state for the exact owned Task or identified occurrence. |
| Awaiting confirmation | A dedicated configured review section while the task stays uncompleted. |

The managed description carries the existing Task ID; it does not derive a new
identity from title or provider ID. Explain and record the field/section mapping
in private configuration. Preserve parent text outside the managed portion.
If the connector cannot safely separate/read/write those portions, leave that
field unsupported instead of replacing the whole description. An absent marker
or duplicated task cannot be repaired by title matching.

## Completion review and parent decisions

Use a parent-selected dedicated review section for
**Completion detected — awaiting parent confirmation**. Preserve task identity,
parent date, owner and notes when placing it there. The parent can inspect the
linked evidence and check it complete. Verify both placement and completion
through available authorized reads before recording synchronization.

Rejection is an explicit parent instruction to School-OS unless the selected
mapping establishes an equally explicit tool action. Moving the task out of a
section by itself is not evidence of rejection. Save the approved rejected
review entry, and return its presentation to ordinary open work when authorized;
the same evidence must not reopen that suggestion. A connector unable to read
or move sections leaves review presentation unsupported; do not substitute
completion, arbitrary labels or a new custom-field mechanism.

## Listing, edits and recurrence

Read the complete relevant project inventory, required description fields and
completion evidence through the current connector. An active-only list cannot
distinguish completed tasks from deleted/missing tasks. If the route cannot read
completed state, report that limit instead of inferring completion from absence.
Apply the D5 fieldwise three-way comparison and preserve conflicting observations.
Read back the owned marker and intended values after an update. A missing
response never authorizes a blind create or repeat.

Todoist recurring dates can advance the task to its next date when completed;
patterns can depend on the scheduled date or completion date. A moved due date
therefore does not independently establish School-OS occurrence completion.
[Recurring-date behavior](https://www.todoist.com/help/todoist/features/introduction-to-recurring-dates-YUYVJJAV).
Use native recurrence only if its exposed semantics preserve the approved school
series and independently verify occurrences. Otherwise use the approved next
14 days of explicit, non-recurring occurrence Tasks with their own owned IDs;
retain overdue Tasks and the complete series on Drive. Do not select a recurrence
mode just because it sounds similar to the school instruction.

Task creation, updates, authentication and API calls belong to the agent's
connector. This mapping requires no SDK or scheduled process. App-native fields
the selected connector cannot expose remain unsupported. No live Todoist route
has been qualified here.
