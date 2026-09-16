# D6 — Freshness first, then the requested brief

The user approved the manual freshness conversation (Q7), rejected retained audio
files (Q8), and selected combined email/audio delivery with a text-only fallback
on audio failure (Q9). The daily run-start scope is also approved (Q3). These
amendments replace the former open retention/order and manual-brief proposals.
The [active plan](../../PLAN.md) records approvals. This is written guidance;
no mail, audio, task update, simulation or test has been executed.

## Ordinary daily brief: complete ingestion first

Use all School-OS-pending mail in configured scope through run start, including
earlier not-ingested emails. Follow discovery continuation, process individual
emails/replies and all required attachments, save substantive knowledge and
sources, and verify persistence. Each email is fully ingested or not ingested.
No partial-email success or agent batch boundary satisfies the ordinary daily
gate. If the declared ingestion cannot be completed, report the scoped blocker.

A fictional 06:00 run discovers a museum-departure correction and a school notice
with an attached consent form. Both emails must be fully ingested before the
daily brief. A 06:05 arrival belongs to the next daily run. Gmail read/unread
status changes none of these obligations.

## One starter, any number of household recipes

The approved starter selects newly verified or substantively corrected knowledge,
shows original school dates and includes relevant open tasks. Keep “Completion
detected — awaiting parent confirmation” distinct from both open work and
parent-confirmed completion. An unchanged reread is not new school news.

Users and agents may create and choose any number of compatible recipes: weekly
planning, one child's learning history, a trip, or an audio presentation. Selection
and presentation vary; source accuracy, truthful coverage and task meaning remain.
Use existing D1 system/instance/extensions separation, not a recipe registry or
scheduler. See [brief instructions](../../../../../operations/brief-recipes.md).

For the starter, a failed task-app sync does not block a knowledge brief after
complete relevant ingestion. Use verified Drive state and disclose that recent
app edits may be missing. Do not claim the two sides agree. Historical import
does not authorize sending a backlog, and action-free information does not
require inventing a task-app write.

## Manual brief: offer to refresh the knowledge first

A parent may explicitly choose a limited manual brief, after the agent explains
that saved knowledge may be outdated and offers to ingest newer emails first.
Describe available last successful ingestion/discovery coverage and original
Date of the newest ingested email relevant to the scope; state unknowns. These
are different dates: a newest email date alone does not establish search freshness.
Do not report a global newest email as proof that a particular child's topic is
current. Do not claim new mail exists unless observed; it may exist.

For example, Gemini Spark finds a saved museum notice but cannot establish that
mail after Monday was ingested. It asks:

> “The trip information may be outdated: I can verify ingestion only through
> Monday, and the newest saved trip email is dated Friday. Would you like me to
> ingest new emails first, or send a brief using this saved information now?”

If the parent chooses refresh, complete the authorized ingestion before composing.
If the parent chooses now, send the authorized manual brief with the same clear
freshness limitation. If refresh is unavailable, explain the capability gap and
let the parent choose a limited result. An ordinary “send a brief” request is
not a choice to conceal a known gap. The normal daily gate remains unchanged.

## Configured audio: together with email, or an explicit failure notice

Audio narrates the same selected verified information, qualifications and task
state as the written brief. When the audio tool is properly configured and
requested, prepare and check the audio before sending the email. Attach or
otherwise deliver the audio with that email through the authorized supported
route. Do not routinely send email first and promise audio later.

If audio generation or preparation fails, send the text email without audio and
include a clear notice such as “The audio brief could not be generated; your
written brief is below.” Do not hide the failure or discard the useful text.
An unknown generation/send outcome is checked using the agent's available means;
it is not automatic permission to resend an email. No timeout, background retry
queue or delivery scheduler is introduced.

A parent may also request delivery directly in agent chat. After verified delivery
to the parent through the selected email or chat destination, audio work is done.
**Do not keep a canonical audio archive on Drive.** Discard accessible temporary
copies after verified delivery. Parent-delivered attachments/chat files and
provider-managed service retention are outside School-OS archive management;
School-OS does not promise to delete those external copies. Useful source and
sender attribution remains, without D7's deferred jobs/runs register.

## The agent validates an uncertain effect

Consider a fictional authorized daily email send. The call yields no usable response. The message may have been sent, accepted but not yet visible, or never applied. The agent first classifies what it actually knows: a missing transport response is not a provider error response; a generic error alone supplies no rate-limit, authorization, timeout or success evidence. It checks the authorized mail service through available sent-output or delivery-lookup tools/APIs, in the relevant account and scope, for the intended content/destination/occurrence evidence. A complete relevant result may support that the effect happened once. A short, stale or empty search may not. Sent evidence establishes sending, not parent receipt or reading.

The same reasoning applies to other authorized effects. A task-app create is checked against the relevant target and School-OS task identity where supported; title similarity is not identity. An audio generation is checked against available artifact/job evidence. Scheduler management is outside the MVP under D7. Provider IDs may help locate current results but cannot become canonical school-email or attachment identities. Each connector’s actual lookup completeness, visibility delay, marker support and permission must be established from that route, not guessed from a vendor name.

The agent **does not blindly repeat an unknown write or send**. If it has evidence the effect was not applied, a retry may be considered under an approved rule; if evidence remains ambiguous, it reports the unknown outcome and stops that effect, or asks the parent for a duplicate-risk decision if a retry is desired. The executing agent uses its judgment over the available evidence and explains the result. This direction does not require a central evidence-threshold table, a new retry service or a job register. New canonical record/adapter meanings still require approval. The user-directed agent-owned validation approach does not guarantee exactly-once external effects or unattended permissions.

The earlier proposal described a common School-OS effect engine with durable owned effect IDs, pre-dispatch intent records and D2-style recovery. **That engine is superseded for this MVP direction**, not reintroduced under another name. Normal successful saving and useful output attribution remain agent obligations, while the user excluded both the separate records/ordinary-save framework and general D2 repair from the MVP. If the agent’s own observation or save is interrupted, the brief must not promise that School-OS can reconstruct every half-written effect record. Any new narrow persistence/continuity protocol is a separate architecture proposal; it cannot be inferred from “validate using available means.”

## Remaining architecture and testing boundary

Q7–Q9 no longer await approval. Concrete Q1/Q2 data/index design and narrow Q4/Q6
discovery/completed-email reuse choices remain in the
[numbered review](../OPEN-QUESTIONS.md). They do not reopen approved brief meanings
or restore the deferred record/save, scheduling or installation frameworks.
Complete retained instructions/code under approved decisions, then publish and
verify the whole agreed MVP and stop for the user's testing direction.
