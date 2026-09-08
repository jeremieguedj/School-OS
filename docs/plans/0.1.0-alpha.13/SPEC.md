# School-OS 0.1.0-alpha.13 implementation specification

- Status: implementation blocked; M1–M3 and M4-001–M4-002 complete, M4-003 awaits observed private-surface evidence; the authorized private instance is an unsupported alpha.11 migration predecessor
- Approved plan: [PLAN.md](PLAN.md), revision 21
- Inventory baseline: `main` at `4617215`, with `release.yaml` declaring
  `0.1.0-alpha.12`
- Target release: `0.1.0-alpha.13`
- Milestone status: M1 complete; M2 in progress; M3 pending; M4 pending

## Authority and boundaries

This specification turns the approved alpha.13 plan into file-level work. The
release plan owns product scope, sequencing, and acceptance criteria. This file
owns the implementation detail linked by that plan. If the two conflict, stop
and reconcile them rather than silently changing a product decision.

This work remains subject to the repository's product principles, architecture,
contracts, privacy boundary, and instruction-ownership rules. It authorizes
repository implementation only; it does not authorize a release, access to a
private instance, provider effects, or production activation.

The selected provider mapping for the first connected journey is the existing
ChatGPT Work, Google Drive, Gmail, and Todoist path, entered manually with no
scheduler and with optional audio disabled. Because the repository has no
executable authenticated adapters for that path, the first three milestones run
the same interfaces through a dependency-free Python 3.12 reference runner, a
clean filesystem-backed synthetic instance, and fake storage, mail, task, and
delivery adapters. This is executable behavioral evidence, not a production
conformance claim. Milestone 4 must observe the exact real surfaces before it
makes one. The core does not depend on those providers.

## Existing implementation inventory

The current repository is mostly contracts and recipes. Documented behavior is
not evidence of executable support.

| Area | Actual alpha.12 support | Alpha.13 disposition |
|---|---|---|
| Release build | `scripts/build_release.py` builds reproducible archives from an exact committed ref and verifies archive paths, inventory, and checksums. | Reuse its algorithms. Move provider-independent verification into the shared package so installed validation does not call Git. Keep Git tree reading and archive construction in the development script. |
| Repository validation | `scripts/validate.py` validates selected schemas/templates, runs the privacy scan, smoke-builds `HEAD`, and runs 77 standard-library tests. | Modify to call shared validators and cover every new schema, registry, template, migration, and behavioral suite. Keep it as the complete repository gate. |
| Installed validation | No installed-package command exists. | Add `scripts/validate_installed.py`; it must use only the standard library and supplied package/instance files. |
| Instance scaffolding | Onboarding is prose; templates contain placeholders; no scaffolder or installation manifest exists. | Add deterministic scaffolding and an installation-manifest schema/template. Preserve user confirmation and provider-returned references as inputs. |
| Routing and reference resolution | `START-HERE.md`, `templates/BOOTSTRAP.md`, recipes, and string references provide manual routing. There is no operation registry or executable identity/type/location check. | Add the small registry and resolver specified below; keep recipes authoritative for dependencies, capabilities, effects, and stop conditions. |
| Capability validation | `schemas/capability-profile.schema.json` and `scripts/validate_capability_profile.py` validate status and operation/surface membership. Limits and verification are opaque strings; scheduled fields are mandatory at the profile root. | Reuse the fail-closed validation, add structured decision-changing observations, allow scheduler-free manual profiles, separate authentication health, and add deterministic execution-plan tests. |
| Operation state | `templates/state/operation-state.yaml` has only `idle`, `active_operation`, last success, and last error. There is no schema, transition validation, attempt history, effect intent, or recovery implementation. | Replace the placeholder for new installs with JSON state and immutable checkpoint records. Migrate existing instances only in M4. |
| Daily/manual execution | `daily-run.md` is a seven-phase prose recipe. `manual-daily-run.md` currently permits production sending only by scheduler `run-now`; there is no executable daily pipeline. | Make both manual and scheduled entrypoints invoke the same operation. Permit a qualified direct manual surface without a scheduler. Keep scheduling an optional trigger. |
| Source catalog | The contract requires raw UTF-8 Markdown and two independent comparisons. `validate_source_record.py` checks adapter body strings against a heading-delimited Markdown section. It does not build records, validate facts/coverage, verify persisted bytes, or safely frame delimiter-like body text. | Replace its parser with the versioned, byte-counted catalog codec below; retain its direct equality rule and legacy-read support. Add builder, coverage, readback, and identity checks. |
| Canonical facts/knowledge | `fact.schema.json`, a decision table, synthetic prose fixtures, and one rolling-provenance migration exist. No general parser, serializer, index, guideline, or rolling-update builder exists. | Reuse fact meaning and Migration 0001. Add structured extraction results and deterministic canonical/derived builders. |
| Canonical tasks | The prose contract and `action-items.md` template contain more fields than `task.schema.json`; no reconciliation code exists. | Make the schema match the contract, use a structured canonical register, preserve a migration reader for the supported legacy table, and implement stable-ID reconciliation. |
| Provider state/task sync | `provider-state.schema.json`, `task-sync.md`, and the Todoist mapping are descriptive. The schema lacks last synchronized projections and complete binding/history detail. | Extend provider state and add a generic task port plus mechanical reconciliation. Keep Todoist mapping provider-specific and private bindings durable. |
| Brief/delivery | Rendering and delivery are prose plus a short expected-output fixture. There is no brief-input schema, renderer, delivery-ledger schema, or executable duplicate guard. | Add deterministic HTML/plain-text rendering, durable delivery intent/result records, a fake send sink, and unknown-effect reconciliation. |
| Adapters | Mail, task, scheduler, and runtime adapters are Markdown mappings. The optional ElevenLabs worker is the only provider-calling runtime code. No storage adapter is implemented. | Add narrow Python protocols and fakes for M1–M3. Do not label Markdown mappings executable. Leave optional audio behavior independent; adapt it only if selected in M4. |
| Upgrade/migration | `system-upgrade.md`, Migration 0001, its Python transformer, and tests cover the existing rolling-provenance change and two upgrade coordination modes. | Reuse them. Add only migrations required by actual alpha.13 state/configuration/record changes, with legacy readers and fail-closed exceptions. |
| Tests | Current executable tests cover release bytes, schema basics, capability failure, Migration 0001, raw-body equality, audio, and prose assertions. No connected operation or fresh-process recovery test exists. | Retain useful unit tests; make connected artifact/effect tests the primary evidence. Prose assertions remain narrow regression checks only. |
| Local build artifacts | Ignored `dist/` contains alpha.12 artifacts but is not tracked or authoritative. | Never use it as the candidate source. Build from an exact committed ref into a fresh temporary directory. |

### Existing files to retire from active behavior

Retirement means “no longer authoritative for new execution,” not immediate
deletion. Preserve migration inputs until M4 upgrade checks pass.

- Retire the scheduler-only rule in `core/operations/manual-daily-run.md` and
  corresponding assertions in `tests/test_manual_daily_run_contract.py`.
- Retire `idle` as sufficient proof of exclusive admission. The state record is
  evidence only; admission also requires a declared serialization mode.
- Retire heading-only raw-body framing in `scripts/validate_source_record.py`
  for newly written records. Keep a fail-closed legacy reader.
- Retire `templates/state/operation-state.yaml` for new installs after the JSON
  state template is validated. Preserve it as a migration input until M4.
- Retire the incomplete `configuration.schema.json` from active template
  validation after dedicated household, integration, policy, and daily-values
  schemas exist.
- Retire recipe-substring tests as evidence that an operation works. They may
  continue to protect a small number of policy phrases.

## Cross-cutting implementation design

### Package layout and responsibilities

Add a standard-library-only `school_os/` package. Do not add a workflow engine,
plugin framework, database, worker pool, or dependency installer.

| File | Responsibility | Primary inputs | Primary outputs |
|---|---|---|---|
| `school_os/contracts.py` | JSON/YAML loading, the supported JSON-Schema subset, canonical JSON bytes, SHA-256, and common validation errors. | Bytes or paths plus schemas. | Parsed mappings, canonical bytes, hashes, diagnostics. |
| `school_os/package.py` | Provider-independent archive, checksum, inventory, version, and extracted-tree verification. | Archive, `SHA256SUMS`, extracted root, release manifest, transported source-identity evidence. | `PackageVerification` or fail-closed diagnostics. |
| `school_os/install.py` | Scaffold confirmed configuration/state, build installation manifest, and validate/read back installed files. | Verified package, confirmed settings, selected adapters, observed object references. | Candidate files and verified installation manifest; no provider effects itself. |
| `school_os/references.py` | Resolve exact references and verify identity, type, and containment through the selected storage port. | `ObjectReference`, expected role, instance root. | Verified `ResolvedObject` or `ambiguous`/`invalid` result. |
| `school_os/capabilities.py` | Validate profiles, authentication health, conditional requirements, and conservative batch plans. | Profile, operation, entrypoint, selected features, requested bounds. | `ExecutionPlan` or specific blocked/degraded result. |
| `school_os/adapters.py` | Define small structural protocols and normalized result records for storage, mail, tasks, delivery, and optional scheduling. | Provider-neutral requests. | Provider-neutral pages, objects, snapshots, writes, and effect outcomes. |
| `school_os/operations.py` | Operation admission, legal state transitions, attempts, immutable checkpoint chaining, guarded writes, effect intents, and recovery selection. | Operation state/checkpoints plus adapter observations. | Next safe step and verified checkpoint/state candidates. |
| `school_os/catalog.py` | Stable source identity, normalized source validation, versioned catalog parsing/serialization, mechanical raw-body insertion, coverage validation, and index candidates. | Complete conversations and validated extraction results. | Exact record bytes, Fact records, coverage, hashes. |
| `school_os/tasks.py` | Canonical task/register parsing, stable identity, source reconciliation, provider projection, parent-edit preservation, and binding updates. | Action Facts, canonical tasks, provider snapshot/state, policy. | Canonical candidate, provider patch plan, review cases. |
| `school_os/brief.py` | Build/validate brief input and deterministically render HTML and plain text. | Verified current-run facts, guidelines, tasks, grouping/theme config. | Rendered bytes plus counts and content hashes. |
| `school_os/daily.py` | Execute the one sequential daily phase order using injected ports and interpreter results. It owns no provider-specific mapping. | Resolved instance, execution plan, ports, semantic interpreter. | `OperationResult` and durable artifacts/evidence. |

The existing scripts become thin command wrappers. `scripts/build_release.py`,
`validate_instance.py`, and `validate_capability_profile.py` import shared code
without changing their CLI exit meanings. Add:

- `scripts/validate_installed.py PACKAGE_OR_EXTRACTED_ROOT [--instance-root …]`;
- `scripts/scaffold_instance.py --answers ANSWERS.json --references REFERENCES.json --output DIR`;
- `scripts/run_operation.py --instance INSTANCE_REFERENCE --operation OPERATION [--entrypoint manual|scheduled]` for runtimes that can execute Python; and
- `scripts/run_synthetic_journey.py` only if the end-to-end unittest cannot
  provide an equally reproducible operator-facing check.

Provider-capable runtimes without Python may implement the same schemas and
state transitions directly through their adapter surface. They must pass the
same behavior/conformance fixtures; they do not get weaker acceptance criteria.

### Core interface records

Use frozen dataclasses or typed mappings at Python boundaries and JSON at
durable/exchange boundaries. Every operation returns one of `COMPLETE`,
`NEEDS_CONTINUATION`, `BLOCKED`, or `CANCELLED` with an operation ID, attempt ID,
current phase, checkpoint reference, and concise reason.

The adapter protocols expose only the calls needed by the connected path:

```text
StoragePort
  read(reference) -> ReadResult(bytes, identity, kind, parent, mime, version)
  list_scoped(parent, page_token) -> Page[ObjectMetadata]
  create(parent, name, bytes, mime) -> EffectResult
  replace(reference, bytes, expected_version?) -> EffectResult

MailPort
  search(scope, page_token) -> Page[ConversationIdentity]
  read_conversation(identity) -> CompleteConversation
  read_attachment(identity) -> AttachmentRead
  send(DeliveryRequest) -> EffectResult
  find_delivery(DeliveryLookup) -> CompleteMatchSet

TaskPort
  read_snapshot(scope, page_token) -> Page[ProviderTask]
  read_completed(scope, page_token) -> Page[ProviderTask]
  read_activity(scope, page_token) -> Page[ProviderEvent]
  read_comments(provider_id, page_token) -> Page[ProviderComment]
  read_task(provider_id) -> ProviderTask
  find_by_canonical_id(task_id) -> CompleteMatchSet
  create_task(ProviderTaskCandidate) -> EffectResult
  apply_patch(provider_id, ManagedPatch) -> EffectResult
  write_comment(provider_id, SystemComment) -> EffectResult

SchedulerPort
  inspect(schedule_reference) -> SchedulerState
  trigger(schedule_reference) -> EffectResult
```

`EffectResult.outcome` is exactly `confirmed`, `definitely_not_applied`, or
`unknown`. “Request accepted” is evidence, not automatically `confirmed`; each
adapter declares what readback establishes confirmation. A caller may retry only
`definitely_not_applied`. Unknown effects go through reconciliation.

The semantic interpreter is a narrow boundary rather than an adapter framework:

```text
interpret(ExtractionPacket) -> ExtractionResult
```

The packet contains code-assigned source segments with stable segment IDs and
UTF-8 byte boundaries plus compact existing-record/task context. The result
references those segments and supplies fact text/flags/scope, task relationship
suggestions, and coverage decisions. Code supplies provider IDs, raw bodies,
timestamps, byte boundaries, record IDs, Fact IDs, task IDs, links, and
serialization. The deterministic fixture interpreter returns checked-in
expected results; semantic accuracy is measured separately from mechanical
correctness.

### Schemas and canonical encodings

All new JSON is UTF-8, ends with one newline, and uses sorted keys and compact
separators when a content hash or idempotency key depends on its bytes.

Add these schemas:

- `schemas/object-reference.schema.json`: opaque storage adapter/object ID,
  expected `file` or `folder` kind, permitted ancestor/root reference, optional
  MIME type, and optional provider version evidence;
- `schemas/operation-registry.schema.json`: version plus a map from stable
  operation name to exact installed recipe path only;
- `schemas/installation-manifest.schema.json`: package version/source identity,
  archive and inventory hashes, intended relative paths, returned object
  references, per-file hashes, and verification status;
- `schemas/operation-state.schema.json`: current operation pointer/status,
  serialization mode/evidence, checkpoint reference/hash, and last terminal
  summary;
- `schemas/operation-checkpoint.schema.json`: logical operation/attempt identity,
  pinned release, scope/configuration fingerprint, phase/unit state, artifact
  references/hashes, effect records, verification evidence, blocker, predecessor
  reference/hash, and sequence number;
- `schemas/source-conversation.schema.json`: complete ordered message identities,
  metadata, exact plaintext bodies, attachments, pagination/scope evidence;
- `schemas/extraction-result.schema.json`: byte-span-based candidates, flags,
  entity scopes, coverage decisions, attachment outcomes, and review cases;
- `schemas/canonical-tasks.schema.json`: task-register version and array of the
  complete logical tasks described by `core/contracts/tasks.md`;
- `schemas/brief-input.schema.json`: local window, entity order, news,
  guidelines, tasks, links, labels, theme, and canonical input hashes; and
- `schemas/delivery-ledger.schema.json`: delivery key, variant, intended content
  hash, recipients/config fingerprint, intent time, outcome, provider identity,
  and verification evidence.

Modify existing schemas as follows:

- `capability-profile.schema.json`: make scheduler fields conditional on a
  scheduled entrypoint; add structured read/pagination/file-transfer/local-exec
  observations, separate authentication health, network-path statuses, byte and
  record limits with explicit unknowns, adapter versions, and expiry/recheck
  triggers.
- `task.schema.json`: add owner, last supporting-source date, provider bindings,
  lifecycle/completion history, projection status, revision, and last modified
  evidence. Preserve separate source and parent-planned dates.
- `provider-state.schema.json`: require unique bindings, provider revision,
  last synchronized managed projection and its hash, cursor evidence, and
  verified readback. Provider-owned fields remain outside the managed
  projection.
- `instance.schema.json`: add exact operation registry, capability profile,
  installation manifest, operation state, delivery ledger, and canonical task
  references. References use the object-reference contract for new instances.
- Replace the catch-all use of `configuration.schema.json` with dedicated
  `household`, `integrations`, `policies`, and machine-readable daily-values
  validation that matches the actual templates.

The approved `daily-run-personal-values.md` remains the single private daily
companion. Give it strict YAML front matter for machine-readable references and
validated presentation values; the prose below remains explanatory. Adapter
selection, credentials, provider bindings, and operation procedure stay out of
that file.

Use these canonical formats for the reference implementation:

- Source catalog records remain raw UTF-8 Markdown. New records declare format
  version 2. Each raw message frame includes immutable message ID and exact
  UTF-8 body byte length; the parser reads that exact count before looking for
  the next frame. Delimiter-like headings inside a body are therefore inert.
  The serializer inserts the adapter-returned body bytes mechanically.
- The canonical task register becomes versioned JSON matching
  `canonical-tasks.schema.json`. The existing Markdown table is a supported
  legacy input and optional derived human view, not a second authority.
- Derived guidelines, rolling updates, and run indexes use versioned structured
  JSON as generator inputs/state. Human-facing Markdown or HTML views are
  derived and carry their input hashes and generator version.

Legacy catalog v1 is readable only when its framing is unambiguous and every
body can be reverified against the source adapter. A changed record is rewritten
as v2 after both losslessness gates pass. Ambiguous legacy framing blocks and
requires a fresh complete source read; it is never guessed.

### Identity and replay rules

- `operation_id` is created once at admission and survives every attempt.
  `attempt_id` is new for each invocation/resumption.
- Source `record_id` is derived from adapter ID plus immutable conversation
  identity. Ordered message IDs determine membership; filenames never do.
- Code assigns a Fact ID from record ID, immutable source message ID, source
  byte span, and candidate kind. An existing matching span/kind keeps its Fact
  ID. The interpreter never invents IDs.
- A new task ID is derived from its opening action Fact ID. New supporting Facts
  preserve the existing ID only through an explicit validated task relationship;
  ambiguous relationships become review cases. Title equality is never
  identity.
- Provider objects carry or bind the canonical task ID. Create reconciliation
  searches that identity completely and blocks on multiple matches.
- Identical verified inputs/configuration/generator versions produce identical
  canonical candidates, brief bytes, content hashes, delivery keys, and no
  unintended mutations.
- A delivery key is independent of attempt ID. It is derived from instance ID,
  operation kind, local delivery window, and policy-controlled variant. A
  correction/resend requires explicit authorization and a distinct variant.

### Durable and local ownership

| State | Durable owner | Notes |
|---|---|---|
| Installed release, manifest, exact references, capability profile, installation manifest | Private instance storage | Production authority; Git checkout and local extraction are not runtime authority. |
| Source catalog, canonical Facts/tasks, derived indexes, delivery ledger, operation state/checkpoints | Private instance storage | Must survive total loss of local files and conversation. |
| Mail source and Sent objects | Selected mail provider | Evidence/source, not a replacement canonical knowledge store. |
| Parent edits and task object/activity | Selected task provider | Parent-facing projection; canonical identity/history remain in the instance. |
| Extracted package, source/extraction packets, rendered candidates, caches | Local run directory | Recoverable/discardable. Persist only verified artifacts referenced by a checkpoint. No local database. |
| Reusable code, schemas, recipes, synthetic fixtures | GitHub release | Never contains private instance material. |

## Operation state, checkpoints, and recovery

### State model

The private `operation-state.json` is the admission pointer. Each successful
checkpoint is an immutable, create-only JSON object under the operation's state
area. It references the previous checkpoint ID and SHA-256. After creating and
reading back a checkpoint, update the admission pointer through a guarded write.
If the pointer update is uncertain, recovery performs a scoped, paginated search
for that operation ID and accepts only one valid longest checkpoint chain;
ambiguity blocks.

One instance has at most one active mutating operation. Read-only inspection may
coexist but cannot update state. Admission must record one of:

- `native_conditional`: the storage adapter atomically conditions the admission
  pointer update on observed version evidence;
- `runtime_serialized`: the verified runtime/scheduler serializes the exact
  instance key and exposes sufficient readback; or
- `attended_single_writer`: scheduler-free manual execution, or a bounded manual
  run with every competing scheduler verified paused, one actor identified, and
  other mutators explicitly excluded for the attempt.

A shared `idle` value alone is never serialization evidence. A distributed lock
service is not required. When manual and scheduled entrypoints coexist, use the
same runtime serialization queue or pause/verify the scheduler for an attended
manual attempt; otherwise report `BLOCKED`.

### Legal transitions

| From | To | Required evidence |
|---|---|---|
| no current operation, `complete`, or `cancelled` | `running` | Admission checks, serialization evidence, pinned release, scope and configuration fingerprint, first attempt/checkpoint. |
| `running` | `running` | One bounded unit or phase checkpoint verified; no phase is claimed complete without its acceptance evidence. |
| `running` | `needs_continuation` | Planned boundary, approval pause, or capacity reduction recorded after all invoked effects are checkpointed. |
| `needs_continuation` | `running` | New attempt, compatible release/configuration, refreshed capabilities/auth, serialization reacquired, pending effects reconciled. |
| `running` or `needs_continuation` | `blocked` | Specific integrity, identity, authorization, capability, repeated non-progress, conflict, or unresolved-effect evidence. |
| `blocked` | `running` | Blocking condition is observed resolved; ordinary recovery gates still pass. |
| `running` | `complete` | Every required phase verified, no pending/unknown effect, final canonical/provider readbacks pass, then eligible cursors commit. |
| `running`, `needs_continuation`, or `blocked` | `cancelled` | Explicit cancellation, no unresolved external effect, and durable cancellation checkpoint. Cancellation never means rollback. |

`complete` and `cancelled` are terminal for that operation ID. Start a new
logical operation for later work. Partial execution is never `complete`.

### Checkpoint boundaries

Checkpoint after preflight/admission, after every fully verified source batch,
after each canonical guarded write, before and after every consequential
provider effect, after rendering/readback, and immediately before and after
cursor/delivery-ledger finalization. Also checkpoint before a known execution
limit, handoff, approval pause, or planned stop.

A checkpoint stores compact IDs, counts, hashes, references, and outcomes—not
complete source bodies or rendered content. Those bytes live in their durable
artifacts. `completed_units` contains only verified stable unit IDs;
`remaining_work` contains the next page token, ordered source IDs, or phase
marker needed to continue.

### Guarded writes and uncertain effects

For a canonical/storage write:

1. Read exact identity, metadata, and complete current bytes.
2. Validate and construct the complete candidate.
3. Check source/history/parent-field preservation and expected version.
4. Persist an effect intent containing target, previous evidence, and candidate
   hash.
5. Write through the adapter, read the exact target back, and compare identity
   and complete bytes.
6. Record `confirmed`; on an unknown response, reread and reconcile. Retry only
   when the adapter can prove `definitely_not_applied`. Drift or ambiguity
   blocks.

For task creation, the intent includes canonical task ID and managed projection
hash. Recovery completes a provider-wide scoped lookup by canonical ID: zero
matches may be retried only after the adapter proves the earlier call was not
applied, one exact match is adopted and bound, and multiple/conflicting matches
block. Update, move, completion, reopen, and system-comment recovery read the
known object plus applicable activity/comments and compare the intended managed
projection/effect identity.

For delivery, persist the delivery key, content hash, recipient/configuration
fingerprint, and intent before sending. Recovery first checks the durable ledger,
then performs the adapter's complete Sent lookup. One exact verified match is
recorded; an existing ledger result suppresses a duplicate. Zero matches permits
a retry only when the adapter can establish `definitely_not_applied` after its
declared consistency window. Multiple matches or an inconclusive lookup is
`BLOCKED`, never a blind resend.

### Failure outcomes and batch reduction

- Use `NEEDS_CONTINUATION` for a healthy planned boundary or resumable approval
  pause with a known next step.
- Use `BLOCKED` for missing/ambiguous references, stale authentication, required
  capability failure, unsupported oversized single input, source losslessness
  failure, conflicting provider state, repeated non-progress, or an unresolved
  effect.
- Optional unavailable behavior is `degraded` only when the recipe and private
  policy both permit it. Required task sync or delivery is never skipped.
- On a capacity failure, halve the configured record bound, never below one,
  and constrain bytes to the observed maximum. If the same first unit fails
  twice at the minimum bound, block with `oversized_unit` or `non_progress`.
  Never truncate a source.

## Milestone 1 — Install a minimal candidate in a clean test instance

**Status:** complete (M1-001 through M1-006).

### Deliverable

A package built from an exact commit can be verified and scaffolded into a
fresh temporary instance without Git, network access, dependency downloads, or
conversation state. It resolves `daily-run` and its exact private references,
produces a scheduler-free manual execution plan, and fails specifically when a
required capability is missing.

### Ordered tasks

**Task status:** M1-001 through M1-006 complete.

**Sequencing resolution (2026-09-07):** M1-002's installed validator must
verify the registry as a required payload, but M1-003 creates the registry and
its schema. The authorized read-only GPT-5.6 Sol High consultation found that
making the registry optional would weaken the approved fail-closed package
gate. M1-003 therefore precedes M1-002, and M1-002 now depends on both
M1-001 and M1-003. Installed validation must pass with Git unavailable and
must fail if it attempts to invoke Git.

| ID | Depends on | Work and affected files | Observable acceptance |
|---|---|---|---|
| M1-001 | — | Set `release.yaml` to the alpha.13 candidate version with `status: unreleased`; create `school_os/contracts.py` and `school_os/package.py`; refactor `scripts/validate_instance.py`, `scripts/build_release.py`, and `scripts/validate.py` to reuse them without changing safe build behavior. | Existing tests remain green; exact-ref builds identify alpha.13; package verification runs against an extracted package with `.git` absent. |
| M1-003 | M1-001 | Add `core/operations/registry.json`, its schema, `school_os/references.py`, object-reference schema, and resolver tests. Update `templates/BOOTSTRAP.md` and instance manifest/template references. | The registry validates and every mapped recipe is a safe installed regular payload file; `daily-run` resolves the installed recipe and exact objects among multiple synthetic instance/release lookalikes; wrong type, parent/root, identity, MIME, version, or ambiguity blocks. |
| M1-002 | M1-001, M1-003 | Add installed validation command and tests: `scripts/validate_installed.py`, `tests/test_installed_validation.py`. Validate manifest/version/status, archive/inventory evidence when supplied, all managed payload hashes, schemas, registry, and required files; do not run repository-only tests or Git commands. Permit `unreleased` only behind an explicit candidate-test flag. | A clean exact-ref candidate containing the completed M1-003 registry and schema passes offline in explicit candidate mode with `.git` absent and Git unavailable; production mode rejects `unreleased`. Missing registry/schema/mapped recipes, invalid registry data, changed bytes, undeclared or missing files, version disagreement, invalid supplied archive/checksum evidence, or any attempted Git invocation fail specifically. |
| M1-004 | M1-003 | Add dedicated configuration schemas, YAML-front-matter validation for `daily-run-personal-values.md`, installation-manifest schema/template, `school_os/install.py`, and `scripts/scaffold_instance.py`. | Confirmed synthetic answers and observed references produce byte-stable, schema-valid files with no unresolved placeholders; missing answers or fabricated references fail before output acceptance. |
| M1-005 | M1-001, M1-004 | Extend the capability schema/validator and add `school_os/capabilities.py`. Update templates and capability contracts for conditional scheduler requirements, auth health, network paths, structured limits, and manual execution. | A manual profile with storage/mail/tasks and no scheduler qualifies; a scheduled profile still requires scheduler evidence; unknown limits are constrained, never unlimited; missing required capability yields a named blocker. |
| M1-006 | M1-002–M1-005 | Add synthetic installation answers/references/corpus, filesystem fake storage, fixture mail/task adapters, send sink, and reproducible setup in `tests/support/` and `tests/synthetic-fixtures/alpha13/`. | A fresh process installs and resolves the candidate using only extracted files. Test output identifies exact installed paths/hashes and the next operation; it performs no mail/task/send effect. |

**M1-004 implementation note (2026-09-07):** `scaffold_instance.py` writes and
validates only a local candidate directory. It requires an already verified
package/archive pair, confirmed answers, and structural observed-reference
evidence. `school_os.install.verify_candidate_readback` is the separate
acceptance gate: it resolves every declared returned object and compares exact
bytes through the storage port before changing the manifest outcome to
`verified`. This keeps fabricated or unreadable provider references from being
accepted without making the scaffolder perform provider effects.

### Milestone check

M1 completes only when M1-001 through M1-006 pass from a clean checkout and the
release plan is updated with evidence. It does not claim that daily-run behavior
or any real provider is conformant.

## Milestone 2 — Connect a complete normal operation

**Status:** complete (M2-001–M2-007 complete).

### Deliverable

The M1-installed synthetic instance runs one direct manual `daily-run` through
the actual persisted outputs of every predecessor stage: discovery, catalog,
knowledge/tasks, task projection, brief rendering, send sink, final evidence,
and eligible cursors. No hand-edited or separately prepared intermediate file
may make the scenario pass.

### Ordered tasks

| ID | Depends on | Work and affected files | Observable acceptance |
|---|---|---|---|
| M2-001 | M1 complete | Add operation-state/checkpoint schemas/templates and `school_os/operations.py`; update instance/file-map templates and state docs. | Legal transitions and checkpoint hashes validate; illegal skips, completion with a pending phase/effect, and corrupt predecessor chains fail. |
| M2-002 | M2-001 | Add source/extraction schemas and `school_os/catalog.py`; replace new-record framing in `scripts/validate_source_record.py`; update source contract/recipe and synthetic corpus. | Complete paginated fixture output becomes one stable v2 record; raw bodies with heading/delimiter text round-trip exactly; source-to-record equality and intended-to-persisted bytes are independently proved before indexing. |
| M2-003 | M2-002 | Expand fact/task/provider schemas; add `school_os/tasks.py` canonical reconciliation and structured derived knowledge builders; update task/source contracts and templates. | Expected update, guideline, and action are source-linked; guidelines never become tasks; task/register/index outputs validate and are rebuildable from verified Facts. |
| M2-004 | M2-001, M2-003 | Add task protocol/fake behavior, pull-first provider reconciliation, managed projection hashes, bindings, guarded provider writes, and `task-sync.md` updates. | One provider task is created with the canonical ID, read back, bound once, and reflected in durable canonical/provider state; unrelated provider fields remain unchanged. |
| M2-005 | M2-003 | Add brief-input/delivery-ledger schemas, `school_os/brief.py`, default HTML/plain templates/theme, expected files, and brief/delivery recipe updates. | Identical inputs render byte-identical HTML/text with separate ordered sections, escaped unusual text, source links, empty states, and mobile-readable fixtures. Send sink returns one verified message and ledger entry. |
| M2-006 | M2-001–M2-005 | Add adapter protocols and `school_os/daily.py`; add/update thin `run_operation` entrypoint; revise `daily-run.md`, `manual-daily-run.md`, capability/adapter docs, and manual contract tests so manual and scheduled triggers share the same operation. | A scheduler-free qualified manual run executes every required phase. Scheduler capability is not requested. A scheduled entrypoint uses the same function and adds scheduler-specific admission checks. |
| M2-007 | M2-006 | Add `tests/test_connected_daily_run.py` using only M1 installer output and predecessor artifacts. Record expected artifact/effect hashes in synthetic fixtures. | The connected run accounts for every in-scope source and phase, verifies catalog/task/brief/delivery, commits cursors last, ends `COMPLETE`, and fails if any intermediate artifact is substituted. |

**M2-001 implementation note (2026-09-07):** New candidate instances carry a
schema-valid `operation-state.json` and file-map entry, both covered by the
installation-manifest hash/readback gate. Checkpoints are create-only records;
their canonical bytes are hashed into the successor pointer. The state module
validates the approved transition table, recipe-supplied completion phases, and
pending/unknown-effect gates without duplicating daily-operation policy. This
does not advance `data_schema_version` or claim alpha.12 upgrade compatibility:
Migration 0002 remains M4 work.

**M2-002 implementation note (2026-09-07):** `school_os.catalog` uses a
byte-counted v2 Markdown frame for each adapter-returned UTF-8 body. It proves
source-to-record equality separately from intended-to-persisted byte equality;
legacy heading framing remains readable only for migration input.

**M2-003 implementation note (2026-09-07):** `canonical-tasks.json` is the
versioned canonical register. `school_os.tasks` derives source-linked
guidelines, rolling updates, and stable action tasks from validated Fact spans;
guidelines fail if treated as actions, and task titles are never identity.

**M2-004 implementation note (2026-09-07):** Provider reconciliation pulls a
complete synthetic snapshot first, resolves canonical IDs without title matching,
records a managed-projection hash before create/patch, and accepts bindings only
after exact readback. Parent/provider-owned fields are not part of the patch.

**M2-005 implementation note (2026-09-07):** `school_os.brief` deterministically
renders the versioned input contract to escaped HTML/plain text. The delivery
ledger confirms a content-hash/key once through the send sink and blocks repeats.

**M2-006 implementation note (2026-09-07):** `school_os.adapters` now exposes
provider-neutral storage, mail, task, and optional scheduler protocols with
normalized complete-read, pagination, and effect-result records. The shared
`school_os.daily.run_daily` qualifies the exact entrypoint before any phase,
requires operation/attempt identities and verified outputs for all seven phases,
and adds scheduler admission only for a scheduled entrypoint. The thin Python
`scripts/run_operation.py` is synthetic-only until a selected authenticated
adapter host binds real stage callables; it makes no provider-effect claim.

**M2-007 implementation note (2026-09-07):**
`tests/test_connected_daily_run.py` builds/extracts the exact current package,
scaffolds an M1 synthetic instance, and makes all seven manual stages consume
the predecessor's read-back artifact. The synthetic fixture records verified
hashes for discovery, catalog, Facts/knowledge/tasks, provider state, rendered
briefs, delivery ledger, final evidence, and the last-written eligible cursors.
Altering the catalog artifact between stages blocks before task sync or delivery.

### Milestone check

M2 completes only after the connected test proves stage-to-stage custody. Unit
tests and recipe wording cannot substitute. The test sink is not evidence that
Gmail, Todoist, Drive, or a scheduled runtime conforms.

## Milestone 3 — Prove recovery and safe repeated execution

**Status:** complete (M3-001–M3-006).

### Deliverable

Fresh processes with empty local run directories recover solely from the
installed release, exact private references, provider state, operation pointer,
and immutable checkpoints. They continue or block safely without duplicate
catalog history, tasks, comments, or delivery.

### Ordered tasks

| ID | Depends on | Work and affected files | Observable acceptance |
|---|---|---|---|
| M3-001 | M2 complete | Complete recovery/admission logic in `school_os/operations.py` and daily-run entrypoint; add fresh-process harness and checkpoint-chain discovery. | Planned batch stop returns `NEEDS_CONTINUATION`; a new process resumes the same operation ID with a new attempt ID and completes after local files are deleted. |
| M3-002 | M3-001 | Add storage-write fault injection and catalog/index recovery cases in `tests/test_operation_recovery.py`. | Interruption after record creation but before index/pointer update adopts verified bytes, publishes one index entry, and never duplicates/renumbers Facts. |
| M3-003 | M3-001 | Add task create/update/comment fault injection, last-projection comparison, and parent-edit cases. | Lost task-create response binds exactly one existing provider task; replay creates none. Parent title/due/group/progress changes allowed by policy and completion history survive source updates; conflicting managed edits become review cases. |
| M3-004 | M3-001 | Add lost-send response, Sent lookup, delivery-ledger, correction variant, and duplicate-entrypoint cases. | Interruption after accepted send yields one delivery after recovery; unchanged replay and overlapping manual/scheduled admission do not send again; an inconclusive Sent lookup blocks; an authorized correction uses a distinct key. |
| M3-005 | M3-002–M3-004 | Add release/configuration fingerprint change, stale-auth, capacity reduction, minimum-unit non-progress, cancellation, and terminal-state tests. | Compatible resumption continues; material configuration/release change requires reconciliation; oversized source is never truncated; pending unknown effects prevent cancel/complete. |
| M3-006 | M3-005 | Update recipes/contracts/tests README with the proven transition and recovery behavior; record compact expected evidence. | A clean full suite demonstrates all M3 interruption points and verifies durable state after each fresh-process restart. |

**M3-001 implementation note (2026-09-07):** `school_os.operations`
discovers one valid longest immutable checkpoint chain and rejects ambiguity;
resumption requires the same operation ID, a new attempt ID, and an exact
predecessor pointer. `school_os.daily` can checkpoint a planned boundary as
`NEEDS_CONTINUATION` and resume after a durable predecessor output. A new Python
process completes after discardable local output is deleted.

**M3-002 implementation note (2026-09-07):** `recover_catalog_index` adopts a
record only after independent source and persisted-byte verification. It makes
one stable index row containing unchanged Fact IDs, is idempotent on replay,
and blocks corrupted bytes, duplicate rows, or conflicting provenance.

**M3-003 implementation note (2026-09-07):** Task replay adopts a lost create
by canonical ID, and comment recovery adopts exactly one immutable effect after
lookup. Parent-edited title/group remain untouched and become review cases.

**M3-004 implementation note (2026-09-07):** Delivery now persists a pending
intent before sending, reconciles a lost response through exactly one matching
delivery, blocks inconclusive/ambiguous lookup, and prevents duplicate intent.
Correction variants derive distinct deterministic delivery keys.

**M3-005 implementation note (2026-09-07):** Resumption requires matching
pinned release/configuration evidence; stale auth blocks qualification, limits
remain conservative, resumed non-progress blocks, and cancellation cannot
terminalize an unknown effect.

**M3-006 implementation note (2026-09-07):** The operation-state contract,
daily recipe, and private-state guidance now state the exact immutable-chain,
new-attempt, fingerprint, checkpoint, and unknown-effect requirements. The
compact synthetic evidence manifest is checked by the fresh-process suite;
child processes discard local work and recover catalog, task create/update/
comment, and delivery durable state without a duplicate effect. This remains synthetic
repository evidence, not provider or private-instance conformance.

### Required behavioral matrix

| Behavior | Required observation |
|---|---|
| Connected outputs | Every stage reads the exact persisted hash/reference emitted by its predecessor; fixture injection between stages fails. |
| Source preservation | Multiple messages, missing final newline, Unicode, Markdown headings, delimiter-like text, and whitespace round-trip byte-for-byte and compare to adapter bodies independently. |
| Catalog interruption | Record exists but index/pointer does not: recovery verifies/adopts once; corrupt or ambiguous bytes block. |
| Reset recovery | Delete all local files and start a new process at each checkpoint boundary; durable state alone selects the next safe step. |
| Task interruption | Lost create/update/comment responses reconcile from immutable canonical ID and provider readback without duplicate effects. |
| Parent edits | Allowed title, planned due, group/scope, progress comment, completion, and history survive later source support; system-owned provenance cannot be overwritten. |
| Repeated inputs | A second unchanged operation changes no canonical/provider object and preserves stable IDs/hashes. |
| Duplicate prevention | Manual with no scheduler sends once; manual/scheduled overlap is serialized or blocked; lost response reconciles to one send; correction variant is distinct. |
| Failure honesty | Missing source bytes, stale auth, unsupported attachment, oversized single source, ambiguous reference/effect, and repeated non-progress return the specified blocked/degraded state without cursor advancement. |

### Milestone check

M3 completes only when all required failures run in fresh processes with local
state removed. A passing uninterrupted operation is insufficient.

## Milestone 4 — Expand coverage and establish release readiness

**Status:** blocked (M4-001–M4-002 complete; M4-003 awaits observed private-surface evidence).

M4 is sufficiently specified to bound later work, but concrete real-provider
limits and migrations must be based on observed authorized surfaces and private
legacy inventories. Do not invent them in advance.

### Ordered tasks

| ID | Depends on | Work and affected files | Observable acceptance |
|---|---|---|---|
| M4-001 | M3 complete | Extend catalog/import runner for complete multi-page scopes, larger bounded batches, no-new-message runs, supported attachment extraction, and explicit unsupported outcomes. Update import/attachment recipes and fixtures. | Complete enumeration evidence accounts for every item; batch resume is stable; no-new-message daily run still regenerates required rolling/brief output; unsupported content is visible and never inferred. |
| M4-002 | M3 complete | Implement only actual format/config/state migrations, expected as `migrations/0002-alpha13-structured-state.md` plus transformer/tests; update release schema/manifest only during implementation. | Supported alpha.12 templates/records migrate with verified backups and idempotence; unsupported private variants stop with exact exceptions; compatible extensions remain. |
| M4-003 | M3 complete | Exercise manual/scheduled coexistence, retry/overlap behavior, separate network paths, auth refresh, constrained limits, and any claimed non-Python equivalent. Update runtime/scheduler/mail/task/storage adapter mappings and conformance fixtures. | Each claimed execution surface has current observed evidence. Fake adapters or interactive evidence do not establish scheduled conformance. |
| M4-004 | M4-001–M4-003 | Record representative onboarding, bounded import, daily update, no-new-message, and interruption measurements in a small checked-in synthetic baseline. | Available tokens/tool calls/bytes/elapsed/repeated work are labeled measured; unavailable values are explicit; no benchmark framework or private telemetry is introduced. |
| M4-005 | M4-002–M4-004 | Extend `.github/workflows/validate.yml`, release tests, changelog, release manifest, package verification, migration/upgrade docs, and release recipe. Implement draft-asset verification and post-publication checks using the existing release workflow surface. | Clean checkout and extracted package gates pass; archive/tag/commit/manifest/assets agree; older synthetic instance upgrades and resumes; publication remains blocked until all release gates pass. |
| M4-006 | M4-005 | Perform authorized real-surface conformance and release-candidate validation; keep evidence private when it contains instance/provider data. | Every support claim has surface-specific evidence, repository privacy scan is clean, and no production activation occurs without separate authorization. |

**M4-001 implementation note (2026-09-08):** `school_os.importer` records every
provider page token and immutable conversation disposition, then chooses whole
records from deterministic byte/record bounds and durable completed IDs. It
extracts only exact supported `text/plain` UTF-8 attachment content and exposes
unsupported, inaccessible, duplicate, and manual-review outcomes without
inventing content. The daily runner proves an empty discovery still regenerates
required rolling/brief outputs. These are synthetic repository checks only.

**M4-002 implementation note (2026-09-08):**
`school_os.migrate_alpha13.migrate_alpha12` transforms only the declared
alpha.12 idle state, instance/file map, and exact readable task table into
schema-2 alpha.13 candidates. It requires an explicit target release version,
preserves convertible task/history fields, is byte-stable from the same backup
inputs, and blocks active state or undocumented legacy shapes. Upgrade backup,
exact-ID write, readback, and activation remain governed by `system-upgrade.md`.
The transformer also requires both the legacy manifest and active-release
version to be exactly `0.1.0-alpha.12`; a schema-1 predecessor alone is not a
supported input.

**M4-003 status (2026-09-08):** Repository work now marks capability evidence
as `unverified`, `synthetic`, or `observed`; scheduled mutation qualification
requires `observed`. Synthetic tests cover independent network paths,
authentication/limits, manual/scheduled delivery-key overlap, and the
observed-evidence gate, but cannot establish a real execution surface. Current
authorization now permits a read-only private Drive inventory, which found an
alpha.11/schema-1 instance. That inventory does not establish runtime, mail,
task, or scheduler conformance, and the alpha.11 predecessor is outside
Migration 0002's explicit alpha.12 input. M4-003 is not complete, and
M4-004–M4-006 remain blocked by its dependency.

**Private-upgrade consultation (2026-09-08):** A bounded GPT-5.6 Sol High
read-only review confirmed that there is no approved direct alpha.11-to-
alpha.13 path. Extending Migration 0002 to support alpha.11 would alter the
explicit supported-predecessor and release-upgrade boundary and requires new
user approval. The least-risk path within existing scope is a read-only audit
for conformance with the immutable released alpha.12 requirements, followed
only if it passes by a separately verified alpha.11-to-alpha.12 upgrade; the
alpha.13 candidate remains non-installable until its own release gates pass.
Candidate staging may support testing only and cannot be activated. The review
also found a missing explicit source-version check in the transformer; that
fail-closed defect is corrected and regression-tested without broadening the
migration scope.

**Alpha.12 compatibility-audit result (2026-09-08):** The authorized read-only
private audit found native-document source-catalog storage alongside raw
Markdown. Because alpha.12 requires raw UTF-8 Markdown storage and direct
byte-level source-to-catalog comparison, the conditional staged route does not
pass. No content was converted or written. A preservation mapping that proves
lossless source equivalence, or a separately approved alpha.11 migration
scope, is required before any private upgrade can resume.

Optional adapters from work package 10 receive independent IDs only when the
user selects a concrete deployment need. They do not become dependencies of
M4-001 through M4-006 and do not block alpha.13 otherwise.

## Configuration, migration, packaging, and validation changes

### Configuration

- Keep household values, provider selection, credentials, and provider state in
  their current private owners. The scaffolder accepts secrets only as external
  references; it never prints or stores secret values.
- Add configured `max_records_per_unit`, `max_bytes_per_unit`, and delivery
  correction policy. Defaults are conservative and may only be lowered by
  observed limits; unknown is not unlimited.
- Add explicit manual-entrypoint authorization and serialization configuration.
  Scheduler configuration remains nullable.
- Keep recipients and provider delivery configuration outside
  `daily-run-personal-values.md`.

### Migration

- Data schema version 2 is expected because operation state, canonical task
  storage, provider projection state, exact references, and catalog framing
  change. M1 may declare schema 2 for clean candidate installs. Do not claim
  alpha.12 upgrade compatibility or mark the release `released` until M4
  delivers and tests Migration 0002.
- Migration 0002 must inventory exact targets, parse only declared alpha.12
  legacy forms, create/read back generation-specific backups, build candidates,
  validate preservation, write through the existing upgrade coordination mode,
  read back, and prove idempotence.
- Existing catalog records may remain v1 until read/changed if they are
  unambiguous and source-reverified. Task and operation state must migrate before
  the alpha.13 runner can mutate them.
- No private migration fixture belongs in Git. Unsupported legacy variation is
  an explicit blocker requiring a private, approved mapping.

### Packaging and installation

- Build from a clean exact commit; never package ignored `dist/` contents.
- During M1, set the manifest version to `0.1.0-alpha.13` with
  `status: unreleased`. Installed validation may accept that candidate only with
  an explicit test/development flag; production installation still requires a
  released immutable source identity.
- The installed validator must be included in the archive and runnable after
  extraction with no network, Git, or third-party package.
- Scaffolding writes to a candidate directory first. A storage-capable installer
  then creates files, records returned identities, reads them back, and accepts
  the installation manifest only after every hash and containment check passes.
- Release publication remains draft-first and immutable. Implementation must add
  asset-upload/readback/post-publication verification on the actual GitHub
  release surface; `build_release.py` alone does not publish anything.

### Validation gates

Each milestone runs, at minimum:

1. focused new unit and behavioral tests;
2. `python3 scripts/validate.py` from a clean checkout;
3. `python3 scripts/validate_installed.py` against the exact built candidate once
   M1 provides it;
4. local-link and registry/reference checks;
5. `git diff --check` and an in-scope file review;
6. the repository privacy scan including every new tracked file; and
7. commit, push, and verification that the intended remote branch resolves to
   the pushed commit.

M4 additionally requires migration/upgrade tests, reproducible release rebuild,
draft asset verification, post-publication asset checks, and separate observed
evidence for every real execution-surface support claim.

## Assumptions, unresolved decisions, and deferred scope

### Explicit assumptions

- CPython 3.12 and the standard library are the executable reference for M1–M3;
  the fakes implement the interfaces selected for the documented
  ChatGPT Work/Drive/Gmail/Todoist journey without claiming those services ran.
- The synthetic filesystem/fake-provider instance has the same durable/local
  ownership boundary as a real instance; deleting its local run directory does
  not delete its durable provider-state directory.
- Exact plaintext body means the complete string returned by the selected mail
  adapter. If only HTML, snippets, or incomplete bodies are available, the
  adapter must declare that limitation and the configured operation blocks or
  records the approved attachment/body outcome.
- Normal household operation has one active mutating operation. Coordination is
  scoped to admission and consequential effects, not a general locking system.
- The supported alpha.12 legacy forms are the checked-in templates/contracts and
  independently specified migration cases. Private deviations are not assumed.

### Unresolved decisions and approvals

No unresolved product decision blocks M1–M3. The design choices above implement
the approved plan without changing its acceptance criteria.

Before M4 can make production support or release claims, implementation must
resolve these evidence-dependent items:

- which exact real runtime/provider/authorization surfaces alpha.13 will claim;
- the limits, authentication behavior, consistency windows, idempotency/search
  behavior, and serialization mode actually observed on each selected surface;
- the exact private legacy variants affected by Migration 0002; and
- whether any work-package-10 adapter or offline speech bundle is selected.

User approval is required before inspecting or migrating a private instance,
incurring paid/externally visible adapter effects, selecting optional adapter
scope that expands the release work, publishing the release, or activating a
production schedule/manual sender. If a real provider cannot meet the specified
reconciliation contract, changing the contract or weakening acceptance also
requires explicit user approval; the default outcome is a precise blocker.

### Deferred scope

- The additional historical-retrieval acceptance case remains deferred and is
  not a work package, task, or alpha.13 release gate.
- General instruction-packet compilation, arbitrary Markdown parsing, multiple
  interchangeable catalog layouts, a generic merge engine, distributed locks,
  worker pools, background cancellation infrastructure, learned throughput
  optimization, a layout/template engine, full vendor emulation, and broad
  benchmark infrastructure remain deferred.
- Google Sheets task support, additional attachment extractors, runtime speech
  adapters, and offline speech packages remain independent extensions.
- Automatic continuation is used only when an authorized mechanism exists.
  Otherwise a later manual or scheduled session resumes from durable state.
- Historical import remains separate and never implies task-provider mutation or
  delivery authorization.
