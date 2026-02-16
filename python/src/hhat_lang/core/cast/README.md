# Cast System

The `cast/` module implements H-hat's type casting and transformation system, which is fundamental to bridging classical and quantum computations. This module defines how data is converted between types, particularly in the critical quantum-to-classical casting protocol.

## Overview

Casting in H-hat is more than simple type conversion—it's a complete transformation pipeline that handles:
- Classical-to-classical type conversions
- Quantum-to-classical evaluation (with lazy evaluation)
- Data sampling and post-processing
- Result interpretation and validation

## Structure

```
cast/
├── __init__.py         # Module exports
├── base.py             # Base cast definitions and protocols
└── transform_fns.py    # Transform function implementations
```

## Key Components

### base.py

Defines the core casting infrastructure:

**Classes:**
- `CastDefinition` - Abstract base class for all cast operations
- `CastGraph` - Manages the graph of available cast transformations
- `CastProtocol` - Protocol defining cast function signatures

**Key Functions:**
- `is_iterable()` - Check if data supports iteration
- `is_dict_like()` - Check if data supports dictionary-like access
- `is_result_obj()` - Validate quantum result objects

**Type Annotations:**
```python
CastFnType = Callable[[DataDef | Literal | Any], Literal]
```

### transform_fns.py

Implements specific type transformation functions:
- Classical primitive conversions (int → float, bool → int, etc.)
- String conversions and formatting
- Collection transformations
- Quantum sampling interpretation

## The Quantum Cast Protocol

The quantum-to-classical cast is a multi-stage process:

```
┌─────────────────────┐
│ Quantum Data (@q)   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 1. Lazy Evaluation  │  Translate to Low-Level Quantum (LLQ)
│    & Translation    │  Fallback to dialect if needed
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 2. Backend          │  Execute on quantum backend
│    Execution        │  Sample results
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 3. Post-Processing  │  Interpret sampling according to criteria
│    & Interpretation │  Statistical analysis
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 4. Classical Cast   │  Convert to target classical type
│                     │  Return result
└─────────────────────┘
```

### Workflow Details

**Stage 1: Lazy Evaluation & Translation**
- Quantum data content is not evaluated until cast
- Translated to Low-Level Quantum language (LLQ)
- If LLQ or backend lacks an instruction, fallback to dialect implementation

**Stage 2: Backend Execution**
- Translated code executed by quantum backend
- Produces data sampling from quantum computation
- Classical computations use regular dialect workflow

**Stage 3: Post-Processing**
- Sample results interpreted according to criteria
- Statistical analysis and normalization
- Error mitigation if applicable

**Stage 4: Classical Casting**
- Processed result cast to target classical type
- Type validation and conversion
- Result returned to code evaluation

## Usage Examples

### Classical Cast

```python
# Define cast from int to float
cast_fn = CastDefinition(
    from_type=IntType(),
    to_type=FloatType(),
    transform=lambda x: float(x.value)
)

# Apply cast
result = cast_fn.apply(IntLiteral(42))  # FloatLiteral(42.0)
```

### Quantum Cast

```python
# Cast quantum qubit to boolean (measurement)
@qubit_var = QuantumVariable(state=|0>)

# When cast is requested
result = cast(@qubit_var, BoolType)
# 1. Lazy eval → measure instruction in LLQ
# 2. Backend executes → samples measurements
# 3. Post-process → majority vote or single shot
# 4. Cast → BoolLiteral(False)  # measured |0> → False
```

## Integration Points

### Dependencies

- **core.code.ir_graph**: IR representation for cast operations
- **core.data.core**: Literal and data definitions
- **core.types.abstract_base**: Type system integration
- **core.execution.abstract_program**: Quantum program execution
- **core.memory.core**: Memory management during casts

### Used By

- **core.compiler**: Compile-time type checking and cast insertion
- **core.execution**: Runtime cast execution
- **dialects.heather.execution**: Heather-specific cast implementations
- **core.fns**: Function return type casting

## Rules and Constraints

1. **Type Safety**: All casts must be explicitly defined or derivable
2. **Quantum Isolation**: Quantum data cannot contain classical data that might collapse it
3. **Lazy Evaluation**: Quantum casts only evaluate when necessary
4. **Fallback Chain**: LLQ → Backend → Dialect implementation
5. **Immutability**: Casts produce new values, don't mutate originals

## Design Principles

### Explicit Over Implicit
All casts must be explicit in the code. H-hat does not perform automatic type coercion.

### Composability
Casts can be chained: `A → B → C` is automatically available if `A → B` and `B → C` exist.

### Backend Agnostic
Cast definitions work with any quantum backend by using LLQ as an abstraction layer.

## Performance Considerations

- **Cast Graph Caching**: Available casts cached for fast lookup
- **Lazy Evaluation**: Quantum casts defer expensive operations
- **Sampling Optimization**: Smart sampling strategies reduce backend calls
- **Transform Inlining**: Simple casts may be inlined by compiler

## Error Handling

Common cast errors:
- `InvalidCastError` - No cast path exists between types
- `QuantumEvaluationError` - Backend execution failed
- `SamplingError` - Insufficient or invalid samples
- `TypeMismatchError` - Cast result doesn't match target type

## Future Extensions

- **Probabilistic Casts**: Handle uncertainty in quantum results
- **Approximate Casts**: Allow lossy conversions with guarantees
- **Vectorized Casts**: Batch operations for efficiency
- **Custom Cast Protocols**: User-defined casting strategies

## Related Documentation

- [Core README](../README.md) - Overall core architecture
- [Types System](../types/README.md) - Type definitions
- [Execution System](../execution/README.md) - Runtime execution
- [Quantum Protocol](../lowlevel/README.md) - Low-level quantum interface
