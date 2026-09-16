# School-OS implementation plan

**Current branch:** `codex/restart-implementation`, in the existing repository.
**Status:** retained restart MVP operations, contracts, adapters, and examples
are authored and statically reviewed; they remain untested and
unqualified. Q10 is resolved: the linked-piece proposal was rejected and the
delegated assessment retains the single 64 KiB page maximum. No trials may begin
before complete implementation publication and remote verification.

The authoritative [restart plan](docs/plans/restart/PLAN.md) records decisions,
retained scope, explicit deferrals and the
[current execution authorization](docs/plans/restart/PLAN.md#current-execution-authorization).
The [coverage map](docs/plans/restart/implementation/COVERAGE.md) maps every
principle/use case. The [progress log](PROGRESS.md) records completed work units.

All remaining published Q1/Q2 data/index, Q4 discovery and Q6 reuse recommendations
are explicitly approved. Any new architecture still requires approval. D2 generic
save/repair, D7 centralized jobs and D8 packaged lifecycle remain deferred.
The current [page-size assessment](docs/plans/restart/implementation/PAGE-SIZE-ASSESSMENT.md)
records the Q10 decision. A whole record that exceeds 64 KiB blocks without
truncation or an invented overflow format; actual size, I/O and query evidence
may later justify changing the one shared maximum to 128 or 256 KiB. The former
[segment proposal](docs/plans/restart/implementation/SEGMENT-REPRESENTATION-PROPOSAL.md)
is rejected history.

Implement other retained features through clear agent procedures and the approved
small Python standard-library helper subset; do not rebuild the retired runtime.

## Preservation and isolation

[OrgoS Restart Documentation](https://github.com/jeremieguedj/School-OS/releases/tag/orgos-restart-documentation)
is published at fixed annotated tag `orgos-restart-documentation`, targeting
`09f6be151cd549431343b9ebe44a1d03371d2f4f`. The remote branch/tag and release were
verified. This preserves the complete pre-implementation tracked tree, approved
plans, decisions, architecture and frozen evidence. The earlier
`restart-baseline-2026-09-14` remains intact.

The implementation branch was created from that snapshot with a clean working
tree. The old executable runtime, contracts/schemas, installers, wrappers and
legacy validation workflow are retired from active operation; short historical
document pointers and unchanged frozen restart studies preserve useful context.
No private/untracked material is part of cleanup or publication.

## Sequence

1. Finish retained implementation review through at most three bounded Sol
   workers with distinct file ownership. Use no Astra workers. The root agent
   primarily coordinates, resolves escalations and architecture questions, and
   owns integration, publication, privacy and coverage review.
2. Review the complete result against the approved contracts and product
   principles. Perform publication hygiene, commit/push and verify the remote
   implementation revision. Do not execute functional tests before this boundary.
3. Run the explicitly authorized three isolated seven-day school-email trials:
   context-free fresh worker, Gemini Spark browser, ChatGPT Work browser. Use the
   same fixed interval and revision, separate new Drive folders and no inherited
   instances or extracted answers. No outbound brief, personal task-app mutation
   or schedule is authorized by these trials.
4. Audit observable execution, source coverage, knowledge/actions, inefficiencies,
   failures and source-supported query retrieval. Preserve private evidence and
   publish only sanitized results. Report limitations; do not infer compatibility
   from a vendor name or completed batch.

The autonomous goal is not complete at the documentation snapshot or the first
implementation slice. If an external blocker prevents a trial, preserve work and
report it precisely. Broader qualification remains outside the named trial scope.

## Published checkpoint

Accepted implementation material is published at
`972ac4f1023be1aad4003af6a44ffbe527cb0c8f` on `codex/restart-implementation`;
the exact remote revision was verified. This is an incomplete, untested
checkpoint predating the Q10 decision, not the complete-MVP trial gate. The documentation
snapshot remains separate and unchanged.
