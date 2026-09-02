# Manual-first installation

This is the required baseline installation route. It does not assume that the agent can connect to GitHub.

## User supplies the package

1. Download a tagged School-OS release asset from GitHub.
2. Share the release package with the agent.
3. If the agent cannot expand archives, extract the release first and place the extracted release folder in the target Google Drive or otherwise make every package file readable to the agent.
4. Tell the agent the target Drive root and that it should run the onboarding operation.

The agent must reject an unpinned branch/archive as an install source.

## Agent installation

The agent follows `core/operations/onboarding.md` from the supplied release:

1. Reads `START-HERE.md` and `release.yaml`.
2. Collects selected integration choices.
3. Validates the actual capability profile.
4. Creates the private Drive instance and copies the release into its versioned `system/` area.
5. Creates private configuration and state from templates.
6. Runs a no-send validation.
7. Waits for approval before initial import, external sync, delivery, or scheduling.

## Recurring operation

After successful installation, the scheduler receives only the stable private Drive bootstrap reference and operation name. It runs from the installed Drive release and does not need GitHub access.
