from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from hhat_lang.core.data.core import (
    AsArray,
    Literal,
    LiteralArray,
    Symbol,
)
from hhat_lang.core.data.var_def import (
    VarDef,
    expand_type_as_container,
    type_members_recursive,
)
from hhat_lang.core.types import BUILTIN_STD_TYPE_MODULE_PATH, POINTER_SIZE
from hhat_lang.core.types.new_base_type import QSize, Size
from hhat_lang.core.types.new_builtin_core import builtin_types
from hhat_lang.core.types.new_core import SingleTypeDef, StructTypeDef

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

if __name__ == "__main__":
    print(f"{types_dict=}")
    print(i_t)
    print(point)
    print(point.size)
    print(place)
    print(place.size)
    print(expand_type_as_container(i32))
    print(expand_type_as_container(i_t))
    print(expand_type_as_container(point))
    print(expand_type_as_container(place))
    print(qdataset)
    print(expand_type_as_container(qdataset))
    print(qdataframe)
    print(expand_type_as_container(qdataframe))
    print(type_members_recursive(expand_type_as_container(qdataframe)))
    x0 = VarDef.declare(Symbol("x0"), Symbol("i_t"))
    print(x0)
    x0.assign((Literal("2", Symbol("u32")),), ())
    print(x0)
    print(x0.get())
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
        type_members_recursive(expand_type_as_container(qdataframe)),
    )
    print(qv2)
    print(qv2.get(Symbol("@data")))
    # assert qv2.get(Symbol("@values"))

    qv3 = VarDef.declare(Symbol("@v3"), Symbol("@dataframe"))
    qv3.assign(
        (
            Literal('"df"', Symbol("str")),
            qv1,
        ),
        type_members_recursive(expand_type_as_container(qdataframe)),
    )
    print(qv3)
    assert qv2 == qv3, False
