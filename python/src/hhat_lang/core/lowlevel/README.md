# Low Level Backends Overview

Adapter interfaces that translate resolved program operations into target device or runtime instructions for quantum execution. This layer connects Core IR and evaluated state to concrete backend languages and drivers while preserving determinism, correctness, and clear error propagation. It is dialect agnostic and backend agnostic and it exposes a precise contract that concrete adapters implement.

## 1. Purpose
Provide a single abstraction that receives quantum data, program structure, allocation indices, runtime evaluator context, a quantum oriented stack, and symbol information, then emits target specific instructions and an assembled program artifact. The design emphasizes explicit ownership of resources, stable ordering of effects, and typed error reporting without relying on exceptions for normal control flow.

## 2. Context and Scope
**Position in the pipeline**
* Input comes from linked Core IR and from evaluated state that determines data values and allocation state.
* Output is a backend program string or equivalent instruction stream suitable for a target language or driver.
* The layer neither defines type rules nor performs linking. It consumes already validated structures and focuses on emission.

**Responsibilities**
* Initialize target language environment by emitting headers, pragmas, or capability declarations as required by the target.
* Map abstract operations to concrete target instructions while honoring quantum and classical boundaries.
* Assemble a complete program artifact with a deterministic layout derived from the program structure and allocation indices.
* Integrate with the evaluator to support optional execution or submission to a runtime after emission.

## 3. Abstraction Model
The base adapter aggregates the following runtime and structural inputs
* Quantum data reference that identifies the working quantum entity or aggregate under emission.
* Program block from the intermediate representation that supplies the ordered sequence of operations and nested structure.
* Index manager that exposes which indices are currently bound to the quantum data reference and that yields a deterministic ordering of these indices.
* Evaluator handle used to interact with the execution subsystem when emission must coordinate with runtime state or when optional execution follows emission.
* Quantum oriented stack used for scoped resources or for staging values across emission steps where stack discipline is required.
* Symbol table view that allows resolution of names during emission in cases where target languages require explicit bindings or declarations.

The adapter validates at construction that the quantum data reference has an assigned index set. On failure the adapter aborts emission by raising a typed handler or a runtime error according to policy. No implicit recovery is performed. Otherwise the adapter caches the number of indices and retains references to all inputs. No implicit global state is used for these concerns.

## 4. Interface Contract
Concrete backends implement the following routines while preserving the semantics described here. Names of routines are abstracted in this document. The contract specifies behavior rather than identifiers.
* Initialization routine returns an ordered tuple of target specific prologue elements such as headers or capability declarations. The tuple order is stable and deterministic for a given program and configuration. Prologue content is deterministic for a fixed program and configuration.
* Epilogue routine can be present in concrete backends and emits target specific footers such as measurements or synchronization directives. When present epilogue content is deterministic.
* Instruction generation routine accepts operation descriptors and optional adapter parameters and returns either a typed success result or a typed error. Success yields a collection of target instructions that are suitable for later assembly. Errors include structured information for diagnostics and are not delivered via exceptions during normal operation.
* Program assembly routine produces a textual program artifact or equivalent final representation required by the target driver. The routine may consume previously generated instructions or may traverse the program block directly. The output is pure with respect to the adapter state other than deterministic counters or caches that do not affect semantics. Assembly composes the prologue, the body, and an optional epilogue in a deterministic order for a fixed input.
* Invocation routine provides a callable entry point that orchestrates initialization, instruction generation, and program assembly. The return value is defined by the adapter and can be the final artifact or a driver facing result.

## 5. Processing Flow
Emission proceeds in the following canonical order
1. Query the index manager for the set of indices that the quantum data reference currently occupies and cache their count. Ordering is provided by the indexing subsystem and is read as needed.
2. Produce target prologue elements through the initialization routine. These elements can include pragmas, version markers, or allocation statements required before body emission.
3. Traverse the program block in a deterministic order. For each operation produce target instructions using the instruction generation routine. Instruction emission consults the symbol table when a mapping from abstract names to concrete identifiers is necessary.
4. Assemble the final program using the program assembly routine. Assembly composes the prologue, the body, and an optional epilogue in a deterministic order. Program assembly can return an empty artifact when the program has no target instructions.
5. Optionally pass the program to the evaluator for execution or submission. Side effects on the evaluator are explicit and occur only through the adapter handle.

## 6. Resource and Index Discipline
* Indices originate from the memory subsystem. The adapter does not allocate or free indices and only queries and reads them.
* Emission reads the current assignment supplied by the indexing subsystem and uses it consistently. Mutation of the assignment during a single emission pass is outside the contract. Adapters prevent it by snapshot and validation or abort emission.
* Ordering of indices follows the order provided by the indexing subsystem. Instruction templates must not reorder bits or wires implicitly. Any reordering required by a target must be explicit.
* The quantum oriented stack is used only for structured scopes within emission. The adapter does not leak stack frames across calls.

## 7. Error Model and Results
* The instruction generation routine returns a typed result on success and a typed handler on failure. Initialization returns a prologue tuple and program assembly returns a program artifact. Adapters avoid exceptions during normal flow and reserve raising for boundary integration scenarios. Unsupported instruction fallback is backend specific and may not be present. When no fallback exists, adapters raise a not implemented error.
* Construction may escalate a typed handler when the quantum data reference has no assigned index set. This protects against emitting instructions that reference unmanaged resources.
* Instruction generation reports invalid operations such as unsupported gates, arity mismatches, paradigm violations, or references to missing symbols. Errors carry structured context for diagnostics.
* Program assembly reports format violations such as conflicting declarations or missing prologue requirements for the chosen target.

## 8. File Inventory
1. `__init__.py`: Package marker with no runtime behavior.
2. `abstract_qlang.py`: Defines the base adapter for quantum low level emission. The adapter aggregates a quantum data reference, a program block from the intermediate representation, an index manager, an evaluator handle, a quantum oriented stack, and a symbol table view. Construction queries the index manager to validate that the quantum data reference is in use and caches the number of indices. It specifies the four routines described in the interface contract section that concrete backends must implement. Instruction generation relies on a typed result container to return success and failure in a uniform way.
