from __future__ import annotations

from typing import Any

from hhat_lang.core.code.base import BaseBuiltinInstr
from hhat_lang.core.code.new_ir import IRNode, IRGraph
from hhat_lang.core.data.core import Symbol, CompositeSymbol
from hhat_lang.core.memory.core import MemoryManager


class BuiltinInstr(BaseBuiltinInstr):
    def resolve(
        self,
        mem: MemoryManager,
        node: IRNode,
        ir_graph: IRGraph,
        name: Symbol | CompositeSymbol,
        **kwargs: Any
    ) -> Any:
        """

        Args:
            mem: ``MemoryManager`` instance
            node: ``IRNode`` instance
            ir_graph: ``IRGraph`` instance
            name: name of the built-in function as ``Symbol`` or ``CompositeSymbol``
            **kwargs: extra arguments for the function to work

        Returns:
            Whatever the built-in function should return
        """

    def __repr__(self) -> str:
        return f"{self._name}({' '.join(str(k) for k in self.args)})"
