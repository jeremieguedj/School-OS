# Test strategy

All fixtures are synthetic. Tests must never require a real household, inbox, Drive instance, task project, or credential.

## Initial test suites

- Source catalog: multi-message order, atomic facts, source coverage, action/guideline separation, and attachment outcomes.
- Task sync: immutable IDs, grouping, provider projection, freeform completion comments, reopen behavior, and source evidence.
- Brief: seven-day received-date grouping, separate news/guidelines/actions, stable sort order, and source links.
- Installation: manually supplied release package with no GitHub access.
- Upgrade: staged release, declared migration, validation, and failed-upgrade preservation.
- Adapter: actual runtime/provider/auth profile capability checks.

Every future behavior change should add a synthetic fixture or expected-output case before modifying a release contract.
