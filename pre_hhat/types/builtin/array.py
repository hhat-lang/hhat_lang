"""Data types as array groups"""

from pre_hhat import default_protocol
from pre_hhat.grammar import ast as gast
from pre_hhat.types import groups as group
import pre_hhat.types as types


class ArrayNull(group.ArrayNuller):
    def __init__(self, *value, protocol=default_protocol, var=None):
        default = []
        super().__init__(
            *value,
            type_name=ArrayNull,
            default=default,
            value_type=types.SingleNull,
            var=var
        )
        self.protocol = protocol

    @property
    def value(self):
        return self._value

    @property
    def indices(self):
        return self._indices

    def _format_value(self, value):
        for k in value:
            if not isinstance(value, self.value):
                raise ValueError(f"{self.name}: must have types.SingleNull value to set to.")
        return list(value), tuple(types.SingleInt(k) for k in range(len(value)))

    def __getitem__(self, item):
        return self

    def __setitem__(self, key, value):
        return self

    def __bool__(self):
        return False

    def __eq__(self, other):
        if isinstance(other, ArrayNull):
            if len(self) == len(other):
                for s, o in zip(self, other):
                    if s != o:
                        return False
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
        if isinstance(other, (types.SingleNull, ArrayNull)):
            self.value.extend(other.value)
        return other

    def __contains__(self, item):
        return item in self.value

    def __repr__(self):
        values = " ".join(["null" for _ in self])
        return f"({values})"


class ArrayInt(group.ArrayMorpher):
    def __init__(self, *value, protocol=default_protocol, var=None):
        default = [types.SingleInt(0)]
        super().__init__(
            *value,
            type_name=ArrayInt,
            default=default,
            value_type=types.SingleInt,
            var=var
        )
        self.protocol = protocol

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, item):
        if isinstance(item, types.SingleInt):
            self._value.extend(item.value)
            self._indices += (len(self._indices),)
        elif isinstance(item, ArrayInt):
            self._value.extend(item.value)
            self._indices = tuple(k for k in range(len(self._indices + item._indices)))
        else:
            raise ValueError(f"{self.name}: must have types.SingleInt or ArrayInt value to set to.")

    @property
    def indices(self):
        return self._indices

    def _format_value(self, value):
        # print(f'* arrayint format value={value}')
        if len(value) > 0:
            for k in value:
                if not isinstance(k, self.value_type):
                    raise ValueError(f"{self.name}: can only contain integer values.")
        else:
            value = self.default
        return list(value), tuple(types.SingleInt(k) for k in range(len(value)))

    def __getitem__(self, item):
        if item in self.indices or types.SingleInt(item) in self.indices:
            return self.value[item]
        else:
            raise ValueError(f"{self.name}: there is no index {item} in the variable.")

    def __setitem__(self, key, value):
        if key in self.indices:
            if isinstance(key, int):
                self.value[key] = value
            elif isinstance(key, types.SingleInt):
                self.value[key.value[0]] = value

    def __bool__(self):
        return True

    def __eq__(self, other):
        if isinstance(other, ArrayInt):
            if len(self) == len(other):
                for s, o in zip(self, other):
                    if s != o:
                        return False
                return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        if len(self) == len(other):
            for s, o in zip(self, other):
                if not (s > o):
                    return False
            return True
        if len(self) > len(other):
            return True
        return False

    def __ge__(self, other):
        if len(self) == len(other):
            for s, o in zip(self, other):
                if not (s >= o):
                    return False
            return True
        if len(self) > len(other):
            return True
        return False

    def __lt__(self, other):
        if len(self) == len(other):
            for s, o in zip(self, other):
                if not (s < o):
                    return False
            return True
        if len(self) < len(other):
            return True
        return False

    def __le__(self, other):
        if len(self) == len(other):
            for s, o in zip(self, other):
                if not (s <= o):
                    return False
            return True
        if len(self) < len(other):
            return True
        return False

    def __add__(self, other):
        if isinstance(other, types.SingleInt):
            for n, k in enumerate(self):
                self.value[n] += other.value
            return self
        if isinstance(other, ArrayInt):
            self.value.extend(other.value)
            return self.__class__(self.value + other.value)
        if isinstance(other, types.SingleNull):
            return self
        if isinstance(other, ArrayCircuit):
            raise NotImplementedError(f"{self.name}: need to implement addition with circuit type.")
        raise NotImplementedError(f"{self.name}: not implemented addition with {other.name}.")

    def __iadd__(self, other):
        if isinstance(other, types.SingleInt):
            for n, k in enumerate(self):
                self.value[n] += other.value[0]
            # self.value.extend(other.value)
            return self
        if isinstance(other, ArrayInt):
            for n, v in enumerate(zip(self, other)):
                if n < len(other):
                    self.value[n] += v[1]
            return self
        if isinstance(other, types.SingleNull):
            return self
        if isinstance(other, tuple):
            # print(f'* arrayint add tuple={other} type={type(other)} vals={[type(p) for p in other]}')
            value, stack = other
            res = types.circuit_transform(value, stack)
            new_value = self.value[0] + round(res)
            # print(f"RECEIVED RES: {new_value}")
            return self.__class__(new_value)
        raise NotImplementedError(f"{self.name}: not implemented appending with {other.name}.")

    def __contains__(self, item):
        return item in self.value

    def __repr__(self):
        values = " ".join([str(k) for k in self])
        return f"({values})"


class ArrayStr(group.ArrayAppender):
    def __init__(self, *value, protocol=default_protocol, var=None):
        default = [types.SingleStr("")]
        super().__init__(
            *value,
            type_name=ArrayStr,
            default=default,
            value_type=types.SingleStr,
            var=var
        )
        self.protocol = protocol

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, item):
        if isinstance(item, types.SingleStr):
            self._value.extend(item.value)
            self._indices += (len(self._indices),)
        elif isinstance(item, ArrayStr):
            self._value.extend(item.value)
            self._indices = tuple(k for k in range(len(self._indices + item._indices)))
        else:
            raise ValueError(f"{self.name}: must have types.SingleStr or ArrayStr value to set to.")

    @property
    def indices(self):
        return self._indices

    def _format_value(self, value):
        for k in value:
            if not isinstance(k, self.value_type):
                raise ValueError(f"{self.name}: can only contain string values.")
        return list(value), tuple([types.SingleInt(k) for k in range(len(value))])

    def __getitem__(self, item):
        if item in self.indices or types.SingleInt(item) in self.indices:
            return self.value[item].strip('"').siptr("'")
        else:
            raise ValueError(f"{self.name}: there is no index {item} in the variable.")

    def __setitem__(self, key, value):
        if key in self.indices:
            if isinstance(key, int):
                self.value[key] = value
            elif isinstance(key, types.SingleInt):
                self.value[key.value[0]] = value

    def __bool__(self):
        return True if len(self.value) > 0 else False

    def __eq__(self, other):
        if isinstance(other, ArrayStr):
            if len(self) == len(other):
                for s, o in zip(self, other):
                    if s != o:
                        return False
                return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        if len(self) == len(other):
            for s, o in zip(self, other):
                if not (s > o):
                    return False
            return True
        if len(self) > len(other):
            return True
        return False

    def __ge__(self, other):
        if len(self) == len(other):
            for s, o in zip(self, other):
                if not (s >= o):
                    return False
            return True
        if len(self) >= len(other):
            return True
        return False

    def __lt__(self, other):
        if len(self) == len(other):
            for s, o in zip(self, other):
                if not (s < o):
                    return False
            return True
        if len(self) < len(other):
            return True
        return False

    def __le__(self, other):
        if len(self) == len(other):
            for s, o in zip(self, other):
                if not (s <= o):
                    return False
            return True
        if len(self) <= len(other):
            return True
        return False

    def __add__(self, other):
        if isinstance(other, types.SingleStr):
            for n in range(len(self)):
                self.value[n] += other.value[0]
            return self
        if isinstance(other, ArrayStr):
            for n, v in enumerate(zip(self, other)):
                if n < len(other):
                    self.value[n] += v[1]
            return self
        if isinstance(other, types.SingleNull):
            return self
        if isinstance(other, ArrayCircuit):
            raise NotImplementedError(f"{self.name}: need to implement addition with circuit type.")
        raise NotImplementedError(f"{self.name}: not implemented addition with {other.name}.")

    def __iadd__(self, other):
        if isinstance(other, types.SingleStr):
            self.value.extend(other.value)
            return self
        if isinstance(other, ArrayStr):
            self.value.extend(other.value)
            return self
        if isinstance(other, types.SingleNull):
            return self
        if isinstance(other, ArrayCircuit):
            raise NotImplementedError(f"{self.name}: not implemented appending with circuit type.")
        raise NotImplementedError(f"{self.name}: not implemented appending with {other.name}.")

    def __contains__(self, item):
        return item in self.value

    def __repr__(self):
        values = " ".join([str(k) for k in self.value])
        return f"({values})"


class ArrayBool(group.ArrayMorpher):
    def __init__(self, *value, protocol=default_protocol, var=None):
        default = []
        super().__init__(
            *value,
            type_name=ArrayBool,
            default=default,
            value_type=types.SingleBool,
            var=var
        )
        self.protocol = protocol

    @property
    def value(self):
        return self._value

    @property
    def indices(self):
        return self._indices

    def _format_value(self, value):
        for k in value:
            if not isinstance(k, self.value_type):
                raise ValueError(f"{self.name}: can only contain boolean types.")
        return list(value), tuple([types.SingleInt(k) for k in value])

    def __getitem__(self, item):
        if item in self.indices or types.SingleInt(item) in self.indices:
            return self.value[item]
        else:
            raise ValueError(f"{self.name}: there is no index {item} in the variable.")

    def __setitem__(self, key, value):
        if key in self.indices:
            if isinstance(key, int):
                self.value[key] = value
            elif isinstance(key, types.SingleInt):
                self.value[key.value[0]] = value

    def __bool__(self):
        for k in self:
            if not k.str_values(k.value[0]):
                return False
        return True

    def __eq__(self, other):
        if len(self) == len(other):
            for s, o in zip(self, other):
                if s != o:
                    return False
            return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        if len(self) == len(other):
            for s, o in zip(self, other):
                if not (s > o):
                    return False
            return True
        if len(self) > len(other):
            return True
        return False

    def __ge__(self, other):
        if len(self) == len(other):
            for s, o in zip(self, other):
                if not (s >= o):
                    return False
            return True
        if len(self) >= len(other):
            return True
        return False

    def __lt__(self, other):
        if len(self) == len(other):
            for s, o in zip(self, other):
                if not (s < o):
                    return False
            return True
        if len(self) < len(other):
            return True
        return False

    def __le__(self, other):
        if len(self) == len(other):
            for s, o in zip(self, other):
                if not (s <= o):
                    return False
            return True
        if len(self) <= len(other):
            return True
        return False

    def __add__(self, other):
        if isinstance(other, types.SingleBool):
            res = ()
            for k in self:
                res += ((other + k),)
            return self.__class__(*res)
        if isinstance(other, ArrayBool):
            res = ()
            for n, v in enumerate(self):
                if n < len(other):
                    res += ((v + other.value[n]),)
                else:
                    res += (v,)
            return self.__class__(*res)
        if isinstance(other, types.SingleNull):
            return self
        if isinstance(other, ArrayCircuit):
            raise NotImplementedError(f"{self.name}: not implemented addition with circuit type.")
        raise NotImplementedError(
            f"{self.name}: not implemented addition with {other.__class__.__name__}"
        )

    def __iadd__(self, other):
        if isinstance(other, (types.SingleBool, ArrayBool)):
            self.value.extend(other.value)
            return self
        if isinstance(other, types.SingleNull):
            return self
        if isinstance(other, ArrayCircuit):
            raise NotImplementedError(f"{self.name}: not implemented appending with circuit.")
        raise NotImplementedError(
            f"{self.name}: not implemented appending with {other.__class__.__name__}"
        )

    def __contains__(self, item):
        return item in self.value

    def __repr__(self):
        values = " ".join([str(k) for k in self])
        return f"({values})"


class ArrayHashmap(group.ArrayAppender):
    def __init__(self, *value, protocol=default_protocol, var=None):
        default = dict()
        super().__init__(
            *value,
            type_name=ArrayHashmap,
            default=default,
            value_type=types.SingleHashmap,
            var=var
        )
        self.protocol = protocol

    @property
    def value(self):
        return self._value

    @property
    def indices(self):
        return self._indices

    def _format_value(self, value):
        if isinstance(value, (tuple, list)):
            if types.is_circuit(value):
                pass
            pass
        if isinstance(value, types.SingleHashmap):
            pass
        if isinstance(value, ArrayHashmap):
            pass
        raise NotImplementedError(f"{self.name}: cannot use types of {value}.")

    def __iter__(self):
        yield from self.value[0].items()

    def __len__(self):
        return len(self.value[0].keys())

    def __getitem__(self, item):
        return self.value[0].get(item, None)

    def __setitem__(self, key, value):
        if key in self.value[0].keys():
            self.value[0] = value
        else:
            raise ValueError(f"{self.name}: cannot assign {key}; invalid key.")

    def __bool__(self):
        return True if len(self) > 0 else False

    def __eq__(self, other):
        if isinstance(other, (types.SingleHashmap, ArrayHashmap)):
            if self.value[0].keys() == other.value[0].keys():
                return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        if isinstance(other, ArrayHashmap):
            if self.value[0].keys() > other.value[0].keys():
                return True
        return False

    def __ge__(self, other):
        if isinstance(other, ArrayHashmap):
            if self.value[0].keys() >= other.value[0].keys():
                return True
        return False

    def __lt__(self, other):
        if isinstance(other, ArrayHashmap):
            if self.value[0].keys() < other.value[0].keys():
                return True
        return False

    def __le__(self, other):
        if isinstance(other, ArrayHashmap):
            if self.value[0].keys() <= other.value[0].keys():
                return True
        return False

    def __add__(self, other):
        if isinstance(other, (types.SingleHashmap, ArrayHashmap)):
            return self.__class__(*(tuple(self) + tuple(other)))
        if isinstance(other, ArrayCircuit):
            raise NotImplementedError(f"{self.name}: not implemented addition with circuit yet.")
        raise NotImplementedError(
            f"{self.name}: not imeplemented addition with {other.__class__.__name__}."
        )

    def __iadd__(self, other):
        if isinstance(other, (types.SingleHashmap, ArrayHashmap)):
            self.value[0].update(other.value[0])
            return self
        if isinstance(other, ArrayCircuit):
            raise NotImplementedError(f"{self.name}: not implemented appending with circuit.")
        raise NotImplementedError(
            f"{self.name}: not implemented appending with {other.__class__.__name__}."
        )

    def __contains__(self, item):
        return item in self.value[0].keys()

    def __repr__(self):
        values = ", ".join([f"{k}:{v}" for k, v in self])
        return f"({values})"


class ArrayCircuit(group.ArrayAppender):
    def __init__(self, *value, protocol=default_protocol, var=None):
        default = []
        self._counter = 0
        super().__init__(
            *value,
            type_name=ArrayCircuit,
            default=default,
            value_type=(group.Gate, group.GateArray, gast.AST, ArrayCircuit),
            var=var
        )
        self._true_len = 0
        self.protocol = protocol
        self.indices_array = self._get_indices_array()

    @property
    def value(self):
        return self._value

    @property
    def indices(self):
        return self._indices

    def _get_indices_array(self):
        for k in self.indices:
            pass
        return []

    def _format_value(self, value):
        if len(value) > 0:
            res = []
            indices = ()
            count = types.SingleInt(0)
            for k in value:
                if isinstance(k, (group.Gate, group.GateArray, ArrayCircuit)):
                    res.append(k)
                    indices += k.indices
                    for _ in k.indices:
                        count = count + types.SingleInt(1)
                if isinstance(k, gast.AST):
                    res.append(k)
                if k is None:
                    indices += count,
                    count = count + types.SingleInt(1)
            indices = tuple(set(indices))
            self._true_len = count.value[0]
            return res, indices
        return [], ()

    def _flatten_indices(self, value):
        res = ()
        for k in value:
            if isinstance(k, (tuple, list)):
                res += self._flatten_indices(k)
            elif isinstance(k, (int, types.SingleInt)):
                res += (k,)
            elif k is None or isinstance(k, str):
                continue
            else:
                res += self._flatten_indices(k.var_indices)
        return res

    def _get_true_len(self):
        res = types.SingleInt(0)
        for k in self.value:
            if not isinstance(k, (gast.AST, types.SingleNull)) and k is not None:
                elem_len = max(self._flatten_indices(k))
                res = elem_len if elem_len > res else res
        return res

    def __len__(self):
        return self._true_len

    def __getitem__(self, item):
        return self.value[item]

    def __setitem__(self, key, value):
        pass

    def __bool__(self):
        return True if len(self) > 0 else False

    def __eq__(self, other):
        if len(self.value) == len(other.value):
            if len(self) == len(other):
                for s, o in zip(self, other):
                    if s != o:
                        return False
                return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        if isinstance(other, ArrayCircuit):
            if len(self) > len(other):
                return True
            return False
        raise ValueError(f"{self.name}: cannot do 'gt' with {other.__class__.__name__}.")

    def __ge__(self, other):
        if isinstance(other, ArrayCircuit):
            if len(self) >= len(other):
                return True
            return False
        raise ValueError(f"{self.name}: cannot do 'ge' with {other.__class__.__name__}.")

    def __lt__(self, other):
        if isinstance(other, ArrayCircuit):
            if len(self) < len(other):
                return True
            return False
        raise ValueError(f"{self.name}: cannot do 'lt' with {other.__class__.__name__}.")

    def __le__(self, other):
        if isinstance(other, ArrayCircuit):
            if len(self) <= len(other):
                return True
            return False
        raise ValueError(f"{self.name}: cannot do 'le' with {other.__class__.__name__}.")

    def __add__(self, other):
        if isinstance(other, group.Gate):
            return ArrayCircuit(*(self.value + [other]))
        if isinstance(other, group.GateArray):
            return ArrayCircuit(*(self.value + other.value))
        if isinstance(other, ArrayCircuit):
            return ArrayCircuit(*(self.value + other.value))
        if isinstance(other, gast.AST):
            return ArrayCircuit(*(self.value + [other]))
        if isinstance(other, tuple):
            value, stack = other
            # print(f'+ CIRCUIT = {value} {self}')
            res = types.circuit_transform(self, stack)
            new_value = value.value[0] + round(res)
            # print(f'[C] RECEIVED RES: {new_value} {value.__class__}')
            return value.__class__(new_value)
        return other.__class__()

    def __iadd__(self, other):
        if isinstance(other, types.SingleNull):
            return self
        if isinstance(other, (group.Gate, group.GateArray)):
            self.value.append(other)
            self._indices += other.indices
            self._indices = tuple(set(self._indices))
            self._true_len = len(self._indices)
            return self
        if isinstance(other, ArrayCircuit):
            self.value.extend(other)
            len_k = len(other.value)
            self._indices += tuple(self._counter + p for p in range(len_k))
            self._counter += len_k
            return self
        if isinstance(other, gast.AST):
            # print(f"+= AST!? {other}")
            self.value.append(other)
            # self._indices += (None,)
            return self
        raise ValueError(f"{self.name}: cannot append {other.__class__.__name__} type.")

    def __contains__(self, item):
        for k in self:
            if item in k:
                return True
        return False

    def __repr__(self):
        res = ""
        num_len = len(str(len(self.value)))
        c_steps = 0
        for n, k in enumerate(self.value):
            cur_num_len = len(str(n))
            num_space = "0" * (num_len - cur_num_len)
            if not isinstance(k, gast.AST):
                extra = f" | circuit step {'0'*(num_len-len(str(c_steps)))}{c_steps}"
                c_steps += 1
                if isinstance(k, list):
                    values = " ".join([str(p) for p in k])
                    values = f"( {values} )" if len(k) > 1 else values
                else:
                    values = f"{k}"
            else:
                extra = f" | non circuit step"
                values = f"{k}"
            res += f"  - seq {num_space}{n}{extra}: {values}\n"
        return f"(\n{res})"
