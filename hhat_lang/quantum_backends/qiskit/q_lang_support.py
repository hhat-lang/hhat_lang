from qiskit_aer import QasmSimulator


supported_lang = {
    "openqasm": {
        "2.0": QasmSimulator().from_backend('qasm_simulator'),
        # TODO: implement/call something for 3.0 as well
        "3.0": lambda x: None,
    }
}
