import pre_hhat.types.groups as group
import pre_hhat.types as types
import pre_hhat.core.utils as utils


def get_single(data):
    data_types = {
        int: SingleInt,
        str: StrDisambiguation,
        bool: SingleBool,
        dict: SingleHashmap,
        None: SingleNull,
    }
    return data_types.get(data, False)


class StrDisambiguation:
    def __new__(cls, data, **kwargs):
        if data.startswith('"') or data.startswith("'"):
            return SingleStr(data)
        if data.startswith("0b"):
            return SingleBin(data)
        if data.startswith("0x"):
            return SingleHex(data)
        raise ValueError(f"{cls.__class__.__name__}: cannot generate data type for {data}.")


class SingleInt(group.SingleMorpher):
    def __init__(self, value=None):
        super().__init__(value, type_name=SingleInt)

    def _format_value(self, value):
        if isinstance(value, str):
            if value.isdigit():
                return [int(value)]
        if isinstance(value, int):
            return [value]
        if isinstance(value, SingleInt):
            return [value.value[0]]
        if value is None:
            return [0]
        raise ValueError(f"{self.name}: can only receive integer data.")

    def __hash__(self):
        return hash((self.name, self.value[0]))

    def __getitem__(self, item):
        return self.value[0]

    def __eq__(self, other):
        if isinstance(other, SingleInt):
            return self.value == other.value
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        if isinstance(other, SingleInt):
            return self.value[0] > other.value[0]
        raise NotImplementedError(
            f"{self.name}: operation not implemented for {self.name} and {other.name}."
        )

    def __ge__(self, other):
        if isinstance(other, SingleInt):
            return self.value[0] >= other.value[0]
        raise NotImplementedError(
            f"{self.name}: operation not implemented for {self.name} and {other.name}."
        )

    def __lt__(self, other):
        if isinstance(other, SingleInt):
            return self.value[0] < other.value[0]
        raise NotImplementedError(
            f"{self.name}: operation not implemented for {self.name} and {other.__class__.__name__}."
        )

    def __le__(self, other):
        if isinstance(other, SingleInt):
            return self.value[0] <= other.value[0]
        raise NotImplementedError(
            f"{self.name}: operation not implemented for {self.name} and {other.name}."
        )

    def __add__(self, other):
        if isinstance(other, int):
            return self.__class__(self.value[0] + other)
        if isinstance(other, SingleInt):
            return self.__class__(self.value[0] + other.value[0])
        if isinstance(other, types.ArrayInt):
            for n, k in enumerate(other):
                other.value[n] += self.value[0]
            return other
        if isinstance(other, SingleNull):
            return self
        if isinstance(other, tuple):
            value, stack = other
            res = types.circuit_transform(value, stack)
            new_value = self.value[0] + round(res)
            return self.__class__(new_value)
        raise NotImplementedError(
            f"{self.name}: operation not implemented for {self.name} and {other.__class__.__name__}."
        )


class SingleStr(group.SingleAppender):
    def __init__(self, value=None):
        super().__init__(value, type_name=SingleStr)

    def _format_value(self, value):
        if isinstance(value, str):
            return [value]
        if value is None:
            return [""]
        raise ValueError(f"{self.name}: can only receive string data.")

    def __hash__(self):
        return hash((self.name, self.value[0]))

    def __getitem__(self, item):
        return self.value[0].strip('"').strip("'")

    def __eq__(self, other):
        if isinstance(other, SingleStr):
            return self.value[0] == other.value[0]
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        if isinstance(other, SingleStr):
            return len(self) > len(other)
        return False

    def __ge__(self, other):
        if isinstance(other, SingleStr):
            return len(self) >= len(other)
        return False

    def __lt__(self, other):
        if isinstance(other, SingleStr):
            return len(self) < len(other)
        return False

    def __le__(self, other):
        if isinstance(other, SingleStr):
            return len(self) <= len(other)
        return False

    def __add__(self, other):
        if isinstance(other, str):
            return self.__class__(self.value[0] + other)
        if isinstance(other, SingleStr):
            return self.__class__(self.value[0] + other.value[0])
        if isinstance(other, types.ArrayStr):
            vals = ()
            for n in range(len(other)):
                vals += (self.value[0] + other.value[n],)
            return other.__class__(*vals)
        if isinstance(other, SingleNull):
            return self
        if isinstance(other, types.ArrayCircuit):
            raise NotImplementedError(f"{self.name}: need to implement addition with circuit type.")
        raise NotImplementedError(
            f"{self.name} not implemented addition with {other.__class__.__name__}."
        )

    def __repr__(self):
        return f"{self.value[0]}"


class SingleBin(group.SingleMorpher):
    def __init__(self, value=None):
        super().__init__(value, type_name=SingleBin)

    def _format_value(self, value):
        if isinstance(value, (str, int)):
            return [utils.get_hex(value)]
        if isinstance(value, (SingleInt, SingleHex)):
            return [utils.get_hex(value.value)]
        if isinstance(value, SingleBin):
            return [value.value]
        if value is None:
            return ["0b0"]
        raise ValueError(f"{self.name}: wrong type {value.__class.__name__}.")

    def __hash__(self):
        return hash((self.name, self.value[0]))

    def __getitem__(self, item):
        return self.value[0]

    def __eq__(self, other):
        if isinstance(other, SingleBin):
            return self.value[0] == other.value[0]
        if isinstance(other, (SingleInt, SingleHex)):
            return int(self.value[0]) == int(other.value[0])
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        if isinstance(other, SingleBin):
            return self.value[0] > other.value[0]
        if isinstance(other, SingleInt):
            return int(self.value[0]) > other.value[0]
        if isinstance(other, SingleHex):
            return int(self.value[0]) > int(self.value[0])
        else:
            return False

    def __ge__(self, other):
        if isinstance(other, SingleBin):
            return self.value[0] >= other.value[0]
        if isinstance(other, SingleInt):
            return int(self.value[0]) >= other.value[0]
        if isinstance(other, SingleHex):
            return int(self.value[0]) >= int(self.value[0])
        else:
            return False

    def __lt__(self, other):
        if isinstance(other, SingleBin):
            return self.value[0] < other.value[0]
        if isinstance(other, SingleInt):
            return int(self.value[0]) < other.value[0]
        if isinstance(other, SingleHex):
            return int(self.value[0]) < int(self.value[0])
        else:
            return False

    def __le__(self, other):
        if isinstance(other, SingleBin):
            return self.value[0] <= other.value[0]
        if isinstance(other, SingleInt):
            return int(self.value[0]) <= other.value[0]
        if isinstance(other, SingleHex):
            return int(self.value[0]) <= int(self.value[0])
        else:
            return False

    def __add__(self, other):
        if isinstance(other, (SingleHex, SingleBin, SingleInt)):
            return self.__class__(int(self.value[0]) + int(other.value[0]))
        if isinstance(other, (SingleNull, types.ArrayNull)):
            return self
        if isinstance(other, types.ArrayCircuit):
            raise NotImplementedError(f"{self.name}: not implemented adding with circuit type yet.")
        raise NotImplementedError(
            f"{self.name}: not implemented adding with {other.__class__.__name__}."
        )

    def __repr__(self):
        return f"{self.value[0]}"


class SingleHex(group.SingleMorpher):
    def __init__(self, value=None):
        super().__init__(value, type_name=SingleHex)

    def _format_value(self, value):
        if isinstance(value, (str, int)):
            return [utils.get_hex(value)]
        if isinstance(value, (SingleInt, SingleBin)):
            return [utils.get_hex(value.value)]
        if isinstance(value, SingleHex):
            return [value.value]
        if value is None:
            return ["0x0"]
        raise ValueError(f"{self.name}: wrong type {value.__class.__name__}.")

    def __hash__(self):
        return hash((self.name, self.value[0]))

    def __getitem__(self, item):
        return self.value[0]

    def __eq__(self, other):
        if isinstance(other, SingleHex):
            return self.value[0] == other.value[0]
        if isinstance(other, (SingleInt, SingleBin)):
            return int(self.value[0]) == int(other.value[0])
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        if isinstance(other, SingleHex):
            return self.value[0] > other.value[0]
        if isinstance(other, SingleInt):
            return int(self.value[0]) > other.value[0]
        if isinstance(other, SingleBin):
            return int(self.value[0]) > int(self.value[0])
        else:
            return False

    def __ge__(self, other):
        if isinstance(other, SingleHex):
            return self.value[0] >= other.value[0]
        if isinstance(other, SingleInt):
            return int(self.value[0]) >= other.value[0]
        if isinstance(other, SingleBin):
            return int(self.value[0]) >= int(self.value[0])
        else:
            return False

    def __lt__(self, other):
        if isinstance(other, SingleHex):
            return self.value[0] < other.value[0]
        if isinstance(other, SingleInt):
            return int(self.value[0]) < other.value[0]
        if isinstance(other, SingleBin):
            return int(self.value[0]) < int(self.value[0])
        else:
            return False

    def __le__(self, other):
        if isinstance(other, SingleHex):
            return self.value[0] <= other.value[0]
        if isinstance(other, SingleInt):
            return int(self.value[0]) <= other.value[0]
        if isinstance(other, SingleBin):
            return int(self.value[0]) <= int(self.value[0])
        else:
            return False

    def __add__(self, other):
        if isinstance(other, (SingleHex, SingleBin, SingleInt)):
            return self.__class__(int(self.value[0]) + int(other.value[0]))
        if isinstance(other, (SingleNull, types.ArrayNull)):
            return self
        if isinstance(other, types.ArrayCircuit):
            raise NotImplementedError(f"{self.name}: not implemented adding with circuit type yet.")
        raise NotImplementedError(
            f"{self.name}: not implemented adding with {other.__class__.__name__}."
        )

    def __repr__(self):
        return f"{self.value[0]}"


class SingleBool(group.SingleMorpher):
    bool_values = {True: "T", False: "F"}
    str_values = {"T": True, "F": False}

    def __init__(self, value=None):
        super().__init__(value, type_name=SingleBool)

    def _format_value(self, value):
        if isinstance(value, bool):
            return [self.bool_values[value]]
        if isinstance(value, str):
            if value in ["T", "F"]:
                return [value]
        if value is None:
            return ["T"]
        raise ValueError(f"{self.name}: can only receive boolean data (T or F).")

    def __hash__(self):
        return hash((self.name, self.value[0]))

    def __getitem__(self, item):
        return self.value[0].strip('"').strip("'")

    def __eq__(self, other):
        if isinstance(other, SingleBool):
            return self.value == other.value
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        return False

    def __ge__(self, other):
        return False

    def __lt__(self, other):
        return False

    def __le__(self, other):
        return False

    def __bool__(self):
        return self.str_values[self.value[0]]

    def __add__(self, other):
        if isinstance(other, str):
            if other in ["T", "F"]:
                if other == "T" and self.value[0] == "T":
                    return self.__class__("T")
                return self.__class__("F")
            raise ValueError(f"{self.name}: addition must be between booleans.")
        if isinstance(other, SingleBool):
            if self == other and other.value[0] == "T":
                return self.__class__("T")
            else:
                return self.__class__("F")
        if isinstance(other, SingleNull):
            return self
        raise NotImplementedError(
            f"{self.name}: not implemented addition with {other.__class__.__name__}."
        )

    def __repr__(self):
        return f"{self.value[0]}"


class SingleHashmap(group.SingleAppender):
    def __init__(self, value=None):
        super().__init__(value, type_name=SingleHashmap)

    def _format_value(self, value):
        if isinstance(value, tuple):
            return [{to_single(p[0]): to_single(p[1]) for p in value}]
        if value is None:
            return [dict()]
        raise ValueError(f"{self.__class__.__name__}: wrong input value.")

    def __iter__(self):
        yield from self.value[0].items()

    def __len__(self):
        return len(self.value[0].keys())

    def __getitem__(self, item):
        return self.value[0].get(item, SingleNull())

    def __eq__(self, other):
        if self == other:
            return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        if isinstance(other, SingleHashmap):
            if len(self) > len(other):
                return True
        return False

    def __ge__(self, other):
        if isinstance(other, SingleHashmap):
            if len(self) >= len(other):
                return True
        return False

    def __lt__(self, other):
        if isinstance(other, SingleHashmap):
            if len(self) < len(other):
                return True
        return False

    def __le__(self, other):
        if isinstance(other, SingleHashmap):
            if len(self) <= len(other):
                return True
        return False

    def __add__(self, other):
        if isinstance(other, SingleHashmap):
            return self.__class__(*(tuple(self) + tuple(other)))
        if isinstance(other, types.ArrayCircuit):
            raise NotImplementedError(f"{self.name}: not implemented addition with circuit yet.")
        raise NotImplementedError(
            f"{self.name}: not implemented addition with {other.__class__.__name__}."
        )

    def __repr__(self):
        values = ", ".join([f"{k}:{v}" for k, v in self])
        return f"({values})"


class SingleNull(group.SingleNuller):
    def __init__(self):
        super().__init__(SingleNull)

    def _format_value(self, value):
        return []

    def __hash__(self):
        return hash(self.name)

    def __getitem__(self, item):
        return "null"

    def __eq__(self, other):
        if isinstance(other, SingleNull):
            return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        return None

    def __ge__(self, other):
        return None

    def __lt__(self, other):
        return None

    def __le__(self, other):
        return None

    def __add__(self, other):
        return other

    def __iadd__(self, other):
        return other


def to_single(data):
    res = get_single(type(data))
    if res:
        return res(data)
    raise ValueError("Invalid data type to be transformed.")
