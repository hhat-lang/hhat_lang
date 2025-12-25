from __future__ import annotations

from collections import OrderedDict

from hhat_lang.core.data.core import Symbol


class TypeDef1:
    _name: Symbol
    _members: TypeMembers

    def __init__(self, name: Symbol):
        self._name = name
        self._members = TypeMembers()

    def add_member(self, member_name, member_type):
        self._members += (member_name, member_type)
        return self


class TypeMembers:
    _is_leaf: bool
    _content: OrderedDict

    def __init__(self):
        self._content = OrderedDict()

    def __iadd__(self, other):
        if other[0] not in self._content:
            self._content[other[0]] = other[1]
            return self
        raise ValueError(f"{other[0]} already added")


if __name__ == "__main__":
    pass
