---
schema_version: 1
timezone: REPLACE_WITH_IANA_TIMEZONE
references:
  source_checkpoint:
    object_id: REPLACE_WITH_PRIVATE_REFERENCE
    kind: file
    permitted_ancestor_id: REPLACE_WITH_PRIVATE_INSTANCE_ROOT
  source_catalog_folder:
    object_id: REPLACE_WITH_PRIVATE_REFERENCE
    kind: folder
    permitted_ancestor_id: REPLACE_WITH_PRIVATE_INSTANCE_ROOT
  source_catalog_index:
    object_id: REPLACE_WITH_PRIVATE_REFERENCE
    kind: file
    permitted_ancestor_id: REPLACE_WITH_PRIVATE_INSTANCE_ROOT
  canonical_action_register:
    object_id: REPLACE_WITH_PRIVATE_REFERENCE
    kind: file
    permitted_ancestor_id: REPLACE_WITH_PRIVATE_INSTANCE_ROOT
  guidelines:
    object_id: REPLACE_WITH_PRIVATE_REFERENCE
    kind: file
    permitted_ancestor_id: REPLACE_WITH_PRIVATE_INSTANCE_ROOT
  rolling_updates:
    object_id: REPLACE_WITH_PRIVATE_REFERENCE
    kind: file
    permitted_ancestor_id: REPLACE_WITH_PRIVATE_INSTANCE_ROOT
  brief_template:
    object_id: REPLACE_WITH_PRIVATE_REFERENCE
    kind: file
    permitted_ancestor_id: REPLACE_WITH_PRIVATE_INSTANCE_ROOT
  delivery_state:
    object_id: REPLACE_WITH_PRIVATE_REFERENCE
    kind: file
    permitted_ancestor_id: REPLACE_WITH_PRIVATE_INSTANCE_ROOT
  final_run_checkpoint:
    object_id: REPLACE_WITH_PRIVATE_REFERENCE
    kind: file
    permitted_ancestor_id: REPLACE_WITH_PRIVATE_INSTANCE_ROOT
  runtime_profile:
    object_id: REPLACE_WITH_PRIVATE_REFERENCE
    kind: file
    permitted_ancestor_id: REPLACE_WITH_PRIVATE_INSTANCE_ROOT
presentation:
  brief_heading: REPLACE_WITH_SUPPORTED_BRIEF_HEADING
---

# Daily Run Personal Values

This is the private companion to the generic `daily-run.md` operation. Populate
it only with household-specific values, exact private references, and supported
presentation choices. Do not place adapter identities, provider bindings,
credentials, or a replacement operation recipe here.

The required machine-readable values and exact private references are the YAML
front matter above. The explanatory prose below does not override them.

## Approved customization boundary

These values may customize source scope, household grouping, ordering, and
presentation only where the generic operation explicitly permits it. They may
not override source-backed fact requirements, task reconciliation, provider
readback, duplicate-delivery prevention, or sent-message verification.

The generic daily operation compares the front-matter runtime-profile reference
with the runtime configuration before side effects. A mismatch requires setup or
health validation; it is not resolved by changing this document's prose.
