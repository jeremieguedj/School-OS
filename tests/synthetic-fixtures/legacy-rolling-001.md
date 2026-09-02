# Synthetic legacy rolling-update fixture

## Source record facts

| Fact ID | Source ID | Received day | Scope | Text | Update | Guideline | Action |
|---|---|---|---|---|---:|---:|---:|
| SYN-001-F1 | SYN-THREAD-001 | 2026-01-08 | child_1 | The class completed its first science observation. | yes | no | no |

## Legacy rolling input

```text
## 2026-01-08
- Child 1: The class completed its first science observation. [TID:SYN-THREAD-001]
```

## Expected decision

Exactly one eligible source Fact matches after presentation-only normalization. Migration is allowed.

