# Migration 0002 — alpha.13 structured state

## Purpose

Transform only the declared alpha.12 template forms into alpha.13 structured
state: the idle YAML admission pointer, the alpha.12 instance/file-map
references, and the exact readable canonical-task table. This migration does
not inspect a private instance automatically, infer undocumented Markdown, or
reinterpret source facts, provider bindings, parent edits, or history.

## Supported input and target

Supported alpha.12 input is exactly:

- an `instance.yaml` with data schema version 1 and the alpha.12
  `active_release` and `state` reference shapes;
- an idle `state/operation-state.yaml` with no active operation, historical
  success value, or error value;
- a version-1 `state/file-map.yaml`; extension file-map entries are retained
  unchanged while the two alpha.13 operation entries are added; and
- the declared `data/action-items.md` title, headings, tables, columns, and
  row widths. A row is mechanically converted, and completion rows attach only
  to an existing open task.

The target is data schema version 2, an alpha.13 active-release/registry
reference, `operation-state.json`, an operation-checkpoints folder reference,
an installation-manifest reference, and `canonical-tasks.json`. The target
release version is an explicit verified migration input; it is never copied
from the old active release. The old files remain immutable backup evidence.

Active alpha.12 operations, non-null historical state values, unknown instance
keys, altered table headings/columns, malformed rows, completion rows without
an open task, and any unrecognized prose are exact blocking exceptions. They
require an authorized private mapping; this repository must not guess one.

## Procedure

1. Under `system-upgrade.md`, inventory exact IDs and complete bytes of each
   supported target. Verify the supplied alpha.13 package and target release
   identity before creating candidates.
2. Create/read back generation-specific backups of every target before a write.
   Preserve user extension files and configuration that are outside this
   migration's declared targets.
3. Run `school_os.migrate_alpha13.migrate_alpha12` with the old manifest,
   idle state, file map, readable task table, target release version, and target
   schemas. It returns byte-stable candidates only; it never writes a private
   file.
4. Validate each candidate against its schema, compare the task conversion
   field-for-field with the legacy row, and record a journal checkpoint. Replace
   exact targets using the selected coordination mode, then read back exact
   bytes and hashes before the next target.
5. Re-run the transformer against the same alpha.12 backup inputs and require
   byte-identical candidates. After activation records Migration 0002 complete,
   validate existing targets and skip rather than rewriting them.

If a declared input or readback is unsupported, ambiguous, or drifted, stop
before activation, preserve the backups/journal, and report the exact exception.
