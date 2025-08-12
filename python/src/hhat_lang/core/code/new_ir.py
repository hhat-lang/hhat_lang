from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Iterator, Hashable

from hhat_lang.core.code.abstract_new_ir import BaseIRBlock
from hhat_lang.core.code.symbol_table import SymbolTable
from hhat_lang.core.code.utils import ResultPHF, get_hash, gen_phf
from hhat_lang.core.data.core import (
    WorkingData,
    CompositeWorkingData,
    Symbol,
    CompositeSymbol,
)
from hhat_lang.core.data.fn_def import BaseFnCheck, FnDef
from hhat_lang.core.types.abstract_base import BaseTypeDataStructure


##############
# IR SECTION #
##############

class BaseIRModule(ABC):
    """Base abstract class for IR module definitions."""

    _path: Path
    _symbol_table: SymbolTable
    _main: BaseIRBlock

    @property
    def path(self) -> Path:
        return self._path

    @property
    def uid(self) -> int:
        return hash(self._path)

    @property
    def symbol_table(self) -> SymbolTable:
        return self._symbol_table

    @property
    def main(self) -> BaseIRBlock:
        return self._main

    def __hash__(self) -> int:
        return hash((hash(self._path), hash(self._symbol_table), hash(self._main)))

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return hash(self) == hash(other)

        return False

    def __contains__(self, item: Symbol | CompositeSymbol | BaseFnCheck) -> bool:
        return item in self._symbol_table.type or item in self._symbol_table.fn

    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError()


class BaseIR(ABC):
    """
    Base class for the IR.

    IR holds information about the main code execution (as an IR block), or a symbol
    table containing type definitions or function definitions, and a reference table
    to point the definitions of types or functions from other IRs.
    """

    _ref_table: RefTable
    _module: BaseIRModule

    @property
    def module(self) -> BaseIRModule:
        return self._module

    @property
    def ref_table(self) -> RefTable:
        return self._ref_table

    @abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError()


class BaseIRFlag(ABC, Enum):
    """
    Base for IR flag classes. It should be used to create enums for instructions,
    such as ``CALL``, ``DECLARE``, ``ASSIGN``, ``RETURN``, etc.
    """


class BaseIRInstr(ABC):
    """
    Base IR instruction classes.
    """

    _name: BaseIRFlag
    args: tuple[BaseIR | WorkingData | CompositeWorkingData, ...] | tuple
    _hash_value: int

    def __init__(self):
        self._hash_value = hash((hash(self.name), hash(self.args)))

    @property
    def name(self) -> Any:
        return self._name

    @abstractmethod
    def resolve(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError()

    def __hash__(self) -> int:
        return self._hash_value

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, BaseIRInstr):
            return hash(self) == hash(other)

        return False

    def __iter__(self) -> Iterable[BaseIR | WorkingData | CompositeWorkingData]:
        return iter(self.args)

    @abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError()


###########################
# REFERENCE TABLE CLASSES #
###########################

class RefTypeTable:
    """Reference to types from another IR"""

    _table: dict[Symbol | CompositeSymbol, IRHash]
    __slots__ = ("_table",)

    def __init__(self):
        self._table = dict()

    def add_ref(self, type_name: Symbol | CompositeSymbol, ir_path: Path) -> None:
        if isinstance(type_name, Symbol | CompositeSymbol) and isinstance(ir_path, Path):
            self._table[type_name] = IRHash(ir_path)

        else:
            raise ValueError(f"wrong reference type table input ({type_name})")

    def get_irpath(self, type_name: Symbol | CompositeSymbol) -> Path:
        return self.get_irhash(type_name).key

    def get_irhash(self, type_name: Symbol | CompositeSymbol) -> IRHash:
        return self._table[type_name]

    def __hash__(self) -> int:
        return hash(self._table)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, RefTypeTable):
            return hash(self) == hash(other)

        return False

    def __contains__(self, item: Symbol | CompositeSymbol) -> bool:
        return item in self._table

    def __len__(self) -> int:
        return len(self._table)

    def __iter__(self) -> Iterable[tuple[Symbol | CompositeSymbol, IRHash]]:
        return iter(self._table.items())


class RefFnTable:
    """Reference to functions from another IR"""

    _table: dict[BaseFnCheck, IRHash]
    __slots__ = ("_table",)

    def __init__(self):
        self._table = dict()

    def add_ref(self, fn_name: BaseFnCheck, ir_path: Path) -> None:
        if isinstance(fn_name, BaseFnCheck) and isinstance(ir_path, Path):
            self._table[fn_name] = IRHash(ir_path)

        else:
            raise ValueError(f"wrong reference type table input ({fn_name})")

    def get_irpath(self, fn_name: BaseFnCheck) -> Path:
        return self.get_irhash(fn_name).key

    def get_irhash(self, fn_name: BaseFnCheck) -> IRHash:
        return self._table[fn_name]

    def __hash__(self) -> int:
        return hash(self._table)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, RefFnTable):
            return hash(self) == hash(other)

        return False

    def __contains__(self, item: Symbol | CompositeSymbol | BaseFnCheck) -> bool:
        match item:
            case BaseFnCheck():
                return item in self._table

            case Symbol() | CompositeSymbol():
                for k in self._table:
                    if item == k.name:
                        return True

                return False

            case _:
                return False

    def __len__(self) -> int:
        return len(self._table)

    def __iter__(self) -> Iterable[tuple[BaseFnCheck, IRHash]]:
        return iter(self._table.items())


class RefTable:
    """To store reference for types and functions from another IR"""

    _types: RefTypeTable
    _fns: RefFnTable
    __slots__ = ("_types", "_fns")

    def __init__(
        self, *, type_ref: RefTypeTable | None = None, fn_ref: RefFnTable | None = None
    ):
        self._types = type_ref or RefTypeTable()
        self._fns = fn_ref or RefFnTable()

    @property
    def types(self) -> RefTypeTable:
        return self._types

    @property
    def fns(self) -> RefFnTable:
        return self._fns

    def __hash__(self) -> int:
        return hash(hash(self._types) + hash(self._fns))

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, RefTable):
            return hash(self) == hash(other)

        return False

    def __contains__(self, item: Symbol | CompositeSymbol | BaseFnCheck) -> bool:
        return item in self._types or item in self._fns


####################
# IR GRAPH CLASSES #
####################

class IRHash:
    """
    IR key class to handle the nodes for the IRGraph.

    Use ``key`` attribute when comparing between ``IRModule``. It is also hashable.

    Use ``uid`` attribute when comparing between type or function name
    and an ``IRHash``, ``IRNode`` or ``IRModule``. This is the default when applying
    ``hash`` function to this class instance.
    """

    _key: Path
    _uid: int
    __slots__ = ("_key", "_uid")

    def __init__(self, ir_path: Path):
        if isinstance(ir_path, Path):
            self._key = ir_path
            self._uid = hash(ir_path)

        else:
            raise ValueError("ir_path must be of type Path")

    @property
    def key(self) -> Path:
        return self._key

    @property
    def uid(self) -> int:
        return self._uid

    def __hash__(self) -> int:
        return self._uid

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, IRHash):
            return hash(self) == hash(other)

        if isinstance(other, BaseIRModule):
            return hash(self) == hash(other.path)

        return False

    def __repr__(self) -> str:
        return f"#{self._key[:-8]}/{self._uid}"


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

    def __contains__(self, item: Symbol | CompositeSymbol | BaseFnCheck) -> bool:
        return item in self._ir.module

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
        if all(isinstance(k, IRNode) for k in data) and isinstance(phf, ResultPHF) or phf is None:
            self._data = data
            self._phf = phf

        else:
            raise ValueError("node set accepts only IRNode instances")

    @property
    def phf(self) -> ResultPHF | None:
        return self._phf

    @classmethod
    def new_set(cls, *data: Hashable, phf: ResultPHF) -> NodeSet:
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

            case _:
                return False

        return False

    def __getitem__(self, item: IRHash | int) -> IRNode:
        if isinstance(item, IRHash):
            if self._phf is not None:
                return self._data[
                    get_hash(hash(item), self.phf)
                ]

            raise ValueError("node set must have phf attribute defined")

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

    def __init__(self):
        self._is_built = False
        self._nodes = NodeSet()
        self._tmp_nodes = ()

    @property
    def nodes(self) -> NodeSet:
        """Last node in a program will always be its 'main' file."""
        return self._nodes

    @property
    def is_built(self) -> bool:
        return self._is_built

    def add_node(self, ir: BaseIR) -> IRHash:
        """Add an IR to the graph node."""

        node = IRNode(ir)
        self._tmp_nodes += (node,)
        return node.irhash

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

        if not self._is_built:
            node_res, node_phf = gen_phf(self._tmp_nodes)
            self._nodes = NodeSet.new_set(*node_res, phf=node_phf)
            self._tmp_nodes = ()

            if self._check_refs():
                self._is_built = True

            else:
                raise ValueError("missing nodes to build the ir graph")

        else:
            raise ValueError("ir graph is already built.")

    def update(self, cur_node_key: IRHash, new_node: BaseIR) -> None:
        """
        Update to a new node (IR module) from a given current node key (``IRHash``)

        Args:
            cur_node_key:
            new_node:
        """

        # TODO: implement it
        raise NotImplementedError()


####################################
# BUILDING REFERENCE TABLE SECTION #
####################################

def build_reftable(
    types: dict[Symbol | CompositeSymbol, Path] | None = None,
    fns: dict[BaseFnCheck, Path] | None = None,
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

def import_type(
    node_key: IRHash, importing: Symbol | CompositeSymbol, ir_graph: IRGraph
) -> BaseTypeDataStructure:
    """
    Import a type ``importing`` from an IR module's hash value ``node_key``. Return
    the type instance.
    """

    node: IRNode = ir_graph.nodes[node_key]
    return node.ir.module.symbol_table.type.get(importing)


def import_fn(node_key: IRHash, importing: BaseFnCheck, ir_graph: IRGraph) -> FnDef:
    """
    Import a function check instance ``importing`` from an IR module's hash value ``node_key``.

    Args:
        node_key: the ``IRHash`` instance
        importing: the function ``BaseFnCheck`` instance
        ir_graph: the program's ``IRGraph``

    Returns:
        A ``FnDef`` instance
    """

    node: IRNode = ir_graph.nodes[node_key]
    return node.ir.module.symbol_table.fn.get(importing)
