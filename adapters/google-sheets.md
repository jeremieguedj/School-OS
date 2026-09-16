# Google Sheets — optional parent task surface

Use only when the parent selects a particular spreadsheet and task range. Apply
[task synchronization](../operations/task-sync.md) and
[completion review](../operations/completion-review.md). Canonical Tasks remain
in Drive JSON; the spreadsheet projects them for parent interaction.

## Select the column mapping

Use a dedicated task table or explicitly selected existing table. Read its
headers and explain which fields are managed versus parent-editable before
adopting the supported mapping in `selected_task_projection`. Do not replace an
existing workbook or infer a private spreadsheet from these illustrative names.

| School-OS concept | Table meaning |
|---|---|
| `task_id` | Dedicated managed School-OS Task ID column, exact text; never the row number. |
| Action, context, source reference | Clearly named managed columns; retain qualifications and a canonical reference if display space is limited. |
| School deadline/condition | Managed school-evidence column, separate from parent planned date. |
| Owner, planned date, progress, personal notes | Selected parent-editable columns with their individual D5 comparison bases. |
| Parent-confirmed completion | Explicit completed value or checkbox, read as a genuine boolean under the chosen mapping. |
| Awaiting parent confirmation | Supported visible task-status column or distinct review section; completion remains false. |

These are tool projection meanings, not another canonical schema. Record actual
column names and range in private configuration. A supplied table can display
`Open`, `Completion detected — awaiting parent confirmation`, and `Completed`
as clearly distinct statuses. Do not let a status and checkbox silently disagree:
read both where configured and resolve a contradictory edit. Parent rejection
requires an explicit review action supported by the selected table or a direct
instruction to the agent; ordinary sorting/moving a row is not rejection.

## Read, locate and preserve edits

Read bounded ranges covering the selected task inventory, including identity and
every mapped field. A filtered view, hidden rows, a connector's truncated preview
or the first blank row does not prove inventory exhaustion. Follow the actual
range and continuation evidence. Find the exact owned marker again after sorting
or row insertion; duplicate markers are a conflict, not two new Tasks.

Sheets can omit trailing empty cells/rows from value responses. Interpret an
omission as a blank only when the returned range and connector contract establish
that the cell was actually included. Otherwise it is unread/unknown. Preserve
explicit false completion, zero values and deliberate clears; do not use
truthiness to decide whether a field exists. Dates must retain the intended
calendar/timezone meaning rather than copying a locale-dependent display string.
[Official cell-value semantics](https://developers.google.com/workspace/sheets/api/guides/values).

Read values as data. Keep source text and IDs as literal text rather than executing
them as formulas. Preserve existing formulas and unrelated cells; write only the
agreed mapped cells for the identified Task. The connector owns its safe literal
write mechanism. If that cannot be established, report the unsupported write.

## Synchronize and verify

Apply the D5 three-way field table; do not overwrite a parent's edit with an old
export. Read back the exact marker and changed fields after each bounded update,
including an explicit clear. Update canonical sync evidence only for verified
fields. An unknown append outcome requires marker lookup before any repeat;
never append another row merely because the call did not return.

Keep one row per independent Task, including individual recurring occurrences
under the approved 14-day projection when necessary. A once-per-household Task
has one row even if it benefits two children. Row deletion is missing projection,
not school cancellation. No Apps Script, custom API wrapper, polling or new
dependency is required. This mapping is authored, not live-qualified.
