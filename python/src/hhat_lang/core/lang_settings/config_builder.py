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
    version: str = field(default="")
    options: dict = field(default_factory=dict)


class ConfigBuilder:
    def __init__(self):
        self.dialect: ConfigData | None = None
        self.backend: ConfigData | None = None
        self.ql3: ConfigData | None = None

    def set_dialect(self, dialect_name: str, version: str) -> ConfigBuilder:
        if self.dialect is None:
            self.dialect = ConfigData(dialect_name, version)
        return self

    def set_quantum_backend(self, quantum_backend_name: str, **options: Any) -> ConfigBuilder:
        if self.backend is None:
            self.backend = ConfigData(quantum_backend_name, **options)
        return self

    def set_quantum_lowlevel_lang(self, lang_name: str, version: str, **options: Any) -> ConfigBuilder:
        if self.ql3 is None:
            self.ql3 = ConfigData(lang_name, version, **options)
        return self

    def build_file(self) -> None:
        # TODO: find a better path to it later
        cur_dir = Path(__file__).parent.parent.parent / "dialects" / self.dialect.name
        cur_dir.touch()
        with open(cur_dir / "dialect_settings.json", "w") as dialect_file:
            json.dump(
                {
                    "dialects": asdict(self.dialect),
                    "backend": asdict(self.backend),
                    "lowlevel_lang": asdict(self.ql3),
                },
                dialect_file
            )
        print(cur_dir)
        with open(cur_dir / "dialect_settings.json", "r") as dialect_file:
            res = json.load(dialect_file)
        print(res)
