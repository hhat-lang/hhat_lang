from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from hhat_lang.core.config.utils import read_file

DEFAULT_QUANTUM_CONFIG_FILE = "quantum_config.toml"


@dataclass(frozen=True)
class QuantumDeviceSpecs:
    max_n_qubits: int
    qubit_topology: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> QuantumDeviceSpecs:
        return cls(
            max_n_qubits=int(data["max_n_qubits"]),
            qubit_topology=dict(data.get("qubit_topology", {})),
        )

    def validate(self) -> None:
        if self.max_n_qubits < 1:
            raise ValueError("quantum device max_n_qubits must be greater than zero.")

    def serialize(self) -> dict[str, Any]:
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

    def __post_init__(self) -> None:
        object.__setattr__(self, "file_extension", self.file_extension.lstrip("."))

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> QuantumLowLevelLanguage:
        return cls(
            name=str(data["name"]),
            package_name=str(data["package_name"]),
            package_version=str(data["package_version"]),
            file_extension=str(data["file_extension"]),
        )

    def validate(self) -> None:
        if not self.name:
            raise ValueError("quantum low-level language name must be defined.")
        if not self.package_name:
            raise ValueError("quantum low-level language package_name must be defined.")
        if not self.file_extension:
            raise ValueError("quantum low-level language file_extension must be defined.")

    def serialize(self) -> dict[str, Any]:
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
    device_kind: str
    device_platform: str
    computation_paradigm: tuple[str, ...]
    specs: QuantumDeviceSpecs
    qll: QuantumLowLevelLanguage
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> QuantumDevice:
        return cls(
            name=str(data["name"]),
            is_active=_read_bool(data["is_active"], field_name="is_active"),
            vendor=str(data["vendor"]),
            device_kind=str(data["device_kind"]),
            device_platform=str(data["device_platform"]),
            computation_paradigm=_read_string_tuple(data["computation_paradigm"]),
            specs=QuantumDeviceSpecs.from_mapping(data["specs"]),
            qll=QuantumLowLevelLanguage.from_mapping(data["qll"]),
            extra=dict(data.get("extra", {})),
        )

    def validate(self) -> None:
        if not self.name:
            raise ValueError("quantum device name must be defined.")
        if not self.vendor:
            raise ValueError(f"quantum device {self.name!r} must define a vendor.")
        if self.device_kind not in {"device", "simulator"}:
            raise ValueError(f"quantum device {self.name!r} kind must be 'device' or 'simulator'.")
        if not self.device_platform:
            raise ValueError(f"quantum device {self.name!r} must define a platform.")
        if not self.computation_paradigm:
            raise ValueError(
                f"quantum device {self.name!r} must define at least one computation paradigm."
            )
        self.specs.validate()
        self.qll.validate()

    def serialize(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "is_active": self.is_active,
            "vendor": self.vendor,
            "device_kind": self.device_kind,
            "device_platform": self.device_platform,
            "computation_paradigm": list(self.computation_paradigm),
            "specs": self.specs.serialize(),
            "qll": self.qll.serialize(),
            "extra": self.extra,
        }


@dataclass(frozen=True)
class QuantumDeviceConfig:
    title: str
    version: str
    devices: tuple[QuantumDevice, ...]

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> QuantumDeviceConfig:
        return cls(
            title=str(data["title"]),
            version=str(data["version"]),
            devices=tuple(QuantumDevice.from_mapping(device) for device in data["devices"]),
        )

    @property
    def active_devices(self) -> tuple[QuantumDevice, ...]:
        return tuple(device for device in self.devices if device.is_active)

    def validate(self) -> None:
        if not self.title:
            raise ValueError("quantum device configuration title must be defined.")
        if not self.version:
            raise ValueError("quantum device configuration version must be defined.")
        if not self.devices:
            raise ValueError("quantum device configuration must contain at least one device.")
        for device in self.devices:
            device.validate()
        if not self.active_devices:
            raise ValueError(
                "quantum device configuration must contain at least one active device."
            )

    def serialize(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "version": self.version,
            "devices": [device.serialize() for device in self.devices],
        }


def load_quantum_device_config(file: Path | str) -> QuantumDeviceConfig:
    config = QuantumDeviceConfig.from_mapping(read_file(Path(file)))
    config.validate()
    return config


def write_quantum_device_config(config: QuantumDeviceConfig, file: Path | str) -> None:
    config.validate()
    path = Path(file)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dump_quantum_device_config(config), encoding="utf-8")


def dump_quantum_device_config(config: QuantumDeviceConfig) -> str:
    config.validate()
    lines = [
        f"title = {_format_toml_value(config.title)}",
        f"version = {_format_toml_value(config.version)}",
    ]

    for device in config.devices:
        lines.extend(
            (
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
                f"qubit_topology = {_format_toml_value(device.specs.qubit_topology)}",
                "",
                "[devices.qll]",
                f"name = {_format_toml_value(device.qll.name)}",
                f"package_name = {_format_toml_value(device.qll.package_name)}",
                f"package_version = {_format_toml_value(device.qll.package_version)}",
                f"file_extension = {_format_toml_value(device.qll.file_extension)}",
            )
        )

        if device.extra:
            lines.extend(
                (
                    "",
                    "[devices.extra]",
                    *(
                        f"{key} = {_format_toml_value(value)}"
                        for key, value in sorted(device.extra.items())
                    ),
                )
            )

    return "\n".join(lines) + "\n"


def _format_toml_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return repr(value)
    if isinstance(value, int | float):
        return str(value)
    if isinstance(value, list | tuple):
        return "[" + ", ".join(_format_toml_value(item) for item in value) + "]"
    if isinstance(value, dict):
        items = (
            f"{_format_toml_key(str(key))} = {_format_toml_value(item)}"
            for key, item in sorted(value.items())
        )
        return "{ " + ", ".join(items) + " }"
    if value is None:
        raise TypeError("TOML does not support null values.")

    raise TypeError(f"cannot serialize value {value!r} as TOML.")


def _format_toml_key(key: str) -> str:
    if key.replace("_", "").replace("-", "").isalnum():
        return key
    return repr(key)


def _read_bool(value: Any, *, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{field_name} must be a boolean value.")
    return value


def _read_string_tuple(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value,)
    return tuple(str(item) for item in value)
