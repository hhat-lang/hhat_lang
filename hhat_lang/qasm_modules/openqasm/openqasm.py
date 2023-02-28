"""OpenQASM devices"""

from qiskit.providers.aer import AerSimulator

from hhat_lang import num_shots
import hhat_lang.types as types
from hhat_lang.qasm_modules.openqasm.base import DummyDevice, OpenQasmBase


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
        result_items = tuple(device_run.result().items())
        return types.SingleHashmap(result_items)
