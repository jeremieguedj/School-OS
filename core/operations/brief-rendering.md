# Daily-brief rendering operation

## Inputs

Read only the declared private derived files:

- rolling update stream;
- recent guidelines;
- canonical outstanding tasks;
- configured group/order and recipient settings;
- delivery state; and
- optional current-run delta for audio.

## Rendering rules

- Render News, Guidelines, and Action Items as separate sections.
- Group each section's entries by the configured local received day, newest first.
- Group task presentation by configured person/entity order followed by the household group.
- Validate every rolling update's atomic Fact references through the source-catalog contract before rendering it. Use the stored source identifier for the human-facing source link; Fact IDs remain provenance metadata and need not be shown to the reader.
- Use source-linked factual wording. Do not introduce a task, deadline, or recommendation that is absent from its canonical input.
- Keep guidelines separate from tasks.
- Give source-backed tasks a direct action/source link when one exists; never invent URLs.
- Render accessible, mobile-safe links using ordinary anchor elements and visible link text.
- Audio, if enabled, narrates only the current run delta under its selected adapter's rules. Audio unavailability is a disclosed optional degradation, not a reason to fabricate output.

## Delivery

Use the private delivery state to prevent duplicate daily sends. A user-requested immediate brief is authorized for delivery when it was dispatched through the configured schedule's verified run-now control; it receives the same scheduler identity, reservation, verification, and ledger rules as a cadence-triggered run. Verify the sent result through the selected mail adapter before recording success. If delivery outcome is ambiguous, follow the installed delivery policy and do not blindly resend.
