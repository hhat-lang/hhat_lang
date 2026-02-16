
# H-hat quantum language

[![Unitary Foundation](https://img.shields.io/badge/Supported%20By-Unitary%20Foundation-FFFF00.svg)](https://unitary.foundation)
[![Discord Chat](https://img.shields.io/badge/dynamic/json?color=blue&label=Discord&query=approximate_presence_count&suffix=%20online.&url=https%3A%2F%2Fdiscord.com%2Fapi%2Finvites%2FJqVGmpkP96%3Fwith_counts%3Dtrue)](http://discord.unitary.foundation)

!!! warning

    This is a work in progress and may be seeing as such. Errors, inconsistencies,
    tons of experimentation are modifications are happening. Until the version 0.3 is released, it is prone to breaking changes.


*H-hat is a rule system, compiler framework, and a statically typed, functional and distributed system inspired, quantum programming language.*

It aims to support explicit function overloading, algebraic data types, ownership and RAII-like features, strict and lazy evaluation, reflective cast, metaprogramming, structured typing-like approach, concurrency, backend kind-based types (CPU and QPU), and multi-architecture targeting computation (e.g. CPU: x86_64, aarch64; gate- and analog-based QPU: superconducting, trapped ion, neutral atoms, photonics, etc.)

The language is intended to be used on single computers, HPCs and embedded systems, for local and distributed computation. Inspired by Fortran, Erlang, Rust, C and Lean, it focuses on good performance, integration, distributed computing resilience, and algorithmic verifiability.

  
## Language features

- Code reasoning closer to classical programming languages
- Quantum data types, variables, functions just as its classical counterpart
- Additionally, there are quantum primitives to define some general platform-independent instruction
  sets
- Classical and quantum parts have similar syntaxes and components
- Quantum variables:
    - hold quantum and classical instructions
    - execute its content and perform measurement once a `cast` function is called upon it
    - re-execute the same data content every time it is cast
- Platform- and quantum logic language- independent
- Can hold many syntaxes/dialects implementations to work in harmony with each other

## Code Organization

!!! note

    The development is still in alpha phase.


The code has been developed in two different development programming languages (DPL) so far: Python (`python/`) and Rust (`rust/`). *Rust is being carried out for further development*.

Inside each DPL folder there are `README.md` files with information regarding implementation, folder purpose and code organization.


### H-hat Heather

H-hat defines some rules and concepts to its paradigm so programmers can understand how to use it.
However, it does not explicitly implement a particular syntax or interpreter/JIT/AOT compiler. The main
idea is to give programmers freedom to develop their own syntax and/or interpreter/compiler versions
that are compatible with those rules.

To showcase some features and present programmers with its paradigm, a *dialect* is developed,
called **Heather**. It is a simple dialect with simple syntax that can make concrete what
programming a H-hat code should/does look like. You may find its implementation in both DPLs.

New reference dialects may emerge in the future.


## Getting Started

You can get started by checking out the [Getting Started page](getting_started.md).


## License

MIT

## How to Contribute

Check the [How to Contribute](how_contribute.md) page.


## Code of Conduct

We coexist in the same world. So be nice to others as you expect others to be nice to you :)
