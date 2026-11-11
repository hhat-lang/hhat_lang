
# Rule system

!!! info

    Section in progress. More information to be added.


the H-hat rule system governs the specification of the dialects and their well-formedness rules, in which all languages must adhere to be part of the language family. Concretely, the rules are the following:

**Classical and quantum entities** must be able to coexist in the same program.
Quantum paradigm is a first-class entity just as its classical counterpart. It possesses quantum types, literals, constants, variables and functions that are denoted by the `@` prefix.

**Quantum data** must be lazily evaluated and linear, requiring a cast operator to realize it, to consume it and to drop it.

**Reflective cast** is an operator that takes one data and one type as arguments. If the data is quantum and type is classical, it triggers the realization of the accumulated instructions inside the quantum data, their emission as a Q3L and execution (with measurements) in a target backend, with subsequent sampling outcome being translated into the target classical type according to some rules described in Section 5. The classical type can be a wildcard value when all that quantum data’s fields have been previously cast.

**No quantum physics properties** such as qubits, quantum states, gates, circuits, pulses, Hamiltonians or measurement are exposed to the user as language constructs. They are handled internally by the compiler, keeping the dialects platform-independent.

**Quantum functions** must be declarative in nature to keep the quantum model abstracted away from platform-specific definitions. Quantum low-level languages and target backends will define how each primitive quantum function is interpreted. Quantum functions may have classical arguments, and must be accumulated when applied to quantum data. The rule system must fix each primitive’s signature and intended effect on the data model. A reference semantics is future work, with backends implementing against it.

**Artefact kinds** are the definitional artefacts (types, constants, behavioral definitions) and the companion artefacts (documentation and proofs) which are first-class entities and live in their own specific locations, with specific but dialect-coherent grammars. Compiler passes may trigger them through different model-driven processes.

**Companion artefacts** are specifically part of the rule system’s model-driven process, being a project’s mandatory artefacts invoked through the toolchain during flagged building and release steps.
