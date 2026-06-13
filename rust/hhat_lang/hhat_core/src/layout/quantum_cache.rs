use std::collections::HashMap;

use crate::frontend::types::Ty;
use crate::layout::quantum::{QuantumField, QuantumLayout};


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
            Ty::Primitive(p) => QuantumLayout::Primitive(p.clone()),
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
                QuantumLayout::Struct(s.name.clone(), fields)
            }
            Ty::Enum(e) => {
                assert_eq!(
                    e.variants.len(),
                    2,
                    "quantum enums must have exactly 2 variants, got {}",
                    e.variants.len()
                );
                QuantumLayout::Enum(
                    e.name.clone(),
                    [
                        e.variants[0].name().clone(),
                        e.variants[1].name().clone(),
                    ],
                )
            }
            Ty::Array(_) => todo!("quantum array layout"),
        }
    }
}


#[cfg(test)]
mod tests {
    use super::*;
    use crate::frontend::types::{TyEnum, TyPrimitive, TyStruct};
    use crate::layout::arch::Arch;
    use crate::layout::base::LayoutCache;
    use crate::SymbolId;

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
    fn primitive_layout_keeps_type() {
        let mut cache = QuantumLayoutCache::new();
        assert!(matches!(
            cache.layout_of(&Ty::Primitive(TyPrimitive::QU4)),
            QuantumLayout::Primitive(TyPrimitive::QU4)
        ));
    }

    #[test]
    fn struct_sums_members() {
        let mut cache = QuantumLayoutCache::new();
        let layout = cache.layout_of(&bell_t());
        assert_eq!(layout.qubits(), 2);

        let QuantumLayout::Struct(name, fields) = &layout else {
            panic!("expected struct");
        };
        assert_eq!(*name, qsym(0));
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

        let QuantumLayout::Enum(name, variants) = &layout else {
            panic!("expected enum");
        };
        assert_eq!(*name, qsym(10));
        assert_eq!(variants, &[qsym(11), qsym(12)]);
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

        let QuantumLayout::Struct(_, fields) = &layout else {
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

        let QuantumLayout::Struct(_, fields) = &layout else {
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
}
