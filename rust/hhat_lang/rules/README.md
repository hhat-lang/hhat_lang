# H-hat rule system's rules through procedural macros

> [!warning]
> This crate should not be used directly. It is part of [`rulesystem` crate](../rulesystem) which in turn is part of [`hhat-core` crate](../core). Only hhat-core should be used by dialect builders. This crate is for reference only.
>


There are many tools to design metamodels and model-based software so their construction can be done and verified before producing any code. However, most of those solutions are external to the tools that produce the code, making it fragmented and creating a new source of possible mismatch between meaning and intention.

Another point is that if a rule is let for a dialect builder to define on their own dialect compiler, then it will depend on each one's interpretation of the rule. This is not ideal to enforce the rules are compliant and consistent across dialects, and to pass on checks by the H-hat tooling.

Given the challenges above, it was decided that H-hat rule system should be created inside Rust so that the rule is directly reflected as code, and as procedural macros and macros so that dialect builders do not have to create any rule or rule logic.

Here sit those rules and rules logics.
