from __future__ import annotations

from abc import ABC, abstractmethod
from collections import deque
from copy import deepcopy
from pathlib import Path

from typing import Any, Iterable

from hhat_lang.core.code.base import BaseIRBlock, BaseIRInstr
from hhat_lang.core.data.utils import DataKind, isquantum, has_same_paradigm
from hhat_lang.core.error_handlers.errors import (
    ErrorHandler,
    TypeSymbolConversionError,
    sys_exit,
    TypeNotFoundError,
)
from hhat_lang.core.types import POINTER_SIZE, BUILTIN_STD_TYPE_MODULE_PATH
from hhat_lang.core.types.new_core import StructTypeDef, SingleTypeDef
from hhat_lang.core.data.core import (
    Symbol,
    CompositeSymbol,
    Literal,
    LiteralArray,
    AsArray,
)
from hhat_lang.core.types.new_builtin_core import builtin_types
from hhat_lang.core.types.new_base_type import Size, QSize
from hhat_lang.core.types.new_builtin_core import CoreTypeDef
from hhat_lang.core.utils import HatOrderedDict

ContentType = BaseIRBlock | BaseIRInstr | Literal | LiteralArray | HatOrderedDict

i32 = builtin_types[BUILTIN_STD_TYPE_MODULE_PATH][Symbol("i32")]
str_t = builtin_types[BUILTIN_STD_TYPE_MODULE_PATH][Symbol("str")]
qu3 = builtin_types[BUILTIN_STD_TYPE_MODULE_PATH][Symbol("@u3")]

i_t = SingleTypeDef(Symbol("i_t")).add_member(i32).set_sizes(i32.size)
qarru3_t = (
    SingleTypeDef(Symbol("@arra-u3_t"))
    .add_member(AsArray(Symbol("@u3")))
    .set_sizes(Size(POINTER_SIZE), QSize(0, None))
)


point = (
    StructTypeDef(Symbol("point"), num_members=2)
    .add_member(Symbol("x"), i32)
    .add_member(Symbol("y"), i32)
    .set_sizes(i32.size + i32.size)
)

place = (
    StructTypeDef(Symbol("place"), num_members=2)
    .add_member(Symbol("name"), str_t)
    .add_member(Symbol("coords"), point)
    .set_sizes(str_t.size + point.size)
)

qdataset = (
    StructTypeDef(Symbol("@dataset"), num_members=2)
    .add_member(Symbol("tag"), str_t)
    .add_member(Symbol("@values"), AsArray(Symbol("@u3")))
    .set_sizes(Size(POINTER_SIZE), QSize(0, None))
)

qdataframe = (
    StructTypeDef(Symbol("@dataframe"), num_members=2)
    .add_member(Symbol("name"), str_t)
    .add_member(Symbol("@data"), AsArray(Symbol("@dataset")))
    .set_sizes(Size(POINTER_SIZE), QSize(0, None))
)

types_dict = dict()
types_dict.update(deepcopy(builtin_types))

types_dict[Path("src/hat_types/")] = {i_t.name: i_t}
types_dict[Path("src/hat_types/")].update({qarru3_t.name: qarru3_t})
types_dict[Path("src/hat_types/")].update({point.name: point})
types_dict[Path("src/hat_types/")].update({place.name: place})
types_dict[Path("src/hat_types/")].update({qdataset.name: qdataset})
types_dict[Path("src/hat_types/")].update({qdataframe.name: qdataframe})


class VarHeader:
    _name: Symbol
    _type: Symbol | CompositeSymbol
    _is_quantum: bool
    _uid: int
    _hash_value: int
    __slots__ = ("_name", "_type", "_is_quantum", "_uid", "_hash_value")

    def __init__(
        self,
        var_name: Symbol,
        var_type: Symbol | CompositeSymbol,
        uid: int | None = None,
    ):
        if has_same_paradigm(var_name, var_type):
            self._name = var_name
            self._type = var_type
            self._is_quantum = isquantum(var_name)
            if uid:
                self._uid = uid

            else:
                from random import randint

                self._uid = randint(2, 2 << 32)

            self._hash_value = hash(
                (
                    var_name,
                    var_type,
                )
            )

    @property
    def name(self) -> Symbol:
        return self._name

    @property
    def type(self) -> Symbol | CompositeSymbol:
        return self._type

    @property
    def is_quantum(self) -> bool:
        return self._is_quantum

    @property
    def uid(self) -> int:
        return self._uid

    def __hash__(self) -> int:
        return self._hash_value

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return hash(self) == hash(other)

        return False


class VarDef:
    _header: VarHeader
    _data: HatOrderedDict

    def __init__(self, var_name: Symbol, var_type: Symbol):
        self._header = VarHeader(var_name, var_type)
        self._data = expand_type(var_type)
        if isinstance(self._data, ErrorHandler):
            sys_exit(error_fn=self._data)

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

    @classmethod
    def declare(cls, var_name: Symbol, var_type: Symbol | CompositeSymbol) -> VarDef:
        return VarDef(var_name, var_type)

    def _assign(self, values: Any, params: Any | None = None) -> Any:
        if isinstance(values, type(self._data) | tuple):
            _d = HatOrderedDict()
            if isinstance(params, tuple):
                for k, v in zip(params, values):
                    _d[k] = self._assign(v, k)
            _d[params] = self._assign(values)
            return _d
        return HatOrderedDict({params: values})

    def _iter_data_container(
        self, data_container: Any, params: Any, values: Any
    ) -> Any:
        match data_container, params, values:
            case [HatOrderedDict(), tuple(), VarDef()]:
                self._iter_data_container(data_container, params, values._data)

            case [HatOrderedDict(), tuple(), tuple()]:
                for k, p, q in zip(data_container.values(), params, values):
                    self._iter_data_container(data_container, p, q)

            case [HatOrderedDict(), HatOrderedDict(), VarDef()]:
                self._iter_data_container(data_container, params, values._data)

            case [HatOrderedDict(), HatOrderedDict(), HatOrderedDict()]:
                for p in params:
                    self._iter_data_container(data_container[p], params[p], values)

            case [HatOrderedDict(), HatOrderedDict(), tuple()]:
                raise ValueError(f" ?  {data_container} | {params} | {values}")

            case [HatOrderedDict(), tuple(), HatOrderedDict()]:
                for p, (k, q) in zip(params, values.items()):
                    if p in data_container and p in values:
                        self._iter_data_container(data_container, p, q)

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
                Container(),
                Symbol(),
                Literal()
                | LiteralArray()
                | BaseIRBlock()
                | BaseIRInstr()
                | HatOrderedDict(),
            ]:
                print("c s llbio")
                data_container.add(values)

            case _:
                raise ValueError(
                    f"{data_container} ({type(data_container)}) "
                    f"| {params} ({type(params)}) "
                    f"| {values} ({type(values)})"
                )

    def assign(self, values: Iterable[ContentType], params: Iterable[Symbol]) -> VarDef:
        self._iter_data_container(self._data, params, values)
        return self

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
                print("something else?")
                return False

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


class Container(ABC):
    _data: Iterable
    _type: str

    @property
    def value(self) -> Iterable:
        return self._data

    @abstractmethod
    def add(self, value: ContentType) -> None:
        raise NotImplementedError()

    @abstractmethod
    def __getitem__(self, item):
        raise NotImplementedError()

    @abstractmethod
    def get(self) -> Any:
        raise NotImplementedError()

    @abstractmethod
    def __add__(self, other: Any) -> Any:
        raise NotImplementedError()

    @abstractmethod
    def __radd__(self, other: Any) -> Any:
        raise NotImplementedError()

    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        raise NotImplementedError()

    def __iter__(self) -> Iterable:
        return iter(self._data)

    def __repr__(self):
        return f"{self._type}({' '.join(str(k) for k in self._data)})"


class MutableContainer(Container):
    _data: tuple[ContentType] | tuple
    _type = "mut"

    def __init__(self):
        self._data = ()

    def add(self, value: ContentType) -> None:
        if isinstance(value, self.__class__):
            self._data = (self + value)._data

        else:
            self._data = (value,)

    def get(self) -> ContentType | None:
        return self._data[0]

    def __getitem__(self, item):
        return self._data[0]

    def __add__(self, other: Any) -> Any:
        if isinstance(other, self.__class__):
            return other

        raise ValueError()

    def __radd__(self, other: Any) -> Any:
        if isinstance(other, self.__class__):
            return self

        raise ValueError()

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return self.value == other.value

        return False


class ArrayContainer(Container):
    _data: tuple[ContentType] | tuple
    _type = "array"

    def __init__(self):
        self._data = ()

    def add(self, value: ContentType) -> None:
        if isinstance(value, self.__class__):
            self._data = (self + value)._data

        else:
            self._data += (value,)

    def get(self) -> Any:
        return self._data

    def __getitem__(self, item):
        return self._data[item]

    def __add__(self, other: Any) -> Any:
        if isinstance(other, self.__class__):
            for k in other:
                self.add(k)

            return self

        raise ValueError()

    def __radd__(self, other: Any) -> Any:
        if isinstance(other, self.__class__):
            for k in self:
                other.add(k)

            return other

        raise ValueError()

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return self.value == other.value

        return False


class LazySequenceContainer(Container):
    _data: deque[ContentType]
    _type = "lazy"

    def __init__(self):
        self._data = deque()

    def add(self, value: ContentType) -> None:
        if isinstance(value, self.__class__):
            self._data.extend(value._data)
            return None

        if isinstance(value, deque):
            self._data.extend(value)
            return None

        self._data.append(value)
        return None

    def get(self) -> Any:
        return self._data

    def __getitem__(self, item):
        if isinstance(item, int):
            return self._data[item]

        raise ValueError()

    def __add__(self, other: Any) -> Any:
        if isinstance(other, self.__class__):
            for k in other:
                self.add(k)

            return self

        raise ValueError()

    def __radd__(self, other: Any) -> Any:
        return other + self

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return all(p == q for p, q in zip(self.value, other.value))

        return False


def get_type(type_name: Symbol | CompositeSymbol | AsArray) -> Any | None:
    for k in types_dict.values():
        for p, q in k.items():
            if type_name == p:
                return q

    return None


def expand_type(data: Any) -> Container | HatOrderedDict | ErrorHandler:
    match data:
        case CoreTypeDef():
            if data.is_quantum:
                return LazySequenceContainer()

            return MutableContainer()

        case SingleTypeDef():
            res = HatOrderedDict()
            for k in data.members:
                res[data] = expand_type(k)

            return res

        case StructTypeDef():
            res = HatOrderedDict()
            for k, v in data:
                res[k] = expand_type(v)

            return res

        case Symbol() | CompositeSymbol():
            if res := get_type(data):
                return expand_type(res)

            return TypeNotFoundError(data)

        case AsArray():
            if res := get_type(data.value):
                return expand_type(res)

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
            if values in types_dict:
                return type_members_recursive(types_dict[values])

            return (values,)

        case AsArray():
            if values.value in types_dict:
                return type_members_recursive(types_dict[values.value])

            return (values.value,)

        case Container():
            return ()

        case _:
            raise ValueError(f"{values} ({type(values)})")


if __name__ == "__main__":
    print(i_t)
    print(point)
    print(point.size)
    print(place)
    print(place.size)
    print(expand_type(i32))
    print(expand_type(i_t))
    print(expand_type(point))
    print(expand_type(place))
    print(qdataset)
    print(expand_type(qdataset))
    print(qdataframe)
    print(expand_type(qdataframe))
    print(type_members_recursive(expand_type(qdataframe)))
    qv1 = VarDef.declare(Symbol("@v1"), Symbol("@dataset"))
    print(qv1)
    qv1.assign(
        (
            Literal('"balance"', Symbol("str")),
            LiteralArray((Literal("@1", Symbol("@u3")), Literal("@2", Symbol("@u3")))),
        ),
        (Symbol("tag"), Symbol("@values")),
    )
    print(qv1)
    qv2 = VarDef.declare(Symbol("@v2"), Symbol("@dataframe"))
    print(qv2)
    qv2.assign(
        (
            Literal('"df"', Symbol("str")),
            qv1._data,
        ),
        type_members_recursive(expand_type(qdataframe)),
    )
    print(qv2)

    qv3 = VarDef.declare(Symbol("@v3"), Symbol("@dataframe"))
    qv3.assign(
        (
            Literal('"df"', Symbol("str")),
            qv1,
        ),
        type_members_recursive(expand_type(qdataframe)),
    )
    print(qv3)
    assert qv2 == qv3, False
