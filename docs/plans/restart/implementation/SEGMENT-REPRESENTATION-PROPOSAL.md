# Q10 linked-piece proposal — rejected

**Status:** rejected by the user on 2026-09-16. It is not part of the School-OS
architecture or implementation.

Implementation review had proposed a `record_segment` family, per-piece IDs,
owner and field links, ordinals, JSON-text chunks, next references, expected
counts, reconstruction checks, and immutable replacement chains for a Knowledge
statement, Knowledge relationship history, or Task completion-review history
that could not fit a page.

The user rejected that design because it would add brittle cross-file
reconstruction and extra Drive reads and writes. Do not implement `record_segment`,
`segment_refs`, linked chunks, field sharding, truncation, or a fallback raw blob.

The current decision is in the [page-size assessment](PAGE-SIZE-ASSESSMENT.md):
retain one 64 KiB encoded UTF-8 page maximum, continue ordinary record collections
across existing pages, and block a whole canonical record that cannot fit. If
actual whole-record sizes or authorized trial I/O/query results justify it, a
later decision may change the single shared installed-contract maximum to 128 or
256 KiB without changing stable IDs, locators, or existing pages.

The full rejected proposal remains recoverable from repository history and the
published implementation-review checkpoints. It is historical design evidence,
not operating guidance.
