# Connected source host protocol

This is the finite Codex-host contract for connected Gmail attachment and
direct HTTPS image/PDF ingestion. It does not authorize arbitrary connector
names, arbitrary links, crawling, hidden metadata extraction, or embedded-file
extraction.

## Native capabilities used

The exact host surface inspected for this implementation exposes:

- `gmail_read_attachment(message_id, attachment_id | filename)`, whose
  `structuredContent.result` uses snake-case fields and supplies original bytes
  through `file_uri.download_url`; `size_bytes` is optional; and truncated
  provider extraction is referenced by `extraction_file_uri`.
- `view_image(path, detail)`, where `path` is a local file and
  `detail="original"` preserves the original resolution. Its returned image is
  interpreted by the host model; the tool itself does not return a text
  transcription.

Gmail is therefore connector-normalized by `CodexGmailPort`. The two local
source helpers return raw mappings through `JsonlPeer.call`; they must never be
passed through connector `structuredContent` normalization.

## Executable host loop

Run the child in its mode-0700 bridge directory. For each emitted
`SCHOOL_OS_REQUEST <id> <kind> <sha256> <request_path>` line, execute:

```text
python3.12 scripts/run_source_host.py prepare RUN_DIR REQUEST_PATH SHA256
```

For `resource.fetch_https`, the command performs the fetch and returns a JSON
object with `action="respond"`. Paste only its `control` object as one JSON line
to the child. The concrete fetcher allows HTTPS GET only, resolves and rejects
non-public addresses on every redirect, pins TLS to an inspected address while
retaining hostname verification, requests identity encoding, applies one
end-to-end deadline, follows a bounded non-repeating redirect chain, reads at
most `max_bytes + 1`, requires real EOF and any declared length to agree, and
returns standard padded base64.

For `extract.image`, the command returns `action="view_image"` and exact
`arguments`. Invoke only:

```text
view_image({"path": ACTION.arguments.path, "detail": "original"})
```

Transcribe all reader-visible content without using hidden metadata. Write the
finite result `{"detail":"original","text":"..."}` as a mode-0600
`*.view-result.json` direct child of `RUN_DIR`, then execute the returned
completion command with that path. Paste only the completion output's `control`
object to the child. The prepare step copies verified bytes to a host-owned
random path; completion requires the same device, inode, size, modification
time, SHA-256, MIME, dimensions, and source identity after viewing. A changed
file or empty transcription blocks. Blank or decorative disposition is not
inferred by this helper.

## Gmail and PDF boundaries

`ConnectedSourceAdapters.gmail_attachment` validates the advertised Gmail
identity, filename, MIME, `size_bytes`, `file_uri`, optional extraction URI, and
truncation fields. It downloads only `file_uri.download_url` through the finite
HTTPS route and binds the resulting size, MIME, URL chain, file ID, and SHA-256.
Inline `content` and `images` are preview-only and never become evidence. The
provider extraction path is not selected by this release, so even a complete
`extraction_file_uri` is validated as a reference but not read.

PDF input is parsed before Poppler runs. Every MediaBox, CropBox, and rotation
is finite and bounded; CropBox must be within MediaBox; embedded/associated
files and substantive unsupported annotation types block. The per-page
`pdftoppm` command uses `-cropbox` and an explicit `-scale-to` derived from both
the configured dimension and pixel limits. Aggregate planned pixels, produced
PNG bytes, output text bytes, page count, per-page time, and original bytes are
bounded. Every page is then processed by the same stable original-detail image
handoff in order. Live Gmail shape and image semantic accuracy remain
unqualified until observed on the authenticated target surface.
