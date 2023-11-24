import json
import pathlib


here = pathlib.Path(__file__).parent.resolve()
BASE_CONFIG_PATH = here / "hhat_interpreter_base_config.json"

BASE_CONFIG_DATA = json.load(open(BASE_CONFIG_PATH, "r"))

BASE_CONFIG_NAME = "openqasm2+qiskit_config"
