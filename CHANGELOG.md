# Changelog

## 0.1.0-alpha.2 — release candidate

- Corrected the release manifest/schema contract so the packaged manifest is installable and schema-valid.
- Added deterministic migration of legacy rolling updates from source-only provenance to atomic Fact references.
- Added synthetic migration input and expected-output fixtures.
- Required tag, commit, manifest version, and released status agreement during existing-instance migration.

## 0.1.0-alpha.1 — non-installable packaging dry run

- Published tag pointed to a manifest that still declared `0.1.0-dev` and `unreleased`; installers must reject it.

## Unreleased foundation

- Established generic GitHub/Drive separation architecture.
- Added manual-first installation and Drive-hosted runtime model.
- Added provider-neutral source-catalog, task, capability, adapter, and release contracts.
- Added reference templates for Gmail, Todoist, ChatGPT Work, Claude, scheduler, and optional audio integration.
- Added synthetic fixtures and privacy boundaries.

