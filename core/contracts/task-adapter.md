# Agent-managed task adapter contract

The normative recovery implementation is
`docs/plans/mvp-recovery/TASK-ADAPTER-SPEC.md`. This portable contract exposes
three finite semantic operations:

```text
read_snapshot(request) -> complete normalized snapshot
apply_action(committed_action) -> normalized result and exact readback
reconcile_action(committed_action) -> normalized result and exact readback
```

The user's instance agent owns all provider-native operations and configuration.
School-OS owns canonical task meaning, stable IDs, base/local/remote comparison,
conflict policy, effect identities and Drive checkpoints. No adapter may mutate
a provider until the exact high-level action is current in Drive with outcome
`unknown` and an incremented dispatch attempt.

Provider layouts and API response fields are not part of this contract. A
conformant adapter returns canonical normalized field names, proves all required
collections complete, preserves unrelated provider-owned state, and returns an
exact normalized native readback. Missing or ambiguous evidence blocks.
