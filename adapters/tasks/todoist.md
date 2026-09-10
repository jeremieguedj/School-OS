# Todoist task-provider adapter

Status: agent-operated reference procedure. The active project, sections,
labels, account and native task operations belong to the user's private
instance agent. School-OS exchanges only the normalized snapshots, committed
semantic actions and verified results defined by
`core/contracts/task-adapter.md`; it does not ship a Todoist connector worker.

## Representation

| Canonical dimension | Todoist representation |
|---|---|
| Logical entity/household group | Configured Todoist section |
| Workflow state | Exactly one configured managed label |
| Task title | Todoist task content |
| Parent planned due | Todoist due date |
| Parent progress/completion note | Newest qualifying non-system comment |
| Immutable canonical task ID | System-owned marker in the task description plus private binding |

Group and workflow are independent dimensions. Preserve unrelated user labels and fields.

## Required Todoist operations

In addition to the daily complete-snapshot task baseline, this adapter's runtime
profile must provide and verify the distinct completed/activity/move/complete/
reopen capabilities required by Todoist's representation:

1. authenticated-user and timezone read;
2. project lookup by configured ID;
3. complete pagination over active tasks;
4. completed-task and activity reads over the configured overlap window;
5. direct comment reads for changed tasks, using the connector's supported
   page size and continuation tokens until complete;
6. section/label discovery and mapping verification;
7. create, patch update, move, complete, reopen, and comment write;
8. exact task readback after every write.

## Field ownership

| Canonical field | Todoist behavior |
|---|---|
| Immutable task ID | System-owned description marker; never rely on title alone |
| Action | Parent-editable task title |
| Source-backed context/provenance | System-owned description fields |
| Entity scope | Parent section move may update scope when policy permits |
| Workflow state | Exactly one managed label |
| Source deadline | Description/provenance only |
| Parent planned due | Todoist due date |
| Parent comment | Imported verbatim as progress or completion history |

Descriptions are system-owned. Unsupported freeform description edits are repaired or escalated according to the core task policy.

## Completion policy

The core policy determines whether completion requires a parent comment. When required, the adapter must reopen the same task, restore its canonical section/workflow, and add the configured fixed reminder when the provider reports completion without a qualifying comment.

## Limitations

Todoist capability and history retention vary by account and connector surface. The
runtime profile must declare exact activity, comments, pagination, completed-task,
and readback limits before enabling this adapter. For the currently supported
Todoist connector, comment reads use `limit=10` and must follow every returned
continuation token; a smaller page is never permission to inspect only the first
page.
