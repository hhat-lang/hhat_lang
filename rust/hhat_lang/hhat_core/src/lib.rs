#![allow(dead_code, unused)]

pub mod frontend;
pub mod backend;
mod core;
pub mod layout;

pub use frontend::base::IRInfra;
pub use backend::base::BackendCompiler;
pub use core::{CoreCompiler, Literal, SymbolId};
pub use layout::quantum::{
    PrimitiveQuantumInstr, QuantumLayoutCache, QuantumProgram, QuantumTypeLayout,
};


#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
    }
}
