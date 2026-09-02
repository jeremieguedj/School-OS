# Attachment-processing operation

## Purpose

Record every attachment's existence and extract facts only from attachment content the selected runtime actually reads.

## Procedure

1. Record source message identity, attachment identity, filename, declared MIME type, and presence.
2. Read the attachment only if the active capability profile supports it.
3. For readable content, preserve the extractor outcome and derive facts with ordinary source coverage.
4. For unreadable, unsupported, inaccessible, oversized, or excluded content, record the precise outcome and produce no inferred facts.
5. Never treat an attachment filename, link text, or surrounding email summary as proof of the attachment's contents.
6. Keep any remote binary or source link as provenance when configured; do not duplicate private binaries into this repository.

## Terminal outcomes

`extracted`, `duplicate`, `unsupported`, `inaccessible`, `excluded_by_policy`, or `manual_review`.

Attachment failure must be visible in the catalog and must not silently disappear.
