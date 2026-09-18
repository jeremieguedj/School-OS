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

## 2026-09-08 — alpha.13 M4-004 measured continuation integration

- Published and remotely verified the preceding source/semantic checkpoint at
  `64dbc3b1a5af60ed9da2d40c94c3a139640708f3`. Root independently reran its
  focused 13-test source/import/semantic matrix successfully and accepted the
  stable interfaces for later authenticated runtime binding.
- Integrated the complete accepted M4-004 measurement delta, then regenerated
  it from the current source path with `PYTHONPATH=. python3
  scripts/measure_synthetic.py`. The command now exercises strict plaintext
  admission and typed catalog construction as well as onboarding, complete
  paginated enumeration, bounded import selection, full daily/no-new runs, and
  a measured interruption followed by a new attempt. The baseline records
  actual elapsed nanoseconds, canonical input/output byte counts, helper and
  provider-fake calls, checkpoint time, completed units, and zero repeated
  phases; unavailable model-token and host-deadline values remain explicit.
- `school_os.daily` now starts elapsed accounting before admission and uses a
  measured estimate plus reserve before each next complete phase. It creates and
  verifies a concrete continuation checkpoint before returning
  `NEEDS_CONTINUATION`; a resumed attempt retains predecessor history and does
  not replay completed phases. The boundary cannot interrupt an active phase or
  provider call, which remains an explicit practical limit.
- `python3 scripts/validate.py` passes 179 tests after regeneration. M4-004's
  generic implementation is complete, but the same command must run once more
  after the separately open task-core repair before its task-sync timing becomes
  final release evidence. This run used only synthetic fixtures/fakes and made
  no private or provider effects. Next: staged privacy/diff checks, commit/push/
  remote verification, then hand off main to the queued task/brief/runtime work.

## 2026-09-08 — alpha.13 integration handoff and brief-policy gate

- The source/measurement writer relinquished main at the clean, remotely
  verified commit `b643e1fbf779be72144790de28dd956aa1da753d` after 179 passing
  tests, privacy and diff checks. M4-004 must still be regenerated after the
  task repair; authenticated M4-003/M4-009 acceptance remains outstanding.
- Independent review rejected the isolated task candidate despite its passing
  tests: incremental source batches could discard history or regress task
  resolution, a source correction could overwrite an accepted parent edit,
  and an unknown create outcome could produce a duplicate. A separate isolated
  implementation session is repairing exactly those three cases. No rejected
  task candidate has been integrated into main.
- The selected runtime transport was probed with an echo-disabled terminal and
  hashed private request/response files, including exact large-payload transfer.
  Plain-pipe input returned EOF and is not the selected mechanism. A separate
  isolated session now owns the bounded authenticated bridge, bootstrap package
  references, within-phase continuation, capability enforcement, and durable
  keyed delivery implementation. These probes are not observed daily-run or
  unattended-provider acceptance.
- Brief input/rendering work remains isolated and uncommitted. Automatic
  approval review rejected both attempted missing-date policy API shapes,
  treating them as unapproved policy/contract changes. The selected recipe
  requires received dates, while a parent-origin task may have no school email.
  The proposed explicit parent-added presentation exception awaits direct user
  steering. Brief integration and all test sends remain paused; independent
  task/runtime repairs may continue. No new missing-date behavior is approved
  by this checkpoint.
- Next: resolve that one brief policy gate, review and integrate completed
  isolated candidates, regenerate current measurements, then perform the
  authorized fresh-package/instance/manual/scheduled/Sheet acceptance. Source
  evidence and exact private references remain outside Git. No test email or
  temporary schedule has been created, and no release-completion claim is made.

## 2026-09-08 — alpha.13 M4-005 release-preparation and audio-delta regression

- Added a read-only `scripts/verify_release.py` verifier and a manually
  dispatchable readback job on the existing validation workflow. The verifier
  builds from one exact local commit, validates the archive/checksum, requires
  a matching GitHub release/tag/commit/manifest status, requires exactly the
  archive and checksum assets, resolves an annotated tag to the same commit,
  and compares downloaded bytes with the local candidate. It fails on source
  mismatch, missing/duplicate/unexpected assets, truncated bytes, lightweight
  tags, or mutable published releases. It creates no tag/release and performs
  no upload, publish, replacement, deletion, push, or provider action.
- Documented the alpha.12-only structured-state migration boundary and explicit
  alpha.11 fail-closed behavior. Added the alpha.13 `UNRELEASED` changelog
  entry; `release.yaml` remains `0.1.0-alpha.13`, schema 2, migration 0002,
  and `status: unreleased`.
- The optional local audio worker now accepts only upstream-provided
  current-run `new`/`changed` records. Synthetic worker coverage includes new
  News and changed Guidelines/Actions, while regenerated seven-day rolling
  display records and unchanged open actions fail closed. The connected runtime
  still owns delta construction and must record optional audio degradation while
  completing HTML/text when disabled or unavailable; no second delta generator,
  API call, or delivery was added.
- Validation before the final local commit: `python3 scripts/validate.py`
  passed 187 tests; focused release/audio/upgrade tests, diff check, and the
  staged tracked-file privacy scan passed. Next: commit this isolated unit,
  rebuild and validate the exact resulting candidate with `--candidate-test`,
  then hand the SHA and the remaining real draft/published, runtime-delta,
  visual, private upgrade, and M4-003/M4-009 evidence gates to root. No release
  readiness or M4-005 completion claim follows from this preparation alone.

## 2026-09-08 — alpha.13 M4-005 installed-package bytecode portability repair

- GitHub Actions Python 3.12 reproduced a real package-integrity failure in
  the connected daily and fresh-process installed-package tests: a packaged CLI
  imported `school_os`, Python created `__pycache__` below the extracted release
  root, and the required subsequent inventory verification correctly rejected
  that undeclared file. Local macOS Python used an external cache prefix, so it
  did not expose the defect.
- The narrow repair sets `sys.dont_write_bytecode = True` in non-runtime
  packaged thin entrypoints before their first package import, preserving the
  fail-closed inventory verifier. It does not ignore cache files or weaken
  payload equality. A new extracted-package test clears bytecode-related
  environment settings, runs the packaged scaffold and installed validators,
  and compares package verification before and after. Next: commit the repair,
  then run it and the full suite from the exact committed archive under ordinary
  bytecode defaults.

- Committed the repair as `75796667d7765383b7c8341fd10333c78de203c5` and
  verified it under bundled CPython 3.12.14 with `sys.pycache_prefix is None`
  and `sys.dont_write_bytecode is False`. The focused extracted/connected/fresh
  installed package matrix passed (9 tests), including ordinary child-process
  bytecode defaults; the full `scripts/validate.py` suite passed 188 tests.
  An exact-ref archive built from that commit passed `validate_installed.py
  --candidate-test`; privacy and diff checks are clean. No GitHub, provider,
  private-instance, tag, release, or push action occurred. Next: root may
  integrate these local commits and re-run CI; only a CI observation can close
  the prior hosted failure.

## 2026-09-08 — alpha.13 M4-005 release-readback portability correction

- Removed the release-verification test's fixed alpha.13/unreleased expectation.
  It now follows the exact committed `release.yaml` version/status, rejects the
  opposite status, and uses a separate released synthetic candidate to prove the
  release-status mismatch path. This preserves coverage when the separately
  authorized final release commit changes its manifest to `released`.
- Corrected the gated `gh release create` recipe to pass `--target` with the
  full candidate SHA, matching the verifier's strict `targetCommitish` binding.
  Local `gh release create --help` confirms `--target branch` accepts a full
  commit SHA and is compatible with `--verify-tag`. No command that creates a
  tag or release was invoked.
- Bundled CPython 3.12.14 with ordinary bytecode defaults passed 11 focused
  release-verification/installed-package tests and `git diff --check`. Next:
  commit this narrow correction and rerun the full bundled validation suite
  from its exact resulting commit; publication readback remains pending an
  actual separately authorized draft or published release.

## 2026-09-08 — alpha.13 M4-005 final-manifest test decoupling

- Corrected two remaining ambient-manifest assumptions. Release verification
  now parses `HEAD:release.yaml` with the repository's strict YAML loader
  rather than working-tree bytes, so its candidate identity test follows the
  exact commit being packaged. The installed-validation production rejection
  now builds an isolated unreleased Git fixture with a rebuilt inventory; the
  actual HEAD archive is validated according to its own manifest state and
  still receives the inventory-corruption negative check.
- Bundled CPython 3.12.14 under ordinary bytecode defaults passed the focused
  release-verification and installed-package set (11 tests) after both fixes.
  Next: commit, run the full bundled validation and exact committed archive
  candidate check, then hand the final SHA to root. No manifest status, tag,
  release, push, or external-provider state was changed.

- Committed the test decoupling as `b04ca84a65a5be4920b1a1961033247ea785b96c`.
  Bundled CPython 3.12.14 then passed the full `scripts/validate.py` suite
  (189 tests) under ordinary bytecode defaults. An archive built from that
  exact SHA passed `validate_installed.py --candidate-test`; diff and tracked
  privacy checks are clean. Next: commit this final evidence record and hand
  root the resulting isolated SHA. Real GitHub draft/published readback and
  all separate private/provider acceptance gates remain intentionally unrun.

## 2026-09-08 — alpha.13 release preparation independently accepted

- Integrated the isolated release candidate through
  `d8194d955aa47f31a23d94e5787fe706d29519b2`. Root independently passed 23
  focused package/connected-install/release/audio tests on CPython 3.12.14,
  then 11 release/installed-validation tests after correcting final-manifest
  assumptions. The worker's final full suite passed 189 tests and its exact
  final archive passed installed candidate validation.
- This fixes the three extracted-package failures reproduced from the prior
  main CI run: ordinary Python wrote bytecode before immutable inventory
  verification. The entrypoints now prevent that mutation before imports;
  inventory checks remain strict. Tests no longer rely on the committed
  manifest remaining unreleased, and the release creation recipe passes the
  exact target commit required by readback verification.
- Plan revision 34 preserves pending brief-policy, task, runtime and private
  acceptance gates. Runtime work currently supplies isolated adapter/bootstrap
  primitives; the concrete daily worker bindings are still required and no
  bootstrap-only result is accepted as a connected daily run.
- Next: validate and publish this integration, verify actual CI, then review
  the task candidate with independent hard-process-death recovery. No email,
  schedule, production-instance change, or formal release was performed.

## 2026-09-08 — alpha.13 task reconciliation independent-review repair

- Repaired the reopened canonical/provider reconciliation after independent
  failure reproduction. Source and parent Action/Group changes now use a true
  field-level base/canonical/provider comparison; local-only corrections
  project, parent-only edits enter canonical state, equal changes converge, and
  divergent changes remain explicit review cases without overwrite. Workflow,
  origin, source context/link/due, and canonical identity receive full managed
  drift checks. Actual canonical changes advance revision/evidence, and binding
  validation enforces one object per task/provider globally.
- Source task relationships now use stable source/message/content chronology
  with Fact ID only as the final tie, reject conflicting changes at one source
  coordinate, preserve a monotonic support date, and persist current completion
  resolution. Completed source actions do not create provider tasks or enter the
  connected brief; an explicit reopen restores eligibility.
- Parent-row admission now issues an immutable canonical ID independent of its
  mutable Sheet locator. The durable claim intent carries complete candidate and
  canonical-task evidence, so either half of an interrupted checkpoint can be
  reconstructed before a guarded claim. Unknown managed IDs, missing durable
  bindings, and inconsistent canonical/provider state block rather than create
  a duplicate.
- Missing-completion-comment handling now returns a durable occurrence-stable
  reminder intent before effects. Recovery verifies the exact effect ID/text,
  writes or adopts one reminder, then reopens and exactly reads the provider
  object even when it is already open. Tests cover lost comment responses,
  failures before and after reopen, lost returned state, later repeated
  completion, qualifying completion, and parent reopen history.
- Tightened the Google Sheets adapter so every overwritten cell is guarded by
  its cached prior value in addition to canonical identity. Native comment
  operations re-resolve canonical identity around lookup/write/readback and
  require explicit canonical task, provider object, effect, and exact-text
  evidence; unanchored native comments are not claimed as stable row anchors.
  Updated the generic task/Sheet contracts accordingly.
- The connected installed-run test now persists and verifies both returned
  canonical tasks and provider state in recovery order, then supplies the
  refreshed canonical task artifact to brief generation. Synthetic evidence
  remains repository behavior only and does not establish authenticated or
  unattended provider conformance.
- Validation passed the complete repository gate with 182 tests plus JSON
  schema/template/release-smoke checks; the direct privacy scan and
  `git diff --check` passed. No private value, provider effect, release, or push
  occurred. Next: integrate this isolated candidate with the coordinated source
  chronology schema changes, rerun the complete gate, and independently review
  the combined diff before publication.

## 2026-09-08 — alpha.13 task independent-review blocker repair in progress

- Reproduced all three follow-up review failures against `95eb0bd`: a
  relation-only incremental Fact could not target an existing source task, a
  source Action correction silently replaced an accepted parent Action edit,
  and a lost accepted create followed by one empty snapshot could create a
  duplicate provider row.
- Canonical task reconciliation now retains compact opening and ordered source
  relation evidence, merges new relationship Facts without requiring historical
  Facts to be resent, preserves source Fact/lifecycle evidence and monotonic
  support dates, and resolves late-arriving evidence by source chronology.
  `source_projection` is now the explicit common base: source-only changes
  apply, parent-only values remain, equal changes converge, and divergent
  source/parent values block before mutation or provider projection.
- Provider state now admits a narrow `task_create` effect intent with canonical
  ID, exact managed projection, projection hash, effect outcome, and verification.
  The first reconciliation journals only the intent; continuation performs the
  create. Unknown responses retain the intent, adopt exactly one exact later
  match, and block on an empty snapshot unless the adapter supplies explicit
  `definitely_not_applied` evidence. Focused regressions cover the one-empty-
  snapshot duplicate case and evidence-authorized retry.
- Focused task/provider tests pass, and the complete unit suite currently passes
  188 tests after updating the connected and Sheets synthetic flows to persist
  create intent before mutation. Contracts and the alpha.13 specification now
  describe the incremental merge, source/parent three-way rule, and create
  effect recovery semantics. No live provider, private data, delivery, schedule,
  release, or push was touched.
- Next: rerun the connected hash fixture and all 188 tests after documentation
  updates, exercise exact standalone reproductions for all three blockers,
  inspect the scoped diff, run `scripts/validate.py`, privacy and diff checks,
  then append final evidence and create one scoped local commit.

## 2026-09-08 — alpha.13 task independent-review blockers repaired

- Completed the bounded follow-up repair without changing Fact/source schemas,
  the existing parent-claim and missing-comment recovery design, private data,
  any provider, delivery, schedule, release, or remote branch. The permanent
  regression matrix now covers relation-only correction/completion, omission of
  historical Facts, late older lifecycle evidence, accepted-parent/source
  divergence before projection, durable create-intent journaling, one invisible
  snapshot after a lost accepted create, exact-match adoption, conflicting and
  multiple matches, missing intent, and explicit negative-evidence retry.
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate.py` passed the complete
  repository gate with 190 tests plus JSON schema, template-manifest, and
  release-smoke checks. The direct privacy scan and `git diff --check` passed.
  The connected synthetic run persists and reads back provider create state
  before its create call; fresh-process recovery starts from a durable unknown
  create intent and adopts exactly one verified provider row.
- Changed scope is limited to `school_os/tasks.py`, provider-state schema,
  task/Sheets contracts and alpha.13 specification, connected/recovery/task/
  provider/Sheets tests and one synthetic expected-hash fixture, plus this
  append-only log. The coordinated brief decision remains untouched.
- Next: create one scoped local commit in this isolated worktree and return its
  exact SHA to the coordinator. The coordinator should integrate it with the
  separate source-chronology work, rerun the complete combined gate and an
  independent diff review, then handle any authorized publication.

## 2026-09-08 — alpha.13 abrupt-stop task-effect recovery repair

- Follow-up process-death reproduction rejected `f696443`: although ordinary
  create exceptions returned an unknown intent, `SystemExit` after an accepted
  create could leave only the older durable `pending` state, and the same gap
  existed between an accepted missing-comment reminder and returned state.
- Added one bounded `checkpoint_effect_intent` callback used by both effects.
  Immediately before every initial or evidence-authorized retry dispatch, core
  changes the exact intent to `unknown`, increments `dispatch_attempt`, adds
  effect-specific identity/hash evidence, and requires the callback's exact
  durable readback. A stop before dispatch is therefore conservative; a stop
  after provider acceptance cannot restore retryable `pending` state.
- Unknown create recovery still adopts exactly one exact canonical-ID/projection
  match and blocks zero, multiple, or conflicting matches. Unknown reminder
  recovery now adopts one exact occurrence-ID/text match and blocks a zero-match
  lookup. Either zero may retry only after the adapter supplies explicit
  `definitely_not_applied` evidence, followed by another durable pre-dispatch
  checkpoint. Existing parent-claim, occurrence IDs, reopen/readback, binding,
  and Sheet guard behavior was retained.
- Permanent Python 3.12 regressions write provider state to a durable temporary
  file, raise `SystemExit` after provider acceptance, restore the pre-dispatch
  `unknown` intent, expose one temporarily empty complete lookup, verify no
  duplicate create/comment, and then adopt the original exact effect. The
  focused task/provider/Sheets/connected/fresh-process matrix passed 53 tests.
- On bundled CPython 3.12.14, the complete validation with
  `PYTHONDONTWRITEBYTECODE=1` passed 192 tests plus schemas, template manifests,
  and release smoke checks. The unsuppressed reference-runtime run passed all
  task/effect tests but retained the separately owned three packaging failures
  caused by generated `__pycache__` entries making the release inventory
  incomplete; no installer/release CLI files were changed or workaround added.
- Next: run the privacy and diff gates, inspect the superseding scoped diff,
  commit the abrupt-stop repair locally, and return the new exact SHA. The
  coordinator should integrate it with source chronology and the separate
  packaging fix before the final unsuppressed combined release gate.

## 2026-09-08 — alpha.13 task capability alignment and final isolated validation

- Reconciled the daily task capability list with the implemented complete-
  snapshot core and selected Sheets adapter. The unconditional baseline is now
  identity/configuration read, complete current snapshot, complete comments,
  create, guarded update, comment write, and exact verification. Current status
  and parent fields come from that snapshot; comparison with the durable prior
  snapshot records only the observed current transition and does not claim
  unavailable intermediate activity.
- Guarded `tasks.update` explicitly covers Action/Group and core-authorized
  status/reopen changes for Sheets. Distinct completed-list, activity, move,
  complete, and reopen capabilities remain catalogued as adapter-specific
  requirements for providers such as Todoist rather than fictitious Sheets or
  unconditional daily-run endpoints. A focused contract regression enforces
  this boundary.
- Bundled CPython 3.12.14 validation with
  `PYTHONDONTWRITEBYTECODE=1` passed the complete 193-test repository gate plus
  schemas, template manifests, and release-smoke checks. The earlier unsuppressed
  reference-runtime run passed every then-present task and effect test; its three
  failures remain the separately owned generated-`__pycache__`
  release-inventory issue, for which candidate `7165056` is under coordinator
  review. This work did not change installer/release code or suppress that known
  integration dependency in source.
- Next: run direct privacy and diff checks, inspect all changes since `f696443`,
  create the superseding local commit, and return its exact SHA and the bounded
  runtime callback/capability interface to the coordinator.

## 2026-09-08 — alpha.13 task correction independently accepted

- Integrated task candidate `c2e94ea7a3bbfc4bba0d0f7404c29014f8fd7384`,
  preserving main's current source/semantic contract and both progress
  histories. Root passed 48 focused task/Sheets tests and independent hard-exit
  recovery: four fresh processes per task create/reminder, exit immediately
  after provider acceptance, one transient empty lookup that blocks, then one
  exact adoption. Each case issued its effect exactly once and cleared its
  reconciled intent. These are synthetic process-reset checks, not private
  provider acceptance.
- The combined tree passed 212 tests on ordinary CPython 3.12.14. Separately
  executing the measurement command exposed its stale immediate-create
  assumption. Adapted it to persist/read back canonical and provider intent
  state, invoke the new pre-dispatch checkpoint, and measure the real second
  reconciliation call. The regenerated scenario creates one task, creates no
  task on the unchanged run, and resumes without repeated completed phases.
  Its regression now executes the command instead of trusting a saved fixture.
- GitHub CI for the preceding release-preparation commit
  `22ae5f1cf920f65b3f36ec76e2cc50a56fe9c9bb` completed successfully, confirming
  the package-bytecode correction on the actual CI surface.
- Plan revision 35 records accepted repository task correction while keeping
  chained package, concrete runtime workers, pending brief policy, and private
  source/Sheet/manual/scheduled acceptance open. Next: publish this validated
  task integration, review the isolated runtime primitives, then implement the
  concrete connected workers. No provider effect, test send, or schedule was
  performed by this repository work.

## 2026-09-08 — alpha.13 runtime primitive review and next bounded workers

- Task/measurement merge `ed63d8227d083670afde5c1e3b1948091a8dad73` passed
  the exact-commit 212-test CPython 3.12.14 gate and actual GitHub CI. Independent
  hard-exit create/reminder recovery also passed from its verified extracted
  archive with Git absent; the package inventory remained unchanged.
- Independent Sol High review rejected isolated runtime primitive candidate
  `a69ce99f79a9feb88f4affffcf57788c41af85cb`. Root reproduced all five issues:
  Sent readback could confirm a different provider ID; a partial phase could
  continue without a durable checkpoint; extraction could accept archive bytes
  different from the admitted hash; bootstrap readback could be claimed without
  content; and semantic bridge responses could admit nonfinite JSON. A separate
  isolated repair is limited to those checks and regressions. This candidate is
  not integrated or accepted as runtime support.
- A parallel bounded implementation now owns concrete admitted-instance
  artifact storage and ingestion workers through audited Fact/catalog/index
  artifacts, using the existing source contracts. It must invoke real helpers
  on predecessor bytes, persist per-unit continuation, and stop on unresolved
  substantive source coverage. It owns no task, brief, delivery, or scheduling
  effects and must consult before extending shared host request kinds.
- Dated-only visual review is provisional. Its initial fixtures accidentally
  used the generic template; those comparisons do not establish defects in the
  selected private template. The reviewer is repeating the checks with the
  exact supplied template and supported placeholder mapping. The undated-parent
  policy question still blocks brief integration and sends.
- Next: independently recheck the five runtime fixes, integrate accepted
  primitives while preserving current task/measurement changes, review concrete
  ingestion workers and correctly configured visual evidence, then continue
  the already approved fresh-instance acceptance. All private values and repro
  artifacts remain outside Git; no test send or schedule has been created.

## 2026-09-08 — user-added task recipe exception approved

- The user explicitly approved tasks added directly in the selected task tool,
  whether Sheets or another conformant provider. Release plan revision 36 and
  SPEC now permit eligible undated user-origin tasks under Parent-added tasks
  within their ordinary child/household action section. Preserve canonical
  wording and scope; invent neither received dates nor source links.
- This resolves the former policy pause. Required source-origin dates and
  unresolved-finite eligibility remain strict; missing source evidence must not
  be treated as proof of user origin. No provider-specific policy or configurable
  exception framework is needed.
- Existing brief work remains a candidate pending review and deterministic/visual
  checks, including the selected template's link separators and bold guideline
  scope. No email, schedule, private installation, or release is claimed here.
- Next: complete and review the isolated brief candidate, integrate the repaired
  runtime primitives and concrete ingestion workers, then execute the gated
  fresh-instance acceptance path. Private recipient/configuration values remain
  outside Git.

## 2026-09-08 — alpha.13 M4-003 approved runtime-adapter design checkpoint

- Recorded the approved finite Codex-local host bridge before implementation.
  The synchronous standard-library core uses private mode-0600 request/response
  files under a mode-0700 run directory, short hash-bound PTY controls, static
  request-kind dispatch, bounded payloads, one-use response verification, and
  explicit unknown-effect reconciliation. It does not expose arbitrary tool
  execution or treat synthetic responses as observed authorization.
- Recorded the connected composition boundary: exact predecessor artifacts,
  explicit selected capabilities, durable exact delivery intent and Sent
  readback, same-phase unit continuation, and admitted archive/checksum
  bootstrap references. The selected Drive replacement limitation and the
  distinction between interactive and scheduled evidence remain explicit.
- Status remains pending. No authenticated connector, provider write, private
  value, schedule, release, or production instance was touched. Next: implement
  the independent bridge/response writer and focused synthetic transport tests,
  then add connected delivery/daily/bootstrap pieces without editing the
  separately owned task, source, or renderer files.

## 2026-09-08 — alpha.13 M4-003 runtime bridge and recovery implementation

- Implemented the finite Codex-local bridge in `school_os/codex_bridge.py` and
  the noncanonical PTY response writer. Requests and responses are private,
  bounded, hash-bound, one-use files; only fixed Drive/Gmail/Sheets/comment and
  semantic kinds can dispatch. Flat/nested structured content is normalized;
  mismatched IDs, hashes, paths, modes, wrappers, truncation, replay, arbitrary
  kinds, and tool errors fail closed. Synthetic transport covers a 1,048,634-
  byte response without placing private payload bytes in terminal controls.
- Added `school_os/connected_daily.py`, which verifies every phase's actual
  persisted artifact and passes it to the next phase. Canned `verified: true`
  results cannot authorize a phase. `school_os.daily` now requires the selected
  capability set explicitly and can checkpoint/repeat bounded units inside one
  phase using `phase_complete`, `completed_units`, and `remaining_work`.
  Partial phases never enter `completed_phases`; budget checks remain between
  units and cannot preempt an in-flight provider/model call.
- Added `school_os/delivery.py`. Operational send state is durable and read back
  before dispatch, includes key/variant/To/CC/BCC/subject/body hashes, and is
  treated as possibly applied across abrupt process death. Confirmation checks
  the returned Gmail ID through raw MIME, SENT label, exact recipients, subject
  marker, and both bodies. Recovery paginates Sent candidates and accepts one
  exact match only; zero, multiple, or non-progress blocks without resend.
- Corrected the fresh-bootstrap gap: create-only installation now admits and
  reads back the exact release archive and `SHA256SUMS` as payload objects,
  records their exact references and hashes, and verifies the pinned pair before
  safe extraction. A Python 3.12 test removes the original extracted checkout
  and successfully rebuilds from recovered package bytes.
- Added precise Codex-local runtime/scheduler docs and reconciled the older
  ChatGPT Work direct-manual prohibition. Current project discovery does not
  establish an eligible local cron surface; the documented scheduled test is a
  separately authorized thread heartbeat and interactive evidence remains
  insufficient for it.
- Focused Python 3.12 validation passed 51 tests with ambient bytecode controls
  removed. The complete 192-test run currently has three known extracted-
  package inventory failures from pre-verification `__pycache__` creation in
  other thin entrypoints; the separately assigned release worker owns that
  portability repair. This session set `sys.dont_write_bytecode` before
  School-OS imports in its owned `run_operation.py` entrypoint.
- Genuine pending dependency: the generic daily capability list names task
  history/move operations that the selected native Sheets surface does not
  expose. The coordinator was given the narrow snapshot/batchUpdate/comment
  mapping proposal; no nonexistent capability is claimed here. Brief input
  policy/API and task abrupt-stop repair are also still owned by their separate
  sessions. No provider mutation, private value, send, schedule, release, or
  production effect occurred. M4-003/M4-009 acceptance remains pending.
- Next: finish CLI/parser and bridge pagination tests, rerun complete validation
  after the assigned portability/task/brief deltas are integrated by the
  coordinator, then commit this isolated candidate and report its exact SHA.

## 2026-09-08 — alpha.13 M4-003 runtime scope correction

- Removed the generic `school_os.connected_daily` callback composition and its
  self-selected artifact-hash test because neither constituted a concrete
  connected execution path. Renamed the host-mode result to
  `BOOTSTRAP_READBACK_VERIFIED`; it proves only exact bootstrap metadata/content
  identity through the finite bridge and does not claim runtime readiness.
- The missing concrete installed entrypoint must still bind recovered admitted
  package/state custody, Drive artifact and checkpoint persistence,
  Gmail-to-catalog import, semantic interpretation plus independent audit,
  accepted native-Sheets task synchronization, finalized brief input/rendering,
  exact delivery, and cursor commit last. Those interfaces remain dependent on
  separately owned task and brief acceptance work.
- Strengthened connector normalization for observed CallToolResult shapes with
  tool metadata alongside `structuredContent.result`. Metadata and model-facing
  text blocks are never treated as semantic verification; absent structured
  content blocks.
- Delivery now closes the durable effect checkpoint after exact Sent readback
  and heals a crash between confirmed-ledger and confirmed-effect persistence.
  A pending ledger with no effect checkpoint is provably pre-dispatch and may
  proceed once; a pending effect always reconciles and never blindly resends.
- Final owned focused validation passed 51 tests on CPython 3.12.14. The prior
  complete run exercised 190 tests and had only the three separately owned
  package-inventory/bytecode failures; the coordinator has since accepted that
  release repair on main. `git diff --check` passed. No connector call,
  provider mutation, private value, send, schedule, release, or production
  effect occurred in this candidate.

## 2026-09-08 — alpha.13 M4-003 primitive review repair

- Reproduced and repaired all five confirmed synthetic review gaps against
  candidate `a69ce99f79a9feb88f4affffcf57788c41af85cb`: mismatched Gmail
  provider IDs can no longer confirm or heal delivery state; a partial daily
  unit cannot advance without a nonempty durable checkpoint identity; package
  extraction rebinds both archive and checksum bytes to admitted hashes;
  bootstrap readback requires narrow storage-only profile qualification plus
  complete strict base64 bytes and two independent size agreements; and
  nonfinite semantic/host results fail the bridge's JSON gate.
- Added direct regressions for post-send/suppression/reconciliation ID mismatch,
  absent/empty partial-unit checkpoints, a self-consistent substituted archive,
  empty-bootstrap success claims and unused invalid profiles, a valid narrow
  storage-only bootstrap profile, and a `NaN` semantic response. The primitive-
  only architecture and explicit missing connected-worker boundary are
  unchanged.
- Bundled CPython 3.12.14 passed the five exact review regressions and the
  broader 55-test owned runtime/recovery matrix. `git diff --check` passed.
  The three historical package/bytecode failures belong to the already accepted
  release repair on main and were neither hidden nor reimplemented here. No
  provider call, private value, send, schedule, push, release, or production
  effect occurred.

## 2026-09-08 — runtime primitives integrated for exact-package validation

- Integrated the complete reviewed primitive delta through `43b054c`, retaining
  the accepted task effect callback, executable measurement regression, and
  approved user-added task policy. Independently reran the five original
  invalid-input cases: wrong Sent identity, absent bootstrap content/profile,
  nonfinite semantic JSON, non-durable partial-phase continuation, and replaced
  admitted archive bytes now reject. The owned 52-test matrix passes.
- These are bounded transport, delivery, continuation, and package-recovery
  primitives. The host CLI explicitly verifies bootstrap readback only; concrete
  connected daily execution and authenticated acceptance remain unfinished.
- Combined working-tree validation passed 228 of 229 tests; the measurement
  command exposed missing synthetic pinned-package references. Added those
  references. Its next run correctly rejected the old committed package schema
  paired with the new installer. Commit this candidate locally, then rerun the
  actual command and full ordinary-CPython suite against the exact new package
  before push or acceptance. No provider or release effect occurred.

## 2026-09-08 — exact runtime primitive candidate validated

- Exact local commit `512b408` passed all 229 tests on ordinary CPython 3.12.14,
  schemas/templates, and immutable release-package smoke validation. The actual
  measurement command also passed against that exact package; refreshed its
  baseline while preserving durable task intent/callback behavior and the
  executable regression. The earlier mixed-schema measurement failure is
  resolved, without weakening package validation or suppressing ordinary child
  interpreter behavior.
- Concrete ingestion candidate is independently under review. A separate
  isolated worker owns canonical-task/Sheets binding, while the brief worker
  implements the now-approved user-added task exception and presentation fixes.
  The generic transport/delivery primitives do not establish a connected daily
  operation or any actual provider acceptance.
- Next: publish the validated primitive integration and verify its exact CI;
  review/integrate the concrete workers, then complete fresh-instance acceptance.

## 2026-09-08 — alpha.13 isolated brief input/rendering correction (in progress)

- In isolated worktree `schoolos-alpha13-brief-worktree` at base
  `b24855c350048a08efbba318da97b08679f094d0`, replaced the minimal brief
  rendering boundary with a deterministic v2 input builder and renderer.
  It derives a displayed source day from a mapped mail internal timestamp in
  the configured timezone; filters News to the inclusive seven-day window
  using only `is_update && !is_action && !is_guideline`; preserves canonical
  Fact/Action text; requires an explicit upstream current-guideline selection;
  and requires an explicit all-unresolved-finite task view rather than reading
  workflow labels as resolution.
- The renderer now preserves configured children before the household, groups
  visible Received days newest-first with stable input order inside a day,
  renders an undated parent-origin task group, emits explicit empty lists,
  escapes text/ordinary hrefs, avoids internal-ID links, and supports only an
  exact declared template placeholder map. The packaged default is fluid with
  16px horizontal padding and tonal banners. Delivery helpers remain unchanged.
- Focused synthetic brief tests cover eligibility, canonical wording,
  received/undated groups, escaping/link preservation, template mapping and
  empty fallbacks, and the required current-guideline dependency. The connected
  synthetic path now assembles a v2 brief input from predecessor artifacts.
  No private source, recipient, provider, delivery, scheduler, or production
  instance was accessed or changed.
- **Exact remaining work:** run focused and complete validation; inspect and
  correct any failures; perform synthetic desktop/mobile visual inspection of
  the rendered default HTML if local tooling permits; run privacy/diff checks;
  review the isolated diff for private leakage; commit only this bounded brief
  candidate in this isolated worktree; then report its commit, changed files,
  validation, visual-check limitation/evidence, and the explicit upstream
  current-guideline-selection dependency to the coordinator. Do not push,
  release, send, schedule, alter delivery code, modify `/Users/jguedj/School-OS`,
  or read coordination/source-baseline material. If a genuine unresolved design
  flaw appears, stop the affected work and report it for the coordinator's
  independent Sol consultation rather than inventing policy.

## 2026-09-08 — alpha.13 undated parent-task presentation approval blocker

- The coordinator supplied a grounded correction: the selected existing brief
  recipe treats a missing/malformed source received date as a rendering blocker,
  so this acceptance path must not use the earlier generic undated-parent
  presentation. The intended generic boundary is a small explicit
  `undated_parent_task_policy`, with `render` available only when explicitly
  selected and the acceptance recipe selecting `block`.
- Automatic approval review rejected the attempted implementation because it
  classified the blocking default as a new policy requiring direct user
  approval. No workaround or indirect policy change was attempted. The current
  isolated renderer still supports undated parent-origin presentation and is
  therefore not ready to commit for the selected recipe.
- **Exact remaining work:** obtain a coordinator/user-approved API/default for
  the explicit undated-parent-task policy; then implement only that approved
  boundary, update focused synthetic tests and the operation recipe, run visual
  inspection if tooling permits, complete validation/privacy/diff checks, and
  commit this isolated candidate only. Keep the original isolation/no-send/no-
  scheduler/no-push instructions from the prior entry in force. If approval is
  not supplied, stop the affected implementation and hand off this exact
  blocker; do not silently omit the parent task, invent a date, or infer a
  different policy.

## 2026-09-08 — alpha.13 explicit missing-date policy rejected

- Following the coordinator's safer direction, attempted a required (no
  default) `undated_parent_task_policy` input field, allowing only explicit
  `block` or `render`. Automatic approval review rejected that shape as well:
  it called the mandatory field a changed brief contract and required direct
  user approval. No code from either rejected patch was applied.
- **Exact remaining work:** wait for direct user approval of the explicit
  selected-recipe missing-date-policy field, or a different directly approved
  product contract. Until then, do not commit the current renderer because it
  would render an undated parent-origin task contrary to the selected recipe.
  The prior isolation, no-send, no-scheduler, no-push, privacy, validation,
  visual-check, and handoff requirements remain in force.

## 2026-09-08 — alpha.13 approved parent-added brief presentation

- Direct user approval resolved the presentation gate. The v2 brief contract
  now renders only explicitly `parent`-origin, unresolved-finite tasks with no
  source-received date under the exact `Parent-added tasks` heading inside their
  configured child or household action section. The renderer does not derive
  origin from absent source data, invent a received date or URL, or relax the
  existing source-origin date/link requirements.
- Corrected the selected-template entry fragments to render a visible em dash
  before `Source`/`Link` anchors and a bold guideline-scope prefix. Added
  provider-independent parent-task coverage across child and household groups,
  absent-link behavior, completed-task rejection from the explicit unresolved
  view, malformed/missing source-date blockers, and refreshed synthetic
  connected-run output hashes.
- Focused CPython 3.12.14 validation passed: `tests.test_brief` and
  `tests.test_tasks` (18 tests). A visible desktop and narrow-mobile selected-
  template inspection confirmed both Parent-added groups, unlinked parent
  items, bold scope, visible separators, correct order, and no horizontal
  overflow. Privacy scan and `git diff --check` passed.
- Complete CPython validation exercised 178 tests; 175 passed. The three
  failures are pre-existing in this isolated base package path: connected-run
  and synthetic-installation extraction reject an incomplete
  `RELEASE-INVENTORY.sha256`. That package-cache correction is already accepted
  on main and is outside this isolated brief candidate; no brief regression was
  reported by the full suite. Next: review the final brief-scope diff, commit
  only the isolated candidate, and hand off its local SHA. Observed provider,
  delivery, scheduler, and private acceptance remain separate work.

## 2026-09-08 — alpha.13 brief omission and scope hardening

- The v2 builder now retains an item's exact canonical scope in
  `scope_display` separately from its configured presentation route. A
  multi-child guideline routed to the household visibly keeps its original
  multi-child prefix, while a single configured child keeps the friendly
  display name. The generic full-content renderer now includes household News
  instead of silently omitting it.
- Template validation now requires each declared placeholder exactly once in
  both HTML and text. A selected entry-slot template still blocks when
  household News has no declared slot, so support in the generic default does
  not weaken selected-template fail-closed routing. Connected synthetic output
  hashes were refreshed for the intended generic layout change.
- Focused CPython 3.12.14 validation passed: `tests.test_brief` and
  `tests.test_tasks` (19 tests). A new selected-template desktop rendering
  visibly preserved the bold multi-child guideline prefix, Parent-added groups,
  separators, ordering, and no horizontal overflow. The responsive source
  template itself is unchanged from the earlier narrow-mobile inspection.
  No private source, recipient, provider, delivery, scheduler, or production
  instance was accessed or changed.
- Connected synthetic regression remained blocked before brief execution by the
  existing incomplete `RELEASE-INVENTORY.sha256` package root (the same two
  installed-candidate failures); privacy scan and `git diff --check` passed.
  **Exact remaining work:** review the isolated delta; create a local
  superseding commit only in this worktree; then report the final SHA and the
  full `b248..final` delta to the coordinator. Do not push, release, send,
  schedule, modify `/Users/jguedj/School-OS`, or access private/provider state.

## 2026-09-08 — reviewed brief renderer integrated

- Integrated the complete brief candidate through `71c7493`, retaining accepted
  source/task/runtime work and both progress histories. Root reran 24 brief/task
  tests and directly confirmed the three review corrections: generic household
  news remains visible, duplicate template placeholders block, and multi-child
  guideline scope survives household routing. The approved Parent-added tasks
  exception, strict source dates, visible link separators, and bold guideline
  scope are now implemented.
- The selected private template passed worker desktop/mobile visual inspection;
  final integrated connected content and visual acceptance remain outstanding.
  No private template, recipient, or source content was added to Git.
- Combined validation reached 237/238 tests; its executable measurement exposed
  the obsolete brief-v1 input without verified links. Adapted measurements to
  persist the synthetic Fact predecessor and invoke the actual v2 builder with
  explicit fixture current-guideline/unresolved-task selection and source
  metadata. Refresh measurements and rerun the exact combined package before
  accepting/publishing this integration. The synthetic connected journey itself
  reaches COMPLETE; refreshed dependent artifact hashes preserve task evidence.
- Independent review rejected initial concrete ingestion/task candidates on
  restart and real connector-shape defects. Isolated repair workers own those
  corrections and actual MIME normalization. They remain unaccepted; no live
  installation, send, schedule, or release has occurred.

## 2026-09-08 — alpha.13 brief measurement integration

- Integrated the reviewed v2 brief path into the synthetic connected daily run
  and measurement command. The measurement now persists the canonical Facts
  predecessor, supplies explicit synthetic source metadata, current guideline
  selection, and unresolved-task selection to `build_brief_input`, then renders
  the actual v2 brief. It creates no provider, delivery, scheduler, or private
  side effect.
- Bundled CPython 3.12.14 executed the adapted synthetic measurement
  successfully. Its evidence is synthetic only: the observed path now includes
  one `brief.build_brief_input` call and nine persisted artifacts, including
  `facts.json`. Regenerate the checked baseline from the final committed source
  before accepting the integration, then run full repository and installed
  candidate validation.
- Recorded the user’s development cost constraint: delegate feasible
  implementation, routine integration, tests, and documentation to lower-cost
  agents; use Terra High by default, Sol High for difficult fixes or focused
  reviews, and reserve Astra for coordination or genuine escalation. This
  constrains development workflow only and adds no runtime vendor dependency.
- Integrated real-source content and selected-template visual acceptance,
  optional-audio degradation, observed runtime/provider execution, remote
  release verification, and all pending ingestion/task/MIME candidates remain
  separate and unaccepted.

## 2026-09-08 — alpha.13 brief integration validated

- Regenerated the checked synthetic measurement baseline from the integrated
  v2 source path.  The synthetic journey persists nine artifacts, including
  `facts.json`, invokes `brief.build_brief_input` exactly once per rendered
  daily path, and records the corrected pause after `reconcile` before the
  resumed task, brief, and commit phases.  This is synthetic evidence only;
  it does not establish runtime, provider, delivery, scheduler, or private
  acceptance.
- Ordinary CPython 3.12.14 validation passed all 238 repository tests.  The
  full validator also passed schemas, templates, package smoke checks, and the
  tracked-file privacy scan.  `git diff --check` passed.  No private source,
  recipient, credential, provider mutation, delivery, schedule, tag, or
  release action occurred.
- Next: publish this exact accepted repository integration, verify the remote
  commit and its CI, then retain the remaining observed-runtime, live/provider,
  visual, audio, and release gates as separate work.

## 2026-09-08 — alpha.13 brief integration publication pending

- Committed the validated integration locally as `d40f781` (`feat: integrate
  deterministic v2 daily brief rendering`).  The working tree was clean and
  the branch was one commit ahead of `origin/main` immediately afterward.
- Publishing to the shared default branch is pending direct confirmation in
  this task.  The repository-side guard rejected the push request, so no
  remote branch, CI run, tag, release, provider, or private-instance state was
  changed.  Once confirmed, push the local commit, verify `origin/main` equals
  the resulting commit, and inspect the resulting GitHub CI run before treating
  publication as complete.

## 2026-09-08 — alpha.13 brief integration published

- The exact amended integration commit
  `6cb12446a2b535646351c82fe5825e9b3d371bda` was fast-forwarded to
  `origin/main`; remote SHA readback matched. GitHub Actions **Validate** run
  `34290495210` completed successfully for that exact SHA. The prior local
  publication-pending entry is superseded.
- CI supplies the exact-commit validation after the final PROGRESS-only amend;
  the earlier local ordinary-CPython suite passed all 238 tests, with schema,
  template, package, privacy, and diff checks. The current working tree is
  clean. No release/tag, provider, private-instance, email, or scheduler
  action occurred.
- Repository brief integration is complete. Remaining gates are unchanged:
  observed authenticated runtime and source/provider execution, final
  connected visual/audio acceptance, fresh-instance/manual/scheduled test
  acceptance, independent audits, and release readiness. Unaccepted ingestion,
  task, and MIME candidates remain isolated.

## 2026-09-08 — Gmail full/raw MIME normalizer integrated

- Integrated the independently accepted normalizer from
  `973e5cb93b831646e4209ea22f435aa38a008085` as
  `school_os.gmail_source`. It cross-binds observed Gmail snake-case full/raw
  message and thread identities, strict RFC2822 base64url bytes, complete MIME
  structure and headers, transport/charset bytes, provider Unicode, attachments,
  and ordered full-thread raw membership before existing source admission.
- The independent review replay closed the five prior unsafe inputs and
  accepted valid ISO-8859-1 quoted-printable custody; its focused Gmail/privacy
  suite passed 17 tests and its candidate full suite passed 237 tests. This
  integration intentionally does not claim connected ingestion binding,
  attachment/PDF/image extraction, direct-resource retrieval, provider access,
  delivery, schedule, or private acceptance.
- Next: run the focused normalizer/custody/semantic tests and repository privacy
  checks on this integrated tree, then commit this scoped integration locally.

## 2026-09-08 — connected source and task workers integrated

- Integrated accepted source delta
  `a69ce99f79a9feb88f4affffcf57788c41af85cb..0352ed1b3a9afc6f0be22bf49f117c37a568f003`
  and accepted task delta
  `512b408..65d890d6c58624f3a90c8da4bbadb2a392463e5d`, preserving the
  current MIME/brief/release work. Both supplied the same reviewed
  `connected_storage` implementation, now present once.
- The source worker rereads complete changed threads and binds full/raw Gmail
  message and thread identities before source custody/audit artifacts. The task
  and Sheets workers preserve canonical-before-provider ordering, guarded
  literal cells, parent/provider recovery, and exact readback. Their respective
  independent reviews accepted the repaired counterexamples.
- Combined focused source/task/Sheets/custody/semantic/bridge validation passed
  58 tests; the full ordinary-CPython validator then passed on exact local
  commit `ba30a265189bde5442eb5f537e9e975294c88e6b`, including package and
  tracked privacy gates. These are repository
  workers only: bootstrap/daily composition, attachment/direct-resource
  extraction, observed provider binding, delivery/scheduler, and private
  acceptance remain open.

## 2026-09-08 — alpha.13 published integration CI portability repair

- Published `main` SHA
  `683ba296919430ebaacd321282a7cd690554ad63` is unchanged, but its exact
  GitHub Actions **Validate** run `34294692219` failed before any private or
  provider-facing work. The failed log identified one test subprocess whose
  `PYTHONPATH` and working directory still named an untracked local temporary
  worktree (`/private/tmp/schoolos-alpha13-brief-worktree`), which does not
  exist on GitHub runners.
- Replaced only that stale temporary path with the test module's repository
  `ROOT`, preserving the isolated child-process assertion while making it
  checkout-portable. Focused `tests.test_connected_tasks` passed, followed by
  the complete ordinary-CPython validator (all 277 tests plus schema, package,
  privacy, and tracked-file checks). No provider, private data, schedule,
  release, tag, or external mutation occurred.
- Next: commit and publish this minimal portability correction, then verify the
  resulting exact remote SHA and GitHub Validate run. The failed run remains
  evidence that `683ba296...` itself is not publication-verified.

## 2026-09-08 — connected ingestion discovery/catalog phase split integrated

- Verified `main` began clean at published
  `000fd387c962b42d4b9ab4ef5c73f99a5ab33991`; remote readback matched and its
  exact GitHub Actions **Validate** run `34295354704` passed. Integrated only
  the independently accepted ingestion delta
  `0352ed1b3a9afc6f0be22bf49f117c37a568f003..14031a1ee9df6309f5bad84840850934e75bcdc9`.
- Discovery now performs one bounded search and persists a body-free immutable
  inventory with exact page, hit, disposition, scope, anchor, and recheck
  evidence. Catalog takes the versioned inventory reference, never searches,
  maintains only run-scoped work, and exposes an eligible cursor only as a
  completion-time proposal for a later commit phase. Complete zero-hit
  inventory is accepted without catalog writes; a nonempty conversation without
  an immutable searched-message anchor blocks both construction and persisted
  artifact validation.
- The accepted source-custody, full-thread recheck, Facts/audit, and shared
  storage behavior remains intact. This is repository-only ingestion staging:
  no daily composition, live connector/provider call, delivery, scheduler,
  private-instance action, tag, or release occurred.
- Focused source/recovery/custody/semantic/bridge/task validation passed 45
  tests. The complete ordinary-CPython validator then passed with schema,
  package, and tracked-file privacy checks; `git diff --check` passed.

## 2026-09-08 — alpha.13 connected task reconcile/task-sync phase split

- Split the concrete task worker without changing task-core, Sheets, shared
  storage, Fact, audit, or brief policy. `ConnectedTaskWorker.reconcile(...)`
  admits audited Fact references (or the existing verified empty disposition),
  reconciles and guarded-persists the canonical register, then returns its
  exact current `StoredArtifact` reference and the canonical unresolved-task
  view. `task_sync(...)` consumes that reference plus provider state and runs
  only the existing provider reconciliation/effect recovery path; it does not
  read Facts or call canonical source reconciliation. `run_once(...)` remains
  the compatibility composition of those two explicit stages.
- The provider-only phase retains current-pointer/readback behavior, canonical
  result persistence, parent/user-added/task completion/reminder handling,
  pre-dispatch unknown-effect checkpoints, native literal scope guards, final
  canonical/provider references, and post-sync brief view. The upcoming daily
  composition must call `reconcile`, carry `canonical_tasks.reference` exactly
  into `task_sync`, and pass its final `brief_tasks` to the accepted v2 brief
  builder; derived knowledge remains that later composition's responsibility.
- Focused CPython 3.12.14 task/Sheets/provider recovery matrix passed 31 tests,
  including the real fresh-process create/reminder hard exits and v2 brief-input
  compatibility. The new direct API regression corrupts the Fact bytes after
  reconcile and proves task_sync neither reads them nor re-derives source state.
  Full `scripts/validate.py` passed all 278 tests plus JSON-schema, manifest,
  package-smoke, and privacy checks; direct privacy scan and `git diff --check`
  also passed. The compact `/private/tmp` handoff is present and the scoped diff
  is ready for one local commit. No provider, private source, email, schedule,
  release, push, or production effect occurred.

## 2026-09-08 — alpha.13 task-sync exact canonical handoff repair

- Independent review found that `task_sync` discarded the version on the exact
  canonical artifact returned by `reconcile` through `.current()`. A valid
  later mutable write could therefore substitute canonical bytes and drive a
  provider effect across the explicit phase boundary. The repair keeps
  `.current()` only in `reconcile`, the explicit Fact/readmission phase, and
  reads the supplied canonical handoff version intact in `task_sync` before it
  reads provider state or can invoke a provider effect.
- The added v2-to-v3 regression advances the canonical object to valid but
  substituted bytes after `reconcile`; `task_sync(v2)` rejects immediately,
  has only the attempted canonical read, and leaves the provider untouched. It
  restores v2 to prove the exact handoff succeeds and still does not reread
  Facts. No recovery framework was added: a restart must explicitly re-enter
  `reconcile` to obtain a newly admitted exact handoff before `task_sync`.
- Focused bundled-CPython task/Sheets/core recovery validation passed 32 tests,
  including real fresh-process create/reminder hard exits and the original
  phase API/v2 brief compatibility checks. Required completion: direct
  privacy/diff checks, compact handoff update, and one local commit. No
  provider, private source, email, schedule, release, push, or production
  effect occurred.

## 2026-09-08 — isolated task-phase integration prepared

- Shared `main` was left unchanged at
  `d18afffd692a83949e554ca243f84139ab454e90`. The accepted task-phase range
  was replayed only in an isolated worktree, retaining `main`'s accepted
  source discovery/catalog, MIME custody, brief, storage, documentation, and
  CI-portability work. The resulting branch is a local fast-forward candidate,
  not a publication or provider action.
- The integrated worker makes `reconcile` the one mutable canonical-reference
  readmission point and carries its returned versioned artifact directly into
  `task_sync`. Task sync rejects a newer substituted canonical version before
  provider-state read or effect dispatch; existing source reconciliation,
  parent/user-added handling, literal Sheets guards, unknown-effect recovery,
  and final brief view retain their prior semantics.
- Remaining gates are unchanged: compose the real daily entrypoint with the
  exact handoff, complete bootstrap/attachment and direct-resource extraction,
  bind observed authenticated providers, and obtain the outstanding M4-008 and
  M4-009 acceptance evidence. No provider, private source, mail, scheduler,
  release, tag, push, or shared-main mutation occurred.

## 2026-09-09 — recovery MVP execution specification drafted

- Stopped implementation and replaced the active execution route with
  `docs/plans/mvp-recovery/PLAN.md`. The recovery plan is a combined plan and
  implementation specification, ready for a new execution session, for one fresh
  install MVP: Drive-canonical source/knowledge/tasks, live Google Sheets and
  isolated Todoist projections,
  manual and scheduled verified test briefs, ElevenLabs audio, complete bounded
  source custody, and durable replay/fresh-session recovery.
- Grounded the plan in current `main` at `bc0128d`, the accepted split
  ingestion/task/Sheets/brief primitives, and the stopped connected candidate
  lineage `9357733 -> d7f3ae3 -> 127219b -> cef9190 -> e44c434`. The candidate
  is explicitly review input rather than an accepted release base. Historical
  implementations, worktrees, tests, and documents are retained but do not
  preempt the new routing.
- Added `docs/plans/mvp-recovery/SOL-HANDOFF.md`, a copyable prompt for a new
  GPT-5.6 Sol High owner. It enforces the unsent 90-minute first thin journey,
  four-active-hour ceiling, final frozen package/configuration/interpreter, fixed
  E2E endpoint, bounded helper/escalation policy, task-tool pull-before-push and
  failure-safe guided switch, exact audio-before-multipart-send ordering, and the
  prohibition on production, goal, or monitoring effects.
- Private domains, recipients, provider IDs, task roots, schedule values, and
  unsanitized reference adapter/settings receipts remain only in gitignored
  `private/mvp-recovery/TEST-PARAMETERS.md` and `ADAPTER-SOURCES.md`. No private
  value was added to Git. Read-only private grounding was performed, but no
  runtime code, provider mutation, private-instance mutation, task-project
  mutation, delivery, scheduler mutation, goal, tag, release, commit, or push
  was performed.
- Root completed the documentation review and corrected audio delivery order,
  failure-safe task-tool activation, phase sequencing, and planned mutable-state
  handling. Privacy scanning of all four changed/new documents against the
  private source identifiers and recipient/domain values passed. Local links,
  Phase 0–5 ordering, six pending implementation statuses, Git-ignore boundaries,
  and `git diff --check` passed. No broad runtime test suite was needed for this
  documentation-only change.
- The accepted documentation checkpoint is ready for commit/push and exact
  remote readback under repository continuity. After publication, the next
  action is to open a new GPT-5.6 Sol High session with the private companion and
  paste the handoff prompt. Implementation remains unstarted.

## 2026-09-09 — one-hour recovery status checkpoint

- Replaced the recovery plan and Sol handoff's 90-minute milestone target and
  four-hour autonomous cap with a mandatory status check-in after 60 elapsed
  wall-clock minutes, including setup, helper work, tool calls, and waiting.
  The recorded deadline survives compaction, delegation, and phase changes.
- The hour is explicitly not a completion deadline. Scope, quality, live
  coverage, validation, and consultation requirements remain unchanged. At the
  checkpoint, preserve unfinished work, report evidence and remaining work,
  propose the next step, and await user direction. Necessary cleanup must not
  become an excuse to postpone the report.
- Documentation-only change; implementation and live testing remain unstarted.
  Next: publish this timing correction, then use the updated Sol handoff when
  the user starts execution.

## 2026-09-09 — recovery MVP Phase 0 candidate reconciled

- Began the authorized fresh recovery execution from `main` at `8d66626`; the
  ignored private clock fixes the one-hour checkpoint at 2026-09-09T18:43:30Z.
  The exact 14-day source bounds and private-input hashes were frozen only in
  ignored recovery evidence. No live resource or provider effect occurred in
  this work unit.
- Reviewed actual branches, worktrees, tags, history, the accepted `bc0128d`
  runtime baseline, and stopped lineage through `e44c434`. The public
  reconciliation ledger classifies each delta. Integrated only the lineage's
  code, runtime documentation, scripts, and tests; current recovery-plan and
  historical progress/status changes remain authoritative on `main` and were
  not replayed.
- Added an explicit manual unsent-preview path to the connected composition.
  It excludes `mail.send` from admission, rejects scheduled or delivery-variant
  use, persists deterministic brief input/HTML/text, leaves the delivery ledger
  unmodified, records zero effects, commits the completed source/task state and
  eligible cursor last, and returns `PREVIEW_READY` instead of claiming daily
  delivery completion. Recovery re-admits the exact preview artifacts.
- Bundled CPython 3.12.14 validation passed all 326 repository tests plus schema,
  template-manifest, package-smoke, and tracked privacy checks. The focused
  preview regression separately passed and proves zero sends, zero reservation,
  unchanged delivery state, stored render references, and cursor-last order.
- Next: run direct privacy/diff/link checks, commit and push this accepted
  candidate source checkpoint, build and validate its exact immutable package,
  record interpreter/dependency evidence, then perform the authorized empty-root
  and empty-Sheet gate before the first live unsent source/task/brief journey.

## 2026-09-09 — recovery MVP Phase 1 live setup gate

- Committed and pushed the reconciled candidate as `b8ca4f3`; exact remote-ref
  readback matched. Its reproducible alpha.13 archive and extracted tree both
  passed installed validation, and the installed connected-operation entrypoint
  returned `INSTALLED_ENTRYPOINT_VERIFIED`.
- Created one new isolated Drive root and one native task Sheet on the
  authorized test surface. The external Sheet was moved to the authorized tests
  parent after readback exposed the installer's empty-root boundary. Final
  readback proves the root has zero children, the Sheet has one empty `Tasks`
  tab, and no values, charts, or provider data exist. Exact IDs, URLs, hashes,
  source bounds, and private settings remain only in ignored evidence.
- Added a finite host-dispatch CLI for the existing JSONL bridge. It validates
  the request through `HostBindingDispatcher`, exposes only the reviewed native
  binding through a mode-0600 private file, validates the returned connector
  envelope, and writes the exact child response. Its focused regression passes.
- Prepared and locally validated the ignored early setup plan from the exact
  frozen package and private companion: two source domains, four ordered
  household groups, one recipient, empty CC/BCC, Sheets selected, no scheduler,
  no audio, and the fixed 14-day `[start,end)` source bounds.
- Next: rebuild the exact candidate package with the host-dispatch CLI, re-run
  installed validation, then execute the create-only installation through that
  bridge before the first bounded unsent preview. Todoist, delivery, audio, and
  scheduling remain untouched.

## 2026-09-09 — recovery MVP revised early package verified

- Rebuilt the early alpha.13 package from `c75068d` after adding the required
  host-dispatch boundary. Archive and extracted-tree installed validation
  passed, the extracted preview entrypoint returned
  `INSTALLED_ENTRYPOINT_VERIFIED`, and an independent rebuild produced
  byte-identical archive bytes.
- Rebuilt and validated the ignored setup plan against that exact extracted
  package. Re-read the live gate immediately before installation: the Drive
  root remains empty and the isolated Sheet remains blank.
- The Sheet remains temporarily beside the root for the installer's initial
  empty-root proof. After create-only installation it must be moved into the
  test root and the selector, parent, and complete root inventory re-verified
  before preview. No installation write, source import, task write, delivery,
  Todoist binding, audio call, or schedule action has started.
- Next: execute the create-only setup through the packaged host dispatcher,
  move and verify the empty Sheet under the installed root, recover from the
  stable bootstrap, and run the first bounded unsent preview.

## 2026-09-09 — recovery MVP live setup adapter repairs

- The first real dispatcher call failed closed before any write because the
  Drive connector returns a flat structured-content envelope while the stopped
  candidate admitted only a nested `result`. Added the observed flat-envelope
  path without accepting text-only fallback; the full suite passed 328 tests.
- A fresh install then exposed filename-derived Drive MIME behavior. JSON and
  Markdown filenames do not remain `application/octet-stream`, so operation
  state and managed payload creation now declare their provider-reported MIME.
  Focused setup tests and the full 328-test validator passed.
- A third fresh install reached manifest creation but its create receipt was
  incomplete. Added exact-ID reconciliation that adopts only an object whose
  name, parent, MIME, and bytes all read back exactly; the full suite passed 329
  tests. These fixes are committed and pushed through `d65efdb`.
- The fourth fresh install executed 101 validated bridge calls and repeated the
  manifest boundary. Exact-ID metadata/content readback ran, but an exact
  manifest identity predicate still disagreed, so installation correctly
  blocked. The four attempted roots are retired and will not be reused. Exact
  IDs and response evidence remain only in ignored recovery artifacts.
- No bootstrap was admitted. Source import, task projection, delivery,
  Todoist, audio, and scheduling remain untouched. Next: retain a private
  sanitized per-create predicate journal, reproduce the manifest mismatch on a
  fresh root, and repair only the proven provider disagreement before another
  package/root cycle.

## 2026-09-09 — recovery MVP archive MIME diagnosis and approved repair

- Read-only reconstruction of the fourth fresh-install attempt corrected the
  prior stage description: the blocked object was the pinned
  `system/package/release.archive` immediately before manifest creation, not
  the manifest itself.
- Exact-ID metadata and raw-byte readback proved the object ID, name, parent,
  URL, byte length, complete bytes, and frozen package hash. The sole mismatch
  was Drive classifying the gzip bytes as `application/x-gzip` after the
  installer requested `application/octet-stream`.
- The approved repair admits a finite gzip MIME equivalence only for that
  byte-proven pinned archive, persists the actual provider MIME, and keeps
  every other MIME exact. Create failures now name individual failed predicates
  instead of collapsing them into one ambiguous error.
- Next: pass focused and full repository validation, publish the repaired
  checkpoint, rebuild and verify its immutable package, and use a new empty
  Drive root and Sheet for the next early integration attempt.

## 2026-09-09 — recovery MVP fresh installation admitted

- The finite archive MIME repair and per-property readback diagnostics passed
  331 repository tests, installed-package checks, schema/template validation,
  and tracked privacy checks. Commit `5c7c57d` was pushed and exact remote-ref
  readback matched.
- Built and installed-validated the immutable alpha.13 archive from that exact
  commit. An independent rebuild was byte-identical. The frozen archive
  SHA-256 is `ad96c783a4d4500225f9a09fe96642ab969572309c99acf4ec40268b999650ad`.
- Created a new isolated Drive root and native Sheet under the authorized test
  parent. Initial readback proved the root empty and the Sheet contained one
  empty `Tasks` tab before the packaged installer wrote anything.
- The packaged create-only installer completed beyond the prior archive gate
  and produced the manifest, verified admission, and bootstrap. Exact inventory
  readback found all 29 expected installed objects with no missing or unexpected
  child. The Sheet was then moved into the installed root as planned; readback
  proved 30 total exact children, one Sheet parent, all 13 required headers,
  and zero task rows.
- No source import, task creation, delivery reservation, Todoist operation,
  audio call, email, or schedule action occurred. Private identities, bootstrap,
  setup plan, and receipts remain only in ignored recovery evidence.
- Next: recover through the stable bootstrap using only installed package bytes,
  then run the bounded real source/task/Sheets/render path to the unsent preview
  gate without reserving or sending a delivery.

## 2026-09-09 — recovery MVP unsent-preview bootstrap handoff repair

- Pre-source inspection of the admitted runtime found that the installed daily
  entrypoint already implements the required manual-only `--preview-only` path,
  but the stable bootstrap wrapper neither accepted nor forwarded that flag.
  Running the wrapper as admitted would therefore enter delivery composition,
  which is forbidden before the early gate; no source or delivery call was made.
- Added the finite flag across the bootstrap handoff and rejected preview use
  with the scheduled entrypoint, legacy bootstrap-readback mode, scheduler
  admission, or synthetic stage results. Focused bootstrap/CLI tests pass.
- This is executable-package drift, so the previously admitted root is retired
  from runtime evidence without modification. Next: pass full validation,
  checkpoint and push the repair, rebuild the immutable package, and install it
  only into another new empty root and isolated Sheet before the preview.

## 2026-09-09 — recovery MVP Drive storage architecture approval

- Published and remotely verified the preview handoff repair at exact commit
  `a654f04832a403881569a526b81edc72a48a0466`; the frozen interpreter passed all
  333 repository tests and produced a reproducible installed-valid package.
- Later fresh-install attempts demonstrated that the per-logical-file topology
  causes many sequential Drive operations before source work. One attempt
  stopped on a generic unknown folder-create failure with no reconciled folder;
  another was interrupted during read-only metadata after more than 70 bridge
  operations. No source, task, delivery, Todoist, audio, email, or scheduler
  effect occurred. Exact private receipts remain gitignored.
- The user approved the bounded hybrid architecture after one GPT-6 Astra
  consultation: five initial physical files (`BOOTSTRAP.json`, package,
  readable settings, `CURRENT.json`, and one immutable state bundle), immutable
  successor generations with previous-state preservation, bundle-member
  references, post-install projection binding, full readbacks where equivalent
  provider checksum receipts are unavailable, and privacy-safe diagnostics.
  The single mutable ZIP alternative was rejected.
- Added `docs/plans/mvp-recovery/DRIVE-STORAGE-SPEC.md` as the focused authority
  for encoding, topology, admission/publication ordering, interrupted-effect
  recovery, current connector fallbacks, call accounting, implementation order,
  and focused/live proof. Updated both active plans to link this contract.
- No provider call or tracked runtime change occurred in this work unit. Next:
  validate and publish this documentation checkpoint, then implement the
  deterministic bundle codec and focused contracts before refactoring the
  installer/bootstrap path.

## 2026-09-09 — recovery MVP deterministic bundle implementation

- Published and remotely verified the approved storage specification checkpoint
  at exact commit `e6e49edb05f68fe91eb9b612f43074e06d3ef28b` before changing runtime code.
- Added the provider-neutral `school_os.bundles` codec. It produces byte-stable
  uncompressed ustar archives with canonical inventory JSON, normalized member
  metadata, exact hashes and lengths, predecessor binding, fixed state/source/
  output bounds, and safe read-time rejection of traversal, links, duplicates,
  undeclared members, tampering, oversize content, and nonzero trailers.
- Added checked-in contracts for bundle manifests, bundle-member references,
  the mutable current-state pointer, and the immutable bootstrap descriptor.
  Six focused bundle tests pass, including rebuild equality and schema
  validation.
- The frozen Python 3.12.14 interpreter passed the complete repository
  validation: 339 tests plus JSON-schema and template-manifest checks. A prior
  invocation with macOS system Python 3.9 failed on pre-existing Python-version
  requirements (`zip(strict=...)`, `datetime.UTC`, and `Path.stat` behavior);
  it is not accepted validation and made no changes.
- No provider call or external effect occurred. Next: publish this bounded codec
  checkpoint, then implement the five-object installer/current/bootstrap
  composition and fresh-process recovery against the new contracts.

## 2026-09-09 — recovery MVP five-object installer core

- Published and remotely verified the deterministic bundle checkpoint at exact
  commit `836f6416004292f82f82d7022d747f77857403f0`.
- Added the provider-neutral five-object create/recover boundary in
  `school_os.install`. It verifies the release archive and internal inventory
  without a sixth checksum object; creates package, settings, initial state,
  current pointer, and bootstrap in that order; retains the finite gzip MIME
  equivalence; and performs no duplicate read after a create surface has already
  returned complete verified bytes.
- Bootstrap binds the mutable `CURRENT.json` by stable exact ID/parent/MIME but
  deliberately not a stale provider version. Recovery obtains the pointer's
  current version and exact canonical bytes, then verifies package/settings/
  state hashes, state manifest bindings, initial predecessor absence, and every
  bundle entry. Immutable package/settings/state references remain versioned.
- Focused coverage proves exactly five objects, one recovery read per physical
  file, adoption after one lost create response without duplication, state-byte
  tamper rejection, and recovery after only the current-pointer version changes.
  Existing installer tests remain green. The complete frozen-interpreter gate
  passes 343 tests plus schema/template checks.
- This is not yet the active connected setup/bootstrap route, and successor
  state publication is not yet implemented. No provider call or external effect
  occurred. Next: publish this core checkpoint, compose the real settings and
  initial logical entries in connected setup, separate projection binding, and
  route connected bootstrap recovery through these five objects.

## 2026-09-09 — recovery MVP immutable successor publication

- Published and remotely verified the five-object installer core at exact
  commit `95a3a08`.
- Corrected bootstrap admission so the immutable descriptor binds the stable
  current-pointer identity but does not pin generation 1. `CURRENT.json` alone
  names the current immutable state and previous generation, allowing later
  publication without rewriting bootstrap or introducing a circular hash.
- Added successor publication: verify the current base/version, require exact
  admitted writer-exclusion evidence, build and verify one immutable successor,
  create it first, replace/read back `CURRENT.json` second, and preserve the
  prior state reference. Lost pointer-update responses adopt only the exact
  intended bytes by the existing pointer ID; they never cause an automatic
  second mutation.
- Added the finite connected Drive pointer replacement surface. It labels its
  pre-read explicitly as a drift guard rather than compare-and-swap, performs
  complete byte readback, and preserves the byte-proven gzip MIME equivalence
  for the new package filename.
- Focused tests cover predecessor preservation, recovery following generation
  2, insufficient serialization evidence blocking before creation, and exact
  lost-response adoption. The complete frozen-interpreter validation passes 346
  tests plus schema/template checks. No provider call or external effect
  occurred.
- Next: publish this successor checkpoint, then compose human-readable settings
  and initial logical bundle members in the connected setup route. Projection
  initialization/binding remains deliberately after five-object admission.

## 2026-09-09 — recovery MVP connected setup composition

- Published and remotely verified immutable successor publication at exact
  commit `6349a8c118c245663284d7b258d2b377c48c2575`.
- Added the readable installation-settings contract and a connected composition
  seam that validates the existing private setup payloads, moves frozen
  instance/household/integration/policy/daily/source/delivery settings into one
  deterministic YAML document, and maps mutable logical records into the
  initial state bundle without provider writes.
- The initial task selector is explicitly `unbound` with Sheets selected; task
  projection initialization and binding therefore cannot precede canonical
  installation admission. The logical file map contains bundle entry paths,
  not fabricated Drive IDs. Package/settings hashes produce the deterministic
  configuration fingerprint.
- Focused composition coverage and the complete frozen-interpreter gate pass
  347 tests plus schema/template checks. This seam is not yet selected by the
  setup CLI or connected bootstrap, so the old connected installer remains the
  active executable route until the next atomic wiring unit is complete. No
  provider call or external effect occurred.
- Next: publish this composition checkpoint, then atomically route connected
  setup and bootstrap through five-object install/recovery and add the separate
  post-admission Sheet initialization/binding operation.

## 2026-09-09 — recovery MVP provider-connected five-object install seam

- Published and remotely verified the connected composition checkpoint at exact
  commit `ed9de538b0014dd8f22200c4b53afadb4046f67d`.
- Added a provider-connected hybrid installer that verifies the exact root and
  complete empty listing, delegates to the five-object admission core, and
  returns only the stable bootstrap/current/configuration evidence with
  projection status `unbound`. It accepts no Sheet surface and therefore cannot
  initialize or bind a projection before canonical installation.
- The connected fake-provider test proves exactly five direct root children by
  name and a JSON bootstrap. The complete frozen-interpreter gate passes 348
  tests plus schema/template checks. The existing setup CLI still selects the
  archived per-file function; changing that selection waits for hybrid package
  extraction and bundle-backed runtime resolution so no half-wired live route
  is exposed.
- No provider call or external effect occurred. Next: publish this seam, add
  hybrid recovered-package extraction, then implement the bundle-backed runtime
  resolver and switch setup/bootstrap dispatch together.

## 2026-09-09 — recovery MVP hybrid package extraction

- Published the provider-connected five-object install seam at `47fd1fa`.
- Added hybrid package extraction that derives the conventional checksum input
  from the already-admitted bootstrap hash, reuses the existing archive/
  inventory/safe-extraction verifier, and rejects changed package bytes before
  creating the destination. No checksum file is added to Drive.
- Focused valid/tampered extraction coverage passes. The complete frozen-
  interpreter gate passes 349 tests plus schema/template checks. The hybrid
  setup/bootstrap CLI selection and bundle-backed daily resolver remain open;
  the old executable route is still selected and no live install should start.
- No provider call or external effect occurred. Next: publish this extraction
  checkpoint, add hybrid bootstrap recovery/dispatch and bundle-member runtime
  resolution, then switch the setup and bootstrap scripts atomically.

## 2026-09-09 — recovery MVP exact bundle-member references

- Published and remotely verified hybrid package extraction at exact commit
  `03f7bc64dc20a23a3fb29d782df9566adbf82dd6`.
- Added the typed bundle-member reference and resolver. A reference contains the
  real physical bundle object/version plus bundle hash, logical entry path,
  entry hash, and length; it exposes no member-level provider ID. Resolution
  requires the exact already-verified bundle bytes and exact member evidence.
- Focused coverage proves physical/logical identity separation, checked-in
  schema round-trip, exact bytes, and rejection when the same member is offered
  from different physical bundle bytes. The complete frozen-interpreter gate
  passes 350 tests plus schema/template checks.
- No provider call or external effect occurred. Next: publish this reference
  checkpoint, implement a bundle-backed working-state/store boundary, then
  route connected bootstrap/daily workers without preserving any assumption
  that logical members are separate Drive objects.

## 2026-09-09 — recovery MVP staged-versus-durable working state

- Published and remotely verified exact bundle-member references at exact
  commit `123aaf57a43c748d486401b1025865c3ee64c59e`.
- Added `BundleWorkingState`, which reconstructs logical entry metadata from one
  verified current bundle, supports disposable staged changes, refuses durable
  references for staged bytes, and clears the staged set only after immutable
  successor creation and exact `CURRENT.json` publication succeeds.
- Focused coverage proves the pre-publication reference refusal, changed bundle
  and member hashes after publication, and generation advancement. The complete
  frozen-interpreter gate passes 351 tests plus schema/template checks.
- This working state is not yet wired into connected ingestion/task/delivery
  workers. No provider call or external effect occurred. Next: publish this
  checkpoint, implement the hybrid bootstrap/runtime document and bundle-backed
  connected resolver, then atomically select the new setup/bootstrap route and
  add post-admission Sheet binding.

## 2026-09-09 — recovery MVP hybrid bootstrap handoff

- Published and remotely verified the staged-versus-durable working-state
  checkpoint at exact commit `5ac833529605ecaa7e036c585ddec165c5984cf4`.
- The installed-package bootstrap now dispatches by the admitted bootstrap MIME:
  the archived Markdown layout retains its old verifier, while the JSON layout
  runs the five-object hybrid recovery and package extraction path.
- The hybrid handoff reuses the already-verified settings and state-bundle bytes
  through mode-0600 private files bound by SHA-256 in the child runtime
  document. The installed child re-verifies those hashes and the full bundle
  before composition, avoiding another provider download without treating the
  private handoff files as durable state.
- Focused bootstrap/bundle coverage passes 37 tests, including layout dispatch,
  exact private-file permissions, hash binding, and state rehydration. The setup
  CLI and connected daily resolver are still deliberately on the archived
  layout, so no live package is admitted yet. No provider call or external
  effect occurred.
- Next: publish this bootstrap checkpoint, implement the bundle-backed connected
  resolver and post-admission Sheet binding, then switch the setup/bootstrap
  route atomically and run the complete frozen-interpreter gate.

## 2026-09-09 — recovery MVP post-admission Sheets binding

- Published and remotely verified the hybrid bootstrap handoff at exact commit
  `6a38639904a2b438f957f7ddc176e46239768567`; its complete gate passed 353
  tests plus schema/template validation.
- Added the separate post-admission Sheets binding transition. It re-recovers
  the admitted five-object generation, requires the exact initial unbound
  selector, initializes and verifies the isolated Sheet scope, stages a binding
  with the logical provider-state member path, then advances `CURRENT.json`.
- Focused coverage proves the successful binding is generation 2 and that a
  failed pointer publication leaves generation 1 and its unbound selector
  authoritative even though the already-initialized isolated Sheet remains.
  The exact selector representation is now recorded in the approved storage
  specification. No provider call or external effect occurred.
- Next: publish this binding checkpoint, add a bundle-native logical artifact/
  checkpoint model without same-bundle self-references, then route the connected
  resolver and setup CLI through the hybrid path as one validated unit.

## 2026-09-09 — recovery MVP carrier-relative peer references

- Published and remotely verified post-admission Sheets binding at exact commit
  `e6cadb8ca9863ea32464ee286fcc236985ac2d3b`; 62 focused setup, bundle, and
  bootstrap tests passed.
- Added a typed carrier-relative peer reference containing exact logical path,
  SHA-256, byte length, and media type, plus checked-in schema and resolver.
  It deliberately contains no provider identity or whole-bundle hash and is
  unusable without the verified enclosing bundle; this permits checkpoints to
  name peer artifacts without a self-hash cycle.
- Focused coverage proves schema round-trip, exact resolution, absence of fake
  physical identity, and rejection against a changed verified carrier. The
  approved storage specification now records this exact two-level reference
  rule. No provider call or external effect occurred.
- Next: publish this reference checkpoint, implement the bundle transaction/
  phase-publication store using peer references, then adapt the connected
  resolver and setup CLI without exposing a half-wired live route.

## 2026-09-09 — recovery MVP bundle transaction and configuration resolver

- Published and remotely verified carrier-relative peer references at exact
  commit `a8675551007b94ac0682d615319757b7d8ec2070`; 63 focused tests passed.
- Added an immutable bundle transaction store. It reads exact logical members,
  stages replacements/additions with carrier-relative evidence, exposes no
  durable reference for dirty bytes, and advances to a durable store only after
  immutable successor creation plus exact pointer publication.
- Added the provider-free hybrid configuration resolver. It consumes the
  already-verified settings/current/state handoff, validates every file-map
  member, resolves the entrypoint-specific capability profile by path/hash,
  requires an active bound Sheets selector, and reconstructs the exact isolated
  Sheet scope without another Drive call.
- Focused integration exposed two pre-live issues and fixed them: the profile
  registry now has exact `manual`/`scheduled` slots, and the owned YAML codec
  preserves empty lists/mappings as `[]`/`{}` instead of changing them to empty
  mappings. The installation-settings schema now fixes the hybrid instance
  shape. Tests prove a phase artifact and its peer checkpoint can publish in one
  generation and then resolve from the verified carrier.
- No provider call or external effect occurred. Next: run the complete gate and
  publish this checkpoint, then implement the hybrid operation/checkpoint
  publisher and adapt one thin preview phase chain before selecting the CLI.

## 2026-09-09 — recovery MVP atomic hybrid operation boundary

- Published and remotely verified the bundle transaction/configuration resolver
  at exact commit `b257b7a1a0eaf3db15ef48450943bd7523d7e81e`; the complete frozen-
  interpreter gate passed 358 tests plus schema/template validation.
- Added a hybrid checkpoint publisher that validates the existing operation
  transition first, stages an immutable checkpoint and replacement operation
  state in one bundle transaction, publishes one successor generation, verifies
  both exact peer bytes from the new carrier, and only then returns their full
  durable member references.
- Focused end-to-end storage coverage now proves five-object install generation
  1, verified post-admission Sheets binding generation 2, provider-free hybrid
  configuration resolution, and atomic preflight admission generation 3. The
  checkpoint and state durable references share the exact verified bundle hash;
  the checkpoint peer contains no provider identity. No provider call or
  external effect occurred.
- Next: validate and publish this boundary, then adapt hybrid discovery/catalog
  persistence to source bundles and use this publisher at the first complete
  phase boundary. The active CLI remains on the archived route until the thin
  preview path is coherent.

## 2026-09-09 — recovery MVP immutable content-bundle publication

- Published and remotely verified the atomic hybrid operation boundary at exact
  commit `d070638940c801cb2e101c21223a985ed42981e8`; 52 focused setup, bundle,
  and operation-state tests passed.
- Added bounded source/output bundle publication using the same exact create/
  uncertain-response adoption/readback path as installation objects. It binds
  the content to the admitted instance, package, settings, and configuration,
  validates all bundle bytes, and deliberately does not advance `CURRENT.json`.
- Focused coverage publishes complete text and PDF source bytes into one source
  bundle, verifies its carrier and members, and proves current state remains on
  the predecessor generation until a later state transaction records the full
  content references. The storage specification now makes this two-step
  durability/canonicality boundary explicit. No provider call or external
  effect occurred.
- Next: publish this checkpoint, add the catalog-state adoption transaction for
  a verified source bundle, then compose discovery/catalog through that path.
  The active CLI remains unchanged until the complete unsent preview chain is
  wired and validated.

## 2026-09-09 — recovery MVP source-bundle canonical adoption proof

- Published and remotely verified immutable content-bundle publication at exact
  commit `00609535404e920f588bb835082c7c3988d67a7c`; 20 focused bundle and
  hybrid-lifecycle tests passed.
- Extended the focused hybrid lifecycle through source adoption: it publishes
  exact source bytes in an immutable source bundle, constructs the full
  physical/member reference, stages that reference in the catalog index, and
  atomically publishes the catalog index plus operation checkpoint/state as
  generation 4. The test proves the source bundle remains noncanonical before
  that state advance and the canonical index names its exact bundle hash after.
- No provider call or external effect occurred. The mandatory communication
  checkpoint stopped further implementation before connected discovery/catalog
  adapters were routed through this primitive.
- Next: adapt connected discovery/catalog output construction to source-bundle
  entries and the atomic adoption boundary, then continue reconcile/task/render
  staging. Keep the setup CLI archived until the entire unsent preview route is
  coherent and validated.

## 2026-09-09 — recovery MVP installed hybrid ingestion path

- Added the approved bundle-native connected-ingestion seam without changing
  source interpretation or storage architecture. The established Gmail,
  catalog, semantic-audit, and Fact worker now runs over an explicitly
  disposable local staging store while the adapter captures exact raw RFC2822
  messages, supported attachment originals, and bounded direct-resource bytes.
- A complete bounded batch publishes one verified immutable source bundle,
  constructs a schema-version-2 canonical index containing only full physical
  bundle/member references, stages queryable Facts and Fact indexes, and
  atomically advances operation checkpoint/state with `CURRENT.json`. The
  catalog-only boundary does not advance the eligible source cursor and leaves
  reconcile as explicit remaining work.
- Added the installed `scripts/run_hybrid_ingestion.py` command and focused
  coverage proving that local staging identities cannot leak into canonical
  source references. The complete frozen-interpreter gate passes 360 tests plus
  schema/template validation.
- No provider call or external effect occurred in this work unit. Next: commit
  and remotely verify this path, build and independently validate the exact
  package, create a new empty authorized acceptance root and isolated Sheet,
  install/bind/recover it, then run and validate the live bounded ingestion.

## 2026-09-10 — recovery MVP cold-recovery URL compatibility

- Published and remotely verified the installed hybrid ingestion path at exact
  commit `0effd93ab48b650fd66284993a3fbc14e6db204a`; the complete frozen-
  interpreter gate passed 360 tests plus schema/template validation.
- Built and installed that exact package into a new empty authorized test root,
  then initialized and bound a new isolated Sheet as post-admission generation
  2. The first cold-recovery check stopped before any provider request because
  the Drive connector returned its normal `usp=drivesdk` URL decoration while
  `BootstrapDocument` still rejected every query string.
- Retired that test root as required after a runtime-code correction. The
  correction admits only the single exact Google Drive SDK decoration on a
  canonical Drive/Docs URL; non-Google hosts, different values, extra
  parameters, duplicate parameters, fragments, and non-HTTPS URLs remain
  rejected. This aligns the bootstrap-document boundary with the already-
  admitted exact-object readback rule and does not change the approved storage
  architecture.
- Focused regression coverage and the complete frozen Python 3.12.14 gate pass:
  360 tests plus schema/template validation; the tracked-file privacy scan also
  passes. No live source read, ingestion, task write, email, audio, Todoist, or
  scheduler effect occurred in the retired instance.
- Next: publish this compatibility checkpoint, rebuild and independently
  validate the exact package, create a new empty authorized acceptance root and
  isolated Sheet, install/bind/cold-recover it, then execute and validate the
  live bounded ingestion from the installed package.

## 2026-09-10 — recovery MVP live Gmail raw-encoding compatibility

- Published and remotely verified the exact Drive SDK URL compatibility at
  commit `9b303fe21afc5ca24dece73c9f8f5c99bb3143e0`, built and independently
  validated its package, and installed the five-object layout into a new empty
  authorized test root. Post-admission Sheet initialization/binding reached
  verified generation 2, and cold recovery reconstructed package, settings,
  pointer, and state bytes exactly from Drive.
- The first installed live ingestion read the bounded Gmail discovery set and
  stopped before any Drive/state mutation when one raw RFC2822 field failed the
  decoder's unpadded-only check. A bounded read-only diagnostic isolated the
  property: the connector returns the URL-safe alphabet with canonical `=`
  padding, no standard-base64 `+`/`/` characters, and no whitespace. Exact bytes
  therefore remain recoverable; rate limiting was not involved.
- Corrected the narrow inconsistency by admitting zero to two canonical
  URL-safe padding characters for raw RFC2822, matching the existing strict
  Gmail body decoder. Standard base64, whitespace, misplaced/excess padding,
  and undecodable forms remain rejected. This is an adapter compatibility fix,
  not a storage or source-custody architecture change.
- Focused coverage proves padded and unpadded values decode to identical exact
  bytes while malformed alternatives fail closed. The complete frozen Python
  3.12.14 gate passes 361 tests plus schema/template validation, and the
  tracked-file privacy scan passes.
- The stopped generation-2 instance is retained only as private evidence; no
  source bundle, canonical ingestion state, task, email, audio, Todoist, or
  scheduler effect was created. Next: publish this fix, rebuild the exact
  package, use a new empty root and isolated Sheet, then repeat install,
  bind, cold recovery, and the live bounded ingestion through validation.

## 2026-09-10 — recovery MVP bounded CSS resource inventory

- Published and remotely verified the canonical Gmail base64url-padding fix at
  exact commit `7a145f3e9a26c3f2725076cc9ae83c9d5b62a4f8`. A new isolated five-object
  installation and post-install Sheet binding reached generation 2, and a cold
  recovery again proved the package, settings, current pointer, and state from
  Drive before execution.
- The live ingestion then read the complete bounded Gmail selection and stopped
  before any source-bundle or state mutation because one HTML alternative used
  CSS resource references. Private inspection isolated seven direct HTTPS CSS
  URLs: four presentation-only web fonts and three image assets. It found no
  CSS imports, non-HTTPS or relative URLs, data or CID URLs, `srcset`, picture,
  source, SVG, linked stylesheets, objects, embeds, or iframes.
- Extended the existing direct image/PDF inventory parser at its current seam:
  direct HTTPS CSS image references now enter the same bounded resource-fetch
  path, recognized web-font suffixes remain presentation-only, and imports,
  non-HTTPS URLs, and malformed quoted URLs continue to fail closed. This does
  not add CSS execution, rendering, crawling, base-URL resolution, or a new
  custody/reference model.
- The complete frozen Python 3.12.14 interpreter gate passes 361 tests plus schema
  and template validation, including the tracked-file privacy scan. The stopped
  instance is retained only as private evidence and has no canonical ingestion
  result or downstream task, delivery, audio, Todoist, or scheduler effect.
- Next: publish this fix, build and verify its exact immutable package, use a new
  empty authorized root and isolated Sheet, then repeat installation, binding,
  cold recovery, and execute the live ingestion through canonical validation.

## 2026-09-10 — recovery MVP direct-resource extractor binding

- Published and remotely verified CSS direct-resource inventory support at
  exact commit `0df55f7e73c8c03ff664e9875b510c3193ba00d2`. Its exact immutable
  package passed installed validation, then a new isolated instance completed
  the five-file install, post-install Sheet binding at generation 2, and cold
  Drive recovery. Measured connector calls were 30 for install, 24 for binding,
  and 13 for recovery; underlying Drive API operations and hidden retries remain
  unavailable from the connector.
- The live run enumerated and read the complete bounded Gmail selection and
  fetched ten direct HTTPS resources, then correctly stopped before Drive/state
  publication because resource coverage remained unresolved. Private metadata-
  only diagnosis found eight exact PNG resources and two exact single-frame GIF
  resources, all with successful, complete, byte-count-consistent reads.
- The failure was an ordinary composition omission: the installed hybrid worker
  configured the existing attachment extractors but did not pass the existing
  image/PDF extractors to its direct-resource seam. The two GIFs also exercised
  an omitted single-frame MIME admission even though the selected Pillow decoder
  can verify their exact signature, MIME, frame count, and dimensions.
- Bound the existing PDF/image extractors to direct resources using deterministic
  content identities and admitted only exact single-frame GIF images through the
  same signature/MIME/dimension/frame checks. No storage, canonical-reference,
  source-policy, extraction, or provider architecture changed; animated or
  malformed GIFs still fail closed.
- Focused source/import/hybrid tests pass, and the complete frozen Python 3.12.14
  gate passes 363 tests plus schema/template validation and the tracked privacy
  scan. The diagnosed generation-2 instance is retained only as private evidence
  and has no canonical ingestion or downstream effect.
- Next: publish this compatible fix, rebuild the exact immutable package, create
  a new empty root and isolated Sheet, and repeat install, bind, cold recovery,
  live ingestion, and canonical result validation.

## 2026-09-10 — recovery MVP exact 8-bit MIME transport preservation

- Published and remotely verified the direct-resource extractor binding at
  exact commit `bab04fa34e6e997229b0309af63c5b816fc69941`. A new immutable
  package and isolated instance again passed install, generation-2 Sheet
  binding, cold Drive recovery, and installed-package verification.
- The live run successfully gave all ten direct PNG/GIF resources complete
  original-detail visual extraction. It then completed bounded interpretation
  and independent audit of the first source conversation, with 14 exact source-
  linked announcement Facts and byte-complete `no_fact` coverage for the
  remaining body and presentation content.
- The next source conversation stopped before publication because one raw MIME
  leaf used non-ASCII `8bit` transport and the raw parser attempted only ASCII
  surrogate recovery. A local byte-level reproduction proved Python's parsed
  `decode=True` result preserves the exact original bytes, including CRLF, for
  the already-supported identity/8bit/binary transport modes.
- Updated only that exact-byte recovery branch. Base64, quoted-printable, and
  7bit continue through their stricter existing paths; unsupported or lossy
  cases still block. Added regression coverage for exact UTF-8 8bit transport.
  This is an adapter correction and does not change source, custody, storage,
  or provider architecture.
- Focused source tests pass, and the complete frozen Python 3.12.14 gate passes
  364 tests plus schema/template validation and the tracked privacy scan. The
  stopped instance retained no source bundle, state advance, task, delivery,
  audio, Todoist, or scheduler effect.
- Next: publish this fix, rebuild the exact package, create a new empty isolated
  instance, and repeat the live ingestion through every source unit and final
  canonical validation.

## 2026-09-10 — recovery MVP declared-versus-verified resource MIME

- Published and remotely verified the exact 8-bit transport repair at commit
  `96d80472ba4796ae8147ad0f43347bd677d59805`. Its immutable package passed
  installed validation, five-object installation into a new empty isolated root,
  post-install Sheet binding at generation 2, and cold Drive recovery.
- The live run completed full original-detail resource extraction, semantic
  interpretation, and independent audit for its first conversation. The next
  conversation proved the 8-bit repair, then stopped before source publication
  on one direct asset whose server-declared MIME was GIF while its exact byte
  signature and decoder format were PNG. Private original-detail inspection
  confirmed the asset contains visible source content, so exclusion would not
  satisfy complete inventory.
- Implemented the existing adapter seam's narrow custody correction: direct
  resource evidence now retains both the provider-declared MIME and the
  byte-verified MIME, while extractor selection and catalog MIME use only the
  verified signature. Unsupported signatures, incomplete reads, missing
  extractors, and failed complete-unit checks remain blocking dispositions.
  Storage layout, canonical references, source scope, and provider architecture
  are unchanged.
- Focused import, custody, connected-ingestion, and hybrid tests pass (34 tests),
  including a declared-GIF/verified-PNG round trip through catalog and semantic
  provenance. The stopped isolated root has no source bundle, state advance,
  task, delivery, audio, Todoist, or scheduler effect.
- The complete frozen Python 3.12.14 gate passes 364 tests plus schema/template
  validation; the direct tracked-file privacy scan and `git diff --check` also
  pass. The current continuation has no wall-clock checkpoint and must stop for
  consultation only if further progress requires an architecture change.
- Next: run the complete repository/privacy gate, commit and push this compatible
  repair, rebuild the exact immutable package, create another new empty root and
  Sheet, then repeat install, bind, cold recovery, live ingestion, and canonical
  validation.

## 2026-09-10 — recovery MVP installed recovery-directory invariant

- Published and remotely verified the declared-versus-verified MIME repair at
  exact commit `35c302eeba071fb0723a9e29156ed6b3f3cf6ab8`. Its immutable
  package passed five-file installation and post-install Sheet binding in a new
  isolated root. Cold recovery completed with 7 exact metadata reads and 6
  exact content reads and no scoped search.
- The recovered package then stopped locally before ingestion because bootstrap
  extraction verified the required `School-OS-<version>` directory and renamed
  it to `installed-<operation>`, while every installed entrypoint correctly
  requires the release-directory identity. No source bundle, state advance,
  task, delivery, audio, Todoist, or scheduler effect occurred.
- Corrected only the bootstrap destination name and updated its regression
  assertion. The approved five-file layout, Drive references, hashes,
  publication ordering, source rules, and provider architecture are unchanged.
- Next: complete validation, publish the compatible repair, rebuild the exact
  immutable package, create a new empty isolated instance, and repeat install,
  bind, cold recovery, live ingestion, and canonical validation.

## 2026-09-10 — recovery MVP bounded direct-resource exclusion

- Published and remotely verified the recovery-directory repair at exact commit
  `b8e69183041b308578dba2ebd83dc49e4866fc70`. Its immutable package passed
  five-file installation, post-install Sheet binding, cold Drive recovery, and
  installed-package validation in a new isolated instance.
- Live ingestion completed source interpretation and independent audit through
  three conversations and was processing the fourth when one direct HTTPS
  resource returned a provider-proven content length above the frozen per-item
  byte bound. The run stopped locally before source-bundle or state publication;
  no task, delivery, audio, Todoist, or scheduler effect occurred.
- The accepted importer and source-custody contracts already define
  `excluded_by_policy` as the finite terminal outcome for an oversized bounded
  direct resource. Completed the missing connected-adapter path with a typed
  exclusion carrying exact request/final URL and redirect provenance. Declared
  overflow reads no response body; unknown-length overflow reads only through
  the first byte beyond the bound. Neither path creates extracted text or a
  Fact, while malformed, contradictory, incomplete, or unsupported responses
  still fail closed.
- Focused connected-source, source-custody, hybrid-ingestion, and connected-
  ingestion tests pass. The complete frozen CPython 3.12.14 gate passes 364
  tests plus schema/template validation, including catalog serialization of the
  visible policy exclusion and the tracked-file privacy scan. No architecture,
  source bound, storage, reference, provider, or state contract changed.
- Next: commit and publish the compatible repair, rebuild its exact immutable
  package, create a new empty acceptance root and isolated Sheet, repeat install,
  binding, cold recovery, and execute live ingestion through canonical Drive
  publication and independent validation.

## 2026-09-10 — recovery MVP publication gate blocked

- Committed the validated bounded-resource repair locally as exact runtime
  commit `b5a8d461353d0931cc7235ca4227948a779d6035`. The environment denied both
  attempts to push to the configured private GitHub origin because it requires
  a new explicit authorization for that destination. The branch is one commit
  ahead of its remote; no alternate publication path was attempted.
- Built the exact `0.1.0-alpha.13` immutable package from that commit. Its
  archive SHA-256 is
  `8c64b5e50a66bd419b8252830ca12c6686d9a108ca0d0ca5b65a7d826d758606`;
  checksum verification and both extracted-tree and archive installed-package
  validation pass under frozen CPython 3.12.14.
- Safely terminated the superseded local ingestion worker while it was waiting
  for the already-diagnosed oversized resource response. That root remains at
  generation 2 with no source bundle or ingestion state advance and no task,
  delivery, audio, Todoist, or scheduler effect.
- Per `START-HERE.md`, do not create the next live root from an unpublished
  runtime. Next: obtain explicit authorization for the configured private
  GitHub push, push and verify the remote exact commit, then create the new
  empty root and Sheet and execute install, bind, cold recovery, ingestion, and
  canonical validation from the already-verified package.

## 2026-09-10 — recovery MVP image-exclusion decision boundary

- After explicit authorization, pushed the pending commits and verified the
  remote recovery branch at exact commit
  `17f164bff12b82521f0eb222e44c534c27a0155d`. The executable package remains
  exact runtime commit `b5a8d461353d0931cc7235ca4227948a779d6035`.
- Created a new isolated root and native one-tab Sheet. The five-file install
  passed with 30 connector calls; post-install Sheet binding passed with 24;
  cold recovery passed with 13 and the installed entrypoint verified. The
  counts remain distinct from unavailable underlying provider operations and
  hidden retries.
- The final installed package began live Gmail ingestion. Complete discovery
  used two searches, 36 message reads, and one complete-thread read before the
  first direct resource. Several exact image resources were fetched and staged
  locally with original-detail extraction, but no source bundle or successor
  state was published.
- The user then requested that images be excluded for this run. The approved
  connected runtime has no per-run image-exclusion selector: images are part of
  the frozen source-custody scenario and are required to remain inventoried,
  byte-verified, and extracted. Adding such a selector or silently converting
  all image outcomes to policy exclusions would change the frozen source-policy
  and configuration contract. Per the instruction not to make architecture
  changes, stopped the local worker safely before Drive publication.
- The root remains at generation 2 with no canonical ingestion, task, delivery,
  audio, Todoist, or scheduler effect. Next requires a user decision: continue
  the approved architecture and process its bounded images, or explicitly
  authorize a revised source-policy/configuration contract, rebuilt package,
  and new empty root for an image-excluded scenario.

## 2026-09-10 — recovery MVP temporary all-image exclusion authorized

- The user selected the revised source-policy option for current MVP
  qualification: completely exclude images now, preserve the implemented image
  pipeline, and defer a selective policy for meaningful images versus
  decorative headers and footers until after the MVP is proven.
- Implemented the exclusion at the connected composition boundary. All MIME
  attachments matching `image/*` and all resources inventoried as
  `html_embedded` receive the existing canonical `excluded_by_policy` outcome
  before any image download or extraction. Their source identity and inventory
  provenance remain visible; no image bytes, semantic segment, or Fact is
  produced. Text and PDF behavior is unchanged, and the image readers,
  validation, MIME/signature, and extractor bindings remain in the package.
- Added focused zero-fetch/zero-extraction coverage for MIME images and embedded
  images plus composer assertions proving the policy is active while image
  extractors remain bound. Focused validation passed 36 tests. The full frozen
  CPython 3.12.14 gate passed 366 tests plus schema/template validation and the
  tracked-file privacy scan.
- Next: publish the exact runtime, rebuild its package, create a new empty root
  and Sheet, then repeat install, binding, cold recovery, live ingestion, and
  canonical validation.

## 2026-09-10 — recovery MVP PDF render timeout isolated

- Published the all-image-exclusion runtime at exact commit
  `bbfebcd5c2dc3a26dcef49e27a969aa766bb0c3c`. Its immutable package passed
  five-file installation, post-install Sheet binding, cold Drive recovery, and
  installed-package validation in a new isolated instance.
- Live ingestion independently interpreted and audited five conversations. The
  active image policy was observed end to end: discovered image attachments and
  HTML-embedded images received visible `excluded_by_policy` outcomes before
  fetch or extraction. No source bundle or successor state was published.
- A later direct PDF fetched with exact complete-byte evidence but failed before
  the image-extraction callback. Private structural diagnosis isolated the one
  failing property: the local `pdftoppm` subprocess exceeded the existing
  10-second timeout. The document passed MIME/signature, completeness, byte,
  encryption, page-count, feature-inventory, page-box, and aggregate-pixel
  checks. With a wider diagnostic bound, the same page rendered and reached the
  callback in about nine seconds.
- Implemented a compatible bounded correction: HTTPS fetch retains its
  10-second deadline while PDF rendering receives a separate 30-second
  per-page deadline, capped at 60 seconds by adapter validation. Focused source,
  import, and hybrid-ingestion validation passes 28 tests. No Drive state,
  task, delivery, audio, Todoist, or scheduler effect occurred; the superseded
  worker was stopped while waiting for the already-fetched response.
- Next: run the complete validation gate, commit and publish the repair, rebuild
  the exact immutable package, create a new empty root and Sheet, repeat install,
  binding, cold recovery, and complete live ingestion through canonical Drive
  publication and independent validation.

## 2026-09-10 — recovery MVP configured attachment bound mismatch isolated

- Published and remotely verified the PDF-render repair at exact commit
  `65e13061f6ed5c3dd3cb05f66a3a32e57ccd7300`; its package passed checksum and
  installed validation. One incorrectly ordered setup attempt placed the Sheet
  inside the root before installation and was abandoned without installation
  writes. No product change was made for that operator error.
- A new correctly ordered root passed the five-file install with 30 connector
  calls. A newly created post-install Sheet then bound as generation 2 with 24
  calls. Cold recovery used 13 calls, and the recovered package validated.
- Live ingestion reproduced the first five independent semantic audits, fetched
  and fully rendered the previously blocked direct PDF, and independently
  audited that sixth conversation. Two more conversations also passed complete
  independent semantic audits, including one explicit no-Fact disposition.
  The run then stopped before the ninth semantic step because a supported MIME
  PDF attachment exceeded the configured per-unit byte bound. No source bundle
  or successor state was published.
- Focused evidence established that the attachment is below the already-
  qualified finite source-host and JSONL response ceilings and below the source-
  bundle capacity. The connected worker applied the configured byte limit to
  attachment admission, but `ConnectedSourceAdapters` independently retained a
  smaller default for exact-byte fetches. Updated composition to pass the same
  configured finite bound to both layers; focused source/import/hybrid tests
  pass 28 tests.
- Next: run the complete validation gate, commit and publish the compatible
  repair, rebuild the package, freeze a private per-unit value within the
  existing qualified ceiling that admits the observed PDF, create a new empty
  root, and repeat install/bind/recovery/live ingestion through canonical Drive
  publication and validation.

## 2026-09-10 — recovery MVP fresh package admitted; attachment envelope mismatch isolated

- The configured source-bound composition repair passed the complete frozen
  CPython 3.12 validation gate: 367 tests plus schema, template, package, and
  privacy validation. Published and remotely verified exact commit
  `70ffaafa7dd1cda53b0d83581e44c0e9e1ed188f`; its immutable archive passed
  checksum, archive, extracted-tree, and installed-package validation.
- A new isolated root passed exact-parent and empty-root proof. The five-file
  hybrid installation completed with 30 connector calls and an exact
  five-object readback. A fresh post-install Sheet bound atomically as
  generation 2 with 24 calls. Cold Drive recovery used 13 calls and its
  recovered package validated.
- Live source discovery repeated the bounded inventory. Standalone and embedded
  email images remained excluded before fetch. The direct PDF passed complete
  byte fetch and page-render transcription, and the prior eight semantic
  expectations were reused only through exact packet-bound helpers.
- The formerly byte-blocked supported Gmail PDF attachment reached the
  attachment connector. The run then stopped before attachment-byte download or
  canonical publication because the connector's flat structured attachment
  object also carried one undeclared nested `structuredContent` property.
  A second read-only diagnostic replay reproduced the same surplus property on
  both attachment responses. No source bundle, successor state, task, delivery,
  audio, Todoist, or scheduler effect occurred.
- Implemented a narrow connector-envelope normalization, not an architecture
  change. It removes the observed redundant wrapper only when its declared
  inner and outer attachment fields agree exactly; conflicting, malformed, and
  otherwise surplus fields remain blocking. Focused bridge/source/ingestion
  validation passed 28 tests. The complete frozen CPython 3.12 gate passed 368
  tests plus schema, template, package, and privacy validation.
- Next: publish the exact repair, rebuild and verify its immutable package, use
  another new empty root as required, and resume the same live ingestion
  journey.
- Published and remotely verified that repair at exact commit
  `98121f1ccc3d4be15f6ef7b9e9e397f51db72917`. Its rebuilt immutable package
  passed checksum and installed validation. A new isolated root then passed the
  30-call five-file installation, exact-object readback, 24-call post-install
  Sheet binding, 13-call cold Drive recovery, and recovered-package validation.
- The exact package's live ingestion repeated bounded discovery, exact message
  reads, image pre-fetch exclusions, and the direct-PDF render. The first Gmail
  attachment read did not reproduce the prior surplus-field rejection; the
  connector instead returned a tool-level error with no usable attachment
  result, which the bridge classified as unknown and blocked. No source bundle,
  successor state, task, delivery, audio, Todoist, or scheduler effect occurred;
  the root remains at generation 2.
- Next: on one bounded diagnostic attachment read, preserve only the private
  raw connector failure and a public-safe status/reason/stage classification.
  Do not infer throttling from the generic error. If the read succeeds, rerun
  the same installed ingestion; if it exposes a reproducible runtime contract
  defect, fix it within the approved architecture and rebuild from a new root.

## 2026-09-10 — recovery MVP attachment diagnostic identified a concrete envelope mismatch

- Reconstructed the exact first eligible non-image attachment target from the
  frozen source scope using read-only paginated discovery, then performed one
  bounded diagnostic attachment read. The connector call succeeded: it returned
  a nonempty PDF file reference and exposed no HTTP status, Google error reason,
  retry delay, timeout classification, or other failure field. The preceding
  generic failure therefore remains transient and unclassified; this evidence
  does not establish rate limiting.
- The successful raw response did expose a reproducible contract mismatch. Its
  declared attachment fields were accompanied by a nested connector payload
  that repeats those fields and adds three connector-private transport fields.
  The current exact-redundancy normalizer intentionally rejects that surplus,
  so the installed package would still stop before attachment-byte download or
  canonical publication. Raw identifiers and the complete connector envelope
  remain mode-0600 under the ignored private recovery evidence tree.
- No Drive, Sheets, task, delivery, audio, Todoist, or scheduler mutation was
  performed. Next: implement a finite Gmail attachment projection that accepts
  the documented declared fields only when the nested and outer declared values
  agree, ignores only the three now-observed connector-private transport fields,
  and continues to reject conflicts or any other surplus. Prove it with focused
  static tests and the complete validation gate before building a new immutable
  package and using a new empty live root.

## 2026-09-10 — recovery MVP attachment projection and connector diagnostics repaired

- Implemented the finite attachment projection against a synthetic equivalent
  of the newly observed connector envelope. The bridge accepts only the ten
  documented attachment fields, requires the nested and outer declared values
  to agree exactly, validates the three connector-only transport fields and
  their file-reference relationship, removes them before ingestion, and still
  rejects incomplete, conflicting, malformed, or newly surplus metadata. The
  exact ignored private live envelope now passes the repaired normalizer without
  copying any private value into Git.
- Preserved the JSONL protocol and unknown-effect safety rule. After any invoked
  connector failure, the host now leaves a request-bound mode-0600 private
  evidence receipt containing the complete raw connector result or invocation
  exception, its hash, operation kind, and correlation token, but no request
  arguments. The child recomputes and exposes only privacy-safe stage,
  response-observed, HTTP status, reason, domain, retry delay, connector code,
  evidence path, and receipt hash. Legacy generic error wrappers remain valid;
  private provider text is verified not to appear in the surfaced exception.
- Focused bridge/bootstrap/source/ingestion validation passes 51 tests. The
  complete frozen CPython 3.12 gate passes 370 tests plus schema, template,
  package, and privacy validation. No provider call or mutation was made while
  implementing or validating these repairs. Next: commit and publish the exact
  code/docs checkpoint, rebuild its immutable package, and use a new empty root
  for the next live end-to-end ingestion run.

## 2026-09-10 — connector evidence discipline made durable for future developers

- Added a clearly developer-only section to `AGENTS.md` requiring complete raw
  private connector capture before runtime fixes, evidence-based failure-stage
  classification, full response-topology inspection, privacy-safe synthetic
  fixtures, exact private-receipt replay before another package/root, and
  automatic raw-error preservation. It explicitly forbids inferring rate limits
  from generic failures or blindly retrying unknown write outcomes.
- The user authorized the next live ingestion as an interim four-local-calendar-
  day inclusive window ending at the exclusive start of tomorrow in the private
  configured timezone. Exact bounds remain private; standalone and embedded
  images remain excluded. This compatibility run does not replace the final
  14-day recovery acceptance case.
- Next: validate and publish this documentation-only continuity checkpoint,
  freeze the exact four-day bounds privately, build the exact package, create a
  new empty root and isolated Sheet, install/bind/recover, then run live
  ingestion through canonical Drive publication and independent validation.

## 2026-09-10 — four-day live run isolated whitespace-only MIME alternative

- Published and remotely verified the developer-continuity checkpoint at exact
  commit `657546a65bae309ac20e33516fb9c1b2a04f8aa3`. Its immutable package passed
  checksum and installed-tree validation. A new exact-parent empty root passed
  the five-file installation in 30 connector calls; a new isolated Sheet bound
  as generation 2 in 24 calls; cold recovery used 13 calls and the recovered
  package validated.
- The four-day Gmail inventory began with images excluded before fetch. The
  first two conversations passed independent semantic interpretation and audit.
  The third conversation stopped before canonical publication because a
  `multipart/mixed` message exposed one substantive plaintext body and a second
  two-byte whitespace-only plaintext leaf around an inline image. The adapter
  preserved both leaves but counted both as body candidates and blocked as
  ambiguous. No source bundle or successor state was published.
- A bounded read-only diagnostic replay preserved the exact successful
  connector response privately and proved that both full and raw views agree on
  the three-leaf topology and that the second plaintext leaf decodes to only
  whitespace. Implemented a narrow MIME repair: retain every exact leaf and its
  custody evidence, select the sole substantive plaintext body when all other
  plaintext bodies are independently full/raw-verified whitespace, and still
  reject multiple substantive or unverifiable alternatives. The exact private
  response now admits with one selected body; focused source/import/bridge/
  ingestion coverage passes 73 tests. The complete frozen CPython 3.12 gate
  passes 371 tests plus schema, template, package, and privacy validation.
- Next: publish the compatible repair, rebuild the immutable package, create the
  required new empty root and Sheet, and repeat install/bind/recovery plus the
  complete four-day ingestion through canonical Drive publication and
  independent validation.

## 2026-09-10 — MIME accounting architecture approved for implementation

- The single GPT-6 Astra consultation confirmed that repeated live MIME failures
  come from conflating one presentation body with complete message content. The
  user approved its detailed bounded remedy and authorized implementation plus a
  new four-day live ingestion. The approved change does not alter hybrid Drive
  storage, canonical state, publication transactions, task semantics, or
  delivery behavior.
- Recorded `mime-accounting-v1` as the active source boundary in the recovery
  plan, Gmail adapter contract, and source-catalog contract. Exact byte custody,
  full/raw reconciliation, identities, provenance, finite bounds, audit, and
  cursor gates remain strict. Deterministic MIME traversal must assign every
  content-bearing node one disposition and preserve every substantive admitted
  text unit; a primary body is only a presentation alias.
- Implementation order is schema/contracts, shared accounting and Gmail
  normalization, catalog custody v2, semantic packet/audit v2, connected
  ingestion/publication equality, focused generated/table tests, complete gate,
  exact package build, then a new empty root/Sheet and the privately frozen
  four-day live run with images excluded. HTML conversion, calendar semantics,
  unsupported opaque-format reconstruction, migration, and any new Drive object
  remain out of scope.
- Next: implement and validate the approved source-contract change before any
  further provider mutation.

## 2026-09-10 — MIME accounting implementation passes static and exact-receipt gates

- Implemented the approved `mime-accounting-v1` boundary without changing the
  five-file Drive layout, checkpoint publication, task model, or delivery
  architecture. The reconciled Gmail tree now records every structural and
  content leaf, preserves every exact plaintext unit and HTML evidence unit,
  selects a primary body only as a deterministic presentation alias, and
  retains padding and same-alternative exact duplicates with explicit
  dispositions. Non-text leaves remain bound to the existing attachment
  outcome pipeline; the temporary image exclusions still occur before fetch.
- Added source schema v3, catalog custody version 2, independently constructed
  source snapshots, semantic packet/result version 2, one-to-one MIME audit
  acknowledgments, and exact raw-message bundle-reference validation. Legacy
  schema/custody readers and synthetic fixtures remain active only for their
  existing compatibility tests; new connected Gmail records use the accounted
  path. No new Drive object, migration, HTML conversion, calendar semantics, or
  generalized workflow was introduced.
- Replayed the previously failing ignored private full/raw connector receipt
  through the new normalizer. It now proves one complete message with three
  leaves and two preserved text units: one `interpret` and one `padding`; no
  private identity or content was copied to Git or logs. Added table-driven
  mixed, alternative, padding, HTML-evidence, nullable-primary, catalog
  round-trip, and semantic-packet tests. The complete suite passes 375 tests.
- Next: commit and push this accepted implementation checkpoint, run the
  committed package/privacy gate, build the exact immutable package, and create
  a new empty live root and isolated Sheet for the four-day ingestion.

## 2026-09-10 — four-day ingestion reaches verified source publication and isolates checkpoint schema defect

- Published and remotely verified the MIME-accounting implementation at exact
  commit `67c5de51055974502610b4c8e59ddaf374ea2190`; its immutable package passed
  installed and privacy validation. One attempted root was correctly rejected
  because the isolated Sheet had been moved into it before installation. That
  root remains isolated test evidence and was not reused. A second empty root
  completed the exact five-file installation in 30 connector calls, after which
  the Sheet was moved, verified, and bound as the selected projection.
- Cold recovery succeeded from Drive. The fixed four-day Gmail inventory found
  eight complete conversations. All eight passed independent semantic review;
  the formerly failing multipart message now preserves one substantive text
  unit, one padding unit, and one policy-excluded inline image without fetching
  the image. The source bundle was created and byte-read back successfully with
  eight exact raw messages, eight catalog records, 19 Facts, no fetched image,
  no attachment bytes, and no direct-resource bytes.
- Canonical state publication then stopped before a successor state write. The
  exact local failure is a checkpoint contract mismatch: hybrid ingestion emits
  the approved typed physical source-bundle reference, while the legacy
  operation-checkpoint schema admitted only an individually stored artifact's
  three-string shape. Updated that schema to admit both exact legacy artifacts
  and exact hybrid source/output bundle references, and added dependency-free
  `oneOf` enforcement plus focused valid/missing-version regression coverage.
  This implements the approved Drive-storage specification; it does not change
  the physical layout or introduce another architecture.
- The already-created source bundle is preserved as failed-run evidence and is
  not retried or adopted by a changed package. Next: pass the complete repository
  gate, commit/push the checkpoint fix, build that exact package, create a new
  empty root and isolated Sheet, and repeat the four-day journey through final
  canonical Drive readback.

## 2026-09-10 — exact four-day source ingestion and fresh recovery pass

- Committed and remotely verified the hybrid-checkpoint compatibility repair at
  exact commit `263b152decb36f0a58537a5bb663e3b46e2c2a4e`. The complete repository
  gate passed 376 tests plus schema, template, release-package, and privacy
  validation. The exact immutable package passed installed-tree validation.
- Created a new isolated empty root and a new isolated one-tab Sheet. The exact
  five-file installation completed in 30 connector calls. Only after admission,
  the Sheet moved under the root and its generation-2 binding completed in 24
  calls. Cold recovery of that bound installation completed in 13 reads.
- The fixed four-day ingestion completed and committed Drive generation 3. Its
  eight discovered conversations match eight complete thread reads and sixteen
  full/raw message reads. Independent semantic review accepted all eight
  records and produced 19 source-linked Facts, including one action Fact. The
  exact source bundle preserves eight raw messages; attachment and direct-
  resource byte counts are zero, and no image/attachment read was issued under
  the temporary image exclusion. Ingestion used 25 Gmail calls and 13 Drive
  calls, including the source-bundle write/readback, successor state write/
  readback, and guarded `CURRENT.json` update/readback.
- A separate post-commit cold recovery selected generation 3 in 13 reads.
  Offline validation resolved every catalog, interpretation, audit, Facts, and
  raw-message member reference against the exact source bundle; the Fact index
  exactly covers the canonical Facts; and operation-state points to the exact
  committed checkpoint. Private receipts live under
  `private/mvp-recovery/artifacts/live-263b152-4d/`.
- This is a passed source-ingestion compatibility gate, not the complete Phase 1
  preview. The checkpoint deliberately remains `running` with `reconcile` as
  remaining work; the eligible source cursor has not advanced, the one action
  Fact has not yet become a canonical task/Sheet row, and no unsent brief has
  been rendered. No email, audio, Todoist, scheduler, or production effect was
  attempted. Next: implement or invoke the existing hybrid task-reconciliation,
  Sheets-projection, render, and cursor-last continuation without changing the
  approved architecture.

## 2026-09-10 — Live Sheet empty-value mismatch isolated and repaired

- Continued the ignored four-day hybrid root from Drive generation 3 through
  source-canonical reconciliation. Static reconstruction revalidated all 19
  Facts and deterministically produced one canonical task, five guidelines, and
  13 rolling updates before any provider write.
- The task reconciler durably published the create intent and its pre-dispatch
  unknown marker. Sheets accepted exactly one guarded row create. Immediate
  verification then failed because the connector omitted the blank trailing
  `Source Due` CellData, which the grid adapter represented as null, while the
  canonical managed projection represents the same unset optional value as an
  empty string. Recovery found the created canonical ID and correctly refused
  to adopt the apparent field conflict; it did not create a duplicate.
- Fixed `GoogleSheetsTaskSync._provider_task` to normalize only an absent/null
  optional source deadline to the canonical empty string. Added a regression
  using a provider-shaped row with the blank cell absent. The focused Sheet
  suite passes 21 tests; complete `scripts/validate.py` passes 377 tests plus
  schema/template/package/privacy validation.
- The affected live root remains private failed-path evidence with an unresolved
  task-create outcome and must not be resumed for acceptance. No email, audio,
  Todoist, or scheduler effect occurred. Because runtime code changed, next:
  commit and push this repair, rebuild the exact package, create a new empty
  root and isolated Sheet, repeat the four-day ingestion, and continue through
  the unsent preview gate before binding Todoist/audio.

## 2026-09-10 — agent-managed two-way task adapter architecture approved

- The user clarified that School-OS must not own Google Sheet layout or native
  maintenance logic. Google Sheets and Todoist remain fully two-way editable
  projections, but the user's instance agent performs complete provider reads,
  native guarded operations, pagination and exact readback through one finite
  normalized interface.
- One bounded GPT-6 Astra xhigh consultation reviewed the current implementation
  at `c375916`. It confirmed that the existing reconciler mixes canonical
  decisions with provider writes, hard-codes Sheet scope in hybrid setup, and
  lacks durable pre-dispatch intent boundaries for ordinary claims, patches and
  reopen operations. It recommended a complete normalized snapshot, one
  committed high-level action, and verified normalized result protocol.
- Recorded the detailed approved boundary and implementation sequence in
  `docs/plans/mvp-recovery/TASK-ADAPTER-SPEC.md`; linked it from the recovery and
  root plans; and aligned the Drive-storage projection-binding section. The
  five-file layout, Drive authority, source/task semantics, images-disabled
  policy and final live acceptance matrix are unchanged.
- Next: implement the finite schemas and pure task state machine, replace active
  hybrid Sheet routing with an agent binding, add the tracked hybrid preview
  continuation, validate and publish the exact package, then execute a new
  private four-day image-excluded live ingestion through `PREVIEW_READY`.

## 2026-09-10 — agent-managed task interface and tracked hybrid preview implemented

- Added strict normalized snapshot, high-level action and result schemas plus
  `school_os.agent_tasks`. Reconciliation now has a provider-free path that
  imports supported parent changes, durably records `needs_review` conflicts,
  emits only finite semantic actions, marks one action unknown before dispatch,
  and advances a binding/cursor only after normalized postconditions pass.
- Replaced the hybrid initial Sheet-specific state/selector with an unbound
  version-2 selector and generic selected provider state. The new post-install
  binding accepts an agent-prepared complete empty snapshot and hash-bound
  opaque adapter configuration; core performs no Sheet setup or layout parsing.
  Hybrid resolution verifies that configuration and exposes only the selected
  semantic binding.
- Added tracked installed entrypoints for agent task binding and the four-step
  preview continuation: plan, authorize, confirm and finish. The finish path
  rereads exact source-bundle custody, renders/stores HTML and text in an output
  bundle, leaves delivery unreserved/unsent, and advances the eligible source
  cursor only in the terminal `PREVIEW_READY` generation.
- Fixed-layout Sheet modules and the legacy connected setup script remain in
  Git as historical tests/reference but are excluded from release payloads.
  Active hybrid imports no longer require them. The Google Sheets and Todoist
  documents now describe user-agent procedures over the shared semantic
  contract rather than native core workers.
- Focused adapter, installation and release-builder validation passes 37 tests;
  the complete unit suite passes 382 tests. No provider call or mutation was
  made in this implementation unit.
- Next: run the complete committed validation/privacy/package gate, publish the
  exact checkpoint, build and validate its immutable package, then create a new
  private root and agent-owned isolated Sheet for the authorized four-day live
  ingestion and preview exchange.

## 2026-09-10 — exact agent-task package published; live install paused at settings consent

- Complete validation passed 383 tests plus schema, template, package and
  privacy checks. Commit `970d9b2e4a7a8cabbf23af31eb79d73c1ea9930d` is
  remotely verified, and its immutable alpha.13 archive and extracted tree
  both pass installed-package validation.
- The execution agent created and verified a new isolated native Sheet with a
  deliberately agent-owned layout. School-OS has no column, range or native
  Sheet logic for that surface; the pending binding will contain only the
  normalized adapter contract plus an opaque private configuration hash.
- A first local install attempt used the host's Python 3.9 and stopped before a
  write because that interpreter lacks `datetime.UTC`. The qualified bundled
  CPython 3.12.14 then began the exact five-file install. Package creation was
  confirmed, but the connector safety layer rejected the settings-file upload
  because it contains private test parameters. The connector exposed no HTTP
  status because this was a local consent rejection, not a Google response.
- The affected Drive root is permanently failed-path evidence and will not be
  reused. Two same-run roots accidentally created while reconciling a flat
  connector receipt were kept empty and quarantined; one may be selected only
  as a fresh empty root after the settings-write consent boundary is resolved.
  No ingestion, task projection write, email, audio, Todoist or scheduler
  effect occurred. Next: obtain explicit authorization for the private
  settings payload at the isolated canonical Drive destination, then resume on
  a verified-empty root with the same exact package and qualified interpreter.

## 2026-09-10 — agent-operated four-day preview completes; two qualification defects repaired

- With explicit authorization for the private settings payload, the exact
  `970d9b2e4a7a8cabbf23af31eb79d73c1ea9930d` package completed its five-file
  installation, generic post-install task binding and Drive cold recovery in a
  new isolated root. The bounded image-excluded ingestion committed eight
  complete source conversations, eight raw-message custody members and 13
  source-linked Facts. Exact source-bundle readback and a second Drive recovery
  validated the catalog, Facts/indexes and unchanged eligible cursor at the
  intermediate `reconcile` boundary; attachment, direct-resource and image
  reads remained zero.
- A complete agent-owned Sheet snapshot produced two canonical task actions.
  Each action was made current as unknown before the native write, translated
  by the instance agent into its private layout, read back exactly and then
  confirmed in Drive with stable semantic identity. The second authorization
  committed successfully but the installed wrapper then collided with the
  first authorization's fixed local state filename. No second provider action
  was attempted: a new private directory cold-recovered the one exact unknown
  action, after which its guarded write and confirmation completed without a
  duplicate.
- The installed finish path stored and reread an immutable HTML/text output
  bundle, advanced the eligible source cursor only in terminal generation 9,
  and returned `PREVIEW_READY`. Delivery remained unreserved and unsent; no
  audio, Todoist, scheduler or production effect occurred. A final cold
  recovery selected the complete operation state.
- Content review also exposed that the private expectation helper could accept
  several legacy zero-Fact notes for one current packet. The canonical semantic
  audit binds its packet hash, but an empty private candidate list had no span
  that bound the independent review decision to that packet. Therefore the
  affected zero-Fact classifications were not sufficient independent
  correctness evidence even though source custody remained exact.
- Added `school_os.semantic_expectations` to require the exact packet hash,
  catalog identity, ordered segment/content hashes and auxiliary-inventory
  hashes before any private expectation can drive a response. Added a
  cross-packet zero-Fact rejection test, text-tamper and unknown-field tests,
  and developer guidance in `AGENTS.md`. Updated the private live helper to use
  this gate.
- Changed the installed preview runtime artifact name to include its committed
  generation while retaining exclusive creation. A focused repeated-authorize
  regression proves two same-named phases in one directory produce distinct
  artifacts and an exact same-generation replay still cannot overwrite.
- Focused semantic/ingestion/task/bootstrap validation passes 59 tests. The
  complete qualified-Python gate passes 387 tests plus schema and template
  validation, and the tracked privacy scan passes. No provider call occurred
  while implementing these repairs.
- Next: commit, push and remotely verify the compatible repair; build and
  validate the exact immutable package; create a new empty authorized root and
  isolated agent-owned Sheet; then repeat the same private four-day,
  image-excluded journey through cold-recovered `PREVIEW_READY` using only
  packet-bound independent expectations.

## 2026-09-10 — fresh packet-bound four-day preview passes both repairs

- Committed and pushed `6eb787e80f01da722f250cc4a7b1c6d9a61c04f6`.
  The focused gate passed 59 tests; the complete qualified CPython 3.12.14 gate
  passed 387 tests plus schema/template validation, privacy scan and diff
  checks. The immutable `0.1.0-alpha.13` package passes extracted-package and
  checksum verification.
- Created a new folder under the authorized test parent, proved its exact
  parent/type/identity and empty child inventory, then installed exactly five
  initial files. Installation used 30 connector calls: five uploads, 12
  metadata reads, ten byte fetches and three scoped listing calls. No connector
  result reported an error. A new native Sheet was created only after
  admission, populated by the instance agent with its private layout, read
  completely and bound as the selected projection in generation 2.
- The unchanged frozen four-day source scope completed nine conversations and
  nine raw-message custody members. Fresh independent review produced nine
  packet-bound expectations and 27 source-linked Facts. The prior and current
  catalogs share eight records with no removals; the two shared records that
  previously used zero-Fact notes now produce six Facts, while one newly
  discovered record produces eight. All nine private expectation packet hashes
  equal the nine accepted audit packet hashes. Attachment, direct-resource and
  image reads were zero. Source publication committed generation 3 without
  advancing the eligible cursor.
- A complete empty Sheet snapshot planned three canonical task creations. Each
  authorization was durably current before its guarded native write; each blank
  target row was written once, read back exactly and confirmed in Drive. The
  same run directory completed three `authorize` phases at generations 5, 7
  and 9, proving the second-authorize filename collision is repaired while
  exclusive same-generation overwrite protection remains tested. No pending
  action or review case remains.
- Finish published and exactly reread one immutable output bundle containing
  nonempty brief input, HTML and text, committed the eligible cursor last, and
  returned terminal generation 11 `PREVIEW_READY`. Delivery state has no
  reservation or effect; no email, audio, Todoist or scheduler call occurred.
  A separate Drive-only cold recovery selected generation 11. Static final
  validation matched all source/member hashes, Fact indexes, private packet
  bindings, three Sheet canonical IDs, three Drive task bindings and output
  member hashes.
- Private receipts and the final sanitized summary are under
  `private/mvp-recovery/artifacts/live-6eb787e-4d/`; connector exchanges are
  under `private/mvp-recovery/runs/live-6eb787e-4d-*`. Next: preserve this
  compatibility gate, then resume the recovery plan's distinct final 14-day
  Todoist switch, two-send, audio, interruption/replay, scheduler-disable and
  fresh-session acceptance chain from a new final root when authorized.

## 2026-09-10 — consolidated final-chain execution authorized

- The user approved an execution sequence that completes static qualification
  and accumulates ordinary compatible fixes before creating the next live test
  environment. A full restart is reserved for changes that invalidate the
  frozen runtime evidence; documentation, tests, planned mutable task/provider
  state and conclusively reconciled transient outcomes do not trigger one.
- Added the exact seven-step sequence and evidence-invalidation rules to the
  recovery plan: static path inventory, consolidated repair, candidate freeze,
  one clean 14-day installation/ingestion, both task lifecycles and guided
  switch, the two authorized delivery/recovery cases, and evidence closure.
  This changes execution ordering only; the approved Drive layout, agent-owned
  task adapters, temporary all-image exclusion and acceptance matrix remain
  unchanged.
- No provider mutation or test email was made in this planning unit. Next:
  inventory the active installed Todoist/switch/delivery/audio/scheduler and
  recovery seams against their contracts and package inventory, run their
  focused tests, and record one bounded repair list before changing runtime
  code.

## 2026-09-10 — final-chain static implementation consolidated

- Added the provider-neutral Drive-generation task continuation and installed
  task sync/switch entrypoints. Complete normalized snapshots import parent
  add/edit/comment/complete/reopen state before projection; each finite action
  is current as unknown before dispatch and advances its base only after exact
  normalized readback. Guided switching stages Todoist while Sheets remains
  selected, activates only after exact target proof, reuses dormant mappings,
  blocks dormant dispatch, and aborts only actions proven undispatched.
- Corrected hybrid ingestion to retain every prior catalog row, Fact and Fact
  index across later bounded batches. Only refreshed record rows are replaced;
  a refresh that would silently remove a prior Fact blocks. The operation now
  persists a finite current-run new/changed source delta, and task imports add
  parent-origin task changes to that same delta without treating system
  projection metadata as parent news.
- Added exact audio-manifest construction from the persisted current delta and
  private explicit voice/tag routing. The existing ElevenLabs worker now
  requires configured account-qualified voices, uses `eleven_v3`, preserves the
  fixed 2,000-character prefix rule, reads its key only from the environment,
  makes one synthesis request, and never substitutes a fallback voice.
- Added the ordered hybrid delivery continuation: render and store HTML/text,
  reserve the delivery, persist current delta and audio intent, record exactly
  one terminal audio outcome, attach only verified MP3 bytes, persist Gmail
  intent/effect checkpoints, send one structured multipart message, verify the
  exact raw Sent MIME, advance the eligible source cursor last, and complete the
  operation. A lost Gmail response recovers from Drive and reconciles the one
  exact Sent match without a second send; failed/unavailable audio remains a
  truthful independent disposition and cannot fabricate attachment success.
- Extended the finite Gmail bridge only for the bounded nested MIME and
  base64url attachment form actually exposed by the connector. The bridge
  rejects unknown MIME fields, excessive nesting, malformed/empty binary data,
  and incomplete attachment metadata. Existing privacy-safe raw connector
  error preservation remains unchanged.
- Fixed two cross-boundary integrity gaps found during static review: the same
  source-bundle hash may not name conflicting physical Drive references, and
  dormant task providers cannot authorize or confirm actions. Added regressions
  for both, for failure-safe switch abort, cumulative ingestion, exact audio,
  ordered delivery and lost-response recovery.
- The final installed wrapper inventory found and repaired one additional
  composition defect before freeze: the task/reconcile wrapper was manual-only,
  so a scheduled delivery could not traverse the same operation checkpoints.
  It now accepts the admitted manual or scheduled profile and requires private
  runtime-serialization evidence for scheduled execution; the provider-neutral
  state machine and delivery semantics are unchanged.
- The final qualified bundled Python gate passes 431 tests plus schema/template
  validation; focused task/delivery gates pass 28 tests and diff checks pass.
  No Drive, Gmail, Sheets, Todoist, ElevenLabs, scheduler, or other live
  provider call occurred in this implementation unit. Next: rerun the complete
  gate with the final guards, inspect the exact release payload, commit/push and
  verify the checkpoint, build/validate its immutable package, then freeze and
  start one new clean 14-day acceptance environment.

## 2026-09-10 — final 14-day instance installed and Sheet bound

- Committed and remotely verified the consolidated final runtime at exact
  source commit `a9a29b7a3cf2b645503c6fec787b4a034b56676a`. Its immutable
  `0.1.0-alpha.13` archive has SHA-256
  `d065cf68abcf67fc29a55f8d58d8515353dc846171f5605c703c65b5d15c6b63`,
  passes extracted-package validation, and runs under CPython 3.12.14 with the
  recorded private dependency fingerprint. The complete repository validator
  passed 431 tests plus schema, template, and privacy checks before freeze.
- Froze the exact private 14-day inclusive-start/exclusive-end bounds in the
  configured timezone, the two approved domains, recipient restriction,
  image-before-fetch exclusion, required audio policy, package, commit, and
  empty-root identity only in ignored mode-0600 evidence. No private value was
  added to Git.
- Two setup roots were quarantined before admission after host-orchestration
  defects: a newly created ID lost connector grounding across orchestration
  cells, and the first large private receipt exceeded a terminal single-line
  transport limit. The exact connector failure was a workspace argument clamp
  reporting missing `fileId`, not a Drive quota response. Replaced the local
  evidence transport with length-bounded raw-mode chunks and proved a 750 KB
  round trip before creating the final root. Neither defect changed product
  code or architecture.
- The final root passed exact empty-parent/type checks and installed the five
  physical objects in 30 connector calls: 12 metadata reads, three scoped
  listings, five uploads, and ten byte fetches. A separate clean local run
  rediscovered the exact five-file inventory, then cold-recovered the installed
  package with seven metadata reads and six byte fetches. Search-index delay was
  handled by one direct read-only folder inventory; it was not used as
  containment evidence.
- The instance agent created one isolated native Sheet from a locally rendered
  and verified workbook, placed it directly under the admitted root, and read
  the complete managed `A1:J200` range. The exact headers were present and all
  provider task cells were empty. Its normalized `agent-task-v1` snapshot and
  private adapter mapping passed the installed schema, and the binder published
  and exactly reread Drive generation 2 with Sheets selected. No source import,
  Todoist project, audio call, email, or scheduler effect has occurred.
- Private package, scenario, connector, recovery, Sheet, and binding evidence is
  under `private/mvp-recovery/artifacts/final-a9a29b7/` and corresponding
  `private/mvp-recovery/runs/final-a9a29b7-*` directories. Next: run the exact
  installed image-excluded 14-day Gmail ingestion, independently bind semantic
  expectations, publish its source/Facts checkpoint, and complete the task plus
  stored-unsent-preview gate before binding Todoist or audio.

## 2026-09-10 — final ingestion false rejection isolated and repaired

- The installed 14-day run reached 57 bounded bridge operations, including the
  required PDF extraction handoff, then stopped before any Drive publication.
  Preserved private terminal evidence identified the exact local rejection:
  semantic packet content did not match MIME accounting. No Google connector
  error, provider write, cursor movement, email, audio, Todoist or scheduler
  effect occurred.
- The defect was in the final packet-integrity comparison, not source custody
  or extraction. Extracted attachment/resource segments were already validated
  exactly against typed source outcomes, but the subsequent MIME-accounting
  check compared body-only MIME identifiers with every packet segment. The
  compatible repair limits that comparison to body, body-supplement and HTML
  evidence while retaining the independent exact check for extracted content.
  A regression proves a MIME-accounted body plus a completely extracted PDF
  passes both validation paths.
- Corrected a separate repository-validator false positive without weakening
  privacy checks. Its credential regex crossed line boundaries and treated an
  `os.environ` key lookup as literal secret material. Horizontal whitespace is
  now required around assignments, only the finite environment-read forms are
  exempted, and hard-coded credential values remain rejected. Regressions cover
  environment reads, control flow and literal secrets.
- Focused MIME/privacy validation passes 16 tests. The complete qualified
  CPython 3.12.14 repository validator passes 434 tests plus schemas, manifests,
  release smoke-build, privacy scan and diff checks. Since executable bytes
  changed, the `a9a29b7` root is diagnostic evidence only. Next: commit, push
  and remotely verify this repair; build and validate its exact immutable
  package; then create one new empty 14-day root and resume the full live chain.

## 2026-09-11 — exact extracted-preview locator failure replayed and repaired

- Published semantic-accounting and privacy-scan repairs at exact source
  commit `84aec1d5a409441deef73234de492b0e9dfd1723`; the remote recovery branch
  was verified at the same commit. Its immutable `0.1.0-alpha.13` package has
  SHA-256
  `4c817f3943782a9a98b280ea7f8214d55d454fa387f03dfa0a0c49c64294df5b`
  and passed installed validation under the privately fingerprinted CPython
  3.12.14 runtime.
- A new exact empty root accepted the five-file hybrid installation in 30
  bridge requests. Separate cold recovery used 13 requests. A new isolated
  native Sheet was created only after admission, read completely, and bound as
  the selected agent-managed projection at Drive generation 2; a second cold
  recovery revalidated that state in 13 requests.
- The installed image-excluded 14-day ingestion completed 71 bounded bridge
  requests and stopped before any source publication with the local sanitized
  error `resource URL is not direct HTTPS`. No source checkpoint, cursor,
  canonical task, delivery, audio, Todoist, or scheduler effect occurred. The
  connector attachment calls themselves succeeded; this is not evidence of a
  Google quota or rate-limit failure.
- The exact private attachment receipts showed that the original file locator
  remained direct HTTPS while an optional, ignored complete-extraction preview
  used a connector-internal `sediment:` locator. The adapter had incorrectly
  applied the original-resource HTTPS rule to that noncanonical preview. It now
  validates only the observed finite preview-reference shape, accepts direct
  HTTPS or the finite internal locator, ignores the preview, and continues to
  fetch and verify the original attachment bytes. Wrong schemes, missing
  authority, fragments, wrong preview MIME, and unknown surplus remain
  blocking.
- Both exact mode-0600 receipts replay through the repaired dispatcher/adapter
  boundary and reach the original-resource fetch. The privacy-safe replay
  summary is
  `private/mvp-recovery/artifacts/final-84aec1d/extraction-locator-replay.json`
  with SHA-256
  `8de28dfdcc1746350a9ef276057598963dce077fb9d28651389bac5330477f8a`.
  Focused source/bridge/ingestion validation passes 55 tests; the complete
  qualified validator passes 434 tests plus schemas, manifests, release smoke,
  privacy, and diff checks.
- This is a compatible connector-boundary repair, not an architecture change.
  Because executable bytes changed, the installed root is retained as
  diagnostic evidence only. Next: commit, push, and remotely verify the repair;
  build and validate its exact immutable package; then create one new empty
  final root and resume the 14-day live ingestion through canonical publication
  and validation.

## 2026-09-11 — MIME-internal CID reference isolated and repaired

- Published the connector-preview repair at exact commit
  `0ecd4e1507f157fab43d410d7785844265c4c983`; the remote recovery branch was
  verified at the same commit. Its immutable `0.1.0-alpha.13` package has
  SHA-256
  `24ebc8b70e3ce40740bf86224fdfff76ddf85db59ed5bcfc56f41d53ab923290`
  and passed installed validation under the privately fingerprinted CPython
  3.12.14 runtime.
- A new exact empty root accepted the five-file installation in 30 bridge
  requests. Cold recovery used 13 requests. A new isolated native Sheet was
  imported, completely read, normalized by the agent-managed adapter and bound
  at Drive generation 2; post-bind cold recovery used another 13 requests. No
  Todoist, audio, email or scheduler effect occurred.
- The first installed 14-day ingestion stopped before publication when the
  read-only content helper wrote an empty PDF-page transcription. The runtime
  correctly rejected it. Drive cold recovery proved the pre-ingestion
  generation remained current. A clean retry used a new local run directory,
  passed the nonempty original-detail PDF handoffs and exact semantic
  interpretation/audit boundaries, then stopped after 92 bridge requests on
  `HTML resource URL is not a direct HTTPS URL`. No source checkpoint, cursor,
  task, delivery or other external effect was published.
- Exact private full/raw diagnosis isolated one and only one failing resource
  scheme: `cid:`. It is a MIME Content-ID reference to bytes already represented
  by the complete raw-message/MIME inventory, not a remote direct-resource URL.
  The importer now recognizes only a finite well-formed CID shape, retains the
  reference in the preserved raw HTML/MIME evidence, and leaves the
  corresponding MIME leaf to the attachment/image policy instead of emitting a
  second fetch target. Empty, authority-bearing or fragmented CID forms still
  block, as do HTTP and other non-HTTPS resource URLs.
- The exact mode-0600 connector pair replays through bridge normalization,
  Gmail full/raw reconciliation and direct-resource discovery with zero
  emitted direct resources. The private replay summary is
  `private/mvp-recovery/artifacts/final-0ecd4e1/cid-html-replay.json` with
  SHA-256
  `1c5d4d37820c5cc573d2963faa3d6e85be290e7696fb93ad0b2f59d20b21c776`.
  Focused Gmail/import/custody/connected/hybrid ingestion validation passes 48
  tests. This is a compatible source-classification repair, not an architecture
  change. Next: complete repository validation, commit/push/verify, build the
  exact package, and create one new empty final root for the 14-day chain.

## 2026-09-11 — valid source-archive readback transport bound repaired

- Published the CID classification repair at exact commit
  `592c76a6a403762ccfcc3259f2a1a7f01456f0ab`; the remote recovery branch was
  verified at the same commit. Its immutable `0.1.0-alpha.13` package has
  SHA-256
  `25af6d3bb9449a3dc6f9e9aeda066ce80b1d16687461a760dd13618cfcb50229`
  and passed installed validation under the qualified CPython 3.12.14 runtime.
- A new empty root passed the five-file installation in 30 bridge requests,
  separate cold recovery in 13, post-admission agent-managed Sheet binding in
  24, and another Drive-only cold recovery in 13. The installed image-excluded
  14-day ingestion completed the bounded Gmail reads, PDF extraction and
  independent interpretation/audit work, then stopped after 265 bridge requests
  before canonical source/state publication.
- The exact failure was local and fully isolated: a verified 16,066,560-byte
  immutable source archive was returned by Drive as 21,424,967 bytes of
  base64-bearing JSON, which exceeded the bridge's 16 MiB ordinary-response
  ceiling. This was not a connector error, quota response, rate-limit signal,
  source-bound violation, or architecture failure. The archive create is a
  noncanonical orphan candidate because the successor state and pointer were
  never published.
- The bridge now keeps the 16 MiB response ceiling for ordinary operations and
  derives a finite `drive.fetch` ceiling from the approved 64 MiB maximum bundle
  size, base64 expansion, and a 16 MiB validated-envelope allowance. Bundle,
  member, ingestion and effect limits are unchanged. The exact preserved
  mode-0600 receipt replays through host normalization, response framing,
  decoded-byte/length validation and child consumption. Its private replay
  summary is under
  `private/mvp-recovery/runs/final-592c76a-large-fetch-replay/`; the summary
  SHA-256 is
  `95f8ce84f325f6ebf49ffca0aec41638cb57e7263c4a4f4614cd2f82e5b0e08d`.
- Focused bridge/bundle/ingestion/source validation passes 75 tests. The complete
  qualified repository validator passes 435 tests plus schemas, manifests,
  release smoke-build, privacy and diff checks. This is a compatible transport
  sizing repair within the approved hybrid architecture. Because executable
  bytes changed, the current root remains diagnostic evidence only. Next:
  commit/push/verify, build and validate the exact package, then create one new
  empty final root and rerun the complete 14-day chain through canonical
  ingestion publication and independent Drive-only recovery.

## 2026-09-11 — 14-day ingestion committed; integrated semantic check found one missed action

- Published the operation-specific Drive fetch-bound repair at exact commit
  `ddd53642766692008fbf38e5f9f3c70a20e602ee`; the remote recovery branch was
  verified at that commit. Its immutable `0.1.0-alpha.13` package has SHA-256
  `9e55709d611c9622f42d01d3d2b192d0fd0c244820a029bda6ba487e71342608`
  and passed installed validation under the qualified CPython 3.12.14 runtime.
- A new empty root passed five-file installation in 30 bridge requests, separate
  cold recovery in 13, post-admission agent-managed Sheet binding in 24, and
  post-bind cold recovery in 13. The isolated Sheet was completely read and had
  no task rows before binding.
- The exact installed image-excluded 14-day ingestion completed in 275 bounded
  bridge requests and committed Drive generation 3: 38 complete source records,
  41 raw messages, one required attachment, one inventoried direct resource and
  43 source-linked Facts. The eligible cursor remained unchanged at the catalog
  boundary. A new 13-request Drive-only recovery admitted the exact package,
  settings, pointer and state bundle. The tracked preview plan then reread the
  complete Sheet and exact source bundle and committed generation 4 with zero
  provider effects. No email, Todoist, audio or scheduler effect occurred.
- Integrated independent content validation rejected the assembled semantic
  result: one of the 43 accepted Facts contains a finite parent response
  requirement but was marked `is_action: false`. The other 42 Facts are
  non-action updates; the standing-policy Fact remains non-actionable. Therefore
  the resulting zero-task state is not acceptance evidence even though every
  packet-level audit had passed. The exact packet-bound private expectation is
  being corrected from source evidence, not from generated output.
- A separate compatible runtime defect was exposed by the same state: a
  genuinely action-free, completely read snapshot remained at `task_sync` and
  the next command would attempt to authorize a nonexistent action. The runtime
  now advances that case directly to `brief_delivery`; pending-action behavior
  is unchanged. Focused transition/task/CLI validation passes 29 tests. Developer
  continuity guidance now requires an integrated independent check of semantic
  flags and an explicit justification for aggregate zero-action results.
- Private receipts and runtime evidence are under
  `private/mvp-recovery/artifacts/final-ddd5364/` and corresponding
  `private/mvp-recovery/runs/final-ddd5364-*` directories. Next: finish the exact
  expectation correction, add the focused semantic replay, run the complete
  repository gate, commit/push/verify, freeze one package, and use one new empty
  final root for the full live chain. The current root remains durable diagnostic
  evidence only once executable bytes change.

## 2026-09-11 — final-package replay exposed unstable Gmail attachment identity

- Published the verified zero-action transition and developer continuity update
  at exact commit `c59d077e6c180ac41490d741c0600137a2d1d25d`; the remote recovery
  branch was verified at that commit. Its immutable `0.1.0-alpha.13` package has
  SHA-256
  `f6a944c58cfb64fa516b06e18879864c5b0ca6efe3693dce5240a561ba880568`
  and passed installed validation under the qualified CPython 3.12.14 runtime.
- A new empty root passed the five-file installation in 30 bridge requests,
  separate cold recovery in 13, post-admission agent-managed Sheet binding in
  24, and another Drive-only cold recovery in 13. Interrupted ingestion attempts
  did not publish canonical source state; a subsequent cold recovery still
  admitted generation 2. No task, email, Todoist, audio or scheduler effect
  occurred.
- Static exact-packet replay now reuses earlier semantic work only when the
  frozen packet hash and paired independent audit hash match. Prior PDF evidence
  was recovered into exact one-page and eight-page boundaries, and image MIME
  ingestion remained excluded.
- The next clean live replay reproduced a stable-identity failure before
  publication: one PDF retained the same Gmail source message and exact original
  bytes but its provider attachment ID differed from the prior accepted run.
  The current catalog content ID, Fact provenance and duplicate-replay behavior
  depend on that field, so bytes-only adoption would weaken the explicit source
  identity requirement. The complete private receipt and hashes are in
  `private/mvp-recovery/runs/final-c59d077-ingestion-r5/attachment-identity-mismatch-summary.json`
  with the surrounding mode-0600 raw receipts in the same run directory.
- This is an identity-contract question, not a rate-limit, transcription or
  Drive-storage failure. Under the instruction not to make architecture changes,
  the ingestion path is paused. Next decision: approve a stable attachment
  identity derived from the immutable Gmail message plus canonical MIME-part
  coordinates while retaining the provider attachment ID as a current-read
  locator, or record the connector behavior as a blocking incapability.

## 2026-09-11 — temporary body-only source policy implemented locally

- The user deferred all attachment support, extending the prior image-only
  exclusion to every MIME attachment and directly referenced HTML image/PDF.
  The focused authority is
  `docs/plans/mvp-recovery/ATTACHMENT-DEFERRAL-PLAN.md`. This work unit is
  explicitly local-only: no release package, fresh installation, test root, or
  live provider call is authorized before a separate user approval.
- The active connected composers now select explicit body-only Gmail
  normalization, a global `*/*` attachment exclusion, and both finite direct
  resource-origin exclusions. The Gmail source adapter blocks attachment reads
  before its provider method, no direct-resource fetcher is bound, and no
  attachment or direct-resource extractor is bound on the active path. Existing
  attachment/PDF/image/resource code remains available and its prior focused
  tests remain active as dormant-path coverage.
- Policy-excluded attachment identity is derived from the exact source message
  and normalized MIME-part coordinate. The connector attachment ID is neither
  required nor persisted in body-only normalized output. Exact raw RFC2822
  custody and complete MIME accounting remain mandatory, so the system neither
  invents attachment content nor treats ignored bytes as body Facts.
- A new global MIME exclusion regression proves text, PDF, image, and an unseen
  MIME type all stop before the read callback. Direct embedded-image and linked-
  PDF regressions prove zero fetch/extractor calls. A normalizer/catalog replay
  proves two otherwise identical Gmail reads with different transient attachment
  locators produce identical body-only normalized and catalog bytes.
- The ignored exact private receipt set was replayed locally through the new
  normalizer. One observed distinct-locator pair produced identical body-only
  output; the mode-0600 result is retained beside the prior private mismatch
  evidence. Focused source/ingestion validation passes 58 tests. The complete
  local unit suite passes 442 tests. Local schemas, template manifests, privacy
  scan, and diff checks pass. No release archive was produced or admitted, and
  no School-OS connector was invoked. Next: report for explicit approval before
  any release build or fresh live installation.

## 2026-09-11 — body-only three-message qualification stopped before ingestion

- The exact source commit `98dd7437b79924baad448c84d7f067235f247dbc`
  was clean, pushed, and verified on the remote recovery branch before the
  package build. The local attachment-identity replay remained stable across a
  changed transient Gmail locator; 68 focused tests plus schema, manifest,
  privacy, diff, installed-package, composition, and entrypoint checks passed.
  The single requested complete-suite invocation produced its test progress but
  its terminal summary was not retained, so this run does not claim a fresh
  complete-suite pass.
- Exactly one `0.1.0-alpha.13` package was built from that commit with SHA-256
  `c2a3c3be507fa4cf61c4a6c48d271185aa56ec55e0bd0e12f352157a2e611f02`.
  Exactly three existing authorized singleton-thread inbound messages were
  frozen, including body-only coverage for one MIME attachment and 27 direct
  HTML resources. No input or delivery email was sent.
- Exactly one new empty Drive root received one five-file installation in 30
  bridge requests and passed a separate 13-request cold recovery. Because the
  admitted ingestion runtime requires a task projection, exactly one empty
  native Sheet was created, scoped, read back, and bound through the existing
  agent-managed adapter contract. The successful binding published generation
  2 in 24 bridge requests; no task lifecycle or Todoist operation occurred.
- Before the one authorized ingestion began, a repository-wide diagnostic used
  to locate the private expectation schema printed private frozen source-body
  material to visible terminal output. This violates the qualification's
  privacy boundary. The journey was stopped immediately: ingestion did not
  start, canonical source state was not published, and attachment/resource
  reads, extraction, task, delivery, audio, Todoist, and scheduler effects all
  remained zero. This is an operator-evidence-handling failure, not a product or
  provider failure.
- Privacy-safe stop evidence is under
  the timestamped stopped body-only three-message directory under
  `private/mvp-recovery/runs/`; the one immutable
  package and validation evidence remain under
  `private/mvp-recovery/artifacts/body-only-3msg-98dd743/`. All files in both
  trees were rechecked at mode 0600 and all directories at mode 0700. This root
  and installation are retained as stopped diagnostic evidence and must not be
  represented as a passing body-only qualification. A separately authorized
  clean journey is required to qualify ingestion.

## 2026-09-11 — restart principles and managed-agent architecture simulation

- The user retired the previous implementation as a restart foundation and
  explicitly authorized the new source-retention and operating choices.
  `PLAN.md` now routes current work to `docs/plans/restart/PLAN.md`; prior
  qualification plans remain historical evidence rather than implementation
  requirements for the restart.
- Updated `docs/product-principles.md`: raw material stays at its source and is
  downloaded only for temporary processing; Drive holds substantive knowledge,
  accurate source/part references, configuration and operating state. Stable
  source-account identity is independent of a replaceable connector. Core
  operation must work in managed/cloud agent applications without a dedicated
  personal machine or coding CLI.
- Added the known tools/adapters/connections/jobs/runs register and a core query
  use case for any capable reader to list known schedules and identify a brief's
  producer/sender. The register distinguishes desired settings from observed
  external status and preserves per-job bindings and historical attribution.
  Users may use any number of agents/jobs. Concurrent updates to the same Drive
  data are explicitly outside scope; no coordination subsystem was added.
- `docs/plans/restart/SIMULATION.md` records the opinion, architecture, primary
  agent-documentation constraints, detailed identity rules, every product
  priority/use-case mapping, failures found and remaining live tests. The
  development-only executable model in its `simulation/` directory passes
  96 assertions across 60 retained state snapshots: 15 fictional source
  records, 21 consolidated facts, four canonical actions, three jobs and two
  modeled outputs. All historical/daily gaps close only after explicitly
  assumed alternative reading/restoration events.
- The modeled journey covers historical pagination/rescan, separate daily
  coverage, missed invocation, interruption, temporary cleanup, source readback
  mismatch, replacement agents/connectors, thread replies, inline corrections,
  quoted history, identical filenames, repeated bytes, changing retrieval
  handles, account-qualified message IDs, parent completion, pending effects,
  known-job queries and output attribution. It does not call real connectors
  or implement real MIME/PDF/image parsing, natural-language query grading,
  task-app synchronization, audio generation, installation or upgrades.
- Independent review repaired lost provenance, weak query/parent-state checks,
  premature completion, old deadline replay and inaccurate job input bindings.
  A separate fresh-agent interpretation of the synthetic text found a semantic
  omission in the expected catalog: term-wide handbook qualifications and page
  references. These and the reminder's immediate instruction are now retained.
  The separate interpretation and its limits are preserved; scenario hints
  in the source fixture mean it was only partly blinded. No vendor-app benchmark
  or general semantic-quality pass is claimed.
- The state-model run, local documentation links and diff checks pass. The
  existing full repository validator passes 442 tests with Python 3.12.14,
  plus schema, manifest and existing release-smoke validation. An initial run
  used the system Python 3.9.6 and failed on unsupported language/library
  features; that was an environment mismatch, not a runtime repair. The privacy
  scan also flagged an old diagnostic run-directory basename as ID-like; the
  public historical log now names its parent directory and purpose instead.
  New fictional artifacts are separately privacy-scanned before publication.
- No private mailbox/Drive instance was accessed, no live scheduler or delivery
  effect occurred, and no runtime or published release was changed. Next work:
  qualify a small source/attachment read and Drive write round trip in the
  actual managed agent apps, then an unattended schedule and a fresh different
  agent's recovery/query. Keep physical Drive layout and blanket compatibility
  claims provisional until those observations exist.

## 2026-09-11 — message identity evidence and independence from provider metadata

- The user requested a bounded live Gmail identity check, deep cross-agent and
  harness research, and an identification design that works without provider
  message IDs. During the work, the user explicitly added a product principle:
  critical paths and recovery must not depend on API/provider-specific
  parameters or connector metadata. `docs/product-principles.md` now makes
  that a distinct design priority and requires source-information-based
  identity/acceptance decisions, with technical handles confined to access.
- The read-only sub-agent probe lasted 121.7 seconds: seven selected messages,
  two bounded thread windows, six replies, 63 full observations and seven
  metadata observations. Native message/thread IDs, RFC reply/identity headers,
  and independent header/text witnesses stayed stable. All 15 populated
  attachment-locator slots changed; 40 MIME coordinates stayed stable. No
  attachment bytes were downloaded or compared. The 46 connector calls were
  reads with no reported errors or mutations. Private request/raw/topology
  receipts remain under the admitted ignored message-identity-probe run
  directory, with files 0600 and directory 0700. Only aggregates are published.
- `docs/plans/restart/identity/REPORT.md` documents the probe, provider/protocol
  contracts, the five named product families, Copilot, Composio, Pipedream,
  n8n, Zapier, LangChain, SDKs and representative MCP implementations. Native
  Gmail IDs are documented immutable; Graph default IDs can change; RFC IDs
  can be missing/reused; identically named fields differ between connectors.
  Unknown closed-connector contracts are not mislabeled as observed changes.
  This is a representative primary-source survey, not certification of every
  marketplace integration or future version.
- The current design assigns School-OS-owned source/attachment record IDs.
  It reasons from original subject, actual receipt time, sender, To/Cc roles,
  attachment names and relevant content/context. Source dates retain their
  meaning, timezone and precision; sender date and observation time cannot
  substitute for receipt time. These are combined evidence, not a universally
  unique or always-present tuple. External handles and RFC IDs may accelerate
  retrieval but cannot decide identity or acceptance. Ambiguous occurrences
  remain explicit, and unrelated work can continue.
- The focused synthetic experiment passes 38 cases, including removal of all
  provider/RFC IDs from both stored and incoming observations, specific replies,
  reused citations, changed IDs, unknown content, To/Cc roles, timezone
  presentation and duplicate attachments/copies. Every case also erases all
  external ID fields and requires an unchanged matching decision. Independent
  review exposed an early alias-authority shortcut; the final matcher has no
  alias-based identity path. It stores content digests, not raw bodies.
- The experiment is a decision model, not an installed matcher or a vendor
  benchmark. Its precise normalized fields and completeness claims are fixture
  assumptions; it does not prove live normalization, indexed search, a durable
  unresolved-work queue or physical-occurrence identity when evidence is
  indistinguishable. The original 96-assertion lifecycle model is prominently
  marked historical and superseded on its provider-derived source key.
- Focused experiment, source-note/local-link checks, schema/manifest checks,
  privacy scan and diff checks are the appropriate validation for this
  research/documentation change. No existing runtime, private Drive instance,
  scheduler, delivery or release was modified. The prior 442-test runtime pass
  is historical; no new full-runtime qualification is claimed here. Next:
  qualify the source-information recipe on one synthetic thread in two actual
  managed agent apps, including a fresh session with saved external IDs removed.

## 2026-09-11 — raw-MIME identity evaluation exposes recipe failures

- The user asked whether the new recipe had actually been simulated for
  determinism, false positives/negatives, threads, attachments and HTML images.
  The earlier 38 prepared cases did not cover that boundary. The new
  `docs/plans/restart/identity/mime-evaluation/README.md` records a completed
  diagnostic evaluation, explicitly not a robustness or production pass.
- A separate agent authored 54 fictional MIME observations and delivery truth
  without reading the matcher. The generator recreates real synthetic PDF/PNG
  bytes and ignored raw email files; the manifest binds every file's hash.
  The evaluator parses those files into the unchanged old flat witness, with
  truth labels excluded from observation extraction and matching. No private
  mailbox, Drive, source attachment or live connector was accessed.
- Across 1,431 pairs tested in both directions, 292 same-delivery comparisons
  yielded 62 content associations, 73 false splits and 157 abstentions. The
  2,566 distinct-delivery comparisons yielded 2,172 distinctions, 392
  abstentions and two wrong associations: opposite directions of one pair
  with identical MIME child bytes but different selected HTML roots. Four
  indistinguishable-delivery comparisons remained association-only, with no
  physical-occurrence proof. The 98 targeted comparisons are reported
  separately; these correlated synthetic comparisons are not real-world rates.
- Tested distinctions include replies and quoted context, changed PDF/image
  bytes, repeated filenames, attachment multiplicity and image placement.
  Failed matching cases include HTML/plain views, changed CID presentation,
  data-URI embedding, reordered attachment presentation and rounded receipt
  time. Missing CID/remote resource coverage remains explicit. PDF semantics,
  OCR, complex HTML resources and scoped duplicate CIDs were not graded.
- Three fresh-process runs with different hash seeds and zoned environments
  produced equal reports; JSON reload and all 2,862 external-ID mutation checks
  preserved decisions. Three ingestion orders produced equal content groups
  and seven pending items, but retained the identity mistakes. Reversed
  catalog order changed candidate serialization, not candidate sets/statuses.
  Separate boundary checks reproduced display-name and coarse-time false
  splits, an unhandled malformed date, and a timezone-less timestamp that
  matches in UTC but splits in Los Angeles.
- Independent review verified counts, targeted cases, projection boundaries,
  direction asymmetry and the report's limits. Requirements now call for
  compatible observation comparisons, preserved MIME/content relationships,
  explicit unknown date semantics, scoped unresolved work and processing
  coverage separate from identity. These are proposed refinements; the old
  executable matcher is unchanged so its failures remain reproducible.
- The generator reproduced identical fixture bytes; focused evaluation and
  fresh-process checks completed. The unchanged 38-case experiment still
  passes its limited assertions. Schema/manifest validation, local document
  links, privacy scanning of tracked and new files, and diff checks pass.
  No legacy runtime, installed instance, scheduler, delivery or release was
  modified, and no new full-runtime qualification is claimed.
- Next: refine the comparison/coverage contract against the frozen corpus,
  then evaluate an untouched challenge set. Only then qualify the same
  synthetic journey in two managed agent apps, with a fresh-session recovery
  and external IDs removed. Live enumeration, extraction quality, Drive
  checkpoints, runtime capacity and downstream task deduplication remain open.

## 2026-09-11 — metadata-only identity and individual-message thread handling

- The user explicitly rejected content inspection as an identity dependency and
  requested an updated recipe using subject, senders, sending time, filenames
  and related source metadata, with an explanation of thread handling.
  `docs/product-principles.md` and the new
  `docs/plans/restart/identity/METADATA-RECIPE.md` now make that boundary explicit.
  Bodies, quotes, HTML, MIME content structure, images, attachment bytes,
  summaries and content fingerprints cannot decide identity or break a tie.
- School-OS assigns and persists its own record IDs. Matching uses the logical
  mailbox, original subject, actual sender address, sending timestamp, separately
  understood receipt timestamp, To/Cc and comparable original attachment names.
  Unknown fields and date precision remain explicit; generated filenames and
  incompatible inline/attachment inventories do not become required evidence.
  One supported candidate permits a metadata association. Visible collisions
  stay unresolved; indistinguishable metadata can still hide a false association.
- Every reply is an individual message with its own metadata, record and
  processing coverage. Daily scans expand individual message metadata in returned
  threads, including previously seen threads. There is no permanently processed
  thread flag. Optional subject/participant grouping is inferred navigation;
  it cannot deduplicate messages or prove exact reply parentage. Thread-only
  summaries leave individual-message cataloging incomplete.
- Content is still read to extract substantive school information and manage
  its processing coverage, independently of identity. No source archive, new
  runtime dependency or concurrent-write mechanism was introduced. The earlier
  content-assisted proposal and MIME repair recommendations are marked
  superseded; their original executable experiments remain unchanged as evidence.
- This work updates design documents only. No new matcher or simulation pass,
  private source access, installed-instance change, schedule, delivery or release
  is claimed. Next: implement explicit metadata-only decision/acceptance rules,
  evaluate collisions, partial dates and replies, then qualify actual managed
  agent message-metadata access and daily discovery. Independent review found
  no material contradiction with the requested boundary. Document links, staged
  privacy scanning and diff checks passed; repository continuity applies to
  publication of this documentation-only change.

## 2026-09-13 — live metadata stress test exposes collision and filename limits

- The user requested stressing the metadata-only design with their own emails.
  A collecting sub-agent made 127 read-only Gmail calls: 632 separately
  addressable entries, 871 search observations and 109 individual metadata
  observations covering 92 entries plus 17 independent repeat reads. Complete
  receipts were preserved before normalization in the gitignored private
  `private/mvp-recovery/runs/metadata-stress-2026-09-13/` directory with mode-0700
  directories and mode-0600 files. No source values are published.
- Added the development-only model, evaluator, independent fictional checks,
  aggregate results, protocol and findings under
  `docs/plans/restart/identity/metadata-stress/`. Identity and grouping inspect
  no bodies, HTML, MIME content structure, images, attachment bytes or content
  fingerprints. Provider snapshot references support private test construction,
  pairing and grading only; they never enter matcher evidence or saved records.
  This is consistency with observed Gmail entries, not independent proof of
  physical delivery identity or identifier permanence.
- One pair shared all available permitted comparison fields, including the
  same second-resolution source Date. Both records present caused abstention;
  a singleton catalog incorrectly associated the other entry. Holdout, negative
  pair, daily ingestion and JSON restart failures all reproduce this one pair.
  The 46-historical/46-daily replay persisted 91 records, then repeated the same
  mistake after reload. A targeted replay across nine previously seen threads
  correctly retained 19 later entries separately; the same pair still collided.
- Of 101 entries exposing named attachments, 42 contained repeated nonempty
  filenames with distinct exposed retrieval candidates. Physical-file equality
  was not established. Of 36 entries exposing inline names, six had blank names
  and one had repeated nonempty names. These are filename-selection limits, not
  complete HTML/image processing tests. Live inventories have unverified original
  and complete scope and are excluded from automatic identity comparison.
- Private evidence exposed `from_` versus declared `from`, flattened address
  presentation in search sender/recipient lists, explicit empty recipient groups
  and two outer-whitespace subject differences. Small observation handlers and
  fictional regression cases fix the observed address presentation; subject
  differences remain explicit. Search timestamp semantics cannot be inferred
  because source Date and internal timestamp coincide in every compared sample.
  Under the conservative policy all 189 search/header-catalog trials abstain.
- Independent review passed after narrowing the one-pair statement to unmodified
  live-metadata trials; 92 injected hidden occurrences separately reproduce the
  information limit. All 38 fictional policy checks pass with two reproduced
  limitations reported separately. Catalog order, JSON round trip and irrelevant
  external-ID changes preserve decisions. Fresh-process Python 3.9.6/3.12.14 runs
  with different timezones/hash seeds reproduce saved evaluation and checks;
  all code and private dataset SHA-256 bindings verify.
- Current recipe and plans now link the findings and require addressing visible
  source-candidate multiplicity before sequential reuse can erase it. No content
  fallback, provider-ID authority, source archive or concurrent-write mechanism
  was introduced. No installed runtime, private Drive instance, schedule, task,
  email or release was changed. The older content/MIME experiments are unchanged.
- Next: agree acceptable uncertainty for indistinguishable occurrences, qualify
  attachment candidate selection, then test individual-message discovery and
  Drive-backed daily/restart work in actual managed agent apps. This local study
  qualifies neither complete mailbox discovery nor cross-agent production use.
  Privacy scanning of tracked and new public files, local document links, private
  permission/ignore checks and diff validation pass. Publish only the accepted
  public files through the existing recovery branch; verify its remote revision
  before handoff.

## 2026-09-14 — approved logical-email plan and corrected evidence interpretation

- The user approved the point-by-point corrections and requested updating the
  plan and summarizing its artifacts. Reconciled `docs/product-principles.md`,
  root `PLAN.md`, `docs/plans/restart/PLAN.md` and the metadata recipe. School-OS
  reuses logical-email records on sufficiently supported normalized metadata
  agreement without contradictory evidence. A different provider handle alone
  neither proves a different logical email nor requires another canonical record.
  The residual indistinguishability risk remains explicit; no content or provider
  identity fallback is introduced and existing catalog records are not silently
  destructively merged.
- Corrected the live-study report and protocol throughout. The original
  `wrong_association` scoring uses distinct Gmail entries as its reference; the
  observed 92-entry/91-record replay did not establish distinct logical-email or
  school-information loss. All unmodified-live mismatches concern the same pair.
  Repeated filenames were within parent emails and may include representations
  of one file; timestamp changes were not observed. Thread grouping disagreements
  do not determine ingestion correctness. The earlier progress entry preserves
  its original interpretation and is superseded by this correction.
- The current recipe now specifies address presentation/domain normalization,
  preserved local-part spelling and recipient roles, decoded/unfolded subjects
  with outer whitespace trimmed, each individual message/reply's original Date,
  and parent-email-plus-original-filename attachment candidate groups. Source
  association, content processing and attachment coverage remain separate.
- Added durable enumeration choices: bounded windows, all available continuation
  pages even after short pages, completed/unfinished windows and scope on Drive,
  and replay of an unfinished window when a pagination token is unavailable.
  Incomplete or silently capped listing routes cannot claim complete coverage.
- Added `docs/plans/restart/README.md` as the current artifact guide, with reading
  order, authority, evidence and limitations. Marked `docs/architecture.md` as
  retired implementation reference; updated the older lifecycle simulation and
  identity research entry points to direct readers to the current plan/recipe.
- The work plan proceeds through one small revised development model, a bounded
  managed-agent/Drive historical-to-daily slice, interruption recovery, registered
  daily scheduling and a fresh session in a second managed agent. Exact Drive
  layout is chosen from the pilot, with measured operational cost. Any number
  of agents/jobs remains allowed; concurrent same-data writes and a dedicated
  personal CLI remain outside the target architecture.
- Original executable experiments, JSON results, private data and code/data
  bindings remain unchanged. The frozen metadata evaluator does not implement
  every newly approved rule, including subject trimming and durable-window
  recovery. No new live source read, private-instance write, runtime change,
  migration, schedule, delivery or release occurred.
- Validation: independent consistency review, document links, tracked/new-file
  privacy scan and diff checks pass. All 25 tracked experiment Python/JSON files
  are unchanged, and saved model/evaluator SHA-256 bindings still match. Commit
  only the accepted documentation and verify the published recovery branch
  revision. Next implementation action is the small revised model and
  meaningful logical-email tests recorded in the restart plan; it is not started
  by this documentation update.

## 2026-09-14 — architecture approval and user-directed testing handoff

- The user made the product principles document the source of truth and grounding
  for decisions not explicitly covered by an approved plan or specification.
  Updated its decision authority and the repository entry point accordingly.
  Every new or changed architecture decision now requires explicit user approval
  before adoption or implementation, including compatible architectural additions.
  Prior explicit approvals remain valid; routine nonarchitectural implementation
  may proceed within approved scope. Principles compliance alone is not approval.
- Added `docs/plans/restart/ASTRA-HANDOFF.md` with the full copyable prompt for a
  fresh Astra High coordinator session in this directory. It carries the current
  design/evidence, bounded delegation and the same approval limits for all agents.
  The unresolved Drive layout must be proposed and approved before implementation;
  a pilot cannot select a new architecture autonomously.
- Updated the root plan, restart plan, artifact guide and metadata recipe to end
  the next implementation phase after the agreed new project code and continuity
  documents are committed, pushed and the remote revision verified. The agent
  must stop and check in; the user personally manages and oversees testing.
  No tests, simulations, replay experiments, probes, pilots, ingestion or schedules
  may start without the user's subsequent direction. Test code and fictional
  fixtures may be prepared without execution. Older automatic transitions into
  model evaluation or managed-agent qualification are superseded.
- Publication hygiene is distinct from functional testing: diff, privacy,
  document-link, Git status and remote-revision checks remain required. The
  implementation handoff must explicitly report untested code, known risks,
  pending approvals and a proposed testing sequence for the user to direct.
  Check publication hooks/CI before publishing new code; do not trigger tests
  indirectly or silently disable checks to bypass this boundary.
- This work changes documentation only. No new implementation session, product
  code, executable experiment, private source read, live operation or test run
  was started. The frozen experiments and their saved results remain unchanged.
  Next: give the saved prompt to the fresh coordinator; resolve any new
  architecture choices explicitly, implement the agreed code, publish and stop
  before user-directed testing.
- Documentation checks: independent consistency review, tracked/new-file privacy,
  local document links and diff checks pass. Publish only these eight documents
  through the current recovery branch and verify its remote revision; no new
  restart branch or baseline tag is created by this prompt update.

## 2026-09-14 — clarify whole-project scope beyond email identity

- The user challenged the impression that only email identity had been defined.
  Inspection confirms that the product principles, restart design and historical
  lifecycle simulation cover setup, ingestion, knowledge, tasks, queries, briefs,
  tools/schedules, recovery, agent replacement, extensions and upgrades at
  differing levels of detail. Identity has the most detailed recently revised
  procedure; that does not define the boundary of the project.
- The prior handoff's "agreed initial project-code scope" was too vague and its
  implementation checklist overemphasized the email model. Added an explicit
  whole-project delivery checklist to the restart plan and full lifecycle scope
  to the Astra prompt. Updated root routing, the artifact guide and identity
  recipe so completion of an isolated model cannot be reported as completion of
  the restart. Every principle/use case must map to design, deliverables, pending
  approvals and implementation status; any proposed reduction must be explicit.
- This consolidates existing requirements without approving new architecture.
  Exact Drive layout, schemas, adapter contracts and other unresolved choices
  still require explicit user approval before implementation. Historical model
  mechanisms are not an approved production specification. Implementation and
  actual managed-agent qualification remain separate, and the user retains
  control of all test execution after the required publication handoff.
- Independent read-only review found the corrected scope consistent with the
  existing principles and approval/testing boundaries. Only documentation was
  changed; no runtime, experiment, source access, live operation or functional
  test was performed. Next: the fresh coordinator reconciles the complete
  checklist, obtains missing architectural approvals, implements the agreed
  project, publishes it and stops for user-directed testing.
- Publication checks: tracked-file privacy, local document links and diff checks
  pass for the six changed documents. Commit and publish only this documentation
  correction on the existing recovery branch, then verify the remote revision.

## 2026-09-14 — restart coordinator preparation and architecture checkpoint

- Resumed in the existing repository directory. Inspected `START-HERE.md`,
  `AGENTS.md`, product principles, current/root plans, latest progress, the
  current metadata recipe, corrected live-study README/protocol, lifecycle
  simulation, actual branch/tree/history and publication hooks/CI. The tree was
  clean at `39d752c364a1cf404e5a6fc5739148b7d35a6b35` on
  `codex/mvp-recovery`, matching its remote-tracking revision.
- Created dedicated branch `codex/restart-school-os` and annotated baseline tag
  `restart-baseline-2026-09-14` at that exact commit before any legacy cleanup.
  The old runtime remains physically present and explicitly retired as the new
  foundation; no production replacement or private-instance migration is claimed.
- Used three bounded workers for read-only scope review, read-only legacy and
  publication review, and fictional scenario preparation. The coordinator owns
  integration and all Git mutations. Workers share the architecture-approval and
  no-testing boundaries. The scope reviewer subsequently prepared only a new,
  isolated development model of the current metadata procedure.
- Added `docs/plans/restart/implementation/COVERAGE.md`, mapping all nine design
  priorities, seven core use cases, other mandatory principle sections and ten
  whole-project delivery areas to existing design, deliverables and approval
  dependencies. No required project area is removed or silently deferred.
- Added `ARCHITECTURE-PROPOSAL.md` in that directory, revision 2 after independent
  document review. D1–D8 recommend physical Drive layout, records/write recovery,
  execution/adapters, precise ingestion/coverage, knowledge/tasks, outputs/effects,
  tools/schedules and packaged upgrades. Each includes alternatives, tradeoffs
  and unknowns. All eight remain **pending explicit user approval**. The user
  was asked to approve all or selected decisions, or request revisions; no
  dependent production architecture has been adopted or implemented.
- Document review made lost-first-write discovery, pending verification during
  partial updates, UTC-month routing, replay progress limits, recurring required
  actions, developer-only raw receipt custody and the future nonempty CI entry
  point explicit in the proposal. Private receipt and packet-expectation hashes
  remain developer evidence, never canonical source identity. This review is
  not a functional test or qualification result.
- Prepared `implementation/TESTING-PROPOSAL.md` and
  `implementation/fixtures/scenarios.json`: 12 wholly fictional source cards and
  29 scenarios spanning the complete lifecycle, with independent logical and
  semantic expectations. They are scenario data, not canonical schemas or
  adapter contracts. Proposed testing stages remain for the user to direct.
- Prepared `identity/revised-model/README.md`, `model.py` and `test_model.py`
  under the restart plan. The standalone in-memory examples cover normalized
  logical-email reuse, contradictory evidence, individual replies, attachment
  groups with separate read coverage and abstract window continuation/replay.
  Independent fictional story labels expose residual indistinguishability.
  Its exact-zoned-Date fixture domain is explicitly limited and does not adopt
  D4's production threshold. No Drive storage, full-catalog recovery, installed
  adapter or production schema is implemented by this development model.
  Code and checks are authored only; no execution or passing result is claimed.
- Identified retired instruction conflicts: raw-source archival, MIME/content
  identity, immutable generation machinery, exact provider-reference dependence,
  conditional-write coordination and automatic validation/pilot sequencing.
  Preserved applicable privacy and continuity safeguards, frozen studies and
  original results. Root README now marks its implementation claims historical.
- Publication inspection found no configured custom hooks and only inactive
  samples. The tracked workflow tests pull requests, pushes to `main` and manual
  dispatch. Its validator also builds/verifies packages. None is run. A read-only
  remote check found no open PR for the restart branch and no repository
  rulesets. The intended branch/tag were absent remotely before publication.
  Publish the preparation only to this dedicated branch and preservation tag;
  do not create a PR, dispatch CI or silently disable checks.
- This is an architecture/preparation checkpoint, **not the whole-project code
  handoff**. Production T1–T10 work remains pending. Exact next action: obtain
  the user's explicit D1–D8 decisions, record them in the active plan, implement
  all approved deliverables and prepare their tests, then commit/push/verify the
  whole implementation and stop for the user's subsequent testing direction.
  No tests, simulations, model replays, smoke runs, package builds, connector
  probes, ingestion, scheduled jobs, deliveries or managed-agent pilots have
  been executed in this session.
- Publication hygiene for this preparation: tracked-file privacy scan has zero
  findings; all 87 local file-link targets in the nine changed/new Markdown
  documents exist; staged diff whitespace checks pass. Frozen study/model/result
  trees and the CI workflow have no changes from the baseline. Hooks remain
  unconfigured apart from inactive samples. These are publication checks only,
  not functional validation. Commit the twelve in-scope files, push this branch
  and the baseline tag, and verify both remote targets before reporting the
  preparation checkpoint published.

## 2026-09-14 — Sol-authored architecture decision guide

- The user requested a Sol agent to prepare an HTML walkthrough of the
  architecture proposal, optimized for reading ease and cognitive processing.
  Delegated one bounded artifact to GPT-5.6 Sol; the coordinator retained
  integration, continuity and Git control in the same repository/branch.
- Added `docs/plans/restart/implementation/architecture-guide.html`, a standalone
  document with inline styling, no external assets or JavaScript, a short
  orientation, approved/pending distinction, system flow, plain-language D1–D8
  summaries, expandable approval scope/tradeoffs/unknowns, an explicitly fictional
  parent walkthrough, decision recap and source links. It includes responsive
  layout and print styling, without claiming rendered-layout verification.
- Linked the guide from the active restart plan and artifact guide. The written
  architecture proposal revision 2 remains authoritative; all D1–D8 approvals
  remain pending. The guide records no approval, introduces no architectural
  decision and does not start production implementation or testing.
- Source-text review corrected the distinction between provider access aids and
  content extraction, kept the example's informational fact separate from its
  actionable request, and simplified visible decision wording. Publication
  hygiene is limited to privacy, document links, diff and Git/remote checks.
  No tests, simulations, model replays, builds, probes or live operations run.
- Exact next action remains the user's explicit architectural decisions, recorded
  in the active plan before dependent code. Publish this guide on the existing
  restart branch and verify the remote revision; keep the later whole-project
  implementation/publication/testing stop unchanged.
- Publication hygiene: privacy scan has no findings; all 33 HTML links and
  source-section anchors resolve, including the two new guide links from the
  plan/README. Diff checks pass. No browser rendering or functional verification
  was performed. Hooks remain inactive samples and CI triggers are unchanged.


## 2026-09-14 — D1 physical Drive layout approved

- The user explicitly replied "D1 approved" after clarification that the design
  uses multiple JSON pages, with a default 64 KiB limit per encoded JSON page
  and at most 100 entries per directory page. More pages can be added; these
  limits do not cap total instance history. Practical Drive capacity and access
  cost remain unqualified.
- Recorded approval of revision 2 D1 in full in the active restart plan and
  proposal ledger. Updated the root plan, restart artifact guide, coverage map
  and HTML guide to distinguish approved D1 from pending D2–D8. D1 includes the
  bootstrap, system/instance/extensions areas, page headers/routing, durable
  directory continuations, bounded access and lossless long-text segmentation.
- D1 does not approve record meanings, write recovery, adapter contracts or any
  other D2–D8 mechanism. Production implementation remains pending their relevant
  dependencies. Frozen studies and the retired runtime are unchanged.
- Exact next action: obtain explicit decisions on D2–D8, record them, and
  implement the complete approved T1–T10 scope. The later whole-project
  commit/push/remote-verification checkpoint and mandatory stop before testing
  remain unchanged. No tests, simulations, replays, probes or live School-OS
  operations were executed. Publication hygiene only is permitted for this update.
- Publish the approval record on the existing restart branch and refresh the
  existing private architecture guide. This documentation checkpoint is not
  the completed whole-project implementation handoff.
- Publication hygiene found no privacy issues; all 100 local links and section
  anchors in the changed current documents resolve, and diff whitespace checks
  pass. Hooks remain inactive samples; CI triggers are unchanged and the restart
  branch has no open PR. These checks do not establish functional validation.

## 2026-09-14 — Query coverage and incomplete answers approved

- During D2 review, the user explicitly said "Okay, make it so" after the
  recommendation to check processing coverage alongside verified knowledge and
  either complete missing processing within authorized scope or answer with the
  limitation. Recorded this specific approval in the active plan. It does not
  approve the rest of D2 or D3–D8; D1 remains approved unchanged.
- Architecture proposal revision 3 adds the approved query-coverage rule and
  cross-references it from query behavior. Completed writes do not establish
  discovery/content completeness. Unread material cannot be assumed irrelevant;
  neither an empty result nor an unfinished coverage lookup supports exhaustive
  lists, counts or absence claims. Coverage inspection and processing stay
  bounded, and a useful source-linked answer may disclose the remaining gap.
- Corrected the conversational implication that every user question would clear
  the pending-work backlog. The accepted rule applies to answering with known
  coverage; exact daily/import/resume recovery triggers and ordering remain
  separate pending operation-recipe choices.
- Updated root/restart continuity, coverage mapping and the HTML guide. One
  bounded worker owned only the prepared testing proposal and fictional fixture
  inventory: S30 covers a hidden unread email with tomorrow's required action;
  S31 covers incomplete bounded coverage lookup without inventing hidden gaps.
  The inventory now has 13 source cards and 31 scenarios. The coordinator owns
  integration, publication and the existing private guide.
- No tests, simulations, model replays, builds, probes, ingestion, schedules or
  live School-OS effects were executed. Fictional cases are authored only;
  production code and remaining architecture dependencies are still pending.
- Exact next action: obtain explicit decisions for remaining D2 and D3–D8,
  implement all approved T1–T10 deliverables, publish/verify the complete new
  project, and stop for the user's testing direction. This approval/document
  publication is not the completed whole-project implementation handoff.
- Publication hygiene: privacy scan found no issues; all 112 local document
  links/section anchors resolve and diff whitespace checks pass. Hooks remain
  inactive samples, CI triggers are unchanged, and the restart branch has no
  open PR. Frozen evidence and the retired implementation have no changes in
  this unit. These checks are publication hygiene, not functional validation.

## 2026-09-14 — D2 deferred; interrupted-write recovery outside MVP

- The user decided to skip D2 for now and exclude interrupted-write recovery
  from the MVP. Recorded this explicit scope reduction in the active plan and
  architecture proposal revision 4. The D2 write-intent discovery, partial-write
  repair, reconciliation and automatic resumption mechanism is deferred, not an
  MVP implementation or acceptance requirement. Preserve its proposal and
  prepared fictional cases for later work.
- This decision supersedes the initial whole-project recovery requirement for
  this feature. Product principles remain unchanged as the broader direction;
  the MVP exception is explicit in the entry point, coordinator handoff, root
  and restart plans, coverage map and HTML guide. Original T2/T8 coverage cannot
  be reported fully delivered without naming the deferral.
- D1, the approved query-coverage rule, normal verified persistence, source
  custody, honest incomplete coverage, bounded discovery/window continuation and
  fresh-agent access to saved knowledge remain in scope. D6 external effects
  and D8 upgrades remain separate pending decisions; their D2 intent dependencies
  must be reviewed rather than silently reinstating deferred recovery.
- D2 also bundled schemas, UUID representation and locator structure. Skipping
  its review leaves those undecided; it does not approve an alternative write
  design or remove canonical knowledge/tasks/configuration/register requirements.
  No replacement persistence architecture has been adopted or implemented.
- Exact next action: review D3, followed by D4–D8. Present the minimum record and
  ordinary-write design separately before dependent coding. Implement the
  approved MVP scope, publish/verify its complete code and continuity, then stop
  for the user's testing direction. This documentation checkpoint is not the
  completed implementation handoff.
- No tests, simulations, replays, builds, probes, ingestion, scheduled jobs or
  live School-OS effects were run. Only publication hygiene is permitted for
  this update; frozen studies and retired code remain unchanged.
- One bounded worker updated only the testing proposal and fictional scenario
  inventory. S13 and S12's interrupted-write branch are marked post-MVP/deferred;
  their original stimuli and expectations remain intact. The proposed MVP test
  sequence excludes those branches, preserves normal verification and S30–S31,
  and keeps D6 effects/D8 upgrades subject to their separate architecture review.
- Publication hygiene: no privacy findings; all 119 local document links and
  section anchors resolve; diff whitespace checks pass. Hooks remain inactive
  samples, CI triggers are unchanged, and the restart branch has no open PR.
  These are publication checks only, not functional validation.

## 2026-09-14 — D3 code-execution capability required

- The user explicitly decided that a School-OS agent must be able to execute
  code and reports confirming that capability with all major personal-agent
  suppliers. Recorded this as an approved capability requirement, with the
  supplier availability attributed to the user. No independent runtime/adapter
  qualification or capability probe is claimed.
- Architecture proposal revision 5 supersedes the earlier requirement to support
  agents without code execution. Language/version, dependencies, SDKs, code entry
  points and exact adapter contracts remain undecided; this is not approval of
  all D3. Code execution does not imply a personal computer, persistent process,
  coding CLI, or that every operation must execute code. Product principles
  remain unchanged; the requirement is compatible with their managed/cloud and
  capability-led direction.
- Updated the entry point, active/root plans, next-coordinator handoff, coverage
  map and guide. D1 and the query-coverage rule remain approved. D2 interrupted
  canonical-write recovery remains outside MVP and its record structures remain
  undecided. No production runtime or dependency was adopted by this update.
- One bounded worker updated only the testing proposal and fictional inventory:
  S01/S22 assume code-capable agents; S02 adds one absent-code branch. Counts
  remain 13 fictional source cards and 31 prepared scenarios. D4 expectations
  and frozen studies are unchanged; no case was executed.
- The user requested a clearer D4 explanation after recording D3. The HTML
  guide now separates its unchanged proposal into metadata sufficiency, search
  windows, work/transfer limits and reading repeated appearances/attachments.
  D4 is not approved or qualified by this explanatory change.
- Exact next action: explain/review D4, then D5–D8; resolve remaining D3 and the
  minimum record/ordinary-write design before dependent code. The agreed MVP
  implementation/publication checkpoint and mandatory stop before testing remain
  unchanged. No tests, simulations, model replays, builds, connector probes,
  ingestion, schedules or live School-OS operations ran.
- Publication hygiene: no privacy findings; all 119 local document links and
  section anchors resolve; diff whitespace checks pass. Hooks remain inactive
  samples, CI triggers are unchanged, and the restart branch has no open PR.
  These checks provide no functional validation or product qualification.

## 2026-09-15 — Expanded architecture decision walkthroughs

- The user requested a clearer D4 explanation, especially whether bounded work
  can end a run before its daily task is complete, and equivalent detail for all
  remaining decisions. Added seven linked Markdown/HTML briefs under
  `docs/plans/restart/implementation/decision-briefs/`, with fictional emails,
  step-by-step flows, parent-visible results, alternatives and open choices.
  Updated the existing viewable architecture guide to lead with these briefs.
- The D4 example distinguishes an execution from the daily task: a completely
  enumerated pass of 40 admitted appearances with 25 read leaves 15 known unread.
  These are not necessarily 40 logical emails, and incomplete discovery may hide
  more work. Per-run/transfer ceilings do not cap total history or guarantee
  throughput. An unread correction illustrates why a partial answer is limited.
- Recorded missing D4/D6/D7 decisions: continuation trigger/owner, total catch-up
  budget, freshness target, escalation and brief timing. D6 also exposes pending
  email/audio order and effect-record persistence after D2's exclusion; D8 exposes
  its interruption boundary. These are unapproved choices, not adopted policy.
  Revision 6 adds this review context without changing existing approvals.
- Remaining D3 and the minimum record/ordinary-write dependency have separate
  briefs. D1, approved query coverage and required code capability stay approved;
  D2 interrupted canonical-write repair stays outside MVP. No production runtime,
  schema, dependency, schedule or recovery mechanism was implemented by this work.
- Three bounded workers owned separate explanatory Markdown files. The
  coordinator reviewed and integrated all content, authored the additional
  foundation briefs and HTML presentation, and owns repository/Site publication.
- Publication hygiene found no privacy issues; 268 local document links/anchors
  resolve and diff whitespace checks pass. Hooks remain inactive samples. CI
  still runs on main pushes, pull requests or manual dispatch; this restart branch
  has no open PR. No CI settings or checks were disabled. Frozen studies and the
  retired runtime remain unchanged. These checks are not functional validation.
- No tests, simulations, replays, application builds, connector probes, ingestion,
  schedules or live School-OS operations ran. Fictional examples are written
  illustrations only. Publishing the static review artifact is not application
  qualification or the completed whole-project implementation checkpoint.
- Exact next action: review the expanded D4 brief and its open completion policy
  with the user, then resolve D5–D8, remaining D3 and minimum record/ordinary-write
  dependencies explicitly before dependent coding. After agreed MVP implementation,
  commit/push, verify the exact remote revision and stop for the user's testing
  direction. This documentation publication preserves that mandatory stop.

## 2026-09-15 — Agent-managed execution and a smaller MVP

- Recorded the user's explicit D5 approval and revised D4/D6 directions in the
  active approval ledger and architecture proposal revision 7. D4 withdraws the
  proposed School-OS 25-processing/100-listing/8 MiB caps and batch manager. One
  logical run must complete its intended ingestion; the capable executing agent
  owns resource-aware batches, continuation and its runtime recovery using the
  authored guidance. D1's bounded data pages remain approved.
- D6 now assigns uncertain-effect validation to the executing agent through its
  available authorized means. Verify complete intended ingestion before composing
  the ordinary daily brief; blocked ingestion is incomplete work, not a finished
  partial daily result. Separate coverage-qualified knowledge questions remain
  supported. No generic School-OS persisted-effect or D2 repair engine is selected.
- The user explicitly deferred D7 centralized tools/jobs/capability management,
  scheduler control and registry-backed queries, and D8 package/installer/upgrade/
  compatibility/migration machinery. Users and agents manage their own jobs under
  nonconcurrent-instance assumptions. D1 system/instance/extensions separation
  remains for future lifecycle work; minimum first-use setup remains unresolved.
  Repository history/baseline, frozen evidence and privacy safeguards are retained.
- These are explicit MVP exceptions to the original whole-product assignment and
  broader product principles. The principles were not rewritten. Updated root/
  restart plans, entry point, coordinator handoff, coverage mapping, decision
  briefs and the viewable guide to prevent deferred features returning as hidden
  prerequisites. D5's approved behavior is not being resubmitted for approval.
- Authored `implementation/AGENT-EXECUTION-GUIDANCE.md`: practical resource advice,
  complete-ingestion obligation, evidence-led agent verification and clear limits
  without an orchestration engine. Three bounded workers updated separate briefs
  and coverage/testing artifacts; the coordinator owns integration and publication.
- Prepared inventory now includes 13 fictional source cards and 33 scenarios.
  S32 describes one logical run beyond former caps without executing or generating
  a large workload; S33 describes a blocked ingestion preventing normal briefing.
  Existing IDs/stimuli remain with explicit current/deferred scope annotations.
  No tests, simulations, replays, builds, probes, ingestion, schedules or live
  School-OS actions were executed. The small development model and frozen studies
  remain unchanged. Static guide preparation provides no functional evidence.
- Asked for explicit approval of a finite daily boundary: all relevant mail not
  yet fully processed by School-OS through run start, including backlog/attachments
  even if the mailbox marks it read, with later arrivals in the next run. No answer
  is recorded yet; it remains a proposal. Remaining D4 identity/discovery details,
  D6 selection/task-app-freshness/audio choices, D3 and minimum record/normal-write/
  first-use contracts remain to resolve. Agent validation does not require inventing
  a central evidence table, retry service or notification subsystem.
- Exact next action: resolve those remaining retained-MVP choices, implement only
  approved scope, prepare unexecuted checks, commit/push the agreed code and
  continuity, verify the exact remote revision, and stop for the user's testing
  direction. This decision/documentation publication is not the code handoff.
- Publication hygiene: no privacy findings and all 282 local document links and
  anchors resolve. Diff whitespace checks pass after correcting Markdown hard
  breaks. Hooks are inactive samples, CI triggers are unchanged and the restart
  branch has no open PR. No checks were disabled and these inspections provide
  no functional validation or qualification.

## 2026-09-15 — Minimal Python helpers; separate save framework deferred

- Recorded the user's explicit D3 direction: start with minimal useful Python
  standard-library routines, name actual scripts in the recipes, and leave all
  remaining work to the executing agent and its authorized tools. No Python
  version pin, external dependency, SDK, persistent service or fixed provider
  set is selected. Specific new architecture still requires explicit approval.
- The user excluded the open records/ordinary-save framework dependency from
  MVP. Removed that blanket approval prerequisite throughout the current plan,
  coverage map, briefs, fixtures and guide. Preserve canonical Drive data, D1/D5
  meanings, normal agent save verification, coverage and cleanup. Do not replace
  the excluded framework with another schema registry, writer or repair engine.
- Authored three isolated pure functions in `helpers/source_metadata.py`:
  `normalize_subject`, `normalize_address_parts` and `utf8_size`. Subject input
  must explicitly distinguish raw headers from already-decoded values; static
  review identified and corrected a possible double-decoding ambiguity. Address
  parts must already be reliably extracted. The helper guide states supported
  input limits and agent/tool alternatives without changing canonical meaning.
- Prepared ten fictional check methods in
  `helpers/prepared_checks/check_source_metadata.py`, without importing or
  executing them or the new helper. These support later user-directed testing;
  they are not evidence of correctness or portability. The existing fictional
  inventory remains 13 source cards and 33 scenarios with scope annotations.
- Focused workers owned helper authoring, two decision briefs and traceability
  updates; a separate bounded static review inspected the helper text. The
  coordinator integrated their work and owns all Git/artifact publication.
  Frozen studies, retired runtime and the committed preservation tag are intact.
  The current identity recipe's old run-budget wording now follows the approved
  agent-managed complete-run direction; identity evidence rules are unchanged.
- Updated the viewable guide to revision 8 and all seven companion pages. The
  helper subset is authored, not installed or tested. It does not complete the
  retained whole-project deliverables. D2 repair, the separate record/save
  framework, D7 central management and D8 packaged lifecycle remain excluded.
- Publication hygiene found no privacy issues, 315 local document links/anchors
  resolve and diff whitespace checks pass. Hooks are inactive samples; CI only
  starts on main pushes, pull requests or manual dispatch, and this restart
  branch has no open PR. No checks were disabled. These are publication checks,
  not functional validation. Static guide authoring/packaging is separate from
  School-OS application execution.
- No tests, simulations, model replays, imports/compilation of new helpers,
  application builds, smoke runs, connector probes, pilots, ingestion, scheduled
  jobs or live School-OS effects ran. No revised-architecture qualification claim
  is made.
- Exact next action: obtain the still-pending D4 finite daily scope/cutoff and
  identity/discovery decisions and D6 selection/task-app freshness/audio choices,
  while continuing independent approved recipe work. The unanswered cutoff
  question remains pending; this D3 approval does not answer it. Implement all
  retained agreed deliverables, prepare unexecuted checks, publish code and
  continuity to `codex/restart-school-os`, verify the exact remote revision,
  then stop for the user's testing direction. This helper/documentation update
  is an intermediate publication, not the completed whole-project handoff.

## 2026-09-15 — Architecture in practice: diagrams and seven walkthroughs

- The user requested a new page on the existing architecture website explaining
  the layers/components and everyday use cases in plain language. Authored
  `docs/plans/restart/implementation/architecture-in-practice.html` with a layered
  diagram, Drive layout, discovery/content/persistence coverage diagram, task
  synchronization flow, audio flow and two-agent shared-Drive diagram. Linked it
  from the existing overview and restart/brief indexes.
- Seven fictional walkthroughs cover first setup, a fact question, task-app
  parent edits, daily email ingestion, vaccination-form completion evidence,
  optional audio and a fresh Gemini Spark manual email brief after GPT Work.
  Actor names are illustrative, with actual authorization/capabilities assumed;
  the page does not claim provider support or a finished/qualified product.
- Explained mailbox read status versus School-OS processing coverage; each reply
  and attachment candidate's independent coverage; metadata-only identity;
  normal save verification; temporary-copy cleanup; bounded pages without a
  whole-history cap; synchronization timing; and fresh-agent use of Drive rather
  than prior chat. The ordinary daily brief still requires complete ingestion.
- The task-app parent-completion path is approved D5 and is not resubmitted.
  The walkthrough exposes two narrower unresolved policies in the active plan:
  when email evidence may automatically close a task, and whether an explicitly
  requested manual brief may be sent with disclosed coverage gaps. Each has a
  concrete recommendation, alternative, tradeoffs and remaining unknowns. Neither
  is adopted; no sent-mail scope, monitoring service or new task state machine
  is introduced. Removed stale wording in the D5 explanation that implied the
  excluded records framework remained an approval prerequisite.
- Two workers performed focused read-only source review and a third reviewed
  the completed page for design accuracy. The coordinator owns the authored
  page, integration, continuity, Git and private Site publication. Existing
  frozen studies, scenarios, helper/runtime code and product principles were
  unchanged. Page diagrams are explanatory HTML/CSS, not simulations.
- Publication hygiene: privacy and local document-link checks found no issues;
  diff whitespace checks pass. Applicable hooks/CI are inspected before push;
  no checks are disabled and no PR or workflow is created. Static document
  authoring and packaging do not execute the School-OS application. No browser
  testing, functional tests, model replays, helper imports, builds, connector
  probes, ingestion, scheduling, task updates, email sends or audio generation
  were performed. This is documentation publication, not qualification.
- Exact next action: review the page's pending D4/D6 and task-completion/manual-
  brief policy choices with the user, keep specific architecture decisions
  unadopted until explicitly approved, and continue independent approved work.
  The full agreed MVP must still be committed/pushed with its remote revision
  verified before the mandatory stop for user-directed testing. This explanatory
  page is not the completed whole-project implementation checkpoint.

## 2026-09-15 — Setup, shared adapters, parent confirmation and brief recipes

- Recorded three explicit user decisions in the active restart plan and product
  principles: setup interviews offer known tools available to the current agent;
  one shared semantic adapter per tool can be created when missing and reused
  by other agents through their own connectors; clear task-fulfillment evidence
  becomes Completion detected — awaiting parent confirmation, represented by a
  supported status or section until the parent checks it complete; and the daily
  brief is a starter template among any number of user/agent-created recipes.
- The user accepted newly verified/corrected information, original dates,
  relevant open tasks and failed task-sync disclosure as the daily starter's
  selection. This is not a fixed selection rule for all briefs. Custom weekly
  and event recipes can retrieve still-relevant older information. The ordinary
  daily complete-ingestion gate, coverage accuracy and source/task meaning remain.
- Authored reusable instructions under `operations/`: setup interview, shared
  adapter selection/authoring, an API-agnostic adapter writing template,
  completion review and brief recipes. Connector access/authentication/API/SDK
  and transport mechanics stay separate from shared School-OS tool semantics.
  No vendor-specific adapter or actual connector compatibility is claimed.
- Expanded `architecture-in-practice.html` with shared adapter/connector diagrams,
  D1 routing and bounded page details, an explicitly illustrative JSON reading
  sketch, and step-by-step reads/interpretation/saves for the seven scenarios.
  Added brief-recipe selection examples and replaced the proposed automatic
  closure with the approved parent-confirmation flow. Clarified the still-pending
  manual limited-brief exception with a saved museum notice and unread newsletter.
- Updated the overview, D3/D5/D6 source briefs and their static companion pages,
  whole-project coverage, entry points and handoff. A focused static review
  caught a stale task-sync choice and an over-restrictive weekly example; both
  were corrected. The explanation does not approve a canonical field schema,
  new registry, selection engine, scheduler, recovery framework or installer.
- Prepared 15 written fictional operation review cases with a proposed sequence.
  The frozen studies, the prior 13-source/33-scenario inventory, retired runtime,
  helpers and their unexecuted checks are preserved. These instructions/cases are
  an intermediate delivered subset; the entire retained MVP is not implemented.
- No tests, simulations, model replays, helper imports/compilation, application
  builds, smoke runs, source/task/mail/audio probes, ingestion, schedules or
  live School-OS effects ran. Static document authoring and publication hygiene
  do not establish functional validation or revised-architecture qualification.
- Exact next action: publish this accepted instruction/documentation subset to
  `codex/restart-school-os`, verify its remote revision and update the existing
  architecture website. Then continue only independent approved implementation
  while resolving D4 daily scope/identity/discovery choices and D6 audio/manual
  limited-brief policy. Once the whole agreed MVP is published and verified,
  stop for the user's testing direction; this is not that final testing handoff.
- Publication hygiene: no privacy findings; all 311 local document links/anchors
  resolve; diff whitespace checks pass. Applicable Git hooks are inactive
  samples. CI is unchanged and runs on main pushes, pull requests or manual
  dispatch; this restart branch has no open pull request. No checks were disabled.

- Publication completed: instruction/guide commit
  `087c061507731bac997624936dc6610ef0674f19` was pushed and the exact remote
  restart revision verified. The existing owner-private architecture website
  was updated successfully with nine static pages referencing that source.
  Website publication hygiene found 141 local links/anchors resolving and no
  privacy findings. No browser test or deployed-page fetch was performed.
- Next action is now the remaining architecture choices and independent approved
  implementation stated above; publication of this subset is no longer pending.
  Testing remains stopped, and no whole-project completion claim is made.


## 2026-09-15 — Consolidated remaining architecture questions

- At the user's request, reconciled the open website choices against the active
  approval ledger, product principles, retained whole-project scope and recent
  discussion of missing schemas and historical-query indexing.
- Added `implementation/OPEN-QUESTIONS.md` and one nine-item numbered section in
  the main HTML guide. The practical walkthrough links to that section instead
  of keeping a second incomplete list. Each question explains the recommendation,
  example, alternatives, tradeoffs, served principles/use cases and limits.
- Q1 concrete retained fields/links, Q2 topic/entity lookup conventions and Q6
  exact content-read reuse evidence still need detailed proposals before final
  approval. Q3–Q5 and Q7–Q9 have recommendations. No new architecture is adopted.
  The broad D2 record/save framework remains outside MVP; D1/D5 and other prior
  approvals are not reopened. Household source/tool/recipe choices remain in
  the approved interview and request flow.
- Read-only worker review caught two gaps: Q6 had been labeled ready despite
  its missing deciding rule, and Q4 understated the full-range fallback's cost.
  Corrected both: Q6 explicitly remains proposal work; proposed full-range
  enumeration occurs every daily run and can require repeated body/attachment
  reads depending on the reuse rule. Its efficiency is not qualified.
- Fixed stale active-plan wording about starter selection: the user's later
  approval already selects newly verified/corrected information and failed-sync
  disclosure for the starter, with arbitrary compatible household recipes.
- No product code, frozen studies or prepared checks changed. No tests,
  simulations, replays, builds, browser tests, connector probes or live School-OS
  operations ran. Only static authoring, review and publication hygiene apply.
- Exact next action: publish this review and verify its remote revision and Site
  deployment, then supply Q1/Q2/Q6 proposals and resolve the remaining questions
  before dependent implementation. Continue independent approved work. The next
  phase is completing the agreed MVP; testing remains reserved for the user's
  subsequent direction after the whole agreed implementation is published.
- Publication hygiene passed: zero privacy findings, 187 local document links
  and anchors resolve, and the diff has no whitespace errors. Both repositories
  have only inactive sample hooks. The restart branch has no open pull request;
  existing CI applies to main pushes, pull requests or manual dispatch. The
  Site is static and owner-private. No checks were disabled or tests triggered.

- Publication completed: review commit
  `fbfc16d568fdc9879496e23dc7ec4491470c16e4` was pushed to
  `codex/restart-school-os` and the exact remote revision verified. Site source
  `a4fc2da7542e0f525984644deea5b9e1e6222080` was pushed, packaged as static
  content and published as version 11. Deployment status reports success at
  https://school-os-architecture-guide.jeremieg.chatgpt.site/#open-questions.
  Existing owner-private access was preserved. Site publication hygiene found
  144 local links/anchors resolving and zero privacy findings; no browser or
  functional test was performed.
- Publication of this review is complete. Exact next action: supply the concrete
  Q1/Q2/Q6 proposals and resolve the remaining numbered choices before dependent
  implementation. No approval, feature completion or testing authority is
  inferred from this documentation publication.


## 2026-09-15 — Numbered decisions and concrete data architecture proposal

- Recorded the user's Q3 run-start scope and Q5 known-timezone, second-or-finer
  original-Date approvals. Q6 now exposes fully-ingested/not-ingested for the
  whole logical email; partial-email/PDF resumption is outside MVP, while bodies,
  required attachments, honest evidence and discovery coverage remain required.
- Q7 now permits a limited manual brief after explaining outdated-knowledge risk,
  available source/ingestion freshness, and offering new ingestion first. Q8
  rejects a canonical audio archive; temporary audio is discarded after verified
  delivery. Q9 selects configured audio with email, or email alone with an audio-
  failure notice. Updated actual brief/execution instructions, current plans,
  principle amendments, metadata recipe, D4/D6 briefs and website scenarios.
- Q4's full-history-every-day fallback was not accepted. The replacement proposal
  uses live arrival-time discovery windows, unfinished windows and backlog,
  accepting the explicit older-delayed-visibility limitation. It is unapproved.
  Q6's binary outcome is approved; the narrow rule for skipping a later supported
  metadata match remains explicitly proposed, not silently adopted.
- Authored DATA-ARCHITECTURE-PROPOSAL.md and a viewable data-architecture.html page
  for Q1/Q2: child/family/school applicability, dated memberships, distinct
  knowledge/action meanings, one task per independent obligation, parent-created
  tasks, source/coverage/configuration/sync fields, owned references, concrete
  linked JSON and bounded entity/topic/incoming-correction indexes. The source
  includes ingestion and retrieval traces and explicit alternatives/tradeoffs.
  No schema, ID, catalogue or index contract is adopted by publication.
- Bounded workers drafted the proposed contract, updated two approved-operation
  files and reviewed the data architecture. Integration addressed listed-child
  lookup, historical membership, topic-classification omissions, task-index
  dependencies, parent-created tasks, later corrections, long-lived rules and
  late-reported observations. Catalogue reads avoid default body downloads, but
  completeness costs can grow with history; no performance is qualified.
- Prepared six additional written Q1/Q2 cases pending architecture approval and
  amended stale manual/audio expectations. Frozen studies and retired runtime
  remain untouched. No tests, simulations, model replays, builds, helper runs,
  connector probes, ingestion, sends, audio generation or scheduled jobs ran.
- Exact next action: publish the proposal and updated decision/instruction
  documents, verify remote revision and Site success, then obtain Q1/Q2 and
  narrow Q4/Q6 decisions before dependent coding. Continue independent approved
  work. The full MVP is still incomplete; its final verified publication must
  stop for the user's separate testing direction.
- Publication hygiene: zero privacy findings, 315 local document links/anchors
  resolve, and diff whitespace checks pass. Both checkouts have inactive sample
  hooks only; CI remains limited to main pushes, pull requests or manual dispatch.
  This restart branch has no open pull request. No checks were disabled and no
  testing will be triggered by this documentation publication.

- Publication completed: commit
  `1aa7af7bfa2cec07ac3c8c4d4fb7ccaa9fbb4440` was pushed and verified on the
  remote `codex/restart-school-os` branch. Site source
  `9df687217aca4395c1a3c833473a1e15f9488ec5` was pushed and packaged as static
  HTML; version 12 deployment reports success. Ten published pages include
  https://school-os-architecture-guide.jeremieg.chatgpt.site/data-architecture.html.
  Existing owner-private access was preserved. All 173 local Site links/anchors
  resolved and the static pages had zero privacy findings. No browser test or
  deployed-page probe was performed.
- The skill-advertised packaging path became unavailable after authoring; the
  installed Sites static packaging helper successfully produced the same-source
  archive. No application build or test was substituted.
- Exact next action is now Q1/Q2 proposal review and the narrow Q4/Q6 decisions,
  then dependent implementation after explicit approval. Publication of this
  proposal/instruction subset is complete; the whole MVP and user-directed
  testing handoff are still ahead. No schema/index approval is inferred.


## 2026-09-15 — Final architecture approval and documentation snapshot preparation

- User explicitly approved all remaining published recommendations: Q1/Q2 exact
  data/index architecture, Q4 simplified arrival-time discovery and Q6 reuse of a
  fully-ingested email on a supported metadata match. Existing MVP deferrals remain.
- User authorized autonomous implementation followed by three isolated seven-day
  school-email ingestion/audit trials after implementation is published and its
  remote revision verified. This supplies the previously reserved subsequent
  testing direction; it does not authorize early tests, outbound messages,
  personal task-app writes, schedules or changes to existing instances.
- User then requested a recoverable GitHub snapshot titled **OrgoS Restart
  Documentation** before implementation and a clean restart free of legacy runtime
  pollution. Selected annotated tag `orgos-restart-documentation` and a new
  implementation branch `codex/restart-implementation` from that checkpoint in
  this same directory. Old runtime remains recoverable in tag/history.
- Inspected clean `codex/restart-school-os` at
  `ec7d70067ff9d8e55278596c0c51063fbdb02bd1`; preservation tag
  `restart-baseline-2026-09-14` already exists. Only sample local hooks were found;
  current CI tests main pushes/PRs/manual dispatch, not this branch/tag publication.
- Workers review approval wording, legacy isolation and publication boundaries.
  No functional tests, connector probes or ingestion have run in this phase.
- Exact next action: finish documentation hygiene, commit/push and verify the
  snapshot/tag/release; create the implementation branch, retire legacy active
  paths, then delegate the complete approved MVP and integrate it.


## 2026-09-16 — Documentation snapshot published; clean implementation branch

- Published GitHub release **OrgoS Restart Documentation** with annotated tag
  `orgos-restart-documentation`. Verified tag target and remote documentation
  branch at `09f6be151cd549431343b9ebe44a1d03371d2f4f`; verified the release name,
  tag, published state and documentation-prerelease designation.
- Created `codex/restart-implementation` from that tag in the same directory;
  working tree was clean at branch creation. No history rewrite or baseline-tag
  movement occurred. No open PR from the snapshot branch was found.
- Retired 230 tracked legacy files, including runtime/contract/schema/installer/
  provider wrapper code and the legacy CI workflow. The workflow ran retired
  package tests and was explicitly retired with that code, not silently bypassed.
  Keep standalone privacy hygiene, existing private/untracked material, current
  helper/operation material and frozen restart study files.
- Replaced competing historical document entry points with snapshot/current-plan
  pointers. Updated agent safeguards to retain raw private evidence, failure
  classification, independent semantic expectations and truthful action coverage
  without imposing retired packet/generation machinery.
- Assigned three bounded implementation workers: storage/knowledge/query,
  ingestion/extraction/continuation, and setup/task-sync/brief/shared adapters.
  Coordinator owns integration, coverage, Git and any new architecture escalation.
- Snapshot hygiene: zero privacy findings, 243 local document links/anchors
  resolved and clean diff whitespace. This is publication hygiene, not testing.
- Exact next action: integrate the complete retained MVP, review and publish it,
  verify the exact remote revision, then begin the three authorized isolated
  ingestion/audit trials. No functional test or ingestion has started.


## 2026-09-16 — Retained operations authored; overflow representation escalated

- Workers authored operational data/identity contracts, bounded storage,
  knowledge/query, historical/daily ingestion, extraction and continuation,
  task synchronization, setup/interview, completion review and brief procedures.
  Added shared semantic mappings for Drive, Gmail, Sheets, Todoist and optional
  ElevenLabs, and connected fictional data/ingestion examples.
- Coordinator added startup/daily composition and an operation dependency index,
  and prepared the exact isolated-trial protocol. No functional execution occurred.
- Integration fixed a circular completion-review/ingestion gate: evaluate complete
  source evidence within ingestion; save/read back Knowledge/Tasks before the
  final fully-ingested flag. Ingestion-only trials do not project to task apps.
- Cross-review identified a genuine missing approved shape: long-value segments
  were required but their stored records/references were not defined. Prepared
  SEGMENT-REPRESENTATION-PROPOSAL.md and asked the user to approve the narrow new
  canonical representation. It remains unadopted; affected writes block honestly.
  Do not reduce scope or begin the trials before the complete MVP prerequisite.
- Private Site version 13 deployed successfully from source
  `1d5ecbd22a0c1b351d2fb9c3f7a25ce0ad3b81c6`, recording final numbered-review approval
  and linking documentary references to the snapshot. The subsequent Q10 escalation
  is recorded here and in the active decision ledger, pending integration.
- Exact next action: resolve cross-review findings, obtain the segment-format
  answer while continuing independent approved work, integrate and publish the
  retained MVP, then conduct the three authorized ingestion trials.


## 2026-09-16 — Sol handoff and publication-hygiene review

- Updated current continuity summaries to reflect the actual checkpoint: the
  documentation snapshot is published and verified; retained operations,
  contracts, adapters and fictional examples are authored but untested; and Q10
  remains a publication-blocking architecture decision. Historical progress
  entries were not rewritten.
- Recorded the user's current staffing direction: bounded workers are Sol only,
  no Astra worker is assigned, and the root agent primarily coordinates,
  handles architecture and other escalations, integrates and owns publication.
  The existing `ASTRA-HANDOFF.md` path remains only as a historical filename.
- Clarified extraction's oversized-value guard. Until Q10's segment shape is
  approved and added to the contract, the agent may save only bounded
  `statement` values; an oversized substantive value blocks retention and full
  ingestion and must never be truncated.
- Focused static review found no new architecture gap in the current data,
  storage and task material. The locator fallback order, window-specific
  observed-Email directory chains, exact nested configuration/Email/coverage
  shapes and task synchronization meanings are materially consistent. This is
  review evidence only, not functional validation.
- Publication hygiene found zero privacy findings and zero findings across 233
  local document links/anchors; staged and unstaged whitespace checks passed.
  The frozen metadata/MIME study paths have no staged or unstaged changes. Only
  sample Git hooks are present. The legacy CI workflow is explicitly retired
  with the legacy runtime and preserved in the documentation snapshot; no
  replacement functional CI or disabled current check is claimed. This review
  did not stage, commit, push or alter gitignored/private material.
- No tests, simulations, helper execution/import, builds, connector/browser
  probes, ingestion, sends, task-app effects or live operations ran. The three
  seven-day isolated ingestion trials remain authorized only after the complete
  implementation is published and its exact remote revision is verified.
- Exact next action: obtain Q10 approval, integrate the approved segment shape,
  finish static review and publication hygiene, commit/push the complete retained
  MVP and verify its exact remote revision; only then begin the three authorized
  isolated trials.
- Final concurrent-state hygiene rerun: zero privacy findings and zero findings
  across 265 local document links/anchors. A transient missing-anchor report
  occurred while another owned HTML file was being written; the completed file
  contains the target and the clean rerun supersedes that transient observation.


## 2026-09-16 — Restart implementation checkpoint; Q10 remains open

- Accepted the authored operating recipes, retained contracts, shared semantic
  adapters, minimal helper references and fictional examples after bounded review.
  These are untested; full MVP implementation remains incomplete until the
  oversized-value representation is approved and integrated.
- Website sources now distinguish approved Q1–Q9 from the single new Q10 question,
  with a readable concrete segment proposal. No proposed segment schema has been
  adopted or used to save instance data.
- User requires no Astra workers. Both current bounded workers are explicitly Sol;
  earlier workers were stopped. Root coordinates, handles architecture/escalations,
  reviews integration and owns Git/publication.
- Publishing this accepted-work checkpoint preserves progress; it does not satisfy
  the complete-implementation prerequisite for the three ingestion trials. No
  functional tests, simulations, probes, ingestion or external task/send effects
  have run. The frozen studies and private material remain unchanged.
- Exact next action: obtain the explicit Q10 decision, implement that approved
  representation with Sol workers, publish and verify the complete retained MVP,
  then conduct the three already-authorized isolated ingestion/audit trials.


## 2026-09-16 — Accepted restart checkpoint published and verified

- Committed and pushed the accepted implementation checkpoint at
  `972ac4f1023be1aad4003af6a44ffbe527cb0c8f` on
  `codex/restart-implementation`; `git ls-remote` matched the exact SHA and
  the working tree was clean. The snapshot tag/release is unchanged.
- Publication hygiene passed with zero privacy findings, 398 local document
  links/anchors resolved and no whitespace findings. Frozen study paths had
  no changes; no functional test was executed.
- Static website source at `8176dee5da2ee78030e7812cc69ced3133f18fe3`
  includes the readable Q10 proposal, approved Q1–Q9 history and current
  retained implementation links. Its 11 static pages passed privacy and
  local-link hygiene; those checks do not establish functional behavior.
- Q10 remains the sole new architecture answer needed. Do not call the full
  retained MVP complete or begin the three ingestion trials. Exact next action:
  obtain the segment-format decision, delegate the approved change to Sol,
  integrate/publish/verify the complete implementation, then run the already
  authorized three isolated trials.
- Site version 14 deployed successfully at the existing owner-private guide,
  with source revision recorded above. The current open-question section links
  the concrete Q10 representation; no testing was triggered by publication.


## 2026-09-16 — Isolated trial handoffs prepared, still unexecuted

- Rechecked the clean restart branch and exact remote checkpoint
  `f69bde273a8c4d96345e5388ef7862a629d46522`; the documentation snapshot still
  targets `09f6be151cd549431343b9ebe44a1d03371d2f4f`. Prior goal work made
  concrete progress by publishing the implementation checkpoint and guide.
- A context-free Sol author prepared TRIAL-PROMPTS.md and linked it from the
  trial protocol. The templates supply the same final revision and seven-day
  scope, separate assigned folders, route-specific fresh task wrappers,
  explicit effect limits, and common source-grounded query handoffs. Filled
  private inputs and independent evaluator expectations stay out of Git.
- No prompt was dispatched to a tested agent. No connector/browser probe,
  functional test, ingestion, send, task-app change or schedule ran.
- Q10 remains unanswered and unadopted. Trial preparation does not satisfy
  the complete-implementation prerequisite. Exact next action remains explicit
  approval of the segment representation, Sol implementation, full publication
  and remote verification, then the three already-authorized isolated trials.


## 2026-09-16 — Autonomous goal blocked on Q10 approval

- Verified clean `codex/restart-implementation` at published checkpoint
  `75bc4ef6d3608b5681444f28031b8f6ed71ce727`. The preceding goal turn made
  concrete progress by publishing the isolated-trial prompt templates.
- The same explicit-approval blocker has persisted for three consecutive goal
  turns. Q10 remains a proposal; no user answer has adopted its new stored
  representation. Independent implementation, review and trial preparation
  are preserved; further meaningful execution depends on that answer.
- Mark the autonomous goal blocked rather than repeatedly polling for approval
  or adopting a new canonical schema without authorization. No tests, connector
  probes or ingestion trials have run. The full objective remains unfinished.
- Exact next action on approval: use Sol workers to implement the approved Q10
  format, integrate and publish the complete retained MVP, verify the exact
  remote revision, then perform the three authorized isolated ingestion audits.


## 2026-09-16 — Q10 rewritten as a standalone parent explanation

- User asked for a self-contained explanation of what Q10 solves and why the
  existing architecture left a gap. A Sol worker rewrote the Markdown proposal
  and viewable brief; coordinator reviewed the unchanged proposed architecture.
- Explain JSON, the chosen per-file byte bound, ordinary growth across more
  pages versus one oversized field, and the missing cross-agent piece format.
  A fictional guideline walkthrough and diagrams show saving, reconstruction,
  missing-piece handling and later edits. Costs, unknowns and alternatives are
  explicit; exact JSON now follows the explanation in an optional reference.
- This is clarification only: Q10 remains unapproved and unimplemented. No
  tests, probes, simulations, ingestion or external user-account effects ran.
  The goal remains blocked on the explicit architecture decision.
- Next action: publish this clearer explanation and retain the existing Q10
  approval boundary before dependent implementation and the authorized trials.
- Publication complete: proposal revision
  `e8bce725b4a2d104441b7a795a76a72c9cd707cb` was pushed and its remote SHA
  verified. Private Site version 15 deployed successfully from source
  `744eaba2dd69e611f890ff488e83e8fb3a818ca1`. Document privacy/link hygiene
  passed; the working proposal remains unapproved and no functional execution
  occurred. The next action is the user's Q10 decision.

## 2026-09-16 — Q10 rejected; retain one 64 KiB page maximum

- The user rejected linked overflow pieces because of brittleness and Drive
  I/O, and explicitly delegated the page-size decision after assessing likely
  record sizes, ease of increasing the limit, retrieval quality and cost.
- Sol workers updated the current contracts, operating guidance, plans and
  website sources. The coordinator decided to retain 64 KiB (65,536 UTF-8
  bytes) as the single maximum. Ordinary pagination splits collections between
  whole records; no segment family, linked field pieces, fallback blob or
  separate soft/hard limits are introduced. Oversized records remain visible
  blockers with measured required size, never truncated or falsely complete.
- Public primary-source research and fictional page sizes inform this starting
  choice; neither establishes actual managed-connector limits or real school
  record distributions. Larger packed pages can reduce file calls but increase
  irrelevant transfer/context and whole-page save/readback volume. Downloaded
  bytes, model-visible context and billed usage must be measured separately.
- A future evidence-based increase changes one shared installed contract limit;
  existing valid pages, IDs and references remain usable without eager migration
  or merging. Every agent must read the updated contract; route compatibility
  still needs evidence. See the [page-size assessment](docs/plans/restart/implementation/PAGE-SIZE-ASSESSMENT.md).
- Prepared the requested page-size evaluation in the authorized trial protocol:
  actual page/record bytes, Drive I/O, complete readback, retrieval accuracy,
  preserved qualifications, latency and exposed token/cost evidence. A matched
  64/128/256 KiB comparison uses the same saved records and source-grounded
  questions in marked noncanonical areas within the existing trial roots.
  Unexercised sizes and unavailable cost evidence remain explicit unknowns.
- Q10 is resolved; no current architecture approval remains pending. No tests,
  connector probes, model replays or ingestion have run. Private launch inputs
  were prepared in ignored mode-0600 files without copying old instance state.
- Next action: finish publication hygiene, commit/push the retained MVP and
  verify the remote revision, publish the updated private guide, then begin only
  the already-authorized three isolated ingestion/audit trials. Implementation
  publication is not functional validation or whole-product qualification.

- Final static integration review found no publication blocker. Diff, privacy and
  local document-link hygiene passed; only sample Git hooks and no active
  functional CI or matching pull request were present. Frozen studies are
  unchanged. This establishes publication hygiene only, not tested behavior.

- Complete retained implementation published and remote verified at
  `138ca7954bdb3b7e9de065199fdb4903d6a924a3` on
  `codex/restart-implementation`. The coverage map accounts for every principle,
  use case and T1–T10 deliverable; D2 generic repair, D7 centralized registry/jobs
  and D8 packaged lifecycle remain explicitly deferred. The new independent
  three-route trials will pin this implementation revision. No functional
  execution has occurred at this checkpoint.
- Private architecture guide version 16 deployed successfully from Site source
  `ec43f61c001a25ca563ceadb51965aa68899ff5c`, with links pinned to the published
  implementation. Site privacy and local-link hygiene passed. Q10 now explains
  the retained limit and evaluation rather than requesting segment approval.

## 2026-09-16 — Post-publication trial preflight paused

- Published implementation remains pinned at
  `138ca7954bdb3b7e9de065199fdb4903d6a924a3`; continuity publication was
  `6bda4a1ddec20c6c31becf8437f17085fd4a5d9f`. No ingestion has started.
- Sol browser preflight found fresh Gemini Spark and ChatGPT Work composers;
  Work visibly offered a non-Astra Sol selection. No prompt was submitted.
- Drive preflight established connector access but did not verify the intended
  tests-parent folder. The metadata route returned an invalid-argument response;
  a metadata-only search did not establish the exact pointer. No trial folders
  or canonical data were created. Raw receipts and local preservation-failure
  provenance remain private; do not classify this as an ingestion defect.
- Independent source enumeration and the semantic oracle have not started.
  Private continuation is in `private/restart-trials/preflight/status.json`.
- A fresh context-free worker could not spawn because this session reached its
  agent-thread limit. The coordinator asked whether to create a separate Sol
  task for that route; no replacement trial was silently substituted.
- The user requested unblocking the existing autonomous goal. Available goal
  tools expose no resume action, and CUA prohibits operating the Codex app.
  The existing goal remains blocked in the UI; no false completion or replacement
  goal was created. The architecture blocker itself is resolved. Next: the user
  resumes the existing goal via app controls, then continue exact-folder
  verification and the authorized trials, preserving fresh-agent isolation.

## 2026-09-16 — Goal resumed; isolated folders verified

- The existing goal is now active. The prior turn made concrete progress through
  publication and browser/Drive preflight evidence; it did not complete trials.
- Diagnosed the prior metadata failure as argument projection: a descriptive
  wrapper containing a folder URL was passed where the tool needed the folder
  reference. Extracting the referenced ID allowed a successful metadata read;
  the intended Tests parent was not missing. Cached browser confirmation was
  kept separate from live connector evidence.
- Created and metadata-verified three distinct fresh child folders for the
  coordinator, Gemini Spark and ChatGPT Work routes. No previous instance data
  was copied. Shared private inputs pin implementation
  `138ca7954bdb3b7e9de065199fdb4903d6a924a3` and received-time interval
  `[2026-09-09T14:53:31Z, 2026-09-16T14:53:31Z)` for every route.
- Browser trial prompts are being prepared for the verified isolated folders.
  A separate Sol auditor handles source expectations without reading tested
  outputs. The fresh context-free worker still needs an available agent slot
  or the user's answer about a separate Sol task; no experienced worker has
  been substituted. Next: launch browser trials, preserve their actual handles,
  and audit the three routes without cross-instance contamination.

## 2026-09-16 — Trial source preflight and private-transfer approval pending

- The operating implementation remains pinned at
  `138ca7954bdb3b7e9de065199fdb4903d6a924a3`. Coordinator searches by both Gmail
  identifier and metadata observed 17 matching message entries in the fixed
  interval, with no continuation. These are provider-entry observations and
  must not be treated as a count of canonical logical emails.
- The independent oracle read all 17 observed message bodies and prepared
  source-bound expectations and questions without reading tested outputs.
  Three image attachment receipts expose authenticated references but no local
  binary or inline image. Their visual semantics remain unknown, so the audit
  does not establish complete content coverage. Logical associations use only
  approved metadata; RFC/provider message IDs are not canonical identity.
- The first private launch-input preparation mistakenly retained only one of
  two configured school-sender domains. The frozen v1 evidence is preserved.
  Corrected v2 inputs contain both domains while retaining the same common
  scope, fixed interval and separate verified route folders.
- The exact cause of every earlier empty query remains unestablished. Current
  observations do not justify an endpoint-failure conclusion or attribute all
  prior empties to the local input error.
- Neither browser trial was submitted and no live run handle exists. Automatic
  approval review rejected uploading the private instructions to Gemini because
  they contain mailbox, child/school and Drive details. Explicit transfer
  approval for both Gemini and ChatGPT Work is pending; no alternate transfer,
  partial prompt or other bypass was used.
- A fresh context-free worker remains unavailable because the current session
  is at its agent-thread limit. The separate Sol-task question is still pending,
  and no experienced worker or existing task was substituted.
- The goal remains active. Next: await explicit upload approval and the
  fresh-task answer, then launch only the permitted routes and record their
  actual handles. Preserve the independent image-review gap unless a supported
  route exposes the images. This checkpoint is preflight and source-audit
  evidence, not functional product qualification.

## 2026-09-16 — Fresh first-route worker launched

- A retry successfully launched the fresh context-free worker as
  `gpt-5.6-sol` at high reasoning with no inherited turns. The prior separate
  Sol-task approval question is therefore moot; the earlier capacity history is
  retained above as chronology.
- The worker is assigned the actual first-route Drive setup and ingestion, pinned
  to `138ca7954bdb3b7e9de065199fdb4903d6a924a3` and corrected v2 inputs. It may
  use only its assigned coordinator route folder, must not read oracle or
  other-route results, and has no authority for outbound delivery, task-app,
  mailbox or schedule effects.
- The worker is running. Its launch does not establish that setup, ingestion or
  any functional behavior succeeded, and no product qualification is claimed.
- Gemini Spark and ChatGPT Work trials remain unsubmitted. Automatic approval
  review rejected the Gemini upload; both private uploads await explicit transfer
  consent. No alternate channel or bypass has been used. The independent source
  audit's image-evidence gap also remains open.
- Next: follow the same fresh-worker handle and inspect its actual result. When
  ingestion is ready, administer the independent common questions against that
  route. Separately await explicit consent before either browser prompt upload.

## 2026-09-16 — Independent source oracle visual coverage completed

- The independent oracle now covers all 17 observed message bodies and all three
  JPEG candidates across two parent messages. Visual evidence adds qualified,
  source-bound knowledge for both parents. Partially legible handwriting and
  exact chart-mark counts remain explicit unknowns.
- No task or completion expectation changed. Review against the seven existing
  common questions found no expected-answer or source-support amendment, so the
  original prompts remain unchanged. A private current-oracle manifest binds the
  immutable baseline expectations and questions to the versioned visual addendum
  and exact source receipts, preventing accidental reuse of stale 0/3 coverage.
- During the first capture attempt, two raw connector responses were returned but
  lost before private preservation when the local receipt sink failed; neither
  was interpreted. A synthetic Unicode payload then verified bounded chunked
  mode-0600 capture and atomic rename. Two targeted source rereads were preserved
  completely before decoding and visual review. This narrow receipt-capture
  repair is source-audit evidence, not product validation.
- The fresh Sol first-route worker remains running. Its launch still does not
  prove setup or ingestion succeeded; browser upload intervention also remains
  pending. Gemini Spark and ChatGPT Work are unsubmitted while explicit private
  transfer approval is pending, with no bypass used.
- Next: follow the same fresh-worker handle and inspect its actual result, then
  administer the independent common questions when ingestion is ready. Await
  explicit transfer approval before either browser launch.

## 2026-09-16 — First-route setup blocked; live Drive state audited

- The fresh context-free Sol worker finished its first-route attempt against the
  pinned implementation. It created the assigned folder hierarchy and staged 28
  pinned files locally, but no operating file was verified on Drive. Local
  staging is not persistence or successful setup.
- The connector upload receipt records an error with no structured result. Two
  browser file-assignment calls did not return a completed result and were
  interrupted. The retry requested explicit operation and tool timeouts, but
  successful enforcement of those bounds was not established. This distinguishes
  local preparation, connector response and browser intervention; it does not
  establish a transport, provider, authorization, permission or authentication
  root cause.
- An independent read-only live Drive audit followed three returned direct-folder
  references and 12 returned folder entries below the coordinator route. It
  observed zero files in the returned items. The audit used
  `google_drive_list_folder` with `url` and `top_k: 100`, not Drive search. Those
  responses contain no continuation token or explicit exhaustion state, so the
  short pages do not prove complete discovery. No bootstrap file, current system
  document, canonical configuration, page file or exact product-principles target
  was returned. Without a target reference, exact readback was unavailable and
  existence remains unresolved rather than proven absent.
- Setup did not reach mailbox reads or searches, ingestion, canonical indexes or
  pages, retrieval questions, or the page-size comparison. None of those checks
  is qualified by this attempt. The independently frozen source oracle remains
  complete for its intended comparison scope: 17 observed bodies and 3/3 JPEGs,
  with handwriting qualifications retained and no task/completion change.
- Gemini Spark and ChatGPT Work remain unsubmitted pending explicit consent to
  transfer their private v2 instructions. No alternate upload path or other
  bypass was used. The original three-route trial objective remains unfinished.
- Next: obtain explicit private-transfer approval and launch only the permitted
  browser routes. Separately diagnose the first route's local upload path within
  the existing architecture before any narrowly scoped setup recheck.

- Coordinator correction: the browser retry had been allowed on an empty
  returned listing. That response did not establish exhaustive discovery, so
  the retry relied on insufficient absence evidence. Both upload effects remain
  unresolved. The [trial report](docs/plans/restart/TRIAL-RESULTS.md) records this
  execution defect separately from connector/runtime limitations; the approved
  unknown-effect verification rule remains unchanged.

- A read-only inspection of the browser extension's upload prerequisite was
  blocked by browser security before opening a diagnostic tab. No settings were
  changed. The setting and actual upload root cause remain unknown.
- All workers have finished and there is no live trial process to wait on.
  The repeated private-transfer approval blocker remains, after completing
  independent source review, first-route observation and publication work.
  Execution is blocked, not complete. Exact next action: the user authorizes
  sharing the prepared mailbox, child/school and assigned-folder instructions
  with Gemini Spark and ChatGPT Work; then continue those existing isolated
  routes. Preserve the first attempt and resolve its upload capability and
  uncertain effects before any narrowly scoped recheck.


## 2026-09-16 — User-directed realistic first setup

- Updated product principles first to capture the core first-use path: one fresh,
  unconfigured ZIP/folder link and “setup my schoolOS,” with setup instructions
  discoverable through README/START-HERE/AGENTS and a single-line Claude import.
- The static starter and agent-led setup are an explicit narrow addition to D8;
  automated upgrades/migrations/compatibility/release machinery remain deferred.
  No new canonical schema, identity, save engine or runtime dependency is adopted.
- Two bounded Sol workers handle setup/entry instructions and the clean package
  preparer. The coordinator owns continuity, review and Git publication. No Astra
  worker is used. The previous trial worker now doing development cannot count
  as a fresh context-free participant in a future trial.
- Revised trial preparation separates the minimal opening message, parent
  interview answers, later scoped ingestion request, source-grounded questions
  and page-size evaluation. The historical guided prompts/results and unresolved
  upload effects are preserved; no private v2 prompt upload is resumed.
- Current boundary: implement and publish, then report readiness and stop. No new
  trial, ingestion, smoke run, connector probe or functional check is authorized
  by this work unit. Publication details follow after verification. Exact next
  action is finishing starter publication, then waiting for the user's testing
  direction using the revised realistic entry flow.

- Static integration review completed. Consumer entry files also route already
  configured instances to the requested operation; setup does not repeat merely
  because starter files remain. The guide defers canonical bootstrap creation
  until required interview/tool answers are available. The developer packager
  reads an exact committed revision and includes only 30 approved operating/entry
  files plus empty directory entries; it is not shipped as an instance runtime.
- Privacy scan, relative document links/anchors and diff hygiene are clean. Hook
  inspection found only sample hooks, no core.hooksPath override and no active
  workflow; no check was disabled. Functional setup/ingestion remains untested.


## 2026-09-16 — Fresh starter published; readiness stop

- Source revision `ba6bcc3bec96dfc542fd83cb792318ac8e54ce56` is committed and pushed on
  `codex/restart-implementation`; the remote branch was verified at that exact
  SHA. The annotated `school-os-starter-2026-09-16` tag peels to the same SHA.
  The OrgoS Restart Documentation snapshot, old releases and frozen evidence
  remain unchanged.
- Published [School-OS-setup.zip](https://github.com/jeremieguedj/School-OS/releases/download/school-os-starter-2026-09-16/School-OS-setup.zip)
  on the [dedicated prerelease](https://github.com/jeremieguedj/School-OS/releases/tag/school-os-starter-2026-09-16). The archive is 98,205 bytes,
  with 30 operating/entry files and nine directory entries. `instance/` and
  `extensions/` are empty; no private configuration, canonical IDs, retired
  runtime, developer trials, tests or expected answers are included.
- The archive was prepared from the exact committed revision. Privacy, member,
  relative-link, archive byte/CRC and Git hygiene completed. GitHub's uploaded
  asset size and digest match the reviewed archive:
  `ebbfbe0d13145a26c765f0ac9eaa52bb22e40b3856c567b1396fbae8f0438ad4`.
  This hash binds a public distribution artifact only, never source identity.
- No new setup trial, ingestion, connector probe, smoke run, helper test or
  functional evaluation ran. Publication hygiene is not product qualification.
  Prior Drive upload failures/unknown effects remain unresolved and retained;
  actual download/setup/write capabilities are matters for the directed trials.
- Ready for the user's testing phase. All routes will begin with the same ZIP
  link plus “setup my schoolOS,” discover the guide, interview for missing
  choices/options, establish separate new test instances and verify setup.
  Ingestion is then a separate scoped request with a common seven-day interval;
  independent question audits and the 64/128/256 KiB comparison follow.
- Exact next action: **stop and wait for the user to direct revised testing**.
  Do not submit the historical private v2 prompts or reuse previous trial roots.
  Future private interview answers still require the applicable disclosure
  authority. No architecture decision remains open for this setup change.
- This entry and links are a continuity-only publication after the source tag;
  they do not change the pinned starter contents or claim the overall trial goal
  is complete.


## 2026-09-16 — Revised trials resumed under no-repair instruction

- The user approved testing and uploads for all three agents, then explicitly
  required results review before any bug is addressed. The goal tool now reports
  active status. The prior turn was a user-directed wait; this turn resumed
  preparation and created a fresh context-free Sol trial from the exact published
  ZIP link plus “setup my schoolOS,” with no additional initial wrapper.
- Sol reported starter discovery and asked the parent interview questions. No
  configured Drive instance, ingestion or retrieval outcome is established yet.
  The route was held before external writes while answers are prepared.
- Browser inventory was initially rejected by approval review under the earlier
  wait instruction. After rechecking active goal status, the same read-only
  request succeeded. Opening a new Gemini tab was then rejected because review
  still required a direct unblock. Root asked for clarification; no alternative
  browser route or bypass was attempted. Neither browser trial was submitted.
- A separate Sol evaluator is preparing private interview answers and an audit
  plan without live calls or tested-agent output. Proposed common seven-day
  received/arrival bounds are 2026-09-09T17:53:48Z inclusive through
  2026-09-16T17:53:48Z exclusive; the older oracle covers a different interval.
- Product material stays frozen at ba6bcc3bec96dfc542fd83cb792318ac8e54ce56.
  No bug fix, product workaround, implementation edit or repair/retest is
  authorized. Record findings and limits for joint user review after the trials.

- Evaluator preparation completed without live calls. The private common answer
  sheet and audit plan are mode 0600 under a mode-0700 ignored directory. They
  preserve verified user settings only, not prior canonical state or route IDs.
  Parent identity and new per-route destinations remain to be supplied/established;
  actual capabilities must be observed. No tested-agent output informed source
  expectations, and no new source oracle has been claimed.
- The fresh Sol route's four private initial evidence files and directory modes
  were verified. All workers are paused/finished; there is no live browser trial
  process. Pending clarification is an authorization wait, not a running test.
  This turn made launch/evidence/preparation progress; the overall goal remains
  active and incomplete. No product implementation files changed.


## 2026-09-16 — Initial Sol evidence audit; no repair

- Previous goal turn classified as progress: fresh launch, preserved interview
  observations, private evaluator preparation and published no-repair authority.
  Current goal remains active; all worker handles now report completed or
  interrupted. No browser task handle exists, so this is not a live-process wait.
- Read-only review of the saved Sol action log found that the runtime read the
  local repository START-HERE and setup procedure before the supplied ZIP.
  Although the launch had no inherited conversation and only the minimal user
  prompt, it does not establish bundle-only instruction discovery. Recorded
  this environmental limitation without restarting or changing product files.
- The worker's reported missing packaged path in the checkout is not established
  as a documentation defect: the pinned repository entry explicitly distinguishes
  repository and packaged paths. Broad/truncated reads and tool discovery are
  recorded as reported agent inefficiencies, not independently complete traces.
- Independently inspected the local downloaded ZIP: 98,205 bytes and the exact
  published digest. A mode-0600 private audit records this distribution evidence;
  it is neither canonical email identity nor functional setup validation.
- The browser authorization clarification remains pending after the same
  automatic-review rejection. No rejected action was retried or bypassed this
  turn. No new live-source/account action, configuration write, ingestion,
  implementation fix, workaround or retest occurred. Continue the existing
  trials only after the pending authorization issue is resolved; keep all
  results for joint review with the user.


## 2026-09-16 — Explicit start confirmation; live trials and audit proceed

- User directly confirmed: “The goal is unblocked. Start all three tests and
  uploads now.” This clears the preceding runtime authorization ambiguity. The
  no-fix/no-defect-workaround instruction remains in force. The fresh Gemini page
  opened successfully; no further generic testing approval is needed.
- A bounded Sol browser operator owns the two new browser tasks, exact minimal
  opening prompt, private observable evidence and requested interview replies.
  It must stop at verified setup or a concrete blocker before ingestion.
- A separate Sol evaluator began the independent read-only source audit for the
  common fixed received/arrival interval, without reading tested-agent results.
  All expectations and raw receipts stay private; no new oracle completion is
  claimed until its actual report.
- Coordinator created three new route destination folders under the verified
  tests parent. Metadata readback confirmed each identity/name/type/parent.
  One URL-form metadata read returned INVALID_ARGUMENT; actual readback using
  that folder's returned ID succeeded. No repeated create or product patch was
  performed. Complete raw receipts are preserved privately.
- Three private interview replies contain common household/source/tool choices,
  distinct assigned destinations and isolation/no-effect/no-repair limits.
  The parent display name comes from the observed signed-in profile; no legal
  identity was inferred. No evaluator answers or prior canonical state are sent.
- The attempt to resume the same initial Sol trial handle hit the agent-thread
  capacity limit. It was not replaced or relaunched as a new trial. Continue
  that same route when a bounded worker finishes. Current browser/source workers
  remain active; do not infer a stopped provider task from observation timeout.

## 2026-09-16 — Source reference prepared; existing setup attempts continue

- Independent source audit completed its message reads for the current interval:
  17 provider observations, 17 full reads, two exhausted searches, three JPEG
  fetches and seven source-supported questions. Counts are observations, not
  logical-email ground truth. Fresh JPEG pixels were unavailable; earlier visual
  evidence is explicitly supplementary, not fresh attachment qualification.
- Two early search receipts were lost on local sink failures before later
  preserved reads. Record this evaluator intervention and evidence limit. No
  tested-agent output informed the reference inventory. Detailed evidence stays
  in the ignored private trial directory.
- With evaluator capacity freed, the original Sol starter worker resumed with
  ordinary interview answers. It reached Drive-root qualification; setup writes
  and ingestion success are not yet established. No replacement trial or hidden
  reset occurred, and the earlier repository-instruction exposure remains.
- Browser operator reported no submitted prompts after a tab-binding error and
  stalled app selection. Root interrupted that stalled operator turn, confirmed
  the original Spark composer was empty, and directed the operator to open its
  own fresh browser tabs. This changes evaluator control, not product behavior;
  no provider task was restarted. Record the delay separately from product bugs.
- Prepared the common separate ingestion request privately. It has not been
  supplied before verified setup. Product source and published starter remain
  unchanged. Continue the three attempts, then audit and report without fixes.

## 2026-09-16 — Browser prompts submitted; Drive distribution directed by user

- Browser operator could not bind the coordinator-owned tab and stalled twice
  on native-app attachment, without submitting either prompt. Root took over
  browser control and submitted the exact starter link plus “setup my schoolOS”
  to Spark and Work. Work's visible selection was GPT-5.6 Sol Light. Actual task
  handles and task-relevant observations are preserved privately.
- Work returned a network error before the interview; root did not click Retry.
  Spark reported external-download restrictions and requested uploaded material.
  The user specifically directed a Google Drive ZIP link for Spark. Root uploaded
  the same 98,205-byte public starter under the verified tests parent and checked
  returned metadata against the intended name, MIME, size, identity and parent.
  Its observed Drive link was supplied to the same Spark task, which resumed.
- Review rejected Sol's configured-bootstrap upload for missing specific private
  data authority. Root surfaced the rejection. The user then explicitly authorized
  personal-data uploads to Drive and the agents needed for the goal. Root conveyed
  that authority while retaining effect verification and no-repair boundaries.
- Review also rejected displaying full raw browser trees. Root instead saved
  observations privately without emitting their contents; a Sol observer extracts
  only relevant findings. No account/history material is added to public records.
- No product implementation changed. Await setup readback or concrete blockers,
  then separately request ingestion only on configured routes. Work's failure
  remains preserved; no unrequested retry or replacement was launched.
- Subsequent saved-evidence review clarified that Work has only provisional
  frontend conversation state; no durable server task handle is established.
  Spark remains running without interview questions. Independent second review
  confirmed the source reference's attachment and receipt-chain limitations.

## 2026-09-16 — Sol setup readback complete; ingestion requested

- Sol reports exact actual readback for the configured entry point and all 37
  instance JSON files: five core, 11 locator roots, eight catalogues and 13
  indexes. It also checked public system inventory and folder contents. Source
  access, ingestion and external effects were not claimed as part of setup.
- The same test worker received the separate common seven-day ingestion request.
  No evaluator expectations or other-instance data were supplied. It remains
  under no-fix/no-workaround and read-only-mailbox limits, with canonical writes
  confined to its assigned Drive instance. Query evaluation follows later.
- A separate Sol reviewer is checking preserved setup evidence against the
  approved contracts and ordinary interview answers. This independent review
  distinguishes actual readback from echoes, exact saved values from semantic
  validity, and folder observations from proven exhaustion. No product repairs.
- Spark reached its ordinary setup interview after the user-directed Drive ZIP
  handoff. Root supplied the authorized private answers and standard starter
  brief-template preference as configuration only. Spark is setting up; no
  ingestion request has been sent to it. Work remains at its un-retried network
  failure with no confirmed durable task handle.

## 2026-09-16 — Independent setup review and first ingestion observations

- Sol reports discovery of 17 in-scope observations, exhausted continuation, full
  MIME reads for all 17 and successful reads of three attachment candidates.
  It is interpreting content; the discovery window remains durably unfinished.
  Fetch success is not a verified complete-ingestion claim.
- Independent setup audit confirms exact actual readback for START-HERE and all
  37 instance pages. Schema, references, UUIDs, bounds and approved configuration
  scope pass the preserved-evidence comparison; maximum setup page is 5,795 bytes.
  This does not exercise pages near 64 KiB or larger candidate limits.
- Audit corrected the strength of inventory claims: folder lists expose no
  continuation/exhaustion evidence, so matching returned counts do not prove full
  inventories or extensions empty. Fresh destination creation is separately
  documented. All 30 public/root files match reported sizes, but 29 lack content
  readback. Preserve these unverified areas without repairs or corrective calls.
- Canonical configuration evidence supports continuing the separate ingestion
  attempt. Spark remains in setup, Work remains un-retried, and no product files
  or published starter have changed.

## 2026-09-16 — Setup audit completed; Spark held for uncertain effects

- Independent Sol setup audit completed privately. Preserved setup activity is
  135 attempts: 13 successful folder creates, 68 uploads (67 successes plus one
  predispatch review rejection), 38 exact content readbacks, 15 listings and one
  invalid metadata call. Core configuration/scope/reference/bound checks pass;
  public-file content and listing-exhaustion limits remain as recorded above.
- Spark's live progress claimed setup writes and completion but supplied no
  visible final readback. It also mentioned decoding/conversion/retry issues
  and deletion of a test file without an observed target or outcome. Root stopped
  that response and asked for read-only inspection of the assigned instance and
  an evidence-based account of existing saves and uncertain effects. Do not
  mistake these progress claims for confirmed errors or provider mutations.
- This is a preserved coordinator intervention, not a silent product fix,
  cleanup, restart or successful setup qualification. Spark ingestion has not
  started. Sol continues its independent ingestion; Work remains un-retried.
- Exact next action: inspect the Sol ingestion result and Spark read-only report;
  continue query/audit work only where actual saved state supports it. Preserve
  failures for joint user review, without addressing bugs during the trials.

## 2026-09-16 — Spark failed setup independently confirmed

- Spark returned its read-only report: partial setup, missing procedures, format
  conversion and incomplete verification. No ingestion was requested or claimed.
  The coordinator did not instruct repair, cleanup or resumption.
- Independent read-only metadata using exact observed handles confirms that the
  reported test JSON exists directly under My Drive/root, outside the assigned
  route. Its current existence/location is confirmed; authorship and whether a
  deletion was ever attempted are not established by metadata alone.
- Independent metadata/content fetch confirms a native Google Doc entrypoint
  with 18 logical-role IDs and one generic catalogue root. This fails the pinned
  24-role/eight-catalogue contract. Other file counts, absent operations and
  decode/corruption statements remain self-reported in this bounded audit.
- Four complete connector receipts and the audit are preserved privately at
  mode 0600. No broad Drive search, mutation, repair, cleanup, replacement task
  or failed-effect retry occurred. Spark is a failed setup outcome with later
  ingestion/query/page-size stages unexercised. Sol ingestion continues; Work
  remains at its un-retried launch/network failure.

## 2026-09-16 — Sol ingestion reported complete; saved-data queries begin

- Sol reports final persistence/readback complete, including 46 non-coverage
  indexes, coverage page/locator/catalogue/index and completed discovery window.
  Saved outcome is 17 Email, three Attachment Group, 21 Knowledge, 10 Task,
  17 Topic and one source-established Entity record, with 17/17 ingestion flags.
  Folder counts remain nonexhaustive observations under the known connector limit.
- It reports initial attachment download transport/DNS failures before response,
  then successful authorized escalated reads. Temporary raw copies and bearer
  configurations were removed after persistence; private audit receipts remain.
  No mailbox mutation, external task write, outbound delivery or schedule.
- The independent source evaluator is comparing actual saved core readbacks
  against its frozen source-bound expectations. It has not been shown query
  answers and must not adapt expectations to the tested output or repair data.
- Root supplied the seven common questions only after reported ingestion
  completion, using the private question-only artifact. Answers must come from
  actual saved-Drive retrieval, with source/record support and coverage limits;
  no mailbox reread, memory-based gap filling, record repair or external effect.
- User asked about missing Spark interview text after refresh. Saved full views
  show it present after cancel but absent from a later view before refresh, in
  the same task/tab; no root Edit invocation is recorded. UI hiding versus
  provider transcript replacement remains unknown. User chose to investigate;
  root ended that inquiry and continued testing without resending answers.
- Next: grade the seven answers against preserved source and saved-record
  evidence, then perform the authorized size assessment where the actual data
  makes it meaningful. Preserve all failed routes and do not implement fixes.

## 2026-09-16 — Semantic defects confirmed; independent query grading starts

- Independent source comparison verified six core saved pages and all 17 source
  associations, but found seven material semantic instances: one substantive
  omission, two unexpected canonical tasks, recurring and conditional actions
  flattened into finite tasks, and two individual completion units collapsed
  to household completion. Exact evidence stays private; no fix was made.
- The omission was checked against all Knowledge/Task text, not merely source
  links. The evaluator corrected its earlier overly broad zero-action summary;
  the frozen reference already contained a justified no-action disposition and
  was not changed to match the tested output.
- Sol answered all seven questions from actual saved-Drive retrieval and
  preserved 89 read receipts. The independent evaluator now grades answers,
  source support, limitations and retrieval efficiency. It must not expose
  expected answers to the tester or repair records.
- Authorized the separate 64/128/256 KiB evaluation using only complete saved
  records in a private noncanonical area of the same Sol root. No new instance,
  mailbox read, synthetic padding, field splitting or contract-limit change.
  Candidates not approached by real page sizes must remain unexercised.
- Reconciled the active plan's top section with current outcomes; superseded
  launch/approval holds remain historical. Next: finish the two audits, publish
  and verify sanitized continuity, then stop for joint review without fixes.

## 2026-09-16 — Seven query answers independently graded

- Independent grading found six passes and one qualified pass, with no incorrect
  main answers. All seven include a relevant limitation. Three answers recover
  conditions or individual completion units from supporting prose despite the
  weaker canonical Task fields. Good answers do not erase storage defects.
- The qualified answer supports its main negative correction conclusion, with
  an ancillary relationship citation gap recorded privately. Different source
  aliases were assessed for their actual support, not rejected merely because
  they differed from the reference inventory. The oracle remains frozen.
- All 89 reported operations have non-error receipts: six folder lists and 83
  file reads. The corresponding 83 cache files exactly match receipt payloads.
  Retrieval swept the full layout, including all 48 index shards, for answers
  citing 14 canonical records; selective retrieval efficiency is not established.
- Size comparison's initial packing preserves all 105 ordered complete records
  and ten family/routing boundaries. All candidates have the same ten-page
  partition; the largest remains approximately 46.6 KB. Near-limit behavior is
  unexercised. Continue the already-authorized exact readback/query comparison,
  then review the evidence and publish results without repairs.

## 2026-09-16 — Independent public-summary precision review

- Corrected the Entity count: ten saved Entity records in total, including one
  established from source evidence during ingestion. Earlier entries listing one
  source-established Entity describe the ingestion addition, not the full total.
- Distinguished ingestion-coverage `fully_ingested` states from parent task
  completion, and canonical-task inventory disagreements from absence of any
  source-supported guidance. No source expectations changed.
- Narrowed the independent six-core-page claim to successful receipt decoding
  and exact handle/page-ID binding. The tester's reported write/readback equality
  is separate evidence, not a comparison independently repeated by that audit.
- Clarified the qualified query answer: its conflict citation is precise; the
  separate supports relation has no exact citation in that answer and is outside
  the independent frozen correction support. No answers or product files changed.

## 2026-09-16 — Live size comparison finished; keep the existing limit

- Sol completed comparison provider operations with no reported failure or
  retry: 30 uploaded candidate pages, 30 full verification readbacks and 24
  query reads, plus four evaluation-folder creates. No further provider call
  is planned; final independent query review uses preserved evidence only.
- Independent local audit verified 30/30 exact candidate readbacks and identical
  reconstruction of 105 ordered whole records across ten family boundaries.
  All three limits produce the same grouping. Largest canonical core page is
  46,597 bytes; largest comparison page is 46,607 bytes, 71.1% of 64 KiB; largest
  compact record is 2,335 bytes. No near-limit, multi-page-family or oversize
  behavior is exercised. Evaluation artifacts remain isolated inside the Sol root.
- The coordinator retains the existing 64 KiB maximum. This sample supplies no
  packing benefit from a larger limit and cannot qualify larger payloads or
  their cost. Model-visible bytes, actual tokens, cost and active time are unknown.
- Each candidate's seven-question batch read eight pages/101 records; reported
  answers are semantically equal. Final independent grading is underway. The
  evaluation's direct page routing differs from production index traversal, so
  fewer reads than the baseline do not establish a benefit from larger pages.
- Next: finish evidence review and final publication, verify the remote revision,
  and stop for joint user review. The implementation and starter remain frozen;
  failures are retained without fixes, cleanup or retests.

## 2026-09-16 — Trial audit concluded; stop for joint review

- Final independent comparison-query review verifies all 24 receipts against
  preserved candidate pages/caches and all answer payloads against retrieved
  records. Grades are 18 passes and three qualified passes across 21 answers;
  each candidate repeats the same six passes and one citation qualification.
  No remembered-only factual payload was found, and the oracle stayed unchanged.
- Exact full-page query bytes are 125,509 / 125,517 / 125,517; the eight-byte
  difference is threshold-label length. Requested-field bytes, model-visible
  context, billed tokens and cost are unknown. The direct evaluation route
  cannot establish a larger-page efficiency benefit over indexed retrieval.
- Authorized trials and audits are concluded: one Sol ingestion with semantic
  failures, failed Spark setup and failed Work launch. Dependent stages on the
  browser routes remain unexercised. This is not a successful three-agent
  ingestion comparison or broad product qualification. No repairs were made.
- Retain the existing 64 KiB maximum. Publish the sanitized results and updated
  plan/protocol, verify the exact remote revision, and stop for joint user review.
  After publication, the next action is the user's decision about findings; no
  fixes, cleanup, browser retries or further tests are authorized implicitly.
- Publication hygiene covers diff/privacy/document links, Git state and remote
  revision only; it does not add functional validation. Private files are 0600
  under 0700 directories and remain ignored. Only sample hooks and no active
  workflows were found; no check was disabled. Starter source remains
  `ba6bcc3bec96dfc542fd83cb792318ac8e54ce56`.

## 2026-09-16 — Second browser attempts authorized with strict controller isolation

- User explicitly authorized new Spark and ChatGPT Work attempts and required
  separate isolated controller contexts and browser interaction. Use fresh Sol
  controllers without inherited turns, distinct new tabs/folders/private logs,
  no cross-route transcript or oracle exposure, and serialized browser-action
  leases. Root coordinates and reviews, without operating their tabs.
- Reverified the existing tests parent and unchanged Drive ZIP metadata; created
  and metadata-verified two new assigned destinations. No previous instance was
  modified. Prepared private route-only interview/request packets with verified
  destination replacements and unchanged fixed seven-day source interval.
- Explicit new authority allows controlled transient launch/read retries. Unknown
  write effects still require verification. Product fixes remain forbidden.
  Setup must be independently verified before ingestion is requested.
- Next: launch the isolated controllers, preserve complete private observations,
  and continue setup/ingestion/query cases within each approved boundary.

## 2026-09-16 — Isolated Spark launch observed; Work lease granted

- Fresh Spark controller reports successful creation of its own new browser tab
  and submission of the exact Drive ZIP/minimal setup opening. Provider is
  retrieving package metadata; no interview or persisted setup outcome yet.
  No retry, evaluator handoff or ingestion request was sent.
- Spark controller marked its tab for handoff and explicitly released browser
  control. The Work controller verified only its own private packet and made no
  browser calls while waiting. Root then granted Work the exclusive UI lease.
- No tab was shared, no root UI operation occurred, and no transcript/results
  passed between controllers. Both remain confined to their own route data.
  Next: observe Work launch, then alternate bounded interview observations while
  provider tasks run independently.

## 2026-09-16 — Both provider tasks launched in isolated sessions

- Work controller confirmed ChatGPT Work with GPT-5.6 Sol Light, submitted its
  exact minimal opening once in a new owned tab, and observed an active response.
  No error or retry at this checkpoint. This establishes launch only, not setup.
- Work released the browser-action lease and marked its tab for handoff. Root
  granted Spark the next bounded observation/interview lease. Provider tasks
  continue independently; controllers never operate the browser concurrently.
- No source ingestion, external task write, output send or schedule has been
  requested. Setup readback remains the gate before the next stage.

## 2026-09-16 — Both interviews answered; browser evidence limitation recorded

- Each controller answered its provider's ordinary interview from only its own
  authorized packet and established destination/isolation before writes. Both
  providers are working; no setup success or ingestion is yet established.
- Controllers confirmed a supported-runtime limitation: full emit:false AX
  observations remain in their separate persistent REPL memories; no documented
  filesystem/export API is available for durable raw-AX copies. Private disk
  logs contain action/status metadata and handles, not full raw UI receipts.
  Earlier intended durable capture must not be reported as achieved.
- Do not bypass the API restriction, use global clipboard or expose raw private
  states. Preserve each CUA session, report this process-evidence limitation, and
  use independently preserved direct Drive connector readbacks for saved-state
  qualification. This is evaluator evidence handling, not a product repair.
- Root continues alternating exclusive browser leases. No controller has operated
  the other's tab or received its transcript/output. Provider tasks may progress
  in parallel inside distinct instances. Next: obtain completed setup claims and
  inspect their actual saved state before authorizing ingestion.

## 2026-09-16 — Spark activity changes observed during isolated setup

- Controller compared successive full snapshots in memory and observed changed
  task activity. Expanding only the owned task's activity exposed package reading,
  assigned-folder creation, saves and verification activity. These are visible
  provider activity claims, not independent saved-state qualification.
- Spark remains active without a final setup claim, additional interview or
  supported error. No prompt, reload, retry or ingestion was issued.
- Spark released the lease with no call in flight; Work received the next bounded
  activity inspection. Continue allowing independent provider execution, then
  apply the saved-state review gate after a final setup report.

## 2026-09-16 — Work entered its Drive-save phase

- Isolated Work activity changed and reports local instance generation complete
  plus an in-progress 64-file Drive-save set. It was uploading entity
  configuration at observation time and reported no error. Actual complete
  persistence/reference readback remains pending; the reported count is not
  independently verified setup completeness.
- The controller issued no prompt, coaching, retry or ingestion request, then
  released browser control with no call in flight. Root assigned the next bounded
  observation to Spark. Both providers continue their own setup procedures.

## 2026-09-16 — Spark claims completion; saved-state audit begins

- Spark made a final setup/configuration-complete claim and asked to begin
  ingestion. Its isolated controller held the request and released UI control.
  No ingestion permission or request was sent.
- Root independently listed only the assigned Spark root, fetched its actual
  entrypoint and listed its system/instance children, preserving four complete
  connector receipts privately before interpretation. The root observation shows
  expected top-level areas and native-document entry files. Returned counts do
  not prove exhaustive inventory; format conversion alone is not corruption.
- Spark controller now audits only its own preserved/read-back setup against
  its interview and pinned neutral contracts, with no browser calls or writes.
  It receives no Work results or prior evaluator findings. Root retains the
  ingestion-stage decision. Work has the exclusive browser lease for its own
  progress observation; it last reported 50 of 64 saves with readback pending.

## 2026-09-16 — Work claims completion; both setups held for audit

- Work now claims 64 installed files and actual byte/reference readback for
  34 private pages plus START-HERE. It reports Drive qualified, Gmail selected
  but untested, and no ingestion or outbound effects. These remain provider
  claims until independent saved-state comparison; a different file count alone
  is not a defect where contract-compliant packing differs.
- A bounded browser observation timed out and reset the controller CUA session,
  losing older in-memory raw snapshots. The controller used the authorized
  read-only retry to reattach its saved exact tab, without restarting the provider
  task, submitting a duplicate prompt or repeating writes. Final state is in
  memory and sanitized logs/handles are durable. Keep the evidence-loss limit.
- Root independently captured Work's root listing, actual entrypoint fetch and
  system/instance listings. Expected top-level areas are observed; no list
  exhaustion is inferred. All four complete receipts are private.
- Each fresh controller now audits only its own provider's saved setup against
  its authorized answers and pinned neutral contracts. Neither holds a browser
  lease, receives other-route results, reads an oracle or changes an instance.
  Both provider tasks remain awaiting ingestion; root will decide the next stage
  from saved-state evidence, without repairs or hidden coaching.

## 2026-09-16 — Second Spark setup fails saved-route audit

- Independent actual Drive readbacks resolve all 18 page IDs exposed by Spark's
  entrypoint, but only one is a page catalogue. Its route names `catalogue_root`,
  which is not a canonical family. Required Email, Attachment Group, Ingestion
  Coverage and Knowledge source/month and pending catalogue routes are not
  reachable. An exhausted generic empty catalogue cannot establish those empty
  inventories. This is a semantic structure failure, not merely a file-count
  disagreement or a write-echo inference.
- The audit stopped at that decisive defect. Spark ingestion remains blocked;
  no fixes, rewritten prompts, source reads or further Spark browser operations
  are authorized by this finding. The saved instance is preserved.
- Root checked the local published starter's exact digest and independently
  compared its data contract, storage procedure and setup procedure with the
  pinned Git objects: all bytes match. That does not prove what Spark read or
  copied; no unsupported cause is assigned to the failure.
- Work's own saved-state audit continues separately. It receives no Spark
  findings or context. Root will decide its ingestion gate independently.

## 2026-09-16 — Work passes setup gate; separate ingestion authorized

- Work's independent required setup audit returned pass with limits: 160 checks
  cover the configured entrypoint, all 24 required roles, 34 bounded JSON pages,
  identities, references, routes and authorized household/source/tool choices.
  All 26 reusable system files and three unchanged root instruction files match
  the supplied ZIP exactly. No ingestion records or canonical tasks were present.
- Empty derived entity-index coverage requires the existing canonical Membership
  fallback. Folder-list counts still lack exhaustion evidence; every required
  referenced target was fetched separately. No universal compatibility or
  complete outside-scope effect audit is claimed.
- Audit cost was 77 direct Drive reads, with 76 complete envelopes preserved plus
  four coordinator receipts. A local encoder failure lost one initial listing;
  one read-only repeat was preserved. No connector-reported errors. Keep this
  separate from provider setup cost and the earlier browser evidence-loss limit.
- Root accepted the setup gate and gave only Work the exclusive browser lease
  to submit its own unchanged ingestion request once. No audit findings, oracle,
  expected record counts or Spark context go into that provider message. Spark
  stays preserved at its failed setup. Exact next action: observe Work's separate
  ingestion, then audit actual saved meaning and questions without fixes.

## 2026-09-16 — Work ingestion dispatched; independent expectations frozen

- The isolated Work controller confirmed idle state and submitted the separate
  unchanged ingestion request exactly once. The exact bounds are visibly present
  and the provider is active. Later activity reports source enumeration and
  attachment review, followed by extraction/persistence work; these remain
  provider claims until independently audited. No questions or fixes were sent.
- A separate context-free Sol evaluator prepared a private expectation map from
  the existing source-bound reference before reading Work output. It covers
  substantive knowledge, task dispositions, applicability, completion units,
  source links and seven question expectations. Controllers receive no oracle.
  The existing lost-search-receipt and fresh-JPEG-pixel limits remain unchanged.
- Exact next action: let Work finish, preserve its actual saved pages and report,
  then compare those with the frozen expectations and evaluate the requested
  questions. Root continues exclusive browser-action leases; Spark remains held.

## 2026-09-16 — Work reports one source-content scope gap

- Work activity reports one message whose substantive newsletter is reachable
  only through an external HTML image URL. It is preserving `not_ingested` for
  that email and continuing the other discovered messages. No final saved-state
  outcome has yet been audited.
- Local review of the frozen packet confirms there is no explicit external-image
  prohibition. Work inferred one from read-only mailbox scope and the instruction
  not to introduce substitute workarounds; its captured explanation cites no
  named School-OS attachment rule. Preserve this scope-interpretation issue and
  do not assert a connector failure, unsupported fetch, or proven product defect.
- The coordinator made no provider correction, expanded source request or
  workaround. Let the provider finish and audit actual saved coverage and meaning;
  any later common questions must preserve the observed ingestion limitation.

## 2026-09-16 — Work question reporting and independent saved-state audit

- Work reached a final idle ingestion response. The separate question packet
  had not yet been submitted when the controller identified that in-chat answers
  could not be exported durably through the documented Chrome API. In-memory AX
  alone would not provide a durable exact-answer artifact for independent review.
- Root authorized one explicit output-format adjustment: keep all common
  questions unchanged and append a request for a downloadable Markdown/plain-text
  copy of the same answers, citations, limitations and concise retrieval summary.
  It explicitly forbids Drive mutations, new source fetches and repairs. Preserve
  the final submitted prompt privately and record artifact-generation overhead
  separately. This changes evidence delivery, not expected answers or product code.
  If the provider cannot supply a supported download, report that limitation.
- The independent Sol evaluator may now read the final saved Work instance from
  its verified private binding and compare it with the already-frozen source
  expectations. It receives no browser transcript, other route context or revised
  oracle. Reads are confined to the assigned instance; no Gmail read or mutation
  is authorized. Questions and this audit can proceed as independent read-only work.

## 2026-09-16 — Work answer capture encounters observer timeouts

- The unchanged seven questions plus the authorized downloadable-report sentence
  were submitted once; the saved private prompt preserves the exact original
  prefix. Last supported activity says Drive-only retrieval finished and report
  artifact creation was underway, retaining the 16/17 ingestion limit.
- Two later read-only observations returned CDP transport timeouts before any UI
  state. No final answer or downloadable artifact was observed, and no download
  or repeated question prompt was attempted. These observation failures do not
  establish a provider-task failure or success.
- Root authorized one bounded observer recovery: preserve exact own handles,
  reset only that controller's CUA session, reattach the same owned tab and try
  a compact documented DOM read. No page reload, provider restart, resubmission,
  global browser controls or other-tab operation. If that also fails, stop browser
  retries and report question-result availability as unknown. Independent saved
  Drive audit continues within its existing read-only scope.

## 2026-09-16 — Final answer artifact recovered locally; index audit corrected

- Same-tab observer recovery returned the final seven-answer response and a named
  Markdown report. Several documented capture attempts did not return the file;
  a final download-event wait with a Library Download click was interrupted after
  exceeding seven minutes. No file path or bytes returned from that operation,
  and its partial local effect could not be inferred from the timeout alone.
- Root ended all browser retries, then authorized only an exact-filename local
  check. The expected report existed as an 11,819-byte regular file with creation
  and modification timestamps during the question stage. Its unchanged bytes
  were copied privately and compared exactly, without modifying the original or
  inventorying unrelated downloads. The absent browser receipt limits attribution
  to the interrupted call. The independent evaluator will verify question and
  citation correspondence before grading this candidate artifact.
- The saved-state evaluator corrected its first interpretation of derived roots:
  Entity/Topic routes use nested bucket `page_ids`. After the coordinator's
  contract check, it resolved all 24 referenced index pages. All 55 inspected shard
  references resolve to canonical records with current page hints. The earlier
  statement that there were no linked shards is withdrawn; this was an evaluator
  interpretation error, not a product defect or instance repair.
- Saved-state audit stands at 61 provider reads attempted and 59 complete receipts
  preserved; two initial entry reads were lost to the local evidence sink. No
  further broad reads are planned. Exact next action: finish source-semantic and
  seven-answer grading, publish the qualified findings and stop for joint review.

## 2026-09-16 — Work ingestion audit complete; question grading remains

- Actual saved state confirms 16 fully ingested emails and one not-ingested
  source with no linked Knowledge and one missing frozen substantive meaning.
  The provider explicitly kept the run incomplete. Six additional source-bound
  Task findings cover two unsupported obligations, one recurring-to-finite case
  with narrowed completion scope, one conditional-to-finite case, and two
  individual-completion cases collapsed to household state. No fixes were made.
- All 17 source metadata mappings and checked canonical/source references pass;
  94 locator entries, four nonempty catalogue entries, eight index-coverage
  entries, 24 referenced index pages and 55 shard references resolve with current
  checked identities/revisions. These structural passes do not qualify meaning.
- Largest saved data page: 34,714 bytes; largest compact record: 2,184 bytes.
  No 64 KiB overflow and no extra page-size trial. Audit cost/receipt counts and
  the corrected nested-index interpretation are retained above and in the report.
- The exact candidate answer file is now with the independent evaluator for all
  seven grades and citation/provenance checks. It requires no further provider
  reads. Exact next action: integrate those results, publish final continuity and
  stop for joint review before any product fix or new trial.

## 2026-09-16 — Second browser trials and audits concluded; review stop

- Both second attempts used fresh Sol controllers with separate contexts, tabs,
  packets and new Drive roots. Root serialized browser actions; no controller
  received the other's transcript or the evaluator's expected answers. The
  signed-in Chrome profile was shared, so account/profile isolation is not claimed.
- Spark failed its required canonical catalogue-route audit; no ingestion was
  requested into that failed setup. Work passed setup and saved 16 fully ingested
  emails plus one explicitly not-ingested source. The whole Work run is incomplete.
- Work's final saved-data audit has eight material finding instances: the explicit
  incomplete-source gap, six Task-meaning defects and one omitted response
  deadline. The last finding was exposed by Q2 and confirmed locally against the
  original source body and frozen receipt hash; it is not inferred from message
  timestamps. No evidence shows a retrieval miss from correctly saved deadline
  data, because the linked canonical records omit it.
- Seven answers graded five pass, one qualified pass and one fail. All 21 file
  citations resolve to the reviewed snapshot; Q7's record-level source support is
  weaker, and Q2 contradicts the source deadline. Query operation counts, tokens,
  costs and efficiency remain unknown; report links/self-description are not a
  measured trace. The recovered candidate file's browser-receipt provenance limit
  remains explicit.
- Final ingestion-audit I/O is 62 attempted Drive reads with 60 complete receipts;
  two early reads were lost to the evaluator's local sink. Current configuration
  root references were independently checked as the last read. All 24 referenced
  index pages resolve after correcting the evaluator's nested-root interpretation.
  The known frozen-source/JPEG and browser-observation limits are retained.
- Updated the active plan, results, protocol, artifact guide, coordinator handoff
  and whole-project coverage map so implementation and observed qualification stay
  separate. Runtime/starter files, failed instances and frozen studies are unchanged.
  Task-app writes, completion review, email/audio delivery, schedules, upgrades,
  broad suites and larger/year-scale behavior remain unexercised.
- Final publication uses only diff/privacy/document-link/Git hygiene and remote
  verification. Exact next action after publication: review all findings with the
  user. Do not repair bugs, clean up trial artifacts, or launch new tests without
  subsequent direction. The authorized bounded evaluation is complete; the
  School-OS product is not qualified for routine use.

## 2026-09-16 — Read-only root-cause review and three-route reconciliation

- The user requested a model/cost recommendation, clarification of the omitted
  fresh-Sol run in the last response, and diagnosis in the existing Spark and Work
  sessions. The prior final response summarized only the browser reruns; the
  original Sol ingestion and audit remain preserved and must be included in the
  combined account. No missing third run is silently created or rerun.
- User authority now permits read-only diagnostic conversations and existing
  evidence inspection. Request concise action/decision explanations supported by
  observable history, not hidden reasoning. Provider self-explanations remain
  claims until checked; no fixes, replay, new ingestion or provider effects.
- Work's existing isolated Sol controller prepared a bounded diagnostic prompt;
  an independent Sol reviewer is mapping proven divergences from local evidence.
  Root keeps browser leases exclusive and manages the Spark investigation without
  passing Work context to its controller. A retained agent-slot limit requires
  staging delegation rather than starting overlapping browser controllers.
- Exact next action: gather and cross-check the diagnostic reports, consolidate
  all three route outcomes and publish qualified causes and remaining unknowns.

- The independent local review is now in `ROOT-CAUSE-REVIEW.md`. It establishes
  Q2's source-to-Knowledge omission, propagation to Task and wrong answer; Q7's
  citation weakness; four Task findings first visible in Knowledge disposition
  and two in completion-subject derivation. These are proven output divergences,
  not proof of a hidden model mechanism. Sol and Work share the high-level Task
  pattern, while Work's recurring finding has an additional scope aspect.
- Work's old tab handle was unavailable. Its isolated controller reopened the
  exact existing conversation URL, verified the original history and absence of
  a prior diagnostic, submitted once and observed the response start. Subsequent
  bounded observations retain an active Stop control and no supported error.
  No completed diagnostic artifact has yet been captured. No new provider task,
  prompt replay, ingestion or fix occurred.
- A new isolated Spark controller was refused by the app's retained-agent limit,
  including after the local reviewer completed. The user was asked whether root
  may conduct a read-only Spark-only diagnostic directly. That answer is pending;
  Spark has received no diagnostic prompt and its prior evidence is preserved.
- A bounded second document review corrected a summary count, distinguished the
  repeated high-level pattern from Work's extra scope defect, and kept the image
  access question separate from explicit semantic requirements. Publication
  hygiene is limited to diff, privacy, document links, hooks/CI and Git state.
- This is an interim diagnostic checkpoint, not a completed root-cause phase or
  permission to fix. Exact next action: capture Work's existing response when it
  finishes; resolve the Spark controller choice; obtain/cross-check its diagnostic
  and return to joint review. Product/starter and trial instances remain unchanged.

## 2026-09-16 — Spark root-cause diagnostic completed

- After the user directed the Sol High coordinator to complete the Spark
  investigation, root reopened only the exact existing Spark task and submitted
  one read-only diagnostic prompt. No new task, setup run, ingestion, Drive
  mutation, external effect or fix occurred.
- Spark identified its retained generator as the earliest divergence: it created
  one page catalogue using the invalid `catalogue_root` family and assumed the
  concrete family/month and pending routes would be created during ingestion.
  The supplied storage and data contracts required those routes to be reachable
  at setup, so the interpretation was incompatible with the contract.
- Spark's readback checked its entrypoint, configuration and Entity locator. It
  established internal reference consistency but did not read back the catalogue
  or compare reachable routes against the contract. This explains why it claimed
  completion despite the independently confirmed saved-state failure.
- A chronology follow-up corrected Spark's initial overstatement: storage and
  the relevant data-contract section were read before generation, while identity,
  adapters, helpers and most operations were read afterward. It also recognized
  the existing system-file set only after generating/uploading instance JSON.
  Split reading remains a plausible contributor, not a proven technical cause.
- Archive corruption, Drive JSON conversion, unavailable files and connector
  error are not supported causes. Provider-reported generator lines are
  consistent with the saved output but the VM script itself was not acquired.
- Exact next action: capture and cross-check Work's existing diagnostic response,
  then publish the final no-fix root-cause accounting for joint review.

## 2026-09-16 — Work root-cause diagnostic completed

- The isolated Work controller observed the existing diagnostic finish and saved
  a privacy-safe normalized capture. A named downloadable artifact was visible
  and its Download control returned, but original bytes were not recovered at the
  expected path; no broad local scan was performed.
- Work confirms that Q2's deadline was absent before persistence, leaving the
  later Drive-only query unable to recover it. Q7 retrieved the relevant saved
  material but stopped at aggregate page/catalogue citations.
- Work attributes the Task failures to extraction/classification mistakes such
  as promoting guidance, flattening conditions/lifecycle and generalizing
  household scope. These explanations fit the output but remain retrospective.
  Its blanket attribution to Task derivation conflicts with stronger saved-state
  evidence: four divergences already occur in Knowledge, while two first occur
  in Task completion-subject derivation.
- No logged connector, write, truncation or context-limit failure explains the
  semantic defects. Structural checks compared generated payloads with persisted
  bytes and therefore could not establish source-semantic accuracy.
- The remote-image source remained explicitly not ingested. Work describes a
  derived third-party-fetch authorization boundary; reachability and authorization
  remain unknown because no fetch was attempted. Binary coverage correctly kept
  the source incomplete.
- Spark and Work diagnostics are now complete and cross-checked. No fix, replay,
  fresh source read or external mutation occurred. After publishing this no-fix
  diagnostic checkpoint, the exact next action is joint review with the user.

## 2026-09-17 — First remediation approvals recorded; implementation held

- The user dropped the proposed conversation/worktree experiment and is
  reviewing the published second-round remediation treatments one by one.
- The user explicitly approved both architecture recommendations: a temporary
  finite setup-route manifest over the existing concrete catalogue pages, with
  no persisted catalogue-of-routes schema; and one least-stateful read of a
  directly embedded substantive remote email image through an authorized route,
  represented as parent-email body content rather than an Attachment Group.
  Remote locators remain access aids, never identity evidence, and unavailable
  content keeps the whole Email `not_ingested`.
- The user explicitly approved T01 bootstrap contract validation. Its proposed
  standard-library helper consumes already-read saved page bytes and the
  temporary manifest, performs no Drive I/O or route selection, and returns
  `valid`, `invalid` or `insufficient_evidence` for the specified structural and
  reachability invariants.
- No T01 code, remote-image behavior, data-contract text, setup/storage recipe,
  fixture or starter package was implemented in this work unit. No test, trial,
  connector operation, instance repair or external effect was performed.
- Exact next action: continue recording the user's decisions treatment by
  treatment. Wait for an explicit instruction to implement before changing the
  approved product procedures, contracts, helpers, fixtures or starter.

## 2026-09-17 — Complete remediation package approved; implementation still held

- The user explicitly approved T02 through T19 in addition to the previously
  approved T01 and both prerequisite architecture recommendations. The full
  second-round remediation design is therefore approved as one cohesive package.
- T17 is approved with a specific constraint: do not require separate Chrome
  profiles, because an alternate profile would not have the user's signed-in
  Spark and ChatGPT Work services. Use separate agent conversations/sessions,
  controllers, serially operated tabs, Drive instances and evidence boundaries;
  disclose the shared signed-in profile and do not claim account-level or
  provider-memory isolation.
- This work unit records decisions only. No School-OS product code, procedure,
  helper, fixture or starter was changed; no test, trial, connector operation,
  instance repair or external effect was performed.
- Exact next action: wait for the user's explicit instruction to implement the
  approved remediation package. After implementation and publication, stop at
  the plan's retest authorization gate unless the user separately directs the
  retest.

## 2026-09-17 — Remediation implemented locally; publication review in progress

- The user supplied the separate instruction to implement the complete approved
  package, publish it and run fresh isolated Sol, Gemini Spark and ChatGPT Work
  setup and seven-day ingestion trials, followed by a comparative report. No
  additional readiness approval is required.
- T01-T19 and both prerequisite architecture decisions are implemented in the
  active contracts, operating instructions, setup entrypoints, standard-library
  helpers and fictional evaluation fixtures. Drive remains canonical; no queue,
  scheduler, database, lock, generic write-repair engine or second-model judge
  was introduced.
- The integrated deterministic suite passed 37 tests, Python compilation passed
  with a temporary bytecode cache, and privacy, Markdown-link and whitespace
  publication checks passed. These are local checks, not agent or connector
  qualification.
- An independent Sol integration review found pre-publication gaps in starter
  link packaging, strict bootstrap reference validation, evaluator continuation
  validation and stale trial-status text. These are being corrected before the
  implementation commit and do not count as trial findings.
- Exact next action: finish those pre-publication corrections, rerun the allowed
  local checks, commit and publish the exact starter, then start the authorized
  three-route retest. After the first trial operation, preserve new defects
  without repair and stop after the privacy-safe comparative report.

## 2026-09-17 — Remediation and immutable round-two starter published

- The independent regression review found all pre-publication blockers clear.
  The final deterministic suite passed 46 tests, Python compilation passed, and
  the privacy and staged-diff checks passed. No active repository hook or CI
  workflow was found that would trigger live testing indirectly.
- Published and remotely verified implementation commit
  `aae44ef13be8392130f9b5aec7889b040c0ca45b` on
  `codex/restart-implementation`.
- Built the starter from that exact commit. The archive contains 41 files and
  the empty instance/extensions directory entries. Its SHA-256 is
  `5cabbe0779c39a8ac547ee17ec8365cb0d244a95591cccc20658aab27e142f50`.
- Published the exact bytes as `School-OS-setup-round-2.zip` on the immutable
  `school-os-starter-2026-09-17-round-2` prerelease. A fresh release download
  matched the local archive byte for byte and reported the same digest.
- These checks establish publication integrity only. The exact next action is
  to upload those same bytes once to the authorized School OS Tests Drive area,
  create three new isolated destinations and run the already authorized fresh
  Sol, Gemini Spark and ChatGPT Work setup/ingestion trials. Once trial execution
  begins, preserve defects without repair and stop after the comparative report.

## 2026-09-17 — Round-two trials stopped at setup gate; 0 of 3 passed

- All routes received the same Drive-hosted immutable starter and distinct fresh
  Drive destinations. Spark and Work used separate controllers, conversations,
  serial browser operation and evidence areas within the user's one signed-in
  Chrome profile; account/profile/provider-memory isolation is not claimed.
- Fresh Sol discovered the starter, completed the interview and saved 67 files,
  including 35 JSON pages. Its independent audit preserved 55 of 55 Drive
  responses and found the saved Active Task and Completed Task history roles
  collapsed onto one undifferentiated empty Task locator. The finite manifest
  had 24 logical roles but 23 unique roots. The T01 helper incorrectly returned
  `valid` because its selector could not distinguish the two Task roles. Sol
  failed setup review and received no ingestion request.
- Spark received the setup prompt and interview answers but began source
  retrieval before setup completion or an ingestion request, so it was stopped.
  A controller top-level-composer mistake also created a second unintended task,
  which was stopped. Spark made no setup-completion claim; its assigned Drive
  root read back empty. Provider or methodological effects outside that root
  remain unknown.
- Work accepted the opening prompt and remained visibly working without showing
  an interview, completion, error or provider action. Browser control then hung,
  including one pending call for about 1,012 seconds. The controller was
  interrupted without retry; the assigned Drive root read back empty and the
  provider task's final state remains unknown.
- Result: 0/3 setup gates passed. Therefore no authorized ingestion, common
  questions, source-semantic audit or 64/128/256 KiB comparison ran. Sol's
  5,327-byte setup-page maximum is not canonical Knowledge/Task size evidence;
  retain 64 KiB.
- No product or instance repair, cleanup, retry loop, mailbox mutation, outbound
  effect, task-app write, audio or schedule occurred. The privacy-safe report is
  `docs/plans/restart/ROUND-2-TRIAL-RESULTS.md`. Exact next action: publish this
  report and return to the user for joint review. Proposed fixes and any further
  test require explicit approval.

## 2026-09-17 — Round-two findings published; joint-review stop

- Published the privacy-safe repository report and continuity update at exact
  commit `fe1f8d98b903cc030504582bf5a340ca086c3384` on
  `codex/restart-implementation`; the remote branch was verified at that exact
  revision before this final continuity entry.
- Published version 23 of the existing School-OS architecture guide. The
  self-contained results page is
  `https://school-os-architecture-guide.jeremieg.chatgpt.site/round-2-results.html`.
  The Sites deployment reported `succeeded`.
- Publication hygiene only: the updated Markdown links resolve, the privacy scan
  and diff checks pass, and the site page's local links and required result
  sections were checked. These are not functional product validation.
- Exact next action: stop for joint review. The follow-up proposals in the
  report are not approved. Do not repair, clean up, retry or run additional
  tests until the user explicitly directs the next work.

## 2026-09-17 — Round-two root-cause retrospective completed

- At the user's direction, conducted read-only retrospective follow-ups without
  resuming setup or ingestion, modifying Drive, repairing an instance or running
  another product test. Requests asked for concise decision summaries tied to
  visible records, not hidden chain-of-thought.
- Sol reports that it understood Active Tasks and Completed Task history as
  distinct roles but deliberately reused one Task locator because the available
  selector exposed no active/completed discriminator. That account matches the
  saved bootstrap and manifest. The validator separately failed to reject two
  logical roles sharing one root. Evidence is strong for the immediate failure
  and blind spot, but does not select the missing concrete representation.
- Spark's visible history proves a premature retrieval-labeled transition after
  the parent explicitly reserved mailbox use for later ingestion. Spark
  attributes it to treating future mailbox filters as current permission. That
  explanation fits the timeline but remains retrospective; visible history does
  not prove a Gmail request dispatched. The adjacent second task remains a
  separate controller/UI incident with an unresolved creation path.
- The exact Work task was subsequently located by its title, Work label and
  matching opening prompt. Its first response, marked at 58 seconds, contains
  the expected setup interview; no answer followed. Work reports temporary
  read-only starter inspection and no persistent or downstream action. The
  visible unanswered interview establishes a correctly pending setup; detailed
  tool activity remains a provider claim. The original controller missed the
  response while browser control hung, and that observation failure's technical
  cause remains unknown.
- The public retrospective is
  `docs/plans/restart/ROUND-2-ROOT-CAUSE-RETRO.md`. Exact next action remains
  joint review; no repair, cleanup, retry or additional trial is approved.
