//!
//! Composing primitives for Cranelift framework form.
//!

use cranelift_codegen::ir::{types, Type};
use crate::frontend::types::TyPrimitive;
use crate::layout::arch::Arch;


/// Primitive kinds: single and pair.
///
#[derive(Clone, Debug)]
pub enum PrimitiveKind {
    /// for single primitive types: bool, integers, float numbers
    Single(Type),
    /// for composed types: complex numbers `C64` and `C128`, and string
    Pair(Type, Type),
}


#[derive(Clone, Debug)]
pub struct PrimitiveLayout {
    pub size: u32,
    pub align: u32,
    pub repr: PrimitiveKind,
}


impl PrimitiveLayout {

    /// Get a layout for primitive types.
    ///
    pub fn get_layout(ty: &TyPrimitive, arch: Option<Arch>) -> Self {
        match ty {
            TyPrimitive::Bool => PrimitiveLayout {
                size: 1,
                align: 1,
                repr: PrimitiveKind::Single(types::I8)
            },
            TyPrimitive::U32 | TyPrimitive::I32 => PrimitiveLayout {
                size: 4,
                align: 4,
                repr: PrimitiveKind::Single(types::I32)
            },
            TyPrimitive::U64 | TyPrimitive::I64 => PrimitiveLayout {
                size: 8,
                align: 8,
                repr: PrimitiveKind::Single(types::I64)
            },
            TyPrimitive::F32 => PrimitiveLayout {
                size: 4,
                align: 4,
                repr: PrimitiveKind::Single(types::F32)
            },
            TyPrimitive::F64 => PrimitiveLayout {
                size: 8,
                align: 8,
                repr: PrimitiveKind::Single(types::F64)
            },
            TyPrimitive::C64 => PrimitiveLayout {
                size: 8,
                align: 4,
                repr: PrimitiveKind::Pair(types::F32, types::F32)
            },
            TyPrimitive::C128 => PrimitiveLayout {
                size: 16,
                align: 8,
                repr: PrimitiveKind::Pair(types::F64, types::F64)
            },
            TyPrimitive::String => match arch {
                Some(a) => PrimitiveLayout {
                    size: a.pointer_size * 2,
                    align: a.pointer_align,
                    repr: PrimitiveKind::Pair(a.pointer_type, a.pointer_type),
                },
                None => panic!("string must have Arch definition (32 or 64 bits)"),
            }
        }
    }
}

