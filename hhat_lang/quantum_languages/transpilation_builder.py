from __future__ import annotations
from typing import Any, Callable, Iterable

from hhat_lang.interpreter.memory import Mem
from hhat_lang.quantum_languages.api import QuantumLanguageAPI


class TranspilerBuilder:
    def __init__(self):
        self.rules = dict()

    def create_rule(self):
        pass

    def add_rules(self, name: str, rule: Any) -> None:
        pass


    def execute(self) -> None:
        pass


