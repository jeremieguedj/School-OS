# Onboarding operation

## Goal

Install one pinned School-OS release into a new private Google Drive instance without requiring the agent to contact GitHub.

## Required input

- A user-supplied tagged release package or extracted release directory.
- A chosen private Drive root.
- Direct user answers for household structure, timezone, source scope, delivery destinations, and selected integrations.

## Procedure

1. Read the supplied package's `START-HERE.md` and `release.yaml`.
2. Confirm the package is a tagged release asset, not an unpinned working branch. Record the observed version and assurance level.
3. Collect integration choices before capability preflight; never infer a provider from visible connectors.
4. Probe the selected runtime, Drive, mail, task, scheduler, and optional audio capabilities.
5. Create the private Drive layout and copy the selected release under `system/releases/<version>/`.
6. Read back every installed managed file and record the installed file map.
7. Create private configuration from the templates. Discover every Drive/provider ID through actual tool results.
8. Create initial private state and a stable bootstrap referring to the instance manifest.
9. Run a no-send/no-external-write validation on bounded synthetic or user-approved real inputs.
10. Present the capability and validation report. Only after explicit approval may the agent import history, synchronize external tasks, send a test brief, or enable a schedule.

## Output

Write an onboarding result to private state with the installed version, capability outcomes, created IDs, declared degraded features, and validation status. Do not place private IDs or report content in this repository.
