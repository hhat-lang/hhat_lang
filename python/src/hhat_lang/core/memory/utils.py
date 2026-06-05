from __future__ import annotations

from typing import Any, Hashable

from hhat_lang.core.utils import gen_uuid


class ScopeValue:
    """Holds a value for scopes"""

    _value: int

    def __init__(self, obj: Hashable, *, counter: int):
        """
        Hold a value for scope.

         Args:
             obj: object must be hashable
             counter: from the execution counter, to keep track of scope nesting
        """

        self._value = gen_uuid(gen_uuid(obj) + counter)

    @property
    def value(self) -> int:
        return self._value

    def __hash__(self) -> int:
        return self._value

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, ScopeValue):
            return self._value == other._value

        if isinstance(other, int):
            return self._value == other

        return False

    def __repr__(self) -> str:
        return f"S#{self._value}"
