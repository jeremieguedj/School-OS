# School-OS recovery MVP plan and implementation specification

- Status: recovery implementation in progress; Phase 0 reconciliation is
  complete and Phase 1 hybrid live-ingestion qualification is active
- Written: 2026-09-09
- Release identity: record the early candidate in Phase 0 and freeze the final
  identity in Phase 2; do not assume that `main`,
  an older tag, or a published candidate branch is the final package
- Private companion: `private/mvp-recovery/TEST-PARAMETERS.md` and
  `private/mvp-recovery/ADAPTER-SOURCES.md` in the working checkout; both are
  gitignored and must never be copied into tracked files or logs
- Approved Drive storage contract:
  [`DRIVE-STORAGE-SPEC.md`](DRIVE-STORAGE-SPEC.md). It supersedes the active
  per-logical-file installation layout while preserving the recovery plan's
  domain semantics and live acceptance matrix.

## Outcome and fixed endpoint

Deliver the smallest fresh-install School-OS that proves one complete household
journey on the authorized test surfaces:

1. install an exact frozen package into a new empty folder under the authorized
   School OS Tests parent;
2. freeze a new inclusive-start/exclusive-end 14-day source window at execution
   start and ingest every message in the private companion's two-domain scope;
3. preserve complete email bodies, supported attachments, and bounded directly
   referenced PDF assets with provenance; inventory every image but terminate it
   as `excluded_by_policy` without fetching, interpreting, or creating Facts;
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

For the current MVP qualification only, the user has explicitly selected a
temporary all-image exclusion policy. MIME attachments matching `image/*` and
direct resources discovered as `html_embedded` remain visible in the canonical
source inventory as `excluded_by_policy`, with their source identity and
provenance, but are not downloaded, sent to image extraction, added to semantic
packets, or converted into Facts. Text and PDF processing are unchanged. The
existing image fetch, verification, MIME/signature, and extraction code remains
available but inactive. A later include/exclude policy for meaningful images
versus decorative headers and footers is deferred until after the MVP is proven.

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
| `school_os.connected_ingestion.ConnectedIngestionWorker`, candidate `school_os/connected_sources.py`, `scripts/run_source_host.py` | Bind the frozen `[start,end)` search, full/raw Gmail reads, complete bodies, attachment bytes, bounded PDF resources, the temporary pre-fetch all-image exclusion, persisted Facts/audit, and continuation. Retain the inactive image pipeline and existing custody/semantic validators. |
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
test sends, temporary scheduling, or adapter reads. Pause for a real missing
decision, unavailable authorization/capability, or required architecture change. Do not create goals or
production effects. Repository commits and pushes are required continuity steps
for accepted work. A release may be created only after all live gates pass using
the exact same immutable tested package and the user-authorized release workflow;
it never activates production. Do not run continual monitor/wait loops.

The current user-authorized continuation has no wall-clock checkpoint. Proceed
through execution and validation of live ingestion. This removes only the former
timed reporting interval; all safety, evidence, privacy, scope, and acceptance
requirements remain unchanged. Stop and consult the user if progress requires an
architecture change.

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

**Status: complete.** Candidate code and tests are reconciled in
[`RECONCILIATION.md`](RECONCILIATION.md); exact package freeze and live-gate
preparation remain. Inspect `main`, all named candidate commits/branches,
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

### Phase 1 — storage simplification and early live integration

**Status: in progress.** The preview handoff repair is complete at `a654f048`.
The approved five-file hybrid Drive layout and MIME-accounting source boundary
are implemented; the current four-day compatibility journey is exercising an
exact installed package before the final 14-day acceptance root is frozen.
The subsequent live replacement attempt exposed structurally excessive Drive
calls and generic connector failures before source work. The approved
[`DRIVE-STORAGE-SPEC.md`](DRIVE-STORAGE-SPEC.md) now replaces the per-file
installation with five initial physical files and binds the task projection
after admission. This executable/contract change requires a rebuilt package and
new empty root before the early preview resumes.
The exact `b8e69183` package passed five-object installation, post-install Sheet
binding, cold Drive recovery, and installed-package verification. Its live
ingestion then reached a direct HTTPS resource whose server-proven byte length
exceeded the frozen per-resource bound. The source contract already admits the
visible `excluded_by_policy` terminal outcome for an oversized bounded resource,
but the connected adapter raised before producing that outcome. The active
compatible repair carries a typed, provenance-bound policy exclusion through
the existing importer and catalog path for both declared and observed overflow;
it reads no body after a declared overflow and produces no inferred Fact. It
does not change the frozen bounds, source scope, storage layout, canonical
references, or provider architecture. Contradictory, malformed, or incomplete
responses remain blocking. A rebuilt package and new empty root are required
before Phase 1 live evidence can be accepted.
The user subsequently authorized a temporary current-MVP source-policy change:
all image MIME attachments and HTML-embedded image resources are inventoried as
`excluded_by_policy` before provider fetch or extraction. The image processing
implementation is preserved for a later selective source policy. This frozen
policy change requires another exact package and a new empty root; it does not
change storage, canonical references, task semantics, or provider architecture.
Live qualification of that package proved the image policy before encountering
a separate direct PDF. Exact-byte private diagnosis established that the PDF
was complete, valid, unencrypted, one page, within every byte/page/geometry/
pixel bound, and free of unsupported embedded-file features. The only failing
property was the local page renderer exceeding the shared 10-second timeout;
the same page rendered and reached the extraction callback in about nine
seconds when given a wider bound. The compatible repair keeps the 10-second
HTTPS deadline and adds a distinct bounded 30-second per-page PDF-render
deadline. This is an implementation defect correction within the existing PDF
custody path, not a storage, source-policy, provider, or architecture change.
A rebuilt exact package and another new empty root are required before Phase 1
live evidence can be accepted.
That rebuilt package passed the PDF-render gate and independently audited the
first eight conversations, then stopped before the ninth conversation's
semantic step because a supported MIME PDF attachment exceeded the configured
per-unit byte bound. The provider advertised a complete downloadable original;
the declared size is below the already-qualified finite source-host and bridge
ceilings, and the approved source-bundle limit can preserve it. Diagnosis found
that connected composition used the configured bound for admission while the
exact-byte adapter retained an unrelated smaller default. The compatible repair
constructs the byte adapter with the same configured finite bound. For the next
fresh scenario, freeze a private configured value no larger than the existing
qualified host ceiling and large enough for the observed attachment. This
changes package/configuration bytes and therefore requires a new empty root; it
does not change source meaning, storage layout, provider contracts, or
architecture.
The rebuilt package then passed the five-file install, generation-2 Sheet
binding, and cold recovery, and the attachment reached the connector. Two
independent live attempts reproduced one exact response-shape mismatch: the
declared flat attachment fields also include a redundant nested
`structuredContent` copy. The active compatible bridge repair strips that
wrapper only when the inner and outer declared fields agree exactly;
conflicting, malformed, or otherwise surplus fields remain blocking. Focused
and complete validation pass. Because executable package bytes changed, another
new empty root is required before live acceptance can resume.
That exact rebuilt package subsequently passed a new five-file install,
generation-2 Sheet binding, cold recovery, and installed validation. Its live
run did not reproduce the surplus-field rejection; instead, the first Gmail
attachment call returned a connector-level tool error without a usable
attachment result. No canonical publication occurred. Preserve sanitized
private failure details on the next bounded read before deciding whether any
runtime repair is needed; rate limiting remains unproven.
A bounded diagnostic read succeeded without any provider error fields and
identified the remaining exact mismatch: the nested copy can include three
connector-only transport fields in addition to the matching declared fields.
The compatible repair now validates and removes only that finite transport
shape, retains fail-closed disagreement and unknown-surplus checks, and records
the complete raw connector outcome privately on later errors while showing the
running agent a sanitized machine diagnosis and evidence path. This changes
executable bytes, so live qualification resumes from a new empty root.
The user authorized that immediate requalification as a four-local-calendar-day
inclusive ingestion window (today plus the preceding three days, with an
exclusive start-of-tomorrow end) in the private configured timezone. Freeze the
exact bounds only in private evidence and keep the temporary all-image exclusion.
This is a bounded live compatibility gate; it does not replace the recovery
MVP's final 14-day acceptance case.
The subsequent four-day run isolated a broader normal-email compatibility
defect: the adapter flattened one `multipart/mixed` message and treated a
full/raw-verified whitespace-only plaintext padding leaf as a second competing
body. The user approved the bounded `mime-accounting-v1` source-contract repair
recommended by the single Astra consultation. Exact message bytes, complete
full/raw reconciliation, stable identities, limits, provenance, independent
audit, and cursor gates remain strict. MIME structure is instead traversed
deterministically with every node assigned one audited disposition; every
substantive admitted text unit is preserved and interpreted, while verified
padding and exact same-alternative duplicates remain byte-accounted no-Fact
units. The primary body is only a presentation alias and cannot hide other
content. This change is confined to Gmail normalization, source catalog/schema,
semantic packet/audit, and connected ingestion/publication validation. It adds
no Drive object, provider framework, migration, HTML conversion, calendar
semantics, or storage-layout change. Fresh installs only remain in scope.
The exact `263b152` package has now passed a new five-file installation,
generation-2 Sheet binding, cold recovery, and the complete privately frozen
four-day source batch. Drive generation 3 contains eight audited catalog
records, eight exact raw messages, and 19 source-linked Facts; image fetches
remained at zero. A second cold recovery revalidated the committed state and
source bundle. The checkpoint truthfully remains at `reconcile`, with the
eligible source cursor unchanged; task projection and unsent brief rendering
remain required before the Phase 1 gate can close.
The first continuation attempt then proved the Sheet task write occurred but
found a contract-equivalent empty-value mismatch during exact readback: Google
Sheets omitted the blank `Source Due` CellData (normalized as null) while the
managed projection represents an unset source deadline as the empty string.
The durable unknown-effect checkpoint and recovery conflict guard worked as
designed and did not create a duplicate. The adapter now normalizes only that
optional empty field and includes a provider-shaped regression. Because
executable code changed, the attempted root is evidence only; rebuild the
package and start another new empty root.
For the later final recovery acceptance, use the Phase 0 `window_start_ms` and
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

**Gate:** one source must be traceable from provider identity through complete
catalog content and a Fact; one action must have the same canonical ID in Drive
and Sheets; and the stored unsent brief must be deterministic. No fabricated
success and no import cursor advance before all bounded
source work has durable evidence. This is early integration evidence, not
completed delivery, audio, or full-window acceptance.

The live Drive adapter may accept the finite provider-reported MIME set
`application/octet-stream`, `application/gzip`, or `application/x-gzip` only
for the pinned `system/package/release.archive`, and only when its bytes have
the gzip signature and match the already-frozen package size/hash. Persist the
provider's actual MIME in the object reference. Every other managed object
retains exact MIME matching. Drive create/readback failures must identify the
specific failed identity, kind, name, parent, MIME, URL, or byte predicate.

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
