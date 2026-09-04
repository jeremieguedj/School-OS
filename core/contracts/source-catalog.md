# Source catalog contract

## Purpose

The source catalog is the private canonical record of processed communications. It preserves source provenance, atomic facts, coverage, and available raw content so derived outputs can be rebuilt without rereading unrelated history.

## Logical record

A catalog record contains:

- a stable `record_id`;
- one or more source conversation/thread identifiers when intentionally folded;
- ordered source message identifiers;
- source metadata needed for provenance;
- one raw body for every ordered source message, retained verbatim from the complete body returned by the selected mail adapter;
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

## Coverage

Every substantive sentence or clause in source text maps to one or more facts or an explicit no-fact outcome with a reason such as greeting, boilerplate, duplicate, or unavailable content. Attachments receive a separate presence/processing outcome. The catalog never invents attachment content it could not read.

## Lossless acceptance gate

For each ordered source message, the catalog record identifies the immutable message ID and contains a distinct raw-message section. Before accepting a new or changed record, compare that section directly with the complete plaintext body returned for the same message ID by the selected mail adapter. The strings must be equal without deletion, substitution, summarization, reordering, ellipsis, or whitespace normalization. Headers and metadata exposed separately by the adapter remain required provenance fields but are not invented when the adapter does not expose them.

The complete raw Markdown file must then be read back byte-for-byte. A record is verified only when both comparisons pass: source body to raw-message section, and intended Markdown bytes to persisted Markdown bytes. Comparing persisted content only with an agent-authored draft is circular and does not prove losslessness. An unverified record must not enter the catalog index or drive any Fact, derived record, task, brief, delivery, or cursor change.

## Derived filters

- Current tasks derive from unresolved action facts, excluding guidelines.
- Guidelines derive from guideline facts.
- Rolling updates derive from update facts that are neither actions nor guidelines.
- Durable profiles derive from durable facts.

Derived data retains source fact references and is not a replacement for the source catalog.
