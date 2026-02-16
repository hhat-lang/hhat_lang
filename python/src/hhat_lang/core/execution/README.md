# Execution System

The `execution/` module implements H-hat's runtime execution engine, responsible for executing compiled IR code and managing both classical and quantum program execution.

## Overview

This module provides the execution infrastructure that:
- Executes intermediate representation (IR) code
- Manages program state during execution
- Coordinates classical and quantum computations
- Handles quantum backend interfacing

## Structure

```
execution/
├── __init__.py           # Module exports
├── abstract_base.py      # Abstract execution interfaces
└── abstract_program.py   # Program execution abstractions
```

## Key Components

### abstract_program.py - Program Execution

**Classes:**
- `QuantumProgram` - Represents executable quantum program
- `Program` - Classical program representation
- `ProgramState` - Runtime state management
- `ExecutionContext` - Execution environment

**QuantumProgram Structure:**
```python
class QuantumProgram:
    ir_graph: IRGraph           # Compiled IR
    quantum_circuit: Circuit    # Quantum circuit representation
    backend_config: BackendConfig  # Quantum backend settings
    classical_code: IRGraph     # Classical computation parts
```

### abstract_base.py - Execution Interfaces

Abstract base classes for execution:
- `Executor` - Base executor interface
- `Evaluator` - Expression evaluation protocol
- `InterpreterBase` - Interpreter abstraction

## Execution Model

### Hybrid Execution

H-hat programs consist of both classical and quantum parts:

```
┌─────────────────────────────────────┐
│         H-hat Program               │
│  ┌──────────────┐  ┌──────────────┐│
│  │   Classical  │  │   Quantum    ││
│  │     Code     │◄─┤     Code     ││
│  │              │─►│              ││
│  └──────────────┘  └──────────────┘│
│         │                 │         │
└─────────┼─────────────────┼─────────┘
          │                 │
          ▼                 ▼
   ┌──────────┐      ┌──────────┐
   │ Classical│      │ Quantum  │
   │  Runtime │      │ Backend  │
   └──────────┘      └──────────┘
```

### Execution Flow

```
Start Program
    ↓
Initialize State
    ↓
Execute IR Node
    ├─ Classical Operation → Classical Runtime
    └─ Quantum Operation → Queue for Backend
         │
         ▼
    Quantum Cast Triggered
         │
         ▼
    Send to Quantum Backend
         │
         ▼
    Receive Samples
         │
         ▼
    Post-Process Results
         │
         ▼
    Continue Classical Execution
```

## Classical Execution

### Direct Evaluation
Classical operations execute immediately:

```python
# Classical code
let x:i32 = 42
let y:i32 = x + 10    # Executes immediately
print(y)               # Output: 52
```

### Stack-Based Execution
Uses call stack for function invocation:
```
Stack Frame
│
├── Local Variables
├── Parameters
├── Return Address
└── Saved Context
```

## Quantum Execution

### Lazy Evaluation
Quantum operations are deferred until measurement/cast:

```python
# Quantum code
let q:@qubit = |0>    # Prepare state
let q2:@qubit = h(q)  # Queue gate application
let q3:@qubit = x(q2) # Queue another gate

# No execution yet!

let result:bool = cast(q3, bool)  # Now execute!
```

### Circuit Construction
Quantum operations build a circuit:

```
|0> ─┤ H ├─┤ X ├─┤ M ├ → classical bit
```

### Backend Execution
When cast is triggered:
1. Translate circuit to backend format
2. Submit to quantum backend
3. Collect measurement samples
4. Post-process results
5. Return to classical execution

## Program State Management

### ExecutionContext

Tracks execution state:
```python
class ExecutionContext:
    variables: dict[Symbol, DataDef]     # Variable values
    functions: dict[Symbol, FnDef]       # Function definitions
    call_stack: list[StackFrame]         # Call stack
    quantum_state: QuantumState          # Quantum program state
    memory: MemoryManager                # Memory management
```

### State Transitions

```
Initial State
    ↓
Variable Declaration
    ↓
Function Call (push frame)
    ↓
Expression Evaluation
    ↓
Function Return (pop frame)
    ↓
Quantum Cast (backend execution)
    ↓
Final State
```

## Integration Points

### Dependencies
- **core.code**: IR interpretation
- **core.data**: Variable and function definitions
- **core.memory**: Memory management
- **core.cast**: Type casting during execution
- **low_level.quantum_lang**: Quantum backend interface

### Used By
- **dialects.heather.execution**: Heather-specific execution
- **toolchain.cli**: Run compiled programs
- **core.compiler**: Execute at compile-time (const evaluation)

## Execution Modes

### Interpreted Mode
Execute IR directly without further compilation:
```python
interpreter = Interpreter(ir_graph)
result = interpreter.execute()
```

### JIT Compilation
Compile hot paths to native code for performance:
```python
jit_executor = JITExecutor(ir_graph)
result = jit_executor.execute()  # Compiles on first run
```

### Hybrid Mode
Mix interpretation and compilation:
```python
hybrid_executor = HybridExecutor(ir_graph)
result = hybrid_executor.execute()
```

## Performance Considerations

### Classical Optimization
- **Instruction caching**: Reuse decoded instructions
- **Branch prediction**: Predict likely paths
- **Register allocation**: Minimize memory access

### Quantum Optimization
- **Circuit optimization**: Reduce gates before submission
- **Batching**: Combine multiple quantum operations
- **Caching**: Cache backend results when deterministic

## Error Handling During Execution

### Runtime Errors
```python
try:
    execute_program(ir_graph)
except DivisionByZeroError:
    handle_division_error()
except QuantumEvaluationError:
    handle_quantum_error()
except StackOverflowError:
    handle_stack_error()
```

### Quantum Backend Errors
- Backend timeout
- Insufficient qubits
- Gate not supported
- Measurement failure

## Debugging Support

The execution system supports:
- **Breakpoints**: Pause execution at specific points
- **Step execution**: Execute one instruction at a time
- **State inspection**: View variables and quantum state
- **Call stack traces**: Debug function calls
- **Quantum circuit visualization**: See circuit before execution

## Usage Examples

### Execute Program

```python
from hhat_lang.core.execution import ProgramExecutor

executor = ProgramExecutor(
    ir_graph=compiled.ir_graph,
    backend_config=quantum_config
)

result = executor.execute()
print(f"Program result: {result}")
```

### Custom Executor

```python
from hhat_lang.core.execution.abstract_base import Executor

class MyExecutor(Executor):
    def execute_instruction(self, instruction):
        # Custom execution logic
        pass
```

## Quantum Backend Interface

### Backend Configuration

```python
backend_config = {
    "provider": "qiskit",
    "backend": "aer_simulator",
    "shots": 1024,
    "optimization_level": 2
}
```

### Backend Execution

```python
# Translate to backend format
circuit = translate_to_backend(quantum_ir)

# Execute
job = backend.run(circuit, shots=1024)
result = job.result()

# Process samples
samples = result.get_counts()
```

## Related Documentation
- [Core README](../README.md)
- [Code IR](../code/README.md)
- [Cast System](../cast/README.md)
- [Quantum Backend](../lowlevel/README.md)
