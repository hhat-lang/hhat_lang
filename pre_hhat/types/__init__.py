from .builtin import (
    SingleNull,
    SingleBool,
    SingleInt,
    SingleStr,
    SingleHashmap,
    SingleBin,
    SingleHex,
    ArrayBool,
    ArrayInt,
    ArrayStr,
    ArrayCircuit,
    ArrayNull,
    ArrayHashmap,
)
from .groups import (
    ArrayType,
    BaseGroup,
    SingleType,
    SingleNuller,
    SingleAppender,
    SingleMorpher,
    SingleIndexGate,
    MultipleIndexGate,
    ControlTargetGate,
    Gate,
    GateArray,
)

from .type_transform import circuit_transform, protocol_transform


def get_type(name):
    data_types = {
        "null": ArrayNull,
        "bool": ArrayBool,
        "int": ArrayInt,
        "str": ArrayStr,
        "hashmap": ArrayHashmap,
        "bin": SingleBin,
        "hex": SingleHex,
        "circuit": ArrayCircuit,
    }
    return data_types.get(name, False)


circuit_types = ArrayCircuit().value_type


def is_circuit(data):
    if isinstance(data, (tuple, set, list)):
        for k in data:
            p = is_circuit(k)
            if p:
                return True
        return False
    try:
        if isinstance(data, ArrayCircuit):
            return True
        try:
            if isinstance(data(), circuit_types):
                return True
        except TypeError:
            if isinstance(data, circuit_types):
                return True
    except TypeError:
        if isinstance(data(), ArrayCircuit):
            return True
    return False
