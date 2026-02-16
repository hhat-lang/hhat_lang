# Type System

The `types/` module implements H-hat's comprehensive type system, including built-in types, type checking, type inference, and custom type definitions.

## Overview

Provides:
- Built-in classical types (int, float, bool, str)
- Built-in quantum types (@qubit, @qint, @qfloat)
- Custom type definitions (structs, enums)
- Type checking and validation
- Type inference
- Type conversion rules

## Structure

```
types/
├── __init__.py              # Module exports
├── abstract_base.py         # Abstract type interfaces
├── core.py                  # Core type system
├── builtin_base.py          # Built-in type base classes
├── builtin_types.py         # Built-in type implementations
├── builtin_conversion.py    # Type conversion rules
├── new_base_type.py         # Custom type base
├── new_builtin_core.py      # New built-in core types
├── new_builtin_std.py       # New built-in std types
├── new_core.py              # New type system
├── resolvers.py             # Type resolution
└── utils.py                 # Type utilities
```

## Built-in Classical Types

### Integer Types
- **Signed**: `i8`, `i16`, `i32`, `i64`, `i128`
- **Unsigned**: `u8`, `u16`, `u32`, `u64`, `u128`

### Floating Point
- `f32` - 32-bit float
- `f64` - 64-bit float (default)

### Other Primitives
- `bool` - Boolean (true/false)
- `str` - String
- `char` - Single character

## Built-in Quantum Types

### Core Quantum Types
- `@qubit` - Single quantum bit
- `@qint` - Quantum integer
- `@qfloat` - Quantum float
- `@bool` - Quantum boolean

### Quantum Integer Sizes
- `@u2`, `@u4`, `@u8`, `@u16`, `@u32` - Quantum unsigned integers

### Special Quantum Types
- `@bell_t` - Bell state (entangled pair)
- Custom quantum types

## Custom Types

### Structs
```heather
type Point {
    x:f64
    y:f64
}
```

### Enums
```heather
type Status {
    ON
    OFF
    ERROR
}
```

### Generic Types
```heather
type Option<T> {
    Some { value:T }
    None
}
```

## Type Hierarchy

```
Type (abstract)
│
├── PrimitiveType
│   ├── IntType
│   ├── FloatType
│   ├── BoolType
│   └── StringType
│
├── QuantumType
│   ├── QubitType
│   ├── QIntType
│   └── QFloatType
│
├── CompositeType
│   ├── StructType
│   ├── EnumType
│   └── TupleType
│
├── CollectionType
│   ├── ArrayType
│   ├── MapType
│   └── SetType
│
└── FunctionType
    └── ClosureType
```

## Type Checking

### Static Type Checking
All types checked at compile time:
```heather
let x:i32 = 42      // OK
let y:i32 = 3.14    // Error: type mismatch
let z:i32 = cast(3.14, i32)  // OK with explicit cast
```

### Type Inference
Types can be inferred:
```heather
let x = 42          // Inferred as i32
let y = 3.14        // Inferred as f64
let q = |0>         // Inferred as @qubit
```

## Type Conversion

### Implicit Conversions
H-hat has NO implicit conversions - all casts must be explicit.

### Explicit Casting
```heather
let x:i32 = 42
let y:f64 = cast(x, f64)  // OK
let z:i32 = cast(3.14, i32)  // OK, truncates to 3
```

## Quantum Type Rules

### Quantum Isolation
Quantum types cannot be nested in classical types without casting:
```heather
// Invalid
let x:i32 = @q  // Error!

// Valid
let x:i32 = cast(@q, i32)  // OK, triggers measurement
```

### Quantum Operations
Only quantum operations allowed on quantum types:
```heather
let q:@qubit = |0>
let q2:@qubit = h(q)      // OK, quantum gate
let result = q + q2       // Error! No arithmetic on qubits
```

## Type Metadata

Each type carries metadata:
```python
class TypeDef:
    name: str
    size: int                    # Size in bits
    alignment: int               # Memory alignment
    is_quantum: bool             # Classical or quantum
    is_copyable: bool            # Can be copied
    is_mutable: bool             # Can be mutated
    traits: list[Trait]          # Implemented traits
```

## Traits

Types can implement traits:
```heather
type MyType #[Printable Debug Clone] {
    value:i32
}
```

Common traits:
- `Printable` - Can be printed
- `Debug` - Debug representation
- `Clone` - Can be cloned
- `Comparable` - Can be compared
- `Hashable` - Can be hashed

## Integration Points

### Dependencies
- **core.data**: Type annotations on data
- **core.memory**: Memory layout calculations

### Used By
- **core.compiler**: Type checking
- **core.cast**: Cast definitions
- **core.execution**: Runtime type checks
- **dialects.heather**: Dialect-specific types

## Type Resolution

Resolution order:
1. Built-in types
2. Imported types
3. User-defined types in current module
4. User-defined types in parent scopes

## Usage Examples

### Define Custom Type
```python
from hhat_lang.core.types import StructType, IntType

point_type = StructType(
    name="Point",
    fields={
        "x": IntType(32),
        "y": IntType(32)
    }
)
```

### Type Checking
```python
from hhat_lang.core.types import type_check

if not type_check(value, expected_type):
    raise TypeMismatchError(...)
```

## Related Documentation
- [Core README](../README.md)
- [Data](../data/README.md)
- [Cast System](../cast/README.md)
- [Compiler](../compiler/README.md)
