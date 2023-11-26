from __future__ import annotations
from typing import Any

from copy import deepcopy
from hhat_lang.datatypes import DataType, DataTypeArray
from hhat_lang.syntax_trees.ast import ASTType, DataTypeEnum
from hhat_lang.builtins.type_tokens import TypeToken
from hhat_lang.interpreter.post_ast import R, ATO


################
# SINGLE TYPES #
################

class DefaultType(DataType):
    @property
    def token(self):
        return TypeToken.DEFAULT

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
        return TypeToken.BOOLEAN

    @property
    def type(self):
        return DataTypeEnum.BOOL

    def cast(self) -> Any:
        if self.value in self.convert2bool_dict.keys():
            return self.value
        raise ValueError(f"Wrong value for boolean: {self.value}.")

    def __add__(self, other: Any) -> Any:
        if isinstance(other, Bool):
            return Bool(self.convert2bool_dict[self.data] and self.convert2bool_dict[other.data])
        if isinstance(other, BoolArray):
            return BoolArray(
                *tuple(map(
                    lambda x: self.convert2bool_dict[self.data] and self.convert2bool_dict[x],
                    other.data
                ))
            )
        raise ValueError(f"cannot add {self.__class__.__name__} with {other.__class__.__name__}")

    def __radd__(self, other: Any) -> Any:
        if isinstance(other, Bool):
            return Bool(self.convert2bool_dict[other.data] and self.convert2bool_dict[self.data])
        if isinstance(other, BoolArray):
            return BoolArray(
                *tuple(map(
                    lambda x: self.convert2bool_dict[x] and self.convert2bool_dict[self.data],
                    other.data
                ))
            )
        raise ValueError(f"cannot add {self.__class__.__name__} with {other.__class__.__name__}")

    def __mul__(self, other: Any) -> Any:
        if isinstance(other, Bool):
            return Bool(self.convert2bool_dict[self.data] or self.convert2bool_dict[other.data])
        if isinstance(other, BoolArray):
            return BoolArray(
                *tuple(map(
                    lambda x: self.convert2bool_dict[self.data] or self.convert2bool_dict[x],
                    other.data
                ))
            )
        raise ValueError(f"cannot multiply {self.__class__.__name__} with {other.__class__.__name__}")

    def __rmul__(self, other: Any) -> Any:
        if isinstance(other, Bool):
            return Bool(self.convert2bool_dict[other.data] or self.convert2bool_dict[self.data])
        if isinstance(other, BoolArray):
            return BoolArray(
                *tuple(map(
                    lambda x: self.convert2bool_dict[x] or self.convert2bool_dict[self.data],
                    other.data
                ))
            )
        raise ValueError(f"cannot multiply {self.__class__.__name__} with {other.__class__.__name__}")


class Int(DataType):
    @property
    def token(self):
        return TypeToken.INTEGER

    @property
    def type(self):
        return DataTypeEnum.INT

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


class Atomic(DataType):
    @property
    def token(self):
        return TypeToken.ATOMIC

    @property
    def type(self):
        return DataTypeEnum.ATOMIC

    def cast(self) -> str:
        if isinstance(self.value, str):
            return str(self.value)
        if isinstance(self.value, ATO):
            return self.value.token
        raise ValueError(f"Casting to Atomic not found for {self.value}.")

    def __add__(self, other: Any) -> Any:
        if isinstance(other, Atomic):
            return AtomicArray(*tuple(map(lambda x: x, (self.data,) + (other.data,))))
        if isinstance(other, AtomicArray):
            return AtomicArray(*tuple(map(lambda x: x, (self.data,) + other.data)))

    def __radd__(self, other: Any) -> Any:
        pass

    def __mul__(self, other: Any) -> Any:
        pass

    def __rmul__(self, other: Any) -> Any:
        pass


###############
# ARRAY TYPES #
###############

class BoolArray(DataTypeArray):
    bool_dict = dict(T=True, F=False)

    @property
    def token(self):
        return TypeToken.BOOLEAN_ARRAY

    @property
    def type(self):
        return DataTypeEnum.BOOL

    def cast(self) -> Any:
        return tuple(Bool(k) for k in self.value)

    def __add__(self, other: Any) -> Any:
        if isinstance(other, BoolArray):
            return BoolArray(*tuple(map(lambda x, y: x + y, self.data, other.data)))

    def __radd__(self, other: Any) -> Any:
        if isinstance(other, BoolArray):
            return BoolArray(*tuple(map(lambda x, y: x + y, other.data, self.data)))

    def __mul__(self, other: Any) -> Any:
        if isinstance(other, BoolArray):
            return BoolArray(*tuple(map(lambda x, y: x * y, self.data, other.data)))

    def __rmul__(self, other: Any) -> Any:
        if isinstance(other, BoolArray):
            return BoolArray(*tuple(map(lambda x, y: x * y, other.data, self.data)))


class IntArray(DataTypeArray):
    @property
    def token(self):
        return TypeToken.INTEGER_ARRAY

    @property
    def type(self):
        return DataTypeEnum.INT

    def cast(self):
        res = ()
        for k in self.value:
            if isinstance(k, IntArray):
                res += tuple(Int(p) for p in k)
            elif isinstance(k, Int):
                res += Int(k),
            else:
                res += k,
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


class AtomicArray(DataTypeArray):
    @property
    def token(self):
        return TypeToken.ATOMIC_ARRAY

    @property
    def type(self):
        return DataTypeEnum.ATOMIC

    def cast(self) -> Any:
        res = ()
        for k in self.value:
            if isinstance(k, Atomic):
                res += k,
            elif isinstance(k, AtomicArray):
                res += k.data
            else:
                raise ValueError(f"Casting to AtomicArray on unknown data {k}.")
        return res

    def __add__(self, other: Any) -> Any:
        if isinstance(other, Atomic):
            return AtomicArray(*(self.data + (other.data,)))
        if isinstance(other, AtomicArray):
            return AtomicArray(*(self.data + other.data))
        raise ValueError(f"AtomicArray add method on unknown data {other}.")

    def __radd__(self, other: Any) -> Any:
        if isinstance(other, Atomic):
            return AtomicArray(*((other.data,) + self.data))
        if isinstance(other, AtomicArray):
            return AtomicArray(*(other.data + self.data))
        raise ValueError(f"AtomicArray add method on unknown data {other}.")

    def __mul__(self, other: Any) -> Any:
        raise NotImplementedError("Multiplication of AtomicArray not implemented.")

    def __rmul__(self, other: Any) -> Any:
        raise NotImplementedError("Multiplication of AtomicArray not implemented.")


class Hashmap(DataTypeArray):
    @property
    def token(self):
        return TypeToken.HASHMAP

    @property
    def type(self):
        return DataTypeEnum.HASHMAP

    def cast(self) -> Any:
        res = dict()
        for k in self.value:
            if isinstance(k[0], Atomic):
                res.update({k[0]: k[1]})
            else:
                raise ValueError(f"Casting to Hashmap error: unknown '{k[0]}' key.")
        return res

    @staticmethod
    def _add_fn(self: Hashmap, second: Hashmap) -> Hashmap:
        first_data = deepcopy(self.data)
        second_data = deepcopy(second.data)
        first_data.update(second_data)
        return Hashmap(*first_data.items())

    def __add__(self, other: Any) -> Any:
        if isinstance(other, Hashmap):
            return self._add_fn(self, other)
        raise ValueError(f"Cannot add {self.__class__.__name__} and {other.__class__.__name__}.")

    def __radd__(self, other: Any) -> Any:
        if isinstance(other, Hashmap):
            return self._add_fn(other, self)
        raise ValueError(f"Cannot add {self.__class__.__name__} and {other.__class__.__name__}.")

    def __mul__(self, other):
        pass

    def __rmul__(self, other):
        pass


class MultiTypeArray(DataTypeArray):
    @property
    def token(self):
        return TypeToken.MULTI_ARRAY

    @property
    def type(self):
        return ASTType.ARRAY

    def cast(self) -> Any:
        pass

    def __add__(self, other):
        raise NotImplementedError("Addition not implemented for multi-array.")

    def __radd__(self, other):
        raise NotImplementedError("Addition not implemented for multi-array.")

    def __mul__(self, other):
        raise NotImplementedError("Multiplication not implemented for multi-array.")

    def __rmul__(self, other):
        raise NotImplementedError("Multiplication not implemented for multi-array.")


class QArray(DataTypeArray):
    @property
    def token(self) -> str:
        return TypeToken.Q_ARRAY

    @property
    def type(self) -> str:
        return DataTypeEnum.Q_ARRAY

    def cast(self) -> tuple[Any]:
        print(f">>> cast @array -> {self.value}")
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

        from hhat_lang.builtins.functions import MetaQFn

        if isinstance(other, MetaQFn):
            self.data += other,
            return self

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

        if isinstance(other, R):
            pass


builtin_data_types_dict = {
    DataTypeEnum.BOOL: Bool,
    DataTypeEnum.INT: Int,
    DataTypeEnum.ATOMIC: Atomic,
}
builtin_classical_array_types_dict = {
    DataTypeEnum.BOOL: BoolArray,
    DataTypeEnum.INT: IntArray,
    DataTypeEnum.ATOMIC: AtomicArray,
    DataTypeEnum.HASHMAP: Hashmap,
    ASTType.ARRAY: MultiTypeArray,
}
builtin_quantum_array_types_dict = {
    DataTypeEnum.Q_ARRAY: QArray,
}
builtin_array_types_dict = {
    **builtin_classical_array_types_dict,
    **builtin_quantum_array_types_dict,
}
data_types_list = tuple(builtin_data_types_dict.keys())
classical_array_types_list = tuple(builtin_classical_array_types_dict.keys())
quantum_array_types_list = tuple(builtin_quantum_array_types_dict.keys())
array_types_list = tuple(builtin_array_types_dict.keys())
