# Google Drive — canonical storage

Use this shared mapping with [setup](../operations/setup.md) and
[storage](../operations/storage.md). The selected private root contains the
readable entry point and approved `system`, `instance` and `extensions` areas.
Drive stores processed Knowledge, Tasks, source metadata, coverage and
configuration. Raw email/attachment bytes stay at their source.

## Map the concepts

| School-OS meaning | Drive representation and required observation |
|---|---|
| Entry point | Readable supplied instruction document identifying the instance and its configuration/directory roots. |
| Canonical page | Full UTF-8 JSON file with the approved page envelope and family records, within the installed data contract's current 64 KiB maximum. |
| Directory/index page | Bounded JSON entries with explicit School-OS continuation, at most 100 entries and within the byte limit. |
| Page/record identity | School-OS IDs inside content; Drive file IDs, names and links are access aids. |
| Successful save | Read back actual complete saved content, confirm instance/page/family/revision and intended values under the storage procedure. |

An authorized connector must be able to read the file contents, not merely its
title, snippet or metadata. Do not convert canonical JSON to a native document
whose representation changes the data contract. If only metadata or a summary
is available, the canonical read is unsupported through that route.

## Find, read and write

Start with the selected entry point and follow its references. Check the
instance identity on each canonical page. Resolve stale access aids through the
approved directories; never pick an identically named file from another instance.
An ambiguous root or duplicate page ID requires review before a dependent write.

Follow every connector continuation when listing is needed. Drive documents
partial/empty pages before enumeration finishes and an `incompleteSearch`
indicator; a connector may omit those signals. If it cannot establish exhaustion,
report incomplete discovery rather than treating a short list as complete.
Temporary provider page tokens do not replace School-OS directory references.
[Drive listing semantics](https://developers.google.com/workspace/drive/api/reference/rest/v3/files/list)
and [search scope](https://developers.google.com/workspace/drive/api/guides/search-files).

Use the selected-root boundary for writes. Create/update only the intended
bounded files; preserve unrelated data and extensions. Follow the storage
procedure for page/catalogue/index updates. Read back the changed content before
claiming persistence or removing a temporary processing copy. A file handle or
generic write receipt does not establish canonical correctness. If a write result
is unknown, inspect the authorized target before repeating it; no repair engine
or multi-file transaction is implied.

Folder creation, file reads/writes, authentication, API calls and byte transfer
belong to the executing connector. This mapping imposes no SDK, personal machine
or process. An agent that can search Drive but cannot retrieve full files or
write/read back JSON cannot perform all these operations. State that limit and
continue only independent supported work. No live Drive route is qualified here.
