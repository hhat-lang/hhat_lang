use std::path::Path;


#[repr(C)]
#[derive(Clone, Debug)]
pub struct SymbolId(pub u32);

impl SymbolId {
    pub fn read(&self) -> u32 { self.0 }
}


#[derive(Clone, Debug)]
pub enum Literal {
    Bool(bool),
    U32(u32),
    I32(i32),
    U64(u64),
    I64(i64),
    F32(f32),
    F64(f64),
    C64(f32, f32),
    C128(f64, f64),
    Str(String),
}



pub trait CoreCompiler {
    type MachineCode;

    fn compile(&mut self, source_path: String) -> Self::MachineCode;
}
