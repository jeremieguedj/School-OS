# Temporary body-only source policy

Status: local implementation and validation complete; awaiting explicit user
approval for any package build, fresh installation, or live provider call.

This focused plan temporarily removes attachment and directly referenced binary
content from the recovery MVP's configured ingestion scope. It does not delete
the existing attachment, PDF, image, or direct-resource implementation. Those
paths remain dormant until a later source policy defines which content is useful
and how stable provider locators are mapped to canonical source identities.

## Active behavior

For the temporary body-only policy:

1. Gmail full/raw reads and deterministic MIME accounting remain required. The
   exact raw RFC2822 message remains source-custody evidence; it may physically
   contain encoded attachment bytes because Gmail's raw-message representation
   is indivisible.
2. Every non-body MIME leaf is represented by an `excluded_by_policy` outcome
   whose canonical identity is derived from the immutable source message and
   normalized MIME-part coordinate. A connector attachment ID is only a
   transient read locator and is neither required nor persisted in this mode.
3. No attachment endpoint is called. No attachment is downloaded separately,
   extracted, interpreted, emitted as a Fact, or copied into a dedicated
   attachment member in the source bundle.
4. Direct HTML image and PDF references may still be deterministically
   inventoried from the admitted HTML evidence, but both `html_embedded` and
   `html_linked` origins terminate as `excluded_by_policy` before any HTTP fetch
   or extractor call.
5. Admitted plaintext bodies and substantive MIME text bodies retain the
   existing exact-byte custody, semantic interpretation, audit, Fact, task, and
   brief behavior. A message containing no admissible body produces no inferred
   attachment content.

The policy reason is one fixed repository constant. A wildcard MIME exclusion
must cover every syntactically valid attachment MIME type, including types not
seen in fixtures. Unknown MIME structure, conflicting full/raw evidence,
malformed source identity, incomplete pagination, or failed body admission still
blocks; attachment deferral is not a general permissiveness switch.

## Local implementation order

1. Add an explicit body-only mode to Gmail normalization. Preserve the existing
   attachment-processing mode and its tests, but make both active connected
   composers select body-only mode.
2. Give excluded MIME leaves stable message-plus-part identities and remove any
   dependency on the connector's attachment ID from normalized/canonical output.
3. Extend the existing attachment exclusion matcher with the single global
   `*/*` policy and bind no active attachment extractor in body-only composition.
4. Exclude both finite direct-resource origins before fetch and bind no active
   resource extractor in body-only composition.
5. Update source policy documentation and recovery acceptance language so
   `excluded_by_policy` is the complete disposition for attachments and direct
   resources during this temporary phase.

## Required local proof

- Replay the ignored exact private Gmail evidence locally and prove that changing
  only the transient connector attachment ID cannot change body-only normalized
  or catalog bytes.
- Test text, PDF, image, and an unfamiliar MIME attachment. Every case must be
  excluded without invoking the attachment read callback.
- Test embedded-image and linked-PDF HTML references. Both must be excluded
  without invoking network fetch or extraction callbacks.
- Prove admitted body text still reaches deterministic catalog and semantic
  inputs, while attachment text never appears in semantic input or Facts.
- Preserve fail-closed tests for malformed full/raw MIME evidence and retain the
  existing attachment/PDF/image tests as dormant-path coverage.
- Run focused source/ingestion tests and the complete repository validation
  locally.

## Approval boundary after local proof

This work unit ends after code, documentation, private exact-receipt replay, and
local tests pass. It must not build a release package, create or reuse a test
root, install anything, or call Google, Todoist, ElevenLabs, email, or scheduler
surfaces. A later fresh package/install/live run begins only after explicit user
approval.
