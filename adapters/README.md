# Adapters

Adapters connect generic School-OS operations to a specific runtime/provider/auth combination.

An adapter is selected only through private instance configuration. It must not contain a household name, account, project ID, recipient, source domain, credential, or task binding.

## Layout

- `runtimes/` — runtime capability and tool mapping.
- `mail/` — source/discovery/delivery mapping.
- `tasks/` — parent task-provider mapping.
- `schedulers/` — recurring execution mapping.
- `audio/` — optional speech-generation mapping.

An adapter is supported only after it passes the relevant contract/fixture checks for its actual runtime/provider/auth profile.
