# Live-email stress test of metadata-only identity

Study date: 2026-09-13. **The design is not yet reliable enough for automatic
deduplication without an explicit collision policy.** Real source metadata
exposed a collision that a sequential importer silently collapsed. Attachment
filenames also frequently identified multiple exposed candidates. The
metadata-only boundary remains intact; this study adds no content or external-ID
fallback and changes no installed runtime.

## What was tested

A collecting sub-agent made **127 read-only Gmail calls**, observing **632
separately addressable entries** across recent, older school-subject, reply and
attachment cohorts. Of those, **92 received individual header reads**, including
**17 independent repeat reads**: 109 header observations and 871 search
observations, 980 observations overall. Cohorts overlap. This is a bounded
convenience sample, not a mailbox census or a population error-rate estimate.

The development matcher uses a verified logical mailbox, original subject,
sender address and second-resolution, timezone-known source Date header for
automatic association. To/Cc and comparable original attachment inventories
can distinguish candidates when available. Search timestamps have unestablished
meaning here; attachment lists have unverified original/complete scope. Neither
is silently promoted into stronger evidence. See the [protocol](PROTOCOL.md).

No bodies, quoted replies, HTML, MIME content structure, images, attachment bytes
or content fingerprints were inspected or used. Some connector receipts
incidentally contain snippets; those remain private and unused. No email,
Drive instance, task or schedule was changed. Complete private receipts were
preserved before normalization with restricted permissions; only aggregates,
fictional checks and reusable evaluation code are published.

Gmail message and thread IDs were used privately for **test construction,
observation pairing and grading**, including selecting known repeat reads and
holding out entries. They never entered matcher evidence or saved matching
records. Outcomes therefore measure consistency with Gmail's snapshot references,
not independently proven physical deliveries, exact reply parentage, or permanent
provider-ID stability.

## Findings from actual email observations

### 1. A real visible metadata collision defeats singleton matching

Two separately addressable Gmail entries had the same decoded subject,
normalized sender, second-resolution source Date header and normalized To.
Cc was unknown for both. Their exposed search filename lists also agreed;
the named-attachment lists were empty. Two independent metadata reads per entry
confirmed stable observed values. We did not inspect whether their contents or
physical delivery histories differed.

With both catalog records present, the matcher correctly abstained. With only
one present, it associated the other entry with that record. The rule “there is
only one existing matching record” therefore does not establish that incoming
mail is already cataloged.

| Experiment using observed header metadata | Result against the snapshot reference |
|---|---|
| Replay 92 first observations against the full catalog | 90 associations; 2 collision abstentions |
| Independently reread 17 observations | 15 associations; 2 collision abstentions |
| Hold out each of 92 entries | 90 correctly distinguished; 2 wrong associations |
| Compare all 4,186 distinct entry pairs | 4,185 distinguished; 1 wrong association |
| Restrict to 23 same-subject/sender pairs | 22 distinguished; 1 wrong association |

All the wrong outcomes above are **the same pair**, exercised in different
directions or setups. They are not independent failure incidents. The two
abstentions in each replay are safer behavior, not successful identifications.

The required correction is to preserve known candidate multiplicity **before**
sequential reuse can erase it. A completed source lookup must account for
separately exposed candidates, rather than check only how many records already
exist in School-OS. Preserve unresolved observations and their processing state;
do not let a match mark unread material processed. Repeated appearances across
pages are also possible, so row count alone is not proof of separate deliveries.
This is a required design refinement, not a fix implemented by this study.

Even that correction cannot detect an additional occurrence that is not
separately exposed and has identical allowed metadata. No arrangement or hash
of the same fields can supply the missing distinction. The remaining choice is
whether to accept some uncertain associations or retain more unresolved work.

### 2. Attachment filenames are candidate selectors, not unique identities

Among the 632 entries, 101 exposed nonempty named-attachment lists, totaling
155 entries. **42 of those 101 messages contained a repeated nonempty filename**:
42 pairs, 84 entries. Each pair had different retrieval locators and reported
MIME types, with equal reported sizes. They were not identical duplicate rows.
This does not establish that they represent different physical files; they could
be different representations. No bytes were fetched to decide.

Inline-image lists were nonempty for 36 messages, totaling 69 entries. Six
messages had blank inline names; one had five entries sharing a nonempty name.
Across 239 comparable repeated search observations, named and inline filename
multisets remained equal. Short-window repeatability did not make names unique.

Parent-message metadata plus filename must return a candidate set. Preserve
duplicate names and unknown inventories; do not choose by list position or make
reported MIME types, sizes or temporary locators new mandatory identity keys.
Unresolved attachment selection must not prevent cataloging the parent email.
This test covers exposed image metadata, not completeness of HTML-image
discovery or the ability to process those images.

### 3. Stable source facts still arrive in incompatible presentations

All 871 search observations exposed sender under `from_`, while the declared
tool schema used `from`. Search formatted names and addresses as a display label
followed by a bare address; metadata headers used RFC-style address syntax.
Naively applying the same address parser to both views disagreed for 90 of 92
paired senders. A small handler for the actually observed flattened presentation
made all 92 agree. Recipient lists used the same presentation difference.
After handling that format and explicit empty address groups, To agreed in
91 pairs and was unknown in one; Cc agreed in 16 and was unknown in 76.

Two subjects also differed: metadata preserved one outer ASCII space on each
side, while search omitted them. Interior text agreed. The evaluator preserves
this difference; it does not silently strip arbitrary subject whitespace or
claim those views are interchangeable.

These are observed reasons for a thin metadata adapter and explicit unknowns.
They are not reasons to introduce another strict dependency on one connector's
entire response envelope. Unexpected formatting should leave an observation
pending without stopping unrelated messages.

### 4. Timestamp precision and meaning limit available routes

Every header Date read was parseable and zoned. In all 223 paired
search/header comparisons, the search timestamp, source Date and provider
internal timestamp agreed. Because the latter two always coincided, this sample
**cannot establish what the search timestamp means**. Nor does it prove actual
sender-clock accuracy or independent receipt time.

Consequently all 189 search observations paired to the header catalog abstained
under the conservative model; individual header reads supplied the stronger
route. This is a deliberate evidence threshold, not 189 observed date changes.
An agent exposing only a date or an undocumented search timestamp is not yet
qualified for automatic reuse by this model.

Projecting the 92 source Dates to a UTC day increased same-subject/sender
collisions from one pair to 17 pairs across six groups. Coarse dates are useful
for search, but cannot replace exact evidence with invented seconds.

## Historical ingestion, daily work and restart replay

The offline stateful simulation ordered the 92 header-read entries by their
observed source Dates, seeded 46 historical records, then processed 46 daily
entries. It saved each accepted new record and reloaded the catalog before a
repeat pass.

- Daily ingestion correctly created 45 records and incorrectly associated one
  entry from the collision pair. The saved catalog contained 91 records.
- After JSON reload, 45 daily observations associated correctly and the same
  collision remained incorrectly associated. Persistence preserved the mistake.
- A separate replay seeded the earliest observed member of each of nine sampled
  multi-message provider threads. It correctly retained **19 later messages**
  individually; one later collision entry was incorrectly associated.

The global historical/daily cut contained no threads spanning its boundary,
which is why the targeted thread replay was necessary. “Earliest observed” is
not proof that a sampled message was the original thread starter.

Individual-message handling works for the ordinary later-message cases sampled.
Optional subject/participant grouping suggested 310 pairs within the same
provider thread and 57 pairs across different provider threads; it missed 39
same-provider-thread pairs. These counts cover all 632 sampled search entries,
not just the nine replayed threads. Neither grouping is
an independent parentage oracle. Threads must remain navigation aids and never
carry a permanent processed flag that suppresses later messages.

This was a local development simulation. It did not run a scheduled job, perform
Drive recovery, or switch between managed agent applications. The evaluator is
not a runtime dependency that a parent must install.

## Injected stresses, repeatability and discovery limits

On each of the 92 header observations, injected missing/unknown-zone/malformed
or rounded time evidence, unknown timestamp meaning, incomplete candidate
lookup and visible two-record collisions all caused abstention in their
respective profiles. Removing optional fields or reordering recipients retained
90 correct associations and the same two collision abstentions. These are
artificial stresses using real metadata, not additional live connector failures.

Deliberately presenting a distinct hidden occurrence with identical metadata to
a singleton catalog produced a wrong association in all 92 constructed cases.
That demonstrates the information limit; it is not 92 additional observed
duplicates. All 38 independent [fictional policy checks](policy-results.json)
passed their stated expectations, separately from two reproduced limitations.

Catalog reversal/shuffling, JSON serialization and irrelevant external-ID changes
did not alter decisions. Fresh-process runs under Python 3.9.6 and 3.12.14,
using different machine timezones and hash seeds, exactly reproduced the saved
evaluation and policy results. See [validation results](validation-results.json).
Determinism is established for those cases; correctness does not follow from it.

Recent pages returned 100, 98, 100 and 90 observations while **every page still
had a next-page marker**. Several other cohorts were capped. A short page must
not be treated as completion. There were no connector errors during this run,
but complete mailbox discovery, indexing delay, partial recipient lists,
local-calendar-day behavior across DST and sustained capacity remain unqualified.

## What should happen before implementation

1. Decide the acceptable treatment of indistinguishable occurrences. The current
   boundary cannot guarantee both perfect deduplication and no missed deliveries.
   First address visible multiplicity so the importer does not create its own
   hidden collisions.
2. Keep the small, evidence-based address/presentation handling; preserve raw
   metadata alongside comparison values. Fetch one richer metadata view when
   useful, then leave unresolved work visible without a retry loop.
3. Qualify attachment candidate selection and per-attachment processing coverage
   without assuming filenames uniquely identify objects or every inline image
   has a name.
4. Qualify the same individual-message discovery, pagination and metadata recipe
   in the actual managed agent apps, then test Drive-backed daily checkpoints
   and a real fresh-session handoff. This one Gmail connection cannot establish
   compatibility with Gemini Spark, Grok Bot, GPT Work, Claude Cowork or Meta Muse.

## Evidence and reproduction

[Collection aggregates](collection-results.json) describe scope and observed
connector behavior. [Evaluation results](results.json) bind the frozen private
observation/reference files and exact model/evaluator code by SHA-256. The
private audit records every trial's source observation and result. Original
collection snapshots and raw receipts are retained privately; no source values
are in these public artifacts.

Run the fictional checks with `python3 check_model.py`. The private evaluation
requires the separately authorized private dataset and runs through
`evaluate.py --private-root <private-run-directory>`. It performs no live calls.
The retired content-assisted and MIME experiments remain unchanged.
