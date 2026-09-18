# Start here

Read [AGENTS.md](AGENTS.md), then establish this root's actual state. A fresh
starter has no verified canonical configuration or instance ID in `instance/`.
For that state, perform the parent's setup request through the dedicated
[first-setup operation](system/operations/setup.md) and only the dependencies it
declares. Setup updates this file into the readable configured bootstrap required
by the [storage procedure](system/operations/storage.md#bootstrap-an-instance).

When this root already resolves to a verified instance configuration and its
required bootstrap roles, follow [startup](system/operations/startup.md), select
the parent's current requested operation, and use the configured instance state.
Do not force a configured instance through first setup again merely because its
root began as this starter.

The installed product authority is
[system/docs/product-principles.md](system/docs/product-principles.md). Reusable
material belongs in `system/`; private configuration and canonical data created
during setup belong in `instance/`; compatible household additions belong in
`extensions/`.

Do not infer mailbox access, ingestion permission, delivery permission, or task
application write authority from the bundle link or from the request to set up
School-OS. Do not use repository history or optional development references as
household facts or required setup inputs. Use this supplied bundle as the setup
source; do not preload another School-OS conversation, development checkout or
existing instance into a fresh setup.
