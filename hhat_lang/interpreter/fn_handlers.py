from uuid import uuid4

from hhat_lang.interpreter.post_ast import R


class Fn:
    def __init__(self, name: str, args: R | None, body: R):
        self.id = str(uuid4())
        self.name = name
        self.args = args
        self.body = body

    def __repr__(self) -> str:
        args = "(" + " ".join(str(p) for p in self.args) + ")" if self.args is not None else ""
        return f"fn%{self.name}{args}({self.body})"
