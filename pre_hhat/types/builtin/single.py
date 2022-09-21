from pre_hhat.types import groups as group
from pre_hhat.types.builtin import (
    ArrayInt,
    ArrayCircuit,
    ArrayStr,
    ArrayBool,
    ArrayNull,
    ArrayHashmap,
)


class SingleInt(group.SingleMorpher):
    def __init__(self, value):
        super().__init__(value, type_name=SingleInt)

    def _format_value(self, value):
        if isinstance(value, str):
            if value.isdigit():
                return [int(value)]
        if isinstance(value, int):
            return [value]
        if isinstance(value, SingleInt):
            return [value.value[0]]
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
        raise NotImplemented(
            f"{self.name}: operation not implemented for {self.name} and {other.name}."
        )

    def __ge__(self, other):
        if isinstance(other, SingleInt):
            return self.value[0] >= other.value[0]
        raise NotImplemented(
            f"{self.name}: operation not implemented for {self.name} and {other.name}."
        )

    def __lt__(self, other):
        if isinstance(other, SingleInt):
            return self.value[0] < other.value[0]
        raise NotImplemented(
            f"{self.name}: operation not implemented for {self.name} and {other.name}."
        )

    def __le__(self, other):
        if isinstance(other, SingleInt):
            return self.value[0] <= other.value[0]
        raise NotImplemented(
            f"{self.name}: operation not implemented for {self.name} and {other.name}."
        )

    def __add__(self, other):
        if isinstance(other, int):
            return self.__class__(self.value[0] + other)
        if isinstance(other, SingleInt):
            return self.__class__(self.value[0] + other.value[0])
        if isinstance(other, ArrayInt):
            return other + self.value[0]
        if isinstance(other, SingleNull):
            return self
        if isinstance(other, ArrayCircuit):
            raise NotImplemented(f"{self.name}: need to implement addition with circuit type.")
        other_name = other.__class__.__name__
        raise NotImplemented(
            f"{self.name}: operation not implemented for {self.name} and {other_name}."
        )


class SingleStr(group.SingleAppender):
    def __init__(self, value):
        super().__init__(value, type_name=SingleStr)

    def _format_value(self, value):
        if isinstance(value, str):
            return [value]
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
        if isinstance(other, ArrayStr):
            return self.value[0] + other
        if isinstance(other, SingleNull):
            return self
        if isinstance(other, ArrayCircuit):
            raise NotImplemented(f"{self.name}: need to implement addition with circuit type.")
        raise NotImplemented(
            f"{self.name} not implemented addition with {other.__class__.__name__}."
        )

    def __repr__(self):
        return f"{self.value[0]}"


class SingleBool(group.SingleMorpher):
    bool_values = {True: "T", False: "F"}
    str_values = {"T": True, "F": False}

    def __init__(self, value):
        super().__init__(value, type_name=SingleBool)

    def _format_value(self, value):
        if isinstance(value, bool):
            return [self.bool_values[value]]
        if isinstance(value, str):
            if value in ["T", "F"]:
                return [value]
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
        raise NotImplemented(
            f"{self.name}: not implemented addition with {other.__class__.__name__}."
        )

    def __repr__(self):
        return f"{self.value[0]}"


class SingleHashmap(group.SingleAppender):
    def __init__(self, value):
        super().__init__(value, type_name=SingleHashmap)

    def _format_value(self, value):
        try:
            return (dict(value),)
        except TypeError:
            raise ValueError(f"{self.__class__.__name__}: wrong input value.")

    def __iter__(self):
        yield from self.value[0].items()

    def __len__(self):
        return len(self.value[0].keys())

    def __getitem__(self, item):
        return self.value[0].get(item, None)

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
            return ArrayHashmap(*(tuple(self) + tuple(other)))
        if isinstance(other, ArrayCircuit):
            raise NotImplemented(f"{self.name}: not implemented addition with circuit yet.")
        raise NotImplemented(
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
        return hash((self.name, self.value[0]))

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
