# Memory Layer Overview

Runtime memory model for evaluation across classical and quantum computation. This directory specifies stack based frames for lexical and call scopes, a heap for dynamic storage, an index accounting facility for quantum resources, scope tracking keyed by stable identifiers, and orchestration that binds these mechanisms into a coherent manager for program execution. The design is value oriented and integrates with Core IR, the type system, and error semantics.

## 1. Purpose
Provide precise memory control with deterministic behavior:
1. Track lifetimes through explicit scopes keyed by stable values derived from intermediate blocks and dynamic depth.
2. Model function frames with ordered parameters, argument type validation, return channels, and last in first out discipline.
3. Offer a heap for dynamic entries addressed by symbols with strict key validation.
4. Manage a fixed budget of indices for quantum operations with reservation by owner, allocation, and release.
5. Present a classical manager and a quantum aware extension that adds index accounting without changing core stack and heap semantics.

## 2. Scope
1. Stable scope identifiers with process local determinism and equality comparability against integers for convenience in tables and traces.
2. Stack frames for general blocks and for function calls with two entry modes by position and by name, ordered insertion, and a return slot.
3. Heap entries indexed by symbols with typed retrieval and explicit freeing on scope exit.
4. Index accounting for a finite pool with tracking of available positions, allocated positions, resource declarations per owner, and an in use mapping from owner to positions.
5. Orchestration that creates and frees scopes, advances current scope, and exposes stack and heap to evaluators.


## 3. Core Concepts
**Scope value**
* A numeric value created from a stable function of a block identity and a depth counter. The value is deterministic within a process for the same inputs. It serves as the key for scope tables. Equality supports comparison with the same numeric form. A textual representation shortens the value for debugging.

**Stack frame**
* An ordered mapping that holds declarations and values within a scope. Keys are symbols and qualified names and a header descriptor when the frame represents a function call. Entries may be declared without assignment and later filled. Retrieval yields either a stored value or a typed failure value that carries the missing key.
* A function frame validates argument types against a header descriptor. Two entry modes are supported. Position only mode consumes values in the declared order. Named mode consumes pairs of argument name and value. A dedicated channel stores the return and allows the caller to retrieve it before frame teardown.

**Stack**
* A last in first out collection of frames. Frames are created by the evaluator at scope and call boundaries. The active frame is always the last one. Pushing a value associates a symbol with a container or associates a literal with itself. Membership tests query the active frame. Freeing removes the last frame.

**Heap**
* A dictionary of dynamic entries addressed by symbols. Setting requires a symbol key and a container value. Getting returns the stored value or a typed failure value for an invalid key. Freeing removes an entry by key.

**Index accounting**
* A manager for a fixed pool of indices used by quantum operations. Internal state consists of a double ended queue of available positions, a double ended queue of allocated positions, a resources map from owners to requested counts, and a mapping from owners to the positions currently in use. Owners are variable members or composite working entities.
* Reservation declares the future need of an owner by count. Allocation reads the declared count, assigns that many positions if sufficient capacity exists, and records ownership. Freeing returns positions to the available pool in deterministic order and updates counters.
* Operations return typed results. Allocation failure encodes both requested and available counts. Request for an unknown owner yields a typed failure value. Duplicate reservation for the same owner yields a typed failure value. Unknown conditions produce a generic typed failure value. No exceptions are used for normal flow in index operations.

## 5. Processing Flow
* Create a manager from a block identity and a depth counter and establish the initial scope. The scope table is an ordered mapping keyed by scope values and each entry owns a distinct heap.
* On scope or call entry the evaluator creates a frame and may stage function arguments.
* For quantum programs declare index requirements per owner, request indices when execution reaches the owning operation, and free them upon completion.
* On scope or call exit retrieve any staged return then remove the frame and free the scope heap as required.

## 6. Resource and Scope Discipline
**Lifetimes**
* The evaluator creates a frame when entering a scope and removes it on scope exit. Heaps are created per scope and are removed as a unit at scope exit. A return slot is consumed on retrieval and does not persist across frames.

**Depth counter**
* The interpreter maintains a non negative depth counter that increases on call entry and decreases on return. Scope values capture the counter at creation time to distinguish nested and recursive scopes that share the same block identity.

**Determinism**
* Insertion order in frames is preserved for iteration and printing. Heap iteration follows the host dictionary order and is not used for program meaning. Index allocation preserves the order in which positions are pulled from the available pool and returned upon freeing. Scope selection uses the last created scope as the current one.

## 7. Function Entry and Return
**Entry preparation**
* A function frame receives a header descriptor. Arguments are provided either as a sequence of values in the declared order or as name value pairs. The frame validates types against the header. On type mismatch evaluation terminates with a typed error in development configurations. Argument staging materializes bindings. In development configurations control may terminate upon misuse. In production configurations control continues after successful staging.

**Return handling**
* The callee writes the return value into the frame return slot. The caller retrieves it and clears the slot before the frame is freed. The return slot holds a single value.

## 8. Quantum Index Lifecycle
**Reservation**
* The owner declares the count of required positions. The declaration succeeds only if the requested count does not exceed the remaining capacity after current allocations. Reservation does not reduce capacity. Ownership is established on allocation.

**Allocation**
* A request reads the declared count for the owner. If the owner is known and sufficient capacity exists the manager assigns the positions and records the assignment under the owner. If capacity is insufficient a typed failure value reports both requested and maximum available counts. If the owner is unknown a typed failure value is returned.

**Release**
* Freeing by owner returns positions to the available pool and updates counters. The order of returned positions is preserved within a request.

## 9. File Inventory
* `__init__.py`: Package marker without runtime behavior.
* `core.py`: Implements stack frames and stack for scoped storage with function aware behavior, heap for dynamic entries per scope, scope values and scope tables for lifetime control, index accounting for quantum resources with reservation and request semantics, and memory orchestration that binds these mechanisms into classical and quantum aware managers.
