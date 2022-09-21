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
