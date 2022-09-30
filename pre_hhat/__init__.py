# type: ignore[attr-defined]
"""A micro H-hat version."""

import os
import json
from importlib import metadata as importlib_metadata


cur_path = os.path.dirname(__file__)
examples_dir = os.path.abspath(os.path.join(cur_path, "..", "examples"))
qasm_dir = os.path.abspath(os.path.join(cur_path, "qasm_modules"))
quantum_tools_path = os.path.abspath(os.path.join(cur_path, "quantum_tools.json"))
config_path = os.path.abspath(os.path.join(cur_path, "hhat_config.json"))


examples_files = [
    "hello.hht",
    "simple_print.hht",
    "add_and_print.hht",
    "add_many_and_print.hht",
    "int_add_many_print.hht",
    "quantum_add_int.hht",
    "simple_quantum_pipe.hht"
]


def get_quantum_module():
    qm = json.loads(open(quantum_tools_path, "r").read())
    return qm["resource"]["name"], qm["resource"]["version"], qm["resource"]["type"]


def get_execute_mode():
    qm = json.loads(open(quantum_tools_path, "r").read())
    return qm["resource"]["execute_mode"]


def get_num_shots():
    qm = json.loads(open(quantum_tools_path, "r").read())
    return qm["resource"]["shots"]


def get_behavior():
    qm = json.loads(open(quantum_tools_path, "r").read())
    return qm["resource"]["behavior"]


def get_default_protocol():
    dp = json.loads(open(config_path, "r").read())
    return dp["protocols"]["default"]


execute_mode = get_execute_mode()
num_shots = get_num_shots()
default_protocol = get_default_protocol()
behavior_type = get_behavior()


def get_version() -> str:
    try:
        return importlib_metadata.version(__name__)
    except importlib_metadata.PackageNotFoundError:  # pragma: no cover
        return "unknown"


version: str = get_version()
