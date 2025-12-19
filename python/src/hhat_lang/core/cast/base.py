from __future__ import annotations

from abc import ABC, abstractmethod
from collections import Counter
from typing import Any, Callable, Mapping, Protocol, runtime_checkable

from hhat_lang.core.code.ir_graph import IRGraph, IRNode
from hhat_lang.core.data.core import Literal
from hhat_lang.core.data.var_def import DataDef
from hhat_lang.core.error_handlers.errors import InterpreterEvaluationError
from hhat_lang.core.execution.abstract_program import QuantumProgram
from hhat_lang.core.memory.core import MemoryManager
from hhat_lang.core.types.abstract_base import BaseTypeDef

CastFnType = Callable[[DataDef | Literal | Any], Literal]
"""cast function type annotation"""


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


def get_sample(sample: BaseBitString) -> DataDef:
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


class BaseCastOperator(ABC):
    """Cast base class to handle the casting workflow"""

    _data: DataDef | Literal
    _to_type: BaseTypeDef
    _cast_fn: CastFnType

    def __init__(
        self,
        data: DataDef | Literal,
        to_type: BaseTypeDef,
        cast_fn: CastFnType,
    ):
        if (
            isinstance(data, DataDef | Literal)
            and isinstance(to_type, BaseTypeDef)
            and isinstance(cast_fn, Callable)
        ):
            self._data = data
            self._to_type = to_type
            self._cast_fn = cast_fn

        else:
            raise InterpreterEvaluationError(
                error_where="cast operator instantiation",
                msg=f"data {data} must be DataDef or literal, "
                f"type must be BaseTypeDataStructure and cast function"
                f" a callable.",
            )

    @abstractmethod
    def flush(self) -> BaseCastOperator:
        """Use this method to execute the cast logic."""

        raise NotImplementedError()

    @abstractmethod
    def cast(self) -> BaseCastOperator:
        """Use this method to perform the cast conversion."""

        raise NotImplementedError()

    @abstractmethod
    def retrieve_cast_data(self) -> DataDef | Literal:
        """
        Retrieve the cast data with the correct type. Must be used after
        ``flush`` and ``cast`` methods.
        """

        raise NotImplementedError()


class BaseCastC2C(BaseCastOperator):
    """Class to handle classical data casting to classical type"""

    _mem: MemoryManager
    _node: IRNode
    _ir_graph: IRGraph

    def __init__(
        self,
        data: DataDef | Literal,
        to_type: BaseTypeDef,
        cast_fn: CastFnType,
        mem: MemoryManager,
        node: IRNode,
        ir_graph: IRGraph,
    ):
        if (
            isinstance(mem, MemoryManager)
            and isinstance(node, IRNode)
            and isinstance(ir_graph, IRGraph)
        ):
            super().__init__(data=data, to_type=to_type, cast_fn=cast_fn)
            self._mem = mem
            self._node = node
            self._ir_graph = ir_graph

    def flush(self) -> BaseCastC2C:
        raise NotImplementedError()

    @abstractmethod
    def cast(self) -> BaseCastC2C:
        raise NotImplementedError()

    def retrieve_cast_data(self) -> DataDef | Literal:
        pass


class BaseCastQ2C(BaseCastOperator):
    """Class to handle quantum data casting to classical type"""

    _program: QuantumProgram

    def __init__(
        self,
        data: DataDef | Literal,
        to_type: BaseTypeDef,
        cast_fn: CastFnType,
        mem: MemoryManager,
        node: IRNode,
        ir_graph: IRGraph,
    ):
        super().__init__(data=data, to_type=to_type, cast_fn=cast_fn)
        self._program = QuantumProgram(
            qdata=self._data,
            mem=mem,
            node=node,
            ir_graph=ir_graph,
            base_llq=None,
            executor=None,
        )

    def flush(self) -> BaseCastQ2C:
        self._program.run()
        return self

    @abstractmethod
    def cast(self) -> BaseCastQ2C:
        raise NotImplementedError()

    def retrieve_cast_data(self) -> DataDef | Literal:
        return self._cast_fn(self._data)


class BaseCastC2Q(BaseCastOperator):
    """Class to handle classical data casting to quantum type"""

    def flush(self) -> BaseCastC2Q:
        raise NotImplementedError()

    @abstractmethod
    def cast(self) -> BaseCastC2Q:
        raise NotImplementedError()

    def retrieve_cast_data(self) -> DataDef | Literal:
        raise NotImplementedError()


class BaseCastQ2Q(BaseCastOperator):
    """Class to handle quantum data casting to quantum type"""

    def flush(self) -> BaseCastQ2Q:
        raise NotImplementedError()

    @abstractmethod
    def cast(self) -> BaseCastQ2Q:
        raise NotImplementedError()

    def retrieve_cast_data(self) -> DataDef | Literal:
        raise NotImplementedError()
