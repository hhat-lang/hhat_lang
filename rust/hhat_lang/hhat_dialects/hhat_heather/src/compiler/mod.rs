use std::fs;
use std::path::Path;
use hhat_core::{BackendCompiler, CoreCompiler};
use hhat_core::frontend::base::FrontendCompiler;
use crate::ir::hir::HIRModule;
use crate::ir::mir::MIRModule;

pub struct HeatherCompiler {
    
}


impl FrontendCompiler for HeatherCompiler {
    type ParsedCode = HIRModule;
    type IRCode = MIRModule;

    fn parse(&mut self, source_code: String) -> Self::ParsedCode {
        todo!()
    }

    fn compile_to_ir(&mut self, parsed_code: Self::ParsedCode) -> Self::IRCode {
        todo!()
    }
}


impl BackendCompiler for HeatherCompiler {
    type IRCode = MIRModule;
    type MachineCode = ();

    fn compile_to_machine_code(&mut self, ir_code: Self::IRCode) -> Self::MachineCode {
        todo!()
    }
}


impl CoreCompiler for HeatherCompiler {
    type MachineCode = ();

    fn compile(&mut self, source_path: String) -> Self::MachineCode {
        let path = Path::new(&source_path);
        let source_code = fs::read_to_string(path).expect("could not open the file {path}");
        
        todo!()
    }
}
