# Attachment-processing operation

## Purpose

Record every attachment's existence and extract facts only from attachment content the selected runtime actually reads.

## Procedure

1. Record source message identity, attachment identity, filename, declared MIME type, and presence.
2. Read the attachment only if the active capability profile supports its exact
   declared MIME type and size. Record the observed MIME/identity/byte-length
   readback before treating any content as readable.
3. For supported readable content, preserve the exact extracted UTF-8 text and
   extracted-text hash, separately record an original-content hash only when
   the observed surface returned original bytes, and derive facts with ordinary
   source coverage. Every attachment Fact also records the attachment identity,
   origin, MIME type, and either an exact extracted-text byte span or a
   provider-backed page/region locator. The selected alpha.13 test path may use
   its observed PDF/image extractor; unselected format extractors remain
   independent.
4. For unreadable, unsupported, inaccessible, oversized, or excluded content, record the precise outcome and produce no inferred facts.
5. Never treat an attachment filename, link text, or surrounding email summary as proof of the attachment's contents.
6. Keep any remote binary or source link as provenance when configured; do not duplicate private binaries into this repository.

## Terminal outcomes

`extracted`, `duplicate`, `unsupported`, `inaccessible`, `excluded_by_policy`, or `manual_review`.

Attachment failure must be visible in the catalog and must not silently disappear.
An unsupported or manual-review outcome contains no inferred attachment text or
facts. A declared supported attachment whose identity, MIME type, or byte count
does not read back exactly is `inaccessible`, not extracted. A selected readable
PDF/image without a verifiable locator is `manual_review`, not a silent skip.
