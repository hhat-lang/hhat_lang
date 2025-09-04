# Code Layer Overview

Structural substrate for the core intermediate representation. This layer defines the unit of compilation, the shape of executable blocks and instructions, the symbol tables for types and functions, cross module reference tables, an explicit program graph over intermediate representation units, and supporting utilities for perfect hashing and instruction lifecycle. The layer is paradigm aware across classical and quantum computation while remaining dialect neutral and backend neutral.

## 1. Purpose
Provide a precise model for representing, linking, and interrogating programs after lowering from dialects and before evaluation or backend emission. Emphasis is on explicit identity, deterministic ordering where required such as symbol and function tables, and symmetry between type entities and function entities. Cross module dependencies are recorded and validated in a graph that supports constant time lookup via a generated perfect hash function.

## 2. Design Overview
* Unit of compilation is identified by a filesystem path and exposes a main executable block together with a symbol table. Hash and equality for the unit are defined in terms of path identity and table contents.
* Symbol tables are split by kind. Type entries map a symbol or composite symbol to a concrete type structure. Function entries map a function name to a set of overloads keyed by signature. Signatures are defined by the function name and an ordered tuple of argument types. Equality and hashing for signatures are derived from these fields.
* Reference tables encode imports across units. One table maps type names to the unit that defines them. Another maps function signatures to the unit that defines them. Both support membership queries by name based keys and by signature based keys.
* The program graph stores units as nodes. Nodes carry both the unit and a key object derived from the unit path. A build procedure locks the graph by generating a perfect hash function over the nodes and by validating that all recorded references resolve to present nodes.
* Instructions are modeled with an abstract callable interface, an explicit lifecycle status, and an annotation of the data paradigm. Quantum specific instructions may carry a flag that indicates argument generation should be skipped during preparation.
* Utilities provide a perfect hashing scheme with tunable parameters for collision free indexing of finite tuples, and a validator that enforces containment constraints between quantum and classical data.

## 3. Structural Units
The compilation unit encapsulates three concerns: identity, declarations, and entry block.
* **Identity**: a path value yields a numeric identifier via the implementation defined hash primitive. This identifier is process local and intended for in memory indexing. It is not a persistent identifier across runs.
* **Declarations**: a table of types and a table of functions. Queries by name return either a concrete definition for types or the mapping from signatures to definitions for functions. Queries by full signature return the single definition for that signature when present.
* **Entry block**: a block level container whose tag classifies the block kind. Blocks are iterable over their arguments which can include values, composite values, nested blocks, or instructions.

## 4. Symbol and Reference Tables
**Type table**
* Backed by an ordered mapping to preserve insertion order, which allows deterministic iteration and reproducible printing.
* Keys are symbols or composite symbols. Values are concrete type structures that are expected to be hashable and comparable.
* Addition is idempotent for the same key and does not overwrite an existing entry. Retrieval by key returns either a definition or a default value when specified. Removal is out of scope for this layer.

**Terminology**
* Symbol denotes an atomic program identifier.
* Composite symbol denotes a qualified identifier formed from multiple segments.
* Function signature denotes a function name paired with an ordered tuple of argument types.

**Function table**
* A two level mapping. The outer mapping keys by function name. The inner mapping keys by signature and stores the definition. This supports multiple overloads for the same name.
* A signature is constructed from the function name and the ordered tuple of argument types. A companion key built from the same fields supports query by name and argument types without requiring argument names.
* Signature construction enforces that names are symbols and argument types are symbols or composite symbols. Violations raise errors during signature creation.
* Queries support three modes. By name to return all overloads for that name. By signature to return a single definition when present or no result when absent. By membership to test whether a name or a signature is present. Membership by signature presumes that the function name exists in the table.

**Reference tables**
* Two independent mappings record imports. One for type names to defining unit. One for function signatures to defining unit.
* Each entry maps a name like key to a key object that encapsulates the defining unit path and derives a numeric identifier from it. Membership supports checking by names or signatures. Equality and hashing for the key object are defined to enable direct comparison with node keys in the program graph.

## 5. Program Graph
**Nodes and keys**
* Each node wraps a unit. The node stores the unit path, a numeric identifier derived from the unit path, and a key object that exposes both the path and the numeric identifier.
* Membership over a node supports queries by symbol, composite symbol, function signature, or by path value. This allows testing whether a declaration belongs to a particular unit.
* Membership over the node set also permits queries that pair a unit path with a declaration name or signature.
* Signature based membership relies on function table semantics and presumes the name is present.

**Graph construction**
* Nodes are accumulated in a staging collection. The last added node can be designated as the main unit of the program.
* A build procedure constructs an immutable set of nodes ordered by a perfect hash function over the node keys. During the build, every reference from every node must resolve to an existing node. If a reference is missing, construction fails with an error.
* After build, nodes can be addressed in constant time by applying the generated perfect hash function to the key object.
* Constant time addressing assumes the provided key belongs to the built set of nodes.

**Complexity**
* Addressing a node by key runs in constant time after the graph is built.
* Graph construction enumerates parameter values for the perfect hash function and is proportional to the parameter search bounds times the number of nodes.

**Lookup helpers**
* A utility constructs a reference table from two mappings provided by the compiler. One mapping associates type names with defining unit paths. The other associates function signatures with defining unit paths.
* Two procedures implement import semantics over the graph. Given a node key for the importing unit and a type name the type definition is returned if present. Given a node key and a function signature the single definition is returned if present. Listing the available overloads by name is performed through the function table rather than this helper.
* If the function name is not present the signature lookup fails with an error rather than returning no result.

**Error semantics**
* A missing function name renders signature based lookup ill formed and raises an error.
* A missing signature under a present name yields no result.

## 6. Instruction Model
**Abstract instruction**
* Instructions are callable and carry a lifecycle status. The status admits the following values in increasing order of progress: not started, running, timeout, interrupted, done, error. Status begins at not started.
* Each instruction exposes its data paradigm. A query determines whether the instruction is quantum or classical.

**Paradigm specific behavior**
* Quantum instructions can carry a flag that indicates argument generation should be skipped during preparation. Classical instructions never set this flag.
* A validator enforces that classical data cannot contain quantum attributes while quantum data can contain classical attributes.

## 7. Utilities and Perfect Hashing
**Perfect hash function**
* The generator searches for parameters a and r that yield a collision free arrangement of a given finite tuple under a chosen prime and tuple size. The search space for a is bounded by a large constant. The search space for r depends on the machine word size and is compatible with word sizes of sixty four or one hundred twenty eight bits.
* The resulting parameters are returned together with the ordered tuple. A companion evaluator computes the position for any value under the returned parameters in constant time.

**General hashing**
* A key object encapsulates a path and exposes both the path and a numeric identifier derived from it. Equality supports comparison with another such key as well as with a unit by comparing the unit path.
* Key domain objects define hashing and equality through their observable fields. The design avoids relying on object identity for program semantics.

## 8. File Inventory

* `abstract.py`: abstract definitions for units, reference tables for types and functions, and the small key object used as the node key in the program graph. Hashing and equality are specified for the key object and for the module abstraction, and are provided where semantic identity matters elsewhere.
* `base.py`: base structures for function signature keys and function queries by signature, together with abstract blocks, instruction flags, and instruction containers. Hashing and equality are derived from semantic fields.
* `instructions.py`: abstract instruction interface with lifecycle status and paradigm attribute, plus classical and quantum specializations and the quantum only argument generation flag.
* `new_ir.py`: concrete node wrapper, node set with perfect hash indexing, program graph construction with validation of cross unit references, helpers to build reference tables, and import helpers for types and functions.
* `symbol_table.py`: ordered tables for types and for functions, including overload support under a two level mapping and membership semantics for names and signatures.
* `utils.py`: lifecycle status enumeration, validator for quantum and classical attribute composition, and primitives to generate and evaluate perfect hash functions with parameters a and r under a chosen prime.
