//!
//! Quantum memory layout for quantum data types.
//!
//! This is the quantum counterpart to the classical `TypeLayout` / `LayoutCache`
//! machinery. Classical layouts count bytes and insert alignment padding; quantum
//! layouts count qubits with no padding at all (we cannot afford wasting qubits).
//!
//! Primitive quantum types report their qubit width directly (`@bool` → 1, up to
//! `@u8` → 8). Structs sum their quantum members back-to-back. Two-variant enums
//! occupy exactly one qubit (`|0⟩` and `|1⟩`).
//!
//! A `QuantumProgram` collects the full qubit budget for a single quantum variable:
//! data qubits from its type layout, ancilla qubits from instructions, and classical
//! register bits from cast (measurement) operations.
//!

use std::collections::HashMap;

use crate::frontend::types::{Ty, TyEnum, TyPrimitive, TyStruct};
use crate::SymbolId;

/// Qubit count for a quantum primitive type.
///
#[derive(Clone, Debug)]
pub struct QuantumPrimitiveLayout {
    pub qubits: u32,
}

impl QuantumPrimitiveLayout {
    /// Return the qubit count for a quantum primitive.
    ///
    /// Panics on classical primitives since they have no quantum representation.
    ///
    pub fn layout(ty: &TyPrimitive) -> Self {
        match ty {
            TyPrimitive::QBool => QuantumPrimitiveLayout { qubits: 1 },
            TyPrimitive::QU2 => QuantumPrimitiveLayout { qubits: 2 },
            TyPrimitive::QU3 => QuantumPrimitiveLayout { qubits: 3 },
            TyPrimitive::QU4 => QuantumPrimitiveLayout { qubits: 4 },
            TyPrimitive::QU8 => QuantumPrimitiveLayout { qubits: 8 },
            other => panic!(
                "classical primitive {:?} has no quantum layout",
                other
            ),
        }
    }
}

/// Layout for a single quantum member inside a struct.
///
/// Tracks the member's name, its qubit offset within the parent struct,
/// and its own quantum layout (so nested types can be inspected).
///
#[derive(Clone, Debug)]
pub struct QuantumMemberLayout {
    pub name: SymbolId,
    pub qubit_offset: u32,
    pub layout: QuantumTypeLayout,
}

/// Qubit layout for a quantum struct type.
///
/// Only quantum members contribute to the qubit count; classical members
/// inside a quantum struct are handled separately by the classical
/// `LayoutCache` and do not appear here.
///
#[derive(Clone, Debug)]
pub struct QuantumStructLayout {
    pub qubits: u32,
    pub members: Vec<QuantumMemberLayout>,
}

impl QuantumStructLayout {
    /// Build the quantum layout for a struct by walking its members.
    ///
    /// Classical members are skipped. Quantum members are laid out
    /// back-to-back with no alignment or padding.
    ///
    pub fn layout(ty: &TyStruct, cache: &mut QuantumLayoutCache) -> Self {
        let mut offset: u32 = 0;
        let mut members: Vec<QuantumMemberLayout> = Vec::new();

        let _ = ty
            .iter()
            .map(|(sid, member_ty)| {
                if member_ty.is_quantum() {
                    let member_layout = cache.layout_of(member_ty);
                    let member_qubits = member_layout.qubits();
                    members.push(QuantumMemberLayout {
                        name: sid.clone(),
                        qubit_offset: offset,
                        layout: member_layout,
                    });
                    offset += member_qubits;
                }
            })
            .collect::<Vec<()>>();

        Self {
            qubits: offset,
            members,
        }
    }
}

/// Qubit layout for a quantum enum type.
///
/// Currently only 2-variant named enums are allowed: the first variant
/// maps to `|0⟩` and the second to `|1⟩`, so exactly 1 qubit is needed.
///
#[derive(Clone, Debug)]
pub struct QuantumEnumLayout {
    pub qubits: u32,
}

impl QuantumEnumLayout {
    /// Build the quantum layout for a 2-variant enum.
    ///
    /// Panics if the enum does not have exactly 2 variants.
    ///
    pub fn layout(ty: &TyEnum) -> Self {
        assert_eq!(
            ty.variants.len(),
            2,
            "quantum enums must have exactly 2 variants, got {}",
            ty.variants.len()
        );
        Self { qubits: 1 }
    }
}

/// Unified quantum type layout: primitive, struct, or enum.
///
#[derive(Clone, Debug)]
pub enum QuantumTypeLayout {
    Primitive(QuantumPrimitiveLayout),
    Struct(QuantumStructLayout),
    Enum(QuantumEnumLayout),
}

impl QuantumTypeLayout {
    /// Total qubit count for this type layout.
    ///
    pub fn qubits(&self) -> u32 {
        match self {
            QuantumTypeLayout::Primitive(l) => l.qubits,
            QuantumTypeLayout::Struct(l) => l.qubits,
            QuantumTypeLayout::Enum(l) => l.qubits,
        }
    }
}

/// Cache for quantum type layouts, keyed by `Ty`.
///
/// Mirrors the classical `LayoutCache` so each quantum type is computed
/// once and reused across all quantum variables in the program.
///
pub struct QuantumLayoutCache {
    cache: HashMap<Ty, QuantumTypeLayout>,
}

impl QuantumLayoutCache {
    pub fn new() -> Self {
        Self {
            cache: HashMap::new(),
        }
    }

    pub fn has(&self, ty: &Ty) -> bool {
        self.cache.contains_key(ty)
    }

    /// Insert a quantum type layout into the cache.
    ///
    /// For structs, member types are inserted recursively before the
    /// struct entry itself is built, so nested lookups always succeed.
    ///
    pub fn insert_layout(&mut self, ty: &Ty) -> Option<QuantumTypeLayout> {
        match ty.clone() {
            Ty::Primitive(p) => self.cache.insert(
                ty.clone(),
                QuantumTypeLayout::Primitive(QuantumPrimitiveLayout::layout(&p)),
            ),
            Ty::Struct(s) => {
                for (_sid, member_ty) in s.iter() {
                    if member_ty.is_quantum() && !self.has(member_ty) {
                        self.insert_layout(member_ty);
                    }
                }
                let struct_layout = QuantumStructLayout::layout(&s, self);
                self.cache.insert(
                    ty.clone(),
                    QuantumTypeLayout::Struct(struct_layout),
                )
            }
            Ty::Enum(e) => self.cache.insert(
                ty.clone(),
                QuantumTypeLayout::Enum(QuantumEnumLayout::layout(&e)),
            ),
            Ty::Array(_) => {
                unimplemented!("quantum array layout is not yet specified")
            }
        }
    }

    /// Look up a previously inserted layout.
    ///
    /// Panics if the type has not been inserted yet.
    ///
    pub fn layout_of(&mut self, ty: &Ty) -> QuantumTypeLayout {
        match self.cache.get(ty) {
            Some(l) => l.clone(),
            None => panic!("quantum layout of type {:?} not found", ty),
        }
    }
}

/// A minimal quantum instruction type.
///
/// Quantum instructions may require ancilla qubits beyond the data qubits
/// of the variable. This count is accumulated into the `QuantumProgram`
/// to compute the total qubit budget for the Q3L backend.
///
#[derive(Clone, Debug)]
pub struct QuantumInstruction {
    pub name: SymbolId,
    pub ancilla_qubits: u32,
}

/// A quantum program for a single quantum variable.
///
/// Built when the variable completes its lifecycle (declaration, assignment,
/// cast). Collects:
/// - `data_qubits`: from the root type layout (how many qubits the type needs),
/// - `ancilla_qubits`: accumulated from quantum instructions,
/// - `classical_register_bits`: one bit per cast (measured) attribute.
///
pub struct QuantumProgram {
    pub root_layout: QuantumTypeLayout,
    pub data_qubits: u32,
    pub ancilla_qubits: u32,
    pub classical_register_bits: u32,
}

impl QuantumProgram {
    /// Create a quantum program from the variable's root type layout.
    ///
    pub fn new(root_layout: QuantumTypeLayout) -> Self {
        let data_qubits = root_layout.qubits();
        Self {
            root_layout,
            data_qubits,
            ancilla_qubits: 0,
            classical_register_bits: 0,
        }
    }

    /// Apply a quantum instruction, accumulating its ancilla qubits.
    ///
    pub fn apply_instruction(&mut self, instr: &QuantumInstruction) {
        self.ancilla_qubits += instr.ancilla_qubits;
    }

    /// Record that a quantum attribute was cast (measured), adding one
    /// classical bit to the output register.
    ///
    pub fn cast_attribute(&mut self) {
        self.classical_register_bits += 1;
    }

    /// Total qubits the Q3L backend must allocate: data + ancilla.
    ///
    pub fn total_qubits(&self) -> u32 {
        self.data_qubits + self.ancilla_qubits
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::frontend::types::{Ty, TyEnum, TyPrimitive, TyStruct};
    use crate::SymbolId;

    // ── 1. Primitive quantum types ───────────────────────────────

    #[test]
    fn primitive_qbool_is_1_qubit() {
        let layout = QuantumPrimitiveLayout::layout(&TyPrimitive::QBool);
        assert_eq!(layout.qubits, 1);
    }

    #[test]
    fn primitive_qu2_is_2_qubits() {
        let layout = QuantumPrimitiveLayout::layout(&TyPrimitive::QU2);
        assert_eq!(layout.qubits, 2);
    }

    #[test]
    fn primitive_qu3_is_3_qubits() {
        let layout = QuantumPrimitiveLayout::layout(&TyPrimitive::QU3);
        assert_eq!(layout.qubits, 3);
    }

    #[test]
    fn primitive_qu4_is_4_qubits() {
        let layout = QuantumPrimitiveLayout::layout(&TyPrimitive::QU4);
        assert_eq!(layout.qubits, 4);
    }

    #[test]
    fn primitive_qu8_is_8_qubits() {
        let layout = QuantumPrimitiveLayout::layout(&TyPrimitive::QU8);
        assert_eq!(layout.qubits, 8);
    }

    #[test]
    #[should_panic(expected = "classical primitive")]
    fn classical_primitive_has_no_quantum_layout() {
        QuantumPrimitiveLayout::layout(&TyPrimitive::U32);
    }

    // ── 2. Simple quantum struct ─────────────────────────────────

    /// @bell_t { @s:@bool, @t:@bool } → 2 qubits, offsets 0 and 1.
    #[test]
    fn struct_bell_t_is_2_qubits() {
        let mut cache = QuantumLayoutCache::new();

        let name = SymbolId(0, true);
        let mut bell = TyStruct::new(&name);
        bell.add_member(&SymbolId(1, true), Ty::Primitive(TyPrimitive::QBool));
        bell.add_member(&SymbolId(2, true), Ty::Primitive(TyPrimitive::QBool));
        bell.done();

        cache.insert_layout(&Ty::Struct(bell.clone()));
        let layout = cache.layout_of(&Ty::Struct(bell));
        assert_eq!(layout.qubits(), 2);

        if let QuantumTypeLayout::Struct(sl) = layout {
            assert_eq!(sl.members.len(), 2);
            assert_eq!(sl.members[0].qubit_offset, 0);
            assert_eq!(sl.members[1].qubit_offset, 1);
        } else {
            panic!("expected QuantumTypeLayout::Struct");
        }
    }

    /// A quantum struct with mixed classical/quantum fields.
    /// Only quantum fields count toward the qubit layout.
    #[test]
    fn struct_with_classical_members_only_counts_quantum() {
        let mut cache = QuantumLayoutCache::new();

        let name = SymbolId(0, true);
        let mut mixed = TyStruct::new(&name);
        mixed.add_member(&SymbolId(1, true), Ty::Primitive(TyPrimitive::QBool));
        mixed.add_member(&SymbolId(2, false), Ty::Primitive(TyPrimitive::U32));
        mixed.add_member(&SymbolId(3, true), Ty::Primitive(TyPrimitive::QU8));
        mixed.add_member(&SymbolId(4, false), Ty::Primitive(TyPrimitive::Bool));
        mixed.done();

        cache.insert_layout(&Ty::Struct(mixed.clone()));
        let layout = cache.layout_of(&Ty::Struct(mixed));
        assert_eq!(layout.qubits(), 9); // 1 + 8, classical fields ignored

        if let QuantumTypeLayout::Struct(sl) = layout {
            assert_eq!(sl.members.len(), 2); // only 2 quantum members
            assert_eq!(sl.members[0].qubit_offset, 0);
            assert_eq!(sl.members[1].qubit_offset, 1);
        } else {
            panic!("expected QuantumTypeLayout::Struct");
        }
    }

    // ── 3. Simple quantum enum ───────────────────────────────────

    /// @polarization { @V, @H } → 1 qubit.
    #[test]
    fn enum_polarization_is_1_qubit() {
        let mut cache = QuantumLayoutCache::new();

        let name = SymbolId(0, true);
        let mut pol = TyEnum::new(&name);
        pol.add_variant(&SymbolId(1, true), None);
        pol.add_variant(&SymbolId(2, true), None);
        pol.done();

        cache.insert_layout(&Ty::Enum(pol.clone()));
        let layout = cache.layout_of(&Ty::Enum(pol));
        assert_eq!(layout.qubits(), 1);
    }

    /// @side { @L, @R } → also 1 qubit.
    #[test]
    fn enum_side_is_1_qubit() {
        let mut cache = QuantumLayoutCache::new();

        let name = SymbolId(10, true);
        let mut side = TyEnum::new(&name);
        side.add_variant(&SymbolId(11, true), None);
        side.add_variant(&SymbolId(12, true), None);
        side.done();

        cache.insert_layout(&Ty::Enum(side.clone()));
        let layout = cache.layout_of(&Ty::Enum(side));
        assert_eq!(layout.qubits(), 1);
    }

    #[test]
    #[should_panic(expected = "exactly 2 variants")]
    fn enum_with_three_variants_panics() {
        let name = SymbolId(0, true);
        let mut bad = TyEnum::new(&name);
        bad.add_variant(&SymbolId(1, true), None);
        bad.add_variant(&SymbolId(2, true), None);
        bad.add_variant(&SymbolId(3, true), None);
        bad.done();

        let mut cache = QuantumLayoutCache::new();
        cache.insert_layout(&Ty::Enum(bad));
    }

    // ── 4. Nested quantum structs ────────────────────────────────

    /// nested { @bell_t, @u4, @polarization } → 7 qubits (2 + 4 + 1).
    #[test]
    fn nested_struct_is_7_qubits() {
        let mut cache = QuantumLayoutCache::new();

        // @bell_t { @s:@bool, @t:@bool }
        let bell_name = SymbolId(0, true);
        let mut bell = TyStruct::new(&bell_name);
        bell.add_member(&SymbolId(1, true), Ty::Primitive(TyPrimitive::QBool));
        bell.add_member(&SymbolId(2, true), Ty::Primitive(TyPrimitive::QBool));
        bell.done();
        let bell_ty = Ty::Struct(bell);

        // @polarization { @V, @H }
        let pol_name = SymbolId(3, true);
        let mut pol = TyEnum::new(&pol_name);
        pol.add_variant(&SymbolId(4, true), None);
        pol.add_variant(&SymbolId(5, true), None);
        pol.done();
        let pol_ty = Ty::Enum(pol);

        // nested { @bell_t, @u4, @polarization }
        let nested_name = SymbolId(6, true);
        let mut nested = TyStruct::new(&nested_name);
        nested.add_member(&SymbolId(7, true), bell_ty);
        nested.add_member(&SymbolId(8, true), Ty::Primitive(TyPrimitive::QU4));
        nested.add_member(&SymbolId(9, true), pol_ty);
        nested.done();

        // insert only the top-level; members resolve recursively
        cache.insert_layout(&Ty::Struct(nested.clone()));
        let layout = cache.layout_of(&Ty::Struct(nested));
        assert_eq!(layout.qubits(), 7);

        if let QuantumTypeLayout::Struct(sl) = layout {
            assert_eq!(sl.members.len(), 3);
            assert_eq!(sl.members[0].qubit_offset, 0); // bell_t at 0
            assert_eq!(sl.members[1].qubit_offset, 2); // u4 at 2
            assert_eq!(sl.members[2].qubit_offset, 6); // polarization at 6
        } else {
            panic!("expected QuantumTypeLayout::Struct");
        }
    }

    /// Three-level nesting: outer contains a middle struct that itself
    /// contains an inner struct, verifying recursive resolution.
    #[test]
    fn deeply_nested_struct_resolves_recursively() {
        let mut cache = QuantumLayoutCache::new();

        // inner { @a:@u2 } → 2 qubits
        let inner_name = SymbolId(0, true);
        let mut inner = TyStruct::new(&inner_name);
        inner.add_member(&SymbolId(1, true), Ty::Primitive(TyPrimitive::QU2));
        inner.done();
        let inner_ty = Ty::Struct(inner);

        // middle { inner, @b:@u3 } → 2 + 3 = 5 qubits
        let mid_name = SymbolId(2, true);
        let mut mid = TyStruct::new(&mid_name);
        mid.add_member(&SymbolId(3, true), inner_ty);
        mid.add_member(&SymbolId(4, true), Ty::Primitive(TyPrimitive::QU3));
        mid.done();
        let mid_ty = Ty::Struct(mid);

        // outer { middle, @c:@bool } → 5 + 1 = 6 qubits
        let outer_name = SymbolId(5, true);
        let mut outer = TyStruct::new(&outer_name);
        outer.add_member(&SymbolId(6, true), mid_ty);
        outer.add_member(&SymbolId(7, true), Ty::Primitive(TyPrimitive::QBool));
        outer.done();

        // only insert the outermost type; everything resolves recursively
        cache.insert_layout(&Ty::Struct(outer.clone()));
        let layout = cache.layout_of(&Ty::Struct(outer));
        assert_eq!(layout.qubits(), 6);

        if let QuantumTypeLayout::Struct(sl) = layout {
            assert_eq!(sl.members[0].qubit_offset, 0); // middle at 0
            assert_eq!(sl.members[1].qubit_offset, 5); // @bool at 5
        } else {
            panic!("expected QuantumTypeLayout::Struct");
        }
    }

    // ── 5. TypeLayout ↔ QuantumTypeLayout round-trip ─────────────

    /// A primitive quantum `Ty` produces a zero-sized classical layout
    /// and a qubit-counted quantum layout.
    #[test]
    fn round_trip_primitive() {
        use crate::layout::arch::Arch;
        use crate::layout::base::LayoutCache;

        let ty = Ty::Primitive(TyPrimitive::QBool);

        // classical: quantum primitives are zero-sized
        let mut classical = LayoutCache::new(Arch::get_arch64());
        classical.initialize(Some(Arch::get_arch64()));
        let cl = classical.layout_of(&ty);
        assert_eq!(cl.size(), 0);
        assert_eq!(cl.align(), 0);

        // quantum: QBool is 1 qubit
        let mut quantum = QuantumLayoutCache::new();
        quantum.insert_layout(&ty);
        let ql = quantum.layout_of(&ty);
        assert_eq!(ql.qubits(), 1);
    }

    /// A quantum struct with both classical and quantum members can have
    /// its two layouts computed independently.
    #[test]
    fn round_trip_struct() {
        use crate::layout::arch::Arch;
        use crate::layout::base::LayoutCache;

        // @mixed { @q:@bool, c:U32 }
        let name = SymbolId(0, true);
        let mut mixed = TyStruct::new(&name);
        mixed.add_member(&SymbolId(1, true), Ty::Primitive(TyPrimitive::QBool));
        mixed.add_member(&SymbolId(2, false), Ty::Primitive(TyPrimitive::U32));
        mixed.done();
        let ty = Ty::Struct(mixed);

        // classical layout: only the U32 member (4 bytes, align 4)
        let mut classical = LayoutCache::new(Arch::get_arch64());
        classical.initialize(Some(Arch::get_arch64()));
        classical.insert_layout(&ty, &Some(Arch::get_arch64()));
        let cl = classical.layout_of(&ty);
        assert_eq!(cl.size(), 4);
        assert_eq!(cl.align(), 4);

        // quantum layout: only the @bool member (1 qubit)
        let mut quantum = QuantumLayoutCache::new();
        quantum.insert_layout(&ty);
        let ql = quantum.layout_of(&ty);
        assert_eq!(ql.qubits(), 1);
    }

    // ── 6. QuantumProgram with instructions and cast ─────────────

    /// Full @v:@bell_t workflow from the issue: 2 data qubits, a @sync
    /// instruction with 1 ancilla, and only @v.@t is cast (1 creg bit).
    #[test]
    fn quantum_program_bell_t_workflow() {
        let mut cache = QuantumLayoutCache::new();

        // @bell_t { @s:@bool, @t:@bool }
        let name = SymbolId(0, true);
        let mut bell = TyStruct::new(&name);
        bell.add_member(&SymbolId(1, true), Ty::Primitive(TyPrimitive::QBool));
        bell.add_member(&SymbolId(2, true), Ty::Primitive(TyPrimitive::QBool));
        bell.done();

        cache.insert_layout(&Ty::Struct(bell.clone()));
        let layout = cache.layout_of(&Ty::Struct(bell));

        let mut qprog = QuantumProgram::new(layout);
        assert_eq!(qprog.data_qubits, 2);
        assert_eq!(qprog.ancilla_qubits, 0);
        assert_eq!(qprog.total_qubits(), 2);

        // @sync instruction with 1 ancilla qubit
        let sync_instr = QuantumInstruction {
            name: SymbolId(10, true),
            ancilla_qubits: 1,
        };
        qprog.apply_instruction(&sync_instr);
        assert_eq!(qprog.ancilla_qubits, 1);
        assert_eq!(qprog.total_qubits(), 3);

        // cast only @v.@t → 1 classical bit
        qprog.cast_attribute();
        assert_eq!(qprog.classical_register_bits, 1);
    }

    /// Multiple instructions with varying ancilla counts (0, 2, 3)
    /// applied to a @u4 variable.
    #[test]
    fn quantum_program_accumulates_ancillas() {
        let mut cache = QuantumLayoutCache::new();

        let ty = Ty::Primitive(TyPrimitive::QU4);
        cache.insert_layout(&ty);
        let layout = cache.layout_of(&ty);

        let mut qprog = QuantumProgram::new(layout);
        assert_eq!(qprog.data_qubits, 4);

        qprog.apply_instruction(&QuantumInstruction {
            name: SymbolId(20, true),
            ancilla_qubits: 0,
        });
        assert_eq!(qprog.total_qubits(), 4);

        qprog.apply_instruction(&QuantumInstruction {
            name: SymbolId(21, true),
            ancilla_qubits: 2,
        });
        assert_eq!(qprog.total_qubits(), 6);

        qprog.apply_instruction(&QuantumInstruction {
            name: SymbolId(22, true),
            ancilla_qubits: 3,
        });
        assert_eq!(qprog.total_qubits(), 9);
    }

    /// Cast two attributes → classical register should be 2 bits.
    #[test]
    fn quantum_program_cast_multiple_attributes() {
        let mut cache = QuantumLayoutCache::new();

        let name = SymbolId(0, true);
        let mut s = TyStruct::new(&name);
        s.add_member(&SymbolId(1, true), Ty::Primitive(TyPrimitive::QBool));
        s.add_member(&SymbolId(2, true), Ty::Primitive(TyPrimitive::QU2));
        s.done();

        cache.insert_layout(&Ty::Struct(s.clone()));
        let layout = cache.layout_of(&Ty::Struct(s));

        let mut qprog = QuantumProgram::new(layout);
        assert_eq!(qprog.data_qubits, 3);

        // cast both attributes
        qprog.cast_attribute();
        qprog.cast_attribute();
        assert_eq!(qprog.classical_register_bits, 2);
    }

    /// Cache reuse: inserting a type twice does not break anything,
    /// and different quantum variables sharing the same type get
    /// identical layouts without recomputation.
    #[test]
    fn layout_cache_reuses_entries() {
        let mut cache = QuantumLayoutCache::new();

        let ty = Ty::Primitive(TyPrimitive::QU3);
        cache.insert_layout(&ty);
        cache.insert_layout(&ty); // second insert is harmless

        let l1 = cache.layout_of(&ty);
        let l2 = cache.layout_of(&ty);
        assert_eq!(l1.qubits(), l2.qubits());
        assert_eq!(l1.qubits(), 3);
    }
}
