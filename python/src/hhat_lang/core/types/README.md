# Types Layer Overview

Type system foundation for classical and quantum data. This directory defines the kinds of type structures, the representation of size in bits and in qubit counts, the discipline for member composition across paradigms, a catalog of built in types, conversion rules among compatible built ins, and the interface by which types produce variable templates for the data layer. The design is value oriented and interoperates with the Core IR and symbol tables for cross module resolution.

## 1. Purpose
Provide precise and inspectable typing constructs that
1. Classify types by structural kind and encode their semantics for membership and construction.
2. Represent size with explicit units for bits and qubits, including exact and bounded forms.
3. Enforce paradigm discipline so that classical declarations cannot contain quantum members while quantum declarations may contain classical members when allowed by structure.
4. Offer a variable creation protocol that yields templates used by the data layer to instantiate containers under a chosen mutability policy.
5. Supply a stable catalog of built in classical and quantum types with well defined sizes and conversion rules.

## 2. Scope
1. Structural kinds for single member, record, enumeration, union and a reserved remote union.
2. Size descriptors for bits and for qubits with lower bound and optional upper bound.
3. Rules for member addition, temporary staging of forward referenced members, and validation of paradigm compatibility.
4. A callable interface on types that returns a variable template keyed by a name and a mutability policy.
5. A catalog of built in types for integers, booleans, and floating point values together with quantum counterparts measured in qubits.
6. Conversion relations among compatible built ins and a concrete integer to unsigned casting routine with overflow and negativity checks.
7. Utilities that expose structural kind classification and a minimal abstract base to avoid circular dependencies.

## 3. Core Concepts
**Type identity**
* A type is named by a symbol or a composite symbol that carries a quantum marker when applicable. Name equality is value based within a process. The name is the stable handle used by symbol tables, imports, and variable templates.

**Structural kinds**
* The directory defines distinct structural categories. A single member kind models an alias like structure that refers to exactly one member of the same structural kind. A record kind maps member names to member types. An enumeration kind maps names to alternatives. A union kind is reserved for disjoint alternatives with a shared storage model. A remote union kind is reserved for future quantum data across process boundaries.

**Size semantics**
* Bit size is represented by an explicit integer value in bits. Quantum size is represented by a pair consisting of a lower bound and an optional upper bound measured in qubits. Quantum size supports deferred completion: if only a lower bound is known initially the upper bound can be computed later from members and cached on the descriptor. A constant for pointer size in bits provides a portable default when a structure does not specify a more precise size. Classical types carry a quantum size descriptor with minimum zero and a computed maximum of zero after resolution to support uniform handling by the quantum size resolver.

**Membership discipline**
* Member addition observes two invariants. First the member must match the structural kind required by the container. Second a classical container must not accept a quantum member. A quantum container may accept classical members where the structure allows it. Violations produce typed error values for reporting through evaluators and tools.

**Invocation and variables**
* Single member, record, enumeration, and built in single types implement a call protocol that accepts a variable name and a mutability policy and yields a variable template. Union, remote union, and array are reserved and do not implement variable construction. The template carries the declared type name, the structural description for members, and the requested policy. The data layer consumes this template to construct a concrete container and to enforce assignment and retrieval rules.

**Temporary staging**
* During IR construction some member types may be declared in other files or in later positions. A staging area records these members as pairs of names and unresolved type references. Resolution is performed by compiler or linking logic using the type table and import resolution rather than by this directory. Only record structures stage unresolved members. Built in types and enumeration and union and array do not stage members.

## 4. Structural Families
**Single member**
* Models an alias like structure with exactly one member of the same structural kind as the container. The internal mapping associates the container name to the referenced member name. Variable templates produced by this kind describe a single entry layout.

**Record**
* Associates member names to member types in an ordered mapping. Addition checks paradigm compatibility and preserves insertion order for deterministic iteration and printing. A staging operation accepts unresolved member pairs that are later validated and committed into the mapping.

**Enumeration**
* Associates alternatives keyed by names. Alternatives can be provided by name or by a reference to another type object. Addition checks paradigm compatibility at the level of names. Variable templates describe the set of alternatives for downstream consumers.

**Union and remote union**
* Reserved kinds for disjoint alternatives and for remote quantum composition. These kinds are not specified and define no member operations.

**Array**
* Reserved for repeated element structures. The current implementation records an array flag and size defaults and does not define member operations, length metadata, or a structural kind enumerant.

## 5. Built in Catalog and Conversion
**Built in catalog**
* Classical types include signed and unsigned integers with sizes 16, 32, and 64 bits, a boolean of 8 bits, and floating point values of 32 and 64 bits. Quantum types include a boolean measured as one qubit, fixed width quantum integers that require two, three, or four qubits, and a generic quantum integer whose quantum size is bounded between the smallest and largest fixed width quantum integers. Quantum built ins use the pointer size constant as their bit size.

**Compatibility and casting**
* A relation maps three generic built ins to their compatible targets. The generic integer maps to all signed and unsigned integer widths in this directory. The generic floating point maps to both floating point widths. The generic quantum integer maps to all fixed width quantum integers available here.
* A casting routine implements integer to unsigned conversion for both literal values and variable containers. It rejects negative values and values that exceed the representable range computed as two to the power of the bit size. Errors are reported as typed values that distinguish negativity and overflow from general cast incompatibility.
* Only integer to unsigned conversion is implemented at present. Other relations are compatibility specifications and not casting implementations.

## 6. Size Resolution
**Bit size**
* The bit size descriptor is a simple wrapper around an integer in bits. It is set on construction for built in types and defaults to the pointer size constant for user declared structures when a specific size is not known.

**Quantum size**
* The quantum size descriptor stores a minimum and an optional maximum. A resolver derives a maximum after members are known. For record like composition the intended maximum equals the sum of member maxima. For enumeration the intended maximum equals the maximum across alternatives. The present implementation computes the sum across members for all composite kinds which is a conservative upper bound for enumeration. The first resolution fixes the maximum on the descriptor and subsequent calls return the cached value. Quantum structures must carry a descriptor and missing descriptors are errors.

**Complexity**
* Resolution runs in time linear in the number of referenced members visited in the intermediate representation graph.

**Resolution phases**
* Compile time functions are reserved for computing bit and quantum sizes from declarations and from the type table when full information is present. Runtime functions are reserved for interpreting dynamic sizes if the language gains features that depend on runtime values. Placeholders exist for these routines and are intended to be completed when the language specifies such features.

## 7. File Inventory
1. `__init__.py`: Defines a constant with the size of a pointer in bits. This value is used as the default bit size for built in quantum types and for user declared structures when a precise size is not known.
2. `abstract_base.py`: Declares the abstract base for type structures together with size descriptors for bits and qubits. Provides storage for the type name, the structural kind, quantum status, built in status, array flag, the ordered member mapping, and a staging area used by records for unresolved members. Exposes iteration over ordered members and membership queries over the internal mapping. The abstract call protocol returns a variable template and defers container construction to the data layer.
3. `builtin_base.py`: Defines the concrete built in structural form for a single member type. The form fixes the structural kind, sets bit size and quantum size defaults, and exposes a casting entry point that delegates to conversion routines. Built in types are fully specified at declaration time and reject staging of unresolved members. The call protocol returns a variable template with a single entry layout. This file also introduces classical and quantum integer families grouped for convenient checks.
4. `builtin_types.py`: Constructs the catalog of built in classical and quantum types with explicit bit sizes and quantum sizes. The generic quantum integer receives a quantum size interval whose lower bound equals the smallest fixed width quantum integer and whose upper bound equals the largest fixed width quantum integer. A mapping from symbolic names to the corresponding built in instances enables table driven lookup.
5. `builtin_conversion.py`: Specifies compatibility relations among generic built ins and implements the integer to unsigned casting routine. The routine supports literals and variable containers, computes the maximum representable value from the target bit size, and returns typed errors for negativity, overflow, or general incompatibility.
6. `core.py`: Implements concrete structural families for single member, record, enumeration, union, remote union, and array. Member addition enforces kind matching and paradigm discipline. Record types preserve insertion order, support staging of unresolved members, and produce variable templates carrying ordered layouts. Enumeration types accept alternatives by name or by reference to other types while enforcing paradigm compatibility at the name level. Union and array are reserved for future completion. A helper tests membership validity by checking classical versus quantum constraints.
7. `utils.py`: Defines the finite classification of structural kinds and a minimal abstract base used to avoid circular imports. A reserved kind is included for remote union to enable future expansion without breaking existing code.
8. `resolve_sizes.py`: Provides a resolver for quantum size that walks the intermediate representation graph from a declaring node, resolves member types through the symbol table, computes the sum of member maxima, and fixes the maximum on the descriptor. Placeholders exist for compile time and runtime size resolution for both bits and qubits.
