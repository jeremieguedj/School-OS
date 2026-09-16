# Store and retrieve bounded School-OS data

Use this procedure for ordinary canonical pages, directories, catalogues, and
derived indexes. Apply [the retained data contract](../contracts/data.md) exactly.
This is an agent procedure, not a storage runtime or interrupted-write repair
engine.

## Bootstrap an instance

1. Start from the supplied School-OS materials and parent-selected Drive
   location. If an entrypoint already exists, resolve it before creating
   anything. Do not create a second instance because a handle changed.
2. For a new instance, assign a School-OS UUID v4 `instance_id`. Create the
   bounded configuration page and bootstrap areas needed to reach canonical
   family directories, locators, page catalogues, and derived-index roots.
3. Create or resolve the Household Entity. Save its reference, parent-selected
   timezone, bounded Source Account references, and the entity/topic directory
   roots in configuration. Add optional tool, recipe, and destination choices
   only when the parent selected them.
4. Store no credentials. Keep current Drive and connector handles in explicit
   access-aid fields.
5. Read back each page and directory entry you create. Confirm instance ID,
   page ID, family, revision, continuation, and intended values.
6. Keep the entrypoint and roots discoverable through the instance
   configuration. Do not invent another registry or required global filename.

### Readable bootstrap roles

The human-readable instance entrypoint must enumerate the installed logical
roles below. For each role, give the School-OS-owned root `page_id`, its page
`family`, and its route/scope in plain text. The entrypoint may use any readable
layout; this table defines required reachability, not a new JSON record or
registry.

| Logical root role | Root page family | Route or scope the entrypoint must identify |
|---|---|---|
| Instance configuration | `configuration` | This `instance_id` and its current configuration page. |
| Canonical family directories and locators | `record_locator` | One bounded root for each installed canonical family, naming that `canonical_family`; this includes Source Account, Entity, Topic, Membership, Email, Attachment Group, Ingestion Coverage, Discovery Window, Knowledge, and Task. |
| Source/month page catalogues | `page_catalogue` | Bounded catalogue-directory roots that reach each logical Source Account + UTC original-Date month route for Email, Attachment Group, Ingestion Coverage, and Knowledge, plus the discoverable unknown-date pending routes. |
| Discovery windows | `record_locator` | One bounded Discovery Window directory root per logical Source Account. Window-specific observed-Email directories remain reachable from each Discovery Window record rather than being mixed into this root. |
| Active Tasks | `record_locator` | The bounded active-Task route. |
| Completed Task history | `record_locator` | The bounded completed-Task history route. |
| Entity index | `entity_index` | The entity-index root directory. |
| Topic index | `topic_index` | The topic-index root directory. |
| Incoming Knowledge relationships | `incoming_relationship_index` | The target-Knowledge reverse-lookup root directory. |
| Derived-index coverage | `index_coverage` | The bounded shared coverage-directory root used for catalogue revision comparison. |

The bootstrap identifies logical roles and owned page IDs; current Drive URLs or
handles are optional access aids. Resolve every listed page and verify its
`instance_id`, `family`, route key, and continuation before relying on it. A
missing, conflicting, or inaccessible root is unresolved setup, not an empty
history. New bounded continuation pages extend the listed root and do not require
adding every page to the bootstrap.

## Route a canonical record

1. Validate the record family, School-OS ID, required fields, references,
   explicit unknowns, and dates against the contract.
2. Select the canonical route:
   - Email, Attachment Group, and Ingestion Coverage: logical mailbox plus UTC
     original-Date month; unknown original dates go to the pending route.
   - Knowledge: the original-Date month of its one primary source.
   - Active Task: active-task directory; completed Task: task history.
   - Entity, Topic, Membership, configuration, Source Account, and Discovery
     Window: their bounded family or source-account directory.
3. Resolve the current page through the locator. Treat `page_hint` and handles
   only as read-saving aids. Verify the returned page and record IDs.
4. If no existing page has room under the data contract's current maximum
   encoded page size and family limits, allocate a new page, link it through
   explicit continuation, and update the bounded directory. Rollover and page
   splitting occur only between complete records or entries.
5. Keep one family per page. Never truncate content or silently drop records to
   meet a limit. If one complete required record cannot fit on an otherwise
   empty page, follow the data contract's oversized-record rule: report the
   observed encoded bytes and required minimum size, and leave the operation
   incomplete.

## Normal save sequence

For each affected page:

1. Read the current page and verify its identity and revision before editing.
   This is a collision check, not concurrent-write support.
2. Apply only the intended record changes. Increment `content_revision` once.
   Confirm encoded UTF-8 size before the write.
3. Write the complete bounded page. Perform the normal readback and compare every
   intended value, its page ID, family, instance ID, and new revision. A
   necessary supported re-read is allowed; it does not become an automatic
   recovery loop.
4. Update the family locator if the record moved or is new. Read the locator
   entry back and resolve the record through it.
5. Update the matching page-catalogue entry with the canonical page ID and exact
   new revision. Read that entry back.
6. Derive all required entity, topic, and incoming-relationship entries from
   the verified canonical values. Update each bounded index page and read it
   back.
7. Only after every required derived write/readback succeeds, update the shared
   index-coverage entry to the canonical revision. Read it back.

If a derived update fails, leave the prior coverage revision. The canonical
record can still be used through fallback. If a canonical or catalogue write
has an unknown outcome, stop, preserve the uncertainty, and report it. Do not
blindly retry a possible duplicate effect or claim interrupted-write recovery.

## Maintain bounded directories and pages

- Keep every page at or below the data contract's current maximum encoded page
  size.
- Keep directory and index pages at 100 entries or fewer.
- Follow and verify every explicit continuation. A short page is not exhausted
  unless its continuation says so.
- When splitting a page between complete records, preserve every record exactly
  once, update locators, update catalogue entries, then rebuild affected derived
  entries and coverage. Do not split one record's fields into separately linked
  storage.
- A locator maps canonical record ID to current page ID. A page catalogue maps
  canonical page ID to current content revision and Drive access aid. Neither is
  canonical record content.
- A changed Drive handle updates only its access aid.

## Increasing the shared page maximum

After a page-budget decision, change the maximum by updating the authoritative
installed data contract and ensuring every operating agent reads that same
revision before it writes. Use one shared maximum, not separate soft and hard
limits. Base an increase on observed whole-record bytes or I/O and retrieval
evidence from routes that could completely write and read the tested pages; mark
an unexercised size honestly.

An increase adds no configuration field, schema variant, record ID, reference
shape or automatic change engine. Existing valid smaller pages, IDs, directories
and indexes remain valid and need no eager merge or rewrite. Apply the new maximum
through ordinary future page writes and normal readback, and report any route that
cannot completely transfer or verify a page at that size.

## Stale index fallback

1. Traverse the relevant small page catalogue through explicit exhaustion.
2. Traverse index coverage and compare every canonical page ID and
   `content_revision`.
3. Treat any missing entry, mismatch, unread page, or unfinished continuation
   as incomplete coverage.
4. Use a fresh index to select candidates, then read canonical records.
5. With incomplete coverage, scan affected canonical source/month and active
   Task pages. If the scan cannot finish with authorized capabilities, report
   the unfinished scope. Never infer absence from zero stale-index hits.

## Non-atomic limits

Canonical page, locator, catalogue, derived index, and coverage changes are
separate bounded writes. The sequence is not a transaction. An interruption
after a canonical change but before the catalogue update can mask index
staleness. This MVP does not repair or always detect that case. Preserve and
report a known uncertain outcome; do not describe revision comparison as an
interrupted-write repair guarantee.
