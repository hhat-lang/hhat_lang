# H-hat Language Python Package
This directory contains the **Python implementation** of the H-hat language and its toolchain. The package is structured into several subpackages so that the compiler, dialects, low-level language support and user tooling are all kept separate.

## Directory overview
```
hhat_lang/
├── __init__.py
├── core/
├── dialects/
├── low_level/
└── toolchain/
```
### `__init__.py`
This file marks `hhat_lang` as a Python package.

### `core/`
The `core` package defines the foundational of the **H-hat language**. It exposes the data types, execution model, error handling, import mechanisms, memory management, type system and other low-level abstractions that dialects and tooling build upon. New dialects and backends should rely on the stable APIs in `core` for representing programs and manipulaing state. Everything outside of this package is considered dialect or backend specific and may change over time. The package also includes small utilities such as classes to represent hierarchical namespaces and result types.

### `dialects/`
This package contains implementations of H-hat dialects. A dialect is a domain specific language built on top of the H-hat core that defines its own syntax, semantics and tooling. The primary dialect provided here is **Hearther**, a simple dialect designed to demonstrate H-hat concepts and encourage developers to create their own dialects.

The Heather dialect includes grammer definitions, a parser and visitor, abstract syntax tree (AST) definitions, simple and SSA IR builders, an interpreter, code generators and dialect-specific toolchain. It provides a complete example of how to build a dialect on top of the H-hat core.

### `low_level/`
The `low_level` package abstracts away the details of *quantum assembly languages and hardware backends*. It includes code generators that translate the H-hat intermediate representation into concrete low-level languages such as OpenQasm V2, and integrations that allow programs to be run on simulators or hardware. By isolating these components, the core IR and dialects remain decoupled from any particular assembly language or target platform.

### `toolchian/`
The `toolchain` package implements the **user-facing tooling** used to create, manage and run H-hat projects. It defines a command-line interface (CLI) built on the Typer framework for tasks such as scaffording a new project or file, executinga project and displaying help. Supporting modules handle creating project structures and integrating optional features like Jupyter notebook support and syntax highlighting.