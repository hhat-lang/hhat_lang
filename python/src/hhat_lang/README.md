# H‑hat Python Package
High-level container for the Python implementation of the H‑hat language stack. Provides:
* Core language substrate (IR, type system, memory / scope, import + linking, execution contracts, error model, backend abstraction).
* Dialect hosting surface (example dialect(s), parsing + lowering entry points, dialect-specific assets).
* Low-level target integration (quantum assembly language representations, backend adapters / emitters).
* User tooling (CLI, project scaffolding, notebook integration, auxiliary developer utilities).

## 1. Architectural Overview
End-to-end flow (conceptual pipeline):
Dialect Frontend (parse / build) → Core IR (modules, blocks, instructions) → Linking / Imports → Execution (interpreter / evaluator) → Low-Level Backend Adapter → Target Runtime (simulator / hardware / serialization)

## 2. Directory Topology
```
hhat_lang/
├── __init__.py        # Package marker / version surface (keep lightweight)
├── core/              # Stable substrate: IR, types, memory, execution, imports, error model, low-level abstraction
├── dialects/          # Dialect implementations + their parsers / lowerers / dialect-specific artifacts
├── low_level/         # Target-facing quantum language abstractions + backend adapter layering
└── toolchain/         # User & developer tooling (CLI, project scaffolds, notebook helpers)
```

Subdirectory scope (conceptual — refer to local READMEs for expansion):
* `core/`: Owns fundamental invariants. Defines data & control abstractions consumed by all other layers. Treated as the most stable boundary.
* `dialects/`: Houses one or more domain-specific syntactic/semantic layers built atop `core`. Each dialect lowers into the same IR to ensure uniform backend interoperability.
* `low_level/`: Encapsulates translation to concrete quantum (or hybrid) target languages and hardware/software backends. Keeps vendor / platform specifics out of `core` & dialect logic.
* `toolchain/`: Provides operational entry points: command-line interface, project creation, optional notebook integration, and any workflow utilities.
