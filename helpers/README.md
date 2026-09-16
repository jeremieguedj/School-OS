# Small source-metadata helpers

Status: **written, not run or qualified**. These Python standard-library
functions support the approved
[metadata recipe](../contracts/identity.md). They have no
I/O, provider dependency, command-line entry point, persistence layer or model
calls. No Python version or minimum runtime is pinned here.

The executing agent may use [source_metadata.py](source_metadata.py) for these
specific operations when its code environment supports them. An agent may also
perform the same approved normalization through its available tools, retaining
the same meaning and uncertainty boundaries. The approved requirement that
School-OS agents can execute code still applies; using a tool for one operation
does not introduce a supported no-code runtime.

| Function | Intended use and result |
|---|---|
| normalize_subject(text: str, *, representation: str) -> str | Require representation to be raw_header or decoded. Decode/unfold raw headers once; preserve already decoded text literally. Both trim outer whitespace while preserving case, punctuation, reply/forward prefixes and meaningful interior spacing. |
| normalize_address_parts(local_part: str, domain: str) -> tuple | Given already reliably extracted address parts, trim outer space/tab, preserve local-part spelling/dots/plus tags and lowercase the domain. Return the two parts as a tuple. |
| utf8_size(text: str) -> int | Measure the exact UTF-8 byte length of supplied text. It does not serialize an object, select a storage limit, split a page or write data. |

Retain the original observed values alongside comparison values. These helpers
return only derived values and cannot preserve originals for the caller. They
do not establish logical-email identity, choose a candidate, assign canonical
IDs, prove equal content, or complete unread processing. Existing canonical
references must not be renamed after normalization.

The required keyword-only representation argument describes this call's input,
not a canonical record field. Select raw_header only when the supported source
route establishes that the value is an undecoded header. Select decoded only
when it establishes that the value is already decoded. Do not infer the route
from whether the subject happens to contain encoded-word syntax. Missing or
unknown representation produces no comparison value; obtain a supported view
or keep the comparison unresolved.

The decoded route checks controls/Unicode and trims outer whitespace without
RFC decoding or unfolding. Literal encoded-word syntax stays literal, even
when it resembles a valid encoded word. A CRLF fold in a value declared decoded
is rejected rather than silently unfolded. This prevents double decoding a
connector-decoded subject that intentionally contains encoded-word text.

Raw-header decoding supports B (base64) and Q encoded words using ASCII/US-ASCII,
UTF-8/UTF8, ISO-8859-1/Latin-1/Latin1 and Windows-1252/CP1252 charset labels, with
strict decoding. A supported header wrap is CRLF followed by space or tab:
remove the CRLF and retain the following whitespace. Bare newlines, other
control characters, malformed words, unsupported charsets and oversized encoded
words are rejected. Literal spacing is preserved; whitespace separating two
encoded words is omitted according to their encoding semantics. An ambiguous
literal encoded-word opener is rejected rather than guessed. Decoding never
uses replacement characters or ignores invalid bytes.

Address extraction belongs to the agent's supported source-metadata route.
This helper never separates a display name, chooses a sender from a list or
parses a complete address. Its small input subset excludes quoted local parts,
domain literals and non-ASCII domains; it does not perform IDNA conversion,
alias matching or provider-specific dot/plus equivalence. Its shape checks do
not replace reliable extraction or full source-address validation. Unsupported
forms remain explicit until a supported route can preserve their meaning.

All functions reject non-string inputs with TypeError instead of turning
missing metadata into an empty string. Unsupported or malformed values raise
ValueError with a message that omits source values. An empty subject is an
observed empty comparison value, not evidence that a missing subject is known.
The byte-size helper accepts any valid Unicode text, including whitespace and
newlines, unchanged; invalid Unicode that cannot encode as strict UTF-8 is
rejected. A caller must handle errors without printing private inputs or an
unsanitized connector exception.

There is no date parser, association threshold, canonical record schema,
serializer, provider SDK, pagination code, writer, batch manager, ordinary-save
framework or recovery framework here. Resource management, substantive content
processing and authorized provider work stay with the executing agent and its
tools under the active recipes. These functions introduce no personal-machine,
persistent-process or coding-CLI requirement.

Repository developers may consult the optional
[prepared checks](prepared_checks/check_source_metadata.py) for explicit raw and
decoded counterparts, missing/unknown representation, folded versus invalid
headers, mixed literal/encoded spacing, strict decoding, preserved address
distinctions, rejected unextracted forms and exact multibyte UTF-8 measurement.
That developer-only artifact is not required for setup or operation and may be
absent from a distributed starter. The checks are **written but not run**. No
module import, compilation, example execution, test, build, formatter, typecheck
or connector probe was performed during authoring. Do not run these prepared
developer checks until the user's testing direction. This hold does not prohibit
authorized installed operations from using the helper functions.
