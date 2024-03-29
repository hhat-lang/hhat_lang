# TODOs' list

## Grammar

- [ ] syntax
  - [x] id tokens
    - [x] variables and functions
    - [x] quantum variables and functions
  - [x] quantum data
  - [ ] data types
    - [x] boolean
    - [x] integer
    - [ ] float
    - [ ] complex
    - [ ] string
    - [ ] hashmap
    - [x] quantum data
  - [x] main scope
    - [x] expressions
      - [x] `pipe` expressions
      - [x] `single` expression scope
      - [x] `sequential` expression scope
      - [x] `concurrent` expression scope
      - [x] `parallel` expression scope
  - [ ] function scope
    - [ ] write down its syntax
  - [ ] alternative quantum variable scope
    - [ ] function-like syntax
  - [ ] import scope
    - [ ] decide how it will look like 
    - [ ] import syntax
- [ ] semantics
  - [ ] transform AST as R (just call it R for now) to accommodate more data relative to its execution by the Evaluator
    - [ ] function calls
      - [ ] function only
        - [x] built-in's
        - [ ] user-defined
      - [x] with args
    - [ ] variables
    - [x] literals
    - [ ] quantum data
      - [ ] reads R backwards until reaches the beginning of its expression
        - [x] for single expressions
        - [ ] for intricate expressions
      - [x] holds R data structure to be executed at the right moment
  - [ ] main
    - [ ] checking expressions
      - [x] transform into data
    - [ ] checking scopes
      - [ ] concurrent & parallel scopes
        - [ ] _a posteriori_ variable calls wait until variable is unlocked from usage on current expression
      - [ ] variable
        - [ ] lasts until scope ends unless below
        - [ ] lives to upper scope if it is the last 'operation' in the expression
  - [ ] functions
    - [ ] store function into memory to be accessible as R data structure
    - [ ] args in order and types as keys to access correct function content (function will support overloading -- most probably)
  - [ ] imports
    - [ ] get the R data structure from imported functions
    - [ ] store functions in memory
 

## Functionality

- [x] basics
  - [x] data as arrays
  - [x] built-in functions
  - [x] variables are immutable
  - [x] data passes only to the next element expression
    - [x] to
      - [x] single element expression
      - [x] scope expression
    - [x] from
      - [x] single element expression
      - [x] scope expression
- [ ] scope
  - [x] scopes create array of data
  - [ ] sequential scopes produce sequential code execution
  - [ ] concurrent scopes produce concurrent code execution
  - [ ] parallel scopes produce parallel code execution
  - [ ] execute variable-dependent expression according to variable's unlocking time
  - [ ] data lives only inside scope
    - [ ] unless the last data that will be passed to the next expression
    - [ ] unless the last data is a variable that will live on the upper scope lifetime
- [ ] quantum helm
  - [ ] quantum data
    - [x] quantum data as an R data structure holder for later execution... thing
  - [ ] quantum function
    - [ ] quantum functions as symbolic structures
      - [ ] make arithmetic operations work with them
    - [ ] transpiled into the correct representation on transpilation + quantum compilation time
  - [ ] quantum compiling
    - [ ] write quantum function transpiler
    - [ ] write measurement interpreter
    - [ ] write casting-to-type function
    - [ ] gate-based backends
      - [ ] write openqasm backend
      - [ ] write netqasm backend
      - [ ] write cqasm backend
    - [ ] pulse-based backends
      - [ ] write pulser backend
    - [ ] digital-analog backends
      - [ ] write qadence backend
- [ ] functions
- [ ] imports
- [ ] IOs
  - [ ] user (peripherals)
    - [ ] input
    - [ ] output
  - [ ] system
    - [ ] input
    - [ ] output
  - [ ] gpu
    - [ ] input
    - [ ] output
  - [ ] qpu
    - [ ] input
    - [ ] output
  - [ ] network
    - [ ] input
    - [ ] output


## QASM-like languages and pulse sequence-oriented instructions

- [ ] OpenQASM
  - [ ] 2
  - [ ] 3
- [ ] NetQASM
- [ ] Pulser
- [ ] cQASM
- [ ] Q1ASM


## Quantum backends

- [ ] Qiskit
- [ ] Simulaqron
- [ ] Netsquid
- [ ] SquidASM
