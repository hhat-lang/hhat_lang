from __future__ import annotations

import tomllib

import pytest

from hhat_lang.core.config.quantum_device import (
    QuantumDevice,
    QuantumDeviceConfiguration,
    QuantumDeviceSpecs,
    QuantumLowLevelLanguage,
    read_quantum_device_config,
    write_quantum_device_config,
)
from hhat_lang.core.config.utils import read_file


def _dummy_device(
    name: str,
    *,
    active: bool,
    vendor: str,
    kind: str,
    platform: str,
    paradigms: tuple[str, ...],
    qubits: int,
    qll_name: str,
    package_name: str,
    extension: str,
) -> QuantumDevice:
    return QuantumDevice(
        name=name,
        is_active=active,
        vendor=vendor,
        device_kind=kind,
        device_platform=platform,
        computation_paradigm=paradigms,
        specs=QuantumDeviceSpecs(
            max_n_qubits=qubits,
            qubit_topology={"kind": "line", "couplings": [[0, 1], [1, 2]]},
        ),
        qll=QuantumLowLevelLanguage(
            name=qll_name,
            package_name=package_name,
            package_version="0.1.0",
            file_extension=extension,
        ),
        extra={"region": "test", "notes": f"{vendor} dummy device"},
    )


def _dummy_config() -> QuantumDeviceConfiguration:
    return QuantumDeviceConfiguration(
        devices=(
            _dummy_device(
                "AerSimulator",
                active=True,
                vendor="Qiskit",
                kind="simulator",
                platform="superconducting",
                paradigms=("gate",),
                qubits=32,
                qll_name="openqasm",
                package_name="hhat_lang.low_level.quantum_lang.openqasm.v2",
                extension="qasm",
            ),
            _dummy_device(
                "default.qubit",
                active=True,
                vendor="PennyLane",
                kind="simulator",
                platform="state-vector",
                paradigms=("gate",),
                qubits=20,
                qll_name="openqasm",
                package_name="hhat_lang.low_level.quantum_lang.openqasm.v2",
                extension="qasm",
            ),
            _dummy_device(
                "H1-1",
                active=False,
                vendor="Quantinuum",
                kind="device",
                platform="trapped ions",
                paradigms=("gate",),
                qubits=20,
                qll_name="openqasm",
                package_name="hhat_lang.low_level.quantum_lang.openqasm.v2",
                extension="qasm",
            ),
            _dummy_device(
                "Starmon-5",
                active=False,
                vendor="Quantum Inspire",
                kind="device",
                platform="superconducting",
                paradigms=("gate",),
                qubits=5,
                qll_name="openqasm",
                package_name="hhat_lang.low_level.quantum_lang.openqasm.v2",
                extension="qasm",
            ),
            _dummy_device(
                "Aquila",
                active=False,
                vendor="QuEra",
                kind="device",
                platform="neutral atoms",
                paradigms=("analog",),
                qubits=256,
                qll_name="bloqade",
                package_name="hhat_lang.low_level.quantum_lang.bloqade",
                extension="json",
            ),
        )
    )


def test_write_and_read_quantum_device_config(tmp_path):
    path = tmp_path / "quantum_config.toml"

    write_quantum_device_config(_dummy_config(), path)
    raw = tomllib.loads(path.read_text(encoding="utf-8"))

    assert raw["title"] == "H-hat Compiler Quantum Device Configuration"
    assert raw["available"]["active_devices"] == ["AerSimulator", "default.qubit"]
    assert len(raw["devices"]) == 5

    loaded = read_quantum_device_config(path)

    assert [device.name for device in loaded.active_devices] == ["AerSimulator", "default.qubit"]
    assert loaded.devices[0].specs.qubit_topology["couplings"] == [[0, 1], [1, 2]]
    assert loaded.devices[-1].qll.package_name == "hhat_lang.low_level.quantum_lang.bloqade"
    assert read_file(str(path))["available"]["active_devices"] == ["AerSimulator", "default.qubit"]


def test_read_manually_written_quantum_device_config(tmp_path):
    path = tmp_path / "quantum_config.toml"
    path.write_text(
        """
title = "H-hat Compiler Quantum Device Configuration"
version = "0.1.0"

[[devices]]
name = "Tuna-17"
is_active = true
vendor = "QuTech"
device_kind = "device"
device_platform = "superconducting"
computation_paradigm = ["gate"]

[devices.specs]
max_n_qubits = 17
qubit_topology = { kind = "grid", rows = 4, columns = 5 }

[devices.qll]
name = "openqasm"
package_name = "hhat_lang.low_level.quantum_lang.openqasm.v2"
package_version = "2.0"
file_extension = "qasm"

[devices.extra]
calibration = "manual"
""",
        encoding="utf-8",
    )

    config = read_quantum_device_config(path)

    assert config.active_devices[0].name == "Tuna-17"
    assert config.devices[0].specs.qubit_topology["kind"] == "grid"
    assert config.devices[0].extra["calibration"] == "manual"


def test_quantum_device_config_requires_active_device():
    config = QuantumDeviceConfiguration(
        devices=(
            _dummy_device(
                "inactive-sim",
                active=False,
                vendor="Qiskit",
                kind="simulator",
                platform="state-vector",
                paradigms=("gate",),
                qubits=8,
                qll_name="openqasm",
                package_name="hhat_lang.low_level.quantum_lang.openqasm.v2",
                extension="qasm",
            ),
        )
    )

    with pytest.raises(ValueError, match="at least one active device"):
        write_quantum_device_config(config)
