from __future__ import annotations

import sys
from abc import abstractmethod
from collections import OrderedDict
from typing import Any, Iterable

from hhat_lang.core.code.base import BaseIRBlock, BaseIRInstr
from hhat_lang.core.data.core import (
    CompositeSymbol,
    Symbol,
    Literal,
    LiteralArray,
    AsArray,
)
from hhat_lang.core.data.utils import AbstractDataDef, DataKind, has_same_paradigm
from hhat_lang.core.data.var_assignment import types_dict
from hhat_lang.core.data.var_utils import (
    BaseCollection,
    DataHeader,
    Container,
    LazySequenceContainer,
    MutableContainer,
    ArrayContainer,
    VarHeader,
)
from hhat_lang.core.error_handlers.errors import (
    VariableFreeingBorrowedError,
    QuantumDataNotAppendableError,
    sys_exit,
    ErrorHandler,
    VarContainerParamsTypeError,
    VariableWrongMemberError,
    TypeNotFoundError,
    TypeSymbolConversionError,
)
from hhat_lang.core.types.abstract_base import BaseTypeDef
from hhat_lang.core.types.new_base_type import TypeDef
from hhat_lang.core.types.new_builtin_core import CoreTypeDef
from hhat_lang.core.types.new_core import SingleTypeDef, StructTypeDef
from hhat_lang.core.types.utils import BaseTypeEnum
from hhat_lang.core.utils import HatOrderedDict

# TODO: remove dependencies from types_dict and incluse IRGraph/IRNodes logic


class DataDef(AbstractDataDef):
    """
    Data container for constant, variable and temporary data definitions.
    """

    _header: DataHeader
    _data_type: BaseCollection
    _borrowed: DataHeader | None

    def __init__(self, *_args: Any, **kwargs: Any):
        self.check_type()

    @property
    def name(self) -> Symbol | CompositeSymbol:
        return self._header.name

    @property
    def type(self) -> BaseTypeDef:
        return self._header.type

    @property
    def is_quantum(self) -> bool:
        return self._header.is_quantum

    @property
    def kind(self):
        return self._header.kind

    @property
    def borrowed(self):
        return self._borrowed

    @property
    def data(self) -> BaseCollection:
        return self._data_type

    def check_type(self) -> None:
        if has_same_paradigm(self._header.name, self._header.type.name):
            if self.is_quantum and self._header.kind is DataKind.APPENDABLE:
                return None

            if not self.is_quantum:
                return None

        sys_exit(
            error_fn=QuantumDataNotAppendableError(self._header.name, self._header.kind)
        )

    def get_type_member(self, index: int) -> Symbol:
        return self.type[index][0]

    @abstractmethod
    def assign(self, *args: Any, **kwargs: Any) -> DataDef:
        """
        Assign some data to this data container. Should return itself.
        """

        raise NotImplementedError()

    @abstractmethod
    def get(self, *args: Any, **kwargs: Any) -> Any:
        """
        Retrieve data container content based on the given member, for instance.
        """

        raise NotImplementedError()

    @abstractmethod
    def borrow_to(self):
        """
        This data container method will take its own data and will borrow to the other data.
        """

        raise NotImplementedError()

    @abstractmethod
    def return_borrow(self):
        """
        This data container method will take its own data (which was borrowed) and give it back.
        """

        raise NotImplementedError()

    def __call__(self, *args, **kwargs):
        """
        Calling data container instance is the equivalent of using its `assign` method.
        """

        return self.assign(*args, **kwargs)

    def __iter__(self) -> Iterable:
        return iter(self._data_type)

    def free(self) -> None:
        if self._borrowed:
            sys.exit(VariableFreeingBorrowedError(self.name)())

        del self
        return None


ContentType = BaseIRBlock | BaseIRInstr | Literal | LiteralArray | HatOrderedDict


class VarDef:
    _header: VarHeader
    _data: HatOrderedDict
    _data_type: BaseTypeEnum

    def __init__(self, var_name: Symbol, var_type: Symbol):
        self._header = VarHeader(var_name, var_type)
        self._data = expand_type_as_container(var_type)
        if isinstance(self._data, ErrorHandler):
            sys_exit(error_fn=self._data)

        self._data_type = get_data_type(var_type)
        if isinstance(self._data_type, ErrorHandler):
            sys_exit(error_fn=self._data_type)

    @property
    def name(self) -> Symbol:
        return self._header._name

    @property
    def type(self) -> Symbol | CompositeSymbol:
        return self._header._type

    @property
    def is_quantum(self) -> bool:
        return self._header._is_quantum

    @property
    def data(self) -> HatOrderedDict:
        return self._data

    def _assign(self, data_container: Any, params: Any, values: Any) -> None:
        match data_container, params, values:
            case [HatOrderedDict(), tuple(), VarDef()]:
                self._assign(data_container, params, values._data)

            case [HatOrderedDict(), tuple(), tuple()]:
                for k, p, q in zip(data_container.values(), params, values):
                    self._assign(data_container, p, q)

            case [HatOrderedDict(), HatOrderedDict(), VarDef()]:
                self._assign(data_container, params, values._data)

            case [HatOrderedDict(), HatOrderedDict(), HatOrderedDict()]:
                for p in params:
                    self._assign(data_container[p], params[p], values)

            case [HatOrderedDict(), HatOrderedDict(), tuple()]:
                raise ValueError(f" ?  {data_container} | {params} | {values}")

            case [HatOrderedDict(), tuple(), HatOrderedDict()]:
                for p, (k, q) in zip(params, values.items()):
                    if p in data_container and p in values:
                        self._assign(data_container, p, q)

                    else:
                        raise ValueError()

            case [HatOrderedDict(), Symbol(), Container()]:
                data_container[params].add(values)

            case [
                HatOrderedDict(),
                Symbol(),
                Literal() | LiteralArray() | BaseIRBlock() | BaseIRInstr(),
            ]:
                data_container[params].add(values)

            case [
                HatOrderedDict(),
                TypeDef(),
                Literal() | LiteralArray() | BaseIRBlock() | BaseIRInstr(),
            ]:
                data_container[params].add(values)

            case [
                Container(),
                Symbol(),
                Literal()
                | LiteralArray()
                | BaseIRBlock()
                | BaseIRInstr()
                | HatOrderedDict(),
            ]:
                data_container.add(values)

            case _:
                raise ValueError(
                    f"{data_container} ({type(data_container)}) "
                    f"| {params} ({type(params)}) "
                    f"| {values} ({type(values)})"
                )

    def _assign_single(self, data_container: HatOrderedDict, values: Any) -> None:
        match values:
            case Literal() | LiteralArray() | BaseIRBlock() | BaseIRInstr():
                data_container[next(iter(data_container.keys()))].add(values)

            case tuple():
                self._assign_single(data_container, next(iter(values)))

            case _:
                raise ValueError(
                    f"{data_container=} {type(data_container)=} | {values=} ({type(values)=})"
                )

    def _get(self, data: Any, member: Symbol | None = None) -> Any:
        # TODO: if the final data is a OrderedDict, it must be converted to a valid
        #  H-hat type data (for instance, hashmap)
        match data:
            case OrderedDict():
                return data[member] if member else data

            case Container():
                return data.get(member)

            case _:
                return data

    def _check_eq(self, lhs: Any, rhs: Any) -> bool:
        match lhs, rhs:
            case [VarDef(), VarDef()]:
                res = ()
                for k, v in lhs:
                    if k in rhs:
                        res += (self._check_eq(v, rhs.data[k]),)

                    else:
                        return False

                return all(res)

            case [HatOrderedDict(), HatOrderedDict()]:
                res = ()
                for k, v in lhs.items():
                    if k in rhs:
                        res += (self._check_eq(v, rhs[k]),)

                    else:
                        return False

                return all(res)

            case [x, y]:
                return x == y

            case _:
                return False

    @classmethod
    def declare(cls, var_name: Symbol, var_type: Symbol | CompositeSymbol) -> VarDef:
        return VarDef(var_name, var_type)

    def assign(
        self,
        values: Iterable[ContentType],
        params: TypeDef | dict | HatOrderedDict | tuple,
    ) -> VarDef:
        if self._data_type is BaseTypeEnum.SINGLE:
            self._assign_single(self._data, values)

        if isinstance(params, TypeDef):
            params = expand_type_as_container(params)

        if isinstance(params, dict | HatOrderedDict):
            params = type_members_recursive(params)

        if not isinstance(params, tuple):
            sys_exit(params, error_fn=VarContainerParamsTypeError(self.name))

        self._assign(self._data, params, values)
        return self

    def get(self, member: Symbol | None = None) -> ContentType:
        if member:
            if member in self._data:
                return self._get(self._data[member])

            sys_exit(member, error_fn=VariableWrongMemberError(self.name))

        return self._data[next(iter(self._data))].get()

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, VarDef):
            return self._check_eq(self, other)
        return False

    def __contains__(self, item: Any) -> bool:
        return item in self._data

    def __iter__(self) -> Iterable:
        return iter(self._data.items())

    def __repr__(self) -> str:
        return f"{self.name}[{' '.join(f'{k}:{v}' for k, v in self._data.items())}]"


def get_type(type_name: Symbol | CompositeSymbol | AsArray) -> Any | None:
    for k in types_dict.values():
        for p, q in k.items():
            if type_name == p:
                return q

    return None


def expand_type_as_container(data: Any) -> Container | HatOrderedDict | ErrorHandler:
    match data:
        case CoreTypeDef():
            if data.is_quantum:
                return LazySequenceContainer()

            return MutableContainer()

        case SingleTypeDef():
            res = HatOrderedDict()
            for k in data.members:
                res[data] = expand_type_as_container(k)

            return res

        case StructTypeDef():
            res = HatOrderedDict()
            for k, v in data:
                res[k] = expand_type_as_container(v)

            return res

        case Symbol() | CompositeSymbol():
            if res := get_type(data):
                return expand_type_as_container(res)

            return TypeNotFoundError(data)

        case AsArray():
            if res := get_type(data.value):
                return expand_type_as_container(res)

            if data._is_quantum:
                return LazySequenceContainer()

            return ArrayContainer()

        case _:
            return TypeSymbolConversionError(data)


def type_members_recursive(
    values: Container | HatOrderedDict,
) -> tuple[Symbol | CompositeSymbol | HatOrderedDict] | tuple:
    match values:
        case HatOrderedDict():
            _r = ()
            for k, v in values.items():
                _res = type_members_recursive(v)
                _r += (k,) if not _res else (HatOrderedDict({k: _res}),)

            return _r

        case Symbol() | CompositeSymbol():
            return (values,)

        case AsArray():
            return (values.value,)

        case Container():
            return ()

        case _:
            raise ValueError(f"{values} ({type(values)})")


def get_data_type(value: Symbol | CompositeSymbol) -> BaseTypeEnum | ErrorHandler:
    for t, q in types_dict.items():
        if value in q:
            return types_dict[t][value].type

    return TypeNotFoundError(value)
