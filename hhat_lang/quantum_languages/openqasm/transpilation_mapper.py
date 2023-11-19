"""Mapping functions to OpenQASM 2.0 and 3.0"""
from functools import partial


builtin_quantum_fn_mapper = {
    "2.0": {
        "@shuffle": partial(
            map,
            lambda n: f"h q[{n}];\n"
        ),
        "@sync": partial(
            map,
            lambda n: f"cx q[{n[0]}], q[{n[1]}];\n"
        ),
    },
    "3.0": {

    }
}
