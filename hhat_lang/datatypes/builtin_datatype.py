from typing import Any

from hhat_lang.datatypes.hhat_base_datatype import DataType, DataTypeArray


################
# SINGLE TYPES #
################

class DefaultType(DataType):
    @property
    def token(self):
        return "default-type"

    @property
    def type(self):
        return "default-type"

    def cast(self) -> Any:
        return self.value

    def __add__(self, other: Any) -> Any:
        raise ValueError(f"cannot add with {self.__class__.__name__}.")

    def __radd__(self, other: Any) -> Any:
        raise ValueError(f"cannot add with {self.__class__.__name__}.")

    def __mul__(self, other: Any) -> Any:
        raise ValueError(f"cannot multiply with {self.__class__.__name__}.")

    def __rmul__(self, other: Any) -> Any:
        raise ValueError(f"cannot multiply with {self.__class__.__name__}.")

    def __repr__(self) -> str:
        return f"<default>{self.data}"


class Bool(DataType):
    undo_bool_dict = {True: "T", False: "F"}
    convert2bool_dict = dict(T=True, F=False)

    @property
    def token(self):
        return "bool"

    @property
    def type(self):
        return "bool"

    def cast(self) -> Any:
        if self.value in self.convert2bool_dict.keys():
            return self.value
        raise ValueError(f"Wrong value for boolean: {self.value}.")

    def __add__(self, other: Any) -> Any:
        if isinstance(other, Bool):
            return Bool(self.convert2bool_dict[self.data] and self.convert2bool_dict[other.data])
        raise ValueError(f"cannot add {self.__class__.__name__} with {other.__class__.__name__}")

    def __radd__(self, other: Any) -> Any:
        if isinstance(other, Bool):
            return Bool(other.data and self.data)
        raise ValueError(f"cannot add {self.__class__.__name__} with {other.__class__.__name__}")

    def __mul__(self, other: Any) -> Any:
        ...

    def __rmul__(self, other: Any) -> Any:
        ...


class Int(DataType):
    @property
    def token(self):
        return "int"

    @property
    def type(self):
        return "int"

    def cast(self) -> Any:
        return int(self.value) if isinstance(self.value, str) else self.value

    def __add__(self, other: Any) -> Any:
        if isinstance(other, Int):
            return Int(self.data + other.data)
        if isinstance(other, IntArray):
            return IntArray(*tuple(map(lambda x: self.data + x, other.data)))
        if isinstance(other, int):
            return Int(self.data + other)
        if isinstance(other, tuple):
            return IntArray(*tuple(map(lambda x: self.data + x.data, other)))
        raise ValueError(f"cannot add {self.__class__.__name__} with {other.__class__.__name__}")

    def __radd__(self, other: Any) -> Any:
        if isinstance(other, Int):
            return Int(other.data + self.data)
        if isinstance(other, IntArray):
            return IntArray(*tuple(map(lambda x: x + self.data, other.data)))
        if isinstance(other, int):
            return Int(other + self.data)
        if isinstance(other, tuple):
            return IntArray(*tuple(map(lambda x: x.data + self.data, other)))
        raise ValueError(f"cannot add {self.__class__.__name__} with {other.__class__.__name__}")

    def __mul__(self, other: Any) -> Any:
        if isinstance(other, Int):
            return Int(self.data * other.data)
        if isinstance(other, IntArray):
            return IntArray(*tuple(map(lambda x: self.data * x, other.data)))
        if isinstance(other, int):
            return Int(self.data * other)
        raise ValueError(f"cannot multiply {self.__class__.__name__} with {other.__class__.__name__}")

    def __rmul__(self, other: Any) -> Any:
        if isinstance(other, Int):
            return Int(other.data * self.data)
        if isinstance(other, IntArray):
            return IntArray(*tuple(map(lambda x: x * self.data, other.data)))
        if isinstance(other, int):
            return Int(other * self.data)
        raise ValueError(f"cannot multiply {self.__class__.__name__} with {other.__class__.__name__}")


###############
# ARRAY TYPES #
###############

class BoolArray(DataTypeArray):
    bool_dict = dict(T=True, F=False)

    @property
    def token(self):
        return "bool-array"

    @property
    def type(self):
        return "bool"

    def cast(self) -> Any:
        return tuple(Bool(k) for k in self.value)

    def __add__(self, other: Any) -> Any:
        if isinstance(other, BoolArray):
            return BoolArray(*tuple(map(lambda x, y: x and y, self.data, other.data)))

    def __radd__(self, other: Any) -> Any:
        if isinstance(other, BoolArray):
            return BoolArray(*tuple(map(lambda x, y: x and y, other.data, self.data)))

    def __mul__(self, other: Any) -> Any:
        ...

    def __rmul__(self, other: Any) -> Any:
        ...


class IntArray(DataTypeArray):
    @property
    def token(self):
        return "int-array"

    @property
    def type(self):
        return "int"

    def cast(self):
        res = ()
        for k in self.value:
            if isinstance(k, IntArray):
                res += tuple(Int(p) for p in k)
            elif isinstance(k, Int):
                res += Int(k),
        return res

    def __add__(self, other: Any) -> Any:
        if isinstance(other, IntArray):
            return IntArray(*tuple(map(lambda x, y: x + y, self.data, other.data)))
        if isinstance(other, Int):
            return IntArray(*tuple(map(lambda x: x + other.data, self.data)))
        print(f"* [add] what is other? {type(other)} {other}")

    def __radd__(self, other: Any) -> Any:
        if isinstance(other, IntArray):
            return IntArray(*tuple(map(lambda x, y: x + y, other.data, self.data)))
        if isinstance(other, Int):
            return IntArray(*tuple(map(lambda x: other.data + x, self.data)))
        print(f"* [radd] what is other? {type(other)} {other}")

    def __mul__(self, other: Any) -> Any:
        if isinstance(other, IntArray):
            print(f"mult int array: {self.data} ({type(self.data)}) | {other.data} ({type(other.data)})")
            return IntArray(*tuple(map(lambda x, y: x * y, self.data, other.data)))
        if isinstance(other, Int):
            return IntArray(*tuple(map(lambda x: x * other.data, self.data)))
        print(f"* [mul] mult int array: {self.data} ({type(self.data)}) | {other.data} ({type(other.data)})")

    def __rmul__(self, other: Any) -> Any:
        if isinstance(other, IntArray):
            print(f"mult int array: {self.data} ({type(self.data)}) | {other.data} ({type(other.data)})")
            return IntArray(*tuple(map(lambda x, y: x + y, other.data, self.data)))
        if isinstance(other, Int):
            return IntArray(*tuple(map(lambda x: other.data * x, self.data)))
        print(f"* [rmul] mult int array: {self.data} ({type(self.data)}) | {other.data} ({type(other.data)})")


class QArray(DataTypeArray):
    @property
    def token(self) -> str:
        return "@array"

    @property
    def type(self) -> str:
        return "@array"

    def cast(self) -> tuple[Any]:
        return tuple(k for k in self.value)

    def __add__(self, other: Any) -> Any:
        if isinstance(other, QArray):
            self.data += other,
            return self
        if isinstance(other, Int):
            # TODO: implement the casting
            return
        if isinstance(other, IntArray):
            # TODO: implement the casting
            return
        if isinstance(other, Bool):
            # TODO: implement the casting
            return
        if isinstance(other, BoolArray):
            # TODO: implement the casting
            return

        from hhat_lang.interpreter import R

        if isinstance(other, R):
            self.data += other,
            return self

    def __radd__(self, other):
        if isinstance(other, QArray):
            other.data += self.data
            return other
        if isinstance(other, Int):
            # TODO: implement the casting
            return
        if isinstance(other, IntArray):
            # TODO: implement the casting
            return
        if isinstance(other, Bool):
            # TODO: implement the casting
            return
        if isinstance(other, BoolArray):
            # TODO: implement the casting
            return

        from hhat_lang.interpreter import R

        if isinstance(other, R):
            self.data += other,
            return self

    def __mul__(self, other):
        if isinstance(other, QArray):
            pass
        if isinstance(other, Int):
            # TODO: implement the casting
            return
        if isinstance(other, IntArray):
            # TODO: implement the casting
            return
        if isinstance(other, Bool):
            # TODO: implement the casting
            return
        if isinstance(other, BoolArray):
            # TODO: implement the casting
            return

        from hhat_lang.interpreter import R

        if isinstance(other, R):
            pass

    def __rmul__(self, other):
        if isinstance(other, QArray):
            pass
        if isinstance(other, Int):
            # TODO: implement the casting
            return
        if isinstance(other, IntArray):
            # TODO: implement the casting
            return
        if isinstance(other, Bool):
            # TODO: implement the casting
            return
        if isinstance(other, BoolArray):
            # TODO: implement the casting
            return

        from hhat_lang.interpreter import R

        if isinstance(other, R):
            pass


builtin_data_types_dict = {
    "bool": Bool,
    "int": Int,
}
builtin_array_types_dict = {
    "bool": BoolArray,
    "int": IntArray,
    "@array": QArray,
}
data_types_list = tuple(builtin_data_types_dict.keys())
array_types_list = tuple(builtin_array_types_dict.keys())
