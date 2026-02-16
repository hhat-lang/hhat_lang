# Code Representation

The `code/` module implements H-hat's Intermediate Representation (IR) system, providing the internal data structures and abstractions for representing program code throughout the compilation and execution pipeline.

## Overview

This module defines how H-hat represents code internally, from high-level constructs down to executable instructions. It provides:
- **IR Graph**: Directed acyclic graph representation of code
- **Instructions**: Low-level executable operations
- **Symbol Tables**: Scope management and symbol resolution
- **Function Definitions**: Function signatures and bodies
- **Code Blocks**: Structured code organization

## Structure

```
code/
├── __init__.py         # Module exports
├── abstract.py         # Abstract base classes for code structures
├── base.py             # Core code representation classes
├── instructions.py     # Instruction definitions
├── ir_block.py         # Code block structures
├── ir_custom.py        # Custom IR node types
├── ir_graph.py         # IR graph data structure
├── symbol_table.py     # Symbol table management
├── tools.py            # Code manipulation utilities
└── utils.py            # Helper functions
```

## Key Components

### ir_graph.py - IR Graph System

The IR Graph is the central representation of code in H-hat:

```
┌─────────────────────────────────────────┐
│           IR Graph                      │
│  ┌─────────┐      ┌─────────┐         │
│  │  Entry  │─────▶│  Node1  │         │
│  │  Point  │      │ (const) │         │
│  └─────────┘      └────┬────┘         │
│                         │               │
│                         ▼               │
│                    ┌─────────┐         │
│                    │  Node2  │         │
│                    │  (add)  │         │
│                    └────┬────┘         │
│                         │               │
│                         ▼               │
│                    ┌─────────┐         │
│                    │  Exit   │         │
│                    │  Node   │         │
│                    └─────────┘         │
└─────────────────────────────────────────┘
```

**Classes:**
- `IRGraph` - Directed acyclic graph of IR nodes
- `IRNode` - Individual instruction or operation
- `IREdge` - Connection between nodes with data flow

**Key Methods:**
- `add_node()` - Insert operation into graph
- `add_edge()` - Connect nodes with data dependency
- `optimize()` - Apply optimization passes
- `to_executable()` - Convert to executable form

### base.py - Function and Code Definitions

Defines the structure of functions and code elements:

**Classes:**
- `FnHeaderDef` - Function signature definition
  ```python
  # fn sum (a:u64 b:u64) u64 { ::add(a b) }
  FnHeaderDef(
      name=Symbol("sum"),
      type=Symbol("u64"),
      args_names=(Symbol("a"), Symbol("b")),
      args_types=(Symbol("u64"), Symbol("u64"))
  )
  ```
- `FnBodyDef` - Function body implementation
- `CodeSection` - Organized code segment
- `CodeBlock` - Executable block with scope

### instructions.py - Instruction Set

Defines low-level executable instructions:

**Instruction Types:**
- **Arithmetic**: `ADD`, `SUB`, `MUL`, `DIV`, `MOD`
- **Logical**: `AND`, `OR`, `NOT`, `XOR`
- **Comparison**: `EQ`, `NE`, `LT`, `GT`, `LE`, `GE`
- **Memory**: `LOAD`, `STORE`, `ALLOC`, `FREE`
- **Control Flow**: `JUMP`, `BRANCH`, `CALL`, `RETURN`
- **Quantum**: `APPLY_GATE`, `MEASURE`, `PREPARE_STATE`
- **Cast**: `CAST`, `CHECK_TYPE`

**Instruction Format:**
```python
@dataclass
class Instruction:
    opcode: OpCode
    operands: list[Symbol | Literal]
    result: Symbol | None
    metadata: dict[str, Any]
```

### symbol_table.py - Symbol Management

Manages scopes and symbol resolution:

**Classes:**
- `SymbolTable` - Hierarchical symbol lookup
- `Scope` - Individual lexical scope
- `SymbolEntry` - Symbol with type and metadata

**Symbol Resolution:**
```
Global Scope
    ├── main: fn_t
    ├── Point: type_t
    └── Function Scope (sum)
            ├── a: u64
            ├── b: u64
            └── Block Scope
                    └── temp: u64
```

### ir_block.py - Code Blocks

Structured code organization:

**Classes:**
- `IRBlock` - Sequential code block
- `ConditionalBlock` - If/else structures
- `LoopBlock` - While/for loops
- `FunctionBlock` - Function bodies

### abstract.py - Base Abstractions

Abstract base classes for extensibility:
- `CodeElement` - Base for all code structures
- `Transformable` - Code transformation protocol
- `Analyzable` - Code analysis interface

## Data Flow Through IR

### 1. Parsing → IR Construction

```
Source Code (Heather)
        ↓
    Parser
        ↓
    AST Nodes
        ↓
    IR Builder
        ↓
    IR Graph
```

### 2. IR Optimization

```
Initial IR
    ↓
Dead Code Elimination
    ↓
Constant Folding
    ↓
Common Subexpression Elimination
    ↓
Optimized IR
```

### 3. IR → Execution

```
IR Graph
    ↓
Instruction Selection
    ↓
Register Allocation
    ↓
Executable Instructions
    ↓
Execution Engine
```

## Usage Examples

### Building IR Graph

```python
from hhat_lang.core.code.ir_graph import IRGraph, IRNode
from hhat_lang.core.code.instructions import OpCode

# Create graph
graph = IRGraph()

# Add nodes
const_node = IRNode(OpCode.CONST, value=42)
add_node = IRNode(OpCode.ADD, operands=[const_node, const_node])

graph.add_node(const_node)
graph.add_node(add_node)
graph.add_edge(const_node, add_node)

# Optimize
graph.optimize()
```

### Function Definition

```python
from hhat_lang.core.code.base import FnHeaderDef
from hhat_lang.core.data.core import Symbol

# Define function header
header = FnHeaderDef(
    name=Symbol("factorial"),
    type=Symbol("u64"),
    args_names=(Symbol("n"),),
    args_types=(Symbol("u64"),)
)
```

### Symbol Table

```python
from hhat_lang.core.code.symbol_table import SymbolTable, Scope

# Create symbol table
symbols = SymbolTable()

# Add global scope
global_scope = Scope("global")
global_scope.add_symbol("PI", FloatType(), is_const=True)

symbols.push_scope(global_scope)
```

## Integration Points

### Dependencies

- **core.data.core**: Symbol and literal definitions
- **core.types**: Type system for code validation
- **core.memory**: Memory layout for code execution

### Used By

- **core.compiler**: Compiles source to IR
- **core.execution**: Executes IR instructions
- **dialects.heather.compiler**: Dialect-specific IR generation
- **core.fns**: Function IR representation

## Code Representation Principles

### 1. Immutability
IR nodes and graphs are immutable once constructed. Transformations create new structures.

### 2. Type-Aware
Every IR node carries type information for validation and optimization.

### 3. Backend-Agnostic
IR abstracts away target-specific details, supporting multiple backends.

### 4. Optimization-Friendly
IR designed for easy analysis and transformation.

### 5. Debuggable
Rich metadata enables source mapping and debugging.

## Optimization Passes

Implemented optimizations:

1. **Dead Code Elimination**: Remove unreachable code
2. **Constant Folding**: Evaluate constants at compile-time
3. **Common Subexpression Elimination**: Reuse computed values
4. **Inline Expansion**: Inline small functions
5. **Loop Unrolling**: Optimize small loops
6. **Strength Reduction**: Replace expensive ops with cheaper ones

## Quantum-Specific IR

Special handling for quantum operations:

```python
# Quantum gate application
gate_node = IRNode(
    OpCode.APPLY_GATE,
    gate="h",  # Hadamard
    qubits=[qubit_var],
    is_quantum=True
)

# Measurement
measure_node = IRNode(
    OpCode.MEASURE,
    qubits=[qubit_var],
    output=classical_var,
    is_quantum=True
)
```

## Performance Considerations

- **Graph Traversal**: Optimized BFS/DFS for analysis
- **Node Pooling**: Reuse node objects for memory efficiency
- **Lazy Evaluation**: Defer expensive operations
- **Caching**: Memoize analysis results

## Error Handling

Common errors:
- `IRConstructionError` - Invalid graph construction
- `SymbolNotFoundError` - Undefined symbol reference
- `TypeMismatchError` - Type inconsistency in IR
- `InvalidInstructionError` - Malformed instruction

## Related Documentation

- [Core README](../README.md) - Core architecture overview
- [Compiler](../compiler/README.md) - IR compilation
- [Execution](../execution/README.md) - IR execution
- [Types System](../types/README.md) - Type integration
