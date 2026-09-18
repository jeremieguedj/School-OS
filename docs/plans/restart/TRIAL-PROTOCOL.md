# Authorized three-agent ingestion trials

Status: the T01-T19 three-route retest is complete at the setup gate and is now
the captured first baseline round for the authorized
[autonomous remediation cycle](AUTONOMOUS-REMEDIATION-CYCLE.md). That cycle
supersedes the former joint-review stop only for one unchanged fresh pre-fix
round, selected nonarchitectural or already approved-architecture treatments,
and two unchanged post-fix rounds. Keep the existing 64 KiB canonical limit.
Architecture-changing treatments remain backlogged until explicit approval.
See the [round-two results](ROUND-2-TRIAL-RESULTS.md) and historical
[results](TRIAL-RESULTS.md); private source and receipt evidence remains outside
Git. The [active plan](PLAN.md#2026-09-17-autonomous-remediation-cycle--active)
and cycle plan control authorization.
This evaluator protocol is never supplied as the agent's opening prompt. Use the
[minimal handoff](TRIAL-PROMPTS.md); keep source values and instance links private.

## Fixed inputs and isolation

The coordinator records one published implementation SHA and one exact seven-day
arrival/received-time interval, ending at the start of the trial series, with
explicit timezone, precision and boundary semantics. All three trials use those
same values. The current maximum encoded page size is 64 KiB (65,536 bytes), as
defined by the published data contract. All three routes use that same maximum
for their canonical instances; do not tune it per route. The evaluator may prepare
household/guardian, child/school/class, timezone, logical mailbox/source scope,
Drive destination and tool choices privately as an interview answer sheet.
Disclose only authorized answers when asked, not a preloaded configuration
artifact. Do not copy old knowledge, tasks, coverage,
record IDs, bindings or inferred answers.

After testing is directed, locate and verify the user's existing tests parent
folder. Create three distinct fresh child folders, preserving all earlier failed
folders and unresolved effects, for:

1. A context-free agent supervised by the coordinator. Spawn without inherited
   conversation. Supply only the published starter ZIP link and “setup my schoolOS.”
   Supply scope and private answers during the ensuing interview, not upfront.
2. A new Gemini Spark task through the user's browser.
3. A new ChatGPT Work task through the user's browser.

The browser routes use the user's existing signed-in Chrome profile. Give each
route a separate conversation/session, controller, tab, Drive instance and
private evidence directory, and operate the shared browser UI serially. Record
the controller, task/session alias, tab, signed-in provider account, assigned
Drive destination and evidence boundary. The final methodology must disclose
shared profile, cookies and account state and any unknown provider memory. It
may claim separate conversations, tabs and Drive instances, but not
browser-profile, account-level or provider-memory isolation. Never paste one
route's output into another; detected cross-route contamination invalidates the
comparison.

### Controller binding before every follow-up

Before sending an interview answer, ingestion request, common question,
retrospective request or evaluation request, the controller compares the visible
destination with the private round manifest. All six values must match: provider,
provider task, conversation, route, assigned Drive root and current stage. The
composer must be visibly attached to that exact task. A top-level composer, a
composer whose task cannot be established, or any mismatch blocks the follow-up.
Navigating to the expected page is insufficient; record a new observation
immediately before the send.

The evaluator records one of these states without collapsing them into a generic
running or failed label:

| State | Meaning and controller consequence |
| --- | --- |
| `active` | The bound task is still processing. Observe; do not answer an interview that has not appeared. |
| `awaiting_user_input` | The bound task has asked for input. A follow-up is allowed only when the exact binding, stage and task composer are verified. |
| `completed` | The current stage has a final response. Advance only through the next gate defined by this protocol. |
| `approval_blocked_before_delivery` | The provider stopped before an external delivery or other approval-gated effect. Preserve the stop; do not report delivery or bypass it. |
| `dispatched_unknown_effect` | Dispatch may have occurred but its effect cannot be established. Verify safely when possible; never retry the possible effect blindly. |
| `controller_observation_unavailable` | The controller cannot establish current state or task binding. Do not send a follow-up through an unverified surface. |

Observations are ordered. A later final response supersedes an earlier running
snapshot; the earlier snapshot remains evidence but cannot keep the route marked
active. A controller interruption does not turn the last running snapshot into a
failure or prove that no final response appeared.

One launch retry is allowed only when preserved evidence proves both that the
original attempt was not dispatched and that it had no effect. Record that
attempt separately as `proven_no_dispatch_retry`. The retry uses the same exact
route binding and opening message. A second retry, a retry after unknown
dispatch, or a retry after an unknown effect is blocked.

Provide the assigned folder when the agent asks for its destination and before
its first persistent write. State that it must disregard previous School-OS
instances and confine writes to that folder and descendants. Record this as the
isolation scope answer, not part of the minimal opening prompt. This
is a scope instruction, not a request to erase provider memory or delete old
instances. No trial may read another trial's generated records or the independent
expectation inventory. Use the same recipe revision; do not make hidden mid-trial
instruction changes. Record any intervention and its reason.

Mailbox access is read-only: no read/unread changes, labels, deletion or sends are
part of the test. Task extraction is canonical to each isolated Drive instance;
external personal task synchronization, audio generation, outbound briefs and
scheduled jobs are not in this authorization. Record those capabilities as
unexercised rather than simulated successes. Do not add a task connector solely
to satisfy a test the user did not request.

## Publication checkpoint

Before starting, record retained deliverables, explicit MVP deferrals, the
published SHA, starter asset link, coverage map and unqualified capabilities.
Preserve the snapshot and frozen studies. The user's 2026-09-17 instruction
already authorizes the revised flow after publication verification; no additional
readiness approval is required. Do not submit private v2 trial attachments or
resume the earlier guided prompts. Use the new minimal one-link setup flow.

## Independent reference and receipts

After the user directs testing following the publication/readiness checkpoint,
the coordinator independently enumerates the
same authorized source interval and reads substantive source content. Preserve
complete relevant connector results privately before normalization; keep raw
failures with mode 0600 under an admitted ignored directory. Do not use a
provider-entry count as the count of logical emails. Distinguish observations,
logical associations, unresolved associations and actual processed content.

Before the first source or Drive dispatch, create the route's admitted
gitignored private evidence directory with owner-only access. Use the local
[`trial_evaluation`](../../../helpers/trial_evaluation.py) preflight to write,
read back and remove a harmless synthetic receipt. Stop before dispatch if it
fails. For every later connector operation, preserve the complete response
envelope or thrown exception before normalization and record dispatch, observed
provider response and verified receipt persistence separately. Only then derive
a privacy-safe report row. A receipt failure after dispatch is evaluator failure,
not provider failure or success. Verify a possible remote effect with an
available safe read; never repeat a write blindly. Repeat only a known-safe read.

Before each trial connector dispatch, capture the exact callable tool signature
or schema exposed to that controller and the proposed argument object. Run the
route-neutral `validate_call_schema` gate with those inputs. It checks exact
argument names, required and optional keys, simple declared types, and any
caller-declared mutually exclusive locator groups. An invalid result blocks
dispatch and is recorded as local call-schema validation, not a provider error.
For example, an object does not satisfy a declared string `query`, and an
attachment read with required `message_id` and `attachment_id` does not validate
when only the attachment locator is present. The evaluator must not infer a
provider signature from another route or add provider-specific defaults.

Bind the oracle to the exact bytes of one private round manifest and one exact
private source-input record. Preserve and verify both SHA-256 digests. The source
input declares a nonempty set of private query/input aliases without publishing
the underlying addresses or query values. The oracle supplies exactly one
ordered enumeration chain for every declared alias. Each chain begins with a
null request token; every later request token equals the preceding observed next
token; every page carries exact preserved receipt bytes and their digest; and the
final observed next token is null. Missing, duplicate or unexpected aliases,
missing or altered receipt bytes, broken token continuity, or a non-null final
token rejects the oracle.

The interval is recorded as `[start,end)`: start inclusive, end exclusive, with
explicit timezone and precision. Preserve each candidate's supported comparable
arrival/received timestamp and apply the interval boundary locally. A provider
query can narrow candidates but is not boundary proof by itself. Missing or
incomparable arrival evidence fails the oracle preflight instead of silently
including or excluding that candidate.

Before a tested route can use the oracle, verify the exact round-manifest and
source-input byte digests, exact interval fields, every independent enumeration
chain and receipt digest, terminal nulls, and local boundary-filter result.
Reject an oracle bound to another manifest, source input or interval, even when
its dates appear similar. Reuse is allowed only with those same exact inputs.
Re-enumerate or reread source only when receipt integrity is
insufficient, the source becomes unavailable, or evidence shows the bound source
projection changed; record that bounded recheck as a method event.

This preflight proves integrity of the supplied receipt bytes, exact source-input
binding, caller-recorded token continuity and caller-recorded terminal nulls. It
does not parse an opaque provider receipt to derive its token, prove that the
provider returned every possible item, or turn provider-entry counts into logical
email counts. Those observations and limits remain separate audit evidence.

Build expectations directly from the source evidence, independently of the
agents' extracted output. Cover substantive claims, qualifications, date meaning,
child/family/school applicability, deadlines, finite/conditional/recurring actions,
corrections and possible completion evidence. An action-free or fact-free email
requires an explicit source-supported reason. Developer evidence hashes may bind
receipts to expectations privately; they are not canonical identity keys.

Required attachments are part of whole-email ingestion. Unsupported reads,
unknown inventory, unavailable exact original Date or incomplete listing remain
visible failures/limitations. Do not silently redefine the trial as body-only or
weaken association to provider IDs, content or rounded timestamps.

## Independent setup gate

The tested agent's setup-complete statement and its own checks are observations,
not the evaluator's setup verdict. The independent evaluator derives the first
finite installation expectation directly from the exact immutable starter
supplied to that route. After verifying the starter revision and bytes, enumerate
every supplied root document and every file beneath `system/`, preserving each
safe relative path and its exact bytes. Do not obtain this inventory from the
tested agent, its generated instance or a remembered file list.

For the final installation-material gate, create a second exact expectation by
replacing only the starter's `START-HERE.md` value with the exact complete
configured-entrypoint bytes intended by this setup operation. Keep the starter
bytes for every other root document and every `system/` file. Read every expected
installed target from the route's assigned Drive root, preserving its complete
saved bytes and observed ancestry through the selected root. There is no mutable
or arbitrary-byte exception for `START-HERE.md`. A listing alone, the ZIP
remaining beside an empty folder, a link written into the entrypoint, or a
tested-agent self-report does not establish installed material.

Run `check_installation_materials` over the phase-two exact expectation and saved
readbacks. Preserve its result as `valid`, `invalid` or
`insufficient_evidence`, with privacy-safe diagnostic counts and codes.

Next, independently read the complete saved `START-HERE.md` bytes and derive the
temporary bootstrap manifest only from the roles, root page IDs, families and
route/scope values visibly enumerated there. Record whether that derivation is
`valid` or `insufficient_evidence`; exact bytes without a complete visible
manifest do not pass. Do not fill missing values from the tested agent's report,
another file, a prior round or the evaluator's expected topology.

Only after successful entrypoint derivation, run `check_bootstrap` over that
derived manifest and exact canonical page readbacks. Preserve its `valid`,
`invalid` or `insufficient_evidence` result separately. The evaluator does not
accept any of these three results from the tested agent.

The setup gate passes only when the installation-material result, entrypoint
derivation result and bootstrap result are all `valid`. An `invalid` result is a
setup failure. Otherwise any `insufficient_evidence` result keeps setup
incomplete. Do not send the ingestion request while the combined gate is failed
or incomplete.

## What each agent must do

- Discover setup from the starter ZIP and minimal request, conduct the ordinary
  parent interview, then set up the assigned fresh folder. Do not inject a
  developer reading list or filled configuration. Reuse explicit interview answers.
- Save an identified Drive bootstrap, current reusable system instructions,
  configuration, selected semantic mappings and canonical/index directories.
- Discover all in-scope mail through available continuation, including short pages;
  preserve windows and truthful coverage.
- Associate each logical email from approved metadata, process body and required
  attachments, preserve substantive knowledge and action items, save and read back.
- Mark only fully processed, persisted and verified logical emails fully ingested.
- Answer a small common set of source-grounded questions by retrieving its own
  canonical Drive records, explaining evidence/freshness limits and source links.
- Report incomplete work and exact capability gaps. Never claim a successful run
  because its environment ended or one batch finished.

## Audit and comparison

Keep a private per-trial action log with observable tool/UI operations, timestamps,
interventions, failures and verified saved outcomes. Record useful measures only
when observed: elapsed active/wait time, tool calls, repeated reads/writes,
unnecessary whole-history downloads, setup friction and parent questions. Mark
unobservable counts unknown instead of estimating them as facts.

Compare each trial independently against source expectations and the contract:

- isolation, identity, source links, page bounds and fresh-agent discoverability;
- search exhaustion and date boundaries versus actual email ingestion;
- body and attachment completeness, source-date preservation and reply separation;
- substantive claim/qualification/correction preservation;
- individual versus family/school scope and independent task completion units;
- canonical task state, especially detected completion awaiting parent confirmation;
- index/catalogue consistency, retrieval route, omissions and duplicate claims/tasks;
- unsupported capabilities, uncertain effects and cleanup of accessible raw copies.

Choose several common questions from independently observed source evidence.
Include a concrete fact with a qualification, an action/deadline, applicability to
a child versus the family, and a recent change when the material supports it.
Ask an evolution/trend question only with an honest interval and coverage caveat;
seven days cannot demonstrate year-long trend quality. If a case is absent, report
it unexercised instead of inventing school content.

For each answer document the observable retrieval/evidence trace: question scope,
configuration/entities resolved, directories/pages used where observable, cited
claims and source references, relevant correction/coverage checks, answer and
limitations. Request a concise explanation of supporting evidence, never private
hidden reasoning. A persuasive explanation is not a substitute for correct data.

After the independent setup gate passes, audit coverage from the configuration
page and the concrete bootstrap roles for that instance. Follow the installed
contract rather than a remembered flat field list: every explicit continuation;
nested
`entries[].buckets[].page_ids[]`; window source-index roots; locator, catalogue
and index-coverage targets; and supported `page_hint` values. Resolve canonical
record references through hints, locators and bounded directory/catalogue
fallback. Record visited pages, unresolved hard references, unresolved advisory
hints, unknown required shapes, duplicate/conflicting IDs, cycles and exhaustion
privately. An unresolved required target, unknown shape or unfinished
continuation makes the audit incomplete rather than empty. The evaluator helper
reads already-collected pages only and never repairs the instance.

Use an exported answer or diagnostic only when the evaluated prompt, final
response and explicit export action bind to the same tested task/session, and the
supported export receipt itself carries the exact expected artifact SHA-256 and
byte count. The separately recorded artifact metadata, receipt values and exact
downloaded bytes must all agree. A saved receipt without that artifact binding, a
digest or byte-count mismatch, a same-name local file, or plausible content is
insufficient. In those cases, grade the visible response and disclose the
artifact limitation. Canonical Drive readback and independent source evidence
remain primary.

Before defining an image-dependent expectation, preserve the exact private image
or a faithful private rendering and show every relevant page, crop or frame to an
independent evaluator. Record the artifact and portion reviewed, then author the
expected facts/actions before inspecting the tested agent's extraction. Label
OCR as derived. Missing, cropped or unreadable pixels remove only the unsupported
image-specific expectation and become an evaluation limitation. Private school
images, renderings and hashes remain outside Git and public reports.

## Page-size measurement and narrow comparison

Measure page behavior only during the subsequently user-directed trials, after
the implementation publication/readiness checkpoint. The canonical trial instances continue to use the one
current contract maximum recorded above. The comparison does not change that
maximum, create another trial root, or re-ingest source material.

For each route, record these values privately when they are actually observable:

- each encoded canonical page's byte count and complete-record count, together
  with the sample count and maximum; report p50 and p95 only when the sample is
  large enough for those percentiles to be meaningful, otherwise mark them not
  meaningful;
- any complete canonical record that cannot fit on an otherwise empty page,
  including its encoded page bytes and minimum required page size; keep this
  distinct from the bytes of a raw email attachment or temporary download;
- Drive reads, writes, verification readbacks, any retries actually performed
  and their reasons, and transferred bytes when the connector exposes them;
- downloaded/source bytes and model-visible context separately when either is
  exposed, because downloaded bytes do not establish how much content the model
  could see; and
- tokens and monetary cost only when the route exposes actual values. Otherwise
  use `unknown`; label any separately useful calculation a rough estimate and
  state its inputs and assumptions.

Keep evaluator measurements out of the initial setup prompt. After a route has
produced its canonical records, issue the separate evaluation request and prepare
a narrow analytical comparison of 64 KiB, 128 KiB and 256 KiB maxima using the same ordered complete
successfully saved records and the same common source-grounded queries. Keep the
comparison pages clearly noncanonical and private in a marked evaluation area
inside the existing assigned trial folder; do not connect them to the bootstrap,
canonical directories or indexes. Do not create another School-OS instance or
read the mailbox again. Pack only between complete records; do not truncate or
introduce a field-splitting representation. Report a canonical record that did
not save because of overflow separately rather than reconstructing it from raw
source for this comparison.

For each candidate, observe the page distribution and storage operations above,
then fully read every comparison page through its exact encoded end and compare
the reconstructed records with the same canonical input values. Run the same
queries as actual retrievals from each candidate's comparison pages, and record
the pages and records read. Compare that read evidence and each answer against
the independently source-derived expected records. An answer remembered from the
canonical query or an earlier candidate is not retrieval evidence. Assess answer
correctness, retained source qualifications, omissions, and irrelevant records or
bytes read. Record connector and model visibility limits, inference quality
uncertainties and any cost unknowns. A larger candidate maximum permits fewer or
larger pages; it does not require existing smaller pages to be merged or rewritten.
If a trial never produces pages approaching a candidate maximum, or a route cannot
completely write and read them, mark that candidate unexercised rather than
claiming it qualified. The comparison supplies evidence for a later coordinator
decision; it does not itself change the shared contract maximum or require another
user approval checkpoint.

Retain the fictional near-limit prepared case in
[`examples/evaluation`](../../../examples/evaluation/README.md): one complete
record fits near 64 KiB, adding the next whole record rolls to another page, and
readback reconstructs both records exactly. It is preparation, not provider or
limit qualification. In the authorized comparison, preserve canonical family
and route boundaries and measure exact bytes including the marked noncanonical
envelope. If one record alone exceeds a candidate maximum, record its required
page bytes and do not truncate or reconstruct it from raw source.

## Failures, changes and final report

A failed trial is evidence; do not erase its folder or quietly replace it. Keep
first-attempt results intact. Follow the active remediation cycle's phase
boundary: no issue found inside a round is repaired before that round closes.
After the pre-fix round, implement only treatments classified and authorized as
class A or B; backlog class C architecture decisions. Do not change the product
between post-fix rounds A and B. Continue independent unaffected cases when it is
safe and verifiable to do so.

Keep detailed private audit artifacts separate from reusable public documentation.
Publish sanitized failures, inefficiencies, coverage/results and implementation
revision, with a private artifact link supplied to the user through an authorized
channel. Do not put raw school messages, child information, provider IDs, private
folder URLs or credentials in Git or a public website. Report implemented,
exercised, passed, failed and unexercised status separately; do not claim broad
vendor compatibility or product qualification from three trials.
Use the privacy-safe
[`trial report template`](../../../examples/evaluation/TRIAL-REPORT-TEMPLATE.md)
so receipt state, reference completeness, export provenance, visual grounding,
achieved browser isolation and 64/128/256 KiB evidence remain separate.
