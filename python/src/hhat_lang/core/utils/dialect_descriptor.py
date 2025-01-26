from __future__ import annotations

from pathlib import Path
import json
from dataclasses import dataclass, field

from hhat_lang.core.utils import DIALECT_FILENAME


@dataclass(slots=True, frozen=True, repr=False)
class DialectDescriptor:
    name: str
    short: str
    version: str
    options: dict = field(default_factory=dict)

    def __repr__(self) -> str:
        return f"{self.short}#{self.version}"


def get_dialect_data(dialect_dir: Path, dialect_name: str) -> DialectDescriptor:
    dialect_path = dialect_dir / dialect_name
    if dialect_path.exists():
        with open(dialect_path / DIALECT_FILENAME, "r") as f:
            dialect_data = json.load(f)
        return DialectDescriptor(**dialect_data["dialect"])
    raise ValueError(f"Could not find {dialect_name} in {get_dialect_data()}")
