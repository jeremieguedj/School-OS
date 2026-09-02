# Test strategy

All fixtures are synthetic. Tests must never require a real household, inbox, Drive instance, task project, or credential.

## Initial test suites

- Source catalog: multi-message order, atomic facts, source coverage, action/guideline separation, and attachment outcomes.
- Task sync: immutable IDs, grouping, provider projection, freeform completion comments, reopen behavior, and source evidence.
- Brief: seven-day received-date grouping, separate news/guidelines/actions, stable sort order, source links, and atomic Fact provenance.
- Installation: manually supplied release package with no GitHub access; tag, commit, manifest version, and released status agree.
- Upgrade: staged release, declared migration, validation, and failed-upgrade preservation.
- Adapter: actual runtime/provider/auth profile capability checks.

The five `legacy-rolling-*` fixtures exercise the deterministic provenance migration's success, zero-match, ambiguous-match, configured-group-projection, and singular-record-date fallback paths. Only the exact-one-match/group-projection/date-fallback fixtures may produce migrated output; the other two must block without changing the input.

Every future behavior change should add a synthetic fixture or expected-output case before modifying a release contract.

## Executable validation

Run the complete dependency-free validation gate from the repository root:

```text
python3 scripts/validate.py
```

The command parses every JSON Schema document, validates the instance template
and release manifest against their corresponding schemas, and discovers the
standard-library `unittest` suites. It also smoke-builds and verifies the exact
committed release package; this check does not require the manifest to have
`status: released`. A conservative tracked-source privacy scan rejects Drive
URLs/identifiers, non-synthetic email addresses, credential markers, and any
newline-separated private needles supplied through `SCHOOL_OS_PRIVATE_NEEDLES`.
Needle values are never stored in the repository or echoed in diagnostics. The
rolling-provenance suite covers allowed
migration paths, fail-closed zero/ambiguous/stale/date/filter cases, invalid
pre-existing references, and a byte-stable idempotent rerun.

`scripts/migrate_rolling_provenance.py` composes a candidate from a JSON plan but
does not write a rolling file. Backup, replacement, and readback remain explicit
caller responsibilities under the migration contract.

Build a deterministic archive from an exact Git ref with:

```text
python3 scripts/build_release.py --ref TAG_OR_COMMIT --version VERSION --output-dir dist
```

The archive has one `School-OS-VERSION/` root, normalized metadata, and an
internal `RELEASE-INVENTORY.sha256`. The adjacent `SHA256SUMS` authenticates the
archive itself. Packaging reads committed blobs from the selected ref and never
copies `.git`, working-tree modifications, prior inventories, or build outputs.
