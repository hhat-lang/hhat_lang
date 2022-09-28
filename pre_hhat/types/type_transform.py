import pre_hhat.types as types
from pre_hhat import execute_mode, default_protocol
from pre_hhat.core.ast_exec import Exec
from pre_hhat.protocols import protocols_list
from pre_hhat.qasm_modules import QuantumDevice


def circuit_transform(circuit, stack):
    device = QuantumDevice()
    result = device.run(data=circuit, stack=stack)
    if execute_mode == "all":
        protocol_res = protocols_list[default_protocol](result)
        return protocol_res
    if execute_mode == "one":
        return tuple(result.value[0].keys())[0]
    raise ValueError(f"{__name__}: invalid execute mode.")


def protocol_transform(protocol_name):
    pass
