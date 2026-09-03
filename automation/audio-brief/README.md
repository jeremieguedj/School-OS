# Local audio brief worker

This folder contains the local, deterministic ElevenLabs part of the School-OS
audio-delivery workflow. It is intentionally generic: no household data,
contact name, Drive ID, provider identifier, or credential belongs here.

## Boundary

The local scheduled Codex task reads the private Drive knowledge base and writes
a temporary, source-linked manifest matching `manifest.example.json`. This
worker does not search Gmail, read Drive, or send WhatsApp messages. That keeps
the audio generator testable and gives a future WhatsApp UI step an explicit,
verified file to send.

The manifest should cover a fixed local daily window, such as 6:00 AM to 6:00
AM America/Los_Angeles. It should include only source-received facts and
action/guideline events that occurred in that window. The scheduled task must
keep a small send ledger so it does not deliver the same window twice.

## Secret setup: macOS Keychain

Use Keychain Access rather than a shell command, so the API key never enters
shell history:

1. Open **Keychain Access** and select the **login** keychain.
2. Choose **File → New Password Item**.
3. Set **Keychain Item Name** to `School-OS.ElevenLabs.APIKey`.
4. Set **Account Name** to your macOS login name.
5. Paste the ElevenLabs API key into **Password**, then save.

The script reads this item only when it actually calls ElevenLabs. It never
writes it to the repository, a manifest, a log, or an output file. If a
different Keychain account is needed later, pass `--keychain-account`; the
default is the current macOS user.

## Voice compatibility

The worker uses ElevenLabs' multi-speaker dialogue endpoint,
`POST /v1/text-to-dialogue`, with `model_id: "eleven_v3"`. API version and
model version are distinct: `v1` belongs in the URL and `eleven_v3` belongs in
the JSON body.

The bundled, verified fallback mapping is Roger
(`CwhRBWXzGAHq8TQ4Fs17`) and Sarah (`EXAVITQu4vr4xnSDxMaL`). They were
confirmed to generate a multi-voice MP3 through this endpoint. Before every
paid synthesis request, the worker calls `GET /v1/voices` and refuses to run
if any configured voice ID is absent. This prevents a confusing paid request
failure when a copied recipe contains library or workspace-specific IDs.

If you want different voices, first list the voices available to *your* API
key, then update a private voice map or your local copy of the mapping. Do not
assume an ID published by someone else is licensed for your account.

Each private manifest selects a generic `voice_role` (`voice_a` or `voice_b`)
rather than placing household names in this public worker. The role mapping is
the only part that changes when an instance owner chooses a different voice.
Each record also supplies a private `subject_label`. The worker uses those
labels only in the spoken opening to summarize the sections covered that day.
It speaks the school name as `S-H-A`, produces a filename such as
`SHA Daily Brief Wednesday September 2nd.mp3`, and does not use commas in that
filename.

## Safe local test

This validates the manifest, voices, tags, and character cap without reading a
secret, contacting ElevenLabs, generating audio, or sending any message:

```sh
python3 automation/audio-brief/elevenlabs_audio_brief.py \
  --manifest automation/audio-brief/manifest.example.json \
  --output-dir /private/tmp/school-os-audio-test \
  --dry-run
```

## Production invocation

Only the local scheduled task should use this after it has written a private,
Drive-derived manifest to a run-scoped temporary directory:

```sh
python3 automation/audio-brief/elevenlabs_audio_brief.py \
  --manifest /private/tmp/school-os-audio/2026-09-03/manifest.json \
  --output-dir /private/tmp/school-os-audio/2026-09-03 \
  --whatsapp-compatible
```

The output is a new `sha-daily-audio-YYYY-MM-DD.mp3`. The script refuses to
overwrite a same-date file, verifies `audio/mpeg` and the MP3 signature, and
prints a SHA-256 after writing it.

WhatsApp delivery remains deliberately separate. It should accept only this
freshly verified file, resolve a user-confirmed contact, verify the outgoing
attachment in the WhatsApp app, and record delivery only after a confirmed
send.

## WhatsApp compatibility staging

An ElevenLabs MP3 can pass structural MP3 checks yet still be rejected by the
WhatsApp desktop media uploader. The observed cause was the raw ElevenLabs
file's ID3v2.4 tag. WhatsApp accepted a stream-copy remux carrying exactly the
same MPEG audio bytes with an ID3v2.3 tag. Use `--whatsapp-compatible` for
scheduled WhatsApp delivery; it keeps the exact user-facing filename and does
not transcode or degrade the audio.

For a standalone equivalent:

```sh
ffmpeg -nostdin -v error -i "raw-brief.mp3" -map 0:a:0 \
  -c:a copy -id3v2_version 3 "SHA Daily Brief Wednesday September 2nd.mp3"
```

Preserve the raw worker output for audit purposes and attach the staged copy.
