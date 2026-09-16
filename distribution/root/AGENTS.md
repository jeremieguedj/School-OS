# Agent instructions for a fresh School-OS setup

First inspect whether this root resolves to a verified canonical instance
configuration and readable bootstrap. When it does not and the parent asks to
“setup my schoolOS,” select the first-setup operation and follow the authoritative
[setup instructions](system/operations/setup.md), the product
[principles](system/docs/product-principles.md), and the exact dependencies that
setup declares. Do not duplicate or replace that procedure from memory.

When the instance is configured, do not rerun first setup merely because the
consumer root files remain. Follow [startup](system/operations/startup.md) and
select the parent's current requested operation from the installed instructions
and verified instance state. Missing or unreadable configuration in a previously
used location is not proof of a fresh instance; preserve it and report the
uncertainty instead of overwriting or resetting it.

Before first setup, treat `system/` as pinned reusable material and the empty
private areas as unconfigured. Create household configuration and canonical data
only under the parent-selected private `instance/` destination, and place
compatible household-authored additions in `extensions/` as the setup procedure
directs. Do not alter official `system/` material during private setup.

The bundle link authorizes reading the supplied material. It does not authorize
mailbox ingestion, task-application writes, outbound messages or audio,
schedules, or other external effects. While the instance is unconfigured,
perform only setup until the parent separately requests another operation. Once
configured, the parent's current request and the selected installed operation
govern authority. Keep credentials out of School-OS files, preserve unknown
capabilities honestly, and verify every persisted setup value through actual
readback before reporting setup complete.

Revision-pinned public development references in the system material are
optional context only. They are not required setup inputs and must not replace
the bundled operating instructions.
