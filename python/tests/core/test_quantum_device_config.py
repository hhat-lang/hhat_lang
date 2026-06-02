from __future__ import annotations

from pathlib import Path

import pytest

from hhat_lang.core.config.quantum_device import (
    QuantumDevice,
    QuantumDeviceConfig,
    QuantumDeviceSpecs,
    QuantumLowLevelLanguage,
    dump_quantum_device_config,
    load_quantum_device_config,
    write_quantum_device_config,
)
from hhat_lang.core.config.utils import read_file


def _dummy_config() -> QuantumDeviceConfig:
    return QuantumDeviceConfig(
        title="H-hat Compiler Quantum Device Configuration",
        version="0.1.0",
        devices=(
            QuantumDevice(
                name="AerSimulator",
                is_active=True,
                vendor="IBM",
                device_kind="simulator",
                device_platform="superconducting",
                computation_paradigm=("gate",),
                specs=QuantumDeviceSpecs(
                    max_n_qubits=32,
                    qubit_topology={"kind": "all-to-all"},
                ),
                qll=QuantumLowLevelLanguage(
                    name="openqasm",
                    package_name="qiskit",
                    package_version="1.0",
                    file_extension="qasm",
                ),
                extra={"basis_gates": ["h", "cx", "rz"]},
            ),
            QuantumDevice(
                name="Tuna-17",
                is_active=False,
                vendor="QuTech",
                device_kind="device",
                device_platform="superconducting",
                computation_paradigm=("gate",),
                specs=QuantumDeviceSpecs(
                    max_n_qubits=17,
                    qubit_topology={"kind": "line", "size": 17},
                ),
                qll=QuantumLowLevelLanguage(
                    name="netqasm",
                    package_name="netqasm",
                    package_version="0.15",
                    file_extension=".nqasm",
                ),
            ),
        ),
    )


def test_write_and_load_quantum_device_config(tmp_path: Path) -> None:
    config_file = tmp_path / "quantum_config.toml"

    write_quantum_device_config(_dummy_config(), config_file)
    config = load_quantum_device_config(config_file)

    assert config.title == "H-hat Compiler Quantum Device Configuration"
    assert [device.name for device in config.devices] == ["AerSimulator", "Tuna-17"]
    assert [device.name for device in config.active_devices] == ["AerSimulator"]
    assert config.devices[0].specs.qubit_topology == {"kind": "all-to-all"}
    assert config.devices[1].qll.file_extension == "nqasm"


def test_dump_quantum_device_config_is_readable_toml(tmp_path: Path) -> None:
    config_file = tmp_path / "quantum_config.toml"
    config_file.write_text(dump_quantum_device_config(_dummy_config()), encoding="utf-8")

    data = read_file(config_file)

    assert data["title"] == "H-hat Compiler Quantum Device Configuration"
    assert data["devices"][0]["qll"]["name"] == "openqasm"
    assert data["devices"][0]["extra"]["basis_gates"] == ["h", "cx", "rz"]


def test_quantum_device_config_requires_active_device() -> None:
    inactive_device = QuantumDevice(
        name="InactiveSimulator",
        is_active=False,
        vendor="Test",
        device_kind="simulator",
        device_platform="superconducting",
        computation_paradigm=("gate",),
        specs=QuantumDeviceSpecs(max_n_qubits=1),
        qll=QuantumLowLevelLanguage(
            name="openqasm",
            package_name="qiskit",
            package_version="1.0",
            file_extension="qasm",
        ),
    )
    config = QuantumDeviceConfig(
        title="H-hat Compiler Quantum Device Configuration",
        version="0.1.0",
        devices=(inactive_device,),
    )

    with pytest.raises(ValueError, match="at least one active device"):
        config.validate()


def test_quantum_device_config_validates_device_kind() -> None:
    invalid_device = QuantumDevice(
        name="InvalidDevice",
        is_active=True,
        vendor="Test",
        device_kind="processor",
        device_platform="superconducting",
        computation_paradigm=("gate",),
        specs=QuantumDeviceSpecs(max_n_qubits=1),
        qll=QuantumLowLevelLanguage(
            name="openqasm",
            package_name="qiskit",
            package_version="1.0",
            file_extension="qasm",
        ),
    )
    config = QuantumDeviceConfig(
        title="H-hat Compiler Quantum Device Configuration",
        version="0.1.0",
        devices=(invalid_device,),
    )

    with pytest.raises(ValueError, match="'device' or 'simulator'"):
        config.validate()


def test_quantum_device_from_mapping_keeps_single_paradigm_string_intact() -> None:
    device = QuantumDevice.from_mapping(
        {
            "name": "AerSimulator",
            "is_active": True,
            "vendor": "IBM",
            "device_kind": "simulator",
            "device_platform": "superconducting",
            "computation_paradigm": "gate",
            "specs": {"max_n_qubits": 32},
            "qll": {
                "name": "openqasm",
                "package_name": "qiskit",
                "package_version": "1.0",
                "file_extension": "qasm",
            },
        }
    )

    assert device.computation_paradigm == ("gate",)


def test_quantum_device_from_mapping_rejects_non_boolean_active_flag() -> None:
    with pytest.raises(TypeError, match="is_active must be a boolean"):
        QuantumDevice.from_mapping(
            {
                "name": "AerSimulator",
                "is_active": "false",
                "vendor": "IBM",
                "device_kind": "simulator",
                "device_platform": "superconducting",
                "computation_paradigm": ["gate"],
                "specs": {"max_n_qubits": 32},
                "qll": {
                    "name": "openqasm",
                    "package_name": "qiskit",
                    "package_version": "1.0",
                    "file_extension": "qasm",
                },
            }
        )
