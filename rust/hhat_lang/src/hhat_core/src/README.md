# H-hat core features

This crate serves to define H-hat's rule system and the language core features.

## Refactoring phase

For context during the code refactoring, what is actually being used and refactored:

### Code that will be used with some rework, but mostly new work

- [mem/core.rs](mem/core.rs) contains the structure and logic for memory blocks
- [mem/manager.rs](mem/manager.rs) contains the manager for all the memory-related constructs, such as memory block, heap, stack, index, etc
- [mem/defs.rs](mem/defs.rs) contains the constants for standard definitions for memory-based operations
- [mem/heap.rs](mem/heap.rs) contains the heap-related code
- [mem/index.rs](mem/index.rs) contains the index-relate code
- [mem/data.rs](mem/data.rs) contains the data-related code
- [utils.rs](utils.rs) contains some utilities constants and functions such as generating constant-size hashmaps and fullnames for the identifiers in the user program


### Code that needs complete rework

- [mem/stack.rs](mem/stack.rs) contains the stack-related code; must replace old code for the working one, namely mem/core.rs's `MemBlock` code with its errors/success enum


### Stale code used for reference only

Some codes can be used to build new and improved ones, such as:
- [mem/type_container.rs](mem/type_container.rs) contains an attempt to build some data structures
- [lib.rs](lib.rs) contains tests using mem/alloc.rs code must be rewritten to account for mem/core.rs code
