from __future__ import annotations

import json
from abc import ABC
from enum import StrEnum
from pathlib import Path
from typing import Any


class BackendDataFileType(StrEnum):
    JSON = "json"
    YAML = "yaml"
    TOML = "toml"


# TODO: finish writing BackendConfig with methods to serialize and deserialize data
class BackendConfig:
    """
    Contains number of qubits, their arrangements, and other device
    technical specifications.
    """

    _max_num_qubits: int
    _qubits_arrangements: dict[str, tuple[int, ...]]

    def __init__(self, data: dict[str, Any]):
        # fetch data somehow
        pass

    @property
    def max_num_qubits(self) -> int:
        return self._max_num_qubits

    @property
    def qubits_arrangements(self) -> dict[str, tuple[int, ...]]:
        return self._qubits_arrangements


# TODO: finish writing BackendInfo with methods to serialize and deserialize data
class BackendInfo:
    """
    All the parameters that backend uses, such as name, version and its
    configuration, such as maximum number of qubits, their arrangements
    (if relevant), and other device technical specifications.
    """

    _name: str
    _version: str
    _config: BackendConfig

    @classmethod
    def _load_error(cls, file_type: BackendDataFileType) -> BaseException:
        raise NotImplementedError(
            f"Loading Quantum Backend data from {file_type.value} "
            f"file is not available at the moment."
        )

    def __init__(self, name: str, version: str, config: dict[str, Any]):
        self._name = name
        self._version = version
        self._config = BackendConfig(config)

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> str:
        return self._version

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


# TODO: include methods to handle H-hat memory to store and retrieve data from
#  it and also to handle the low-level data, parse, compile, execute and
#  retrieve data from H-hat to backend and vice-versa.
class BaseLowLevelAPI(ABC):
    """
    Use it to build the connection with the low level quantum language implementation.
    """

    _backend_info: BackendInfo

    @property
    def name(self) -> str:
        return self._backend_info.name

    @property
    def version(self) -> str:
        return self._backend_info.version
