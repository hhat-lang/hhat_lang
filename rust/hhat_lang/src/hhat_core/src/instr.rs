use crate::ir::Identifier;

//-----------------------
// QUANTUM INSTRUCTIONS
//-----------------------

/// Quantum instruction handler
pub struct QuantumInstr<'a> {
    pub id: Identifier,
}

impl<'a> CodeInstr<'a> for QuantumInstr<'a> {
    fn new(&mut self, id: Identifier) -> Self {
        QuantumInstr { id }
    }

    fn push<T>(&mut self, value: &T) -> Self {
        todo!()
    }

    fn get<T>(&mut self) -> Option<&T> {
        todo!()
    }
}

//-------------------------
// CLASSICAL INSTRUCTIONS
//-------------------------

/// Classical instruction handler
pub struct ClassicalInstr<'a> {
    pub id: Identifier,
}

/// Classical and quantum instructions data holder
pub struct Instructions<'a> {
    data: Vec<dyn CodeInstr<'a>>,
}

//---------------------------
// CODE INSTRUCTIONS TRAITS
//---------------------------

/// To be implemented by classical and quantum instructions
pub trait CodeInstr<'a> {
    fn new(&mut self, id: Identifier) -> Self;
    fn push<T>(&mut self, value: &T) -> Self;
    fn get<T>(&mut self) -> Option<&T>;
}
