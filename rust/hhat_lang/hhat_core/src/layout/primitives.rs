//!
//! Composing primitives for Cranelift framework form.
//!

use cranelift_codegen::ir::{types, Type};
use crate::core::Arenable;
use crate::frontend::types::TyPrimitive;
use crate::layout::arch::Arch;


/// Primitive kinds: single and pair.
///
#[derive(Clone, Debug)]
pub enum PrimitiveKind {
    /// for quantum types; they are zero-sized zero-alignment types
    None,
    /// for single primitive types: bool, integers, float numbers
    Single(Type),
    /// for composed types: complex numbers `C64` and `C128`, and string
    Pair(Type, Type),
}


#[derive(Clone, Debug)]
pub struct PrimitiveLayout {
    pub size: u32,
    pub align: u32,
    /// Number of qubits this primitive occupies in the quantum layout.
    /// Always 0 for classical primitives.
    pub qubits: u32,
    pub kind: PrimitiveKind,
}


impl PrimitiveLayout {

    /// Get a layout for primitive types.
    ///
    pub fn layout(ty: &TyPrimitive, arch: Option<Arch>) -> Self {
        // qubit footprint is independent of the classical (size/align/kind) one
        let qubits = ty.qubits();
        let (size, align, kind) = match ty {
            TyPrimitive::Bool => (1, 1, PrimitiveKind::Single(types::I8)),
            TyPrimitive::U32 | TyPrimitive::I32 => (4, 4, PrimitiveKind::Single(types::I32)),
            TyPrimitive::U64 | TyPrimitive::I64 => (8, 8, PrimitiveKind::Single(types::I64)),
            TyPrimitive::F32 => (4, 4, PrimitiveKind::Single(types::F32)),
            TyPrimitive::F64 => (8, 8, PrimitiveKind::Single(types::F64)),
            TyPrimitive::C64 => (8, 4, PrimitiveKind::Pair(types::F32, types::F32)),
            TyPrimitive::C128 => (16, 8, PrimitiveKind::Pair(types::F64, types::F64)),
            TyPrimitive::String => match arch {
                Some(a) => (
                    a.pointer_size,
                    a.pointer_align,
                    PrimitiveKind::Pair(a.pointer_type, a.pointer_type),
                ),
                None => panic!("string must have Arch definition (32 or 64 bits)"),
            },
            // Quantum primitives have no classical footprint (zero-sized, zero-aligned);
            // their footprint lives in `qubits` instead.
            TyPrimitive::QBool
            | TyPrimitive::QU2
            | TyPrimitive::QU3
            | TyPrimitive::QU4
            | TyPrimitive::QU8 => (0, 0, PrimitiveKind::None),
        };
        PrimitiveLayout { size, align, qubits, kind }
    }
}

impl Arenable for PrimitiveLayout {}
