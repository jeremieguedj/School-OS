# Fictional remediation acceptance cases

Status: **written, not run or qualified**. Every person, school, message, date,
route and identifier below is invented. These are independent source oracles for
later user-authorized checks, not canonical records, new schemas, model prompts,
or evidence about a provider.

## Source-to-saved meaning

Fictional source: “Return Robin's vaccination form by September 20. Families
who already submitted it do not need to respond.” The temporary source checklist
contains the request, Robin-only scope, September 20 response deadline and the
already-submitted exception. A saved result missing any one of those meanings
fails semantic comparison and leaves the Email `not_ingested`. A result that
preserves all four in reread Knowledge and the applicable Task passes this case.

Repeat the same comparison independently for: “Upload one reading log for each
child every Friday while enrolled.” Dropping the recurrence, enrollment
condition, per-child completion unit, or Friday timing fails. The checklist is
discarded after a passing comparison and is never saved as instance data.

## Action classification and cardinality

| Fictional source | Expected Knowledge | Expected Task inventory |
|---|---|---|
| “Students may bring a hat.” | `action_disposition: none` | No Task. |
| “Submit one household emergency-contact form for both children.” | `finite` | One household-completion Task with both beneficiaries. |
| “Return one signed consent form for Robin and one for Alex.” | `finite` | Two Tasks, one completed independently by each child/person. |
| “Bring lunch only if your child does not receive a school meal.” | `conditional` | Conditional Task(s) retaining that condition and the applicable completion subject. |
| “Upload one reading log per child every Friday while enrolled.” | `recurring` | A recurring series and independent projected occurrences under the existing 14-day rule. |

Importance does not alter these results. The expected inventory is derived from
the fictional source before inspecting tested output.

## Date roles

Fictional source: “Reply by September 12 for the museum visit on September 28.
Buses leave at 8:15 AM.” The expected saved meaning contains a response
deadline, event date and departure time as three distinct roles, preserving each
stated precision and leaving any unstated year or timezone unknown. “When must I
reply?” returns September 12. Substituting September 28 or storing September 12
as an event date fails even though the value itself appeared in the source.

## Narrow query and claim evidence

For “How has Robin's math feedback evolved this year?”, the ordinary plan
resolves Robin, math/fractions, teacher feedback and the school-year interval;
reads only matching Entity/Topic buckets, their canonical Knowledge, incoming
or outgoing relationships, relevant coverage and active Tasks; and reuses every
page read during the question. A stale March topic-index coverage entry causes
predictable broadening to the affected March source/month catalogue. It does not
justify scanning unrelated lunch, sports or sibling routes.

Draft answer: “Robin is improving in fractions, but the teacher still recommends
multiplication practice.” Treat these as two material claims. Each needs its
readable Knowledge and source location; cite any qualification or correction
that changes either claim. A catalogue containing their page IDs is routing
evidence and does not satisfy the claim citations. “No later correction was
found” also requires complete readable discovery and ingestion coverage through
the stated cutoff, or the conclusion must be qualified.

## Directly embedded substantive image

Fictional parent Email body displays an embedded image reading “Picture Day:
October 4. Order forms due September 27.”

- With an authorized reachable route, perform one least-stateful image read,
  preserve both date roles and any source-established action, cite the parent
  Email body with a descriptive image location, discard temporary pixels, and
  complete coverage only after semantic readback passes.
- With an authorized route that returns an unavailable result, retain that
  reason and keep the whole Email `not_ingested`.
- When authority is unknown, do not fetch. Retain the distinct authority gap and
  keep the Email `not_ingested`.

No variant crawls another link, signs in, submits a form, converts the image to
an Attachment Group, uses its URL or bytes for Email identity, or stores the raw
image in School-OS.
