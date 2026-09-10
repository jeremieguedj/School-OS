# Gmail mail adapter

Status: reference adapter template.

## Required capabilities

- Search messages using configured inclusion/exclusion criteria.
- Enumerate result pages to completion.
- Fetch complete threads/messages in source order.
- Expose immutable message and thread identifiers.
- Expose received timestamps.
- List attachment metadata and read supported attachments.
- Send HTML/text messages and verify provider acceptance or Sent visibility.

## Normalized mapping

| School-OS concept | Gmail concept |
|---|---|
| Source conversation | Gmail thread, with one or more immutable message IDs |
| Source message | Gmail message ID |
| Received date | Provider received/internal timestamp converted to instance timezone |
| Source link | Configured Gmail thread/message deep link |
| Attachment identity | Message attachment/part identity plus observed metadata |
| Delivery result | Provider response and verified sent record |

## Catalog requirements

The adapter must return actual available message content, not a generated
summary. A runtime that exposes only snippets cannot claim lossless catalog
capability. Threading is provider metadata; ordered immutable messages are the
durable evidence unit.

The adapter reconciles the complete full and raw MIME trees before content
selection. It preserves tree order and ancestry, provider and normalized part
identities, declared/effective MIME metadata, exact transport and decoded hashes,
whole-part locators, and the provider Unicode value when exposed. The admission
boundary strictly decodes raw bytes and requires exact equality with that value
before cataloguing.

`mime-accounting-v1` deterministically distinguishes independent mixed content,
alternative representations, related roots, verified whitespace padding,
inline assets, attachments, and subordinate embedded messages. The primary
plaintext body is a presentation alias, not a completeness boundary. Every
substantive admitted text unit is preserved and independently audited; every
other content-bearing node has an explicit outcome or blocks. A raw-message read
anchors the evidence but is not itself a substitute for content accounting.
Attachments and direct image/PDF references remain separately inventoried
outcomes. For the current recovery run, image outcomes are recorded before any
separate fetch and terminate as `excluded_by_policy`.
