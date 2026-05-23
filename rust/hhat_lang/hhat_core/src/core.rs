use std::ops::{Index, IndexMut};


/// An instance that can be inside an arena.
///
pub trait Arenable {

}


/// An instance that can be used as an arena index holder.
///
pub trait ArenaIndexHolder {
    fn read(&self) -> u32;

    fn is_quantum(&self) -> bool;
}


/// SymbolId is used to store symbols from parsing to easily access them on
/// later steps in the compilation process.
///
/// First item is the actual position of the symbol in the arena, and the
/// second item is whether it is quantum data.
///
#[repr(C)]
#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub struct SymbolId(
    pub u32,  // position in arena
    pub bool  // is quantum?
);

impl ArenaIndexHolder for SymbolId {
    /// Get symbols' integer (`u32`) position in arena.
    ///
    fn read(&self) -> u32 { self.0 }

    /// Easily access to whether symbol is quantum.
    ///
    fn is_quantum(&self) -> bool { self.1 }
}


#[derive(Clone, Debug, PartialEq)]
pub enum Literal {
    // Classical
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
    // Quantum
    QBool(bool),
    QU2(u8),
    QU3(u8),
    QU4(u8),
    QU8(u8),
}

impl Literal {
    pub fn is_quantum(&self) -> bool {
        match self {
            // Classical
            Literal::Bool(_)
            | Literal::U32(_)
            | Literal::U64(_)
            | Literal::I32(_)
            | Literal::I64(_)
            | Literal::F32(_)
            | Literal::F64(_)
            | Literal::C64(_, _)
            | Literal::C128(_, _)
            | Literal::Str(_) => false,

            // Quantum
            Literal::QBool(_)
            | Literal::QU2(_)
            | Literal::QU3(_)
            | Literal::QU4(_)
            | Literal::QU8(_) => true,
        }
    }
}


/// TypeId is used to refer to type definition stored in an arena.
///
#[repr(C)]
#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub struct TypeId(
    pub u32,   // position in arena
    pub bool   // is quantum?
);


impl ArenaIndexHolder for TypeId {
    fn read(&self) -> u32 { self.0 }

    fn is_quantum(&self) -> bool { self.1 }
}


/// Arena to store relevant data such as variables, types, functions, etc.
///
pub struct Arena<T: Arenable + Clone> {
    data: Vec<T>,
}

impl<T> Arena<T>
where
    T: Arenable + Clone,
{
    pub fn new() -> Self {
        Self { data: Vec::<T>::new() }
    }

    pub fn push(&mut self, data: T) {
        self.data.push(data)
    }

    pub fn item<U: ArenaIndexHolder>(&self, id: &U) -> Option<&T> {
        self.data.get(id.read() as usize)
    }

    pub fn get(&self, index: usize) -> Option<&T> {
        self.data.get(index)
    }
}


pub trait CoreCompiler {
    type MachineCode;

    fn compile(&mut self, source_path: String) -> Self::MachineCode;
}
