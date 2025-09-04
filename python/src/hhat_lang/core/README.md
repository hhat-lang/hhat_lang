# Core Layer Overview

Foundational abstractions and interfaces that define the program model, its intermediate representation (IR), the runtime memory model, evaluator contracts, cross-module linking, backend integration points, and error semantics. This layer is dialect-agnostic and backend-agnostic; it bounds the stable contracts used by compilers and tools within the project.

## 1. Purpose
Provide a coherent kernel for building, linking, and evaluating programs across classical and quantum paradigms. Emphasis is on:
* Ordered maps and explicit equality/hash semantics facilitate separate compilation. Python’s `hash()` is process‑local; cross‑run stability requires explicit identifiers (e.g., UUID v5 from canonical strings).
* Clear separation of concerns: syntax lives in dialects; execution/backends implement pluggable interfaces; core holds types, IR shape, and runtime contracts.
* Employ typed result propagation (`Ok`/`Error`) with explicit error codes along runtime paths; validation errors and precondition violations may raise exceptions.

## 2. Subsystem Layout
High‑level roles of the immediate subdirectories (detailed specifications appear in each subdirectory’s README):
* `code/`: Structural IR substrate (modules, blocks, instructions, symbol and reference tables, hashing helpers).
* `compiler/`: Lowering contracts from dialect-specific parses/builders into Core IR.
* `data/`: Canonical symbolic entities (symbols, literals), function signatures/definitions, and value containers.
* `types/`: Type-system primitives, built-ins, and size/compatibility utilities.
* `memory/`: Runtime memory model (stack/heap/scopes) and allocation/index management.
* `execution/`: Evaluator traits and program orchestration interfaces.
* `imports/`: Cross-IR linking and reference resolution protocols.
* `lowlevel/`: Backend adapter interfaces for emitting device/runtime instructions.
* `error_handlers/`: Centralized error codes and typed error handlers.

This README intentionally omits per‑file details for these directories; refer to each subdirectory’s README for specifications.

## 3. Processing Flow
Dialect Source → (Dialect Parser) → Compiler Lowering → Core IR Module(s) → Imports/Linking (external symbol refs) → Execution (evaluators + memory) → Low-level Emission (backend adapters).

Types and data entities propagate along this path: the compiler populates symbol/reference tables; the imports layer binds external entries; the execution layer materializes runtime values via the memory model; low‑level back ends consume resolved operations.

## 4. File Inventory
Technical description of the files in this directory (excluding subdirectories):

* `__init__.py`: Defines `DataParadigm` (`StrEnum`) with members `classical` and `quantum`. This enum provides an explicit, comparable tag used across core subsystems (types, data containers, evaluators) to select paradigm‑specific behavior. Invariants: the set of paradigms is fixed; clients must not rely on implicit truthiness or ad hoc strings.

* `namespace.py`: Namespacing utilities for stable, fully-qualified identifiers.
  - `Namespace`: Tuple‑backed namespace; supports membership tests and compact `repr` via dot‑separated segments. Serves as the canonical container for hierarchical scopes (e.g., module, package, dialect qualifiers).
  - `FullName`: Couples a `Namespace` with a terminal name; supports membership checks against the enclosing namespace and renders as `namespace.name`. Used wherever stable, human-readable, and hashable identifiers are required without embedding type information.

* `utils.py`: Core utilities used across IR construction and evaluation.
  - `gen_uuid(obj)`: UUID version 5 (OID namespace) converted to an integer; determinism assumes the input representation (`str(obj)`) is stable across runs (avoid ephemeral object representations) to ensure reproducible layout and indexing.
  - `SymbolOrdered`: Ordered mapping specialized for symbol-like keys. Accepts `str`, `Symbol`, `CompositeSymbol`, `WorkingData`, or `int` and normalizes to canonical keys, preserving insertion order. Contract: key normalization is lossless for symbol types; iteration preserves deterministic ordering; suitable for building symbol tables and composite data structures.
    The `keys()` method yields normalized values (e.g., `Symbol.value`) rather than typed key objects; use `items()` to retrieve typed keys.
  - `Result`/`Ok`/`Error`: Minimal typed result wrapper used by evaluators and instruction executions. `Ok` yields the successful payload; `Error` carries an `ErrorHandler`. Encourages explicit, inspectable handling of success and failure without raising exceptions through core layers.

## 5. Status
The core package provides stable scaffolding and directory-level READMEs. File-by-file documentation lives in each subdirectory. This document covers only the files defined directly in `core/` and the architectural role of its subdirectories.
