# Capability contract

A runtime may execute an operation only when its selected adapters declare every capability required by that operation.

## Capability declaration

Each adapter reports:

| Field | Meaning |
|---|---|
| `capability_id` | Stable logical capability name |
| `status` | `available`, `unavailable`, or `unknown` |
| `verification` | Actual observation or probe that established the status |
| `limits` | Relevant size, page, pagination, duration, or rate limits |
| `degradation` | Allowed behavior when unavailable |

Capabilities are facts about a runtime/provider combination, not a source of business policy.

## Core capability families

```text
storage.scoped_list
storage.read_complete
storage.create_file
storage.replace_verified
storage.get_metadata
storage.copy_verified
storage.restore_verified

release.read_package
release.verify_sha256
release.verify_inventory
release.verify_source_identity

coordination.ensure_idle

mail.search
mail.read_complete_message
mail.read_complete_thread
mail.list_attachments
mail.read_attachment
mail.send
mail.verify_send

tasks.list_complete
tasks.read_identity
tasks.discover_configuration
tasks.list_completed
tasks.read_activity
tasks.read_comments
tasks.create
tasks.update
tasks.move
tasks.complete
tasks.reopen
tasks.write_comment
tasks.verify

scheduler.ensure
scheduler.inspect
scheduler.disable
scheduler.verify

audio.generate
audio.retrieve
```

Release and upgrade operations use the `release.*` capabilities to read the supplied package, verify its archive checksum and complete payload inventory, and establish that its immutable tag, commit, version, and release status agree. `storage.copy_verified` is required to stage or back up files with readback evidence; `storage.restore_verified` is required before an operation may promise automatic rollback. `coordination.ensure_idle` is required before an upgrade can cross its first private-write gate.

The `coordination.ensure_idle` capability entry and private upgrade journal together declare exactly one coordination mode without adding a private-state schema field. `native_conditional` means the storage adapter exposes a provider generation/revision precondition that is atomically bound to replace and restore calls. `supervised_operational_single_writer` is permitted only for a bounded attended upgrade when every mutating schedule is verified paused or disabled, one actor is identified, all other direct and automated mutators are explicitly excluded, and the storage surface can fetch complete bytes, compute SHA-256, read `modified_time`, create new exact-ID backup/checkpoint objects, replace an exact target file ID, and immediately read it back. The fallback records version evidence as the exact target file ID plus `modified_time` plus SHA-256 of the complete bytes; it does not claim provider-level conditional-write capability. The operation must stop if the exclusive guard or any evidence becomes unknown.

The selected operation recipe declares which capabilities are required and which are optional. Missing required capability stops before side effects. Missing optional capability produces the recipe's documented degraded result.

## Capability profile

Onboarding writes an observed capability profile to the private instance state. It records no secrets and no private source content. The conformance unit is the exact runtime, provider, authorization, and execution surface. Interactive evidence cannot authorize scheduled execution. A runtime must recheck capabilities when authentication, provider configuration, adapter version, execution surface, or selected model/effort changes.
