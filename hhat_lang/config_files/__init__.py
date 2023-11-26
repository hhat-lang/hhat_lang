import json
from pathlib import Path


here = Path(__file__).parent.resolve()
BASE_CONFIG_PATH = here / "hhat_interpreter_base_config.json"
BASE_CONFIG_DATA = json.load(open(BASE_CONFIG_PATH, "r"))


# Base configuration for quantum language, backend, devices
BASE_Q_LANG_NAME        = "openqasm"
BASE_Q_LANG_VERSION     = "2.0"
BASE_Q_BACKEND_NAME     = "qiskit"
BASE_Q_BACKEND_VERSION  = "0.45.0"
BASE_Q_BACKEND_DEVICE   = "qasm_simulator"
