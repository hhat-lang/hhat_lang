# $\hat{H}$ quantum language

A high abstraction quantum programming language.

*Disclaimer*: This is a work still in early stages and may be seeing as such. So errors, inconsistencies, tons of experimentation, modifications and trials will happen.

To check on the syntax and some documentation, go to the `docs` folder.

------
Contents
------
* [Summary](#summary)
* [Objectives](#objectives)
* [Features](#features)
* [Data Types](#data-types)
* [TODOs](#todos-)
* [Installation](#installation)
* [Progress](#progress)
* [Got an error?](#got-an-error)
* [License](#license)
* [Credits](#credits)


--------
Summary
--------

* A (high level) quantum algorithms builder
* Handling output quantum data with contextualized meaning
* Quantum and classical variables are arrays of data
* No qubit approach: it will be handled by the language as operations (quantum) on indexes; The interpreter/compiler will be responsible to transpile it to low level QASM instructions
* Convert high level languages commands and procedures into low level quantum instructions for quantum languages such as openQASM, cQASM, NetQASM, Q1ASM to be executed on their respective hardware/simulator
* Debugging results and quantum processes through post-measurement analysis (probably)


-----------
Objectives
-----------

* Provide an intermediate picture between classical high-level and QASM-like programming languages
* Make use of basic and complex quantum instructions and procedures in a qubit-free environment
* Bring light to measurement results and their analysis
* Be simples enough to be used by software developers with little knowledge on quantum computing
* Prepare the path for quantum devices with hundreds or thousands of qubits
* Integrate with common programming languages through function calls
* Integrate with quantum hardware and compilers
* Debugging through (partial) quantum analysis of measurement results for results and inner processes comparing them to simulated ones (using fisher information, linear entropy, entanglement measurements, etc)

--------
Features
--------

* simple syntax
* static-typed
* array-like programming
* quantum functions for quantum data
* quantum commands are referred with `@` before the word, i.e. `@init`, `@sync`
* measurements automatically made after executing quantum variable content through interaction with classical functions and classical data
* measurement result contextualized according to the data type it is interacting with


Data Types
------

- **null**: no data
- **bool**: binary data, i.e. true and false, full and empty; represented as `T` and `F`
- **int**: integer numbers
- **float**: floating point numbers
- **str**: sequence of 0 or more characters between quotes `""`
- **circuit**: sequence of 1 or more quantum gates for 1 or more qubits in 1 or more steps (can include other circuits as well)
- **hashmap**: an unordered associative array of keys and values


TODOs:
-----

* Include explanation over the current language syntax, semantics and features

------
Installation
------

To set up the language in your package manager you can use one of the following methods. (It is recommended to have [anaconda](https://www.anaconda.com/products/individual) installed with Python 3+, preferably Python 3.8.)

### Method 1: conda (easy)

* In the root folder, run:
```
python3 -m pip install -r requirements.txt
python3 -m pip install -e .
```


### Method 2: venv (advanced)

Consider all the following commands to be typed in the terminal.

* Create a venv (recommended python3.8 or 3.9): `python3.8 -m venv .venv` (the venv will be located in the folder `.venv` inside the hhat_lang root folder)
* Deactivate any other environment you might have active, i.e. conda: `conda deactivate`, until you have no environment
* Activate our new venv through: `source .venv/bin/activate`
* Install all the requirements: `python3 -m pip install -r requirements.txt`
* In the root folder, run: `python3 -m pip install -e .`
* To deactivate the newly created environment, type: `deactivate`
-----

So far, you can:

* Run the lexer, the parser and the evaluator ("interpreter") for:
    - Variables of type: `int`, `circuit`

    - Built-in functions `add`, `print`, `@init`, `@not`, `@and`

How?

* Run `hhat <path/to/your_hhat_code_here.hat>`


## Progress

- [ ] language base
  - [x] create lexer</summary>
      - [x] tokens
      - [x] comments/ignored symbols
  - [x] create parser (grammar)
      - [x] main
      - [x] params
      - [x] body
      - [x] return
      - [ ] conditional (in progress)
      - [ ] loop (in progress)
      - [x] functions
      - [ ] function imports
      - [ ] protocols imports
      - [ ] user type imports
  - [x] create ast
  - [ ] create interpreter
      - [ ] types
          - [x] int
          - [x] bool (in progress)
          - [ ] float (in progress)
          - [ ] complex (future implementation)
          - [x] str (in progress)
          - [x] hashmap (in progress)
          - [x] circuit
      - [ ] create built-in functions
          - [x] print
          - [x] add
          - [ ] mult
          - [ ] div
          - [ ] pow
          - [ ] sqrt
          - [x] @h
          - [x] @x
          - [x] @z
          - [ ] @y
          - [ ] @cnot
          - [ ] @swap
          - [ ] @cz
          - [ ] @rx
          - [ ] @rz
          - [ ] @ry
          - [ ] @t
          - [ ] @tdag
          - [ ] @s
          - [ ] @sdag
          - [ ] @cr
          - [x] @toffoli
          - [x] @and
          - [x] @not
          - [x] @init
          - [ ] @ampl
      - [x] create functions handler
          - [x] function calling
          - [x] scope variables
          - [x] returns
  - [ ] quantum variables
    - [x] pipe
    - [ ] correct qubit allocation on QASM transpilation when many quantum variables inside one quantum variable scope
  - [ ] base simulators
    - [x] openQASM 2.0
    - [ ] openQASM 3.0
    - [ ] NetQASM
    - [ ] cQASM
  - [ ] base QASM transpilers
    - [x] openQASM 2.0
    - [ ] openQASM 3.0
    - [ ] NetQASM
    - [ ] cQASM
  - [ ] protocols (for measurements results & context)
    - [ ] simple context
      - [x] weighted average
      - [x] biggest value
      - [ ] threshold
      - [ ] others
    - [ ] user defined context
  - [ ] user defined types
  - [ ] include built-in error handler
- [ ] include debugger mode
- [ ] IDE, notebooks
  - [ ] define syntax model for:
    - [ ] highlighting
    - [ ] autocompletion
  - [ ] include language kernel on jupyter notebook


Got an error?
------
Open an issue!


-------
License
-------

MIT

-------
Credits
-------
Code is being developed by [Doomsk](https://github.com/Doomsk). The author thanks [Kaonan](https://github.com/kaosmicadei), [T1t0](https://github.com/adauto6), [Anneriet](https://github.com/anneriet), [Penguim](https://github.com/danilodsp) and [Lucasczpnk](https://github.com/lucasczpnk) for great discussions and help developing the first language concepts.
