from __future__ import annotations

from typing import Any

from hhat_lang.core.quantum_lowlevel_api.base import BackendConfig, BackendInfo


# TODO: finish this builder, using BackendConfig and
#  BackendInfo methods to serialized and deserialize
class BackendInfoBuilder:
    """
    Builds the data to be used by `BackendInfo` and `BackendConfig` instances.

    Currently available only as json.
    # TODO: implement in other file formats, such as toml and yaml.
    """

    _name: str
    _version: str
    _config: dict[str, Any]

    def add_name(self, name: str) -> BackendInfoBuilder:
        self._name = name
        return self

    def add_version(self, version: str) -> BackendInfoBuilder:
        self._version = version
        return self

    def add_config(self, config: dict[str, Any]) -> BackendInfoBuilder:
        self._config = config
        return self


class BackendConfigBuilder:
    pass
