# Agent instructions

Read [START-HERE.md](START-HERE.md) before working in this repository.

## Development continuity

For repository maintenance, follow the authoritative
[repository development continuity](START-HERE.md#repository-development-continuity)
requirements in `START-HERE.md`.

## School-OS developers only — live connector evidence discipline

This section governs development of School-OS and its provider/runtime adapters.
It is not an operating procedure for parents or other regular users.

When a live connector response exposes a possible runtime defect:

1. Preserve the complete raw connector result or thrown exception before
   normalization in a mode-0600 file under an admitted gitignored private run
   directory. Never put provider IDs, URLs, message text, request arguments, or
   unsanitized errors in Git, patches, terminal output, or chat.
2. Classify the failure boundary from evidence: local validation, dispatch,
   transport/no response, provider error response, or response normalization.
   Do not infer throttling, authorization failure, timeout, or provider success
   from a generic tool error.
3. Inspect the complete key topology, nesting, types, and duplicated values.
   Do not implement from a summarized or truncated observation. Derive a
   privacy-safe synthetic fixture that represents every relevant observed field,
   including connector-only envelope metadata.
4. Keep the adapter boundary explicit: project only the documented provider
   result into School-OS, require duplicated declared values to agree, validate
   any finite recognized transport annotations, and reject conflicts or unknown
   surplus. Connector display/transport metadata is never canonical data.
5. Before rebuilding a package or creating another live test root, replay the
   exact ignored private receipt locally through the proposed repair, run
   conflict and malformed-envelope tests, and pass the focused suite. A test
   invented from memory is not evidence that the observed response is handled.
6. Preserve future failures automatically. Normal logs may expose only
   privacy-safe stage, response-observed state, HTTP status, provider reason and
   domain, retry delay, connector code, and the private receipt path/hash. The
   complete raw error remains private and durable enough for the next developer
   to diagnose without repeating the provider effect.
7. If upstream supplies no status or reason, record that absence. A retry or
   cool-off policy must not be justified as rate-limit handling until rate-limit
   evidence exists, and an unknown write outcome must be reconciled rather than
   blindly retried.
