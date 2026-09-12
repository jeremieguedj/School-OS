# Raw-MIME identity evaluation

**Historical evaluation:** the user subsequently chose
[metadata-only identity](../METADATA-RECIPE.md), removing content inspection from
matching. The MIME/content repair proposals below are superseded as an identity
plan. These results remain evidence about the old pipeline; they do not measure
the new recipe. Content extraction and its coverage still need separate validation.

The existing email matching recipe **does not pass this evaluation**. The earlier
38 prepared-input cases did not establish MIME handling, false-match/split
behavior or environment-independent normalization. This larger experiment finds
incorrect associations, false splits, and an environment-dependent timestamp
decision. It does not repair or qualify a production implementation.

## What was executed

A separate agent authored [54 fictional observations](corpus/manifest.json),
including actual MIME messages and generated PDF/PNG bytes, without reading the
matcher. Delivery labels describe the fictional source history independently
of what the algorithm returns. The generator binds each file to a SHA-256 digest;
the evaluator verifies those bindings before parsing. Coverage requests included
adversarial cases suggested during review, so this is an independently labeled
diagnostic corpus, not a blind benchmark or random mailbox sample.

[adapter.py](adapter.py) decodes those files into the existing
[experiment.py](../experiment.py) witness format. It normalizes decoded header
encodings, address display names, transfer encodings, supported charsets, zoned
sender dates and CRLF/LF. It retains all outer text alternatives, attachment
names, media types, decoded content digests and multiplicity. Nested email is
treated as an attachment, not another outer message. No provider, RFC Message-ID,
thread ID or citation supplies identity evidence.

The adapter deliberately exposes the existing **flat** body/attachment boundary.
Its coverage report also records MIME topology and common HTML references, but
the old matching witness does not use that structure. This tests the proposed
decision procedure plus an explicit observation boundary, not an actual Gmail
or vendor connector. It does not imply that every possible adapter must flatten
MIME or that every agent has raw MIME access.

Every unordered pair is tested in both retrieval directions: 1,431 pairs and
2,862 comparisons. An independently selected diagnostic subset contains 49
pairs, or 98 comparisons. Counts in opposite directions are correlated; they
are not independent trials. The evaluator receives truth for grading; the
observation adapter and resolver do not receive delivery or communication labels.

## Results

The full [results](results.json) and [pair audit](pair-results.json) preserve the
measurements. This table reports comparisons, not distinct emails:

| Independently known relationship | Correct association or distinction | Incorrect decision | Unresolved |
|---|---:|---:|---:|
| Same delivery, possibly different presentation: 292 | 62 content associations | 73 false splits | 157 |
| Distinct deliveries with distinguishable full source evidence: 2,566 | 2,172 distinctions | 2 incorrect content associations | 392 |
| Different deliveries with identical available evidence: 4 | 4 content associations, occurrence unverified | No occurrence claim was made | Physical occurrence remains unresolved in all 4 |

The two incorrect associations are the two directions of **one pair**. The 73
false splits occur across 41 pairs. Some limited incoming views abstain while
the reverse direction incorrectly declares a new observation. A false split
means the recipe asserts a distinct source for two views of one delivery; it
does not mean an uncertain view had to be accepted as an exact match.

Automatic association recall is **62/292 (21.2%)** for the deliberately difficult
same-delivery comparisons. Counting abstentions as successful identity matches
would conceal 157 unresolved positive lookups. The 49 targeted pairs produce,
in both directions: 20 correct associations, 44 correct distinctions, 14 false
splits, 2 incorrect associations, 16 abstentions and 2 indistinguishable-delivery
content associations. There is no headline accuracy score: easy unrelated
negatives dominate the all-pairs corpus, and these are not real-world rates.

### Concrete successes and failures

| Case | Observed result |
|---|---|
| Equivalent quoted-printable/base64, supported charsets, encoded/folded subjects, address display names, CRLF/LF, equivalent timezone | Correct association in the selected cases after MIME/header decoding |
| A reply, another reply with the same subject/sender/times but different text, quoted reply, forward, quote-only delivery | Distinguished from the other tested messages; quoted history was retained |
| Same attachment name but different decoded PDF bytes; two different payloads sharing a name; one versus two identical attachments; removed attachment | Correct distinctions |
| Different MIME boundary and base64 wrapping for the same PDF bytes; rewrapped image-only message | Correct associations |
| HTML-only or multipart alternative presentation versus plain text | False splits; these observations need a compatible comparison or an unresolved result |
| Connector reserialization changes attachment listing order | False split; raw MIME order and presentation order need separate treatment |
| CID token renamed with both link and image part updated; CID image converted into a data URI | False splits despite the stipulated same source and exact same image bytes |
| Inline image bytes changed, image placement changed, image-only payload changed | Correct distinctions |
| Nested email changed versus its original; nested email versus outer original | Correct distinctions |
| Nested email repackaged | False split; this fixture also changes a terminal line break, so it is not an isolated transfer-encoding test |
| Receipt displayed at minute precision | False split because the old witness treats a rounded value as an exact instant |
| Missing receipt/sender date, partial envelope, snippet, unread attachment projection, unsupported charset | Unresolved selected positive cases; missing evidence is not proof of absence |
| Same MIME child bytes/order but a different selected HTML root | **Incorrect content association** because the flat witness omits which body is selected |

The final row is material: one message selects an HTML body saying Monday, the
other selects Tuesday. Hashing the same flat collection of child content loses
that difference. A related MIME message specifies its root using `start`, or the
first part when `start` is absent. This is source structure to interpret during
the read, not a provider identifier to persist as the canonical key.
[RFC 2387 §3](https://www.rfc-editor.org/rfc/rfc2387.html)

Sorting all attachments is not a general repair: original mixed/alternative
MIME order can matter. Normalize an arbitrary connector listing only when that
listing is known to be presentation order. Preserve source structure and the
association between a body reference and its particular part.
[RFC 2046 §5.1](https://www.rfc-editor.org/rfc/rfc2046.html)

## Determinism and state replay

- Repeated evaluation in three fresh processes with different hash seeds and
  UTC/Los Angeles timezones produced identical reports for the zoned corpus.
- JSON serialization/reload preserved every tested catalog decision. All 2,862
  comparisons remained unchanged after contradictory external identity hints
  were supplied. Existing catalog records were never mutated by resolution.
- Reversing a fixed catalog changed the serialized candidate ordering for ten
  incoming observations. The candidate sets and decision statuses were equal;
  this is an output-order issue, not a changed identity result.
- Forward, reverse and shuffled ingestion produced the same content groupings
  and seven pending observations after one replay. Each produced 35 accepted
  content records. This is **not** successful deduplication: the independently
  authored history has 30 physical deliveries and 28 communications, and the
  groupings retain the measured false splits and wrong association. Equal wrong
  results remain wrong. Own record names may differ with allocation order;
  they are persisted names, not a globally reproducible content hash.

[boundary_checks.py](boundary_checks.py) separately exercised five assumptions
outside the original prepared-input contract; its [results](boundary-results.json)
show:

1. An unnormalized display-name address causes a false split. The new MIME
   adapter handles this particular representation; arbitrary connectors remain
   unqualified.
2. A minute-rounded receipt represented as an exact second causes a false split.
3. The **same timezone-less timestamp matches in UTC but becomes a new
   observation in Los Angeles**. The old parser inherits the process timezone.
4. An unparseable timestamp raises `ValueError` instead of returning a scoped
   unresolved result.
5. Equivalent catalog candidates appear in input order, so serialized output
   changes when that order changes.

An additional mathematical demonstration shows why time-interval overlap must
not become an identity relation: one minute-wide observation can overlap two
different precise deliveries that do not overlap each other. This illustrates
a risk in a proposed repair; it does not claim that the current matcher performs
that merge.

## Images, attachments and completeness

The simulation actually decodes PDF/PNG attachment bytes and data-URI bytes;
the comparisons use their digests, not invented digest literals. It inventories
the tested CID references and reports the deliberately absent CID target as
missing. Both remote-image references remain unread; no network download occurs.
Image-only email has a binary payload even when the text-body count is zero.

**Matching the email and finishing its substantive processing are separate
decisions.** Identifying an email by its observed HTML does not mean a remote
poster was downloaded, a PDF's instructions were extracted, or an image's
deadline was understood. The coverage sidecar exposes the missing CID and remote
resources; the old matcher's two completeness booleans alone cannot establish
that processing is complete.

No PDF text extraction, OCR, browser rendering or agent interpretation was
graded here. The PNGs are tiny color fixtures, not representative school posters.
The common-reference inspector is diagnostic. Scoped duplicate CIDs, nested
inline resources, CSS, SVG and `srcset` are not covered by these fixtures; no
support is claimed because a parser contains a limitation flag. Duplicate CIDs
can occur in alternative contexts, so globally assuming one unique CID per
message would be another fragile shortcut.
[RFC 2392 §2](https://www.rfc-editor.org/rfc/rfc2392.html)

## Required recipe changes before acceptance

The findings strengthen the provider-independent principle; they do not justify
replacing the provider ID with another brittle universal tuple or hash.

1. **Keep the School-OS record ID separate from matching.** Assign and persist
   it once. Subject, addresses, receipt intervals, attachment names and optional
   fingerprints narrow and corroborate candidates; they do not generate a
   universally unique email ID.
2. **Compare explicitly compatible observations.** Decoding a specified transfer
   encoding is different from deciding that arbitrary HTML, a rendered view and
   plain text contain the same information. Preserve timestamp meaning, timezone
   and precision. Unknown or malformed values remain unknown. A fingerprint or
   presentation mismatch alone must not force creation of a distinct source.
3. **Preserve the content relationships that matter.** Keep each reply separate;
   inspect its content and relevant quoted context. Distinguish the outer email,
   attached email, attachment occurrences and embedded resources. Interpret MIME
   roots/order and HTML references when that source representation is available.
   A CID can be used temporarily to understand a document without becoming its
   durable identity. Missing structural information requires another view or
   an explicit uncertainty, not a mandatory-MIME failure for the whole instance.
4. **Allow a bounded unresolved result.** Save candidate scope, reason and next
   useful read. Continue unrelated work. Do not silently merge, repeatedly create
   new accepted records, or rerun the same failing lookup without new evidence.
   Never join records transitively through partial evidence.
5. **Track processing coverage separately.** Known source, bytes read, attachment
   interpretation, linked-resource availability and facts saved are distinct
   states. Never close ingestion because an identity comparison succeeded.

These are acceptance requirements and proposed refinements, **not implemented
repairs**. The executable old matcher is preserved so its failures remain
reproducible. This analysis does not add a required Python/MIME stack to the
parent's system, an archive on Drive, or concurrent-write coordination.

Even a correct implementation cannot promise always-resolved physical identity
when different deliveries expose exactly the same information. The safe result
is a content association with occurrence uncertainty, even if only one matching
record has been cataloged so far. The practical quality target is explicit error
and unresolved-case measurement, not a claim of zero errors across unknown apps.

## Remaining qualification

The next bounded development step is to refine the evidence/decision contract
against this frozen corpus, then rerun it without changing gold labels to suit
the repair. A separate untouched challenge corpus should check generalization.
Do not claim the prior lifecycle simulation is requalified by this pair test.

After that, run the same synthetic thread, reply, PDF and HTML-image journey in
two actual managed agent apps, including saved-state recovery in a fresh session
with external IDs removed. Measure enumeration/pagination completeness,
individual-reply access, representation fidelity, attachment/resource coverage,
Drive checkpoints, interruptions, and pending-work continuation. Then expand
qualification per adapter/runtime. This evaluation accessed no private mailbox
or Drive, scheduled no jobs and sent no messages.

The entire raw corpus is only 36,045 bytes; the largest file is 2,353 bytes. This
is a correctness probe, not a memory, token, duration, large-attachment or managed
VM capacity test. Those limits remain unmeasured here. Source discovery, actual
provider operations and downstream task deduplication also remain untested.

## Reproduce

From the repository root, using Python 3.9+ and its standard library:

```sh
python3 docs/plans/restart/identity/mime-evaluation/generator.py
python3 docs/plans/restart/identity/mime-evaluation/evaluate.py
python3 docs/plans/restart/identity/mime-evaluation/boundary_checks.py --output docs/plans/restart/identity/mime-evaluation/boundary-results.json
```

Raw fictional `.eml` files are generated under the ignored `corpus/raw/` directory.
Only the generator, truth manifest and analysis artifacts belong in Git. Saved
witnesses contain source fields and digests, not raw bodies or attachment bytes.
The final report binds the generator, manifest, adapter, evaluator and unchanged
original matcher hashes. Deterministic execution is checked separately from
identity correctness; this command intentionally reports failed decisions rather
than rewriting expected labels to obtain an all-green result.
