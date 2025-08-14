# Code IR Overview

Intermediate Representation (IR) substrate: structural program building blocks (modules, blocks, instructions), symbol & reference tables, PHF-assisted (perfect hash function) indexing helpers, and minimal utilities required for deterministic multi-IR linking. This layer is intentionally lean: semantic richness lives in type / data definitions and evaluator logic outside this directory.

## 1. Purpose
Provide canonical, reproducible in-memory forms of program units that other subsystems (compiler, execution, imports, memory, low-level backends) can consume without depending on dialect parsing details. Emphasis: structural integrity, stable hashing, linkability.

## 2. Provided Components
* IR Module: Owns the top-level executable block (main/root) and its symbol table.
* IR Block: Ordered container of IR instructions (no implicit edges; control only via explicit terminators or higher-level evaluator protocol).
* IR Instruction Base: Minimal opcode + argument tuple + cached hash; quantum/classical distinction surfaced via flag/paradigm traits in instruction specializations.
* Symbol Table: Ordered maps for types and function definitions (preserving deterministic insertion/hashing order).
* Reference Table: Cross-IR indirection maps for externally defined types/functions (type refs + function refs) storing origin IR identity.
* Perfect Hash Utilities: Parameter search + hashing primitives to compactly arrange references / grouped symbols with collision-free indexing for reproducible builds.

## 3. Responsibilities
Included:
* Structural data classes for instructions, blocks, modules, IR containers.
* Deterministic hashing of structural elements (stable equality + graph identity support).
* Storage & retrieval of typed entities (types, functions) via ordered symbol table abstractions.
* Reference indirection enabling separate compilation / multi-module linkage without eager materialization of foreign definitions.
* Basic quantum vs classical instruction flagging (status lifecycle, optional argument generation skip hints).
Excluded:
* Parsing or lowering logic (handled by compiler layer).
* Execution semantics or side-effect evaluation (execution layer).
* Type system definitions (types directory) and memory allocation (memory directory).
* Backend emission or quantum gate mapping (lowlevel directory).

## 4. Interaction with Other Core Layers
Flow: Compiler emits IR Module (symbol table + main block) → Imports layer augments Reference Table with external symbols → Execution layer walks instructions referencing symbol & reference tables → Low-level backend consumes resolved operations.

Key contracts:
* Imports: Consumes/produces RefTable entries keyed by symbol/function signature objects.
* Memory: Resolves concrete data objects for instruction arguments (evaluator uses symbol table entries to retrieve definitions).
* Types/Data: Supplies concrete type descriptors and function definition payloads stored in symbol table collections.

## 5. Lifecycle Position
Stage boundaries:
1. Construction: Compiler creates blocks, instructions, symbol table entries.
2. Linking: Reference table populated (external IR keys bound); PHF utilities optionally compute collision-free layouts.
3. Execution: Read-only traversal; structural objects treated as immutable.
4. Finalization: Downstream (backend / serialization) consumes resolved instruction stream; IR objects persist for debugging / introspection.
