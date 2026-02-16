# Compiler

The `compiler/` module implements H-hat's compilation infrastructure, transforming source code through various stages into executable intermediate representation (IR).

## Overview

This module provides the core compilation pipeline that:
- Manages built-in module compilation
- Coordinates compilation phases
- Integrates with dialect-specific compilers
- Handles module dependencies

## Structure

```
compiler/
├── __init__.py            # Module exports
├── core.py                # Core compiler logic
└── builtin_modules.py     # Built-in module compilation
```

## Key Components

### core.py - Core Compiler

The main compilation engine:

**Classes:**
- `Compiler` - Main compiler orchestrator
- `CompilationContext` - Tracks compilation state
- `CompilationPhase` - Individual compilation stages

**Compilation Pipeline:**
```
Source Files
    ↓
Lexing & Parsing (Dialect-specific)
    ↓
AST Construction
    ↓
Semantic Analysis
    ↓
Type Checking
    ↓
IR Generation
    ↓
Optimization
    ↓
Executable IR
```

### builtin_modules.py - Built-in Modules

Manages compilation of standard library modules:

**Responsibilities:**
- Compile built-in types (int, float, bool, etc.)
- Compile built-in functions (print, cast, etc.)
- Load standard library modules
- Provide module caching

**Built-in Modules:**
- `std.math` - Mathematical functions
- `std.io` - Input/output operations
- `std.quantum` - Quantum operations
- `std.types` - Type utilities

## Compilation Phases

### Phase 1: Lexical Analysis
- Tokenize source code
- Handle comments and whitespace
- Identify keywords and symbols

### Phase 2: Parsing
- Build Abstract Syntax Tree (AST)
- Validate syntax
- Error recovery

### Phase 3: Semantic Analysis
- Symbol resolution
- Scope checking
- Declaration validation

### Phase 4: Type Checking
- Infer types
- Validate type constraints
- Check cast requirements

### Phase 5: IR Generation
- Transform AST to IR
- Generate symbol tables
- Create code blocks

### Phase 6: Optimization
- Apply optimization passes
- Dead code elimination
- Constant folding

## Integration Points

### Dependencies
- **core.code**: IR representation
- **core.types**: Type system
- **core.data**: Data definitions
- **dialects.heather.compiler**: Heather-specific compilation

### Used By
- **toolchain.cli**: Command-line compiler
- **dialects.heather**: Dialect compilation
- **core.execution**: Execute compiled code

## Usage Example

```python
from hhat_lang.core.compiler import Compiler

compiler = Compiler()

# Compile source file
compiled = compiler.compile_file("main.hat")

# Access compiled IR
ir_graph = compiled.ir_graph
symbol_table = compiled.symbols
```

## Related Documentation
- [Core README](../README.md)
- [Code IR](../code/README.md)
- [Types](../types/README.md)
