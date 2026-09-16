# D8 — Package and upgrade management are deferred

Updated 2026-09-15 to record the user's MVP scope decision. D8's packaged
installation, version management, upgrades, migrations, compatibility machinery
and extension manager are **outside the MVP**. They are no longer pending
prerequisites for the current implementation. The
[active plan](../../PLAN.md) records this explicit reduction from the broader
[product direction](../../../../product-principles.md).

The earlier ZIP, release-manifest, staged-version and activation proposals are
historical design context. They must not be implemented by treating them as
already approved or necessary consequences of the Drive layout.

## The approved Drive separation remains

D1 already separates `system`, `instance` and `extensions` beneath a readable
Drive entry point, with bounded JSON pages and directories. That physical
separation stays approved and leaves room for future package and extension
support. It does not require the MVP to build the deferred management features.

| Area | Meaning retained from D1 |
|---|---|
| `system` | School-OS instructions and supporting system material. |
| `instance` | Private configuration, processed knowledge, tasks, source indexes, coverage and in-scope operating state. |
| `extensions` | Separation reserved for user additions and future extension support. |

This scope update chooses no new folder schema, release pin, activation protocol
or installer. It also does not turn the approved `extensions` area into an
automatic compatibility or upgrade service. Preserving room for a future
feature is different from delivering that feature now.

## First use follows the approved separation

The MVP still needs a usable Drive instance. For example, a parent who asks an
agent to catalog fictional Juniper School mail must be able to identify the
Drive starting point, configure the relevant source account and school scope,
and save the resulting knowledge and coverage.

Those needs remain as agent/tool operations under approved D1 instructions.
The user has excluded the separate records/ordinary-save framework as an MVP
deliverable or gate. Do not recreate a ZIP installer, manifest, version selector
or general writer under the label of minimum setup. Preserve the existing
approved layout, data meanings and normal verification; surface any specific
new architectural choice if one is actually needed.

The parent should eventually receive a clear account of what was configured
and what remains unavailable. This brief does not invent a setup-complete
message or declare an instance ready before the procedure is agreed and its
required work is actually done.

Raw emails and attachments remain at their sources. Only temporary processing
copies are used, then discarded after verified persistence. Private information
and credentials do not belong in the reusable repository. The approved agent
small Python standard-library helper direction remains; other work belongs to
the agent and tools. New architectural dependencies still need specific approval.

## What the MVP will not claim

The project will not claim a supported packaged install/update journey,
automatic version selection, migration from retired instances, compatibility
checking across releases, or preservation performed by an extension manager.
It will not promise staged activation, rollback or repair of an interrupted
upgrade. These are deferred capabilities, not completed features awaiting only
testing.

D2 interrupted canonical-write recovery remains outside the MVP as well.
Normal save verification and honest incomplete status still matter for the
in-scope operations. Deferring installation machinery does not justify claiming
that partially saved setup or processed data is complete.

For a future “Friday lunch list” addition, the existing separation can keep its
files distinct from official material. That alone does not establish a supported
extension contract, upgrade compatibility or migration path. Any later mechanism
requires its own explicit architecture approval.

## Repository preservation is still required

This deferral concerns product features, not permission to lose the existing
project or its evidence. Preserve the repository and Git history, current
principles, approved design, continuity documents and applicable privacy rules.
Preserve frozen studies and their executable/result bytes.

The pre-cleanup baseline is tag `restart-baseline-2026-09-14`, targeting
`39d752c364a1cf404e5a6fc5739148b7d35a6b35`. The coordinator owns its publication
and remote verification. Retiring obsolete project code must protect unrelated
work and prevent old operating instructions from being selected as the new
foundation. It does not migrate or erase a private installed instance.

The agreed implementation still requires the repository handoff: inspect hooks
and CI, perform permitted publication hygiene, commit and push accepted code
and continuity, verify the remote revision, then stop for the user's testing
direction. Package deferral does not waive those development obligations.
This update authorizes no build, installation, migration, test or live effect.
