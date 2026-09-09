# School-OS recovery MVP plan and implementation specification

- Status: recovery specification ready; implementation stopped pending a new
  GPT-5.6 Sol High execution session
- Written: 2026-09-09
- Release identity: record the early candidate in Phase 0 and freeze the final
  identity in Phase 2; do not assume that `main`,
  an older tag, or a published candidate branch is the final package
- Private companion: `private/mvp-recovery/TEST-PARAMETERS.md` and
  `private/mvp-recovery/ADAPTER-SOURCES.md` in the working checkout; both are
  gitignored and must never be copied into tracked files or logs

## Outcome and fixed endpoint

Deliver the smallest fresh-install School-OS that proves one complete household
journey on the authorized test surfaces:

1. install an exact frozen package into a new empty folder under the authorized
   School OS Tests parent;
2. freeze a new inclusive-start/exclusive-end 14-day source window at execution
   start and ingest every message in the private companion's two-domain scope;
3. preserve complete email bodies, supported attachments, and bounded directly
   referenced image/PDF assets with provenance;
4. create source-linked, queryable Facts and canonical Drive tasks;
5. import parent changes and new/completed/reopened tasks from the one selected
   task tool into Drive before refreshing any task projection;
6. prove Google Sheets and an isolated Todoist project as interchangeable
   editable projections of the same Drive task IDs, using a guided switch that
   loses neither status nor parent edits and creates no duplicate canonical task;
7. send exactly one manual and one real scheduled test brief only to approved recipients,
   verify duplicate suppression, then disable and verify the temporary schedule;
8. generate a live ElevenLabs audio brief by the existing ordered delivery recipe;
   audio may fail independently, but success may be recorded only from a real
   verified artifact/provider result; and
9. prove replay, interruption recovery, and continuation by a fresh agent from
   durable Drive state.

The endpoint is fixed when the package/configuration/interpreter are frozen.
Do not add acceptance criteria during execution except to reflect a direct user
requirement. The MVP ends with a disabled test schedule, retained private test
evidence, no modification to any production task project or production School-OS
instance, and an explicit pass/block result for every case below.

## Scope and invariants

Google Drive is always canonical for installation, source custody, knowledge,
Facts, operation state, and tasks. Google Sheets and Todoist are editable
projections. A task-tool read happens before the canonical reconciliation and
before any outbound projection refresh. Drive adopts supported parent additions,
title and planned-date edits, comments, completion, and reopen events using stable
canonical/provider identities. Source due dates do not become provider reminder
dates. Project sections or grouping labels remain distinct from workflow state.

Exactly one task tool is selected at a time. Switching tools is a guided
configuration operation, not a data migration: read and reconcile the old
selected tool, freeze its final provider state, select the new tool, then project
the existing Drive register into it. Switching back repeats the same procedure.
No title matching, synthesized task URLs, unscoped provider mutation, or
dual-provider writes are allowed.

The source inventory and brief have different purposes. Inventory acceptance
requires every source and supported content unit to have a disposition. The brief
uses the existing daily eligibility recipe, including the approved Parent-added
tasks exception. It must not dump every preserved Fact merely to demonstrate
coverage. Facts and knowledge remain source-linked and queryable independently of
brief eligibility.

Only fresh installation is in scope. Defer upgrades, migration of old private
instances, broad runtime/adapter matrices, generalized workflow engines,
distributed recovery, parallel workers, and ongoing monitor models. Preserve
archived implementations, worktrees, branches, documentation, and useful tests as
historical evidence; exclude them from active routing and the frozen release
rather than deleting them preemptively.

## Grounded repository baseline

At planning time, `main` and `origin/main` are
`bc0128d8335df9c12805c15ee7abca004fb62f35`. They contain the accepted v2 brief,
Gmail MIME normalization, source custody and semantic packet/audit logic,
connected ingestion discovery/catalog phases, canonical task reconciliation,
Google Sheets projection, exact reconcile-to-task-sync handoff, delivery
primitives, package verification, and deterministic tests. The relevant accepted
modules are:

| Responsibility | Existing implementation to retain and minimally repair |
|---|---|
| Package/install | `school_os.package`, `school_os.install`, `scripts/build_release.py`, `scripts/verify_release.py`, `scripts/validate_installed.py`, `scripts/scaffold_instance.py` |
| Routing/recovery | `school_os.references`, `school_os.operations`, `school_os.daily`, `scripts/run_operation.py`, operation-state/checkpoint schemas |
| Source custody | `school_os.gmail_source`, `school_os.catalog`, `school_os.importer`, `school_os.semantic`, `school_os.connected_ingestion` |
| Canonical tasks | `school_os.tasks`, `school_os.connected_tasks`, task/register/provider schemas and `core/contracts/tasks.md` |
| Sheets | `school_os.sheets`, `school_os.connected_sheets`, `adapters/tasks/google-sheets.md` |
| Brief/delivery | `school_os.brief`, `school_os.delivery`, daily/manual/brief recipes and templates |
| Audio | `automation/audio-brief/elevenlabs_audio_brief.py`, its manifest example/tests, and `adapters/audio/elevenlabs.md` |
| Validation | current deterministic tests, `scripts/validate.py`, `scripts/privacy_scan.py`, and `scripts/measure_synthetic.py` |

The connected end-to-end composition is not on `main`. The candidate lineage
`9357733 -> d7f3ae3 -> 127219b -> cef9190 -> e44c434` adds connected bootstrap,
setup, source byte/extraction adapters, a seven-phase daily runner, installed
entrypoints, complete Drive pagination, benign Drive receipt-URL normalization,
capability-profile readmission, exact time bounds, separate manual/scheduled test
variants, and durable fresh-process resume. That lineage is a stopped candidate,
not an accepted base. Older bootstrap/source branches are inputs to its history,
not additional implementations to stack blindly.

The private reference installation contains working Todoist and ElevenLabs paths.
Use it read-only through `private/mvp-recovery/ADAPTER-SOURCES.md`. The installed
Todoist recipe is richer than the tracked reference: it reads active, completed,
and bounded activity/comment streams; uses provider ID plus canonical marker
integrity; imports parent title, planned-date, comment, complete, and reopen
changes; and distinguishes section/group labels from workflow state. Sanitize and
port only behavior needed by this MVP. Its source Markdown is an exact reusable
procedure, not proof that a connected Python worker already exists. Reuse the
existing ElevenLabs worker and private adapter/settings rather than inventing a
replacement audio design.

The private audio recipe uses ElevenLabs Text-to-Dialogue with `eleven_v3`, its
configured per-group source voices and tags, and only the current reconciliation
delta. It speaks exact canonical wording without paraphrase and does not narrate
the rolling seven-day HTML brief. Its prefix is truncated at 2,000 characters
including opening, closing, and tags. Make at most one provider call per audio
effect and never auto-retry an uncertain or failed call. Verify a fresh MP3's
MIME, signature, nonempty bytes, and hash. Distinguish `skipped_empty`,
`unavailable`, and `failed`. Setup must verify every configured voice ID against
the account and may not silently substitute fallback voices. The credential
comes only from the runtime `ELEVENLABS_API_KEY` secret and is never stored in
Drive.

### Remaining code-change map

Names marked **proposed** do not exist on `main`; confirm the candidate before
creating them. Keep the authoritative semantics in the linked contracts and
recipes rather than duplicating them in a new framework.

| File or seam | Exact MVP deliverable |
|---|---|
| Candidate `school_os/connected_bootstrap.py`, `connected_setup.py`, `connected_profiles.py`; `scripts/setup_connected_instance.py`, `run_connected_operation.py`, `readmit_connected_profile.py` | Reconcile onto `main`; recover only admitted package/bootstrap/profile bytes; fresh create-only setup; finite operation routing; exact readback and profile selection. |
| `school_os.connected_ingestion.ConnectedIngestionWorker`, candidate `school_os/connected_sources.py`, `scripts/run_source_host.py` | Bind the frozen `[start,end)` search, full/raw Gmail reads, complete bodies, attachment bytes, bounded direct resources, image/PDF extraction, persisted Facts/audit, and continuation. Retain existing custody/semantic validators. |
| `school_os.connected_tasks.ConnectedTaskWorker` and `school_os.connected_sheets.CodexSheetsTaskPort` | Preserve `reconcile` as the Drive-canonical readmission step and `task_sync` as the exact provider handoff; keep last-sync conflict handling, guarded literal writes, lifecycle/history, and brief task view. |
| **Proposed** `school_os/connected_todoist.py` plus the existing generic task port/contract | Sanitize the supplied private procedure into a finite connected adapter: complete scoped active/completed/activity/comment reads, stable provider ID and canonical marker checks, parent-change import, bounded guarded effects, exact readback, and provider state. |
| Candidate `school_os.connected_daily.ConnectedDailyRuntime` | Replace the current hard-coded Sheets construction with one selector-dispatched task port. Ordinary runs read/write only the selected provider. Carry exact `reconcile` output into selected `task_sync`; retain all-current Facts/tasks for brief building and cursor-last commit. |
| **Proposed** thin guided-switch command in `scripts/` backed by a small function beside connected task selection | Final old-provider pull and Drive persist; stage/read back target projection; atomically activate selector only after target proof; retain dormant mappings for switchback; leave old selected if preparation fails. |
| `school_os.brief`, `school_os.delivery`, candidate connected daily delivery phase, `automation/audio-brief/elevenlabs_audio_brief.py` | Implement render/validate -> reserve -> persist current reconciliation delta -> one-call MP3 generate/verify -> one multipart send -> exact Sent readback -> commit. Record empty/unavailable/failed audio separately; keep email success independent while requiring one live MP3 for MVP. |
| `school_os.references`, `school_os.operations`, `school_os.daily`, `scripts/run_operation.py` | Route fresh manual, scheduled, task-sync, and guided-switch operations from installed references; recover phase outputs/effect receipts from Drive after process/local-state loss; reject substituted package/config/profile bytes. |
| `scripts/build_release.py`, `scripts/validate_installed.py`, release inventory | Package only the active fresh-install route and required assets. Keep upgrade/migration and superseded implementation files in Git for future use while excluding them from active operation routing; do not delete useful code. |

No broad new audit, raw-byte revision packet, workflow engine, or general adapter
registry is a deliverable. Add focused cases at the existing seams only.

## Execution ownership and controls

One GPT-5.6 Sol High owner drives the entire recovery, keeps plan status current,
and makes integration decisions. It may have at most one GPT-5.6 Terra High
helper active for a bounded implementation or test task; a single later fresh
read-only session may check content correctness. There is no independent
code-review loop. One GPT-6 Astra
consultation is optional only for a specific unresolved technical question after
Sol records the reproduction and viable options. Consultants cannot expand
scope. If the specification proves flawed, stop the affected path, record the
conflict, and request the actual product/architecture/scope/access/budget decision.

Do not pause for known authorized provider calls, private test writes, the two
test sends, temporary scheduling, or adapter reads. Pause for the mandatory
status checkpoint, a real missing decision, or unavailable authorization/capability. Do not create goals or
production effects. Repository commits and pushes are required continuity steps
for accepted work. A release may be created only after all live gates pass using
the exact same immutable tested package and the user-authorized release workflow;
it never activates production. Do not run continual monitor/wait loops.

Check in with the user after 60 minutes of elapsed wall-clock time from the
start of execution, regardless of the phase reached or amount completed. Count
setup, helper work, tool calls, and waiting; do not reset the clock after
compaction, delegation, a repair, or a phase change. Record the start and check-in
deadline in durable progress and consult the clock between bounded work units.
This rule replaces the previous 90-minute target and four-hour autonomous cap.

One hour is a communication checkpoint, not a deadline to finish the MVP or any
milestone. Preserve every feature, acceptance criterion, evidence requirement,
and consultation rule. Do not rush changes, skip verification, weaken contracts,
reduce coverage, substitute synthetic results, or claim incomplete work is done
to fit the hour. An honest partial result is the expected report when work remains.

At the checkpoint, stop starting new work, pause helpers safely, preserve the
exact unfinished state and any pending external outcome, and report to the user.
Give completed outcomes with evidence, unfinished work, blockers or decisions,
and the proposed next step with estimated time. Await the user's direction before
resuming. Do not postpone the report to finish a milestone, test suite, or commit;
report any necessary bounded cleanup separately. Avoid long blocking calls near
the deadline and do not abandon an in-flight write or leave a test schedule
running unintentionally. A user-authorized continuation starts a new one-hour
check-in interval unless the user specifies otherwise.

Freeze one candidate package/configuration/interpreter for the early thin run.
After its findings and the Todoist/audio bindings are complete, freeze one exact
final source commit, release label, package, configuration fingerprint,
dependency set, and interpreter before the full-window/two-send acceptance
chain. Determine the label from refs/manifests and choose the first unused
identity only if needed; no version bump is required merely to start recovery.
Runtime code, interpreter, frozen policies/recipes, source window, or declared
test-scenario changes require a rebuilt final package and new empty final root.
The selected-provider switch, parent task edits, cursors, delivery records, and
temporary schedule creation/disable are planned mutable test state with recorded
revisions; they do not invalidate the root or frozen scenario. Documentation-only
corrections also do not invalidate runtime evidence. Existing independent
source/expected-content evidence may be reused only when exact source IDs,
window, and bytes match; final installed outputs must come from the final package.

## Phases, deliverables, and stop conditions

### Phase 0 — reconcile and freeze the candidate

**Status: pending.** Inspect `main`, all named candidate commits/branches,
worktrees, history, current tests, and both private companion files. Produce a
short reconciliation ledger classifying each candidate delta as retain, repair,
supersede, archive-only, or reject. Start from `main`; selectively integrate the
smallest coherent connected path. Do not merge documentation status claims or
duplicate implementations wholesale.

As the first execution act, freeze the new 14-day inclusive-start/exclusive-end
source bounds in the private timezone and record them only in private evidence.
The early and final roots use those same bounds; never substitute the stale prior
test inventory.

Repair only demonstrated gaps. The expected composition seam is the candidate's
`connected_bootstrap.py`, `connected_setup.py`, `connected_sources.py`,
`connected_profiles.py`, `connected_daily.py`, and thin scripts, joined to the
accepted main modules above. Inventory the private Todoist and audio procedures
and identify their later binding seams, but do not delay the Phase 1 thin journey
to implement them.

Deliver one exact early candidate commit with a generated package and checksum,
installed validation, privacy scan, focused behavioral checks, and a recorded
interpreter/dependency fingerprint. Confirm every runtime entrypoint executes
from extracted package bytes and resolves only the admitted Drive root.

**Gate:** before creating test resources, verify the authorized parent and source
settings, recipient restriction, frozen source bounds, and installed-package
validation. Create only the new scoped test root and empty Sheet; record their
returned IDs and verify their scope before data writes. Do not require an ID
before the authorized creation that returns it. Todoist and schedule objects are
created and recorded in their later phases. A failed or ambiguous reconciliation
blocks the affected path.

### Phase 1 — early live integration

**Status: pending; first implementation target, without a completion deadline.**
The mandatory one-hour status checkpoint applies even if this phase has not
started or finished. Use the Phase 0 `window_start_ms` and
`window_end_ms` 14-day `[start,end)` bounds, recorded only in private evidence.
Use a new
empty folder under the authorized School OS Tests parent and an empty isolated
Sheet. Do not reuse any unfinished root or old inventory.

Run the smallest real manual journey through bootstrap, one complete bounded
source batch, semantic interpretation, canonical task reconciliation, selected
Sheets projection, deterministic brief render, and cursor-last commit. This
journey is an unsent preview composed from the existing import, task-sync, and
render entrypoints. Commit only completed source/task operations and their own
eligible import cursor; leave delivery unreserved and do not claim a completed
daily-send outcome. It must not consume a third smoke email, modify the two frozen
TEST variants, clear a delivery ledger, or change recipe content to manufacture
a send. It is acceptable for the first batch to
contain fewer sources than the full window, provided its bounded continuation is
truthful and every admitted source unit is processed. The manual run has no
scheduler dependency.

At the one-hour checkpoint, report the actual source, task, and preview outcomes
achieved so far and preserve the exact next action. Incomplete integration is a
valid status report; it does not justify relaxing this phase's acceptance gate.

**Gate:** one source must be traceable from provider identity through complete
catalog content and a Fact; one action must have the same canonical ID in Drive
and Sheets; and the stored unsent brief must be deterministic. No fabricated
success and no import cursor advance before all bounded
source work has durable evidence. This is early integration evidence, not
completed delivery, audio, or full-window acceptance.

### Phase 2 — finish bindings and freeze the final candidate

**Status: pending.** Add only the Todoist, selected-provider dispatch,
failure-safe guided-switch, and audio delivery seams in the code-change map.
Sanitize public adapter code; leave private values in the companion. Reuse the
existing task, delivery, audio, recovery, and validation helpers. Focused
behavioral checks must prove pull-before-push, last-sync conflict handling,
staged target activation, exact audio ordering, one-call uncertainty, and
email-without-fabricated-audio degradation.

Freeze the final source commit, package/checksum, interpreter/dependencies,
policies/recipes, source window, recipients, and declared test scenario. Record
the allowed mutable revisions: task/tool state and selector transitions, cursors,
delivery ledger, and temporary schedule. Install the final package into a new
empty final Drive root with new isolated Sheet and Todoist targets. Verify both
targets are empty and scoped before any projection.

**Gate:** exact installed validation and privacy checks pass; every entrypoint
executes from final package bytes; Sheets stays selected initially; target
staging cannot activate Todoist early; audio voices/secret capability and the
temporary scheduler surface are qualified or produce a precise blocker.

### Phase 3 — final-root inventory, tasks, switch, and manual delivery

**Status: pending.** Exhaust pagination for the frozen domain/time scope.
Full-read and exact-filter every hit; retain ordered thread membership. Prove
exact complete plaintext for each message. Inventory every provider attachment
and each bounded directly referenced image/PDF asset. Verify original bytes,
MIME/signature, size/hash, redirects, extraction/page or exact-text locator, and
read/fetch evidence. A substantive missing, ambiguous, unsupported, or unreadable
unit blocks acceptance; it is not a passing disposition.

Build Facts only from source-equal persisted content. Independently check every
source disposition, Fact wording/classification/provenance, relation, and expected
extraction unit. Keep expected-content notes independent of generated outputs.
Query representative Facts that are eligible and ineligible for the brief. Render
the existing-recipe brief from eligible updates, current guidelines, unresolved
finite tasks, and the approved Parent-added exception; inventory completeness
does not put every Fact in the brief.

With Sheets selected, prove source task creation and parent
add/edit/comment/complete/reopen. Import the complete scoped Sheet snapshot into
Drive first, then guarded-write/read back. Preserve relationships, completion
history, immutable IDs, and source provenance. Use stable identity plus
last-synced base/local/remote comparison; an ambiguous conflict becomes
`needs_review` and overwrites neither side.

Perform the guided switch: final Sheets pull and Drive persist; save its provider
state; stage and verify the Todoist projection while Sheets remains selected;
activate Todoist only after target proof. Failure leaves Sheets active. The
staged target write is the sole exception to ordinary single-provider writes.
Exercise the same parent lifecycle in Todoist using complete bounded active,
completed, activity, and comment streams. Pull to Drive before refresh. Switch
back through the dormant Sheets mapping without duplicate rows. A missing
required completion comment uses the existing reopen/reminder rule.

After final canonical readback, run the one manual TEST delivery in this exact
order: render/validate HTML and text; reserve delivery; persist current
reconciliation delta; generate and verify the run-delta MP3; send one multipart
email; verify exact Sent readback; commit. If audio fails, email/canonical state
may complete without a fabricated attachment, but MVP remains blocked until one
of the two emails contains a verified MP3.

**Gate:** every source case passes; inventory matches an independent listing;
every Fact resolves to source; expected brief inclusions/exclusions match;
Sheets -> Todoist -> Sheets retains the same Drive IDs, parent changes,
relations, and status exactly once; and manual HTML/text/audio equals stored
artifacts and independent expected content.

### Phase 4 — scheduled run, audio, replay, and interruption

**Status: pending.** Create one temporary schedule with the separate scheduled
TEST variant from the private companion. Let the real scheduler fire once. Verify
the scheduled run uses the same admitted package, frozen window, Drive state,
selected task tool, processing recipe, delivery ledger, and recipient allowlist.
Disable it immediately after the observed run and independently verify inactive;
leave unrelated schedules unchanged.

Select the earliest supported trigger at least five minutes ahead, with a
maximum intended delay of fifteen minutes. Record the trigger and a deadline
twenty minutes after it. If the run has not completed by that deadline, deactivate
the test schedule, preserve its observed status, and report the scheduled case
blocked. Use scheduler completion events or bounded status checks; do not keep an
expensive model polling while the clock advances.

Replay both manual and scheduled delivery keys and prove no duplicate. Exercise
at least one interruption before a task-write effect and one unknown task-write
outcome after provider acceptance using the existing runner/effect checkpoints,
without editing canonical state by hand or sending extra email. Discard local run
files and continue in a fresh process. Then start a fresh agent/session
from `START-HERE.md`, the stable bootstrap, and durable state; it must discover
the exact next action without conversational memory and complete or report the
same blocker.

The scheduled email follows the same ordered delivery sequence as the manual
email: persist the small current reconciliation delta across invocations,
render/validate, reserve, generate/verify the one-call MP3, send one multipart
email, verify Sent, then commit. Use existing focused failure checks or a
naturally observed failure for fallback evidence; do not build a fault-injection
framework or deliberately break secrets. An empty-delta audio skip is valid when
the recipe applies, but at least one of the two emails must include a real
verified MP3.

If a delivered-email fault would require a third test send, stop and request
specific extra-send authorization. Do not invent another variant. **Gate:** real
schedule fired once and is verified inactive; replay sends zero
duplicates; interrupted effects reconcile exactly once; fresh agent resumes from
Drive; Sheets/Todoist canonical identities remain stable; and live audio
succeeds at least once. Existing focused or naturally observed evidence confirms
independent audio degradation without making a deliberate live failure a gate.

### Phase 5 — evidence closure and handoff

**Status: pending.** Fix only defects required by the acceptance cases, rebuild,
and rerun the affected chain from a new empty root whenever package/config bytes
change. Do not broaden into upgrades or adapter matrices. Record the exact final
commit, package/checksum, interpreter, configuration fingerprint, new root,
provider evidence references, and pass/block matrix privately. Run focused
regressions, installed validation, privacy scan, link/reference checks, and a
diff review. Broad repository CI/test count is supporting evidence; the live E2E
matrix is primary.

Update this plan, root `PLAN.md`, and append `PROGRESS.md`. Keep rejected and
historical branches clearly excluded. Commit and push accepted repository
checkpoints per `START-HERE.md`. After every live gate passes, the authorized
release workflow may publish the exact same tested immutable package; verify tag,
commit, manifest, asset bytes, checksum, and remote readback. Release publication
never authorizes production cutover.

## Required end-to-end acceptance cases

| Case | Required observation |
|---|---|
| Fresh install | Complete empty-root proof, immutable package/admission/bootstrap readback, isolated Sheet/project, exact package execution |
| Complete inventory | Independent listing matches the frozen two-domain `[start,end)` scope; every body, attachment, and supported direct asset has a disposition |
| Facts and queries | Every Fact/source link resolves; representative eligible and brief-ineligible facts are queryable and content-correct |
| Manual brief | Existing eligibility rules, approved parent-added exception, stored HTML/text equality, approved recipient only, exact Sent verification, no scheduler |
| Sheets lifecycle | Stable IDs; parent add/edit/comment/complete/reopen pulled to Drive before guarded refresh |
| Todoist lifecycle | Same lifecycle using active/completed/activity/comment pagination and canonical marker integrity in one isolated project |
| Guided switch | Sheets -> Todoist -> Sheets preserves the same Drive IDs, parent changes, relationships, and completion state with no duplicates |
| Scheduled brief | Real scheduler fires once with its own TEST variant, exact delivery verified, schedule disabled and inactive afterward |
| Replay/recovery | Same delivery keys suppress; pre-effect interruption and lost response reconcile; local deletion and fresh agent resume from Drive |
| Audio | Real verified ElevenLabs MP3 from the persisted current reconciliation delta in one multipart test email; independent failure never fabricates or rolls back email/canonical success |

The compact live evidence trail must be readable in this order: independent
source inventory, source dispositions and Facts, canonical task/register plus
selected projection, brief input/render/delivery, audio result, operation
checkpoint/final evidence, scheduler inactive proof. Every source is covered,
while brief content remains governed by eligibility.

## Completion and blocker rules

Mark the MVP complete only when every required case passes on one frozen final
package/configuration chain. A real provider incapability, ambiguity in source
completeness, inability to preserve canonical task semantics, missing approved
recipient/access, failed live audio, or inability to disable the schedule is a
precise blocker. Stop the affected path, preserve durable evidence, and continue
independent in-scope work. Never weaken contracts, infer success, modify
production, or substitute synthetic evidence for a required live observation.
