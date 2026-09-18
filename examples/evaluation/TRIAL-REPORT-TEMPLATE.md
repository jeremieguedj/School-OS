# School-OS isolated trial report

Status: `[implemented | exercised | passed | failed | incomplete | unexercised]`

## Bound implementation and route

- Published starter revision and identical-asset evidence: `[privacy-safe revision and result]`
- Route and access method: `[route]`
- Agent task/session alias: `[private alias, not provider ID]`
- Assigned Drive instance alias and confinement result: `[privacy-safe result]`
- Source interval and exhaustion evidence: `[private binding plus sanitized result]`
- Round-manifest/oracle byte binding: `[exact digest match/rejected/unknown]`
- Half-open interval: `[start-inclusive/end-exclusive, timezone, precision]`
- Comparable arrival timestamps and local boundary filter: `[verified/failed/unknown]`
- Canonical 64 KiB contract used: `[yes/no/unknown]`

## Achieved isolation

- Controller: `[private alias]`
- Conversation/session: `[separate/contaminated/unknown]`
- Tab use: `[separate and serial/other]`
- Browser profile: `existing signed-in Chrome profile shared across browser routes`
- Shared state disclosed: `[cookies, signed-in provider account, other account state, unknowns]`
- Separate boundaries: `[Drive instance, evidence directory, controller context]`
- Cross-route output transfer observed: `[none/describe]`
- Claim limit: do not claim account-level or provider-memory isolation.

## Controller observations and follow-up guard

- Exact expected binding: `[provider/task/conversation/route/root aliases plus stage]`
- Composer at each follow-up: `[bound task/top level/unknown]`
- Follow-up guard result: `[authorized/blocked and privacy-safe reason]`
- Current controller state: `[active/awaiting_user_input/completed/approval_blocked_before_delivery/dispatched_unknown_effect/controller_observation_unavailable]`
- Earlier running snapshot superseded by later final response: `[yes/no/not applicable]`
- Initial launch dispatch/effect evidence: `[proven no dispatch and no effect/unknown/dispatched]`
- One separately tracked no-dispatch retry: `[unused/used once/blocked]`
- Exact opening-message digest matched for initial and retry: `[yes/no/not applicable]`

A mismatched route, root, task, conversation, provider or stage blocks the
follow-up. A top-level or unverified composer also blocks it. Do not turn a
controller observation gap into a tested-agent failure.

## Evidence-capture preflight

- Private sink: `[ready/failed]`
- Owner-only directory and mode-0600 receipt readback: `[verified/failed]`
- First provider dispatch occurred only after successful preflight: `[yes/no]`
- Dispatch / provider response / receipt persistence states: `[separate sanitized summary]`
- Private receipt inventory: `[private path supplied only through an authorized channel]`

## Pre-dispatch call-schema gate

| Stage / operation alias | Exact signature observed | Argument names/types valid | Exclusive locator groups valid | Dispatch blocked if invalid | Result / diagnostic codes |
|---|---:|---:|---:|---:|---|
| `[privacy-safe alias]` | | | | | |

Record an invalid proposed call as local validation. Do not count it as provider
dispatch, provider rejection or transport failure.

## Independent setup gate

- Immutable starter bytes/revision independently verified: `[yes/no]`
- Installation expectation derived by evaluator from that starter: `[yes/no]`
- Expected root documents / `system/` files: `[privacy-safe counts]`
- Every expected installed target read completely: `[yes/no; missing count]`
- Saved bytes and ancestry through selected root preserved: `[yes/no/insufficient]`
- Exact intended configured `START-HERE.md` bytes preserved privately: `[yes/no]`
- Phase-two expectation substitutes only those exact entrypoint bytes: `[yes/no]`
- Complete saved configured entrypoint read back: `[yes/no]`
- Saved entrypoint exactly matches intended configured bytes: `[yes/no/insufficient]`
- Installation-material result: `[valid/invalid/insufficient_evidence]`
- Installation-material diagnostics: `[privacy-safe counts and codes]`
- Manifest derived only from complete saved `START-HERE.md`: `[yes/no]`
- Visible role / root page ID / family / route-scope fields complete: `[yes/no; missing counts]`
- Entrypoint-to-manifest derivation result: `[valid/insufficient_evidence]`
- Bootstrap inputs use that exact derived manifest: `[yes/no]`
- Bootstrap result: `[valid/invalid/insufficient_evidence]`
- Bootstrap diagnostics: `[privacy-safe counts and codes]`
- Tested-agent self-report used as any evaluator gate result: `[must be no]`
- Combined setup gate: `[passed/failed/incomplete]`
- Ingestion request withheld unless all three results were valid: `[yes/no/not applicable]`

`passed` requires installation materials, entrypoint derivation and bootstrap to
be `valid`. Any `invalid` result makes the gate `failed`; otherwise any
`insufficient_evidence` result makes it `incomplete`. Keep all three gates and
their evidence separate.

## Saved-state and reference audit

- Audit roots: `[configuration and approved bootstrap roles, privately bound]`
- Pages visited / unresolved: `[counts]`
- Continuations exhausted: `[yes/no/unknown]`
- Nested bucket references followed: `[yes/no/not present]`
- Duplicate/conflicting IDs and cycles: `[counts and privacy-safe classification]`
- Unknown required shapes: `[count/status]`
- Audit conclusion: `[complete/incomplete; never substitute empty for unknown]`

## Semantic comparison

- Source expectation binding: `[private receipt hashes and reviewer/time binding]`
- Saved Knowledge and Task comparison: `[pass/fail/incomplete]`
- Missing, merged, duplicate, overbroad or unsupported meaning: `[sanitized findings]`
- Finite, conditional and recurring dispositions: `[result]`
- Completion units and scope: `[result]`
- Zero-action sources: `[source-grounded justification or not applicable]`

## Source-oracle preflight

- Exact private round-manifest bytes preserved: `[yes/no]`
- Manifest digest matches oracle binding: `[yes/no]`
- Exact private source-input bytes preserved: `[yes/no]`
- Source-input digest matches oracle binding: `[yes/no]`
- Required private query aliases / observed independent chains: `[counts only]`
- Missing, duplicate or unexpected query aliases: `[counts and status]`
- Every chain starts with null and has continuous request/next tokens: `[yes/no]`
- Every enumeration page's exact receipt digest verified: `[yes/no; count]`
- Every chain ends with an observed null next token: `[yes/no]`
- Oracle interval exactly matches `[start,end)`, timezone and precision: `[yes/no]`
- Every candidate has a supported comparable arrival/received timestamp: `[yes/no]`
- Local half-open filter applied: `[yes/no; in-scope/excluded counts only]`
- Reuse attempted for another manifest, source input or interval: `[no/rejected/incorrectly allowed]`
- Preflight conclusion: `[ready/rejected; sanitized reason]`
- Proof limit: `[receipt integrity and recorded token chain only; provider completeness remains a separate claim]`

## Report/export provenance

| Artifact used | Evidence strength | Same-task final response | Export observed | Receipt saved | Exact bytes bound | Limitation |
|---|---|---:|---:|---:|---:|---|
| `[artifact alias]` | `[task-bound / visible-output-only / unbound]` | | | | | |

- Export receipt carries expected artifact SHA-256: `[yes/no]`
- Export receipt carries expected artifact byte count: `[yes/no]`
- Receipt, artifact metadata and downloaded bytes all agree: `[yes/no]`
- Missing or mismatched exact binding downgraded to visible-output-only: `[yes/no/not applicable]`

Canonical Drive readback and independent source evidence remain primary. A
same-name local file or a receipt with no exact digest-and-length binding is not
evidence of the tested task's downloaded artifact.

## Visual expectations

| Private artifact alias | Pixels/rendering reviewed | Portion reviewed | Expectation authored first | OCR label | Result |
|---|---|---|---:|---|---|
| `[alias]` | `[exact pixels / faithful rendering / unavailable]` | | | `[derived/not used]` | `[grounded/evaluation limitation]` |

Remove unsupported image-specific expectations when the pixels were not visible;
retain other independently grounded findings.

## 64 KiB evaluation

Canonical pages retain the 65,536-byte maximum. Comparison pages are private,
noncanonical, use the same ordered successfully saved records, and are not
connected to the bootstrap, directories, or indexes.

| Candidate | Actually written and read to exact end | Pages | Largest page bytes | Complete records reconstructed | Query pages/bytes | Visible tokens/cost | Result |
|---:|---:|---:|---:|---:|---|---|---|
| 64 KiB | | | | | | `[observed/unknown]` | |
| 128 KiB | | | | | | `[observed/unknown]` | |
| 256 KiB | | | | | | `[observed/unknown]` | |

- Whole records above 64/128 KiB: `[counts and privacy-safe aggregates]`
- Canonical overflow blockers: `[observed exact required bytes or none observed]`
- Near-limit rollover preserved every record whole: `[yes/no/unexercised]`
- Filtering before model context: `[observed behavior/unknown]`
- Keep/change recommendation: `[retain 64 KiB unless repeated observed evidence supports a shared-limit change]`

## Final result and limits

Report product behavior, evaluator failures, route limitations, unknown effects,
and unexercised capabilities separately. Do not infer broad vendor compatibility
or successful retrieval from an unexecuted or incomplete comparison.
