# Alpha.13 plan review: simplicity and product fit

- Date: 2026-09-07
- Reviewed snapshot: release plan revision 1, committed and pushed as `3acd660`
- Status: historical review; simplicity findings incorporated in plan revision 2
- Method: review against documented personas, use cases, priorities, and
  existing implementation; no private-instance execution performed

## Subsequent disposition

At the user's request, the current [release plan](PLAN.md) now incorporates the
simplicity recommendations directly into its work packages. The user deferred
discussion of the historical-retrieval acceptance addition below; that addition
is not a current work item or release gate. The user subsequently approved the
complete-path development approach; plan revision 3 defines its implementation
milestones and completion checks. Implementation has not started. The review
below preserves the assessment of revision 1; the current plan governs planning
scope.

## Assessment

The reliability objectives are justified. The risk of over-engineering lies
mainly in the breadth of the proposed infrastructure and in making all ten work
packages prerequisites for one release. Several narrowly useful helpers could
otherwise become a general workflow platform before parents see the benefits.

Keep verified manual sending and checkpointed continuation: both are approved
product decisions. Keep losslessness, provenance, exact readback, stable task
identity, parent-edit preservation, and recovery from uncertain effects. The
simplifications below change how these are implemented and sequenced; they do
not weaken their requirements or amend the captured plan.

## Product basis

The [product principles](../../product-principles.md) identify one or two parents
or guardians as the primary users and expect low concurrent-write risk. They
also identify a development agent, an instance agent, and an unfamiliar runtime
as distinct agent roles. These needs lead to different design constraints:

| Persona or use case | Implication for this release |
|---|---|
| Parent managing school communications | Deliver reliable information and actionable exceptions with minimal operating work. |
| Instance agent installing, running, querying, or customizing | Provide exact entrypoints, small helpers, and sufficient saved state to resume. |
| Previously unknown runtime | Discover required functional capabilities and degrade explicitly; do not require exhaustive VM introspection. |
| Development agent | Keep small reusable modules and focused tests; avoid a framework whose abstractions exceed demonstrated operations. |
| Historical retrieval and new applications | Preserve accessible canonical facts and provenance, including facts outside briefs and tasks. |
| Compatible private extensions and upgrades | Maintain contracts and migrate actual changes; new providers need not ship together. |

The documented priority order puts losslessness and determinism ahead of
simplicity, followed by efficiency and portability. Therefore, removing
verification to reduce calls would be the wrong simplification. Removing
redundant metadata, repeated discovery, or unsupported generalization is the
appropriate target.

## Assessment by work package

| Part | Recommendation | Smallest sufficient scope |
|---|---|---|
| 1. Release and installation | Keep; focused hardening | Reuse the existing builder and checksum rules, add installed validation and scaffolding, verify actual assets. |
| 2. Routing and instructions | Keep routing; simplify generation | Start with a small operation-to-recipe map and declared dependencies. Defer a general instruction-packet compiler. |
| 3. Capabilities and planning | Keep functional probes; simplify adaptation | Record required features and a few actionable limits. Use conservative configured batches with bounded reduction on failure. |
| 4. Checkpoints and recovery | Essential; constrain machinery | Use compact operation state and receipts for pending writes/effects. Support sequential resumption before worker orchestration. |
| 5. Ingestion | Essential; focus on demonstrated formats | Build one supported catalog path with exact body copying, provenance joins, bounded work, and explicit attachment outcomes. |
| 6. Reconciliation | Keep; avoid generic merge machinery | Parse supported formats, retain field ownership and needed previous projections, and escalate unresolved conflicts. |
| 7. Manual sending | Essential and approved | One daily operation and delivery policy, manual or scheduled invocation, with sufficient verified overlap prevention. |
| 8. Rendering | Keep; modest presentation controls | One deterministic HTML/text renderer with existing grouping and simple theme values. |
| 9. Tests, metrics, upgrades | Keep; narrow initial infrastructure | Target observed failures and changed schemas, record a small performance baseline, and use the existing staged-upgrade procedure. |
| 10. New adapters | Independent follow-ups | Deliver according to concrete user/runtime demand; do not gate core reliability on every new provider or an offline speech bundle. |

## Where to reduce complexity

### 1. Avoid building an instruction compiler before direct routing is measured

The immediate problem is an agent failing to find or obey an installed recipe.
A short request-to-operation map, exact references, and narrow dependency reads
address that directly. A compiler combining registries, recipe fragments,
capabilities, fingerprints, and runtime variations creates another artifact that
must be generated, versioned, validated, and kept consistent.

Start with direct routing and helpers that own repeated mechanical rules. Add
generated instruction packets only if measured repeated reads or omission rates
remain material. Required runtime behavior must still come from installed
recipes and contracts; this recommendation is not permission to guess missing
instructions.

### 2. Prefer a few meaningful limits to a runtime optimizer

Unfamiliar runtimes need capability discovery. They do not need to expose exact
RAM, token budget, process lifetime, or network topology before every operation.
Some limits are unobservable or change during execution. Trying to model them
all can consume more work than a normal household update.

Probe the operations actually needed, distinguish connector and shell access,
and record limits that change an execution decision. Start with conservative
record/byte bounds, bounded retries, and a simple reduction rule on capacity
failure. If one complete record exceeds a surface's limit, preserve the explicit
blocked outcome rather than shrinking the source. Defer learned throughput
optimization and broad environment benchmarking.

### 3. Keep recovery evidence without creating a workflow engine

Saved progress and unknown-outcome handling are warranted by actual failures.
Begin with one compact operation snapshot, verified artifact references, and
pending-effect receipts. Keep identity stable across attempts and preserve the
last verified checkpoint during updates. Do not introduce a separate journal,
manifest, and history service for every helper when the same evidence can live
in the operation record.

Checkpoint bounded work units and record intent before non-idempotent effects.
Continue to verify every required write. The efficiency goal is fewer redundant
state writes and less evidence printed into context, not reduced verification.

Use the existing single-writer posture. Manual/scheduled overlap is now a real
risk to handle through verified runtime serialization or bounded operational
coordination; an idle flag or a same-name Drive file is not a lock. A distributed
lock service, worker pool, generalized background-process registry, and
cross-runtime cancellation framework are unnecessary for the sequential
baseline. If optional workers are introduced later, track and contain those
specific workers then.

### 4. Preserve task semantics without supporting every possible format

Parent edits, completion history, immutable IDs, and source provenance are
essential. Support the known canonical record/register formats and explicit
legacy migrations. Store the previous synchronized fields needed to recognize
edits, and make ambiguous cases visible.

Defer arbitrary Markdown interpretation and a general multi-writer merge
framework. Batch catalog volumes may reduce provider calls, but select one
bounded representation first; a storage-layout optimizer is not required.
Retain stable logical IDs and retrieval paths regardless of physical grouping.

### 5. Make testing proportional while preserving behavioral coverage

A reset test, stale-write test, lost-send-response test, paginated import test,
and fresh-session resume test give direct value. They can use small fake
adapters at the interfaces exercised by the helpers. Full emulation of every
vendor environment is not necessary for the first release.

Record input/output tokens when observable, tool calls, bytes, elapsed time,
and repeated work for a few representative workloads. Exact peak memory and
vendor-wide certification are useful only where measurable and decision-relevant.
Test actual schema migrations and extension preservation; do not build a
universal migration framework for hypothetical future formats. Mocks establish
code behavior, not production capability conformance, which still requires
observations on the selected execution surface.

### 6. Separate application breadth from foundational reliability

A deterministic brief renderer directly removes repeated agent work. A modest
template and theme configuration are appropriate. A layout engine, multiple
template languages, and extensive presentation customization are not needed.

Google Sheets and native speech may be valuable, especially when they are the
available interaction surfaces in a target runtime. Prioritize an adapter when
it enables a concrete supported deployment. An offline speech distribution
adds model files, platform dependencies, storage demands, and maintenance; it
should be an independent optional deliverable rather than a base-release gate.
Maintain existing optional capabilities while sequencing new implementations.

## Product gaps to watch while simplifying

The plan is heavily oriented toward ingestion and brief delivery. Historical
retrieval and building new applications are also explicit core use cases.
Add a small acceptance case that retrieves a preserved historical fact which
was never a task or a brief item, then resolves its source. This tests the
existing canonical-data purpose; it does not require a new search service or
query framework.

Keep operator complexity out of the parent's normal experience. The agent
should handle mechanical recovery and targeted re-reading where possible.
Surface unresolved source meaning, needed authorization, and actual
provider blockers with concise explanations. A trigger warning should not
automatically become another parent task or a demand to inspect a technical log.

## Recommended first release scope

Prioritize a complete useful path:

1. Install a verified package and resolve exact operation references.
2. Ingest a bounded source set with mechanical body preservation and provenance.
3. Resume after full local-environment loss, reconciling pending effects safely.
4. Preserve canonical task semantics and synchronize a selected configured
   provider through the existing contracts.
5. Render and verify a manual brief without a scheduler, using the same operation
   and delivery rules as scheduling when configured.
6. Retrieve an older source-backed fact independently of brief/task inclusion.
7. Demonstrate focused failure tests, a performance baseline, and a safe upgrade.

Keep provider boundaries and small reusable helpers throughout. Defer the broad
instruction compiler, sophisticated resource optimization, worker management,
general format/merge frameworks, comprehensive benchmark infrastructure, and
optional adapter breadth until evidence or a concrete deployment requires them.

This review originally proposed scope refinements to the captured ten-part
baseline. Their subsequent disposition is recorded above and in the current
release plan. No implementation or private-instance changes are authorized by
this review itself.
