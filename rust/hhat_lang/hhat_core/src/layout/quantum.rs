//!
//! Quantum memory layouts.
//!
//! Mirrors the classical [`crate::layout::base`] machinery, but for qubits:
//!   - **no alignment / no padding** — we cannot afford to waste qubits;
//!   - primitive qubit counts: `@bool`=1, `@u2`=2, `@u3`=3, `@u4`=4, `@u8`=8;
//!   - struct = sum of its members' qubits (recursive);
//!   - enum (2-variant only, for now) = 1 qubit (`|0>` / `|1>`).
//!
//! A [`QuantumProgram`] is created whenever a quantum variable completes its
//! cycle (declaration, assignment, cast). It owns the variable's quantum type
//! layout plus the primitive quantum instructions (which may add ancilla
//! qubits) and the classical register implied by the cast attributes.
//!

use std::collections::HashMap;

use crate::core::ArenaIndexHolder;
use crate::frontend::types::Ty;
use crate::layout::base::TypeLayout;
use crate::SymbolId;


/// Quantum layout of a type, recursively. Carries qubit counts only — no
/// alignment, no padding.
#[derive(Clone, Debug)]
pub enum QuantumTypeLayout {
    Primitive(QPrimitiveLayout),
    Struct(QStructLayout),
    Enum(QEnumLayout),
}

impl QuantumTypeLayout {
    /// Total number of qubits this type occupies.
    pub fn qubits(&self) -> u32 {
        match self {
            QuantumTypeLayout::Primitive(p) => p.qubits,
            QuantumTypeLayout::Struct(s) => s.qubits,
            QuantumTypeLayout::Enum(e) => e.qubits,
        }
    }

    /// Build the quantum layout directly from a frontend type. This is the
    /// authoritative path: the `Ty` knows exactly which primitives it holds.
    pub fn from_ty(ty: &Ty) -> Self {
        match ty {
            Ty::Primitive(p) => {
                QuantumTypeLayout::Primitive(QPrimitiveLayout { qubits: p.qubits() })
            }
            Ty::Struct(s) => {
                let mut members: Vec<QMemberLayout> = Vec::with_capacity(s.members.len());
                let mut offset: u32 = 0;
                for (sid, t) in s.iter() {
                    let layout = QuantumTypeLayout::from_ty(t);
                    let q = layout.qubits();
                    members.push(QMemberLayout { name: sid.clone(), offset, layout });
                    offset += q; // no alignment/padding: members are packed back-to-back
                }
                QuantumTypeLayout::Struct(QStructLayout { qubits: offset, members })
            }
            Ty::Enum(e) => {
                // For now only 2-variant quantum enums are allowed -> 1 qubit.
                debug_assert!(
                    e.variants.len() == 2,
                    "quantum enums must have exactly 2 variants, got {}",
                    e.variants.len()
                );
                let variants: Vec<SymbolId> = e.iter().map(|v| v.name().clone()).collect();
                QuantumTypeLayout::Enum(QEnumLayout { qubits: 1, variants })
            }
            Ty::Array(_) => todo!("quantum array layout"),
        }
    }

    /// Convert an already-computed classical [`TypeLayout`] into its quantum
    /// layout. Supports primitives and structs (the cases exercised when a
    /// quantum variable is cast); enums/arrays should be built via
    /// [`QuantumTypeLayout::from_ty`].
    pub(crate) fn from_type_layout(tl: &TypeLayout) -> Self {
        match tl {
            TypeLayout::Primitive(p, _) => {
                QuantumTypeLayout::Primitive(QPrimitiveLayout { qubits: p.qubits })
            }
            TypeLayout::Struct(s, _) => {
                let mut members: Vec<QMemberLayout> = Vec::with_capacity(s.members.len());
                let mut offset: u32 = 0;
                for m in &s.members {
                    let layout = QuantumTypeLayout::from_type_layout(&m.layout);
                    let q = layout.qubits();
                    members.push(QMemberLayout { name: m.name.clone(), offset, layout });
                    offset += q;
                }
                QuantumTypeLayout::Struct(QStructLayout { qubits: offset, members })
            }
            TypeLayout::Enum(_, _) => {
                todo!("convert quantum enum from TypeLayout; build from Ty instead")
            }
            TypeLayout::Array(_, _) => todo!("quantum array layout"),
        }
    }
}


#[derive(Clone, Debug)]
pub struct QPrimitiveLayout {
    pub qubits: u32,
}


#[derive(Clone, Debug)]
pub struct QStructLayout {
    pub qubits: u32,
    pub members: Vec<QMemberLayout>,
}

impl QStructLayout {
    pub fn member(&self, name: &SymbolId) -> Option<&QMemberLayout> {
        self.members.iter().find(|m| m.name == *name)
    }
}


/// A struct member in the quantum layout. `offset` is the qubit index of the
/// member's first qubit within the struct (no padding between members).
#[derive(Clone, Debug)]
pub struct QMemberLayout {
    pub name: SymbolId,
    pub offset: u32,
    pub layout: QuantumTypeLayout,
}


#[derive(Clone, Debug)]
pub struct QEnumLayout {
    pub qubits: u32,
    pub variants: Vec<SymbolId>,
}


/// Permanent store for quantum type layouts so they are computed once and
/// reused across every quantum variable in the program.
pub struct QuantumLayoutCache {
    cache: HashMap<Ty, QuantumTypeLayout>,
}

impl QuantumLayoutCache {
    pub fn new() -> Self {
        Self { cache: HashMap::new() }
    }

    /// Pre-compute the layouts for all primitive quantum types.
    pub fn initialize(&mut self) {
        use crate::frontend::types::TyPrimitive::*;
        for p in [QBool, QU2, QU3, QU4, QU8] {
            let _ = self.layout_of(&Ty::Primitive(p));
        }
    }

    pub fn has(&self, ty: &Ty) -> bool {
        self.cache.contains_key(ty)
    }

    /// Get the cached quantum layout, building and caching it on a miss.
    pub fn layout_of(&mut self, ty: &Ty) -> QuantumTypeLayout {
        if let Some(layout) = self.cache.get(ty) {
            return layout.clone();
        }
        let layout = QuantumTypeLayout::from_ty(ty);
        self.cache.insert(ty.clone(), layout.clone());
        layout
    }
}

impl Default for QuantumLayoutCache {
    fn default() -> Self {
        Self::new()
    }
}


/// A simple primitive quantum instruction. Beyond its identity, it may require
/// extra ancilla qubits to be allocated when composing the Q3L code.
#[derive(Clone, Debug)]
pub struct PrimitiveQuantumInstr {
    pub name: SymbolId,
    pub ancillas: u32,
}

impl PrimitiveQuantumInstr {
    pub fn new(name: SymbolId, ancillas: u32) -> Self {
        Self { name, ancillas }
    }
}


/// Everything that happens under a single quantum variable. Built when the
/// variable is cast, it owns the variable's quantum memory layout, the
/// primitive quantum instructions applied to it (carrying ancilla counts), and
/// the cast attributes that define the classical register.
#[derive(Clone, Debug)]
pub struct QuantumProgram {
    /// The root quantum variable (e.g. `@v`).
    pub var: SymbolId,
    /// Quantum type layout of the variable.
    pub layout: QuantumTypeLayout,
    /// Primitive quantum instructions applied to the variable.
    pub instrs: Vec<PrimitiveQuantumInstr>,
    /// Attributes cast to classical values; their count is the classical
    /// register (`creg`) size.
    pub cast_attrs: Vec<SymbolId>,
}

impl QuantumProgram {
    pub fn new(var: SymbolId, layout: QuantumTypeLayout) -> Self {
        Self { var, layout, instrs: Vec::new(), cast_attrs: Vec::new() }
    }

    /// Build a quantum program for a variable from its type, using (and
    /// populating) the permanent quantum layout cache.
    pub fn from_variable(var: SymbolId, ty: &Ty, cache: &mut QuantumLayoutCache) -> Self {
        let layout = cache.layout_of(ty);
        Self::new(var, layout)
    }

    pub fn add_instr(&mut self, instr: PrimitiveQuantumInstr) {
        self.instrs.push(instr);
    }

    pub fn cast_attr(&mut self, attr: SymbolId) {
        self.cast_attrs.push(attr);
    }

    /// Qubits used by the variable's data.
    pub fn data_qubits(&self) -> u32 {
        self.layout.qubits()
    }

    /// Ancilla qubits required by the instructions.
    pub fn ancilla_qubits(&self) -> u32 {
        self.instrs.iter().map(|i| i.ancillas).sum()
    }

    /// Total quantum memory size: data qubits plus instruction ancillas.
    pub fn total_qubits(&self) -> u32 {
        self.data_qubits() + self.ancilla_qubits()
    }

    /// Classical register size: the number of cast attributes.
    pub fn classical_size(&self) -> u32 {
        self.cast_attrs.len() as u32
    }
}


#[cfg(test)]
mod tests {
    use super::*;
    use crate::frontend::types::{Ty, TyEnum, TyPrimitive, TyStruct};

    fn sym(pos: u32) -> SymbolId {
        SymbolId(pos, true)
    }

    fn bell_t() -> Ty {
        // type @bell_t { @s:@bool, @t:@bool }
        let mut s = TyStruct::new(&sym(0));
        s.add_member(&sym(1), Ty::Primitive(TyPrimitive::QBool));
        s.add_member(&sym(2), Ty::Primitive(TyPrimitive::QBool));
        s.done();
        Ty::Struct(s)
    }

    fn polarization() -> Ty {
        // type @polarization { @V, @H }
        let mut e = TyEnum::new(&sym(10));
        e.add_variant(&sym(11), None);
        e.add_variant(&sym(12), None);
        e.done();
        Ty::Enum(e)
    }

    #[test]
    fn primitives_have_correct_qubit_counts() {
        let cases = [
            (TyPrimitive::QBool, 1),
            (TyPrimitive::QU2, 2),
            (TyPrimitive::QU3, 3),
            (TyPrimitive::QU4, 4),
            (TyPrimitive::QU8, 8),
        ];
        for (p, expected) in cases {
            let q = QuantumTypeLayout::from_ty(&Ty::Primitive(p.clone())).qubits();
            println!("{:?} -> {} qubit(s) (expect {})", p, q, expected);
            assert_eq!(q, expected);
        }
    }

    #[test]
    fn simple_struct_sums_members() {
        let q = QuantumTypeLayout::from_ty(&bell_t());
        println!("@bell_t -> {} qubits (expect 2)", q.qubits());
        assert_eq!(q.qubits(), 2);
        if let QuantumTypeLayout::Struct(s) = &q {
            println!("  members: {:?}", s.members.iter().map(|m| (m.name.read(), m.offset)).collect::<Vec<_>>());
            assert_eq!(s.members[0].offset, 0);
            assert_eq!(s.members[1].offset, 1);
        } else {
            panic!("expected struct layout");
        }
    }

    #[test]
    fn simple_enum_is_one_qubit() {
        let q = QuantumTypeLayout::from_ty(&polarization());
        println!("@polarization -> {} qubit(s) (expect 1)", q.qubits());
        assert_eq!(q.qubits(), 1);
    }

    #[test]
    fn nested_struct_recurses() {
        // type @nested { a:@bell_t, b:@u4, c:@polarization } -> 2 + 4 + 1 = 7
        let mut s = TyStruct::new(&sym(20));
        s.add_member(&sym(21), bell_t());
        s.add_member(&sym(22), Ty::Primitive(TyPrimitive::QU4));
        s.add_member(&sym(23), polarization());
        s.done();
        let q = QuantumTypeLayout::from_ty(&Ty::Struct(s));
        println!("@nested -> {} qubits (expect 7 = 2+4+1)", q.qubits());
        assert_eq!(q.qubits(), 7);
        if let QuantumTypeLayout::Struct(sl) = &q {
            let offsets: Vec<u32> = sl.members.iter().map(|m| m.offset).collect();
            println!("  member offsets: {:?} (expect [0, 2, 6])", offsets);
            assert_eq!(offsets, vec![0, 2, 6]);
        }
    }

    #[test]
    fn type_layout_converts_to_quantum_layout() {
        use crate::layout::arch::Arch;
        use crate::layout::base::LayoutCache;

        let mut cache = LayoutCache::new(Arch::get_arch64());
        cache.initialize(Some(Arch::get_arch64()));
        // ensure the struct's classical layout exists
        let _ = cache.layout_of(&Ty::Primitive(TyPrimitive::QBool));

        // primitive: classical TypeLayout(QBool) -> quantum 1 qubit
        let tl_prim = cache.layout_of(&Ty::Primitive(TyPrimitive::QU4));
        let q_prim = QuantumTypeLayout::from_type_layout(&tl_prim);
        println!("TypeLayout(QU4) -> quantum {} qubits (expect 4)", q_prim.qubits());
        assert_eq!(q_prim.qubits(), 4);

        // struct: insert @bell_t classically, then convert its TypeLayout
        cache.insert(&bell_t());
        let tl_struct = cache.layout_of(&bell_t());
        let q_struct = QuantumTypeLayout::from_type_layout(&tl_struct);
        println!("TypeLayout(@bell_t) -> quantum {} qubits (expect 2)", q_struct.qubits());
        assert_eq!(q_struct.qubits(), 2);
    }

    #[test]
    fn quantum_program_maps_qubits_and_ancillas() {
        let mut qcache = QuantumLayoutCache::new();
        qcache.initialize();

        for ancillas in [0u32, 1, 2, 3] {
            let mut prog = QuantumProgram::from_variable(sym(0), &bell_t(), &mut qcache);
            prog.add_instr(PrimitiveQuantumInstr::new(sym(99), ancillas)); // @sync
            prog.cast_attr(sym(2)); // only @v.@t is cast -> creg res[1]

            println!(
                "ancillas={} -> data={} + anc={} = total {} qubits, creg={}",
                ancillas,
                prog.data_qubits(),
                prog.ancilla_qubits(),
                prog.total_qubits(),
                prog.classical_size(),
            );
            assert_eq!(prog.data_qubits(), 2);
            assert_eq!(prog.ancilla_qubits(), ancillas);
            assert_eq!(prog.total_qubits(), 2 + ancillas);
            assert_eq!(prog.classical_size(), 1);
        }
    }
}
