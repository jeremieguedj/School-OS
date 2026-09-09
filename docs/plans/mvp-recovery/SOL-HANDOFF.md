# New GPT-5.6 Sol High execution prompt

Copy the prompt below into a new GPT-5.6 Sol High session opened in the repository
checkout.

```text
Own and complete the School-OS recovery MVP specified in
docs/plans/mvp-recovery/PLAN.md. This is a fresh execution session. Work
autonomously through the fixed endpoint; do not stop after planning, a partial
implementation, or the first successful test.

First read AGENTS.md, START-HERE.md, docs/product-principles.md, root PLAN.md,
docs/plans/mvp-recovery/PLAN.md, the narrow latest PROGRESS.md entries, and the
relevant alpha.13 plan/spec. Then inspect actual Git branches, worktrees, refs,
history, modules, scripts, recipes, contracts, and tests. Read the gitignored
private/mvp-recovery/TEST-PARAMETERS.md and
private/mvp-recovery/ADAPTER-SOURCES.md. Those private files are authoritative
for exact test parent/root settings, approved recipients, domains, timezone,
task surfaces, schedule values, reference adapter sources, and audio settings.
Never copy their private values into Git, patches, public logs, or chat.

The current planning baseline says main/origin main at bc0128d contains the
accepted source/task/Sheets/brief primitives and phase splits. The stopped
connected candidate lineage is 9357733 -> d7f3ae3 -> 127219b -> cef9190 ->
e44c434. Treat that lineage as review input, not accepted truth. Reconcile all
candidate deltas against main and selectively integrate the smallest coherent
path. Preserve useful archived code/docs/tests but exclude rejected or
superseded implementations from active routing and the frozen package. Do not
assume an older tag, main, or the candidate branch already works.

Google Drive is always canonical for the installation, knowledge, Facts,
operation state, and tasks. Google Sheets and Todoist are editable projections.
There is exactly one selected task tool. Every task sync first imports complete
scoped parent changes/new tasks/comments/completion/reopen into Drive, then
refreshes the selected projection with stable identities and guarded readback.
The guided Sheets -> Todoist -> Sheets switch is configuration selection, not
software/data migration, and must preserve canonical IDs, relationships, parent
changes, and status without duplicates. Pull and canonically persist the old
selected provider, stage and verify the target projection while the old selector
remains active, then activate the target; failure leaves the old provider active.
Reuse dormant mappings when switching back. Use stable identity and last-sync
base/local/remote comparison; preserve parent edits and source provenance, and
mark ambiguous conflicts `needs_review` without overwriting. Reuse and sanitize
the user-reported working Todoist procedure supplied privately; do not invent a
second task model.

Reuse the existing ElevenLabs worker and the privately supplied reference recipe
and settings. The source was read during planning but this runtime path is not
yet live-qualified. Audio is MVP-required and follows this order: render and
validate HTML/text, reserve delivery, persist the current reconciliation delta,
generate and verify one `eleven_v3` Text-to-Dialogue MP3, send one multipart
email, verify exact Sent readback, then commit. Speak exact canonical run-delta
wording with configured per-group voices/tags and the fixed 2,000-character
prefix limit including opening/closing/tags. Validate every source voice against
the account; never silently substitute. Make at most one audio call and never
auto-retry an uncertain/failing call. Verify MIME/signature/nonempty bytes/hash.
Keep `ELEVENLABS_API_KEY` only in the runtime secret environment, never Drive.
Audio failure does not fabricate or roll back email/canonical success, but final
MVP acceptance requires one real verified MP3 in one of the two emails.

Only fresh installs are in scope. Create a new empty folder under the authorized
School OS Tests parent, a live isolated Sheet, and a live isolated Todoist
project. Read the supplied reference instance only for adapter/settings/domain
grounding. Do not
reuse an unfinished test root or old inventory, modify a production task
project, or touch a production School-OS instance. At execution start freeze a
new exact 14-day inclusive-start/exclusive-end window using the private timezone
and the same two private domains. Store exact values only in the private
companion/evidence.

Prioritize the first thin live path through an
admitted candidate package/bootstrap, a bounded real source batch, complete
custody/Facts, canonical task plus Sheets row, and rendered unsent brief. Compose
this preview from existing
import, task-sync, and render entrypoints: commit only completed source/task
operations and their eligible import cursor, leave delivery unreserved, and do
not claim a completed daily-send outcome. Do not send or bind Todoist/audio before
this early integration gate passes. There are exactly two allowed emails: the final full-
window manual and scheduled TEST variants. Never add a smoke variant, clear the
ledger, or change recipe content.

Check in with me after 60 minutes of elapsed wall-clock time from execution
start, regardless of progress. Include setup, helper work, tool calls, and
waiting. Record the start and deadline durably; do not reset the clock after
compaction, delegation, repairs, or phase changes. This replaces the old
90-minute target and four-hour autonomous cap.

The hour is a status checkpoint, NOT a completion deadline. Do not take shortcuts,
rush changes, remove scope, weaken contracts, skip tests or verification, reduce
live coverage, substitute synthetic evidence, or mark incomplete work complete
to fit it. Preserve all acceptance criteria and consultation rules. Report honest
partial progress when work remains.

At the checkpoint, stop starting new work, safely pause helpers, checkpoint
unfinished work and pending external outcomes, and report: verified outcomes,
what remains, blockers or decisions, and the proposed next step with estimated
time. Await my direction before continuing. Do not delay the report to finish a
milestone, test suite, or commit. Use bounded tool calls near the deadline; do
only necessary cleanup to avoid abandoning an in-flight write or leaving a test
schedule active, and report that cleanup separately. An authorized continuation
starts another one-hour check-in interval unless I specify otherwise.

Complete every E2E case in the recovery plan: exhaustive source inventory with
complete bodies/images/PDF attachments and bounded direct referenced assets;
source-linked queryable facts; brief content under the existing eligibility
recipe; manual send with no scheduler; Sheets and Todoist parent
add/edit/comment/complete/reopen; the guided switch; a real scheduled TEST run;
schedule disabled and independently verified inactive; duplicate replay;
pre-effect interruption and lost-response recovery; local-state deletion; and
fresh-agent/session continuation from Drive. Use independent expected-content
notes so generated output does not audit itself. The full inventory does not
mean every Fact appears in the brief.

Freeze a candidate package/configuration/interpreter for the early unsent thin
run. Bind Todoist/audio afterward, then freeze the exact final commit,
package/checksum, configuration fingerprint, dependencies, and interpreter
before the full 14-day/two-send chain. Determine any label from current refs and
manifests; do not bump merely to start. Changes to code, interpreter, source
bounds, policies, recipes, or the frozen test scenario require a rebuilt package
and new empty final root. Planned task edits, provider-selector switches,
cursors, delivery records, and temporary schedule creation/disable are recorded
mutable state and do not require reinstalling. Documentation-only changes do not
invalidate runtime evidence. Reuse independent source evidence only when
source IDs/window/bytes match. Prefer existing deterministic scripts and minimal
repairs; final outputs must come from the final installed package.

You are the single GPT-5.6 Sol High owner. You may use at most one Terra High
helper active for a bounded implementation/test task; use at most one later fresh
read-only content-correctness session. Do not create an independent review loop.
Use at most one
GPT-6 Astra consultation for one specific unresolved technical question after
recording the reproduction and options. If the plan is flawed, stop only the
affected path and request the real product/architecture/scope/access/budget
decision. Known test writes, provider reads, the two approved sends, temporary
scheduler, and private adapter reads are already authorized; do not ask the user
to approve them again.

Do not create goals, run production effects, add an upgrade path, broaden
provider/runtime matrices, create generalized workflow or parallel recovery
machinery, or start ongoing monitor/wait loops. Commit and push accepted
repository checkpoints as required by START-HERE.md. After every live gate
passes, the authorized release workflow may publish the exact same tested
immutable package and must verify tag/commit/manifest/asset/checksum readback;
this never authorizes production cutover. Keep
PROGRESS.md append-only in intent and update the recovery plan/root PLAN status
after meaningful work. Use focused tests and installed/privacy/reference checks;
the live E2E acceptance matrix is primary. Finish with the exact commit/package/
interpreter/config fingerprint, pass/block evidence for every case, schedule
inactive proof, private evidence locations, changed files, validation, and the
next action. Raw source and completed-task evidence remains private and durable
in Drive; ignored local receipts are convenience only. A blocked source or
failed/unavailable audio is a blocker, not a passing disposition. If an email
fault would require a third send, request specific authorization rather than
inventing a variant. Do not claim completion while any required live case is
open.
```
