# Source catalog contract

## Purpose

The source catalog is the private canonical record of processed communications. It preserves source provenance, atomic facts, coverage, and available raw content so derived outputs can be rebuilt without rereading unrelated history.

## Logical record

A catalog record contains:

- a stable `record_id`;
- one or more source conversation/thread identifiers when intentionally folded;
- ordered source message identifiers;
- source metadata needed for provenance;
- one nullable primary-body presentation alias for every ordered source
  message, plus every ordered admitted MIME text unit retained verbatim from
  the complete message returned by the selected mail adapter;
- a complete `mime-accounting-v1` inventory binding the raw message, MIME tree,
  every content-bearing node, and exactly one audited disposition per node;
- atomic Fact records;
- source coverage entries ordered with the source;
- attachment presence and processing outcomes; and
- a processing status/checkpoint.

A record must not be discovered by filename alone. Source identifiers and stored ordered message identifiers are authoritative.

## Atomic Fact

Each fact has a stable `fact_id`, source-message reference, local received date, entity scope, category, source-supported text, and independent booleans:

| Flag | Meaning |
|---|---|
| `is_update` | Recent status/news suitable for a rolling update stream |
| `is_durable` | Lasting reference knowledge |
| `is_guideline` | Standing routine, conditional behavior, or rule |
| `is_action` | Finite unresolved parent task or decision |

A guideline is never an action. Facts may not combine unrelated claims merely to reduce record count.

New body Facts carry the stable record ID, immutable message ID, content ID,
content hash, non-empty UTF-8 byte span, and exact `source_quote` that supports
the claim. A Fact's `text` is concise canonical source-supported wording for
derived views; it may paraphrase the quote, but an independent audit must accept
the exact quote, canonical wording, and classification. Unsupported wording or
an incorrect span/flag blocks. Attachment Facts retain those record
and message identities and add the immutable attachment/resource ID, origin
(`mime_attachment`, `html_embedded`, or `html_linked`), declared MIME type,
separate original-content and extracted-text hashes, and one verified locator:
an exact byte span in preserved extracted UTF-8 text or a provider-backed
page/region. For an attachment Fact, the byte span is in that attachment's
extracted text rather than the message body. An unavailable original-byte hash
is recorded as unavailable, never synthesized. Derived knowledge stores Fact and record IDs
so it can be rebuilt without weakening source provenance.

## Coverage

Every UTF-8 byte of preserved source text is covered exactly once by a Fact,
an explicit no-fact outcome, or an explicit review outcome with a reason.
Independent review may accept a faithful source ambiguity when it is retained
as review and no guessed deadline, task, completion, or other claim is promoted.
An omitted clause, unsupported wording, or wrong classification remains a
blocking audit error. Attachments and direct HTML image/PDF references receive
separate presence/processing outcomes. The catalog never invents
attachment/resource content it could not read.

## Lossless acceptance gate

New MIME-accounted records use source schema v3 while retaining the v2
raw-UTF-8 Markdown framing codec in `school_os.catalog` with
`custody_version: 2`. Its
header records stable record/conversation identity, ordered message metadata,
scope, pagination evidence, MIME accounting, primary-body alias custody, and
every ordered attachment and direct-resource outcome. Primary and supplemental
text units use declared byte-counted frames with immutable content IDs and exact
UTF-8 lengths. A message with no primary body still exists through the header
membership and accounting inventory. The parser reads each declared byte count
before looking for another frame, so headings, HTML comments, and delimiter-like
text are data, not structure. V1 heading framing remains a fail-closed
migration input and is not used for new records.

Each extracted attachment/resource text has its own byte-counted content frame,
stable code-assigned content ID, exact text hash, and source-message association.
The header separately retains original-content hash only when original bytes
were observed, the extracted-text hash, read/fetch evidence, all expected
page/image/text units, and the original extraction locator. Direct HTML
resources also retain raw and strictly decoded HTML-part hashes, occurrence,
attribute, original/final URL, and redirect chain. Parsing must dereference each
frame exactly once and reject missing, duplicate, unreferenced, or inconsistent
content.

For each ordered source message, the catalog identifies the immutable message ID
and carrier-relative raw-message entry, then accounts for the complete reconciled
MIME tree in source order. Every content-bearing part must map to preserved text,
an attachment/resource outcome, verified padding, an exact duplicate in the same
alternative group, or a precise blocking disposition. The primary body is only
a presentation alias to one preserved content ID. Every substantive text unit
must reach interpretation and independent audit; no winning-body heuristic may
discard another unit. Source text is compared without deletion, substitution,
summarization, reordering, ellipsis, or whitespace normalization.

The complete raw Markdown file must then be read back byte-for-byte. A record is
verified only when the independently constructed adapter snapshot matches the
declared message membership, raw-message hashes, MIME accounting, ordered text
units, and persisted Markdown bytes. Reconstructing both sides from the catalog
is circular and does not prove losslessness. An unverified record must not enter
the catalog index or drive any Fact, derived record, task, brief, delivery, or
cursor change.

## Derived filters

- Current tasks derive from unresolved action facts, excluding guidelines.
- Guidelines derive from guideline facts.
- Rolling updates derive from update facts that are neither actions nor guidelines.
- Durable profiles derive from durable facts.

Derived data retains source fact references and is not a replacement for the source catalog.
