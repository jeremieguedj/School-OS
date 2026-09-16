# Open decisions before completing the MVP

Updated 2026-09-15. Recommendations for review; **no new approvals recorded**.

The [active plan](../PLAN.md) records approvals. This review inventory is grounded in the [product principles](../../../product-principles.md) and [whole-project coverage](COVERAGE.md).

This is the single current list of known open decisions for the retained MVP. None is approved by publication of this page. Questions 1, 2 and 6 need more detailed proposals from me before you can give final approval. Questions 3, 4, 5, 7, 8 and 9 have recommendations ready for your decision. Question 4’s cost also depends on the read-reuse rule in question 6. You can answer by number and change any recommendation.

The next phase is completing the agreed implementation. Testing is a later, separate phase that you personally direct after the whole agreed MVP is committed, pushed and its remote revision verified. Answers here do not authorize tests or live operations.

## Q1. What exact information and links must the saved JSON records contain?

**Data structure · Detailed proposal still owed before approval.**

**Recommendation:** Use a small shared structure for the data the MVP actually needs: source observations and attachment candidates, substantive knowledge, linked tasks and parent state, discovery/content coverage, and the selected configuration and synchronization information. Preserve the approved separation between school evidence and parent decisions. Specify how School-OS-owned references connect these pieces.

**Example:** A school request becomes a source-linked knowledge statement plus a linked task. A teacher observation about Robin stays knowledge even if it creates no task. Both keep dates, qualifications and evidence; completion belongs to task state.

**Alternative and tradeoff:** Mostly free-text records would give agents more freedom, but make cross-agent interpretation and reliable filtering harder. A comprehensive schema registry and generic write engine would add machinery that you already excluded from MVP.

**Why it matters:** Serves lossless knowledge, accurate task synchronization, source-linked answers and fresh-agent use (P1, P2, P5, P7, P9; U1, U2, U4).

**Remaining detail / limits:** I still owe you connected JSON examples and a field table: required/optional values, unknown versus empty values, original/observed/effective dates, attribution, source references, task-to-knowledge links, correction/conflict relationships, coverage and reference lookup. Include instance configuration and the last verified task-sync values. The current page sketch is not that contract. This question is not ready for final schema approval; approving a general direction would not approve unseen fields or ID rules.

## Q2. How should the index find all relevant information about a child and topic over time?

**Finding information · Detailed proposal still owed before approval.**

**Recommendation:** Use the already-approved rebuildable topic/entity directories, with a small explicit convention for entity identity, topic labels and supported aliases, dates and references to candidate knowledge pages. Read the actual records and coverage before answering. If an index is stale or incomplete, use the source/month route or disclose the unfinished search.

**Example:** For “How has Robin’s math feedback evolved this year?”, locate Robin and math-related observations, read the dated feedback and sources, and compare the history. “Struggles with fractions” in autumn and “now confident” in spring can both be true; the later observation is not automatically a correction.

**Alternative and tradeoff:** Searching all knowledge from the year avoids topic-index maintenance but costs more reads. Uncontrolled free-text tags are simple but can miss synonyms or confuse children with the same name. A large subject ontology would add substantial maintenance.

**Why it matters:** Serves efficient historical questions, truthful completeness and fresh-agent access (P1–P4, P6, P7; U2).

**Remaining detail / limits:** I still owe you actual entity/topic and directory-entry examples, supported alias rules (for example math/numeracy), date filtering, ambiguity handling, index update/rebuild behavior and a full Robin-query trace. We must define how an agent knows the index covers the requested period; an index hit alone is not evidence of completeness. No search-performance claim is qualified. This question is not ready for final index-contract approval.

## Q3. Should a daily run cover every School-OS-pending item through the start of that run?

**Daily ingestion · Recommendation ready for your decision.**

**Recommendation:** Yes: all relevant material in the configured source/import scope that School-OS has not fully processed, including older unfinished work, through the run-start cutoff. Gmail read/unread status does not define processing. Later arrivals belong to the next run. This is a finite input boundary, not a message-count or batch limit.

**Example:** A run starts at 06:00. An email you opened yesterday still needs ingestion if School-OS never processed it. A relevant attachment left unfinished last week also belongs. Mail arriving at 06:05 waits for the next run.

**Alternative and tradeoff:** Keep admitting arrivals while the run works. The brief can be fresher at the end, but the task can keep expanding and completion becomes harder to define.

**Why it matters:** Serves complete daily information, predictable completion and capable-agent resource management (P1–P4, P6; U1, U5).

**Remaining detail / limits:** The search-time evidence and late-appearing mail policy are question 4. A source that cannot expose the full agreed scope must remain explicitly incomplete. This does not choose the household’s school, mailbox or historical import starting date; setup already asks for those.

## Q4. How should we catch relevant mail that appears late in a search?

**Discovery and missed mail · Recommendation ready for your decision.**

**Recommendation:** Require each selected mail mapping to explain the search time’s meaning, timezone and boundary behavior, and how discovery can account for newly visible older items. Keep the agreed input boundary distinct from original sending Date. If the available route cannot reliably identify changes since the last discovery, re-enumerate the whole configured source range through that run’s cutoff on every daily run, in agent-managed windows. Reuse logical records; whether content can be skipped depends on question 6. The range begins at the household’s chosen import boundary, not the beginning of the mailbox by default.

**Example:** A message sent Monday becomes visible to the connector on Wednesday. Searching only by “sent since Tuesday” would miss it. The agent must revisit a range that includes it, or use a route whose supported discovery behavior includes it.

**Alternative and tradeoff:** Use a fixed overlap, such as the last seven days. That costs fewer reads, but older delayed items can be missed. The fallback repeats metadata listing across that history every daily run. If sufficient reusable coverage evidence is unavailable under question 6, it can also require repeated body and attachment reads. This can be expensive as history grows; it is not yet an efficiency-qualified design. Neither approach can prove completeness when the source itself silently omits or caps results.

**Why it matters:** Serves losslessness, missed-work handling, explicit coverage and agent portability (P1, P2, P4, P6, P9; U1, U2).

**Remaining detail / limits:** Actual connector search semantics and delayed visibility are unqualified. The recommendation supplies a fallback, not a guarantee that hidden source items are discoverable. Save the searched scope and completed/unfinished windows on Drive; follow every continuation. No School-OS batch controller, permanent provider cursor or central scheduler is introduced.

## Q5. How precise must the original email Date be for automatic association?

**Email identity · Recommendation ready for your decision.**

**Recommendation:** Use the stricter proposed threshold: the original individual-message Date must have a known timezone and second-or-finer precision, alongside verified mailbox, original subject, normalized sender, adequate lookup coverage and no comparable contradiction. Try an available richer metadata read when the listing is insufficient; keep the association unresolved if the evidence remains inadequate.

**Example:** “10 September” alone is insufficient under this proposal. “10 September, 08:15:23 −07:00” can qualify with the other required metadata. Several compatible candidates remain ambiguous even with precise dates.

**Alternative and tradeoff:** Allow minute/day precision under an explicit sufficiency rule or source-grounded agent judgment. That reduces unresolved work, but increases the risk of joining distinct messages.

**Why it matters:** Serves metadata-only identity, preserved uncertainty and cross-connector continuity (P1, P2, P6, P9; U1).

**Remaining detail / limits:** No timestamp precision proves uniqueness. Missing optional metadata is unknown, not a contradiction or a reason by itself to create a duplicate. The allowed identity metadata, normalization, per-reply identity and parent-bound attachments are already approved and are not reopened here. The frozen Gmail study did not qualify this stricter threshold or establish distinct logical emails from provider-entry counts.

## Q6. When a matching email appears again, what may the agent safely skip reading?

**Content coverage · Detailed proposal still owed before approval.**

**Recommendation:** Keep prior verified coverage for what it actually establishes. Reuse the logical email under the metadata recipe, but do not give newly encountered or uncertain body/attachment material completion just because metadata matches. Process material whose coverage cannot be established for that appearance; preserve same-parent attachment candidate groups and unresolved inventory.

**Example:** The body was processed yesterday, but a relevant PDF is still unread. Finding the same email today does not complete that PDF. Two same-name attachments in one email cannot inherit each other’s read coverage.

**Alternative and tradeoff:** Always reread every appearance: simpler and more expensive. Skip all content whenever allowed metadata matches: cheaper, but a match cannot establish unread or uncertain content coverage, so that alternative does not satisfy the approved coverage rule.

**Why it matters:** Serves complete extraction, independent source/content coverage and efficient reuse (P1, P2, P4, P9; U1).

**Remaining detail / limits:** I still owe you the concrete reuse decision table: exactly which prior coverage evidence lets an agent skip a body or attachment on a later appearance, what a changed connector or incomplete inventory means, and when rereading is required. The recommendation above preserves approved safeguards but does not settle that rule. It is not ready for final approval. A changed provider handle proves neither new content nor prior processing. Bodies and bytes remain available for extraction only; no hashes, body comparisons or content fingerprints are introduced for source identity or thread association. Finite enumeration and real blockers must not turn into endless reread loops.

## Q7. May a parent explicitly request a manual brief despite known processing gaps?

**Manual briefs · Recommendation ready for your decision.**

**Recommendation:** Yes, only when the parent explicitly chooses a limited manual output after the relevant gaps are made clear. Use verified information and state what is missing prominently. An ordinary request to “send a brief” is not approval to omit known relevant material. Keep the ordinary daily complete-ingestion requirement.

**Example:** The museum notice is saved, but today’s newsletter is unread. The parent says, “Send what you know now and tell me what is missing.” The proposed email would clearly warn that the newsletter might contain a correction.

**Alternative and tradeoff:** Require complete relevant ingestion for every manual brief. This is simpler and avoids sending an update that may soon change, but can delay useful information the parent wants now.

**Why it matters:** Serves useful parent-directed access, honest uncertainty and simple workflows (P1, P3, P6; U2, U5).

**Remaining detail / limits:** This exception remains unapproved. Recipe freedom does not grant it. Existing knowledge-question disclosure and the starter’s failed-task-sync disclosure are already approved. Source scope, recipients and permission to send still come from the authorized request/configuration.

## Q8. Should generated audio be retained on Drive until the parent deletes it?

**Audio storage · Recommendation ready for your decision.**

**Recommendation:** Yes, retain the derived audio with enough source/output attribution to identify what brief it represents, available through the selected instance’s normal references. This makes the same audio accessible to another authorized agent later. Raw email and attachments still remain at their sources.

**Example:** You can ask Gemini Spark for the audio brief previously generated by GPT Work without depending on GPT Work’s temporary workspace.

**Alternative and tradeoff:** Keep audio only at its generating service, or choose a retention period. Those use less Drive storage but can reduce availability or add cleanup rules. Any automatic deletion mechanism would need its own concrete design; none is approved here.

**Why it matters:** Serves reusable outputs, fresh-agent access and source custody (P1, P3, P5–P7; U5).

**Remaining detail / limits:** Actual audio generation, download and Drive upload support remain to qualify later. The minimal output-to-brief/source references belong in the question 1 examples; this does not restore a central jobs/runs registry. There is no selected audio vendor or new permission implied.

## Q9. When both email and audio are requested, should email go first?

**Audio delivery · Recommendation ready for your decision.**

**Recommendation:** Yes as the starter behavior: after complete agreed ingestion, send the authorized text brief without waiting for optional audio. Deliver the audio separately through the configured route when generation succeeds. Report unsupported or failed audio honestly. Users may explicitly choose a conformant combined-delivery recipe instead.

**Example:** The written brief is ready at 06:10; audio generation takes longer. Email can arrive at 06:10. If audio fails, report that failure without describing the already verified email send as failed.

**Alternative and tradeoff:** Wait and deliver text and audio together. That keeps them in one package, but audio failure or delay can hold up the entire delivery.

**Why it matters:** Serves timely useful briefs, optional capability support, recipe choice and truthful outcomes (P3, P4, P6, P7; U5).

**Remaining detail / limits:** Delivery destinations and capable audio/mail routes are selected during setup or the request. An uncertain generation/send uses the already-approved executing-agent verification rule; do not blindly retry or invent a background scheduler. No live send or audio operation is authorized by approving this policy.

## What is settled or outside the MVP

Already approved: D1’s multiple bounded JSON pages and directories; metadata-only identity and separate coverage; small Python helpers with agent/tool operations; setup interviews and shared per-tool semantic adapters; D5 knowledge/task meanings and synchronization; detected completion awaiting parent confirmation; the daily complete-ingestion gate; the starter’s content selection and task-sync disclosure; and any number of user/agent-created brief recipes. You do not need to approve those again.

Still outside MVP: interrupted canonical-write repair, the separate generic records/ordinary-save framework, a central tools/jobs/scheduler register, and packaged installation/upgrades. Questions 1–2 concern specific data-shape and lookup gaps in retained features, not a reinstatement of that framework. Household tool/account choices, source scope (including whether Sent mail is authorized), recipients and selected recipes belong to the already-approved setup/request flow.

## Work and handoff after these decisions

Implementation still owed after the applicable decisions: complete the concrete linked-data examples, startup/storage access, extraction and historical/daily ingestion, query procedures, full task synchronization, brief/delivery/audio procedures, fresh-agent and missed-work guidance, conformant adapter material and prepared checks. Preserve the frozen studies and baseline. The coverage map tracks every retained deliverable and explicit exclusion. Publish the agreed implementation and continuity, verify the remote revision, then stop for your testing direction. Any specific new architecture discovered during that work must be surfaced before adoption; this list is not blanket approval for future choices.
