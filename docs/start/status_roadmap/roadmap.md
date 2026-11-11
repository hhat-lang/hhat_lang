
# Roadmap


This page contains roadmaps for past and present development.


## Version 0.3 (2026-2027)


!!! info

    This roadmap page covers what is expected for the version `0.3` release. A more long-term roadmap will be available in the future. 


H-hat version 0.3 is expected to bring the first fully working ecosystem, with Heather as a reference language. The following is an overview of the features to be available:

- Rule system's rules for quantum logic and enforcing constraints
- Rule system macros to be used in the dialect compiler building
- Basic compiler logic on data (ownership, borrowing, drop checks)
- Quantum low-level languages (Q3L) interfaces and quantum backends
- Heather compiler passes (source to IR, IR to Cranelift, Cranelift's JIT, IR to Q3L, Q3L to quantum backend)
- Basic typed message passing logic
- Reflective cast mechanism
- Minimal compiler diagnostics
- Minimal CLI and toolchain features for project management

Below you can find features by category. The items are not necessarily presented in order of priority or logic.


### Rule system


- Rules for quantum data, logic and its behavior (creation, ownership, borrowing, drop, lazy data behavior and realization)
- Procedural macros and macros for incorporating rules into dialect's host compiler
- Rules checks on dialect's host compiler
- Rules internal validation


### Compiler framework


- Compiler features for including the rule system on dialect's host compiler
- Compiler features for including data lifetime cycle (creation, ownership, borrowing, dropping)
- Compiler features for including the typed message passing
- Typed message passing mechanism
- Compiler passes for rules checks
- Compiler checks and diagnostics for users' code
- Reflective cast mechanism (realization of lazy quantum data)
- Q3L

### Toolchain framework


- CLI for project management (project creation, files creation, project update, project build, project execution)


### Heather dialect


- Compiler pass from source code to high-level interemediate representation (HIR)
- Compiler pass from HIR to mid-level intermediate representation (MIR)
- Compiler pass from MIR to Cranelift's CLIF and MIR to Q3L
- Compiler pass from CLIF to machine code and execution
- Compiler pass from Q3L to quantum backend, execution and output retrieval
- Typed message passing mechanism