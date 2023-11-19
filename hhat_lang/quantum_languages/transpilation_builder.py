from __future__ import annotations
from typing import Any, Callable, Iterable


class TranspilerBuilder:
    def __init__(self):
        self.rules = dict()

    def create_rule(self):
        pass

    def add_rules(self, name: str, rule: Any) -> None:
        pass


