

pub trait BackendCompiler {
    type IRCode;
    type MachineCode;

    fn compile_to_machine_code(&mut self, ir_code: Self::IRCode) -> Self::MachineCode;
}
