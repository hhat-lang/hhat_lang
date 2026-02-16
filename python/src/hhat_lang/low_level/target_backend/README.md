# Target Backend

The `target_backend/` module provides interfaces to quantum hardware and simulator backends, executing quantum circuits on real and simulated quantum computers.

## Overview

Provides quantum execution backends:
- Qiskit (IBM Quantum)
- SquidASM (NetSquid Quantum Networking)
- Unified backend interface
- Hardware abstraction

## Structure

```
target_backend/
├── __init__.py     # Module exports and backend registry
├── qiskit/         # IBM Qiskit backend
└── squidasm/       # SquidASM backend
```

## Key Components

### qiskit/ - IBM Qiskit Backend

**IBM Qiskit:**
- Industry-leading quantum computing platform
- Access to IBM Quantum systems
- Advanced simulators
- Rich tooling ecosystem

**Features:**
- Real IBM quantum hardware access
- High-fidelity simulators (Aer)
- Noise modeling
- Transpilation and optimization
- Job management

**Supported Devices:**
- IBM Quantum systems (cloud)
- Local simulators (qasm_simulator, statevector_simulator)
- GPU-accelerated simulators

### squidasm/ - SquidASM Backend

**SquidASM:**
- Quantum network simulator
- Built on NetSquid
- Distributed quantum computing
- Quantum internet research

**Features:**
- Multi-node quantum networks
- Entanglement distribution
- Quantum teleportation
- Network protocols

**Use Cases:**
- Quantum networking research
- Distributed quantum algorithms
- Quantum communication protocols

## Backend Interface

Unified interface for all backends:

```python
class QuantumBackend:
    def compile(self, circuit) -> CompiledCircuit:
        """Compile circuit for backend"""
        pass
    
    def execute(self, circuit, shots=1024) -> Result:
        """Execute circuit on backend"""
        pass
    
    def get_capabilities(self) -> dict:
        """Get backend capabilities"""
        pass
```

## Execution Flow

```
H-hat Quantum Circuit
        ↓
Backend Selection
        ↓
Circuit Translation (to QASM)
        ↓
Backend Compilation
        ↓
Optimization/Transpilation
        ↓
Job Submission
        ↓
Quantum Execution
        ↓
Result Retrieval
        ↓
H-hat Result Processing
```

## Backend Selection

### Automatic Selection
```python
from hhat_lang.low_level.target_backend import get_backend

backend = get_backend(
    prefer="simulator",
    features=["statevector"]
)
```

### Manual Selection
```python
from hhat_lang.low_level.target_backend.qiskit import QiskitBackend

backend = QiskitBackend(
    device="ibmq_qasm_simulator",
    shots=1024
)
```

## Qiskit Integration

### Example Usage
```python
from hhat_lang.low_level.target_backend.qiskit import QiskitBackend

# Initialize backend
backend = QiskitBackend("ibmq_qasm_simulator")

# Execute circuit
compiled = backend.compile(quantum_circuit)
result = backend.execute(compiled, shots=1024)

# Get results
counts = result.get_counts()
print(counts)  # {'00': 512, '11': 512}
```

### Real Hardware Access
```python
from qiskit import IBMQ

# Load IBM Quantum account
IBMQ.load_account()

# Select real device
backend = QiskitBackend("ibmq_manila")
result = backend.execute(circuit, shots=100)
```

## SquidASM Integration

### Network Simulation
```python
from hhat_lang.low_level.target_backend.squidasm import SquidASMBackend

# Initialize network backend
backend = SquidASMBackend(
    nodes=["Alice", "Bob"],
    topology="star"
)

# Execute distributed quantum protocol
result = backend.execute_protocol(protocol)
```

## Backend Capabilities

### Query Capabilities
```python
capabilities = backend.get_capabilities()

print(capabilities)
# {
#     'max_qubits': 5,
#     'gates': ['h', 'x', 'y', 'z', 'cx', 'rx', 'ry', 'rz'],
#     'measurements': True,
#     'conditional': True,
#     'noise_model': True,
#     'multi_node': False
# }
```

## Performance Optimization

### Circuit Optimization
- Gate synthesis
- Circuit depth reduction
- Qubit mapping
- Error mitigation

### Batch Execution
```python
# Execute multiple circuits efficiently
results = backend.execute_batch(circuits, shots=1024)
```

### Caching
- Result caching for identical circuits
- Compilation caching
- Credential caching

## Error Handling

### Hardware Errors
- Connection timeout
- Job failure
- Device unavailable

### Software Errors
- Invalid circuit
- Unsupported gates
- Resource limits exceeded

## Integration

- **low_level.quantum_lang**: Receives QASM circuits
- **core.execution**: Provides results to execution engine
- **core.cast**: Cast operations trigger backend execution
- **toolchain.config**: Backend configuration

## Configuration

### Backend Configuration
```json
{
    "backend": {
        "default": "qiskit",
        "qiskit": {
            "device": "ibmq_qasm_simulator",
            "shots": 1024,
            "optimization_level": 2
        },
        "squidasm": {
            "nodes": 2,
            "topology": "line"
        }
    }
}
```

## Related Documentation
- [Low-level README](../README.md)
- [Quantum Language](../quantum_lang/README.md)
- [Core Execution](../../core/execution/README.md)
- [Configuration](../../toolchain/config/README.md)
