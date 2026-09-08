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

The Codex host implementation follows this exact dispatch shape. `readPrivate`
and `writePrivate` below are implemented with bounded local commands whose
outputs remain inside the functions executor; they are never appended to the
model-visible result.

```javascript
const dispatch = Object.freeze({
  "drive.get_metadata": tools.mcp__codex_apps__google_drive_get_file_metadata,
  "drive.fetch": tools.mcp__codex_apps__google_drive_fetch,
  "drive.list_folder": tools.mcp__codex_apps__google_drive_list_folder,
  "drive.create_folder": tools.mcp__codex_apps__google_drive_create_folder,
  "drive.upload_file": tools.mcp__codex_apps__google_drive_upload_file,
  "drive.update_file": tools.mcp__codex_apps__google_drive_update_file,
  "gmail.search_ids": tools.mcp__codex_apps__gmail_search_email_ids,
  "gmail.read": tools.mcp__codex_apps__gmail_read_email,
  "gmail.read_thread": tools.mcp__codex_apps__gmail_read_email_thread,
  "gmail.read_attachment": tools.mcp__codex_apps__gmail_read_attachment,
  "gmail.send": tools.mcp__codex_apps__gmail_send_email,
  "sheets.get_metadata": tools.mcp__codex_apps__google_drive_get_spreadsheet_metadata,
  "sheets.get_cells": tools.mcp__codex_apps__google_drive_get_spreadsheet_cells,
  "sheets.batch_update": tools.mcp__codex_apps__google_drive_batch_update_spreadsheet,
  "comments.read_spreadsheet": tools.mcp__codex_apps__google_drive_get_spreadsheet_comments,
  "comments.write_file": tools.mcp__codex_apps__google_drive_bulk_update_file_comments,
});
const request = JSON.parse(await readPrivate(requestPath, requestSha256));
const invoke = dispatch[request.kind];
if (!invoke) throw new Error("unexpected School-OS request kind");
let responseValue;
try {
  const toolResult = await invoke(request.args);
  responseValue = {protocol: 1, request_id: request.request_id, result: toolResult};
} catch (error) {
  responseValue = {protocol: 1, request_id: request.request_id,
                   error: {class: "tool_exception", effect: "unknown"}};
}
const response = asciiJson(responseValue) + "\n";
await writePrivateNoncanonical(responsePath, response);
```

The semantic kinds are separately dispatched to actual interpreter and
independent-audit callbacks over the immutable packet boundary. Fixture or
synthetic callbacks are labeled synthetic and cannot authorize provider writes.
Connector structured content is inspected explicitly: current tools may return
the payload flat or under `structuredContent.result`, with tool metadata beside
it; both are normalized by checked-in code and error wrappers block. Text
content blocks and metadata never establish semantic verification.

## Selected connector limits

- Drive folder listing has a bounded `top_k` and no continuation token on this
  surface. A result that reaches the configured cap is incomplete and blocks.
- Drive raw-file replacement exposes no atomic revision precondition. It is
  permitted only under proven serialization with exact file ID, immediate
  pre-write `modified_time` plus complete-byte SHA-256 guard, and immediate
  exact readback. Create-only installation remains a separate protocol.
- Gmail discovery follows every `next_page_token`; the search overfetches whole
  boundary seconds and code filters `internal_date` to exact `[start,end)`.
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
