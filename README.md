# H-hat quantum language

[![Unitary Foundation](https://img.shields.io/badge/Supported%20By-Unitary%20Foundation-FFFF00.svg)](https://unitary.foundation)
[![Discord Chat](https://img.shields.io/badge/dynamic/json?color=blue&label=Discord&query=approximate_presence_count&suffix=%20online.&url=https%3A%2F%2Fdiscord.com%2Fapi%2Finvites%2FJqVGmpkP96%3Fwith_counts%3Dtrue)](http://discord.unitary.foundation)

H-hat is a high-level abstraction quantum programming language.


> [!WARNING]
>
>   This is a work in progress and may be seeing as such. Errors, inconsistencies, tons of
> experimentation, modifications and trials are happening. Until there is a stable version, it is
> prone to breaking changes.

## What `H-hat` is

- A quantum programming language family and the ecosystem to build it
- An abstraction layer _above_ QASM-like languages
- A language to
    - Use higher-level abstraction to harness quantum resources, such as superposition,
      entanglement, etc.
    - Need _no_ specialized knowledge on quantum mechanics or quantum information theory
    - Close the gap between developers/programmers/computer scientists and quantum physicists
    - Use quantum data and quantum data structures to reason about quantum information processing
    - Solve problems using quantum logic, but not raw quantum mechanics approach

## What `H-hat` *is not*

- A replacement for quantum logic-level quantum computation (circuit-like quantum computing, for
  instance), such as QASM-like languages
- A full stack programming language with direct access to the hardware
- A simulator

## Language features

- Code reasoning closer to classical programming languages
- Quantum data types, variables, functions just as its classical counterpart
- Additionally, there is quantum primitives to define some general platform-dependent instruction
  set
- Classical and quantum parts have similar syntaxes and components
- Quantum variables:
    - hold quantum and classical instructions
    - execute its content and perform measurement once a `cast` function is called upon it
    - re-execute the same data content every time it is cast
- Platform- and quantum logic language- independent
- Can hold many syntaxes/dialects implementations to work in harmony with each other

## Code Organization

The code is organized by the development language chosen to develop H-hat, also known as main
development language (**MDL**). For instance, a `python/`
folder will contain `Python` code to make a workable version of H-hat, as a `rust/` folder will
contain a respective `Rust` code. Each programming language development folder must reproduce the
same results regardless the language chosen. It means different MDLs will converge on
the expected behavior and a H-hat code should work in any of those implementations.

### Current MDLs

Some MDLs are being actively developed and have their own branch. For example,
development branch for `Python` MDL is
in [dev/python](https://github.com/hhat-lang/hhat_lang/tree/dev/python), while *in progress* branch
should be in `dev/python_impl/[custom_name]`. Once stable,
their folders should appear in the main branch.

### How to use H-hat

> [!NOTE]
>
> The development is still in alpha phase, but some features are being released in different MDLs to
> test concepts, functionalities, feasibility and performance.

Each MDL folder (for example `python/`) will contain more information about their implementation as
well as how to install and/or start coding with H-hat. You may want to look directly into the folder
of your preferred (available) programming language.

### H-hat Heather

H-hat defines some rules and concepts to its paradigm so programmers can understand how to use it.
However, it does not explicitly implement a particular syntax or interpreter/JIT/compiler. The main
idea is to give programmers freedom to develop their own syntax and/or interpreter/compiler versions
that are compatible with those rules.

To showcase some features and present programmers with its paradigm, a *dialect* is developed,
called **Heather**. It is a simple dialect with simple syntax that can make concrete what
programming a H-hat code should/does look like. You may find its implementation in some of the MDL
folders as `[MDL]/dialects/heather/` (ex: `python/dialects/heather/`).

New reference dialects may emerge in the future.

## Documentation

Documentation can be found at https://docs.hhat-lang.org.

## License

MIT

## How to Contribute

!!! info "Important"

    Please read this documentation before to understand how the repository is organized and how the language structure works.

You can check the [TODOs.md](TODOs.md) page to see what is listed to be done. There (probably) are issues in the [H-hat issue's page](https://github.com/hhat-lang/hhat_lang/issues) that you may want to check and try to solve/implement as well.


At last, reach us out at the [Discord](http://discord.unitary.foundation)'s `#h-hat` channel to
learn more on how to contribute and chat, if you feel like doing so.

## Code of Conduct

We coexist in the same world. So be nice to others as you expect others to be nice to you :)
 the same world. So be nice to others as you expect others to be nice to you :)
