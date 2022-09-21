"""Protocols to define behavior of circuit upon operation with other types"""

from abc import ABC, abstractmethod


class Protocols(ABC):
    name = ""

    @abstractmethod
    def __call__(self, *args, **kwargs):
        ...


class BiggestValue(Protocols):
    name = "biggest_value"

    def __call__(self, *args, **kwargs):
        pass


class WeightedAverage(Protocols):
    name = "weighted_average"

    def __call__(self, *args, **kwargs):
        pass


protocols_list = {BiggestValue.name: BiggestValue(), WeightedAverage.name: WeightedAverage()}
