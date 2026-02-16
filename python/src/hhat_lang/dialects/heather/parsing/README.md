# Heather Parsing

The `parsing/` module implements Heather's parser infrastructure, transforming token streams into Abstract Syntax Trees (AST) and IR.

## Overview

Provides parsing infrastructure:
- AST construction from grammar
- Parse tree to AST transformation
- IR visitor pattern
- Parsing utilities

## Structure

```
parsing/
├── __init__.py      # Module exports
├── ir_visitor.py    # IR construction visitor
└── utils.py         # Parsing utilities
```

## Key Components

### ir_visitor.py - IR Visitor

Implements visitor pattern for IR construction:

**IRVisitor Class:**
- Traverses parse tree
- Constructs IR nodes
- Builds symbol tables
- Validates semantics

**Visitor Methods:**
```python
def visit_function_def(self, node):
    # Convert function definition to IR
    pass

def visit_variable_decl(self, node):
    # Convert variable declaration to IR
    pass

def visit_expression(self, node):
    # Convert expression to IR
    pass
```

### utils.py - Parsing Utilities

Helper functions for parsing:
- Token extraction
- Error recovery
- Source location tracking
- AST manipulation

## Parsing Pipeline

```
Source Code
    ↓
Lexer (Tokenization)
    ↓
Token Stream
    ↓
Parser (Grammar Application)
    ↓
Parse Tree
    ↓
IR Visitor (Transformation)
    ↓
Abstract Syntax Tree (AST)
    ↓
IR Generation
    ↓
Intermediate Representation
```

## Visitor Pattern

The visitor pattern allows clean separation:

```python
class IRVisitor:
    def visit(self, node):
        method_name = f"visit_{node.type}"
        method = getattr(self, method_name, self.generic_visit)
        return method(node)
    
    def visit_function(self, node):
        # Specific handling for function nodes
        pass
    
    def generic_visit(self, node):
        # Default handling
        pass
```

## AST Nodes

Common AST node types:
- `FunctionNode` - Function definitions
- `TypeNode` - Type definitions
- `VariableNode` - Variable declarations
- `ExpressionNode` - Expressions
- `StatementNode` - Statements
- `LiteralNode` - Literal values

## Error Handling

### Syntax Errors
Detected during parsing:
```
Error: Expected '}' after function body
  ┌─ main.hat:15:10
  │
15│ fn sum(a:i32 b:i32) i32 { ::add(a b)
  │                                     ^ expected '}'
```

### Semantic Errors
Detected during visitor traversal:
```
Error: Undefined variable 'x'
  ┌─ main.hat:20:15
  │
20│     let y = x + 10
  │             ^ 'x' not defined in this scope
```

## Integration

- **dialects.heather.grammar**: Grammar definitions
- **dialects.heather.compiler**: Uses parser
- **core.code**: Constructs core IR
- **core.error_handlers**: Error reporting

## Usage

```python
from hhat_lang.dialects.heather.parsing import parse_heather

ast = parse_heather(source_code)
ir = ast.to_ir()
```

## Related Documentation
- [Heather README](../README.md)
- [Grammar](../grammar/README.md)
- [Compiler](../compiler/README.md)
- [Core Code](../../../core/code/README.md)
