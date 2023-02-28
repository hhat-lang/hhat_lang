"""Interpreter/Evaluator"""
import pre_hhat.core.ast_exec as ast_exec
import pre_hhat.core.memory as memory


# noinspection PyArgumentList,PyStatementEffect
class Evaluator:
    def __init__(self, pre_eval_ast):
        if isinstance(pre_eval_ast, memory.SymbolTable):
            self.code = pre_eval_ast
            self.main = self.code["main"]
        else:
            raise ValueError(
                f"{self.__class__.__name__}: ast must be of SymbolTable type (from PreEvaluator)."
            )

    def init_main(self, stack):
        stack["scope"] = "main"
        stack["mem"].init("main")
        return self.main

    def run(self):
        interpreter = ast_exec.Exec()
        stack = interpreter.new_stack()
        main_code = self.init_main(stack)
        interpreter.walk_tree(main_code, stack, memory.SymbolTable("func", self.code["func"])) # self.code["func"])
