# Shared tool mappings

These supplied mappings belong with official `system` instructions. They define
School-OS meanings for a tool; each executing agent uses its own authorized
connector. They are not API clients, credential stores, capability probes or
evidence that a managed agent supports the operation.

| Mapping | Operations | Required capability boundary |
|---|---|---|
| [Google Drive](google-drive.md) | Setup, bounded canonical storage and readback | Full file contents, selected-root access, bounded listing and verified writes. |
| [Gmail](gmail.md) | Individual-message discovery, content and authorized email send | Original metadata, declared search-time meaning, complete continuation, body/attachment access; sending is separately authorized. |
| [Google Sheets](google-sheets.md) | Optional parent task projection | Identified rows, mapped columns, parent-edit readback and complete relevant range access. |
| [Todoist](todoist.md) | Optional parent task projection | Read/write owned identity marker, task state and selected review section; occurrence coverage where recurrence is used. |
| [ElevenLabs](elevenlabs.md) | Optional audio companion | Selected authorized generation and retrievable audio, plus a separately capable delivery route. |

Setup offers only tools actually available or explicitly requested, with their
known limits. It does not select all these tools. Configuration references the
chosen mapping; another agent reuses it through its own connector. Missing
semantics remain unsupported or unknown. A conformant user-created mapping may
be added in `extensions` using [the writing template](../operations/tool-adapter-template.md).
Account/container identifiers stay in private configuration, not these files.

Product descriptions below were checked against linked official documentation
on 2026-09-16. They establish product concepts, not a particular connector's
capabilities. School-OS policy comes from [the data contract](../contracts/data.md)
and [operations](../operations/README.md). No probe, functional check or effect
was performed while authoring these mappings.
