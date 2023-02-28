from hhat_lang import get_quantum_module


module, _, device_type = get_quantum_module()
if module == "cqasm":
    raise NotImplementedError("cQASM not implemented yet.")
elif module == "netqasm":
    if device_type == "simulator":
        from hhat_lang.qasm_modules.netqasm import QuantumSimulator as QuantumDevice
    elif device_type == "hardware":
        from hhat_lang.qasm_modules.netqasm import QuantumHardware as QuantumDevice
    raise NotImplementedError("NetQASM not implemented yet.")
elif module == "openqasm":
    if device_type == "simulator":
        from hhat_lang.qasm_modules.openqasm import QuantumSimulator as QuantumDevice
    elif device_type == "hardware":
        from hhat_lang.qasm_modules.openqasm import QuantumHardware as QuantumDevice
elif module == "q1asm":
    raise NotImplementedError("Q1ASM not implemented yet.")
else:
    raise NotImplementedError(f"{module} QASM language is not implemented. Should it be?")
