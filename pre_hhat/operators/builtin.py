"""Operators Base for all operations to be derived from"""

from abc import ABC, abstractmethod

from pre_hhat import execute_mode, num_shots
import pre_hhat.types as types


class Operators(ABC):
    @abstractmethod
    def __call__(self, *args, **kwargs):
        ...


class Collector:
    mode = execute_mode
    shots = num_shots

    def __init__(self, code):
        self.code = code
        self.data = []

    def _collect_one(self):
        res = dict()
        for k in range(self.shots):
            pass

    def _collect_all(self):
        pass

    def __iter__(self):
        yield from self.code

    def __call__(self, stack=None, *args, **kwargs):
        if stack is not None:
            if self.mode == "one":
                self._collect_one()
                return ()
            elif self.mode == "all":
                self._collect_all()
                return ()
            else:
                raise ValueError(f"{self.__class__.__name__}: execute mode must be 'one' or 'all'.")
        raise ValueError(f"{self.__class__.__name__}: needs a stack from Evaluator.")
