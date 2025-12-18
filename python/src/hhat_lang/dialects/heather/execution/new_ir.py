from __future__ import annotations

from typing import Any

from hhat_lang.core.code.abstract import BaseIR, IRHash
from hhat_lang.core.code.ir_graph import IRGraph
from hhat_lang.core.data.core import CompositeSymbol, Symbol
from hhat_lang.core.execution.abstract_base import BaseIRManager
from hhat_lang.dialects.heather.code.simple_ir_builder.ir import IR


class IRManager(BaseIRManager):
    """Handle IR codes for Heather dialect through ``IRGraph`` instance"""

    def __init__(self):
        self._graph = IRGraph()

    def add_ir(self, ir: IR) -> None:
        """
        Add a single IR

        Args:
            ir: the ``IR`` instance to be added to the manager
        """

        self._graph.add_node(ir)

    def link_ir(
        self,
        *refs: Symbol | CompositeSymbol,
        ir_importing: BaseIR,
        ir_imported: BaseIR,
        **kwargs: Any,
    ) -> None:
        """
        Link two IRs, where one is the importer (importing IR) and the other is the imported IR.

        Args:
            *refs: list of symbols of types or functions from the ``ir_imported`` instance
            ir_importing: the ``IR`` instance that will import data from another ``IR`` instance
            ir_imported: the imported ``IR``, which contains the data to be imported
            **kwargs: Extra data if needed
        """

        importing = IRHash.get_key(ir_importing)
        imported = IRHash.get_key(ir_imported)
        self._graph.add_edge(*refs, node_key=importing, link_key=imported)

    def update_ir(self, prev_ir: IR, new_ir: IR) -> None:
        """
        Update a current ``IR`` instance for a new ``IR`` instance. It will replace the current
        one on the IR graph as well, from its node position to all the current's relationships.

        Args:
            prev_ir: (the current, or to be) previous ``IR`` instance
            new_ir: the new ``IR`` instance, to replace the current ``IR`` instance
        """

        prev_key = IRHash.get_key(prev_ir)
        self._graph.update_node(prev_key, new_ir)
