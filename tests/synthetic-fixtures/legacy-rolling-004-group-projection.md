# Synthetic legacy rolling-update group-projection fixture

## Private grouping configuration

```yaml
entities: [child_1, child_2, household]
grouping:
  shared_group_id: household
  unscoped_update_group: household
```

## Source record facts

| Fact ID | Source ID | Received day | Scope | Text | Update | Guideline | Action |
|---|---|---|---|---|---:|---:|---:|
| SYN-004-F1 | SYN-THREAD-004 | 2026-01-08 | child_1, child_2 | A shared school event will take place on Friday. | yes | no | no |
| SYN-004-F2 | SYN-THREAD-005 | 2026-01-08 | unscoped | The school announced a community celebration. | yes | no | no |

## Legacy rolling input

```text
## 2026-01-08
- Family: A shared school event will take place on Friday. [TID:SYN-THREAD-004]
- Family: The school announced a community celebration. [TID:SYN-THREAD-005]
```

## Expected decision

The first fact projects to the shared group because it has multiple recognized entities. The second projects to the configured unscoped update group. Both have exactly one eligible match and migration is allowed.

