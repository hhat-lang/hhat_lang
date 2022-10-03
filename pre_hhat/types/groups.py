import sys
from abc import ABC, abstractmethod
from pre_hhat.grammar import ast as gast
import pre_hhat.types as types


class BaseGroup(ABC):
    @abstractmethod
    def _format_value(self, value):
        ...

    def _format_value_type(self, value):
        if isinstance(value, type):
            return value
        if isinstance(value, tuple):
            for k in value:
                if not isinstance(k, type):
                    raise ValueError(f"{self.__class__.__name__}: wrong value for value type.")
            return value
        return value

    @abstractmethod
    def __iter__(self):
        ...

    @abstractmethod
    def __len__(self):
        ...

    @abstractmethod
    def __bool__(self):
        ...

    @abstractmethod
    def __add__(self, other):
        ...

    @abstractmethod
    def __repr__(self):
        ...


#####################################
# Generic groups for data #
#####################################


class SingleType(BaseGroup):
    def __init__(self, value, type_name, data_rule, default=None, var=None):
        self.var = var
        self.name = type_name
        self.default = default
        self.rule = data_rule
        self.value = self._format_value(value)

    @abstractmethod
    def _format_value(self, value):
        ...

    def __iter__(self):
        yield from self.value

    def __len__(self):
        return len(self.value)

    @abstractmethod
    def __getitem__(self, item):
        ...

    @abstractmethod
    def __bool__(self):
        ...

    @abstractmethod
    def __eq__(self, other):
        ...

    @abstractmethod
    def __ne__(self, other):
        ...

    @abstractmethod
    def __gt__(self, other):
        ...

    @abstractmethod
    def __ge__(self, other):
        ...

    @abstractmethod
    def __lt__(self, other):
        ...

    @abstractmethod
    def __le__(self, other):
        ...

    @abstractmethod
    def __add__(self, other):
        ...

    @abstractmethod
    def __repr__(self):
        ...


class SingleAppender(SingleType):
    def __init__(self, value, type_name, default, var=None):
        super().__init__(value, type_name=type_name, data_rule="appender", default=default, var=var)

    @abstractmethod
    def _format_value(self, value):
        ...

    @abstractmethod
    def __bool__(self):
        ...

    def __repr__(self):
        return "".join([str(k) for k in self])


class SingleMorpher(SingleType):
    def __init__(self, value, type_name, default, var=None):
        super().__init__(value, type_name=type_name, data_rule="morpher", default=default, var=var)

    @abstractmethod
    def _format_value(self, value):
        ...

    @abstractmethod
    def __bool__(self):
        ...

    def __repr__(self):
        return "".join([str(k) for k in self])


class SingleNuller(SingleType):
    def __init__(self, type_name, default, var=None):
        super().__init__(None, type_name=type_name, data_rule="nuller", default=default, var=var)

    @abstractmethod
    def _format_value(self, value):
        ...

    @abstractmethod
    def __bool__(self):
        ...

    def __repr__(self):
        return f""


class ArrayType(BaseGroup):
    def __init__(
        self,
        *value,
        type_name=None,
        data_rule=None,
        default=None,
        value_type=None,
        var=None
    ):
        self.var = var
        self.default = default
        self.name = type_name
        self.value_type = self._format_value_type(value_type)
        self._value, self._indices = self._format_value(value)
        self.rule = data_rule

    @property
    @abstractmethod
    def value(self):
        ...

    @property
    def indices(self):
        return self._indices

    @abstractmethod
    def _format_value(self, value):
        ...

    def __iter__(self):
        yield from self.value

    def __len__(self):
        return len(self.value)

    @abstractmethod
    def __getitem__(self, item):
        ...

    @abstractmethod
    def __setitem__(self, key, value):
        ...

    @abstractmethod
    def __bool__(self):
        ...

    @abstractmethod
    def __eq__(self, other):
        ...

    @abstractmethod
    def __ne__(self, other):
        ...

    @abstractmethod
    def __gt__(self, other):
        ...

    @abstractmethod
    def __ge__(self, item):
        ...

    @abstractmethod
    def __lt__(self, other):
        ...

    @abstractmethod
    def __le__(self, other):
        ...

    @abstractmethod
    def __add__(self, other):
        ...

    @abstractmethod
    def __iadd__(self, other):
        ...

    @abstractmethod
    def __contains__(self, item):
        ...

    @abstractmethod
    def __repr__(self):
        ...


class ArrayAppender(ArrayType):
    def __init__(self, *value, type_name=None, default=None, value_type=None, var=None):
        super().__init__(
            *value,
            type_name=type_name,
            data_rule="appender",
            default=default,
            value_type=value_type,
            var=var
        )

    @abstractmethod
    def _format_value(self, value):
        ...


class ArrayMorpher(ArrayType):
    def __init__(self, *value, type_name=None, default=None, value_type=None, var=None):
        super().__init__(
            *value,
            type_name=type_name,
            data_rule="morpher",
            default=default,
            value_type=value_type,
            var=var
        )

    @abstractmethod
    def _format_value(self, value):
        ...


class ArrayNuller(ArrayType):
    def __init__(self, *value, type_name=None, default=None, value_type=None, var=None):
        super().__init__(
            *value,
            type_name=type_name,
            data_rule="nuller",
            default=default,
            value_type=value_type,
            var=var
        )

    @abstractmethod
    def _format_value(self, value):
        ...


########################################
# Here are the groups for quantum data #
########################################


class Gate(BaseGroup):
    def __init__(self, *value, name: str = None, ct=None, **kwargs):
        if len(set(value)) == len(value):
            self.name = (name.upper(),)
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
            elif isinstance(k, types.SingleInt):
                res += (k,)
            elif isinstance(k, int):
                print("GATE INT INDEX ERROR")
                exit()
        return res

    def _format_indices(self, value):
        return self.flatten(*value)

    @abstractmethod
    def _format_value(self, value):
        ...

    @staticmethod
    def _format_ct(value):
        return value

    def __bool__(self):
        return True if len(self) > 0 else False

    def __add__(self, other):
        inter_indices = set(self.indices).intersection(set(other.indices))
        self_multi = isinstance(self, MultipleIndexGate)
        other_multi = isinstance(other, MultipleIndexGate)
        if (self_multi or other_multi) and not inter_indices and self.name == other.name:
            return MultipleIndexGate(*(self.indices + other.indices), name=self.name[0])
        return GateArray(self, other)

    def __getitem__(self, item):
        return self

    def __iter__(self):
        yield from self.value

    def __len__(self):
        return len(self.value[0].keys())

    def __contains__(self, item):
        if not isinstance(item, BaseGroup):
            return item in self.value
        return item.value in self.value

    def __repr__(self):
        value = list(self.value[0].keys())
        if self.ct is not None:
            values = []
            value_len = sum(self.ct)
            for k in range(value_len):
                c_start = k * value_len
                c_end = k * value_len + self.ct[0]
                indices = " ".join([str(k) for k in value[c_start:c_end]])
                if not indices:
                    break
                control = "(" + indices + ")" if len(value[c_start:c_end]) > 1 else indices
                t_start = k * value_len + self.ct[0]
                t_end = k * value_len + self.ct[0] + self.ct[1]
                indices = " ".join([str(k) for k in value[t_start:t_end]])
                target = "(" + indices + ")" if len(value[t_start:t_end]) > 1 else indices
                values.append(f"{self.name[0]}(c:{control}, t:{target})")
            return " ".join(values)
        else:
            if self.name[0] is not None:
                res = " ".join([f"{k}" for k in value if not isinstance(k, types.SingleNull)])
                return f"{self.name[0]}({res})"
            else:
                return "(" + " ".join([str(k) for k in value]) + ")"


class GateArray(BaseGroup):
    def __init__(self, *value, **kwargs):
        self.value, self.indices, self.raw_indices, self.name = self._format_value(value)
        self.ct = self._format_ct(value)

    def _get_indices(self, value):
        if isinstance(value, list):
            indices = ()
            for k in value:
                indices += k.indices
            return indices
        if isinstance(value, Gate):
            return value.indices
        if isinstance(value, GateArray):
            return value.indices
        if isinstance(value, gast.AST):
            return ()
        raise ValueError(f"{self.__class__.__name__}: cannot get indices from {value}.")

    def _get_names(self, value):
        if isinstance(value, list):
            names = ()
            for k in value:
                names += self._get_names(k)
            return names
        if isinstance(value, Gate):
            return value.name
        if isinstance(value, GateArray):
            return value.name
        if isinstance(value, gast.AST):
            return ()
        raise ValueError(f"{self.__class__.__name__}: cannot get name from {value}.")

    @staticmethod
    def _indices_intersection(left, right):
        if left is None or right is None:
            return False
        left = set(left) if isinstance(left, tuple) else {left}
        right = set(right) if isinstance(right, tuple) else {right}
        return left.intersection(right)

    def _format_value(self, gates):
        value = []
        indices = ()
        name = ()
        prev = None
        for n, k in enumerate(gates):
            if 0 < n < len(gates):
                prev_indices = self._get_indices(prev[-1])
                k_indices = self._get_indices(k)
                inter_indices = self._indices_intersection(prev_indices, k_indices)
                if not inter_indices and not isinstance(prev[1], gast.AST):
                    prev_name = self._get_names(prev[1])
                    k_name = self._get_names(k)
                    inter_name = self._indices_intersection(prev_name, k_name)
                    if inter_name and len(prev[-1].name) == 1:
                        value[-1] = MultipleIndexGate(
                            *(prev_indices + k_indices), name=prev_name[0]
                        )
                        if isinstance(indices[-1], tuple):
                            indices = indices[:-1] + (indices[-1] + k.indices,)
                        else:
                            indices = indices[:-1] + ((indices[-1],) + k.indices,)
                    else:
                        value[-1] = [prev[-1], k]
                        last_index = (
                            indices[-1] if isinstance(indices[-1], tuple) else indices[-1],
                        )
                        indices = indices[:-1] + (last_index + k.indices,)
                        name = name[:-1] + ((name[-1], k.name[0]),)
                    prev = k
                    continue
            if isinstance(k.value, list):
                value.extend(k.value)
            else:
                value.append(k)
            indices += k.indices
            name += k.name
            prev = k
        return value, indices, indices, name

    @staticmethod
    def _format_ct(value):
        return tuple(k.ct for k in value)

    def __add__(self, other):
        return self.__class__(self, other)

    def __getitem__(self, item):
        if item < len(self.value):
            return self.value[item]
        raise ValueError(f"{self.__class__.__name__}: cannot have non-integer index.")

    def __iter__(self):
        yield from self.value

    def __bool__(self):
        return True if len(self) > 0 else False

    def __len__(self):
        return len(self.value)

    def __contains__(self, item):
        for k in self:
            if item.value in k.value:
                return True
        return False

    def __repr__(self):
        top_values = []
        for k in self.value:
            if isinstance(k, list):
                elem = " ".join([str(q) for q in k])
                elem = f"( {elem} )" if len(k) > 1 else elem
            else:
                elem = str(k)
            top_values.append(elem)
        res = ", ".join(top_values)
        return f"( {res} )" if len(top_values) > 1 else f"{res}"


class SingleIndexGate(Gate):
    def __init__(self, *value, name=None, **kwargs):
        if name is not None:
            super().__init__(*value, name=name)
        else:
            raise ValueError(f"{self.__class__.__name__}: must have a name.")

    def _format_value(self, value):
        return [{value[0]: self.name[0]}]


class MultipleIndexGate(Gate):
    def __init__(self, *value, name="", **kwargs):
        super().__init__(*value, name=name)

    def _format_value(self, value):
        return [{k: self.name[0] for k in value}]


class ControlTargetGate(Gate):
    def __init__(self, *value, name=None, ct=None):
        if ct is not None and name is not None and self.check_value_mask(value, ct):
            super().__init__(*value, name=name, ct=ct)
        else:
            raise ValueError(
                f"{self.__class__.__name__}: cannot have invalid values, ct or empty name."
            )

    def check_value_mask(self, value, ct):
        res = ()
        counter = 0
        for k in value:
            if isinstance(k, int):
                counter += 1
            if isinstance(k, tuple):
                res += (self.check_value_mask(k, ct),)
        if counter > 0 and len(res) == 0:
            if counter == sum(ct):
                return True
            return False
        elif counter == 0 and len(res) > 0:
            return all(res)
        else:
            return False

    def _format_value(self, value):
        return [{k: self.name[0] for k in value}]

    def __add__(self, other):
        return GateArray(self, other)
