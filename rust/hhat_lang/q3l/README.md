
# Quantum Low-Level Languages (Q3L)


H-hat is meant to be a high-level abstraction programming language with hybrid capabilities: classical and quantum coexist in the same program. However, when the code is lowered, the quantum side must be compiled into a target quantum backend language so it can be executed in the device (or simulator). Here is where the quantum low-level languages (q3l) engine and interface are defined for each of the available languages and quantum backends.

The Q3L specific implementations are elsewhere, but they rely on this very crate to be compatible and interoperable with H-hat. For instance, Q3L for OpenQASM implementations will be located at [this repository](https://github.com/hhat-lang/hhat-openqasm).
