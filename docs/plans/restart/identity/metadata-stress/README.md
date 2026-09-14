# Live-email stress test of metadata-only identity

Study date: 2026-09-13; interpretation corrected on 2026-09-14. **This test did
not demonstrate that School-OS lost a distinct logical email or school
information.** It found presentation differences, attachment candidate groups
and a pagination requirement. It also exposed a limit in the test's grading
reference: different Gmail entries can represent the same logical email.

The executable model and published JSON remain frozen evidence of the earlier
conservative baseline. They do not implement every subsequent design decision,
including approved subject outer-whitespace normalization. The metadata-only
boundary remains intact; no content or provider-ID fallback is introduced, and
no installed runtime has changed.

## What was tested

A collecting sub-agent made **127 read-only Gmail calls**, observing **632
separately addressable entries** across recent, older school-subject, reply and
attachment cohorts. Of those, **92 received individual header reads**, including
**17 independent repeat reads**: 109 header observations and 871 search
observations, 980 observations overall. Cohorts overlap. This is a bounded
convenience sample, not a mailbox census or a population error-rate estimate.

The frozen development matcher uses a verified logical mailbox, original subject,
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
not independently established logical emails, physical deliveries, exact reply
parentage or permanent provider-ID stability. Requiring one canonical record per
Gmail entry was a test-oracle assumption, not a School-OS product requirement.

The original machine-readable scoring labels are preserved:

- `correct_association` means the selected record belongs to the same Gmail
  snapshot reference used by the test.
- `wrong_association` means it belongs to a different snapshot reference. This
  label alone does not establish a product false positive or lost information.
- `correct_distinct` means an entry held out from the reference catalog was
  treated as new; it does not independently prove a different logical email.
- `false_split` means a new record was proposed for an observation whose
  snapshot reference already had a record. No such outcome appeared here.
- `abstention` means the model declined to decide under its test policy; it is
  neither an identification nor proof of a defective source.

## Findings from actual email observations

### 1. Two Gmail entries shared the available metadata

Two separately addressable Gmail entries had the same decoded subject,
normalized sender, second-resolution source Date header and normalized To.
Cc was unknown for both. Their exposed search filename lists also agreed;
the named-attachment lists were empty. Two independent metadata reads per entry
confirmed stable observed values. We did not inspect whether their contents or
physical delivery histories differed.

With both catalog records present, the matcher abstained. With only one present,
it associated the other entry with that record. If these are two representations
of one logical email, that association may be the intended product behavior.
The experiment did not establish otherwise.

| Experiment using observed header metadata | Result against the snapshot reference |
|---|---|
| Replay 92 first observations against the full catalog | 90 `correct_association`; 2 abstentions |
| Independently reread 17 observations | 15 `correct_association`; 2 abstentions |
| Hold out each of 92 entries | 90 `correct_distinct`; 2 `wrong_association` |
| Compare all 4,186 distinct snapshot-entry pairs | 4,185 `correct_distinct`; 1 `wrong_association` |
| Restrict to 23 same-subject/sender pairs | 22 `correct_distinct`; 1 `wrong_association` |

All `wrong_association` outcomes above concern **the same pair**, exercised in
different directions or setups. They are not independent incidents or confirmed
logical-email errors. The abstentions follow from seeding two records using the
snapshot reference; that does not prove two product records were necessary.

The corrected design target is a logical email, not every provider entry or
listing appearance. Preserve relevant observations and any unresolved candidate
groups, but do not manufacture separate logical emails solely because handles
or list rows differ. Source association and content-processing coverage remain
separate: a match alone does not establish that available material was read.

Two genuinely different logical emails with identical permitted metadata remain
a theoretical limit of a metadata-only recipe. The constructed tests below
illustrate that condition; this observed pair did not prove it occurred. That
limit does not justify declaring the product failed or adding a content or
provider-ID identity fallback.

### 2. Attachment candidates must stay bound to their parent email

Among the 632 entries, 101 exposed nonempty named-attachment lists, totaling
155 entries. **42 of those 101 messages contained a repeated nonempty filename
within that parent email**: 42 pairs, 84 entries. Each pair had different retrieval locators and reported
MIME types, with equal reported sizes. They were not identical duplicate rows.
This does not establish that they represent different physical files; they could
be different representations. No bytes were fetched to decide.

Inline-image lists were nonempty for 36 messages, totaling 69 entries. Six
messages had blank inline names; one had five entries sharing a nonempty name.
Across 239 comparable repeated search observations, named and inline filename
multisets remained equal. Short-window repeatability did not make names unique.

Logical attachment lookup uses the School-OS parent-email record plus the
original filename. The same name on another email is a different parent-scoped
lookup, not a collision. Multiple exposed candidates under one parent/name may
be generated representations of one attachment; these counts do not establish
that different logical documents were confused.

Keep an unresolved same-parent candidate group when the exposed metadata cannot
support the selection needed. Preserve unknown inventories and avoid selecting
by list position or turning reported MIME types, sizes or temporary locators
into mandatory identity keys. The group must not prevent cataloging its parent.
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
side, while search omitted them. Interior text agreed. Treating those outer
spaces as significant was an unnecessarily strict baseline choice. The user
has approved trimming outer subject whitespace for comparison while retaining
the original metadata. That normalization is **not implemented in the frozen
evaluator**, so its two recorded subject differences remain unchanged. The
approval does not imply deleting meaningful internal text or reply prefixes
from message identity.

These are ordinary responsibilities of a thin metadata adapter. The observed
address presentation differences were resolved; they are not outstanding
sender-identity failures. Unfamiliar formatting can remain unknown without
making the whole instance depend on one connector's response envelope.

### 4. No timestamp inconsistency was observed

Every header Date read was parseable and zoned. In all 223 paired
search/header comparisons, the search timestamp, source Date and provider
internal timestamp agreed. Because the latter two always coincided, this sample
**cannot establish what the search timestamp means**. Nor does it prove actual
sender-clock accuracy or independent receipt time.

All 189 search observations paired to the header catalog abstained because the
frozen model required an explicitly understood source timestamp and did not
assign sending or receipt meaning to the search field. Individual header reads
supplied its required route. These are **strict test-policy abstentions, not
189 timestamp defects**. Missing precision or a different timestamp meaning in
another agent remains a qualification question, not an observed problem here.

Artificially projecting the 92 source Dates to a UTC day increased
same-subject/sender collisions from one pair to 17 pairs across six groups.
That injected degradation is hypothetical. Each real message or reply should
use its own available sending time, not the original thread starter's date.

## Historical ingestion, daily work and restart replay

The offline stateful simulation ordered the 92 header-read entries by their
observed source Dates, seeded 46 historical records, then processed 46 daily
entries. It saved each accepted new record and reloaded the catalog before a
repeat pass.

- Daily ingestion created 45 records and associated one entry with the other
  entry of the observed pair. The saved catalog contained 91 records for 92
  Gmail references: a snapshot-cardinality mismatch, not a demonstrated lost
  logical email.
- After JSON reload, 45 daily observations scored `correct_association` and
  the same pair produced one `wrong_association` under the original oracle.
  Persistence reproduced that decision; it did not establish a product error.
- A separate replay seeded the earliest observed member of each of nine sampled
  multi-message provider threads. It created records for **19 later entries**
  individually; one later entry of the same pair received `wrong_association`
  under the snapshot oracle.

The global historical/daily cut contained no threads spanning its boundary,
which is why the targeted thread replay was necessary. “Earliest observed” is
not proof that a sampled message was the original thread starter.

The replay handled messages individually using their own source Dates.
Optional subject/participant grouping suggested 310 pairs within the same
provider thread and 57 pairs across different provider threads; it missed 39
same-provider-thread pairs. These counts cover all 632 sampled search entries,
not just the nine replayed threads. These are grouping disagreements, not
ingestion failures or proof of wrong reply parentage. Neither grouping is an
independent parentage oracle. A reply keeps its own identity and sending time;
threads remain navigation aids and never carry a permanent processed flag that
suppresses later messages.

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

Deliberately assigning a different truth label to a hypothetical hidden
occurrence with identical metadata produced `wrong_association` in all 92
constructed cases. The stipulated distinction comes from the test, not an
observation of different logical emails. These illustrate a theoretical
information limit; they are not 92 observed duplicates or product failures.
All 38 independent [fictional policy checks](policy-results.json)
passed their stated expectations, separately from two reproduced limitations.

Catalog reversal/shuffling, JSON serialization and irrelevant external-ID changes
did not alter decisions. Fresh-process runs under Python 3.9.6 and 3.12.14,
using different machine timezones and hash seeds, exactly reproduced the saved
evaluation and policy results. See [validation results](validation-results.json).
Determinism is established for those cases; correctness does not follow from it.

Recent pages returned 100, 98, 100 and 90 observations while **every page still
had a next-page marker**. Several other cohorts were capped. This is a concrete
operational lesson: continue pagination when the source reports another page;
a short page is not completion.

The revised procedure uses bounded date windows and saves completed windows,
the unfinished window and processing progress on Drive. A temporary page token
can accelerate the current run, but it is not the only durable resume state.
A fresh agent can restart the unfinished window and reconcile overlapping
observations using the metadata recipe. This procedure is a design update, not
implemented or verified by the frozen evaluator. There were no connector errors
during the study. Complete mailbox discovery, indexing delay, partial recipient
lists, local-calendar-day behavior across DST and sustained capacity remain
unqualified.

## What should happen before implementation

1. Evaluate logical-email behavior without treating provider-entry cardinality
   as product truth. Preserve unresolved evidence, but do not require another
   canonical email solely because another provider handle exists.
2. Apply the approved address and subject presentation normalization, retaining
   original metadata for provenance. Keep richer metadata reads bounded and
   unfinished work visible without retry loops.
3. Qualify parent-scoped attachment lookup and processing coverage, including
   generated representations and unnamed inline candidates.
4. Implement durable completed/unfinished date-window progress, then qualify
   pagination, Drive checkpoints and a fresh-session handoff in actual managed
   agent apps. This one Gmail connection cannot establish compatibility with
   Gemini Spark, Grok Bot, GPT Work, Claude Cowork or Meta Muse.

## Evidence and reproduction

[Collection aggregates](collection-results.json) describe scope and observed
connector behavior. [Evaluation results](results.json) bind the frozen private
observation/reference files and exact model/evaluator code by SHA-256. The
private audit records every trial's source observation and result. Original
collection snapshots and raw receipts are retained privately; no source values
are in these public artifacts.

Reproduction reruns the **earlier frozen baseline**, not the complete revised
plan. Run the fictional checks with `python3 check_model.py`. The private evaluation
requires the separately authorized private dataset and runs through
`evaluate.py --private-root <private-run-directory>`. It performs no live calls.
The retired content-assisted and MIME experiments remain unchanged.
