# Test strategy

All fixtures are synthetic. Tests must never require a real household, inbox, Drive instance, task project, or credential.

## Initial test suites

- Source catalog: multi-message order, atomic facts, source coverage, action/guideline separation, and attachment outcomes.
- Task sync: immutable IDs, grouping, provider projection, freeform completion comments, reopen behavior, and source evidence.
- Brief: seven-day received-date grouping, separate news/guidelines/actions, stable sort order, source links, and atomic Fact provenance.
- Installation: manually supplied release package with no GitHub access; tag, commit, manifest version, and released status agree.
- Upgrade: staged release, declared migration, validation, and failed-upgrade preservation.
- Adapter: actual runtime/provider/auth profile capability checks.

The four `legacy-rolling-*` fixtures exercise the deterministic provenance migration's success, zero-match, ambiguous-match, and configured-group-projection paths. Only the exact-one-match/group-projection fixtures may produce migrated output; the other two must block without changing the input.

Every future behavior change should add a synthetic fixture or expected-output case before modifying a release contract.
