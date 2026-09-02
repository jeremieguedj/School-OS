# Source catalog contract

## Purpose

The source catalog is the private canonical record of processed communications. It preserves source provenance, atomic facts, coverage, and available raw content so derived outputs can be rebuilt without rereading unrelated history.

## Logical record

A catalog record contains:

- a stable `record_id`;
- one or more source conversation/thread identifiers when intentionally folded;
- ordered source message identifiers;
- source metadata needed for provenance;
- raw message text retained verbatim where available;
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

## Derived filters

- Current tasks derive from unresolved action facts, excluding guidelines.
- Guidelines derive from guideline facts.
- Rolling updates derive from update facts that are neither actions nor guidelines.
- Durable profiles derive from durable facts.

Derived data retains source fact references and is not a replacement for the source catalog.
