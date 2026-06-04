from __future__ import annotations

import pytest

from hhat_lang.core.config.quantum_device import (
    QuantumDevice,
    QuantumDeviceConfig,
    QuantumDeviceSpecs,
    QuantumLowLevelLanguage,
    load_quantum_config,
    write_quantum_config,
)
from hhat_lang.core.config.utils import read_file


def _device(
    name: str,
    vendor: str,
    platform: str,
    qll_name: str,
    active: bool = False,
    max_n_qubits: int = 32,
) -> QuantumDevice:
    return QuantumDevice(
        name=name,
        is_active=active,
        vendor=vendor,
        device_kind="simulator" if active else "device",
        device_platform=platform,
        computation_paradigm=("gate",),
        specs=QuantumDeviceSpecs(
            max_n_qubits=max_n_qubits,
            qubit_topology={"kind": "line", "size": max_n_qubits},
        ),
        qll=QuantumLowLevelLanguage(
            name=qll_name,
            package_name=f"hhat-{qll_name}",
            package_version="0.1.0",
            file_extension="qasm" if qll_name == "openqasm" else "nqasm",
        ),
        extra={"source": vendor.lower().replace(" ", "-")},
    )


def test_quantum_device_config_round_trips_toml(tmp_path):
    config_path = tmp_path / "quantum_config.toml"
    config = QuantumDeviceConfig(
        title="H-hat Compiler Quantum Device Configuration",
        version="0.1.0",
        devices=(
            _device("AerSimulator", "Qiskit", "superconducting", "openqasm", active=True),
            _device("default.qubit", "PennyLane", "simulator", "openqasm"),
            _device("H-Series", "Quantinuum", "trapped ions", "openqasm", max_n_qubits=20),
            _device("Starmon-5", "Quantum Inspire", "superconducting", "openqasm", max_n_qubits=5),
            _device("Aquila", "QuEra", "neutral atoms", "openqasm", max_n_qubits=256),
        ),
    )

    write_quantum_config(config, config_path)
    loaded = load_quantum_config(config_path)

    assert loaded == config
    assert [device.name for device in loaded.active_devices] == ["AerSimulator"]
    assert read_file(config_path)["devices"][0]["specs"]["max_n_qubits"] == 32


def test_quantum_device_config_requires_an_active_device(tmp_path):
    config_path = tmp_path / "quantum_config.toml"
    config = QuantumDeviceConfig(
        title="H-hat Compiler Quantum Device Configuration",
        version="0.1.0",
        devices=(_device("inactive-aer", "Qiskit", "superconducting", "openqasm"),),
    )

    with pytest.raises(ValueError, match="at least one active device"):
        write_quantum_config(config, config_path)


def test_quantum_device_config_rejects_invalid_device_kind():
    raw_config = {
        "title": "H-hat Compiler Quantum Device Configuration",
        "version": "0.1.0",
        "devices": [
            {
                "name": "broken",
                "is_active": True,
                "vendor": "Example",
                "device_kind": "backend",
                "device_platform": "simulator",
                "computation_paradigm": ["gate"],
                "specs": {"max_n_qubits": 4},
                "qll": {
                    "name": "openqasm",
                    "package_name": "hhat-openqasm",
                    "package_version": "0.1.0",
                    "file_extension": "qasm",
                },
            }
        ],
    }

    with pytest.raises(ValueError, match="device_kind"):
        QuantumDeviceConfig.from_dict(raw_config)
