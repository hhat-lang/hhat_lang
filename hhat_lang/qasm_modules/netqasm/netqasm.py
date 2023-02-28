"""NetQASM devices"""

# TODO: include netqasm package, functionalities and features

from hhat_lang.types import ArrayCircuit
from hhat_lang.qasm_modules.netqasm.base import DummyDevice, NetQasmBase


class QuantumSimulator(NetQasmBase):
    """
    NetQASM language
    default version = 1.0

    class type = simulator

    """

    name = "NetQASM simulator"


class QuantumHardware(NetQasmBase):
    name = "NetQASM hardware"

    def __init__(self, **kwargs):
        self.version = "0.1"
        self.device = DummyDevice(**kwargs)

    def run(self, data: ArrayCircuit, **kwargs) -> dict:
        device_run = self.device.run(data, **kwargs)
        return device_run.result()
