from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, TypeVar, Generic

from hhat_lang.core.type_system import FullName
from hhat_lang.dialects.heather.syntax.ast import Member
from hhat_lang.dialects.heather.syntax.base import FnArgId, FnArgType, FnArgItem

T = TypeVar("T")


class BaseFunctionData(ABC):
    """
    To be used as a holder of function name (FullName),
    args (BaseFunctionArgs class) and body (BaseFunctionBody class).
    """

    _name: FullName
    _type: FullName | None
    _args: BaseFunctionArgs
    _body: BaseFunctionBody

    def add_name(self, name: FullName) -> BaseFunctionData:
        self._name = name
        return self

    def add_type(self, fn_type: FullName | None) -> BaseFunctionData:
        self._type = fn_type
        return self

    def add_args(self, *args: T) -> BaseFunctionData:
        self._args = BaseFunctionArgs()
        self._args.add(*args)
        return self

    def add_body(self, body: T) -> BaseFunctionData:
        self._body = BaseFunctionBody(body)
        return self

    @property
    def name(self) -> FullName:
        return self._name

    @property
    def type(self) -> FullName | None:
        return self._type

    @property
    def args(self) -> BaseFunctionArgs:
        return self._args

    @property
    def body(self) -> BaseFunctionBody:
        return self._body

    @abstractmethod
    def __call__(self, *args: Any, **options: Any) -> T:
        pass

    def __repr__(self) -> str:
        return f"Fn(Name:{self.name} Type:{self.type} Args:({self.args}) Body:({self.body}))"


class BaseFunctionArgs(ABC, Generic[T]):
    """
    To be used as a holder of function arguments.
    """

    args: tuple[T, ...]

    def add(self, *args: T) -> None:
        # TODO: implement when some arg is an expression other than a terminal value
        self.args = tuple(
            FnArgItem(arg[0], arg[1])
            if isinstance(arg, Member)
            else arg
            for arg in args
        )

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