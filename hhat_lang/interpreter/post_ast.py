from __future__ import annotations

from typing import Any, Iterable, Union
from uuid import uuid4

from hhat_lang.syntax_trees.ast import ATO, AST, ASTType, ExprParadigm


class R:
    """Post-AST formatter

    Defines some extra properties for the AST
    data to be used on semantics and execution.
    """
    def __init__(
            self,
            ast_type: ASTType,
            value: ATO | R | tuple[Union[ATO, R], ...],
            paradigm_type: ExprParadigm,
            role: str,
            execute_after: tuple[str, ...] | None,
            has_q: bool = False,
    ):
        self.type = ast_type
        self.value = value if isinstance(value, tuple) else (value,)
        self.id = str(uuid4())
        self.parent_id = ""
        self.paradigm = paradigm_type
        self.role = role
        self.execute_after = execute_after if execute_after else ()
        self.assign_parent_id()
        self.has_q = has_q

    def assign_parent_id(self):
        for k in self.value:
            if isinstance(k, R):
                k.parent_id = self.id

    def __hash__(self) -> int:
        return hash(self.value)

    def __len__(self) -> int:
        return len(self.value)

    def __iter__(self) -> Iterable:
        yield from self.value

    def __repr__(self) -> str:
        has_q = "<" + ("含" if self.has_q else "無") + ">"
        return str(self.type.name) + has_q + f"[{self.paradigm.name}]" + "(" + " ".join(str(k) for k in self.value) + ")"
