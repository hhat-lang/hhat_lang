from abc import ABC, abstractmethod


class Gate(ABC):
    def __init__(self, *value, name: str = None, ct=None, **kwargs):
        if len(set(value)) == len(value):
            self.name = name
            self.raw_indices = value
            self.indices = self._format_indices(value)
            self.raw_value = value
            self.value = self._format_value(value)
            self.ct = self._format_ct(ct)
        else:
            raise ValueError("Gate: can only have unique indices.")

    def flatten(self, *value):
        res = ()
        for k in value:
            if isinstance(k, tuple):
                res += self.flatten(*k)
            elif isinstance(k, int):
                res += k,
        return res

    def __iter__(self):
        yield from self.value.items()

    @abstractmethod
    def _format_value(self, value):
        ...

    def _format_indices(self, value):
        return self.flatten(*value)

    @staticmethod
    def _format_ct(value):
        return value

    def __add__(self, other):
        if isinstance(other, self.__class__) and \
            not set(self.indices).intersection(set(other.indices)) and \
            self.name == other.name:
            return self.__class__(*(self.indices + other.indices), name=self.name, ct=self.ct)
        return GateArray(self.__class__(*self.indices, name=self.name, ct=self.ct),
                         other.__class__(*other.indices, name=other.name, ct=other.ct))

    def __repr__(self):
        value = self.flatten(*self.value)
        if self.ct is not None:
            values = []
            value_len = sum(self.ct)
            for k in range(value_len):
                c_start = k * value_len
                c_end = k * value_len + self.ct[0]
                indices = ' '.join([str(k) for k in value[c_start:c_end]])
                if not indices:
                    break
                control = '(' + indices + ')' if len(value[c_start:c_end]) > 1 else indices
                t_start = k * value_len + self.ct[0]
                t_end = k * value_len + self.ct[0] + self.ct[1]
                indices = ' '.join([str(k) for k in value[t_start:t_end]])
                target = '(' + indices + ')' if len(value[t_start:t_end]) > 1 else indices
                values.append(f"{self.name}(c:{control}, t:{target})")
            return " ".join(values)
        else:
            if self.name is not None:
                return " ".join([f"{self.name}({k})" for k in value])
            else:
                return "(" + " ".join([str(k) for k in value]) + ")"


class GateArray:
    def __init__(self, *value, **kwargs):
        self.value = self._format_value(value)
        self.raw_indices = self._format_raw_indices(value)
        self.indices = self._format_indices(value)
        self.ct = self._format_ct(value)

    @staticmethod
    def _format_value(value):
        res = []
        for n, k in enumerate(value):
            if 1 < n < len(value):
                if set(res[n - 1].indices).intersection(set(k.indices)):
                    res[n - 1] = res[n - 1] + k.__class__(*k.indices, name=k.name, ct=k.ct)
                else:
                    res.append(k)
            else:
                res.append(k)
        return res

    @staticmethod
    def _format_indices(value):
        res = set()
        for k in value:
            res.update(k.indices)
        return tuple(res)

    @staticmethod
    def _format_raw_indices(value):
        return tuple((k.raw_indices,) for k in value)

    @staticmethod
    def _format_ct(value):
        return tuple(k.ct for k in value)

    def __repr__(self):
        values = ', '.join([str(k) for k in self.value])
        return f"{values}"


class SingleIndexGate(Gate):
    def __init__(self, *value, name=None, **kwargs):
        if name is not None:
            super().__init__(*value, name=name)
        else:
            raise ValueError(f"{self.__class__.__name__}: must have a name.")

    def _format_value(self, value):
        return {k: self.name for k in value}


class MultipleIndexGate(Gate):
    def __init__(self, *value, name=None):
        if name is not None and len(value) > 1:
            super().__init__(*value, name=name)
        else:
            raise ValueError(f"{self.__class__.__name__}: must have a name and many indices.")

    def _format_value(self, value):
        return {value: self.name}


class ControlTargetGate(Gate):
    def __init__(self, *value, name=None, ct=None):
        if ct is not None and name is not None:
            super().__init__(*value, name=name, ct=ct)
        else:
            raise ValueError(f"{self.__class__.__name__}: cannot have empty ct nor name values.")

    def _format_value(self, value):
        return {k: self.name for k in value}

    def __add__(self, other):
        return GateArray(self, other)
