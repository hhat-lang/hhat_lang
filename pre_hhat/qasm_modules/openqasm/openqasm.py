"""OpenQASM devices"""

from qiskit.providers.aer import AerSimulator

from pre_hhat import num_shots
import pre_hhat.types as types
from pre_hhat.qasm_modules.openqasm.base import DummyDevice, OpenQasmBase


class QuantumSimulator(OpenQasmBase):
    """
    OpenQASM language
    default version = 2.0

    class type = simulator

    """

    name = "OpenQASM simulator"

    def __init__(self, **kwargs):
        self.version = kwargs.pop("version") if "version" in kwargs.keys() else "2.0"
        self.device = AerSimulator(**kwargs)

    def run(self, data, stack, **kwargs):
        circuit_qasm = self.circuit_to_qasm(data, stack)
        device_run = self.device.run(circuit_qasm, shots=num_shots, **kwargs)
        result = device_run.result().data()["counts"]
        return types.SingleHashmap(tuple(result.items()))


class QuantumHardware(OpenQasmBase):
    """
    OpenQASM hardware (dummy hardware)

    default version = dummy version
    """

    name = "OpenQASM hardware"

    def __init__(self, **kwargs):
        self.version = kwargs.pop("version") if "version" in kwargs.keys() else "0.1"
        self.device = DummyDevice(**kwargs)

    def run(self, data, **kwargs):
        device_run = self.device.run(data, **kwargs)
        return types.SingleHashmap(tuple(device_run.result().items()))
