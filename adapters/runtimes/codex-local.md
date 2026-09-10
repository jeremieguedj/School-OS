# Codex local runtime adapter

Status: finite bridge and bootstrap-readback primitives implemented;
connected daily binding and authenticated manual/scheduled acceptance pending.

This adapter runs the installed standard-library Python core locally and asks
the Codex host to execute only the finite connector request kinds declared in
`school_os.codex_bridge.REQUEST_SPECS`. It has no SDK credentials, OAuth token,
daemon, general RPC method, worker pool, or arbitrary tool-name dispatch.

## Private transport

Create a per-run directory with mode `0700`. The Python peer creates canonical
request JSON with `O_EXCL` and mode `0600`, fsyncs it, and prints only:

```text
SCHOOL_OS_REQUEST REQUEST_ID FIXED_KIND SHA256 ABSOLUTE_PATH
```

The host verifies that exact file internally and uses a static switch from the
fixed kind to the installed authenticated action. Large or private request and
response JSON must not be emitted with `text()` or copied into terminal logs.
The host serializes the complete tool result with ASCII JSON escaping and a
trailing newline, then starts the packaged response writer in a PTY:

```text
stty -echo -icanon min 1 time 0
python3 scripts/write_host_response.py RUN_DIR RESPONSE_PATH BYTE_COUNT
```

Use shell single-quote escaping for every path (`'` becomes `'"'"'`) and pass
the payload through the PTY write operation with the exact declared byte count.
The helper exclusive-creates and fsyncs the mode-`0600` response and prints only
its path, length, and SHA-256. The host returns one short control line to the
runner:

```json
{"request_id":"...","response_path":"/.../REQUEST_ID.response.json","sha256":"..."}
```

The peer verifies containment, filename/ID, regular-file mode, configured size,
hash, protocol, wrapper, and one-use semantics before consuming and unlinking
both transient files. Plain-pipe `exec_command` is not supported because its
stdin closes immediately. Canonical PTY mode is not supported for response
payloads because large lines are truncated; synthetic probes established the
noncanonical transport at 65,591 and 1,048,634 bytes.

## Static host pump

Every request must use the checked-in `HostBindingDispatcher` complete-request
entrypoint. Directly invoking a native tool with `request.args` is forbidden:
that bypasses request validation, removes neither bridge-only hash/size fields,
does not replace child paths with host-owned snapshots, and does not validate
the native result. The executable host loop is exactly:

```python
dispatcher = HostBindingDispatcher(run_directory)
control = dispatcher.dispatch_request_file(
    request_id=request_id,
    kind=kind,
    request_sha256=request_sha256,
    request_path=request_path,
    invoke=invoke_fixed_native_tool,
)
child_stdin.write(json.dumps(control, separators=(",", ":")) + "\n")
child_stdin.flush()
```

`invoke_fixed_native_tool(tool_name, native_args)` resolves `tool_name` only
from `HOST_BINDINGS`; it never accepts a child-provided tool name. The dispatcher
reads and hashes the mode-0600 request, revalidates its wrapper and args, creates
and later removes owned snapshots, normalizes the admitted native
`CallToolResult` envelope, validates that provider result, and exclusive-writes
the raw validated result in the peer response wrapper. The
child `JsonlPeer.connector_call` consumes that raw result and never unwraps a
second connector envelope. Tool exceptions cross only as `effect: unknown`.

`tests/support/host_roundtrip_child.py` plus
`ConnectedBootstrapTests.test_child_ports_roundtrip_through_actual_host_dispatcher`
exercise this exact child process/request file/dispatcher/native-result/response
file path for Drive, Gmail attachment/send, Sheets, and comments. A host pump or
sample that uses a different path is not a supported execution surface.

The fixed native invoker must return the complete connector `CallToolResult`,
including an `isError` result. If the runtime throws instead of returning that
shape, it must let the exact exception reach `HostBindingDispatcher`; an
out-of-process pump must serialize the exception's available name, message,
status/code, and cause into a private error-shaped native result rather than
printing or flattening it. After an invoked failure, the dispatcher leaves a
mode-0600 `REQUEST_ID.connector-error.json` receipt in the run directory. The
receipt contains the complete raw connector outcome or private invocation
exception and no request arguments. The child surfaces only recomputed
privacy-safe stage/status/reason/domain/retry/code fields plus the receipt path
and hash; missing upstream fields remain unavailable. The ordinary JSONL error
wrapper and its `effect: unknown` reconciliation rule do not change.

The semantic kinds are separately dispatched to actual interpreter and
independent-audit callbacks over the immutable packet boundary. Fixture or
synthetic callbacks are labeled synthetic and cannot authorize provider writes.
Connector structured content is inspected explicitly by the mandatory host
dispatcher. Declared connector results are accepted from the observed flat or
`structuredContent.result` shapes; Gmail attachment transport annotations are
validated and removed at that boundary. Text content blocks and metadata never
establish semantic verification.

## Selected connector limits

- Drive scoped listing uses the metadata-only paginated search shape, never the
  legacy non-paginated folder response. The host constructs one exact
  `'<parent_id>' in parents and trashed = false` filter and exhausts the
  advertised `document`, `image`, and `folder` categories independently,
  returning each opaque `next_page_token` unchanged. Legacy response shapes
  and malformed, repeated, or over-bound continuation evidence block
  completeness.
- Drive raw-file replacement exposes no atomic revision precondition. It is
  permitted only under proven serialization with exact file ID, immediate
  pre-write `modified_time` plus complete-byte SHA-256 guard, and immediate
  exact readback. Create-only installation remains a separate protocol.
- Gmail discovery follows every `next_page_token`. Optional private
  `seed_after_inclusive_ms`/`seed_before_exclusive_ms` bounds add deliberately
  widened epoch-second provider predicates: the inclusive start backs up one
  whole second and the exclusive end advances one whole second. Every returned
  search hit is then read in `full` form and its exact 13-digit `internal_date`
  is filtered to `[start,end)`. A competing provider date predicate blocks.
  Complete conversation membership is read separately. Reaching the bounded
  thread-message cap is incomplete and blocks. Raw RFC 2822 and provider `full`
  Unicode are distinct reads and must satisfy the strict source-admission gate.
- Gmail attachment extraction and exact source-linked HTTPS resource fetches
  are separate bounded paths. Provider-extracted text never proves original
  bytes; every PDF page/image unit must carry its actual extraction evidence.
- Sheets uses native metadata, bounded CellData, and raw `batchUpdate`. Native
  comments are read through all pages and written with immutable effect text;
  an absent anchor is recorded, never synthesized. This surface has no separate
  historical task-activity or move endpoint, so the capability profile must not
  claim either.

Manual and scheduled profiles are distinct. An observed interactive connector
probe does not establish background authorization, timeout, retry, overlap, or
scheduler conformance. No private IDs, queries, recipients, or credentials
belong in this adapter.

The installed profile-selection object retains exact immutable profile bytes
independently for `manual` and `scheduled`. The guarded
`scripts/readmit_connected_profile.py` route qualifies one observed profile for
its matching entrypoint, creates and reads it back, then replaces and reads back
that selector by its existing exact Drive ID. It cannot promote an unverified
profile or use manual evidence for scheduled admission.

The current `scripts/run_operation.py --host-jsonl` path stops after exact
bootstrap identity/readback and reports `BOOTSTRAP_READBACK_VERIFIED`. Before
calling Drive it validates a narrow bootstrap-read profile: matching execution
surface, authentication, local execution, complete storage read/file transfer,
the storage network path, and `storage.read_complete`. Mail, task, pagination,
daily-operation, and scheduler conformance are not inferred. The readback must
contain strict raw base64 bytes whose decoded length matches both the fetch and
Drive metadata sizes. It does not run source import, semantic processing, task
synchronization, brief rendering, delivery, or cursor commit. A concrete
installed daily entrypoint still needs accepted bindings for recovered
state/package custody, Drive artifact/checkpoint persistence, Gmail-to-catalog
import, interpretation plus
independent audit, native-Sheets task synchronization, finalized brief input
and rendering, exact delivery, and last-step cursor commit.

Every host result, including semantic results that bypass connector structured-
content normalization, must remain finite JSON. Delivery confirmation binds the
raw Sent observation ID to the exact ID requested from `read_sent`; matching
bodies or headers from a different provider object cannot confirm or heal
durable state. Every non-final same-phase unit must also persist and return a
nonempty durable checkpoint identity before the next unit starts.
