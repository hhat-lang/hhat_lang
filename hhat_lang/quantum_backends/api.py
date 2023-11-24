from __future__ import annotations
from typing import Any, Callable

from abc import ABC, abstractmethod

from importlib import import_module
from hhat_lang.interpreter.post_ast import R
from hhat_lang.quantum_backends import QUANTUM_BACKENDS_PATH
from hhat_lang.config_files import BASE_CONFIG_DATA, BASE_CONFIG_NAME


class QuantumBackendAPI:
    def __init__(self):
        self.config_name = BASE_CONFIG_NAME
        self.config_data = BASE_CONFIG_DATA

    def get_backend(self) -> Callable:
        name = self.config_data["quantum_backend"]["name"]
        version = self.config_data["quantum_backend"]["version"]
        quantum_backend = import_module(f"{QUANTUM_BACKENDS_PATH}.{name}")
        # TODO: define properly the module for backends
        return quantum_backend.backend_mapper[version]

    def load_qasm(self, ) -> Any:
        ...

    def transpile(self, code: R, **kwargs: Any) -> Any:
        ...

    def execute(self) -> Any:
        ...


