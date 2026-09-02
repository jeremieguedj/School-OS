# Updates

## Discovering updates

An agent without GitHub access cannot independently discover a remote release. The required baseline is:

1. The user learns of a release through GitHub notifications or another channel.
2. The user downloads and shares the new tagged release package.
3. The agent compares the supplied `release.yaml` to the private installed instance manifest.
4. The agent previews and, after approval, performs the upgrade operation.

A connected agent may optionally check release metadata, but daily production runs remain independent of that connectivity.

## Upgrade rules

- Never execute a live source branch.
- Never overwrite the current installed release in place.
- Stage the new version separately.
- Read back staged files and validate compatibility.
- Back up and verify only declared private migration targets.
- Activate only after validation passes.
- Record the result in private state.

See `core/operations/system-upgrade.md`.
