# Metadata-only email identity and thread handling

Status: current user-directed design. This supersedes the content-assisted
identity proposal in [the research report](REPORT.md) and its MIME-based repair
recommendations. It is not yet an implemented or validated replacement matcher.

## Boundary

Email identity and thread association use source metadata only. They must not
read or compare bodies, quoted text, HTML, MIME content structure, embedded
images, attachment bytes, summaries, semantic content or content fingerprints.
There is no content-inspection fallback when metadata is ambiguous.

Agents still read content to extract school information, tasks and deadlines.
That processing has its own coverage and completion state. A content extraction
failure cannot change the email's record ID or prevent metadata cataloging of
other messages. Matching metadata does not prove content equality or completed
extraction. Raw material remains in its source system, with temporary processing
downloads discarded after verified persistence of the resulting records.

## Record and evidence

Assign a School-OS source ID once and persist it on Drive. It is an internal
record name, not a provider ID or a hash of a supposedly unique metadata tuple.
Keep the following separately as lookup and matching evidence:

| Source metadata | Comparison rule |
|---|---|
| Mailbox/account | The same logical mailbox, independent of the current connector binding; preserve separate provenance for different parents' accounts |
| Original subject | Preserve the actual subject, including reply/forward prefixes; remove only known display/header-encoding artifacts, not meaningful text |
| Sender address | Compare the actual address, not its display name; no provider-specific removal of dots, aliases or plus tags |
| Sending date/time | Preferred message timestamp; retain its meaning, timezone and precision |
| Received date/time | Additional evidence or an alternative timestamp route when both sides expose receipt time; never substitute it for sending time |
| To and Cc | Compare addresses within their respective roles; presentation order does not matter |
| Original attachment filenames and count | Supporting evidence when the original names and comparable inventory scope are exposed; preserve repeated names, ignore listing order |

Convert timestamps to a common timezone only when their timezone is known.
Never use the agent machine's timezone to fill a gap. Rounded timestamps denote
intervals, not fabricated exact seconds. An overlapping interval narrows the
search but is not exact agreement or permission to merge records transitively.

Missing fields are unknown, not empty. In particular, an unavailable attachment
inventory is not an email with zero attachments. A connector-generated download
name, temporary filename, or an incomparable mixture of inline images and named
attachments supplies no identity discriminator. Do not parse HTML or download
attachments to repair that inventory for identity purposes. The email can be
matched using its other metadata; attachment lookup can remain unresolved.

Provider message IDs, thread IDs, RFC identity/reply IDs and citations may help
an adapter locate a result. They do not decide identity, prove thread membership,
or resolve a collision. No operation requires a saved external ID to remain valid.

## Matching recipe

1. Search the source index within the same mailbox. The ordinary route uses
   original subject, sender and the message's sending timestamp; compare To/Cc,
   receipt time and comparable original attachment names when available. If the
   sending timestamp is unavailable, compare receipt time with receipt time.
   Search broadly enough for the reported precision and presentation differences.
2. Compare metadata with the candidate records. Use explicit same-field agreement
   and differences, not a similarity score or content-based tiebreaker. A known
   original filename difference can distinguish otherwise matching messages;
   an unknown or incompatible listing cannot. A single subject-only or otherwise
   weak partial hit is insufficient. Missing anchors or partially overlapping
   times call for a richer metadata view, or a pending item if none is available.
3. One sufficiently supported compatible candidate in the completed relevant
   lookup permits reuse of its School-OS record as a **metadata association**.
   This means one match among the candidates inspected, not a proof of unique
   physical delivery or identical content. Preserve the observed evidence and
   lookup scope, rather than claiming stronger certainty.
4. If comparable metadata establishes a distinct message, or the completed
   relevant lookup finds no existing match with adequate metadata available,
   assign a new School-OS record. An incomplete search, an uncertain date or
   unfamiliar formatting alone must not manufacture a distinct source.
5. Multiple compatible candidates, known metadata collisions or inadequate
   observations remain explicitly unresolved. Preserve existing records and any
   known distinct occurrences. Never select the first result or use current
   list position as a persistent discriminator. Save the reason and next useful
   metadata read once; continue unrelated work without an automatic retry loop.

Two emails can share every metadata field above, even while carrying different
contents. Visible collisions remain unresolved. If an additional occurrence is
not separately exposed and all its metadata matches a single known record,
this recipe cannot detect that hidden collision. Automatic metadata association
therefore carries a residual false-match risk. It cannot promise zero false
positives/negatives or lossless detection of every distinct delivery. This is
the explicit limit of the chosen boundary, not a reason to reintroduce content
inspection or provider-ID authority.

## Threads and replies

The unit of identity, processing coverage and daily discovery is the individual
message. Every reply is evaluated using its own subject, sender, timestamps,
recipients and attachment metadata. It does not inherit the original email's
ID, attachments or processed status. A forwarded email is another outer message;
its embedded original is not extracted to establish identity.

On a daily scan, enumerate individual message metadata in every relevant result.
If the source returns a thread, expand its individual messages, including when
the thread was seen before. Never skip it because it was once marked processed,
and never use the thread's original date as coverage for later replies. Recheck
the prior discovery boundary at its known precision and keep incomplete
pagination or indexing coverage explicit; the largest sender timestamp is not
proof that discovery is complete. The exact supported search route still needs
qualification in each app.

Threads are optional, reversible groupings for navigation. A separate lookup
subject may remove recognized reply prefixes such as `Re:`; forwards retain
their forwarded status. Combine the subject stem with overlapping participants
to propose related correspondence, then display its individual messages by
their observed times. Label this grouping **inferred** and preserve any timestamp
ties or unknown ordering. Do not merge existing groups merely because a partial
observation or recurring subject connects them.

A shared subject alone does not prove a conversation. Repeated newsletters can
share a subject and participants; a genuine reply can change its subject.
Without reply IDs or content, exact parent-child reply relationships and
changed-subject continuity may remain unknown. Keep messages independently
usable, permit grouping to be corrected, and never use group membership to
decide message identity, deduplication or completion. A provider changing its
thread grouping cannot rename School-OS message records.

If an agent can expose only a thread summary, and no individual message metadata,
mark that thread's message catalog coverage incomplete. Use another supported
metadata route when available; otherwise retain pending work. Do not represent
the summary as one fully cataloged email.

For example, these fictional messages retain separate IDs even when shown in
one inferred conversation (all times on the same day in the same known zone):

| School-OS ID | Subject | Sender | Sent time | Named attachments |
|---|---|---|---|---|
| source-a | Museum visit | School | 09:00 | permission.pdf |
| source-b | Re: Museum visit | Parent | 09:14 | None observed in a complete named-attachment listing |
| source-c | Re: Museum visit | School | 09:18 | revised-permission.pdf |

A later scan reuses the metadata associations for source-a and source-b, and
catalogs source-c independently if it is new to the instance. This example is
a design walkthrough, not an executed simulation or claim that the provider
exposes all those fields uniformly.

## Attachments and content processing

Attachments have their own School-OS child records under the associated email.
Locate a named attachment using the parent metadata and its original filename,
with count/multiplicity when available. Duplicate filenames cannot be resolved
by inventing a stable list ordinal or comparing bytes; preserve the ambiguity.
Missing inline-image metadata does not block email identity. Discovering and
interpreting inline images belongs to content processing, with its own coverage.

Known separate messages and attachments remain separate even if their metadata
matches. A metadata association does not authorize collapsing their facts or
claiming an unread binary equals one processed previously. Source identity and
semantic reconciliation of school information are separate responsibilities.

## Validation status and next work

The previous 38-case matcher and 54-observation MIME evaluation are historical
evidence for the removed content-assisted route. Their success/failure totals
do not measure this recipe. No runtime or private instance was changed by this
design update. No new end-to-end simulation is claimed.

Next: implement a small metadata-only decision model with explicit acceptance
rules for sufficient evidence, and evaluate missing/rounded timestamps,
colliding headers, attachment-list differences, individual replies, recurring
subjects and fresh-session continuity. Then qualify message-level metadata
access and daily discovery in actual managed agent apps. Keep any unresolved
collision visible and report it separately from a wrong association.
