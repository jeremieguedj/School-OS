# Metadata-only live stress-test protocol

This records the bounded, user-authorized, read-only development study of the
connected Gmail account performed on 2026-09-13. Interpretation was corrected on
2026-09-14. The executable model and JSON remain a frozen earlier baseline;
they do not implement all subsequently approved changes. This is not
installation, ingestion into a private School-OS instance, a scheduler run or
an assertion about other vendors' agents.

## Evidence and privacy

The collecting agent preserves complete request/response receipts before
normalization in a gitignored private run directory with directory mode 0700
and file mode 0600. No email address, subject, timestamp, filename, source ID,
source URL, snippet or raw error is published. Public reports contain aggregate
counts and file/code bindings only; the private audit links individual trials
to the exact observations used.

Use search results and individual `metadata` reads. Do not fetch full messages,
raw MIME, threads with body content, or attachment bytes. Some responses
incidentally include snippets; preserve them only as part of the complete
private connector receipt and never inspect or use them for this study.

Keep source metadata and a separate test reference in different files.
Native Gmail IDs support private test construction, observation pairing and
grading, including catalog seeding and repeated/distinct entry labels, for this
snapshot audit only. They are excluded from matcher inputs, saved matching
records and decisions. This tests consistency with Gmail's snapshot entries,
not an independent proof of distinct logical emails, physical deliveries or ID
permanence. Two references can represent one logical email. A difference in
their assigned test records is therefore insufficient to demonstrate a product
false positive or loss of school information. Gmail thread IDs similarly provide
a comparison grouping, not exact parentage truth or an identity discriminator.

## Frozen baseline and subsequent normalization decisions

The frozen development [model](model.py) makes the previously unspecified acceptance
rule explicit: automatic association requires a verified logical mailbox,
original subject, sender address and an exact timezone-known source timestamp.
It uses source sending time; an independently understood receipt timestamp is
an alternate same-meaning route when sending time is unavailable. Sending and
receipt timestamps never substitute for each other.

For this conservative baseline, exact means second precision; minute/day
overlap is candidate evidence and yields an unresolved result. That is a test
policy, not a universal uniqueness property or a claim that second precision is
available everywhere. UTC day degradation is tested; local calendar days that
cross daylight-saving changes are not qualified by the fixed-duration interval
representation in this small model.

Optional To/Cc fields compare complete role-specific addresses. Partial or
incomparable lists must be mapped to unknown; arbitrary truncated recipient
lists are not qualified by tests that merely omit the whole optional field.
Original attachment names compare as multisets only under a recognized original
named-attachment scope with known complete inventory. Generated download names
and unknown scopes cannot distinguish messages. An independent pre-live review
caught an initial overly permissive scope check; the model was corrected before
live outcome evaluation. Live search attachment lists have unverified complete
scope and are analyzed separately, not promoted into mandatory identity evidence.
Repeated filename diagnostics are scoped within each parent email. Multiple
exposed candidates can be generated representations, not necessarily different
logical files. Current logical attachment lookup uses the parent School-OS
record plus original filename; unresolved same-parent candidate groups remain
explicit. Different provider locators, reported sizes or MIME types do not
become canonical identity requirements.

The observed sender/recipient presentation differences were repaired in the
frozen evaluator and checked with fictional metadata. The user has subsequently
approved trimming subject outer whitespace for comparison while retaining the
original metadata. That subject change is not implemented in the frozen model;
its two observed outer-space differences and recorded results remain unchanged.

Search's timestamp remains semantically unassigned unless its meaning is
established. Matching a Date header in a sample does not establish a universal
field contract. Gmail `internal_date` is not automatically relabeled receipt
time. Source Date headers supply the primary live identity route in this study.
All observed values agreed. The 189 search-view abstentions were a strict
baseline policy consequence, not evidence of changed or defective timestamps.
Each message and reply uses its own sending time, never an inherited thread
starter date. Hypothetical precision loss is reported separately from live
observations.

## Original scoring labels and their limits

Frozen result labels are retained so the experiment remains reproducible:

| Label | Meaning within the snapshot-reference test |
|---|---|
| `correct_association` | Selected the record seeded for the same Gmail snapshot entry |
| `wrong_association` | Selected a record seeded for a different Gmail snapshot entry; not independently a logical-email error |
| `correct_distinct` | Treated a held-out snapshot entry as new; not independent proof of a different logical email |
| `false_split` | Proposed a new record for an observation whose snapshot reference already had one |
| `abstention` | Declined to decide under the baseline evidence policy |

Do not convert these labels into product accuracy rates. In particular, the
92-entry/91-record daily replay is a snapshot-cardinality mismatch, not a
confirmed product false positive. All `wrong_association` results on unmodified
live metadata concern one observed pair; their repetitions in several scenarios
are not independent incidents. The 92 injected hidden-occurrence cases stipulate
a different truth label despite identical metadata. They illustrate a
hypothetical information limit, not 92 observed logical-email failures.

## Experiments and denominators

- Recent search pages, bounded older school-subject searches, replies, named
  attachment/inline-image summary lists and repeated targeted subject searches.
  Record all caps and pagination; no whole-mailbox completeness claim.
- First metadata reads define a frozen reference catalog. Replaying those same
  inputs is a self-consistency check, not independent repeat-read evidence.
  Subsequent metadata reads are graded separately.
- Search views of those messages are compared against the header-based catalog
  without silently borrowing fields from the grading reference.
- Hold out each reference record, and compare distinct snapshot-entry pairs, reporting
  same-subject/sender near-neighbours separately from easy unrelated negatives.
- Measure repeated metadata among separately addressable entries and loss of
  discrimination under deliberate minute/day projection. Entry multiplicity
  does not prove different logical emails, and a lack of repeated metadata does
  not establish universal uniqueness.
- Inject missing/rounded/malformed/unknown-zone evidence, optional-field removal,
  ID changes, incomplete candidate lookup and known/hidden collisions. These
  are artificial stresses derived from actual metadata, not newly observed
  connector failures. Report association, wrong association, false split,
  correct distinction and abstention separately for every profile.
- Reverse/shuffle catalog order and serialize/reload the records. Simulate an
  historical/daily boundary within the frozen sample, checking later messages
  in previously seen provider threads. This is not a live scheduled job or a
  proof of live indexing/pagination completeness.
- Compare optional subject/participant grouping with the provider's snapshot
  grouping. Disagreement is not an ingestion failure or a measured false reply
  parentage decision: neither grouping is an independent conversation oracle.

Demonstrate what sequential association does when two reference entries share
the available metadata, without presuming that both require distinct product
records. Preserve unresolved observations and processing coverage where needed;
do not infer different logical emails solely from handles or repeated listing
rows. A genuinely different logical email with identical permitted evidence is
a theoretical limit. Do not add a content or provider-ID fallback to force
agreement with the snapshot oracle.

## Pagination and durable progress in the revised plan

The study observed short pages that still reported another page. Continue
according to explicit pagination state within bounded date windows; do not use
page length as proof of completion. Save completed windows, the unfinished
window and processing progress on Drive. A current page token may accelerate
retrieval, but it is not the only resume state: a new agent can restart the
unfinished window and reconcile the overlap using metadata.

This durable-window procedure is an approved design direction, not implemented
or exercised by the frozen test. The study intentionally capped some searches.

All-candidate comparisons are complete only within the frozen test corpus.
Candidate enumeration for the actual mailbox, sustained capacity, actual Drive
recovery, attachment content processing and other agent environments remain
separate qualification work.
