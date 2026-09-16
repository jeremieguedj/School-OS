# Source identity and completed-email reuse

This is the operating contract for logical email and attachment association.
Use it with [data](data.md), [storage](../operations/storage.md) and
[ingestion](../operations/ingestion.md). It implements the approved metadata-only
recipe without requiring the development studies or prior conversations.
These instructions do not claim that a connector has been qualified.

## Keep identity, access and processing separate

A School-OS Email represents one logical email in one logical mailbox. Assign
its owned `email_id` once under the data contract. Knowledge, attachment groups,
tasks and coverage use School-OS references. Reconnection, a different tool
handle or normalized presentation must not rename the record.

The agent's connector uses provider IDs, URLs, thread IDs or temporary tokens to
reach data. Keep useful current values only as `access_aids`. They do not prove
identity, that two entries are distinct, or that content was processed.

Use only allowed source metadata for identity and optional thread association.
Do not inspect or compare bodies, quoted text, HTML, MIME structure, inline
images, attachment bytes, summaries, hashes or content fingerprints for those
purposes. Read content separately to extract school information. There is no
content fallback when metadata is inadequate.

## Prepare observed and comparison metadata

Verify the logical source account from the selected configuration and supported
account evidence, independently of the current connection handle. Do not merge
the two parents' mailboxes. Preserve the original observed values, their meaning
and their inventory scope alongside normalized comparison values.

| Field | Comparison and uncertainty rule |
|---|---|
| Original subject | Decode known raw-header encoding, unfold supported header folds and trim outer whitespace. Preserve case, words, punctuation, meaningful interior spacing and reply/forward prefixes. An explicitly empty subject differs from missing subject. |
| Sender | Obtain the actual address through a supported metadata route. Trim presentation whitespace, lowercase the domain and preserve local-part spelling, dots and plus tags. A display name is not an address. |
| Individual original Date | Require a known timezone and second-or-finer precision for automatic association. Compare equivalent zoned instants; preserve the supplied value, zone, precision and `original_email_date` meaning. |
| Received/arrival time | Keep separately when exposed. It supports arrival-window discovery and may provide comparable supporting evidence; it never replaces original Date. |
| To and Cc | Normalize addresses and compare within their respective roles without regard to ordering. Missing or partial recipients remain unknown. An established empty role is different from an unknown role. |
| Original attachment names/count | Compare only when original-filename provenance and inventory scope are comparable. Preserve repeated names; ignore listing order. Generated download names and incomparable inline/named inventories are not contradictions. |

Use [source_metadata.py](../helpers/source_metadata.py) when applicable:
`normalize_subject` requires a reliably known `raw_header` or `decoded`
representation; `normalize_address_parts` accepts reliably extracted local and
domain parts. Read the [helper limits](../helpers/README.md). Unsupported inputs
need a supported tool route or an unresolved comparison, not lossy conversion.
The helper does not parse Date, infer missing timezone/seconds or choose a match.

If listing time is unclear, obtain an individual message's original Date from
an available richer metadata view. One such read may resolve the view; otherwise
leave the association unresolved rather than starting an automatic retry loop.
Day/minute precision or unknown timezone can narrow candidate lookup but cannot
satisfy the automatic threshold.

## Associate one individual message

1. Establish the logical mailbox, original subject, normalized sender and
   sufficiently precise original Date. Keep unknown optional evidence explicit.
2. Use the mailbox's source index, routing by the original Date's UTC month.
   Read all relevant directory continuations and candidate pages; use supported
   ranges broad enough for the observed date presentation. Verify referenced
   records through the storage procedure. A stale locator, unfinished lookup or
   inaccessible relevant page does not establish absence.
3. Compare the core fields and every comparable supporting field. Require
   supported agreement and no contradictory comparable evidence. Unknown
   optional metadata alone is neither a contradiction nor a reason to create
   another email.
4. Apply the decision table. Save original observations, normalized values and
   the association result under the data contract, retaining existing knowledge.

| Evidence | Decision |
|---|---|
| Exactly one supported logical match; no comparable contradiction | Reuse its `email_id`; apply the content-reuse rule below. |
| Adequate core evidence; complete relevant index lookup; no compatible existing record | Create one owned Email record and its linked `not_ingested` coverage. Preserve comparable differences that distinguish it. |
| Several compatible logical records | Keep pending candidate references and uncertainty; do not choose the first, destructively merge records or delete knowledge. |
| Core evidence insufficient, or relevant lookup incomplete | Preserve the observation in the discoverable pending work/source area with unresolved association. Do not manufacture a new resolved logical email. Continue unrelated work and report the scope blocked by this item. |

An existing catalog duplication needs explicit reconciliation, not silent
cleanup during ingestion. A conflicting source observation does not authorize
overwriting earlier observations to force agreement.

## Reuse verified whole-email ingestion

For a unique supported metadata match, resolve `coverage_ref` and verify the
saved canonical coverage before deciding whether content is needed.

| Saved result and current evidence | Content action |
|---|---|
| `fully_ingested`; no explicit new or contradictory inventory/coverage evidence | Reuse the verified outcome and skip body and attachment content. Update useful source access aids only when needed; unchanged rereads are not newly learned knowledge. |
| `not_ingested`, absent/unverifiable coverage, or explicit new required material | Ingest the whole logical email under the binary completion rule. Do not claim that unread content inherited completion. |
| Explicit evidence challenges a previously complete inventory or required coverage | Preserve prior knowledge and mark the logical email `not_ingested` until the whole email again meets the completion conditions. Explain the evidence that reopened it. |
| Different provider handle or unknown optional metadata alone | Do not reopen a verified fully ingested email for that reason. |

A metadata match alone is insufficient: the skip rule also requires the saved,
verified `fully_ingested` outcome. This policy accepts the residual possibility
of distinct emails sharing all permitted metadata. It does not prove identical
bytes, introduce a per-appearance ledger, or make provider-entry counts a target.

## Replies and attachment groups

Obtain each reply's own subject, sender, original Date and available recipients
and attachment metadata. A connector returning a thread must expose its
individual messages; the starter's identity and processed state do not cover a
reply. Optional subject/participant grouping is navigation only. A changed
subject may leave a reply ungrouped without preventing individual ingestion.

Find attachment groups by parent `email_ref` and original filename when known.
The same filename under another email is another context. Same-parent repeated
names remain a candidate group; handles, MIME labels and list positions do not
prove separate physical originals. `candidate_ref` is local to that group, not
permanent attachment identity. Preserve unknown names and inventory scope.

Account for every exposed required candidate during whole-email processing.
If both candidates are read, uncertainty about whether they represent one
physical original does not itself block full ingestion. If a required candidate
is unread or its processing cannot be established, the email is not ingested.
Use group-qualified provenance when exact physical attribution is unresolved.
Do not inspect HTML or bytes to repair identity; meaningful embedded material
is read for substantive extraction with its own processing evidence.

## Completion boundary

An association decision is not ingestion completion. Follow
[extraction](../operations/extraction.md) for the body and required material,
then verify normal saves under the data contract. A source discovery window and
the emails it exposed have separate completion states. These instructions add
no interrupted-write repair or concurrent-update protocol.
