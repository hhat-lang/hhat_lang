from abc import ABC


class AST(ABC):
    def __init__(self, value, value_type, ast_type, *args):
        self.value = value
        self.type = value_type
        self.ast_type = ast_type
        self.args = args

    def __bool__(self):
        return self.value is not None

    def __len__(self):
        return len(self.args)

    def __iter__(self):
        yield from self.args

    def __repr__(self):
        value = str(self.value) if self.value else ""
        args = " ".join(str(k) for k in self.args)
        return value + (f"({args})" if args else "")


class Literal(AST):
    def __init__(self, value, literal_type):
        super().__init__(value, literal_type, "literal")


class Array(AST):
    def __init__(self, *values):
        super().__init__(None, None, "array", *values)


class Id(AST):
    def __init__(self, value):
        super().__init__(value, None, "id")


class Expr(AST):
    def __init__(self, *values):
        super().__init__("expr", None, "expr", *values)


class Operation(AST):
    def __init__(self, name, *values):
        super().__init__(name, None, "oper", *values)


class Main(AST):
    def __init__(self, *exprs):
        super().__init__("main", None, "main", *exprs)


class Program(AST):
    def __init__(self, *exprs):
        super().__init__("program", None, "program", *exprs)
