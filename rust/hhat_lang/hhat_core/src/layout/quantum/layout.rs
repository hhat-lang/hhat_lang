//!
//! Quantum layout definitions: the qubit-only layout of a type.
//!
//! No alignment and no padding; we cannot afford to waste qubits.
//!   - primitive qubit counts: `@bool`=1, `@u2`=2, `@u3`=3, `@u4`=4, `@u8`=8;
//!   - a struct stacks its quantum fields back-to-back (recursive);
//!   - a quantum enum (2-variant, for now) takes a single qubit (`|0>`/`|1>`).
//!

use crate::core::{Arenable, ArenaIndexHolder};
use crate::frontend::types::{Ty, TyEnum, TyPrimitive, TyStruct};
use crate::SymbolId;


/// Quantum layout of a type: qubit counts only, no alignment, no padding.
///
#[derive(Clone, Debug)]
pub enum QuantumLayout {
    Primitive(QuantumPrimitiveLayout),
    Struct(QuantumStructLayout),
    Enum(QuantumEnumLayout),
}

impl QuantumLayout {
    /// Total number of qubits this type occupies.
    ///
    pub fn qubits(&self) -> u32 {
        match self {
            QuantumLayout::Primitive(q) => q.qubits,
            QuantumLayout::Struct(q) => q.qubits,
            QuantumLayout::Enum(q) => q.qubits,
        }
    }

    /// Build the quantum layout for a type from the frontend type.
    ///
    pub fn layout(ty: &Ty) -> Self {
        match ty {
            Ty::Primitive(p) => QuantumLayout::Primitive(QuantumPrimitiveLayout::layout(p)),
            Ty::Struct(s) => QuantumLayout::Struct(QuantumStructLayout::layout(s)),
            Ty::Enum(e) => QuantumLayout::Enum(QuantumEnumLayout::layout(e)),
            Ty::Array(_) => todo!(),
        }
    }
}

impl Arenable for QuantumLayout {}


#[derive(Clone, Debug)]
pub struct QuantumPrimitiveLayout {
    pub qubits: u32,
}

impl QuantumPrimitiveLayout {
    pub fn layout(ty: &TyPrimitive) -> Self {
        let qubits = match ty {
            TyPrimitive::QBool => 1,
            TyPrimitive::QU2 => 2,
            TyPrimitive::QU3 => 3,
            TyPrimitive::QU4 => 4,
            TyPrimitive::QU8 => 8,
            _ => 0,
        };
        Self { qubits }
    }
}

impl Arenable for QuantumPrimitiveLayout {}


/// Quantum layout of a struct: its quantum fields packed back-to-back (no
/// padding) plus the total qubit count. Classical fields hold no qubits and are
/// left out.
///
#[derive(Clone, Debug)]
pub struct QuantumStructLayout {
    pub qubits: u32,
    pub members: Vec<QuantumMemberLayout>,
}

impl QuantumStructLayout {
    pub fn layout(ty: &TyStruct) -> Self {
        let mut offset: u32 = 0;
        let mut members: Vec<QuantumMemberLayout> = Vec::with_capacity(
            ty.members.iter().filter(|(field_sid, _ty)| field_sid.is_quantum()).count()
        );
        let _ = ty.iter().map(|(sid, t)| {
            let layout = QuantumLayout::layout(t);
            let tmp_qubits = layout.qubits();
            if tmp_qubits > 0 {  // only quantum fields take qubits
                members.push(
                    QuantumMemberLayout {
                        name: sid.clone(),
                        offset,
                        layout,
                    }
                );
                offset += tmp_qubits;
            }
        }).collect::<Vec<()>>();

        Self {
            qubits: offset,
            members,
        }
    }

    /// Quantum field (attribute) with the given name, if any.
    ///
    pub fn member(&self, name: &SymbolId) -> Option<&QuantumMemberLayout> {
        self.members.iter().find(|m| m.name == *name)
    }

    pub fn get(&self, index: usize) -> Option<&QuantumMemberLayout> {
        self.members.get(index)
    }
}

impl Arenable for QuantumStructLayout {}


/// A quantum attribute (struct field): its name, the qubit `offset` of its
/// first qubit inside the struct (no padding), and its own quantum layout.
///
#[derive(Clone, Debug)]
pub struct QuantumMemberLayout {
    pub name: SymbolId,
    pub offset: u32,
    pub layout: QuantumLayout,
}


/// Quantum layout of an enum. For now only 2-variant quantum enums exist and
/// they take a single qubit; classical enums hold no qubits.
///
#[derive(Clone, Debug)]
pub struct QuantumEnumLayout {
    pub qubits: u32,
    /// variant names in order; the first and second map to `|0>` and `|1>`
    pub variants: Vec<SymbolId>,
}

impl QuantumEnumLayout {
    pub fn layout(ty: &TyEnum) -> Self {
        let variants: Vec<SymbolId> = ty.iter().map(|v| v.name().clone()).collect();
        Self {
            qubits: if ty.is_quantum() { 1 } else { 0 },
            variants,
        }
    }
}

impl Arenable for QuantumEnumLayout {}


#[cfg(test)]
mod tests {
    use crate::frontend::types::{Ty, TyEnum, TyPrimitive, TyStruct};
    use crate::layout::arch::Arch;
    use crate::layout::base::LayoutCache;
    use crate::layout::quantum::QuantumLayout;
    use crate::SymbolId;

    /// Check the qubit count for every primitive quantum type.
    ///
    #[test]
    fn check_quantum_primitive_layouts() {
        // @bool: 1, @u2: 2, @u3: 3, @u4: 4, @u8: 8
        let prims = [
            (TyPrimitive::QBool, 1u32),
            (TyPrimitive::QU2, 2u32),
            (TyPrimitive::QU3, 3u32),
            (TyPrimitive::QU4, 4u32),
            (TyPrimitive::QU8, 8u32),
        ];
        let _ = prims.iter().map(|(p, qubits)| {
            let qlayout = QuantumLayout::layout(&Ty::Primitive(p.clone()));
            println!("quantum primitive layout: {:?}", qlayout);
            assert_eq!(qlayout.qubits(), *qubits);
        }).collect::<Vec<()>>();
    }

    /// Check a simple quantum struct: @bell_t { @s:@bool, @t:@bool } => 2 qubits,
    /// fields packed at offsets 0 and 1.
    ///
    #[test]
    fn check_quantum_struct_layout() {
        let bell_name = SymbolId(1, true);
        let s_name = SymbolId(2, true);
        let t_name = SymbolId(3, true);
        let mut bell_ty = TyStruct::new(&bell_name);
        bell_ty.add_member(&s_name, Ty::Primitive(TyPrimitive::QBool));
        bell_ty.add_member(&t_name, Ty::Primitive(TyPrimitive::QBool));
        bell_ty.done();

        let qlayout = QuantumLayout::layout(&Ty::Struct(bell_ty));
        println!("quantum struct layout: {:?}", qlayout);
        assert_eq!(qlayout.qubits(), 2);

        let qstruct = match qlayout {
            QuantumLayout::Struct(q) => q,
            other => panic!("expected quantum struct layout, got {:?}", other),
        };
        assert_eq!(qstruct.members.len(), 2);
        assert_eq!(qstruct.members[0].name, s_name);
        assert_eq!(qstruct.members[0].offset, 0);
        assert_eq!(qstruct.members[1].name, t_name);
        assert_eq!(qstruct.members[1].offset, 1);
    }

    /// Check a simple quantum enum: @polarization { @V, @H } => 1 qubit.
    ///
    #[test]
    fn check_quantum_enum_layout() {
        let polarization_name = SymbolId(1, true);
        let v_name = SymbolId(2, true);
        let h_name = SymbolId(3, true);
        let mut polarization_ty = TyEnum::new(&polarization_name);
        polarization_ty.add_variant(&v_name, None);
        polarization_ty.add_variant(&h_name, None);
        polarization_ty.done();

        let qlayout = QuantumLayout::layout(&Ty::Enum(polarization_ty));
        println!("quantum enum layout: {:?}", qlayout);
        assert_eq!(qlayout.qubits(), 1);

        let qenum = match qlayout {
            QuantumLayout::Enum(q) => q,
            other => panic!("expected quantum enum layout, got {:?}", other),
        };
        // @V -> |0>, @H -> |1>
        assert_eq!(qenum.variants, vec![v_name, h_name]);
    }

    /// Check a nested quantum struct:
    /// @bell_t { @s:@bool, @t:@bool }       => 2 qubits
    /// @outer  { @a:@bool, @inner:@bell_t } => 1 + 2 = 3 qubits
    ///
    #[test]
    fn check_nested_quantum_struct_layout() {
        let bell_name = SymbolId(1, true);
        let mut bell_ty = TyStruct::new(&bell_name);
        bell_ty.add_member(&SymbolId(2, true), Ty::Primitive(TyPrimitive::QBool));
        bell_ty.add_member(&SymbolId(3, true), Ty::Primitive(TyPrimitive::QBool));
        bell_ty.done();

        let outer_name = SymbolId(4, true);
        let inner_name = SymbolId(5, true);
        let mut outer_ty = TyStruct::new(&outer_name);
        outer_ty.add_member(&SymbolId(6, true), Ty::Primitive(TyPrimitive::QBool));
        outer_ty.add_member(&inner_name, Ty::Struct(bell_ty));
        outer_ty.done();

        let qlayout = QuantumLayout::layout(&Ty::Struct(outer_ty));
        println!("nested quantum struct layout: {:?}", qlayout);
        assert_eq!(qlayout.qubits(), 3);

        let qstruct = match qlayout {
            QuantumLayout::Struct(q) => q,
            other => panic!("expected quantum struct layout, got {:?}", other),
        };
        assert_eq!(qstruct.members[0].offset, 0);  // @a
        assert_eq!(qstruct.members[1].offset, 1);  // @inner
        // the nested field is itself a quantum struct of 2 qubits
        assert_eq!(qstruct.members[1].layout.qubits(), 2);
    }

    /// Check a struct mixing classical and quantum fields: only the quantum
    /// fields appear in the quantum layout, packed with no alignment.
    ///
    #[test]
    fn check_mixed_quantum_struct_layout() {
        // type @mixed { c1:U32, @q1:@bool, c2:Bool, @q2:@u8 }
        // quantum layout: @q1 @0 (1q), @q2 @1 (8q) => 9 qubits
        let mixed_name = SymbolId(1, true);
        let q1_name = SymbolId(3, true);
        let q2_name = SymbolId(5, true);
        let mut mixed_ty = TyStruct::new(&mixed_name);
        mixed_ty.add_member(&SymbolId(2, false), Ty::Primitive(TyPrimitive::U32));
        mixed_ty.add_member(&q1_name, Ty::Primitive(TyPrimitive::QBool));
        mixed_ty.add_member(&SymbolId(4, false), Ty::Primitive(TyPrimitive::Bool));
        mixed_ty.add_member(&q2_name, Ty::Primitive(TyPrimitive::QU8));
        mixed_ty.done();

        let qlayout = QuantumLayout::layout(&Ty::Struct(mixed_ty));
        println!("mixed quantum struct layout: {:?}", qlayout);
        assert_eq!(qlayout.qubits(), 9);

        let qstruct = match qlayout {
            QuantumLayout::Struct(q) => q,
            other => panic!("expected quantum struct layout, got {:?}", other),
        };
        // only the quantum fields, no classical ones
        assert_eq!(qstruct.members.len(), 2);
        assert_eq!(qstruct.members[0].name, q1_name);
        assert_eq!(qstruct.members[0].offset, 0);
        assert_eq!(qstruct.members[1].name, q2_name);
        assert_eq!(qstruct.members[1].offset, 1);
        assert_eq!(qstruct.member(&q2_name).unwrap().layout.qubits(), 8);
    }

    /// Check a struct holding a mixed inner struct (classical + quantum fields):
    /// only the inner quantum field's qubits count, the classical one is ignored.
    ///
    #[test]
    fn check_mixed_inner_struct_layout() {
        // type @inner { c:U32, @q:@u4 }  => 4 qubits on the quantum side
        let inner_name = SymbolId(1, true);
        let q_name = SymbolId(3, true);
        let mut inner_ty = TyStruct::new(&inner_name);
        inner_ty.add_member(&SymbolId(2, false), Ty::Primitive(TyPrimitive::U32));
        inner_ty.add_member(&q_name, Ty::Primitive(TyPrimitive::QU4));
        inner_ty.done();

        // type @wrap { @a:@bool, inner:@inner } => 1 + 4 = 5 qubits
        let wrap_name = SymbolId(4, true);
        let inner_field = SymbolId(6, true);
        let mut wrap_ty = TyStruct::new(&wrap_name);
        wrap_ty.add_member(&SymbolId(5, true), Ty::Primitive(TyPrimitive::QBool));
        wrap_ty.add_member(&inner_field, Ty::Struct(inner_ty));
        wrap_ty.done();

        let qlayout = QuantumLayout::layout(&Ty::Struct(wrap_ty));
        println!("mixed inner struct quantum layout: {:?}", qlayout);
        assert_eq!(qlayout.qubits(), 5);

        let qstruct = match qlayout {
            QuantumLayout::Struct(q) => q,
            other => panic!("expected quantum struct layout, got {:?}", other),
        };
        assert_eq!(qstruct.members.len(), 2);
        assert_eq!(qstruct.members[0].offset, 0);  // @a
        assert_eq!(qstruct.members[1].offset, 1);  // inner, packed right after @a
        assert_eq!(qstruct.member(&inner_field).unwrap().layout.qubits(), 4);
    }

    /// Check a type that also has a classical TypeLayout can have its quantum
    /// layout built: the two are independent derivations of the same type.
    ///
    #[test]
    fn check_typelayout_to_quantum_layout() {
        let mut lcache = LayoutCache::new(Arch::get_arch64());
        lcache.initialize(Some(Arch::get_arch64()));

        // a quantum struct also goes through the (untouched) classical pass
        let bell_name = SymbolId(1, true);
        let mut bell_ty = TyStruct::new(&bell_name);
        bell_ty.add_member(&SymbolId(2, true), Ty::Primitive(TyPrimitive::QBool));
        bell_ty.add_member(&SymbolId(3, true), Ty::Primitive(TyPrimitive::QBool));
        bell_ty.done();

        lcache.insert_layout(&Ty::Struct(bell_ty.clone()), &Some(Arch::get_arch64()));
        let classical = lcache.layout_of(&Ty::Struct(bell_ty.clone()));
        // quantum data occupies no classical memory
        assert_eq!(classical.size(), 0);

        // the quantum layout is derived separately, from the type
        let quantum = QuantumLayout::layout(&Ty::Struct(bell_ty));
        assert_eq!(quantum.qubits(), 2);
    }
}
