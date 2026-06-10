//!
//! Quantum memory layout for quantum data types.
//!
//! Classical layouts (see [`crate::layout::base`]) measure sizes in bytes and apply
//! alignment padding to satisfy Cranelift's requirements. Quantum layouts work
//! differently: they count *qubits*, and no alignment padding is applied.
//!
//! See [`QuantumTypeLayout`], [`QuantumLayoutCache`], and [`QuantumProgram`].

use std::collections::HashMap;
use crate::core::{ArenaIndexHolder, Arenable};
use crate::frontend::types::{Ty, TyEnum, TyPrimitive, TyStruct, TyVariants};
use crate::SymbolId;


/// Qubit count for a primitive quantum type.
///
/// Classical primitives are rejected; calling [`QuantumPrimitiveLayout::layout`]
/// on a non-quantum type will panic.
///
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
            other => panic!(
                "QuantumPrimitiveLayout::layout called on classical primitive: {:?}",
                other
            ),
        };
        Self { qubits }
    }
}

impl Arenable for QuantumPrimitiveLayout {}


/// Qubit layout for a quantum struct type.
///
/// Counts only the qubit-bearing (quantum) fields. Classical fields in a quantum
/// struct are valid but are handled by the classical LayoutCache — they do not
/// contribute to the qubit count here. No alignment padding is inserted.
///
#[derive(Clone, Debug)]
pub struct QuantumStructLayout {
    pub qubits: u32,
    pub members: Vec<QuantumMemberLayout>,
}

impl QuantumStructLayout {
    pub fn layout(ty: &TyStruct, cache: &mut QuantumLayoutCache) -> Self {
        let mut total: u32 = 0;
        let mut members: Vec<QuantumMemberLayout> = Vec::new();

        for (sid, member_ty) in ty.iter() {
            if !sid.is_quantum() {
                continue; // classical members belong to the classical layout
            }
            let member_layout = cache.layout_of(member_ty);
            let q = member_layout.qubits();
            members.push(QuantumMemberLayout {
                name: sid.clone(),
                qubit_offset: total,
                layout: member_layout,
            });
            total += q;
        }

        Self { qubits: total, members }
    }
}

impl Arenable for QuantumStructLayout {}


/// Qubit layout for a single struct member, including its offset within the parent.
///
#[derive(Clone, Debug)]
pub struct QuantumMemberLayout {
    pub name: SymbolId,
    pub qubit_offset: u32,
    pub layout: QuantumTypeLayout,
}


/// Qubit layout for a quantum enum type.
///
/// Quantum enums must have exactly 2 named variants. They always use 1 qubit:
/// the first variant maps to |0> and the second to |1>.
///
#[derive(Clone, Debug)]
pub struct QuantumEnumLayout {
    pub qubits: u32,
}

impl QuantumEnumLayout {
    pub fn layout(ty: &TyEnum) -> Self {
        let named_count = ty
            .variants
            .iter()
            .filter(|v| matches!(v, TyVariants::Named(_, _)))
            .count();
        assert_eq!(
            named_count, 2,
            "quantum enum {:?} must have exactly 2 named variants, found {}",
            ty.name, named_count
        );
        Self { qubits: 1 }
    }
}

impl Arenable for QuantumEnumLayout {}


/// Unified qubit descriptor for any quantum type.
///
#[derive(Clone, Debug)]
pub enum QuantumTypeLayout {
    Primitive(QuantumPrimitiveLayout),
    Struct(QuantumStructLayout),
    Enum(QuantumEnumLayout),
}

impl QuantumTypeLayout {
    pub fn qubits(&self) -> u32 {
        match self {
            QuantumTypeLayout::Primitive(l) => l.qubits,
            QuantumTypeLayout::Struct(l) => l.qubits,
            QuantumTypeLayout::Enum(l) => l.qubits,
        }
    }
}

impl Arenable for QuantumTypeLayout {}


/// A primitive quantum instruction that may request ancilla qubits.
///
#[derive(Clone, Debug)]
pub struct QuantumInstruction {
    pub ancilla_qubits: u32,
}

impl QuantumInstruction {
    pub fn new(ancilla_qubits: u32) -> Self {
        Self { ancilla_qubits }
    }
}


/// Program-wide cache for quantum type layouts.
///
pub struct QuantumLayoutCache {
    cache: HashMap<Ty, QuantumTypeLayout>,
}

impl QuantumLayoutCache {
    pub fn new() -> Self {
        Self { cache: HashMap::new() }
    }

    pub fn has(&self, ty: &Ty) -> bool {
        self.cache.contains_key(ty)
    }

    pub fn insert_layout(&mut self, ty: &Ty) {
        let layout = match ty {
            Ty::Primitive(p) => {
                QuantumTypeLayout::Primitive(QuantumPrimitiveLayout::layout(p))
            },
            Ty::Struct(s) => {
                for (sid, member_ty) in s.iter() {
                    if sid.is_quantum() && !self.cache.contains_key(member_ty) {
                        self.insert_layout(member_ty);
                    }
                }
                QuantumTypeLayout::Struct(QuantumStructLayout::layout(s, self))
            },
            Ty::Enum(e) => {
                QuantumTypeLayout::Enum(QuantumEnumLayout::layout(e))
            },
            Ty::Array(_) => {
                todo!("quantum array layout")
            },
        };
        self.cache.insert(ty.clone(), layout);
    }

    pub fn layout_of(&mut self, ty: &Ty) -> QuantumTypeLayout {
        if !self.cache.contains_key(ty) {
            self.insert_layout(ty);
        }
        self.cache[ty].clone()
    }
}

impl Default for QuantumLayoutCache {
    fn default() -> Self {
        Self::new()
    }
}


/// Tracks the full qubit and register requirements for a single quantum variable.
///
/// A quantum variable needs three things allocated before it can run:
/// data qubits from its declared type, ancilla qubits for the gates that operate
/// on it, and classical register bits for each attribute that gets measured (cast).
///
pub struct QuantumProgram {
    pub root_layout: QuantumTypeLayout,
    pub data_qubits: u32,
    pub ancilla_qubits: u32,
    pub classical_register_bits: u32,
}

impl QuantumProgram {
    pub fn new(root_layout: QuantumTypeLayout) -> Self {
        let data_qubits = root_layout.qubits();
        Self {
            root_layout,
            data_qubits,
            ancilla_qubits: 0,
            classical_register_bits: 0,
        }
    }

    pub fn add_instruction(&mut self, instr: &QuantumInstruction) {
        self.ancilla_qubits += instr.ancilla_qubits;
    }

    /// Called once for each quantum attribute that gets cast (measured) to classical.
    /// Each measurement produces one classical bit, so the register grows by one.
    ///
    pub fn cast_attribute(&mut self) {
        self.classical_register_bits += 1;
    }

    pub fn total_qubits(&self) -> u32 {
        self.data_qubits + self.ancilla_qubits
    }
}


#[cfg(test)]
mod tests {
    use crate::frontend::types::{Ty, TyEnum, TyPrimitive, TyStruct};
    use crate::layout::arch::Arch;
    use crate::layout::base::LayoutCache;
    use crate::layout::quantum::{
        QuantumEnumLayout, QuantumInstruction, QuantumLayoutCache,
        QuantumPrimitiveLayout, QuantumProgram, QuantumTypeLayout,
    };
    use crate::SymbolId;

    #[test]
    fn primitive_qbool_is_one_qubit() {
        assert_eq!(QuantumPrimitiveLayout::layout(&TyPrimitive::QBool).qubits, 1);
    }

    #[test]
    fn primitive_qu2_is_two_qubits() {
        assert_eq!(QuantumPrimitiveLayout::layout(&TyPrimitive::QU2).qubits, 2);
    }

    #[test]
    fn primitive_qu3_is_three_qubits() {
        assert_eq!(QuantumPrimitiveLayout::layout(&TyPrimitive::QU3).qubits, 3);
    }

    #[test]
    fn primitive_qu4_is_four_qubits() {
        assert_eq!(QuantumPrimitiveLayout::layout(&TyPrimitive::QU4).qubits, 4);
    }

    #[test]
    fn primitive_qu8_is_eight_qubits() {
        assert_eq!(QuantumPrimitiveLayout::layout(&TyPrimitive::QU8).qubits, 8);
    }

    #[test]
    #[should_panic]
    fn classical_primitive_rejected() {
        // Bool has no place in a quantum layout.
        QuantumPrimitiveLayout::layout(&TyPrimitive::Bool);
    }

    #[test]
    fn struct_two_qbools_equals_two_qubits() {
        // type @bell_t { @s:@bool, @t:@bool }  ->  2 qubits
        let mut cache = QuantumLayoutCache::new();
        let mut ty = TyStruct::new(&SymbolId(1, true));
        ty.add_member(&SymbolId(2, true), Ty::Primitive(TyPrimitive::QBool));
        ty.add_member(&SymbolId(3, true), Ty::Primitive(TyPrimitive::QBool));
        ty.done();

        assert_eq!(cache.layout_of(&Ty::Struct(ty)).qubits(), 2);
    }

    #[test]
    fn struct_mixed_primitive_sizes() {
        // type @mixed { @a:@bool, @b:@u4, @c:@u8 }  ->  1+4+8 = 13 qubits
        let mut cache = QuantumLayoutCache::new();
        let mut ty = TyStruct::new(&SymbolId(1, true));
        ty.add_member(&SymbolId(2, true), Ty::Primitive(TyPrimitive::QBool));
        ty.add_member(&SymbolId(3, true), Ty::Primitive(TyPrimitive::QU4));
        ty.add_member(&SymbolId(4, true), Ty::Primitive(TyPrimitive::QU8));
        ty.done();

        assert_eq!(cache.layout_of(&Ty::Struct(ty)).qubits(), 13);
    }

    #[test]
    fn enum_two_variants_is_one_qubit() {
        // type @polarization { @V, @H }
        let mut ty = TyEnum::new(&SymbolId(1, true));
        ty.add_variant(&SymbolId(2, true), None); // @V -> |0>
        ty.add_variant(&SymbolId(3, true), None); // @H -> |1>
        ty.done();

        assert_eq!(QuantumEnumLayout::layout(&ty).qubits, 1);
    }

    #[test]
    #[should_panic]
    fn enum_single_variant_rejected() {
        let mut ty = TyEnum::new(&SymbolId(1, true));
        ty.add_variant(&SymbolId(2, true), None);
        ty.done();
        QuantumEnumLayout::layout(&ty);
    }

    #[test]
    fn nested_struct_qubit_counts_stack() {
        // inner: { @a:@bool, @b:@u2 }       ->  3 qubits
        // outer: { @inner:inner, @c:@u4 }   ->  3+4 = 7 qubits
        let mut cache = QuantumLayoutCache::new();

        let mut inner = TyStruct::new(&SymbolId(1, true));
        inner.add_member(&SymbolId(2, true), Ty::Primitive(TyPrimitive::QBool));
        inner.add_member(&SymbolId(3, true), Ty::Primitive(TyPrimitive::QU2));
        inner.done();

        let mut outer = TyStruct::new(&SymbolId(4, true));
        outer.add_member(&SymbolId(5, true), Ty::Struct(inner));
        outer.add_member(&SymbolId(6, true), Ty::Primitive(TyPrimitive::QU4));
        outer.done();

        assert_eq!(cache.layout_of(&Ty::Struct(outer)).qubits(), 7);
    }

    #[test]
    fn deeply_nested_struct() {
        // a: { @x:@u2 }                ->  2
        // b: { @inner:a, @y:@u3 }      ->  2+3 = 5
        // c: { @middle:b, @z:@bool }   ->  5+1 = 6
        let mut cache = QuantumLayoutCache::new();

        let mut a = TyStruct::new(&SymbolId(1, true));
        a.add_member(&SymbolId(2, true), Ty::Primitive(TyPrimitive::QU2));
        a.done();

        let mut b = TyStruct::new(&SymbolId(3, true));
        b.add_member(&SymbolId(4, true), Ty::Struct(a));
        b.add_member(&SymbolId(5, true), Ty::Primitive(TyPrimitive::QU3));
        b.done();

        let mut c = TyStruct::new(&SymbolId(6, true));
        c.add_member(&SymbolId(7, true), Ty::Struct(b));
        c.add_member(&SymbolId(8, true), Ty::Primitive(TyPrimitive::QBool));
        c.done();

        assert_eq!(cache.layout_of(&Ty::Struct(c)).qubits(), 6);
    }

    #[test]
    fn classical_cache_sees_zero_for_quantum_primitive() {
        let mut lcache = LayoutCache::new(Arch::get_arch64());
        lcache.initialize(Some(Arch::get_arch64()));

        let classical = lcache.layout_of(&Ty::Primitive(TyPrimitive::QU4));
        assert_eq!(classical.size(), 0, "classical layout should be zero-sized for @u4");

        let mut qcache = QuantumLayoutCache::new();
        let quantum = qcache.layout_of(&Ty::Primitive(TyPrimitive::QU4));
        assert_eq!(quantum.qubits(), 4, "quantum layout should report 4 qubits for @u4");
    }

    #[test]
    fn classical_and_quantum_struct_layouts_agree_on_scope() {
        let mut lcache = LayoutCache::new(Arch::get_arch64());
        lcache.initialize(Some(Arch::get_arch64()));

        let mut ty = TyStruct::new(&SymbolId(1, true));
        ty.add_member(&SymbolId(2, true), Ty::Primitive(TyPrimitive::QBool));
        ty.add_member(&SymbolId(3, true), Ty::Primitive(TyPrimitive::QBool));
        ty.done();

        lcache.insert_layout(&Ty::Struct(ty.clone()), &Some(Arch::get_arch64()));
        let classical = lcache.layout_of(&Ty::Struct(ty.clone()));
        assert_eq!(classical.size(), 0);

        let mut qcache = QuantumLayoutCache::new();
        let quantum = qcache.layout_of(&Ty::Struct(ty));
        assert_eq!(quantum.qubits(), 2);
    }

    #[test]
    fn program_primitive_no_instructions() {
        let root = QuantumTypeLayout::Primitive(
            QuantumPrimitiveLayout::layout(&TyPrimitive::QU4)
        );
        let prog = QuantumProgram::new(root);

        assert_eq!(prog.data_qubits, 4);
        assert_eq!(prog.ancilla_qubits, 0);
        assert_eq!(prog.total_qubits(), 4);
        assert_eq!(prog.classical_register_bits, 0);
    }

    #[test]
    fn program_accumulates_ancilla_and_cast() {
        // @bell_t { @s:@bool, @t:@bool }
        // + instruction needing 1 ancilla
        // + instruction needing 2 ancilla
        // cast @v.@t -> 1 classical bit
        let mut cache = QuantumLayoutCache::new();

        let mut ty = TyStruct::new(&SymbolId(1, true));
        ty.add_member(&SymbolId(2, true), Ty::Primitive(TyPrimitive::QBool));
        ty.add_member(&SymbolId(3, true), Ty::Primitive(TyPrimitive::QBool));
        ty.done();

        let root = cache.layout_of(&Ty::Struct(ty));
        let mut prog = QuantumProgram::new(root);

        prog.add_instruction(&QuantumInstruction::new(1));
        prog.add_instruction(&QuantumInstruction::new(2));
        prog.cast_attribute();

        assert_eq!(prog.data_qubits, 2);
        assert_eq!(prog.ancilla_qubits, 3);
        assert_eq!(prog.total_qubits(), 5);
        assert_eq!(prog.classical_register_bits, 1);
    }

    #[test]
    fn program_enum_root_no_ancilla() {
        let mut ty = TyEnum::new(&SymbolId(1, true));
        ty.add_variant(&SymbolId(2, true), None);
        ty.add_variant(&SymbolId(3, true), None);
        ty.done();

        let mut cache = QuantumLayoutCache::new();
        let root = cache.layout_of(&Ty::Enum(ty));
        let prog = QuantumProgram::new(root);

        assert_eq!(prog.data_qubits, 1);
        assert_eq!(prog.total_qubits(), 1);
    }

    #[test]
    fn program_with_zero_ancilla_instruction() {
        let root = QuantumTypeLayout::Primitive(
            QuantumPrimitiveLayout::layout(&TyPrimitive::QBool)
        );
        let mut prog = QuantumProgram::new(root);
        prog.add_instruction(&QuantumInstruction::new(0));

        assert_eq!(prog.total_qubits(), 1);
    }

    #[test]
    fn cache_returns_same_layout_twice() {
        let mut cache = QuantumLayoutCache::new();
        let ty = Ty::Primitive(TyPrimitive::QU8);
        let first = cache.layout_of(&ty);
        let second = cache.layout_of(&ty);
        assert_eq!(first.qubits(), second.qubits());
    }

    #[test]
    fn cache_marks_type_as_present_after_insert() {
        let mut cache = QuantumLayoutCache::new();
        let ty = Ty::Primitive(TyPrimitive::QU3);
        assert!(!cache.has(&ty));
        let _ = cache.layout_of(&ty);
        assert!(cache.has(&ty));
    }
}
