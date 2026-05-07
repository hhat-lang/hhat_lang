//!
//! Base layouts for types to be used for MIR.
//!

use crate::layout::adt::{ArrayLayout, EnumLayout, StructLayout};
use crate::layout::primitives::PrimitiveLayout;


#[derive(Clone, Debug)]
pub enum TypeLayout {
    Primitive(PrimitiveLayout, MemoryRegion),
    Struct(StructLayout, MemoryRegion),
    Enum(EnumLayout, MemoryRegion),
    Array(ArrayLayout, MemoryRegion),
}

impl TypeLayout {
    pub fn size(&self) -> u32 {
        match self {
            TypeLayout::Primitive(layout, _) => layout.size,
            TypeLayout::Struct(layout, _) => layout.size,
            TypeLayout::Enum(layout, _) => layout.size,
            TypeLayout::Array(layout, _) => layout.size,
        }
    }

    pub fn align(&self) -> u32 {
        match self {
            TypeLayout::Primitive(layout, _) => layout.align,
            TypeLayout::Struct(layout, _) => layout.align,
            TypeLayout::Enum(layout, _) => layout.align,
            TypeLayout::Array(layout, _) => layout.align,
        }
    }

    pub fn with_mem_region(&mut self, mem_region: MemoryRegion) {
        match self {
            TypeLayout::Primitive(_, mr)
            | TypeLayout::Struct(_, mr)
            | TypeLayout::Enum(_, mr)
            | TypeLayout::Array(_, mr) => *mr = mem_region
        }
    }
}


/// Where to store data: global scope, stack or heap.
///
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum MemoryRegion {
    GlobalScope,
    Stack,
    Heap,
}