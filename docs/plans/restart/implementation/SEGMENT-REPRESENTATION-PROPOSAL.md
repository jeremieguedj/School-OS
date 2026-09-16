# One remaining implementation gap: oversized values

Status: concrete recommendation for approval, not adopted. The user approved the
published data architecture. During implementation review we found that it reserves
`segment_refs` and numbered lossless pieces but never defines their stored shape.
That omission prevents different fresh agents from interoperating on oversized
knowledge, relationship history and completion-review history. All other published
architecture decisions remain approved.

## Recommendation

Use one narrow `record_segment` family for values that would make their owner's
canonical JSON page exceed 64 KiB. Each segment is ordinary bounded Drive JSON,
with its own School-OS ID, its owner, the field being split, its position and the
next segment reference. A short descriptor on the owner tells the reader where
to start and how many pieces to expect. No writer, service, queue or repair
framework is added; the agent performs normal saves and readback.

For a long Knowledge statement, keep the already-approved `segment_refs` field
instead of `statement` and give it this concrete descriptor:

```json
{
  "value_encoding": "json_text",
  "first_ref": {"family": "record_segment", "id": "segment_<uuid-v4>"},
  "segment_count": 2
}
```

For the other already-approved split histories, replace the oversized
`relationships` or `parent_state.completion_reviews` array with
`{"state":"segmented","segment_refs": <the same descriptor>}`. This explicitly
adds one known alternative to those fields; it is not an empty or unknown array.
Small values retain their existing shape. No other field is enabled by implication.

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

`next_ref` is omitted on the last segment. Allowed owner/field combinations are
Knowledge `statement`, Knowledge `relationships`, and Task
`parent_state.completion_reviews`. The last uses a Task owner reference. Ordinals
start at 1. Segment IDs are assigned once, never derived from content. Segments
are located through the same bounded family-directory/locator mechanism; they
are not new source emails, claims or Tasks.

## Exact meaning and flow

1. Encode the whole field value as ordinary JSON text: a JSON string for a
   statement or a JSON array for history. Split that text losslessly at character
   boundaries, preferring paragraph boundaries where possible. Each segment's
   fully encoded containing page must remain within 64 KiB, including escaping
   and envelope overhead. No hashes or provider IDs define the pieces.
2. Write a complete new chain with new segment IDs whenever the owning logical
   value changes. Verified segment records are immutable; never rewrite the
   currently referenced chain before changing its owner. Save and read back the
   new pages and their locator/catalogue entries, then switch and read back the
   owner descriptor and required derived indexes.
   The owner revision changes when the logical field value changes. An index is
   built from the reconstructed whole value, never just its first segment.
3. A reader follows `first_ref`, verifies owner/field/ordinal on each segment,
   follows `next_ref`, and expects exactly `segment_count` distinct segments.
   Concatenate the chunks, decode the JSON once, and require the original field
   type. A missing piece, cycle, duplicate ordinal, wrong owner, wrong type or
   unexpected continuation is incomplete data, never a shortened fact or history.
4. Edit through the owning record using a new verified chain. A segment is not
   independently edited while leaving its owner's revision unchanged. Old chains
   may remain unreachable; cleanup is not required for correctness and no garbage
   collector or repair engine is introduced. Save/readback is non-atomic as already
   accepted; this adds no recovery promise, checksum identity or repair engine.
5. A large reference list does not grow on the owner: the first reference, count
   and next links remain bounded while more segments extend capacity. Whole-email
   ingestion cannot complete until all required pieces are saved and checked.

A segment directory is canonical access machinery, not a semantic search index.
Only the owning Knowledge/Task contributes a semantic result. A reader may obtain
pieces in manageable units, but cannot call a partially read required value complete.

## Why this choice

This supports lossless retained knowledge (P1), bounded access (P4), fresh-agent
portability and provider independence (P6/P9), and the existing fact/history and
task-review use cases. It completes the already-approved segmentation concept
without reinstating D2's generic writer or repair design.

The cost is extra Drive reads/writes only for oversized values. Replacing an
oversized value copies its chain and can leave old unreachable pieces, increasing
storage; no automatic cleanup guarantee is proposed. JSON-encoded
chunks are less convenient to read alone; the complete reconstructed value has
the same original type and meaning. Standard JSON handling in the executing
agent's existing environment is sufficient; no new dependency or permanent
process is proposed.

Credible alternatives:

- **Separate segment families for each field.** More self-describing individual
  pieces, but three parallel formats and more adapter/documentation work.
- **Raise the page limit or allow oversized records.** Fewer reads, but changes
  approved D1 resource bounds and may fail on managed-agent transfer limits.
- **Block oversized values in the MVP.** No new shape, but cannot preserve the
  approved long information/history requirement; affected ingestion stays incomplete.

Remaining unknowns are actual connector cost and reliability, to be observed
later. Approval of this representation does not qualify it or authorize a new
unrelated test sequence. The three already authorized ingestion trials still
follow completion and verified publication of the retained implementation.
