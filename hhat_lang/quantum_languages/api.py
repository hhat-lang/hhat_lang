from __future__ import annotations

from typing import Any, Callable
from importlib import import_module

from hhat_lang.config_files import BASE_CONFIG_DATA, BASE_CONFIG_NAME
from hhat_lang.quantum_languages import QUANTUM_LANGUAGES_PATH


class QuantumLanguageAPI:
    def __init__(self):
        self.config_name = BASE_CONFIG_NAME
        self.config_data = BASE_CONFIG_DATA[self.config_name]

    def get_lang_mapper(self) -> Callable:
        name = self.config_data["quantum_language"]["name"]
        version = self.config_data["quantum_language"]["version"]
        quantum_language = import_module(f"{QUANTUM_LANGUAGES_PATH}.{name}")
        return quantum_language.builtin_quantum_fn_mapper[version]

    def parse_code(self, code: Any) -> Any:
        ...
