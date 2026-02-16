# Language Concepts

Deep dive into H-hat's core concepts, type system, and advanced features.

## Overview

H-hat is designed with several key principles that set it apart:

- **Unified quantum-classical programming**
- **Strong static type system**
- **Ownership and memory safety**
- **Reflective cast system**
- **Platform independence**

## Quick Navigation

<div class="grid cards" markdown>

-   :material-book-alphabet:{ .lg .middle } __Core Concepts__

    ---

    Understand fundamental H-hat ideas

    * [Rule System](../rule_system.md)
    * [Language Design](language_design.md)
    * [Compiler Framework](compiler_framework.md)
    * [Nomenclature](naming.md)

-   :material-code-braces-box:{ .lg .middle } __Type System__

    ---

    Learn about H-hat's type system

    * [Types Overview](../concepts/types.md)
    * [Quantum Types](../concepts/quantum_types.md)
    * [Cast System](../concepts/casting.md)

-   :material-memory:{ .lg .middle } __Memory & Ownership__

    ---

    Understand memory management

    * [Ownership Model](../concepts/ownership.md)
    * [Memory Management](../concepts/memory.md)

-   :material-rocket-launch:{ .lg .middle } __Advanced Topics__

    ---

    Explore advanced features

    * [Concurrency](../concepts/concurrency.md)
    * [Meta-programming](../concepts/metaprogramming.md)

</div>

## Core Concepts

### The Rule System

H-hat defines a set of rules and concepts that form the paradigm. These rules provide the foundation for all dialect implementations.

[Learn about the rule system →](../rule_system.md)

### Language Design

Understand the design decisions behind H-hat:

- HIR-based compilation
- Module system
- Cast mechanism
- Type inference
- And more

[Read the language design →](language_design.md)

### Compiler Framework

H-hat is a compiler framework, not just a language:

- Support for multiple dialects
- Pluggable backends
- Multi-stage compilation
- JIT and AOT compilation

[Explore the compiler framework →](compiler_framework.md)

## Type System

### Static Typing

H-hat uses strong static typing to catch errors at compile time:

```heather
let x:i32 = 42              // Explicit type
let y:qubit = |0>           // Quantum type
let z = true                // Type inference
```

### Backend-Specific Types

Types are associated with backend kinds:

- **CPU types**: `i32`, `f64`, `bool`, `str`
- **QPU types**: `qubit`, `qint`, `qfloat`
- Cross-backend operations require explicit casts

### Algebraic Data Types

Define complex types with structs and enums:

```heather
// Struct
type Point { x:f64 y:f64 }

// Enum
type Option<T> {
    Some(T)
    None
}
```

## Memory Management

### Ownership

Each value has a single owner:

```heather
let x = create_data()   // x owns the data
let y = x               // ownership moves to y
// x is now invalid
```

### Borrowing

Reference data without taking ownership:

```heather
fn process(data:&Data) -> i32 {
    // Borrow data, don't own it
    data.value
}

let x = create_data()
let result = process(&x)  // x still valid after call
```

### RAII

Resources are automatically freed when they go out of scope:

```heather
{
    let data = allocate()
    // use data
}  // data is automatically freed here
```

## The Cast System

### Lazy Evaluation

Quantum operations are accumulated, not immediately executed:

```heather
let q:qubit = |0>
let q2:qubit = h(q)      // Operation recorded, not executed
let q3:qubit = x(q2)     // Another operation recorded
```

### Cast Triggers Execution

The `cast` operation executes accumulated quantum operations:

```heather
let result:bool = cast(q3, bool)  // Now everything executes
```

### Cross-Backend Casting

Cast between classical and quantum types:

```heather
// Quantum to classical
let q:qubit = |0>
let b:bool = cast(q, bool)

// Classical to quantum (if cast function exists)
let x:i32 = 42
let qx:qint = cast(x, qint)
```

## Function Overloading

Define multiple functions with the same name:

```heather
fn process(x:i32) -> i32 { ... }
fn process(x:f64) -> f64 { ... }
fn process(x:qubit) -> qubit { ... }

let a = process(42)      // Calls i32 version
let b = process(3.14)    // Calls f64 version
let c = process(|0>)     // Calls qubit version
```

Resolution happens at compile time based on argument types.

## Generics

Write code that works with multiple types:

```heather
fn identity<T>(x:T) -> T {
    x
}

let a:i32 = identity(42)
let b:f64 = identity(3.14)
let c:qubit = identity(|0>)
```

## Modules and Imports

### File-Based Modules

Each `.hat` file is a module:

```
my_project/
├── main.hat
├── math/
│   ├── basics.hat
│   └── advanced.hat
└── quantum/
    └── gates.hat
```

### Importing

Import functions, types, and constants:

```heather
// Single import
use(fn:math.basics.add)

// Multiple imports
use(
    fn:math.basics.add
    fn:math.basics.multiply
    type:quantum.gates.Gate
)
```

## Platform Independence

### Backend Abstraction

Write once, target multiple platforms:

```heather
fn quantum_algorithm(q:qubit) -> bool {
    let q2 = h(q)
    let q3 = rz(q2, pi/4)
    cast(q3, bool)
}
// Works on any quantum backend
```

### Configuration-Driven

Backend capabilities are defined in configuration:

- Available operations
- Hardware constraints
- Optimization passes
- Default settings

## Concurrency (Planned)

### Actor Model

Process-based concurrency inspired by Erlang:

```heather
// Future syntax (not yet implemented)
spawn(fn:worker, args)
send(pid, message)
receive()
```

### Message Passing

Safe communication between processes:

- No shared memory
- Explicit message passing
- Fault tolerance
- Supervision trees

## Metaprogramming (Planned)

### Meta-Functions

Functions that operate on code:

```heather
// Future syntax
@meta
fn generate_gates(n:i32) -> Code {
    // Generate code at compile time
}
```

### Modifiers

Decorators for functions and types:

```heather
// Future syntax
@memoize
fn expensive_computation(x:i32) -> i32 {
    // Automatically cached
}
```

## Learning Path

### For Beginners

1. Start with [Getting Started](../getting_started.md)
2. Read [Your First Program](../getting_started/first_program.md)
3. Explore [Basic Examples](../examples/basic/first_code.md)
4. Learn [Heather Syntax](../dialects/heather/syntax.md)

### For Intermediate Users

1. Understand [Type System](../concepts/types.md)
2. Learn [Ownership Model](../concepts/ownership.md)
3. Master [Cast System](../concepts/casting.md)
4. Study [Compiler Framework](compiler_framework.md)

### For Advanced Users

1. Deep dive into [Language Design](language_design.md)
2. Explore [Concurrency](../concepts/concurrency.md)
3. Study [Meta-programming](../concepts/metaprogramming.md)
4. Contribute to [Implementation](../rust/rust_guide.md)

## Reference Materials

### Core Documentation

- [Rule System](../rule_system.md) - Fundamental rules
- [Language Design](language_design.md) - Design decisions
- [Compiler Framework](compiler_framework.md) - Implementation
- [Nomenclature](naming.md) - Terminology

### Syntax & Grammar

- [Heather Syntax](../dialects/heather/syntax.md) - Concrete syntax
- [Heather Grammar](../dialects/heather/grammar.md) - Formal grammar

### Examples

- [Basic Examples](../examples/basic/first_code.md)
- [Quantum Examples](../examples/quantum/quantum_types.md)
- [Advanced Examples](../examples/advanced/custom_types.md)

## Next Steps

<div class="grid cards" markdown>

-   __Read Language Design__

    Understand design principles

    [:octicons-arrow-right-24: Language Design](language_design.md)

-   __Learn Type System__

    Master H-hat's types

    [:octicons-arrow-right-24: Types Overview](../concepts/types.md)

-   __Explore Examples__

    See concepts in action

    [:octicons-arrow-right-24: Examples](../examples/index.md)

-   __Study Syntax__

    Learn Heather dialect

    [:octicons-arrow-right-24: Heather Syntax](../dialects/heather/syntax.md)

</div>

---

Questions about language concepts? Ask on [Discord](http://discord.unitary.foundation) or check the [community page](../community/index.md)!
