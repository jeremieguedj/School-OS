# Independent fictional MIME corpus

Run `python3 ../generator.py` from this directory to recreate the ignored raw
`.eml` files and `manifest.json`. The generator uses Python 3.9+ and the standard
library only. It does not import or read any MIME parser, identity resolver,
existing experiment, private source, connector result or network resource.

All people, institutions, messages, attachments, receiving-system events and
delivery histories are fictional. Addresses and remote-resource URLs use
`example.org`. PNG images and minimal single-page PDF documents are constructed
from source, without external inputs. Remote references are never downloaded.
Generated MIME files are ignored to keep encoded binary literals out of Git;
the source and manifest reproduce and bind every file through SHA-256.

The manifest contains 54 observations and all 1,431 unordered pairs, with a
separate `targeted` flag on 49 difficult or diagnostic pairs. Reports should show
the targeted subset separately because unrelated negatives dominate all-pairs
totals. The authored truth is physical delivery history, not the output expected
from a resolver. `communication_id` groups communication content; ordinarily it
equals `occurrence_id`, but the library reminder has multiple deliveries of the
same communication. Distinct deliveries whose complete available evidence is
identical are labeled `indistinguishable_occurrence`. Two observations of one
delivery remain `same_occurrence` even when a projection loses evidence needed
to prove the match. A resolver should be allowed to preserve that uncertainty.

`received_at` explicitly records a zoned value, availability and precision, and
is independent of the sender's MIME `Date`. A minute value denotes the containing
minute. Body-only projections omit envelopes and attachments; missing is not an
empty inventory. Snippets are incomplete body evidence. The optional
`projection_fields` states these limits where relevant.

Encoding, charset, line endings, encoded headers, display-address formatting,
HTML/plain alternatives, CID replacement and exact-byte data-URI embedding are
explicit presentations of selected original deliveries. The attachment-order
case specifically stipulates a connector reserialization of one delivery; it
does not assert that arbitrary MIME order changes preserve source identity.
Separately authored changes to inline placement are different communications
despite identical resource bytes. The unobserved bytes behind remote URLs remain
unknown. Replies, forwarding, quoted history, attachment multiplicity, duplicate
filenames and nested message attachments have separately authored histories.
Two related-message cases share every MIME child and their order but select
different HTML roots with the `start` parameter. Additional cases retain an
unresolved CID reference and an unsupported declared charset as incomplete
evidence, with fixture truth unchanged by a reader's fallback strategy.
