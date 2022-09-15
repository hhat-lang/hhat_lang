from pre_hhat.grammar.ast import AST
from pre_hhat.operators.classical import (Add, Print)
from pre_hhat.operators.quantum import (X, H)
from pre_hhat.types.builtin import (SingleInt, SingleStr,
                                    ArrayInt, ArrayStr, ArrayCircuit)


class Evaluator:
    pass


def run(code):
    ev = Evaluator()
