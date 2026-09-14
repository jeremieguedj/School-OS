# Revised metadata development model

Prepared 2026-09-14. **Code and fictional checks authored; not executed.** No
test, model replay, simulation, compilation or functional validation has been
performed for this revision. No passing count or accuracy result is claimed.

This is the small development model requested by the
[current restart plan](../../PLAN.md#implementation-phase-stop-before-testing).
It illustrates the [approved metadata recipe](../METADATA-RECIPE.md) separately
from the unchanged [frozen study](../metadata-stress/README.md). It is one
component of the whole-project assignment, not an implemented School-OS runtime.

## Boundary

`model.py` uses standalone Python standard-library functions and in-memory
fictional objects. These objects are development examples, **not** canonical
production schemas, a Drive layout, an adapter contract, a persistence protocol,
an installed runtime dependency or approved production architecture.
[D1–D8](../../implementation/ARCHITECTURE-PROPOSAL.md) remain pending approval.

The supported Date fixture domain contains a declared individual original Date
with exact seconds and an explicit numeric timezone. Equivalent known zones
compare as the same instant; original observations remain available. Coarse,
missing, malformed, timezone-unknown and unclear-meaning observations remain
pending in this limited model. This restriction makes the examples inspectable;
it **does not decide the production acceptance threshold**. It does not show
that minute-precision metadata is always inadequate. No received, observation
or provider internal time substitutes for the individual original Date.

The address examples support bare addresses, bracketed display names and the
observed style of flattened display-name/address presentation. They preserve
local-part spelling, dots and plus tags while normalizing domain case. This is
not a complete RFC parser or cross-connector qualification. Recipient fixtures
are complete address sets per To/Cc role, or explicitly unknown/partial; a valid
empty role is represented as an empty complete set. Attachment-name comparison
is limited to complete original-name inventories with matching declared scope.

Neither content nor HTML/MIME structure, byte hashes, provider/RFC IDs, thread
IDs or access hints participate in identity decisions. The model does not infer
conversation groups, exact reply parentage, or physical attachment equality.

## Prepared examples

| Area | Authored examples and intended checks |
|---|---|
| Normalization | Decoded/unfolded subjects; outer whitespace; meaningful case/spacing and reply prefixes; bracketed/flattened addresses; original values preserved |
| Logical reuse | Independently labeled repeated appearances reuse an owned record despite changed access hints; different source metadata or mailbox retains distinctions |
| Optional evidence | Recipient order versus To/Cc roles; explicit empty versus missing/partial; comparable original attachment scopes and repeated names |
| Uncertainty | Incomplete relevant lookup; unsupported Date view; unverified mailbox; several existing compatible records preserved without choosing/merging |
| Replies | An original, a first reply and a later reply each use their own original Date and records |
| Attachment groups | Same filename under different parents; repeated names within one parent; independent candidate reading; fresh passes start without inherited completion; unknown names/scope remain explicit |
| Enumeration | A short page with continuation remains unfinished; absence of continuation alone does not establish exhaustion; serialized window scope supports replay without a token |
| Separate progress | Daily enumeration cannot close historical work or unread attachment content |
| Information limit | An independently authored pair of distinct fictional notices with identical permitted metadata is reused; the example exposes the residual information limit rather than claiming true identity is proved |

The test expectations in `test_model.py` are authored independently of the
model's outputs. Fictional story labels provide logical-email expectations;
there is no live provider-entry-count ground truth. The indistinguishable pair
is an explicit limitation example, not a demonstrated error in the Gmail study.

The attachment pass tracks which exposed candidates were read, separately
from association. Even `declared_inventory_read` does not prove exact individual
attachment identity, body coverage, successful extraction, saved knowledge or
verified persistence. Work references are local to that fictional pass; their
position or spelling does not become a stable attachment identity.

The window snapshot illustrates what information can survive replacement:
mailbox, configured scope, boundaries and their meaning/zone/precision, track,
enumeration state and already associated School-OS record IDs. Serialization is
an example only. The model does not write Drive, simulate actual storage
consistency, independently restore the full catalog, or establish a complete
listing route. Its small in-memory catalog is not a scalable production lookup.

## Later user-directed checks

The user selects whether and when to execute these prepared checks. The next
authorized step would be a focused run of `test_model.py` from this directory,
followed by review of failures and limitations. No execution is requested by
this document; publication hygiene is not functional validation.

Remaining product qualification includes actual original-Date access and
normalization, complete enumeration, attachment/image reading, independent
substantive extraction, bounded Drive writes/readback and interrupted recovery,
knowledge answers, task synchronization, briefs/audio, schedules, fresh-agent
handoff, package installation/upgrades and compatible extension preservation.
This model neither implements those capabilities nor reduces their required
project scope. Any resulting new architecture decision needs explicit approval.
