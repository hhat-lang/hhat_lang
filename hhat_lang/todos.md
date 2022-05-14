# TODO's

Implement on `new_evaluator.Eval` :

* function params and return clause
* circuit type
* `if`, `elif` and `else` code
* `loop` code

## Function Params & Return

* Params should appear inside function variable dictionary content
* Maps the external params according to function internal params (check whether they are the same type\*\*)
* Maps the return processed information to its external destination code

** except circuit type that will be converted to measurement type

## Circuit type

* circuit type is a list of graphs (nodes represent the single qubit quantum gates while edges represent two+ quantum gates)
* they represent the design of an algorithm, not its data as qubits
* they only 'collapse' to measurement when called inside classical instructions/operations\*\*\*

*** they will wrap up its current data as QASM instructions in a .qasm file (or equivalent) and sent it to be processed by the quantum processor/simulator; the measurement result will then be sent to the classical instruction/operation that interacted with the circuit variable

## Conditional code (`if|elif|else`)
@tchecopunk

* define a way for the test (conditional argument) to be executed; if it is true, goes to the next element in the _same_ tuple, executing the body and then adding 2 to `stats['skip']`; otherwise, it adds 1 to the `stats['skip']`, breaks in the tuple loop

## Loopdiloop `loop`

* a
* b
* c

---

um oferecimento TAFUQ JETBROLLAS™.
