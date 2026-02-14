# Target Backends

Execution backends that take generated quantum language code and run it on simulators or quantum hardware, returning measurement results.

## Overview

After the quantum language backend (e.g., OpenQASM v2) produces a program string, a target backend compiles it into a runnable circuit, executes it, and returns the measurement results as bitstring distributions. Currently, the only implemented backend uses Qiskit with the Aer simulator.

## Directory Structure

```
target_backend/
  __init__.py
  qiskit/                     # Qiskit-based backend
    __init__.py
    openqasm/
      __init__.py
      code_executor.py        # Circuit loading, sampling, and execution
  squidasm/                   # SquidASM backend (placeholder)
    __init__.py
```

## Module Details

### qiskit/openqasm/code_executor.py

Three functions forming the execution pipeline:

**`load_qasm(code: str) -> QuantumCircuit`**
Parses an OpenQASM v2.0 string into a Qiskit `QuantumCircuit` using `qasm2.loads()`.

**`sample_circuit(circuit, qdata, metadata=None) -> counts | ErrorHandler`**
Executes the circuit on the Aer simulator and returns measurement counts:
1. Creates an `AerSimulator` backend
2. Transpiles the circuit for backend compatibility
3. Creates a `SamplerV2` instance
4. Runs with configurable shot count (default: `num_qregs * 888`). The `888` multiplier is an arbitrary default -- callers can override via `metadata["shots"]`. More shots give more precise probability distributions but take longer.
5. Extracts counts from the `DataBin` result object
6. Returns a `Counter`-like dict mapping bitstrings to counts, or `InvalidQuantumComputedResult` on failure

**`execute_program(code: str, qdata, debug=False) -> counts | ErrorHandler`**
End-to-end execution: calls `load_qasm()` then `sample_circuit()`. If `debug` is `True`, prints the results. Returns the bitstring distribution or an error.

### squidasm/

Placeholder for a future [SquidASM](https://github.com/QuTech-Delft/squidasm) backend, intended for quantum network simulation. Currently contains only an empty `__init__.py`.

## Connections

- **[`../quantum_lang/`](../quantum_lang/)**: Produces the QASM code string that this module executes
- **[`../../dialects/heather/interpreter/quantum/program.py`](../../dialects/heather/interpreter/quantum/program.py)**: Calls `execute_program()` after `gen_program()` produces the QASM code
- **[`../../core/error_handlers/`](../../core/error_handlers/)**: Returns `InvalidQuantumComputedResult` when execution fails

## Design Notes

The backend is currently hardcoded to `AerSimulator` (a local simulator). There is a TODO to make this configurable via project settings, which would allow switching to real quantum hardware (IBM Quantum), different simulators, or other providers. The error handling after a failed quantum computation also needs a proper recovery strategy beyond the current minimal handling.

## Current Status

Qiskit/Aer backend is functional. Uses a hardcoded `AerSimulator` -- configurable backend selection (real hardware, different simulators) is a TODO. SquidASM is a placeholder.
