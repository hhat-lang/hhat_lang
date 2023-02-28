import hhat_lang.types as types
from hhat_lang import execute_mode, default_protocol
from hhat_lang.core.ast_exec import Exec
from hhat_lang.protocols import protocols_list
from hhat_lang.qasm_modules import QuantumDevice


def circuit_transform(circuit, stack):
    device = QuantumDevice()
    result = device.run(data=circuit, stack=stack)
    if execute_mode == "all":
        protocol_res = protocols_list[default_protocol](result)
        # print(f'[CIRCUIT TRANSF] stack memory so far: {stack["mem"]}')
        # print(f'[CIRCUIT TRANSF] protocol res: {protocol_res}')
        return protocol_res
    if execute_mode == "one":
        return tuple(result.value[0].keys())[0]
    raise ValueError(f"{__name__}: invalid execute mode.")


def protocol_transform(protocol_name):
    pass
