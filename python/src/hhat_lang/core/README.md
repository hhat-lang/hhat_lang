# H-hat Core

Language-agnostic substrate for H-hat. Provides: intermediate representations (IR), type system, memory & scope model, execution interfaces, symbol/import resolution, error model, and low-level backend abstraction.

Focus: deterministic IR construction + portable execution semantics for both classical and quantum operations.

> Deprecation Notice: Any legacy AST-based build path is deprecated and will be removed. Only direct construction of Core IR objects is supported going forward.

## 1. Scope & Responsibilities
Included:
* Stable in-memory IR objects (program/module, blocks, instructions, symbol tables).
* Type primitives (classical + quantum) and size/layout utilities.
* Memory model (stack / heap abstraction, scope frames, index & qubit allocation).
* Execution contracts: evaluators consume IR + memory and emit side-effects to backend adapters.
* Import/link layer (cross-module symbol/type resolution; namespace integrity).
* Error categorization and propagation utilities (typed, non-exceptional flow where practical).
* Backend boundary traits for quantum/classical target emission.


## 2. High-Level Data / Control Flow
Dialect Frontend (Direct IR Builder) → Core IR Module(s) → (Optional: Link/Import) → Interpreter / Program (Evaluator + Memory) → Backend Adapter → Target Runtime

Key transitions:
1. Build: Frontend constructs canonical IR instructions directly (modules, blocks, symbol & type tables) – no intermediate AST layer.
2. Linking: Inter-module references resolved via namespace + symbol tables (no partial binding at runtime) using reference tables (`RefTable` for types & functions).
3. Execution: `BaseInterpreter` / `BaseProgram` coordinate an Evaluator walking IR blocks; memory manager mediates value & qubit allocation; backend adapter receives finalized low-level operations.
4. Backend emission is intentionally side-effect isolated (pure-ish translation functions with explicit state objects).

Determinism goals: identical source + dependency graph → identical IR graph IDs & instruction ordering (facilitates reproducible testing and potential memoization).


## 3. Directory Overview
Only conceptual roles; per-file detail intentionally omitted here.

* `code/`: IR structures (modules, blocks, instructions), symbol & reference tables, helper utilities for graph-like traversals.
* `compiler/`: (Legacy abstraction – slated for removal) Previously housed transformations from parsed structures into IR. Direct IR builders in dialect frontends should be used instead.
* `data/`: Canonical symbolic entities (variables, literals, function signatures) used across IR stages.
* `error_handlers/`: Central error enumerations + lightweight Result-like helpers; unify reporting format.
* `execution/`: Abstract program & evaluator contracts; scheduling / stepping semantics over IR.
* `imports/`: Resolution & namespace binding for cross-unit symbols, including type merging guardrails.
* `lowlevel/`: Abstract quantum language / backend target traits (e.g., emission surface for QASM-like languages).
* `memory/`: Runtime memory / scope frames, allocation strategies (indices, qubits), lifetime & ownership invariants.
* `types/`: Type system primitives and registry support for dialect or backend extensions.
* Root helpers (`namespace.py`, `utils.py`): canonical naming + deterministic ID generation + ordered mappings.

## 4. Core Abstractions
IR:
* Instruction: minimal opcode + operand/value references + optional attributes/flags.
* Block: ordered instruction list; no implicit control-flow edges beyond explicit terminators (keeps analysis simple).
* Module: owns symbol/type tables and top-level blocks (entry + subsidiary) plus import metadata.

Type System:
* Distinguishes classical scalar/composite vs quantum entities (e.g., qubit arrays); layout metadata available for memory planning.
* Registration mechanism allows dialect or backend to introduce new intrinsic types while preserving core invariants (unique name, stable size semantics if classical).

Memory Model:
* Frame stack (lexical scopes) + heap-like region for dynamic or composite values.
* Deterministic allocation order; provides stable IDs for referencing values and quantum resources.

Execution:
* `BaseInterpreter` defines parse/evaluate orchestration; `BaseProgram` encapsulates execution context (IR block, evaluator, low-level language, stacks, symbol table).
* Evaluator consumes a Program (collection of modules) and drives instruction dispatch (`run` / recursive `walk`).
* Side-effects mediated through a narrow backend interface to isolate target-specific behavior.

Import / Linking:
* Namespace objects ensure collisions resolved explicitly; no silent shadowing across modules.
* `RefTable` holds per-IR references: `RefTypeTable` (types) + `RefFnTable` (functions) keyed by symbols/function signatures to originating IR hashes.
* Linking produces a fully resolved symbol table + populated reference tables before execution (no lazy resolution during evaluation phase).

Errors:
* Typed error objects; common pattern: return Ok(value) | Err(error) instead of raising (except truly exceptional conditions – programmer mistakes, internal invariants).

Low-Level Backend Interface:
* Defines capability surface (emit gate, allocate qubit, map measurement, etc.).
* Backends declare feature flags; lowering or execution may branch on availability early to fail fast.

## 5. Extension Points
Add a new Type:
1. Define type descriptor (ensuring unique canonical name and size / arity metadata).
2. Register with type registry in `types/` before IR construction needing it.
3. Provide lowering logic in dialect compiler if syntax introduces the type.

Add an Instruction:
1. Specify opcode + operand schema + side-effect classification (pure, reads memory, writes memory, affects control, quantum operation).
2. Extend instruction factory / enum in `code/`.
3. Update evaluator dispatch table; ensure Result-based error paths.
4. Add minimal tests (construction, evaluation, error case) under `tests/core`.

Add a Backend Adapter:
1. Implement required low-level interface methods (qubit allocation, gate emission, finalize / serialize).
2. Declare capability flags; add mapping layer from IR instruction subset to backend ops.
3. Provide adapter-specific tests asserting translation correctness & failure modes.

Import Mechanism Extension:
* For dialect-specific resolution rules, wrap or extend importer utilities; never bypass namespace validation.

## 6. Design Principles & Invariants
* Separation of Concerns: IR is structurally simple; semantic richness resides in types + symbol metadata.
* Determinism: ID and ordering generation functions are pure with respect to input graph shape.
* Explicit State: Memory / backend state objects passed, not global singletons.
* Fail Fast: Validate opcode/type compatibility on construction when feasible.
* Minimal Hidden Mutation: Instruction objects are immutable post-finalization (conceptual contract; enforce via usage discipline).
* Namespace Clarity: Fully-qualified names required at linking boundaries; short names only inside a resolved module scope.


## 7. Program Lifecycle
1. Build IR: Dialect frontend directly creates IR modules (blocks, instructions, symbol & type tables).
2. Link: Imports resolved; cross-module references validated; type compatibility checks executed.
3. Prepare Execution: Memory manager initializes global frame; backend adapter declares capabilities.
4. Evaluate: Instruction iteration + dispatch; memory & backend operations emitted.
5. Finalize: Backend flush / serialization; collected results returned.
