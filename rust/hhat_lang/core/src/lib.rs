#![allow(dead_code, unused)]

pub mod backend;
mod core;
pub mod frontend;
pub mod layout;

pub use backend::base::BackendCompiler;
pub use core::{CoreCompiler, Literal, SymbolId};
pub use frontend::base::IRInfra;

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {}
}
