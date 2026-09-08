# School-OS 0.1.0-alpha.13 release plan

- Status: approved completion plan; M1–M3 require chained revalidation after the installer correction, and M4 implementation plus observed fresh-test-instance evidence remains
- Revision: 29, updated 2026-09-08
- Original snapshot: committed as `3acd660` on 2026-09-07
- Target release: `0.1.0-alpha.13`
- Specification inventory baseline: `main` at `4617215`, with `release.yaml`
  declaring `0.1.0-alpha.12`

## Purpose and authority

Capture the current ten-part proposal for deterministic, efficient, portable,
and resumable School-OS execution. At the user's request, this revision
incorporates the findings and scope recommendations from the
[simplicity review](REVIEW.md) directly into the work packages. The original
snapshot remains available in Git history at `3acd660`.

The two approved product decisions remain in force. The user has also approved
the complete-path development approach: connect one existing journey early,
verify its recovery behavior, then expand coverage. The selected alpha.13
completion target is a newly created empty private test instance under the
user's test parent. The existing private instance is read-only evidence for
source-domain and configuration discovery and must remain unchanged. This
revision records that approach as implementation milestones with deliverables
and completion checks.
The linked [implementation specification](SPEC.md) grounds those milestones in
the alpha.12 codebase and defines the implementation tasks, interfaces, state
transitions, migrations, and behavioral checks. M1–M3 have previously accepted
synthetic implementation, but their release claims are reopened for one chained
exact-package revalidation after the installer correction. M4-001's generic
adapter/plaintext/resource admission correction is implemented and awaits its
observed binding; M4-002 remains complete for its declared synthetic alpha.12
input. M4-003's repository safety
work is complete, but its required observed-surface evidence remains incomplete.
The existing-instance inventory reports an alpha.11 predecessor, whereas
M4-002 supports only alpha.12 input. Its alpha.12-compatibility audit found
native document source-catalog storage alongside raw Markdown, so it is
historical evidence only and is not the alpha.13 test deployment or a
release-acceptance migration.

The candidate Drive write-path review exposed an alpha.13 installation-contract
defect: the current local manifest requires its own post-create storage ID,
although the selected Drive create surface returns that ID only after bytes are
written. The repair is within the approved installation sequence: create and
verify immutable payloads first, then a non-self-referential content manifest,
then an immutable admission receipt, then the stable bootstrap. M1-004 and
M1-006 are reopened for this corrective validation; M2–M3 retain their accepted
synthetic behavior but require revalidation against the repaired installer.

The earlier inactive candidate read back its declared create-only generation,
but one preserved, excluded staging object prevents that root from establishing
clean-instance acceptance. It remains unchanged and is not reused. Independent
reconciliation of the source contract and implementation found that its
multipart block was overbroad: the canonical catalog owns the complete
plaintext string returned by the selected mail adapter, while MIME transfer and
charset decoding belong to the adapter and attachments have separate outcomes.
The smallest compatible correction admits one provider-designated complete
plain-text alternative after standards-conformant transport decoding, then
proves exact UTF-8 catalog equality. It still blocks HTML-to-text conversion,
HTML-only bodies, incomplete content, or ambiguous plain alternatives. Raw MIME
storage is neither required nor authorized for this path.

**Direct HTML resource correction (2026-09-08):** A bounded GPT-5.6 Sol High
read-only consultation found that direct image/PDF resources referenced by a
complete HTML MIME alternative are source material that cannot be silently
ignored merely because they have no mail-provider attachment identity. Under
the user's authorized complete source-coverage test scope, M4-001 may add only
direct, source-linked resource discovery and retrieval: preserve the HTML-part
identity/hash and occurrence locator; assign a stable resource identity and
`html_embedded` or `html_linked` origin; and keep original/extracted hashes and
an exact-text or page/region locator distinct. Fetches are bounded to those
exact URLs with redirect, byte, MIME/signature, and readback checks. No link
following inside a resource, arbitrary crawling, authenticated web navigation,
HTML-to-text conversion, or canonical raw HTML/MIME storage is allowed. A
decorative/tracking exclusion needs evidence; an ambiguous or unreadable
substantive resource blocks the affected import. A complete empty plaintext
body cannot establish message coverage while an embedded substantive resource
remains unprocessed.

The user has authorized the new test instance to ingest the last 14 days of the
grounded school-mail scope; execute real manual and temporary scheduled brief
email runs; create and exercise a Google Sheets task projection; and validate
Facts, guidelines, updates, actions, briefs, and task rows independently against
their sources. Exact private scope, recipient, schedule, and provider references
remain private. The temporary schedule must be verified inactive after the test.
No production instance or production schedule is part of this acceptance.

The user has deferred discussion of the review's historical-retrieval acceptance
case. That proposed addition is not part of the current work or release gates.
Existing historical-retrieval functionality and canonical-data requirements
remain product requirements; this deferral does not remove them.

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

## Development execution policy

This section governs development agents maintaining this repository. It does
not add a School-OS runtime requirement or authorize private-instance access,
provider effects, release publication, paid services, or production activation.

Development proceeds autonomously through the ordered authorized tasks and all
four milestones. A completed task or milestone is a recoverable checkpoint, not
a reason to stop or seek routine confirmation. On every resumption, compaction,
or environment reset, inspect `AGENTS.md`, `START-HERE.md`, this plan and its
linked specification, the relevant latest `PROGRESS.md` entries, branch,
worktree, history, and implementation/test evidence. Reconcile discrepancies
and continue from the first unfinished dependency; read narrowly after that
recovery rather than relying on conversation memory or repeatedly loading
unrelated history.

After every meaningful work unit, update task/milestone status in this plan,
implementation details in `SPEC.md` when needed, the root `PLAN.md` summary,
and append `PROGRESS.md` with completed and unfinished work, changed files,
validation, decisions, blockers, and the exact next action. Run meaningful
behavioral tests and privacy scans including new files, commit only accepted
in-scope changes, push to `origin/main`, verify the remote SHA, and then
continue immediately. Preserve historical entries and unrelated user changes.
Before a predictable execution limit, handoff, or blocked stop, leave a
recoverable progress checkpoint that identifies uncommitted work and any
publication failure.

If evidence shows the approved design is flawed, contradictory, infeasible, or
unsafe, stop the affected implementation. Record the reproduction and consult
one GPT-5.6 Sol sub-agent with High reasoning in a bounded, read-only role,
using fresh context containing this policy, task identifiers, relevant
plan/spec text, code references, violated assumption, reproduction, options,
and a specific decision question. Do not implement the disputed design while it
reviews. Escalate to one GPT-6 Astra High consultation only if Sol cannot
resolve the issue or identifies a fundamental architectural problem. Evaluate
advice against the approved constraints, record the finding and resolution in
this plan, `SPEC.md`, and `PROGRESS.md`, and resume automatically only when the
resolution remains in scope. A consultant cannot authorize new product scope,
incompatible architecture, private access, or external effects. Ordinary coding
mistakes and transient tool failures may be fixed directly; repeated failure
requires reassessment rather than indefinite workaround attempts.

Finish every repository task that can be completed under existing authorization,
including M4 work independent of unavailable real-provider evidence. Stop only
when all authorized implementation and applicable validation are complete and
remotely verified, or when a genuine blocker prevents useful authorized work.
Document blocked work precisely and do not mark it or its milestone complete.
At final stop, distinguish repository implementation from production conformance
and release readiness, and report milestones, validation, remote commit,
remaining work, and any exact decision or access needed.

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
module boundaries below are proposals, subject to implementation design. Extract
shared helpers as the connected use case needs them; a generic workflow engine
or a comprehensive set of abstractions is not a prerequisite.

## Simplicity findings incorporated in this revision

The documented household has one or two parents and low expected write
concurrency. Keep the checks needed for losslessness, determinism, and safe
recovery, while reducing machinery that creates no demonstrated benefit.

| Area | Current direction | Defer until justified |
|---|---|---|
| Routing | Small operation-to-recipe map, exact references, narrow dependencies | General instruction-packet compilation |
| Capabilities | Required functional probes and a few actionable limits | Exhaustive VM profiling and throughput optimization |
| Recovery | Sequential operation, compact checkpoints, pending-effect receipts | Worker pools, distributed lock services, general cancellation infrastructure |
| Formats and reconciliation | Supported canonical formats, field ownership, needed prior projection values | Arbitrary Markdown parsing and general multi-writer merging |
| Tests and metrics | Focused failure cases and representative performance measurements | Full vendor emulation and comprehensive benchmark infrastructure |
| Additional integrations | Independent work selected for concrete deployment needs | Making every new adapter or offline speech bundle a release prerequisite |

These are scope refinements. Source preservation, exact readback, provenance,
stable task identity, parent-edit preservation, and unknown-outcome handling
remain mandatory. Keep source interpretation separate from mechanical checks.
The agent handles routine recovery and targeted source re-reading; unresolved
meaning, required authorization, and real provider blockers receive concise
user-facing explanations instead of automatically becoming parent tasks.

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

- Add a small versioned operation-to-recipe map, for example
  `core/operations/registry.json`, with exact recipe references. Recipes retain
  ownership of dependencies, required capabilities, and allowed effects; the
  map must not become a second independently maintained policy definition.
- Update onboarding to populate exact private references for operation
  entrypoints. The stable bootstrap resolves the instance manifest, active
  release, selected operation, and relevant configuration.
- Implement a reference resolver that checks object identity, expected type,
  and permitted instance location. Recovery discovery uses scoped, paginated
  searches and stops on ambiguity.
- Resolve only the current operation's and phase's declared dependencies. Start
  with direct reads of the authoritative installed recipes. Defer a general
  operation-packet builder unless measurements show that repeated reads or
  instruction omissions remain material after direct routing is fixed.
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

- Extend `capability-profile.schema.json` with the small set of structured
  observations that changes execution decisions: complete reads/pagination,
  file transfer, local execution, relevant payload limits, and an execution
  budget when observable. Unknown values remain explicit. Exhaustive memory,
  process-lifetime, or network-topology introspection is not a precondition.
- Represent network paths separately: connector access, shell HTTPS access,
  package downloads, and external service access. Success on one path does not
  imply success on another.
- Separate relatively stable capability observations from current authentication
  health. Add minimal authenticated probes for integrations needed by the
  current operation, plus revalidation after relevant changes or failures.
- Use conservative configured record/byte bounds, constrained by observed
  limits. Add a simple bounded reduction rule after capacity failures and
  detect repeated non-progress. An oversized single source needs an explicit
  blocked or supported processing outcome, not truncation. Defer learned
  throughput optimization and a general resource planner.
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
- Persist a compact current operation snapshot remotely after bounded work
  units and before consequential external effects. Preserve the last verified
  checkpoint during updates. Reuse artifact references and effect receipts
  instead of introducing a separate journal or manifest for every helper.
- Implement guarded mutation helpers: read and validate current state,
  construct a candidate, check preservation rules, write through the adapter,
  read back, and record verification. Unexpected data loss fails validation;
  legitimate lifecycle changes remain possible.
- Record pending-effect receipts for sends, task creation, comments, and similar
  actions in operation state. Persist intent before invocation and treat
  unconfirmed attempts as potentially executed until provider reconciliation
  establishes the outcome. Reuse the delivery ledger and provider bindings for
  their existing permanent records instead of duplicating their authority.
- Implement recovery that checks release/configuration compatibility,
  reconciles unfinished writes, and returns the next safe step. Implement the
  sequential path first. General worker registries, pools, and cancellation
  infrastructure are deferred. If optional workers are later used, their
  operation ownership and superseded-result handling must be implemented then.

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
- Keep transport normalization in the mail adapter. MIME transfer decoding and
  declared-charset decoding may produce the adapter's Unicode plaintext body;
  the adapter must detect decoding replacement or loss and may use a complete
  provider raw read as verification input without making raw MIME a canonical
  artifact. For `multipart/alternative`, admit only one provider-designated,
  complete `text/plain` alternative. A separate attachment inventory never
  competes with the body. Multiple plausible plain parts, HTML-only or
  HTML-derived text, malformed/incomplete parts, or any unprovable decoding are
  explicit non-admitting outcomes.
- Select one bounded catalog representation for the initial implementation,
  preserving logical identities and source references. Physical volumes may
  reduce provider calls; a storage-layout optimizer and multiple interchangeable
  formats are deferred. Support the selected attachment extraction path through
  observed MIME/size capabilities, with explicit unsupported or incomplete
  outcomes. For every attachment the selected runtime reports readable in the
  test scope, preserve its attachment identity and the smallest source locator
  needed for attachment-derived Facts: an exact extracted-text span when
  available, otherwise a page/region locator into the provider attachment. Keep
  an original-content hash and extracted-text hash distinct, and claim the
  former only when the surface exposes the original bytes. Unselected extraction
  adapters remain independent extensions; that deferral cannot turn a selected
  readable attachment into a silent skip.
- Add structural coverage checks and omission warnings. Suspicious
  classifications trigger review; keyword matches do not automatically decide
  task meaning.

**Benefit:** Most copying and catalog assembly moves out of model output, while
semantic work stays focused on bounded source material.

**Impact if deferred:** Large imports remain vulnerable to sampling, identifier
corruption, missed attachments, and unverifiable completeness claims.

**Acceptance:** Fixtures cover multi-page discovery, embedded formatting,
multiple requests, negation, completed actions, attachments, decoded transfer
encodings and source charsets, alternative selection and ambiguity, decoding
loss, and interrupted publication. Every admitted Unicode body must still equal
the framed catalog text exactly and the persisted file must equal the intended
UTF-8 bytes.

## 6. Mechanical reconciliation of knowledge and canonical tasks

### Work and deliverables

- Implement parsers and serializers for the defined canonical catalog and
  register formats, with explicit migration for supported legacy forms. Add
  round-trip tests so parsing and rewriting preserve required information.
  Defer arbitrary Markdown interpretation.
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
- Keep conflict handling scoped to those supported fields and operations.
  Unresolved conflicts become explicit review cases; a general multi-writer
  merge framework is deferred.
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
  bounded operational coordination where necessary. A shared `idle` field
  alone cannot establish exclusivity. A distributed lock service is not a
  prerequisite for the household single-writer model.
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
- Package one default template and a small set of validated theme settings for
  colors, labels, and existing presentation choices. Keep recipients and
  provider configuration in their existing owners. Defer a layout engine,
  multiple template languages, and extensive customization controls.
- Emit rendered files and record their input fingerprints, template version,
  counts, and content hashes in the operation's verification evidence. A
  separate rendering-manifest subsystem is unnecessary.
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

- Build small fake adapters at the interfaces exercised by the connected path.
  Prioritize pagination, stale authentication, stale writes reported as
  successful, lost send responses, environment loss, and fresh-session
  recovery. Defer full vendor-environment emulation.
- Add end-to-end scenarios that restart the process and discard local storage
  between steps. Test operation outcomes and persisted artifacts instead of
  relying primarily on recipe-text assertions. Each stage must consume the
  actual output of its predecessor, including installed configuration and
  persisted references; separately prepared intermediate fixtures cannot
  substitute for the connected-path check.
- Maintain synthetic expected facts and task outcomes for semantic evaluation.
  Measure interpretation quality separately from deterministic assembly and
  recovery.
- Record a small baseline for representative onboarding, bounded backfill,
  daily-update, and no-new-message cases: observable input/output tokens, tool
  calls, bytes, elapsed time, and repeated work after interruption. Label
  unavailable or estimated values. Collect peak memory only when observable
  and useful; broad benchmark infrastructure is deferred.
- Create explicit migrations only for state, configuration, and record formats
  actually changed by this release. Reuse the existing staged-upgrade protocol,
  preserve compatible extensions, verify backups and migrations, and activate
  only after compatibility checks. Defer a universal migration framework.
- Treat fake-adapter tests as evidence of helper behavior. They do not establish
  production capability conformance; selected real execution surfaces still
  need observed validation before production claims.
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

**Scope:** Independent additions retain separate adapter IDs and contracts.
Google Sheets is now the selected required task adapter for the alpha.13 test
deployment and release acceptance. The remaining additions stay optional and
do not collectively become prerequisites.

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

**Acceptance:** Google Sheets passes its task-contract tests and observed
read/write/reconciliation checks on the test surface, including stable canonical
IDs, explicit parent-editable columns, completion behavior, exact row readback,
and duplicate prevention. Each other adapter selected for delivery passes its
applicable contract tests and observed capability checks. Unselected adapters
and the offline speech bundle do not block the release.

## Approved implementation sequence and milestones

Build and verify one connected implementation of an existing user journey
early, then expand it. The user approved this development approach after its
explanation. The ten work packages describe what changes; the milestones below
describe the order in which usable behavior and evidence are delivered. Do not
finish all infrastructure packages in isolation before connecting the journey.

M1's create-only implementation correction is present, but M1 clean-instance
acceptance is reopened. M2 and M3 retain accepted synthetic implementation,
but their chained revalidation against the repaired exact package is pending.
M4 now has authorized observed work on the new test instance. Completing
milestones 1–3 establishes the synthetic connected implementation with recovery
evidence; M4 supplies the actual semantic, authenticated, provider, presentation,
measurement, and release evidence.

### Milestone 1 — Install a minimal candidate in a clean test instance

**Status:** reopened for clean-instance revalidation (M1-001–M1-003 and M1-005
remain complete; the corrected M1-004/M1-006 implementation must pass from the
exact package in the new empty test root).

**Sequencing correction:** M1-003 precedes M1-002. M1-002 validates the
required registry and registry schema that M1-003 creates, so it cannot safely
run first. This correction preserves the approved fail-closed package gate and
stable task identifiers; it does not change product scope.

**Work and deliverables:** Select one existing runtime/provider combination as
the first conformance target. Define a small synthetic corpus containing a
school update, a standing guideline, and an actionable request, with explicit
expected source, knowledge, and task results. Build a candidate archive from an
exact commit and install it into a clean synthetic instance. Deliver the
installed validator, resolved configuration/references, minimum capability
checks, and a reproducible test setup. Start with fake provider adapters and a
send sink; reuse existing adapters and helpers where adequate.

**Completion checks:** The extracted package validates without Git or dependency
downloads. The installed operation can resolve its recipe, required private
configuration, and provider references without relying on the developer's
checkout or conversation. Missing required capabilities produce a specific
blocked result. Manual execution can qualify without a scheduler.

**Work-package coverage:** The portions of 1–3 and 9 needed to install and enter
this journey. Implement only the shared interfaces needed by the next milestone.

### Milestone 2 — Connect a complete normal operation

**Status:** synthetic implementation accepted but milestone reopened
(M2-001–M2-007 require one chained run from the revalidated M1 installation;
actual semantic/provider acceptance remains in M4).

**Work and deliverables:** Use the installed candidate to execute this sequence:

```text
Discover sources in the selected scope
  -> preserve the complete source bodies and verify the catalog
  -> reconcile canonical knowledge and tasks
  -> synchronize the configured task provider
  -> render and verify the brief
  -> send through the test sink and verify delivery
  -> persist completion evidence and the eligible cursors
```

Deliver the minimum executable helpers, recipe changes, and checkpoint/effect
records needed for that sequence. Use the manual entry point with a configured
task provider to exercise the approved no-scheduler path. Each stage consumes
its predecessor's actual persisted output; no manual repair or replacement of
intermediate artifacts is part of the passing test. Keep source interpretation
separate from deterministic assembly, with semantic expectations evaluated as
described in work package 9.

**Completion checks:** Verify source-body equality and persisted-byte readback,
source-linked canonical records, stable task identity and provider bindings,
the expected brief content, and confirmed test delivery. The completed operation
must account for every required phase and every source in the fixture's scope.
Changing inputs by hand between phases cannot make a failed scenario pass.

**Work-package coverage:** The connected portions of 4–8, plus installation,
routing, capability, and behavioral tests from 1–3 and 9. Unit tests support this
check but do not replace it.

### Milestone 3 — Prove recovery and safe repeated execution

**Status:** synthetic implementation accepted but milestone reopened
(M3-001–M3-006 require recovery/replay revalidation from the repaired installed
generation).

**Work and deliverables:** Extend the same scenario with focused failure cases.
Restart in a fresh process and discard the simulated agent's local files while
retaining the test instance's durable provider state. Exercise interruption
after a catalog write, during task synchronization, and after a send is accepted
but its response or completion checkpoint is lost. Also stop at a planned batch
boundary, resume in a new invocation, repeat unchanged inputs, and reconcile a
parent edit to an existing task. Deliver restartable tests and compact evidence
of the resulting canonical state, task bindings, and delivery receipts.

**Completion checks:** A fresh execution recovers from installed instructions
and durable state, verifies or reconciles work already performed, and continues
the same logical operation without duplicate tasks or sends. Confirmed work is
not blindly repeated, parent edits/history survive, and partial work is never
reported as complete. If a provider cannot resolve an uncertain effect, the
operation reports the specific blocker instead of guessing or retrying blindly.

**Work-package coverage:** Recovery and repeatability across 4–9. This milestone
is required before calling the initial connected implementation complete; a
successful uninterrupted run alone is insufficient.

### Milestone 4 — Expand coverage and establish release readiness

**Status:** in progress (M4-001 implementation complete pending observed
binding; M4-002 complete for synthetic alpha.12 input; M4-003–M4-009 pending or in
progress under the fresh-test-instance authorization; M4-006 remains the final
release gate).

**Work and deliverables:** Extend the working scenario to the complete 14-day
school-mail scope in the new test instance, repeated daily runs, supported
attachment cases, actual semantic interpretation, Google Sheets task
reconciliation, real manual and scheduled email delivery, manual/scheduled
duplicate-policy checks, materially different capability/network paths, and the
state or configuration changes that need an upgrade. Use the authenticated
runtime/connector path to invoke the checked-in helpers with actual predecessor
artifacts; `--stage-results` and canned interpreter output cannot establish this
path. Independently audit every in-scope source through canonical inventory and
each eligible brief/task projection. Record presentation checks and observed
execution budgets as the cases grow, then set checkpoint boundaries from those
observations. Deliver the applicable migrations, upgrade checks, conformance
evidence, package validation, and release results. Google Sheets is the selected
work-package-10 adapter; other additions remain independent.

**Completion checks:** Meet the acceptance criteria of all ten work packages for
the selected path. Verify one successful complete authenticated path as well as
negative cases; constrained execution; honest blocked/degraded outcomes;
preserved compatible extensions; and recovery across actual changed formats.
Compare source bytes/text, semantic inventory, derived views, Sheet rows, and
both delivered messages against independent evidence. Confirm scheduler
execution directly; an interactive trigger cannot substitute for it. Regress
the existing optional audio current-run-delta input even when audio delivery is
disabled, render and visually inspect representative HTML, validate the exact
package, and complete repository privacy and release checks.

**Work-package coverage:** Remaining scope in 1–9, plus only the selected items
from 10. This milestone distinguishes a working first journey from the release's
broader reliability and portability obligations.

### Completion coverage map

The ten approved work packages remain unchanged. The specification's stable
task IDs now cover their missing executable and observed acceptance:

| Work package | Remaining task coverage | Release acceptance |
|---|---|---|
| 1. Packaging/install | Revalidate M1-004/M1-006; M4-005/M4-006 | Exact package creates one clean admitted generation and later validates as the release artifact. |
| 2. Routing/isolation | Revalidate M1-003/M1-006; M4-003/M4-009 | A fresh invocation starts from the returned bootstrap and resolves only the new test instance. |
| 3. Capabilities/limits | Revalidate M1-005/M3-005; M4-003/M4-004/M4-009 | Synthetic measurement starts from existing implementation; current auth/network/limits are later observed per surface and determine final checkpoint boundaries. |
| 4. Checkpoints/recovery | Revalidate M2-001 and M3; M4-004/M4-009 | The connected path checkpoints actual bounded work, resumes from durable state, and reconciles uncertain effects. |
| 5. Ingestion/semantics | Reopen M4-001; add M4-007/M4-009 | The complete 14-day scope, including every selected readable attachment, is catalogued, semantically interpreted, and independently source-audited without canned results. |
| 6. Knowledge/tasks | Revalidate M2-003/M2-004/M3-003; M4-008/M4-009 | Canonical inventory retains every supported Fact; only action Facts project to verified Sheet tasks. |
| 7. Manual delivery | Revalidate M2-006/M3-004; M4-003/M4-009 | Real manual and scheduled entries use the same operation/delivery policy and produce no duplicate for one delivery key. |
| 8. Brief rendering | Revalidate M2-005; M4-005/M4-009 | Eligible source-linked content renders to verified HTML/text, passes visual checks, and preserves optional audio delta input. |
| 9. Tests/measurement/upgrade/release | Revalidate M1–M3; M4-002/M4-004–M4-006/M4-009 | Synthetic, package, observed, privacy, upgrade, and release-readiness gates pass with evidence kept in its proper owner; publication remains separately authorized. |
| 10. Selected adapters | M4-008/M4-009 | Google Sheets passes contract and real read/write/reconciliation checks; other optional adapters remain independent. |

Two presentation/delivery choices remain pending and must not be guessed: whether
the 14-day requirement changes ordinary brief eligibility or only the ingestion
and inventory-audit window, and the exact test recipient set. Until those are
resolved privately, source discovery, adapter implementation, synthetic tests,
package preparation, and non-delivery validation continue independently.

### Scope and purpose of this sequence

Installation is a lifecycle operation, not a phase to repeat before each daily
brief. The test setup and later daily operation remain separately authorized
operations, even though the development check connects their outputs.

Historical import remains a separate optional operation. An import must not
send mail or mutate a task provider without authorization for those effects.
A small development corpus is a test fixture, not permission to sample a
parent's requested import; production completion still covers its entire scope.
Provider boundaries remain generic throughout, and the first runtime does not
define the system's compatibility ceiling.

This sequence discovers integration defects early: configuration accepted by an
installer but unreadable by the next step, facts that cannot be reconciled,
lost parent edits, or delivery that cannot be resumed safely. If each subsystem
is completed in isolation first, these defects emerge later and can require
redesign of already-built abstractions. Omitting this sequence is not itself a
correctness violation; it raises integration, rework, and time-to-feedback risk.

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
- Keep the historical-retrieval acceptance addition pending separate discussion
  as requested by the user. Do not add a new retrieval work package or release
  gate in this revision.
- Reconsider deferred abstractions only when measured cost, repeated failures,
  or a concrete deployment justifies them. This remains a plan, not an
  instruction to implement every possible extension before shipping.

## Revision history

- Revision 1: captured the ten-part technical proposal and both approved product
  decisions; preserved in Git at `3acd660`.
- Revision 2: incorporated the simplicity review into the work packages and
  narrowed the proposed build sequence. Deferred discussion of the additional
  historical-retrieval acceptance case at the user's request. Implementation
  has not started.
- Revision 3: recorded the user's approval of the complete-path development
  approach. Defined four implementation milestones, their deliverables,
  completion checks, and work-package coverage; required real stage-to-stage
  handoffs in the connected test. Implementation has not started, and the
  additional historical-retrieval acceptance case remains deferred.
- Revision 4: linked the implementation specification grounded in the alpha.12
  repository. All four milestones remain pending; no runtime, manifest, release,
  or private instance changed. The additional historical-retrieval acceptance
  case and independent optional adapters remain deferred as previously approved.
- Revision 9: completed M2-001's operation-state/checkpoint contracts and
  validation. M2 is now in progress; M2-002 is next. The data-schema migration
  and alpha.12 compatibility claim remain deferred to M4 as specified.
- Revision 10: recorded the durable development execution policy: autonomous
  ordered implementation, evidence-based continuity/publication checkpoints,
  bounded design-failure consultation, existing authorization boundaries, and
  completion only at repository readiness or a genuine blocker.
- Revision 11: completed M2-006's provider-neutral adapter protocols and one
  shared manual/scheduled daily runner. Manual execution now qualifies without
  a scheduler; scheduled execution adds only its scheduler admission gate.
- Revision 12: completed M2 with an installed synthetic manual daily journey.
  Its persisted stage artifacts and recorded hashes are verified end-to-end;
  catalog substitution blocks before later effects. M3 recovery proof is next.
- Revision 13: completed M3-001's planned-boundary, durable-chain discovery,
  new-attempt recovery, and fresh-process local-work-loss proof.
- Revision 14: completed M3-002 catalog/index write-fault recovery with
  lossless re-verification, one-row adoption, Fact-ID preservation, and replay.
- Revision 15: completed M3-003 task/comment effect recovery and parent-edit
  preservation through canonical IDs, complete lookup, and review cases.
- Revision 16: completed M3-004 durable delivery intent and lost-send recovery;
  duplicate keys, ambiguous lookup, and correction variants remain guarded.
- Revision 17: completed M3-005 lifecycle safeguards for release/configuration
  drift, stale authentication, constrained capacity, non-progress, and
  terminal unknown effects.
- Revision 18: completed M3-006 with compact synthetic recovery evidence,
  recovery-contract/recipe documentation, and fresh child-process checks for
  catalog, task/comment, and delivery durable-state adoption. M4-001 is next.
- Revision 19: completed M4-001 complete-page enumeration, stable bounded
  import batches, no-new-message output regeneration, and explicit supported
  text/unsupported attachment outcomes. M4-002 migration work is next.
- Revision 20: completed M4-002's strict alpha.12 structured-state/task
  transformer, schema-2 candidate release metadata, migration procedure, and
  synthetic idempotence/blocker coverage. M4-003 conformance work is next.
- Revision 21: completed M4-003's repository safety preparation: synthetic
  network/auth/limit/overlap checks and an explicit observed-evidence gate for
  scheduled qualification. The required private runtime/provider/scheduler
  observations are unavailable under current authorization, so M4 remains
  blocked and dependent M4-004–M4-006 do not start.
- Revision 22: authorized read-only preflight found an alpha.11 private
  predecessor rather than the declared alpha.12 Migration 0002 input. A
  bounded GPT-5.6 Sol High consultation confirmed that direct alpha.11-to-
  alpha.13 support would change the approved upgrade boundary and needs new
  user approval. It also identified a missing source-version guard in the
  transformer; that in-scope fail-closed correction is covered by regression
  testing. No private file, provider, scheduler, or release was changed.
- Revision 23: the authorized read-only alpha.12-compatibility audit found
  native-document source-catalog storage in the alpha.11 instance. Alpha.12
  requires raw UTF-8 Markdown and direct byte-level source comparison, so the
  staged alpha.11-to-alpha.12 route fails closed. No content was converted,
  copied, or activated; an approved preservation mapping or explicit new
  alpha.11 migration scope is required before upgrade work can resume.
- Revision 24: a further authorized read-only check found that the alpha.11
  capability profile is scheduled-only and predates alpha.13's explicit
  `observed` evidence classification. It cannot qualify an attended upgrade
  surface or satisfy M4-003's runtime/scheduler evidence requirement. No
  private capability record or provider object was modified.
- Revision 25: recorded the authorized inactive candidate-only Drive/Gmail
  observation boundary and bounded GPT-5.6 Terra High review. Candidate work
  may collect only the specified storage/mail catalog and recovery evidence;
  all other M4-003 surfaces and dependent tasks remain incomplete.
- Revision 26: corrected the impossible self-referential create-only manifest
  sequence, reopened M1-004/M1-006, and required M2–M3 revalidation against the
  repaired installer.
- Revision 27: recorded the first candidate's multipart fail-closed safeguard
  and the excluded staging object that prevents clean-root acceptance. This was
  a conservative safety checkpoint, not a final interpretation of the older
  adapter-returned-plaintext contract.
- Revision 28: reconciled that contract with the implementation, selected the
  bounded adapter-side decoding/plain-alternative correction, and incorporated
  the authorized fresh test instance, 14-day import, actual semantic audit,
  Google Sheets task adapter, real manual/scheduled delivery, visual/audio
  regression, observed-budget checkpointing, and corrected release-task
  dependencies. The existing instance and earlier candidate remain unchanged.
- Revision 29: recorded the bounded direct-HTML-resource correction from the
  authorized GPT-5.6 Sol High consultation. It extends M4-001 source accounting
  only for exact image/PDF references in complete HTML alternatives and retains
  all no-crawler, no-HTML-conversion, provenance, and blocker boundaries.
