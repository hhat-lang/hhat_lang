"""Implement quantum operators"""

from abc import abstractmethod

from .builtin import Operators

from pre_hhat.types import groups as group


class QuantumOperator(Operators):
    @abstractmethod
    def __call__(self, *args, **kwargs):
        ...


class X(QuantumOperator):
    name = "@X"

    def __call__(self, *args, **kwargs):
        return tuple(group.MultipleIndexGate(*args, name=self.name))


class Z(QuantumOperator):
    name = "@Z"

    def __call__(self, *args, **kwargs):
        return tuple(group.MultipleIndexGate(*args, name=self.name))


class H(QuantumOperator):
    name = "@H"

    def __call__(self, *args, **kwargs):
        return tuple(group.MultipleIndexGate(*args, name=self.name))


class Cnot(QuantumOperator):
    name = "@CNOT"

    def __call__(self, *args, **kwargs):
        return tuple(group.ControlTargetGate(*args, name=self.name, ct=(1, 1)))


class Swap(QuantumOperator):
    name = "@SWAP"

    def __call__(self, *args, **kwargs):
        return tuple(group.ControlTargetGate(*args, name=self.name, ct=(1, 1)))


class Toffoli(QuantumOperator):
    name = "@TOFFOLI"

    def __call__(self, *args, **kwargs):
        return tuple(group.ControlTargetGate(*args, name=self.name, ct=(2, 1)))
