from pre_hhat import get_quantum_module


module, _, device_type = get_quantum_module()
if module == 'cqasm':
    import pre_hhat.qasm_modules.cqasm as qasm
elif module == 'netqasm':
    import pre_hhat.qasm_modules.netqasm as qasm
elif module == 'openqasm':
    if device_type == 'simulator':
        from pre_hhat.qasm_modules.openqasm import QuantumSimulator as QuantumDevice
    elif device_type == 'hardware':
        from pre_hhat.qasm_modules.openqasm import QuantumHardware as QuantumDevice
elif module == 'q1asm':
    import pre_hhat.qasm_modules.q1asm as qasm
