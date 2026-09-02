# Synthetic legacy rolling-update singular-record-date fallback fixture

## Source record metadata

```text
Record received date: 2026-01-08
```

The legacy source record has no per-Fact received-date column and has exactly one record-level local date.

## Source record facts

| Fact ID | Source ID | Scope | Text | Update | Guideline | Action |
|---|---|---|---|---:|---:|---:|
| SYN-005-F1 | SYN-THREAD-005 | child_1 | The class completed its first science observation. | yes | no | no |

## Legacy rolling input

```text
## 2026-01-08
- Child 1: The class completed its first science observation. [TID:SYN-THREAD-005]
```

## Expected decision

The singular record-level date is permitted as the legacy Fact-date fallback. Exactly one eligible Fact matches and migration is allowed.

