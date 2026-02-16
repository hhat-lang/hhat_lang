# Error Handlers

The `error_handlers/` module defines H-hat's comprehensive error system, providing structured error types for all possible error conditions in the language implementation.

## Overview

This module implements a hierarchical error system that:
- Provides specific error classes for each error category
- Includes detailed error messages and context
- Supports error recovery and reporting
- Integrates with debugging and IDE tooling

## Structure

```
error_handlers/
├── __init__.py    # Module exports
└── errors.py      # All error class definitions
```

## Error Hierarchy

```
HhatError (Base)
│
├── SyntaxError
│   ├── UnexpectedTokenError
│   ├── InvalidSyntaxError
│   └── ParsingError
│
├── SemanticError
│   ├── UndefinedSymbolError
│   ├── DuplicateDefinitionError
│   ├── ScopeError
│   └── ImportError
│
├── TypeError
│   ├── TypeMismatchError
│   ├── InvalidCastError
│   ├── UnknownTypeError
│   └── TypeInferenceError
│
├── RuntimeError
│   ├── DivisionByZeroError
│   ├── NullReferenceError
│   ├── IndexOutOfBoundsError
│   └── StackOverflowError
│
├── QuantumError
│   ├── QuantumEvaluationError
│   ├── InvalidQuantumOperationError
│   ├── MeasurementError
│   └── EntanglementError
│
├── CompilationError
│   ├── IRConstructionError
│   ├── OptimizationError
│   └── CodeGenerationError
│
├── MemoryError
│   ├── AllocationError
│   ├── AccessViolationError
│   └── MemoryLeakWarning
│
└── ConfigError
    ├── InvalidConfigError
    ├── MissingConfigError
    └── BackendConfigError
```

## Key Error Classes

### Base Error

```python
class HhatError(Exception):
    """Base class for all H-hat errors"""
    
    def __init__(
        self,
        message: str,
        line: int | None = None,
        column: int | None = None,
        file: str | None = None,
        context: str | None = None
    ):
        self.message = message
        self.location = (line, column, file)
        self.context = context
```

### Syntax Errors

Errors during lexing and parsing:
```python
SyntaxError("Expected '}' after function body", line=42, column=10)
UnexpectedTokenError("Found 'else' without matching 'if'")
```

### Semantic Errors

Errors in program meaning:
```python
UndefinedSymbolError("Variable 'x' not defined")
DuplicateDefinitionError("Function 'sum' already defined")
ScopeError("Cannot access private member from outside class")
```

### Type Errors

Type system violations:
```python
TypeMismatchError("Expected i32, found f64")
InvalidCastError("Cannot cast @qubit to i32 without measurement")
TypeInferenceError("Cannot infer type of variable 'x'")
```

### Runtime Errors

Errors during execution:
```python
DivisionByZeroError("Division by zero in expression")
IndexOutOfBoundsError("Array index 5 out of bounds [0..3]")
NullReferenceError("Attempted to access null reference")
```

### Quantum Errors

Quantum-specific errors:
```python
QuantumEvaluationError("Quantum backend execution failed")
InvalidQuantumOperationError("Cannot apply gate 'H' to classical data")
MeasurementError("Measurement produced invalid result")
EntanglementError("Invalid entanglement operation")
```

### Compilation Errors

Errors during compilation:
```python
IRConstructionError("Failed to construct IR for expression")
OptimizationError("Invalid optimization transformation")
CodeGenerationError("Cannot generate code for unsupported operation")
```

### Memory Errors

Memory management issues:
```python
AllocationError("Failed to allocate memory for array")
AccessViolationError("Attempted to access freed memory")
MemoryLeakWarning("Potential memory leak detected")
```

### Configuration Errors

Configuration and setup issues:
```python
InvalidConfigError("Invalid quantum backend configuration")
MissingConfigError("Required configuration 'qubits' not found")
BackendConfigError("Quantum backend failed to initialize")
```

## Error Properties

Each error includes:
- **Message**: Human-readable error description
- **Location**: File, line, and column where error occurred
- **Context**: Surrounding code snippet
- **Stack Trace**: Call stack at error point
- **Suggestions**: Possible fixes (when available)

## Error Reporting

### Console Output
```
Error: Type mismatch
  ┌─ main.hat:15:10
  │
15│     let x:i32 = 3.14
  │                 ^^^^ expected i32, found f64
  │
  = help: use explicit cast: cast(3.14, i32)
```

### Structured Format
```json
{
  "error": "TypeMismatchError",
  "message": "Expected i32, found f64",
  "location": {
    "file": "main.hat",
    "line": 15,
    "column": 10
  },
  "context": "    let x:i32 = 3.14",
  "suggestion": "use explicit cast: cast(3.14, i32)"
}
```

## Error Recovery

H-hat implements error recovery strategies:

### Panic Mode
Skip tokens until synchronization point (`;`, `}`, etc.)

### Phrase Level
Insert/delete tokens to recover

### Error Productions
Special grammar rules for common errors

### Global Correction
Minimal token changes to fix error

## Usage Examples

### Raising Errors

```python
from hhat_lang.core.error_handlers.errors import TypeMismatchError

if actual_type != expected_type:
    raise TypeMismatchError(
        f"Expected {expected_type}, found {actual_type}",
        line=node.line,
        column=node.column,
        file=current_file
    )
```

### Error Handling

```python
from hhat_lang.core.error_handlers.errors import HhatError

try:
    compile(source_code)
except HhatError as e:
    print(f"Error at {e.location}: {e.message}")
    if e.context:
        print(f"Context: {e.context}")
```

## Error Guidelines

### For Error Messages
1. **Be specific**: "Variable 'x' not defined" not "Undefined variable"
2. **Include location**: Always provide line/column if available
3. **Suggest fixes**: Help users resolve the error
4. **Use context**: Show relevant code snippet

### For New Errors
1. **Inherit correctly**: Choose appropriate parent class
2. **Document well**: Explain when error occurs
3. **Test thoroughly**: Include error case tests
4. **Localize**: Support internationalization

## Integration Points

### Dependencies
- Standard library `Exception`
- No internal dependencies (avoid circular imports)

### Used By
- **All modules**: Every module raises specific errors
- **core.compiler**: Compilation errors
- **core.execution**: Runtime errors
- **dialects.heather**: Dialect-specific errors
- **toolchain.cli**: Error reporting to user

## IDE Integration

Error information supports:
- **Syntax highlighting**: Mark error locations
- **Quick fixes**: Suggest automatic corrections
- **Hover information**: Show error details on hover
- **Problem panel**: List all errors in workspace

## Testing Errors

```python
import pytest
from hhat_lang.core.error_handlers.errors import TypeMismatchError

def test_type_mismatch():
    with pytest.raises(TypeMismatchError) as exc_info:
        # Code that should raise error
        check_type(i32_type, f64_value)
    
    assert "Expected i32" in str(exc_info.value)
```

## Future Enhancements

- **Error codes**: Unique codes for each error type (E001, E002, etc.)
- **Multi-language**: Localized error messages
- **Error links**: Link to documentation for each error
- **AI suggestions**: Use ML for better error fix suggestions

## Related Documentation
- [Core README](../README.md)
- [Compiler](../compiler/README.md)
- [Types](../types/README.md)
- [Execution](../execution/README.md)
