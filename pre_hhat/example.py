"""Example of code."""

from pre_hhat.interpreter.pre_evaluator import PreEvaluator
from pre_hhat.grammar.cst import parsing_code, examples


def run():
    for k in examples:
        code_ast = parsing_code(k)
        print()
        print('*  AST:')
        print(f"      {code_ast}")
        print()
        pre_eval = PreEvaluator(code_ast)
        table = pre_eval.walk_tree()
        print()
        print('*  SymbolTable:')
        print(f"      {table}")


if __name__ == '__main__':
    run()
