from __future__ import annotations


class WorkingData:
    """
    Defines everything that can work as a literal, a variable, a function
    or a type name.
    """

    _name: str
    _type: str

    @property
    def name(self) -> str:
        return self._name

    @property
    def type(self) -> str:
        return self._type


class Symbol(WorkingData):
    """
    It can be a variable, a function, a type, an argument or a parameter name.
    """

    pass


class Atomic(Symbol):
    """
    An atomic data.
    """

    pass


class Literal(WorkingData):
    """
    Any defined literal by the dialect.
    """

    pass
