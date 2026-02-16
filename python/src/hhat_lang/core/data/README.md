# Data Structures

The `data/` module defines H-hat's core data structures for representing program data: variables, functions, literals, and symbols.

## Overview

This module provides the foundational data types used throughout the H-hat system:
- **Symbols**: Named identifiers for variables, types, functions
- **Literals**: Constant values (42, 3.14, "hello", true)
- **Variables**: Mutable data containers with types
- **Functions**: Callable code with parameters and return values

## Structure

```
data/
├── __init__.py          # Module exports
├── core.py              # Core data structures (Symbol, Literal)
├── var_def.py           # Variable definitions
├── var_assignment.py    # Variable assignment logic
├── var_utils.py         # Variable utilities
├── fn_def.py            # Function definitions
└── utils.py             # Helper functions
```

## Key Components

### core.py - Core Data Types

**Symbol Types:**
```python
Symbol           # Simple identifier: x, sum, Point
CompositeSymbol  # Qualified name: std.math.pi
Tmp              # Temporary variable: $t1, $t2
SimpleObj        # Object reference
ObjArray         # Array/collection
```

**Literal Types:**
```python
IntLiteral       # 42, -10, 0xFF
FloatLiteral     # 3.14, -0.5, 1e-10
BoolLiteral      # true, false
StringLiteral    # "hello world"
QuantumLiteral   # |0>, |1>, |+>, |->
```

### var_def.py - Variable Definitions

**Classes:**
- `DataDef` - Base variable definition
- `ClassicalVar` - Classical variable
- `QuantumVar` - Quantum variable (@q)
- `VarMetadata` - Variable metadata

**Variable Properties:**
```python
var = DataDef(
    name=Symbol("x"),
    type=IntType(),
    is_mut=False,      # Mutability
    is_quantum=False,  # Classical/quantum
    scope="local"      # Scope level
)
```

### var_assignment.py - Assignment Logic

Handles variable assignment operations:
- Declaration vs assignment
- Type checking on assignment
- Mutability validation
- Quantum variable constraints

### fn_def.py - Function Definitions

**Classes:**
- `FnDef` - Complete function definition
- `FnSignature` - Function type signature
- `Parameter` - Function parameter

**Function Structure:**
```python
fn_def = FnDef(
    name="sum",
    params=[
        Parameter("a", IntType()),
        Parameter("b", IntType())
    ],
    return_type=IntType(),
    body=IRGraph(...)
)
```

## Data Classification

### Classical Data
Standard computational data:
- Integers: `i8`, `i16`, `i32`, `i64`, `i128`
- Unsigned: `u8`, `u16`, `u32`, `u64`, `u128`
- Floats: `f32`, `f64`
- Booleans: `bool`
- Strings: `str`

### Quantum Data
Quantum computational data (prefixed with `@`):
- `@qubit` - Single qubit
- `@qint` - Quantum integer
- `@qfloat` - Quantum float
- `@bool` - Quantum boolean
- Custom quantum types

## Variable Lifecycle

```
Declaration
    ↓
[Optional] Initialization
    ↓
Usage (read/write)
    ↓
Scope Exit → Cleanup
```

### Classical Variables
```python
let x:i32 = 42      # Immutable, initialized
let mut y:f64       # Mutable, uninitialized
y = 3.14            # Assignment
```

### Quantum Variables
```python
let q:@qubit = |0>  # Quantum state
let q2:@qubit = h(q) # Gate application
```

## Integration Points

### Dependencies
- **core.types**: Type definitions
- **core.memory**: Memory management

### Used By
- **core.code**: IR variable references
- **core.execution**: Variable evaluation
- **core.compiler**: Symbol tables
- **dialects.heather**: Dialect-specific variables

## Data Constraints

### Quantum Isolation Rule
Quantum data may contain classical instructions and data internally, but classical data **cannot** contain quantum data that might cause premature collapse.

```python
# Valid
let @q:@qubit = classical_fn(|0>)  # Classical inside quantum OK

# Invalid
let x:i32 = @q  # Must use explicit cast!
let x:i32 = cast(@q, i32)  # Cast required
```

### Mutability Rules
- Immutable by default (`let x`)
- Explicit mutability (`let mut x` or `<mut>` modifier)
- Quantum variables are inherently mutable due to superposition

## Usage Examples

### Variable Definition
```python
from hhat_lang.core.data import DataDef, Symbol

var = DataDef(
    name=Symbol("counter"),
    type=IntType(),
    is_mut=True
)
```

### Literal Creation
```python
from hhat_lang.core.data import IntLiteral, FloatLiteral

answer = IntLiteral(42)
pi = FloatLiteral(3.14159)
```

## Related Documentation
- [Core README](../README.md)
- [Types](../types/README.md)
- [Memory](../memory/README.md)
- [Execution](../execution/README.md)
