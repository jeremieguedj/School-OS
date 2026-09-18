# School-OS

School-OS gives a capable agent shared instructions and a canonical Google Drive
knowledge base for a household's school communications, tasks and briefs.
Original emails and attachments stay at their source; saved knowledge retains
source links, scope, dates and qualifications.

## Set up a fresh School-OS

[Download the clean round-two starter ZIP](https://github.com/jeremieguedj/School-OS/releases/download/school-os-starter-2026-09-17-round-2/School-OS-setup-round-2.zip)
from the dedicated unqualified prerelease. Use this asset, not the repository
source-code archive.

Give a new agent session one accessible link to the fresh School-OS ZIP or folder
and say only: **“setup my schoolOS.”** The agent starts with
[START-HERE.md](START-HERE.md), reads [AGENTS.md](AGENTS.md), and follows the one
authoritative [setup procedure](operations/setup.md). In a distributed starter,
that procedure is at `system/operations/setup.md`. A fresh-setup evaluation must
start outside this development repository and without a prior School-OS
conversation; otherwise it does not establish discovery from the starter alone.

The fresh starter has reusable operating material plus empty `instance/` and
`extensions/` areas. It contains no configured household, canonical IDs or
ingested school data. Sharing its link supplies neither credentials nor permission
to ingest mail, update tasks, send messages or create schedules. The setup
procedure interviews the parent, shows the tools that agent can actually offer,
then saves and verifies only the approved configuration and canonical bootstrap.

If this is already a configured private instance, use its readable entry point
and [startup procedure](operations/startup.md); preserve its configuration, data
and extensions.

## Repository development

The [operation guide](operations/README.md) contains the reusable instructions.
[Product principles](docs/product-principles.md) and the
[approved restart plan](docs/plans/restart/PLAN.md) govern development of this
repository, not a parent's ordinary setup session.

**Status:** the approved restart MVP and second-round T01–T19 remediation are
implemented in source and published from exact commit
`aae44ef13be8392130f9b5aec7889b040c0ca45b`. Deterministic local checks pass.
The three fresh-agent retests ended with 0/3 setup gates passed, so ingestion and
query stages did not run; see the
[round-two results](docs/plans/restart/ROUND-2-TRIAL-RESULTS.md). The retired
implementation is not the foundation of this project. No provider compatibility
claim is made from source or local checks alone.

## Current project material

- `operations/`: agent procedures for setup, ingestion, knowledge, tasks and briefs.
- `helpers/`: the approved small Python standard-library routines.
- `docs/product-principles.md`: product authority.
- `docs/plans/restart/`: approved design, continuity and historical evidence.
- `scripts/privacy_scan.py`: independent development publication hygiene.

Drive instances separate `system`, `instance` and `extensions`. Canonical data uses
bounded JSON pages and owned IDs; provider handles only aid access. The current
shared maximum is 64 KiB per encoded page. Pages roll over between complete
records; fields are not split into linked storage. Evidence from the later
authorized trials may support changing the shared maximum without changing IDs,
adding instance configuration or rewriting valid smaller pages. Agents use shared
semantic adapters through their own connectors. No dedicated computer, persistent
local runtime, coding CLI or central scheduler is required.

The MVP includes the distributable fresh starter and discoverable agent-led setup.
It defers generic interrupted-write repair, centralized jobs management, and
automated upgrades, migrations, compatibility handling and release management.
Users and agents operate nonconcurrently on the same Drive data. See the
[coverage map](docs/plans/restart/implementation/COVERAGE.md) for retained versus
deferred scope.

## Preserved history

The [OrgoS Restart Documentation snapshot](https://github.com/jeremieguedj/School-OS/releases/tag/orgos-restart-documentation)
fixes the approved documentation and the complete pre-cleanup tracked tree at
`09f6be151cd549431343b9ebe44a1d03371d2f4f`. Legacy code, schemas, installers, adapters
and validation workflow are recoverable there and in Git history. The earlier
`restart-baseline-2026-09-14` tag also remains intact. Frozen restart studies retain
their original code and results and are not active operating recipes.

Development stays in this repository on `codex/restart-implementation`. Only
current instructions are offered to new instance agents. Private household data,
provider receipts and credentials must never be committed.
