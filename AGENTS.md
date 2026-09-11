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
8. Test provider-equivalent empty values, not only populated fixtures. Native
   tables and connector grids may spell the same empty cell as an omitted field,
   `null`, or an empty string. Normalize only contract-equivalent empty forms at
   the adapter boundary, then test immediate create/readback and the
   lost-response recovery pass against the observed connector shape. A fixture
   that echoes the write request verbatim cannot prove provider readback.
9. Bind every private independent semantic expectation to the exact packet
   hash and ordered segment identities/content hashes before it can generate an
   interpretation or audit response. An empty candidate list is a substantive
   zero-Fact decision, not a reusable default. Prove with a cross-packet test
   that a zero-Fact expectation for one packet is rejected for every other
   packet.
10. Treat semantic flags as acceptance-critical content, not incidental
    metadata. After all packet audits pass, independently compare the assembled
    Fact inventory with the packet-bound source expectations, including finite
    response requirements and their `is_action` disposition. A packet audit
    cannot validate itself through an expectation copied from generated output,
    and a zero-action aggregate must be explicitly justified before task sync is
    accepted. Separately, the runtime must advance a genuinely action-free,
    completely read task snapshot directly to the brief boundary without
    attempting to authorize a nonexistent provider action.
