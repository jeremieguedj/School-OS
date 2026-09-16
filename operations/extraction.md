# Read a whole email and retain school meaning

Use this procedure inside [ingestion](ingestion.md) when a logical email needs
content. Read [identity](../contracts/identity.md), [data](../contracts/data.md),
[knowledge](knowledge.md) and [storage](storage.md). The agent interprets source
material through its available authorized tools; these instructions do not
require a resident process, particular model, document parser or task provider.

## Establish the complete material to read

1. Resolve the individual logical Email and its original source context. Keep
   it `not_ingested` during the work. Do not use body similarity to resolve an
   uncertain identity or a thread summary to stand in for an individual reply.
2. Read the complete individual body through a supported source route. A listing
   snippet, shortened preview or summary is insufficient. Distinguish a
   source-established empty body from unavailable text. Interpret quoted
   historical text in context; it is not automatically a new instruction from
   the current sender.
3. Establish the complete exposed attachment inventory for the selected route
   and configured source scope. Preserve original filenames and inventory
   scope. An unavailable inventory does not mean no attachments.
4. Group candidates by parent Email and original filename under the identity
   contract. Preserve every same-name candidate, unknown names and uncertainty;
   do not pick the first candidate. Current retrieval handles locate material
   but do not prove permanent physical identity.
5. Determine each group's requirement from source meaning and the configured
   substantive scope. Use `required` for relevant school material,
   `not_required` only with a source-grounded reason it lies outside that scope,
   and `unknown` if the requirement cannot be established. Cost, file size,
   inconvenient format or an uninformative filename is not an exclusion reason.
6. Read every candidate of every required group. Use appropriate supported
   text, image, document or audio interpretation tools when needed. A filename,
   generated summary or successful download alone does not establish that the
   content was read. Check for omitted pages, truncated text and meaningful
   material contained in images or tables. Meaningful embedded material must
   be processed; it is never an identity fallback.

Temporary processing copies may exist only as needed by the executing agent.
Do not make raw bodies or attachments a canonical Drive archive. If a required
format is unavailable, extraction is incomplete: preserve the source context,
report the capability limitation and keep the whole email `not_ingested`.
There is no completed partial-email or per-part resume workflow.

## Preserve what the source actually establishes

Read for substantive school information, including information with no action.
Retain enough meaning that another capable agent can answer from canonical
Knowledge without recovering the raw body merely to discover a lost exception.
For each substantive item, establish:

| Question | What to retain |
|---|---|
| What is asserted or requested? | The fact, guideline, update or observation, with its meaningful detail. |
| What qualifies it? | Conditions, exceptions, negation, uncertainty, applicability and any stated evidence limitations. |
| Who does it concern? | Its true household, child, class or school scope, and separately the reporter or other contextual entity links. |
| When does it apply? | Source original Date, observation/effective dates, deadlines and recurrence meaning separately, with actual timezone and precision. |
| Is action required? | `none`, `finite`, `conditional` or `recurring`, with the actual condition or completion requirement. |
| What supports it? | Email and body/attachment-group references, readable locations, and qualifications when a same-name group's physical member remains uncertain. |
| Does it change existing knowledge? | An evidenced correction, replacement, conflict or support relationship; otherwise a distinct dated observation. |

Do not compress a conditional requirement into an unconditional task, or a
school-wide rule into a child-specific observation. “Optional unless you request
transport” preserves both optionality and the transport condition. “No signature
is needed if the form was already submitted” must not become a request for
another signature.

Use configured entities and approved topic meanings. Do not guess which child
a pronoun names when several are plausible. Keep unresolved attribution visible.
Store school-wide or household-wide meaning once with explicit applicability;
do not copy the same claim under every child. Link child observations to that
child so a later year-long subject query can find them without treating a
sibling's result as evidence.

Retain meaningful text as one complete Knowledge `statement`, with complete
qualifications and relationships on the same owning record, as specified by
[data](../contracts/data.md#page-envelope-and-limits). Never truncate or invent
a field-splitting representation. If the complete required record exceeds the
current page maximum even on an otherwise empty page, report the observed
encoded bytes and required minimum page size, and keep the email
`not_ingested`.

## Reconcile Knowledge and action

Use [knowledge](knowledge.md) to consult relevant existing Knowledge and Tasks
through bounded indexes and supported fallback. Repeated ingestion must retain
the established source relationship and existing parent state; it does not
justify duplicating every claim or overwriting an older record in place.

- A later assessment can describe development rather than error. “Mira now
  works independently with fractions” can coexist with an earlier dated report
  that she needed help. Do not create a correction solely because dates differ.
- “The deadline in yesterday's notice was wrong; it is Friday” supports a
  correction relationship. Preserve both source dates and the corrected school
  deadline. Record the evidence rather than applying a general latest-wins rule.
- Incompatible instructions without an evidenced correction remain a visible
  conflict. Do not pick the convenient version.
- Create a canonical Task only when the source establishes action. Determine
  the independent completion unit: one household form covering siblings is one
  household task; separately required submissions are separate tasks.
- Preserve source-derived school timing independently of the parent's owner,
  planned date, progress, notes and completion. New source information can
  update the school's deadline without moving the parent's planned date.
- For recurring action, retain the series meaning and use the approved native
  recurrence or fourteen-day occurrence projection in [task sync](task-sync.md).
  Never mark an entire series complete because one occurrence was done.
- Clear evidence satisfying the exact task becomes **Completion detected —
  awaiting parent confirmation**, following [completion review](completion-review.md).
  A receipt never directly completes a task, downgrades an already completed
  task or authorizes a search of Sent mail outside configured scope.

Record `action_disposition: none` when a read item has no required action. If
the whole email yields no actions, retain its substantive Knowledge and report
that result honestly. Do not manufacture a task or request a nonexistent task
provider action merely to move to a brief.

## Attribute each result to its own source material

Every Knowledge source reference names the logical Email and its body or
attachment group, with a useful extraction location. Exactly one source is
primary for canonical month routing; supporting sources remain linked. The
primary source's original Date is not the observation/effective date of the
claim, and neither is the time School-OS processed it.

When same-parent same-name candidates contain separate relevant information,
save all of it with honestly group-qualified provenance. Do not claim an exact
physical member if permitted metadata cannot establish one. Reading one
candidate does not cover another, even if their generated names or apparent
contents look alike. Content is useful for extracting meaning, not proving
attachment identity or optional thread association.

## Save, check, and clean up

1. Save Knowledge, source references, dates, qualifications, scope, topics,
   relationships and resulting canonical Tasks under
   [the normal save sequence](storage.md#normal-save-sequence).
2. Check ordinary readback against the substantive source meaning. Confirm
   every action requirement and its disposition; do not verify an empty task
   inventory merely by rereading an empty inventory the agent just wrote.
3. Save candidate processing evidence and resulting Knowledge references.
   An empty Knowledge list is valid only after actual reading establishes no
   substantive in-scope information for that material.
4. Apply the whole-email conditions in [ingestion](ingestion.md). Save and read
   back `fully_ingested` only after body, complete inventory, known requirements
   and every required candidate satisfy those conditions. Otherwise retain
   `not_ingested`; preserve verified Knowledge and describe the remaining gap.
5. Discard accessible temporary raw copies only after verified persistence of
   the extracted information, source links and processing state. If persistence
   is unverified, do not claim successful cleanup after a complete ingestion.
   If an agent loses temporary resources, the source remains the reread route;
   local material is never the critical recovery record.

External task projection and brief delivery are separate authorized operations.
This extraction procedure supplies canonical information; it does not send
messages or silently repair an interrupted set of canonical writes.
