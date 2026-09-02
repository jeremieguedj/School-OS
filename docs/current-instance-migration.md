# Migration of an existing private deployment

This document prepares, but does not itself authorize, migration of a live School-OS-style private Drive system.

## Required sequence

1. Create a private inventory of current files, parent folders, roles, references, and schedules.
2. Classify each private file as reusable system logic, configuration, canonical data, derived data, state, or duplicate/historical material.
3. Extract only reviewed generic rules into this repository.
4. Build synthetic fixtures independently of live private content.
5. Install the first release alongside the existing system without moving live canonical data.
6. Map existing private files through private state.
7. Run old and new operations in no-send/no-provider-write shadow mode against the same bounded input window.
8. Compare catalog, source coverage, derived results, task decisions, and brief output.
9. Obtain explicit approval before changing any live scheduled operation.
10. Disable the old scheduler before enabling a new bootstrap-based scheduler, and verify the supervised first production run.

The repository must not receive the private inventory, mapping, or shadow outputs.
