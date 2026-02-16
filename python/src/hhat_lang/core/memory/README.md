# Memory Management

The `memory/` module implements H-hat's memory management system for variable storage, allocation, and lifetime management.

## Overview

Provides:
- Variable storage and retrieval
- Memory allocation strategies
- Scope-based lifetime management
- Classical and quantum memory separation

## Structure

```
memory/
├── __init__.py    # Module exports
├── core.py        # Core memory manager
└── utils.py       # Memory utilities
```

## Key Components

### MemoryManager

Central memory management:
```python
class MemoryManager:
    classical_memory: dict[Symbol, Any]
    quantum_memory: dict[Symbol, QuantumState]
    stack: list[StackFrame]
    heap: Heap
```

## Memory Layout

```
┌─────────────────────────────────┐
│         Stack Memory            │
│  ┌──────────────────────┐      │
│  │  Global Scope        │      │
│  ├──────────────────────┤      │
│  │  Function Frame      │      │
│  │  - Local vars        │      │
│  │  - Parameters        │      │
│  ├──────────────────────┤      │
│  │  Block Scope         │      │
│  └──────────────────────┘      │
├─────────────────────────────────┤
│         Heap Memory             │
│  - Dynamic allocations          │
│  - Large objects                │
│  - Quantum state storage        │
└─────────────────────────────────┘
```

## Scope Management

Variables are scoped by blocks:
```heather
let x:i32 = 42      // Global scope
{
    let y:i32 = 10  // Block scope
    // x and y visible
}
// Only x visible
```

## Quantum Memory

Quantum variables stored separately:
- Classical memory: standard data structures
- Quantum memory: quantum state vectors
- Separation prevents accidental measurement

## Integration Points

- **core.data**: Variable definitions
- **core.execution**: Runtime memory access
- **core.types**: Memory layout calculations

## Related Documentation
- [Core README](../README.md)
- [Data](../data/README.md)
- [Execution](../execution/README.md)
