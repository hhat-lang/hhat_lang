#![allow(dead_code, unused)]

pub mod frontend;
pub mod backend;
mod core;
pub mod layout;

pub use frontend::base::IRInfra;
pub use backend::base::BackendCompiler;
pub use core::{CoreCompiler, Literal, SymbolId};


#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
    }
}
