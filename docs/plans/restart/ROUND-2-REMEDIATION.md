# Approved second-round remediation

Status: implemented in source on 2026-09-17; local deterministic checks passed.
Publication and the three fresh-agent trials are tracked in the active
[plan](PLAN.md) and [progress log](../../../PROGRESS.md). This document records
the cohesive implementation and does not replace first-round evidence in
[trial results](TRIAL-RESULTS.md) or the [root-cause review](ROOT-CAUSE-REVIEW.md).

## Architecture boundaries retained

- Drive remains canonical. No database, cache, queue, scheduler, lock, recovery
  journal or second-model judge was added.
- Pages retain one 65,536-byte maximum and complete records. A larger limit is
  considered only from observed evidence.
- Setup's finite expected-route manifest and bootstrap diagnostics are temporary;
  no catalogue-of-routes record or new family exists.
- A directly embedded substantive remote image may receive one authorized
  least-stateful read. Its meaning belongs to the parent Email body. Raw pixels
  are not retained and the locator never supplies identity.
- Generic interrupted-write recovery, centralized jobs and automated upgrades
  remain outside this MVP.

## Product and setup treatments

| Treatment | Implemented behavior | Primary files |
| --- | --- | --- |
| T01 | A pure helper validates exact saved bootstrap bytes against a caller-selected finite manifest and returns `valid`, `invalid` or `insufficient_evidence`. | `helpers/bootstrap_contract.py`, `operations/storage.md`, `operations/setup.md` |
| T02 | A temporary source checklist is compared with complete saved Knowledge and Tasks before whole-email completion. | `operations/semantic-review.md`, `contracts/data.md`, ingestion/extraction/knowledge recipes |
| T03 | Explicit guidance distinguishes information, optional guidance, finite/conditional/recurring action and independent completion units. | `contracts/data.md`, `operations/semantic-review.md`, `examples/remediation/README.md` |
| T04 | The semantic comparison checks every date's value and meaning separately. | Same semantic-review and fictional cases |
| T05 | Query guidance starts with bounded Entity/Topic/time/Task/coverage routes, reuses pages within the question and broadens only for a stated fallback reason. | `contracts/data.md`, existing `operations/query.md` |
| T06 | Material claims cite readable canonical/source locations; aggregate routing pages alone do not support a claim. | `contracts/data.md`, existing query procedure |
| T07 | Authorized substantive embedded images are processed as parent-body content; unavailable access keeps the Email incomplete. | `docs/product-principles.md`, `contracts/data.md`, semantic review and fictional case |
| T08 | A fresh setup uses only the supplied bundle and parent answers; inherited repository/conversation context is disclosed. | root and consumer entrypoints, setup docs |
| T09 | The agent interviews for desired outcomes before inspecting only relevant available connector routes. | `operations/setup.md`, adapter guidance |
| T10 | Every setup write verifies actual placement under the selected Drive root plus full saved content. | setup instructions and Drive adapter |
| T11 | Every route receives one immutable starter artifact; private evidence binds commit, digest, upload and link. | `docs/setup-bundle.md`, trial protocol |
| T12 | One identical launch retry is allowed only after evidence establishes no dispatch and no effect. | bundle/trial guidance |
| T13 | Listing completeness requires explicit provider exhaustion; otherwise only finite referenced targets may be verified and remaining inventory stays unknown. | Drive/adapter/setup/startup guidance |

## Evaluation treatments

| Treatment | Implemented behavior | Primary files |
| --- | --- | --- |
| T14 | Owner-only receipt-sink preflight, exclusive mode-0600 receipt saves and separate dispatch/provider/receipt states. | `helpers/trial_evaluation.py`, trial protocol |
| T15 | Read-only traversal follows current contract references, nested bucket page IDs and continuations; unknown shapes and unresolved required targets remain incomplete. | evaluator helper and fictional traversal case |
| T16 | Downloaded reports require a same-task prompt/final/export/receipt/byte chain; otherwise only visible output is graded. | evaluator helper, protocol and artifact case |
| T17 | Spark and Work use the existing signed-in Chrome profile, with separate conversations, controllers, serial tabs, Drive roots and evidence. Shared browser/account state is disclosed. | trial protocol, prompt handoff and report template |
| T18 | Image-specific expectations require independent review of the exact pixels or faithful private rendering before tested output. | evaluator helper, protocol and image case |
| T19 | Canonical pages stay at 64 KiB; evaluation can pack the same ordered records into marked private noncanonical 64/128/256 KiB pages without splitting records. | evaluator helper, protocol and near-limit case |

## Local validation performed

The following checks were executed after integration:

- 37 Python standard-library tests covering privacy scanning, metadata helpers,
  bootstrap validation and evaluator helpers: passed;
- compilation of current helper and build scripts with temporary bytecode cache:
  passed; and
- repository Markdown relative-link and whitespace checks: passed after excluding
  generated consumer-template paths whose links are resolved inside the ZIP.

These checks establish deterministic local behavior only. Agent, connector,
Drive and Gmail outcomes are established separately by the authorized trials.

## Publication and trial rule

Build the starter from the exact committed revision, verify its archive and
privacy properties, publish those immutable bytes, and give every route the same
Drive link. Once trial execution begins, do not repair product or instance defects.
Preserve evidence, continue only independent unaffected checks, publish the
privacy-safe comparison and return to the parent for review.
