from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from hhat_lang.core.config.utils import read_file

QuantumDeviceKind = Literal["simulator", "device"]
TomlValue = str | int | float | bool | list[Any] | dict[str, Any] | None


@dataclass(frozen=True)
class QuantumDeviceSpecs:
    max_n_qubits: int
    qubit_topology: TomlValue = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> QuantumDeviceSpecs:
        if "max_n_qubits" not in data:
            raise ValueError("quantum device specs must define 'max_n_qubits'")
        return cls(
            max_n_qubits=int(data["max_n_qubits"]),
            qubit_topology=data.get("qubit_topology"),
        )

    def as_dict(self) -> dict[str, TomlValue]:
        return {
            "max_n_qubits": self.max_n_qubits,
            "qubit_topology": self.qubit_topology,
        }


@dataclass(frozen=True)
class QuantumLowLevelLanguage:
    name: str
    package_name: str
    package_version: str
    file_extension: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> QuantumLowLevelLanguage:
        return cls(
            name=_require_text(data, "name"),
            package_name=_require_text(data, "package_name"),
            package_version=_require_text(data, "package_version"),
            file_extension=_require_text(data, "file_extension"),
        )

    def as_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "package_name": self.package_name,
            "package_version": self.package_version,
            "file_extension": self.file_extension,
        }


@dataclass(frozen=True)
class QuantumDevice:
    name: str
    is_active: bool
    vendor: str
    device_kind: QuantumDeviceKind
    device_platform: str
    computation_paradigm: tuple[str, ...]
    specs: QuantumDeviceSpecs
    qll: QuantumLowLevelLanguage
    extra: dict[str, TomlValue] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> QuantumDevice:
        kind = _require_text(data, "device_kind")
        if kind not in {"simulator", "device"}:
            raise ValueError("device_kind must be 'simulator' or 'device'")

        return cls(
            name=_require_text(data, "name"),
            is_active=bool(data.get("is_active", False)),
            vendor=_require_text(data, "vendor"),
            device_kind=kind,
            device_platform=_require_text(data, "device_platform"),
            computation_paradigm=tuple(str(value) for value in data.get("computation_paradigm", ())),
            specs=QuantumDeviceSpecs.from_dict(data.get("specs", {})),
            qll=QuantumLowLevelLanguage.from_dict(data.get("qll", {})),
            extra=dict(data.get("extra", {})),
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "is_active": self.is_active,
            "vendor": self.vendor,
            "device_kind": self.device_kind,
            "device_platform": self.device_platform,
            "computation_paradigm": list(self.computation_paradigm),
            "specs": self.specs.as_dict(),
            "qll": self.qll.as_dict(),
            "extra": self.extra,
        }


@dataclass(frozen=True)
class QuantumDeviceConfig:
    title: str
    version: str
    devices: tuple[QuantumDevice, ...]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> QuantumDeviceConfig:
        devices = tuple(QuantumDevice.from_dict(device) for device in data.get("devices", ()))
        config = cls(
            title=_require_text(data, "title"),
            version=_require_text(data, "version"),
            devices=devices,
        )
        config.validate()
        return config

    @property
    def active_devices(self) -> tuple[QuantumDevice, ...]:
        return tuple(device for device in self.devices if device.is_active)

    def as_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "version": self.version,
            "devices": [device.as_dict() for device in self.devices],
        }

    def validate(self) -> None:
        if not self.devices:
            raise ValueError("quantum device config must contain at least one device")
        if not self.active_devices:
            raise ValueError("quantum device config must contain at least one active device")


def load_quantum_config(file: Path | str = "quantum_config.toml") -> QuantumDeviceConfig:
    return QuantumDeviceConfig.from_dict(read_file(Path(file)))


def write_quantum_config(config: QuantumDeviceConfig, file: Path | str = "quantum_config.toml") -> None:
    config.validate()
    Path(file).write_text(_render_quantum_config(config))


def _render_quantum_config(config: QuantumDeviceConfig) -> str:
    lines = [
        f"title = {_toml_value(config.title)}",
        f"version = {_toml_value(config.version)}",
        "",
    ]

    for device in config.devices:
        lines.extend(
            [
                "[[devices]]",
                f"name = {_toml_value(device.name)}",
                f"is_active = {_toml_value(device.is_active)}",
                f"vendor = {_toml_value(device.vendor)}",
                f"device_kind = {_toml_value(device.device_kind)}",
                f"device_platform = {_toml_value(device.device_platform)}",
                f"computation_paradigm = {_toml_value(list(device.computation_paradigm))}",
                "[devices.specs]",
                f"max_n_qubits = {_toml_value(device.specs.max_n_qubits)}",
            ]
        )
        if device.specs.qubit_topology is not None:
            lines.append(f"qubit_topology = {_toml_value(device.specs.qubit_topology)}")

        lines.extend(
            [
                "[devices.qll]",
                f"name = {_toml_value(device.qll.name)}",
                f"package_name = {_toml_value(device.qll.package_name)}",
                f"package_version = {_toml_value(device.qll.package_version)}",
                f"file_extension = {_toml_value(device.qll.file_extension)}",
                "[devices.extra]",
            ]
        )
        for key, value in sorted(device.extra.items()):
            lines.append(f"{key} = {_toml_value(value)}")
        lines.append("")

    return "\n".join(lines)


def _require_text(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"quantum device config must define non-empty '{key}'")
    return value


def _toml_value(value: TomlValue) -> str:
    match value:
        case bool():
            return str(value).lower()
        case int() | float():
            return str(value)
        case str():
            return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
        case list() | tuple():
            return "[" + ", ".join(_toml_value(item) for item in value) + "]"
        case dict():
            items = ", ".join(f"{key} = {_toml_value(item)}" for key, item in sorted(value.items()))
            return "{ " + items + " }"
        case None:
            raise ValueError("None is not a valid TOML value")
        case _:
            raise TypeError(f"unsupported TOML value type: {type(value).__name__}")
