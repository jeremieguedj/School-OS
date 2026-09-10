# Drive storage simplification specification

- Status: approved architecture; implementation specification
- Written: 2026-09-09
- Authority: the recovery MVP plan plus the user-approved hybrid Drive-storage
  decision recorded here
- Scope: fresh installations only; no upgrade or migration route

## Purpose and non-negotiable result

Replace the per-logical-file Drive installation with five initial physical
files while keeping Drive canonical, local state disposable, the last committed
state recoverable, and every existing domain contract intact. The implementation
must reduce physical objects and redundant verification, not weaken identity,
containment, complete-byte, admission, provenance, task, delivery, or recovery
checks.

The only initial children of a proven-empty instance root are:

| Name | Mutability | MIME | Role |
|---|---|---|---|
| `BOOTSTRAP.json` | Immutable | `application/json` | Small installation descriptor binding the exact root, package, settings, current pointer, package hashes, source commit, release identity, and interpreter/runtime requirements. |
| `package.tar.gz` | Immutable | provider-observed gzip MIME from the existing finite admitted set | The exact executable release archive. Its internal release manifest and inventory remain authoritative. |
| `settings.yaml` | Immutable for the accepted installation | `application/octet-stream` unless the provider returns an equivalent exact YAML media type that is explicitly qualified | Human-readable private installation settings and the frozen test scenario. |
| `CURRENT.json` | Mutable admission pointer | `application/json` | The exact currently committed state-generation reference, generation/hash chain, package/settings binding, serialization evidence, and prior generation reference. |
| `state-000001.bundle` | Immutable | `application/x-tar` | Initial logical state checkpoint. Later state generations use monotonically increasing six-digit names. |

Source and output bundles are created only when an operation actually has
content to preserve. There are no empty source/checkpoint folders, placeholder
catalogs, separate setup files for each logical record, or separate checksum
file. A task Sheet or Todoist project is bound only after this five-file
installation is admitted, and is not one of the five canonical installation
objects.

## Physical and logical topology

`package.tar.gz` continues to contain reusable code, schemas, templates,
recipes, and the package inventory. `settings.yaml` contains the existing
logical `instance.yaml`, household, integration, policy, private daily values,
source-scope, delivery-configuration, and initial projection-choice values as
named YAML mappings. It contains no credentials. The active task-provider
selector and provider bindings are mutable logical state in a state bundle;
their initial values must agree with settings.

Every other existing logical artifact is a member of the current state bundle:

| Existing logical role | Bundle member |
|---|---|
| File map and current index | `state/file-map.yaml`, `state/current-index.json` |
| Operation admission and checkpoints | `state/operation-state.json`, `state/operation-checkpoints/<checkpoint-id>.json` |
| Source cursor and catalog index | `state/source-checkpoint.json`, `data/source-catalog-index.json` |
| Canonical Facts/indexes | `data/facts.json`, `data/fact-indexes.json` |
| Canonical tasks | `data/canonical-tasks.json` |
| Guidelines and rolling updates | `data/guidelines.json`, `data/rolling-updates.json` |
| Brief template selection | `state/brief-template.json` |
| Active task-provider selector | `state/task-provider-selector.json` |
| Per-provider task bindings/sync bases | `state/task-providers/<provider-id>.json` |
| Capability profile selection and admitted profiles | `state/runtime-profile-selection.json`, `state/capability-profiles/<profile-id>.json` |
| Delivery ledger and pending/confirmed effects | `state/delivery-state.json` |
| Last run evidence | `state/final-run-checkpoint.json` |

The package owns the generic daily recipe and brief templates; a state member
records only their exact package path and hash-bound selection. Existing JSON
schemas continue to govern their corresponding member bytes. New state that
does not yet have a dedicated schema remains a canonical JSON object with an
explicit `schema_version`; this storage change does not redefine its domain
semantics.

An immutable source bundle contains the exact catalog record bytes, selected
message bodies, supported attachment/direct-resource bytes when observed, the
extracted text and provenance locators, and a source-bundle manifest. A state
generation refers to it but never recopies its bytes. Rendered HTML, text, MP3,
and compact audit artifacts may likewise use immutable output bundles when
needed by the existing delivery/checkpoint contract. Historical bundles are
fetched only when an operation needs their contents.

## References

Physical object references retain exact Drive `object_id`, kind, direct
`permitted_ancestor_id`, provider-observed MIME, and version evidence. URL and
byte length are carried in runtime receipts where available but are not treated
as identity.

A bundle member reference has exactly:

```json
{
  "bundle_reference": {
    "object_id": "opaque-provider-id",
    "kind": "file",
    "permitted_ancestor_id": "opaque-root-id",
    "mime_type": "application/x-tar",
    "version": "opaque-provider-version"
  },
  "bundle_sha256": "64-lowercase-hex",
  "entry_path": "state/operation-state.json",
  "entry_sha256": "64-lowercase-hex",
  "byte_length": 123
}
```

An archive member never receives or pretends to have its own Drive ID. Internal
links between members use stable logical entry paths. The resolver combines
those paths with the already-verified current bundle context and returns the
full member reference above. References from a later state bundle to a source
or output bundle include that already-known physical bundle reference and
member evidence directly.

This two-level rule prevents circular hashes: a bundle does not contain its own
object ID or whole-bundle hash. Those are supplied by `CURRENT.json` after the
immutable upload has been verified. No local path or staged receipt is a
reference.

## Deterministic bundle format and safe reads

State, source, and output bundles are uncompressed POSIX ustar archives. The
writer must:

- validate all logical bytes and domain schemas before archive construction;
- use one `BUNDLE-MANIFEST.json` plus lexicographically sorted member paths;
- encode the manifest as canonical UTF-8 JSON with one trailing newline;
- record each member path, role, schema identifier or media type, exact byte
  length, and SHA-256 in the manifest;
- use only regular files, mode `0644`, UID/GID `0`, empty owner/group names,
  modification time `0`, and no PAX or platform-specific headers;
- reject duplicate paths, absolute paths, backslashes, empty/dot/dot-dot path
  components, names that exceed ustar limits, links, devices, and directories;
- produce identical bytes for identical logical entries and manifest metadata.

The manifest records bundle format `school-os-bundle-v1`, bundle kind,
generation or batch identity, instance ID, package archive hash, settings hash,
configuration fingerprint, predecessor generation and hash when present, and
the complete entry inventory. It cannot record the final archive hash because
that would be self-referential.

A state bundle is limited to 32 MiB, 10,000 logical members, 8 MiB per member,
and 256 Unicode code points per logical path. Source/output bundles are limited
to 64 MiB and 10,000 members, with a 32 MiB per-member hard cap in addition to
the smaller configured ingestion/effect bounds. Exceeding a bound produces a
durable continuation or precise blocker under the existing operation rules; it
does not silently omit or truncate content.

Readers parse members without `extractall`. They enforce the same path/type/
count/size bounds before allocating or writing, reject trailing or undeclared
members and duplicate names, stream/hash each declared length, and compare every
member byte hash to the manifest. Local extraction uses a mode-`0700` new
staging directory and mode-`0600` files, then atomically adopts only the fully
verified tree. Failure deletes only that run's staging directory.

## Installation and admission

The current connector does not expose caller-selected Drive IDs, provider-
computed SHA-256 in normalized write receipts, conditional writes, or a single
complete all-MIME child listing. Therefore the first implementation uses full
byte readback, exact-ID reconciliation where an ID is returned, the existing
finite scoped search only for uncertain outcomes without an ID, and an admitted
single-writer mode. Merely requesting an unsupported receipt field cannot
remove a readback.

Installation ordering is:

1. Read exact root metadata and prove the root empty with complete scoped
   listing.
2. Build and locally validate package evidence, settings, and initial logical
   state. Construct the initial bundle locally; this remains staged only.
3. Create `package.tar.gz`, `settings.yaml`, and `state-000001.bundle`; verify
   exact identity, direct parent, provider MIME, byte length, and complete bytes
   or an actually returned provider SHA-256 bound to that exact version.
4. Create and verify `CURRENT.json`, naming generation 1 and the verified state
   object/hash. It records no prior generation.
5. Create and verify `BOOTSTRAP.json`, naming the exact root and the four prior
   objects and hashes. The host bootstrap receipt supplies the exact bootstrap
   object reference; `BOOTSTRAP.json` never self-references.
6. Recover once from that host receipt in a new local directory. Verify root,
   bootstrap, package, settings, current pointer, current bundle, every required
   member, package inventory, configuration fingerprint, and entrypoint before
   reporting installation admitted.

`CURRENT.json` is the installation admission record. There is no separate
installation manifest or admission file. `BOOTSTRAP.json` binds the immutable
installation components and the stable identity of the mutable current pointer;
`CURRENT.json` binds its current exact version and contents. Package and settings
are immutable for one acceptance root. A changed package, interpreter,
dependency set, frozen source bounds, policy, recipe, or test scenario requires
a new package as applicable and a new empty final root under the recovery plan.

## State publication and durability

For generation `N+1`:

1. Read and verify the admitted `CURRENT.json` version and generation `N` state
   bundle. Validate the requested logical transition and serialization evidence.
2. Build and validate `state-NNNNNN.bundle` locally. At this point it is staged,
   not durable and must never authorize an effect or cursor advance.
3. Create the immutable bundle and verify its physical receipt and complete
   bytes. The object is durable but not current.
4. Replace `CURRENT.json` with a pointer containing generation `N+1`, the new
   exact bundle reference/hash, and generation `N` as `previous`. Read it back
   and verify exact bytes, identity, parent, provider version, predecessor, and
   package/settings bindings.
5. Only then may callers treat the logical records as committed and start a
   dependent external effect. The prior bundle remains immutable and
   recoverable.

With the current connector, replacement is not compare-and-swap. Read-check-
update-readback must not be described as provider atomicity. The MVP uses
`attended_single_writer`: each manual mutation records the actor/attempt,
verified scheduler-disabled state, and exclusion of competing mutators. The
scheduled TEST run uses `runtime_serialized` only if its selected scheduler
surface provides a verified single queue for the exact instance key; otherwise
manual execution is excluded and the scheduled process records equivalent
single-actor evidence. Manual and scheduled mutation are never concurrent.
Native conditional mode remains unavailable until an exposed precondition is
qualified.

A lost pointer-update response is reconciled by exact-ID reading of
`CURRENT.json`. If its bytes select and hash the candidate, the generation is
adopted after bundle verification. If it still selects the predecessor and the
provider response establishes no effect, the guarded replacement may be
attempted under the existing policy. Any other bytes/version, ambiguity, or
unknown outcome blocks; the runtime never advances by name or timestamp.

## Effects and interruption boundaries

Stable operation, checkpoint, task, provider-effect, delivery, and source IDs
retain their existing derivation. Before any consequential provider mutation,
the next state generation commits the effect intent with target scope, stable
idempotency identity, base/local/remote evidence, and outcome `pending`. After
exact provider readback, a successor generation records `confirmed` or
`definitely_not_applied`. An uncertain call records `unknown` before any retry
decision; it is reconciled first and is never blindly retried.

| Interruption | Recovery |
|---|---|
| Before bundle create | Ignore disposable local staging; current generation remains authoritative. |
| Bundle accepted, response lost | Reconcile the exact returned/preallocated ID when available, otherwise perform one bounded root-scoped exact name/hash search; adopt exactly one match or block. |
| Bundle verified, pointer not attempted | Current remains on predecessor; exact candidate may be adopted only by the same transition validator. |
| Pointer response lost | Read exact pointer ID; adopt only exact candidate bytes or preserve predecessor when no effect is established. |
| Intent committed, provider not dispatched | Existing intent evidence permits one policy-governed dispatch. |
| Provider response lost | Reconcile provider by stable effect/canonical identity; confirm one exact match, prove no effect before retry, or mark `unknown` and block. |
| Provider confirmed, successor state not committed | Provider readback plus pending intent permits one confirmation-only state publication, never a repeat effect. |
| Local state deleted | Recover the five objects from the host bootstrap receipt, then inspect current pending effects before doing work. |

Adjacent state changes may share one generation only when the existing safety
boundary allows it. Ingestion commits complete source custody/Facts/tasks and
the eligible cursor together only after all declared bytes are durable. Delivery
still follows render/validate, reserve, persist reconciliation delta, one audio
attempt, send, exact Sent readback, and commit. Bundling changes physical
persistence, not that order.

## Projection binding and task switching

After five-file admission, create or bind the selected isolated task projection,
verify its exact scope and empty/expected contents, and publish its binding in a
new state generation. Installation remains valid if projection binding fails;
task execution remains blocked and no selector is activated.

Every task synchronization first imports complete scoped changes, new tasks,
comments, completion, reopen, and parent edits from the selected projection into
canonical Drive state, then refreshes that projection with stable identities and
guarded readback. The guided Sheets -> Todoist -> Sheets operation continues to
pull and commit the old provider, stage and verify the target while the old
selector remains active, then publish the selector change. Failure preserves the
old selector. Dormant mapping members are retained and reused on switchback.

## Connector capability and diagnostics contract

Required current fallbacks are explicit:

| Capability | Current evidence | Behavior |
|---|---|---|
| Exact metadata and complete byte fetch | Available | Always use for roots, pointer, bundles, and writes lacking equivalent checksum receipts. |
| Complete parent listing | Available only as three finite MIME-category searches plus per-child checks | Use for empty-root proof and bounded uncertain reconciliation; do not use in ordinary exact-ID recovery. |
| Authoritative provider SHA-256 | Not exposed in normalized receipts | Full byte readback remains mandatory. |
| Caller-preallocated file IDs | Not exposed | Use returned exact ID; never invent retries after an unknown create. |
| Conditional update/CAS | Not exposed | Use only admitted single-writer evidence and label update semantics honestly. |
| Underlying API/retry counts | Not exposed | Count bridge calls and bytes; report provider operations/retries as unavailable. |

Optional future connector receipts may replace a redundant download only when
they return provider-computed SHA-256, size, object ID, direct parent, MIME, and
version bound to the same write. Complete one-operation listing, preallocated
IDs, or native preconditions may be used only after focused qualification; none
is required for this MVP.

The bridge preserves a privacy-safe structured failure envelope whenever the
upstream connector exposes it: operation kind and correlation token, local/
dispatch/transport/provider/normalization stage, invocation-began and provider-
response-observed flags, HTTP status, allowlisted Google reason/domain,
`Retry-After`, timeout category and elapsed duration, effect classification and
evidence code, known underlying request/retry counts or `unknown`, and receipt-
validity flags. It must omit raw IDs, URLs, request bodies, credentials, private
values, provider messages, and unsanitized exception text. Rate limiting remains
a hypothesis unless status/reason evidence supports it.

## Call accounting

Measure separately: bridge calls by method, bytes uploaded/downloaded, scoped
search pages, observed connector retries, and underlying API calls/retries when
exposed. Do not equate a bridge call with a quota unit.

Under one-page/no-failure assumptions, full-readback verification, and the
current three-category listing, the working estimate is approximately 20 Drive
calls for installation and 11 for cold recovery, or 31 combined. With one
complete listing and authoritative write receipts, the estimate is 8 plus 11,
or 19. These are targets to measure, not acceptance substitutes. Pagination,
reconciliation, projection creation/binding, Sheets, Gmail, Todoist, audio,
scheduler, and later state/source/output bundles are reported separately.

Routine estimates use `C` durable state commits, `F` new immutable source/output
bundles, and `K` historical bundles fetched: `7 + 6C + 3F + 2K` with current
readback behavior, and `7 + 2C + F + 2K + I` with qualified authoritative
receipts and `I` ID-allocation operations. Actual safety boundaries determine
`C`; call targets never justify omitting a checkpoint.

## Implementation sequence and repository changes

1. Add bundle/member/bootstrap/current schemas and a provider-neutral
   deterministic bundle codec with round-trip, malformed archive, bound, and
   reproducibility tests.
2. Refactor `school_os/install.py` to compose the five objects, verify the
   bootstrap/current chain, and safely recover package/settings/state once.
3. Refactor `school_os/connected_setup.py` to stop creating individual seed
   files/folders, install the five-object generation, then expose a separate
   projection-binding operation. Remove redundant `_create_or_adopt` reads when
   the same normalized receipt already contains an equivalent verified byte
   result; retain full readback for the current connector.
4. Add bundle-backed logical reads and generation publication to
   `school_os/connected_storage.py`. Refactor `connected_bootstrap.py`,
   `connected_profiles.py`, `connected_ingestion.py`, `connected_tasks.py`, and
   `connected_daily.py` to use member references and shared state commits while
   retaining domain algorithms.
5. Extend `school_os/codex_bridge.py` only for privacy-safe diagnostics and
   accounting actually observable from the current tools. Do not build a new
   connector framework.
6. Update setup/bootstrap/operation scripts, active package inventory,
   installed validator, templates, and focused fixtures. Preserve archived
   migration/per-object code and tests as historical, but exclude them from the
   active fresh-install route and frozen package.
7. Build the exact package, use a new empty acceptance root, measure the live
   installation/cold recovery calls, bind the Sheet afterward, and resume the
   recovery plan's existing early preview and final live journey.

Focused repository proof covers deterministic round-trip and exact member
bytes; wrong parent/object/digest/package/settings/configuration; safe extraction
and bounds; lost create and pointer response; delayed visibility; distinct
sanitized 403/429/5xx/timeout diagnostics; deletion before/after publication;
single-writer exclusion; invalid publication preserving the predecessor; no
duplicate effect; and measured calls/bytes. The existing live acceptance matrix
remains unchanged: fresh install/recovery, ingestion/custody/Facts, task
reconciliation and both projections, guided switch, manual and scheduled sends,
audio, replay/interruption, schedule inactive proof, local deletion, and fresh-
session continuation.

## Acceptance and stop rules

The storage change is accepted only when a fresh instance contains exactly the
five initial files before projection/source/output work, cold recovery succeeds
from Drive after local deletion, each logical member is byte/hash/schema exact,
the prior state remains recoverable across publication faults, and measured
counts are reported honestly. A missing source, failed/unavailable required
audio, unresolved provider effect, insufficient serialization evidence, or any
open recovery-plan live case remains a blocker; this specification does not
convert it into a passing disposition.

An implementation finding that requires a sixth initial object, a mutable
all-state archive, weaker readback, concurrent unguarded writers, migration,
new access, or broader product scope crosses the approved architecture boundary
and must stop the affected path for a decision. Ordinary bugs and contract-
preserving representation choices are fixed directly.
