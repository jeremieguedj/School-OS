# Synthetic legacy rolling-update zero-match fixture

## Source record facts

| Fact ID | Source ID | Received day | Scope | Text | Update | Guideline | Action |
|---|---|---|---|---|---:|---:|---:|
| SYN-002-F1 | SYN-THREAD-002 | 2026-01-08 | child_1 | The class completed a science observation. | yes | no | no |

## Legacy rolling input

```text
## 2026-01-08
- Child 1: The class completed an art project. [TID:SYN-THREAD-002]
```

## Expected decision

No eligible source Fact matches exactly. Migration must stop and emit a private exception record; it must not add a Fact ID or alter the input.

