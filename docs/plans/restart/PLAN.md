# School-OS restart architecture and simulation

Status: the user approved the corrected interpretation and operating choices on
2026-09-14. The current [metadata recipe](identity/METADATA-RECIPE.md) defines
logical-email reuse, normalization, parent-bound attachment lookup and durable
search-window recovery. Implementation and managed-agent qualification remain
pending. The [artifact guide](README.md) separates current authority from frozen
experiments and historical proposals.

## Approved architecture and operating choices

- Google Drive holds the instance's instructions/configuration, processed
  knowledge and tasks, source/attachment index and coverage, unfinished work,
  and tools/jobs/runs register. These are logical areas; exact file/table layout
  will be selected through a small managed-agent read/write pilot.
- Raw emails and attachments remain in their source systems. Temporary downloads
  support processing and are discarded after verified persistence. Startup and
  routine work read relevant records in bounded units as history grows.
- Agents use simple adapters for available tools and reason over explicit source
  metadata and operating procedures. No required permanent provider ID, token,
  prior conversation, dedicated personal machine or coding CLI is introduced.
- Catalog logical emails. Reuse a record when the sufficiently supported
  normalized metadata recipe agrees without contradictory evidence. Different
  provider entries or repeated appearances alone neither require duplicate
  records nor prove a product failure. Preserve distinctions supported by source
  metadata and unresolved mappings; do not silently merge existing catalog data.
- Normalize address presentation, domain case and recipient ordering; preserve
  local-part spelling and To/Cc roles. Decode/unfold subjects and trim outer
  whitespace while retaining original observations and meaningful subject text.
- Use each individual message's original Date as the primary identity timestamp,
  preserving meaning, zone and precision. Obtain a richer metadata view for an
  unclear search time. Received and internal timestamps cannot silently replace
  that Date. Thread grouping remains optional navigation; every reply has its
  own record, attachments and processing coverage.
- Bind attachment records to their parent logical email. Parent ID plus original
  filename locates a candidate or same-parent candidate group. Preserve relevant
  candidates and coverage; different retrieval handles do not prove different
  documents, and filename agreement does not mark unread material processed.
- Enumerate bounded search windows through all available continuation pages,
  including after short pages. Persist completed windows and unfinished work on
  Drive independently of content-processing status. A fresh agent can repeat an
  unfinished window without a saved pagination token or local state.
- Allow any number of agents and registered jobs. Record each job's purpose,
  executing agent, scheduler location, selected adapters, input/output scope and
  last verified status, plus run/output attribution. Any capable agent reading
  Drive can answer which known jobs exist and who generated a brief. Concurrent
  updates to the same Drive data remain outside scope.

## Corrected interpretation of the live study

The [study](identity/metadata-stress/README.md) made 127 read-only calls covering
632 Gmail entries, with individual header reads for 92 and 17 independent repeat
reads. Its matching pair may represent one logical email. The 92-entry/91-record
replay disagreed with a provider-entry grading reference; it did not establish
lost school information or a product false positive. Requiring a School-OS record
per provider entry was stronger than the product objective.

Repeated filenames occurred within 42 individual parent emails and may include
alternate representations. Address handling was repaired in the study; subject
trimming is now approved but absent from the frozen evaluator. All compared
timestamps agreed; unknown search-time semantics and injected rounding remain
capability/test questions, not observed timestamp changes. Thread-grouping
disagreement is not an ingestion failure. Short pages with continuation provide
the concrete enumeration lesson.

The original code, receipts and JSON counts remain unchanged. Read the corrected
report before interpreting `wrong_association` or the earlier pass/failure totals.

## Next implementation and qualification sequence

- [x] Reconcile product principles, current recipe, test interpretation and
  artifact authority with the approved decisions.
- [ ] Update a small development model in a new revision, preserving the frozen
  study. Cover repeated observations of one logical email, contradictory source
  metadata, normalizable subjects/addresses, each reply's own Date, same-parent
  attachment groups and interrupted window replay. Supply independent logical
  labels for fictional cases; leave unknown live logical relationships ungraded
  rather than assuming provider-entry differences are product errors. Report
  residual indistinguishability honestly without adding content-based identity.
- [ ] Prove one bounded historical-to-daily slice in an actual managed agent:
  discover individual messages and original Dates, normalize/index them, read
  source content and relevant attachments temporarily, persist knowledge/tasks
  and coverage to Drive, verify readback and discard temporary material. Choose
  the simplest usable Drive layout from that pilot, with measured startup/read/
  write cost. Explicitly retain unsupported or incomplete items.
- [ ] Exercise interruption and continuation through Drive: completed windows,
  unfinished enumeration, pending content, and a lost/expired pagination token.
  Repeat the unfinished window without duplicating already associated logical
  records or inheriting another attachment candidate's completion status.
- [ ] Register and exercise a daily catalog job in a supported managed scheduler.
  Save its location, agent, adapters, scope, last verification and run attribution.
  A saved registration alone must not be treated as proof an external job exists.
- [ ] Start a fresh session in a second managed agent using the Drive instance.
  Query existing school information and known jobs, resume unfinished work, and
  catalog a later reply. The previous conversation, local files and provider
  pagination token are unavailable. Preserve existing job bindings and attribution.
- [ ] Check the slice against every product principle and core use case, then
  expand supported adapters from observed capabilities. Qualify task-sync/brief
  applications on the same canonical state; record unsupported routes and limits.

Advance through one reviewable slice at a time. Reuse evidence, fix demonstrated
problems at the smallest responsible boundary, and measure tool calls, approvals,
elapsed work and recovery effort. Do not rebuild the retired runtime, develop
parallel storage engines or require every vendor to pass before learning from the
first slice. This plan does not initiate live writes, migrations or scheduled jobs.

## Remaining limits

Metadata cannot prove unique physical delivery or equal content. The accepted
policy tolerates indistinguishable logical-email candidates without a record per
provider handle. Exact attachment mapping inside same-name groups, unsupported
inline content, complete discovery through capped tools, actual Drive operations,
managed scheduling, handoff and sustained capacity still need qualification.
Incomplete work stays visible and scoped; none of these unknowns justify an
automatic content/provider-ID fallback or an unbounded retry loop.

## Historical raw-MIME evaluation

The 38-case prepared-observation experiment did not parse raw email or establish
false-positive/negative rates. The user explicitly requested checking the new
recipe's robustness and determinism for threads, attachments and HTML images.

- [x] Generate independently labeled fictional raw MIME with presentation
  variants, replies, attachments, CID/data/remote images and incomplete views.
- [x] Evaluate the existing recipe against those observations; report incorrect
  associations, false splits and abstentions separately, with denominators.
- [x] Check repeated execution, catalog/input order and uncertainty handling.
- [x] Document failures, proposed mitigations and remaining live qualification;
  validate and publish this development analysis without changing the runtime.

The former next step of repairing content/MIME matching is superseded by the
metadata-only design above. Keep the old failing matcher and its results
reproducible as historical evidence.

## Earlier message-identity research

The user challenged the assumption that a provider message ID can be the
canonical source key and explicitly requested a quick sub-agent Gmail test,
deep research across agent/harness surfaces, and a provider-ID-independent
identification design wherever guarantees are absent or uncertain.

- [x] Run a bounded read-only test of existing messages and individual replies,
  preserving private receipts before interpretation and publishing only counts.
- [x] Separate provider contracts, sender-created mail headers, connector
  handles, thread IDs and agent-tool references in primary-source research.
- [x] Design durable School-OS-owned identities with multiple optional matching
  witnesses, conservative ambiguity handling and no mandatory raw archive.
  The subsequent explicit product principle makes source information the sole
  basis for identity/acceptance decisions; external identifiers are access aids.
- [x] Exercise missing/changing IDs, replies, reformatting and indistinguishable
  duplicate cases in a small synthetic experiment.
- [x] Update design authority and continuity and validate the accepted changes.
  Apply the repository commit/push procedure and verify the remote revision
  before reporting the handoff complete.

## Authority and scope

The user retired the previous implementation as the foundation for a restart.
The current product authority is `docs/product-principles.md`, including the
explicitly requested source-residency, tool/job inventory, unrestricted agent
choice and deferred concurrent-write policies. This work updates design documentation and preserves prior synthetic and bounded
read-only metadata evidence. It does not modify the installed
runtime, migrate a private instance, create schedules, send messages or publish
a release.

Earlier recovery and release plans remain historical evidence. They do not
require this design exercise to rebuild a package or create a live test root.
The restart is not backward-compatible by implication: future runtime and
migration work must implement the new principles explicitly rather than claim
that the old runtime already conforms.

## Work units

- [x] Update product principles with the authorized operating choices.
- [x] Build fictional communications and independent semantic expectations.
- [x] Simulate setup, historical ingestion, interruption, daily cataloging,
  scheduling, another agent's queries, job inventory, attribution and switching.
- [x] Exercise detailed message, reply, thread and attachment identities.
- [x] Preserve system-state snapshots and test results; distinguish modeled
  outcomes from real connector/model capabilities.
- [x] Review failures against primary documentation for managed/cloud agents.
- [x] Document conclusions, remaining capability tests and scope exclusions.
- [x] Run appropriate repository checks and privacy checks. Publish the accepted
  files through the repository continuity procedure; verify the remote revision
  before reporting this handoff complete.

## Simulation boundaries

The original lifecycle Python exercise is a development analysis instrument, not
a School-OS runtime or a dependency that a parent or agent must install. Its
communications, accounts, jobs and effects are fictional; the separate Gmail
study uses private read-only observations. Supplied semantic expectations model
correct interpretation; successful model execution cannot certify an LLM's
ability to discover those facts or a real connector's fidelity.

The production target is a managed/cloud agent application with Drive access,
not a dedicated personal computer running a coding CLI. Tool support,
authentication, approvals, temporary storage and scheduled execution must be
qualified on the actual app. Unknown capabilities remain explicit.

Multiple agents and jobs are supported. Simultaneous updates to the same Drive
data are excluded from the current scope; this simulation must not add locks,
leases, fencing or a conflict-resolution engine to address that edge case.
