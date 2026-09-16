# Fictional ingestion review material

These are written examples for reading and later user-directed qualification.
They have not been executed as tests, simulations, connector calls or model
replays. Every person, school, address, message, observation and tool behavior
below is invented. Dates are fixture values, not a claim about current work.

- [Mailbox material](mailbox.md) supplies complete small fictional bodies,
  attachment text and declared discovery observations.
- [Expected decisions](expected-decisions.md) walks through identity,
  extraction, persistence, completed-email reuse and continuation.

Review them against [identity](../../contracts/identity.md),
[ingestion](../../operations/ingestion.md),
[extraction](../../operations/extraction.md),
[continuation](../../operations/continuation.md) and the
[data contract](../../contracts/data.md). The labels `E0`–`E4` and `C1`–`C2` are
fixture labels for discussion, not canonical IDs, provider IDs or proof of
distinct physical emails/files. An actual instance assigns School-OS IDs once.

The examples expose specific decisions and limitations; they do not assert
that a live connector supports the fictional route. The source route's time
semantics, inventory completeness and continuation must be established in the
actual environment. No example establishes a record-per-provider-entry target,
an interruption repair guarantee or permission to send a message or change a
task app.
