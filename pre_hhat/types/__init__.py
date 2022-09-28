from .builtin import (
    SingleNull,
    SingleBool,
    SingleInt,
    SingleStr,
    SingleHashmap,
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
        "circuit": ArrayCircuit,
    }
    return data_types.get(name, False)


def is_circuit(data):
    circuit_types = ArrayCircuit().value_type
    if isinstance(data, (tuple, set, list)):
        for k in data:
            try:
                if isinstance(k(), circuit_types):
                    return True
            except TypeError:
                if isinstance(k, circuit_types):
                    return True
        return False
    try:
        if isinstance(data(), circuit_types):
            return True
    except TypeError:
        if isinstance(data, circuit_types):
            return True
    return False
