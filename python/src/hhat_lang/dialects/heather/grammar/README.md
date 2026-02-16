# Heather Grammar

The `grammar/` module defines the complete grammar specification for the Heather dialect using Arpeggio PEG parser.

## Overview

Defines Heather syntax grammar:
- Constants grammar
- Function grammar
- Type grammar
- Meta-function and modifier grammar
- Generic language constructs

## Structure

```
grammar/
├── __init__.py           # Module exports and constants
├── const_grammar.py      # Constant declarations
├── fn_grammar.py         # Function definitions
├── type_grammar.py       # Type definitions
├── metamod_grammar.py    # Meta-functions and modifiers
└── generic_grammar.py    # Generic constructs
```

## Key Components

### const_grammar.py - Constants

Grammar for constant declarations:
```heather
const PI:f64 = 3.14159265
const MAX_SIZE:u32 = 1024
```

**Tokens:**
- `const` keyword
- Identifier
- Type annotation
- Literal value

### fn_grammar.py - Functions

Grammar for function definitions:
```heather
fn sum(a:i32 b:i32) i32 {
    ::add(a b)
}
```

**Production Rules:**
- Function header: `fn name (params) return_type`
- Parameters: `name:type`
- Function body: `{ statements }`
- Return statement: `:: expression`

### type_grammar.py - Types

Grammar for type definitions:
```heather
// Struct
type Point {
    x:f64
    y:f64
}

// Enum
type Status {
    ON
    OFF
    ERROR
}
```

**Type Categories:**
- Classical types: `i32`, `f64`, `bool`, `str`
- Quantum types: `@qubit`, `@qint`, `@qfloat`
- Custom types: structs, enums
- Generic types: `Option<T>`, `Array<T>`

### metamod_grammar.py - Meta-programming

Grammar for meta-functions and modifiers:
```heather
meta-fn if(options:[opt-body_t]) ir_t { ... }
modifier &(self) T { ... }
```

### generic_grammar.py - Generic Constructs

Common grammar rules:
- Identifiers
- Operators
- Keywords
- Literals
- Comments

## Grammar Constants

Exported in `__init__.py`:

```python
# Keywords
KEYWORDS = [
    "fn", "type", "const", "let", "main",
    "if", "match", "while", "for", "return",
    "use", "meta-fn", "modifier", "cast"
]

# Classical Types
CLASSICAL_TYPES = [
    "i8", "i16", "i32", "i64", "i128",
    "u8", "u16", "u32", "u64", "u128",
    "f32", "f64", "bool", "str", "char"
]

# Quantum Types
QUANTUM_TYPES = [
    "@qubit", "@qint", "@qfloat", "@bool",
    "@u2", "@u4", "@u8", "@u16", "@u32",
    "@bell_t"
]

# Quantum Gates
QUANTUM_GATES = [
    "h", "x", "y", "z", "s", "t",
    "rx", "ry", "rz",
    "cnot", "cx", "swap", "toffoli"
]

# Quantum Literal Pattern
QUANTUM_LITERAL_PATTERN = r"\|[01+\-]+\>"
```

## PEG Grammar

Heather uses **PEG (Parsing Expression Grammar)**:
- Ordered choice (try first, then second)
- Greedy matching
- No ambiguity
- Composable rules

### Example Grammar Rule

```python
def function_def():
    return "fn", identifier, "(", optional(params), ")", \
           optional(return_type), "{", function_body, "}"

def params():
    return param, ZeroOrMore(",", param)

def param():
    return identifier, ":", type_spec
```

## Operator Precedence

```
1. :: (return)           - Highest
2. * (cast)
3. ^, &  (pointer, reference)
4. *, /, %  (multiplicative)
5. +, -  (additive)
6. ==, !=, <, >, <=, >=  (comparison)
7. &&  (logical and)
8. ||  (logical or)
9. =>  (match arm)       - Lowest
```

## Special Syntax

### Quantum Literals
```heather
|0>     // Zero state
|1>     // One state
|+>     // Plus state (superposition)
|->     // Minus state
|00>    // Two-qubit state
```

### Return Operator
```heather
::expression    // Explicit return
```

### Cast Operator
```heather
value * type    // Cast value to type
```

### Quantum Prefix
```heather
@variable       // Quantum variable
@qubit          // Quantum type
```

### Trait Annotations
```heather
#Printable              // Single trait
#[Printable Debug]      // Multiple traits
```

### Modifiers
```heather
<mut>       // Mutable modifier
<ref>       // Reference modifier
<&>         // Reference shorthand
```

## Integration

- **dialects.heather.parsing**: Uses grammar for parsing
- **dialects.heather.compiler**: Grammar-driven compilation
- **toolchain.pygments**: Syntax highlighting based on grammar

## Grammar Testing

```python
from arpeggio import ParserPython
from hhat_lang.dialects.heather.grammar import fn_grammar

parser = ParserPython(fn_grammar)
parse_tree = parser.parse(source_code)
```

## Related Documentation
- [Heather README](../README.md)
- [Parsing](../parsing/README.md)
- [Syntax Documentation](../../../../docs/dialects/heather/syntax.md)
- [Grammar Documentation](../../../../docs/dialects/heather/grammar.md)
