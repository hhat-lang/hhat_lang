//! Base infrastructure for dialects, IR objects, and compilation frameworks
//! implementations.
//!
//!


/// Common trait for IR implementations.
///
/// Ideally, any kind of representation should have this trait implemented
/// (e.g. `AST`, `HIR`, `THIR`, `MIR`, `LIR`, etc.)
///
pub trait IRInfra {
    // TODO: place all the relevant functions later
}



pub trait FrontendCompiler {
    type ParsedCode;
    type IRCode;

    fn parse(&mut self, source_code: String) -> Self::ParsedCode;

    fn compile_to_ir(&mut self, parsed_code: Self::ParsedCode) -> Self::IRCode;
}

