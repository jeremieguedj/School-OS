# ElevenLabs audio adapter

Status: optional reference adapter.

The adapter accepts a source-linked current-run delta, selected voice mapping, and sentence-level delivery/emotion metadata from private configuration. It may generate audio only when the runtime has explicit outbound API capability and authorized credential access.

The adapter must:

- never receive or store credentials in this repository;
- declare supported formats, job/polling behavior, limits, and cost handling;
- return a verified retrievable output before email attachment;
- treat unavailable API access as an optional degraded outcome; and
- avoid narrating content outside the approved current-run delta.
