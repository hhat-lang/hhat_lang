# Welcome to H-hat

<div class="grid cards" markdown>

-   :material-lightning-bolt:{ .lg .middle } __Quick Start__

    ---

    Get up and running with H-hat in minutes

    [:octicons-arrow-right-24: Getting Started](getting_started.md)

-   :material-book-open-variant:{ .lg .middle } __Learn the Language__

    ---

    Understand H-hat's concepts and features

    [:octicons-arrow-right-24: Language Concepts](core/index.md)

-   :material-code-braces:{ .lg .middle } __See Examples__

    ---

    Explore code samples and use cases

    [:octicons-arrow-right-24: Examples](examples/index.md)

-   :material-account-group:{ .lg .middle } __Join the Community__

    ---

    Get help and connect with other developers

    [:octicons-arrow-right-24: Community](community/index.md)

</div>

## What is H-hat?

[![Unitary Foundation](https://img.shields.io/badge/Supported%20By-Unitary%20Foundation-FFFF00.svg)](https://unitary.foundation)
[![Discord Chat](https://img.shields.io/badge/dynamic/json?color=blue&label=Discord&query=approximate_presence_count&suffix=%20online.&url=https%3A%2F%2Fdiscord.com%2Fapi%2Finvites%2FJqVGmpkP96%3Fwith_counts%3Dtrue)](http://discord.unitary.foundation)

!!! warning "Alpha Software"
    H-hat is currently in **alpha stage**. Expect frequent changes, incomplete features, and breaking changes until version 0.3.0 is released.

**H-hat** is a rule system, compiler framework, and a statically typed, functional quantum programming language designed to make quantum computing more accessible and practical.

### Key Characteristics

- **🎯 Unified Paradigm**: Write quantum and classical code with similar syntax
- **🔒 Type Safe**: Catch errors at compile time with strong static typing
- **⚡ High Performance**: Native compilation with zero-cost abstractions
- **🌐 Platform Independent**: Target multiple quantum hardware platforms
- **🔧 Flexible**: Support for multiple dialects and custom backends
- **🚀 Modern**: Ownership, RAII, functional programming, and concurrency

## Language Features

### Quantum as a Natural Extension

H-hat treats quantum computation as a natural extension of classical programming:

```heather
// Define a quantum function
fn quantum_example(q:qubit) -> bool {
    let q2:qubit = h(q)         // Apply Hadamard gate
    let q3:qubit = rx(q2, pi/4) // Rotation
    cast(q3, bool)              // Measure and return
}

// Call it like any function
main {
    let result:bool = quantum_example(|0>)
    print(result)
}
```

### Core Features

**Type System**
:   Strong static typing with type inference, algebraic data types, and backend-specific types for CPU and QPU

**Cast System**
:   Unique reflective cast mechanism for executing quantum operations lazily and converting between types

**Memory Safety**
:   Ownership model inspired by Rust with move semantics, borrowing, and RAII for automatic resource management

**Function Overloading**
:   Write natural APIs with explicit function overloading based on types and arity

**Concurrency**
:   Actor-model inspired by Erlang for fault-tolerant distributed quantum-classical computation

**Metaprogramming**
:   Compile-time code generation and manipulation for maximum flexibility

[Learn more about features →](introduction/features.md){ .md-button }

## Multi-Architecture Support

H-hat is designed to target diverse quantum hardware:

- **Gate-based systems**: Superconducting, trapped ion
- **Analog quantum processors**: Continuous control systems
- **Neutral atoms**: QuEra, Pasqal platforms
- **Photonic systems**: Xanadu, PsiQuantum platforms
- **Classical**: x86_64, ARM64, and other CPU architectures

## Compiler Framework

H-hat is not just a language—it's a complete compiler framework:

- **Multiple dialects**: Heather is the reference syntax; create your own
- **Pluggable backends**: Support for CLIF, MLIR, and custom IRs
- **HIR-based**: Clean intermediate representation for optimization
- **JIT & AOT**: Both just-in-time and ahead-of-time compilation

## Design Philosophy

Inspired by **Fortran**, **Erlang**, **Rust**, **C**, and **Lean**, H-hat focuses on:

1. **Good Performance**: Efficient native code generation
2. **Integration**: Work with existing quantum and classical toolchains
3. **Distributed Computing**: Resilient multi-node computation
4. **Algorithmic Verifiability**: Formal reasoning about programs

## Getting Started

Ready to explore quantum programming with H-hat?

<div class="grid cards" markdown>

-   __Installation__

    Set up H-hat on your system with Python or Rust

    [:octicons-arrow-right-24: Install Now](getting_started.md)

-   __First Program__

    Write your first quantum program

    [:octicons-arrow-right-24: Quick Tutorial](getting_started/first_program.md)

-   __Language Guide__

    Deep dive into H-hat concepts

    [:octicons-arrow-right-24: Learn More](core/index.md)

-   __Examples__

    See H-hat in action

    [:octicons-arrow-right-24: View Examples](examples/index.md)

</div>

## Project Status

H-hat is currently in **alpha development**:

- ✅ Core syntax defined (Heather dialect)
- 🚧 Rust implementation in progress
- 🚧 Basic compilation pipeline working
- 📋 Quantum execution coming soon

[Check detailed status →](introduction/status.md){ .md-button .md-button--primary }

## Code Organization

The project is implemented in two languages:

**Rust** (Primary)
:   Active development in `rust/hhat_lang/` - The production implementation

**Python** (Reference)
:   Proof-of-concept in `python/` - Currently on hold but available for reference

### H-hat Heather

**Heather** is the reference dialect—a concrete syntax implementation of the H-hat paradigm. The framework supports multiple dialects, so you can create your own syntax while leveraging the same compiler infrastructure.

## Community & Support

Join our growing community:

- 💬 **Discord**: [Unitary Foundation Discord](http://discord.unitary.foundation) - `#h-hat` channel
- 🐙 **GitHub**: [hhat-lang/hhat_lang](https://github.com/hhat-lang/hhat_lang)
- 📝 **Blog**: Read our [latest updates](blog/index.md)
- 🤝 **Contributing**: See our [contribution guide](contributing/guide.md)

## License

H-hat is open source software licensed under the **MIT License**.

## Acknowledgments

H-hat is supported by the [Unitary Foundation](https://unitary.foundation), a nonprofit organization dedicated to supporting the quantum open-source ecosystem.

---

**Ready to start?** [Begin your quantum programming journey →](getting_started.md){ .md-button .md-button--primary }
