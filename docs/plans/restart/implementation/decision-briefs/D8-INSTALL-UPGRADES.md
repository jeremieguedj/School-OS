# D8 — Installing, updating and preserving a private instance

Status: explanatory proposal, 2026-09-15. D8 is **not approved**. The
[active plan](../../PLAN.md) records the approved scope; the
[D8 proposal](../ARCHITECTURE-PROPOSAL.md#d8--package-format-upgrades-extensions-and-legacy-retirement)
contains the starting recommendations. The examples here are fictional written
walkthroughs, not installation, upgrade or recovery test results.

A parent supplies a release package to an agent, which installs or updates
School-OS on Drive while preserving private records and compatible additions.
Ordinary use should not require GitHub access or a running home computer.

## What the package contains

Recommend a versioned ZIP containing the agent entry instructions, operation
recipes, code, record and adapter contracts, configuration examples, extension
instructions, license and a release manifest. The manifest would identify the
version, included files, compatible contract/schema versions and qualification
status. The integrity/admission contract still needs approval. Integrity checks
establish the supplied bytes, not functional qualification.

School-OS agents must be able to execute code; that prerequisite is approved.
Language, runtime version, dependencies and entry points remain pending under
D3. User-reported supplier confirmation does not independently qualify ZIP
handling, Drive access or update behavior in a particular agent.

## The three Drive areas are already approved

D1 separates official files, private instance records and user additions. D8
must use that layout without asking the parent to approve it again:

| Area | Illustrative contents | What a compatible update should preserve |
|---|---|---|
| `system` | Official School-OS instructions, code and contracts for a named release | The currently selected release until an approved update is activated |
| `instance` | Household configuration, school knowledge, canonical tasks, source indexes, coverage, known jobs and work | Private information and parent choices |
| `extensions` | A household's compatible weekly lunch-planning application | The addition, its declared ownership and compatible configuration |

The readable bootstrap points an agent to the instance and installed release.
Private records use D1's bounded JSON pages and directories; this does not
require loading the whole school year during startup. Exact minimum record and
ordinary-write contracts remain undecided after D2's review was deferred.

Raw school emails and attachments stay at their sources. The software package
contains no household mail, contacts, credentials or generated briefs.
Credentials remain in their authorized stores.

## A proposed first installation

Imagine a parent whose fictional Juniper School sends a trip permission form.
They want to preserve the deadline and lunch instructions, then ask about them
from a different agent later. Under the proposed successful installation flow:

1. The parent downloads a published School-OS package and gives the ZIP to the
   selected managed agent.
2. The agent reads the package's entry instructions and manifest, checks the
   supported package contents and required capabilities, and explains any
   missing requirement, following the still-pending package contract.
3. It obtains the household's source accounts, school scope, timezone and other
   necessary configuration. Supplied example values must not become accidental
   household settings. Authorizing an installation does not itself select an
   email recipient or create an external schedule.
4. It writes official files and the required initial private records under the
   approved Drive layout, then verifies the required saved contents. Existing
   unrelated Drive material is not replaced by an example template.
5. Only after the required installation is verified does it activate the
   bootstrap's selected release, under the proposed D8 activation procedure.
   Missing capability or incomplete installation is reported explicitly.
6. A later authorized ingestion operation processes the trip email. The agent
   preserves its substantive information and coverage on Drive; it does not
   copy the email into the installed software area.

A proposed parent-facing completion message would be:

> School-OS is installed in the selected Drive instance using release 1.0.0.
> Your school scope and timezone are saved. No scheduled job has been created.
> This release's qualification status is shown in its manifest.

The version is illustrative. No actual restart release is designated installable
or qualified here. Incomplete installation must not produce that message.

## What “pinned version” means

The instance names the official release it uses. A newly published release does
not silently change that choice. A fresh agent reads the same installed version
and applicable instructions from Drive. This avoids depending on yesterday's
conversation or a live development branch.

Private data still evolves as school information arrives and parents complete
tasks. A deliberate upgrade changes the official instructions/code selection.

## A compatible extension through an upgrade

Suppose the household adds a “Friday lunch list” application. It reads saved
school lunch requirements and produces a shopping checklist. It consumes the
existing canonical knowledge; it creates no competing school-information store.
Any new architecture in that addition still requires explicit approval.

Recommend that an extension declare its name/namespace, owned files and supported
contract major version, giving the updater explicit ownership and compatibility
boundaries. This declaration mechanism is a pending D8 choice.

Here is the proposed successful upgrade from illustrative 1.0.0 to 1.1.0:

| State | Official software selection | Private instance and extension |
|---|---|---|
| Before | Bootstrap selects 1.0.0 | Trip task, parent completion and Friday lunch application are saved. |
| Staging | 1.0.0 remains selected; 1.1.0 is copied separately | Existing private data, settings and extension files are preserved. |
| Compatibility/readback review | New official files and declared compatibility are checked | The lunch application's supported contract is compared with the new release. |
| Activation | Bootstrap is deliberately changed to 1.1.0 and read back | Private records and compatible additions remain in place. |

The result would name the new version and retained addition. A conflict would
name the incompatible extension and leave activation undecided, without silently
deleting the lunch application.

## Compatibility is a decision about meaning

Recommend semantic major/minor/patch versions for packages and contracts. An
additive optional field may be compatible if old consumers can still read the
records correctly. A changed meaning or newly required field needs a major
contract version and an explicitly approved migration.

For example, an optional display label may leave the lunch application usable.
Changing a deadline field from “school deadline” to “parent's planned date”
changes meaning even if both values look like dates. Such a change cannot be
called compatible merely because JSON can still be parsed. Actual compatibility
rules, unknown-field behavior and migration steps need a concrete contract.

Recommend leaving incompatible upgrades inactive until the required migration
and extension treatment are approved. Keeping old code does not guarantee that
it can read data after an incompatible migration. Automatic rollback of those
changes is not promised.

## The interruption limit must remain explicit

The current D8 proposal includes a Drive upgrade intent and reconciliation if
the bootstrap change has an unknown outcome. That depends on mechanisms which
cannot simply be imported from deferred D2. Interrupted canonical-write repair
is outside the MVP, and the minimum ordinary-write design is still pending.

Staging describes the intended successful order; it is not proof that a
partially copied release or interrupted bootstrap update is recoverable. The
decision still needed is the MVP boundary when this happens. Recommend, for
review, stopping the affected installation/upgrade, reporting incomplete or
unknown activation, and requiring explicit inspection before further changes.
That recommendation is not yet an approved repair procedure or guarantee that
every failure can durably record its own status.

An alternative is a narrowly defined upgrade-recovery feature. It would need
separate approval and must state exactly how it differs from the deferred D2
mechanism. Another alternative is parent-supervised installation/updates with
the same honest interruption limitation. These choices trade automation against
implementation scope and parent effort; silently restoring general recovery is
not an option.

## Retiring the previous project safely

Repository cleanup concerns the reusable project; it does not migrate or erase
a parent's installed instance. The preservation baseline is
`restart-baseline-2026-09-14`, targeting commit
`39d752c364a1cf404e5a6fc5739148b7d35a6b35`. Its remote publication must be verified
by the coordinator. Git history, current principles, continuity, privacy
safeguards and frozen studies remain preserved. Obsolete operational entry
points must stop directing new agents into the retired runtime.

The pending recommendation is fresh installation; migration from retired
instances remains separately unapproved and must be explained to users.

Before implementation publication, inspect hooks and CI, prepare a meaningful
replacement validation entry point without executing it, and avoid publication
routes that trigger tests. The code handoff requires committed/pushed code and
remote-revision verification, followed by the user's testing stop. It does not
authorize building a ZIP, installing an instance or declaring a release tested.

## Decisions still requiring approval

Approve or revise the ZIP/manifest and integrity contract, version/compatibility
rules, extension declarations, successful staging/activation procedure, explicit
interruption boundary, and fresh-install versus retired-instance migration
scope. D1 is already approved. Remaining D3 and minimum record/write decisions
are dependencies, not assumptions.

In-place replacement is smaller but makes partial updates and extension ownership
harder to inspect. Reinstalling into another instance separates software copies
but adds private-data transfer and identity risks. Staged official versions are
the recommendation, with the limits above. Real archive handling, bounded Drive
copy/readback and compatibility remain unqualified; no build, migration or test
was performed or authorized by this brief.
