#![allow(dead_code, unused)]

pub mod compiler;
pub mod cranelift;
mod ir;
pub mod q3l;
pub mod toolchain;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() {}
}
