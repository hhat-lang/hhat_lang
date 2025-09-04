# Execution Layer Overview

Contracts and orchestration for evaluation over the Core IR. This layer specifies an IR management model based on a program graph of compilation units with dependency relations recorded in module reference tables, an interpreter interface that owns execution configuration and parsing, and an evaluator interface that realizes execution over an intermediate program representation. It also defines a program level assembly that binds working data, indexing and stack based memory control, symbol resolution, and integration with low level quantum targets. The design is backend neutral and dialect aware.

## 1. Purpose
Provide precise execution contracts and runtime orchestration for programs represented in the Core IR. Objectives are:
1. A graph based organization of intermediate units with explicit linking by named references.
2. An interpreter interface that converts source text to an intermediate form and drives evaluation under a consistent configuration.
3. An evaluator interface that defines a single entry procedure for single invocation execution and a recursive traversal routine for structural walking.
4. A program assembly that couples evaluator, memory control, a symbol table, and low level quantum language integration in a single executable object.
5. Deterministic scope and depth accounting to support recursion and well defined resource lifetimes.

The layer specifies interfaces and orchestration boundaries rather than concrete evaluator or parser algorithms.

## 2. Scope
1. Management of IR units in a program graph of compilation units with dependency relations recorded in module reference tables, with addition and linking by reference. Replacement is part of the interface and realized by concrete managers.
2. Parsing of source text into an intermediate form suitable for evaluation.
3. Evaluation over the intermediate form with an entry procedure that coordinates memory and a recursive routine that walks the structure.
4. Program time wiring of working data for quantum operations, index based addressing, a stack for quantum frames, and a symbol table for name resolution.
5. Integration points for device specifications, quantum target backend selection, and target language specifics used during evaluation and emission.

## 3. Core Concepts
1. **IR management**: Intermediate units are modeled as nodes keyed by a path like identity. References that originate in one unit and name types or functions in another unit induce a dependency relation recorded in the importing module reference table. The manager accepts addition of units, linking that registers reference table entries based on simple names or qualified names, and a replacement operation defined at the interface level that concrete managers can realize while preserving graph invariants.
2. **Interpreter role**: The interpreter owns execution configuration. It tracks quantum device characteristics, target backend selection, target language description, and dialect rules for parsing and evaluation. It exposes a parsing capability that converts source text to an intermediate form. It maintains a non negative counter for call depth to coordinate scope creation and destruction during recursion. Violations that produce a negative value are reported as errors.
3. **Evaluator role**: The evaluator realizes execution over the intermediate form. It provides a single entry procedure that prepares memory context and invokes evaluation, and a recursive traversal routine that performs structured walking over blocks and expressions. The evaluator object is callable to compose with higher level drivers.
4. **Program assembly**: A program instance binds the prepared intermediate block, working quantum data, an index based addressing facility, a quantum frame stack, an evaluator instance, a low level quantum language interface, and a symbol table. Running a program returns either a computed result or a typed error value. The assembly is minimal and aims to keep evaluation state explicit and inspectable.

## 4. Execution Model
Typical execution proceeds as follows.
1. Source text is parsed under the interpreter into an intermediate representation. Dialect rules and target language specifics guide the parse.
2. Intermediate units are added to the graph. For each import a reference is recorded in the importing unit reference table that points to the defining unit. Graph build finalizes the node set and validates that all recorded references resolve prior to evaluation.
3. A program instance is assembled from the main intermediate block, the evaluator, working quantum data, index based addressing, a quantum stack, and a symbol table.
4. The evaluator entry procedure receives the intermediate form and a memory control object. It sets up context for the current depth and delegates to the recursive routine which walks blocks and expressions. Name resolution is mediated by the program assembly and its symbol table. The recursive routine may interact with the quantum stack and the low level language interface when quantum instructions are encountered.
5. Upon function calls the interpreter increments the depth counter. After return it decrements the counter. The counter must not drop below zero.
6. Results and domain errors are surfaced as values where possible. Internal contract violations raise exceptions.

## 5. IR Graph Management
**Node identity and keys**
* Each unit carries a path like identity. Nodes refer to units and comparisons use value based equality of the identity.

**Dependencies and linking**
* A reference to a type or a function in another unit is represented by entries in module reference tables. References can be names or qualified names. Linking records these references and validation of dependencies occurs during graph build. Linking can be carried out by dialect specific managers or at IR construction time.

**Update operations**
* A replacement operation is part of the management contract. Concrete managers may swap the underlying unit and preserve incident dependency relations so subsequent queries observe the new unit.

## 6. Memory and Scope Discipline
**Depth management**
* A counter records the current dynamic depth of calls. The interpreter increases the counter upon entry to a call and decreases it upon return. The counter must remain non negative and an error is raised if it would become negative.

**Scope coordination**
* The evaluator creates or selects memory context based on the current depth. This interacts with frame management for quantum operations and with the index based addressing facility.

## 7. File Inventory
1. `__init__.py`: Package marker without runtime behavior.
2. `abstract_base.py`: Defines the IR management interface over a program graph of intermediate units, the interpreter interface with parsing and depth accounting, and the evaluator interface with an entry procedure, a recursive traversal routine, and a callable protocol.
3. `abstract_program.py`: Defines the program assembly that joins the evaluator, intermediate block, quantum working data, index based addressing, quantum stack, low level quantum language integration, and a symbol table, and that exposes a single run capability which returns a result or a typed error value.
