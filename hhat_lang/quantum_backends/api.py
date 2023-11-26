from __future__ import annotations
from typing import Any, Callable

from dataclasses import dataclass, field, InitVar

from importlib import import_module
from hhat_lang.interpreter.post_ast import R
from hhat_lang.quantum_backends import QUANTUM_BACKENDS_PATH
from hhat_lang.quantum_backends.error import (
    NoQuantumBackendError,
    InvalidQuantumBackendError,
)
from hhat_lang.config_files import (
    BASE_CONFIG_DATA,
    BASE_Q_BACKEND_NAME,
    BASE_Q_BACKEND_DEVICE,
    BASE_Q_BACKEND_VERSION,
)


@dataclass
class QBackendConfig:
    json_data: InitVar[dict]
    name: str = field(default=BASE_Q_BACKEND_NAME)
    version: str = field(default=BASE_Q_BACKEND_VERSION)
    device: str = field(default=BASE_Q_BACKEND_DEVICE)

    data: dict = field(init=False, default_factory=dict)

    def __post_init__(self, json_data: dict | None = None) -> None:
        if json_data is None:
            json_data = BASE_CONFIG_DATA
        self.data = json_data["backends"]


class BackendEval:
    def __init__(self, config: QBackendConfig):
        self.config = config
        if backend_name := self.config.data.get(self.config.name, None):
            if backend_name:
                self.module_name = backend_name[self.config.version]
            else:
                raise NoQuantumBackendError(
                    f"No backend named '{self.config.name}' found."
                )
        else:
            raise InvalidQuantumBackendError(
                f"Invalid backend '{self.config.name}'."
            )

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


