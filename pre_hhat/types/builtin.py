from abc import ABC, abstractmethod
from ..grammar.ast import AST


class Types(ABC):
    def __init__(self, *value, name=None):
        self._value = value
        self.name = name

    @property
    @abstractmethod
    def value(self):
        ...

    def __iter__(self):
        yield from self.value

    @abstractmethod
    def __add__(self, other):
        ...

    @abstractmethod
    def __repr__(self):
        ...


class Int(Types):
    def __init__(self, value):
        super().__init__(value, name='int')

    @property
    def value(self):
        return int(self._value[0])

    def __add__(self, other):
        pass

    def __repr__(self):
        return f"{self.value}"


class Str(Types):
    def __init__(self, value):
        super().__init__(value, name='str')

    @property
    def value(self):
        return

    def __add__(self, other):
        pass

    def __repr__(self):
        return f"{self.value}"


class Hashmap(Types):
    def __init__(self, *value):
        super().__init__(*value, name='hashmap')

    @property
    def value(self):
        return

    def __add__(self, other):
        pass

    def __repr__(self):
        values = ', '.join([f"{k[0]}:{k[1]}" for k in self])
        return f"({values})"


class Circuit(Types):
    def __init__(self, *value):
        super().__init__(*value, name='circuit')

    @property
    def value(self):
        return

    def __add__(self, other):
        pass

    def format_value_repr(self):
        values = []
        for k in self:
            if isinstance(k, Circuit):
                values.extend(k)
            if isinstance(k, AST):
                values.append(k)
        return values

    def __repr__(self):
        values = self.format_value_repr()
        return f"{values}"
