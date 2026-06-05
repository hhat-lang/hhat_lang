### Compiler framework

* Base compiler:
    * Parse raw text from project files (PEG) and generate HIR
    * Apply check and resolve passes, lowering HIR to target IR (Cranelift's CLIF, MLIR or Pliron IR) on CPU side, and on relevant target IRs on the sub-compilers
* Sub-compilers:
    * Produce target backend-specific lowering to target IR or machine code.
    * Have their own memory management that interfaces with the main compiler and other sub-compilers through a message passing engine.
* JIT compiler:
    * Execute instructions by the compiler.
    * Sub-compilers may have their own executors (possibly external ones).
* Debugging tools (to be implemented later).
* CLI tools.
* Proof assistant tools (to be implemented later).
* LSP tools (to be implemented later).
