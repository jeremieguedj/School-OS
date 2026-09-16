# Q10: when one saved item is too large for a file

Status: proposal for explicit approval, not adopted. Q1–Q9 and the broader data
architecture remain approved. This page explains one representation detail found
during implementation review; it does not reopen those decisions.

<a id="gap"></a>
## The problem

School-OS stores its processed knowledge and tasks in many bounded JSON files on
Google Drive. **JSON is field-labelled structured text:** for example, a Knowledge
record has a field for its statement, fields describing who or what it applies to,
and fields linking it to its source. It is a readable storage format, not a copy of
the original email or PDF.

School-OS chose a default limit of **64 KiB (65,536 encoded bytes) for each
JSON page**, including field names, punctuation, escaping and the surrounding page
structure. That is a School-OS resource boundary. It is not an inherent limit of
JSON or Google Drive, and it is not a cap on the family's whole history.

When there are many ordinary records, School-OS simply adds more bounded pages:

```text
Many ordinary records

Page 1 (≤ 64 KiB)  →  Page 2 (≤ 64 KiB)  →  Page 3 (≤ 64 KiB)
knowledge A–F          knowledge G–L          knowledge M–R
```

Q10 concerns a different case: **one field in one Knowledge or Task record is too
large to fit even when that record has a page to itself.** Adding another page for
later records does not split that one value.

```text
One unusually large field

Record page (≤ 64 KiB)
├─ ID, scope, source, dates … small enough
└─ statement … too large to fit here by itself
```

A realistic example is a long, extracted school guideline whose conditions,
exceptions and qualifications must be retained. This is the processed guideline,
not a raw email or PDF archive. Two other values can grow over time: the list of
evidence-backed links showing that later Knowledge corrects, supports, replaces or
conflicts with earlier Knowledge; and the review history recording why a Task may
be complete and what the parent decided. This proposal does not claim that typical
school messages are huge or that testing has established how often overflow occurs.

Some terms used below:

- **Knowledge** is one source-linked piece of information School-OS retained, at
  its real child, family or school scope. It is not the entire school year in one
  record.
- A **Task** is one action the parent or family may need to complete.
- A **relationship** is an evidence-backed link between two Knowledge records,
  such as “this later notice corrects that earlier notice.”
- A **completion review** records evidence that a Task may be finished and the
  parent's confirmation or rejection; evidence does not close the Task by itself.

The tiny examples elsewhere in the documentation, such as a one-sentence lunch
rule, are artificial teaching examples. They do not show the size of every real
Knowledge record.

The earlier approved design already said that School-OS must preserve all
meaningful information and split an oversized value into lossless numbered pieces.
It did not define the pieces' owner, links, order, expected count or content format.
Without that definition, one GPT Work session could improvise a format that a later
Gemini session cannot reliably reconstruct. We missed this representation detail;
the broader architecture is not being reopened. Because every new architecture
detail requires the user's explicit approval, the format remains unapproved and a
write needing it remains blocked rather than truncated.

<a id="recommendation"></a>
## Recommendation: one shared linked-piece format

For only the three fields named below, keep the original Knowledge or Task record
as the owner. It retains its School-OS ID, scope, source links, dates and other
ordinary fields. In place of the oversized value, it stores a small pointer to the
first piece and the number of pieces expected.

Each piece stores:

- the owner record and the particular field it belongs to;
- its numbered position;
- part of the value as text; and
- a pointer to the next piece, except on the last piece.

Every piece is itself stored in an ordinary bounded JSON page. The allowed fields
are exactly:

1. Knowledge `statement` — the substantive information and its qualifications;
2. Knowledge `relationships` — its evidence-backed links to other Knowledge; and
3. Task `parent_state.completion_reviews` — its completion-evidence review history.

No other field gains this representation by implication. Small values keep their
existing form. Segments are storage pieces belonging to their owner; they are not
new Knowledge, Tasks, emails or source material.

<a id="shape"></a>
## A fictional walkthrough

Suppose Pine School publishes a detailed fictional field-trip guideline. The
Knowledge record says it applies at school scope and links to the original source.
Its extracted statement preserves many transport rules, medical exceptions and
conditional pickup instructions. After JSON encoding, that single statement would
make its page exceed 64 KiB.

```text
Knowledge record: “Field-trip guideline”
┌──────────────────────────────────────────────────────────────┐
│ ID · school scope · topic · dates · source reference         │
│ statement pointer: first piece = S1, expected pieces = 3     │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────┐  ┌────────────────────┐  ┌────────────────────┐
│ S1 · owner/field   │→ │ S2 · owner/field   │→ │ S3 · owner/field   │
│ position 1 · text  │  │ position 2 · text  │  │ position 3 · text  │
└────────────────────┘  └────────────────────┘  └────────────────────┘
       bounded page             bounded page             bounded page
```

To answer a question, a reader finds the Knowledge record through the approved
index, follows the first pointer, and checks that all three distinct pieces have
the right owner, field and positions. It joins the text and decodes it once to
recover the original complete statement. It then answers using that statement and
its source. If piece 2 is missing, the statement is incomplete. The reader must not
silently answer from pieces 1 and 3 as though it found a shorter guideline.

The same process reconstructs the two permitted history arrays. The semantic index
still points to the owning Knowledge or Task; it does not present each piece as an
independent search result.

<a id="flow"></a>
## How an edit is saved

When the logical value changes, the agent creates a complete new set of pieces with
new School-OS IDs. It writes and reads back those pieces and their normal location
entries first. Only then does it switch the owner to the new first pointer, update
the owner revision and required derived indexes, and read those values back.

```text
write + verify new pieces → switch + verify owner pointer → readers use new chain
```

This order reduces the chance that the owner points to pieces that were never
saved. It is not a transaction and does not promise recovery from an interrupted
multi-file write. Old pieces may remain unreachable after an edit, which costs
Drive storage. The proposal adds no automatic cleanup, repair service, checksum
identity or generic write engine. Those limits match the existing MVP boundary.

<a id="tradeoffs"></a>
## Benefits, costs and unknowns

The proposal gives fresh agents one provider-independent way to preserve and
reconstruct the complete permitted value while every page remains bounded. The
owner pointer stays small even if the chain grows, and the meaning, scope and source
remain on the original record.

The cost is extra Drive reads and writes for values that overflow. Replacing one
copies its complete chain, and old pieces may consume storage. JSON-encoded chunks
are awkward to inspect alone, though the reconstructed result has the original
string or array type. We do not yet know how frequently real data will need this
format or what its connector cost and reliability will be; those are matters for
later authorized trials. This representation does not promise that any arbitrarily
large single value can be processed in every agent environment.

<a id="alternatives"></a>
## Alternatives considered

- **Use a separate piece format for each field.** Each piece could be more specific,
  but School-OS would have three parallel formats and more instructions for agents
  to implement consistently.
- **Raise the page limit or allow occasional large pages.** That would reduce piece
  reads, but it would change the approved bounded-access design and could exceed a
  managed agent's transfer or working limits.
- **Keep blocking these values in the MVP.** This avoids a new stored shape, but an
  affected email cannot be fully ingested without discarding required information.

<a id="decision"></a>
## Exact approval requested

The decision requested is: **for an oversized statement or either of the two
histories listed above, use the linked, numbered pieces shown here, verify that
the complete set is present, and write a new set when the value changes.**

The optional technical reference below defines the exact shared format that this
approval would cover.

Approval would define the format; it would not qualify performance, promise
interrupted-write recovery or automatic cleanup, authorize another field, or start
any trial.

<details>
<summary><strong>Technical reference: exact proposed JSON and rules</strong></summary>

For a segmented Knowledge statement, the existing `segment_refs` field contains:

```json
{
  "value_encoding": "json_text",
  "first_ref": {"family": "record_segment", "id": "segment_<uuid-v4>"},
  "segment_count": 2
}
```

For oversized `relationships` or `parent_state.completion_reviews`, replace the
array with `{"state":"segmented","segment_refs": <the same descriptor>}`. This
means a known segmented value, not an empty or unknown array.

A segment record, inside the normal D1 page envelope, is:

```json
{
  "segment_id": "segment_<uuid-v4>",
  "owner_ref": {"family": "knowledge", "id": "knowledge_<uuid-v4>"},
  "field_path": "statement",
  "ordinal": 1,
  "text_chunk": "first part of the JSON-encoded value",
  "next_ref": {"family": "record_segment", "id": "segment_<another-uuid-v4>"}
}
```

Field dictionary:

| Field | Meaning |
|---|---|
| `segment_id` | A School-OS ID assigned once, never derived from content. |
| `owner_ref` | The owning Knowledge or Task record. |
| `field_path` | Exactly `statement`, `relationships`, or `parent_state.completion_reviews`, valid for that owner family. |
| `ordinal` | One-based position in the chain. |
| `text_chunk` | One lossless portion of the whole field after the whole value is encoded as JSON text. |
| `next_ref` | The next segment; omitted on the last segment. |
| `first_ref` | The owner's pointer to the first segment. |
| `segment_count` | The exact number of distinct segments the reader must find. |
| `value_encoding` | `json_text`: decode once after concatenating every chunk. |

Encode a statement as a JSON string and either history as a JSON array. Split at
character boundaries, preferring paragraph boundaries where possible. Each fully
encoded containing page, including JSON escaping and envelope overhead, must remain
at or below 64 KiB. Locate segments through the approved bounded family directory
and locator mechanism.

A reader verifies owner, field, ordinal, distinct IDs, links and exact count before
concatenating and decoding to the original type. A missing piece, cycle, duplicate
ordinal, wrong owner, wrong type or unexpected continuation means incomplete data.
Indexes are built from the reconstructed whole value. Whole-email ingestion cannot
complete until all required pieces are saved and checked. Verified segments are
immutable; edit only through the owning record by writing a new verified chain.

</details>
