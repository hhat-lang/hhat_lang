from __future__ import annotations

from abc import ABC, abstractmethod
from collections import OrderedDict
from copy import deepcopy
from enum import Enum
from typing import Any, Iterable, Iterator
from uuid import uuid5, NAMESPACE_X500

from hhat_lang.core.code.abstract_new_ir import BaseIRBlock
from hhat_lang.core.code.symbol_table import SymbolTable
from hhat_lang.core.code.utils import get_phf_prime, PHF_R_LIMIT, PHF_A_LIMIT, ResultPHF
from hhat_lang.core.data.core import WorkingData, CompositeWorkingData, Symbol, CompositeSymbol
from hhat_lang.core.data.fn_def import BaseFnCheck


#################################
# PERFECT HASH FUNCTION SECTION #
#################################

def get_hash(value: int, a: int, r: int, n: int, prime: int) -> int:
    p = value * a
    return ((p ^ (p >> r)) % prime) % n


def _gen_res_a_r_phf(
    group_tuple: tuple[IRHash | tuple[IRHash, Symbol | CompositeSymbol | BaseFnCheck], ...],
    tuple_len: int,
    a: int,
    r: int,
    prime: int,
) -> tuple[IRHash | Symbol | CompositeSymbol | BaseFnCheck, ...] | tuple:
    collision: bool = False
    res_list: list = [None for _ in range(tuple_len)]

    for obj in group_tuple:
        h = get_hash(hash(obj), a, r, tuple_len, prime)

        if obj not in res_list and res_list[h] is None:
            res_list[h] = obj

        else:
            collision = True
            break

    if not collision:
        return tuple(res_list)

    return ()


def gen_phf(
    group_tuple: tuple[IRHash | tuple[IRHash, Symbol | CompositeSymbol | BaseFnCheck], ...]
) -> tuple[tuple[IRHash | Symbol | CompositeSymbol | BaseFnCheck, ...], ResultPHF]:
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
    """Use to store unique ``IRNode`` instances"""

    _data: set

    def add(self, value: Any) -> None:
        if isinstance(value, IRNode):
            self._data.add(value)

    def discard(self, value: Any) -> None:
        self._data.discard(value)

    def __contains__(self, x: Any) -> bool:
        return x in self._data

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator:
        return iter(self._data)



class NodeDict(OrderedDict):
    def __init__(self, other=(), /):
        for k in other:
            if len(k) == 2:
                if isinstance(k[0], IRHash) and isinstance(k[1], BaseIR):
                    continue

            raise ValueError("IR node must have a key as IRKey and value as BaseIR")

        super().__init__(other)

    def update(self, m: dict | OrderedDict, /, **_kwargs: Any) -> None:
        """
        Update IR node data with ``m`` argument. Kwargs are ignored.

        Args:
            m: the dictionary or ``OrderedDict`` containing data to be updated into the IR node
            **_kwargs: just to keep the parent function template; not used.
        """

        if len(_kwargs) > 0:
            # this is enforced because arg name at **kwargs can only be of str type,
            # but we need arg name to be of IRKey type
            raise ValueError("do not use **kwargs for IR node")

        if all(isinstance(k, IRHash) and isinstance(v, BaseIR) for k, v in m.items()):
            super().update(m)

        else:
            raise ValueError(
                "cannot update IR node with data other than IRKey for keys and BaseIR for value"
            )

    def pop(self, key: IRHash, default: Any = None) -> BaseIR:
        return super().pop(key, default=default or object())

    def __setitem__(self, key: IRHash, value: BaseIR) -> None:
        if isinstance(key, IRHash) and isinstance(value, BaseIR):
            super().__setitem__(key, value)

        else:
            raise ValueError(
                "to set key and value on IR node, IRKey and BaseIR data are needed, respectively"
            )


class EdgeDict:
    """Define the IR graph edge"""

    _data: OrderedDict[IRHash, dict[Symbol | CompositeSymbol, IRHash]]

    def __init__(self):
        self._data = OrderedDict()

    def add_node(self, node: IRHash) -> None:
        if isinstance(node, IRHash) and node not in self._data:
            self._data.update({node: dict()})

        else:
            raise ValueError(
                f"node {node} ({type(node)}) already in IR edge or wrong type (should be IRKey)"
            )

    def add_links(self, *refs: Symbol | CompositeSymbol, node: IRHash, ref_node: IRHash) -> None:
        """
        Link each reference in ``*refs`` from its reference node ``ref_node`` with the
        reference importer ``node``.

        Args:
            *refs: reference as types or function name (``Symbol``, ``CompositeSymbol``)
            node: the IR block that needs the references to properly import their values
            ref_node: the IR block that contains the references in ``*refs``
        """

        if (
            all(isinstance(k, Symbol | CompositeSymbol) for k in refs)
            and isinstance(node, IRHash)
            and isinstance(ref_node, IRHash)
        ):
            if node in self._data and ref_node in self._data:
                # refs should contain unique values inside a node,
                # so they should not be assigned twice
                self._data[node].update({k: ref_node for k in refs})

        else:
            raise ValueError(
                "IR edge linking references (Symbol, CompositeSymbol) from ref_node"
                " (IRKey) to the node (IRKey); got wrong types"
            )

    def get_node(self, node: IRHash) -> dict[Symbol | CompositeSymbol, IRHash]:
        """Get the dictionary of references for all its imported types and functions"""

        return self._data[node]

    def get_ref(self, node: IRHash, ref: Symbol | CompositeSymbol) -> IRHash:
        """Get the IR key from a given reference inside an importer node"""

        return self._data[node][ref]

    def update_node(self, cur_node: IRHash, new_node: IRHash) -> None:
        """Update a current node IR key to a new one"""

        new_data: OrderedDict[IRHash, dict[Symbol | CompositeSymbol, IRHash]] = OrderedDict()

        for k0, v0 in self._data.items():

            cur_k0 = new_node if k0 == cur_node else k0
            new_data.update(
                {
                    cur_k0: {
                        k1: new_node if v1 == cur_node else v1
                        for k1, v1 in v0.items()
                    }
                }
            )

        self._data = deepcopy(new_data)
        del new_data

    def remove_node(self, node: IRHash) -> None:
        self._data.pop(node)
        new_data: OrderedDict[IRHash, dict[Symbol | CompositeSymbol, IRHash]] = OrderedDict()

        for k, v in self._data.items():
            for p, q in v.items():
                if q != node:
                    new_data[k].update({p:q})

        self._data = deepcopy(new_data)
        del new_data


class EdgeSet:
    _data: tuple[IREdge, ...] | tuple

    def __init__(self):
        self._data = ()

    def add(
        self,
        edge: IREdge,
        to_ir: IRHash,
        importing: Symbol | CompositeSymbol | BaseFnCheck,
        from_ir: IRHash
    ) -> None:
        # if (
        #     isinstance(to_ir, IRHash)
        #     and isinstance(importing, Symbol | CompositeSymbol | BaseFnCheck)
        #     and isinstance(from_ir, IRHash)
        # ):
        #     self._data += IREdge(to_ir=to_ir, importing=importing, from_ir=from_ir),
        if isinstance(edge, IREdge):
            self._data += edge,

    def __contains__(self, item: Any) -> bool:
        for edge in self._data:
            if item in edge:
                return True
        return False

    def __getitem__(self, item: tuple[IRHash, Symbol | CompositeSymbol | BaseFnCheck]) -> IREdge:
        if isinstance(item, tuple):
            for edge in self._data:
                if item in edge:
                    return edge

        raise ValueError(f"edge with {item} not found")


def gen_node_set() -> NodeSet:
    pass


def gen_edge_set() -> EdgeSet:
    pass


class IRGraph:
    """
    Graph to hold IR instances as nodes and their relationship as edges. The relationship
    (stored in ``RefTable``) happens when a type or function is imported from another IR
    module.
    """

    _is_built: bool
    _a_value: int
    _r_value: int
    # _nodes: tuple[IRNode, ...] | tuple
    # _edges: tuple[IREdge, ...] | tuple
    _nodes: dict[IRHash, IRNode]
    _edges: EdgeSet

    def __init__(self):
        # self._nodes = ()
        # self._edges = ()
        self._nodes = dict()
        self._edges = dict()

    @property
    def nodes(self) ->  dict[IRHash, IRNode]:  # tuple[IRNode, ...]:
        """Last node in a program will always be its 'main' file."""
        return self._nodes

    @property
    def edges(self) -> dict[tuple[IRHash, Symbol | BaseFnCheck], IRHash]:  # tuple[IREdge, ...]:
        """Edges between IR nodes"""
        return self._edges

    def add_node(self, ir: BaseIR) -> IRHash:
        node = IRNode(ir.module)
        self._nodes += node,
        node_key = node.key

        for t, t_ir in ir.ref_table.types:
            self.add_edge(to_ir=node_key, importing=t, from_ir=t_ir)

        for f, f_ir in ir.ref_table.fns:
            self.add_edge(to_ir=node_key, importing=f, from_ir=f_ir)

        return node_key

    def add_edge(
        self,
        to_ir: IRHash,
        importing: Symbol | CompositeSymbol | BaseFnCheck,
        from_ir: IRHash
    ) -> None:
        """
        To add a new edge, both the node and the links must exist, so there should be
        a ``IRKey`` associated with them.

        Args:
            to_ir: ``IRHash`` instance from the importer IR module
            importing: the type (``Symbol`` or ``CompositeSymbol``) or
                function name (``BaseFnCheck``)
            from_ir: ``IRHash`` instance from the imported IR module
        """

        if (
            isinstance(to_ir, IRHash)
            and isinstance(importing, Symbol | CompositeSymbol | BaseFnCheck)
            and isinstance(from_ir, IRHash)
        ):
            if to_ir in self.nodes and from_ir in self.nodes:
                # self._edges += IREdge(to_ir=to_ir, importing=importing, from_ir=from_ir),
                self._edges[()] = IREdge(to_ir)

    def build(self) -> None:
        """Build IR graph for performance and optimization purposes"""
        # TODO: implement it
        raise NotImplementedError()

    def update(self, cur_node_key: IRHash, new_node: BaseIR):
        """
        Update to a new node (IR module) from a given current node key (``IRHash``)

        Args:
            cur_node_key:
            new_node:

        Returns:

        """

        # TODO: implement it
        raise NotImplementedError()



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
) -> BaseIRBlock:
    pass


def import_fn():
    pass
