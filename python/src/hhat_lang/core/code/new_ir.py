from __future__ import annotations

from pathlib import Path
from typing import Any, Iterator, Mapping

from hhat_lang.core.code.abstract import BaseIR, IRHash, RefTable
from hhat_lang.core.code.base import BaseFnCheck
from hhat_lang.core.code.utils import ResultPHF, gen_phf, get_hash
from hhat_lang.core.data.core import (
    CompositeSymbol,
    Symbol,
)
from hhat_lang.core.data.fn_def import FnDef
from hhat_lang.core.types.abstract_base import BaseTypeDataStructure


####################
# IR GRAPH CLASSES #
####################

class IRNode:
    """
    Stores node key as ``IRHash`` and value as ``BaseIRModule`` child instance.

    Use ``key`` attribute to retrieve its ``IRHash`` value, when checking a type
    or function. Use ``uid`` attribute to retrieve the hash value from its internal
    ``IRModule`` instance, when comparing between ``IRNode``.
    """

    _uid: int
    _irhash: IRHash
    _ir: BaseIR
    _path: Path
    __slots__ = ("_irhash", "_ir", "_uid", "_path")

    def __init__(self, node: BaseIR):
        self._uid = node.module.uid
        self._path = node.module.path
        self._irhash = IRHash(self._path)
        self._ir = node

    @property
    def irhash(self) -> IRHash:
        return self._irhash

    @property
    def ir(self) -> BaseIR:
        return self._ir

    @property
    def uid(self) -> int:
        return self._uid

    @property
    def path(self) -> Path:
        return self._path

    def __hash__(self) -> int:
        return self._uid

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, IRHash | IRNode):
            return hash(self) == hash(other)

        return False

    def __contains__(
        self, item: Symbol | CompositeSymbol | BaseFnCheck | Path | Any
    ) -> bool:
        return item in self._ir.module or item == self._path

    def __repr__(self) -> str:
        return f"Node({self.irhash})"


class NodeSet:
    """
    Efficiently store ``IRNode`` elements together with the perfect hash function (PHF)
    ``ResultPHF`` instance.
    """

    _data: tuple[IRNode, ...] | tuple
    _phf: ResultPHF | None

    def __init__(self, *data: IRNode, phf: ResultPHF | None = None):
        if (
            all(isinstance(k, IRNode) for k in data)
            and isinstance(phf, ResultPHF)
            or phf is None
        ):
            self._data = data
            self._phf = phf

        else:
            raise ValueError("node set accepts only IRNode instances")

    @property
    def phf(self) -> ResultPHF:
        if self._phf is not None:
            return self._phf

        raise ValueError("node's phf instance is null")

    @classmethod
    def new_set(cls, *data: IRNode, phf: ResultPHF) -> NodeSet:
        return cls(*data, phf=phf)

    def __contains__(
        self,
        item: (
            IRHash | IRNode | Path | tuple[Path, Symbol | CompositeSymbol | BaseFnCheck]
        ),
    ) -> bool:
        match item:
            case IRNode():
                return item in self._data

            case IRHash():
                for node in self._data:
                    if item == node.irhash:
                        return True

            case Path():
                for node in self._data:
                    if item == node.path:
                        return True

            case tuple():
                for node in self._data:
                    _path = item[0]
                    _symbol = item[1]

                    if _path == node.path and _symbol in node.ir.module:
                        return True

        return False

    def __getitem__(self, item: IRHash | int) -> IRNode | None:
        if isinstance(item, IRHash):
            if self._phf is not None:
                res = get_hash(hash(item), self.phf)

                if res is not None:
                    return self._data[res]

            raise ValueError(
                "node set must have phf attribute defined and item hash mush not be null"
            )

        # assuming it is integer
        return self._data[item]

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[IRNode]:
        return iter(self._data)


class IRGraph:
    """
    Graph to hold IR instances as nodes and their relationship as edges. The relationship
    (stored in ``RefTable``) happens when a type or function is imported from another IR
    module.
    """

    _is_built: bool
    _nodes: NodeSet
    _tmp_nodes: tuple[IRNode, ...] | tuple
    _main_node: IRHash

    def __init__(self):
        self._is_built = False
        self._nodes = NodeSet()
        self._tmp_nodes = ()

    @property
    def nodes(self) -> NodeSet:
        """Last node in a program will always be its 'main' file."""
        return self._nodes

    @property
    def main_node(self) -> IRHash:
        return self._main_node

    @property
    def is_built(self) -> bool:
        return self._is_built

    def add_node(self, ir: BaseIR) -> IRHash:
        """Add an IR to the graph node."""

        node = IRNode(ir)
        self._tmp_nodes += (node,)
        return node.irhash

    def add_main_node(self, ir: BaseIR) -> IRHash:
        """Add main IR to the graph node."""
        self._main_node = self.add_node(ir)
        return self._main_node

    def _check_refs(self) -> bool:
        """
        Check references inside the node set so there are no missing IRs to build the ir graph.
        """

        for node in self._nodes:
            for _, irhash in node.ir.ref_table.types:
                if irhash not in self._nodes:
                    return False

            for _, irhash in node.ir.ref_table.fns:
                if irhash not in self._nodes:
                    return False

        return True

    def build(self) -> None:
        """Build IR graph for performance and optimization purposes."""

        if not self._is_built and len(self._tmp_nodes) > 0:
            node_res, node_phf = gen_phf(self._tmp_nodes)
            self._nodes = NodeSet.new_set(*node_res, phf=node_phf)  # type: ignore [arg-type]
            self._tmp_nodes = ()

            if self._check_refs():
                self._is_built = True

            else:
                raise ValueError("missing nodes to build the ir graph")

        else:
            raise ValueError(
                f"ir graph is already built ({self._is_built}) or no nodes were found"
                f" (total nodes: {len(self._tmp_nodes)})."
            )

    def update(self, cur_node_key: IRHash, new_node: BaseIR) -> None:
        """
        TODO: implement it

        Update to a new node (IR module) from a given current node key (``IRHash``)

        Args:
            cur_node_key:
            new_node:
        """

        raise NotImplementedError()

    def get_fns(self, module_path: Path, item: Symbol) -> tuple[BaseFnCheck, ...]:
        for tmp_node in self._tmp_nodes:
            if module_path == tmp_node.path and item in tmp_node.ir.module:
                fns = tmp_node.ir.module.symbol_table.fn.get(item)

                if isinstance(fns, dict):
                    return tuple(fn for fn in fns)

        raise ValueError(f"item {item} not found in ir node at {module_path}")

    def __contains__(self, item: Any) -> bool:
        if isinstance(item, Symbol | BaseFnCheck):

            for tmp_node in self._tmp_nodes:
                if item in tmp_node:
                    return True

        if isinstance(item, Path):
            for tmp_node in self._tmp_nodes:
                if item in tmp_node:
                    return True

        return False

    def __repr__(self) -> str:
        max_n = str(len(self.nodes))
        txt = "".join(
            f"\nN#{'0'*(len(max_n) - len(str(n)))}{n}{k.ir}"
            for n, k in enumerate(self.nodes)
        )
        return f"==============\n=*=IR GRAPH=*=\n==============\n{txt}\n"


####################################
# BUILDING REFERENCE TABLE SECTION #
####################################


def build_reftable(
    types: Mapping[Symbol | CompositeSymbol, Path] | None = None,
    fns: Mapping[BaseFnCheck, Path] | None = None,
) -> RefTable:
    types = types or dict()
    fns = fns or dict()
    ref_table = RefTable()

    for type_name, ir_ref in types.items():
        ref_table.types.add_ref(type_name, ir_ref)

    for f_name, ir_ref in fns.items():
        ref_table.fns.add_ref(f_name, ir_ref)

    return ref_table


################################
# RETRIEVING FUNCTIONS SECTION #
################################


def get_type(
    node_key: IRHash, importing: Symbol | CompositeSymbol, ir_graph: IRGraph
) -> BaseTypeDataStructure | None:
    """
    Import a type ``importing`` from an IR module's hash value ``node_key``. Return
    the type instance or ``None`` if not found.
    """

    node: IRNode | None = ir_graph.nodes[node_key]

    if node is not None:
        return node.ir.module.symbol_table.type.get(importing)

    return None


def get_fn(
    node_key: IRHash, importing: BaseFnCheck, ir_graph: IRGraph
) -> FnDef | dict[BaseFnCheck, FnDef] | None:
    """
    Import a function check instance ``importing`` from an IR module's hash value ``node_key``.

    Args:
        node_key: the ``IRHash`` instance
        importing: the function ``BaseFnCheck`` instance
        ir_graph: the program's ``IRGraph``

    Returns:
        A ``FnDef`` instance or ``None``, if no function is found.
    """

    node: IRNode | None = ir_graph.nodes[node_key]

    if node is not None:
        return node.ir.module.symbol_table.fn.get(importing)

    return None
