#![allow(dead_code, unused)]

mod ir;
pub mod compiler;
pub mod q3l;
pub mod cranelift;
pub mod toolchain;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() {
    }
}
