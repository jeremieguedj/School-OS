# School-OS implementation plan

Status: recovery MVP implementation in progress; Phase 0 complete and Phase 1 fresh-install qualification active
Execution model: resumable. Every completed phase is recorded in `PROGRESS.md`.

## Next-release planning

Implementation is active under an explicit user-authorized continuation with no
wall-clock checkpoint; work proceeds through validated live ingestion unless a
required architecture change needs user consultation. The active recovery route is the
[recovery MVP plan and implementation specification](docs/plans/mvp-recovery/PLAN.md),
with a copyable [new-session Sol High handoff](docs/plans/mvp-recovery/SOL-HANDOFF.md).
It supersedes the alpha.13 completion sequence as the operational plan while
preserving the alpha.13 plan, specification, review, branches, worktrees, tests,
and history as implementation evidence. Resume only in a new GPT-5.6 Sol High
session. The recovery MVP starts from a fresh empty private test root, reconciles
the stopped connected-runtime candidates against current `main`, freezes one
exact package/configuration/interpreter, and proves Drive-canonical knowledge and
tasks through live Sheets, Todoist, email, scheduler, audio, and restart cases.
No runtime implementation, provider mutation, release, goal, or production
change was performed while writing this route; read-only private grounding was
used for the specification.

The user-approved [Drive storage simplification specification](docs/plans/mvp-recovery/DRIVE-STORAGE-SPEC.md)
is the current installation/storage authority. It replaces the active
per-logical-file layout with an immutable package, immutable settings,
immutable bootstrap, one mutable current-state pointer, and immutable bundled
state generations. Task projections bind after canonical installation. This is
a fresh-install contract change only; it does not add migration or weaken the
recovery MVP acceptance cases.

The user-approved [agent-managed task projection specification](docs/plans/mvp-recovery/TASK-ADAPTER-SPEC.md)
is the current task-integration authority. School-OS owns the canonical action
register, stable identities, two-way base/local/remote reconciliation, durable
effect authorization and provider selection. The user's instance agent owns
all Google Sheets, Todoist and other task-tool layout/native operations and
returns complete normalized snapshots and verified readbacks. The existing
fixed-layout Sheet implementation is reference evidence, not active generic
routing.

The installed `970d9b2` agent-task package completed the four-day compatibility
journey through Drive generation 9 and terminal `PREVIEW_READY`: eight complete
conversations, 13 source-linked Facts, two canonically confirmed agent-operated
Sheet actions, an immutable HTML/text output bundle, cursor-last completion,
and fresh Drive recovery all passed with image reads disabled. Delivery stayed
unreserved and unsent. Qualification then exposed two narrow defects: private
zero-Fact expectation notes were not themselves bound to the exact packet even
though the resulting canonical audit was, and repeated preview phases reused a
fixed local filename. Packet-bound expectation evidence and
generation-qualified preview filenames are now the active compatible repair.
Executable bytes change, so final qualification requires a rebuilt package and
a new empty root; the completed `970d9b2` root remains diagnosis evidence only.

The private execution values and unsanitized reference adapter receipts live
only in
gitignored `private/mvp-recovery/TEST-PARAMETERS.md` and
`private/mvp-recovery/ADAPTER-SOURCES.md`. They must not enter Git. The historical
alpha.13 status below is historical evidence of completed and stopped work;
where it describes the next execution step, the recovery MVP route above now
controls.

The current revised plan for the next release, `0.1.0-alpha.13`, is
[the alpha.13 release plan](docs/plans/0.1.0-alpha.13/PLAN.md). It records ten work
packages, deliverables, benefits, deferral impacts, and acceptance criteria,
including the approved manual-sender and cross-session continuation decisions.
Implementation has completed the repository safety portion of M4-003. The
create-only installer correction reopens M1-004/M1-006 clean-instance evidence;
M2–M3 require chained revalidation from that repaired generation. M4-001's
generic correction is implemented and regression-tested: it admits a strictly
decoded, provider-designated complete plaintext body and keeps attachments and
direct resources separate; ambiguous, incomplete, HTML-derived, or lossy
content still blocks. Observed binding and source acceptance remain M4-003/M4-009
work. No raw-MIME canonical architecture is selected.

Direct image/PDF resources referenced by complete HTML alternatives remain
separately inventoried source material. For the current MVP qualification, an
explicit user-authorized temporary policy marks all image MIME attachments and
HTML-embedded image resources `excluded_by_policy` before fetch or extraction;
text and PDFs remain active. The image pipeline is preserved for a later policy
that can distinguish meaningful images from decorative headers and footers.
Live qualification isolated an independent bounded-PDF defect: a valid one-page
document passed every existing admission bound but its local renderer exceeded
the shared 10-second timeout. The active compatible repair retains the network
deadline and gives local PDF page rendering its own 30-second bound; it requires
a rebuilt package and new empty test root, without changing architecture or
the temporary image policy.
The next live gate exposed a second bounded-source mismatch: a supported PDF
attachment was below the qualified connector/bridge ceilings but above the
selected per-unit bound, while the exact-byte adapter ignored that configured
value and kept a smaller hard-coded default. The active compatible repair uses
one configured finite byte limit for admission and fetching. The private test
scenario must freeze a sufficient value within the existing host ceiling, and
the resulting package/configuration requires a new empty root.
That rebuilt package passed five-file installation, post-install Sheet binding,
cold recovery, and the configured byte-admission gate. The next exact live
failure is an attachment connector-envelope mismatch: the connector supplies
the declared flat attachment fields plus a redundant nested
`structuredContent` copy. The active compatible repair removes that wrapper
only when the inner and outer declared fields agree exactly; conflicts and
other surplus fields remain blocking. This is bridge normalization within the
existing Gmail attachment contract, not an architecture change, and requires a
rebuilt package and new empty root before live evidence continues.
The rebuilt package and root passed install, Sheet binding, and cold recovery.
Its live run reached the attachment path without reproducing the surplus-field
rejection, but the first attachment connector call itself returned a generic
tool error with no usable result. The root remains at generation 2. Before any
retry, preserve a private sanitized connector-error envelope so the failure can
be classified as provider rejection, throttling, timeout, or transport error
instead of assuming a cause.
A bounded diagnostic read later succeeded and exposed the exact remaining
compatibility defect: the nested attachment copy can also contain three
connector-only transport fields. The bridge now projects only the documented
attachment fields, requires every duplicated declared value to agree, validates
the finite transport shape, and rejects conflicts or any new surplus. Connector
failures now retain the complete raw outcome in a mode-0600 private evidence
file while surfacing only status/reason/stage and its evidence reference to the
running agent. Focused and complete validation pass; a rebuilt package and new
empty root remain required for the next live run.
Every discovered direct resource must still be audited, excluded with evidence,
or block the affected import; no arbitrary link following, crawler,
HTML-to-text conversion, or raw-MIME canonical store is authorized.

The authorized completion target is a new empty private Drive test instance.
The existing alpha.11 instance may supply source-domain/configuration evidence
read-only and must remain unchanged; it is outside alpha.13's declared alpha.12
migration input and is not this release's test deployment. The fresh test path
must ingest the grounded last-14-day source scope, perform live semantic and
independent source-to-inventory-to-view audits, use the selected Google Sheets
task adapter, execute real manual and temporary scheduled test-email runs, and
verify duplicate suppression and schedule deactivation. Exact private values
stay outside Git. The earlier candidate with an excluded staging object remains
unchanged and supplies no clean-instance acceptance.

The [simplicity review](docs/plans/0.1.0-alpha.13/REVIEW.md) evaluates the original
snapshot against product personas and priorities. The current plan incorporates
those findings: narrow routing, conservative batches, sequential recovery,
supported formats, focused tests, and independent optional adapters. The
proposed additional historical-retrieval acceptance case is
deferred for separate discussion. The user-approved complete-path approach is
organized into four milestones: clean installation, a connected normal
operation, verified recovery, and broader release coverage. The release plan now
links the code-grounded [implementation specification](docs/plans/0.1.0-alpha.13/SPEC.md),
which defines stable tasks and acceptance checks. M1–M3 are reopened for
revalidation without discarding their accepted implementation history. M4-004
synthetic measurement and M4-005 package preparation no longer wait for
real-provider evidence; final M4-006 still does. M4-007's generic semantic
packet/audit implementation is complete pending its authenticated binding.
M2-003/M2-004/M3-003 and M4-008 have their bounded repository correction
integrated after independent source/parent reconciliation and hard-process-death
recovery checks. Chained exact-package revalidation, observed private-Sheet
acceptance, and M4-009 full observed-path
acceptance also remain.
The resolved test policy keeps ordinary daily-brief eligibility under the
existing recipe and sends both authorized test variants only to the approved
private recipient; those values remain outside Git. The corrected generic
M4-001/M4-007 source-custody and semantic-audit implementation is complete and
regression-tested; authenticated invocation, independent private accuracy, and
view projection remain M4-003/M4-009 acceptance work.
The recovery execution also found that the stable bootstrap handoff did not
forward the installed runner's manual-only unsent-preview mode. That finite CLI
handoff is being repaired and regression-tested before any source read; the
changed executable package will be rebuilt and installed only into a new empty
test root.
M4-004 now has a reproducible synthetic measurement command and measured
checkpoint-before-limit behavior refreshed against the corrected source path.
Its task-sync measurements now exercise the accepted durable effect callback
and continuation. Final runtime/brief integration still requires a refresh.
M4-005's repository release preparation is now integrated, including exact
remote asset verification, audio delta regression, and the ordinary-Python
package-cache correction. Actual CI, remote release, visual, connected daily
worker bindings, and private acceptance remain open. The user approved a narrow
provider-independent recipe exception: eligible user-added tasks without an
email received date appear under Parent-added tasks in their ordinary action
section, with no invented date or link. Source-origin date requirements remain
strict. Brief implementation and acceptance can now resume.
The original snapshot remains in Git.

## Objective

Build a reusable, privacy-safe School-OS whose generic source is maintained in GitHub and whose installed runtime executes from a user's Google Drive. Private configuration, knowledge, task records, credentials, and runtime state never enter this repository.

The minimum transport path is manual: a user downloads a tagged release and shares it with an agent. GitHub access is optional for an agent and is never required by a scheduled production run.

## Frozen architecture baseline

The architecture is governed by the approved frozen plan of September 2, 2026:

- GitHub holds reusable system source.
- Each user installs a pinned release into Google Drive.
- Google Drive holds the active runtime plus all private configuration, data, and state.
- Scheduled/manual runs resolve a stable Drive bootstrap and execute only the active installed release.
- Core behavior is separate from runtime and provider adapters.
- Drive is the canonical task and knowledge record; a task provider is the user-facing interaction surface.
- The system is tool agnostic through explicit capability contracts and selected adapters.
- The core must work sequentially without GitHub access, subagents, or a specific AI vendor.

Deferred adversarial-review findings are captured separately in `docs/deferred-adversarial-review.md`. They must not change the frozen baseline without explicit approval.

## Execution phases

1. **Foundation** — create repository entry points, governance, plan/progress tracking, privacy rules, and a generic repository skeleton.
2. **Core contracts** — define the portable data, capability, and configuration contracts; establish one source of truth for each rule.
3. **Operations and templates** — create deterministic, agent-facing onboarding, daily-run, catalog, brief, task-sync, and upgrade recipes plus synthetic templates.
4. **Adapters** — establish the current reference adapters without embedding personal provider IDs, names, domains, or secrets.
5. **Release and validation** — add release metadata, synthetic fixtures, validation checklists, and manual-first installation/update instructions.
6. **Current-instance migration** — inventory the existing private Drive instance, create a private configuration mapping, install the first release alongside it, and shadow-validate it.
7. **Cutover** — only after explicit approval, switch scheduled execution to the installed bootstrap, verify production behavior, and retain rollback material.

## Guardrails

- Do not copy private Drive content, source emails, identifiers, secrets, or family-specific configuration into this repository.
- Do not modify the frozen architecture to incorporate deferred reviewer recommendations unless explicitly approved.
- Do not change the live private Drive system or its schedules during phases 1–5.
- Every repository change must be followed by a readback/verification step.
- Progress writes are append-only in intent: do not erase prior checkpoints.
- Use synthetic fixtures only.

## Completion criteria for the current execution

This execution is complete when phases 1–5 are implemented in the repository and the repository is ready for the private-instance inventory/migration phase. Phase 6 and production cutover require separate inspection and explicit confirmation because they touch private systems.

## Approved alpha.9 daily-run simplification

The next release replaces the routine alpha.7 bootstrap/file-map sweep with one
generic daily operation and one narrowly scoped private companion document.

```text
Scheduled task
  -> generic daily-run.md
  -> private daily-run-personal-values.md
  -> phase-specific provider selector
  -> selected generic adapter
  -> that adapter's private configuration and state
```

`daily-run.md` remains the reusable sequence: catalogue source updates,
reconcile canonical actions and the selected task provider, update derived
knowledge, render the brief, verify delivery, and checkpoint the result. Task
reconciliation remains a required daily phase.

The private `daily-run-personal-values.md` holds only daily-run-specific values
and approved presentation/household customizations. It must not embed adapter
identity, provider bindings, credentials, or a second competing operation
recipe. It may not override factual provenance, task reconciliation,
duplicate-delivery prevention, or verified readback requirements.

Adapter selection remains separate. Each phase resolves its private selector
(for example, the active task-provider record), then reads the selected generic
adapter and only the private configuration/state declared by that adapter.
Routine runs read only the phase-relevant references. The full logical file map
remains available for onboarding, upgrades, recovery, and maintenance, not as a
routine daily-run preflight dependency.

Implementation requires a new immutable `0.1.0-alpha.9` release; the already
published alpha.8 tag must not be changed. The private legacy daily runbook is
retained as read-only migration evidence through verified production runs and is
not deleted during the initial rollout.
