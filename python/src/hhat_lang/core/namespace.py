from __future__ import annotations


class Namespace:
    _name: tuple[str, ...]

    def __init__(self, *names: str):
        self._name = names

    @property
    def namespace(self) -> tuple[str, ...]:
        return self._name

    def __contains__(self, item: str) -> bool:
        return item in self._name

    def __repr__(self) -> str:
        return ".".join(k for k in self._name)


class FullName:
    _name: str
    _namespace: Namespace

    def __init__(self, namespace: Namespace, name: str):
        self._namespace = namespace
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @property
    def namespace(self) -> Namespace:
        return self._namespace

    def __contains__(self, item: str) -> bool:
        return item in self.namespace

    def __repr__(self) -> str:
        with_namespace = f"{self.namespace}." if self.namespace.namespace else ""
        return f"{with_namespace}{self.name}"
