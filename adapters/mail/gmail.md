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

The adapter must return actual available plaintext body content, not a generated summary. A runtime that exposes only snippets cannot claim lossless catalog capability. Threading is provider metadata; ordered immutable messages are the durable evidence unit.
