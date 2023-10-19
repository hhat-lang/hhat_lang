from copy import deepcopy
from typing import Any, Callable, Iterable
from uuid import uuid4, uuid3, NAMESPACE_OID
from dataclasses import dataclass, field
from hhat_lang.syntax_trees.ast import AOT, AST
from hhat_lang.datatypes.builtin_datatype import (
    builtin_array_types_dict
)
from hhat_lang.datatypes.base_datatype import DataType, DataTypeArray


def transform_token_type(data: AOT):
    from hhat_builtin_fn import builtin_fn_dict
    match data.type:
        case "bool":
            return True if data.token == "T" else False if data.token == "F" else None
        case "int":
            return int(data.token)
        case "oper" | "id":
            if data.token in builtin_fn_dict.keys():
                return builtin_fn_dict[data.token]
            return data.token


@dataclass(init=False)
class Data:
    # type: str
    value: tuple[Any]

    def __init__(self, *values: Any):
        self.value = values
        self.id = str(uuid3(NAMESPACE_OID, str(self.value)))

    def format_value(self, value: Any):
        if isinstance(value, tuple):
            return tuple(self.format_value(k) for k in value)
        if isinstance(value, AOT):
            return transform_token_type(value)
        if isinstance(value, AST):
            return (
                tuple(self.format_value(k) for k in value),
                self.format_value(value.node)
            )
        raise NotImplementedError(f"value of type {type(value)}, not implemented!")

    def opers(self, other: "Data", operation: Callable) -> "Data":
        if isinstance(other, Data):
            return Data(*tuple(map(operation, self.value, other.value)))
        raise ValueError(f"wrong type ({type(other)}).")

    def __add__(self, other: "Data") -> "Data":
        return self.opers(other, lambda x, y: x + y)

    def __radd__(self, other: "Data") -> "Data":
        return self.opers(other, lambda x, y: y + x)

    def __mul__(self, other: "Data") -> "Data":
        return self.opers(other, lambda x, y: x * y)

    def __rmul__(self, other: "Data") -> "Data":
        return self.opers(other, lambda x, y: y * x)

    def __str__(self):
        vals = " ".join(str(k) for k in self.value)
        if len(self) > 1:
            return f"({vals})"
        return vals

    def __len__(self) -> int:
        return len(self.value)

    def __iter__(self) -> Iterable:
        yield from self.value


class Var:
    token = "id"

    def __init__(self, name: str):
        self.initialized = False
        self.name = name if name else ""
        self.data = ()
        self.id = str(uuid4())
        self.type = ""

    def analyze_data(self, data: Any) -> Any:
        if isinstance(data, (DataType, DataTypeArray)):
            self.type = data.type
            return data
        if isinstance(data, tuple):
            types = set(k.type for k in data)
            if len(types) == 1 or (len(types) == 2 and "" in types):
                self.type = data[0].type
                return builtin_array_types_dict[self.type](*data)
            else:
                raise NotImplementedError("Var with more than one type not implemented.")
        if isinstance(data, (str, int, bool)):
            raise ValueError("got pure python data on variable. what to do?")
        raise ValueError(f"what is this? {type(data)} | {data}")

    def get_data(self) -> tuple:
        return self.data

    def get(self, item: Any = None) -> Any:
        if item is None:
            return self.get_data()
        return self[item]

    def __call__(self, *values: Any):
        if not self.initialized:
            self.data = self.analyze_data(values)
            self.initialized = True
            return self
        else:
            raise ValueError("Cannot set new values to initialized variable.")

    def __getitem__(self, item: Any) -> Any:
        return self.data[item]

    def __len__(self) -> int:
        return len(self.data)

    def __iter__(self) -> Iterable:
        yield from self.data

    def __repr__(self) -> str:
        content = str(self.data)
        var_type = f"<{self.type}>"
        return "%" + self.name + var_type + (content if self.data else "")


class R:
    def __init__(
            self,
            ast_type: str,
            value: Any,
            is_concurrent: bool,
            role: str,
            execute_after: tuple | None
    ):
        self.type = ast_type
        self.value = value if isinstance(value, tuple) else (value,)
        self.id = str(uuid4())
        self.is_concurrent = is_concurrent
        self.role = role
        self.execute_after = execute_after if execute_after else ()

    def __hash__(self):
        return hash(self.value)

    def __len__(self) -> int:
        return len(self.value)

    def __iter__(self) -> Iterable:
        yield from self.value

    def __repr__(self) -> str:
        return self.type + "(" + " ".join(str(k) for k in self.value) + ")"


class Fn:
    def __init__(self, name: str, args: R | None, body: R):
        self.id = str(uuid4())
        self.name = name
        self.args = args
        self.body = body

    def __repr__(self) -> str:
        args = "(" + " ".join(str(p) for p in self.args) + ")" if self.args is not None else ""
        return f"fn%{self.name}{args}({self.body})"


@dataclass
class Mem:
    parent_id: str = ""
    id: str = field(init=False, default=str(uuid4()))
    data: dict = field(init=False, default_factory=dict)

    def __post_init__(self):
        self.data = self._reset_data()

    @staticmethod
    def _reset_data() -> dict:
        return dict(
            shared=dict(
                stack=(),
                data=(),
                exprs=(),
                vars=dict(),
                fn=dict(),
                main=dict()
            ),
            pvt=dict(
                stack=(),
                data=(),
                exprs=(),
            )
        )

    @property
    def var_list(self) -> tuple:
        return tuple(self.data["shared"]["data"].keys())

    @property
    def fn_list(self) -> tuple:
        return tuple(self.data["shared"]["fn"].keys())

    def pop_stack(self, key: str = "shared") -> Any:
        res = self.data[key]["stack"][-1]
        self.data[key]["stack"] = tuple(self.data[key]["stack"][:-1])
        return res

    def pop_expr(self, key: str = "shared") -> Any:
        res = self.data[key]["exprs"][-1]
        self.data[key]["exprs"] = tuple(self.data[key]["exprs"][:-1])
        return res

    def get_stack(self, key: str = "shared") -> tuple[Any]:
        res = deepcopy(self.data[key]["stack"])
        self.data[key]["stack"] = ()
        return res

    def get_data(self, key: str = "shared") -> tuple[Any]:
        res = deepcopy(self.data[key]["data"])
        self.data[key]["data"] = ()
        return res

    def get_var(self, name: str, key: str = "shared") -> Any:
        return self.data[key]["vars"][name]["data"]

    def get_expr(self, key: str = "shared") -> tuple[Any]:
        expr = self.data[key]["exprs"][-1]
        self.data[key]["exprs"] = tuple(self.data[key]["exprs"][:-1])
        return expr

    def get_fn(self, name: str, n_args: int, args: Any) -> Any:
        # TODO: implement it properly
        # return self.data["shared"]["fn"][n_args]
        raise NotImplemented("Mem.get_fn not implemented yet.")

    def put_stack(self, value: Any, key: str = "shared") -> None:
        self.data[key]["stack"] += value,

    def put_expr(self, value: Any, key: str = "shared") -> None:
        # self.data[key]["exprs"][value.id] = dict(data=value)
        # return value.id
        self.data[key]["exprs"] += value,

    def put_data(self, value: Data | DataType | DataTypeArray, key: str = "shared") -> None:
        self.data[key]["data"] += value,

    def put_var(self, data: Var, scope_id: str, key: str = "shared") -> tuple[str, str]:
        self.data[key]["vars"][data.name] = dict(data=data, scope_id=scope_id)
        return data.id, scope_id

    def put_fn(self, data: Fn):
        # TODO: implement properly how to deal with the data args
        mem_fn = self.data["shared"]["fn"]
        if data.name not in mem_fn:
            mem_fn[data.name] = {len(data.args): {data.args: data.body}}
        else:
            if len(data.args) in mem_fn[data.name]:
                mem_fn[data.name][len(data.args)].update({data.args: data.body})
            else:
                mem_fn[data.name][len(data.args)] = {data.args: data.body}

    def share_stack(self, mem_target: "Mem") -> None:
        mem_target.data["shared"]["stack"] += self.data["shared"]["stack"]

    def share_vars(self, mem_target: "Mem") -> None:
        mem_target.data["shared"]["vars"].update(self.data["shared"]["vars"])

    def share_data(self, mem_target: "Mem") -> None:
        mem_target.data["shared"]["data"] += self.data["shared"]["data"]

    def clear_stack(self, key: str = "shared") -> None:
        self.data[key]["stack"] = ()

    def clear_data(self, key: str = "shared") -> None:
        self.data[key]["data"] = ()

    def clear_var(self, key: str = "shared") -> None:
        self.data[key]["vars"] = dict()

    def clear_exprs(self, key: str = "shared") -> None:
        self.data[key]["exprs"] = ()

    def clear_all(self) -> None:
        self.data = self._reset_data()

    def __contains__(self, item: Any) -> bool:
        return (
            item in self.data["shared"]["stack"]
            or item in self.data["shared"]["data"]
            or item in self.data["shared"]["vars"].keys()
            or item in self.data["shared"]["exprs"]
        )
