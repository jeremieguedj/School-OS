# School-OS progress log

## 2026-09-02 — alpha.3 legacy-date QA correction

- After configured-group-projection validation, private shadow QA identified legacy catalog records without per-Fact local dates.
- The corrected migration permits the record-level date only when it is singular and unambiguous; any range, multiple date, or missing date remains blocking.
- No private rolling data was changed. Prepared `0.1.0-alpha.4` and a synthetic fixture for this compatibility path.
- Next: tag the corrected candidate, rerun the complete migration shadow, then apply only after full verified coverage.

## 2026-09-02 — alpha.2 migration QA correction

- The `v0.1.0-alpha.2` tag/release correctly points to its schema-valid manifest, but its rolling-provenance migration compared raw fact scope to displayed group scope.
- Private shadow QA showed that this would incorrectly block valid multi-entity and unscoped updates that project to the shared group under configuration.
- No private rolling data was changed. Prepared `0.1.0-alpha.3` to use configured group projection and added a synthetic fixture for that behavior.
- Next: tag the corrected candidate, rerun the bounded migration shadow, then apply only after all mappings are verified.

## 2026-09-02 — initialization

- Repository confirmed: `jeremieguedj/School-OS` (private, default branch `main`).
- Frozen architecture baseline accepted for implementation.
- Deferred reviewer findings must be captured without altering the baseline.
- Phase 1 started: establish repository governance and reusable package skeleton.

## Resume instructions

Follow the authoritative
[repository development continuity](START-HERE.md#repository-development-continuity)
requirements, then read this log from top to bottom.

## 2026-09-02 — local audio-worker scaffold

- Added a generic local ElevenLabs audio worker under `automation/audio-brief/`.
- The worker consumes a source-linked private manifest, uses a macOS Keychain secret at runtime, validates ElevenLabs dialogue constraints and fresh MP3 output, and never stores credentials or private household data in the repository.
- Its dry-run path passed without contacting ElevenLabs or generating an audio file. WhatsApp UI delivery, Drive manifest construction, and schedule activation remain intentionally unimplemented pending supervised integration work.

## 2026-09-02 — audio-worker recipe conformance correction

- Re-verified the local audio worker against the private ElevenLabs recipe: the API path is `v1/text-to-dialogue`; the requested dialogue model remains `eleven_v3` in the JSON body.
- Corrected the character-limit edge case to fail closed when the first complete record cannot fit, and reject action statuses outside the recipe's fixed set.
- Added dependency-free tests for the recipe's voice/tag mapping, the oversized-first-record gate, and due-status validation. Local syntax, dry-run, and all three tests pass without an API request.


## 2026-09-02 — foundation and core-contract checkpoint

- Phase 1 complete: generic README, neutral entry points, architecture, privacy boundary, instruction-ownership map, development release manifest, and deferred adversarial-review record committed.
- Phase 2 in progress: created generic contracts for capabilities, source catalog, tasks, adapters, releases, fact-flag decisions, and initial logical schemas.
- Inspected the existing private system's generic instruction structure only; no personal catalog, task, or configuration content was copied into the repository.
- Next: add deterministic operations, private-instance templates, reference adapters, synthetic fixtures, and release/onboarding material.


## 2026-09-02 — reusable-package checkpoint complete

- Phases 1–5 are implemented at initial-package level: repository foundation; generic contracts/schemas; deterministic core operation recipes; private-instance templates; reference runtime/mail/task/scheduler/audio adapters; manual-install/update/migration documentation; and synthetic fixtures.
- Deferred reviewer findings and recommendations are recorded in `docs/deferred-adversarial-review.md` and were not incorporated into the frozen baseline.
- QA passed: all six JSON schemas parsed successfully; required entry, operation, adapter, template, fixture, plan, progress, and deferred-review files were read back from GitHub; targeted scan found no private family names, school domains, recipient address, or sampled live Drive IDs.
- No private Drive files, schedules, provider objects, or emails were modified during repository extraction.
- Next phase: private-instance inventory and configuration mapping under `docs/current-instance-migration.md`. This requires separate inspection/approval because it touches the live private deployment. Do not enable a new scheduler or release a public installer before that phase is validated.


## 2026-09-02 — private migration inventory checkpoint

- Phase 6 started in read-only mode: private Drive layout and logical roles were inventoried and stored only in the private instance migration area.
- The inventory maps current generic instructions, configuration, canonical catalog/task data, derived files, and runtime state to the new model without copying private content into GitHub.
- Existing scheduler, current daily runbook, catalog, task provider, and delivery behavior remain unchanged.
- Next: create a versioned installed release area from a tagged/released package, generate private config/state mappings that initially reference the current files, then run no-send/no-provider-write shadow validation.


## 2026-09-02 — inactive candidate and shadow checkpoint

- A private inactive candidate configuration and logical file map were created in the migration area; all candidate external writes are disabled.
- All mapped private objects resolved successfully, and live scheduler, catalog, task, brief, and state files remained unmodified during shadow reads.
- Bounded shadow checks passed for source-record structure, raw-message membership, record-level update traceability, durable/task provenance, task-binding parity, received-day grouping, section separation, mobile-link rules, and freeform required-comment behavior.
- The first published alpha tag is non-installable because its packaged manifest still declares a development, unreleased version. It remains a packaging dry run.
- Shadow validation also found a legacy compatibility gap: rolling-update bullets carry source identifiers but not atomic Fact IDs required by the new source-catalog contract.
- Prepared `0.1.0-alpha.2` with a schema-valid release manifest, a deterministic fail-closed provenance migration, and synthetic fixtures. Next: verify the new package after tagging, run the declared migration in private shadow mode, and install only after every exception is explicitly mapped.


## 2026-09-02 — alpha.5 release hardening checkpoint

- Private alpha.4 evidence confirms that the versioned release was installed and Migration 0001 completed with verified backup and readback; the candidate remains inactive and scheduled/provider behavior remains unchanged.
- Reconciled the instance template with its strict schema and added dependency-free executable validation for schemas, manifests, rolling-provenance migration behavior, fail-closed negative cases, and idempotence.
- Added deterministic source packaging with a complete internal SHA-256 inventory, external archive checksum, safe-path verification, and reproducible-byte tests.
- Hardened release and upgrade contracts with immutable publication, capability, conditional-write, upgrade-journal, generation/revision, checksum, backup, activation, and recovery gates.
- Added continuous integration. Local validation passes before publication; next: publish and verify an immutable `v0.1.0-alpha.5`, stage it privately, and complete no-external-write operational parity before any activation or scheduler cutover.


## 2026-09-02 — alpha.6 scheduled-runtime conformance checkpoint

- The supervised production probe on the ChatGPT Work scheduled surface failed closed before any Drive, mail, or task-provider side effect because alpha.5 did not declare the complete daily-run dependency set or carry a private scheduled-surface capability profile. The single daily schedule was verified paused.
- Prepared `0.1.0-alpha.6` with a standalone daily-run contract, operation-specific capabilities, an observed capability-profile schema and validator, and production-capable ChatGPT Work runtime/scheduler reference contracts.
- Preserved data schema version 1 and Migration 0001. This is a control-plane completeness release; no private canonical data rewrite or architecture change is required.
- All 44 dependency-free tests pass before the release commit. Next: commit the candidate, run the complete clean-HEAD validation, publish and verify an immutable release, install it privately with a conformant scheduled profile, then perform one supervised production run before resuming the schedule.


## 2026-09-02 — alpha.7 connector-safe upgrade correction

- The immutable alpha.6 scheduled-surface conformance probe passed on the configured ChatGPT Work model/effort, but its Drive update surface exposed no atomic generation/revision precondition. The upgrade correctly stopped before any private write.
- Prepared `0.1.0-alpha.7` with a bounded supervised operational-single-writer fallback while preserving native conditional mode, the frozen architecture, data schema version 1, and Migration 0001.
- The fallback requires paused schedules, one actor, an explicit no-concurrent-mutators guard, exact-ID full-byte SHA-256 and `modified_time` checks immediately before updates, create-only backups and journal checkpoints, immediate readback, and fail-closed manual recovery.
- Declared the attended interactive upgrade capability gate and reconciled private-migration version evidence with both supported coordination modes; automatic restore remains optional unless promised.
- All 55 dependency-free tests pass and the diff check is clean. Next: review and commit the candidate before publishing and verifying a new immutable release.

## 2026-09-03 — alpha.8 routine-run simplification

- Removed the routine daily-run Drive lease prerequisite and its coordination capability requirement.
- Kept exactly one scheduled production sender and made Gmail delivery-key/Sent-message verification the routine duplicate guard.
- Preserved the stricter coordination protocol for attended release upgrades; it does not apply to routine daily brief delivery.
- Added executable regression coverage for the simplified daily-run contract. Next: commit, publish, install, and perform one supervised scheduled production run.

## 2026-09-03 — approved alpha.9 daily-run architecture

- User approved one generic `daily-run.md` plus one private
  `daily-run-personal-values.md`, rather than two competing daily runbooks.
- The private values document will contain only daily values and explicitly
  supported household/presentation customization. Adapter identity and
  provider-specific configuration remain outside it.
- Each daily phase will resolve its own active provider selector, generic
  adapter, and only the private configuration/state declared by that adapter.
  Task reconciliation remains a required daily phase.
- The full logical file map will move out of routine-run preflight and remain
  available for onboarding, upgrades, recovery, and maintenance.
- Alpha.8 is already tagged and cannot be amended. Next: implement/test/publish
  alpha.9, create the companion private values file from the legacy runbook,
  update the private instance manifest and task prompt, then perform a
  supervised scheduled production run. Do not delete the legacy private
  runbook during the initial rollout.

## 2026-09-03 — alpha.12 raw-Markdown losslessness correction

- Production validation of alpha.11 found four native Google Docs whose raw-message sections were shortened even though the generic contract prohibited summaries. The Work turn had no provider, authorization, or runtime blocker and stopped after cataloguing without completing reconciliation, required task sync, delivery, or cursors.
- A new isolated ChatGPT Work cloud agent replaced raw Drive file `school-os-markdown-write-probe-20260903.md` in place, preserved its `text/markdown` MIME type and file ID, and read back the exact 70 UTF-8 bytes including the final newline. Raw Markdown scheduled-surface replacement is therefore observed as available; the earlier contrary assumption is retired.
- Alpha.12 removes the native-Docs daily storage exception, requires direct equality between each complete mail-adapter plaintext body and the corresponding catalog raw-message section, retains exact-byte Drive readback, and forbids successful termination after an intermediate phase.
- Added executable losslessness regressions for summary, truncation, substitution, message reordering, and whitespace normalization. The complete repository validation now passes 77 tests.
- Verified private rollback mapping exists for seven mutable Markdown records. Six remain logically equivalent to their native copies. The raw catalog index and four September 3 source records require a fresh lossless rebuild before activation.
- Next: commit and publish immutable alpha.12; install it privately; restore exact Markdown references and scheduled capability evidence; rebuild the four records from fresh complete Gmail reads; run and monitor a new Work agent using the production prompt; independently verify catalog equality, task reconciliation, and the delivered email; repeat once; then replace the old schedules with one fresh daily 6:00 a.m. schedule.

## 2026-09-07 — alpha.13 planning snapshot

- Selected `0.1.0-alpha.13` as the next planning target after checking the remote
  release tags and current alpha.12 manifest.
- Captured the ten-part technical proposal in
  `docs/plans/0.1.0-alpha.13/PLAN.md`, including deliverables, benefits, impacts
  of deferral, acceptance criteria, and implementation sequence.
- Recorded the user's approval for verified manual sending without a scheduler
  and checkpointed continuation across execution sessions. The remaining
  implementation details are a planning baseline for further review.
- Added a pointer from the root plan. No implementation, release publication,
  manifest-version change, or private-instance activation is included.
- Next: review the committed plan against documented personas, use cases, and
  design priorities for over-engineering; keep review recommendations separate
  from the captured plan pending acceptance.

## 2026-09-07 — alpha.13 simplicity review

- After pushing and verifying planning commit `3acd660`, reviewed the captured
  plan against the documented parent and agent personas, core use cases, and
  simplicity/portability priorities.
- Recorded recommendations in `docs/plans/0.1.0-alpha.13/REVIEW.md` and linked
  them from the root plan. The original release-plan snapshot is preserved.
- Recommended retaining the reliability requirements while narrowing instruction
  generation, runtime optimization, worker orchestration, generic format/merge
  support, benchmark infrastructure, and optional adapter release gates.
- Identified historical source-backed retrieval as a small acceptance check that
  protects the broader canonical-data use case beyond briefs and tasks.
- Review recommendations remain proposed; no implementation scope was silently
  removed, and no private-instance changes were made.
- Next: incorporate accepted review refinements into a subsequent plan revision
  before implementation.

## 2026-09-07 — alpha.13 plan revision 2

- At the user's request, incorporated the simplicity-review findings and
  recommendations into the ten work packages of the alpha.13 plan, preserving
  their benefits, deferral impacts, and acceptance criteria.
- Narrowed routing, capability/batch planning, recovery machinery, format/merge
  support, rendering controls, and test infrastructure. New adapters remain
  independent follow-ups rather than collective release prerequisites.
- Kept both approved product decisions and the source/provenance, write
  verification, task-history, and unknown-effect safeguards.
- Deferred discussion of the proposed additional historical-retrieval acceptance
  case. Existing retrieval requirements remain intact; no new retrieval gate or
  implementation work is included.
- Expanded the recommended connected-path sequence to explain its development
  purpose, initial synthetic case, recovery checks, expansion, and integration
  risks. It is not a new mandatory install/import/send operation for parents.
- Updated the root plan and historical review to reflect revision 2. No runtime
  code, release manifest, or private instance was changed.
- Next: clarify the sequencing recommendation with the user before implementation.

## 2026-09-07 — alpha.13 plan revision 3

- Recorded the user's approval of the complete-path development approach in
  `docs/plans/0.1.0-alpha.13/PLAN.md`.
- Defined four pending milestones: clean candidate installation, one connected
  normal operation, verified interruption recovery and repeated execution, then
  broader coverage and release readiness. Each includes work, deliverables,
  completion checks, and mapping to the existing work packages.
- Required the connected test to consume actual outputs between stages and
  recover from durable state after local environment loss. The initial journey
  exercises verified manual delivery without a scheduler.
- Distinguished the initial connected implementation from full release scope
  and real runtime conformance. Optional adapters remain independent; the
  additional historical-retrieval acceptance case remains deferred.
- Updated the root plan and review disposition. This is a planning-only change;
  no runtime code, release manifest, or private instance was changed.
- Validation: all 77 repository tests and privacy scanning passed, along with
  local-link, plan-structure, and diff checks.
- Next: use the approved milestone sequence for subsequent implementation
  planning when requested; implementation has not started.

## 2026-09-07 — shared repository continuity instructions

- Consolidated repository-maintenance continuity requirements in
  `START-HERE.md`; `AGENTS.md`, the Claude compatibility entry, and the progress
  resume instructions now lead to that single vendor-neutral owner.
- Required maintenance work to follow the approved release plan and linked
  specification, keep milestone status accurate, append evidence-rich progress
  checkpoints, and reconcile documentation with the actual code and Git state
  on resumption.
- Preserved the validation, privacy scan, scoped commit, push, and remote-commit
  verification requirements. No runtime behavior, release plan milestone,
  manifest, or private instance changed.
- Relevant files: `START-HERE.md`, `AGENTS.md`,
  `docs/instruction-ownership.md`, and `PROGRESS.md`.
- Validation: complete `scripts/validate.py` passed all 77 tests, schema and
  manifest checks, the release-package smoke check, and the tracked-file privacy
  scan; a separate privacy scan, targeted entry-point/link checks, and
  `git diff --check` also passed.
- Publication to `origin/main` is the remaining action before the planned stop;
  no blocker or new product decision is open.
- Next: publish and verify this maintenance checkpoint, then wait for user
  confirmation before creating and linking the alpha.13 implementation
  specification. Do not begin runtime implementation.

## 2026-09-07 — alpha.13 implementation specification

- Created `docs/plans/0.1.0-alpha.13/SPEC.md` from the approved release plan and
  the actual alpha.12 tree. It inventories executable support separately from
  prose-only behavior and defines concrete modules, interfaces, schemas,
  durable/local ownership, state transitions, checkpoint boundaries, replay,
  uncertain-effect reconciliation, and failure outcomes.
- Organized ordered work as stable tasks M1-001 through M4-006. Milestones 1–3
  specify the offline clean install, connected scheduler-free manual operation,
  and fresh-process recovery path; Milestone 4 bounds migration, broader
  coverage, real-surface conformance, measurement, and release work.
- Selected the documented ChatGPT Work, Drive, Gmail, and Todoist mapping for
  the first scheduler-free manual journey, exercised in Milestones 1–3 through
  dependency-free Python 3.12 filesystem/fake adapters. This makes no
  real-provider support claim; M4 still requires observed evidence.
- Chose versioned byte-counted raw Markdown for new source records, structured
  JSON for operation/checkpoint/task state, one active mutating operation, and
  three scoped serialization modes. These are technical implementations of the
  approved losslessness, simplicity, manual-send, and cross-session decisions.
- Kept all four implementation milestones pending. No runtime code, manifest,
  release, private instance, provider object, or schedule changed. The optional
  adapters remain independent and the additional historical-retrieval
  acceptance case remains deferred.
- No unresolved product decision blocks Milestones 1–3. Real support claims,
  private migration variants, optional adapter selection, paid/external effects,
  release publication, and production activation require later evidence and/or
  explicit user approval as recorded in the specification.
- Relevant files: `docs/plans/0.1.0-alpha.13/SPEC.md`, its revised release-plan
  link/status in `docs/plans/0.1.0-alpha.13/PLAN.md`, and the reconciled root
  `PLAN.md` pointer.
- Validation: `python3 scripts/validate.py` passed all 77 tests, schema/template
  checks, release-package smoke verification, and the privacy scan with the new
  specification staged. Direct changed-file privacy scanning, local-link checks,
  25 unique stable-task checks, four-plan/four-spec pending-status checks, and
  `git diff --check` also passed.
- Publication remains unfinished for this documentation work.
- Next: commit only these documentation files, push `main`, verify the remote
  commit, and stop without starting implementation.

## 2026-09-07 — alpha.13 M1-001 shared package foundation

- Completed M1-001. `release.yaml` now declares the unreleased
  `0.1.0-alpha.13` candidate; no tag, publication, private instance, provider,
  schedule, or external effect was created.
- Added the standard-library-only `school_os` package. `contracts.py` is now the
  single owner of the supported YAML/JSON-contract subset, canonical JSON
  bytes, SHA-256, and diagnostics. `package.py` owns portable archive,
  checksum, inventory, version, and Git-free extracted-tree verification.
- Refactored `scripts/validate_instance.py`, `scripts/build_release.py`, and
  `scripts/validate.py` to reuse those helpers while preserving their CLI
  meanings. The existing deterministic Git build remains a development-only
  input step; extracted-package verification makes no Git call and accepts no
  Git metadata.
- Added shared-contract coverage and an extracted-archive test that confirms
  the root has no `.git` directory before verification. Changed files:
  `release.yaml`, `school_os/__init__.py`, `school_os/contracts.py`,
  `school_os/package.py`, `scripts/build_release.py`, `scripts/validate.py`,
  `scripts/validate_instance.py`, `tests/test_release_builder.py`,
  `tests/test_shared_contracts.py`, `PLAN.md`, and the alpha.13 plan/spec.
- Validation: `python3 scripts/validate.py` passed 80 tests, all schema/template
  checks, the exact-HEAD release-package smoke build, and the tracked-file
  privacy scan. A direct privacy scan of `school_os` and the new test passed;
  `git diff --check` passed.
- Consulted decisions: no new or conflicting product/architecture decision was
  discovered, so no consulting escalation was required.
- Unfinished: M1-002 through M4-006 remain pending; M1 is in progress. Exact
  next action: implement M1-002, the installed-only validator and its clean
  extracted-candidate negative tests, reusing `school_os.package` without Git
  or repository validation.

## 2026-09-07 — alpha.13 M1-002 sequencing blocker

- Blocked before implementing M1-002 because its required installed validation
  explicitly includes the operation registry, while ordered task M1-003 is the
  first task authorized to create `core/operations/registry.json` and its
  schema. A clean package built after M1-002 but before M1-003 therefore cannot
  both contain and validate the required registry.
- Reproduction/evidence: the M1 ordered-task table in
  `docs/plans/0.1.0-alpha.13/SPEC.md` lists M1-002 with only M1-001 as a
  dependency and says it validates the registry; its immediately following
  M1-003 says it adds that registry and schema. The release-plan M1 completion
  checks require the extracted package to validate.
- Working state is preserved at verified commit `1350122`; no M1-002 code or
  generated artifacts were started. The affected task is marked blocked in the
  release plan and specification.
- Next: obtain the user-authorized GPT-5.6 Sol High read-only consultation on
  whether M1-002 should validate a registry only when it is present, or depend
  on M1-003 / be reordered. Do not implement the disputed validator behavior
  until its recommendation is checked against the approved constraints.

## 2026-09-07 — alpha.13 M1 sequencing consultation resolution

- Consulted GPT-5.6 Sol with High reasoning in a read-only advisory role using
  the M1-002/M1-003 dependency table, current no-registry code state, the clean
  candidate acceptance, and the fail-closed/offline constraints. It confirmed
  that optional registry validation would incorrectly permit an incomplete
  package to pass.
- Resolved without new product authorization: preserve task IDs, execute
  `M1-001 -> M1-003 -> M1-002 -> M1-004 -> M1-005 -> M1-006`, and change
  M1-002 to depend on M1-001 and M1-003. The installed-validation acceptance
  now says Git must be unavailable without preventing validation; any attempted
  Git invocation is a test failure.
- Updated the release plan, implementation specification, and root summary to
  record the defect, resolution, revised order, and M1-003 as the exact next
  task. This restores the existing deterministic, offline, required-file gate;
  it creates no new architecture, provider integration, external effect, or
  release authorization.
- Validation pending for this documentation-only correction. Next: run the
  repository validation and privacy scan; commit and push the resolution; then
  implement M1-003 before M1-002.

## 2026-09-07 — alpha.13 M1-003 deterministic routing

- Completed M1-003 after the approved sequencing correction. Added the versioned
  `core/operations/registry.json`, its strict schema, and the object-reference
  schema. The registry maps `daily-run` only to the installed
  `core/operations/daily-run.md` payload path.
- Added `school_os/references.py`. It resolves opaque IDs through a minimal
  storage port and fail-closes on missing/different identity, kind, root
  containment, MIME, version, unsafe recipe paths, non-regular installed
  recipes, and ambiguous scoped discovery. Exact IDs intentionally beat
  same-named lookalikes.
- Updated the instance contract/template with the active release's exact
  registry path, revised the private bootstrap to resolve recipes through that
  registry, and extended repository validation to validate the registry schema.
- Added five focused resolver/registry tests. Validation: targeted resolver
  tests passed; `python3 scripts/validate.py` passed all 85 tests, schema and
  manifest checks, exact-HEAD release smoke build, and tracked privacy scan.
  A direct privacy scan of each new file and `git diff --check` passed.
- Consulted decisions: the M1 dependency correction remains the governing
  resolution; no new architectural issue appeared. M1-002 is now unblocked and
  next. Exact next action: implement the Git-free installed validator using the
  registry/schema and extracted-tree verification, including the candidate-mode
  and no-Git negative tests.

## 2026-09-07 — alpha.13 M1-002 installed validation

- Completed M1-002 after M1-003. Added `scripts/validate_installed.py`, which
  validates an extracted root or archive using only package bytes: inventory,
  manifest/schema/version, every schema document, registry, and mapped recipe.
  It never invokes Git or repository tests; unreleased candidates require the
  explicit `--candidate-test` flag.
- Added clean candidate tests with `.git` absent and `PATH` excluding Git,
  production rejection of `unreleased`, changed-byte detection, and missing
  registry/archive-evidence failures. `python3 scripts/validate.py` passed all
  88 tests; no provider or private-instance effect occurred.
- Next: M1-004, deterministic instance scaffolding with dedicated configuration
  and installation-manifest contracts.

## 2026-09-07 — alpha.13 M1-004 deterministic instance scaffolding

- Completed M1-004. Added dedicated household, integration, policy, daily-value,
  and installation-manifest schemas; converted the private daily companion to
  strict YAML front matter while retaining explanatory prose; and added the
  installation-manifest template and instance reference.
- Added `school_os.install` and `scripts/scaffold_instance.py`. The command
  accepts confirmed JSON answers, an extracted package plus verified archive,
  and observed/reference-return evidence; it writes a new local candidate only,
  validates every generated file and hash on readback, and rejects missing
  answers, unresolved placeholders, invalid package evidence, and malformed or
  out-of-root references. A separate storage-port readback gate proves each
  returned identity and complete byte sequence before a candidate becomes
  `verified`; no provider mutation occurs in this work unit.
- Added `tests/test_instance_scaffolding.py` (four tests): byte-stable candidate
  generation, schema/hash validation, missing-answer rejection, unreadable
  returned-reference rejection, and CLI coverage. Extended repository validation
  to check each dedicated template/schema and daily front matter. Focused tests
  and `python3 scripts/validate.py` passed 92 tests; the installed validator
  passed against an exact-HEAD candidate archive in explicit candidate mode.
- Consulted decisions: no new product or architectural decision was needed. The
  specification's staged installation boundary is implemented as written: JSON
  reference evidence is not treated as provider proof until exact storage
  readback succeeds.
- Unfinished: M1-005 and M1-006, then M2–M4, remain pending. Exact next action:
  implement M1-005 capability-profile/capability-planning contracts, including a
  scheduler-free qualified manual profile and named capability blockers.

## 2026-09-07 — alpha.13 M1-004 verification and handoff

- Accepted and pushed the M1-004 implementation as
  `0b81f56d061283cddfd3e48485fc39c2df54c6cf`
  (`Implement alpha.13 deterministic instance scaffolding`) on `main`.
- Post-commit evidence: `python3 scripts/validate.py` passed 92 tests, all
  schema/template checks, the tracked-file privacy scan, and the exact-HEAD
  release-package smoke check. An archive built from that exact commit passed
  `python3 scripts/validate_installed.py … --candidate-test` offline.
- Remote verification: `origin/main` resolved to the same commit; the working
  tree is clean. A sandboxed repeat lookup encountered DNS restriction, then
  the approved read-only GitHub lookup confirmed the same remote SHA.
- Next: M1-005. Add the capability-planning module and structured profile
  contracts; prove a scheduler-free manual profile qualifies while scheduled
  execution still requires scheduler evidence.

## 2026-09-07 — alpha.13 M1-005 capability planning

- Completed M1-005. Added `school_os.capabilities` with a fail-closed execution
  planner; expanded the capability profile with authentication health, adapter
  versions, network paths, local/read/pagination/file-transfer observations, and
  explicit record/byte limits. Unknown limits yield one record and 65,536 bytes,
  never an unlimited plan.
- The default template is now a scheduler-free `manual` profile. Manual
  qualification requires available storage/mail/task evidence; `scheduled`
  qualification additionally requires scheduler capabilities, adapter,
  network path, and observed scheduler behavior. Missing/unknown requirements
  return named blockers before provider effects. The legacy `interactive` form
  remains accepted only by the existing upgrade validator, not by the new
  execution planner.
- Updated the wrapper CLI, capability contract, and runtime-conformance tests.
  Focused capability tests and `python3 scripts/validate.py` passed 93 tests;
  no provider or private-instance action occurred.
- Next: M1-006, a fresh-process synthetic installation fixture that uses the
  extracted package and current scaffolder/capability contracts without mail,
  task, or delivery effects.

## 2026-09-07 — alpha.13 M1-006 synthetic clean installation

- Completed M1 and M1-006. Added checked-in synthetic answers, exact-reference
  evidence, an empty source corpus, filesystem storage fake, fixture mail/task
  adapters, and a send sink under `tests/support/` and
  `tests/synthetic-fixtures/alpha13/`.
- Added a fresh-process test that builds the exact candidate, extracts it, runs
  the extracted `scaffold_instance.py` with only fixture inputs, then resolves
  `daily-run` through the extracted registry. It reports candidate paths/hashes
  and creates no mail, task, or delivery effect; the fixture corpus remains
  empty and the fakes show no effects.
- Validation: focused synthetic-installation test and `python3 scripts/validate.py`
  passed 94 tests, schemas/templates, the release smoke check, and tracked-file
  privacy scan. M1 is now complete; no real provider or private instance was
  touched.
- Next: M2-001, versioned operation state/checkpoint contracts and legal
  transition validation.

## 2026-09-07 — alpha.13 M1 completion verification and handoff

- M1 implementation was pushed as
  `22fac8ad116849629189fe5245b46527ebd6f313`
  (`Add alpha.13 synthetic installation fixture`). Its exact archive passed the
  94-test repository gate and offline installed validation in candidate mode;
  `origin/main` was verified at that commit.
- Corrected the release-plan/specification milestone wording in follow-up commit
  `c3590efc25fb29c32a6f3a08a531bf1621491e77`: M1 is complete and M2 remains
  pending until M2-001 begins. No implementation scope changed.
- Working tree is clean. Next: begin M2-001 with the operation-state and
  operation-checkpoint schemas/templates plus legal transition validation.

## 2026-09-07 — alpha.13 M2-001 operation state and immutable checkpoints

- Completed M2-001. Added `schemas/operation-state.schema.json`,
  `schemas/operation-checkpoint.schema.json`, initial JSON state/checkpoint
  templates, `core/contracts/operation-state.md`, and
  `school_os/operations.py`. The module validates the approved transition
  table, canonical checkpoint SHA-256 pointers, exact predecessor chains,
  resumption attempt IDs, recipe-supplied completion phases, and
  pending/unknown-effect gates.
- Updated `schemas/instance.schema.json`, `templates/instance.yaml`,
  `templates/state/file-map.yaml`, `templates/state/README.md`, and
  `school_os/install.py`. New synthetic candidates now include a schema-valid
  `state/operation-state.json` and file map, each declared in the installation
  manifest and proved by the existing exact readback gate. The old YAML state
  remains a migration input only; `data_schema_version` and alpha.12 upgrade
  claims remain unchanged for M4 Migration 0002.
- Added `tests/test_operation_state.py` and manifest validation for both new
  templates. Focused state/scaffolding/synthetic-installation tests passed 17
  tests. The complete `PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate.py`
  gate passed 100 tests, schema/template checks, the exact-HEAD release smoke
  build, and tracked-file privacy scan. A direct privacy scan of every changed
  file and `git diff --check` passed.
- Consulted decisions: none. The state-format version is independent of the
  deferred instance data-schema migration, exactly as the specification allows;
  no contradiction, provider effect, private-instance access, or architectural
  escalation occurred.
- Unfinished: M2-002 through M4-006 remain pending; M2 is in progress. Exact
  next action: commit, push, and verify this M2-001 work unit, then implement
  M2-002's lossless v2 source/extraction contracts and catalog codec.
- Post-commit exact-HEAD validation initially found that the extracted
  synthetic-installation fixture lacked return references for the newly managed
  file map and operation-state files. No provider effect occurred. Added those
  synthetic references and an idle-state assertion; the M2-001 commit will be
  amended only after the exact-HEAD package gate passes.

## 2026-09-07 — alpha.13 M2-001 verification and handoff

- Amended and accepted M2-001 as
  `c928eb12157809576e2c1924fe562e2d3d9a9769`
  (`Implement alpha.13 operation state checkpoints`) on `main`. The initial
  exact-HEAD fixture failure recorded above is fixed in that same commit.
- Post-amend evidence: the complete repository gate passed all 100 tests,
  schema/template checks, tracked-file privacy scan, and exact-HEAD release
  smoke build. The exact archive passed offline
  `scripts/validate_installed.py --candidate-test`.
- Remote verification: `origin/main` resolved to
  `c928eb12157809576e2c1924fe562e2d3d9a9769`; the worktree was clean. The
  sandboxed remote lookup hit DNS restriction, and the approved read-only
  lookup confirmed the same SHA.
- Next: M2-002. Implement the versioned lossless source/extraction schemas and
  catalog codec, preserving adapter body bytes and proving both source-to-record
  equality and intended-to-persisted byte equality before indexing.

## 2026-09-07 — alpha.13 persistent development execution policy

- Recorded the user-authorized development execution policy in the alpha.13
  release plan. It requires autonomous ordered implementation through M4,
  recovery from repository evidence, continuity/publish checkpoints after every
  work unit, bounded read-only consultation for design failures, and a final
  stop only at authorized repository completion or a genuine blocker.
- Created the corresponding persistent development goal without a token budget
  or scheduled automation. This policy applies to development agents only and
  does not widen runtime or external-effect authorization.
- Validation/publication is pending for this documentation checkpoint. Exact
  next action: validate, privacy scan, commit, push, and verify it; then resume
  M2-002 without a routine stop.

## 2026-09-07 — alpha.13 execution-policy verification

- The execution policy was validated by the 100-test repository gate and its
  changed files passed a direct privacy scan and `git diff --check`.
- Published as `3bb832db93e9e6c06d973621649ff2ecce679f38`
  (`Record alpha.13 development execution policy`) on `main`; `origin/main`
  resolved to the same SHA and the worktree was clean.
- Next: continue M2-002 immediately with v2 lossless source/extraction
  contracts and the catalog codec.

## 2026-09-07 — alpha.13 M2-002 lossless v2 catalog codec

- Completed M2-002. Added source-conversation and extraction-result schemas,
  plus `school_os.catalog` with stable record IDs, exact UTF-8 byte-counted
  Markdown frames, strict v2 parsing, source-to-record comparison, and the
  independent intended-to-persisted readback gate. Updated the legacy validator
  to select the v2 codec for new records while retaining its legacy reader.
- Added delimiter-like-heading, Unicode, no-final-newline, truncation,
  reordering, source mismatch, and persisted-byte mismatch tests. Updated the
  source contract and daily recipe to make v2 framing authoritative for new
  records. No private source or provider effect was used.
- Validation/publication pending. Exact next action: run complete validation and
  privacy scan, commit/push/verify M2-002, then continue M2-003.

## 2026-09-07 — alpha.13 M2-002 verification

- M2-002 was accepted as `69c1e7f8470e6aecc5c321bae58d61dfe280c593`
  (`Implement alpha.13 lossless catalog codec`). The complete repository gate
  passed 104 tests and the changed files passed privacy scanning and diff checks.
- `origin/main` resolves to the same commit; no provider or private-instance
  effect occurred. Next: M2-003 canonical facts, tasks, and derived builders.

## 2026-09-07 — alpha.13 M2-003 canonical task and knowledge builders

- Completed M2-003. Expanded Fact provenance to require record/message IDs and
  byte spans; expanded canonical task and provider-state contracts; added the
  versioned `canonical-tasks.json` register and `school_os.tasks`.
- Source Facts now deterministically build source-linked task candidates,
  guidelines, and rolling updates. Guideline/action combinations fail, stable
  task IDs derive only from opening Fact IDs, rebuilds are byte-stable, and no
  title comparison is used as identity. The Markdown task table is explicitly a
  legacy/readable view.
- Added focused task tests and updated contract/template validation. No provider
  or private-instance effect occurred. Validation/publication pending. Exact
  next action: complete repository validation and privacy scan, commit/push/
  verify M2-003, then implement M2-004 guarded provider reconciliation.

## 2026-09-07 — alpha.13 M2-003 verification

- M2-003 was accepted as `1aaa9f028f4ec773fdff5b2333eae41372cc4153`
  (`Implement alpha.13 canonical task builders`). The complete repository gate
  passed 107 tests and every changed file passed privacy/diff checks.
- `origin/main` resolves to the same commit. Next: M2-004 provider protocol,
  pull-first reconciliation, guarded writes, bindings, and parent-edit safety.

## 2026-09-07 — alpha.13 M2-004 guarded provider reconciliation

- Completed M2-004. Added the narrow task-provider protocol, pull-first
  snapshot reconciliation, managed-projection hashes, create/patch intent
  records, exact readback, and unique durable bindings in `school_os.tasks`.
- Extended the synthetic task fake and proved one canonical-ID provider task is
  created/read back/bound once; a replay patches only managed fields and
  preserves the synthetic provider's unrelated parent field. Updated task-sync
  instructions with the same guarded-write boundary.
- Validation/publication pending. Exact next action: run repository validation
  and privacy scan, commit/push/verify M2-004, then implement M2-005 rendering
  and delivery ledger contracts.

## 2026-09-07 — alpha.13 M2-004 verification

- M2-004 was accepted as `5cd9acaed055e520b62808b6ddf421ac231d9476`
  (`Implement alpha.13 provider reconciliation`). The repository gate passed
  108 tests and changed files passed privacy/diff checks.
- `origin/main` resolves to the same commit. Next: M2-005 deterministic brief
  rendering, templates, delivery ledger, and send-sink verification.

## 2026-09-07 — alpha.13 M2-005 deterministic brief and ledger

- Completed M2-005. Added brief-input and delivery-ledger schemas, static
  HTML/plain templates/theme, and `school_os.brief` deterministic renderer.
  It keeps News, Guidelines, and Action Items separate, escapes content/links,
  emits explicit empty sections, and returns stable bytes for identical input.
- Added send-sink ledger confirmation with content hashes and duplicate key
  suppression; tests prove one confirmed delivery entry. No real send/provider
  action occurred. Validation/publication pending. Exact next action: validate,
  privacy scan, commit/push/verify M2-005, then implement M2-006 shared daily
  entrypoints and operation pipeline.

## 2026-09-07 — alpha.13 M2-005 verification

- M2-005 was accepted as `475219335754a6a12f5758412b71f74e7e6378a4`
  (`Implement alpha.13 deterministic briefs`). The repository gate passed 110
  tests and changed files passed privacy/diff checks.
- `origin/main` resolves to the same commit. Next: M2-006 shared daily runner,
  adapter protocols, and manual/scheduled entrypoint alignment.

## 2026-09-07 — alpha.13 M2-006 shared daily entrypoints

- Completed M2-006. Added provider-neutral `school_os.adapters` protocols and
  normalized complete-read, page, and effect outcome records. Added
  `school_os.daily.run_daily`, which fails closed without nonempty
  operation/attempt identities, qualifies the actual manual or scheduled
  surface before phases, passes each verified predecessor result forward, and
  requires every named phase. A scheduled entrypoint adds verified scheduler
  admission; a direct manual entrypoint requests no scheduler capability.
- Added the thin synthetic-only `scripts/run_operation.py` host entrypoint,
  documented the executable adapter boundary, and revised daily/manual recipes
  and contract tests to retire scheduler-only manual dispatch while preserving
  delivery/recovery and no-lease requirements. The entrypoint makes no real
  provider call or production-conformance claim.
- Focused daily/recipe tests passed 10 tests. The complete
  `PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate.py` gate passed 113
  tests plus schema/template and release-smoke validation. No design
  contradiction, provider effect, private-instance access, or consultation
  occurred.
- Changed files: `school_os/adapters.py`, `school_os/daily.py`,
  `scripts/run_operation.py`, `tests/test_daily_runner.py`,
  `tests/test_manual_daily_run_contract.py`, `core/contracts/adapters.md`,
  `core/operations/daily-run.md`, `core/operations/manual-daily-run.md`, root
  `PLAN.md`, and the alpha.13 plan/specification.
- Validation/publication remains pending. Exact next action: privacy-scan the
  changed tracked and new files, commit/push/verify M2-006, then implement the
  M2-007 connected daily-run test using only installer output and predecessor
  artifacts.

## 2026-09-07 — alpha.13 M2-006 verification

- M2-006 was accepted as `8770bc505eaf28f956cc10d546db4029c1de0604`
  (`Implement alpha.13 shared daily entrypoints`). The repository gate passed
  113 tests, schema/template checks, and release-smoke validation; direct
  privacy scanning included all four new files and `git diff --check` passed.
- `origin/main` was read back at the exact same SHA. No real adapter, provider,
  delivery, scheduler, or private instance was touched. Next: M2-007, compose
  the connected daily-run fixture from M1 installer output and actual verified
  predecessor artifacts, then prove substitution fails.

## 2026-09-07 — alpha.13 M2-007 connected installed daily run

- Completed M2-007 and Milestone 2. Added the connected source/fact fixture and
  `tests/test_connected_daily_run.py`. It builds and extracts the exact HEAD
  package, scaffolds the M1 candidate, then runs the scheduler-free manual
  entrypoint through discovery, catalog, reconciliation, provider binding,
  brief/delivery, final evidence, and last-written eligible cursors.
- Every stage reads the verified predecessor artifact. The fixture records
  expected SHA-256 values for all persisted connected artifacts; the catalog
  retains exact source bytes, facts link to the generated record, task sync
  creates and reads back one stable canonical binding, and the send sink records
  exactly one confirmed delivery. A substitution of the persisted catalog
  artifact blocks before task sync or delivery.
- Focused connected tests passed 2 tests. The complete
  `PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate.py` gate passed 115
  tests, schema/template checks, and release-smoke validation. This is synthetic
  behavioral evidence only; it does not establish Gmail, Todoist, Drive, or
  scheduled-runtime conformance. No consultation, private-instance access, or
  provider effect occurred.
- Changed files: `tests/test_connected_daily_run.py`,
  `tests/synthetic-fixtures/alpha13/connected-daily-run.json`, root `PLAN.md`,
  and the alpha.13 plan/specification. Validation/publication is pending.
  Exact next action: privacy-scan, commit/push/verify M2-007, then begin M3-001
  recovery/admission and fresh-process checkpoint-chain work.

## 2026-09-07 — alpha.13 M2-007 verification and milestone handoff

- M2-007 was accepted as `e862dc8e5ab67fbdc5c324ac06c10cf2d33dbdff`
  (`Add alpha.13 connected daily journey`). The 115-test repository gate,
  direct new-file privacy scan, and diff checks passed; `origin/main` was read
  back at the exact same SHA.
- Milestone 2 is complete with synthetic connected-path evidence only. Next:
  M3-001, add durable recovery/admission behavior to the operation and daily
  entrypoint, then prove a fresh process resumes one operation ID with a new
  attempt after local-work loss.

## 2026-09-07 — alpha.13 M3-001 durable admission and fresh-process recovery

- Completed M3-001. Added immutable longest-chain discovery with ambiguity
  blocking and resumption validation that retains one operation ID, requires a
  new attempt ID, and points exactly to the recovered chain tip. The daily
  runner now returns `NEEDS_CONTINUATION` at a verified planned boundary and
  resumes only from supplied durable predecessor output.
- Added focused state/runner tests and a new-process harness that deletes local
  output before resuming the same operation at the next phase. Focused tests
  passed 13 tests; the full validation gate passed 119 tests, schema/template
  checks, and release-smoke validation. No private or provider effect occurred.
- Changed files: `school_os/operations.py`, `school_os/daily.py`,
  `tests/test_operation_state.py`, `tests/test_daily_runner.py`,
  `tests/test_fresh_process_recovery.py`, root `PLAN.md`, and alpha.13 plan/spec.
  Validation/publication pending. Exact next action: privacy-scan, commit/push/
  verify M3-001, then implement M3-002 catalog/index write-fault recovery.

## 2026-09-07 — alpha.13 M3-001 verification

- M3-001 was accepted as `7f3c16548f80fef6f0027248bf2454cdbc1cfa50`
  (`Implement alpha.13 daily recovery admission`). The complete repository gate
  passed 119 tests; direct privacy scanning included the new fresh-process test,
  and `origin/main` was read back at the exact same SHA.
- Next: M3-002 catalog/index write-fault recovery. The task must adopt one
  verified durable record after interruption without duplicate index rows or
  renumbered Facts.

## 2026-09-07 — alpha.13 M3-002 catalog/index write-fault recovery

- Completed M3-002. Added pure catalog recovery that first re-verifies exact
  source bodies and persisted record bytes, then adopts a single stable index
  row with the supplied stable Fact IDs. Existing identical rows are idempotent;
  corrupt bytes, duplicate rows, or a Fact linked to another record block.
- Added storage-write fault simulation: a record exists before the index write,
  then recovery publishes one row and replay leaves it unchanged. Focused tests
  passed 6 tests; the complete gate passed 121 tests, schema/template checks,
  and release-smoke validation. No private or provider effect occurred.
- Changed files: `school_os/catalog.py`, `tests/test_operation_recovery.py`,
  root `PLAN.md`, and the alpha.13 plan/specification. Validation/publication
  pending. Exact next action: privacy-scan, commit/push/verify M3-002, then
  implement M3-003 task fault recovery and parent-edit preservation.

## 2026-09-07 — alpha.13 M3-002 verification

- M3-002 was accepted as `097a3f7351bffc9064a1932dd0a317a37659c47b`
  (`Implement alpha.13 catalog recovery`). The full repository gate passed 121
  tests, direct privacy scanning included the new recovery test, and
  `origin/main` was read back at the same SHA.
- Next: M3-003 task create/update/comment fault recovery and parent-edit
  preservation, using immutable canonical task IDs and provider readback.

## 2026-09-07 — alpha.13 M3-003 task effect recovery and parent edits

- Completed M3-003. Lost task-create responses recover through canonical ID
  without duplication. Lost immutable comments are adopted after complete
  lookup; duplicate comment matches block. Parent-edited title/group fields
  survive reconciliation and create review evidence rather than overwrite.
- Focused tests passed 3 tests; the full gate passed 123 tests. No private or
  provider effect occurred. Changed files: `school_os/tasks.py`,
  `tests/support/fakes.py`, `tests/test_provider_reconciliation.py`, root
  `PLAN.md`, and alpha.13 plan/specification. Validation/publication pending.
  Exact next action: privacy-scan, commit/push/verify M3-003, then implement
  M3-004 delivery recovery and duplicate-entrypoint safety.

## 2026-09-07 — alpha.13 M3-003 verification

- M3-003 was accepted as `8fd22f01e04665e5807c970e6973c71e917a832a`
  (`Implement alpha.13 task recovery`). The 123-test repository gate and direct
  privacy scan passed; `origin/main` was read back at the exact same SHA.
- Next: M3-004 delivery recovery, correction variants, and overlapping-entrypoint
  duplicate prevention.

## 2026-09-07 — alpha.13 M3-004 delivery recovery and duplicate prevention

- Completed M3-004. Delivery intent is durable before send; lost-send recovery
  confirms one matching result, blocks unknown/ambiguous lookup, suppresses a
  duplicate entrypoint from creating the same key, and uses distinct keys for
  correction variants.
- Focused delivery/connected tests passed 5 tests; the full gate passed 124
  tests. No real send occurred. Changed files: `school_os/brief.py`,
  `tests/support/fakes.py`, `tests/test_brief.py`, root `PLAN.md`, and alpha.13
  plan/specification. Validation/publication pending. Exact next action:
  privacy-scan, commit/push/verify M3-004, then implement M3-005 transition,
  stale-auth, capacity, cancellation, and non-progress cases.

## 2026-09-07 — alpha.13 M3-004 verification

- M3-004 was accepted as `133b96a81433ab0661da027a5823398fe4632284`
  (`Implement alpha.13 delivery recovery`). The 124-test gate and direct
  privacy scan passed; `origin/main` was read back at the exact same SHA.
- Next: M3-005 lifecycle safety cases for configuration/release drift, stale
  authentication, capacity/non-progress, cancellation, and terminal effects.

## 2026-09-07 — alpha.13 M3-005 lifecycle safety

- Completed M3-005. Recovery accepts matching release/configuration evidence
  and blocks material drift; stale authentication stops qualification; bounded
  limits remain conservative; a resumed minimum unit with no progress blocks;
  and cancellation cannot hide an unknown provider effect.
- Focused tests passed 14 tests and the complete gate passed 126 tests. No
  private/provider effect occurred. Changed files: `school_os/operations.py`,
  `school_os/daily.py`, operation-state/daily-run tests, root `PLAN.md`, and
  alpha.13 plan/spec. Validation/publication pending. Exact next action:
  privacy-scan, commit/push/verify M3-005, then finish M3-006 recovery docs and
  compact expected evidence.

## 2026-09-07 — alpha.13 M3-005 verification

- M3-005 was accepted as `9c333ee914e0e8c39d7c988e56af8f47f192a5ad`
  (`Implement alpha.13 lifecycle safety`). The 126-test repository gate,
  privacy scan, and diff checks passed; `origin/main` was read back at the same
  SHA. Next: complete M3-006 documentation and fresh-process recovery evidence.

## 2026-09-07 — alpha.13 M3-006 recovery evidence and documentation

- Completed M3-006. Added the compact synthetic recovery-evidence manifest and
  its assertion, then extended the fresh-process harness to delete local work
  and recover catalog/index, provider task creation/update, immutable comments,
  and a pending delivery ledger from durable JSON in child processes. Lost
  update responses now adopt a matching provider projection instead of issuing
  a second patch. The existing
  fresh-process daily case continues to prove planned-boundary continuation
  with one operation ID and a new attempt ID.
- Updated the operation-state contract, daily-run recipe, state-template
  guidance, test strategy, README, root summary, and release plan/specification
  to state immutable longest-chain selection, fingerprint-gated resumption,
  checkpoint boundaries, unknown-effect safety, and the synthetic-evidence
  boundary. M3 is now complete; M4-001 is next.
- Focused recovery tests passed 7 tests (including the lost update response),
  and the complete `PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate.py` gate
  passed 129 tests plus schema/template and release-smoke validation. Direct
  privacy scanning of both new files and `git diff --check` passed.
  Changed files: `tests/test_fresh_process_recovery.py`,
  `tests/support/fresh_process_recovery.py`,
  `tests/synthetic-fixtures/alpha13/recovery-evidence.json`, recovery docs,
  `README.md`, `PLAN.md`, and alpha.13 plan/specification. Commit/push/remote
  verification remain pending. Exact next action: publish and verify this
  M3-006 checkpoint before starting M4-001.

## 2026-09-08 — alpha.13 M3-006 verification and M4 handoff

- M3-006 was accepted as `811f03961da0101454a8ef7db6d0f33f3cf6d21c`
  (`Complete alpha.13 recovery evidence`). The 129-test repository gate,
  direct new-file privacy scan, and diff checks passed; `origin/main` was read
  back at that exact SHA. M3 is complete with synthetic repository evidence.
- Next: M4-001, inspect the import/catalog and attachment path against the
  complete multi-page, bounded-resume, no-new-message, and explicit unsupported
  content requirements before changing the design. Real-provider conformance
  remains outside this evidence and is not authorized here.

## 2026-09-08 — alpha.13 M4-001 bounded import and attachment coverage

- Completed M4-001. Added `school_os.importer` for complete page-token and
  immutable-identity enumeration, stable whole-record batches from durable
  completed IDs, and visible exact attachment outcomes. The initial supported
  extraction is exact `text/plain` UTF-8; unsupported/oversized content has no
  inferred text. Added a synthetic multi-page fixture and focused import tests.
- Added the no-new-message daily-run proof that reconciliation and brief
  generation still run, and updated import/attachment recipes and test guidance
  with the same limits, evidence, and non-inference boundary. No provider,
  delivery, or private-instance effect occurred.
- Focused import/daily tests passed 9 tests; the complete
  `PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate.py` gate passed 133
  tests plus schema/template and release-smoke validation. Direct privacy
  scanning of all three new files and `git diff --check` passed. Changed files:
  `school_os/importer.py`, `tests/test_import_runner.py`,
  `tests/synthetic-fixtures/alpha13/import-pages.json`,
  `tests/test_daily_runner.py`, import/attachment/test documentation, root
  `PLAN.md`, and alpha.13 plan/specification. Commit/push/remote verification
  remain pending. Exact next action: publish M4-001 before M4-002.

## 2026-09-08 — alpha.13 M4-001 verification

- M4-001 was accepted as `d2611583c587175a5ac8fa899cc2379477ae3967`
  (`Add alpha.13 bounded import coverage`). The 133-test repository gate,
  direct new-file privacy scan, and diff checks passed; `origin/main` was read
  back at the same SHA. Next: M4-002, inspect exact alpha.12 template/record
  forms and existing upgrade coordination before implementing only the declared
  migration surface.

## 2026-09-08 — alpha.13 M4-002 structured-state migration

- Completed M4-002. Added the strict `migrate_alpha12` transformer and
  Migration 0002 procedure for the exact alpha.12 idle operation-state YAML,
  instance/file-map forms, and readable task table. It composes schema-valid,
  byte-stable alpha.13 candidates, preserves supported task/completion data,
  requires an explicit target release version, and blocks active state or
  altered/unmappable legacy content without writing private files.
- Updated alpha.13 candidate metadata and new-install output to data schema 2
  and declared Migration 0002. The upgrade recipe documents its strict input,
  backup/readback, idempotence, and compatible-extension boundary. Added an
  alpha.12 synthetic fixture and migration tests. No private migration,
  production activation, or provider effect occurred.
- Focused migration/scaffold/package tests passed 19 tests; the complete
  `PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate.py` gate passed 136
  tests plus schema/template and release-smoke validation. Direct privacy scan
  of all four new files and `git diff --check` passed. Changed files:
  `school_os/migrate_alpha13.py`, `migrations/0002-alpha13-structured-state.md`,
  `school_os/install.py`, `release.yaml`, migration fixtures/tests, upgrade/test
  documentation, root `PLAN.md`, and alpha.13 plan/specification. Commit/push/
  remote verification remain pending. Exact next action: publish M4-002, then
  inspect M4-003's conformance claims against available authorized surfaces.

## 2026-09-08 — alpha.13 M4-002 verification

- M4-002 was accepted as `285124cf486e870b16df61222c31a4a62c84a226`
  (`Add alpha.13 structured state migration`). The 136-test repository gate,
  direct new-file privacy scan, and diff checks passed; `origin/main` was read
  back at the same SHA. Next: M4-003, distinguish synthetic adapter coverage
  from claims requiring observed authorized runtime/provider surfaces.

## 2026-09-08 — alpha.13 M4-003 conformance safety preparation

- Completed the authorized repository portion of M4-003. Capability profiles
  now identify `unverified`, `synthetic`, or `observed` evidence, and scheduled
  qualification fails unless evidence is explicitly observed. The public
  ChatGPT Work runtime/scheduler mappings now identify themselves as reference
  material rather than scheduled-support claims without a private record.
- Added synthetic checks for separate storage/mail/task/scheduler network-path
  failure, authentication/limit qualification, observed-surface gating, and a
  shared manual/scheduled delivery key. Focused conformance/brief/connected
  tests passed 20 tests; the complete
  `PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate.py` gate passed 138 tests
  plus schema/template and release-smoke validation. Privacy scan and
  `git diff --check` passed. No provider, scheduler, delivery, or private
  instance was contacted.
- **Blocker:** M4-003 requires current observed evidence for the exact private
  runtime, storage, mail, task, and scheduled surfaces. The current
  authorization explicitly excludes private-instance inspection and real
  provider/scheduler actions, and this repository contains only synthetic
  evidence. M4-003 therefore remains incomplete; M4-004–M4-006 are dependent
  and cannot start. Changed files: capability schema/template/qualification,
  runtime/scheduler mappings, conformance/daily/brief tests, root `PLAN.md`,
  and alpha.13 plan/specification. Commit/push/remote verification is pending.
  Exact next action: publish this repository checkpoint; resume only with
  authorization and access for no-write observed conformance probes (then any
  separately authorized write/send probes required by the adapters).

## 2026-09-08 — alpha.13 M4-003 repository-checkpoint verification

- The M4-003 repository safeguard work was accepted as
  `a230b6af9f8494f5df93d22f55e371033c56e187`
  (`Require observed scheduled conformance evidence`). The 138-test repository
  gate, privacy scan, and diff checks passed; `origin/main` was read back at
  the same SHA.
- M4-003 remains blocked, not complete: it needs current `observed` evidence
  from the exact authorized private runtime, storage, mail, task, and scheduler
  surfaces. M4-004–M4-006 remain dependency-blocked. Exact next action: obtain
  that access/authorization, run no-write capability probes first, and record
  private surface-specific evidence before any separately authorized mutation.

## 2026-09-08 — alpha.13 private-instance upgrade preflight blocker

- Under explicit user authorization, completed a read-only inventory of the
  existing private Drive installation. It reports release `0.1.0-alpha.11` and
  data schema version `1`; no private catalog, message body, configuration
  secret, provider object, scheduler, or file bytes were changed.
- M4-002 intentionally implements only the declared alpha.12-to-alpha.13
  structured-state migration. The observed alpha.11 instance is therefore an
  unsupported predecessor for a direct alpha.13 upgrade. Existing private
  backup history was observed but not relied upon as a substitute for a
  supported migration input.
- This is a compatibility/design decision rather than a routine coding error.
  Per the alpha.13 execution policy, implementation and any private-instance
  write are paused while a bounded GPT-5.6 Sol High read-only consultation
  evaluates whether the approved plan already supplies a safe supported path
  or requires a new user-approved migration scope.
- Next: record the consultation finding in the alpha.13 specification and
  release plan as appropriate; do not modify the private instance unless a
  supported, approved path is established.

## 2026-09-08 — alpha.13 alpha.11 upgrade-boundary consultation and guard

- Completed the required bounded GPT-5.6 Sol High read-only consultation for
  the authorized private upgrade preflight. It confirmed that no approved
  direct alpha.11-to-alpha.13 path exists: Migration 0002 explicitly accepts
  only alpha.12 forms, while alpha.13 remains an unreleased candidate. Adding
  direct alpha.11 support would change the approved release/upgrade boundary
  and requires new user approval; no private write or activation occurred.
- The consultation also exposed an in-scope fail-closed defect: the transformer
  checked schema-1 shape but did not assert its legacy manifest and active
  release were alpha.12. It now requires both exact alpha.12 version values;
  a regression test proves alpha.11 is rejected without candidates. The release
  plan and specification now record the consultation, current private
  predecessor, and the only within-scope conditional route: first complete a
  read-only alpha.12-compatibility audit, then use the immutable alpha.12
  release only if that audit passes. Alpha.13 itself still needs its release
  gates before any production upgrade.
- Changed files: `school_os/migrate_alpha13.py`,
  `tests/test_alpha13_migration.py`, `PLAN.md`, and the alpha.13 plan and
  specification. No private identifiers, catalog content, credentials, or
  provider records were added to the repository.
- Next: run focused migration tests and the full repository/privacy gate; if
  accepted, publish this guard checkpoint, then perform only the authorized
  read-only alpha.12-compatibility audit of the existing instance.

## 2026-09-08 — alpha.11-to-alpha.12 compatibility audit blocker

- Per the accepted consultation path, performed the authorized read-only
  alpha.12-compatibility audit after publishing the alpha.13 source-version
  guard. The existing alpha.11 source-catalog area contains native-document
  storage alongside raw Markdown. Alpha.12 requires raw UTF-8 Markdown and
  direct byte-level source-to-catalog comparison, so the conditional staged
  alpha.11-to-alpha.12 route fails closed.
- No catalog content, metadata, source message, provider binding, credential,
  scheduler, or file bytes were copied into the repository or changed in the
  private instance. The root plan, alpha.13 plan, and specification record the
  generic incompatibility without private identifiers.
- Next: validate and publish this evidence checkpoint. Direct upgrade remains
  blocked until the user either approves a new alpha.11 preservation/migration
  scope or supplies a separately verified compatible intermediate release and
  mapping; alpha.13 remains unreleased and cannot be activated in either case.

## 2026-09-08 — alpha.11 capability-profile preflight blocker

- Performed one further authorized read-only capability-profile check. The
  alpha.11 profile is scheduled-only and uses an older evidence shape without
  alpha.13's explicit `observed` classification. It therefore cannot qualify
  the attended upgrade surface required by `system-upgrade.md` or establish
  M4-003 runtime/scheduler conformance.
- No private profile, scheduler, provider object, catalog, credential, or file
  was changed. Updated only the generic root-plan/specification summaries and
  this append-only log; no private identifiers or content were recorded.
- Next: validate and publish this checkpoint. The upgrade remains blocked on a
  user-approved alpha.11 preservation/migration scope; alpha.13 release and
  real-surface conformance gates remain separately unfinished.

## 2026-09-08 — alpha.13 inactive candidate observation planning

- Confirmed a newly supplied private Drive root is a folder, private to the
  owner, and empty. No existing private instance was read or changed in this
  work unit; no Gmail message body, task, delivery, scheduler, release, or
  activation effect occurred.
- Completed the user-authorized bounded GPT-5.6 Terra High read-only review.
  It found that a Drive/Gmail mapping can be a compatible expansion when it
  preserves the existing storage/mail contracts unchanged. The approved
  candidate boundary requires an explicit Gmail scope, create-only byte files
  under the exact root with complete readback, lossless UTF-8-only source
  admission, and a fresh-process catalog/index recovery proof. It cannot
  establish delivery, task, scheduler, full daily-run, production, migration,
  or release-readiness conformance.
- Changed files: `PLAN.md`, `docs/plans/0.1.0-alpha.13/PLAN.md`,
  `docs/plans/0.1.0-alpha.13/SPEC.md`, and this append-only log. No private
  identifiers, queries, source content, credentials, or provider records were
  added to the repository.
- Blocker: the required source scope is not yet explicit. The onboarding
  contract requires a direct user source-scope answer; choosing a Gmail query,
  label, window, or target message would risk importing unrelated mail.
  Next: validate and publish this generic planning checkpoint, then obtain the
  bounded Gmail scope before re-listing the candidate root and performing any
  private write.

## 2026-09-08 — alpha.13 candidate manifest write-path blocker

- Recovered the existing private source-scope configuration read-only and
  enumerated its current bounded mail window without changing Gmail. The
  candidate root remains empty. No source body was catalogued and no candidate
  object, task, delivery, scheduler, release, or activation effect occurred.
- **Blocked before candidate creation:** the scaffolder's installation manifest
  requires real object references for every managed file and for the manifest
  itself; its readback gate requires the final stored bytes to match those
  references. The selected Drive create/upload surface returns an object ID only
  after it writes the bytes and exposes no preallocated-ID operation. The
  candidate boundary permits create-only files, so a final self-referential
  manifest cannot be created without an update or a different staging protocol.
  Accepting placeholder references, omitting the manifest self-reference, or
  using a replace without an approved recovery design would weaken the accepted
  installation/readback contract.
- Per the development execution policy, paused the affected write design and
  started one bounded GPT-5.6 Sol High read-only consultation with the relevant
  plan/specification, `school_os/install.py`, Drive create semantics, and the
  concrete empty-root reproduction. No implementation proceeds until its
  recommendation is assessed against approved constraints.
- Changed files: this append-only log only. No private identifiers, queries,
  message content, credentials, or provider records were added to the
  repository. Next: record the consultation finding and either resume with an
  in-scope verified protocol or report the specific architectural decision
  required.

## 2026-09-08 — alpha.13 create-only installation correction

- Completed the required bounded GPT-5.6 Sol High read-only consultation for
  the candidate manifest contradiction. It found the recursive post-create-ID
  requirement is an implementation/contract defect, not an approved product
  invariant or a new architectural decision.
- Resolution within scope: create and read back immutable payloads first;
  create a non-self-referential content manifest containing their exact
  references and hashes; create/read back an immutable admission receipt that
  names that manifest; then create the stable bootstrap last. Its returned ID
  is the external trust anchor for fresh recovery. No mutable pointer, replace,
  placeholder acceptance, or weakened reference verification is allowed.
- Reopened M1-004 and M1-006 for implementation and tests. M2–M3 retain their
  accepted synthetic behavior but must be revalidated once the installer is
  repaired. Updated root and alpha.13 plans/specification accordingly. No
  private candidate or existing-instance write occurred.
- Changed files: `PLAN.md`, `docs/plans/0.1.0-alpha.13/PLAN.md`,
  `docs/plans/0.1.0-alpha.13/SPEC.md`, and this append-only log. Next:
  implement the versioned create-only installation manifest/admission/bootstrap
  flow with loss/recovery and forbidden-update tests before any private Drive
  write.

## 2026-09-08 — alpha.13 create-only installation implementation checkpoint

- Implemented the first corrective installation slice: version-2 content
  manifests no longer contain impossible self-references; added the immutable
  admission-receipt schema/template; clarified bootstrap admission order; and
  added a create-only installer helper that reads back every payload, content
  manifest, admission receipt, and bootstrap without replace operations.
- Added focused fake-storage coverage for create-only ordering and lost create
  responses. Existing local scaffolding remains available while the broader
  recovered-generation and installed-package tests are updated.
- Changed files: `school_os/install.py`, installation schemas/templates,
  `templates/BOOTSTRAP.md`, instance-scaffolding fixtures/tests, root and
  alpha.13 plan/specification, and this append-only log. Focused validation:
  `python3 -m unittest tests.test_instance_scaffolding` passed (6 tests);
  `scripts/privacy_scan.py` and `git diff --check` passed. No private Drive or
  Gmail write occurred.
- Unfinished: add lost-response adoption/ambiguity/tamper/fresh-bootstrap
  recovery tests; make the staged helper construct the real candidate payload
  sequence; run the complete gate from the repaired exact package; then update
  M1/M2/M3 status only if that evidence passes. Next: publish this recoverable
  corrective checkpoint and continue those tests before private candidate work.

## 2026-09-08 — alpha.13 create-only lost-response adoption

- Extended the create-only installer to treat a failed create response as an
  unknown outcome: it performs one exact scoped lookup by parent/name/kind/MIME,
  adopts only a unique matching object after complete byte readback, and never
  retries the create. Missing or ambiguous lookup remains a named blocker.
- Focused validation: `python3 -m unittest tests.test_instance_scaffolding`
  passed (6 tests), including the lost-response adoption path. No private Drive
  or Gmail write occurred.
- Changed files: `school_os/install.py`, `tests/test_instance_scaffolding.py`,
  and this append-only log. Unfinished: ambiguity/tamper/fresh-bootstrap
  recovery coverage and integration of the staged helper with real candidate
  payload construction. Next: validate, publish this checkpoint, then continue
  the remaining M1-004/M1-006 recovery cases before any candidate write.

## 2026-09-08 — alpha.13 immutable bootstrap recovery gate

- Extended the corrected create-only installer with a fresh-bootstrap recovery
  gate. It accepts only the exact bootstrap reference, immutable admission
  receipt, content-manifest hash, root-contained payload references, and exact
  payload bytes. It blocks ambiguous lost creates, altered manifest/receipt or
  payload bytes, parent/MIME disagreement, and incomplete generations; it has
  no replace operation.
- Focused installation/scaffolding, synthetic-installation, and installed
  validation tests passed (12 tests). The complete
  `PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate.py` gate passed 143
  tests plus schema/template and release-smoke validation. `git diff --check`
  and `scripts/privacy_scan.py` passed. No private Drive or Gmail write
  occurred.
- Changed files: `school_os/install.py`, `tests/test_instance_scaffolding.py`,
  the alpha.13 specification, and this append-only log. Unfinished: integrate
  the staged installer with a real candidate payload/layout builder and
  revalidate M1/M2/M3 from the repaired package before touching the candidate
  root. Next: implement that staged payload builder and its exact-reference
  tests; the candidate root remains untouched.

## 2026-09-08 — alpha.13 staged candidate-payload composition

- Added a create-only composition step for the real installation sequence. It
  creates the final idle operation-state payload first, uses only that observed
  reference to compose the remaining final private bytes, and then admits all
  payloads through the immutable manifest/receipt/bootstrap sequence. Internal
  validation-only references are discarded and regression-tested never to
  enter payload bytes or provider writes.
- Focused scaffolding tests passed (9 tests). No candidate folder, existing
  instance, Gmail, task provider, delivery, scheduler, or release was changed.
- Changed files: `school_os/install.py`, `tests/test_instance_scaffolding.py`,
  the alpha.13 specification, and this append-only log. Unfinished: run the
  full package/repository gate, publish this builder checkpoint, then create
  the bounded inactive candidate only after a final empty-root readback.
  Next: validate and publish the staged builder; afterwards perform the
  authorized candidate preflight without touching the existing instance.

## 2026-09-08 — alpha.13 candidate multipart source-admission blocker

- Created and read back a new inactive candidate's create-only private
  installation generation under the user-authorized empty Drive root. The
  package was built from the verified current commit; payloads, content
  manifest, admission receipt, and final bootstrap were read back privately.
  One incorrectly named initial state object was left as an unadmitted staging
  orphan and was not renamed, replaced, or deleted; the correctly named state
  object is the one admitted by the manifest. No existing instance, task,
  delivery, scheduler, release, or Gmail object was modified.
- The fixed, read-only Gmail test scope enumerated to its terminal page. Before
  cataloguing the first selected message, complete thread inspection showed a
  multipart message with both plain-text and HTML alternatives. Alpha.13's v2
  catalog persists exact plaintext only and has neither a raw-MIME preservation
  artifact nor an approved equivalence rule for alternatives. Treating the
  plaintext part as lossless would contradict the source-preservation boundary.
- Per the execution policy, stopped the affected import design and completed
  one bounded GPT-5.6 Sol High read-only consultation. It found the approved
  in-scope result is only an immutable `unsupported`/`manual_review`
  disposition with no source/catalog/index/derived write; a positive raw-MIME
  admission path is a core source/provenance decision requiring user approval.
  No private IDs, queries, domains, message content, credentials, or provider
  records were added to this repository. Next: either implement and validate
  the negative disposition/retry coverage without source admission, or obtain
  explicit approval for a versioned raw-source architecture before importing
  any message; do not continue the 30-message positive import under the current
  contract.

## 2026-09-08 — alpha.13 fail-closed multipart admission gate

- Implemented the consultation's in-scope negative resolution in
  `school_os.importer`: only one complete identity-transfer UTF-8 `text/plain`
  byte sequence may reach a source admission. Alternatives (even byte-equal),
  nested/extra MIME content, attachments, charset or transfer-decoding
  differences, malformed metadata, and unavailable bytes are non-admitting;
  no helper creates catalog/index/derived output.
- Focused importer tests passed (4 tests), including deterministic replay of
  the blocked alternative disposition. No additional private Drive or Gmail
  action occurred after the first-message inspection.
- Complete validation passed: `PYTHONDONTWRITEBYTECODE=1 python3
  scripts/validate.py` ran 145 tests and the schema/template and release-smoke
  checks. `git diff --check` and `PYTHONDONTWRITEBYTECODE=1 python3
  scripts/privacy_scan.py` also passed. Changed files: `school_os/importer.py`,
  `tests/test_import_runner.py`, root plan, alpha.13 plan/specification, and
  this append-only log. Unfinished: publish this safety checkpoint. The
  30-message positive import remains blocked pending explicit approval for a
  versioned lossless raw-source architecture; next: commit, push, verify the
  remote, then report that exact architectural decision rather than import a
  lossy message.

## 2026-09-08 — alpha.13 multipart-admission checkpoint publication

- Published the fail-closed source-admission safeguard as commit
  `91c268b970d23f4617e74cabfb8abc1126bca854` on `main`; `origin/main` was
  read back at that exact commit. The accepted checkpoint contains only generic
  importer behavior, tests, and continuity records; it contains no candidate
  source data or private-instance identifiers.
- Evidence for the accepted work unit: full validation ran 145 tests and the
  schema/template and release-smoke checks; diff and privacy scans passed
  before publication. The candidate remains inactive, and the requested
  positive one-message and 30-message Gmail import remains blocked by the
  unapproved raw-source/provenance architectural decision.
- The authorized GPT-5.6 Terra High read-only verifier confirmed that the
  declared generation's create-only/readback evidence and the no-effect Gmail
  stop remain inside the inactive-candidate boundary. It qualified the claim:
  the preserved, unreferenced staging object means the root cannot establish a
  clean candidate inventory or clean-instance acceptance. It must remain
  untouched; no M1 clean-instance, Gmail/catalog, daily-run, task, delivery,
  scheduler, migration, activation, or release-readiness claim follows. Next:
  validate and publish this verifier-qualified continuity checkpoint, then
  obtain explicit approval for the required core source/provenance extension
  before any positive source admission can resume.

## 2026-09-08 — alpha.13 completion-scope and source-contract reconciliation

- Reconciled the original/current source-catalog and mail-adapter contracts with
  `school_os.importer.admit_exact_plaintext_representation`. The helper's blanket
  rejection of multipart messages, attachment-bearing messages, transfer
  decoding, and non-UTF-8 source charsets is below the adapter boundary and is
  overbroad. The compatible alpha.13 path keeps transport/charset decoding in
  the adapter, admits only a provider-designated complete plaintext body with
  strict decoding evidence, inventories attachments separately, and preserves
  the existing two exact catalog comparisons. Ambiguous/incomplete plain parts,
  HTML conversion, HTML-only content, invalid bytes, or silent replacement
  remain non-admitting. Raw MIME may be verification input but is not selected
  as a canonical artifact; no core architecture change is required while this
  bounded path passes.
- Incorporated the newly authorized completion scope without recording private
  values: use a new empty private test instance; discover source-domain/config
  from the existing instance read-only; select candidate conversations with the
  grounded 14-day query and preserve their full ordered thread membership;
  perform live semantic extraction plus independent source-to-inventory-to-view
  audit; use Google Sheets as the required task adapter; and execute actual
  manual and temporary scheduled test deliveries with duplicate-policy proof.
  The existing instance, earlier candidate, and unrelated schedules remain
  unchanged.
- Reopened M1–M3 acceptance for chained revalidation after the installer repair,
  reopened M4-001 for source admission, retained M4-002 only for its declared
  synthetic alpha.12 input, and added M4-007 semantic execution, M4-008 Sheets,
  and M4-009 full connected private acceptance. M4-004 synthetic measurement and
  M4-005 package preparation no longer wait for real-provider evidence; M4-006
  remains the final all-ten-work-package release gate. Adapter reconciliation
  must permit the approved qualified direct manual sender, distinguish immutable
  installation from guarded mutable replacement, and establish scheduled
  support only on the exact observed surface.
- Closed missing acceptance requirements: actual interpreter results rather
  than canned stage outputs; real connector-to-helper execution; independent
  clause/Fact/classification/projection review; correct guideline/action/update
  filtering; current-run optional-audio regression; HTML visual inspection;
  observed time budgets translated into checkpoint-before-limit behavior; one
  successful complete connected path; and same-key suppression for both manual
  and scheduled test variants.
- Reconciled selected readable attachments with the already-approved attachment
  contract. M4-001 now owns the narrow additive provenance needed for PDF/image
  Facts: attachment identity and MIME plus an exact extracted-text span or
  provider-backed page/region. Original-content and extracted-text hashes remain
  distinct, and no original-byte proof is claimed when the selected surface
  exposes only extracted text. Every selected readable attachment must be
  source-audited or produce a specific blocker; a generic extraction framework
  and unselected extractors remain deferred.
- Two view/delivery choices remain pending and are intentionally not guessed:
  whether the 14-day scope changes ordinary brief eligibility or only import and
  inventory-audit coverage, and the exact test recipient set. Independent
  implementation, measurement, package preparation, source discovery, and
  no-send validation remain executable while those choices are unresolved.
- Changed files in this documentation-only work unit: root `PLAN.md`, alpha.13
  `PLAN.md` and `SPEC.md`, and this append-only log. No runtime code, private
  data, provider object, release, delivery, or schedule was changed. Next: run
  diff/consistency/privacy validation, publish this documentation checkpoint,
  then begin M4-001's bounded adapter-normalization implementation and regression
  matrix while M1–M3 fresh-instance revalidation is coordinated from the exact
  candidate package.

## 2026-09-08 — alpha.13 reconciliation validation and publication blocker

- Validation of the documentation reconciliation passed: the complete
  `scripts/validate.py` gate ran 145 tests plus schema/template and release-smoke
  checks; `scripts/privacy_scan.py` and `git diff --check` passed. The accepted
  local commit contains only root `PLAN.md`, this log, and the alpha.13 plan and
  specification; it contains no private identifiers, queries, recipients,
  source content, credentials, or provider records.
- Publication to `origin/main` did not occur. Automatic approval review rejected
  the default-branch push because it requires explicit user authorization for
  that shared-repository mutation, despite the delegated continuity instruction.
  The local commit is preserved and no workaround or retry was attempted.
- Next: obtain explicit authorization for the `origin/main` push, publish and
  verify the exact remote SHA, then start M4-001's bounded adapter-normalization
  implementation and regression matrix. Independent authorized private
  discovery may continue, but the two pending view/delivery choices still gate
  their dependent brief and send steps. Formal tag/release publication and
  production activation remain separately authorized.

## 2026-09-08 — alpha.13 direct HTML-resource scope correction

- The user subsequently granted explicit authorization to push accepted
  in-scope commits and, only after all gates pass, create formal alpha.13
  releases. The earlier publication rejection remains historical context; the
  reconciled documentation checkpoint was then published and verified on
  `origin/main`. Production activation, migration, existing-instance changes,
  and still-unresolved delivery/schedule effects remain outside that grant.
- A bounded GPT-5.6 Sol High read-only consultation found that direct image/PDF
  references in complete HTML alternatives cannot be silently omitted because
  they lack a mail attachment identity. The approved narrow correction preserves
  HTML-part and occurrence provenance, retrieves only exact source-linked
  direct resources under bounded verification, and accounts for each resource.
  It forbids HTML-to-text conversion, raw-MIME/HTML canonical storage, link
  following, crawling, and authenticated web navigation. An ambiguous or
  unreadable substantive resource blocks; evidence-backed decorative/tracking
  exclusions are visible. No source content, private identifiers, provider
  object, delivery, schedule, or production instance was changed by the review.
- Changed files for this planning checkpoint: root `PLAN.md`, the alpha.13 plan
  and specification, and this append-only log. M4-001 normalized-body and
  attachment implementation is underway locally; direct-resource implementation
  starts only from these recorded boundaries. Next: finish its regression matrix
  and additive provenance contracts, then validate, commit, push, and verify the
  accepted M4-001 work unit.

## 2026-09-08 — alpha.13 M4-001 normalized source admission

- Implemented the bounded M4-001 adapter-side admission contract in
  `school_os.importer`. A complete MIME tree must designate exactly one body
  `text/plain` part; identity, quoted-printable, and base64 transfer decoding
  plus declared-charset decoding are strict and produce the catalog's exact
  canonical UTF-8 bytes. HTML conversion, HTML-only content, multiple plausible
  plain bodies, malformed/incomplete parts, unavailable bytes, invalid
  transport/charset input, and decoding loss remain non-admitting.
- Kept attachments separate and added selected PDF/image extraction hooks with
  distinct original/extracted hashes and exact-text or page/region locators.
  Added direct HTML image/PDF resource inventory and bounded processing: stable
  identity, HTML-part hash/occurrence, origin, exact HTTPS source URL, bounded
  redirect/byte checks, MIME/signature agreement, and mandatory provenance.
  Resources are never crawled or treated as HTML body text; unresolved direct
  resources block message coverage. Fact/operation contracts now carry the
  additive attachment/resource provenance without changing body-Fact meaning.
- Focused import/catalog/task regression tests passed (15 tests). Complete
  `PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate.py` passed 149 tests plus
  schema/template and release-smoke checks; `git diff --check` and the privacy
  scan passed. Local commit, push, and remote verification remain pending this
  accepted work unit. No private source, connector, Drive, Sheet, delivery,
  scheduler, or production-instance action occurred. Changed files: importer,
  source and attachment contracts/operation, Fact/extraction schemas, alpha.13
  and root plans, this log, and focused tests. Next: commit, push, and verify
  the generic M4-001 checkpoint; then implement M4-007's live semantic/audit
  plumbing while holding M4-008 shared task-core work for the coordinator's
  consultation result.

## 2026-09-08 — alpha.13 M4-001 publication verification

- Published the accepted normalized source-admission/provenance checkpoint as
  `f7f3dc8600fdd9fed27d9f85c41e989d38a7be4e` on `main`; `origin/main` was read
  back at that exact commit. The remote work contains only generic source
  handling, schemas/contracts, tests, and continuity records, with no private
  source, URL, configuration, recipient, or provider object.
- M4-001's reusable implementation is complete. Its private authenticated
  binding and full source acceptance remain M4-003/M4-009 evidence, not a
  claim from synthetic tests. Next: begin M4-007 live semantic/audit plumbing;
  leave M4-008 shared task-core changes to the coordinator's consultation and
  isolated adapter handoff.

## 2026-09-08 — alpha.13 M4-007 semantic packet and audit boundary

- Added `school_os.semantic` and the semantic-packet schema. The narrow callable
  boundary accepts only bounded exact body/attachment segments; code assigns
  Fact IDs from record/message/content identity plus UTF-8 byte span and kind.
  Interpreter candidates must reproduce their selected source bytes exactly,
  cover every segment explicitly, and cannot supply provenance IDs. Independent
  audit binds to the packet hash and must account for every segment before a
  result is accepted.
- Focused semantic/import/task tests passed (13 tests). Complete
  `PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate.py` passed 151 tests plus
  schema/template and release-smoke checks; `git diff --check` and the privacy
  scan passed. This is reusable mechanical implementation only: no real model,
  source, provider, Drive, Sheet, mail, scheduler, or delivery action occurred;
  actual authenticated invocation remains M4-003/M4-009 evidence. Changed
  files: semantic helper/schema/tests plus root/alpha.13 continuity documents.
  Next: commit, push, and verify M4-007; then implement M4-004's bounded
  synthetic measurement/checkpoint evidence while M4-008 awaits its reviewed
  isolated handoff and task-core consultation.

## 2026-09-08 — alpha.13 M4-007 publication verification

- Published the accepted semantic packet/audit boundary as
  `581d09871f579ce85d0975c0062b710c2e70c1db` on `main`; `origin/main` was
  read back at that exact commit. The checkpoint contains only generic code,
  schemas, tests, and continuity records; no private source or provider data.
- M4-007's reusable mechanical boundary is complete. Its authenticated live
  invocation and independent private audit remain M4-003/M4-009 evidence. Next:
  begin M4-004's bounded synthetic measurement/checkpoint work; do not alter
  M4-008 shared task core while its consultation and isolated adapter handoff
  remain in progress.

## 2026-09-08 — alpha.13 task-core reconciliation correction

- A bounded GPT-5.6 Sol High read-only consultation reproduced a task-core
  defect: canonical reconciliation is setdefault-only and provider reconciliation
  ignores unbound rows, so parent-origin tasks, parent edits/completion history,
  source corrections, and completion-comment policy cannot be preserved safely.
  M2-003, M2-004, and M3-003 are reopened before accepting the Sheets adapter.
- The accepted in-scope repair is complete scoped snapshot reconciliation with
  explicit ownership/snapshots, stable identity/bindings, append-only lifecycle
  events, explicit source relationships, and one recoverable missing-comment
  reminder. Completion is not a workflow-state expansion. The isolated Sheets
  worker remains mapping/port-only pending review; no shared task code, Sheet,
  source, delivery, scheduler, or private instance changed in this consultation.
  Next: record matching specification detail, implement the shared core and
  regression matrix, then validate and publish the reopened-task checkpoint.

## 2026-09-08 — alpha.13 canonical task and Google Sheets reconciliation implementation

- Implemented the reopened M2-003/M2-004/M3-003 repository correction and
  integrated the reviewed isolated Google Sheets mapping. Canonical task state
  now has explicit source relations, source-due evidence, append-only source
  and parent lifecycle events, uniqueness checks for task/provider bindings,
  and durable per-provider parent snapshots. Completion remains separate from
  the three workflow states; a completed provider observation without a
  nonempty parent comment is reopened with one recoverable immutable reminder.
- The Sheets adapter takes one complete scoped snapshot per explicit sync,
  re-resolves and guards mutable row locators before writes, verifies exact
  readback, preserves unrelated cells, distinguishes source due from parent
  planned due, and exposes/claims unbound parent rows only after core has
  journaled the assigned canonical ID. Replays resolve by ID, never title.
- Synthetic coverage now exercises same-title parent rows, intent-then-claim
  recovery, source correction identity preservation, completion/reopen replay,
  source/provider due separation, one-snapshot multi-task synchronization, and
  guarded row reorder/retarget failures. `python3 -m unittest discover -s
  tests` passed 169 tests; `git diff --check` passed. No live provider, Drive,
  Sheet, mail, scheduler, or private instance was read or changed.
- Next: run privacy/repository validation, commit this shared core/Sheets
  checkpoint, push it to `origin/main`, and verify the remote SHA. Authenticated
  runtime bridge and observed private test-Sheet acceptance remain M4-003/M4-009.

## 2026-09-08 — alpha.13 source custody and semantic audit correction

- Reopened M4-001/M4-007 after independent review and resolved the pending test
  policy generically: both authorized test deliveries use the existing daily
  brief recipe and a private approved recipient outside Git.
- Tightened MIME admission so completeness is explicit and 7bit high-bit bytes
  block; added a combined body/MIME-attachment/resource coverage gate and
  explicit review for unrecognized HTML resource-bearing constructs.
- Semantic interpretation now freezes/deep-copies the packet before the
  callback, hashes the exact interpreted artifact for audit binding, retains
  actual attachment outcomes, and rejects a covered segment without a Fact.
- Next: finish typed source-conversation custody evidence and complete-unit
  attachment/resource validation, run full validation/privacy, and publish the
  corrected checkpoint. No provider or private-instance action occurred.

## 2026-09-08 — alpha.13 source custody completion

- Required selected-body raw-part hash, byte length, full locator, explicit MIME
  completion, and provider-Unicode equality before admission. Strict decoding
  allows a literal replacement character only when it is present in the strict
  decoded bytes; mismatched/provider-inserted substitution blocks.
- Added source-message/content coordinates to attachment outcomes, requires
  observed original bytes and complete PDF units or nonempty image text, carries
  content IDs into semantic Facts, recomputes extracted-text hashes from frozen
  source text, and derives semantic attachment outcomes from frozen provenance
  rather than interpreter assertions.
- Full validation passed 170 tests plus privacy and diff checks. Next: publish
  this final repository custody checkpoint; selected runtime must still provide
  actual complete provider reads/fetches/page extraction before private M4-009
  acceptance. No provider or private instance was touched.

## 2026-09-08 — alpha.13 source-custody and exact semantic-audit integration

- Completed the bounded corrective integration for M4-001/M4-007. One admitted
  body now carries selected raw-part hash/length/whole-part locator, strict
  transfer/charset decode, and exact provider-Unicode equality into a typed v2
  catalog record. Attachments and direct HTML image/PDF resources retain stable
  code-assigned content/outcome identity, source-message association, separate
  original/extracted hashes, exact extracted text frames, complete ordered
  page/image/text units, locators, and typed read/fetch/redirect evidence. Raw
  and strictly decoded HTML-part hashes remain distinct. Missing, duplicate,
  inconsistent, unresolved, or unreferenced custody blocks.
- `school_os.semantic` now builds bounded ordered packets only from a parsed,
  source-equal catalog readback, passes an isolated deep copy to the injected
  interpreter, partitions every UTF-8 source byte into Fact/no-Fact/review
  coverage, and assigns immutable Fact IDs, exact quotes, chronology, and
  attachment/resource provenance in code. Canonical Fact text may be concise
  source-supported wording distinct from its exact quote. Independent audit
  binds the packet hash, exact normalized interpretation, every span and its
  interpreter reason, every canonical wording/classification, and every source
  outcome. A faithfully preserved source ambiguity may pass as review without
  a guessed downstream claim; an audit error remains blocking.
- Added focused end-to-end and tamper regressions covering raw/decoded HTML
  hashes, eight-page attachment completeness, image-resource fetch evidence,
  catalog framing/dereference, bounded packet construction, exact result audit,
  bad EOF/unit/read evidence, lossy decode, and literal-versus-inserted Unicode
  replacement characters. `python3 scripts/validate.py` passed 173 tests and
  `git diff --check` passed. This is synthetic mechanical evidence only; no
  private source, provider, Drive, Sheet, mail, scheduler, or delivery action
  occurred.
- Reconciled the release documents: the generic M4-001/M4-007 correction is
  complete pending authenticated interpreter/source acceptance in M4-003/
  M4-009. M2-003/M2-004/M3-003/M4-008 remain reopened because the separate
  task-core candidate still has focused failure cases under review. Next:
  privacy-scan the staged new test, commit/push/verify this source checkpoint,
  then integrate and refresh the separately accepted bounded M4-004 measurement
  delta without touching task/Sheets/brief/runtime work.
