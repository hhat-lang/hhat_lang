from __future__ import annotations

from collections import deque
from typing import Any


class Scope:
    _name: str
    _access: deque[str]

    def __init__(self, name: str, parent: Scope | None = None):
        self._access = deque()
        self._name = name
        if isinstance(parent, Scope):
            self._access.extend(parent._access)
        self._access.append(self._name)

    @property
    def name(self) -> str:
        return self._name

    @property
    def access(self) -> tuple[str, ...]:
        return tuple(self._access)

    def __hash__(self) -> int:
        return hash((hash(self._name), hash(self.access)))

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Scope):
            return self.name == other.name and self.access == other.access
        return False

    def __repr__(self) -> str:
        return f"#Scope{' > '.join(f'[{en}]{k}' for en, k in enumerate(self.access))}"
