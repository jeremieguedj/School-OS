# Synthetic legacy rolling-update ambiguous-match fixture

## Source record facts

| Fact ID | Source ID | Received day | Scope | Text | Update | Guideline | Action |
|---|---|---|---|---|---:|---:|---:|
| SYN-003-F1 | SYN-THREAD-003 | 2026-01-08 | child_1 | The class completed a science observation. | yes | no | no |
| SYN-003-F2 | SYN-THREAD-003 | 2026-01-08 | child_1 | The class completed a science observation. | yes | no | no |

## Legacy rolling input

```text
## 2026-01-08
- Child 1: The class completed a science observation. [TID:SYN-THREAD-003]
```

## Expected decision

Two eligible source Facts match exactly. Migration must stop and emit a private exception record; it must not choose one, add a Fact ID, or alter the input.

