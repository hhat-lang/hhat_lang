from __future__ import annotations

from abc import ABC, abstractmethod
from collections import OrderedDict
from copy import deepcopy
from enum import Enum
from typing import Any, Iterable, Iterator
from uuid import uuid5, NAMESPACE_X500

from hhat_lang.core.code.abstract_new_ir import BaseIRBlock
from hhat_lang.core.code.symbol_table import SymbolTable
from hhat_lang.core.code.utils import get_phf_prime, PHF_R_LIMIT, PHF_A_LIMIT, ResultPHF, get_hash
from hhat_lang.core.data.core import WorkingData, CompositeWorkingData, Symbol, CompositeSymbol
from hhat_lang.core.data.fn_def import BaseFnCheck, FnDef
from hhat_lang.core.types.abstract_base import BaseTypeDataStructure


#################################
# PERFECT HASH FUNCTION SECTION #
#################################

def _gen_res_a_r_phf(
    group_tuple: tuple[IRHash | tuple[IRHash, Symbol | CompositeSymbol | BaseFnCheck], ...],
    tuple_len: int,
    a: int,
    r: int,
    prime: int,
) -> tuple[IRHash | Symbol | CompositeSymbol | BaseFnCheck, ...] | tuple:
    """
    Generate a perfect hash function (PHF) tuple.

    Args:
        group_tuple: the tuple of IR hashes, or IR hashes and symbol/function check tuple-pairs
        tuple_len:
        a: an integer parameter to define the index for each element in the ``group_tuple``
        r: another integer parameter to define the index for each element in the ``group_tuple``
        prime: the prime number used to define the index for each element in the ``group_tuple``

    Returns:
        A tuple with the ``group_tuple`` ordered by their PHF index. Empty tuple if the PHF
        could not be found.
    """

    collision: bool = False
    res_list: list = [None for _ in range(tuple_len)]

    for obj in group_tuple:
        h = get_hash(hash(obj), a, r, tuple_len, prime)

        if obj not in res_list and res_list[h] is None:
            res_list[h] = obj

        else:
            collision = True
            break

    if not collision and None not in res_list:
        return tuple(res_list)

    return ()


def gen_phf(
    group_tuple: tuple[IRHash | tuple[IRHash, Symbol | CompositeSymbol | BaseFnCheck], ...]
) -> tuple[tuple[IRHash | Symbol | CompositeSymbol | BaseFnCheck, ...], ResultPHF]:
    """
    Generate the perfect hash function (PHF). Each ``group_tuple`` element will be ordered
    in a new tuple according to its newly calculated hash value. Each element has exactly
    one unique index number that wil define its position in the new tuple.

    Args:
        group_tuple: a tuple with IR hash elements, or IR hash and symbol/function
            check tuple-pairs

    Returns:
        A resulting tuple with the elements positioned in their respective index number
        inside the tuple, and a ``ResultPHF`` instance with the ``a`` and ``r`` parameters
        to retrieve the hash values of each element.
    """

    tuple_len: int = len(group_tuple)
    prime = get_phf_prime(tuple_len)

    for a in range(1, PHF_A_LIMIT):
        for r in range(PHF_R_LIMIT):
            res_list = _gen_res_a_r_phf(group_tuple, tuple_len, a, r, prime)

            if res_list:
                return tuple(res_list), ResultPHF(a=a, r=r)

    raise ValueError("could not find satisfactory parameter values to generate the PHF")


##############
# IR SECTION #
##############

class BaseIRModule(ABC):
    """Base abstract class for IR module definitions."""

    _symbol_table: SymbolTable
    _main: BaseIRBlock
    __slots__ = ("_symbol_table", "_main")

    @property
    def symbol_table(self) -> SymbolTable:
        return self._symbol_table

    @property
    def main(self) -> BaseIRBlock:
        return self._main

    def __hash__(self) -> int:
        return hash((hash(self._symbol_table), hash(self._main)))

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return hash(self) == hash(other)

        return False

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
    __slots__ = ("_ref_table", "_module")

    @property
    def module(self) -> BaseIRModule:
        return self._module

    @property
    def ref_table(self) -> RefTable:
        return self._ref_table

    @abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError()


class BaseIRFlag(Enum):
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

    def __iter__(self) -> Iterable:
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

    def __init__(self):
        self._table = dict()

    def add_ref(
        self,
        type_name: Symbol | CompositeSymbol,
        ir_ref: IRHash
    ) -> None:
        if (
            isinstance(type_name, Symbol | CompositeSymbol)
            and isinstance(ir_ref, IRHash)
        ):
            self._table[type_name] = ir_ref

        else:
            raise ValueError(f"wrong reference type table input ({type_name})")

    def get_irkey(self, type_name: Symbol | CompositeSymbol) -> IRHash:
        return self._table[type_name]

    def __hash__(self) -> int:
        return hash(self._table)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, RefTypeTable):
            return hash(self) == hash(other)

        return False

    def __len__(self) -> int:
        return len(self._table)

    def __iter__(self) -> Iterable:
        return iter(self._table.items())


class RefFnTable:
    """Reference to functions from another IR"""

    _table: dict[BaseFnCheck, IRHash]

    def __init__(self):
        self._table = dict()

    def add_ref(self, fn_name: BaseFnCheck, ir_ref: IRHash) -> None:
        if (
            isinstance(fn_name, BaseFnCheck)
            and isinstance(ir_ref, IRHash)
        ):
            self._table[fn_name] = ir_ref

        else:
            raise ValueError(f"wrong reference type table input ({fn_name})")

    def get_irkey(self, fn_name: BaseFnCheck) -> IRHash:
        return self._table[fn_name]

    def __hash__(self) -> int:
        return hash(self._table)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, RefFnTable):
            return hash(self) == hash(other)

        return False

    def __len__(self) -> int:
        return len(self._table)

    def __iter__(self) -> Iterable:
        return iter(self._table.items())


class RefTable:
    """To store reference for types and functions from another IR"""

    _types: RefTypeTable
    _fns: RefFnTable

    def __init__(self):
        self._types = RefTypeTable()
        self._fns = RefFnTable()

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


####################
# IR GRAPH CLASSES #
####################

class IRHash:
    """IR key class to handle the nodes for the IRGraph"""

    _key: str
    _hash_value: int
    __slots__ = ("_key", "_hash_value")

    def __init__(self, ir: BaseIR | BaseIRModule):
        if isinstance(ir, BaseIR):
            self._key = self.get_hash(ir.module)

        elif isinstance(ir, BaseIRModule):
            self._key = self.get_hash(ir)

        else:
            raise ValueError("ir must be of type BaseIR or BaseIRModule")

        self._hash_value = hash(self._key)

    @classmethod
    def get_hash(cls, ir_module: BaseIRModule) -> str:
        return uuid5(NAMESPACE_X500, str(ir_module)).hex

    @property
    def key(self) -> Any:
        return self._key

    def __hash__(self) -> int:
        return self._hash_value

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, IRHash):
            return hash(self) == hash(other)

        return False


class IRNode:
    """Stores node key as ``IRHash`` and value as ``BaseIRModule`` child instance"""

    _key: IRHash
    _value: BaseIRModule
    __slots__ = ("_key", "_value", "_hash_value")

    def __init__(self, node: BaseIRModule):
        self._value = node
        self._key = IRHash(node)
        self._hash_value = hash(self._key)

    @property
    def key(self) -> IRHash:
        return self._key

    @property
    def value(self) -> BaseIRModule:
        return self._value

    def __hash__(self) -> int:
        return self._hash_value

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, IRHash | IRNode):
            return hash(self) == hash(other)

        return False

    def __repr__(self) -> str:
        return f"Node({self.key})"


class IREdge:
    _key: tuple[IRHash, Symbol | CompositeSymbol | BaseFnCheck]
    _value: IRHash
    __slots__ = ("_key", "_value", "_hash_value")

    def __init__(
        self,
        to_ir: IRHash,
        importing: Symbol | CompositeSymbol | BaseFnCheck,
        from_ir: IRHash
    ):
        self._key = (to_ir, importing)
        self._value = from_ir
        self._hash_value = hash((hash(self._key), hash(self._value)))

    @property
    def key(self) -> tuple[IRHash, Symbol | CompositeSymbol]:
        return self._key

    @property
    def value(self) -> IRHash:
        return self._value

    def __hash__(self) -> int:
        return self._hash_value

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, IREdge):
            return hash(self) == hash(other)

        return False

    def __contains__(self, item: tuple[IRHash, Symbol | CompositeSymbol | BaseFnCheck]) -> bool:
        return item == self._key

    def __repr__(self) -> str:
        return f"Edge({self.key[0]}->{self.key[1]}:{self.value})"


class NodeSet:
    """Efficiently store ``IRNode`` elements"""

    _data: tuple[IRNode, ...] | tuple
    _phf: ResultPHF

    def __init__(self, *data: IRNode):
        if all(isinstance(k, IRNode) for k in data):
            self._data = data
        else:
            raise ValueError("node set accepts only IRNode instances")

    @property
    def phf(self) -> ResultPHF:
        return self._phf

    @classmethod
    def new_set(cls, *data: IRNode) -> NodeSet:
        return cls(*data)

    def __contains__(self, x: Any) -> bool:
        return x in self._data

    def __getitem__(self, item: IRHash) -> IRNode:
        return self._data[get_hash(hash(item), self.phf.a, self.phf.r, self.phf.n, self.phf.prime)]

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator:
        return iter(self._data)


class EdgeSet:
    """Efficiently store ``IREdge`` elements."""

    _data: tuple[IREdge, ...] | tuple
    _phf: ResultPHF

    def __init__(self, *data: IREdge):
        if all(isinstance(k, IREdge) for k in data):
            self._data = data

        else:
            raise ValueError("edge set must have only IR edge elements")

    @property
    def phf(self) -> ResultPHF:
        return self._phf

    @classmethod
    def new_set(cls, *data: IREdge) -> EdgeSet:
        return cls(*data)

    def __contains__(self, item: Any) -> bool:
        for edge in self._data:
            if item in edge:
                return True

        return False

    def __getitem__(self, item: tuple[IRHash, Symbol | CompositeSymbol | BaseFnCheck]) -> IRHash:
        edge = self._data[get_hash(hash(item), self.phf.a, self.phf.r, self.phf.n, self.phf.prime)]
        return edge.value

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterable:
        return iter(self._data)


class IRGraph:
    """
    Graph to hold IR instances as nodes and their relationship as edges. The relationship
    (stored in ``RefTable``) happens when a type or function is imported from another IR
    module.
    """

    _is_built: bool
    _nodes: NodeSet
    _edges: EdgeSet

    _tmp_nodes: tuple[IRNode, ...] | tuple
    _tmp_edges: tuple[tuple[IRHash, Symbol | CompositeSymbol | BaseFnCheck], ...] | tuple

    def __init__(self):
        self._is_built = False
        self._nodes = NodeSet()
        self._edges = EdgeSet()
        self._tmp_nodes = ()
        self._tmp_edges = ()

    @property
    def nodes(self) ->  NodeSet:
        """Last node in a program will always be its 'main' file."""
        return self._nodes

    @property
    def edges(self) -> EdgeSet:
        """Edges between IR nodes"""
        return self._edges

    @property
    def is_built(self) -> bool:
        return self._is_built

    def _add_reftable_nodes(
        self,
        node_key: IRHash,
        ref_table: RefTypeTable | RefFnTable,
    ) -> None:
        for ref_s, ref_ir in ref_table:
            if not any(ref_ir == ref.key for ref in self._tmp_nodes):
                self._tmp_nodes += ref_ir,

            self.add_edge(to_ir=node_key, importing=ref_s, from_ir=ref_ir)

    def add_node(self, ir: BaseIR) -> IRHash:
        """Add an IR to the graph node."""

        node = IRNode(ir.module)
        self._tmp_nodes += node,
        node_key = node.key

        self._add_reftable_nodes(node_key, ir.ref_table.types)
        self._add_reftable_nodes(node_key, ir.ref_table.fns)

        return node_key

    def add_edge(
        self,
        to_ir: IRHash,
        importing: Symbol | CompositeSymbol | BaseFnCheck,
        from_ir: IRHash
    ) -> None:
        """
        To add a new edge, both the ``to_ir`` and ``from_ir`` node hashes must exist, then an
        ``IREdge`` instance will be defined for them alongside with the ``importing`` element.

        Args:
            to_ir: ``IRHash`` instance from the importer IR module
            importing: the type (``Symbol`` or ``CompositeSymbol``) or
                function name (``BaseFnCheck``) element
            from_ir: ``IRHash`` instance from the imported IR module
        """

        if to_ir in self.nodes and from_ir in self.nodes:
            self._tmp_edges += IREdge(to_ir=to_ir, importing=importing, from_ir=from_ir),

    def build(self) -> None:
        """Build IR graph for performance and optimization purposes"""

        if not self._is_built:
            self._nodes = NodeSet.new_set(*gen_phf(self._tmp_nodes))
            self._edges = EdgeSet.new_set(*gen_phf(self._tmp_edges))
            # TODO: decide how to handle self._tmp_nodes and self._tmp_edges afterwards, after
            #  the update method is implemented
            self._is_built = True

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


########################################################################
# IR MODULES, TYPES, FUNCTIONS AND GRAPH HELPER/CONSTRUCTORS FUNCTIONS #
########################################################################

def get_imported_node(ir_edge: IREdge, ir_graph: IRGraph) -> IRNode:
    """"""
    if isinstance(ir_edge, IREdge) and isinstance(ir_graph, IRGraph):
        for node in ir_graph.nodes:
            if ir_edge.value == node.key:
                return node

    raise ValueError(f"Could not find node {ir_edge.value} in IR graph.")


def get_imports_from_node(node_key: IRHash, ir_graph: IRGraph) -> IRNode:
    for node in ir_graph.nodes:
        if node.key == node_key:
            imported_node = ()
            imported_keys = ()
            imported_types = dict()
            imported_fns = dict()

            for p in ir_graph.edges:
                if node.key == p.key[0]:
                    if p.value not in imported_keys:
                        new_node = get_imported_node(ir_edge=p, ir_graph=ir_graph)
                        imported_node += new_node,
                        imported_keys += new_node.key,


def import_type(
    node_key: IRHash,
    importing: Symbol | CompositeSymbol,
    ir_graph: IRGraph
) -> BaseTypeDataStructure:
    """
    Import a type ``importing`` from an IR module's hash value ``node_key``. Return
    the type instance.
    """

    ir_hash: IRHash = ir_graph.edges[(node_key, importing)]
    ir_node: IRNode = ir_graph.nodes[ir_hash]
    return ir_node.value.symbol_table.type.get(importing)


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

    ir_hash: IRHash = ir_graph.edges[(node_key, importing)]
    ir_node: IRNode = ir_graph.nodes[ir_hash]
    return ir_node.value.symbol_table.fn.get(importing)
