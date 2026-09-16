# Historical and daily ingestion

Use this operation to catalog and fully process school communications in the
parent-authorized source scope. It produces canonical source-linked knowledge,
tasks and whole-email coverage on Drive. It does not send a brief, change a task
app, create a schedule or expand account permissions merely because ingestion
was requested.

Read [identity](../contracts/identity.md), [data](../contracts/data.md),
[storage](storage.md), [knowledge](knowledge.md), [extraction](extraction.md) and
[continuation](continuation.md), plus the selected source and Drive semantic
adapters. Read only relevant instance configuration and directories; do not load
all canonical bodies at startup. The executing agent uses its own authorized
connectors and manages resources without a School-OS batch controller.

## 1. Establish the authorized finite scope

Resolve the instance and logical Source Account from the readable Drive entry
point. Verify the parent-selected mailbox, school scope, import boundary and
selected source mapping. Retain child, household, school and class context from
configuration. A tool name or provider handle alone does not verify the mailbox.
If setup is missing, follow [setup](setup.md) before source access.

Set the run-start cutoff once, retaining its timezone and precision. The work
includes all relevant School-OS-pending material through that cutoff, including
known older `not_ingested` emails and unfinished discovery windows within scope.
Later arrivals belong to the next run. The mailbox's read/unread icon has no
effect on this rule. A source filter may implement established school/sender
scope, but the agent must not exclude a message because its subject seems
unimportant or its current known topics do not match an expected task.

| Requested operation | Discovery scope |
|---|---|
| Initial historical import | Parent-selected starting boundary through the declared import endpoint, no later than run start; default to run start when that is the requested import scope. |
| Explicit historical rescan | The parent-requested older interval under the same source mapping and identity rules. Existing fully ingested emails can be reused. |
| Normal daily ingestion | Last completed arrival-time boundary through run start, including the prior boundary at its actual precision; also unfinished windows and known in-scope `not_ingested` backlog. |

With no verified prior daily boundary, use the configured import boundary or
obtain the missing source-scope choice; do not guess a seven-day default. Never
advance past an unfinished earlier interval simply because a later window was
completed. Keep known backlog discoverable even if its listing window is complete.

## 2. Establish how the selected route searches

The source adapter must explain arrival/search-time meaning, timezone,
precision, start/end boundary behavior, individual-message access and listing
continuation/exhaustion. Use source received/arrival time for the approved
daily windows. Original sending Date remains the identity timestamp and UTC
source/month routing basis; it is not silently substituted for arrival time.

Use the agent's live connector within its actual capabilities. If a connector
accepts coarser search boundaries, include enough of its supported boundary to
avoid dropping the prior boundary's messages; inspect exposed arrival metadata
to establish membership in the declared interval. Record the actual semantics
in `discovery_window.start`, `end` and `time_basis`. Do not certify an exact
interval that the route cannot establish. Use another authorized supported
route or report the capability limitation.

Normal daily discovery does not rescan all history and has no fixed seven-day
overlap. It can miss older material that becomes visible only after its older
arrival window was completed. Disclose this approved limit when relevant;
explicit historical rescans can revisit those intervals. Do not claim that live
access makes every provider search immediately complete.

## 3. Save and enumerate bounded windows

Choose manageable windows within the finite authorized interval, according to
current connector and agent limits. There is no School-OS quota of messages,
listing entries or transferred bytes that makes a partial logical run successful.
The data contract still bounds each canonical page and directory page.

Before treating a window as processed, save its logical mailbox, source scope,
school references, time basis and precise bounds as a `discovery_window` with
`discovery_state: unfinished`. Verify normal readback through storage. Keep
`observed_email_refs` pointing to bounded source-index pages with continuation,
not an ever-growing array of provider/message IDs.

For each listing page:

1. Preserve the available metadata and obtain individual message metadata when
   the route returns thread summaries. Discover replies in already seen threads.
2. Apply [identity](../contracts/identity.md) to each relevant individual message.
   Complete the relevant canonical lookup before creating a new resolved record.
3. Reuse a supported fully-ingested match under the identity contract; otherwise process
   the whole email using the next section. Preserve unresolved observations and
   blocked items without stopping unrelated source work.
4. Save ordinary source/index progress and useful access aids. Follow every
   available continuation, even if the page is short or empty.

A page count, short page, empty page with continuation or apparent maximum Date
does not establish exhaustion. Mark the window `complete` only when the selected
route establishes exhaustion of its declared scope, and save the supporting
verification time and evidence summary. A silently capped listing leaves the
window unfinished; making it narrower may help but is not proof of completeness.
Discovery may be complete while an exposed email is `not_ingested`.

## 4. Process one whole logical email

For an email needing content, retain its owned identity and `not_ingested`
outcome while doing the work. Read its body, establish the attachment inventory,
and process all required attachment candidates under [extraction](extraction.md).
Use temporary agent resources; raw content stays at the source after cleanup.

The agent checks school information, not only task candidates. Preserve source
dates, qualifications, original meaning, action dispositions and true scope.
Resolve existing entities/topics, reconcile related Knowledge and canonical
Tasks, and preserve parent state under [knowledge](knowledge.md). Handle clear
task-fulfillment evidence through [completion review](completion-review.md);
it does not directly complete a parent task. An individual reply has its own
source references and content evidence.

Save the whole email's intended Knowledge, Tasks, source references, attachment
groups and required locator/index changes in bounded pages. Use the normal
storage readback procedure. Maintain index coverage/revisions under the data
contract; a stale derived index must remain marked by its old coverage and use
the documented fallback, never pretend to contain the new data.

Only then evaluate `ingestion_coverage.ingestion_state`:

| Condition | Required evidence |
|---|---|
| Body processed | Actual individual body read, including a source-established empty body; substantive Knowledge saved and checked. |
| Inventory established | Complete for the selected message route and configured scope; unknown inventory is not zero attachments. |
| Every group classified | `required`, `not_required` or `unknown` with a source-grounded reason; any unknown requirement blocks full ingestion. |
| Every required candidate processed | All exposed required candidates read, substantive information saved and checked, with group-qualified provenance where needed. |

When all conditions hold, save `fully_ingested`, its Knowledge references and
processing evidence, then read the final coverage page back and check it.
`evaluated_at` describes the evaluation; an evidence `verified_at` describes its
named check. Do not write another timestamp merely to record checking that same
timestamp. Discard accessible temporary raw copies after verified persistence.

If any condition fails, the email remains `not_ingested`. Retain source/inventory
observations and report the blocker; do not publish a completed partial email or
claim a part-resume workflow. Previously verified canonical knowledge is not
deleted. The agent can finish reading chunks within its logical run, but an
interrupted set of canonical writes has no School-OS repair guarantee.

## 5. Finish and report the actual outcome

Before reporting ingestion complete, check the relevant bounded discovery
directories and every observed/backlog email's coverage. All required windows
must be exhausted and all required emails fully ingested. An unfinished coverage
lookup itself prevents an exhaustive completion claim. Unresolved identity or
required content within the run's scope is a blocker, not success with omissions.

Report the logical mailbox/school scope, arrival-time interval/cutoff, whether
discovery completed, whether known emails fully ingested, and specific remaining
limitations. Distinguish logical records from provider appearances; do not claim
a complete count before complete traversal. Identify the newly saved or corrected
knowledge and canonical tasks when useful, without claiming external task sync.

Pass a complete input state to the separately authorized daily/brief operation.
A blocked run does not produce an ordinary daily brief. A separate query may
use verified knowledge with limits under [query](query.md), and a parent may
choose the disclosed limited manual path in [brief recipes](brief-recipes.md).
Neither marks this ingestion complete. Use continuation instructions for normal
missed work or lost tokens; do not add schedules, locks or recovery machinery.
