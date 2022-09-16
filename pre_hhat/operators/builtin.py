"""Operators Base for all operations to be derived from"""

from abc import ABC, abstractmethod


class Operators(ABC):
    @abstractmethod
    def __call__(self, *args, **kwargs):
        ...
