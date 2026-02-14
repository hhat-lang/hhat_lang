# Low-Level Language Abstraction

Defines the abstract interface for transforming H-hat quantum data and IR instructions into low-level quantum language code (e.g., OpenQASM).

## Overview

When a H-hat program contains quantum instructions, the dialect's quantum program hands them to a low-level quantum language backend. This module defines the `BaseLowLevelQLang` contract that all such backends must implement.

## Directory Structure

```
lowlevel/
  __init__.py
  abstract_qlang.py    # BaseLowLevelQLang ABC
```

## Module Details

### abstract_qlang.py

**`BaseLowLevelQLang`** (ABC) -- Holds quantum data and transforms it into target-specific code. Constructed with:

- `qvar` (`WorkingData`) -- The quantum variable being processed
- `code` (`IRBlock`) -- The IR block containing quantum instructions
- `idx` (`IndexManager`) -- Qubit index allocator (used to determine `_num_idxs`)
- `executor` (`BaseEvaluator`) -- Classical evaluator for fallback execution
- `qstack` (`BaseStack`) -- Quantum-specific stack

Abstract methods that backends must implement:

| Method | Returns | Purpose |
|--------|---------|---------|
| `init_qlang()` | `tuple[str, ...]` | Generate language header (version, register declarations) |
| `gen_instrs()` | `Result` or `ErrorHandler` | Translate a single IR instruction |
| `gen_program()` | `str` | Produce the complete target-language program |
| `__call__()` | `Any` | Callable interface |

The constructor computes `_num_idxs` from the `IndexManager`'s allocation for the given quantum variable.

> **Note**: The constructor currently imports `IRBlock` from `dialects/heather/code/simple_ir_builder/ir.py`. This is a known coupling between the core abstraction and the Heather dialect that may be refactored to use the abstract `BlockIR` from `core/code/ir.py` instead.

## Connections

- **Implemented by**: [`../../low_level/quantum_lang/openqasm/v2/qlang.py`](../../low_level/quantum_lang/openqasm/v2/qlang.py) (`LowLeveQLang`)
- **Used by**: [`../execution/abstract_program.py`](../execution/abstract_program.py) (`BaseProgram`) and the Heather quantum program
- **Depends on**: [`../memory/core.py`](../memory/core.py) (`IndexManager`, `BaseStack`), [`../execution/abstract_base.py`](../execution/abstract_base.py) (`BaseEvaluator`)

## Implementing a New Backend

To add a new low-level quantum language backend (e.g., NetQASM, Cirq):

1. Create a class inheriting from `BaseLowLevelQLang`
2. Implement `init_qlang()` to return the program header (version declarations, register definitions)
3. Implement `gen_instrs()` to translate individual IR instructions to your target language
4. Implement `gen_program()` to assemble the full program string from header, body, and measurements
5. Create instruction classes inheriting from `QInstr`/`CInstr` (in `core/code/instructions.py`) with a `name` attribute matching the H-hat instruction name (e.g., `"@redim"`)
6. Create a target backend executor with `load`, `sample`, and `execute` functions (see `low_level/target_backend/qiskit/` for reference)

Currently, backend selection is hardcoded in the quantum program. A future configuration system will let projects specify their backend via config files.

## Current Status

ABC is fully defined. The only concrete implementation is the OpenQASM v2 backend.
