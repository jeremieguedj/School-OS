# School-OS agent entry point

This is the neutral entry point for a fresh agent. It is intentionally thin.

## Determine the mode

1. **Fresh starter setup:** when the parent supplies a fresh School-OS ZIP or
   folder link and asks to set it up, read [AGENTS.md](AGENTS.md), then follow the
   authoritative [setup procedure](operations/setup.md), packaged at
   `system/operations/setup.md`. Recognize the starter's reusable `system/` tree,
   empty `instance/` and `extensions/`, and absence of canonical IDs or
   configuration before looking for an installed-instance bootstrap. A starter
   ZIP is in scope; do not run a retired release manifest or installer.
2. **Configured private instance:** begin from that instance's stable readable
   entry point, configuration and [startup procedure](operations/startup.md),
   packaged at `system/operations/startup.md`. Preserve its data and extensions.
3. **Repository development:** read `docs/product-principles.md`,
   `docs/plans/restart/PLAN.md`, and `PROGRESS.md`, then follow the development
   boundary below. These developer materials are not prerequisites for parent
   setup or normal instance operation.
4. Select exactly one operation: setup, import, daily run, manual daily-brief
   request, task sync, brief generation, audit, compatible extension or
   maintenance. Automated upgrade and migration machinery remains outside the
   MVP.

## Product-context routing

Read `docs/product-principles.md` during repository development. In a distributed
starter or installed instance, read the supplied product principles in `system`
during setup and before making decisions about architecture, customization,
integrations, adapters, capability degradation or new applications. Routine
scheduled operations should not reread it unless their selected operation recipe
declares it; they remain governed by the installed recipes and contracts.

## Classify proposed changes

Before changing an installed instance or this reusable system, classify the request:

1. **Configuration or personalization** selects existing behavior without changing core policy.
2. **Compatible expansion** adds a conformant adapter, tool, application, analysis, automation, or workflow while preserving core invariants and contracts. It is normal School-OS evolution and does not make an instance a fork.
3. **Core architectural change** alters an invariant, canonical data meaning, a generic contract incompatibly, or release/upgrade behavior.

Proceed with nonarchitectural work in the first two categories under the selected operation and ordinary user authorization. Every new or changed architecture decision, including one within a compatible expansion, requires explicit user approval under the [product decision authority](docs/product-principles.md#decision-authority). Before the third category, also explain why compatible expansion is insufficient and warn that the change may impair future official updates. Do not treat a user-created adapter as a core change merely because its provider is not included in the official release.

## Repository development and testing boundary

This section applies only when maintaining or testing the reusable School-OS
repository. It is not part of a parent's first-setup interview or an installed
instance's routine operation.

The [product principles](docs/product-principles.md) are the source of truth and
grounding for decisions not explicitly covered by approved plans. Follow the
[current restart plan](docs/plans/restart/PLAN.md) and its
[coordinator handoff](docs/plans/restart/ASTRA-HANDOFF.md) (the filename is
historical). Implement existing explicit
architecture approvals; obtain the user's approval before adopting any new or
changed architecture decision.
Apply the active plan's explicit MVP revisions: interrupted canonical-write
recovery, centralized tools/jobs management, and automated upgrades, migrations,
compatibility handling and release management are deferred. A distributable fresh
starter ZIP/folder and discoverable agent-led setup are included. The executing
agent manages its own resources, batching, continuity and nonconcurrent schedules;
School-OS supplies guidance and completion rules.
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
Setup follows the approved [authoritative parent interview](operations/setup.md):
resolve missing household, school, mailbox, location and tool choices; show the
actual known options available to the executing agent; and ask for the parent's
choice. Do not repeat choices already authorized. Use or author one shared
[tool-semantic adapter](operations/tool-adapters.md)
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

The latest testing boundary is a publication/readiness stop. Finish and publish
the fresh one-link starter and revised setup material, verify the publication,
report readiness, and wait for the user's direction before launching the revised
three-route setup and ingestion trials. Earlier guided-trial attempts and their
unresolved effects remain historical evidence; do not resume their private v2
handoffs. The retained later-test scope still uses one fresh context-free Sol
worker, Gemini Spark and ChatGPT Work in separate new folders, with ingestion
authorized separately after verified setup. It does not permit outbound briefs,
task-app writes, schedules or changes to existing instances. Preserve private
evidence and report incomplete capabilities honestly. Inspect hooks and CI before
publication; never silently bypass checks. See
[the current execution boundary](docs/plans/restart/PLAN.md#current-checkpoint--one-link-setup-implementation-and-testing-hold).

## Instruction hierarchy

For setup or an installed instance, use this order:

1. Platform safety rules and the runtime's actual tool capabilities.
2. Direct user instruction for the current operation.
3. The selected supplied or installed operation recipe.
4. The supplied or installed system architecture and contracts.
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
