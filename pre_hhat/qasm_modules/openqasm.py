"""OpenQASM devices"""

from qiskit.providers.aer import QasmSimulator
from base import BaseQASM, DummyDevice


class QuantumSimulator(BaseQASM):
    """
    OpenQASM simulator

    default version = 2.0
    """
    name = "OpenQASM simulator"

    def __init__(self, **kwargs):
        self.version = kwargs.pop('version') if 'version' in kwargs.keys() else '2.0'
        self.device = QasmSimulator(**kwargs)

    def run(self, *args, **kwargs):
        device_run = self.device.run(*args, **kwargs)
        return device_run.result()

    def circuit_to_qasm(self, data, **kwargs):
        pass


class QuantumHardware(BaseQASM):
    """
    OpenQASM hardware (dummy hardware)

    default version = dummy version
    """
    name = "OpenQASM hardware"

    def __init__(self, **kwargs):
        self.version = kwargs.pop('version') if 'version' in kwargs.keys() else '0.1'
        self.device = DummyDevice(**kwargs)

    def run(self, *args, **kwargs):
        device_run = self.device.run(*args, **kwargs)
        return device_run.result()

    def circuit_to_qasm(self, data, **kwargs):
        pass
