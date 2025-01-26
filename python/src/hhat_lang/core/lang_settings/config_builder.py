"""
To use for defining relevant configuration to build the language settings,
for instance which dialects/dialects is/are being used, the quantum backend,
the quantum low level language
"""

from __future__ import annotations

from typing import Any
from dataclasses import dataclass, field, asdict
from pathlib import Path
import json


@dataclass
class ConfigData:
    name: str = field(default="")
    short_name: str = field(default="")
    version: str = field(default="")
    options: dict = field(default_factory=dict)


class ConfigBuilder:
    def __init__(self):
        self.dialect: ConfigData | None = None
        self.backend: ConfigData | None = None
        self.ql3: ConfigData | None = None
        self.path: str | None = None

    def set_dialect(self, dialect_name: str, version: str) -> ConfigBuilder:
        if self.dialect is None:
            self.dialect = ConfigData(
                dialect_name,
                short_name=dialect_name,
                version=version.replace(".", "_")
            )
        return self

    def set_quantum_backend(
        self,
        quantum_backend_name: str,
        version: str,
        **options: Any
    ) -> ConfigBuilder:
        if self.backend is None:
            self.backend = ConfigData(
                name=quantum_backend_name,
                short_name=quantum_backend_name,
                version=version.replace(".", "_"),
                **options
            )
        return self

    def set_quantum_lowlevel_lang(
        self,
        lang_name: str,
        short_name: str,
        version: str,
        **options: Any
    ) -> ConfigBuilder:
        if self.ql3 is None:
            self.ql3 = ConfigData(lang_name, short_name, version.replace(".", "_"), **options)
        return self

    def write_file(self) -> None:
        # TODO: find a better path to it later
        cur_dir = Path(__file__).parent.parent.parent / "dialects" / self.dialect.short_name
        cur_dir.touch()
        config_path = cur_dir / "dialect_settings.json"
        self.path = config_path

        with open(config_path, "w") as dialect_file:
            json.dump(
                {
                    "dialects": asdict(self.dialect),
                    "backend": asdict(self.backend),
                    "lowlevel_lang": asdict(self.ql3),
                    "path": str(config_path),
                },
                dialect_file
            )

    @classmethod
    def read_file(cls, file_path: str | Path) -> ConfigBuilder:
        with open(file_path, "r") as dialect_file:
            res = json.load(dialect_file)

        config = ConfigBuilder()
        config.set_dialect(res["dialects"]["name"], res["dialect"]["version"].replace("_", "."))
        config.set_quantum_backend(
            res["backend"]["name"],
            res["backend"]["version"].replace("_", "."),
            **res["backend"]["options"]
        )
        config.set_quantum_lowlevel_lang(
            res["lowlevel_lang"]["name"],
            res["lowlevel_lang"]["short_name"],
            res["lowlevel_lang"]["version"].replace("_", "."),
            **res["lowlevel_lang"]["options"]
        )
        config.path = res["path"]

        return config
