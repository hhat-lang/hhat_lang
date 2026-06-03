from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

DEFAULT_QUANTUM_CONFIG_FILENAME = "quantum_config.toml"
DEFAULT_QUANTUM_CONFIG_TITLE = "H-hat Compiler Quantum Device Configuration"
DEFAULT_QUANTUM_CONFIG_VERSION = "0.1.0"
VALID_DEVICE_KINDS = frozenset({"simulator", "device"})


@dataclass(frozen=True, slots=True)
class QuantumDeviceSpecs:
    max_n_qubits: int
    qubit_topology: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> QuantumDeviceSpecs:
        if "max_n_qubits" not in data:
            raise ValueError("quantum device specs must define 'max_n_qubits'.")

        return cls(
            max_n_qubits=int(data["max_n_qubits"]),
            qubit_topology=dict(data.get("qubit_topology", {})),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "max_n_qubits": self.max_n_qubits,
            "qubit_topology": dict(self.qubit_topology),
        }


@dataclass(frozen=True, slots=True)
class QuantumLowLevelLanguage:
    name: str
    package_name: str
    package_version: str = ""
    file_extension: str = ""

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> QuantumLowLevelLanguage:
        return cls(
            name=str(data.get("name", "")),
            package_name=str(data.get("package_name", "")),
            package_version=str(data.get("package_version", "")),
            file_extension=str(data.get("file_extension", "")),
        )

    def to_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "package_name": self.package_name,
            "package_version": self.package_version,
            "file_extension": self.file_extension,
        }


@dataclass(frozen=True, slots=True)
class QuantumDevice:
    name: str
    is_active: bool
    vendor: str
    device_kind: str
    device_platform: str
    computation_paradigm: tuple[str, ...]
    specs: QuantumDeviceSpecs
    qll: QuantumLowLevelLanguage
    extra: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> QuantumDevice:
        paradigms = data.get("computation_paradigm", ())
        if isinstance(paradigms, str):
            paradigms = (paradigms,)

        return cls(
            name=str(data.get("name", "")),
            is_active=bool(data.get("is_active", False)),
            vendor=str(data.get("vendor", "")),
            device_kind=str(data.get("device_kind", "")),
            device_platform=str(data.get("device_platform", "")),
            computation_paradigm=tuple(str(item) for item in paradigms),
            specs=QuantumDeviceSpecs.from_dict(data.get("specs", {})),
            qll=QuantumLowLevelLanguage.from_dict(data.get("qll", {})),
            extra=dict(data.get("extra", {})),
        )

    def validate(self) -> None:
        if not self.name:
            raise ValueError("quantum device must define 'name'.")
        if self.device_kind not in VALID_DEVICE_KINDS:
            raise ValueError(
                f"quantum device '{self.name}' has unsupported device_kind '{self.device_kind}'."
            )
        if not self.computation_paradigm:
            raise ValueError(
                f"quantum device '{self.name}' must define at least one computation paradigm."
            )
        if self.specs.max_n_qubits < 1:
            raise ValueError(
                f"quantum device '{self.name}' must define a positive max_n_qubits value."
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "is_active": self.is_active,
            "vendor": self.vendor,
            "device_kind": self.device_kind,
            "device_platform": self.device_platform,
            "computation_paradigm": list(self.computation_paradigm),
            "specs": self.specs.to_dict(),
            "qll": self.qll.to_dict(),
            "extra": dict(self.extra),
        }


@dataclass(frozen=True, slots=True)
class QuantumDeviceConfiguration:
    devices: tuple[QuantumDevice, ...]
    title: str = DEFAULT_QUANTUM_CONFIG_TITLE
    version: str = DEFAULT_QUANTUM_CONFIG_VERSION

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> QuantumDeviceConfiguration:
        devices = tuple(QuantumDevice.from_dict(item) for item in data.get("devices", ()))
        config = cls(
            title=str(data.get("title", DEFAULT_QUANTUM_CONFIG_TITLE)),
            version=str(data.get("version", DEFAULT_QUANTUM_CONFIG_VERSION)),
            devices=devices,
        )
        config.validate()
        return config

    @property
    def active_devices(self) -> tuple[QuantumDevice, ...]:
        return tuple(device for device in self.devices if device.is_active)

    def validate(self) -> None:
        if not self.devices:
            raise ValueError("quantum device configuration must define at least one device.")

        names: set[str] = set()
        for device in self.devices:
            device.validate()
            if device.name in names:
                raise ValueError(f"duplicate quantum device name '{device.name}'.")
            names.add(device.name)

        if not self.active_devices:
            raise ValueError("quantum device configuration must define at least one active device.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "version": self.version,
            "available": {
                "active_devices": [device.name for device in self.active_devices],
            },
            "devices": [device.to_dict() for device in self.devices],
        }


def read_quantum_device_config(path: str | Path) -> QuantumDeviceConfiguration:
    path = Path(path)
    with path.open("rb") as fp:
        return QuantumDeviceConfiguration.from_dict(tomllib.load(fp))


def write_quantum_device_config(
    config: QuantumDeviceConfiguration,
    path: str | Path = DEFAULT_QUANTUM_CONFIG_FILENAME,
) -> Path:
    config.validate()
    path = Path(path)
    path.write_text(_serialize_quantum_config(config), encoding="utf-8")
    return path


def _serialize_quantum_config(config: QuantumDeviceConfiguration) -> str:
    lines = [
        f"title = {_format_toml_value(config.title)}",
        f"version = {_format_toml_value(config.version)}",
        "",
        "[available]",
        f"active_devices = {_format_toml_value([d.name for d in config.active_devices])}",
    ]

    for device in config.devices:
        lines.extend(
            [
                "",
                "[[devices]]",
                f"name = {_format_toml_value(device.name)}",
                f"is_active = {_format_toml_value(device.is_active)}",
                f"vendor = {_format_toml_value(device.vendor)}",
                f"device_kind = {_format_toml_value(device.device_kind)}",
                f"device_platform = {_format_toml_value(device.device_platform)}",
                f"computation_paradigm = {_format_toml_value(list(device.computation_paradigm))}",
                "",
                "[devices.specs]",
                f"max_n_qubits = {_format_toml_value(device.specs.max_n_qubits)}",
                f"qubit_topology = {_format_toml_value(dict(device.specs.qubit_topology))}",
                "",
                "[devices.qll]",
                f"name = {_format_toml_value(device.qll.name)}",
                f"package_name = {_format_toml_value(device.qll.package_name)}",
                f"package_version = {_format_toml_value(device.qll.package_version)}",
                f"file_extension = {_format_toml_value(device.qll.file_extension)}",
                "",
                "[devices.extra]",
            ]
        )

        for key, value in dict(device.extra).items():
            lines.append(f"{_format_toml_key(str(key))} = {_format_toml_value(value)}")

    return "\n".join(lines).rstrip() + "\n"


def _format_toml_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
    if isinstance(value, int | float):
        return str(value)
    if isinstance(value, Mapping):
        return (
            "{ "
            + ", ".join(
                f"{_format_toml_key(str(key))} = {_format_toml_value(val)}"
                for key, val in value.items()
            )
            + " }"
        )
    if isinstance(value, list | tuple):
        return "[" + ", ".join(_format_toml_value(item) for item in value) + "]"
    if value is None:
        raise ValueError("TOML does not support null values.")

    raise TypeError(f"unsupported TOML value type: {type(value).__name__}")


def _format_toml_key(key: str) -> str:
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]*", key):
        return key

    return _format_toml_value(key)
