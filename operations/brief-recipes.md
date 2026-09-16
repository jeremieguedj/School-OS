# Brief recipes

A **brief recipe** is a reusable set of instructions for selecting and
presenting verified School-OS information for a parent. The starter daily brief
is one template, not the only brief School-OS can produce. A parent and capable
agent may create any number of conformant recipes, then adopt the recipe that
fits a particular purpose.

A recipe controls selection and presentation. It does not redefine source
truth, coverage, task state, identity, ingestion completion or the meaning of a
verified external effect. It also does not authorize a source read, task update,
email send, audio generation or schedule by itself.

Read the selected mapping and instance configuration, then use
[query](query.md), [task synchronization](task-sync.md) and
[the data contract](../contracts/data.md) for the underlying information. The
[daily operation](daily.md) establishes the ordinary daily ingestion gate.

## Where recipes belong

A supplied starter recipe belongs with official School-OS material in D1's
`system` area. A compatible recipe created for a household belongs under its
declared ownership in `extensions`. Use the instance's existing readable entry
point and D1 configuration to make the adopted recipe discoverable.

These instructions do not prescribe a filename, registry, canonical recipe
schema, new Drive location, identifier, precedence rule or priority framework.
If two recipes could satisfy the request, ask the parent to choose rather than
silently selecting by file order. Adopting a recipe records a presentation
choice; it does not install code or create a scheduled job.

## Create a conformant recipe

Write the recipe in plain language so another capable agent can answer these
questions without guessing:

- **Purpose and audience:** What question should the brief answer, and who is
  the authorized recipient?
- **Information selection:** Which facts, events, changes, applicable dates,
  children, schools or activities belong in scope? Does this recipe select
  newly learned information, upcoming events, a specific topic or another
  parent-chosen view?
  Show the source's original date separately from when School-OS verified or
  corrected the information.
- **Task selection:** Which relevant open tasks should appear? Keep
  **Completion detected — awaiting parent confirmation** in a separate review
  group. Do not present those tasks as done. Omit parent-confirmed completed
  tasks unless the recipe has a clear retrospective purpose.
- **Coverage needed:** What source and time scope must be completely discovered,
  processed, saved and verified before this brief can truthfully claim
  completion?
- **Presentation:** What concise sections, grouping and level of detail help the
  parent act? Presentation order may be chosen for the written brief; it must
  not alter meaning or hide uncertainty.
- **Capabilities and delivery:** Which selected tool-semantic adapters and
  authorized connector routes are needed to retrieve, deliver and read back the
  result? State unsupported outputs plainly.
- **Failure disclosure:** How will the brief disclose a failed or unverifiable
  task-app synchronization and any other material gap?

Do not copy raw source content into the recipe. The recipe is reusable guidance,
while each brief is composed from current verified canonical knowledge and task
state.

## Select and adopt a recipe

The parent may choose a supplied recipe, choose a household extension, or ask an
agent to draft a new option. Before adopting it, the agent explains its purpose,
selection rule, required coverage, presentation and required capabilities in
ordinary language. Preserve the parent's explicit choice through the instance's
existing configuration; do not add a registry or automatic ranking mechanism.

Selection does not broaden source scope, grant connector permissions, enable
audio, authorize recipients, or approve an automatic send. Resolve those through
the parent's existing choices and the authorization for the current operation.
If the requested recipe depends on an unavailable capability, report the gap or
offer another known recipe for the parent to choose.

## Run a brief recipe

### 1. Select the adopted recipe

Read the recipe selected for this brief and confirm its intended audience and
purpose. Use the selected version as written. If the request would materially
change the selection or delivery, update or create a recipe with the parent
instead of silently changing its meaning.

Use the requested reporting interval and its timezone. If the recipe refers to
the previous brief but that boundary cannot be established from available
configuration or evidence, obtain the missing interval rather than inventing
one from another agent's chat. An explicit current choice requires no repeat
confirmation. A manual brief is a new requested output, not automatically a
retry of a scheduled send.

### 2. Establish scope and capabilities

Resolve the recipe's source, child, school and time scope against the parent's
authorized configuration. Confirm that the executing agent has usable routes
for the required reads, task state and requested delivery. A connector name is
not evidence that the route can enumerate, update, send or verify the required
operation.

### 3. Complete the required ingestion and coverage

For an ordinary daily brief, complete all relevant School-OS-pending material
within the configured source/import scope through the start of the run, including
older unfinished work. Later arrivals belong to the next run. The mailbox's
read/unread icon does not define what School-OS has ingested. Validate discovery,
processing, normal saving and verification before composing; an agent's internal
batch boundary does not satisfy this gate.

A logical email is either **fully_ingested** or **not_ingested**. Full ingestion
requires its body and required attachment material to be read and substantively
extracted, with resulting knowledge, source references and actual coverage saved
and checked. Required attachments remain in scope; incomplete required content
means not ingested. No partial-email completion/resume workflow is selected.
Internal processing evidence must remain honest. If relevant ingestion or
coverage is blocked or unverifiable, report the blocker and do not issue the
ordinary completed daily brief. Reuse a fully ingested logical email only under
the approved metadata and Q6 rule in [ingestion](ingestion.md). A known new reply,
new required attachment, contradiction or incomplete prior result cannot inherit
the earlier completion.

For a **manual** brief, the parent may choose a limited output from currently
verified information after the following disclosure and choice:

1. Warn that the saved knowledge may be outdated, even when no specific newer
   instruction is known. State known gaps, the latest relevant source date
   available in verified knowledge, and known ingestion freshness. If a date or
   freshness is unknown, say so. A latest saved source is not necessarily the
   latest email the school sent.
2. Ask whether the parent wants fresh mail ingested first or the current verified
   information sent now with those limitations. An ordinary request for a brief
   does not silently select the limited path. Honor an explicit answer already
   given rather than asking again.
3. If the parent chooses ingestion first, complete the needed work within
   authorized scope and capability. If the parent chooses the limited brief,
   include its source dates, freshness warning and material gaps in the output.
   Do not describe it as complete or current beyond the supporting evidence.

This manual choice is approved. It does not relax the ordinary daily ingestion
gate or authorize wider source access, new recipients or an automatic send.

### 4. Retrieve verified knowledge and task state

Retrieve the canonical information selected by the recipe. For the starter
daily brief, include newly verified or substantively corrected information,
show the original school dates, and include relevant open tasks. Separate tasks
awaiting parent confirmation from open work and from parent-confirmed completion.

Use substantive Knowledge and its ingestion evidence, not the timestamp of a
directory rebuild or file move, to decide what is newly verified. A routine save
does not make an old school notice new. Follow incoming corrections and preserve
the distinction between changing circumstances and correction of a false prior
statement. Resolve child, household and school applicability through dated
membership; return one shared fact or household Task once. A custom recipe may
select older applicable information even when it is not new in this interval.

Use the current verified task state available to the operation. If task-app
synchronization failed, was incomplete or could not be verified, disclose that
fact in the brief; do not present the app as current or silently substitute title
matching.

### 5. Compose without changing meaning

Apply the recipe's headings, grouping and concise wording. Preserve source
attribution, original date precision, qualifications and material uncertainty.
Do not turn an inferred preference into a school requirement, an upcoming item
into an overdue task, or a pending parent confirmation into completion.

For the supplied starter, write:

1. A short heading with the reporting interval and covered school/household scope.
2. Newly verified information and substantive corrections, with readable source
   references and original school dates. State qualifications beside the item.
3. Relevant open actions, showing the school deadline separately from the
   parent's planned date and owner. Show conditional applicability honestly.
4. A separate **Awaiting your confirmation** group with linked source evidence.
   A rejected suggestion is not included again on the same evidence.
5. Any material coverage/freshness or task-app synchronization limit, and the
   actual generating agent. An empty update section may say no newly verified
   information was found only for the supported complete scope; it does not mean
   no obligations remain.

Do not copy whole raw emails into the brief. Retain substantive details needed
by the parent and readable provenance; canonical Knowledge remains the durable
source-linked record. For other selected recipes, use their presentation while
preserving the same truth and coverage requirements.

### 6. Deliver only when authorized, then verify

Use the authorized route and recipient for this run. When audio is configured
for an email brief, prepare text and audio for delivery together. If audio
generation or availability is verified to have failed, send the text email with
an explicit notice that the audio failed. Do not silently send text first while
audio is still being prepared, and do not label an unknown audio outcome as a
verified failure. This instruction sets no new timeout, deadline or scheduler.

Inspect the actual delivery result through available authorized evidence. A
generic success response does not prove delivery, and an unknown generation or
send outcome must be reconciled before any repeat. Apply the existing agent
verification rule; do not blindly resend or generate again. Report what was
verified and any remaining uncertainty.

Identify the agent that generated the brief separately from the actual service
and account that sent it, where observed. Include the reporting scope, source
references and generated time in the output or its accompanying report so a
parent can understand what it represents. Never guess a sender from the agent's
brand. State whether there is a draft, a verified sent output, a verified failure
or an unresolved outcome, with its usable output reference when available.
This is attribution for the current output, not a central job/run registry or a
claim to inventory every household job.

School-OS keeps no canonical audio archive. After audio delivery to the authorized
email or chat destination is verified, discard the accessible temporary audio
copy. Preserve needed source/output attribution without retaining audio bytes on
Drive. Do not claim deletion of provider-managed copies or the parent's delivered
copy. If delivery is uncertain, establish the outcome before claiming delivery
or cleanup on that basis.

Adopting a recipe never creates an automatic send or schedule. Scheduler and
installer infrastructure remain outside this operation.

## Fictional recipe examples

These are written illustrations only. They were not run and make no claim about
connector or provider support.

### Starter daily brief

For fictional parent Avery, select school information first verified or
substantively corrected in the chosen daily reporting interval. Show the school's original
date beside each update. Follow with relevant open tasks, then a separate
**Awaiting your confirmation** section. If the task app could not be synchronized
and verified, say so directly even when ingestion and the email brief itself are
complete.

### Weekly planning brief

For fictional siblings Mina and Theo, group the coming week's verified events
by day, then list relevant open tasks by child. Include still-relevant older
notices even if they were processed weeks ago: this recipe selects upcoming
events rather than only newly learned information. Show original source dates
so those notices are not mistaken for new school publications.

### Trip brief

For a fictional museum trip, collect verified arrival instructions, permission
requirements, clothing guidance and relevant open tasks from the declared
trip scope. Keep a returned-form acknowledgment under parent confirmation until
the parent checks the linked task complete. Do not pull unrelated school news
into the trip brief merely because it is recent.

If the latest verified trip notice is old or a newer newsletter is not ingested,
warn Avery that saved knowledge may be outdated. State the known source date
and ingestion freshness, then ask whether to ingest fresh mail first. Avery may
instead explicitly choose a brief now that states those limits. This manual
choice does not mark the missing material ingested.

### Optional audio companion

Narrate the same selected canonical information as a written brief, including
qualifications and task-sync gaps. Audio remains optional and capability-led.
When configured for email, prepare it with the written brief and deliver them
together. A verified audio failure produces the authorized text email with an
audio-failure notice. An unknown outcome first requires agent verification;
it does not justify a blind retry. Discard accessible temporary audio after
verified delivery to the authorized email/chat destination; do not create a
canonical archive or claim control over provider-managed copies. The recipe
does not authorize generation or sending on its own.
