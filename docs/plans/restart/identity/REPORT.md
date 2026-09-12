# Email identity across agents and connectors

School-OS should assign its own durable identifiers to source records. A
provider message ID is a useful access aid when its meaning and scope are
known; it must not be the primary key on which knowledge, tasks and continuity
depend. The same applies to attachment download handles, thread IDs and agent
citations. Critical identity and acceptance decisions use the source’s own
information and content; even a documented stable provider ID is only an access
aid, never an alternative authority for those decisions. The earlier
simulation's provider-derived source-key rule is
superseded by this design.

**Qualification update:** the subsequent
[raw-MIME evaluation](mime-evaluation/README.md) found false splits, an incorrect
content association and timestamp/environment limitations in the illustrative
matching pipeline. Its 54 observations include real synthetic MIME and binary
payloads. The principles below remain the design direction, but the 38-case
prepared matcher is not a qualified implementation of them. Required refinements
and untested capabilities are recorded in that evaluation.

The evidence supports two distinct conclusions. Native Gmail message IDs were
stable in a short live test and are explicitly documented as immutable.
Nevertheless, a universal identifier contract across mail providers, agent
connectors and harnesses does not exist in the reviewed documentation. Some
provider IDs change in defined lifecycle events; connector field names and
model-visible data differ concretely across implementations. A fallback is
therefore required even when Gmail works correctly today.

## Live Gmail observation

The [aggregate receipt](live-probe-summary.json) records a read-only test lasting
121.7 seconds on the currently connected Gmail account, September 11 local time
(September 12 UTC). Existing mail was used; no email was sent, modified or
labeled, and no attachment download was requested. Complete diagnostic receipts
were retained privately before interpretation; none of their identifiers,
addresses, subjects, bodies or source URLs is included here.

| Observation | Result |
|---|---|
| Selected messages | Seven distinct messages across two bounded thread windows of four and three messages |
| Replies | Six had `In-Reply-To`; five had their referenced parent within the selected sample |
| Full message observations | 63: three single-message rounds, three batch rounds and three thread rounds, giving nine observations per selected message |
| Additional metadata reads | Seven |
| Native message IDs | Stable for all seven messages across the compared routes |
| Thread IDs and RFC identity/reply headers | Stable throughout the test |
| Independent corroboration | RFC headers, sender/recipient/date/subject and internal timestamp, plus exact decoded text MIME content, agreed across all full routes |
| Thread access | Both thread-ID lookup and lookup through a particular reply's message ID worked |
| Search | Three searches and three ID-only searches returned the same eight IDs in the same order; three results independently matched selected full reads by subject, timestamp and normalized snippet |
| MIME parts | All 40 observed coordinates/part IDs remained stable |
| Attachment retrieval locators | All 15 populated locator slots changed across repeated reads |
| Provider operations | 46 read calls, zero reported errors, zero mutations, zero attachment-download calls |

The seven-message comparison did not identify a message solely by asking
whether its ID matched. Headers and text were independent witnesses. The
search/full comparison was narrower: three overlapping messages had enough
independent search metadata to cross-check. Thread windows may omit older
messages. Attachment bytes were not compared, so stable part coordinates do
not establish byte equality.

This establishes short-window stability for this account and connector. It
does not test a new conversation, OAuth reconnection, another account, provider
migration, connector update, folder mutation or another vendor's application.
The changing attachment locators corroborate the need to separate retrieval
handles from durable identity; they do not demonstrate a native message-ID
change. Earlier project evidence described an attachment-locator mismatch,
not established mutation of a Gmail message's native ID.

## Which identifier is being discussed

| Identifier | What it identifies | Appropriate School-OS treatment |
|---|---|---|
| School-OS record ID | A durable record within the private instance | Canonical reference used by knowledge, tasks and work records |
| Native provider message ID | A provider's message object, within a defined account/lifecycle | Optional typed lookup alias; retain exact value and scope |
| RFC `Message-ID` header | A sender-generated identifier for a particular message version | Optional search term; never decides identity or acceptance |
| Thread/conversation ID | A group of messages | Context and discovery hint; never substitutes for an individual reply |
| `In-Reply-To` / `References` | Claimed relationship to previous RFC message identifiers | Thread relationship evidence, not the current message's own identity |
| Attachment/part identifier | A part within a particular provider representation | Optional part lookup/structural evidence scoped to the parent |
| Attachment download token or URL | A current retrieval route | Replaceable locator; expiration/change does not rename the source |
| Tool-call ID or citation index | A tool invocation or position in generated output | Execution/display metadata; not a mail key |
| Content fingerprint | Equality of a declared content representation | Corroborating evidence; neither authorship proof nor unique physical occurrence |

A string called `message_id` does not resolve these distinctions. Pipedream's
current Find Emails implementation preserves Gmail's native `id`, but separately
sets `message_id` from the RFC header. Composio explicitly uses `message_id` for
Gmail's native API key and excludes the RFC header and thread ID.[^11][^12]

## Provider and protocol guarantees

Google's Gmail API names the message `id` and MIME `partId` immutable. Its
`historyId` is a changing history marker, and `threadId` is a separate grouping
field. Those are meaningful guarantees for the identified resource, not for
every string emitted by an agent connector.[^1]

Gmail draft editing replaces the underlying message, changing its message ID;
sending a draft creates a sent message with a new ID. A stable draft container
ID and a message ID therefore describe different resources.[^2] Gmail's IMAP
extension exposes the native message identifier as a decimal integer, while
the API uses its hexadecimal representation. A different representation can
look like a different ID; conversion must be documented and lossless, never
inferred from a generic field name.[^3]

Outlook's default Microsoft Graph message ID changes on folder moves. The
optional `Prefer: IdType="ImmutableId"` applies per request and remains stable
within the same mailbox, including folder moves; archive-mailbox moves and
export/reimport are exceptions.[^4] `internetMessageId`, `conversationId`,
`changeKey`, `webLink` and `id` are explicitly different fields.[^5] This is a
direct counterexample to a universal “email provider IDs always remain static”
rule, regardless of which AI calls Graph.

IMAP sequence numbers are positions and can change. UIDs must be interpreted
with mailbox and `UIDVALIDITY`; the protocol allows detectable UID changes
between sessions.[^6] JMAP defines a different object model: Email IDs survive
mailbox changes, but a server merging threads may delete and reinsert affected
Email objects with new IDs.[^7] Provider objects and the human idea of “the same
email” do not have identical lifecycle boundaries.

RFC 5322 recommends, rather than universally requires, a `Message-ID` header.
It defines `In-Reply-To` and `References` separately and requires generators to
make message identifiers unique.[^8] RFC 7352 explicitly acknowledges that
real Message-ID uniqueness can fail, and headers can be missing or repeated.[^9]
Replacing the provider ID with the RFC header alone would merely exchange one
dependency for another.

The Apps Script `GmailThread.getId()` documentation explicitly warns that its
thread ID varies with contained messages. That statement is specific to this
surface; it is not evidence that every REST `threadId` changes in the same
way.[^10] A thread's first message may be useful context, but its ID cannot
identify every reply in that thread.

## Agent and harness coverage

The survey covers the five target product families, Microsoft Copilot, major
programmable mail integrations, general agent SDKs and representative public
MCP implementations. It does not claim to enumerate every marketplace server,
private tool, version or future harness. One counterexample disproves a global
guarantee; certifying every integration would require an inventory and live
tests that do not currently exist.

“Undocumented” below means the reviewed public material does not establish the
contract. It does not mean an identifier is absent or has been observed changing.
Public documents and floating source branches were inspected September 11,
2026; a production adapter must qualify its actual installed version.

| Surface | Evidence about identity and access | Portability conclusion |
|---|---|---|
| Current Codex Gmail plugin | Available tool declarations explicitly name immutable Gmail API IDs, distinguish thread IDs, and provide full/metadata/raw formats. The live test above corroborates current behavior. | Good native-ID evidence for this connection; not a perpetual guarantee for every OpenAI surface. |
| OpenAI Responses Gmail connector | Official guide describes Gmail message-ID search and message reads; outer `mcp_call.id` identifies the invocation.[^13] | Native keys are exposed on documented paths. Do not confuse them with invocation IDs. |
| GPT Work / ChatGPT / Codex product family | Shared plugin catalog is documented; execution surface and policy affect capabilities.[^14][^15] | A shared catalog does not establish identical output contracts everywhere. |
| Claude / Cowork built-in Gmail | Public help describes mail access, citations and original-source links without a returned-ID schema or lifetime contract.[^16] | Native/RFC ID exposure and persistence require actual tool inspection/testing. |
| Claude custom tools / Agent SDK | Server-defined output; documented TypeScript/Python result handling differs; large outputs can become file references.[^17][^18] | SDK name alone establishes neither mail identity nor full-body visibility. |
| Gemini Spark | Workspace/Gmail integration and custom MCP support are documented, without a public built-in mail-ID lifetime schema.[^19][^20] | Built-in connector, custom server and browser path must be assessed separately. |
| Gemini within Gmail | Thread/search capabilities and source citations are documented; source lists carry documented limitations.[^21] | A conversational citation is not sufficient canonical identity evidence. |
| Grok Bot / Grok Gmail connector | Bot documents connector use; Grok's separate Gmail connector docs specify search operators, full messages, headers and attachments. No inspected output-ID lifetime contract.[^22] | The Bot's installed Gmail path and identifier semantics still need qualification; these pages do not establish identical tools on every Grok surface. |
| Meta Muse | Official product page documents email connectors and a persistent computer, without mail-ID/raw-header schemas.[^23] | Persistent execution state does not establish persistent mail identity. |
| Microsoft Copilot | Product citations and audit resource IDs are distinct from Copilot interaction-message IDs. No reviewed contract establishes Graph ImmutableId opt-in for every path.[^24][^25] | Do not infer ID flavor from an Outlook citation or an audit field called ID. |
| Composio Gmail | Version displayed as `20260903_00`; native Gmail message-ID parameter explicitly excludes RFC and thread IDs; full/raw formats documented.[^11] | Strong input semantics; complete model-visible output and installed version still matter. |
| Pipedream Gmail/MCP | Public component v0.3.1 exposes native `id`/`threadId` plus RFC-derived `message_id`; derived text can be truncated and large results can omit messages.[^12] | Field names and completeness flags must be understood before matching. |
| n8n Gmail | Simplified mode requests selected metadata; unsimplified mode fetches raw MIME then parses it. Draft reads distinguish draft `id` from underlying `messageId`.[^26][^27] | Node resource, mode and version alter available matching evidence. |
| Zapier Gmail | Conversation operations use thread IDs; attachment retrieval uses a message ID.[^28] | High-level action names do not define one stable result schema; inspected material leaves header/raw access uncertain. |
| LangChain Gmail toolkit | Source fetches raw internally but GetMessage returns a projection omitting arbitrary RFC headers; GetThread returns message IDs/snippets.[^30][^31] | Backend access does not imply the agent can observe full identity/content. |
| Public Workspace MCP server | Native and RFC IDs are separate; full content export can use a URL with a one-hour lifetime.[^32] | Export location and message identity are demonstrably different objects. |
| Representative standalone Gmail MCP | Public implementation uses native Gmail requests but returns selected formatted text. The inspected repository is archived.[^33] | MCP compatibility does not imply a uniform message schema or current maintenance. |
| OpenAI Agents SDK / general MCP | Tool implementation and state are application-owned; MCP standardizes invocation/results, not email identity.[^34][^35] | No model or harness can confer a missing provider/connector contract. |

These findings support a concrete conclusion: **there is no verified universal
message identifier exposed consistently across this market**. They do not
support claiming that native Gmail IDs are generally unstable.

## Provider-ID-independent design

### Durable records and replaceable lookup evidence

Create a School-OS source record once, with its own opaque ID, and persist it
on Drive before downstream records refer to it. A UUID is one implementation
option, not a required runtime dependency. Do not derive this ID from a provider
ID, RFC header, subject/date tuple or content hash. A connector replacement can
change every external lookup value while the School-OS record and its existing
facts/tasks retain their names.

The record holds a small collection of evidence, not a raw-message archive:

- Logical source account and its verified connection bindings.
- Available original subject, actual received date/time, sender, To/Cc recipients
  with their roles, and source dates with precision and timezone semantics.
  Sender-created identity/reply headers may help search or find context but
  are not acceptance criteria.
- Optional typed provider aliases and current URLs/handles, including origin,
  resource kind, scope, last verification and whether they are merely locators.
- Optional fingerprints of content actually read, with representation and
  completeness recorded; attachment inventory, context and read coverage.
- A human-readable search recipe and any unresolved identity relationship.

These are alternative and complementary witnesses. They are not a new list of
mandatory metadata whose absence invalidates the whole instance. Existing
knowledge remains usable even when a new observation lacks a field. A partial
observation can have a durable pending-work identity without being promoted to
an exact match or a distinct completed source.

### Source-information matching recipe

Start with the original subject, actual received date/time, sender and To/Cc
mailboxes, and attachment names. Keep mailbox identity and recipient roles
explicit. Compare the same timestamp meaning in a common timezone; preserve
its precision. A minute-only rendering cannot silently become a known exact
second, and a sender’s Date is not the receipt timestamp.

Use that information to narrow candidate messages, then reason over the actual
reply and relevant contents when needed. Include attachment count, names and
content when filenames alone cannot distinguish them. Original filenames and
body details are source evidence; connector-generated download filenames,
display names and temporary paths are presentation/access details.

These fields are generally useful and intrinsic to an observed message, but
are not guaranteed unique or identically exposed by every reader. A forwarded
message has its own outer sender, time and content; imported copies may have a
different receipt time. Missing fields require another supported evidence
recipe or a scoped unresolved result. They must not recreate a universal
mandatory metadata gate. The synthetic matcher below was an initial decision
model, not a requirement that every tool expose every field. The raw-MIME
evaluation now demonstrates that its flat witness and incompatibility handling
need refinement before use.

### Finding the original without its old provider ID

1. Try a previously verified lookup alias when the current route supports it.
   Check returned account/resource and corroborating evidence. A stale or
   conflicting handle triggers another lookup route, not record deletion.
2. If available, search by the RFC Message-ID header. Gmail documents
   `rfc822msgid:`; other adapters must expose an equivalent supported search.[^36]
3. Otherwise search using available sender/recipient, subject, date interval
   and distinctive cataloged information. Treat these as candidate filters,
   not a composite primary key. Expand the exact reply, not just the thread
   summary, and compare the content and surrounding qualifications.
4. Compare candidates against the saved evidence. An agent can reason about
   headers, replies and content; small helpers may compute digests or parse
   MIME when available. Neither a hash tool nor raw MIME access is mandatory
   for every operation. The strength of the accepted association must match
   the evidence actually available.
5. Decide from source information: a corroborated content association, distinct
   source evidence or an unresolved occurrence. Preserve useful new lookup
   details separately; neither a provider ID nor an RFC header decides the result.

Search behavior itself needs qualification. Gmail UI/API differ on aliases
and thread-wide matching; calendar dates in API queries have timezone semantics.
Use bounded searches with recorded scope and pagination. Zero results in a
narrow or incomplete search do not prove deletion, and one returned result
does not prove it is the only possible match.[^37]

### What a match permits

| Outcome | Durable behavior |
|---|---|
| A current tool handle retrieves a candidate | Apply the same source-information matching procedure used when IDs are absent. The handle grants no shortcut to identity or acceptance. |
| IDs missing/changed, compatible complete content and context | Preserve the existing School-OS record as a content candidate/association. Reuse only knowledge supported by that context; physical-occurrence uniqueness is not implied. |
| Distinct source evidence | Create a new School-OS record. An email correction or reminder may still refer to an existing canonical task. |
| Similar snippet or insufficient metadata | Retain pending work and seek a richer read; do not merge or manufacture a new accepted source from a guess. |
| Multiple indistinguishable matches | Preserve candidates and uncertainty. Do not pick the first search result or collapse known separate occurrences. |
| Stale/conflicting external alias | Keep prior knowledge and record ID; isolate the unresolved lookup and continue unrelated work. |

A provider handle alone must not authorize sending, deleting,
labeling or replying to a guessed provider object. When a provider action needs
a native ID, obtain the current ID from a verified selected result at execution
time. Provider APIs may require their own IDs for operations; School-OS can
avoid persisting those as canonical keys without pretending those APIs stop
requiring them.

### Replies, duplicates and attachments

Each reply is a separately observed message. RFC relationship headers help
identify its parent; thread membership and quoted text supply context. Neither
the parent's ID nor an identical quoted block identifies the reply. Compare
the full available reply, preserving inline answers and quoted context. Do not
hash only the newly authored text: many distinct replies contain “Yes” or “OK.”
Task reconciliation follows meaning and household context separately from
source identity, preserving completed tasks and explicit corrections.

Keep separate source-account provenance when two parents receive the same
communication. Equal bytes can justify reuse of extraction work, but they do
not prove that two mailbox occurrences are one object. A forward has an outer
message and possibly an embedded original; an embedded `Message-ID` is not the
outer message's identity.

Attachments also receive School-OS-owned child record IDs. Current download
tokens are replaceable. A verified native part ID or original MIME coordinate,
filename, media type, occurrence position and optional content digest can help
find the part again. Duplicate filenames and duplicate bytes remain possible.
A coordinate derived from a connector's reordered list is not automatically
the original MIME coordinate. An unresolved attachment lookup must not rename
its parent or erase previously extracted facts.

Do not redownload every attachment merely to refresh identity. Collect useful
fingerprints during an already-required processing read when the environment
supports it, then discard working bytes. Later read only what the operation
needs. Unread binary content cannot be declared equal because its name and
size match. Filename, size and a digest are witnesses with different strengths,
not a universal attachment ID.

### Why no single hash fixes the problem

A raw-message hash distinguishes exact wire bytes, including transport headers
and MIME encoding differences. Decoded-content fingerprints can tolerate
specified representation changes, but lose that exact-byte meaning. MIME
defines alternative transfer encodings, and some wrappers further clean or
truncate extracted text.[^38][^30] Fingerprint comparisons must use compatible,
named representations and known coverage. A mismatch between different
representations means “not yet comparable,” not “definitely a new email.”

Do not strip quotes, collapse arbitrary whitespace, discard attachment names,
or reduce a message to a summary for exact identity matching. A fingerprint
of a complete text body is not a fingerprint of unread attachments. Hashes
reduce storage and comparison cost; they do not reveal missing information.

There is a hard limit: if two physical messages expose identical headers,
content, timestamps and every other available observation, no algorithm can
recover which occurrence was intended without another distinguishing signal.
An LLM cannot reason its way to information the source does not expose. The
design must preserve that ambiguity, allowing content-based questions while
withholding unsupported occurrence claims. This is an information limit,
not a reason to stop the entire household workflow.

### Bounded operation and development velocity

Use indexed lookup of the available witnesses, followed by small candidate
reads. Partition/query the index as history grows; do not load the full mailbox
or hash all history on each run. Exact physical Drive layout and lookup cost
remain live qualification work. A small set of aliases and evidence per record
is proportional to cataloged sources; raw attachments do not accumulate.

Persist unresolved work once with a reason, candidate scope and next useful
action. Another routine run should not repeat the same failing lookup
indefinitely without new evidence, access or an intentional broader search.
The item stays visible while unrelated cataloging and questions continue.
This is ordinary incomplete-work handling, not a global fatal identity gate.

Adapters supply search/read and explain what their fields represent. They do
not need to invent a universal mail ID or normalize every possible connector
envelope into one rigid shape. Qualify a small real journey per adapter and
reuse its evidence. A changed locator should not trigger a release rebuild,
fresh instance installation or complete historical requalification. Concurrent
updates to the same Drive data remain outside current scope.

## Initial synthetic experiment and its limits

The later [MIME evaluation](mime-evaluation/README.md) supersedes this small
experiment as the current robustness assessment. It reports failures, not a
qualification pass. The following describes only the original prepared cases.

The executed [38-case experiment](experiment.py) and its
[results](experiment-results.json) exercise the matching decisions independently
of the old School-OS runtime. Cases include changed/missing provider IDs,
absence of both provider and RFC IDs from stored and incoming observations,
namespace collisions, reused citations, reply quotes, differing dates, same-name
attachments, unread content, representation changes, and indistinguishable copies.

A serialized record retained its School-OS-owned ID with no provider or RFC
message ID on either side. This is a JSON round-trip within an analysis process,
not a new vendor session. Every matching call preserved existing records;
an independent subsequent call could succeed after an unresolved case. This
does not test a deployed work queue, live indexed search or scheduler.

Independent review caught an unsafe initial shortcut that promoted an alias
to identity authority. The final design removes that shortcut entirely: native
IDs, RFC identifiers, thread IDs and citations are excluded from the matcher’s
decisions. Every case is also rerun with those fields erased from both incoming
and stored observations; the disposition must remain unchanged. Tests cover
received time separately from sender date, timezone presentation, To/Cc roles
and attachment names. Provider details may help retrieve candidates, but cannot
change an identity result based on the same source information.

The experiment deliberately returns `content-match-occurrence-unverified`
without IDs; it does not pass off content equality as proof of one physical
message. Its complete-content flags and normalized header fields are fixture
assumptions. Fingerprints and attachment descriptions are synthetic, not
measurements of real PDFs. The decision procedure demonstrates one conservative
matching route, not an exhaustive production matcher or semantic-quality test.
The earlier 96-assertion lifecycle simulation remains historical evidence;
it has not been retrofitted and requalified with this new identity boundary.

## Remaining risks and targeted validation

| Risk or unknown | Minimum useful validation / mitigation |
|---|---|
| Built-in agents omit RFC headers or native IDs | Inspect the actual tool schema and a bounded read on each intended app; use another authorized read route or explicit partial support. |
| Connector update changes field meaning or projection | Record mapping/version and verify a known nonprivate test message on change; unknown aliases remain locators. |
| IDs disappear after reconnection | Repeat the same synthetic thread in a fresh session and after an authorized reconnect; require own-record continuity through witness lookup. |
| Full body is actually truncated or reformatted | Test long text, HTML/plain alternatives and MIME parts against the returned coverage; do not upgrade snippets to complete evidence. |
| Identical messages / reused RFC IDs | Include duplicates with both equal and different bodies; preserve separate known occurrences and unresolved ambiguity. |
| Attachment locators rotate or structure differs | Refetch metadata, resolve the parent and original part; test duplicate names, duplicate bytes and missing part IDs without bulk redownloads. |
| Narrow search misses an existing record | Track search scope/completeness and bounded expansion; never accept empty search as global uniqueness. |
| Fallback creates new task duplicates | Test source identity and task meaning separately, including reminders, corrections and parent completion. |
| Index grows over school years | Measure narrow lookup and candidate-read cost on realistic synthetic history before fixing the Drive layout. |

The next compatibility test should use one small synthetic thread deliberately
visible in two actual managed agent apps. Remove or invalidate saved external
IDs in the test index, start a fresh session from Drive, and resolve an original,
a specific reply and one attachment using the remaining evidence. This directly
tests the portability requirement without rebuilding the whole product.

## Sources

All linked sources were inspected for this review. Undated documentation is an
observation of the current page, not a lifetime warranty. Public code links on
main/master are observations of the retrieved implementation, not pinned
production dependencies. The local Gmail schema and private aggregate test are
identified separately above; no public link is invented for them.

[^1]: Google. [Gmail Message and MessagePart resources](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages). Updated May 6, 2026.
[^2]: Google. [Create and send draft emails](https://developers.google.com/workspace/gmail/api/guides/drafts).
[^3]: Google. [Gmail IMAP extensions](https://developers.google.com/workspace/gmail/imap/imap-extensions), X-GM-MSGID and X-GM-THRID.
[^4]: Microsoft. [Obtain immutable identifiers for Outlook resources](https://learn.microsoft.com/en-us/graph/outlook-immutable-id). Updated November 7, 2024.
[^5]: Microsoft. [Graph message resource](https://learn.microsoft.com/en-us/graph/api/resources/message?view=graph-rest-1.0).
[^6]: IETF. [RFC 9051, IMAP4rev2](https://www.rfc-editor.org/rfc/rfc9051.html), section 2.3.1. August 2021.
[^7]: IETF. [RFC 8621, JMAP Mail](https://www.rfc-editor.org/rfc/rfc8621.html), Mailboxes, Threads and Email. August 2019.
[^8]: IETF. [RFC 5322, Internet Message Format](https://www.rfc-editor.org/rfc/rfc5322.html), section 3.6.4. October 2008.
[^9]: IETF. [RFC 7352, Sieve: Detecting Duplicate Deliveries](https://www.rfc-editor.org/rfc/rfc7352.html), sections 3 and 6. September 2014.
[^10]: Google. [Apps Script GmailThread](https://developers.google.com/apps-script/reference/gmail/gmail-thread), getId.
[^11]: Composio. [Gmail toolkit](https://docs.composio.dev/toolkits/gmail), displayed version 20260903_00; expanded Fetch Message and Fetch Emails documentation.
[^12]: Pipedream. [Find Emails implementation](https://raw.githubusercontent.com/PipedreamHQ/pipedream/master/components/gmail/actions/find-email/find-email.mjs), component 0.3.1.
[^13]: OpenAI. [MCP and Connectors](https://developers.openai.com/api/docs/guides/tools-connectors-mcp).
[^14]: OpenAI. [Plugins](https://learn.chatgpt.com/docs/plugins).
[^15]: OpenAI. [ChatGPT Work overview](https://learn.chatgpt.com/docs/enterprise/chatgpt-work-overview).
[^16]: Anthropic. [Use Google Workspace connectors](https://support.claude.com/en/articles/10166901-use-google-workspace-connectors).
[^17]: Anthropic. [Agent SDK custom tools](https://code.claude.com/docs/en/agent-sdk/custom-tools).
[^18]: Anthropic. [Agent SDK MCP](https://code.claude.com/docs/en/agent-sdk/mcp).
[^19]: Google. [Gemini Spark operations](https://support.google.com/gemini/answer/17094507?hl=en).
[^20]: Google. [Gemini Spark updates](https://blog.google/innovation-and-ai/products/gemini-app/gemini-spark-updates-june-2026/). June 30, 2026.
[^21]: Google. [Collaborate with Gemini in Gmail](https://support.google.com/mail/answer/14355636?hl=en) and [Workspace source documentation](https://support.google.com/mail/answer/16813283?hl=en).
[^22]: xAI. [Gmail and Google Calendar connector](https://docs.x.ai/grok/connectors/gmail-google-calendar) and [Grok Bot overview](https://docs.x.ai/grok-bot/overview).
[^23]: Meta. [Muse](https://ai.meta.com/muse/), official product page.
[^24]: Microsoft. [Audit logs for Copilot and AI applications](https://learn.microsoft.com/en-ca/purview/audit-copilot).
[^25]: Microsoft. [Connecting Copilot to other services](https://support.microsoft.com/en-us/microsoft-copilot/connecting-microsoft-copilot-to-other-services).
[^26]: n8n. [Gmail message operations](https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.gmail/message-operations/) and [GmailV2 implementation](https://raw.githubusercontent.com/n8n-io/n8n/master/packages/nodes-base/nodes/Google/Gmail/v2/GmailV2.node.ts).
[^27]: n8n. [Gmail GenericFunctions implementation](https://raw.githubusercontent.com/n8n-io/n8n/master/packages/nodes-base/nodes/Google/Gmail/GenericFunctions.ts).
[^28]: Zapier. [Gmail integration catalog](https://zapier.com/apps/gmail/integrations), Get Conversation and Get Attachment.
[^30]: LangChain. [Gmail GetMessage implementation](https://raw.githubusercontent.com/langchain-ai/langchain-google/main/libs/community/langchain_google_community/gmail/get_message.py).
[^31]: LangChain. [Gmail GetThread implementation](https://raw.githubusercontent.com/langchain-ai/langchain-google/main/libs/community/langchain_google_community/gmail/get_thread.py).
[^32]: Taylor Wilsdon / contributors. [Google Workspace MCP Gmail tools](https://raw.githubusercontent.com/taylorwilsdon/google_workspace_mcp/main/gmail/gmail_tools.py).
[^33]: GongRzhe / contributors. [Gmail MCP implementation](https://raw.githubusercontent.com/GongRzhe/Gmail-MCP-Server/main/src/index.ts) and [repository status](https://github.com/GongRzhe/Gmail-MCP-Server), archived March 3, 2026.
[^34]: OpenAI. [Agents SDK](https://developers.openai.com/api/docs/guides/agents/sdk).
[^35]: Model Context Protocol. [Tools specification](https://modelcontextprotocol.io/specification/2025-06-18/server/tools).
[^36]: Google. [Gmail search operators](https://support.google.com/mail/answer/7190?hl=en), rfc822msgid.
[^37]: Google. [Search and filter messages](https://developers.google.com/workspace/gmail/api/guides/filtering). Updated September 10, 2026.
[^38]: IETF. [RFC 2045, MIME Part One](https://www.rfc-editor.org/rfc/rfc2045.html). November 1996.
