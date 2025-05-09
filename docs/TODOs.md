# TODOs

Here sits an updated list of things to implement/write. Feel free to check them out and [place an issue](https://github.com/hhat-lang/hhat_lang/issues) or discuss them at the [Discord](http://discord.unitary.foundation)'s `#h-hat` channel.

## H-hat core modules

### Memory
- [ ] create scope data structure for stack and heap
- [ ] define scopes:
  - [ ] `0` scope for global scope
  - [ ] `main` for main scope
  - [ ] function name with an extra identifier for their respective scope
  - [ ] make sure the current scope can only have access to `0` and its current memory scopes
- [ ] implement writing to, reading from and removing from stack
  - [ ] on the same scope
  - [ ] from a function exit back to the previous scope
- [ ] implement writing to, reading from and removing from heap
  - [ ] on the scope
- [ ] implement freeing memory (when scope is... out of scope)

### Types
- [ ] implement casting from quantum types to classical types
- [ ] implement casting from generic literals to specific literals, e.g. `156` to `u32` or `@2` to `@u3`, etc.

### Error handlers

### Execution

### Low level
- [ ] implement protocol class to interpret the result from quantum data execution into a specific classical data type
- [ ] implement conversion class to cast quantum data to classical data

### Configurations
- [ ] Implement configuration handler
  - [ ] read from file (json? yaml? toml?)
  - [ ] write to file
  - [ ] choose the settings to hold
    - [ ] target backend
      - [ ] name
      - [ ] version
      - [ ] device type: simulator, QPU
      - [ ] execution type: local, remote
      - [ ] maximum number of qubits
      - [ ] low level language(s) supported
      - [ ] execution type: static, dynamic (supports mid-circuit measurement)
  - [ ] transform settings into respective functions/classes (dynamic import)

## Heather dialect
### code

### parsing
- [ ] implement visitor/parser using Heather's AST and grammar

### simple IR builder
- [ ] finish implementing the transformation of AST into IR

### interpreter
- [ ] either remove or give a real purpose for `interpreter.executor.Evaluator`

#### classical
- [ ] finish implementing the `interpreter.classical.executor.Evaluator`

#### quantum
- [ ] connect the quantum computation result with the protocol and conversion class from the chosen classical data type and put the result into the current scope stack

## Low level core
### Quantum languages
- [ ] OpenQASM v2
  - [ ] instructions
    - [ ] if 
    - [ ] @not
    - [ ] @redim
    - [ ] @sync
    - [ ] @if
  - [ ] `LowLevelQLang`
    - [ ] includes mid-circuit measurements
    - [ ] implement `CompositeSymbol`
    - [ ] implement `CompositeLiteral`
    - [ ] implement `CompositeMixData`
    - [ ] implement fallback to H-hat dialect execution on classical code when openQASMv2 does not support the code

### (Quantum) Target backends
- [ ] `qiskit`
  - [ ] change the backend name to `ibm`?
  - [ ] include a generic way to fetch the correct backend (right now `AerSimulator` is hardcoded, but it can be any available local or remote simulator or QPU)

## Toolchain
### project
- [ ] implement `run` module to execute a code

### CLI
- [ ] implement CLI functionalities using the `toolchain.project` module
  - [ ] `new project`
  - [ ] `update`
  - [ ] `run`

## Documentation
- [ ] Describe:
  - [ ] rule system
  - [ ] cli
  - [ ] notebooks
  - [ ] dialect creation tools/API
- [ ] Finalize:
  - [ ] Language ecosystem
  - [ ] Heather syntax

