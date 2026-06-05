# Language design

H-hat language details:

* It is currently being implemented in Rust, primarily using Cranelift framework (although H-hat interface should be prepared to handle [*Cranelift's CLIF*](https://github.com/bytecodealliance/wasmtime/blob/main/cranelift/docs/ir.md), [*MLIR*](https://mlir.llvm.org/), [*Pliron IR*](https://github.com/vaivaswatha/pliron) or other framework), and a intends to build a multi-stage JIT compiler.
* Concrete grammar resolved (described in a user documentation).
* Parsing through PEG.
* No AST is generated; instead, it goes straight to HIR.
* Every file (`.hat`) is a module (an IR node).
* A project is an IR graph of IR nodes, where they are connected through imports.
    * Only imported instances (either explicit by the user or resolved through resolution and checking passes) are present in the final IR node.
    * IR nodes that do not have any connections are not parsed at all.
* Cast is a special operation that invokes a sub-compiler to generate the target IR and execute instructions in that backend context, then returning results, and re-interpreting them into the defined target type (this last step through an internal cast function that must exist between the source data type and target type).
    * Cast, unless by the case of literals below, are only done explicitly (user must enforce them).
    * If types are incompatible on a function call or variable assignment, a compiler error happens.
    * It is a regular function definition with permission to go inside instance properties (almost like what meta-functions and modifiers can do, but without changing permanently an instance).
    * Cast transitivity is not planned for the moment, but might be considered in the future if user demand exists.
    * Lossy casts are not different, it is up to the user to know the consequences of casting a given data to a given type.
    * Casts fails at compile time if there is no cast function from a data type A to a type B. Failing internally may result in a system exit or panic-like end of program, unless there is a explicit logic inside of that cast's implementation to give a `result`-like type (or `option`-like); it is up to its implementation and should be documented.
* Imports must be explicit (unless the core built-in types, such as primitive types, and group functions, such as if and match).
* The language accepts function overloading, so importing the same name from different paths is expected.
    * The resolution happens during the functions checks (return result, arity and arguments types), so no additional information must be provided during importing other than the function name.
    * Function definitions of a same name must have different arguments types, arity or return type in the same file and two imported functions from different files must not collide on the function check.
    * When a function is called, the imports of the same name are checked. It will compare the argument types (and arity) with the existing possible ones. If any conflict happens (same number of arity with same argument types) a compiler error happens; otherwise, it is successfully assigned the function identifiers for that call.
    * If any overload ambiguity, a compiler error happens. The exception is when you have a overloaded functions one with explicit types and another with generics. In this case, the generics one is ignored.
    * No default arguments are supported for now.
    * Variadic functions are accept, using a modifier (the current implementation proposal).
    * No named arguments calls for now.
    * Functions can accept literals, variables, types, other functions, IRs, etc.
* Literals for primitive types on all backend kinds (unless explicitly unsupported).
    * They can be type unspecified and implicitly cast if the type is within the same type group, e.g. a generic integer literal can be converted into a signed integer of 32 bits if the variable type is of that type, but one cannot have an integer literal on an 32 bit-float type variable.
* A simplified and loose version of generics is provided.
    * Simple monomorphization (creating the instances definitions with the expected type during the HIR-to-target IR building and attaching those identifiers to the corresponding callers).
    * No subtyping needed (this is not a object-oriented language).
    * Its syntax sugar is `?`, ex: `?T` (generic type `T`).
    * If a type can fit on a concrete type defined function, always choose it against generic defined ones.
* A super-type for handling scoped generics (as exemplified above in the definitions).
* User can write: type definition, constant definition, function definition, meta-function definition, super-type definition, modifier definition.
* User can have: variable declaration and assignment.
* User can do: function, cast and meta-function calls.
* Operations are explicitly call-like shaped, no unary or binary operators.
    * Exception for constant/variable declaration, assignment, cast and modifier calls; they have their special syntax sugars, but are converted and treated in call-like shape from HIR onward.
* Explicit type annotation upon constant and variable declaration, and on return type of function calls when ambiguity happens.
* Data structures are structs and enums.
    * Structs are much like of what to expect from C or Rust (more towards Rust).
    * Enums are a middle ground between C and Rust: named values (single identifiers or structs; function-like named values like in Rust may be incorporated later).
* Data can be moved, referenced, dereferenced and freed.
    * Freeing (drop) happens according to RAII general logic, unless data is lazy. In that case, the data is automatically freed after cast happens; if cast does not happen, probably the variable is unused and must be discarded (drop can be enforced as strict data then, if compiler cannot remove it completely from the final code version).
    * Moving a data transfers it to the new owner, a new variable or inside a function, and it is their responsibility to free the data.
        * Moving individual struct members are not allowed, only borrowing them.
        * Arrays are considered a single data for all purposes of moving, borrowing and dropping. In the same fashion that moving individual struct members is not permitted, moving individual array elements are not permitted. Slices will be implemented in the future.
    * Referencing can happen as many times as one wants as long as data is not mutable or lazy; in that case only once is permitted (compiler error happens otherwise).
    * Once the borrower goes out of scope, reference is dropped. If data is dropped before borrowing ends, a compiler error must happen.
    * Dereferencing is still ongoing idea to be further defined later.
    * Lazy data cannot be cast twice.
    * No drop/free custom function/behavior defined by the user for now.
    * Move semantics in collections is having the new owner pointing to them instead; unless the data is cross-backend transferred, which in that case a cast function must be involved and the whole ABI thing should happen.
* Cast strict data is straightforward: look up for the corresponding cast function definition and executes it, returning the result.
* Cast lazy data is a reflective process: it triggers a sub-compiler of data type to compile its content to a target IR and execute it.
    * The result is then sent to the corresponding cast function definition that executes it and returns the result.
    * The sub-compiler must contain all the accepted backend kind instructions, and may also contain non-backend kind-specific instructions.
    * If the non-backend kind-specific instructions are not found, they fallback to the compiler's instructions instead, providing a hybrid inter-backend kind computation.
    * Casting type members will not cause the reflective cast trigger; only when the root type is cast that it will trigger the effect.
    * The cast on members are accumulated inside the lazy sequence as another instruction waiting to be executed. Internal cast workflow is responsible to dropping the lazy data after its last step is completed.
    * Cast workflow happens as follows:
        + Data of backend A has the accumulated IR code inside of it (of backend kind A) to be executed by the backend kind A sub-compiler.
        + When data is hybrid, meaning it has other backend kind B, then the sub-compiler (together with the configuration data) can check whether a given backend kind B instruction X is executable by it or not; if not, it must fallback to backend kind B sub-compiler.
        + If backend kind B happens to be the CPU, then it will automatically fallback to H-hat's Cranelift's CLIF compiler.
* Lifetimes are simple: implicit, inferred, checking whether a given variable outlives another variable scope, otherwise compiler error happens.
    * No annotation syntax.
    * They should be known by scope (if scope is higher, it should live at most that longer).
* Concurrency is still not a finalized step, but it is heavily inspired by Erlang's approach.
    * Process-based actor model with message passing strategy to move data between concurrent processes.
    * Borrowed data should not be allowed, at least for now.
    * Supervisor approach for fault tolerant communication across concurrent/cross-backend processes is the way I want to go forward.
    * This feature is open for suggestions.
* Cross-backend memory is still open question. Maybe something can be done in the same way to the concurrency side, using some sort of message passing for handling, synchronization and data transfer. This feature is open for suggestions.
* Layout/ABI for cross-backend communication is also open for suggestions.
* Ownership of a data is defined by its backend kind.
    * No implicit move to another backend kind nor another type indeed is permitted without a cast operation.
    * Even on the right condition, a cast function from the type A to a type B must exist.
* Configuration data for all backends available must exist in a configuration file (or database) that is preloaded during the first step of the compilation (before reading code files and parsing them).
    * These information provide the essential guidance for the compiler and sub-compilers to work properly, namely: their name, instructions available, where to find them (modules paths with binary/links/raw code), default optimization passes, other metadata, etc. This way, the compiler knows which instructions are available for compiler and sub-compilers ahead of time and can determine the best strategy to build the IR (especially for lazy evaluation), or emit an error as soon as invalid backend instructions are found.
    * Available configuration and optimization passes can be defined apart from the "default" configuration metadata.
* Types can be primitives, structs, enums for each one of the backend kinds.
    * They can be recursively defined through a pointer- (or box-)like approach.
    * Types may not have defined size at compile time. For all the known size, that data can exist on stack frames, otherwise they must exist on the heap. No special syntax for that.
* Core library: primitive and essential types (bool, integers, floats, arrays, string, for CPU, and all the related types for all the backend kinds) and some essential group functions (if, match, pipe) are provided and do not require the user to import them explicitly.
* Standard libraries:
    * Functions:
        * basic libraries for IO (`read` and `write` for various files context, e.g. plain file, `socket`, `logging`, maybe some parsing on most common DSLs: JSON, TOML, CSV, etc.)
        * math libraries (arithmetic, trigonometry, linear algebra, etc.), some data-related (datasets, data frames, etc.)
        * and other relevant libraries.
    * For types:
        * `hashmap` (and all associated types, such as `hash-key` and `hash-value`, for instance),
        * `sample_t` (and associated types),
        * Each backend kind type must have their own implementation, even if the types have the same name (but different syntax sugars). They all must be explicitly imported by the user.
* FFIs are still open question and accepting suggestions.
* The language intends to use `option` and `result` types, which should provide the basic guardrails for handling unexpected behaviors.
    * A system exit with message function or panic macro-like function (like in Rust) can be provided.
    * Each backend kind must implement their version of `option` and `result`, so they can handle that properly.
    * Supervisor strategy can then help recovery failures on concurrent/cross-backend processes.
* Different types are never implicitly cast to match one another.
    * The only exception is when there is a generic primitive type (such as `int`) that is being assigned to a variable of type `u32`. In cases like that, where you have a primitive type that can be mapped to a broader primitive type directly. Any other case, integer to float, backend kind A integer to backend kind B integer, etc. are all illegal without explicit cast operation.
* Given there are no unary and binary operators for arithmetic operations (everything follows the call-like structure), there must be exactly an implementation of comparisons for given two different types. If that exists, those data can be used in that function (i.e. they can be compared), otherwise a compiler error happens (no function found for the argument types signature).
* Backend kind inference occurs when there is a type with multiple backend kinds type members on it.
    * The higher hierarchy backend kind sub-compiler will check which instructions it can handle from the other ones and mark the ones it cannot to their own backend kinds.
    * In the most convoluted case, a mixed-backend kind struct will have to invoke all those sub-compilers during the cast operation to execute each backend kind instruction.
    * The instructions for a given backend kind cannot fall back to another backend kind sub-compiler. However, a backend kind sub-compiler can have instructions for other backend kinds on it and it should use them.
    * If instructions are not present and are from other backend kind sub-compilers, those ought to be invoked instead.
* Backend-specific optimization passes and other configuration can be set during compile time and runtime through modifiers on instances.
* Data from certain backend type can only be manipulated by functions of that backend type. The only exception (which is not really an exception) is modifiers. Because they can modify the internals of the data, which is just done on the compilation process, they are allowed to manipulate those internal states.
* Proofs are expected to be incorporated later on the language. Ideally, using Lean, but there are open questions on how to integrate H-hat with Lean in a way that Lean can check H-hat without having to rewrite to Lean. But this is not in the scope for now.
* The language has no garbage collector.
    * Freeing memory is on the compiler's RAII-like engine and user's program design.
* Raw pointer manipulation may be only available through the `unsafe` modifier (`<unsafe *>` syntax).