# Small deterministic helpers

Status: **written and locally checked; not provider-qualified**. These Python standard-library
functions support the approved
[metadata recipe](../contracts/identity.md). They have no
I/O, provider dependency, command-line entry point, persistence layer or model
calls. No Python version or minimum runtime is pinned here.

The executing agent may use [source_metadata.py](source_metadata.py) and
[bootstrap_contract.py](bootstrap_contract.py) for these specific operations
when its code environment supports them. An agent may also perform the same
approved checks through its available tools, retaining the same meaning and
uncertainty boundaries. The approved requirement that School-OS agents can
execute code still applies; using a tool for one operation does not introduce a
supported no-code runtime.

| Function | Intended use and result |
|---|---|
| normalize_subject(text: str, *, representation: str) -> str | Require representation to be raw_header or decoded. Decode/unfold raw headers once; preserve already decoded text literally. Both trim outer whitespace while preserving case, punctuation, reply/forward prefixes and meaningful interior spacing. |
| normalize_address_parts(local_part: str, domain: str) -> tuple | Given already reliably extracted address parts, trim outer space/tab, preserve local-part spelling/dots/plus tags and lowercase the domain. Return the two parts as a tuple. |
| utf8_size(text: str) -> int | Measure the exact UTF-8 byte length of supplied text. It does not serialize an object, select a storage limit, split a page or write data. |
| check_installation_materials(selected_root_id, expected_files, saved_readbacks) -> dict | Compare a caller-selected, phase-specific finite installation expectation with exact bytes and ancestry already read back. |
| check_bootstrap(contract_revision, instance_id, manifest, page_bytes) -> dict | Validate a temporary finite setup-route manifest against exact page bytes already read back. The result is `valid`, `invalid`, or `insufficient_evidence` with deterministic diagnostics. |

## Installation-material check

`check_installation_materials` is a pure transient comparison. The caller gives
it the selected installation-root identity; a map from each expected root
document or `system/` relative path to the exact bytes supplied by the starter;
and one already-read result per path. Each readback contains `relative_path`,
exact `content_bytes`, and the observed `ancestor_ids`. The helper does not open
the ZIP, enumerate Drive, fetch a file or decide what the starter should contain.

Setup uses it twice with two exact expected maps. Immediately after placing the
starter, the first map contains the supplied bytes for every root document and
every `system/` member. At the final setup gate, the second map replaces only
the `START-HERE.md` expectation with the exact complete configured-entrypoint
bytes that setup intends to save; `README.md`, `AGENTS.md`, `CLAUDE.md`, and
every supplied `system/` member retain their exact starter-byte expectations.
The saved entrypoint has no arbitrary-byte exception. The caller derives both
finite expectations from the starter and current setup operation, then discards
them after comparison. They are not a canonical manifest or installed state.

Missing expected bytes, ancestry, or a readback yields
`insufficient_evidence`. A saved-byte mismatch on any expected path, placement
outside the selected root, an unexpected supplied readback, or a duplicate or
conflicting path yields `invalid`. Only the complete matching finite set yields
`valid`. The result does not prove a canonical instance bootstrap; setup also
requires a separate valid `check_bootstrap` result.

Exact configured-entrypoint bytes do not by themselves prove that a fresh agent
can use the entrypoint. Setup and independent evaluation read the complete saved
`START-HERE.md`, derive the temporary bootstrap manifest from the roles, roots,
families and route/scopes visibly enumerated there, and treat any failed
derivation as insufficient evidence. That semantic gate stays outside this byte
helper so School-OS does not acquire a rigid entrypoint parser or format.

## Bootstrap contract check

`check_bootstrap` is a pure contract-revision-1 check. The caller supplies a
temporary manifest with a non-empty `routes` array. Each route contains a unique
human-readable `role`, a `root_page_id`, and an `expected` object containing the
approved page `family` plus its exact route key when applicable:

```json
{
  "routes": [
    {
      "role": "fictional-mailbox-pending-knowledge",
      "root_page_id": "page_catalogue_<uuid-v4>",
      "expected": {
        "family": "page_catalogue",
        "route": {
          "canonical_family": "knowledge",
          "source_account_id": "source_account_<uuid-v4>",
          "source_month": "pending"
        }
      }
    }
  ]
}
```

The manifest is setup's finite expectation, not retained instance data. Setup
derives it from the parent's selected Source Accounts and initial source scope;
the helper never chooses accounts, months, logical roles, or pages. Pass every
complete page readback as a separate `bytes` value. Do not reserialize parsed
objects: the original bytes establish the encoded-size check and ensure the
helper assesses the actual saved representation.

The helper checks strict UTF-8 JSON, duplicate JSON keys, the shared 65,536-byte
limit, identity and schema revision, approved page families and route keys,
positive revisions, directory/index entry bounds, continuation shape, duplicate
or conflicting page IDs, manifest roots, and contract-defined page references.
It follows configuration roots, continuations, locators, catalogues, derived
index directories, index coverage, and Discovery Window Email directories. A
missing root or referenced readback yields `insufficient_evidence`; an observed
contract contradiction yields `invalid`. Either result keeps setup incomplete.
The temporary manifest uses the reserved role names `active-tasks` and
`completed-task-history` exactly once for those two required Task roots. A
missing or renamed role yields `insufficient_evidence` with
`missing_required_manifest_role`; a duplicate yields
`duplicate_required_manifest_role`. If the two exact roles resolve to the same
owned root page ID, the helper returns `invalid` with `task_role_root_alias`.
Each reserved role must use exactly the existing `record_locator` family with
`{"canonical_family": "task"}` as its `locator_key`; another family or selector
yields `required_task_role_expectation_mismatch`. This check adds no canonical
field or persisted discriminator.

This is deliberately not a schema catalogue, provider reader, graph repairer,
writer, or route generator. Diagnostics and the manifest stay temporary. The
helper does not retain source content, call Drive, invent a universal route
count, or turn a generic catalogue root into an approved route.

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

There is no date parser, association threshold, general canonical record schema,
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
absent from a distributed starter. The source-metadata, bootstrap,
installation-material and evaluator prepared checks ran locally on 2026-09-18;
all 73 combined tests passed. Python compilation also passed with bytecode cache
output directed to an admitted temporary directory. These checks make no
connector, agent or provider claim.

## Private trial-evaluation helper

[`trial_evaluation.py`](trial_evaluation.py) implements the approved T14–T19
local evaluator support. It is a development/trial harness, not part of an
installed School-OS instance and not a provider connector. It can:

- preflight an admitted gitignored receipt directory with an owner-only
  synthetic write/read/delete and save exact receipt bytes exclusively as mode
  0600;
- keep dispatch, provider-response observation and local receipt persistence as
  separate states;
- normalize controller observations, retain a later final response over an
  earlier running snapshot, and authorize a follow-up only after exact
  provider/task/conversation/route/root/stage and task-composer binding;
- permit one separately labelled retry only after caller-supplied saved evidence
  proves no dispatch and no effect, while binding every attempt to the SHA-256
  of the same exact caller-supplied opening-message bytes;
- validate a proposed call against the exact caller-supplied callable schema,
  including declared argument names, required/optional keys, simple types and
  mutually exclusive locator groups, without dispatching it;
- preflight a source oracle against exact round-manifest and source-input bytes,
  one independently exhausted enumeration chain per private source-input query
  alias, exact enumeration receipt digests, recorded token continuity, supported
  comparable arrival timestamps and the exact local half-open interval filter;
- traverse already-read pages from caller-supplied configuration/bootstrap roots
  through every page-reference shape in the current contract, including nested
  bucket page IDs, continuations and replaceable page hints, while resolving
  canonical record references and preserving incomplete/unknown results;
- determine whether report bytes have a same-task prompt/final/export chain and
  a supported saved receipt whose exact artifact SHA-256 and byte count agree
  with both recorded artifact metadata and the downloaded bytes, otherwise
  limiting evidence to the observed visible response;
- require an exact private image/rendering binding and an independently authored
  expectation before an image-specific finding is allowed; and
- measure exact canonical readback bytes and create marked noncanonical
  64/128/256 KiB comparison pages from the same ordered complete records.

The helper performs no Gmail, Drive, browser or model operation. Callable
schemas, proposed arguments, controller observations, source-input bytes,
enumeration tokens and receipt evidence are all supplied by the caller. The
oracle preflight verifies the integrity of those supplied bytes and the recorded
token chains; it does not parse an opaque receipt to derive its next token or
prove that a provider returned every possible item. Its reference audit consumes
bytes/pages the evaluator has already acquired; it does not choose bootstrap
roots or repair missing state. `page_hint` remains advisory:
an unresolved hint is reported separately, while an unresolved canonical record
or required page/continuation makes the audit incomplete. Candidate packing
never changes the installed 64 KiB contract and never splits one record.

The fictional examples and report template live in
[`examples/evaluation`](../examples/evaluation/README.md). The corresponding
[`prepared checks`](prepared_checks/check_trial_evaluation.py) passed locally on
2026-09-18 as part of the 73-test combined run. They include injected
receipt-sink classification, exact nested reference traversal, same-name
artifact rejection, independently grounded image expectations, a near-limit
whole-record rollover case, controller binding, call-schema validation, exact
export-receipt binding and multi-chain source-oracle cases.

The optional fictional bootstrap and installation-material checks in
[`prepared_checks/check_bootstrap_contract.py`](prepared_checks/check_bootstrap_contract.py)
exercise a valid empty instance, the separate setup gates, and targeted invalid
or indeterminate variants. They passed locally on 2026-09-18 as part of the
73-test combined run. Prepared checks are not included in the distributed
starter.
