# ChatGPT Work runtime profile

Status: template requiring environment-specific conformance.

This profile maps School-OS contracts to the actual enabled connectors and automation surface in one ChatGPT Work environment. It must be completed only with observed tool capabilities from that environment.

## Required mapping record

- Drive: scoped list, complete read, create, in-place verified replacement, metadata read.
- Mail: complete search/thread read, attachment access, send/readback.
- Tasks: the selected provider's complete required operation set.
- Scheduler: scheduled-run connector authorization, invocation payload, retry/overlap behavior, status inspection, and disable verification.
- Optional audio: outbound API support and safe credential access.

Do not assume one ChatGPT surface has the same capabilities as another. The private instance records the tested profile and limitations.
