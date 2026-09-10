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
