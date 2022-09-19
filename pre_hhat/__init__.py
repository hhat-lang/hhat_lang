# type: ignore[attr-defined]
"""A micro H-hat version."""

import os
import json
from importlib import metadata as importlib_metadata


cur_path = os.path.dirname(__file__)
examples_dir = os.path.abspath(os.path.join(cur_path, "..", "examples"))
qasm_dir = os.path.abspath(os.path.join(cur_path, "qasm_modules"))
quantum_tools_dir = os.path.abspath(cur_path)


def get_quantum_module():
    qm = json.loads(open("quantum_tools.json", "r").read())
    return qm["resource"]["name"], qm["resource"]["version"], qm["resource"]["type"]


def get_execute_mode():
    qm = json.loads(open("quantum_tools.json", "r").read())
    return qm["resource"]["execute_mode"]


execute_mode = get_execute_mode()


def get_version() -> str:
    try:
        return importlib_metadata.version(__name__)
    except importlib_metadata.PackageNotFoundError:  # pragma: no cover
        return "unknown"


version: str = get_version()
