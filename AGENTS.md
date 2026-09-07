# Agent instructions

Read [START-HERE.md](START-HERE.md) before working in this repository.

## Development continuity

School-OS development must remain independent of any particular coding agent, vendor, local workspace, or conversation. GitHub is the durable shared state from which another agent must be able to resume the work.

For every accepted repository change:

1. Run the validation appropriate to the change, including the privacy scan before publishing.
2. Commit all and only the accepted, in-scope files with a descriptive commit message.
3. Push the commit to the repository's intended GitHub branch.
4. Verify that the remote branch resolves to the pushed commit before reporting the work complete.

Never leave accepted work only in an agent's local working tree or in an unpushed commit. Never publish private-instance data, credentials, or unrelated user changes. If GitHub authentication, authorization, validation, or the push fails, report the work as incomplete with the exact blocker and preserve the local changes for recovery.
