from __future__ import annotations

from abc import ABC
from typing import Iterable, TypeVar, Generic

from hhat_lang.core.type_system import FullName

T = TypeVar("T")


class BaseFunctionData(ABC):
    """
    To be used as a holder of function name (FullName),
    args (BaseFunctionArgs class) and body (BaseFunctionBody class).
    """

    _name: FullName
    _type: FullName
    _args: BaseFunctionArgs
    _body: BaseFunctionBody

    def add_name(self, name: FullName) -> None:
        self._name = name

    def add_type(self, fn_type: FullName) -> None:
        self._type = fn_type

    def add_args(self, *args: T) -> None:
        self._args = BaseFunctionArgs()
        self._args.add(*args)

    def add_body(self, body: T) -> None:
        self._body = BaseFunctionBody(body)

    @property
    def name(self) -> FullName:
        return self._name

    @property
    def type(self) -> FullName:
        return self._type

    @property
    def args(self) -> BaseFunctionArgs:
        return self._args

    @property
    def body(self) -> BaseFunctionBody:
        return self._body

    def __repr__(self) -> str:
        return f"Fn(Name:{self.name} Type:{self.type} Args:({self.args}) Body:({self.body}))"


class BaseFunctionArgs(ABC, Generic[T]):
    """
    To be used as a holder of function arguments.
    """

    args: tuple[T, ...]

    def add(self, *args: T) -> None:
        self.args = ()
        for arg in args:
            match arg:
                case T:
                    pass

    def __repr__(self) -> str:
        return " ".join(str(k) for k in self.args)


class BaseFunctionBody(ABC, Generic[T]):
    """
    To be used as a holder of function body.
    """

    body: T

    def __init__(self, body: T):
        self.body = body

    def __repr__(self) -> str:
        return ' '.join(str(k) for k in self.body.nodes)