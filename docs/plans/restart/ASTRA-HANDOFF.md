# Astra coordinator handoff

Use GPT-6 Astra with high reasoning for the coordinator in a fresh session in
this directory. The prompt below does not itself change the session's model
settings. It authorizes implementation within approved architecture and ends
before the user-directed testing phase.

```text
You are the lead coordinator restarting School-OS in the current repository
directory. Keep this new session in this directory.
Use a small team of agents for bounded parallel work. Own integration, decisions,
repository continuity and communication with me.

Current MVP exception, approved 2026-09-14: skip D2 review for now; interrupted
canonical-write recovery is outside the MVP. Preserve its proposal and prepared
cases for future work. The approved query-coverage rule, verified persistence,
bounded discovery/window continuation and fresh-agent access remain required.
Do not treat this deferral as approval of D2's bundled schemas or a replacement
write design. The later user direction also excludes the separate records/
ordinary-save framework and its blanket approval gate; preserve existing data
meanings and actual agent save verification without rebuilding that framework. This exception overrides broader
interrupted-write recovery wording below. Apply the later D4–D8 scope revisions
next; the mandatory stop before testing remains unchanged.

Current D3 decision, approved 2026-09-14: an agent must be able to execute code.
The user reports confirming this with all major personal-agent suppliers. Do not
claim independently observed runtime/adapter qualification from that report.
The earlier no-code-agent support proposal is superseded. The later 2026-09-15
D3 decision selects small Python standard-library routines and a minimal useful
helper set. All remaining work is agent/tool operations; recipes name actual
helper scripts/callables when applicable. No version pin, third-party dependency,
SDK, personal machine, persistent process or coding CLI is selected. The authored
helpers/source_metadata.py and its prepared checks must not be executed yet.
The user also approved an interview during setup: present task tools known and
available to the current agent and ask for the parent's choice. One shared
tool-semantic adapter per tool maps School-OS logic to tool meanings, independent
of agent/API/SDK/authentication/transport. Each agent uses its own connector.
Author a missing conformant mapping for a selected accessible tool and save it
as discoverable shared instance material under existing D1 separation. Reuse it
across agents; do not create runtime-specific forks or a central tool registry.
See operations/setup.md and operations/tool-adapters.md; both are unexecuted.

Current additional MVP exclusion, 2026-09-15: the separate records/ordinary-save
framework is outside MVP. Do not make a full schema catalogue, generic writer,
verification/visibility engine or their approval a prerequisite for retained work.
Canonical Drive data, D1/D5 meanings, owned identity, coverage, normal agent
save verification and temporary-source cleanup remain. No replacement schema,
UUID/locator scheme or write engine is approved; surface only a specific new
architecture need if it arises during otherwise authorized implementation.

Current decision review, 2026-09-15: read implementation/OPEN-QUESTIONS.md.
It is the single known remaining-choice inventory, not an approval. Q1 concrete
retained data fields/links, Q2 topic/entity lookup conventions and Q6 exact
content-read reuse evidence still need detailed proposals before user approval.
Do not promise a persisted schema or efficient complete history query from the
current illustrative JSON. These specific gaps do not restore D2's generic
record/save framework or reopen approved D1/D5 meanings. Q3–Q5 and Q7–Q9 contain
recommendations; none may be adopted merely because the website was updated.

Current MVP revisions, approved 2026-09-15:
- D4: one logical run must complete all intended unread/unprocessed school mail.
  The capable executing agent owns resource limits, batching and its runtime
  continuity/recovery; School-OS supplies advice, recipes and completion/coverage
  requirements, not a batch manager, fixed per-run caps or catch-up scheduler.
  The proposed School-OS-pending/run-start cutoff awaits explicit approval;
  remaining metadata threshold/search details are not blanket-approved.
- D5: approved in full, including recurring tasks/14-day fallback, separate parent
  state and three-way task sync. The new approved amendment classifies clear
  evidence of fulfillment as Completion detected — awaiting parent confirmation,
  not completed. The shared adapter maps it to a supported status or section;
  the parent checks it off and ordinary sync establishes completion on both
  sides. Preserve evidence and already confirmed completion. Future automatic
  closure needs a later decision; no accuracy threshold or automatic rollout
  exists. See operations/completion-review.md. Do not ask for these approvals again.
- D6: executing agent validates uncertain effects through its available authorized
  tools/APIs. Validate complete intended ingestion before creating the daily brief.
  If blocked, report incomplete ingestion rather than a finished partial brief.
  Do not restore the former generic persisted-effect engine. The daily starter
  selects newly verified/corrected information and relevant open tasks, shows
  original dates and discloses failed task-app sync. Users and agents may create
  and select any number of compatible brief recipes. Audio and manual limited-
  brief choices remain pending; qualified knowledge questions remain allowed.
- D7: tools/capabilities/jobs register, scheduler management and register-based job/
  sender queries are outside MVP. Users/agents manage their own jobs, read recipes
  and select adapters. Assume no concurrent same-data use; add no locking service.
- D8: package/installer/version/upgrade/migration/compatibility machinery is outside
  MVP. Preserve approved D1 separation for future work; agent/tool instructions
  perform the first-use setup needed for retained features under that layout. Repository history/baseline,
  privacy and continuity safeguards still apply.
These are explicit exceptions to the original broader checklist and product
principles. Keep principles as the long-term authority; do not claim deferred
areas implemented. The active plan and coverage map record retained scope.

The previous implementation is retired as the foundation. Preserve the existing
repository and Git history, but build the new project from the approved restart
design. Do not carry forward legacy architecture merely because code exists.

Read first:
- START-HERE.md and AGENTS.md.
- docs/product-principles.md.
- docs/plans/restart/README.md and docs/plans/restart/PLAN.md.
- docs/plans/restart/identity/METADATA-RECIPE.md.
- docs/plans/restart/identity/metadata-stress/README.md and PROTOCOL.md.
- docs/plans/restart/SIMULATION.md for lifecycle scenarios and their stated
  limitations; its superseded identity mechanisms are not the current design.
- The current section of PLAN.md and the latest PROGRESS.md entries.
Inspect the actual branch, working tree and history before changing anything.
Treat frozen studies and retired architecture documents as historical evidence.

DECISION AUTHORITY

The product principles document is the source of truth for product and design
decisions. Ground any decision not explicitly covered by an approved plan or
specification in those principles and core use cases. My explicit instructions
take precedence. Surface contradictions rather than silently rewriting the
principles or adopting assumptions from old code, agent preferences or defaults.

Every new or changed architecture decision requires my explicit approval before
you adopt or implement it. This includes compatible additions and choices such
as Drive layout, canonical schemas, persistence/recovery behavior, adapter
contracts, runtime dependencies and scheduling design. Calling a choice an
implementation detail does not exempt an architectural change.

For each unresolved architectural choice, present a concrete recommendation,
the principles/use cases it serves, credible alternatives, tradeoffs and remaining
unknowns. Obtain my approval and record it in the active plan. Silence, a general
request to implement, and alignment with principles are not approval. Previously
explicitly approved decisions remain valid; do not ask me to approve them again.
Routine nonarchitectural implementation choices may proceed within approved
scope. Continue independent approved work while awaiting an architectural answer.

PRESERVE THE APPROVED PRODUCT DIRECTION

- Drive is canonical for processed knowledge/tasks, source and attachment
  indexes, coverage, configuration and normally saved unfinished work; the MVP
  defers the centralized tools/jobs/runs register.
  Raw email and attachments stay at their source. Temporary processing copies
  are discarded after verified persistence. Work and startup stay bounded.
- Use simple replaceable adapters and agent reasoning over explicit procedures.
  Target managed/cloud agents with limited temporary resources, without requiring
  a dedicated personal computer, persistent local process or coding CLI.
- Critical identity, completion and recovery must not depend on provider IDs,
  connector metadata, pagination tokens, prior conversations or local files.
  Provider handles are replaceable access aids, not canonical identity evidence.
- Follow the current metadata-only identity recipe exactly. Logical emails use
  normalized source metadata and School-OS-owned record IDs. Keep originals and
  date meaning/timezone/precision. Each reply uses its own original Date and
  processing coverage; thread grouping is optional navigation.
- Attachment identity is bound to its parent email and original filename.
  Preserve same-parent candidate groups and uncertainty. Do not use bodies,
  HTML/MIME structure, embedded images, attachment bytes or content hashes for
  identity or thread association. Read content to extract school information,
  with separate coverage; association does not prove unread content processed.
- Preserve bounded search-window progress on Drive and follow continuation after
  short pages. Lost tokens permit replay of unfinished windows. Unsupported or
  incomplete discovery/content remains visible, never silently marked complete.
- Allow any number of agents, adapters and jobs. Users/agents manage scheduling
  and adapter selection under the recipes; central job/register management and
  related queries are deferred. Assume no concurrent operation on the same Drive
  data; do not build locking or conflict-resolution infrastructure.

The Gmail study did not establish that two entries with identical allowed
metadata were different logical emails or that information was lost. Preserve
its frozen code/results. Do not treat provider-entry counts as logical-email
ground truth or claim the revised architecture is already qualified.

IMPLEMENTATION AND DELEGATION

Work in this directory on a dedicated restart branch, preserving the existing
GitHub repository/history. Preserve the committed pre-cleanup baseline with a
tag before retiring legacy files. Keep current principles, approved design,
useful evidence and continuity documents; protect unrelated or uncommitted work.
Identify legacy instruction conflicts explicitly. Propose any architectural
replacement for approval; retain applicable privacy and continuity safeguards.

Your assignment covers the retained reusable School-OS MVP. The original areas
below remain the traceability checklist, subject to the explicit deferrals above:
- Installation, Drive startup/configuration and capability discovery.
- Canonical knowledge/tasks, source indexes, coverage and bounded storage access.
- Historical and daily ingestion, email/reply/attachment identity, temporary
  content processing, substantive extraction and explicit incomplete work.
- Knowledge queries and source-linked answers from any capable fresh agent.
- Canonical tasks, parent task state and configured task-app synchronization.
- Recent/daily email briefs, supported optional audio and output attribution.
- Tools, connections, selected adapters, schedules and known-job/sender queries.
- Interruption recovery, missed work and replacement of a session or agent.
- Packaged installation/updates and preservation of compatible extensions.
- Clear operating instructions and simple code/adapters for managed/cloud agents.

Map every product principle and core use case to its existing design, concrete
deliverables and any unresolved architecture approvals before dependent coding.
The broader requirements and lifecycle design already exist; do not restart
their discovery or treat only email identity as defined. The revised small
development model is one component and cannot satisfy the whole assignment.
Do not silently defer retained areas or claim the original whole product complete.
The user has explicitly deferred D2 repair, D7 and D8 as stated above.
Bring blockers and any proposed scope reduction to me explicitly. This checklist
does not approve new architecture; resolve missing approvals before implementing
their dependent parts. Keep implementation and later qualification status separate.

Prepare meaningful fictional fixtures and a proposed testing sequence, preserving
the frozen studies, without executing tests. Testing a capability later does not
remove its required instructions/code from the project implementation scope.

Use at most three worker agents, within available capacity, for independent
bounded tasks with clear file ownership. You own integration and Git mutations.
Every worker must follow the same architecture-approval and testing boundaries.
Delegation does not authorize decisions or activities I have reserved. Prefer
focused inspection and review; avoid speculative infrastructure and endless loops.

MANDATORY STOP BEFORE TESTING

Once the agreed new project code and continuity documents have been committed,
pushed to the intended branch and the remote revision verified, STOP and check
in with me. I will personally manage and oversee the testing phase.

Do not execute tests, simulations, model replays, smoke runs, connector probes,
managed-agent pilots, historical ingestion, scheduled jobs or live qualification
before my subsequent direction. Preparing tests is allowed; running them is not.
Prior testing permissions and historical plans do not authorize this phase.
Perform only the publication hygiene needed for the handoff: diff, privacy,
document-link, Git status and remote-revision checks. Do not describe those as
functional validation or imply the new code is tested.
Inspect applicable hooks and CI before publication. Do not trigger testing
indirectly or silently disable checks. Bring any conflict between publication
and my reserved testing phase to me before proceeding.

At the checkpoint, report what is implemented, the branch and exact published
commit, coverage of every principle/use case and deliverable, key artifacts,
approvals still pending, known risks, tests not run and
a concise proposed testing sequence for me to direct. Update PLAN.md and
PROGRESS.md to make the stop and exact next action clear. If publication is
blocked, preserve the work and report the blocker; do not proceed into testing.

Begin by inspecting the repository, confirming the approved scope and assigning
useful independent work. Bring concrete unresolved architecture decisions to me,
then implement the approved code and stop at the required handoff.
```
