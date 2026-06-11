use std::collections::HashMap;

use crate::frontend::types::{Ty, TyPrimitive};
use crate::SymbolId;


#[derive(Clone, Debug)]
pub enum QuantumLayout {
    Primitive(u32),
    Struct(Vec<QuantumField>),
    Enum(Vec<SymbolId>),
}

impl QuantumLayout {
    pub fn qubits(&self) -> u32 {
        match self {
            QuantumLayout::Primitive(q) => *q,
            QuantumLayout::Struct(fields) => fields.iter().map(|f| f.layout.qubits()).sum(),
            QuantumLayout::Enum(_) => 1,
        }
    }

    pub fn field(&self, name: &SymbolId) -> Option<&QuantumField> {
        match self {
            QuantumLayout::Struct(fields) => fields.iter().find(|f| f.name == *name),
            _ => None,
        }
    }
}


#[derive(Clone, Debug)]
pub struct QuantumField {
    pub name: SymbolId,
    pub offset: u32,
    pub layout: QuantumLayout,
}


pub fn primitive_qubits(ty: &TyPrimitive) -> u32 {
    match ty {
        TyPrimitive::QBool => 1,
        TyPrimitive::QU2 => 2,
        TyPrimitive::QU3 => 3,
        TyPrimitive::QU4 => 4,
        TyPrimitive::QU8 => 8,
        _ => 0,
    }
}


#[derive(Default)]
pub struct QuantumLayoutCache {
    cache: HashMap<Ty, QuantumLayout>,
}

impl QuantumLayoutCache {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn layout_of(&mut self, ty: &Ty) -> QuantumLayout {
        if let Some(layout) = self.cache.get(ty) {
            return layout.clone();
        }
        let layout = self.build(ty);
        self.cache.insert(ty.clone(), layout.clone());
        layout
    }

    fn build(&mut self, ty: &Ty) -> QuantumLayout {
        match ty {
            Ty::Primitive(p) => QuantumLayout::Primitive(primitive_qubits(p)),
            Ty::Struct(s) => {
                let mut fields = Vec::new();
                let mut offset = 0;
                for (name, member) in s.iter() {
                    if !member.is_quantum() {
                        continue;
                    }
                    let layout = self.layout_of(member);
                    let qubits = layout.qubits();
                    fields.push(QuantumField {
                        name: name.clone(),
                        offset,
                        layout,
                    });
                    offset += qubits;
                }
                QuantumLayout::Struct(fields)
            }
            Ty::Enum(e) => {
                assert_eq!(
                    e.variants.len(),
                    2,
                    "quantum enums must have exactly 2 variants, got {}",
                    e.variants.len()
                );
                QuantumLayout::Enum(e.iter().map(|v| v.name().clone()).collect())
            }
            Ty::Array(_) => todo!("quantum array layout"),
        }
    }
}


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
    use crate::frontend::types::{TyEnum, TyStruct};
    use crate::layout::arch::Arch;
    use crate::layout::base::LayoutCache;

    fn qsym(pos: u32) -> SymbolId {
        SymbolId(pos, true)
    }

    fn csym(pos: u32) -> SymbolId {
        SymbolId(pos, false)
    }

    fn bell_t() -> Ty {
        let mut s = TyStruct::new(&qsym(0));
        s.add_member(&qsym(1), Ty::Primitive(TyPrimitive::QBool));
        s.add_member(&qsym(2), Ty::Primitive(TyPrimitive::QBool));
        s.done();
        Ty::Struct(s)
    }

    fn polarization() -> Ty {
        let mut e = TyEnum::new(&qsym(10));
        e.add_variant(&qsym(11), None);
        e.add_variant(&qsym(12), None);
        e.done();
        Ty::Enum(e)
    }

    #[test]
    fn primitive_qubit_counts() {
        assert_eq!(primitive_qubits(&TyPrimitive::QBool), 1);
        assert_eq!(primitive_qubits(&TyPrimitive::QU2), 2);
        assert_eq!(primitive_qubits(&TyPrimitive::QU3), 3);
        assert_eq!(primitive_qubits(&TyPrimitive::QU4), 4);
        assert_eq!(primitive_qubits(&TyPrimitive::QU8), 8);
    }

    #[test]
    fn struct_sums_members() {
        let mut cache = QuantumLayoutCache::new();
        let layout = cache.layout_of(&bell_t());
        assert_eq!(layout.qubits(), 2);

        let QuantumLayout::Struct(fields) = &layout else {
            panic!("expected struct");
        };
        assert_eq!(fields.len(), 2);
        assert_eq!(fields[0].offset, 0);
        assert_eq!(fields[1].offset, 1);
        assert_eq!(layout.field(&qsym(2)).unwrap().offset, 1);
    }

    #[test]
    fn enum_is_one_qubit() {
        let mut cache = QuantumLayoutCache::new();
        let layout = cache.layout_of(&polarization());
        assert_eq!(layout.qubits(), 1);

        let QuantumLayout::Enum(variants) = &layout else {
            panic!("expected enum");
        };
        assert_eq!(variants, &vec![qsym(11), qsym(12)]);
    }

    #[test]
    fn nested_struct_recurses() {
        let mut nested = TyStruct::new(&qsym(20));
        nested.add_member(&qsym(21), bell_t());
        nested.add_member(&qsym(22), Ty::Primitive(TyPrimitive::QU4));
        nested.add_member(&qsym(23), polarization());
        nested.done();

        let mut cache = QuantumLayoutCache::new();
        let layout = cache.layout_of(&Ty::Struct(nested));
        assert_eq!(layout.qubits(), 7);

        let QuantumLayout::Struct(fields) = &layout else {
            panic!("expected struct");
        };
        let offsets: Vec<u32> = fields.iter().map(|f| f.offset).collect();
        assert_eq!(offsets, vec![0, 2, 6]);
    }

    #[test]
    fn struct_ignores_classical_members() {
        let mut mixed = TyStruct::new(&qsym(30));
        mixed.add_member(&qsym(31), Ty::Primitive(TyPrimitive::QBool));
        mixed.add_member(&csym(32), Ty::Primitive(TyPrimitive::Bool));
        mixed.done();

        let mut cache = QuantumLayoutCache::new();
        let layout = cache.layout_of(&Ty::Struct(mixed));
        assert_eq!(layout.qubits(), 1);

        let QuantumLayout::Struct(fields) = &layout else {
            panic!("expected struct");
        };
        assert_eq!(fields.len(), 1);
    }

    #[test]
    #[should_panic]
    fn enum_rejects_more_than_two_variants() {
        let mut e = TyEnum::new(&qsym(40));
        e.add_variant(&qsym(41), None);
        e.add_variant(&qsym(42), None);
        e.add_variant(&qsym(43), None);
        e.done();
        QuantumLayoutCache::new().layout_of(&Ty::Enum(e));
    }

    #[test]
    fn classical_layout_is_blind_quantum_layout_is_not() {
        let mut classical = LayoutCache::new(Arch::get_arch64());
        classical.initialize(Some(Arch::get_arch64()));
        classical.insert_layout(&bell_t(), &Some(Arch::get_arch64()));
        assert_eq!(classical.layout_of(&bell_t()).size(), 0);

        let mut quantum = QuantumLayoutCache::new();
        assert_eq!(
            quantum.layout_of(&Ty::Primitive(TyPrimitive::QU4)).qubits(),
            4
        );
        assert_eq!(quantum.layout_of(&bell_t()).qubits(), 2);
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
