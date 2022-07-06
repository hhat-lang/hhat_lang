# TODO's

Implement on `new_evaluator.Eval` :

- [x] function params and return clause
- [x] circuit type``
- [x] `if`, `elif` and `else` code
- [x] `loop` code
- [ ] unit tests

## Function Params & Return

* Params should appear inside function variable dictionary content
* Maps the external params according to function internal params (check whether they are the same type\*\*)
* Maps the return processed information to its external destination code

** except circuit type that will be converted to measurement type

## Circuit type

* circuit type is a list of graphs (nodes represent the single-index quantum gates while edges represent two+ quantum gates)
* each node contain a data whether it is an actual single gate or whether it is the _control_ or _target_; the edges will have the connections to the indices that composes the multi-index gate and the data with current gate
  * ex: single-index gate: `node(1, data='@x')`
  * ex: multi-index gate: `node(1, data='control'), node(2, data='target'), edge(1, 2, data='@cnot')`
* they represent the design of an algorithm, not its data as qubits (index is the rule)
* they only 'collapse' to measurement when called inside classical instructions/operations\*\*\*

*** they will wrap up its current data as QASM instructions in a .qasm file (or equivalent) and sent it to be processed by the quantum processor/simulator; the measurement result will then be sent to the classical instruction/operation that interacted with the circuit variable

## Conditional code (`if|elif|else`)

* define a way for the test (conditional argument) to be executed; if it is true, goes to the next element in the _same_ tuple, executing the body and then adding 2 to `stats['skip']`; otherwise, it adds 1 to the `stats['skip']`, breaks in the tuple loop

## Loopdiloop `loop`

## unit tests

* Create `htests.py` to include all the logic
* Include simple logic tests for tests for:
  * Variables
  * Functios
  * Loops
  * Conditionals


---

um oferecimento TAFUQ JETBROLLAS™.
