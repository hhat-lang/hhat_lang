from typing import Any, Iterable
from uuid import uuid4

from hhat_lang.datatypes import DataType, DataTypeArray, builtin_array_types_dict


def get_var_type(data: Any, types: set[str]) -> str:
    from hhat_lang.builtins.functions import (MetaFn, MetaQFn)

    # TODO: change this to a more general approach in the future
    # to account for more quantum data types
    if isinstance(data, MetaQFn):
        return "@array"
    if isinstance(data, MetaFn):
        raise NotImplementedError(
            "classical data with multiple data and functions not implemented yet."
        )
    raise ValueError(f"Unexpected types {types}.")


class Var:
    """Variable wrapper

    Object to wrap variable and its data.
    """
    token = "id"

    def __init__(self, name: str):
        self.initialized = False
        self.name = name if name else ""
        self.data = ()
        self.id = str(uuid4())
        # TODO: generalize it for any quantum data type
        self.type = "@array" if name.startswith("@") else ""

    def get_data_types(self, data: Any) -> set:
        if isinstance(data, tuple):
            res = set()
            for k in data:
                res.update(self.get_data_types(k))
            return res
        if isinstance(data, str):
            return {data}
        return {data.type}

    def analyze_data(self, data: Any) -> Any:
        if isinstance(data, (DataType, DataTypeArray)):
            if not self.type:
                self.type = data.type
            return data
        if isinstance(data, tuple):
            types = self.get_data_types(data)  # set(k.type for k in data)
            if len(types) == 1 or (len(types) == 2 and "" in types):
                if not self.type:
                    self.type = data[0].type
                return builtin_array_types_dict[self.type](*data)
            else:
                if not self.type:
                    self.type = get_var_type(data, types)
                print(f"analyze data: {data}")
                return builtin_array_types_dict[self.type](*data)
        if isinstance(data, (str, int, bool)):
            raise ValueError("got pure python data on variable. what to do?")

        from hhat_lang.builtins.functions import MetaFn
        from hhat_lang.interpreter.post_ast import R

        if isinstance(data, (R, MetaFn)):
            return data,
        raise ValueError(f"what is this? {type(data)} | {data}")

    def get_data(self) -> tuple:
        return self.data

    def get(self, item: Any = None) -> Any:
        if item is None:
            return self.get_data()
        return self[item]

    def __call__(self, *values: Any):
        if not self.initialized:
            if self.type == "@array":
                print(f"* [@array] var assign -> {type(values)} {values}")
            self.data = self.analyze_data(values)
            print(f"* [var assign] data -> {self.data}")
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
