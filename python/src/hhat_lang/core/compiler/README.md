# Compiler Layer Overview

Abstract compiler interface and coordination context for lowering into core representations and for driving evaluation across classical and quantum programs. This directory defines contracts for parsing and evaluation. Implementations carry references to cooperating compilers, evaluators, quantum device specifications, backends, and language descriptors.

## 1. Purpose
1. Define a stable abstract interface for compile and run phases.
2. Centralize references to cooperating compilers across dialects and paradigms.
3. Provide consistent entry points for parsing and for evaluation.

## 2. Architectural Role
This layer sits between dialect front ends and runtime evaluators. The compiler consumes source artifacts and produces an intermediate representation or an abstract syntax tree. The compiler invokes evaluation through registered evaluators. The layer does not prescribe the IR shape or the evaluator API. It fixes method names and minimal contracts that implementations must satisfy. Implementations may delegate evaluation to interpreter and evaluator contracts in hhat_lang.core.execution.

## 3. Processing Flow
Dialect source → BaseCompiler.parse → IR or AST → BaseCompiler.evaluate → result value or runtime effect.

## 4. File Inventory
Technical description of files in this directory. Subdirectory contents are documented in their own locations. No subdirectories are present in this path.

### core.py
Module path: `hhat_lang.core.compiler.core`

Public API and contracts:

1. Class `BaseCompiler`
   Abstract base class for compilers. Holds compilation information including cooperating compilers for classical and quantum paradigms, evaluators that execute intermediate code for those paradigms, quantum device specifications, backends, and quantum language descriptors. Inherits from `abc.ABC`.

2. Method `parse(self)`
   Abstract method. Calling this method on the abstract class raises `NotImplementedError`. A concrete implementation ingests program source or a builder context captured at construction time and produces an intermediate artifact such as a module graph or an abstract syntax tree. Implementations should document the concrete return type. Implementations may populate symbol tables or analysis caches as a side effect. Implementations should avoid global state.

3. Method `evaluate(self)`
   Abstract method. Calling this method on the abstract class raises `NotImplementedError`. A concrete implementation consumes the artifact produced by `parse` and drives evaluation through available evaluators. Implementations should document the concrete return type and the meaning of the result. Implementations should define how runtime errors are surfaced.

### __init__.py
Module path: `hhat_lang.core.compiler`

Package marker with no runtime behavior. Establishes the package boundary. Reexports can be added if required.

## 5. Integration Points
Concrete compilers reference the following concepts from other core layers. This document does not specify those layers. The list clarifies roles and boundaries.
1. Cooperating compilers: classical compilers, compilers for other dialects, and quantum compilers.
2. Evaluators: components that evaluate intermediate artifacts for classical and quantum programs.
3. Quantum device specifications: descriptions of available devices and their capabilities.
4. Backends: adapters that translate intermediate artifacts into device or vendor instruction streams.
5. Quantum languages: descriptors that define available instruction sets or syntactic forms for quantum programs.

Interpreter and evaluator contracts are defined in `hhat_lang.core.execution.abstract_base`. Backend adapters are defined in hhat_lang.core.lowlevel.