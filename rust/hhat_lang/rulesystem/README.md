# H-hat rule system

This crate defines the building blocks of H-hat rule system, and provides the features for dialect builders to incorporate it into their languages, turning them into H-hat-compliant dialects.


> [!note]
> This crate is a reference only and should not be used directly. Use [`hhat-core` crate](../core) instead.
>


## Rules

The big-picture rules are defined in the paper ["Toward Declarative Platform-Independent Modeling of Hybrid Quantum--Classical Software"](https://dl.acm.org/doi/10.1145/3837062.3839078). However, rules here also mean anything that define a coherent rule system, and works towards a compliant compiler. For this reason, more rules are added so the H-hat rule system's logic checks are done internally without the dialect builder ever need to write any code for that. This keeps the consistency across all the dialects and compliant with diagnoses and checks done by the H-hat tooling.

A list of the complete rules shall be added here, as well as on the documentation.
