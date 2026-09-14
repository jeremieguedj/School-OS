# Metadata-only live stress-test protocol

This is a bounded, user-authorized, read-only development study of the connected
Gmail account. It is not installation, ingestion into a private School-OS
instance, a scheduler run, or an assertion about other vendors' agents.

## Evidence and privacy

The collecting agent preserves complete request/response receipts before
normalization in a gitignored private run directory with directory mode 0700
and file mode 0600. No email address, subject, timestamp, filename, source ID,
source URL, snippet or raw error is published. Public reports contain aggregate
counts and file/code bindings only; the private audit links individual trials
to the exact observations used.

Use search results and individual `metadata` reads. Do not fetch full messages,
raw MIME, threads with body content, or attachment bytes. Some responses
incidentally include snippets; preserve them only as part of the complete
private connector receipt and never inspect or use them for this study.

Keep source metadata and a separate test reference in different files.
Native Gmail IDs support private test construction, observation pairing and
grading, including catalog seeding and repeated/distinct entry labels, for this
snapshot audit only. They are excluded from matcher inputs, saved matching
records and decisions. This tests consistency with Gmail's observed identities,
not an independent proof of physical delivery identity or ID permanence.
Gmail thread IDs similarly provide a comparison grouping, not exact parentage
truth or an identity discriminator.

## Model chosen before evaluating the live outcomes

The development [model](model.py) makes the previously unspecified acceptance
rule explicit: automatic association requires a verified logical mailbox,
original subject, sender address and an exact timezone-known source timestamp.
It uses source sending time; an independently understood receipt timestamp is
an alternate same-meaning route when sending time is unavailable. Sending and
receipt timestamps never substitute for each other.

For this conservative baseline, exact means second precision; minute/day
overlap is candidate evidence and yields an unresolved result. That is a test
policy, not a universal uniqueness property or a claim that second precision is
available everywhere. UTC day degradation is tested; local calendar days that
cross daylight-saving changes are not qualified by the fixed-duration interval
representation in this small model.

Optional To/Cc fields compare complete role-specific addresses. Partial or
incomparable lists must be mapped to unknown; arbitrary truncated recipient
lists are not qualified by tests that merely omit the whole optional field.
Original attachment names compare as multisets only under a recognized original
named-attachment scope with known complete inventory. Generated download names
and unknown scopes cannot distinguish messages. An independent pre-live review
caught an initial overly permissive scope check; the model was corrected before
live outcome evaluation. Live search attachment lists have unverified complete
scope and are analyzed separately, not promoted into mandatory identity evidence.

Search's timestamp remains semantically unassigned unless its meaning is
established. Matching a Date header in a sample does not establish a universal
field contract. Gmail `internal_date` is not automatically relabeled receipt
time. Source Date headers supply the primary live identity route in this study.

## Experiments and denominators

- Recent search pages, bounded older school-subject searches, replies, named
  attachment/inline-image summary lists and repeated targeted subject searches.
  Record all caps and pagination; no whole-mailbox completeness claim.
- First metadata reads define a frozen reference catalog. Replaying those same
  inputs is a self-consistency check, not independent repeat-read evidence.
  Subsequent metadata reads are graded separately.
- Search views of those messages are compared against the header-based catalog
  without silently borrowing fields from the grading reference.
- Hold out each source record, and compare distinct source pairs, reporting
  same-subject/sender near-neighbours separately from easy unrelated negatives.
- Measure observed metadata collisions and loss of discrimination under
  deliberate minute/day projection. A lack of observed collisions does not
  prove that metadata is unique across the mailbox or future mail.
- Inject missing/rounded/malformed/unknown-zone evidence, optional-field removal,
  ID changes, incomplete candidate lookup and known/hidden collisions. These
  are artificial stresses derived from actual metadata, not newly observed
  connector failures. Report association, wrong association, false split,
  correct distinction and abstention separately for every profile.
- Reverse/shuffle catalog order and serialize/reload the records. Simulate an
  historical/daily boundary within the frozen sample, checking later messages
  in previously seen provider threads. This is not a live scheduled job or a
  proof of live indexing/pagination completeness.
- Compare optional subject/participant grouping with the provider's snapshot
  grouping. Disagreement is a usability finding, not a measured false reply
  parentage decision: neither grouping is an independent conversation oracle.

Known collisions must not be obscured by a sequential importer that first
creates one record and then silently associates a second identical observation.
Explicitly demonstrate that singleton/hidden-collision failure mode. The
metadata-only boundary cannot distinguish truly identical permitted evidence.
Do not add a content or provider-ID fallback to make a test pass.

All-candidate comparisons are complete only within the frozen test corpus.
Candidate enumeration for the actual mailbox, sustained capacity, actual Drive
recovery, attachment content processing and other agent environments remain
separate qualification work.
