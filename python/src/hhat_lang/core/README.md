# H-hat Core

Core, language-agnostic building blocks for H-hat: intermediate representations (IR), type system, memory model, execution traits, error model, and importing and linking.

## Directory Overview
- `code/`: Program IR (block- and table-oriented variants), instruction flags, symbol/reference tables, and graph helpers.
- `compiler/`: Abstractions for lowering parser output into the core IR.
- `data/`: Shared symbolic entities (symbols, literals, variables, function signatures).
- `error_handlers/`: Centralized error codes and typed error handlers.
- `execution/`: Evaluator and program interfaces that run IR against memory and backends.
- `imports/`: Importing and linking types and functions across IR units and dialects.
- `lowlevel/`: Interfaces to backend quantum languages or runtimes.
- `memory/`: Stack/heap, scope handling, index/qubit allocation, and `MemoryManager`.
- `types/`: Type-system primitives, built-ins (classical/quantum), and size utilities. Extend here; register via symbol tables in `code/`.

## Architecture Overview
Parse (dialect) → Compile → IR Module (+ optional IR Graph) → Execute (Evaluator + Memory) → Backend (low‑level)

- Parse (dialect): A dialect frontend (e.g., Heather) parses source into an AST.
- Compile: The compiler lowers AST into the core IR (block‑based preferred).
- IR Module (+ IR Graph): A program becomes an IR Module; multiple modules can be linked via an IR Graph and reference tables (types/functions) when importing across units.
- Execute (Evaluator + Memory): The evaluator steps through the IR; the MemoryManager manages scopes, stack/heap, and index/qubit allocation.
- Backend (low‑level): Low‑level adapters translate evaluated operations to target runtimes (e.g., QASM/Qiskit‑like backends).

## Root Modules

`namespace.py` introduces simple, explicit namespacing so identifiers are easy to read and reason about. Use `Namespace` to represent a path like `std.math` and `FullName` to pair that path with a concrete symbol. This keeps references unambiguous across dialects and modules and makes logs, errors, and docs read naturally (for example, `std.math.add`).

`utils.py` provides a few shared essentials used throughout the core. `gen_uuid` produces stable, deterministic integer IDs from arbitrary inputs; this is helpful for reproducible identifiers (such as scope IDs) across runs. `SymbolOrdered` is an ordered mapping that accepts familiar keys (strings or symbolic objects) and preserves insertion order while exposing plain values on iteration; it’s a practical fit for type members and variable storage when you want predictable layouts. Finally, the lightweight `Result` pattern (`Ok`/`Error`) standardizes how operations return either values or typed errors, keeping control flow explicit without throwing exceptions during normal execution.

Examples
```python
from hhat_lang.core.namespace import Namespace, FullName
from hhat_lang.core.utils import SymbolOrdered, Ok, gen_uuid

ns = Namespace("std", "math")
fullname = FullName(ns, "add")  # "std.math.add"

members = SymbolOrdered()
members["x"] = 1
rid = gen_uuid("scope:main")
assert Ok(42).result() == 42
```
