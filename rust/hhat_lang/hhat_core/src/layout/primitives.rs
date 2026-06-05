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
    pub qubits: u32,
    pub kind: PrimitiveKind,
}


impl PrimitiveLayout {

    /// Get a layout for primitive types.
    ///
    pub fn layout(ty: &TyPrimitive, arch: Option<Arch>) -> Self {
        match ty {
            TyPrimitive::Bool => PrimitiveLayout {
                size: 1,
                align: 1,
                qubits: 0,
                kind: PrimitiveKind::Single(types::I8)
            },
            TyPrimitive::U32 | TyPrimitive::I32 => PrimitiveLayout {
                size: 4,
                align: 4,
                qubits: 0,
                kind: PrimitiveKind::Single(types::I32)
            },
            TyPrimitive::U64 | TyPrimitive::I64 => PrimitiveLayout {
                size: 8,
                align: 8,
                qubits: 0,
                kind: PrimitiveKind::Single(types::I64)
            },
            TyPrimitive::F32 => PrimitiveLayout {
                size: 4,
                align: 4,
                qubits: 0,
                kind: PrimitiveKind::Single(types::F32)
            },
            TyPrimitive::F64 => PrimitiveLayout {
                size: 8,
                align: 8,
                qubits: 0,
                kind: PrimitiveKind::Single(types::F64)
            },
            TyPrimitive::C64 => PrimitiveLayout {
                size: 8,
                align: 4,
                qubits: 0,
                kind: PrimitiveKind::Pair(types::F32, types::F32)
            },
            TyPrimitive::C128 => PrimitiveLayout {
                size: 16,
                align: 8,
                qubits: 0,
                kind: PrimitiveKind::Pair(types::F64, types::F64)
            },
            TyPrimitive::String => if let Some(a) = arch {
                PrimitiveLayout {
                    size: a.pointer_size,
                    align: a.pointer_align,
                    qubits: 0,
                    kind: PrimitiveKind::Pair(a.pointer_type, a.pointer_type),
                }
            } else {
                panic!("string must have Arch definition (32 or 64 bits)")
            }
            TyPrimitive::QBool => PrimitiveLayout {
                size: 0,
                align: 0,
                qubits: 1,
                kind: PrimitiveKind::None,
            },
            TyPrimitive::QU2 => PrimitiveLayout {
                size: 0,
                align: 0,
                qubits: 2,
                kind: PrimitiveKind::None,
            },
            TyPrimitive::QU3 => PrimitiveLayout {
                size: 0,
                align: 0,
                qubits: 3,
                kind: PrimitiveKind::None,
            },
            TyPrimitive::QU4 => PrimitiveLayout {
                size: 0,
                align: 0,
                qubits: 4,
                kind: PrimitiveKind::None,
            },
            TyPrimitive::QU8 => PrimitiveLayout {
                size: 0,
                align: 0,
                qubits: 8,
                kind: PrimitiveKind::None,
            },
        }
    }
}

impl Arenable for PrimitiveLayout {}
