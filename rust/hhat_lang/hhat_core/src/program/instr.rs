//!
//! Primitive quantum instructions.
//!

use crate::SymbolId;


/// A primitive quantum instruction. Besides its identity it may append ancilla
/// qubits when lowered to the Q3L code.
///
#[derive(Clone, Debug)]
pub struct QuantumInstr {
    pub name: SymbolId,
    pub ancilla: u32,
}

impl QuantumInstr {
    pub fn new(name: &SymbolId, ancilla: u32) -> Self {
        Self { name: name.clone(), ancilla }
    }
}
