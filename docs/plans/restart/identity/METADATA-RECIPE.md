# Metadata-only logical email identity and resumable ingestion

Status: current user-approved plan, updated 2026-09-14. This supersedes the
content-assisted proposal and the strict provider-entry interpretation of the
[live metadata study](metadata-stress/README.md). The frozen study does not
implement every rule below. Production implementation and managed-agent
qualification remain pending; follow the [restart plan](../PLAN.md).

## Boundary and durable records

School-OS assigns its own email record ID once and saves it on Drive. Knowledge,
tasks, attachment records and processing state refer to that ID. Comparison
metadata and current retrieval locators remain separate. A normalization repair
or a replacement connector must not rename an existing logical email.

The record represents a logical email, not one provider entry, search appearance
or physical delivery. A repeated scan or duplicate representation can reuse the
same record. Different provider handles alone do not prove different logical
emails and must not force duplicate records or block ingestion.

Identity and thread association use source metadata only. They do not inspect
bodies, quoted text, HTML, MIME content structure, embedded images, attachment
bytes, summaries or content fingerprints. There is no content-inspection or
provider-ID fallback to resolve identity. Provider/RFC IDs, thread IDs and
citations may help obtain a current result but cannot decide its identity.

Content is read separately to extract substantive school information. A metadata
association does not prove content equality or that all relevant material has
been processed. Save processing coverage independently of catalog presence.
Raw material stays in its source system; discard temporary processing downloads
after verifying persistence of knowledge, source references and processing state.

## Source evidence and normalization

Keep observed metadata alongside normalized comparison values. Apply these
small, explicit rules before matching; agent reasoning can select the appropriate
supported metadata view without inventing missing evidence.

| Source field | Comparison rule |
|---|---|
| Logical mailbox | Verify the source account independently of the current connection; retain provenance separately for different parents' mailboxes |
| Original subject | Decode header text encoding, unfold wrapped headers and trim outer whitespace; preserve words, punctuation, case, meaningful interior spacing and reply/forward prefixes |
| Sender address | Extract the actual address from supported display-name, bracketed or flattened forms; trim surrounding whitespace and lowercase the domain; preserve local-part spelling, dots and plus tags |
| Original email Date | Primary source timestamp for identity; retain its meaning, timezone and precision, and compare equivalent known timezones as the same instant |
| Received time | Keep separately as optional supporting information; never silently substitute it for the original Date or an observation time |
| To and Cc | Normalize actual addresses and compare without regard to ordering, preserving their respective roles; missing or partial lists remain unknown |
| Original attachment names/count | Supporting evidence only when original-name provenance and inventory scope are comparable; retain repeated names and ignore listing order |

For example, these fictional presentations compare equally:

| Observation A | Observation B | Comparison value |
|---|---|---|
| `Example School office@EXAMPLE.ORG` | `Example School <office@example.org>` | `office@example.org` |
| ` School update ` | `School update` | `School update` |

An explicit empty recipient field or valid empty address group differs from a
missing field. A missing attachment inventory does not mean zero attachments.
Generated download names and incomparable mixtures of inline and named
attachments cannot distinguish messages. Do not parse HTML or download bytes to
repair inventory for identity purposes.

If search exposes an unclear timestamp, obtain the individual message's original
Date through a supported metadata route. All compared live timestamps agreed;
the earlier abstentions were a strict study policy, not observed date changes.
If the required Date, timezone or precision remains unavailable, retain a scoped
pending association and continue unrelated work. Do not fill unknown seconds or
timezone from the agent's machine. Coarse dates can narrow a search; overlap is
not proof that two exact instants are equal.

These rules follow the distinction between the sender-provided origination Date
and transport time in the [message format standard](https://www.rfc-editor.org/rfc/rfc5322),
and address-case treatment in the [SMTP standard](https://www.rfc-editor.org/rfc/rfc5321).
Gmail also documents its internal timestamp separately from the Date header in
its [message resource](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages).
These sources inform the adapter; their provider-specific fields are not
canonical prerequisites.

## Matching procedure

1. Normalize the available source metadata and search the same mailbox's index
   using subject, sender and original Date. Search broadly enough to accommodate
   the reported precision and presentation. Compare To/Cc and comparable original
   attachment information when available.
2. Require sufficiently supported agreement in the core metadata and no
   contradictory comparable evidence. A subject-only hit or a rounded date alone
   is insufficient. One richer metadata read can resolve an incomplete view;
   otherwise keep that association pending without an automatic retry loop.
3. Reuse an existing logical email record when this recipe agrees. Repeated
   appearances or different source handles with agreeing metadata do not, by
   themselves, create additional logical emails. Keep useful observed references
   and processing coverage without turning provider-entry counts into product
   identity requirements.
4. Create a new School-OS record when adequate metadata and a completed relevant
   index lookup establish no existing association. Comparable differences can
   distinguish messages. Unfamiliar formatting, an incomplete lookup or unknown
   optional fields alone must not manufacture a new email.
5. If an observation remains compatible with several distinct logical records,
   preserve the uncertainty rather than choosing the first. Existing duplicate
   catalog records also require explicit reconciliation; this plan does not
   authorize silently deleting or merging their knowledge. Continue other work.

This is a practical metadata-association policy. It accepts the residual
possibility of genuinely different emails sharing every permitted field; it
does not claim proof of unique physical delivery or equal content. The live
study's two separately exposed entries may represent one logical email. Its
92-entry/91-record result did not establish loss of distinct school information
and is not a reason to require a record per provider entry.

## Replies and optional conversation grouping

Every individual reply uses its own subject, sender, original Date, recipients
and attachment metadata. It never inherits the thread starter's identity, Date,
attachments or processed flag. Repeated newsletters on different dates remain
separate logical emails even if subject and participants are unchanged.

For example, an original sent Monday at 09:00, a reply at 11:20, and a later reply
Tuesday at 08:15 each have their own records and coverage. If a source returns a
thread, obtain individual-message metadata, including replies in previously seen
threads. A thread summary alone cannot establish complete message coverage.

Subject/participant grouping is optional, reversible navigation. It may remove
recognized reply prefixes for lookup while preserving the identity subject.
It does not decide email deduplication, processing completion or exact parentage.
Different grouping from Gmail is not an ingestion failure. A changed-subject
reply may remain ungrouped without making its individual message unusable.

## Attachment lookup and coverage

Every attachment record belongs to its logical parent email. The ordinary lookup
is **parent School-OS email ID + original filename**. The same name under another
email is a different attachment context. Original filenames are not globally
unique attachment identities.

Repeated names within one email identify a candidate group. Its members may be
separate originals or alternate representations of one file; different retrieval
handles or reported MIME types alone do not settle that distinction. Keep all
relevant candidates under the parent and account for their processing coverage.
Do not select the first entry or invent permanent identity from list order.
Exact individual attachment association may remain unresolved without blocking
the parent email. An unidentified or unread candidate must not inherit another
candidate's completion status merely because its filename agrees.

Missing inline-image names leave name-based lookup incomplete. Discovering and
reading meaningful images is content processing, with explicit coverage; it is
not an identity fallback. No attachment-byte or HTML comparison is introduced.

## Bounded enumeration and fresh-session recovery

Search manageable date windows within the configured mailbox/school scope.
Follow the tool's available continuation mechanism even after a short page.
Gmail's [listing contract](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/list)
provides continuation separately from result count; other adapters must establish
their own usable listing route.

Save the mailbox, search scope, date-boundary meaning/precision, completed windows
and unfinished window on Drive. Save accepted source records and processing
coverage as work proceeds. Mark enumeration complete only when the available
route establishes exhaustion. Completion of discovery is separate from completion
of content extraction and individual attachment coverage.

A pagination token is optional working state inside the adapter. If it is lost
or expires, repeat the unfinished window and recognize already cataloged emails
through their metadata. For example: September 1-3 complete, September 4
unfinished; the next agent starts with September 4 using the Drive record. No
saved token, prior conversation or local process is necessary to describe the work.

Daily scans can repeat a bounded overlap and resume missed windows. A maximum
source Date alone is not proof that discovery has caught up; late-arriving or
newly indexed material and the search route's time semantics need qualification.
If a tool silently caps results, narrowing windows can reduce work but cannot
prove completeness. Use an available complete listing route or leave the affected
window's coverage explicit. Stop at the run's budget and persist remaining work.

## Validation status

The [live metadata study](metadata-stress/README.md) observed 632 Gmail entries,
including individual header reads for 92 and 17 independent repeats. Its source
observations remain valid. Its `wrong_association` scores use distinct Gmail
entries as the test reference, which is stronger than logical-email identity;
those scores are not demonstrated product false positives. No distinct school
information loss was established.

The frozen model already handles the observed address presentations. It does not
implement this revision's subject trimming, logical-email acceptance rules,
parent-group processing or durable window recovery. Original code and results
remain unchanged to preserve reproducibility. Older provider-ID and content/MIME
experiments are historical and do not qualify these rules.

Next: implement the approved decision policy in a small development model and
prepare meaningful tests without executing them. Any new or changed architecture
decision requires explicit user approval, grounded in the product principles.
This identity work is one component of the whole-project implementation.
Publish the agreed project code and stop for the user to direct testing,
as required by the [restart plan](../PLAN.md#decision-authority-and-user-checkpoints).
A bounded slice in managed agent apps, Drive checkpoints, daily scheduling and
a second agent's handoff remain proposed user-directed qualification work.
No installed runtime, private-instance migration or live scheduled run is claimed.
