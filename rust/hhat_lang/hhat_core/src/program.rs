use crate::frontend::types::Ty;
use crate::layout::quantum::QuantumLayout;
use crate::layout::quantum_cache::QuantumLayoutCache;
use crate::SymbolId;


#[derive(Clone, Debug)]
pub struct QuantumInstruction {
    pub ancilla: u32,
}

impl QuantumInstruction {
    pub fn new(ancilla: u32) -> Self {
        Self { ancilla }
    }
}


#[derive(Clone, Debug)]
pub struct QuantumProgram {
    pub var: SymbolId,
    pub layout: QuantumLayout,
    pub instructions: Vec<QuantumInstruction>,
    pub cast_attrs: Vec<SymbolId>,
}

impl QuantumProgram {
    pub fn from_cast(var: SymbolId, ty: &Ty, cache: &mut QuantumLayoutCache) -> Self {
        Self {
            var,
            layout: cache.layout_of(ty),
            instructions: Vec::new(),
            cast_attrs: Vec::new(),
        }
    }

    pub fn add_instruction(&mut self, instr: QuantumInstruction) {
        self.instructions.push(instr);
    }

    pub fn cast_attribute(&mut self, attr: SymbolId) {
        self.cast_attrs.push(attr);
    }

    pub fn data_qubits(&self) -> u32 {
        self.layout.qubits()
    }

    pub fn ancilla_qubits(&self) -> u32 {
        self.instructions.iter().map(|i| i.ancilla).sum()
    }

    pub fn total_qubits(&self) -> u32 {
        self.data_qubits() + self.ancilla_qubits()
    }

    pub fn classical_size(&self) -> u32 {
        self.cast_attrs.len() as u32
    }
}


#[cfg(test)]
mod tests {
    use super::*;
    use crate::frontend::types::{TyPrimitive, TyStruct};

    fn qsym(pos: u32) -> SymbolId {
        SymbolId(pos, true)
    }

    fn bell_t() -> Ty {
        let mut s = TyStruct::new(&qsym(0));
        s.add_member(&qsym(1), Ty::Primitive(TyPrimitive::QBool));
        s.add_member(&qsym(2), Ty::Primitive(TyPrimitive::QBool));
        s.done();
        Ty::Struct(s)
    }

    #[test]
    fn quantum_program_totals() {
        let mut cache = QuantumLayoutCache::new();

        let prog =
            QuantumProgram::from_cast(qsym(50), &Ty::Primitive(TyPrimitive::QU4), &mut cache);
        assert_eq!(prog.total_qubits(), 4);
        assert_eq!(prog.classical_size(), 0);

        for ancilla in [0u32, 1, 2, 3] {
            let mut prog = QuantumProgram::from_cast(qsym(50), &bell_t(), &mut cache);
            prog.add_instruction(QuantumInstruction::new(ancilla));
            prog.cast_attribute(qsym(2));
            assert_eq!(prog.data_qubits(), 2);
            assert_eq!(prog.ancilla_qubits(), ancilla);
            assert_eq!(prog.total_qubits(), 2 + ancilla);
            assert_eq!(prog.classical_size(), 1);
        }
    }
}
