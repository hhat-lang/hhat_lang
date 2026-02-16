# Functions System

The `fns/` module implements H-hat's function definition, resolution, and execution infrastructure.

## Overview

This module handles:
- Function definitions and signatures
- Function lookup and resolution
- Meta-function implementations
- Built-in function registry

## Structure

```
fns/
├── __init__.py        # Module exports
├── abstract_base.py   # Abstract function interfaces
└── core.py            # Function implementations
```

## Key Components

### Function Types

**Regular Functions:**
```heather
fn sum(a:i32 b:i32) i32 {
    ::add(a b)
}
```

**Meta-Functions:**
```heather
meta-fn if(options:[opt-body_t]) ir_t { ... }
```

**Built-in Functions:**
- `print()` - Output to console
- `cast()` - Type casting
- `add()`, `sub()`, `mul()`, `div()` - Arithmetic

### Function Resolution

Functions resolved by:
1. Name matching
2. Argument type matching
3. Return type compatibility
4. Scope visibility

## Integration Points

- **core.code**: Function IR representation
- **core.data**: Function definitions
- **core.types**: Function type signatures
- **core.execution**: Function invocation

## Related Documentation
- [Core README](../README.md)
- [Code](../code/README.md)
- [Types](../types/README.md)
