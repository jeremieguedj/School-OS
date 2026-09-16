# School-OS operating instructions

These procedures implement the approved restart MVP as agent instructions and
small mechanical helpers. Agents reason about school meaning and use their own
authorized tools for access and effects. Authored instructions are not evidence
that any particular agent or connector has been qualified.

For an existing instance read [startup](startup.md). For an empty parent-selected
Drive folder read [setup](setup.md). The installed readable START-HERE points to
that instance's `system`, `instance` and `extensions` areas, internal identity,
selected configuration and relevant directories. Do not load the repository's
historical studies or retired release instructions into normal operations.

## Choose the requested operation

| Request | Procedure | Needed supporting material |
|---|---|---|
| Set up my household | [Setup and interview](setup.md) | [Tool mappings](tool-adapters.md), [storage](storage.md), [data contract](../contracts/data.md) |
| Import or catch up school mail | [Ingestion](ingestion.md) | [Identity](../contracts/identity.md), [extraction](extraction.md), [knowledge](knowledge.md), storage |
| Resume unfinished discovery or missed mail | [Continuation](continuation.md) | Ingestion and saved coverage |
| Answer a fact or historical trend question | [Query](query.md) | Knowledge, data contract and relevant coverage |
| Synchronize parent task edits | [Task sync](task-sync.md) | Selected shared adapter, [completion review](completion-review.md) |
| Produce the ordinary daily update | [Daily](daily.md) | Ingestion, task sync when configured, chosen brief recipe |
| Produce a manual or custom brief | [Brief recipes](brief-recipes.md) | Query, freshness conversation, authorized output route |
| Use a new task tool | [Tool adapters](tool-adapters.md) | [Adapter template](tool-adapter-template.md), current agent's available connector |

## Canonical data and actual code

The [data contract](../contracts/data.md) defines the exact approved fields,
references, scope, page envelopes, directories and indexes. [Storage](storage.md)
explains normal bounded reads/writes and verification. [Knowledge](knowledge.md)
separates saved school facts/guidelines/observations from actionable tasks and
preserves individual, family and school scope. The one current encoded-page
maximum is 64 KiB. Pagination keeps records whole; no linked-field format or
per-instance limit is part of the MVP. If later observed whole-record size and
route I/O/retrieval evidence supports an increase, update the shared installed
contract as [storage](storage.md#increasing-the-shared-page-maximum) directs.

The [helper guide](../helpers/README.md) describes the real Python standard-library
[source_metadata.py](../helpers/source_metadata.py) functions for subject
normalization, extracted address parts and UTF-8 text size. No provider SDK,
generic writer, schema service, local daemon or School-OS batch scheduler is
required. Other operations remain the agent's work through tools.

## Installation material boundary

Place the current operating material, `contracts/`, `helpers/`, supplied shared
`adapters/`, and the [product principles](../docs/product-principles.md) in the
instance's `system` area with a known published source revision. Keep the same
relative relationships or make the bootstrap's logical location instructions
explicit. Instance data/configuration belongs in `instance`; compatible household
recipes and new shared tool mappings belong in `extensions`. The setup recipe
establishes the required entry point and configuration through normal agent/tool
operations. This is not a packaged installer, upgrader or compatibility manager.

Do not install the development repository's tests, historical `docs/plans`,
frozen studies, Git state or private developer receipts as operating instructions.
The installed current recipes and contracts are sufficient to perform the retained
operations without the developer conversation. Examples are fictional explanatory
material; never install their household records as real instance data.

## Authority and limits

Follow platform constraints, explicit parent instructions, the selected current
recipe, installed contracts and valid configuration, in that order. The
[product principles](../docs/product-principles.md) govern design decisions and
compatible extensions. A new architecture choice needs explicit approval; a
conformant missing tool mapping can be authored under the approved setup policy.
One shared semantic adapter maps School-OS meanings to one tool's concepts; each
agent's connector owns API calls, credentials, authentication and transport.

Canonical data lives on Drive. Raw school emails/attachments stay at their source;
discard accessible temporary copies after verified persistence. Provider handles
are replaceable access aids, never canonical identity or completion evidence.
Keep unsupported discovery or content visible. The ordinary daily brief requires
complete agreed ingestion; manual requests use their separate freshness rule.

The MVP excludes generic interrupted-write repair, central jobs/register/control,
concurrent same-instance writes and packaged upgrades. These deferrals do not
remove truthful saved coverage, task-app reconciliation, fresh-agent queries,
usable first setup, current output attribution or compatible extensions.
