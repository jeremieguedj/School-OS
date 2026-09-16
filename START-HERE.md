# School-OS agent entry point

This is the neutral entry point for a fresh agent. It is intentionally thin.

## Determine the mode

1. Read the supplied restart instructions. Packaged installation/upgrades are outside this MVP; do not run a retired release manifest or installer.
2. Read `docs/product-principles.md`, `PLAN.md`, and `PROGRESS.md` when maintaining this repository.
3. For a private installed instance, begin from that instance's stable Drive bootstrap and instance manifest.
4. Select exactly one operation: onboarding, import, daily run, manual daily-brief request, task sync, brief generation, upgrade, audit, or maintenance.

## Product-context routing

Read `docs/product-principles.md` during onboarding and before making decisions about architecture, customization, integrations, adapters, capability degradation, or new applications. Routine scheduled operations should not reread it unless their selected operation recipe declares it; they remain governed by the installed recipes and contracts.

## Classify proposed changes

Before changing an installed instance or this reusable system, classify the request:

1. **Configuration or personalization** selects existing behavior without changing core policy.
2. **Compatible expansion** adds a conformant adapter, tool, application, analysis, automation, or workflow while preserving core invariants and contracts. It is normal School-OS evolution and does not make an instance a fork.
3. **Core architectural change** alters an invariant, canonical data meaning, a generic contract incompatibly, or release/upgrade behavior.

Proceed with nonarchitectural work in the first two categories under the selected operation and ordinary user authorization. Every new or changed architecture decision, including one within a compatible expansion, requires explicit user approval under the [product decision authority](docs/product-principles.md#decision-authority). Before the third category, also explain why compatible expansion is insufficient and warn that the change may impair future official updates. Do not treat a user-created adapter as a core change merely because its provider is not included in the official release.

## Restart development and testing boundary

The [product principles](docs/product-principles.md) are the source of truth and
grounding for decisions not explicitly covered by approved plans. Follow the
[current restart plan](docs/plans/restart/PLAN.md) and its
[coordinator handoff](docs/plans/restart/ASTRA-HANDOFF.md) (the filename is
historical). Implement existing explicit
architecture approvals; obtain the user's approval before adopting any new or
changed architecture decision.
Apply the active plan's explicit MVP revisions: interrupted canonical-write
recovery, centralized tools/jobs management and packaged installation/upgrades
are deferred. The executing agent manages its own resources, batching, continuity
and nonconcurrent schedules; School-OS supplies guidance and completion rules.
A logical run must complete its agreed ingestion before daily brief composition;
a real blocker is incomplete work, not a completed partial daily brief. D5 is
approved. The separate query-coverage rule remains required for knowledge answers.
Preserve approved D1 separation for later installation/upgrade work. The separate
records/ordinary-save framework is also outside MVP and is not an approval gate.
Canonical data, approved meanings, agent save verification and cleanup remain.
School-OS starts with minimal Python standard-library routines; the agent and its
tools perform the rest. Recipes name actual scripts when applicable; see
[the helper guide](helpers/README.md). No Python version pin, external dependency,
personal computer, persistent process or coding CLI is required by this choice.
The latest numbered review approves run-start scope, strict original Date
precision, binary whole-email ingestion, the manual freshness conversation, no
audio archive and combined email/audio with an audio-failure fallback. The user
subsequently approved all remaining published recommendations: Q1/Q2 concrete
data/index architecture, Q4 arrival-window discovery and Q6 completed-email reuse.
See the current restart plan and its documentation snapshot checkpoint.
The retained operations, contracts, adapters and fictional examples are now
authored but untested. The user rejected Q10's linked-piece representation and
delegated the page-size decision; the assessment retains one 64 KiB maximum and
allows a later single-limit increase if actual evidence justifies it. A whole
record that exceeds the current limit blocks rather than being truncated or
given an invented overflow format. No current architecture question remains.
For the remaining repository work, use bounded Sol workers only, never Astra.
The root agent primarily coordinates, handles architecture and other escalations,
integrates the result and owns publication.
Setup now includes the approved [parent interview](operations/setup.md): offer
known task tools available to the executing agent and ask for the parent's
choice. Use or author one shared [tool-semantic adapter](operations/tool-adapters.md)
per tool, reusable through each agent's own connector. The adapter defines
School-OS-to-tool meanings; API, SDK, authentication and transport belong to the
connector. Missing conformant mappings may be authored under this approval;
missing connector capabilities must remain explicit. These new instructions
supersede retired runtime-specific adapter definitions. Clear evidence of task
fulfillment now becomes [completion detected awaiting parent confirmation](operations/completion-review.md),
not completed. The shared adapter uses a supported status or section; parent
confirmation then follows ordinary D5 sync. Direct automatic closure is future
work requiring a later decision. The daily brief is a starter template: users
and agents may create and choose any number of compatible
[brief recipes](operations/brief-recipes.md). The approved starter selects newly
verified/corrected information and relevant open tasks, shows original source
dates and discloses failed task-app sync; source accuracy, truthful task/coverage
state and the daily ingestion gate remain required.

The user has now supplied subsequent testing direction: after completing the
retained MVP, committing/pushing it and verifying the remote revision, conduct
three isolated seven-day school-email ingestion trials (a fresh context-free
worker, Gemini Spark through the user's browser, and ChatGPT Work through the
user's browser). Each uses its own fresh instance under the authorized tests
folder. This explicitly supersedes the earlier requirement to wait for another
permission at that checkpoint, only for these ingestion and audit trials.
Do not start functional execution before implementation publication. Do not infer
permission for outbound briefs, task-app writes, schedules or changes to existing
instances. Preserve private evidence and report incomplete capabilities honestly.
Inspect hooks and CI before publication; never silently bypass checks. See
[the current execution authorization](docs/plans/restart/PLAN.md#current-execution-authorization).

## Instruction hierarchy

For an installed instance, use this order:

1. Platform safety rules and the runtime's actual tool capabilities.
2. Direct user instruction for the current operation.
3. The selected installed operation recipe.
4. The installed release architecture and contracts.
5. Valid instance configuration and state.
6. Historical logs and derived files.

Configuration supplies instance values; it does not rewrite generic behavior. Shared tool adapters map School-OS logic to the selected tool's concepts without redefining core policy. Each agent's connector handles that tool's API and access mechanics.

## Read narrowly

Read the selected operation recipe first, then only the dependencies it declares. Do not rely on conversational memory for current state. Stop before writes if required instructions, configuration, state, or capabilities are unavailable or conflict.

## Repository maintenance rule

Keep this file generic. Do not add private household details, provider IDs, domains, recipients, credentials, message content, or operational copies here.

## Repository development continuity

School-OS development must remain independent of any particular coding agent,
vendor, local workspace, or conversation. GitHub is the durable shared state
from which another agent must be able to resume the work.

When maintaining this repository:

1. Follow the current approved release plan and the specification it links.
   Keep milestone status in that release plan accurate; do not infer executable
   support from documentation alone.
2. On resumption, inspect the actual branch, working tree, implementation, and
   Git history, then reconcile the plan, specification, and progress log with
   that evidence before continuing.
3. Append `PROGRESS.md` after each meaningful work unit, before a handoff or
   planned stop, and when blocked. Record completed and unfinished work,
   validation evidence, relevant files, blockers, decisions, and the exact next
   action.
4. For every accepted repository change, run validation appropriate to the
   change, including the privacy scan before publishing; commit all and only
   accepted in-scope files; push the descriptive commit to the intended GitHub
   branch; and verify that the remote branch resolves to that commit before
   reporting the work complete.

When the user reserves the testing phase, step 4 permits publication hygiene
(diff, privacy, document-link, Git status and remote-revision checks), not
functional test execution. Record the delivered code as untested and stop at the
agreed handoff; publishing implementation does not establish product qualification.

Never leave accepted work only in a local working tree or unpushed commit. Never
publish private-instance data, credentials, or unrelated user changes. If
validation, GitHub authentication or authorization, the push, or remote
verification fails, preserve the local changes and report the work as incomplete
with the exact blocker.
