# Records and normal saving — obligations without a framework

**Approved MVP scope direction, 2026-09-15:** do **not** create a separate “minimum records and ordinary-write framework” deliverable or approval gate. The user has excluded that open dependency from this MVP, alongside D2’s general interrupted canonical-write repair engine. This note keeps the obligations that already apply; it does not propose a replacement schema, transaction system, UUID format, locator inventory or persistence engine. The [active plan](../../PLAN.md) is the approval ledger. The earlier catalogue and small write-intent proposal remain historical in [D2](../ARCHITECTURE-PROPOSAL.md#d2--canonical-record-meanings-and-write-recovery) and Git revision `62070eb`.

D1 is already approved: canonical instance data uses multiple bounded JSON pages and paged directories on Drive, with readable bootstrap and separate `system`, `instance` and `extensions` areas. D5 is approved: preserve source-linked school claims and qualifications; evidence-supported corrections/conflicts; finite, conditional and recurring tasks; school deadlines distinct from parent plans/completion; and three-way synchronization when a task app is configured. The source-metadata identity recipe requires School-OS-owned logical email/attachment identities and treats provider handles as replaceable access aids. Coverage remains distinct from identity and from saved knowledge. The approved query rule checks relevant coverage before claiming exhaustive answers.

**Excluding a framework does not mean “do not save.”** The agent still saves substantive information, tasks, source references and the actual processing state to Drive, verifies ordinary successful persistence, and only then discards accessible temporary raw copies. If an authorized route cannot establish what saved or which material was read, the agent reports the specific incomplete outcome; it does not mark it complete. D4 now places one logical ingestion run and internal resource/batch decisions with the executing agent, not a School-OS batch controller. D6 has that agent inspect its own authorized tools/APIs to validate uncertain external effects. Neither direction brings back a central write/effect engine.

## A wholly fictional meaning check

> Cedar School: “Return Robin’s museum permission slip by September 19 at 17:00. If Robin is not attending, reply instead.”

> Parent: “I plan to respond on September 17.”

An agent saving this source-linked information must keep **September 19 as the school deadline** and **September 17 as the parent’s plan**. The alternative reply condition remains visible. The email record’s School-OS-owned identity and its source metadata locate the claim; a current provider handle merely helps retrieve the original. Separate coverage says what was actually read and verified. Those meanings come from approved product and D5 direction; this is a conceptual written example, not a new JSON field list or executed save.

The implementation can use concise records inside D1 pages without first publishing a whole-project record-family catalogue. The agent may prepare only values needed for the selected operation, with clear recipe instructions for their meanings and verification. It must not silently replace approved distinctions: an absent attachment inventory is not an empty one; a received timestamp cannot become original sending Date; a parent’s completion is not reset by replay; an unread candidate cannot inherit another candidate’s verified flag. A new canonical field meaning or cross-operation contract incompatibility is a **new architecture choice** requiring explicit approval under the [product decision authority](../../../../product-principles.md#decision-authority), not an opportunity to smuggle in a framework piecemeal.

## What the deferral does and does not promise

| Retained for MVP | Excluded or unapproved |
|---|---|
| Canonical Drive knowledge/tasks/configuration as needed for selected operations, with School-OS-owned identities and source links | D2’s proposed complete typed-record inventory, UUID representation and separate locator-record structure as a blanket adoption |
| Separate discovery/content coverage and parent task state, using approved meanings | A new centralized schema registry, event engine, atomic whole-instance snapshot or general small-write-intent mechanism |
| Normal agent verification of successful saving and honest reporting when saving is unknown/incomplete | Automatic discovery, repair or resumption of interrupted sets of canonical writes |
| D1 bounded JSON pages and directories; temporary source custody rules | D7 centralized tool/job register and D8 package/update machinery, both deferred from MVP |

The MVP cannot claim that a half-written canonical update will be reconstructed by School-OS after environment loss. The executing agent may use its own available continuity for its task, but that is not an installed D2 repair guarantee. If normal saving fails, avoid a false completion claim and preserve any privacy-safe known gap; do not infer that a generic error means success, rate limit or a safe retry. The exact connector capability and ordinary readback evidence remain for later user-directed qualification. No test, helper, build, connector probe, ingestion or live write was executed through this note.

The earlier note treated a new minimum record/write contract as a prerequisite for **all** dependent code. That gate is now superseded. D3’s small Python standard-library routines may support mechanical transformations, and operation recipes should mention the actual callable when applicable; neither requires building a general record framework. Any genuinely new architecture surfaced during implementation still returns for approval, while routine in-scope representation choices proceed under existing approved meanings.
