# Heather Compiler

The `compiler/` module implements the Heather dialect-specific compiler, transforming Heather source code into executable IR.

## Overview

Provides Heather-specific compilation:
- Heather syntax parsing
- Semantic analysis
- Type checking
- IR generation

## Structure

```
compiler/
├── __init__.py    # Module exports
└── core.py        # Heather compiler implementation
```

## Key Components

### core.py - Heather Compiler

**HeatherCompiler Class:**
- Coordinates compilation pipeline
- Integrates grammar and parser
- Generates Heather-specific IR
- Handles Heather language features

## Compilation Pipeline

```
Heather Source (.hat)
        ↓
Lexing (Generic + Heather tokens)
        ↓
Parsing (Heather grammar)
        ↓
AST Construction
        ↓
Semantic Analysis
        ↓
Type Checking (Heather types)
        ↓
IR Generation (Heather IR)
        ↓
Optimization
        ↓
Executable IR
```

## Heather-Specific Features

### Syntax Features
- `::` return operator
- `*` cast operator
- `@` quantum prefix
- `|state>` quantum literals
- `#[Trait]` trait annotations
- `<modifier>` modifiers

### Semantic Features
- Quantum isolation validation
- Lazy quantum evaluation
- Meta-function expansion
- Modifier application

## Integration

- **dialects.heather.grammar**: Heather grammar rules
- **dialects.heather.parsing**: AST construction
- **dialects.heather.code**: IR generation
- **core.compiler**: Base compilation infrastructure

## Usage

```python
from hhat_lang.dialects.heather.compiler import HeatherCompiler

compiler = HeatherCompiler()
compiled = compiler.compile_file("main.hat")
```

## Related Documentation
- [Heather README](../README.md)
- [Grammar](../grammar/README.md)
- [Parsing](../parsing/README.md)
- [Core Compiler](../../../core/compiler/README.md)
