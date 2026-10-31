
# H-hat implementation in Rust


H-hat consists of a rule system, compiler and toolchain framework, and a language family.
Most of its development is built in [Rust](https://rust-lang.org/).

The folders organization is as follows:

- [`core`](hhat_lang/core)`***` for the H-hat core elements: rule system and compiler framework for dialect building
- [`dialects`](hhat_lang/dialects)`***` for the dialects shipped with H-hat
- [`q3l`](hhat_lang/q3l)`*` for the quantum low-level languages implementations, which are responsible for bridging H-hat to quantum languages such as OpenQASM
- [`rules`](hhat_lang/rules)`**` for the procedural macros and macros used to create H-hat's rule system
- [`rulesystem`](hhat_lang/rulesystem)`**` for the rule system logic and nicer packaging of the rules
- [`src`](hhat_lang/src)`*` for the H-hat ecosystem structure and logic. The one used to generate the CLI and tooling (toolchain framework included) so dialect builders can utilize to include their own dialects. Users will download its binary for project management, compilation, debugging, checks and execution


Items marked with `*` are under planning, with `**` are in queue for development, and with `***` are currently being implemented.


## Rule system development

The rule system is the core feature that enables a language to be considered a H-hat dialect, with a future possibility to be interoperable with other dialects. Every language must adopt the rule system's rules and adhere to its template so to be compliant. More on that at [`rulesystem` README](hhat_lang/rulesystem/README.md) and [`hhat-core` README](hhat_lang/core/README.md).

