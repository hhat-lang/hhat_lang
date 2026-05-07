use cranelift_codegen::ir::{Type, types};


#[derive(Clone, Copy, Debug)]
pub struct Arch {
    pub pointer_size: u32,
    pub pointer_align: u32,
    pub pointer_type: Type,
}


impl Arch {
    pub fn get_arch32() -> Self {
        Self {
            pointer_size: 4,
            pointer_align: 4,
            pointer_type: types::I32,
        }
    }

    pub fn get_arch64() -> Self {
        Self {
            pointer_size: 8,
            pointer_align: 8,
            pointer_type: types::I64,
        }
    }

}