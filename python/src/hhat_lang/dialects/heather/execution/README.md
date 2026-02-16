# Heather Execution

The `execution/` module implements the Heather dialect-specific execution engine for running compiled Heather programs.

## Overview

Provides Heather-specific execution:
- Heather IR interpretation
- Classical and quantum execution
- Heather built-in function execution
- Dialect-specific optimizations

## Structure

```
execution/
├── __init__.py      # Module exports
├── executor.py      # Heather executor
├── new_ir.py        # New IR execution
├── classical/       # Classical execution
└── quantum/         # Quantum execution
```

## Key Components

### executor.py - Heather Executor

Main execution engine for Heather:
- Interprets Heather IR
- Manages execution state
- Coordinates classical/quantum execution

### classical/
Classical computation execution:
- Standard operations
- Control flow
- Function calls
- Memory management

### quantum/
Quantum computation execution:
- Quantum gate application
- State preparation
- Measurement handling
- Circuit construction

### new_ir.py
Enhanced IR execution with:
- Improved performance
- Better quantum handling
- Optimized execution paths

## Execution Flow

```
Heather IR
    ↓
Executor Initialization
    ↓
Instruction Dispatch
    ├─ Classical Instruction
    │  └─ Execute Directly
    └─ Quantum Instruction
       └─ Queue for Backend
            ↓
       Cast Triggered
            ↓
       Backend Execution
            ↓
       Result Processing
            ↓
       Continue Execution
```

## Heather-Specific Features

### Return Operator (`::`)
```heather
fn sum(a:i32 b:i32) i32 {
    ::add(a b)  // Explicit return
}
```

### Cast Operator (`*`)
```heather
let q:@qubit = |0>
let result:bool = q * bool  // Sugar for cast(q, bool)
```

### Pipe Operator
```heather
let result = value
    |> double
    |> increment
    |> print
```

### Quantum Gates
```heather
let q:@qubit = |0>
let q2:@qubit = h(q)      // Hadamard
let q3:@qubit = x(q2)     // Pauli-X
let bell:@bell_t = cnot(q, q2)  // CNOT gate
```

## Integration

- **dialects.heather.code**: Heather IR definitions
- **core.execution**: Base execution system
- **core.cast**: Heather cast implementations
- **low_level.quantum_lang**: Quantum backend interface

## Performance

### Optimizations
- Quantum circuit optimization before submission
- Classical operation inlining
- Loop unrolling for small iterations
- Constant folding

### Quantum Efficiency
- Gate merging
- Circuit simplification
- Minimal measurements
- Result caching when possible

## Usage

```python
from hhat_lang.dialects.heather.execution import HeatherExecutor

executor = HeatherExecutor(compiled_ir)
result = executor.execute()
```

## Related Documentation
- [Heather README](../README.md)
- [Heather Compiler](../compiler/README.md)
- [Core Execution](../../../core/execution/README.md)
- [Quantum Backend](../../../low_level/README.md)
