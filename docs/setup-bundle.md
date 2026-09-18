# Fresh setup bundle

The fresh setup bundle is the publication artifact for the approved first-use
path. A parent gives a new agent session one agent-accessible ZIP or extracted
folder link and asks only, “setup my schoolOS.” The root consumer instructions
route the agent to the existing authoritative `system/operations/setup.md`.
They do not duplicate the setup procedure.

## Publication channel

The starter is published as [School-OS-setup.zip](https://github.com/jeremieguedj/School-OS/releases/download/school-os-starter-2026-09-16/School-OS-setup.zip)
on the dedicated [school-os-starter-2026-09-16 prerelease](https://github.com/jeremieguedj/School-OS/releases/tag/school-os-starter-2026-09-16).
Its verified source commit is `ba6bcc3bec96dfc542fd83cb792318ac8e54ce56`. Use that asset, not GitHub's
source-code ZIP: a repository archive includes development/history material and
is not the clean unconfigured starter. The existing documentation snapshot and
old release assets are preserved. PLAN and PROGRESS record publication status;
this preparation document alone does not claim a successful release.

## Build the artifact

Build only from an exact committed revision:

```sh
python3 scripts/build_setup_bundle.py \
  --revision <40-character-commit-sha> \
  --output dist/School-OS-setup.zip
```

The output path must not already exist. The builder reads every included source
file from the named Git commit rather than from working-tree content. Commit and
publication verification remain coordinator responsibilities; creating the ZIP
does not establish that its revision is pushed or released.

For a comparable multi-agent trial, build this artifact once, calculate its
SHA-256 digest, upload those exact bytes once to the authorized delivery location
and give every route the same immutable link. Record the source commit, digest,
upload observation and link in the private artifact manifest. A matching digest
establishes the uploaded artifact's provenance. When a tested agent cannot expose
the bytes it consumed, report that every route received the same link without
claiming each route independently proved its downloaded bytes.

The ZIP has one top directory, `School-OS/`. Its root contains the generated
consumer `README.md`, `START-HERE.md`, `AGENTS.md`, and the exact Claude import
`CLAUDE.md`. The root README records the source revision. Existing reusable
material is placed under `School-OS/system/` with its source layout preserved:

- product principles;
- retained operating procedures;
- the data and identity contracts;
- the source-metadata helper and its runtime guide; and
- the supplied semantic-adapter catalogue and mappings.

`School-OS/instance/` and `School-OS/extensions/` are emitted as empty directory
entries. The bundle has no household values, credentials, canonical IDs,
configuration pages, ingested data, raw source, or preselected private tools.

## Entry-point transition after setup

The consumer root is also the stable entry path after configuration. On first
setup, the agent follows `system/operations/setup.md` and turns the root
`START-HERE.md` into the readable configured bootstrap required by
`system/operations/storage.md`. The pinned reusable material remains under
`system/`; private configuration and canonical pages are created under
`instance/`; compatible household additions remain under `extensions/`.

A later agent verifies the configured bootstrap and follows
`system/operations/startup.md` for the parent's current request. The retained
root README and agent instructions therefore route by actual instance state;
their presence does not force a configured instance through first setup again.
This transition uses the existing readable-bootstrap architecture and adds no
status field, setup manifest, installer state, or other canonical schema.

## Excluded material

The literal build allowlist excludes repository/development entry files, Git
metadata, plans, progress logs, historical and retired documents, examples,
tests, prepared checks and review cases, private receipts and configuration,
cache files, existing distribution artifacts, and developer scripts. The
packager itself is not shipped in the ZIP.

Development-only relative references may appear in reusable source material:
the active restart plan, prepared helper checks, the private-trial evaluator and
its fictional public examples. When present, the builder rewrites only those
link targets to public GitHub URLs pinned to the exact source revision supplied
to the build. They are optional background references and are not required setup
or runtime inputs; evaluator code, checks and examples are not copied into the
consumer starter. Other local Markdown links must resolve inside the final ZIP.

## Static packaging checks

The developer packager uses a literal member allowlist, rejects symlinks and
non-file Git objects, verifies the exact consumer root and empty private areas,
scans every included text payload with the repository privacy scanner, checks
relative Markdown links, and writes deterministic compressed ZIP entries. These
checks establish archive composition and privacy hygiene only.

Building or inspecting this artifact is not functional verification. It does
not run helpers, tests, smoke checks, simulations, ingestion trials, connector
probes, browser operations, or live-account operations. It does not qualify an
agent, provider, setup route, or persisted instance. Publish the reviewed ZIP as
an agent-accessible GitHub release asset only after the ordinary repository
publication process is complete.

## Fresh-context trial delivery and launch failures

A one-link trial begins in a new projectless agent session with no inherited
School-OS conversation or access to this development checkout. Its opening input
is the same immutable starter link plus “setup my schoolOS.” Record unavoidable
platform instructions and the actual browser/profile/account boundary. If the
agent sees repository instructions, another route's answers or output, or another
route's Drive instance, the run cannot establish fresh starter discovery.

If the common link is inaccessible, classify an input-access failure and do not
silently substitute a source archive, emailed file, pasted tree or different
channel. For a generic launch error, preserve the exact response and check for a
created provider task/session, Drive object or other possible effect. Retry the
identical opening once only when evidence establishes that dispatch did not occur
and no durable effect exists. Continue an existing task when one exists. If the
effect is unknown, stop and report uncertainty. Keep the first response, state
checks, retry decision and any second response separate in private evidence; a
generic error is not proof of timeout, throttling or authentication failure.

These delivery records are evaluation evidence, not part of the starter ZIP,
canonical instance state or School-OS identity. An inaccessible common link or
ineligible retry is a route result and does not justify changing another route's
input.
