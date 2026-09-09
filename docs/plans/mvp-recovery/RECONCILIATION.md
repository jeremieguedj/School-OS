# Recovery MVP candidate reconciliation ledger

Recorded: 2026-09-09
Base: `main` at `8d66626` (`bc0128d` runtime baseline plus recovery-plan documentation)
Review lineage: `9357733 -> d7f3ae3 -> 127219b -> cef9190 -> e44c434`

This ledger classifies the stopped connected-runtime lineage as implementation evidence. It does not accept historical status claims or provider conformance.

| Delta | Disposition | Reason |
|---|---|---|
| Bootstrap antecedents `813b254`, `313901a`, `8cff621` | Retain | Create-only admitted-package recovery, finite host contracts, and installed handoff are the smallest coherent bootstrap seam and pass exact-package tests. |
| Source antecedents `c45e791`, `2634810` | Retain | Bounded attachment/direct-resource byte handling and selected extraction callbacks join the accepted source-custody worker without creating a second catalog. |
| `9357733` connected composition | Repair | Retain setup, bootstrap, seven-phase predecessor handoff, and connected tests. Its delivery-coupled runner cannot serve the required early unsent preview and its task construction remains Sheets-specific. |
| `d7f3ae3` source portability repair | Retain | Keeps connected-source imports dependency-free and preserves fail-closed extraction behavior. |
| `127219b` Drive pagination repair | Retain | Complete scoped listing is required for empty-root proof, recovery, and ambiguity detection. |
| `cef9190` receipt-URL repair | Retain | Admits only the observed benign same-object Drive URL decoration and retains exact identity/readback checks. |
| `e44c434` durable-resume repair | Repair | Retain profile selection and fresh-process state recovery. Replace delivery-only composition with an explicit no-reservation preview path now; later replace hard-coded Sheets dispatch and add audio ordering. |
| Lineage changes to root/release plans and `PROGRESS.md` | Supersede | Current recovery documents on `main` own status and scope. Historical implementation claims are not replayed. |
| Older bootstrap/source worktrees and detached snapshots | Archive-only | Their useful deltas are already represented in the reconciled lineage; stacking them would duplicate implementations. |
| Reusing an earlier private candidate root or staging object | Reject | Recovery acceptance requires a newly empty root and independently verified isolated projections. |

The active candidate imports only the code, runtime documentation, scripts, and tests from the reconciled lineage. Rejected and superseded material remains in Git history and is excluded from active routing/package inventory.
