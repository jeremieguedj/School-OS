# School-OS fresh setup bundle

This bundle is a fresh, unconfigured School-OS starter built from source revision
`{{SOURCE_REVISION}}`. It contains no household information, credentials,
canonical record IDs, configuration, or ingested school data.

Read [START-HERE.md](START-HERE.md) and [AGENTS.md](AGENTS.md), then determine
whether `instance/` contains the verified configuration and readable bootstrap
of a configured instance. If it does not and the parent asks to “setup my
schoolOS,” follow the dedicated
[School-OS setup instructions](system/operations/setup.md). If the instance is
already configured, follow [startup](system/operations/startup.md) and select the
parent's current requested operation. Do not rerun setup merely because these
consumer root files remain present.

Treat this supplied bundle as the source for first setup. Do not search an
ambient development repository, reuse another agent's transcript or copy an
earlier instance to fill its empty private areas. If unrelated context is already
visible, keep it out of setup and disclose that limit when setup is being used to
evaluate fresh one-link discovery.

The bundle has the approved three areas:

- `system/` contains the pinned reusable product instructions, contracts,
  helpers, and supplied semantic adapters.
- `instance/` is intentionally empty until setup creates the parent's private
  configuration and canonical data.
- `extensions/` is intentionally empty until the household adds a compatible
  recipe or semantic adapter.

Access to this bundle is not access to a mailbox, task tool, delivery service,
or private Drive destination. Setup, ingestion, and outbound effects remain
separately authorized operations. Revision-pinned development references that
appear in system material are optional background links and are not setup inputs.

During first setup, the root `START-HERE.md` becomes the readable configured
bootstrap required by the storage procedure. The reusable `system/` material
stays pinned while `instance/` and compatible `extensions/` become private
instance state.
