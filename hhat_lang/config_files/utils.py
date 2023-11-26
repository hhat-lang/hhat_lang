import json
from pathlib import Path
from dataclasses import dataclass, field

from hhat_lang.config_files import (
    BASE_CONFIG_PATH,
    BASE_CONFIG_DATA,
    DEFAULT_CONFIG_NAME,
)


@dataclass
class QConfigData:
    lang_name: str = field(default="openqasm")
    lang_version: str = field(default="2.0")
    backend_name: str = field(default="qiskit")
    backend_version: str = field(default="0.45.0")
    backend_device_type: str = field(default="simulator")
    config_file: Path = field(default=BASE_CONFIG_PATH)

    data: dict = field(init=False, default_factory=dict)
    lang_dir: str = field(init=False)
    lang_type: str = field(init=False)
    backend_device_name: str = field(init=False)

    def __post_init__(self) -> None:
        self.data = BASE_CONFIG_DATA
        lang_data = self.data["languages"][self.lang_name][self.lang_version]
        self.lang_dir = lang_data["dir"]
        self.lang_type = lang_data["type"]
        backend_data = self.data["backends"][self.backend_name][self.backend_version]
        self.backend_device_name = backend_data[self.backend_device_type]


class QConfigTemplate:
    @classmethod
    def get_body(cls) -> dict:
        return dict(languages=dict(), backends=dict())

    @classmethod
    def get_lang(
            cls,
            name: str,
            version: str,
            dir_name: str,
            lang_type: str,
            config_dict: dict | None = None,
    ) -> dict:
        lang_dict = {name: {version: {"dir": dir_name, "type": lang_type}}}
        if config_dict is None:
            return lang_dict
        return config_dict["languages"].update(lang_dict)

    @classmethod
    def get_backend(
            cls,
            name: str,
            version: str,
            device_type: str,
            device_name: str,
            config_dict: dict | None = None,
    ) -> dict:
        backend_dict = {name: {version: {device_type: device_name}}}
        if config_dict is None:
            return backend_dict
        return config_dict["backends"].update(backend_dict)


def build_config_file(
        config: QConfigData,
        file_name: str = DEFAULT_CONFIG_NAME
) -> dict:
    data = QConfigTemplate.get_body()
    data = QConfigTemplate.get_lang(
        name=config.lang_name,
        version=config.lang_version,
        dir_name=config.lang_dir,
        lang_type=config.lang_type,
        config_dict=data,
    )
    data = QConfigTemplate.get_backend(
        name=config.backend_name,
        version=config.backend_version,
        device_type=config.backend_device_type,
        device_name=config.backend_device_name,
        config_dict=data
    )
    json.dump(data, open(Path.home() / file_name, "w"))
    print(f"-- language and backend configuration data file built with success!")
    return data
