#[allow(dead_code, unused_attributes, unused_attributes, unused_variables)]
mod ast;
mod compiler;
mod data_impl;
mod instr;
mod ir;
mod memory;

pub fn add(left: u64, right: u64) -> u64 {
    left + right
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() {
        let result = add(2, 2);
        assert_eq!(result, 4);
    }
}
