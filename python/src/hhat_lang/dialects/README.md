# Dialects

The `dialects` directory holds information about each existing dialect implemented inside H-hat ecosystem.

Each dialect must observe some common organization and convention, folder- and file-wise. As in [`core`](../core/README.md), there are common folders, such as `cast`, `code`, `execution`. However, new ones to account for the language proper implementation, handling code execution and auxiliary features, such as `grammar`, `parsing` and `toolchain`.

On `cast` folder, dialect-specific implementation of:
- built-in and user defined convertion functions
- general classes for types of cast (classical to classical, classical to quantum, quantum to classical and quantum to quantum)

On `code` folder:
- built-in functions implementation
- intermediate representation (IR) implementation

On `execution` folder:
- classical evaluators and quantum programs

On `grammar` folder:
- grammar and syntax definitions for the dialect, considering at least the minimum requirements set by the core rules
