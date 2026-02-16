### Nomenclature and properties

* **Instance**: a single constant, type, variable, function, meta-function, super-type or modifier object.
* **Meta-function**: a specialized function that modifies an input code in a particular (built-in or user defined) way, either through appending, replacing, overwriting or removing code. Below are some further explanations:
    * Everything should be resolved during compile time, unless not possible to be resolved.
    * Each meta-function kind has a particular syntax sugar that will define how code is to be inserted and internally manipulated.
    * Their resolution for each call case must happen at compile time whenever possible (during HIR-to-target IR building).
    * There are three kinds of meta-functions: option (or cases) denoted by `optn`, body (or blocks) denoted by `bdn`, and option-body (or case-blocks) denoted by `opt-bdn`.
    * User can defined custom meta-functions through a simple grammar.
    * Meta-functions work like other functions: they may be overloaded, but the arguments types and return type must be different, otherwise a compiler error happens.
    * Meta-functions may also be recursively called, unless proven to be unsafe/unwise to have it (user feedback needed on that). Examples:
        + `if` is an "option" meta-function that accepts an arbitrary number of test with body that will be received by it as an array of IR code. The logic behind if is: evaluate the test, if it returns true then execute the body and branches off the meta-function; otherwise, goes to the next test (in order) and repeat the process until a test is true or until there are no more tests to check.
        + `match` is an "option-body" meta-function. It receives the argument to be checked and an array of IR code (with the case with body). It will go through each case in order, check whether it matches the pattern, if so, executes the body and branches off the meta-function; otherwise, goes to the next case, until finds a matching pattern or a wildcard default, repeating the checks. It must go exhaustively through the options according to the argument type.
        + `pipe` is a "body" meta-function. It accepts an argument that will be run into a sequence of functions, to be executed in order and the result to be passed forward. The sequence of functions are passed as an IR code (an array of functions in this case). After executing the whole sequence, it branches off the meta-function returning the last value.
    + Meta-functions can only change IR, not create new files, modules or instances (at least for now).
* **Modifier**: a specialized function that access and modifies internals of instances. Additionally:
    * It may contain the self (declared/called instance) and an optional extra parameters.
    * It may change instance's properties such as mutability, reference, dereference, strictness/laziness, etc.
    * A modifier affects an instance from that point on (until another modifier changes that particular behavior).
    * It can be defined by user through a simple grammar, as well a simple syntax to apply it onto an instance.
    * Built-in ones include `&` (reference in Rust style), `*` (pointer), `mut` (mutable), `static` (static or immutable),  `pub` (public), `pvt` (private), `lazy` (to turn a strict data into lazy data), (maybe `unsafe` and `async`? or something in those lines) and some other more.
    * Combinations may produce an incompatible result that should emit a compiler or runtime error, depending on how it can be detected.
    * The only things modifier cannot manipulate/change are: instance backend type, instance name and instance's type internal representation (data structure, members types and members names, etc.)
* **Modifiers**: a special system that can contain one or more modifier functions to be applied to a single instance. They are cumulative (meaning that the leftmost modifier will be applied first to the instance and the resulting output is the new instance that will be the target for the next modifier, and so on) and applied in order of appearance (always left to right).
* **Backend kind**: a kind of device, namely: CPU and QPU (maybe more to be added later?). Further description:
    * Backend kind marks types, data (literals, constants, variables) and functions, and defines how they should behave on their own context (CPU function acting on CPU variable, or QPU function acting on QPU variable, so on).
    * Structs can have different backend kinds as their members. However, there is a hierarchy order that will transform that struct into a specific backend kind. QPU > CPU. It means that QPU can accept any other backend kind as its members, but CPU cannot accept a QPU member type. If a type accepts other kinds, it must be at least the highest hierarchy backend type or higher.
    * Because the backend kinds are distinct (have different syntax sugars), one can have them with the same name (for instance, CPU's `bool` and QPU's `@bool`), but ultimately they will be effectively distinct and unambiguous.
    * Backend kind syntax sugar:
        * CPU: no syntax sugar; variable `v`, type `some_t`, function `some-fn`.
        * QPU: `@`; ex: variable `@v`, type `@some_t`, function `@some-fn`.
* **Target architecture**: a backend kind-based instruction set architecture, for instance, CPU: x86_64, aarch64, aarch32; QPU: gate-based superconducting, gate-base trapped ion, analog-based neutral atoms, etc.
* **HIR**: high-level intermediate representation (HIR) is the data structure coming out of the project's files parsed raw texts.
    * Since H-hat has no AST, HIR is the first construction defined inside the compiler to represent the project's code.
    * It is not type checked, or generics, lazy data, RAII's drops or meta-functions resolved.
    * Imports are resolved, types and group functions are properly identified and stored.
    * Besides the parsing checks happening on the fly, missing imports or unknown calls/symbols are addressed during this step.
* **MIR**: a resolved HIR (middle intermediate representation) that will be transmitted for subsequent sub-compilers so they can resolve it on their own target IR. Further description:
    * Type checked.
    * Generics, meta-function, functions, modifiers and RAII drops resolved.
    * Concrete message passing definitions and resolutions in-place.
    * Unused instances, used-after-free, double-freeing, and illegal borrowing or owning data are reported during this step.
* **Target IR**: target IR is the data structure following MIR.
    * When HIR is into MIR, then MIR is translated into the target IR.
    * It can be [*Cranelift's CLIF*](https://github.com/bytecodealliance/wasmtime/blob/main/cranelift/docs/ir.md) [*MLIR*](https://mlir.llvm.org/), [*Pliron IR*](https://github.com/vaivaswatha/pliron) on CPU backend kind and a target-specific IR for QPU backends, such as [*OpenQASM*](https://openqasm.com/), [*NetQASM*](https://github.com/QuTech-Delft/netqasm), etc.
    * Extra optimizations may happen during this step (further development), but it is up to the target IR specification.
* **Compiler**: the base compiler that do the steps of parsing, doing passes and optimizations, lowering IRs and building the executor's schedule for each of the target machines.
    * Each target machine has its own sub-compiler.
    * Compiler orchestrates sub-compilers through a message passing-inspired engine to handle data across those sub-compilers.
    * It also has a message passing manager to transmit data between sub-compilers.
    * Sub-compiler spawn and spawn order are defined during compile time (at least for the current implementation).
* **Sub-compiler**: a lightweight set of directives, compilation and execution engines for each backend kind, per independent target architecture.
    * It will compile MIR into a suitable IR for the designed target architecture and invoke its execution process.
    * It has its own set of available instructions, rules, memory management.
    * It can receive and send data through compiler's message passing engine.
    * It may be triggered for a full lazy data, a partial lazy data or a single instruction execution. It will depend on which instructions exist on that particular lazy data content.
* **Strict evaluation**: code is evaluated where it is defined. Strict data can be mutable or immutable, depending on whether a modifier is used to change its property.
* **Lazy evaluation**: code is accumulated internally and only evaluated under certain condition, in H-hat's case, during casting. It happens when data of backend kind A is cast to a type of backend kind B (A!=B). Features:
    * Lazy data is always mutable.
    * The lazy content is the same level of IR as its surroundings (HIR if HIR, MIR if MIR, target IR if target IR).
    * When pattern matching or branching uses some lazy evaluation, that chunk of instruction is considered to be part of the lazy content as an instruction; if it cannot be separated from the whole, the entire statement/instruction block must be placed inside the lazy content.
    * Lazy resolution: if two or more lazy data interact somehow through calls, pattern matching, branching, etc., they will become a part of a bigger lazy object.
    * As long as there is a root lazy data to be cast (usually the root data of all respective lazy data), the last one with casting is responsible to trigger the whole chain of lazy instructions accumulated.
    * They cannot be evaluated any other way than through cast operations.
    * Given Lazy data is an IR code, they can be optimized, checked, resolved, emit a compiler error, etc. like any other IR block of instructions.
    * Eligible lazy chunks (pieces of code from a branching, pattern matching, etc. containing a lazy data) should be checked on whether they can alone be executed in a lazy setting or whether the whole structure should be inside of it.
    * When a lazy data A depends on a lazy data B that depends on A, they will form a bigger lazy data that incorporates both, and those specific pieces of instructions are placed in sequential order; then, the last lazy data to be cast by root is the one that will trigger the casting for the lazy; the rest of the instructions and casting will be added to the lazy data content, just as if they were type members from a bigger lazy root data.
    * No lazy data can be partially evaluated. It either gets everything evaluated on the last significant cast operation on a root data, or they cannot be evaluated at all (and thus unused data warning should be emitted).
    * Lazy data is one time execution upon cast operation. It is immediately freed inside cast and cannot be reused.
    * Lazy data accumulates IR code linearly in a first come basis. Each instruction having a numbered order to be executed, to align with message passing processes.
    * Lazy data always go through the same checks, resolutions and optimization passes as any other part of the code. The only difference is the time it is executed is not the time each instruction appears in the code, but rather when it is cast.
* **Group functions**: referring to any arrangement of functions, meta-functions, casts or modifiers instances.
* **Super-type**: a simplified version of Rust's traits and Haskell's type class, a structural typing that provides a weak ad hoc polymorphism as follows: a super-type defines which functions it expect to have with given arity and return type. Further description:
    * If a certain type is at least in one argument in all the functions with those arities and return types listed by the super-type, then that type is a part of that super-type.
    * The super-types are defined in the same file kind that group functions are defined.
    * Given each super-type provide its unique requirements, different super-type may have overlapping functions, without any problem.
    * If super-type A and super-type B have exactly the same functions (with same arity and return type), them a type that satisfies those conditions will be accepted to belong to both super-type categories A and B.
    * Its functions are only list of existing functions out there.
        * Functions are not "methods" of a super-type.
        * Functions are independent, and super-type only purpose is to group some functions together to represent a certain expected behavior for a generic type. Example:
            *  `Printable` would be a super-type that may expect `fmt<arity=1 type=str>` function. So any time a `Printable` is used for a generics, the concrete type must have `fmt` implemented with its argument type. If `u32` is used in that scenario, there must be a function definition `fn fmt(text:u32) str {...}` somewhere so `u32` matches `Printable` super-type requirements.
