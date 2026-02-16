# Heather Code Module

The `code/` module implements Heather-specific code representation and IR building for the Heather dialect.

## Overview

Extends core code representation with Heather-specific:
- IR node types
- Built-in functions and operations
- Code generation utilities

## Structure

```
code/
├── __init__.py                # Module exports
├── builtins/                  # Heather built-in implementations
└── simple_ir_builder/         # Simplified IR construction
```

## Components

### builtins/
Heather-specific built-in implementations:
- Heather standard functions
- Dialect-specific operations
- Sugar syntax implementations

### simple_ir_builder/
Simplified API for constructing IR:
- High-level IR building
- Heather syntax mapping
- AST to IR translation helpers

## Integration

- **dialects.heather.compiler**: Uses IR builders
- **dialects.heather.execution**: Executes generated IR
- **core.code**: Extends core IR system

## Related Documentation
- [Heather README](../README.md)
- [Core Code](../../../core/code/README.md)
- [Heather Compiler](../compiler/README.md)
