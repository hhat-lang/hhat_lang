from __future__ import annotations

from hhat_lang.core.cast.base import (
    BaseCastC2C,
    BaseCastQ2C,
    BaseCastQ2Q,
    BaseCastC2Q,
    CastFnType,
)
from hhat_lang.core.code.ir_graph import IRNode, IRGraph
from hhat_lang.core.data.core import Literal
from hhat_lang.core.data.var_def import DataDef
from hhat_lang.core.memory.core import MemoryManager
from hhat_lang.core.types.abstract_base import BaseTypeDef
from hhat_lang.dialects.heather.cast.conversion_protocols.builtin_fns import (
    cast_fns_dict,
)


class CastC2C(BaseCastC2C):
    def __int__(
        self,
        data: DataDef | Literal,
        to_type: BaseTypeDef,
        mem: MemoryManager,
        node: IRNode,
        ir_graph: IRGraph,
    ):
        d_type: str = data.type.value if isinstance(data, DataDef) else data.type
        cast_fn: CastFnType = cast_fns_dict[(d_type, to_type.name.value)]

        super().__init__(
            data=data,
            to_type=to_type,
            cast_fn=cast_fn,
            mem=mem,
            node=node,
            ir_graph=ir_graph,
        )

    def cast(self) -> CastC2C:
        # TODO: implement it

        return self


class CastQ2C(BaseCastQ2C):
    def __int__(
        self,
        data: DataDef | Literal,
        to_type: BaseTypeDef,
        mem: MemoryManager,
        node: IRNode,
        ir_graph: IRGraph,
    ):
        """
        Class to cast from quantum data to classical type.

        Args:
            data: variable (``DataBaseContainer``) or literal (``CoreLiteral``)
            to_type: the actual type (``BaseTypeDataStructure``) you want to cast to
            mem: the memory manager (``MemoryManager``) the current scope/program is using
            node: the node (``IRNode``) where the program is located
            ir_graph: the program's ir graph (``IRGraph``)
        """

        d_type: str = data.type.value if isinstance(data, DataDef) else data.type
        cast_fn: CastFnType = cast_fns_dict[(d_type, to_type.name.value)]

        super().__init__(
            data=data,
            to_type=to_type,
            cast_fn=cast_fn,
            mem=mem,
            node=node,
            ir_graph=ir_graph,
        )

    def cast(self) -> CastQ2C:
        # TODO: implement it

        return self


class CastQ2Q(BaseCastQ2Q):
    def __init__(
        self,
        data: DataDef | Literal,
        to_type: BaseTypeDef,
        mem: MemoryManager,
        node: IRNode,
        ir_graph: IRGraph,
    ):
        d_type: str = data.type.value if isinstance(data, DataDef) else data.type
        cast_fn: CastFnType = cast_fns_dict[(d_type, to_type.name.value)]

        super().__init__(
            data=data,
            to_type=to_type,
            cast_fn=cast_fn,
            # mem=mem,
            # node=node,
            # ir_graph=ir_graph
        )

    def cast(self) -> BaseCastQ2Q:
        return self


class CastC2Q(BaseCastC2Q):
    def __init__(
        self,
        data: DataDef | Literal,
        to_type: BaseTypeDef,
        mem: MemoryManager,
        node: IRNode,
        ir_graph: IRGraph,
    ):
        d_type: str = data.type.value if isinstance(data, DataDef) else data.type
        cast_fn: CastFnType = cast_fns_dict[(d_type, to_type.name.value)]
        super().__init__(data=data, to_type=to_type, cast_fn=cast_fn)

    def cast(self) -> BaseCastC2Q:
        return self
