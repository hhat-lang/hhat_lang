# Error Handlers Overview

Centralized error semantics for the core layer. This directory defines a catalog of error conditions with stable identifiers and typed handlers that carry structured context. The design favors explicit and inspectable failure values over implicit exception flows. It supports precise pattern matching in evaluators, memory management, typing, and instruction orchestration across classical and quantum paradigms.

## 1. Purpose
Provide a coherent error model that
1. Assigns each failure mode a unique code and a human readable rendering.
2. Encodes contextual data inside the handler for diagnostic precision.
3. Enables propagation through typed results or direct handler values in normal control flow.
4. Escalation to exceptions or process termination is used for contract violations or boundary unwinding.

## 2. Design Overview
* A finite enumeration defines the error code space. Codes are grouped conceptually by subsystem such as indexing, typing, variables and containers, casting, calling, runtime stacks and heaps, symbol tables, instruction lifecycle, and quantum computation results. The set admits extension by appending new codes while preserving existing meanings.
* A typed handler binds one code to payload fields such as names, values, limits, kinds, or signatures. The handler is callable to render a message that embeds these payloads in a canonical sentence suitable for logging and user display. A compact representation string provides a stable process local summary for tracing and metrics.
* Handlers inherit from a common base that is also compatible with exception semantics. Normal usage returns either a handler value or a typed result wrapper rather than raising. Internal subsystems and adapters may raise or terminate for contract violations or when termination is desired.
* The interface is value based. Routing decisions are performed by inspecting the handler type or the code and optional payloads rather than matching on free form strings. Pattern matching on the handler type is standard and equivalent to matching on the code.

## 3. Error Taxonomy
**Index management**
* Unknown index state when no specific condition applies.
* Allocation failure with both requested count and maximum available count recorded.
* Variable already associated with indexes when attempting to assign new ones.
* Invalid variable reference that is not registered with the index manager.

**Type discipline**
* Quantum data nested inside classical data is rejected. The converse is permitted.
* Paradigm mismatch between a declared data kind and a member or value.
* Failure while adding a new member to a composite type declaration.
* Cardinality violation for single member forms.
* Incompatible member assignments for structured records, unions, or enumerations.

**Containers and variables**
* Assignment failure for a container in general.
* Mutation attempted on an immutable variable.
* Access to a wrong member for a variable container.
* Failure to create a variable given a name and an intended type.
* Freeing a variable that currently borrows data is refused.

**Casting**
* Casting a negative value to an unsigned target is refused.
* Casting an integer that exceeds the representable limit is refused.
* General cast failure for incompatible source and target kinds.

**Function invocation**
* Argument types do not match the expected signature derived from declaration.

**Runtime stacks**
* Retrieval failure for requested data from a frame.
* Misuse of a stack frame that is not defined for functions.
* Empty stack underflow.
* Stack overflow.

**Heaps**
* Invalid key for heap access.
* Empty heap when access is attempted.

**Symbol tables**
* Invalid key in the context of type lookup or function lookup. The rendering clarifies the context.

**Quantum computation**
* A quantum data value produced an invalid computed result.

**Instruction resolution**
* An instruction with a given name was not found.
* An instruction is in an invalid lifecycle status for the requested operation.

## 4. Interaction with Core Subsystems
* **Types and data**: Variable containers use these handlers for assignment validation, retrieval, and freeing. Paradigm checks and composite layout checks report typed failures rather than raising.
* **Memory**: The stack and heap models expose key errors through this catalog and provide codes for underflow and overflow. Evaluators can branch on codes to decide recovery or termination.
* **Code and execution**: Instruction lookup and lifecycle enforcement return typed failures on missing instructions or invalid statuses. Symbol table operations surface invalid key conditions and can raise standard exceptions for internal invariants.
* **Results**: Evaluators and helpers propagate success and failure with typed results or handler values. Callers render messages on demand or match on handler type or code for programmatic handling.

## 5. Usage Pattern
* Return a typed result or a handler value on failure in normal control flow. Avoid raising in normal control flow.
* Generate handlers as close as possible to the detection site and include the minimal payload needed to diagnose the issue. Examples are requested versus maximum counts, offending names, expected versus observed kinds, and architectural limits.
* For logging, call the handler to obtain the full message. For compact traces use the representation string which includes the code and a process local numeric identifier.
* At process boundaries where unwinding is required a handler may be raised. The same handler remains inspectable by upstream code.

## 6. File Inventory
1. `__init__.py`: Package marker without runtime behavior.
2. `errors.py`: Defines the error code enumeration and the family of typed handlers. Handlers encode contextual payloads for indexing, typing, containers and variables, casting, function invocation, stack and heap operations, symbol table validation, quantum result validation, and instruction lookup or status. Each handler exposes a callable renderer for human readable messages and a compact representation for tracing. All handlers share a common base compatible with exception semantics while remaining designed for explicit result based propagation.