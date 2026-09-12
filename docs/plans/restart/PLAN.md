# School-OS restart architecture and simulation

Status: the user has replaced content-assisted identity with
[metadata-only matching and thread handling](identity/METADATA-RECIPE.md).
The original simulation, message-identity research and MIME evaluation remain
historical evidence. A new decision model and live application qualification
remain future work.

## Current metadata-only design

- [x] Remove body, HTML, image, attachment-byte and fingerprint comparisons from
  identity and thread association; retain content extraction as a separate job.
- [x] Define source metadata, observation limits and metadata-association outcomes.
- [x] Give each reply its own message identity and coverage; keep inferred thread
  grouping optional and prevent a previously processed thread from hiding new replies.
- [x] Preserve visible collisions and state the residual risk of indistinguishable
  metadata, without a content or provider-ID fallback.
- [x] Update product principles, design authority and continuity documentation.

Next: implement and evaluate the metadata-only decision model, including explicit
criteria for sufficient evidence and collisions, then qualify individual-message
metadata access and daily discovery in managed agent apps. No simulation pass
or operational support is inferred from this documentation update.

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

## Current message-identity follow-up

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
choice and deferred concurrent-write policies. This work changes documentation
and runs a synthetic architectural model. It does not modify the installed
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

The Python exercise is a development analysis instrument, not a School-OS
runtime or a dependency that a parent or agent must install. All communications,
accounts, jobs and effects are fictional. Supplied semantic expectations model
correct interpretation; successful model execution cannot certify an LLM's
ability to discover those facts or a real connector's fidelity.

The production target is a managed/cloud agent application with Drive access,
not a dedicated personal computer running a coding CLI. Tool support,
authentication, approvals, temporary storage and scheduled execution must be
qualified on the actual app. Unknown capabilities remain explicit.

Multiple agents and jobs are supported. Simultaneous updates to the same Drive
data are excluded from the current scope; this simulation must not add locks,
leases, fencing or a conflict-resolution engine to address that edge case.
