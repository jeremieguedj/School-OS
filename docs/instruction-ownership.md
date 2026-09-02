# Instruction ownership

Each durable rule has one owner.

| Rule type | Owner |
|---|---|
| System boundaries and invariants | `docs/architecture.md` |
| Agent routing and precedence | `START-HERE.md` |
| Operation procedure | One file in `core/operations/` |
| Data structure | One file in `schemas/` |
| Classification decisions | `core/decision-tables/` |
| Runtime/provider technical mapping | One selected file in `adapters/` |
| Household values and integration selection | Private instance `config/` |
| Current cursors/bindings/run status | Private instance `state/` |
| Canonical knowledge and task history | Private instance `data/` |

Compatibility files may point to an owner but may not restate its rules. Generated files must identify their canonical inputs and generator operation.
