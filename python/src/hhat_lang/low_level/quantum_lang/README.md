# Quantum Language Interface

The `quantum_lang/` module provides low-level quantum language interfaces for compiling H-hat quantum operations to industry-standard quantum assembly languages.

## Overview

Provides quantum language backends:
- NetQASM (Network Quantum Assembly)
- OpenQASM (Open Quantum Assembly)
- Translation from H-hat IR to quantum languages
- Hardware-agnostic quantum operations

## Structure

```
quantum_lang/
├── __init__.py     # Module exports
├── netqasm/        # NetQASM backend
└── openqasm/       # OpenQASM backend
```

## Key Components

### netqasm/ - NetQASM Backend

**NetQASM** (Network Quantum Assembly):
- Quantum networking focus
- Distributed quantum computing
- Multi-node quantum applications

**Features:**
- Quantum network operations
- Entanglement distribution
- Teleportation protocols
- EPR pair generation

**Target Platforms:**
- NetSquid simulator
- SquidASM

### openqasm/ - OpenQASM Backend

**OpenQASM** (Open Quantum Assembly):
- IBM's quantum assembly language
- Industry standard for gate-based quantum computing
- Wide hardware support

**Features:**
- Gate-based quantum circuits
- Classical control flow
- Measurement operations
- Standard gate library

**Target Platforms:**
- IBM Quantum systems
- Qiskit simulator
- Many other quantum platforms

## Translation Pipeline

```
H-hat Quantum IR
        ↓
Quantum Operation Normalization
        ↓
Backend Selection (NetQASM/OpenQASM)
        ↓
Gate Translation
        ↓
Circuit Optimization
        ↓
Target QASM Output
        ↓
Hardware Execution
```

## Gate Mapping

### H-hat → OpenQASM

| H-hat         | OpenQASM      |
|---------------|---------------|
| `h(q)`        | `h q[0];`     |
| `x(q)`        | `x q[0];`     |
| `y(q)`        | `y q[0];`     |
| `z(q)`        | `z q[0];`     |
| `cnot(q1,q2)` | `cx q[0],q[1];`|
| `rx(q,θ)`     | `rx(θ) q[0];` |

### H-hat → NetQASM

| H-hat         | NetQASM       |
|---------------|---------------|
| `h(q)`        | `H Q0`        |
| `x(q)`        | `X Q0`        |
| `cnot(q1,q2)` | `CNOT Q0 Q1`  |
| `measure(q)`  | `MEAS Q0 M0`  |

## Example Translation

### H-hat Code
```heather
main {
    let q:@qubit = |0>
    let q2:@qubit = h(q)
    let q3:@qubit = x(q2)
    let result:bool = q3 * bool
}
```

### OpenQASM Output
```qasm
OPENQASM 2.0;
include "qelib1.inc";

qreg q[1];
creg c[1];

h q[0];
x q[0];
measure q[0] -> c[0];
```

### NetQASM Output
```netqasm
QALLOC Q0
H Q0
X Q0
MEAS Q0 M0
```

## Backend Selection

Automatic backend selection based on:
1. Target hardware availability
2. Required features (networking, gates)
3. User configuration
4. Circuit complexity

```python
from hhat_lang.low_level.quantum_lang import select_backend

backend = select_backend(
    features=["entanglement"],
    target="simulator"
)
# Returns: NetQASM backend
```

## Integration

- **core.cast**: Triggers quantum execution
- **dialects.heather.execution**: Quantum operation handling
- **low_level.target_backend**: Hardware interfaces
- **core.execution**: Execution orchestration

## Optimization

### Circuit Optimization
- Gate cancellation
- Circuit depth reduction
- Parallelization opportunities
- Resource minimization

### Backend-Specific
- OpenQASM: IBM hardware constraints
- NetQASM: Network topology optimization

## Related Documentation
- [Low-level README](../README.md)
- [Target Backends](../target_backend/README.md)
- [Core Execution](../../core/execution/README.md)
- [Quantum Computing Concepts](../../../../docs/core/quantum_concepts.md)
