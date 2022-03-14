==============
:math:`\hat{H}` quantum language
==============


.. image:: https://img.shields.io/pypi/v/hhat_lang.svg
        :target: https://pypi.python.org/pypi/hhat_lang

.. image:: https://img.shields.io/travis/Doomsk/hhat_lang.svg
        :target: https://travis-ci.com/Doomsk/hhat_lang

.. image:: https://readthedocs.org/projects/hhat-lang/badge/?version=latest
        :target: https://hhat-lang.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status


.. image:: https://pyup.io/repos/github/Doomsk/hhat_lang/shield.svg
     :target: https://pyup.io/repos/github/Doomsk/hhat_lang/
     :alt: Updates


The core quantum language for :math:`C^{\dagger}`` programming language.

*Disclaimer*: This is a work still in very early stages and may be seeing as such, so errors, inconsistencies, tons of experimentation, modifications and trials will happen.

--------
Summary
--------

* A (high level) quantum algorithms builder
* Handling output data with context meaning
* Debugging results and quantum processes through post-measurement analysis
* Convert high level languages commands into low level quantum instructions for quantum languages such as openQASM, cQASM, NetQASM, Q1ASM to be execute on their respective hardware/simulator
* Gates approach - no directed qubit relation since it will be handled by the language, its interpreter/compiler and subsequently by the low level quantum languages compiler


-----------
Objectives
-----------

* Provide an intermediate picture between high-level and QASM-like programming languages
* Make use of basic quantum gates and complex quantum instructions in a dummy-qubit environment
* Bring light to measurement results and their analysis
* Debugging through (partial) quantum analysis of measurement results for results and inner processes comparing them to simulated ones (using fisher information, linear entropy, entanglement measurements, etc)

--------
Features
--------

* simple syntax
* static-typed
* quantum functions for quantum data
* quantum commands are referred with :code:`@` before the word, i.e. :code:`@h`, :code:`@cnot`
* measurements automatically made with :code:`@return`


Data Types
------

- **null**: no data
- **bool**: binary data, i.e. true and false, full and empty; represented as :code:`T` and :code:`F`
- (*to be revised*) **register**: sequence of natural amount of enumerated (indexed) single binary data; :code:`hashmap` with integer keys and single binary values. It is intended to store the output collected from each single measurement operation (aka :code:`@return`)
- **int**: integer numbers
- **float**: floating point numbers
- **str**: sequence of 0 or more characters between quotes :code:`""`
- **list**: sequence of any enumerated data
- **circuit**: sequence of 1 or more quantum gates for 1 or more qubits in 1 or more steps (can include other circuits as well)
- **hashmap**: an unordered associative array of keys and values
- **measurement**: a :code:`hashmap` containing relevant data output from the qubits measurement, such as: unique bits sequences final counting, number of shots, some special grouping of bits sequences counting (depending on extra arguments passed)


TODOs:
-----

- [x] create evaluators
- [/] include built-in error handler
- [/] include debugger mode
- [ ] emulate data types and memory


------
How to Use
------

To set up the language in your package manager you can use one of the following methods.

**Method 1**:

* Run :code:`python3 setup.py install` in the root folder :code:`hhat_lang`

**Method 2**:

* Run :code:`pip3 install -e .` in the root folder

-----

So far, you can:

* Run the lexer, the parser and the evaluator ("interpreter") for:
    - Variables of type: :code:`int`, :code:`str`, :code:`float`
    - Built-in functions :code:`add` and :code:`print`

How?

* Run the :code:`test_run.py` (on the folder :code:`examples`, moved to inside of :code:`hhat_lang` folder) to see the *lexer* and the *parser* results.
* Run your own code through:
.. code-block:: python

    from hhat_lang.evaluator import Code

    c = "main null C: (int res: (:add(1 1), :print))"  # include your code in this line
    code_exec = Code(c)
    code_exec.run() # it will run all the processes and evaluate the code


* [*At your own risk*] In case you are confident to make some changes in the language semantics, to generate the parser you need to change the :code:`prod_semantics.txt` and :code:`semantics_class_list.txt` files. Both files must need the same number of lines and each line is directly connected between them. The intended changes will be subject to the existing classes at :code:`core_ast.py` and :code:`data_ast.py` to handle them.

Got an error?
------
Open an issue!

TODOs:
-----

* Include explanation over the current language syntax, semantics and features


-------
License
-------

Although this code is still private, it will be available as MIT license (free software) once its repository is made public* by Doomsk_.

.. * Documentation: https://hhat-lang.readthedocs.io.

-------
Credits
-------
Code is being developed by Doomsk_, Kaonan_ and T1t0_.

----

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.



.. _Doomsk: https://github.com/Doomsk
.. _Kaonan: https://github.com/kaosmicadei
.. _T1t0: https://github.com/adauto6
.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
