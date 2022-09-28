"""Protocols to define behavior of circuit upon operation with other types"""

from abc import ABC, abstractmethod

import pre_hhat.types as types
from pre_hhat.core.utils import is_hex, is_bin


class Protocols(ABC):
    name = ""

    @abstractmethod
    def __call__(self, *args, **kwargs):
        ...


class BiggestValue(Protocols):
    name = "biggest_value"

    def __call__(self, *args, **kwargs):
        raise NotImplementedError(f"{self.__class__.__name__}: not implemented yet.")


class WeightedAverage(Protocols):
    name = "weighted_average"

    def __call__(self, data, **kwargs):
        if isinstance(data, (types.SingleHashmap, types.ArrayHashmap)):
            res = []
            total = sum([v.value[0] for k, v in data])
            for k, v in data:
                k0 = k.value[0]
                res.append(int(k0, 16 if is_hex(k0) else 2) * v.value[0] / total)
            return sum(res)
        raise ValueError(f"{self.__class__.__name__}: cannot work with {data.__class__.__name__}.")


protocols_list = {BiggestValue.name: BiggestValue(), WeightedAverage.name: WeightedAverage()}
