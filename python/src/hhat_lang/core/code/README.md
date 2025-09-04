# Code Layer Overview

Structural infrastructure for the Core intermediate representation. This layer defines abstract IR containers and modules, block and instruction bases, symbol and reference tables, an IR graph for cross module linkage, and low level utilities for perfect hash indexing and instruction lifecycle tracking. The content is dialect agnostic and back end agnostic. Establishes stable contracts used by compilers and execution subsystems within the project.

## 1. Purpose
Provide a deterministic and inspectable shape for program IR modules and their relationships. The design goals are:
1. Explicit containers for types and functions with well defined hashing and equality so that lookups are deterministic within a process.
2. Separation of concerns between IR structure, instruction hierarchy, symbol storage, and higher level compilation or evaluation logic.
3. Efficient cross module reference lookup through a compact graph representation with perfect hash layout.
4. Paradigm aware instruction bases that carry classical or quantum tags for dispatch and validation without embedding evaluator semantics.

## 2. Scope
Included:
1. Base IR abstractions for modules and IR containers.
2. Symbol and reference tables for types and functions.
3. Instruction and block base classes plus instruction status utilities.
4. IR graph and perfect hash utilities for node indexing.

## 3. Core Concepts
1. IR identity: `IRHash` is a process local identifier derived from a module path. It supports equality and hashing for fast membership and indexing in collections. It is intended for in memory structures and is not persistent across interpreter runs.
2. IR module: `BaseIRModule` holds a module path, a `SymbolTable`, and a main `BaseIRBlock`. It defines equality and hashing over these fields and supports membership tests against stored symbols and functions.
3. IR container: `BaseIR` couples a `BaseIRModule` with a `RefTable`. The reference table records external type and function references by name and the `IRHash` of the providing module.
4. Symbol storage: `SymbolTable` owns a `TypeTable` and a `FnTable`. The type table maps `Symbol` or `CompositeSymbol` to type data structures. The function table maps a symbol name to a dictionary keyed by `BaseFnCheck` with `FnDef` values. This two level organization permits multiple overloads per function name and exact retrieval by signature.
5. Function identity: `BaseFnKey` represents a full function signature used at definition time. `BaseFnCheck` represents a query signature used for lookup. Both use value based hashing derived from name and ordered argument type tuple. The hash is deterministic within a single interpreter process and not stable across runs.
6. Blocks and instructions for IR: `BaseIRBlockFlag` and `BaseIRFlag` are enumerations used to classify block kinds and instruction kinds. `BaseIRBlock` holds an ordered tuple of arguments which can be nested blocks or data values. `BaseIRInstr` carries an instruction name flag and a positional argument tuple with value based hashing.
7. Instruction hierarchy for execution planning: `BaseInstr` is the common interface for runtime instructions with a `status` and a `paradigm` accessor. `QInstr` specializes for quantum instructions and `CInstr` for classical ones. A `QInstrFlag` controls special behaviors such as skipping argument generation.
8. Cross module linkage: `RefTypeTable` and `RefFnTable` map symbols and function checks to the `IRHash` of a provider. `RefTable` is the pair of both.
9. IR graph: `IRNode` wraps a `BaseIR` and exposes its `IRHash`, module `uid`, and `Path`. `NodeSet` stores nodes in a tuple together with perfect hash parameters that enable constant time indexing by `IRHash`. `IRGraph` collects nodes, validates that all references are resolvable within the set, and marks a single main node for program entry.
10. Perfect hash utilities: `ResultPHF` stores parameters for the perfect hash function. Utilities select a prime and search parameter values that yield a collision free mapping for a given tuple of hashable items. These routines are used to build `NodeSet` indices.
11. Quantum name discipline: `check_quantum_type_correctness` validates that a classical symbol does not contain a quantum attribute while quantum symbols may include classical attributes.

## 4. File Inventory
1. `__init__.py`: package marker without runtime behavior.
2. `abstract.py`: definitions for `IRHash`, `BaseIRModule`, `BaseIR`, `RefTypeTable`, `RefFnTable`, and `RefTable`. These establish identity and linking primitives for IR modules.
3. `base.py`: core IR building blocks. Defines `BaseFnKey` and `BaseFnCheck` for function identity, `BaseIRBlockFlag` and `BaseIRFlag` enumerations, `BaseIRBlock` for nested IR block structure, and `BaseIRInstr` for instruction records with value based hashing and equality.
4. `instructions.py`: execution oriented instruction bases. Defines `BaseInstr` with a lifecycle `status` field, `QInstr` for quantum instructions and `CInstr` for classical instructions, and `QInstrFlag` for quantum specific control.
5. `new_ir.py`: graph and import utilities. Defines `IRNode`, `NodeSet`, and `IRGraph` for storing and validating a set of IR modules. Also provides `build_reftable` to construct a `RefTable` from mappings and the accessors `get_type` and `get_fn` to import items from a referenced module using an `IRHash`.
6. `symbol_table.py`: storage for declared items. It defines `TypeTable` and `FnTable` with deterministic iteration order and composite membership semantics and packages them as `SymbolTable`.
7. `utils.py`: low level utilities. Defines `InstrStatus` for instruction lifecycle, the quantum name discipline check, and perfect hash utilities including `get_phf_prime`, `gen_phf`, `get_hash`, and the `ResultPHF` container. Constants bound search limits and contain a guard for 64 bit versus 128 bit platforms.

## 5. Processing Flow
A typical processing sequence is:
Dialect IR builders or compilers produce `BaseIR` instances → The program adds nodes to an `IRGraph` and designates the main module → Build computes perfect hash parameters and validates that every external reference in `RefTable` is satisfied by the node set → Import utilities retrieve types and functions from provider nodes as needed → Execution subsystems consume blocks and instructions through their abstract interfaces and status fields.

## 6. Invariants and Contracts
1. Hashes derived from Python built in `hash` are process local by design. Values stored in `IRHash`, `BaseIRModule.uid`, and perfect hash layouts are not stable across interpreter runs. Function key and function check hashes are also process local. Persisted caches must not depend on these integer values.
2. `IRGraph.build` requires that every referenced symbol or function in every node is provided by some node in the same graph. The build step fails if any reference cannot be satisfied.
3. `FnTable` stores multiple overloads under a single symbol name. Exact retrieval is performed with a `BaseFnCheck` whose equality is name plus the ordered argument type tuple. Membership by symbol name alone reports presence of at least one overload.
4. `SymbolTable` and its sub tables preserve insertion order. This supports deterministic symbol dumps for debugging and testing.
5. `check_quantum_type_correctness` enforces that a classical symbol never contains a quantum attribute. The inverse relation is permitted.
6. `BaseInstr.status` transitions are owned by instruction implementations. Construction sets the status to not started. Implementations update to running and then to done or error. Timeout and interrupted are reserved for evaluator control.
7. Indexing nodes by `IRHash` requires a built graph with perfect hash parameters present in the node set. Before build only temporary storage exists and helper methods over temporary nodes are available.