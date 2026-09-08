# Daily-brief rendering operation

## Inputs

Resolve the selected mail adapter from private integration configuration before
delivery. Read only the declared private derived files:

- rolling update stream;
- recent guidelines;
- canonical outstanding tasks;
- configured group/order and recipient settings;
- delivery state; and
- optional current-run delta for audio.

## Rendering rules

`school_os.brief` builds a versioned brief-input contract from verified source
maps, the explicit current-guideline selection, and the explicit unresolved
finite-task view, then renders fixed HTML and plain-text outputs. Source
received day derives from the mail adapter's internal timestamp in the
configured timezone. Inputs preserve configured child-then-household order,
group received days newest first, retain canonical source/table order inside a
day, escape text and links, and show explicit empty states. Record
input/content hashes in the operation checkpoint rather than creating a
separate rendering manifest.

- Render News, Guidelines, and Action Items as separate sections.
- Group each section's entries by the configured local received day, newest first.
- Group task presentation by configured person/entity order followed by the household group. An explicitly parent-origin, unresolved finite task with no school source date appears under the exact heading `Parent-added tasks` within that ordinary action section, without a received-date group or source URL. This provider-independent exception never derives origin from missing source data; a source-origin task with missing or malformed required source date remains a blocker.
- Validate every rolling update's atomic Fact references through the source-catalog contract before rendering it. Use the stored source identifier for the human-facing source link; Fact IDs remain provenance metadata and need not be shown to the reader.
- Use source-linked factual wording. Do not introduce a task, deadline, or recommendation that is absent from its canonical input.
- Keep guidelines separate from tasks.
- Give source-backed tasks a verified direct action/source link when one exists; never invent URLs or expose internal record identifiers as public links.
- Render accessible, mobile-safe links using ordinary anchor elements and visible link text. Source and task links visibly follow their canonical text as ` — Source` and ` — Link`; guideline scope is a bold visible prefix.
- A supplied template uses only its exact declared placeholder map. Each
  declared placeholder occurs exactly once in both its HTML and plain-text
  bodies; missing, duplicate, unknown, or unresolved placeholders block
  rendering. Every eligible item must resolve to exactly one declared content
  or section slot. A missing household/multi-entity slot is a visible
  configuration blocker, not an omission. The default full-content
  presentation explicitly renders household News as well as Action Items.
  This is not a general template language. The default presentation remains
  fluid at 100% width with 16px horizontal padding and tonal section banners.
- Preserve an item's exact canonical scope string separately from its configured
  presentation route. Guideline scope prefixes use the friendly configured
  entity name only when that canonical scope is the entity itself; a
  multi-entity scope that routes to the household remains visibly exact.
- Audio, if enabled, narrates only the current run delta under its selected adapter's rules. Audio unavailability is a disclosed optional degradation, not a reason to fabricate output.

## Delivery

Use the private delivery state to prevent duplicate daily sends. A qualified,
approved direct manual sender and a cadence-triggered scheduled run use the
same business recipe, delivery-key lookup, verification, and ledger rules. A
manual run still needs the operation's verified storage, mail, task, and
serialization evidence; a scheduler is only required for a scheduled trigger.
Verify the sent result through the selected mail adapter before recording
success. If delivery outcome is ambiguous, follow the installed delivery policy
and do not blindly resend.

The durable delivery ledger records delivery key, variant, content hash,
recipient/configuration fingerprint, provider message identity, and verification.
An existing confirmed key suppresses a duplicate; unknown outcomes go to
reconciliation rather than a blind resend.
