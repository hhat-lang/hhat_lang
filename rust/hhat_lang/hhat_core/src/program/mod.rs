//!
//! Quantum programs.
//!
//! A quantum program is everything that happens under a single quantum variable
//! once it is cast: its quantum layout, the primitive quantum instructions
//! applied to it, and the cast attributes that form the classical register.
//! This is a separate concern from laying types out, which lives in
//! [`crate::layout`]; the primitive quantum instructions live in [`instr`].
//!

pub mod instr;

use crate::frontend::types::Ty;
use crate::layout::quantum::{QuantumLayout, QuantumLayoutCache};
use crate::SymbolId;

pub use instr::QuantumInstr;


/// Everything that happens under a single quantum variable.
///
/// Built when the variable is cast, it holds the variable's quantum layout, the
/// primitive quantum instructions applied to it (each carrying ancilla qubits),
/// and the cast attributes that define the classical register.
///
#[derive(Clone, Debug)]
pub struct QuantumProgram {
    pub var: SymbolId,
    pub layout: QuantumLayout,
    pub instrs: Vec<QuantumInstr>,
    pub cast: Vec<SymbolId>,
}

impl QuantumProgram {
    pub fn new(var: &SymbolId, layout: QuantumLayout) -> Self {
        Self {
            var: var.clone(),
            layout,
            instrs: Vec::new(),
            cast: Vec::new(),
        }
    }

    /// Build the program for a quantum variable from its type, using and
    /// populating the permanent quantum layout cache.
    ///
    pub fn from_variable(var: &SymbolId, ty: &Ty, qlayouts: &mut QuantumLayoutCache) -> Self {
        let layout = qlayouts.layout_of(ty);
        Self::new(var, layout)
    }

    pub fn add_instr(&mut self, instr: QuantumInstr) {
        self.instrs.push(instr)
    }

    pub fn add_cast(&mut self, attr: &SymbolId) {
        self.cast.push(attr.clone())
    }

    /// Qubit range `(offset, width)` of a quantum attribute inside the variable's
    /// register, so the Q3L code knows which qubits to name and measure for that
    /// attribute. The whole variable maps to its full register.
    ///
    pub fn attr_qubits(&self, attr: &SymbolId) -> Option<(u32, u32)> {
        if *attr == self.var {
            return Some((0, self.qsize()));
        }
        match &self.layout {
            QuantumLayout::Struct(s) => s.member(attr).map(|m| (m.offset, m.layout.qubits())),
            _ => None,
        }
    }

    /// Qubits used by the variable's quantum data.
    ///
    pub fn qsize(&self) -> u32 {
        self.layout.qubits()
    }

    /// Ancilla qubits required by the quantum instructions.
    ///
    pub fn ancilla(&self) -> u32 {
        self.instrs.iter().map(|i| i.ancilla).sum()
    }

    /// Total quantum memory size: data qubits plus instruction ancillas.
    ///
    pub fn qmem_size(&self) -> u32 {
        self.qsize() + self.ancilla()
    }

    /// Classical register size: the qubits of the cast attributes, since
    /// measuring an attribute yields that many classical bits.
    ///
    pub fn csize(&self) -> u32 {
        // casting the whole variable measures the whole register
        if self.cast.contains(&self.var) {
            return self.qsize();
        }
        match &self.layout {
            QuantumLayout::Struct(s) => s.members.iter()
                .filter(|m| self.cast.contains(&m.name))
                .map(|m| m.layout.qubits())
                .sum(),
            _ => 0,
        }
    }
}


#[cfg(test)]
mod tests {
    use crate::frontend::types::{Ty, TyPrimitive, TyStruct};
    use crate::layout::quantum::QuantumLayoutCache;
    use crate::program::QuantumProgram;
    use crate::program::instr::QuantumInstr;
    use crate::SymbolId;

    /// Check the logic from a quantum type (a struct) and a dummy quantum
    /// instruction (ancilla 0 to 3) into a QuantumProgram with the full quantum
    /// memory mapped out, including the ancillas.
    ///
    #[test]
    fn check_quantum_program() {
        // type @bell_t { @s:@bool, @t:@bool }
        let bell_name = SymbolId(1, true);
        let s_name = SymbolId(2, true);
        let t_name = SymbolId(3, true);
        let mut bell_ty = TyStruct::new(&bell_name);
        bell_ty.add_member(&s_name, Ty::Primitive(TyPrimitive::QBool));
        bell_ty.add_member(&t_name, Ty::Primitive(TyPrimitive::QBool));
        bell_ty.done();

        let mut qcache = QuantumLayoutCache::new();
        let v_name = SymbolId(4, true);
        let sync_name = SymbolId(5, true);

        let _ = (0u32..=3).map(|ancilla| {
            let mut prog = QuantumProgram::from_variable(
                &v_name, &Ty::Struct(bell_ty.clone()), &mut qcache,
            );
            prog.add_instr(QuantumInstr::new(&sync_name, ancilla));
            prog.add_cast(&t_name);  // only @v.@t is cast => creg res[1]
            println!("quantum program: {:?}", prog);

            assert_eq!(prog.qsize(), 2);
            assert_eq!(prog.ancilla(), ancilla);
            assert_eq!(prog.qmem_size(), 2 + ancilla);
            assert_eq!(prog.csize(), 1);
        }).collect::<Vec<()>>();
    }

    /// Check a primitive quantum variable @q:@u8 and a dummy quantum instruction
    /// (ancilla 0 to 3) build a whole-variable program.
    ///
    #[test]
    fn check_quantum_program_primitive_variable() {
        let mut qcache = QuantumLayoutCache::new();
        let q_name = SymbolId(1, true);
        let instr_name = SymbolId(2, true);

        let _ = (0u32..=3).map(|ancilla| {
            let mut prog = QuantumProgram::from_variable(
                &q_name, &Ty::Primitive(TyPrimitive::QU8), &mut qcache,
            );
            prog.add_instr(QuantumInstr::new(&instr_name, ancilla));
            prog.add_cast(&q_name);
            println!("quantum program (primitive): {:?}", prog);

            assert_eq!(prog.qsize(), 8);
            assert_eq!(prog.ancilla(), ancilla);
            assert_eq!(prog.qmem_size(), 8 + ancilla);
            assert_eq!(prog.csize(), 8);  // whole @u8 cast => 8 classical bits
        }).collect::<Vec<()>>();
    }

    /// Check the classical register reflects the qubit width of the cast
    /// attributes: nothing cast gives 0, a @u8 attribute gives 8, both give 9.
    ///
    #[test]
    fn check_quantum_program_classical_register() {
        // type @reg { @a:@bool, @b:@u8 }
        let reg_name = SymbolId(1, true);
        let a_name = SymbolId(2, true);
        let b_name = SymbolId(3, true);
        let mut reg_ty = TyStruct::new(&reg_name);
        reg_ty.add_member(&a_name, Ty::Primitive(TyPrimitive::QBool));
        reg_ty.add_member(&b_name, Ty::Primitive(TyPrimitive::QU8));
        reg_ty.done();

        let mut qcache = QuantumLayoutCache::new();
        let v_name = SymbolId(4, true);

        // nothing cast
        let prog = QuantumProgram::from_variable(&v_name, &Ty::Struct(reg_ty.clone()), &mut qcache);
        assert_eq!(prog.qsize(), 9);
        assert_eq!(prog.csize(), 0);

        // only @b:@u8 cast => 8 classical bits (not 1)
        let mut prog = QuantumProgram::from_variable(&v_name, &Ty::Struct(reg_ty.clone()), &mut qcache);
        prog.add_cast(&b_name);
        assert_eq!(prog.csize(), 8);

        // both cast => 1 + 8 = 9 classical bits
        prog.add_cast(&a_name);
        assert_eq!(prog.csize(), 9);
    }

    /// Check each quantum attribute maps to its qubit range inside the register,
    /// so the Q3L code can name and measure the right qubits.
    ///
    #[test]
    fn check_quantum_program_attr_qubits() {
        // type @reg { @a:@bool, @b:@u8 }  =>  @a at qubit 0 (1q), @b at qubit 1 (8q)
        let reg_name = SymbolId(1, true);
        let a_name = SymbolId(2, true);
        let b_name = SymbolId(3, true);
        let mut reg_ty = TyStruct::new(&reg_name);
        reg_ty.add_member(&a_name, Ty::Primitive(TyPrimitive::QBool));
        reg_ty.add_member(&b_name, Ty::Primitive(TyPrimitive::QU8));
        reg_ty.done();

        let mut qcache = QuantumLayoutCache::new();
        let v_name = SymbolId(4, true);
        let prog = QuantumProgram::from_variable(&v_name, &Ty::Struct(reg_ty), &mut qcache);

        assert_eq!(prog.attr_qubits(&a_name), Some((0, 1)));
        assert_eq!(prog.attr_qubits(&b_name), Some((1, 8)));
        // the whole variable maps to its full register
        assert_eq!(prog.attr_qubits(&v_name), Some((0, 9)));
        // an unknown attribute has no mapping
        assert_eq!(prog.attr_qubits(&SymbolId(99, true)), None);
    }
}
