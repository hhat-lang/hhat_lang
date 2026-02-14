# Error Handlers

Centralized error handling for the H-hat core. Defines error codes and concrete error classes used across the entire framework and its dialects.

## Overview

H-hat uses a dual error strategy: an `ErrorHandler` base exception class for structured errors, and the `Result`/`Ok`/`Error` pattern (in [`../utils.py`](../utils.py)) for monadic error propagation in instruction execution. When a function returns `ErrorHandler` instead of raising it, callers can inspect errors without unwinding the stack.

## Directory Structure

```
error_handlers/
  __init__.py
  errors.py        # ErrorCodes enum, ErrorHandler ABC, and all concrete error classes
```

## Module Details

### errors.py

**`ErrorCodes`** -- Enum with 20+ error codes grouped by domain:

| Domain | Codes | Triggered by |
|--------|-------|-------------|
| Index | `INDEX_ALLOC_ERROR`, `INDEX_VAR_HAS_INDEXES_ERROR`, `INDEX_INVALID_VAR_ERROR`, `INDEX_UNKNOWN_ERROR` | Qubit/index allocation in `IndexManager` |
| Type | `TYPE_QUANTUM_ON_CLASSICAL_ERROR`, `TYPE_AND_MEMBER_NO_MATCH`, `TYPE_ADD_MEMBER_ERROR`, `TYPE_SINGLE_ASSIGN_ERROR`, `TYPE_STRUCT_ASSIGN_ERROR`, `TYPE_UNION_ASSIGN_ERROR`, `TYPE_ENUM_ASSIGN_ERROR` | Type system validation in [`../types/`](../types/) |
| Container/Variable | `CONTAINER_VAR_ASSIGN_ERROR`, `CONTAINER_VAR_IS_IMMUTABLE_ERROR`, `VARIABLE_WRONG_MEMBER_ERROR`, `VARIABLE_CREATION_ERROR`, `VARIABLE_FREEING_BORROWED_ERROR` | Variable operations in [`../data/variable.py`](../data/variable.py) |
| Cast | `CAST_NEG_TO_UNSIGNED_ERROR`, `CAST_INT_OVERFLOW_ERROR`, `CAST_ERROR` | Type casting in [`../types/builtin_base.py`](../types/builtin_base.py) |
| Memory | `STACK_EMPTY_ERROR`, `STACK_OVERFLOW_ERROR`, `HEAP_INVALID_KEY_ERROR`, `HEAP_EMPTY_ERROR` | Stack/Heap operations in [`../memory/`](../memory/) |
| Quantum | `INVALID_QUANTUM_COMPUTED_RESULT` | Target backend execution |
| Instruction | `INSTR_NOTFOUND_ERROR`, `INSTR_STATUS_ERROR` | Instruction dispatch in low-level backends |

**`ErrorHandler`** -- Abstract base class extending `BaseException`. Each subclass stores contextual data (variable names, values, limits) and implements `__call__()` to produce a human-readable error message. The `error_code` property returns the associated `ErrorCodes` member.

**Concrete error classes** (20+): `IndexAllocationError`, `TypeQuantumOnClassicalError`, `ContainerVarError`, `CastNegToUnsignedError`, `StackEmptyError`, `HeapInvalidKeyError`, `InvalidQuantumComputedResult`, `InstrNotFoundError`, among others. Each corresponds to exactly one `ErrorCodes` value.

## Connections

This module is imported throughout the codebase:

- **`core/data/variable.py`** returns `ContainerVarError`, `ContainerVarIsImmutableError`, `VariableCreationError`, `VariableFreeingBorrowedError`, `VariableWrongMemberError`
- **`core/memory/core.py`** returns index and memory errors
- **`core/types/`** returns type validation errors
- **`low_level/`** returns `InstrNotFoundError`, `InvalidQuantumComputedResult`

## Design Notes

**Return vs. raise**: Throughout the codebase, most functions that can fail return an `ErrorHandler` instance rather than raising it. For example, `IndexManager.add()` returns `IndexVarHasIndexesError` if the variable is already registered, and `VariableTemplate.__new__()` returns `VariableCreationError` on paradigm mismatch. This pattern lets callers inspect errors as values (often using the `Result`/`Ok`/`Error` types from `utils.py`) without try/except overhead. Exceptions are reserved for true programming errors (assertions, `NotImplementedError` for stubs).

**Adding new errors**: Each error needs three things: (1) a new `ErrorCodes` member, (2) a new class inheriting from `ErrorHandler` with `error_code` pointing to that member, and (3) a `__call__` method returning the human-readable message string.

## Current Status

Fully implemented. All error codes have corresponding concrete classes with context-aware messages.
