# Migration 0001 — add atomic Fact references to rolling updates

## Purpose

Upgrade a legacy rolling-update stream whose bullets retain only a source record or thread identifier. The canonical format must retain both the source identifier used for the human-facing source link and the exact atomic Fact ID or IDs that support the bullet.

This migration is deterministic and fail-closed. It never asks a model to guess semantic similarity.

## Legacy and target forms

Legacy:

```text
- {Entity}: {Fact text} [TID:{source_id}]
```

Target:

```text
- {Entity}: {Fact text} [TID:{source_id}] [Facts:{fact_id[,fact_id...]}]
```

Source identifiers are opaque strings. Do not assume a Gmail-specific shape.

## Preflight

1. Read the complete rolling stream, source-catalog index, referenced source records, private file map, and current data schema version.
2. Create and verify a private backup of the rolling stream.
3. Stop if any legacy bullet lacks a received-day heading, entity scope, source identifier, or text.
4. A target-form bullet is idempotently skipped only after all existing Fact references validate.

## Mechanical mapping algorithm

For each legacy bullet, in file order:

1. Resolve its source record from the catalog's stored source identifiers, never from filename resemblance alone.
2. Select catalog facts whose source identifier matches the bullet, `is_update=true`, `is_guideline=false`, and `is_action=false`.
3. Require the fact's local received date to equal the bullet's enclosing received-day heading and its entity scope to match the bullet scope.
4. Normalize only Markdown presentation wrappers and whitespace. A legacy source row may prefix displayed Fact text with its own backticked Fact ID followed by a colon; remove that prefix before comparison. Do not rewrite words or punctuation.
5. Match the bullet text to candidate Fact text exactly after that normalization.
6. If exactly one candidate matches, append its stable Fact ID in the target form.
7. If zero or multiple candidates match, stop the migration and write a private exception record containing the bullet location, source identifier, and candidate Fact IDs. A human or explicitly authorized migration mapping must resolve the exception; the agent must not infer a match.

## Verification

Before replacing the private rolling stream, verify all of the following:

- bullet count, order, received-day headings, scopes, visible text, and source identifiers are unchanged;
- every bullet has at least one Fact reference;
- every referenced Fact exists in the referenced source record;
- every referenced Fact passes the update/guideline/action filters above;
- no Fact ID was invented, changed, or renumbered; and
- readback of the migrated file matches the composed target byte-for-byte or through the instance's declared verified-replacement method.

On any failure, leave the original rolling stream active and record the migration as blocked.

