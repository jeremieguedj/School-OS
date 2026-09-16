# D6 — A daily brief follows complete relevant ingestion

**Current user direction, 2026-09-15:** the executing code-capable agent must finish and validate relevant unread/unprocessed school mail before composing an ordinary completed daily brief. When an external action has an uncertain outcome, that agent assesses the available evidence through its own **authorized** connectors or APIs and validates the effect; School-OS does not silently import a central effect engine. This supersedes the earlier D6 illustration of delivering a partial ordinary daily brief while a relevant listing page and attachment remained unread, and the earlier D6 proposal’s generalized persisted-intent engine. The prior proposal is preserved historically at Git revision `62070eb`. This brief contains wholly fictional written examples, not executed mail, audio, task changes, simulations, probes or qualification evidence.

The [active plan](../../PLAN.md) remains the approval ledger. The [product principles](../../../../product-principles.md) and [approved query-coverage rule](../ARCHITECTURE-PROPOSAL.md#approved-query-coverage-rule) require source-linked knowledge, explicit gaps and reliable claims of coverage. D4 now places completion and internal batching with the executing agent; see the [D4 brief](D4-INGESTION.md). The user’s direction resolves the **daily composition gate and agent-owned effect assessment**. It does not blanket-approve verification-time recency, task selection, audio retention or ordering, reporting-occurrence identity, exact effect evidence/retry policy, D3 adapter contracts or the minimum record/ordinary-write design. D5 semantics are separately approved; D7 job management and D8 lifecycle machinery are deferred. The [architecture proposal’s D6 section](../ARCHITECTURE-PROPOSAL.md#d6--brief-selection-delivery-audio-and-unknown-effects) records this direction; the prior central-effect description is not current MVP authority.

## What must happen before the daily brief

The agent begins with the authorized mailbox/school scope and finite run boundary. The precise cutoff is still an unapproved D4 choice; a proposed interpretation is all relevant School-OS-pending mail discoverable through a declared run-start cutoff, with later arrivals assigned to the next run. The proposed scope interpretation uses School-OS content/discovery **coverage** rather than the mailbox unread flag; explicit confirmation is still pending. A parent opening a source email cannot make School-OS treat it as processed; an unread UI flag does not by itself prove canonical content is missing.

The agent then establishes discovery exhaustion for that scope, including all available continuation pages; reads and extracts relevant individual messages, replies and attachment candidates; saves substantive knowledge, source references and actual coverage on Drive; and verifies the ordinary successful save path. It evaluates whether any relevant content, inventory, association or coverage lookup remains incomplete. Only after that check supports **complete relevant ingestion** does it compose an ordinary completed daily brief from the verified canonical information. Internal chunks or connector pages do not relax this gate. D1’s approved bounded JSON pages constrain each storage transfer, not the total number of relevant messages the agent must handle in its logical run.

If a connector cannot establish complete listing, an attachment is unsupported, the agent loses a necessary source route, or saved coverage cannot be verified, it **reports the scoped gap and does not issue an ordinary completed daily brief**. It must not replace the missing material with a guessed summary, a “no news” claim, or a brief whose ordinary format falsely implies completion. A separate parent-requested **partial/provisional** output is a possible future policy, not approved by this instruction; its label, content, timing and authorization would need a concrete proposal. An individual parent query can still provide verified facts with explicit incompleteness under the already approved query rule, which is a different operation from the completed daily brief.

This direction assumes a capable executing agent can maintain or recover its own logical task while it pages, reads and verifies. Exact agent continuity, source fidelity, completion evidence and unattended capabilities remain unqualified. School-OS must not install a 25-message stopping rule, automatic follow-up schedule or centralized batching engine to make the brief gate appear achievable. A runtime that cannot finish must expose the limitation rather than certify an incomplete daily result.

## A fictional day with a late correction

Suppose fictional Maple School sent three relevant messages before today’s proposed run-start cutoff:

| Source material | Fictional content | Processing state as the run begins |
|---|---|---|
| September 10, “Chess club places” | Booking closes September 18 at noon. | Not yet processed by School-OS. |
| September 15, “Museum departure correction” | The September 25 bus leaves at 08:20 rather than 08:40. | Body not yet processed. |
| September 15, “Swimming reminder” | Bring kit Wednesday; details in an attached newsletter. | Body and newsletter attachment not yet processed. |

The source returns a short page with continuation. The agent follows it, processes each relevant appearance and newsletter candidate, and verifies saved claims/coverage before composing. If the newsletter cannot be read, it reports that relevant ingestion is incomplete and withholds the ordinary completed brief. The chess message’s older sending date does not make it optional: it is pending School-OS processing within the declared scope. The fictional day has no measured speed or promise that any actual runtime could do this work.

After complete relevant processing, a **possible** brief under the still-pending verification-time recency proposal might say:

> **School update — September 15**
>
> **Newly verified older mail:** Chess booking closes September 18 at noon; source sent September 10.
>
> **Correction:** The museum bus leaves at 08:20 on September 25, replacing 08:40.
>
> **Upcoming:** Bring swimming kit Wednesday; the newsletter details were processed.
>
> **Coverage:** The declared daily ingestion scope was completed and saved. Source references accompany each statement.

That copy is illustrative, not an approved format or dispatch. The recency choice remains to be decided: select knowledge first verified/substantively corrected during a requested reporting interval (which surfaces late-processed old mail), or select by original school Date (which may miss newly learned history), or define another explicit hybrid. Historical import still needs an explicit delivery choice rather than automatically emailing a backlog. The brief may include outstanding canonical tasks and parent plans, using the now-approved D5 task meanings; the exact D6 selection policy remains pending. An action-free, completely read task snapshot should not trigger a nonexistent task-app write; task-sync failure cannot erase canonical information. Whether an incomplete task-app sync prevents, qualifies or merely accompanies the completed knowledge brief needs an explicit rule consistent with the verified input state.

## Optional audio and attribution remain choices

Optional audio would narrate the **same selected canonical information**, including qualifications, without copying raw school attachments to Drive. The earlier D6 proposal retained generated audio as a derived Drive artifact until the parent explicitly deletes it, with inputs and attribution. That retention lifetime is **not approved wholesale** by the new instruction. Alternatives include parent-configured retention or shorter derived-artifact retention; those reduce storage but affect replay, attribution and later listening. Email/audio ordering is also open: sending email after both outputs are ready could delay news if audio fails; sending email first could make audio arrive later or never. Neither order is silently selected here. Unsupported audio cannot turn a complete email brief into invented audio success.

Useful operation/output source attribution remains in scope, but the user has deferred D7’s centralized job register, management locations and register-backed historical sender queries. The minimum retained output fields still need to be shaped alongside normal records. Do not require a job registry to validate an email or task action. Changing a sender default must not rewrite whatever historical evidence has actually been saved.

## The agent validates an uncertain effect

Consider a fictional authorized daily email send. The call yields no usable response. The message may have been sent, accepted but not yet visible, or never applied. The agent first classifies what it actually knows: a missing transport response is not a provider error response; a generic error alone supplies no rate-limit, authorization, timeout or success evidence. It checks the authorized mail service through available sent-output or delivery-lookup tools/APIs, in the relevant account and scope, for the intended content/destination/occurrence evidence. A complete relevant result may support that the effect happened once. A short, stale or empty search may not. Sent evidence establishes sending, not parent receipt or reading.

The same reasoning applies to other authorized effects. A task-app create is checked against the relevant target and School-OS task identity where supported; title similarity is not identity. An audio generation is checked against available artifact/job evidence. Scheduler management is outside the MVP under D7. Provider IDs may help locate current results but cannot become canonical school-email or attachment identities. Each connector’s actual lookup completeness, visibility delay, marker support and permission must be established from that route, not guessed from a vendor name.

The agent **does not blindly repeat an unknown write or send**. If it has evidence the effect was not applied, a retry may be considered under an approved rule; if evidence remains ambiguous, it reports the unknown outcome and stops that effect, or asks the parent for a duplicate-risk decision if a retry is desired. The executing agent uses its judgment over the available evidence and explains the result. This direction does not require a central evidence-threshold table, a new retry service or a job register. New canonical record/adapter meanings still require approval. The user-directed agent-owned validation approach does not guarantee exactly-once external effects or unattended permissions.

The earlier proposal described a common School-OS effect engine with durable owned effect IDs, pre-dispatch intent records and D2-style recovery. **That engine is superseded for this MVP direction**, not reintroduced under another name. Normal successful saving and useful output attribution still need a minimum ordinary-write contract, but the user excluded the general D2 interrupted canonical-write repair engine from the MVP. If the agent’s own observation or save is interrupted, the brief must not promise that School-OS can reconstruct every half-written effect record. Any new narrow persistence/continuity protocol is a separate architecture proposal; it cannot be inferred from “validate using available means.”

## What your direction settles, and what remains

Your direction settles who checks uncertain actions and when the ordinary daily
brief may be created. No separate central effect engine or partial-brief policy
is needed to implement that direction. D5 is approved; D7/D8 are deferred.

The remaining D6 product choices are narrower:

- **Content selection:** recommend newly verified or substantively corrected
  knowledge in the requested reporting interval, showing original source dates
  and relevant outstanding tasks. This surfaces late-processed older deadlines.
  Selecting only original source dates is simpler but can miss those updates.
- **Optional audio:** the prior recommendation saves a derived audio artifact
  on Drive until parent deletion. A shorter retention rule uses less storage but
  reduces later access. Email-first avoids waiting on optional audio; combined
  delivery waits for audio. Retention and order remain unapproved.
- **Task-app freshness:** the prior recommendation permits a knowledge brief
  after complete ingestion even if task-app synchronization fails, using verified
  canonical tasks and disclosing the app-state limitation. Blocking the brief
  until task sync succeeds is an alternative with potentially later delivery.

The finite D4 scope/cutoff and minimum D3 record/adapter/output contracts still
need resolution before dependent code. The agent can report a blocked operation
in its existing authorized interaction; this brief does not add an alert service
or require an architectural decision about message wording. No test, probe,
email, audio, task effect or scheduled operation was run.
