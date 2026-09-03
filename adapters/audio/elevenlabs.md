# ElevenLabs audio adapter

Status: optional reference adapter.

The adapter accepts a source-linked current-run delta, selected voice mapping, and sentence-level delivery/emotion metadata from private configuration. It may generate audio only when the runtime has explicit outbound API capability and authorized credential access.

The adapter must:

- never receive or store credentials in this repository;
- declare supported formats, job/polling behavior, limits, and cost handling;
- return a verified retrievable output before email attachment;
- treat unavailable API access as an optional degraded outcome; and
- avoid narrating content outside the approved current-run delta.

## Dialogue voice compatibility

For multi-speaker output, use `POST /v1/text-to-dialogue` with
`model_id: "eleven_v3"` and one `{voice_id, text}` item per turn. The API path
is versioned as `v1`; that is separate from the model identifier.

Voice IDs can be account, workspace, or entitlement specific. Before a paid
dialogue request, retrieve `GET /v1/voices` with the same credential and fail
closed if any configured ID is absent. A verified public fallback pair is
Roger (`CwhRBWXzGAHq8TQ4Fs17`) and Sarah (`EXAVITQu4vr4xnSDxMaL`), but an
instance owner must still validate their own account's catalog.
