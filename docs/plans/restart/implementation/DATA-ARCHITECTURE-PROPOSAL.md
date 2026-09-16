# Proposed retained-data and lookup contract

**Status: proposal for Q1 and Q2 review; not adopted or implemented.**

This document supplies the concrete data-shape and lookup proposal requested in
[OPEN-QUESTIONS.md](OPEN-QUESTIONS.md). It does not reopen the approved D1
physical layout, metadata-only email identity, query-coverage rule or D5
knowledge/task behavior. Every new field, record family, reference convention,
page revision and index rule below still requires explicit user approval before
dependent implementation.

The proposal is deliberately smaller than the historical D2 design. It defines
only the retained data needed to save and find source-linked knowledge, tasks,
coverage and configuration. It does not add a generic record registry, generic
writer, transaction protocol, interrupted-write repair engine, database, vector
service, migration system or external dependency. Ordinary operations would
write bounded Drive JSON pages directly and verify the pages they change. The
MVP would still make no claim to repair an interrupted canonical write.

## The two decisions this proposal asks for

### Q1 — approve this concrete retained-data contract

The recommendation is to use the small record families defined here:

- configuration and logical source accounts;
- entities, topics and dated membership relationships;
- logical emails, parent-bound attachment candidate groups and email-level
  ingestion coverage and bounded discovery-window progress;
- source-linked knowledge records; and
- canonical tasks with parent state and task-app synchronization evidence.

Records use School-OS-owned IDs and typed references. School evidence stays
separate from parent planning and completion. Knowledge is stored once at its
true household, school, class or child scope inside this household’s own Drive
instance. A School entity does not create a shared multi-household database. One Task represents one
independently completed obligation; it is not duplicated merely because several
children benefit from one household action.

### Q2 — approve this concrete entity/topic lookup contract

The recommendation is to use stable entity and topic IDs, dated membership
records, and three small rebuildable lookups. The entity index finds records by
scope or participation; the topic index finds records by a small declared topic
vocabulary and its exact aliases; the incoming-relationship lookup finds later
corrections, replacements, support or conflicts that point to an earlier
Knowledge record. Queries read the canonical records, source discovery coverage
and binary email-ingestion state after using these candidate references.
Household and school membership expands
a child's query without copying school-wide facts onto every child.

Each derived index declares the canonical page revisions it covers. A missing
or mismatched revision makes the index stale, not authoritative. The agent then
scans the affected canonical source/month pages and active-task pages or
discloses the unfinished search.

## Contract rules shared by all pages

### Bounded page envelope

D1 already requires UTF-8 JSON pages containing one record family, a page ID,
instance ID and schema version. This proposal adds only `content_revision`, a
positive integer incremented when a canonical page is successfully changed. It
exists so a derived index can reveal staleness; it is not a generation chain,
lock or repair protocol.

```json
{
  "instance_id": "inst_2c9485f0-5df8-47ad-8e73-843da9f75f13",
  "family": "knowledge",
  "page_id": "page_8bb862cb-c401-4cb9-9868-5579c534e40a",
  "schema_version": "1",
  "content_revision": 4,
  "records": []
}
```

The encoded page, including its envelope, remains at or below D1's approved
64 KiB default. Directory and index pages contain at most 100 entries and use
explicit continuation. More pages extend capacity; these are not total-history
limits. Long substantive text uses D1's numbered, lossless paragraph segments
linked to one Knowledge ID rather than truncation.

### IDs and references

This proposal recommends an opaque UUID v4 assigned once by School-OS for every
canonical record. A readable family prefix may precede the UUID, as in the
fictional examples, but carries no semantic identity. IDs are never derived from
a name, provider ID, source body, hash or connector response.

A canonical reference contains the record family and School-OS ID. An optional
page hint reduces reads but is replaceable:

```json
{
  "family": "entity",
  "id": "entity_7140b96d-b564-4905-b8cc-fb4b71d9588a",
  "page_hint": "page_9f76c841-34a2-4fe8-bbfe-0b2083fda2de"
}
```

Reference equality uses `family` plus `id`; it never uses `page_hint`. A paged
family locator directory maps each record ID to its current page ID. Resolution
checks the hinted page first, verifies the ID, then consults the locator
directory. If the locator entry is absent or stale, the agent may traverse the
bounded family page directory; failure to resolve remains explicit.

Current Drive handles and provider handles are access aids only. They may be
stored in a clearly separated `access_aids` section, but cannot replace a
School-OS ID or prove identity, equality, processing or completion.

### Required, optional and unknown values

The proposal uses these rules consistently:

- System identifiers, `family` and `schema_version` must have their declared
  concrete types; they cannot be unknown.
- A **required** field must be present. If its real-world value is required but
  the source does not establish it, use an explicit unknown object such as
  `{"state":"unknown","reason":"not stated by source"}`.
- An **optional** field is omitted only when the concept does not apply.
- An empty string is substantive only when the source explicitly supplies one;
  it never means unknown.
- An empty array means the relevant inventory was established and had zero
  members. An unknown or partial inventory uses an explicit state instead.
- Canonical records do not use `null`; explicit known, unknown, partial,
  unsupported and unavailable states retain their different meanings.
- A boolean is stored only for a genuine two-valued statement. It must not hide
  unknown or partial evidence.

Known dates preserve value, meaning and precision. An instant also preserves
the supplied timezone. A calendar date without a source timezone does not gain
one from the executing agent:

```json
{
  "state": "known",
  "value": "2026-03-10",
  "precision": "day",
  "meaning": "observation_date"
}
```

```json
{
  "state": "known",
  "value": "2026-03-10T08:15:23-07:00",
  "precision": "second",
  "timezone": "-07:00",
  "meaning": "original_email_date"
}
```

`recorded_at` is the instant the agent authored the record values for the save.
It is separate from the source's original Date, an observation date, a deadline
and an applicability interval. A `verified_at` inside coverage or tool-sync
evidence means the agent completed the named source/content/remote readback at
that time; it does not claim that the JSON field containing the timestamp had
already verified its own persistence. After the bounded JSON write, the agent
reads the final page back once and checks its intended values. That final
readback is operational evidence and does not trigger another timestamp write,
avoiding an infinite write-to-record-its-own-save loop. This proposal adds no
general persisted write-verification log.

## Entity, topic and membership records

### Entity

An Entity identifies a household, child, other person, school, or class/group.
The required fields are `entity_id`, `entity_kind`, `display_name`,
`recorded_at` and `origin`. Optional aliases support exact name resolution
within this instance; aliases never silently merge two entities.

```json
{
  "entity_id": "entity_7140b96d-b564-4905-b8cc-fb4b71d9588a",
  "entity_kind": "child",
  "display_name": "Robin",
  "aliases": ["Robin G."],
  "origin": "parent_configuration",
  "recorded_at": "2026-09-15T16:00:00Z"
}
```

The proposed finite `entity_kind` values are `household`, `child`, `person`,
`school`, and `class_or_group`. A teacher is a `person`; being Robin's teacher is
a dated relationship, not part of the teacher's identity. A subject such as
math is normally a Topic, not an Entity.

### Topic

A Topic is a small, human-readable lookup concept. Required fields are
`topic_id`, `label`, `aliases`, `origin` and `recorded_at`. Optional
`broader_topic_refs` provide explicit query expansion without treating related
topics as aliases.

```json
{
  "topic_id": "topic_e83bf100-a778-448b-b24e-d24535146b7a",
  "label": "math",
  "aliases": ["mathematics", "numeracy"],
  "broader_topic_refs": [],
  "origin": "household_extension",
  "recorded_at": "2026-09-15T16:05:00Z"
}
```

An alias must mean the same topic in this household context. Related terms are
separate topics: `fractions` is co-tagged with `math` and may declare `math` as a
broader topic, but is not silently made an alias. Teacher feedback should also
carry the `teacher-feedback` topic rather than relying on words in its statement.
Query expansion follows only declared broader-topic references and still reads
the actual Knowledge. The proposal has no ontology service, embeddings or
automatic synonym service. An unfamiliar or conflicting label remains
unresolved until an agent or parent selects an existing topic or creates a
distinct one.

### Membership history

A Membership record preserves one dated relationship between entities. Required
fields are `membership_id`, `subject_ref`, `role`, `container_ref`,
`valid_interval`, `origin`, `evidence_refs` and `recorded_at`.

```json
{
  "membership_id": "membership_b2064205-eeda-4ab5-a86c-c57cc97fdcf5",
  "subject_ref": {
    "family": "entity",
    "id": "entity_7140b96d-b564-4905-b8cc-fb4b71d9588a"
  },
  "role": "student",
  "container_ref": {
    "family": "entity",
    "id": "entity_ba7a2221-56ed-4803-85bf-5d85b4fa8962"
  },
  "valid_interval": {
    "start": {
      "state": "known",
      "value": "2026-08-24",
      "precision": "day",
      "meaning": "membership_start"
    },
    "end_state": "ongoing"
  },
  "origin": "parent_configuration",
  "evidence_refs": [],
  "recorded_at": "2026-09-15T16:10:00Z"
}
```

An empty `evidence_refs` is valid only for a parent-declared configuration fact.
A source-derived membership cites Knowledge records. The initial proposed roles
are `household_member`, `student`, `class_member`, and `teacher`. A role does not
imply dates that were not stated. `ongoing`, `ended` and `unknown` are distinct;
absence of an end date does not by itself prove ongoing membership.

Membership history lets a query include one school-wide record for each child
who belonged to that school at the relevant time without copying the record per
child. It also preserves teacher or class changes across a year.

## Source, attachment and ingestion-coverage records

### Logical source account and instance configuration

The instance configuration proposes these minimum retained fields:

| Field | Requirement and meaning |
|---|---|
| `instance_id` | Required approved D1 instance identity. |
| `household_entity_ref` | Required true household scope. |
| `household_timezone` | Required parent-selected display/default planning timezone; never substitutes for a source timezone. |
| `source_accounts` | Required bounded references to logical Source Account records; each retains the logical mailbox, configured school/source scope and parent-selected import boundary. Credentials are excluded. |
| `entity_topic_roots` | Required references to the entity, membership, topic and derived-index directories. |
| `selected_task_projection` | Optional when no task tool is configured; otherwise names the shared tool-semantic adapter, parent-selected connection label and supported field mapping. |
| `selected_brief_recipes` | Optional parent choices made discoverable through the existing D1 configuration. |
| `authorized_destinations` | Optional operation destinations; absence gives no send authority. |

This is operating configuration, not a D7 tools/jobs registry. It does not
inventory every connector, scheduled job or runtime.

A logical Source Account is a canonical record in the `source_account` family,
resolved through its family directory like every typed reference. It has a School-OS ID, parent-readable label,
logical mailbox identity, configured scope, import boundary and selected shared
mail-tool adapter. Current connection or provider handles remain replaceable
access aids in configuration and do not become source identity.

### Logical email

The Email record follows the approved metadata-only recipe. It contains:

- a School-OS `email_id` and logical `source_account_ref`;
- original observed subject, sender, original Date, received time when exposed,
  To/Cc roles, and original attachment names/count when comparably exposed;
- separately stored normalized comparison values;
- association state and any unresolved candidates;
- optional current `access_aids`, clearly excluded from identity; and
- a reference to its email-level ingestion coverage.

Individual replies have individual Email records. A thread summary cannot stand
in for them. Provider IDs, thread IDs, body content, hashes and MIME structure
cannot decide identity. Original Date precision and timezone are preserved; this
the now-approved Q5 threshold requires a known timezone and second-or-finer
precision for automatic association, alongside the other approved metadata and
coverage checks. Even that precision does not prove uniqueness; compatible
multiple candidates remain unresolved.

This fictional compact example shows the proposed separation between observed
identity metadata, normalized comparison values and replaceable access aids:

```json
{
  "email_id": "email_f99baa23-032d-49cd-b180-2b6dc6727c82",
  "source_account_ref": {
    "family": "source_account",
    "id": "source_account_6f173cea-043b-4a42-92c4-f4f1fc54b8f0"
  },
  "observed_metadata": {
    "subject": "Family science night",
    "sender": "Pine School <office@pine.example>",
    "original_date": {
      "state": "known",
      "value": "2026-09-14T15:42:18-07:00",
      "precision": "second",
      "timezone": "-07:00",
      "meaning": "original_email_date"
    },
    "received_time": {
      "state": "known",
      "value": "2026-09-14T22:42:44Z",
      "precision": "second",
      "timezone": "Z",
      "meaning": "received_time"
    },
    "recipients": {
      "state": "known",
      "to": ["family@example.net"],
      "cc": []
    },
    "attachment_inventory": {
      "state": "known_complete",
      "original_names": ["Science-Night.pdf"]
    }
  },
  "comparison_metadata": {
    "subject": "Family science night",
    "sender": {"local_part": "office", "domain": "pine.example"},
    "to": [{"local_part": "family", "domain": "example.net"}],
    "cc": [],
    "original_date_instant": "2026-09-14T22:42:18Z"
  },
  "association": {
    "state": "resolved",
    "pending_candidate_refs": []
  },
  "access_aids": [
    {
      "adapter_ref": "system/tool-adapters/example-mail-tool",
      "provider_handle": "replaceable-message-handle",
      "observed_at": "2026-09-15T16:20:00Z"
    }
  ],
  "coverage_ref": {
    "family": "ingestion_coverage",
    "id": "coverage_a6354db3-9e26-436e-900f-4a1ea3783b98"
  },
  "recorded_at": "2026-09-15T16:21:00Z"
}
```

The `cc: []` value means the comparable recipient inventory explicitly had no Cc
members. Missing or partial recipients would use an explicit state instead. The
example provider handle can change without changing `email_id`.

### Attachment candidate group

An Attachment Group is identified by its parent `email_ref` and original
filename when known. It records inventory scope, all currently exposed
candidates, requirement classification and completion evidence when the email is
fully ingested. Same-name
candidates under one email remain together; different handles or MIME labels do
not prove separate documents. A generated download name is not an original
filename.

`required_for_full_ingestion` has the values `required`, `not_required`, or
`unknown`, with a short source-grounded reason. `not_required` is appropriate
only when the material is established to be outside the configured substantive
scope, such as a purely decorative asset. Unknown requirement blocks the email
from becoming fully ingested.

```json
{
  "attachment_group_id": "attachment_group_4c67171d-5508-431b-929a-a8d65b900ee7",
  "email_ref": {
    "family": "email",
    "id": "email_f99baa23-032d-49cd-b180-2b6dc6727c82"
  },
  "original_filename": {
    "state": "known",
    "value": "Science-Night.pdf"
  },
  "inventory_scope": "complete_for_selected_message_route",
  "candidates": [
    {
      "candidate_ref": "candidate_1",
      "access_aid": "replaceable-attachment-handle",
      "ingestion_evidence": {
        "state": "processed_saved_verified",
        "knowledge_refs": [
          {"family": "knowledge", "id": "knowledge_e3cf85f5-9796-4a55-891f-0e1e849c8106"}
        ],
        "verified_at": "2026-09-15T16:25:00Z"
      }
    }
  ],
  "required_for_full_ingestion": {
    "state": "required",
    "reason": "the notice says the PDF contains event instructions"
  },
  "recorded_at": "2026-09-15T16:22:00Z"
}
```

`candidate_ref` is local to the Attachment Group and is never promoted to
canonical attachment identity. If two same-name candidates cannot be
distinguished, preserve the candidate group and qualified attribution. Unread
or unresolved required processing prevents full ingestion. Uncertainty about
which of two fully processed candidates is the same physical original does not
by itself block the email or create permanent attachment identity.

### Email-level ingestion coverage

The approved Q6 binary direction is represented at the logical-email level: an
email is either `fully_ingested` or `not_ingested`. School-OS does not persist a
partially ingested email or a part-resume workflow. The example below is wholly
complete: the body and required PDF were processed, their Knowledge was saved,
and the required readbacks were verified.

```json
{
  "coverage_id": "coverage_a6354db3-9e26-436e-900f-4a1ea3783b98",
  "email_ref": {
    "family": "email",
    "id": "email_f99baa23-032d-49cd-b180-2b6dc6727c82"
  },
  "body_ingestion_evidence": {
    "state": "processed_saved_verified",
    "knowledge_refs": [
      {"family": "knowledge", "id": "knowledge_d45652fb-cfc8-486f-81d7-b5413c672ff8"}
    ],
    "verified_at": "2026-09-15T16:25:00Z"
  },
  "attachment_inventory": {
    "state": "complete",
    "group_refs": [
      {
        "family": "attachment_group",
        "id": "attachment_group_4c67171d-5508-431b-929a-a8d65b900ee7"
      }
    ]
  },
  "required_attachment_group_refs": [
    {
      "family": "attachment_group",
      "id": "attachment_group_4c67171d-5508-431b-929a-a8d65b900ee7"
    }
  ],
  "ingestion_state": "fully_ingested",
  "evaluated_at": "2026-09-15T16:26:00Z"
}
```

`ingestion_state` may be `fully_ingested` only when:

1. the individual message body was processed, including an explicitly
   established empty body, and its resulting Knowledge was saved and read back;
2. the attachment inventory is complete for the selected route and scope;
3. every attachment group's requirement is known; and
4. every group marked required was processed and its resulting Knowledge was
   saved and read back.

If any condition fails, the email is `not_ingested`. The agent reports the
blocking reason and the logical ingestion operation remains incomplete; it does
not save a partial email-ingestion state for later part-level resumption. Source
and attachment inventory still preserve what was observed, and discovery-window
coverage remains separate.

This proposal intentionally does **not** decide when a later repeated appearance
may reuse prior body or attachment coverage. A metadata match and an existing
`ingestion_state: "fully_ingested"` value do not, by this document alone, authorize skipping
the new appearance. The later Q6 decision table must define what appearance
evidence is sufficient, what changed or incomplete inventory means, and when a
reread is required. No body/byte hash or content comparison is introduced.

### Discovery-window records

A `discovery_window` describes where the mailbox was searched, separately from
an individual email's binary ingestion result. This is a concrete representation
of the already-approved durable window progress. The proposed arrival-time
search policy below is still conditional on Q4 approval.

| Field | Proposed meaning |
|---|---|
| `window_id` | School-OS-owned ID, resolved through the source-account window directory. |
| `source_account_ref` | Logical mailbox; no required provider cursor. |
| `scope_description` and `school_refs` | The configured source scope in tool-independent terms, including applicable inclusion/exclusion choices. A connector query is only an access aid. |
| `time_basis`, `start`, `end` | Declared source time meaning, timezone, precision and inclusive/exclusive boundary flags; never silently reuse original sending Date as arrival time. |
| `discovery_state` | `unfinished` or `complete`; completion requires route-established exhaustion of the declared window. |
| `observed_email_refs` | References to bounded source-index pages containing results, not an unbounded array of message IDs. |
| `verification` | When the agent observed exhaustion or interruption and the relevant route limitation/evidence summary. This does not certify invisible provider material. |
| `access_aids` | Optional temporary continuation/token hints. Their loss does not erase the described window or require a prior conversation. |

```json
{
  "window_id": "window_d23383df-95eb-4f1c-bb49-8091d2641d65",
  "source_account_ref": {"family": "source_account", "id": "source_account_6f173cea-043b-4a42-92c4-f4f1fc54b8f0"},
  "scope_description": "Parent-selected Pine School correspondence in the configured mailbox",
  "school_refs": [{"family": "entity", "id": "entity_ba7a2221-56ed-4803-85bf-5d85b4fa8962"}],
  "time_basis": "source_received_time",
  "start": {"value": "2026-09-14T06:00:00-07:00", "precision": "second", "timezone": "-07:00", "inclusive": true},
  "end": {"value": "2026-09-15T06:00:00-07:00", "precision": "second", "timezone": "-07:00", "inclusive": true},
  "discovery_state": "complete",
  "observed_email_refs": {"source_index_page_ids": ["page_a6273a4f-6c57-49f1-ad04-3d281701c49b"], "continuation": {"state": "exhausted"}},
  "verification": {"observed_at": "2026-09-15T13:05:00Z", "evidence_summary": "Selected route exhausted all continuation pages for this window"}
}
```

These references point to source records; they do not prove those emails were
fully ingested. To assess fresh knowledge, read the relevant window outcomes
and each required email's ingestion result. A window can be completely listed
while an email is not ingested. A lost token allows replay of an unfinished
window. No window falsely advances because a connector returned a short page.

## Knowledge records

All saved school meaning uses one Knowledge family with a required
`knowledge_kind`:

- `fact`: a source-supported proposition;
- `guideline`: a rule, instruction or condition that can remain applicable;
- `update`: a source-announced change in state or plan; or
- `observation`: a dated report, assessment or description.

The kind is independent of actionability. Each record also has an
`action_disposition` of `none`, `finite`, `conditional`, or `recurring`. An
actionable Task points to its supporting Knowledge; the Knowledge record does
not duplicate a reverse Task link. A guideline can therefore produce a recurring
task, while a teacher observation can remain non-actionable.

Required Knowledge fields are:

| Field | Meaning |
|---|---|
| `knowledge_id` | Stable School-OS ID. |
| `knowledge_kind` | One of the four meanings above. |
| `statement` or `segment_refs` | Lossless substantive statement, with long text segmented under D1. |
| `qualifications` | Established exceptions, conditions and uncertainty; empty only when assessed as none. |
| `scope` | True storage/applicability anchor, described below. |
| `entity_links` | Relevant entities with roles such as subject, reporter or school context. |
| `topic_refs` | One or more selected Topic IDs; unresolved topic classification remains explicit. |
| `source_refs` | Email/body or attachment evidence and readable extraction location; exactly one source is designated primary for canonical source/month routing. |
| `dates` | Applicable source, observation, effective or interval dates without conflation. |
| `action_disposition` | `none`, `finite`, `conditional`, or `recurring`; Tasks carry the supporting Knowledge references. |
| `relationships` | Explicit evidenced support/correction/replacement/conflict links; may be established empty. |
| `recorded_at` | Instant the agent authored these record values for the bounded save. |

`scope` contains one anchor Entity and an applicability mode:

- `anchor_only` applies to the household, person, school or class itself;
- `listed_entities` applies only to the required `listed_entity_refs` array in
  that `scope`; every listed Entity receives a derived entity-index entry; or
- `members_at_effective_time` applies to entities with the required Membership
  role during the record's effective interval.

This lets a school-wide guideline be stored once at School scope. A child query
reaches it through dated enrollment. A notice that names Robin alone uses Child
scope. A household policy is stored once at Household scope.

### Fictional teacher-feedback history

These linked examples are proposals, not executed or simulated data. Page hints
are omitted for readability.

```json
{
  "knowledge_id": "knowledge_0f629d53-1ec4-42f7-8c5f-21c7a19cac42",
  "knowledge_kind": "observation",
  "statement": "Robin needed prompts to compare fractions with unlike denominators.",
  "qualifications": ["Observation concerned independent class work during the autumn conference period."],
  "scope": {
    "anchor_ref": {"family": "entity", "id": "entity_7140b96d-b564-4905-b8cc-fb4b71d9588a"},
    "applicability": "anchor_only"
  },
  "entity_links": [
    {"role": "subject", "ref": {"family": "entity", "id": "entity_7140b96d-b564-4905-b8cc-fb4b71d9588a"}},
    {"role": "reporter", "ref": {"family": "entity", "id": "entity_10427a27-2369-4857-979c-713971128626"}},
    {"role": "school_context", "ref": {"family": "entity", "id": "entity_ba7a2221-56ed-4803-85bf-5d85b4fa8962"}}
  ],
  "topic_refs": [
    {"family": "topic", "id": "topic_e83bf100-a778-448b-b24e-d24535146b7a"},
    {"family": "topic", "id": "topic_b7d18075-d15f-4d5c-847f-fe807f8a78cc"},
    {"family": "topic", "id": "topic_bbe44cfa-774d-469d-8a89-137e5cc140c4"}
  ],
  "source_refs": [
    {"email_ref": {"family": "email", "id": "email_3ce1f05a-f927-47fc-872d-40f55f3bef67"}, "part": "body", "location": "conference feedback paragraph", "primary": true}
  ],
  "dates": [
    {"state": "known", "value": "2025-10", "precision": "month", "meaning": "observation_period"}
  ],
  "action_disposition": "none",
  "relationships": [],
  "recorded_at": "2025-10-18T18:30:00Z"
}
```

```json
{
  "knowledge_id": "knowledge_8ee6417d-8325-49b1-acd4-f319f60682ac",
  "knowledge_kind": "observation",
  "statement": "Robin independently explained why two fractions were equivalent.",
  "qualifications": ["Observation concerned a spring small-group activity."],
  "scope": {
    "anchor_ref": {"family": "entity", "id": "entity_7140b96d-b564-4905-b8cc-fb4b71d9588a"},
    "applicability": "anchor_only"
  },
  "entity_links": [
    {"role": "subject", "ref": {"family": "entity", "id": "entity_7140b96d-b564-4905-b8cc-fb4b71d9588a"}},
    {"role": "reporter", "ref": {"family": "entity", "id": "entity_10427a27-2369-4857-979c-713971128626"}}
  ],
  "topic_refs": [
    {"family": "topic", "id": "topic_e83bf100-a778-448b-b24e-d24535146b7a"},
    {"family": "topic", "id": "topic_b7d18075-d15f-4d5c-847f-fe807f8a78cc"},
    {"family": "topic", "id": "topic_bbe44cfa-774d-469d-8a89-137e5cc140c4"}
  ],
  "source_refs": [
    {"email_ref": {"family": "email", "id": "email_aaf8400b-8014-45a4-83d4-b4ab33ac1757"}, "part": "body", "location": "math update paragraph", "primary": true}
  ],
  "dates": [
    {"state": "known", "value": "2026-03-10", "precision": "day", "meaning": "observation_date"}
  ],
  "action_disposition": "none",
  "relationships": [],
  "recorded_at": "2026-03-11T01:20:00Z"
}
```

The spring observation does **not** correct the autumn observation. Both can be
true at their respective times and together show development. A `corrects`
relationship is allowed only when source evidence establishes that a prior
statement was wrong. A prospective policy change uses `replaces`; disagreement
without resolution uses `conflicts_with`; additional evidence may use
`supports`. Each relationship points from the newer record to the earlier one
and includes evidence and a short justification. No reverse-link rewrite is
required.

## Task records and action granularity

A Task is created only for a finite, conditional or recurring actionable
request. Guidelines and observations remain Knowledge even when they create no
Task. One Task represents one independently completed obligation.

Task fields are listed below. School-source fields are required only for
`source_derived` Tasks; the table identifies valid parent-created omissions.

| Field | Meaning |
|---|---|
| `task_id` | Stable School-OS ID; also carried in a supported managed app field. |
| `origin` | `source_derived` or `parent_created`; parent-created Tasks do not require school evidence. |
| `action` and `context` | What must be done and its source-supported or parent-authored context. |
| `scope_ref` | True scope of the actionable obligation: household, school, class or child. |
| `source_context_refs` | School, class or other source context; an established empty array is valid for a personal Task. |
| `completion_subject_ref` | Entity whose single action completes this Task. |
| `beneficiary_refs` | Established children/people affected; complete inventory or explicit unknown. |
| `supporting_knowledge_refs` | Source-derived support; an established empty array is valid for a parent-created Task. |
| `action_kind` | `finite`, `conditional`, `recurring_series`, or `recurring_occurrence`. |
| `school_timing` | Required for source timing when applicable; omitted for a personal Task with no school timing. |
| `parent_state` | Owner, planned date, progress, completion, personal notes and explicit completion-review decisions. |
| `task_sync` | Last verified shared values and observed task-app state. |
| `recorded_at` | Instant the agent authored these record values for the bounded save. |

For recurrence, a `recurring_series` Task preserves the source recurrence and
applicability interval. Each projected `recurring_occurrence` has its own Task ID,
completion subject, due date and parent state, plus `series_ref`. This keeps
occurrence completion independent and supports D5's approved 14-day projection
fallback without growing one record indefinitely.

### One household task for two children

Suppose fictional Pine School requests one emergency-contact confirmation per
household, even when siblings Robin and Jamie both attend. Store the school
request once as Knowledge at School scope and create one Task whose completion
subject is the household:

```json
{
  "knowledge_id": "knowledge_a4f11b51-dc24-470c-a929-90acec03df1f",
  "knowledge_kind": "guideline",
  "statement": "Each household with students at Pine School must confirm its emergency-contact details once.",
  "qualifications": ["One confirmation covers siblings in the same household."],
  "scope": {
    "anchor_ref": {"family": "entity", "id": "entity_ba7a2221-56ed-4803-85bf-5d85b4fa8962"},
    "applicability": "members_at_effective_time",
    "membership_role": "student"
  },
  "entity_links": [
    {"role": "school_context", "ref": {"family": "entity", "id": "entity_ba7a2221-56ed-4803-85bf-5d85b4fa8962"}}
  ],
  "topic_refs": [
    {"family": "topic", "id": "topic_68f256cc-19f3-43ec-9858-c5c2fb1de620"}
  ],
  "source_refs": [
    {"email_ref": {"family": "email", "id": "email_f99baa23-032d-49cd-b180-2b6dc6727c82"}, "part": "body", "location": "required action paragraph", "primary": true}
  ],
  "dates": [
    {"state": "known", "value": "2026-09-18", "precision": "day", "meaning": "school_deadline"}
  ],
  "action_disposition": "finite",
  "relationships": [],
  "recorded_at": "2026-09-15T16:55:00Z"
}
```

```json
{
  "task_id": "task_aa32a59d-03d9-461a-a8e4-ced24ee1870b",
  "origin": "source_derived",
  "action": "Confirm the household emergency-contact details in the school portal.",
  "context": "Pine School requests one confirmation per household.",
  "scope_ref": {"family": "entity", "id": "entity_03a9f0bb-26aa-42c0-b363-314213034b3d"},
  "source_context_refs": [
    {"family": "entity", "id": "entity_ba7a2221-56ed-4803-85bf-5d85b4fa8962"}
  ],
  "completion_subject_ref": {"family": "entity", "id": "entity_03a9f0bb-26aa-42c0-b363-314213034b3d"},
  "beneficiary_refs": [
    {"family": "entity", "id": "entity_7140b96d-b564-4905-b8cc-fb4b71d9588a"},
    {"family": "entity", "id": "entity_4567b2ea-aa5b-441a-b241-78890fd6f248"}
  ],
  "supporting_knowledge_refs": [
    {"family": "knowledge", "id": "knowledge_a4f11b51-dc24-470c-a929-90acec03df1f"}
  ],
  "action_kind": "finite",
  "school_timing": {
    "deadline": {"state": "known", "value": "2026-09-18", "precision": "day", "meaning": "school_deadline"}
  },
  "parent_state": {
    "owner": {"state": "unknown", "reason": "parent has not assigned an owner"},
    "planned_date": {"state": "unknown", "reason": "parent has not planned a date"},
    "progress": "open",
    "completed": false,
    "personal_notes": [],
    "completion_reviews": []
  },
  "task_sync": [],
  "recorded_at": "2026-09-15T17:00:00Z"
}
```

A fictional parent-created personal Task has no fabricated school Knowledge or
deadline:

```json
{
  "task_id": "task_c51b95b9-3e30-4818-b19b-a75cc43e9cd6",
  "origin": "parent_created",
  "action": "Pack an extra snack for Robin's field trip.",
  "context": "Parent-added preparation reminder.",
  "scope_ref": {"family": "entity", "id": "entity_03a9f0bb-26aa-42c0-b363-314213034b3d"},
  "source_context_refs": [],
  "completion_subject_ref": {"family": "entity", "id": "entity_03a9f0bb-26aa-42c0-b363-314213034b3d"},
  "beneficiary_refs": [
    {"family": "entity", "id": "entity_7140b96d-b564-4905-b8cc-fb4b71d9588a"}
  ],
  "supporting_knowledge_refs": [],
  "action_kind": "finite",
  "parent_state": {
    "owner": "Parent A",
    "planned_date": "2026-09-17",
    "progress": "open",
    "completed": false,
    "personal_notes": [],
    "completion_reviews": []
  },
  "task_sync": [],
  "recorded_at": "2026-09-15T17:02:00Z"
}
```

If the source instead requires a separate confirmation per child, create two
Tasks because there are two independent completion units. Shared source
Knowledge remains stored once; each Task links the same Knowledge and its own
child completion subject. A school-wide notice that asks parents to remember a
rule but requires no response creates no Task.

Clear completion evidence creates an entry in
`parent_state.completion_reviews`. Each entry contains its evidence references,
`detected_at`, and an explicit parent-review state: `awaiting_confirmation`,
`confirmed`, or `rejected`. Only an `awaiting_confirmation` entry displays
**Completion detected — awaiting parent confirmation** while
`parent_state.completed` remains false. Evidence by itself does not compute that
state.

A parent's rejection changes that review entry to `rejected` and preserves the
evidence; the same evidence cannot silently reopen it. Materially new evidence
may create a new awaiting entry, while the rejected decision remains in history.
A confirmed review and the parent's checked completion flow through approved D5
synchronization. A later receipt does not reopen or downgrade an already
completed Task. If the review list outgrows a bounded Task page, D1-style numbered
segments linked to the same Task ID preserve the history.

```json
{
  "state": "rejected",
  "evidence_refs": [
    {"family": "knowledge", "id": "knowledge_5ee6ba75-81d9-45c0-bf1e-f18ca29c65d0"}
  ],
  "detected_at": "2026-09-16T08:10:00Z",
  "decided_at": "2026-09-16T15:30:00Z",
  "parent_note": "The receipt was for Jamie's form, not Robin's."
}
```

### Task-app synchronization evidence

Each configured projection entry proposes these fields:

```json
{
  "adapter_ref": "system/tool-adapters/example-task-tool",
  "connection_label": "Parent-selected task account",
  "access_aid": "replaceable-provider-task-handle",
  "identity_marker_verified": true,
  "last_verified_at": "2026-09-15T17:10:00Z",
  "last_verified_shared_values": {
    "owner": "Parent A",
    "planned_date": "2026-09-17",
    "progress": "open",
    "completed": false,
    "personal_notes": []
  },
  "last_observed_remote_values": {
    "owner": "Parent A",
    "planned_date": "2026-09-17",
    "progress": "open",
    "completed": false,
    "personal_notes": []
  },
  "projection_state": "verified"
}
```

The task's canonical `parent_state`, the `last_verified_shared_values` base and a
new remote observation supply D5's approved three-way comparison. Proposed
finite `projection_state` values are `verified`, `missing`, `unknown`, and
`conflict`. The provider handle only locates the current projection. The managed
School-OS Task ID establishes identity; title similarity does not.

No credentials, API request format, retry engine or central binding registry is
stored here. If the selected app or connector cannot carry or verify the managed
identity marker, the projection remains unsupported.

## Directory and derived-index contract

### Canonical routes

The proposal uses D1's approved routes rather than inventing a database:

- Email, attachment and coverage pages route by logical mailbox and normalized
  UTC month of original Date; unknown original dates use the discoverable
  pending area.
- Knowledge pages route primarily by the original-Date month of their one
  designated primary supporting source and retain all source references.
- Task pages use the separately paged active-task directory. Completed Tasks
  remain discoverable through task history pages and their canonical IDs.
- Entity, Topic and Membership families use bounded family directories.
- Family locator pages map canonical record IDs to current page IDs, at most 100
  entries per page.

Changing a Drive handle or page hint does not rename a record. Directory
continuations are explicit and independent of provider pagination tokens.

The canonical page catalogue is a small D1 directory, not a copy of page bodies.
Each entry carries the current readable page revision so index freshness can be
checked without downloading every canonical body:

```json
{
  "instance_id": "inst_2c9485f0-5df8-47ad-8e73-843da9f75f13",
  "family": "page_catalogue",
  "page_id": "page_catalogue_56aeb7cc-68c6-44a0-bda5-fb2983280fcb",
  "schema_version": "1",
  "content_revision": 3,
  "route": {
    "canonical_family": "knowledge",
    "source_account_id": "source_account_6f173cea-043b-4a42-92c4-f4f1fc54b8f0",
    "source_month": "2026-03"
  },
  "entries": [
    {
      "canonical_page_id": "page_8bb862cb-c401-4cb9-9868-5579c534e40a",
      "canonical_family": "knowledge",
      "content_revision": 4,
      "drive_access_aid": "replaceable-drive-handle"
    }
  ],
  "continuation": {"state": "exhausted"}
}
```

The normal save order is canonical page write and readback, then catalogue entry
write and readback, then derived-index update. These are independent bounded
writes, not an atomic transaction. Interruption between them can leave a stale
catalogue that this MVP does not repair or always detect; the agent reports a
known uncertain save outcome, and the D2 repair deferral remains material.

### Entity, topic and incoming-relationship indexes

All three lookups are derived and rebuildable. Entity/topic index month means
the record's semantic time, not its canonical source-page month:

- an Observation uses its observation date or interval;
- a Fact, Guideline or Update uses its effective date or interval;
- a closed interval appears in each overlapping calendar-month shard;
- an explicitly continuing guideline appears in its start month and an
  `open_interval` shard checked by every current or historical applicability query
  whose interval could overlap the continuing rule; and
- unknown applicability appears in an `unknown_interval` shard and must be read
  and qualified rather than silently excluded.

The primary source's original Date still determines the canonical source/month
page. Thus a March email that reports a November observation is stored through
the March source route and indexed in November for a historical trend query.
Index entries retain both semantic and source dates so the distinction remains
visible.

Membership entries use their valid interval. Active Task retrieval always reads
the relevant active-task directory and does not exclude a task merely because
its original email is old; any dated Task index entry uses the task’s school or
parent-planned timing and preserves the chosen meaning. Unknown timing uses the
unknown bucket. Index-root directory entries map an entity/topic ID to its
bucket-page references; bucket directories and continuations also obey D1’s
100-entry and byte limits. Looking up an ID can require several directory pages;
there is no hidden database search operation.

Each entry contains a canonical record reference, record family, the matched
role, and known effective/observation bounds for pruning. It does not copy the
substantive statement. Index entries are paged at 100 or fewer and remain under
64 KiB.

An entity-index page and entry look like this:

```json
{
  "instance_id": "inst_2c9485f0-5df8-47ad-8e73-843da9f75f13",
  "family": "entity_index",
  "page_id": "page_entity_index_268b421e-97a1-4117-a787-f3157ac52714",
  "schema_version": "1",
  "content_revision": 2,
  "index_key": {
    "entity_id": "entity_7140b96d-b564-4905-b8cc-fb4b71d9588a",
    "time_bucket": "2026-03"
  },
  "entries": [
    {
      "record_ref": {"family": "knowledge", "id": "knowledge_8ee6417d-8325-49b1-acd4-f319f60682ac", "page_hint": "page_8bb862cb-c401-4cb9-9868-5579c534e40a"},
      "matched_role": "subject",
      "date_basis": "observation_date",
      "semantic_interval": {"start": "2026-03-10", "end": "2026-03-10"},
      "primary_source_month": "2026-03"
    }
  ],
  "continuation": {"state": "exhausted"}
}
```

A topic-index page uses the same bounded structure:

```json
{
  "instance_id": "inst_2c9485f0-5df8-47ad-8e73-843da9f75f13",
  "family": "topic_index",
  "page_id": "page_topic_index_03d60650-489c-4ace-b262-a7bd3e165852",
  "schema_version": "1",
  "content_revision": 2,
  "index_key": {
    "topic_id": "topic_e83bf100-a778-448b-b24e-d24535146b7a",
    "time_bucket": "2026-03"
  },
  "entries": [
    {
      "record_ref": {"family": "knowledge", "id": "knowledge_8ee6417d-8325-49b1-acd4-f319f60682ac", "page_hint": "page_8bb862cb-c401-4cb9-9868-5579c534e40a"},
      "matched_topic_id": "topic_e83bf100-a778-448b-b24e-d24535146b7a",
      "date_basis": "observation_date",
      "semantic_interval": {"start": "2026-03-10", "end": "2026-03-10"},
      "primary_source_month": "2026-03"
    }
  ],
  "continuation": {"state": "exhausted"}
}
```

Entity indexing includes:

- the Knowledge `scope` anchor;
- every `listed_entity_refs` member when applicability is `listed_entities`;
- every Knowledge `entity_link` role;
- Task scope, completion subject and beneficiaries (active Tasks also remain
  directly reachable through D1’s active-task directory); and
- Membership subjects and containers.

Topic indexing includes only Knowledge topic references. Tasks have no derived
topic-index entries: a task query retrieves Tasks from the active-task directory
and entity index, then reads their linked supporting Knowledge to apply topic
filters. A parent-created task with no school Knowledge is filtered using its
own action/context and explicit beneficiaries; no school source is invented.
This avoids a dependency engine in which changing Knowledge silently
makes an unchanged Task's topic entry stale.

Writers should co-tag specific and broad concepts that the source supports, such
as `fractions`, `math`, and `teacher-feedback`, and queries follow declared
`broader_topic_refs`. Even a fresh topic index cannot prove semantic completeness:
a record may have been classified too narrowly. For a completeness-sensitive
topic question, the agent also reviews the relevant entity/scope/time candidate
Knowledge and applies source-grounded semantic judgment. It discloses any
unfinished fallback rather than claiming that exact topic matches are exhaustive.

A school-wide Knowledge record with no individual subject is indexed under the
School scope (and any explicitly recorded reporter/context roles), not every
child. It is
not copied under Robin and Jamie. A query for Robin first reads Robin's dated
Memberships, then includes applicable Household, School and Class scopes. This
keeps one canonical record at its true scope while making it discoverable for
each relevant child.

Every outgoing Knowledge relationship remains on the newer Knowledge record.
A small incoming-relationship lookup is additionally keyed by the target
Knowledge ID:

```json
{
  "target_knowledge_id": "knowledge_0f629d53-1ec4-42f7-8c5f-21c7a19cac42",
  "entries": [
    {
      "from_ref": {"family": "knowledge", "id": "knowledge_2ab1d913-1782-4c0a-bc10-bf94ce68e293"},
      "relationship": "corrects",
      "relationship_recorded_at": "2026-04-09T19:15:00Z"
    }
  ],
  "continuation": {"state": "exhausted"}
}
```

This lookup lets a query that finds an autumn record discover a correction or
replacement recorded after the requested autumn period. It is rebuildable from
canonical outgoing links, paged at 100 entries and covered by the same freshness
catalogue. The alternative is scanning every later Knowledge month for incoming
links, which avoids one derived lookup but is expensive across years. This is a
reverse-lookup aid, not a generic graph or separate canonical edge family.

### Freshness and completeness

A shared derived-index coverage directory lists canonical page IDs and the exact
`content_revision` for which all required entity, topic and incoming-relationship
entries were emitted.
It avoids copying the same page inventory into every topic shard. Coverage lists
are also paged at 100 entries. The indexes are complete for a requested route and
period only when:

1. the relevant small canonical page-catalogue directory has been traversed
   through explicit exhaustion;
2. every catalogue entry appears in the index coverage pages; and
3. every indexed revision equals the catalogue's current `content_revision`.

For a historical observation query, “relevant catalogue” includes later source
months through the known ingestion snapshot: a new email may describe an old
observation or correct an old claim. Do not check only the original-Date months
matching the requested observation year. The normal completeness check may
therefore read all applicable Knowledge catalogue entries, in small pages, but
not all Knowledge bodies. This metadata cost grows with history; the proposal
does not claim constant-time exhaustive search.

A missing page, mismatched revision, unfinished directory or unread coverage
page makes the index incomplete for that scope. A timestamp such as `built_at`
alone is not completeness evidence.

The shared coverage entry for a canonical page is advanced only after every
required entity/topic/incoming-relationship entry derived from that page has
been written and read back. An unknown index-write outcome leaves the older
coverage revision in place. This is ordinary verification for derived data, not
an interrupted-write repair mechanism.

When incomplete, the agent uses the index only as a candidate accelerator. It
scans the missing or changed canonical source/month pages and relevant active
task pages, following continuations. If it cannot finish within authorized
capabilities, it reports the unfinished search under the approved query-coverage
rule. It must not turn zero index hits into “none exist.” Rebuilding an index is
a normal derived-data operation, not proof that source ingestion was complete.

An interrupted canonical-page or page-catalogue write remains outside the MVP's
repair guarantee. Comparing small catalogues avoids routine body-page downloads,
but a catalogue that was not updated after an interrupted canonical change can
mask staleness. The revision mechanism does not repair or transact either write.

## From one new email to searchable information

This is the proposed agent procedure, not an executed write or a generic writer.
The two completion dimensions remain separate: a source window can be fully
listed while one email remains not ingested, or all observed emails can be fully
ingested while discovery still has another page.

1. Read instance configuration and the selected source/Drive mappings. Resolve
   the logical mailbox, child/family/school entities and existing source index.
2. Associate the individual message using approved metadata and the Q5 Date
   threshold. A known complete email's later-match skip rule still awaits Q6;
   a new reply is independently identified.
3. Read the whole body and required attachment material for the email being
   ingested. Extract substantive claims, dates, exceptions and finite/recurring
   action requirements. Do not use content to decide email/attachment identity.
4. Assign each claim its real applicability. A family science-night notice can
   produce a school-wide event statement, one household RSVP obligation and a
   child-specific accommodation, each with the same source evidence but its own
   scope. Never infer a separate task per child from a household-wide request.
5. Resolve entity and topic references. Preserve ambiguous names or dates as
   unresolved; do not merge similarly named children. Relate corrections only
   when evidence supports them. Maintain one independently completed task per
   actual obligation, with parent state preserved.
6. Write and read back the affected canonical source, attachment, Knowledge and
   Task pages in bounded pieces. Update/read back their page-catalogue and locator
   entries; update the affected derived indexes and their coverage evidence.
   No atomic multi-file save or repair after interruption is promised.
7. Save the email's `fully_ingested` outcome only after required content and
   substantive/source results are verified. A failed required part means
   `not_ingested`; this does not create a part-resume workflow. Discard accessible
   temporary raw copies only after verified persistence.
8. Record completed or unfinished discovery windows separately. New questions
   use canonical records through the indexes; optional task-app synchronization
   uses the shared adapter and its own readback. Task-app failure does not erase
   canonical knowledge or falsely become a successful app sync.

Index freshness remains its own check. If a derived index cannot be updated,
retain its older coverage revision and disclose or use the canonical fallback;
do not turn that failure into silently complete indexed search.

## Narrow query traces

### “How has Robin's math teacher's feedback evolved this school year?”

1. Resolve `Robin` through the Entity directory within the configured household.
   More than one compatible entity is ambiguity, not a first-name match.
2. Resolve `math` and `teacher-feedback` through Topic labels/aliases and expand
   declared broader-topic links such as `fractions` → `math`. Do not treat the
   related terms as synonyms.
3. Read Robin's Membership history for the requested school-year interval.
   Collect the Household, School and Class scopes that overlap that interval,
   including dated teacher relationships when established.
4. Build two candidate sets. The direct-feedback set requires Robin as the
   Knowledge scope anchor, an explicit `listed_entity_refs` member, or the
   `subject` entity role. The context set uses applicable Household/School/Class
   scope and is kept separately. A sibling's feedback record with Jamie as
   subject is excluded even if it shares the same school, teacher and topics.
5. Intersect direct candidates with the expanded math and teacher-feedback topic
   shards. Also review the relevant Robin/scope/year candidates semantically so
   a fractions-only tag cannot make the topic result appear complete.
6. Validate index coverage against the current small page catalogues. Scan any
   missing or stale source/month pages; include `open_interval` and
   `unknown_interval` shards so an older continuing guideline is not missed.
7. Read the actual Knowledge records. Keep observations, qualifications, source
   dates, observation/effective dates and reporter roles. Exclude records whose
   membership/applicability interval does not overlap Robin's. Present shared
   school context separately from direct teacher observations.
8. Follow outgoing links and consult the incoming-relationship lookup for each
   selected Knowledge ID, even when the later relationship was recorded outside
   the requested year. Apply explicit `corrects`, `replaces`, `supports` and
   `conflicts_with` links. Do not interpret chronological improvement as
   correction; the fictional autumn difficulty and spring independence
   observations both remain true.
9. Check source discovery and email-level ingestion coverage for the requested
   school/source/year scope. Any relevant email marked `not_ingested` makes that
   coverage gap explicit.
10. Answer as a dated trend with citations and qualifications. Mention relevant
   open Tasks separately; do not turn feedback into a task unless its supporting
   Knowledge has an actionable disposition.

No step requires loading all instance history, vector search or a live source
read when saved verified Knowledge and sufficient coverage answer the question.

### Household, school and shared-task lookup

For “What applies to both children at Pine School, and what do we still need to
do?” the agent:

1. resolves the household, Pine School, Robin and Jamie entities;
2. verifies each child's overlapping Pine School Membership;
3. reads Pine School and Household entity-index shards for the requested period,
   plus direct child shards;
4. reads canonical Knowledge and filters applicability against membership dates;
5. reads the active-task directory and entity-index task candidates;
6. returns the school-wide Knowledge once, not once per child; and
7. returns the fictional emergency-contact Task once because its completion
   subject is the household, while listing Robin and Jamie as beneficiaries.

If Pine School required one submission per child, the two independently
completed Tasks would both appear. If task-app synchronization is stale or
failed, the answer uses verified canonical Task state and discloses the app-state
limit rather than title-matching remote tasks.

## Alternatives and tradeoffs

### Mostly free-text records

Free text is easier to author initially and harder for another agent to filter,
join and qualify consistently. It weakens stable cross-agent task sync and makes
scope-aware historical questions expensive. The proposed fields retain agent
reasoning for interpretation while persisting its result explicitly.

### Duplicate school-wide knowledge and tasks under each child

Duplication makes a child folder easy to browse, but corrections, provenance and
completion can diverge. It also creates two tasks for one household obligation.
True-scope storage plus dated Membership expansion costs extra index reads and
preserves one canonical meaning.

### Free-text tags only

Tags are simple but can confuse equal names, miss exact synonyms and lose
teacher/school changes over time. Stable Entity/Topic IDs require small
directories and explicit alias decisions, but do not require a large ontology.

### Separate relationship records

A dedicated edge family handles very high relationship counts, but adds another
directory and more reads. The recommendation stores one-way evidenced links on
the newer Knowledge record and derives only the small incoming lookup needed for
reverse discovery. If a link list would exceed its bounded page, the record may
use D1-style numbered relationship segments linked to the same Knowledge ID; no
generic graph service is needed.

### Full scans only

Scanning every source/month Knowledge page avoids index maintenance and becomes
costly as years accumulate. The proposed indexes accelerate the normal query and
retain a deterministic scan fallback. No throughput, latency or Drive-cost claim
is qualified before user-directed testing.

### Database, full-text or vector service

These could improve search but create a second operational dependency and risk a
parallel source of truth. They are unnecessary for the proposed household-scale
bounded indexes and are not selected.

## Remaining limitations and decisions not answered here

- This contract is unapproved until the user decides Q1 and Q2. Publication does
  not authorize implementation, migration, tests or live operations.
- Q3's run-start cutoff and Q5's known-timezone, second-or-finer original-Date
  threshold are approved constraints. Q6's binary email-level ingestion state is
  also approved. Q4's exact discovery mechanism and Q6's repeated-appearance
  content-reuse rule remain separate unapproved decisions; this proposal does
  not choose when prior coverage may be reused.
- A silently capped or incomplete source cannot be made complete by an index.
  Source discovery, body processing and attachment processing remain distinct.
- Alias resolution and topic assignment require semantic judgment. An index can
  miss a concept that was never assigned; the fallback and coverage disclosure
  remain necessary.
- Household membership, enrollment and teacher relationships may have imprecise
  dates. Unknown intervals remain unknown and can widen or qualify a query.
- The proposal does not define concurrent writes. The approved household scope
  assumes no simultaneous mutation of the same Drive data.
- D2 interrupted-write repair and the separate generic record/save framework
  remain outside the MVP. The proposed page revision is index evidence, not a
  substitute repair engine.
- D7 job/scheduler management and D8 packaging/migration machinery remain
  deferred. `schema_version` identifies this proposed initial shape but does not
  provide an upgrade process.
- Actual Drive connector behavior, page costs, search latency, task-app fields
  and fresh-agent performance are unqualified. No fictional example here was
  executed, simulated or validated.

## Approval effect

If Q1 and Q2 are approved, dependent implementation may encode these exact
families, fields, reference rules, directories and indexes within approved D1
pages and D5 meanings. Approval would not authorize tests, live source reads,
connector probes, ingestion, task effects, brief delivery, a generic writer or
interrupted-write recovery. The agreed implementation must still be published
and remotely verified, then stop for the user's separate testing direction.
