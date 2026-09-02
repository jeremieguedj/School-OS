# Release contract

## Source release

A source release is a tagged, immutable version of the reusable repository. A production instance must never execute an unpinned source branch.

## Installed release

An installed release is a managed copy under the private Drive instance's `system/releases/<version>/` area. It is the runtime authority for that instance.

## Version fields

- `system_version`: reusable package version.
- `data_schema_version`: private data structure version.
- `adapter_contract_version`: version of a declared abstract adapter contract.

## Transport modes

1. Manual package: user downloads a tagged release asset and shares it with an agent.
2. Connected retrieval: an authorized agent retrieves that same pinned release.

GitHub connectivity is optional transport only. Production runs read the installed release from Drive.

## Update behavior

An upgrade stages a new installed release, validates compatibility, executes only declared migrations, verifies results, and activates the new release only after success. The installed instance records its current active version and migration history privately.
