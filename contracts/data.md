# Retained data contract

This is the operational School-OS data contract. Agents that create, read, or
change retained data must follow it. It defines bounded JSON records and
lookups; it does not define a generic writer, transaction manager, recovery
engine, database, or migration system.

## Page envelope and limits

Every retained page is UTF-8 JSON and begins with the same identity and revision
fields:

```json
{
  "instance_id": "inst_<uuid-v4>",
  "family": "knowledge",
  "page_id": "page_<uuid-v4>",
  "schema_version": "1",
  "content_revision": 1
}
```

- `instance_id`, `page_id`, `family`, and `schema_version` are required strings.
- `content_revision` is a positive integer. Increment it for each successfully
  changed retained page. It is freshness evidence, not a lock or repair chain.
- A canonical-family page adds required `records`, containing only records of
  the declared family. A directory, catalogue, or derived-index page instead
  adds its contract-specific key or route, required bounded `entries`, and
  `continuation`; it does not also require `records`.
- The **current maximum encoded page size** is the shared contract parameter
  `64 KiB` (65,536 bytes). Every encoded page, including its envelope, must
  remain at or below that maximum.
- Directory and index pages contain no more than 100 entries. They use a
  required `continuation` object: `{"state":"exhausted"}` or
  `{"state":"continues","next_page_id":"page_<uuid-v4>"}`.
- Roll over or split pages between complete records or entries before either
  bound is exceeded. More pages extend capacity; the bounds are not history
  caps.
- The maximum is an upper bound, not a target page size. A later increase would
  permit larger pages; it would not require every page to be large or require
  existing pages to be merged or rewritten.
- Never truncate meaning or split a field away from its owning record to fit a
  page. If one complete required record cannot fit on an otherwise empty page,
  do not invent another representation or claim a partial save or completed
  ingestion. Report the complete page's observed encoded byte count and the
  minimum page size required to retain it, and leave the affected operation
  incomplete under the current shared maximum.

### Temporary bootstrap validation input

Setup derives a finite temporary manifest from the selected Source Accounts and
initial source scope. Each manifest item names one logical role, its root
`page_id`, the expected approved `family`, and the exact applicable route key:
`locator_key`, `route`, `directory_key`, or `index_key`. This manifest is not a
canonical record, is never saved as instance state, and does not define a fixed
route count. Later source/month routes continue to be created through ordinary
storage when first needed.

Before setup completes, reread the exact UTF-8 bytes for every manifest root and
every contract-defined page reference reachable from those roots. Validate the
expected instance and schema revision; approved family and route keys; page and
entry bounds; unique, nonconflicting page IDs; explicit continuation; and
referenced target family/route. Missing readback is insufficient evidence.
Observed malformed or conflicting saved state is invalid. Only a valid saved
graph completes the bootstrap check. The helper may perform this comparison but
must not access Drive, choose the manifest, create pages, repair state, or retain
the temporary manifest or diagnostics.

## References and identity

Every canonical record has one School-OS-owned UUID v4. A readable family
prefix may precede it. IDs are never derived from names, provider IDs, content,
hashes, or connector output.

The configuration record is identified by its `instance_id`; every other
canonical record uses its declared family ID field.

```json
{
  "family": "entity",
  "id": "entity_<uuid-v4>",
  "page_hint": "page_<uuid-v4>"
}
```

`family` and `id` define reference equality. `page_hint` is optional and
replaceable. Resolve a reference by checking the hinted page and verifying the
ID, then the family locator, then the bounded family directory. Preserve an
explicit unresolved result if no canonical record can be found.

Provider and Drive handles belong only in `access_aids`. They locate current
objects; they never establish record identity, equality, ingestion, or task
completion. A local `candidate_ref` inside one Attachment Group is not a
canonical ID.

## Value and date rules

- System IDs, `family`, and `schema_version` cannot be unknown.
- A required real-world value that the source does not establish uses
  `{"state":"unknown","reason":"..."}`.
- Omit an optional field only when its concept does not apply.
- An empty string is valid only when the source explicitly supplied one.
- An empty array means the complete relevant inventory contains zero members.
  Use an explicit `unknown` or `partial` state for an unknown or partial list.
- Do not use `null` in canonical records.
- Use booleans only for genuinely two-valued statements.

A known date is:

```json
{"state":"known","value":"2026-03-10","precision":"day","meaning":"observation_date"}
```

A known instant also carries the supplied timezone:

```json
{"state":"known","value":"2026-03-10T08:15:23-07:00","precision":"second","timezone":"-07:00","meaning":"original_email_date"}
```

Preserve the source's meaning, precision, and timezone. Do not manufacture a
timezone for a date that lacks one. `recorded_at` is the instant the agent
authored the values before saving. A `verified_at` in evidence is when the agent
completed the named source, content, or remote readback. After saving the final
page, perform the normal readback and compare the intended values; that readback
does not cause another timestamp write. A necessary supported re-read is not
forbidden, but it does not create a new persistence meaning or repair protocol.

## Canonical families

The canonical families are `configuration`, `source_account`, `entity`,
`topic`, `membership`, `email`, `attachment_group`, `ingestion_coverage`,
`discovery_window`, `knowledge`, and `task`. Derived families are
`record_locator`, `page_catalogue`, `entity_index`, `topic_index`,
`incoming_relationship_index`, and `index_coverage`.

### Instance configuration

A configuration record contains:

- `instance_id`: the instance's School-OS identity;
- `household_entity_ref`: required Household Entity reference;
- `household_timezone`: parent-selected display and planning timezone;
- `source_accounts`: bounded Source Account references;
- `entity_topic_roots`: an object containing required page-ID strings
  `entity_directory_page_id`, `membership_directory_page_id`,
  `topic_directory_page_id`, `entity_index_directory_page_id`,
  `topic_index_directory_page_id`,
  `incoming_relationship_index_directory_page_id`, and
  `index_coverage_directory_page_id`;
- optional `access_aids`, clearly separated from logical Source Account and
  record identity;
- optional `selected_task_projection` with `adapter_ref`, parent-selected
  `connection_label`, and `supported_field_mapping` when a task tool is
  configured;
- optional `selected_brief_recipes`, a complete array of selected recipe
  references; and
- optional `authorized_destinations`, a complete array of parent-authorized
  destination descriptions. Its absence grants no send authority.

This is operating configuration, not a connector, job, or credential registry.

The nested shape is:

```json
{
  "instance_id": "inst_<uuid-v4>",
  "household_entity_ref": {"family": "entity", "id": "entity_<uuid-v4>"},
  "household_timezone": "America/Los_Angeles",
  "source_accounts": [
    {"family": "source_account", "id": "source_account_<uuid-v4>"}
  ],
  "entity_topic_roots": {
    "entity_directory_page_id": "page_<uuid-v4>",
    "membership_directory_page_id": "page_<uuid-v4>",
    "topic_directory_page_id": "page_<uuid-v4>",
    "entity_index_directory_page_id": "page_<uuid-v4>",
    "topic_index_directory_page_id": "page_<uuid-v4>",
    "incoming_relationship_index_directory_page_id": "page_<uuid-v4>",
    "index_coverage_directory_page_id": "page_<uuid-v4>"
  },
  "access_aids": [
    {
      "adapter_ref": "system/tool-adapters/<selected-mail-tool>",
      "connection_label": "Parent-selected mail connection",
      "provider_handle": "replaceable-connection-or-container-handle",
      "observed_at": "2026-03-12T17:00:00Z"
    }
  ],
  "selected_brief_recipes": ["system/<selected-recipe>"],
  "authorized_destinations": ["parent-authorized destination description"]
}
```

`access_aids`, `selected_task_projection`, `selected_brief_recipes`, and
`authorized_destinations` are optional. The example access values do not grant
authority; they retain choices already made through setup. When present,
`selected_task_projection.supported_field_mapping` is the selected shared
adapter's mapping, not a new canonical schema or provider credential.

### Entity

```text
entity_id       required School-OS ID
entity_kind     household | child | person | school | class_or_group
display_name    required parent-readable string
aliases         required complete array of exact aliases
origin          required source/configuration description
recorded_at     required authored instant
```

Aliases support resolution within one instance and never silently merge
entities. A teacher is a `person`; a dated teacher relationship is Membership.

### Topic

```text
topic_id            required School-OS ID
label               required human-readable label
aliases             required complete array of exact synonyms
broader_topic_refs  required complete array of Topic references
origin              required source/configuration description
recorded_at         required authored instant
```

Aliases must have the same meaning. Related concepts are distinct topics.
Co-tag source-supported specific, broad, and purpose concepts such as
`fractions`, `math`, and `teacher-feedback`. Declared broader links support
expansion; they are not automatic synonyms or an ontology.

### Membership

```text
membership_id  required School-OS ID
subject_ref    required Entity reference
role           household_member | student | class_member | teacher
container_ref  required Entity reference
valid_interval required object
origin         required source/configuration description
evidence_refs  required complete array of Knowledge references
recorded_at    required authored instant
```

`valid_interval.start` is a known or explicit unknown date. Its `end_state` is
`ongoing`, `ended`, or `unknown`; `ended` also requires `end`. Absence of an end
does not prove `ongoing`. Empty `evidence_refs` is allowed only for a
parent-declared configuration relationship.

## Source and ingestion records

### Source Account

A Source Account contains `source_account_id`, a parent-readable `label`, a
tool-independent `logical_mailbox_identity`, `configured_scope`,
`import_boundary`, and `adapter_ref`. It stores no credential. Current connector
or provider handles remain replaceable configuration `access_aids` and do not
define the account's identity.

```json
{
  "source_account_id": "source_account_<uuid-v4>",
  "label": "Parent-readable school mailbox label",
  "logical_mailbox_identity": "Parent-selected logical mailbox",
  "configured_scope": "Parent-selected school/source scope",
  "import_boundary": {
    "state": "known",
    "value": "2025-08-01",
    "precision": "day",
    "meaning": "configured_import_start"
  },
  "adapter_ref": "system/tool-adapters/<selected-mail-tool>"
}
```

### Email

An Email contains:

- `email_id` and `source_account_ref`;
- `observed_metadata`: original subject, sender, original Date, received time
  when exposed, To/Cc roles, and original attachment names/count when exposed;
- `comparison_metadata`: separately normalized subject, reliably extracted
  address parts, comparable recipients, and UTC original instant;
- `association`: `resolved` or `unresolved`, plus a complete
  `pending_candidate_refs` array;
- optional replaceable `access_aids`;
- `coverage_ref` to its Ingestion Coverage; and
- `recorded_at`.

Email identity uses the separately retained observed and comparison metadata.
It never uses provider IDs,
thread IDs, body text, hashes, or MIME structure. Replies are separate Emails.
Automatic association requires all approved metadata and coverage checks,
including an original Date with known timezone and second-or-finer precision.
Multiple compatible candidates remain unresolved.

The complete nested Email shape is:

```json
{
  "email_id": "email_<uuid-v4>",
  "source_account_ref": {"family": "source_account", "id": "source_account_<uuid-v4>"},
  "observed_metadata": {
    "subject": "Family science night",
    "sender": "School Office <office@school.example>",
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
    "sender": {"local_part": "office", "domain": "school.example"},
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
      "adapter_ref": "system/tool-adapters/<selected-mail-tool>",
      "provider_handle": "replaceable-message-handle",
      "observed_at": "2026-09-15T16:20:00Z"
    }
  ],
  "coverage_ref": {"family": "ingestion_coverage", "id": "coverage_<uuid-v4>"},
  "recorded_at": "2026-09-15T16:21:00Z"
}
```

`observed_metadata.subject` and `sender` preserve the original observed strings.
`recipients.state: "known"` means both role inventories are complete; `cc: []`
means a complete zero-member Cc inventory. Unknown or partial recipients use an
explicit state rather than empty arrays. `attachment_inventory.state:
"known_complete"` means `original_names` is the complete comparable original-name
inventory, including repeated names; its array length is the count for that
complete comparable inventory. The approved nested shape adds no separate count
alias. `comparison_metadata.sender`, `to`, and `cc` contain only reliably
extracted local/domain parts. The UTC
`original_date_instant` does not replace the preserved source Date.

`association.state` is `resolved` only for a completed supported association or
new-record decision. An unresolved observation uses `unresolved` and retains all
compatible School-OS Email references in `pending_candidate_refs`; it never
chooses one by order. `access_aids` is optional.

### Attachment Group

An Attachment Group contains:

- `attachment_group_id` and `email_ref`;
- `original_filename`, known or explicit unknown;
- `inventory_scope`;
- `candidates`, each with a group-local `candidate_ref`, current `access_aid`,
  and `ingestion_evidence`;
- `required_for_full_ingestion` with `state` equal to `required`,
  `not_required`, or `unknown`, plus a source-grounded `reason`; and
- `recorded_at`.

Group same-name candidates under the same parent Email. A generated download
name is not an original filename. `not_required` is valid only when evidence
places the material outside configured substantive scope. `unknown` blocks
full ingestion.

### Ingestion Coverage

An Ingestion Coverage record contains:

- `coverage_id` and `email_ref`;
- `body_ingestion_evidence`;
- `attachment_inventory` with `state` and complete `group_refs`;
- `required_attachment_group_refs`;
- `ingestion_state`: `fully_ingested` or `not_ingested`; and
- `evaluated_at`.

The completed nested shape is:

```json
{
  "coverage_id": "coverage_<uuid-v4>",
  "email_ref": {"family": "email", "id": "email_<uuid-v4>"},
  "body_ingestion_evidence": {
    "state": "processed_saved_verified",
    "knowledge_refs": [
      {"family": "knowledge", "id": "knowledge_<uuid-v4>"}
    ],
    "verified_at": "2026-09-15T16:25:00Z"
  },
  "attachment_inventory": {
    "state": "complete",
    "group_refs": [
      {"family": "attachment_group", "id": "attachment_group_<uuid-v4>"}
    ]
  },
  "required_attachment_group_refs": [
    {"family": "attachment_group", "id": "attachment_group_<uuid-v4>"}
  ],
  "ingestion_state": "fully_ingested",
  "evaluated_at": "2026-09-15T16:26:00Z"
}
```

An established empty body still uses `processed_saved_verified` with a complete
empty `knowledge_refs` array. A complete zero-attachment inventory uses
`{"state":"complete","group_refs":[]}` and an empty
`required_attachment_group_refs`. When evidence or inventory is unknown or
partial, preserve that explicit value state under the shared value rules and set
`ingestion_state` to `not_ingested`; only the exact complete states above satisfy
full ingestion.

The body or candidate evidence state `processed_saved_verified` carries the
resulting `knowledge_refs` and `verified_at`. `fully_ingested` is valid only
when the individual body, including an established empty body, was processed;
its Knowledge was saved and read back; attachment inventory is complete; every
group's requirement is known; and every required group was processed with its
Knowledge saved and read back. Otherwise use `not_ingested` and report the
blocking reason operationally. Do not retain a partial-email resume state.

`processed_saved_verified` is a semantic claim, not merely a byte-persistence
claim. Before using it, build a temporary source-bound checklist from the actual
body or candidate: every substantive statement, qualification, correction,
date and date role, request, condition, recurrence rule, applicable person or
group, action disposition, and independent completion unit. Reread the saved
Knowledge and applicable Tasks and compare their meaning with that independent
checklist. Missing or changed meaning keeps the whole Email `not_ingested`.
Discard the checklist after a successful comparison; it is not another record.

A directly embedded remote image that visibly carries substantive information
may be read once through an authorized least-stateful route. Its extracted
claims remain part of the parent Email body: use `part: "body"` and a descriptive
image location in the Knowledge source reference. The remote locator is an
optional replaceable access aid, never Email identity or evidence of successful
processing, and the image does not become an Attachment Group. Do not crawl,
sign in, submit a form, or retain the raw image. Unsupported, inaccessible,
unauthorized, or uncertain access keeps the Email `not_ingested`, with those
outcomes kept distinct operationally.

A unique, sufficiently supported metadata match to an existing
`fully_ingested` Email reuses that result and skips its body and attachments.
Explicit new or contradictory inventory or coverage evidence reopens the Email
as `not_ingested` until the whole Email satisfies the binary rule. A changed
provider handle or unknown optional metadata alone does not reopen it. A reply
is a separate Email. This rule adds no content hash or appearance ledger.

### Discovery Window

A Discovery Window contains:

- `window_id`, `source_account_ref`, `scope_description`, and `school_refs`;
- `time_basis`, and `start`/`end` with value, precision, timezone, and boundary
  inclusivity;
- `discovery_state`: `unfinished` or `complete`;
- `observed_email_refs`, pointing to bounded source-index pages and an explicit
  continuation state;
- `verification`, with observation time and route limitation/evidence summary;
- optional temporary `access_aids`.

```json
{
  "window_id": "window_<uuid-v4>",
  "source_account_ref": {"family": "source_account", "id": "source_account_<uuid-v4>"},
  "scope_description": "Parent-selected school correspondence in the configured mailbox",
  "school_refs": [{"family": "entity", "id": "entity_<uuid-v4>"}],
  "time_basis": "source_received_time",
  "start": {
    "value": "2026-09-14T06:00:00-07:00",
    "precision": "second",
    "timezone": "-07:00",
    "inclusive": true
  },
  "end": {
    "value": "2026-09-15T06:00:00-07:00",
    "precision": "second",
    "timezone": "-07:00",
    "inclusive": true
  },
  "discovery_state": "complete",
  "observed_email_refs": {
    "source_index_page_ids": ["page_<uuid-v4>"],
    "continuation": {"state": "exhausted"}
  },
  "verification": {
    "observed_at": "2026-09-15T13:05:00Z",
    "evidence_summary": "Selected route exhausted all continuation pages for this window"
  }
}
```

Each `source_index_page_ids` item is the root of a bounded directory chain made
only for this Discovery Window. The directory pages reuse `record_locator`
shape: `family: "record_locator"`, `locator_key.canonical_family: "email"`,
bounded `entries` of exact `record_id`/canonical `page_id` pairs, and explicit
`continuation`. Do not share one such directory chain between windows. Within a
canonical Email page, include only the Email whose ID appears in the window
directory entry; other Email records on that source/month page are not observed
by implication. Resolve each entry and verify its `source_account_ref` and the
window's saved scope evidence. `observed_email_refs.continuation` records whether
all saved window-directory chains were traversed to exhaustion; it does not
replace `discovery_state` or certify provider-route exhaustion.

A zero-result exhausted window uses `source_index_page_ids: []` and
`continuation.state: "exhausted"`. An unfinished stored directory uses the
existing `continues` form with `next_page_id`. Lost provider continuation remains
an optional `access_aids` concern and leaves `discovery_state: "unfinished"`;
it does not change Email identity or directory membership.

Completion means the selected route was exhausted for the declared window; it
does not certify invisible provider material or Email ingestion. Normal daily
discovery begins at the last completed arrival-time boundary, inclusive at the
route's actual precision, and ends at run start. It also finishes known
unfinished windows and known `not_ingested` backlog through run start. Follow
all continuations. Arrival time controls discovery; original Date controls
Email identity and canonical month. Do not impose a whole-history scan or fixed
overlap. The accepted limitation is that newly visible material in an older
completed arrival window can be missed unless a parent requests a historical
rescan.

## Knowledge records

A Knowledge record contains:

```text
knowledge_id        required School-OS ID
knowledge_kind      fact | guideline | update | observation
statement           required complete string
qualifications      required complete array
scope               required applicability object
entity_links        required complete array of {role,ref}
topic_refs           required one or more Topic refs, or explicit unresolved state
source_refs          required evidence array; exactly one primary
dates                required complete array preserving each date meaning
action_disposition   none | finite | conditional | recurring
relationships        required complete array
recorded_at          required authored instant
```

`statement` remains one whole string on its owning Knowledge record.
`qualifications` and `relationships` remain complete arrays on that same record.
The complete record is subject to the shared page maximum and its oversized-record
rule; no linked-piece or field-segmentation format is part of this contract.
`scope` contains `anchor_ref` and one applicability mode:

- `anchor_only`: applies to the anchor itself;
- `listed_entities`: requires a complete `listed_entity_refs` array, and every
  listed Entity is indexed; or
- `members_at_effective_time`: requires `membership_role`, and applicability is
  determined from Membership overlap at the effective interval.

Store meaning once at its true scope. A school guideline stays at School scope;
a household rule stays at Household scope; a Robin-only observation stays at
Robin scope. An instance remains household-owned even when it contains School
entities.

Each `source_refs` entry identifies the `email_ref`, `part` (`body` or
`attachment`), a readable `location`, and `primary`. An attachment source also
requires `attachment_group_ref` and its group-local `candidate_ref`. Primary
source original Date month determines the canonical Knowledge route. Preserve
all sources.

Classify source action meaning before deriving Tasks:

| Source meaning | `action_disposition` | Canonical Task result |
|---|---|---|
| Information or optional guidance | `none` | No source-derived Task. |
| One-time obligation | `finite` | One Task for each independently completable unit. |
| Obligation that applies only if a stated condition holds | `conditional` | Conditional Task(s) preserving that condition and completion unit. |
| Ongoing repeating obligation | `recurring` | One recurring series plus independently completable projected occurrences under the existing projection rule. |

Importance alone never establishes an obligation. One household submission is
one Task; one independently completed submission per child is one Task per
child. If the existing fields cannot preserve the source meaning, leave the
Email incomplete and report the representation gap rather than changing the
classification or cardinality.

Every substantive source date or time appears in `dates` with its own role,
value, precision, and source-supplied timezone when present. Original Email
Date, response deadline, event timing, effective timing, recurrence timing, and
parent planning are distinct. A correct value stored under the wrong role is a
semantic failure. Do not fill an unstated year, time, or timezone. A later
correction preserves both observations and the evidenced relationship.

An outgoing relationship is stored on the newer record and contains
`relationship` (`supports`, `corrects`, `replaces`, or `conflicts_with`),
`target_ref`, `evidence_refs`, and `justification`. Use `corrects` only when
evidence establishes that the earlier claim was wrong. Chronological
development can leave both observations true. Use `replaces` for a prospective
rule change, `conflicts_with` for unresolved disagreement, and `supports` for
additional evidence.

## Task records

A Task contains:

- `task_id`;
- `origin`: `source_derived` or `parent_created`;
- `action` and `context`;
- `scope_ref`;
- `source_context_refs` (complete; may be empty for a personal task);
- `completion_subject_ref`;
- `beneficiary_refs` (complete or explicit unknown);
- `supporting_knowledge_refs` (complete; may be empty for a parent task);
- `action_kind`: `finite`, `conditional`, `recurring_series`, or
  `recurring_occurrence`;
- optional `series_ref` on an occurrence;
- optional `school_timing` only when source timing applies;
- `parent_state`;
- `task_sync`; and
- `recorded_at`.

One Task represents one independently completed obligation. One household
submission for siblings is one household Task with both beneficiaries. A
per-child submission is one Task per child. A recurring series preserves the
rule and interval; projected occurrences have independent IDs and state.

`parent_state` contains `owner`, `planned_date`, `progress`, `completed`,
`personal_notes`, and `completion_reviews`. `completion_reviews` is a complete
array retained on the owning Task record. A completion review contains
`evidence_refs`, `detected_at`, and `state`: `awaiting_confirmation`,
`confirmed`, or `rejected`; decided reviews also preserve `decided_at` and an
optional `parent_note`. Evidence does not itself compute pending completion.
Only an awaiting entry displays **Completion detected — awaiting parent
confirmation**, while `completed` remains false. Rejected evidence does not
reopen without materially new evidence. Later receipts do not downgrade a
completed Task.

`owner` is the parent-selected owner string or an explicit unknown object;
`planned_date` is the parent-selected calendar-date string or an explicit
unknown object; `progress` preserves the selected shared task meaning as a
string; `completed` is a boolean; and `personal_notes` is a complete string
array. These parent values are not inferred from school timing.

Each `task_sync` entry contains `adapter_ref`, `connection_label`, replaceable
`access_aid`, `identity_marker_verified`, `last_verified_at`,
`last_verified_shared_values`, `last_observed_remote_values`, and
`projection_state` (`verified`, `missing`, `unknown`, or `conflict`). The
managed School-OS Task ID establishes remote identity. Title similarity does
not. These fields support three-way comparison of canonical state, the last
verified shared base, and the new remote observation without storing credentials,
request formats, or a retry engine.

The nested source-derived Task shape is:

```json
{
  "task_id": "task_<uuid-v4>",
  "origin": "source_derived",
  "action": "Confirm the household emergency-contact details.",
  "context": "One confirmation covers enrolled siblings.",
  "scope_ref": {"family": "entity", "id": "entity_<household-uuid-v4>"},
  "source_context_refs": [
    {"family": "entity", "id": "entity_<school-uuid-v4>"}
  ],
  "completion_subject_ref": {"family": "entity", "id": "entity_<household-uuid-v4>"},
  "beneficiary_refs": [
    {"family": "entity", "id": "entity_<child-uuid-v4>"}
  ],
  "supporting_knowledge_refs": [
    {"family": "knowledge", "id": "knowledge_<uuid-v4>"}
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

A parent-created Task uses `origin: "parent_created"`; established empty
`source_context_refs` and `supporting_knowledge_refs` are valid, and
`school_timing` is omitted when no school timing applies. A
`recurring_occurrence` also requires `series_ref`. Each completion-review item
uses the exact nested shape below; evidence does not create the review state by
itself:

```json
{
  "state": "rejected",
  "evidence_refs": [
    {"family": "knowledge", "id": "knowledge_<uuid-v4>"}
  ],
  "detected_at": "2026-09-16T08:10:00Z",
  "decided_at": "2026-09-16T15:30:00Z",
  "parent_note": "The evidence applied to another obligation."
}
```

`decided_at` and `parent_note` are omitted while `state` is
`awaiting_confirmation`. A task-app projection item is:

```json
{
  "adapter_ref": "system/tool-adapters/<selected-task-tool>",
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

## Directories, catalogues, and derived indexes

### Canonical routing

- Route Email, Attachment Group, and Ingestion Coverage pages by logical Source
  Account and normalized UTC month of original Date. Route unknown dates to a
  discoverable pending area.
- Route Knowledge by the original-Date month of its one primary source.
- Reach active Tasks through the paged active-task directory and completed
  Tasks through history pages.
- Use bounded family directories for Entity, Topic, and Membership.
- A `record_locator` entry maps a canonical `record_id` to its current
  `page_id`.

A `record_locator` page uses the standard identity and revision fields, then
`locator_key: {"canonical_family":"..."}`, bounded `entries` of
`{"record_id":"...","page_id":"..."}`, and `continuation`. If the locator
entry is absent or stale, do not rescan that same locator as proof of absence.
Traverse the separate bounded family-page directory or applicable canonical
page catalogue through explicit exhaustion, inspect the listed canonical pages,
and report an unresolved result if that fallback cannot complete. This is a
read fallback, not locator repair or proof that an interrupted catalogue write
was detected.

An Entity or Topic index-root directory uses the corresponding derived family,
`directory_key` equal to `entity_index_root` or `topic_index_root`, and bounded
entries of `lookup_id` plus `buckets`. Each bucket contains `time_bucket` and a
bounded `page_ids` array; split an entry across continued directory pages rather
than exceeding page limits. An incoming-relationship root uses
`directory_key: "incoming_relationship_index_root"` and entries of
`target_knowledge_id` plus `page_ids`. These are routing directories, not
substantive indexes; the bucket pages below contain canonical references.

### Page catalogue

A `page_catalogue` page replaces `records` with `route`, `entries`, and
`continuation`. `route` contains `canonical_family` and applicable
`source_account_id` and `source_month`. Each entry contains
`canonical_page_id`, `canonical_family`, `content_revision`, and the replaceable
`drive_access_aid`.

Normal save order is canonical page write/readback, catalogue write/readback,
then derived-index write/readback. These are independent writes. Interruption
can leave a catalogue stale in a way this MVP neither repairs nor always
detects.

### Entity and topic indexes

An Entity Index page uses the standard envelope plus:

```json
{
  "index_key":{"entity_id":"entity_<uuid-v4>","time_bucket":"2026-03"},
  "entries":[{
    "record_ref":{"family":"knowledge","id":"knowledge_<uuid-v4>","page_hint":"page_<uuid-v4>"},
    "matched_role":"subject",
    "date_basis":"observation_date",
    "semantic_interval":{"start":"2026-03-10","end":"2026-03-10"},
    "primary_source_month":"2026-04"
  }],
  "continuation":{"state":"exhausted"}
}
```

Index the Knowledge scope anchor, every `listed_entity_refs` member, every
entity-link role, Task scope/completion subject/beneficiaries, and Membership
subject/container.

Knowledge entries require `primary_source_month`. Membership entries use their
valid interval and omit that source-month field when no primary Knowledge source
exists. Task entries use applicable school timing or parent-planned timing; an
unknown time uses `unknown_interval`. The entry's `record_ref.family`,
`matched_role`, and `date_basis` make these meanings explicit.

A Topic Index page has `index_key.topic_id` and `time_bucket`; each entry has
`record_ref`, `matched_topic_id`, `date_basis`, `semantic_interval`, and
`primary_source_month`. Index Knowledge topics only. There is no task-topic
index: retrieve Tasks first, then filter their supporting Knowledge. Filter a
parent-created Task with no supporting Knowledge from its own action, context,
and beneficiaries.

Time buckets use semantic time:

- Observation: observation date or interval.
- Fact, Guideline, Update: effective date or interval.
- Closed interval: every overlapping month.
- Continuing guideline: its start month and `open_interval`.
- Unknown applicability: `unknown_interval`.

Canonical routing still uses source original-Date month. A March source that
reports a November observation is indexed in November and canonically stored
under March.

### Incoming relationships

An `incoming_relationship_index` page is keyed by `target_knowledge_id`. Each
entry contains `from_ref`, `relationship`, and `relationship_recorded_at`.
Outgoing links remain canonical. The incoming lookup is rebuildable and exists
only so a query can find a later correction, replacement, support, or conflict
that points into an earlier requested period.

### Index coverage and freshness

An `index_coverage` page contains bounded `entries` and `continuation`. Each
entry contains `canonical_page_id`, `canonical_family`, `content_revision`, and
`covered_indexes` listing the required derived families emitted for that page.
Advance the entry only after every required derived write and readback succeeds.

An index is complete for a route and period only when the relevant page
catalogue is traversed to exhaustion, every catalogue page appears in index
coverage, and every revision matches. `built_at` alone is not evidence.
Historical observation queries include later source months through the known
ingestion snapshot because a later source can report or correct an older event.

Missing pages, mismatched revisions, unread coverage pages, or unfinished
directories make the index incomplete. Use it only for candidates, scan the
affected canonical source/month and active-task pages, and report an unfinished
fallback if it cannot be completed. Even a fresh topic index can miss a concept
that was classified too narrowly; completeness-sensitive queries also review
the relevant entity/scope/time candidates semantically.

For one question, retain the selected page IDs only in temporary working memory
and reuse each page already read. Start from resolved Entity, Topic, time, Task,
and coverage routes; broaden to affected source/month catalogues only for a
stated stale-index, semantic-fallback, relationship, or coverage reason. This
temporary read set is not a cache or another index.

An answer citation resolves to readable canonical Knowledge and its source
location, not merely a catalogue, directory, index page, or provider handle.
Every source that changes a material claim's condition, correction,
qualification, or confidence must be cited. A completeness-sensitive negative
claim additionally requires readable discovery and ingestion coverage for the
stated scope. Omit or qualify a material claim when that support is unavailable.

## Boundaries

This contract adds no database, vector service, ontology service, credentials,
provider SDK, generic graph, task-title identity, automatic migration,
concurrent-write protocol, generic writer, or interrupted-write repair. It
does not prove source discovery complete or qualify connector behavior,
latency, throughput, or cost.
