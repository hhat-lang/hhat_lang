# Execution

Abstract base classes defining the evaluation and program execution contracts that H-hat dialects must implement.

## Overview

H-hat separates execution into two roles: the **evaluator** handles classical instruction execution with access to memory, type, and function tables; the **program** orchestrates quantum execution by coordinating a low-level quantum language, index allocation, and a quantum stack. Dialects provide concrete implementations of both.

## Directory Structure

```
execution/
  __init__.py
  abstract_base.py      # BaseEvaluator ABC
  abstract_program.py   # BaseProgram ABC
```

## Module Details

### abstract_base.py

**`BaseEvaluator`** (ABC) -- The main execution engine for a dialect. Holds:

- `mem` -- `MemoryManager` for stack/heap/index operations
- `type_table` -- `TypeIR` with all registered types
- `fn_table` -- `BaseFnIR` with all registered functions

Abstract methods: `run(code)` and `__call__()`. Dialects implement these to walk IR blocks and execute instructions against the memory manager.

### abstract_program.py

**`BaseProgram`** (ABC) -- Represents a quantum program unit. Holds:

- `_qdata` -- `WorkingData` for the quantum data being processed
- `_idx` -- `IndexManager` for qubit allocation
- `_block` -- `BlockIR` containing the quantum instructions
- `_executor` -- `BaseEvaluator` for fallback classical execution
- `_qlang` -- `BaseLowLevelQLang` instance for low-level code generation
- `_qstack` -- `BaseStack` for the quantum execution stack

Abstract method: `run()` returns results or `ErrorHandler`.

## Connections

- **[`../memory/`](../memory/)**: `BaseEvaluator` owns a `MemoryManager`; `BaseProgram` uses `IndexManager` and `BaseStack`
- **[`../code/ir.py`](../code/ir.py)**: Both use `TypeIR`, `BaseFnIR`, and `BlockIR`
- **[`../lowlevel/`](../lowlevel/)**: `BaseProgram` delegates code generation to `BaseLowLevelQLang`
- **Implementations**: Heather implements `BaseEvaluator` in [`../../dialects/heather/interpreter/classical/executor.py`](../../dialects/heather/interpreter/classical/executor.py) and `BaseProgram` in [`../../dialects/heather/interpreter/quantum/program.py`](../../dialects/heather/interpreter/quantum/program.py)

## Design Notes

**Why two execution roles?** Classical and quantum execution have fundamentally different models. Classical execution is imperative: walk the IR, evaluate each instruction immediately against memory. Quantum execution is deferred: accumulate instructions into a circuit, compile to a low-level language, run on a backend, then retrieve results. Separating these concerns lets each branch manage its own resource lifecycle (e.g., `BaseProgram` owns qubit allocation via `IndexManager`, while `BaseEvaluator` owns the general-purpose `MemoryManager`).

**Classical fallback**: The quantum program holds a reference to `BaseEvaluator` because not all instructions in a quantum block may be supported by the low-level quantum language. For example, classical control flow or variable lookup within a quantum context falls back to the evaluator. This is noted as a TODO in the OpenQASM v2 backend.

## Current Status

Both ABCs are fully defined. Concrete implementations live in the dialect layer.
