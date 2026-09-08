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
