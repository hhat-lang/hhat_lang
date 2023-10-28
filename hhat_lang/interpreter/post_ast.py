from typing import Any, Iterable
from uuid import uuid4

from hhat_lang.syntax_trees.ast import ASTType, ExprParadigm


class R:
    """Post-AST formatter

    Defines some extra properties for the AST
    data to be used on semantics and execution.
    """
    def __init__(
            self,
            ast_type: ASTType,
            value: Any,
            paradigm_type: ExprParadigm,
            role: str,
            execute_after: tuple[str] | None
    ):
        self.type = ast_type
        self.value = value if isinstance(value, tuple) else (value,)
        self.id = str(uuid4())
        self.paradigm = paradigm_type
        self.role = role
        self.execute_after = execute_after if execute_after else ()

    def __hash__(self) -> int:
        return hash(self.value)

    def __len__(self) -> int:
        return len(self.value)

    def __iter__(self) -> Iterable:
        yield from self.value

    def __repr__(self) -> str:
        return str(self.type) + f"[{self.paradigm.name}]" + "(" + " ".join(str(k) for k in self.value) + ")"
