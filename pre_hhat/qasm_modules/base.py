"""Base to provide common ground for all QASM and dummy QASM devices"""

from abc import ABC, abstractmethod


class BaseQASM(ABC):
    """
    class to provide base specification for QASM modules.
    """
    name = "base for QASM"

    @abstractmethod
    def run(self, *args, **kwargs):
        ...

    @abstractmethod
    def circuit_to_qasm(self, data, **kwargs):
        ...


class DummyDevice:
    """
    class provided to serve as a dummy template
    """
    def __init__(self, **kwargs):
        pass

    def run(self, *args, **kwargs):
        return self

    @staticmethod
    def result():
        from pre_hhat import execute_mode
        if execute_mode == "all":
            return dict(x0=1024)
        if execute_mode == "one":
            return dict(x0=1)
