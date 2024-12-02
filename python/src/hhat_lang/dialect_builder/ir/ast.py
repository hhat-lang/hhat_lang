from __future__ import annotations

from hhat_lang.core.ast import BaseAST


class AST(BaseAST):
    _name: str
    _value: tuple | tuple[AST]

    def __init__(self, name: str, value: tuple[AST, ...]):
        self._name = name
        self._value = value

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> tuple[AST, ...]:
        return self._value
