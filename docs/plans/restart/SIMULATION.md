# School-OS architecture simulation

Keeping original material in its source system is the right default for
School-OS. It removes duplicate archival storage and transfer from everyday
operation, fits replaceable managed agents, and concentrates the product on
useful knowledge and operational visibility. Its important tradeoff is that
rechecking an original requires continued source access. Drive preserves what
was cataloged and where it came from; it cannot reconstruct an uncataloged
detail after the original disappears. That tradeoff is acceptable for the
chosen product, provided coverage and provenance are honest.

The updated [product principles](../../product-principles.md) make this choice
explicit. They also allow any number of agents/jobs, require a tools and
schedulers register, add the known-scheduled-jobs query, and exclude concurrent
updates to the same Drive data from the current scope. No locks, leases,
fencing or concurrent-write conflict engine were simulated or proposed.

## Method and result

The executable [state model](simulation/run_model.py) ran against
[15 fictional communications](simulation/source-fixtures.json) and a separately
authored [semantic expectation fixture](simulation/semantic-expectations.json).
It recorded **60 system states and 96 passing assertions**. The final modeled
instance contains **15 source records, 21 knowledge facts, four canonical
actions, three registered jobs and two output runs**. Twelve messages belong
to the historical interval and three to the subsequent daily interval.

This is an executed, deterministic architectural simulation. It is not a live
Google Drive test, a vendor-agent benchmark, a real attachment parser test or
evidence of LLM interpretation quality. Correct semantic candidates are
supplied by the expectation fixture; the model checks when those candidates
may become available, their persistence, identities and relationships. Query
checks establish that the necessary evidence and task state exist; they do
not generate or grade natural-language answers.

A separate [interpretation review](simulation/INTERPRETATION-REVIEW.md) used a
fresh Codex agent without access to the expectation file or model. It recognized
four distinct requests and two corrections and exposed an omitted term-wide
qualification and page references in the initial expected catalog. Those were
repaired before the final run. The supplied input also contained scenario hints,
so this was only partly blinded; it is not a target-vendor benchmark. The review
explains its assumptions and preserves the independent output.

Corrupted readback is injected and compared for source records. Facts and
actions are checked for their resulting presence and relationships, but separate
lost or altered writes to those derived records are not independently faulted
or read back. Multi-record provider verification remains a live-test requirement.

The named cloud-agent roles express scenarios and documented restrictions.
Successful reads/writes are conditional assumptions of a qualified connection.
An unknown or contradicted tool capability is not assigned a successful
operation merely because the product is named. No personal mailbox was read,
no source archive was created, and no live schedule or email was sent.

The Python script is a developer's analysis instrument. The proposed household
system does not require installing it, running a coding CLI, mounting Drive or
keeping a personal computer awake.

## State ledger

The [readable ledger](simulation/results/state-ledger.md) shows every transition.
The [full snapshots](simulation/results/state-ledger.json) preserve modeled
Drive state, external provider state and temporary-file references separately.
The [final state](simulation/results/final-state.json) and
[assertion results](simulation/results/checks.json) are independently inspectable.
Snapshot duplication is simulation evidence, not a proposed production log format.

| Stage | State and behavior observed in the model |
|---|---|
| Setup | Pinned instance instructions, two stable source accounts, replaceable connections and sending defaults. No raw archive or global active-agent setting. |
| Historical discovery | First page discovers five messages; enumeration remains incomplete. A later rescan consumes all pages and deduplicates already known identities. |
| Interruption before persistence | Temporary source material is discarded. A fresh session refetches the indexed item; no completion was claimed. |
| Interruption after source indexing or facts | Catalog presence is distinct from completed interpretation/task reconciliation. Pending work prevents incomplete results appearing verified. |
| Lost write response or bad readback | Existing records are reconciled rather than duplicated. A readback mismatch keeps verification pending. |
| Scheduling during import | Daily catalog and weekly audio jobs are registered while historical sources remain unfinished. The second creation loses its response; its actual schedule is adopted after an accessible inspection. |
| Limited source reader | Bodies and ordinary text attachments produce useful knowledge. The image instruction, oversized handbook and unavailable club timetable remain explicit gaps. |
| Missed daily invocation | A later invocation processes the missed January 13 interval. Three daily messages complete without closing the three outstanding historical attachment gaps. |
| Replies and corrections | A quoted older exhibition date remains historical; the inline correction is available as newer evidence. The corrected fee deadline survives replay of the older message. |
| Parent state | A recorded swimming-consent completion and its evidence survive a later reminder. A parent planning date survives source replay separately from the school deadline. |
| Alternative reading route | Under an explicitly assumed vision/chunked route, two gaps close. The unavailable attachment remains unread until a separate restoration event, then adds two facts. |
| Another agent's queries | A fresh reader retrieves knowledge and registered-job information from serialized Drive state. Before the timetable is read, the club-time query reports the gap. |
| Sending and attribution | A lost send response stays pending when inspection is unavailable. With matching sent evidence, the existing effect is adopted. Historical generator/scheduler/sender attribution survives a later sender change. |
| Backup agent | A separately registered backup recap coexists with the two existing jobs. Editing a default alone does not rebind an existing job. |
| Inaccessible scheduler/source | Requesting a pause does not change the last observed enabled schedule. Deleting an original does not erase previously cataloged knowledge, but new source verification fails. |

The final zero pending-source count is conditional on the deliberately assumed
alternative reading/restoration events. It is not evidence that any particular
vendor supplies those routes on the intended account.

## Message, thread and attachment identity

The central rule is:

`source message = provider + stable logical mailbox identity + provider message ID`

A logical mailbox is separate from its current connector, authorization record
or agent. Reconnecting or switching adapters maps back to that same mailbox
after account verification. Gmail documents distinct immutable message and
MIME-part IDs; thread IDs group messages rather than identify the whole source
history as one immutable object.[^1]

| Identity case | Simulated check and conclusion |
|---|---|
| Same message fetched again | Reuses its source identity and semantic records. Retry does not create a new communication. |
| Adapter replacement | Source key is unchanged because adapter/connection ID is not part of it. |
| Same ID string in two mailboxes | Produces two distinct source records. Access and provenance remain mailbox-specific. |
| Identical communication in two mailboxes | Keeps two source occurrences. Any decision to share one task requires meaning and household context; matching bytes alone do not decide that. |
| Reply in an existing thread | New message ID produces a new source occurrence. Thread grouping and quoted material do not turn the whole conversation into a new source. |
| Quoted history and inline response | The fixture includes an inline correction inside quoted discussion. Both historical and corrective facts remain available; quoted questions produce no additional task in the supplied interpretation. Actual extraction of that meaning remains an LLM test. |
| Two attachments named `menu.pdf` | Different part IDs remain different occurrences; queue instructions cannot be substituted for menu contents. |
| Same attachment bytes in another message | Distinct source parts retain both provenance links even when they support the same knowledge fact. |
| Same bytes in two parts of one message | Distinct part occurrences remain distinct. A content hash is not an occurrence identity. |
| Changed attachment retrieval handle | Cloned observations use different handles but the same message/part identity. The canonical part key remains unchanged. |
| Missing stable part identity | Filename, size and hash do not manufacture an exact occurrence match. The model returns unresolved; an adequate inventory/read route is required. |
| Inline image and MIME alternatives | A meaningful inline image remains required; a decorative image/container contributes no substantive fact. Equivalent plain/HTML alternatives do not duplicate knowledge in the supplied expectation. |
| Attached email | Its embedded header identity does not become a separately received top-level source. Nested parsing and full MIME-coordinate matching are not implemented by this model. |
| Scope boundary | Account/date scope is applied per message using a half-open interval. Historical context returned in daily thread results is excluded from daily acceptance. Sender/label and alias behavior require separate live qualification. |

A provider's native attachment retrieval field and a connector's download
locator must not be conflated with durable part identity. Gmail documents
`attachmentId` as a separate retrieval handle; this review does not claim that
Google's native field necessarily rotates. The earlier project observed
changing connector-exposed identifiers. The new model tests independence from
such a handle rather than preserving that failure in canonical identity.[^2]

When a connector omits stable part IDs, a route exposing the complete source
structure can potentially supply a reliable mapping. That must be demonstrated;
filename-only matching is insufficient when duplicates exist. The baseline
does not require every agent to hash all raw content, reconstruct MIME or
invent a matching result.

A real source-index trial must also exercise nested multipart messages,
attached/forwarded emails, valid empty root-part identifiers, and missing
identifiers. The adapter must distinguish a known structural root coordinate
from absent inventory. RFC email headers, subjects, filenames and thread IDs
can help locate related material but must not silently replace the mailbox's
native message identity. These parser and connector cases are not implemented
by the synthetic part-label checks above.

## Problems exposed and corrections

The first model passed weak checks while retaining errors. Independent review
and stronger assertions exposed the following, which were repaired and rerun:

1. **Repeated facts lost their earlier provenance.** A dictionary keyed by fact
   identity replaced its first source with the second. Facts now retain a
   deduplicated list of source/part occurrences. A repeated source replay leaves
   that list unchanged.
2. **Parent completion was attached to the wrong task.** The initial harness
   completed the first action rather than the explicit fixture event. The model
   now applies the event to its named task and preserves its evidence through
   the reminder.
3. **Read and write progress were conflated.** A catalog record or a lost write
   response could appear complete too early. Pending processing/verification
   remains separate from accepted source coverage, and queries exclude
   unverified evidence.
4. **Old-source replay could reverse a later deadline correction.** The modeled
   action keeps the later source values and all source support. Its parent date
   remains separate. This scenario uses explicit dated corrections; it does not
   establish a universal “latest timestamp wins” semantic rule.
5. **Historical and daily progress needed separate tracks.** Daily success no
   longer hides old attachment gaps. Enumeration, processing and specific
   pending parts are distinct information in the work record.
6. **Current settings could misdescribe historical outputs.** Each output keeps
   the run's generator, scheduler, sender and configuration revision. Defaults
   and existing job bindings remain separate.
7. **The job register understated the input scope.** An early daily job listed
   only one connection while processing two mailboxes. Its source bindings now
   list both, with an assertion connecting the registered scope to the selected
   messages. Knowledge-only briefs do not inherit an unnecessary source binding.
8. **The expectation fixture omitted surrounding qualifications.** The separate
   interpretation retained the handbook body's term-wide applicability and page
   references that the original expected facts omitted. The final catalog keeps
   them and their body/attachment provenance. It also preserves the reminder's
   immediate instruction separately from the original due date. State checks
   alone had not detected those semantic omissions.

The model also stopped treating copied expected prose as a successful query
answer. Its final query checks expose available evidence and task state, with
natural-language generation explicitly marked untested.

## Check against the product principles and use cases

The proposed durable structure has five kinds of information: a small entry
point with pinned instructions/configuration; a precisely identified source
index with read coverage; substantive knowledge and canonical tasks; bounded
unfinished-work records; and the tools/jobs/runs register. These are logical
records, not a requirement for five files or one file per record. Exact Drive
file/table layout remains a decision for a small live read/write experiment.
The model stores its state in memory and does not prove a scalable Drive query
layout by itself.

| Design priority | What this exercise establishes | What remains unresolved |
|---|---|---|
| 1. Losslessness and provenance | Facts retain exact source/part support, shared facts retain multiple occurrences, and unread attachments remain visible gaps. | Complete semantic extraction, visual/table reading, and arbitrary future questions require actual-agent testing. No archive means uncataloged details depend on the original remaining accessible. |
| 2. Deterministic behavior | Stable identities, separate progress and observed-effect records make replay and modeled recovery repeatable. | Deterministic persistence does not imply identical reasoning across agents. Semantic conflicts need evidence and an explicit decision record. |
| 3. Simplicity | The normal household flow uses small records and no global active-agent or concurrency subsystem. | The simulation harness is not proposed production infrastructure. Adapter/setup complexity must be measured on a first real journey. |
| 4. Efficient execution | Historical/daily work is separated; a modeled per-read budget prevents assuming unlimited source reads. | No VM, token, latency, cost or growing-Drive benchmark was performed. Whole-history loading in the development model is not an acceptable production query strategy. |
| 5. Tool agnosticism | Source identities survive connector replacement; jobs keep distinct bindings and outputs retain historical attribution. | Adapter round trips and source identity agreement across real tools remain unqualified. |
| 6. Capability-led portability | Blocked and unknown capabilities prevent modeled success; serialized Drive records permit session replacement. | This is one local analysis instrument, not execution inside five vendors' cloud products. Unattended permissions and recovery must pass there. |
| 7. Extensibility from canonical data | Queries and multiple registered output jobs reference the same instance knowledge. | No independent task application, audio generator or third-party extension is implemented/tested here. |
| 8. Extensible/upgradable instances | The proposed entry point pins instructions and leaves private state separate. | A pinned release string is not an upgrade test. Installation, migration and preservation of user extensions remain untested. |

| Core use case | Simulation coverage and limit |
|---|---|
| Catalog communications | Twelve historical and three daily messages, attachment gaps, replay and interruption are modeled. Real connector enumeration/parsing and interpretation fidelity need separate evidence. |
| Query school information | Required evidence exists for nine completed query cases; an additional pre-read club query records its missing attachment. This is evidence availability, not answer quality. |
| Ask any reader about known jobs or a brief's sender | The register exposes multiple jobs, host references, observed status/freshness, and historical output attribution. No access to another vendor's scheduler is assumed. |
| Reconcile tasks and sync a selected task application | Four canonical tasks, correction, parent completion and parent planning are modeled. External task synchronization is not tested. |
| Recent email/audio briefs | Scheduling and a modeled send/lost-response recovery are exercised. Brief composition, recency selection, audio synthesis and delivery are not executed. |
| Add applications/workflows | An additional recap job can coexist and reuse canonical knowledge. Extension implementation and compatibility checks are not executed. |
| Install/upgrade a supplied release | Setup state is initialized, but ZIP installation, published release admission and upgrade/migration are not exercised. |

The exercise supports the central ingestion/continuity design; it does not
establish full product acceptance. For development velocity, qualify one small
complete managed-agent journey before choosing the physical Drive layout or
expanding adapters. Reuse that same fictional instance for subsequent probes;
do not restart a full release/install cycle to diagnose each connector mismatch.

## Limits grounded in the target agent environments

| Boundary | Evidence and consequence |
|---|---|
| Cloud state and temporary files | Work and Cowork distinguish execution storage from account-saved records. Cleanup means removing accessible working downloads, not guaranteeing erasure from provider histories, snapshots or backups.[^3] |
| Complete attachment reading | Cowork's documented Workspace connector exposes Gmail attachment metadata, and text extraction omits embedded images. The new no-archive design removes upload work, but cannot remove the need for a capable reader.[^4] |
| Scheduled shared-file writes | Spark requires review for shared-file edits; custom MCP writes require confirmation. A job can launch and still be unable to catalog unattended. If every Drive write is blocked, it cannot even save a new Drive checkpoint explaining the block.[^5] |
| Session/usage limits | Work and Cowork usage windows are accounting constraints, not guaranteed uninterrupted task duration. The simulated reset tests durable progress, not a vendor promise about compaction or runtime.[^6] |
| Grok Bot writing | Published native-write help conflicts with dated connector withdrawal statements. The model records an unqualified write path rather than assuming it works.[^7] |
| Meta Muse access | Public connector documentation does not establish the complete Google read/write operation set. The unknown-capability scenario performs no successful canonical operation.[^8] |
| Source enumeration | Gmail list results are paginated, and result-size estimates do not prove completeness. Thread search can surface messages outside the qualifying scope. Exact reads and per-message selection remain necessary.[^9] |
| Missed runs and old history | Schedules can skip or pause. Provider history can expire. Received-date overlap helps normal catch-up but cannot guarantee finding arbitrarily old newly imported mail; incremental change access or a deliberate bounded rescan is needed.[^10] |
| Another agent's scheduler | Reading the Drive register establishes known configuration and last observation, not live host access. There is no universal cross-vendor schedule-control API assumed by the architecture. |
| Resource limits | The model enforces an **8 MiB transfer quantum as a scenario parameter** and records a maximum modeled quantum of 8 MiB. This does not measure VM memory, parser expansion, tool response limits, or actual streaming availability. Those remain live tests. |

The fixture hashes cover short synthetic text surrogates, not real PDF/image
bytes. Declared attachment sizes exercise the modeled admission/chunking rule;
they do not allocate those bytes. No reported number estimates real throughput,
token consumption, cost or wall-clock duration on a vendor's product.

## What the simulation supports

The architecture is coherent for the intended household workflow if a selected
agent can read the required sources and persist small verified Drive changes.
The source index, substantive knowledge, separate progress tracks and operational
register are sufficient durable concepts for the modeled journeys. Mandatory
archival or global agent exclusion would not resolve the actual remaining
capability gaps.

The next useful tests are narrow and run in the actual managed/cloud apps:

1. Retrieve a real synthetic message and its attachments with stable identities
   exposed; switch readers and verify the same occurrences can be found.
2. Round-trip a small source, fact and task record on the selected Drive layout,
   including blank fields and interruption between separate writes.
3. Run a tiny scheduled catalog operation with personal devices off and no
   parent present; observe actual permissions and persisted output.
4. Start a different agent with the Drive entry point alone; answer a cataloged
   query and list known jobs with honest freshness, then refetch one original.
5. Measure one realistic historical batch and one day of work, including large
   and visual attachments, setup, approvals and recovery effort.

Simultaneous same-data Drive writes remain outside scope. These tests must not
grow into a concurrency subsystem or a requirement for a dedicated CLI host.

## Reproduction and verification

From the development repository, run:

```text
python3 docs/plans/restart/simulation/run_model.py
```

The command regenerates the four result files. It makes no network calls and
does not import the old School-OS runtime. The result records fixture hashes
and the explicit untested categories. Repository validation of the unchanged
runtime is separate from this architectural simulation.

## Sources

Primary documentation was reviewed September 11, 2026. Undated pages are current
documentation observations, not guarantees about every account or future release.

[^1]: Google, [Message and MessagePart resources](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages), updated May 6, 2026.
[^2]: Google, [MessagePartBody](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages.attachments) and [attachments.get](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages.attachments/get).
[^3]: OpenAI, [Work cloud security](https://learn.chatgpt.com/docs/enterprise/chatgpt-work-cloud-security) and [file retention](https://help.openai.com/en/articles/8983778-chat-and-file-retention-policies-in-chatgpt). Anthropic, [Cowork architecture](https://support.claude.com/en/articles/14479288-claude-cowork-architecture-overview).
[^4]: Anthropic, [Google Workspace connectors](https://support.claude.com/en/articles/10166901-use-google-workspace-connectors).
[^5]: Google, [Spark operations](https://support.google.com/gemini/answer/17094507?co=GENIE.Platform%3DDesktop&hl=en) and [custom apps](https://support.google.com/gemini/answer/17209137).
[^6]: OpenAI, [Work/Codex usage](https://help.openai.com/en/articles/20001516-managing-usage-with-gpt-6-astra-in-work-and-codex). Anthropic, [usage and length limits](https://support.claude.com/en/articles/11647753-how-do-usage-and-length-limits-work).
[^7]: Cursor, [Docs/Sheets withdrawal and follow-up](https://forum.cursor.com/t/grok-bot-drive-mcp-should-write-google-docs-body-and-sheet-cells-not-only-file-metadata/169971), staff correction August 31 and follow-up September 8, 2026.
[^8]: Meta, [Muse connectors](https://www.meta.com/help/artificial-intelligence/1687253048996149/).
[^9]: Google, [messages.list](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/list) and [Manage threads](https://developers.google.com/workspace/gmail/api/guides/threads).
[^10]: Google, [Spark schedules](https://support.google.com/gemini/answer/17094710), [Gmail synchronization](https://developers.google.com/workspace/gmail/api/guides/sync), and [Search and filter messages](https://developers.google.com/workspace/gmail/api/guides/filtering).
