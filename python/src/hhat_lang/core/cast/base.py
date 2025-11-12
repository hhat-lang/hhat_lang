from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping, Protocol, runtime_checkable
from collections import Counter

from hhat_lang.core.code.ir_graph import IRNode, IRGraph
from hhat_lang.core.data.core import CoreLiteral
from hhat_lang.core.data.utils import isquantum
from hhat_lang.core.data.variable import BaseDataContainer
from hhat_lang.core.execution.abstract_program import QuantumProgram
from hhat_lang.core.memory.core import MemoryManager
from hhat_lang.core.types.abstract_base import BaseTypeDataStructure


def is_iterable(data: Any) -> bool:
    return True if hasattr(data, "__iter__") else False


def is_dict_like(data: Any) -> bool:
    return True if is_iterable(data) and hasattr(data, "__getitem__") else False


def is_result_obj(data: Any) -> bool:
    return True if hasattr(data, "data") and hasattr(data, "metadata") else False


def get_max_count(sample: BaseBitString) -> str:
    """Return the bitstring of the maximum count"""

    return Counter(sample.get_counts()).most_common(1)[0][0]


def get_min_count(sample: BaseBitString) -> str:
    """Return the bistring of the minimum count"""

    return Counter(sample.get_counts()).most_common()[-1][0]


def get_sample(sample: BaseBitString) -> BaseDataContainer:
    pass


@runtime_checkable
class ResultObj(Protocol):
    @property
    def data(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError()

    @property
    def metadata(self):
        raise NotImplementedError()


@runtime_checkable
class MappingLike(Protocol):
    def __getitem__(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError()

    def __iter__(self) -> Any:
        raise NotImplementedError()

    def shape(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError()


class BaseBitString(ABC):
    """
    Abstract class to define bit string instances regardless the backend platform
    so H-hat can handle the raw measurement results properly.
    """

    _sample: ResultObj | MappingLike | Mapping

    def __init__(self, data: ResultObj | MappingLike | Mapping, **config: Any):
        if isinstance(data, ResultObj | MappingLike | Mapping):
            self._sample = data
            self._config = config

        else:
            raise ValueError(
                "cast operation -> bit string result -> bit string class must be a "
                "result object, a mapping-like object or a dictionary object."
            )

    @property
    def config(self) -> dict:
        return self._config

    @abstractmethod
    def get_counts(self) -> dict:
        raise NotImplementedError()


class CastOperator(ABC):
    """Cast base class to handle the casting workflow"""

    _data: BaseDataContainer | CoreLiteral
    _to_type: BaseTypeDataStructure

    def __init__(
        self,
        data: BaseDataContainer | CoreLiteral,
        to_type: BaseTypeDataStructure,
    ):
        if (
            isinstance(data, BaseDataContainer | CoreLiteral)
            and isinstance(to_type, BaseTypeDataStructure)
        ):
            self._data = data
            self._to_type = to_type

        else:
            raise ValueError(
                f"data {data} must be BaseDataContainer or literal"
                f" and type must be BaseTypeDataStructure"
            )

    @abstractmethod
    def flush(self) -> CastOperator:
        """Use this method to execute the cast logic."""

        raise NotImplementedError()

    @abstractmethod
    def cast(self) -> CastOperator:
        """Use this method to perform the cast conversion."""

        raise NotImplementedError()

    @abstractmethod
    def get_cast_data(self) -> BaseDataContainer | CoreLiteral:
        """Retrieve the cast data with the correct type. Must be used after
        ``flush`` and ``cast`` methods."""

        raise NotImplementedError()


class CastC2C(CastOperator):
    """Class to handle classical data casting to classical type"""

    _mem: MemoryManager
    _node: IRNode
    _ir_graph: IRGraph

    def __init__(
        self,
        data: BaseDataContainer | CoreLiteral,
        to_type: BaseTypeDataStructure,
        mem: MemoryManager,
        node: IRNode,
        ir_graph: IRGraph
    ):
        if (
            isinstance(mem, MemoryManager)
            and isinstance(node, IRNode)
            and isinstance(ir_graph, IRGraph)
        ):
            super().__init__(data=data, to_type=to_type)
            self._mem = mem
            self._node = node
            self._ir_graph = ir_graph

    def flush(self) -> CastC2C:
        raise NotImplementedError()

    def get_cast_data(self) -> BaseDataContainer | CoreLiteral:
        pass


class CastQ2C(CastOperator):
    """Class to handle quantum data casting to classical type"""

    _program: QuantumProgram

    def __init__(
        self,
        data: BaseDataContainer | CoreLiteral,
        to_type: BaseTypeDataStructure,
        mem: MemoryManager,
        node: IRNode,
        ir_graph: IRGraph
    ):
        super().__init__(data=data, to_type=to_type)
        self._program = QuantumProgram(qdata=self._data, mem=mem, node=node, ir_graph=ir_graph)

    def flush(self) -> CastQ2C:
        self._program.run()
        return self

    def get_cast_data(self) -> BaseDataContainer | CoreLiteral:
        pass


class CastC2Q(CastOperator):
    """Class to handle classical data casting to quantum type"""

    def flush(self) -> CastC2Q:
        raise NotImplementedError()

    def get_cast_data(self) -> BaseDataContainer | CoreLiteral:
        pass


class CastQ2Q(CastOperator):
    """Class to handle quantum data casting to quantum type"""

    def flush(self) -> CastQ2Q:
        raise NotImplementedError()

    def get_cast_data(self) -> BaseDataContainer | CoreLiteral:
        pass
