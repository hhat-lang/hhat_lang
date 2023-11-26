from __future__ import annotations

from typing import Any, Callable
from importlib import import_module
from dataclasses import dataclass, field, InitVar

from hhat_lang.config_files import (
    BASE_CONFIG_DATA,
    BASE_Q_LANG_NAME,
    BASE_Q_LANG_VERSION,
)
from hhat_lang.quantum_languages import QUANTUM_LANGUAGES_PATH
from hhat_lang.interpreter.post_ast import R


@dataclass
class QLanguageConfig:
    json_data: InitVar[dict]
    name: str = field(default=BASE_Q_LANG_NAME)
    version: str = field(default=BASE_Q_LANG_VERSION)

    data: dict = field(init=False, default_factory=dict)

    def __post_init__(self, json_data: dict | None = None) -> None:
        if json_data is None:
            json_data = BASE_CONFIG_DATA
        self.data = json_data["languages"]


class QuantumLanguageAPI:
    def __init__(self, config: QLanguageConfig):
        self.config = config
        self.module_name = self.config.data[self.config.name][self.config.version]

    def get_lang_mapper(self) -> Callable:
        quantum_language = import_module(f"{QUANTUM_LANGUAGES_PATH}.{self.module_name}")
        return quantum_language.builtin_quantum_fn_mapper

    def parse_code(self, code: Any) -> Any:
        ...
