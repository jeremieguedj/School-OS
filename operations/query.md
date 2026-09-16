# Answer questions from retained School-OS data

Use canonical records for answers and derived indexes only to find candidates.
Apply [the data contract](../contracts/data.md), verify index coverage, and cite
the retained source locations. Never convert an incomplete lookup into a claim
that no record exists.

## Common query procedure

1. Resolve the household and requested Entity IDs through configuration and
   bounded directories. First-name or title similarity is not identity.
2. Resolve Topic labels and exact aliases. Follow only declared broader-topic
   links. Keep related topics distinct.
3. Resolve the requested time interval and preserve its meaning. Read dated
   Memberships that overlap it; unknown intervals widen or qualify the result.
4. Select candidate Entity and Topic shards, including `open_interval` and
   `unknown_interval` where they could apply.
5. Validate index coverage against the exhausted canonical page catalogue.
   For historical questions, include later source months through the known
   ingestion snapshot: later mail can report or correct an earlier event.
6. If coverage is stale or incomplete, scan the affected canonical
   source/month pages and active Task pages. Report any unfinished portion.
7. Read canonical records and resolve their references. Recheck scope,
   membership overlap, semantic dates, qualifications, and sources; an index
   entry is never the answer.
8. Perform a semantic fallback over relevant entity/scope/time Knowledge for
   completeness-sensitive topic questions. A fresh topic index cannot prove a
   concept was tagged completely.
9. Follow outgoing Knowledge relationships and the incoming lookup. Preserve
   corrections, replacements, support, conflicts, and chronological evolution
   according to their explicit meanings.
10. Check discovery-window coverage and each relevant Email's binary ingestion
    coverage. A complete listing window can contain a `not_ingested` Email, and
    fully ingested observed mail does not prove discovery exhausted.
11. Read active Tasks separately. Apply topic filters through supporting
    Knowledge; for parent-created Tasks without Knowledge, use their action,
    context, and beneficiaries. Preserve canonical parent state and disclose
    task-app sync gaps.
12. Answer with dates, scope, qualifications, source citations, and coverage
    limits. Separate direct evidence, shared context, open actions, and unknowns.

## Child and topic evolution

For “How has Robin's math teacher's feedback evolved this school year?”:

1. Resolve Robin within the configured household. More than one compatible
   Entity is ambiguity.
2. Resolve `math` and `teacher-feedback`; expand explicit links such as
   `fractions` to broader `math` while keeping all topics distinct.
3. Read Robin's overlapping Household, School, Class, and teacher Memberships
   for the school-year interval.
4. Build a direct set requiring Robin as scope anchor, listed entity, or
   `subject`. Build a separate context set from applicable Household, School,
   and Class scope. Exclude a sibling-subject record from direct evidence even
   when it shares school, teacher, and topics.
5. Read matching topic shards and semantically review Robin/scope/year
   candidates so narrow tagging cannot hide relevant feedback.
6. Include old continuing guidance from `open_interval` and qualify records from
   `unknown_interval`.
7. For a late source, use semantic observation/effective time in the trend while
   preserving its later source month. Search later source-month catalogues and
   incoming relationships for retrospective observations and corrections.
8. Read canonical Knowledge and order by the meaning being discussed. Do not
   treat later improvement as correction unless an explicit evidenced
   `corrects` link says so.
9. Report a dated trend with direct observations first, shared context clearly
   labeled, and sources and qualifications attached. List actionable Tasks
   separately.

## Household, school, and shared obligations

For “What applies to both children at Pine School, and what do we still need to
do?”:

1. Resolve Household, School, and both Child Entities.
2. Verify each child's School Membership overlaps the requested interval.
3. Read School and Household shards once, plus direct child shards. Apply
   `members_at_effective_time` using the dated Membership role.
4. Return each canonical school- or household-wide Knowledge record once. Do
   not duplicate it per child.
5. Read the active-task directory and relevant Entity Index entries. A household
   Task with both children as beneficiaries appears once; per-child completion
   obligations appear separately.
6. Use canonical Task state. If remote task sync is stale, missing, unknown, or
   conflicting, state that limit rather than title-matching or substituting the
   app's value.

## Coverage language

Use precise conclusions:

- **Complete for the saved scope** only when discovery windows, binary Email
  ingestion, catalogue/index coverage, canonical reads, and semantic fallback
  all support the requested scope.
- **No matching saved record found** when search completed but source coverage
  does not establish completeness.
- **Search unfinished** with the exact missing route, period, page, or
  capability when fallback could not finish.
- **Unknown** when retained evidence does not establish the value.

Always cite the primary source and readable part/location. Include additional
sources when they affect confidence, qualification, or a relationship. Do not
cite provider handles as identity or mailbox read flags as ingestion proof.
