# School-OS 0.1.0-alpha.13 release plan

- Status: planning snapshot; implementation not started
- Captured: 2026-09-07
- Target release: `0.1.0-alpha.13`
- Baseline: `main` at `095485b`, with `release.yaml` declaring `0.1.0-alpha.12`

## Purpose and authority

Capture the current ten-part proposal for deterministic, efficient, portable,
and resumable School-OS execution. This is the agreed state of planning, not a
claim that every implementation detail or release scope is final. The user has
requested a subsequent review for over-engineering; that review must remain
distinguishable from this snapshot until its recommendations are accepted.

The next target is alpha.13 because alpha.12 is the highest actual existing
release tag and manifest version. Release display titles do not determine
version identity. Recording this target does not publish a release, change the
current release manifest, or activate a private instance.

This plan follows [product principles](../../product-principles.md),
[architecture](../../architecture.md), and
[instruction ownership](../../instruction-ownership.md). The root
[implementation plan](../../../PLAN.md) retains historical development context.
The motivating runtime retros remain private; this document contains only
generic requirements and independently described implementation proposals.

## Approved product decisions

1. **Verified manual sending without a scheduler.** Manual and scheduled runs
   follow the same processing, verification, and duplicate-prevention rules.
   A verified manual execution surface does not require a scheduler.
2. **Checkpointed continuation across execution sessions.** An operation may
   span multiple execution attempts. Continue whenever execution is possible,
   checkpoint before predictable limits, and recover after interruptions.
   Partial execution never becomes a completed operation. Automatic continuation
   depends on an available, authorized mechanism; otherwise the next session can
   resume from the private instance.

For example, after a bounded portion of an import is persisted and verified,
an environment reset must not require starting the import over. Recovery reads
the saved work inventory and reconciles uncertain provider effects before
continuing. A send whose outcome is unknown must not be retried blindly.

Historical import already permits resumption. Implementing the second decision
requires revising daily-run invocation semantics while retaining its obligation
to complete every required phase before reporting success. Both decisions need
consistent recipe, capability, state, test, and upgrade treatment; neither is
permission to bypass provenance, verification, or authorization.

## Proposed implementation shape

Organize executable code as a small shared Python package, such as `school_os/`,
with thin commands in `scripts/`. Helpers accept structured inputs and file
references, perform deterministic work, and return compact results. Adapters
provide authenticated provider access. Python is the reference implementation;
another execution surface may qualify by satisfying the same contracts and
verification requirements.

Keep the dependency footprint small and support execution without package
downloads. Local processing files are recoverable caches or staging artifacts;
the private Drive instance remains the durable authority. Normalized exchange
formats must not introduce a competing canonical data store. New filenames and
module boundaries below are proposals, subject to implementation design.

## 1. Reliable release packaging and installation

### Work and deliverables

- Refactor existing validation into reusable checks. Keep `scripts/validate.py`
  for repository development and add `scripts/validate_installed.py` for
  extracted packages. Installed validation avoids Git commands,
  repository-only tests, and network downloads.
- Extend the release workflow to build from an exact commit, attach the archive
  and checksum to a draft release, verify contents and version agreement, and
  then publish. Add post-publication verification of downloadable assets.
- Add `scripts/scaffold_instance.py`. It accepts confirmed household settings,
  integration selections, and observed provider references, then generates
  configuration and state files from templates.
- Validate every generated file against its schema. Reconcile gaps between
  configuration templates and schemas instead of maintaining separate
  assumptions in the scaffolder.
- Produce an installation manifest recording package identity, intended files,
  returned storage IDs, hashes, and verification status. Installation uses the
  recovery mechanism in part 4.

**Benefit:** Repeatable installation with less agent-written configuration and
fewer dependencies on the host environment.

**Impact if deferred:** Packaging mistakes and installation improvisation can
undermine an otherwise correct release.

**Acceptance:** An extracted package validates and scaffolds an instance without
Git or network downloads; altered files and inconsistent versions are rejected.

## 2. Deterministic routing, instance isolation, and narrow instructions

### Work and deliverables

- Add a versioned operation registry, for example
  `core/operations/registry.json`, declaring each operation's recipe,
  dependencies, supported entrypoints, required capabilities, and allowed
  effects.
- Update onboarding to populate exact private references for operation
  entrypoints. The stable bootstrap resolves the instance manifest, active
  release, selected operation, and relevant configuration.
- Implement a reference resolver that checks object identity, expected type,
  and permitted instance location. Recovery discovery uses scoped, paginated
  searches and stops on ambiguity.
- Add an operation-packet builder. It assembles only instructions and references
  needed for the selected operation and phase, with release and input
  fingerprints. It preserves required rules instead of summarizing them through
  an LLM.
- Update recipes to invoke shared helpers for executable rules, keeping one
  authoritative owner for each rule and avoiding independently maintained
  copies.

**Benefit:** Fresh agents find the right procedure with fewer reads and less
reliance on memory.

**Impact if deferred:** Agents may bypass recipes, use stale instructions, or
confuse similarly named instances.

**Acceptance:** A fresh session selects the correct recipe among multiple
instances and versions without a routine Drive-wide search.

## 3. Capability discovery, resource limits, and execution planning

### Work and deliverables

- Extend `capability-profile.schema.json` beyond prose limits. Record structured
  fields such as maximum payload bytes, supported pagination, execution budget
  where known, file-transfer support, local execution availability, and storage
  persistence observations.
- Represent network paths separately: connector access, shell HTTPS access,
  package downloads, and external service access. Success on one path does not
  imply success on another.
- Separate relatively stable capability observations from current authentication
  health. Add minimal authenticated probes for integrations needed by the
  current operation, plus revalidation after relevant changes or failures.
- Implement a batch planner that selects work units using observed byte, time,
  and tool limits. Use conservative defaults for unknown limits, reduce batch
  size after capacity failures, and detect repeated non-progress.
- Make capability requirements conditional on the operation and configured
  features. Record explicit outcomes for unsupported operations and optional
  degradation.

**Benefit:** The same system adapts to different tools, VMs, and network
restrictions.

**Impact if deferred:** Agents discover limitations through failed work and may
mistake optional feature gaps for complete incompatibility.

**Acceptance:** Synthetic profiles produce predictable execution plans.
Concurrency remains optional; unknown limits are never treated as unlimited.

## 4. Durable checkpoints, guarded writes, and recovery

### Work and deliverables

- Add operation-state and checkpoint schemas containing `operation_id`,
  `attempt_id`, pinned release, scope, configuration fingerprint, completed
  units, remaining work, artifact references, and verification evidence. One
  operation may have multiple execution attempts.
- Define explicit states such as `running`, `needs_continuation`, `blocked`,
  `complete`, and `cancelled`, with validated transitions. A saved checkpoint
  does not constitute completion.
- Persist compact checkpoints remotely after bounded work units and before
  consequential external effects. Maintain a small current snapshot so
  resumption does not require reading an ever-growing log.
- Implement guarded mutation helpers: read and validate current state,
  construct a candidate, check preservation rules, write through the adapter,
  read back, and record verification. Unexpected data loss fails validation;
  legitimate lifecycle changes remain possible.
- Add an effect journal for sends, task creation, comments, and similar actions.
  Persist intent before invocation and treat unconfirmed attempts as potentially
  executed until provider reconciliation establishes the outcome.
- Implement recovery that checks release/configuration compatibility,
  reconciles unfinished writes, and returns the next safe step. Track
  operation-owned workers and reject superseded results.

**Benefit:** Another session can recover using the private instance alone, with
bounded repeated work.

**Impact if deferred:** Resets can lose progress, duplicate external actions, or
leave partial state that requires manual reconstruction.

**Acceptance:** Remove all local files and interrupt execution before and after
provider calls. Recovery preserves verified work and avoids blindly repeating
uncertain effects.

## 5. Deterministic ingestion and separate semantic-quality checks

### Work and deliverables

- Define normalized exchange schemas for source messages, attachment
  inventories, extraction candidates, and coverage mappings. These are
  processing inputs and staging artifacts; canonical records retain their
  established authority.
- Implement complete enumeration with fixed scope boundaries, pagination
  evidence, stable ordering, and deduplication by immutable identity. Record
  thread messages outside the inclusion rule with an explicit disposition.
- Build extraction packets with source segments and compact references. The
  model returns facts, classifications, and coverage decisions; code supplies
  long provider IDs, timestamps, URLs, and raw-body content.
- Add a catalog builder that mechanically inserts exact adapter-returned bodies
  and preserves existing record and Fact IDs. Strengthen the parser against
  duplicate IDs, delimiter-like source text, missing bodies, and reordered
  membership.
- Implement both acceptance comparisons: source body against catalog content,
  then intended catalog bytes against persisted bytes. Publish index entries
  only after verification.
- Support bounded physical volumes without changing logical identities. Add
  attachment extraction paths selected by observed MIME/size capabilities,
  with explicit unsupported or incomplete outcomes.
- Add structural coverage checks and omission warnings. Suspicious
  classifications trigger review; keyword matches do not automatically decide
  task meaning.

**Benefit:** Most copying and catalog assembly moves out of model output, while
semantic work stays focused on bounded source material.

**Impact if deferred:** Large imports remain vulnerable to sampling, identifier
corruption, missed attachments, and unverifiable completeness claims.

**Acceptance:** Fixtures cover multi-page discovery, embedded formatting,
multiple requests, negation, completed actions, attachments, and interrupted
publication.

## 6. Mechanical reconciliation of knowledge and canonical tasks

### Work and deliverables

- Implement parsers and serializers for supported catalog and register formats.
  Add round-trip tests so parsing and rewriting preserve required information.
- Align the task schema with fields already present in the register, including
  owner, source dates, and completion history. Define the boundary between
  canonical task data and provider-binding state.
- Build derived indexes, guidelines, rolling updates, and source links through
  validated Fact references. Record canonical inputs and generator version so
  outputs can be rebuilt.
- Implement task reconciliation using stable task identities and existing
  bindings. Where new facts may concern an existing task but identity is
  ambiguous, produce a review case instead of merging by title.
- Define field ownership and store the last synchronized projection needed to
  distinguish parent changes from system changes. Apply patches that preserve
  parent-owned fields, history, and unrelated provider data.
- Keep parent-created tasks distinguishable from source-derived tasks. Advance
  synchronization state only after required writes verify.

**Benefit:** Reliable rebuilds and synchronization without losing parent
progress or recreating tasks.

**Impact if deferred:** Agents can generate broken links, duplicate tasks,
overwrite edits, or confuse source deadlines with parent plans.

**Acceptance:** Replaying unchanged inputs makes no unintended changes. New
supporting facts preserve task identity; conflicting edits produce explicit
review cases.

## 7. Verified manual delivery independent of scheduling

### Work and deliverables

- Refactor `manual-daily-run.md` and `daily-run.md` around one shared operation
  definition. Manual requests and schedules become entrypoints into the same
  processing sequence.
- Validate capabilities for the execution surface actually performing the work.
  A manual run needs verified storage, mail, and applicable task capabilities;
  it does not require a scheduler.
- Add an admission decision for an existing active or incomplete run: continue
  it, report its progress, or start a new operation when safe.
- Specify how adapters establish serialized execution when manual and scheduled
  runs coexist. Prefer verified runtime serialization; use explicit
  coordination where necessary. A shared `idle` field alone cannot establish
  exclusivity.
- Use a delivery key independent of the execution attempt, shared by manual and
  scheduled paths. Store the intended content identity and verified provider
  result. Give explicitly requested corrections/resends distinct
  policy-controlled identities.
- Recheck authorization and relevant configuration before delayed delivery.
  Material changes during a paused operation require reconciliation rather than
  sending with stale settings.

**Benefit:** A fully supported manual experience, with scheduling added as an
optional trigger.

**Impact if deferred:** Scheduler-free users remain pushed toward ad hoc
execution, and manual/scheduled overlap risks duplicate delivery.

**Acceptance:** Test scheduler-free sending, overlapping entrypoints, resumed
runs, explicit corrections, and interruption immediately after send.

## 8. Deterministic brief rendering and presentation customization

### Work and deliverables

- Define a brief-input schema containing verified news, guidelines, tasks,
  grouping configuration, and stored links.
- Implement a renderer producing HTML and plain text from those inputs. Encode
  stable sorting, section separation, entity order, local-date grouping,
  escaping, and empty-state behavior.
- Package a default template and validated theme settings for colors, labels,
  and presentation choices. Keep recipients and provider configuration in their
  existing configuration owners.
- Emit rendered files and a compact rendering manifest containing input
  fingerprints, template version, counts, and content hashes.
- Derive optional audio input from the permitted current-run delta. Keep speech
  normalization in the audio processing path.
- Add expected-output fixtures and visual checks for mobile layout, long text,
  unusual characters, and customized entity names.

**Benefit:** Consistent output with fewer generated tokens and less layout
reconstruction.

**Impact if deferred:** Presentation remains dependent on the agent; factual
sections or source links may be inconsistently rendered.

**Acceptance:** Identical verified inputs and configuration yield identical
rendered files, with correct content and readable presentation.

## 9. Behavioral testing, measurement, and upgrade delivery

### Work and deliverables

- Build fake storage, mail, task, and scheduler adapters with configurable
  failures: stale authentication, truncated results, successful responses with
  stale content, lost responses, and interrupted execution.
- Add end-to-end scenarios that restart the process and discard local storage
  between steps. Test operation outcomes and persisted artifacts instead of
  relying primarily on recipe-text assertions.
- Maintain synthetic expected facts and task outcomes for semantic evaluation.
  Measure interpretation quality separately from deterministic assembly and
  recovery.
- Add benchmark runs for onboarding, backfill, ordinary daily updates, and
  no-new-message days. Record available token usage, tool calls, bytes
  transferred, runtime, peak memory, and repeated work; label unavailable or
  estimated metrics.
- Create explicit migrations for changed state, configuration, and record
  formats. Preserve compatible extensions, stage the new release, verify
  backups and migrations, and activate only after compatibility checks.
- Update CI and release gates. Each accepted repository milestone includes
  appropriate tests, privacy scanning, commit, push, and remote-commit
  verification.

**Benefit:** Evidence that the system survives the failures motivating this
plan and that efficiency improvements are real.

**Impact if deferred:** Passing unit tests can mask operational failures; new
execution states may be unsafe for older installed recipes.

**Acceptance:** An interrupted synthetic instance resumes successfully, an older
instance upgrades safely, and measured results can be compared with a recorded
baseline.

## 10. Additional adapters as independent extensions

### Work and deliverables

- Implement a Google Sheets task adapter using canonical task IDs, explicit
  editable columns, provider bindings, completion semantics, and verified
  read/write mappings.
- Add extraction adapter mappings for observed server-side text extraction and
  local extraction tools. Declare supported formats, completeness limits,
  provenance, and error outcomes.
- Add runtime-provided speech adapters with capability probes, verified voice
  configuration, bounded requests, retrievable output, and explicit network
  requirements.
- Package optional offline speech dependencies and models separately, with
  version, size, checksum, and compatibility metadata. Keep the base
  installation lightweight.
- Define fallback choices in private configuration. Adapters may use only
  supported, authorized alternatives and must report degradation.
- Supply adapter conformance fixtures and an extension guide that applies
  equally to official and user-created adapters.

**Benefit:** Broader functionality without moving provider-specific behavior
into core operations.

**Impact if deferred:** Users have fewer integration options, but foundational
reliability work can still ship.

**Acceptance:** Each adapter passes its applicable contract tests and has
observed capability evidence on the surface where it will run.

## Proposed implementation sequence

1. Begin with shared interfaces and schemas from parts 1-4, while establishing
   the test harness from part 9.
2. Build one complete path from source retrieval through verified manual
   delivery using parts 5-8.
3. Expand coverage, run measurements and upgrade validation, and add the
   independent extensions from part 10.

Keep the design small: one active mutating operation per instance, short
executable steps, compact remote checkpoints, and complete verification
evidence that does not need to be repeatedly printed into model context.

## Boundaries for implementation planning

- Preserve source losslessness, provenance, canonical task history, and
  compatible instance extensions.
- Keep sequential execution as the baseline. Subagents, fixed vendor-specific
  batch sizes, monthly volumes, and background workers are not prerequisites.
- Distinguish mechanical completeness from semantic interpretation quality.
  Trigger scans support review; they do not certify understanding.
- Do not make optional feature availability a substitute for operation-specific
  capability checks. Do not silently skip a configured required phase.
- Public development artifacts contain generic source and synthetic fixtures;
  private state and retrospective evidence remain outside the repository.
- Revisit implementation scope after the requested simplicity review. This
  document is a planning baseline, not an instruction to implement every
  proposed abstraction before delivering a useful release.
