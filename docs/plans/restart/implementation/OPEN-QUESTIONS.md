# Remaining decisions and recorded answers

Updated 2026-09-15 after the user’s numbered-review answers. The [active plan](../PLAN.md) remains the approval ledger.

Your answers are recorded. Questions 1 and 2 now have a concrete data architecture to review. Question 4 has a simpler replacement proposal. For question 6, binary email completion is approved; only the rule for skipping a later matching appearance still needs an answer. Questions 3, 5, 7, 8 and 9 are settled. The original numbering is preserved.

The next phase is completing the agreed implementation. These answers do not authorize tests or live account operations. The user directs testing after the whole agreed MVP is published and its remote revision verified.

## Q1. What exact information and links must the saved JSON records contain?

**Proposed architecture — awaiting approval.**

Store entities, source emails, substantive knowledge and canonical tasks as linked records. Knowledge declares whether it applies to a child, a family, a school or a defined group. Tasks separately declare the unit that must act, so a once-per-family form stays one family task. The concrete field tables and connected JSON examples are now in the data proposal.

**Example:** Robin’s personal math observation is child-specific; a school lunch guideline is stored once at school level; a once-per-family contact form creates one family task.

See [the proposed data architecture](DATA-ARCHITECTURE-PROPOSAL.md) and its [viewable diagrams and examples](data-architecture.html).

**Alternative and tradeoff:** Mostly free-text records are easier to improvise but make scope, filtering and cross-agent interpretation unreliable. Copying school facts per child creates duplicates and divergent updates. The proposed structure adds a small amount of explicit metadata, with no generic write engine.

**Decision / limits:** Review the exact record fields, references, dates, scope rules and task granularity in the proposal. These are recommendations, not already-adopted schemas.

## Q2. How should the index find all relevant information about a child and topic over time?

**Proposed architecture — awaiting approval.**

Use paged, rebuildable indexes by applicability, topic and time, with source/month routes and explicit index coverage. Resolve the child’s dated family/school memberships, fetch matching records, keep personal observations separate from general guidance, and synthesize the timeline with sources.

**Example:** For Robin’s math evolution, retrieve Robin’s dated math feedback. Read relevant school guidance as context; do not turn a school-wide math update or a sibling’s report into feedback about Robin.

See [the proposed data architecture](DATA-ARCHITECTURE-PROPOSAL.md) and its [viewable diagrams and examples](data-architecture.html).

**Alternative and tradeoff:** Scanning a whole year avoids maintaining topic indexes but grows costly. A search/vector service adds a new dependency and does not itself establish exact scope or completeness. The proposal uses bounded Drive pages and explicit aliases, with a documented fallback when an index is stale.

**Decision / limits:** Review the index entries, membership history, alias rules, completeness limits and end-to-end query traces in the proposal. Efficiency is designed for; it has not been measured.

## Q3. Should a daily run cover every School-OS-pending item through the start of that run?

**Approved.**

Yes. Complete all relevant not-ingested emails in configured scope through run start, including backlog. Later arrivals belong to the next run. Gmail read/unread status is not School-OS processing state.

**Example:** A run starts at 06:00. A school email opened yesterday still needs ingestion if School-OS never processed it. A 06:05 arrival belongs to the next run.

**Decision / limits:** No further approval needed. This is a finite input boundary, not a message-count limit.

## Q4. How should we catch relevant mail that appears late in a search?

**Revised, simpler proposal — awaiting approval.**

Use the connector’s live mailbox access for normal daily discovery from the last completed arrival-time boundary through run start, plus unfinished windows and known not-ingested backlog. Include the prior boundary at its actual precision, follow every continuation, and use metadata association for repeated results. Do not rescan all history every day or impose a fixed seven-day overlap.

**Example:** An email sent Monday but received Wednesday is found by Wednesday’s arrival-time search. An old message that becomes visible only after its older arrival window was marked complete may be missed under this simpler MVP policy.

**Alternative and tradeoff:** The rejected full-history fallback could catch more older changes but costs much more. The simpler policy accepts that newly visible older material is not automatically rediscovered. A parent can explicitly request a historical rescan. Live access alone does not establish every connector’s search behavior.

**Decision / limits:** Approve this narrower assumption and tradeoff? The route must expose usable search-time meaning, timezone/boundary behavior and continuation; otherwise report the capability limit or use a supported route. Original sending Date still defines identity, not arrival time.

## Q5. How precise must the original email Date be for automatic association?

**Approved.**

Require the original individual-message Date with known timezone and second-or-finer precision, alongside the other metadata and lookup requirements. Try a richer metadata view if necessary; unresolved evidence remains unresolved.

**Example:** A day-only date is insufficient. An original Date such as 10 September, 08:15:23 −07:00 can qualify with the remaining evidence.

**Decision / limits:** No further approval needed. Timestamp precision does not prove uniqueness. Unknown optional metadata is not a contradiction or a reason to create a duplicate.

## Q6. When a matching email appears again, what may the agent safely skip reading?

**Binary outcome approved — one reuse rule awaiting approval.**

Approved: each logical email is fully ingested or not ingested. Full means body and all required attachments were extracted, saved and checked; partial-email processing is outside MVP. Proposed remaining rule: a unique supported metadata match to a fully ingested email can reuse that result and skip content unless explicit new or contradictory inventory/coverage evidence challenges it.

**Example:** Yesterday’s fully ingested notice appears again through a different connector handle. Under the proposal it is skipped. A new reply has its own original Date and is ingested separately. If new evidence exposes unprocessed required material, the email cannot be treated as fully ingested.

**Alternative and tradeoff:** Always rereading is more costly. Reusing completion is simpler but cannot detect a content change hidden behind unchanged allowed metadata. This is the residual risk of the metadata-only design, not permission to ignore a known gap.

**Decision / limits:** Approve reusing the fully-ingested result on that supported metadata match? Different handles or unknown optional fields alone would not reopen it. No per-appearance ledger, partial-PDF workflow or content-hash identity is introduced.

## Q7. May a parent explicitly request a manual brief despite known processing gaps?

**Approved with freshness conversation.**

Yes. First warn that knowledge may be outdated, explain available last ingestion/search coverage and latest source-email dates or unknowns, and ask whether the parent wants new mail ingested first. Follow their choice; a brief sent now keeps the limitation visible.

**Example:** “I can verify school-email ingestion only through Monday; the newest saved trip email is dated Friday. Ingest new emails first, or send the saved information now?”

**Decision / limits:** No further approval needed. The newest source Date is not proof of search freshness. The ordinary daily complete-ingestion gate stays unchanged.

## Q8. Should generated audio be retained on Drive until the parent deletes it?

**Decided: no audio archive.**

No. After verified delivery to the parent by authorized email or agent chat, the audio work is done. Do not keep a canonical audio archive on Drive; discard accessible temporary processing copies.

**Example:** The parent receives the audio attached to the email or as a chat artifact. School-OS does not save an extra audio-history copy.

**Decision / limits:** No further approval needed. This does not promise deletion of the parent’s attachment, chat artifact or provider-managed service copies.

## Q9. When both email and audio are requested, should email go first?

**Decided: send together; text fallback on audio failure.**

When audio is properly configured, prepare it and send it with the email. If audio fails, send the email without audio and include a clear audio-failure notice.

**Example:** The audio service fails to generate the narration. The parent still receives the written brief, with “The audio brief could not be generated.”

**Decision / limits:** No further approval needed. Unknown send/generation outcomes still require the agent’s available verification; no blind duplicate send or new background retry system.

## Boundaries

D1 storage, D3 helpers/shared adapters, D5 knowledge/task meanings and prior approvals stay in force. The generic record/save and interrupted-write repair framework, central jobs/scheduler register and packaged lifecycle remain outside MVP. The new field/index design is a proposal, not an implemented or tested data layer.

The recommendations serve source-linked lossless knowledge, simple parent workflows, efficient bounded access, explicit scope, fresh-agent portability and honest completion. The [coverage map](COVERAGE.md) retains the whole deliverable scope.
