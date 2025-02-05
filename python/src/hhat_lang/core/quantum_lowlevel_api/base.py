from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from functools import singledispatchmethod
from pathlib import Path
from typing import Any

from hhat_lang.core.ir import BaseIR
from hhat_lang.core.memory.manager import MemoryManager


class BackendDataFileType(StrEnum):
    JSON = "json"
    YAML = "yaml"
    TOML = "toml"


class BackendDeviceType(StrEnum):
    SIMULATOR = "simulator"
    EMULATOR = "emulator"
    QPU = "qpu"


class BackendParadigm(StrEnum):
    # quantum gate-based instructions
    DIGITAL = "digital"
    # pulse-based instructions
    ANALOG = "analog"
    # classical instructions
    CLASSICAL = "classical"


@dataclass(slots=True, frozen=True)
class BackendMetadata:
    metadata_version: str
    lang_version: str


@dataclass(slots=True)
class QubitLayout:
    layout: dict[str, tuple[int, int]]


@dataclass(slots=True, frozen=True)
class BackendInfo:
    """
    All the parameters that backend uses, such as name, version and its
    configuration, such as maximum number of qubits, their arrangements
    (if relevant), and other device technical specifications.
    """

    name: str
    version: str
    max_num_qubits: int
    device_type: BackendDeviceType
    support_dyn_circuit: bool
    support_single_shots: bool
    metadata: BackendMetadata
    qubit_layout: QubitLayout
    supported_paradigm: set[BackendParadigm] = field(default_factory=set)

    @classmethod
    def _load_error(cls, file_type: BackendDataFileType) -> BaseException:
        raise NotImplementedError(
            f"Loading Quantum Backend data from {file_type.value} "
            f"file is not available at the moment."
        )

    @classmethod
    def _load_json(cls, file_name: str | Path) -> dict[str, Any]:
        with open(file_name) as json_file:
            data = json.load(json_file)
        return data

    @classmethod
    def _load_yaml(cls, file_name: str | Path) -> dict[str, Any]:
        raise cls._load_error(BackendDataFileType.YAML)

    @classmethod
    def _load_toml(cls, file_name: str | Path) -> dict[str, Any]:
        raise cls._load_error(BackendDataFileType.TOML)

    @classmethod
    def load(
        cls,
        file_name: str | Path,
        file_type: BackendDataFileType = BackendDataFileType.JSON,
    ) -> BackendInfo:
        """
        Loads the data from a file. Json is the default value
        """

        data = getattr(cls, str(file_type.value))(file_name)
        return BackendInfo(**data)

    def serialize(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    @singledispatchmethod
    def deserialize(cls, data: Any, extra: BackendDataFileType) -> BackendInfo:
        raise NotImplementedError()

    @classmethod
    @deserialize.register(dict)
    def _(cls, data: dict[str, Any], _extra: BackendDataFileType) -> BackendInfo:
        return BackendInfo(**data)

    @classmethod
    @deserialize.register(str)
    def _(cls, data: str, extra: BackendDataFileType) -> BackendInfo:
        return cls.load(data, extra)


# TODO: include methods to handle H-hat memory to store and retrieve data from
#  it and also to handle the low-level data, parse, compile, execute and
#  retrieve data from H-hat to backend and vice-versa.
class BaseLowLevelAPI(ABC):
    """
    Use it to build the connection with the low level quantum language implementation.
    """

    _backend: BackendInfo
    _mem: MemoryManager

    @property
    def backend(self) -> BackendInfo:
        return self._backend

    @abstractmethod
    def parse_hhat_to_native(self, data: BaseIR) -> Any:
        """
        Parse from H-hat (`BaseIR` instance) to native low-level quantum
        language code.
        """
        pass

    @abstractmethod
    def execute(self, data: Any, **options: Any) -> Any:
        """
        Execute low-level quantum language generated code on the device defined
        at the `backend` instance attribute.
        """
        pass

    @abstractmethod
    def retrieve_result(self, **options: Any) -> Any:
        """
        Retrieve measurements result from low-level quantum language execution.
        """
        pass


class BaseShotEstimator(ABC):
    shots: int

    @abstractmethod
    def __call__(self, **options: Any) -> int:
        pass
