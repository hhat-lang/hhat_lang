from pre_hhat.grammar import ast as gast
from pre_hhat.types import groups as group


def get_type(name):
    data_types = {'bool': ArrayBool,
                  'int': ArrayInt,
                  'str': ArrayStr,
                  'circuit': ArrayCircuit}
    return data_types.get(name, False)


#################
# SINGLE GROUPS #
#################

# Integer

class SingleInt(group.SingleMorpher):
    def __init__(self, value):
        super().__init__(value, type_name=SingleInt)

    def _format_value(self, value):
        if isinstance(value, str):
            if value.isdigit():
                return [int(value)]
        if isinstance(value, int):
            return [value]
        raise ValueError(f"{self.name}: can only receive integer data.")

    def __eq__(self, other):
        if isinstance(other, SingleInt):
            return self.value == other.value
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        if isinstance(other, SingleInt):
            return self.value[0] > other.value[0]
        raise NotImplemented(f"{self.name}: operation not implemented for {self.name} and {other.name}.")

    def __ge__(self, other):
        if isinstance(other, SingleInt):
            return self.value[0] >= other.value[0]
        raise NotImplemented(f"{self.name}: operation not implemented for {self.name} and {other.name}.")

    def __lt__(self, other):
        if isinstance(other, SingleInt):
            return self.value[0] < other.value[0]
        raise NotImplemented(f"{self.name}: operation not implemented for {self.name} and {other.name}.")

    def __le__(self, other):
        if isinstance(other, SingleInt):
            return self.value[0] <= other.value[0]
        raise NotImplemented(f"{self.name}: operation not implemented for {self.name} and {other.name}.")

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
        raise NotImplemented(f"{self.name}: operation not implemented for {self.name} and {other_name}.")


# String

class SingleStr(group.SingleAppender):
    def __init__(self, value):
        super().__init__(value, type_name=SingleStr)

    def _format_value(self, value):
        if isinstance(value, str):
            return [value]
        raise ValueError(f"{self.name}: can only receive string data.")

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
        raise NotImplemented(f"{self.name} not implemented addition with {other.__class__.__name__}.")

    def __repr__(self):
        return f"\"{self.value[0]}\""


# Boolean

class SingleBool(group.SingleMorpher):
    bool_values = {True: 'T', False: 'F'}

    def __init__(self, value):
        super().__init__(value, type_name=SingleBool)

    def _format_value(self, value):
        if isinstance(value, bool):
            return [self.bool_values[value]]
        if isinstance(value, str):
            if value in ['T', 'F']:
                return [value]
        raise ValueError(f"{self.name}: can only receive boolean data (T or F).")

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
        return self.value[0]

    def __add__(self, other):
        if isinstance(other, str):
            if other in ['T', 'F']:
                if other == 'T' and self.value[0] == 'T':
                    return self.__class__('T')
                return self.__class__('F')
            raise ValueError(f"{self.name}: addition must be between booleans.")
        if isinstance(other, SingleBool):
            if self == other and other.value[0] == 'T':
                return self.__class__('T')
            else:
                return self.__class__('F')
        if isinstance(other, SingleNull):
            return self
        raise NotImplemented(f"{self.name}: not implemented addition with {other.__class__.__name__}.")

    def __repr__(self):
        return f"{self.value[0]}"


# Null

class SingleNull(group.SingleNuller):
    def __init__(self):
        super().__init__(SingleNull)

    def _format_value(self, value):
        return []

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


################
# ARRAY GROUPS #
################

# Integer

class ArrayInt(group.ArrayMorpher):
    def __init__(self, *value):
        default = [0]
        super().__init__(*value,
                         type_name=ArrayInt,
                         default=default,
                         value_type=SingleInt)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, item):
        if isinstance(item, SingleInt):
            self._value.extend(item.value)
            self._indices += len(self._indices),
        elif isinstance(item, ArrayInt):
            self._value.extend(item.value)
            self._indices = tuple(k for k in range(len(self._indices + item._indices)))
        else:
            raise ValueError(f"{self.name}: must have SingleInt or ArrayInt value to set to.")

    @property
    def indices(self):
        return self._indices

    def _format_value(self, value):
        for k in value:
            if not isinstance(k, self.value_type):
                raise ValueError(f"{self.name}: can only contain integer values.")
        return list(value), tuple(k for k in range(len(value)))

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
        if isinstance(other, SingleInt):
            for n, k in enumerate(self):
                self.value[n] += other.value[0]
            return self
        if isinstance(other, ArrayInt):
            for n, v in enumerate(zip(self, other)):
                if n < len(other):
                    self.value[n] += v[1]
            return self
        if isinstance(other, SingleNull):
            return self
        if isinstance(other, ArrayCircuit):
            raise NotImplemented(f"{self.name}: need to implement addition with circuit type.")
        raise NotImplemented(f"{self.name}: not implemented addition with {other.name}.")

    def __iadd__(self, other):
        if isinstance(other, SingleInt):
            self.value.extend(other.value)
            return self
        if isinstance(other, ArrayInt):
            self.value.extend(other.value)
            return self
        if isinstance(other, SingleNull):
            return self
        if isinstance(other, ArrayCircuit):
            raise NotImplemented(f"{self.name}: need to implement appending with circuit type.")
        raise NotImplemented(f"{self.name}: not implemented appending with {other.name}.")

    def __contains__(self, item):
        return item in self.value

    def __repr__(self):
        values = " ".join([str(k) for k in self])
        return f"({values})"


# String

class ArrayStr(group.ArrayAppender):
    def __init__(self, *value):
        default = [""]
        super().__init__(*value,
                         type_name=ArrayStr,
                         default=default,
                         value_type=SingleStr)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, item):
        if isinstance(item, SingleStr):
            self._value.extend(item.value)
            self._indices += len(self._indices),
        elif isinstance(item, ArrayStr):
            self._value.extend(item.value)
            self._indices = tuple(k for k in range(len(self._indices + item._indices)))
        else:
            raise ValueError(f"{self.name}: must have SingleStr or ArrayStr value to set to.")

    @property
    def indices(self):
        return self._indices

    def _format_value(self, value):
        for k in value:
            if not isinstance(k, self.value_type):
                raise ValueError(f"{self.name}: can only contain string values.")
        return list(value), tuple([k for k in range(len(value))])

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
        if isinstance(other, SingleStr):
            for n in range(len(self)):
                self.value[n] += other.value[0]
            return self
        if isinstance(other, ArrayStr):
            for n, v in enumerate(zip(self, other)):
                if n < len(other):
                    self.value[n] += v[1]
            return self
        if isinstance(other, SingleNull):
            return self
        if isinstance(other, ArrayCircuit):
            raise NotImplemented(f"{self.name}: need to implement addition with circuit type.")
        raise NotImplemented(f"{self.name}: not implemented addition with {other.name}.")

    def __iadd__(self, other):
        if isinstance(other, SingleStr):
            self.value.extend(other.value)
            return self
        if isinstance(other, ArrayStr):
            self.value.extend(other.value)
            return self
        if isinstance(other, SingleNull):
            return self
        if isinstance(other, ArrayCircuit):
            raise NotImplemented(f"{self.name}: not implemented appending with circuit type.")
        raise NotImplemented(f"{self.name}: not implemented appending with {other.name}.")

    def __contains__(self, item):
        return item in self.value

    def __repr__(self):
        values = " ".join([str(k) for k in self.value])
        return f"({values})"


# Bool

class ArrayBool(group.ArrayMorpher):
    def __init__(self, *value):
        default = []
        super().__init__(*value,
                         type_name=ArrayBool,
                         default=default,
                         value_type=SingleBool)

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
        return list(value)

    def __getitem__(self, item):
        if item in self.indices:
            return self.value[item]
        else:
            raise ValueError(f"{self.name}: there is no index {item} in the variable.")

    def __setitem__(self, key, value):
        if key in self.indices:
            self.value[key] = value

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
        if isinstance(other, SingleBool):
            res = ()
            for k in self:
                res += (other + k),
            return self.__class__(*res)
        if isinstance(other, ArrayBool):
            res = ()
            for n, v in enumerate(self):
                if n < len(other):
                    res += (v + other.value[n]),
                else:
                    res += v,
            return self.__class__(*res)
        if isinstance(other, SingleNull):
            return self
        if isinstance(other, ArrayCircuit):
            raise NotImplemented(f"{self.name}: not implemented addition with circuit type.")
        raise NotImplemented(f"{self.name}: not implemented addition with {other.__class__.__name__}")

    def __iadd__(self, other):
        if isinstance(other, (SingleBool, ArrayBool)):
            self.value.extend(other.value)
            return self
        if isinstance(other, SingleNull):
            return self
        if isinstance(other, ArrayCircuit):
            raise NotImplemented(f"{self.name}: not implemented appending with circuit.")
        raise NotImplemented(f"{self.name}: not implemented appending with {other.__class__.__name__}")

    def __contains__(self, item):
        return item in self.value

    def __repr__(self):
        values = " ".join([str(k) for k in self])
        return f"({values})"


# Circuit

class ArrayCircuit(group.ArrayAppender):
    def __init__(self, *value):
        default = []
        self._counter = 0
        super().__init__(*value,
                         type_name=ArrayCircuit,
                         default=default,
                         value_type=(group.Gate, group.GateArray))
        self._true_len = self._get_true_len()

    @property
    def value(self):
        return self._value

    @property
    def indices(self):
        return self._indices

    def _format_value(self, value):
        res = []
        indices = ()
        for k in value:
            if isinstance(k, group.Gate):
                res.append(k)
                indices += self._counter,
                self._counter += 1
            elif isinstance(k, group.GateArray):
                res.extend(k)
                indices += k.indices,
                self._counter += 1
            elif isinstance(k, ArrayCircuit):
                res.extend(k.value)
                len_k = len(k.value)
                indices += tuple(self._counter + p for p in range(len_k))
                self._counter += len_k
            elif isinstance(k, gast.AST):
                res.append(k)
                indices += None,
        print(res)
        return res, indices

    def _flatten_indices(self, value):
        res = ()
        for k in value:
            if isinstance(k, (tuple, list)):
                res += self._flatten_indices(k)
            elif isinstance(k, int):
                res += k,
            elif k is None or isinstance(k, str):
                continue
            else:
                res += self._flatten_indices(k.indices)
        return res

    def _get_true_len(self):
        res = 0
        for k in self.value:
            if not isinstance(k, gast.AST):
                elem_len = max(self._flatten_indices(k))
                res = elem_len if elem_len > res else res
        return res

    def __len__(self):
        return self._true_len

    def __getitem__(self, item):
        return self

    def __setitem__(self, key, value):
        pass

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
        pass

    def __ge__(self, other):
        pass

    def __lt__(self, other):
        pass

    def __le__(self, other):
        pass

    def __add__(self, other):
        if isinstance(other, group.Gate):
            pass
        if isinstance(other, group.GateArray):
            pass
        if isinstance(other, ArrayCircuit):
            pass
        if isinstance(other, gast.AST):
            pass

        ##################
        # Special cases: #
        ##################

        # Integer
        if isinstance(other, SingleInt):
            pass
        if isinstance(other, ArrayInt):
            pass

        # String
        if isinstance(other, SingleStr):
            pass
        if isinstance(other, ArrayStr):
            pass

    def __iadd__(self, other):
        if isinstance(other, SingleNull):
            return self
        if isinstance(other, (group.Gate, group.GateArray)):
            self.value.append(other)
            self._indices += self._counter,
            self._counter += 1
            return self
        if isinstance(other, ArrayCircuit):
            self.value.extend(other)
            len_k = len(other.value)
            self._indices += tuple(self._counter + p for p in range(len_k))
            self._counter += len_k
            return self
        if isinstance(other, gast.AST):
            self.value.append(other)
            self._indices += None,
            return self

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
            num_space = '0'*(num_len-cur_num_len)
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
