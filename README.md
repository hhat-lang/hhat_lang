# H-hat quantum language

[![Unitary Fund](https://img.shields.io/badge/Supported%20By-UNITARY%20FUND-brightgreen.svg?style=for-the-badge)](http://unitary.fund)

H-hat is a high-level abstraction quantum programming language.


> [!WARNING]
> 
>   This is a work in progress and may be seeing as such. Errors, inconsistencies, tons of experimentation, modifications and trials are happening. Until there is a stable version, it is prone to breaking changes.

As of now, the language is being developed as an *interpreted language* mostly to experiment some ideas and mechanisms on the quantum side. Once it is mature enough, the compiled version will take place.


## What `H-hat` is

- A quantum programming language family and the ecosystem to build it
- An abstraction layer _above_ QASM-like languages
- A language to
  - Use higher-level abstraction to harness quantum resources, such as superposition, entanglement, etc.
  - Need _no_ specialized knowledge on quantum mechanics or quantum information theory
  - Close the gap between developers/programmers/computer scientists and quantum physicists
  - Use quantum data and quantum data structures to reason about quantum information processing
  - Solve problems using quantum logic, but not raw quantum mechanics approach


## What `H-hat` *is not*

- A replacement for quantum logic-level quantum computation (circuit-like quantum computing, for instance), such as QASM-like languages
- A full stack programming language with direct access to the hardware
- A simulator


## Language features

- Code reasoning closer to classical programming languages
- Quantum data types, variables, functions just as its classical counterpart
- Additionally, there is quantum primitives to define some general platform-dependent instruction set
- Classical and quantum parts have similar syntaxes and components
- Quantum variables:
    - hold quantum and classical instructions
    - execute its content and perform measurement once a `cast` function is called upon it
    - re-execute the same data content every time it is cast
- Platform- and quantum logic language- independent
- Can hold many syntaxes/dialects implementations to work in harmony with each other


## Code Organization

The code is organized by the languages that are implementing `H-hat`. So far, `Python` and `Rust` are being used. They are to be taken as benchmarks of one another at this development stage. Each folder should contain all the elements to make the code runnable by itself. The main structure is:

- _implementation_language_folder_/
  - _core_/
  - _dialect_builder_/
  - _interpreter_/


### Core

This folder is where the core and basic internals of the language should be located. It is included the  managers for memory, namespaces, types, functions, variables, etc. for both classical and quantum, managers for quantum resources, backends and platforms.

### Dialect builder

The place to find the tools for developing the language dialects.

### Interpreter

A vanilla version of the language for reference and concrete demonstration purposes.


## Documentation

> [!NOTE]
> 
> Although there is a documentation, it is outdated and should be replaced soon.
 

A documentation can be found [here](https://docs.hhat-lang.org).


## License

MIT
