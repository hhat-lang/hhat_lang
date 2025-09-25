from __future__ import annotations

from abc import ABC
from typing import Iterable


class AST(ABC):
    """
    Abstract syntax tree for the Heather parser. Consuming the
    lexer and generating the AST to structure the code so the IR
    can be generated for the Evaluator to execute the code.

    All the AST code should inherit from this class, including Node
    and Terminal child classes.
    """

    _name: str
    _value: tuple[str | AST | tuple[AST, ...], ...] | tuple[str]

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> tuple[str | AST | tuple[AST, ...], ...] | tuple[str]:
        return self._value

    def __iter__(self) -> Iterable:
        yield from self._value


class Node(AST):
    def __repr__(self) -> str:
        res = " ".join(str(k) for k in self.value)
        return f"{self.name}({res})"


class Terminal(AST):
    def __repr__(self) -> str:
        res = f"[{self.name}]" if self.name != self.value[0] else ""
        return f"{self.__class__.__name__}{res}{self.value[0]}"
