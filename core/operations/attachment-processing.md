# Attachment-processing operation

## Purpose

Record every attachment's existence and extract facts only from attachment content the selected runtime actually reads.

## Procedure

1. Record source message identity, attachment identity, filename, declared MIME type, and presence.
2. Read the attachment only if the active capability profile supports its exact
   declared MIME type and size. Record the observed MIME/identity/byte-length
   readback before treating any content as readable.
3. For supported readable content, require a complete read result. A MIME
   attachment read binds its identity, declared MIME/size, read mode, locator,
   and version evidence. A direct resource fetch binds the exact source URL,
   bounded HTTPS redirect chain, status, EOF, observed byte count, optional
   content length, verified MIME/signature, and final URL.
4. Preserve the exact extracted UTF-8 text and
   extracted-text hash, separately record an original-content hash only when
   the observed surface returned original bytes, and derive facts with ordinary
   source coverage. Every attachment Fact also records the attachment identity,
   origin, MIME type, and either an exact extracted-text byte span or a
   provider-backed page/region locator. The selected alpha.13 test path may use
   its observed PDF/image extractor; unselected format extractors remain
   independent.
5. Require ordered complete-unit evidence for every selected extraction:
   `page:1` through the reported PDF page count, `image:1` for one image, or
   `text:1` for one text attachment. A representative page or signature alone
   is insufficient. Preserve both the whole-extraction locator and each Fact's
   exact byte span in the preserved extracted text.
6. For unreadable, unsupported, inaccessible, oversized, or excluded content, record the precise outcome and produce no inferred facts.
7. Never treat an attachment filename, link text, or surrounding email summary as proof of the attachment's contents.
8. Keep any remote binary or source link as provenance when configured; do not duplicate private binaries into this repository.

## Terminal outcomes

`extracted`, `duplicate`, `unsupported`, `inaccessible`, `excluded_by_policy`, or `manual_review`.

Attachment failure must be visible in the catalog and must not silently disappear.
An unsupported or manual-review outcome contains no inferred attachment text or
facts. A declared supported attachment whose identity, MIME type, or byte count
does not read back exactly is `inaccessible`, not extracted. A selected readable
PDF/image without a verifiable locator is `manual_review`, not a silent skip.
Direct HTML discovery is limited to image/PDF URLs in one complete strictly
decoded HTML alternative. Tracking/decorative exclusions require a recorded
reason. Unrecognized resource-bearing markup, an incomplete fetch, or an
unresolved substantive resource blocks message completion; no linked-resource
crawl or HTML-to-text conversion is permitted.
