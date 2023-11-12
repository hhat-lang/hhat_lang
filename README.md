[![Unitary Fund](https://img.shields.io/badge/Supported%20By-UNITARY%20FUND-brightgreen.svg?style=for-the-badge)](http://unitary.fund)
# H-hat

$\hat{H}$ (H-hat) is a high abstraction quantum programming language.

*Disclaimer*: This is a work still in early stages and may be seeing as such. So errors, inconsistencies, tons of experimentation, modifications and trials will happen.

---

**Note**: Documentation is in progress and can be found [here](https://docs.hhat-lang.org).


------
Contents
------
* [Summary](#summary)
* [Objectives](#objectives)
* [Features](#features)
* [Installation](#installation)
* [Executing Code](#executing-code)
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

* Provide an intermediate picture between classical high-level and QASM (or [QIR](https://www.qir-alliance.org/))-like programming languages
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
* array-like programming approach
* quantum functions for quantum data
* quantum commands and quantum data are referred with `@` before the word, i.e. `@init`, `@sync`, `@q1`
* measurements automatically made after executing quantum variable content through interaction with classical functions and classical data
* measurement result contextualized according to the data type it is interacting with


------
Installation
------

* Install **Python 3.10+**. 
* Set up a virtual environment, such as [anaconda](https://www.anaconda.com/products/individual) or [venv](https://docs.python.org/3/library/venv.html).
* Install the package, via [PYPI](https://pypi.org/) (instructions [below](#pypi-installation)) or in [development mode](#development-mode).

### Setting up a virtual environment

In case you don't know how to set up a virtual environment, see the examples below (choose only one):

#### Using conda

* Install [anaconda](https://www.anaconda.com/products/individual).
* Create an environment for `h-hat` and activate it: `conda activate <name_of_the_env>`

#### Using venv

* Create a venv: `python3.10 -m venv .venv` (the venv will be located in the folder `.venv` inside the hhat_lang root folder)
* Deactivate any other environment you might have active, i.e. conda: `conda deactivate`, until you have no environment
* Activate our new venv through: `source .venv/bin/activate`


### PYPI installation

After setting up your virtual environment, simply use:

```shell
python3 -m pip install hhat-lang
```

### Development mode

In the root folder, run:

```shell
python3 -m pip install -e .
```

-----
Executing Code
-----

After proceeding on your preferred installation method, it's time to run some code. Just type `hhat` in the terminal followed by the file containing your code (`.hat` extension). 

----
Progress
----

You can follow the progress in the [TODOs list](hhat_lang/TODOs-list.md).


------
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
Code is being developed by [Doomsk](https://github.com/Doomsk). The author thanks [Kaonan](https://github.com/kaosmicadei), [T1t0](https://github.com/adauto6), [Anneriet](https://github.com/anneriet), [Penguim](https://github.com/danilodsp) and [Lucasczpnk](https://github.com/lucasczpnk) for great discussions and help on developing the first language concepts.
