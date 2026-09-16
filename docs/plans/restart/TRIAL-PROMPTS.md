# Isolated trial handoff prompts

Status: ready to fill, not executable yet. Use these prompts only after the full
retained implementation is committed, pushed, and the exact remote revision is
verified. Q10 is unresolved at this writing, so the publication prerequisite has
not been met. The [trial protocol](TRIAL-PROTOCOL.md) governs preparation, private
receipts, independent expectations, auditing, and reporting.

## Coordinator fill sheet — private, same values for all routes

Fill these placeholders from verified operating material and private
configuration after publication. Do not commit the filled sheet or paste its
private values into public reports.

| Placeholder | Required value |
|---|---|
| `{{TRIAL_LABEL}}` | Privacy-safe route/trial label for reports |
| `{{FINAL_REVISION}}` | Exact approved, pushed, remote-verified implementation SHA |
| `{{OPERATING_ENTRY}}` | Link to the exact published reusable setup entry for that revision; this is not a pre-existing instance entry point |
| `{{OPERATING_MATERIALS}}` | Exact links to the published reusable product principles, recipes, contracts, helpers, and supplied mappings needed for setup and ingestion |
| `{{ASSIGNED_FOLDER}}` | Distinct empty child folder for this route under the authorized tests parent |
| `{{PRIVATE_EVIDENCE_ARTIFACT}}` | Private audit artifact inside the assigned folder for detailed observable traces |
| `{{MAILBOX_INPUT}}` | Private logical mailbox and connector/account input selected for read-only access |
| `{{HOUSEHOLD_INPUTS}}` | Private household, child/entity, school/class, timezone, and source-scope configuration inputs |
| `{{WINDOW_START}}` | Fixed received/arrival-time lower bound |
| `{{WINDOW_END}}` | Fixed received/arrival-time upper bound, set at the start of the trial series |
| `{{WINDOW_SEMANTICS}}` | Timezone, precision, inclusivity/exclusivity, and connector field meaning for both bounds |

Confirm that all three prompts carry identical window values and semantics. Give
each route its own `{{ASSIGNED_FOLDER}}`. Do not include the independent oracle,
developer audit expectations, prior trial output, private receipt paths, or
fictitious expected school answers.

## Common minimal prompt

> Perform one isolated School-OS setup and complete seven-day school-email
> ingestion using revision `{{FINAL_REVISION}}`.
>
> Your assigned fresh Drive folder is `{{ASSIGNED_FOLDER}}`. Confine every write
> that persists in Drive to that folder and its descendants. Approved temporary
> processing through the task's available workspace remains allowed; discard
> accessible temporary raw source copies after verified canonical persistence.
> All other external writes are prohibited. Disregard prior School-OS instances
> and their generated data; do not delete, edit, or use them. Do not read another
> trial's folder or any evaluator expectations.
>
> Treat `{{OPERATING_ENTRY}}` and these exact published reusable operating
> materials as your authority: `{{OPERATING_MATERIALS}}`. Install them into the
> empty assigned folder as the setup recipe directs, and create that instance's
> readable Drive `START-HERE` there. Then follow their current setup and ingestion
> instructions, contracts, helpers, and supplied mappings. Do not rely on
> remembered School-OS behavior, retired materials, development plans, or examples
> as household facts. Assess the tools actually available in this task and report
> required capabilities that are unavailable or unknown.
>
> Private inputs: mailbox/connection `{{MAILBOX_INPUT}}`; household and school
> configuration `{{HOUSEHOLD_INPUTS}}`. The only source interval is received/
> arrival time from `{{WINDOW_START}}` through `{{WINDOW_END}}`, interpreted
> exactly as `{{WINDOW_SEMANTICS}}`. Use the supplied approved metadata-only
> logical-email identity rules. Cover each in-scope whole email: separate replies,
> body, and every required attachment. Preserve exact original Date meaning when
> available, but do not use provider IDs, content hashes, URLs, or rounded times
> as canonical identity.
>
> Mailbox access is read-only: do not change read state or labels, delete, move,
> or send mail. Do not send a brief, create audio, write to a personal task app,
> or create or change schedules. Canonical School-OS tasks inside your assigned
> Drive instance are in scope. Do not add a task connector merely for this trial.
>
> Complete the entire agreed setup and ingestion run, including continuation,
> verified canonical saves/readback, and truthful discovery and whole-email
> coverage. A batch, partial result, or session boundary is not completion. If a
> real capability or source blocker prevents completion, stop the affected work
> safely, preserve truthful incomplete state, and report the explicit blocker.
> Do not guess that an unknown inventory is empty or claim an external effect
> from an echoed request.
>
> Save the detailed observable retrieval/evidence trace in
> `{{PRIVATE_EVIDENCE_ARTIFACT}}`, including canonical source references and the
> pages or directories consulted where observable. Return only a sanitized
> concise summary with: trial label `{{TRIAL_LABEL}}`; completed or blocked status;
> confirmation that the supplied fixed bounds and semantics were applied;
> observable discovery/content-coverage and verified save/readback outcomes; and
> unsupported or unexercised capabilities. Do not repeat the private folder URL,
> account, household configuration, source content, provider IDs, other URLs,
> credentials, unsanitized exceptions, detailed trace, or hidden reasoning.

## Route wrappers

Prepend exactly one wrapper to the common prompt. Do not silently tailor the
contract after a route starts; record any necessary intervention in the private
audit log.

### Fresh context-free Sol worker

Coordinator launch condition: start a new bounded Sol worker with no inherited
conversation (`fork_turns: none`). Supply only this wrapper and the common prompt.

> You are the fresh context-free Sol worker for this isolated trial. The text
> below is your complete task handoff. Report any missing tool or connector from
> what you can actually observe; do not assume capabilities from the route name.

### Gemini Spark

Coordinator launch condition: start a new Gemini Spark task in the user's
authorized browser session; do not reuse an earlier task or add prior School-OS
conversation. Supply only this wrapper and the common prompt.

> You are operating in the new Gemini Spark task for this isolated trial.
> Establish available browser, mailbox, Drive, code, and file capabilities from
> what you can actually observe. Do not assume them from the route name. Report
> an explicit blocker if the installed instructions cannot be completed with
> this task's authorized tools.

### ChatGPT Work

Coordinator launch condition: start a new ChatGPT Work task in the user's
authorized browser session; do not reuse an earlier task or add prior School-OS
conversation. Supply only this wrapper and the common prompt.

> You are operating in the new ChatGPT Work task for this isolated trial.
> Establish available browser, mailbox, Drive, code, and file capabilities from
> what you can actually observe. Do not assume them from the route name. Report
> an explicit blocker if the installed instructions cannot be completed with
> this task's authorized tools.

## Common post-run source question

The coordinator may fill and send this only after publication and only after the
independent oracle has derived the question and support from source evidence. Use
the same source-grounded question for all routes. Never fill it from an agent's
output or invent a desired answer to cover a missing case.

> Using only canonical records in your assigned instance, answer:
> `{{ORACLE_DERIVED_QUESTION}}`
>
> Scope the answer to `{{QUESTION_SCOPE_AND_TIME}}`. Cite the canonical source
> references supporting each material claim, check relevant corrections and
> discovery/content coverage, and state freshness or coverage limits. Save the
> observable retrieval trace—entities/configuration resolved, indexes,
> directories, pages consulted where observable, and record support—in the
> supplied private evidence artifact. Return a sanitized answer and trace summary
> without private identifiers or URLs. Do not expose hidden reasoning or retrieve
> from the live mailbox merely to repair the saved answer unless the coordinator
> separately records and authorizes that intervention.
