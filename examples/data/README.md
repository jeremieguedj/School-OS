# Fictional retained-data example

Every name, address, school, date, and identifier in this directory is
fictional. These files are written examples only; they were not ingested,
executed, simulated, or qualified.

The files form one connected slice of an instance:

1. `configuration-page.json` selects the household, source account, and bounded
   directory roots. `entity-directory-page.json` and
   `entity-index-directory-page.json` show canonical-ID and index-bucket routing.
2. `source-account-page.json`, `entity-page.json`, `topic-page.json`, and
   `membership-page.json` establish the mailbox and dated household/school
   context.
3. `discovery-window-page.json` points to the window-specific bounded Email
   reference chain in `window-email-directory-page.json`. Its one exact Email
   reference resolves into `email-page.json`; other records on a shared
   source/month page would not join the window by implication.
4. `email-page.json`, `attachment-group-page.json`, and
   `ingestion-coverage-page.json` show one wholly ingested fictional email. The
   body and required PDF both produced saved, verified Knowledge.
5. `knowledge-page.json` stores a retrospective autumn observation, a spring
   observation, and one household action guideline from that March source. The
   two observations show development; neither says the other was wrong.
6. `task-page.json` contains one household completion unit benefiting both
   children.
7. `knowledge-page-catalogue.json`, the Entity and Topic Index examples, and
   `index-coverage-page.json` show semantic-month indexing and revision-based
   freshness. The November observation is canonically stored under its March
   source month but indexed under November. The two index-page files are
   selected pages from the fictional derived set; the coverage record describes
   the full fictional derivation rather than asserting that this example
   directory contains every derived shard.

The examples deliberately do not assert that one saved email proves mailbox
discovery complete. Discovery windows and ingestion execution examples live in
the ingestion guidance. Provider and Drive handles shown here are replaceable
access aids.
